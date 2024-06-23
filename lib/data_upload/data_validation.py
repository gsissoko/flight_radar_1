from copy import deepcopy

from marshmallow import fields, Schema, ValidationError

from lib.data_upload import INTEGRITY_MAPPING, VARIABLE_STATUS, MISSING_VARIABLE_VALUE, VALID_VARIABLE, \
    INVALID_VARIABLE_TYPE
from lib.db_toolkits.exalt_handler import ADMIN_CREDENTIAL
from lib.db_toolkits.exalt_handler.get import ExaltGetHandler
from lib.db_toolkits.utilities import create_connection


class DataValidator:
    def __init__(self, data: list):
        connexion = create_connection(ADMIN_CREDENTIAL)
        self.__mapping = ExaltGetHandler(connexion, connexion.cursor()).get_mapping("flight")
        self.__integrity_mapping = INTEGRITY_MAPPING
        self.__data = data
        self.__schema = self.__generate_schema()
        self.__status, self.__validated_data = self.__validate_data()

    def __generate_schema(self):
        fields_dict = {}
        for key in self.__mapping.keys():
            if key in list(self.__integrity_mapping):
                if self.__mapping[key] == "integer":
                    params = {
                        "required": True,
                        "allow_string": False,
                        "strict": True
                    }
                    fields_dict[key] = fields.Integer(
                        **params
                    )
                elif self.__mapping[key] in ["float", "double", "numeric"]:
                    params = {
                        "required": True,
                        "allow_string": False,
                        "strict": True
                    }
                    fields_dict[key] = fields.Float(
                        **params
                    )
                elif self.__mapping[key] in ["character varying"]:
                    params = {"required": True, "allow_none": False, "strict": True}
                    fields_dict[key] = fields.String(
                        **params
                    )
                elif self.__mapping[key] == ["timestamp with time zone", "date"]:
                    fields_dict[key] = fields.DateTime(required=True)
                elif self.__mapping[key] == "bool":
                    fields_dict[key] = fields.Boolean(required=True)

        return type('GeneratedSchema', (Schema,), fields_dict)

    def __validate_data(self):
        status = {}
        for index in range(len(self.__data)):
            status.update({
                index: {field: VARIABLE_STATUS[VALID_VARIABLE] for field in list(self.__integrity_mapping)}
            })
        try:
            validated_data = self.__schema(many=True).load(self.__data, unknown="exclude")
        except ValidationError as err:
            for index, error_loads in err.messages.items():
                for field_name, message in error_loads.items():
                    error_message = message[0]
                    if "not a valid" in error_message.lower() or "invalid" in error_message.lower():
                        status[index].update({field_name: VARIABLE_STATUS[INVALID_VARIABLE_TYPE]})
                    elif "missing" in error_message.lower() or "field may not be null" in error_message.lower():
                        status[index].update({field_name: VARIABLE_STATUS[MISSING_VARIABLE_VALUE]})
            validated_data = self.__data

        return status, validated_data

    def process(self):
        data_to_upload = deepcopy(self.__validated_data)
        data_status = [{} for _ in range(len(data_to_upload))]
        result = []
        if self.__status is not None:
            for index, field_status in self.__status.items():
                data_status[index] = field_status
                for field_name, status in field_status.items():
                    if status not in [VARIABLE_STATUS[VALID_VARIABLE], VARIABLE_STATUS[MISSING_VARIABLE_VALUE]]:
                        del data_to_upload[index][field_name]

        if data_to_upload:
            result = [
                {
                    **data,
                    "data_status": current_status,
                } for data, current_status in zip(data_to_upload, data_status)
            ]

        return result

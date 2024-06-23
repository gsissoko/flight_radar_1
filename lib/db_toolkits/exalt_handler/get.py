import pandas as pd
import psycopg2

from lib.db_toolkits.exalt_handler import ADMIN_CONNEXION, INTERNAL_FIELDS
from lib.db_toolkits.utilities.processing_functions import process_filters, process_fields

DEC2FLOAT = psycopg2.extensions.new_type(
    psycopg2.extensions.DECIMAL.values,
    "DEC2FLOAT",
    lambda value, curs: float(value) if value is not None else None,
)
psycopg2.extensions.register_type(DEC2FLOAT)


class ExaltGetHandler:
    def __init__(
            self,
            connection: psycopg2.extensions.connection = ADMIN_CONNEXION,
            cursor: psycopg2.extensions.cursor = ADMIN_CONNEXION.cursor()
    ) -> None:
        self.__connection: psycopg2.extensions.connection = connection
        self.__cursor: psycopg2.extensions.cursor = cursor

    def get_properties(self, table_name: str, fields: list = None, filters: dict = None) -> list:
        """Retrieves properties (field values) from the database.

        Args:
            table_name (str): The name of the Postgres table to query.
            fields (list, optional): A list of specific fields to retrieve. If None, all
                fields will be returned. Defaults to None.
            filters (dict, optional): A dictionary containing filters to apply to the query.

        Returns:
            list: A list of dictionaries, where each dictionary represents a row
                containing the requested properties (field values).

        Raises:
            Exception: If there is an error during the database operation.

        """

        filters, filters_params = ("", []) if not filters else process_filters(filters)
        processed_fields = process_fields(fields)

        self.__cursor.execute(f"""SELECT {processed_fields} FROM {table_name} {filters}""", filters_params)

        return pd.DataFrame(
            self.__cursor.fetchall(), columns=[col.name for col in self.__cursor.description]
        ).to_dict("records")

    def get_mapping(self, table_name: str) -> dict:
        """Get the mapping of column names to data types for a given table.

        Args:
            table_name (str): Name of the table.

        Returns:
            dict: A dictionary mapping column names to their respective data types.

        Note:
            This method fetches column names and data types from the database schema.
        """
        schema: list = self.get_properties(
            table_name="information_schema.columns",
            fields=["column_name", "data_type"],
            filters={
                "table_name": {"eq": table_name},
                "table_schema": {"eq": "public"}
            }
        )

        return {
            data["column_name"]: data["data_type"] for data in schema if data["column_name"] not in INTERNAL_FIELDS
        }

    def get_last_indicator_result(self, indicator_name: str):
        """Retrieves the latest result computed for a given indicator
        Args:
            indicator_name (str): Name of the indicator.

        Returns:
            dict: dict containing data
        """
        indicator_result = {}
        query = f"""
        SELECT result 
        FROM indicator WHERE name = '{indicator_name}' 
        ORDER BY computation_timestamp DESC LIMIT 1
        """
        self.__cursor.execute(query)
        indicator = self.__cursor.fetchone()
        if indicator is not None:
            indicator_result = indicator[0]

        return indicator_result

    def get_last_data(self, table_name: str, timestamp_field: str = "creation_timestamp"):
        """Retrieves the latest data recorded in a given table
        Args:
            table_name (str): Name of the table.
            timestamp_field: time_field to use

        Returns:
            dict: dict containing data
        """
        last_data = {}
        query = f"SELECT * FROM {table_name} ORDER BY {timestamp_field} DESC LIMIT 1"
        self.__cursor.execute(query)
        data = self.__cursor.fetchone()
        if data is not None:
            fields = [desc[0] for desc in self.__cursor.description]
            last_data = dict(zip(fields, data))

        return last_data

VALID_VARIABLE = "valid"
INVALID_VARIABLE_TYPE = "invalid"
MISSING_VARIABLE_VALUE = "missing"
VARIABLE_STATUS = {
    MISSING_VARIABLE_VALUE: -1,
    INVALID_VARIABLE_TYPE: 0,
    VALID_VARIABLE: 1,
}

INTEGRITY_MAPPING = {
    "flight_id": {
        "validation": True
    },
    "origin_airport_name": {
        "validation": True
    },
    "origin_airport_long": {
        "validation": True
    },
    "origin_airport_lat": {
        "validation": True
    },
    "destination_airport_name": {
        "validation": True
    },
    "destination_airport_long": {
        "validation": True
    },
    "destination_airport_lat": {
        "validation": True
    }
}

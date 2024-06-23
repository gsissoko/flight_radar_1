def process_filters(filters: dict) -> tuple:
    """Transforms a dictionary of filters into a Postgres WHERE clause and parameters.

    Args:
        filters (dict): A dictionary representing the filters for the query.
            The structure is {field_name: {operator: value}}.
            * operator: The comparison operator (e.g., "eq", "gt", "lt")

    Returns:
        tuple: A tuple containing the where clause and a list of parameters to be used in the query.
    """
    operators: dict = {
        "eq": {"func": lambda x: x, "db_name": "="},
        "neq": {"func": lambda x: x, "db_name": "!="},
        "start": {"func": lambda x: f"{x}%", "db_name": "ILIKE"},
        "gt": {"func": lambda x: x, "db_name": ">"},
        "gte": {"func": lambda x: x, "db_name": ">="},
        "lte": {"func": lambda x: x, "db_name": "<="},
        "lt": {"func": lambda x: x, "db_name": "<"},
        "in": {"func": lambda x: tuple(x), "db_name": "in"},
    }

    mapping: list = []
    prefix: str = ""

    sql_query: str = "WHERE "
    sql_params: list = []
    for field, var_filters in filters.items():
        if field in mapping:
            field = f"{prefix}{field}"

        for operator, value in var_filters.items():
            if operator not in operators:
                raise ValueError(f"Operator '{operator}' is not supported.")
            if len(sql_params) > 0:
                sql_query += " AND "
            sql_query += f"{field} {operators[operator]['db_name']} %s"
            sql_params.append(operators[operator]['func'](value))

    return sql_query, sql_params


def process_fields(fields: list) -> str:
    """Transforms a list of fields into a comma-separated string for Postgresql queries.

    Args:
        fields (list): A list of field names to include in the query.

    Returns:
        str: A comma-separated string representing the selected fields for the Postgres query.
            If the list is empty, returns "*".
    """
    return "*" if not fields else ", ".join(fields)

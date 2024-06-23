import psycopg2


def create_connection(credential: dict) -> psycopg2.extensions.connection:
    """Establishes a connection to a Postgres database.

    This method uses psycopg2's connect method to create a connection to a Postgres database.
    The connection parameters are provided via the 'credential' dictionary.

    Parameters:
    credential (dict): A dictionary containing the following keys:
        - host (str): The hostname of the Postgres database.
        - dbname (str): The name of the database to connect to.
        - user (str): The username to authenticate with.
        - password (str): The password to authenticate with.
        - port (int): The port number to connect to.

    Returns:
    psycopg2.extensions.connection: A connection object representing the database connection.

    Raises:
    psycopg2.OperationalError: If the connection to the database could not be established.
    """
    return psycopg2.connect(
        host=credential["host"],
        dbname=credential["name"],
        user=credential["user"],
        password=credential["password"],
        port=credential["port"]
    )

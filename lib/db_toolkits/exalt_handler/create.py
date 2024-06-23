import psycopg2

from lib.db_toolkits.exalt_handler import TABLES, ADMIN_CONNEXION
from lib.db_toolkits.utilities.table_mappings import MAPPINGS


class ExaltCreateHandler:
    def __init__(
            self,
            connection: psycopg2.extensions.connection = ADMIN_CONNEXION,
            cursor: psycopg2.extensions.cursor = ADMIN_CONNEXION.cursor()
    ) -> None:
        self.__connection: psycopg2.extensions.connection = connection
        self.__cursor: psycopg2.extensions.cursor = cursor
        self.authorized_tables = TABLES

    def __create_table(self, table_name: str) -> dict:
        """Creates a new table named 'airport' in the database if it does not already exist.

        Args:
            table_name (str): The name of the table to create.

        Returns:
            dict: A dictionary containing the response status and message.

        Raises:
            psycopg2.Error: If the table creation fails.
        """
        mapping = MAPPINGS[table_name]
        fields = ", ".join([f"{field_name} {field_type}" for field_name, field_type in mapping.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name}({fields});"
        self.__cursor.execute(query)

        return {
            "status": "success",
            "message": "New table successfully created.",
            "table_name": table_name
        }

    def process(self):
        """Initializes the database and creates all tables needed.

        Returns:
            dict: A dictionary containing the response status and message.

        """
        try:
            [self.__create_table(table_name) for table_name in self.authorized_tables]
            self.__connection.commit()
            result = {
                "status": "success",
                "message": "Database successfully initialized.",
                "tables": self.authorized_tables
            }
        except Exception as e:
            result = {
                "status": "error",
                "message": f"Error occurred during database initialization: {str(e)}"
            }

        self.__cursor.close()
        self.__connection.close()

        return result

import psycopg2
from psycopg2 import sql, DatabaseError
from psycopg2.extras import Json

from lib.db_toolkits.exalt_handler import ADMIN_CONNEXION
from lib.utilities.exceptions import AddException


class ExaltAddHandler:
    def __init__(
            self,
            connection: psycopg2.extensions.connection = ADMIN_CONNEXION,
            cursor: psycopg2.extensions.cursor = ADMIN_CONNEXION.cursor()
    ) -> None:
        self.__connection: psycopg2.extensions.connection = connection
        self.__cursor: psycopg2.extensions.cursor = cursor

    def process(self, table_name: str, data: list) -> dict:
        """
        Add new data to the specified table in the database

        Args:
            table_name (str): The name of the table to be used.
            data (list): List of dictionaries containing the data to be added to the table.

        Returns:
            dict: A dictionary containing the response status and message.

        Raises:
            AddException: If an error occurs while adding a new record to the database.
        """
        if not data:
            raise AddException("No data is provided")

        try:
            # Rollback current transaction
            self.__cursor.execute("ROLLBACK;")
            self.__connection.commit()

            # Extract columns from the first dictionary in the list
            columns = list(col.lower() for col in data[0].keys())

            # Create a list of SQL placeholders
            placeholders = sql.SQL(', ').join(sql.Placeholder() * len(columns))

            # Build the SQL query for inserting multiple rows
            insert_query = sql.SQL(
                "INSERT INTO {} ({}) VALUES {} RETURNING id"
            ).format(
                sql.Identifier(table_name),
                sql.SQL(", ").join([sql.Identifier(col) for col in columns]),
                sql.SQL(', ').join(sql.SQL('({})').format(placeholders) for _ in data)
            )

            # Flatten the list of values from all dictionaries
            values = [
                Json(value) if isinstance(value, dict) else value
                for record in data for value in record.values()
            ]

            # Execute the query
            self.__cursor.execute(insert_query, values)
            self.__connection.commit()

            # Fetch all returned IDs
            inserted_ids = [row[0] for row in self.__cursor.fetchall()]

            return {
                "status": "success",
                "message": f"New records successfully added to {table_name}.",
                "ids": inserted_ids
            }

        except Exception as e:
            self.__connection.rollback()
            raise AddException(f"An error occurred while adding data to the table {table_name}: {str(e)}")

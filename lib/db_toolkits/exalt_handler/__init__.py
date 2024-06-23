from lib.db_toolkits.utilities import create_connection

ADMIN_CREDENTIAL = {
    "name": "exalt_fr_db",
    "host": "localhost",
    "user": "my_exalt_user",
    "password": "myExaltPwd",
    "port": 5432
}

ADMIN_CONNEXION = create_connection(ADMIN_CREDENTIAL)
TABLES = ["flight", "indicator"]
INTERNAL_FIELDS = ["id", "latest_update", "data_status"]

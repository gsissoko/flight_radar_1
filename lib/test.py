import logging
from datetime import datetime

from dateutil import parser

from data_upload.flight_data import FlightDataUploader
from db_toolkits.exalt_handler import ADMIN_CREDENTIAL
from db_toolkits.exalt_handler.create import ExaltCreateHandler

from lib.indicators.processor import IndicatorProcessor


# exalt = ExaltCreateHandler()
# print(exalt.process())


# start = datetime.now()
# print(FlightDataUploader().process())
# print("Time taken: ", datetime.now() - start)

start = datetime.now()
print(IndicatorProcessor().get_airport_with_largest_flights_difference())
print("Time taken: ", datetime.now() - start)


# scheduler = JobHandler()

# params = {
#     "value": 5*60,
#     "initial_date": "2024-06-21T08:57:00+02:00",
#     "description": "Extractor - cron 3"
# }
#
# print(scheduler.start_scheduler())
# # scheduler.add_job(params, "indicator")
# # scheduler.add_job(params, "data_upload")
# print(scheduler.get_jobs())
# # while True:
# #     print(scheduler.get_jobs())
# print(scheduler.remove_all_jobs())

# body = {
# }
# exalt = ExaltCreateHandler()
# exalt.process()
# default_initial_date = (datetime.utcnow() + datetime.timedelta(minutes=2)).replace(tzinfo=datetime.timezone.utc)
# default_initial_date = default_initial_date.isoformat(timespec='seconds')
# flight_job_initial_date = body.get("initial_date", default_initial_date)
# indicator_job_initial_date = (parser.parse(flight_job_initial_date) + datetime.timedelta(minutes=5))
# indicator_job_initial_date = indicator_job_initial_date.isoformat(timespec='seconds')
# flight_job_frequency = body.get("upload_frequency", 1800)
# indicator_job_frequency = body.get("computation_frequency", 1800)

# flight_job_result = JOB_HANDLER.add_job(
#     parameters={
#         "value": flight_job_frequency,
#         "initial_date": flight_job_initial_date,
#         "description": "Flight data upload"
#     },
#     job_name="data_upload"
# )
# if flight_job_result.get("status") == "success":
#     indicator_job_result = JOB_HANDLER.add_job(
#         parameters={
#             "value": indicator_job_frequency,
#             "initial_date": indicator_job_initial_date,
#             "description": "Indicators computation"
#         },
#         job_name="indicator"
#     )


# import psycopg2

# def kill_all_connections(credentials):
#     dbname = credentials["name"]
#     user = credentials["user"]
#     password = credentials["password"]
#     try:
#         # Connect to the database
#         conn = psycopg2.connect(dbname=dbname, user=user, password=password)

#         # Open a cursor to perform database operations
#         cur = conn.cursor()

#         # Query active connections
#         cur.execute("SELECT pid, usename, query FROM pg_stat_activity WHERE datname = current_database() AND state = 'active'")

#         rows = cur.fetchall()

#         # Print information about active connections
#         print("Active connections:")
#         for row in rows:
#             print(f"PID: {row[0]}, User: {row[1]}, Query: {row[2]}")

#         # Terminate each connection
#         for row in rows:
#             pid = row[0]
#             print(f"Terminating PID {pid}")
#             cur.execute(f"SELECT pg_terminate_backend({pid})")

#         # Commit the changes
#         conn.commit()

#     except psycopg2.Error as e:
#         print(f"Error: {e}")
#         conn.rollback()

#     finally:
#         # Close cursor and connection
#         cur.close()
#         conn.close()


#kill_all_connections(ADMIN_CREDENTIAL)

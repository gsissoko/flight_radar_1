from datetime import datetime

import psycopg2

from db_toolkits.exalt_handler.get import ExaltGetHandler
from indicators import INDICATORS
from lib.db_toolkits.exalt_handler import ADMIN_CREDENTIAL
from lib.db_toolkits.exalt_handler.add import ExaltAddHandler
from lib.db_toolkits.utilities import create_connection
from lib.utilities.exceptions import ProcessingException, AddException


class IndicatorProcessor:
    def __init__(self):
        self.__execution_date = datetime.utcnow().isoformat()
        connection = create_connection(ADMIN_CREDENTIAL)
        self.__connection: psycopg2.extensions.connection = connection
        self.__cursor: psycopg2.extensions.cursor = connection.cursor()
        if not ExaltGetHandler(self.__connection, self.__cursor).get_last_data(
                table_name="flight", timestamp_field="latest_update"
        ):
            raise ProcessingException("Unable to compute indicators: No flight data available.")

        self.__exalt_add = ExaltAddHandler(self.__connection, self.__cursor)
        self.__indicator_table = "indicator"
        self.__indicator_results = []

    def get_airline_with_most_live_flights(self):
        """
        Retrieves the airline with the most live flights from the database.

        Returns:
            dict: A dictionary containing the airline with the most live flights and the count of live flights.
        If an error occurs, returns a dictionary with an error message.
        """
        # SQL query to get the airline with the most live flights
        query = """
            SELECT airline, COUNT(*) AS live_flights
            FROM (
                SELECT DISTINCT ON (flight_id) flight_id, airline
                FROM flight
                WHERE live = TRUE
                ORDER BY flight_id, latest_update DESC
            ) AS latest_flights
            GROUP BY airline
            ORDER BY live_flights DESC
            LIMIT 1;
        """

        try:
            self.__cursor.execute(query)
            result = self.__cursor.fetchone()

            airline_dict = {}
            if result:
                airline, live_flights = result
                airline_dict = {"airline": airline, "live_flights": live_flights}

            self.__indicator_results.append(
                {
                    "computation_timestamp": self.__execution_date,
                    "name": "airline_with_most_live_flights",
                    "result": airline_dict,
                }
            )

            return airline_dict

        except psycopg2.Error as e:
            raise ProcessingException(f"Error during indicator computation: {str(e)}")

    def get_airline_with_most_regional_flights_per_continent(self):
        """
        Retrieves the airline with the most regional (same continent) live flights for each continent.

        Returns:
            dict: A dictionary where each key is a continent and the value is another dictionary
                  containing the airline with the most regional flights and the count of those flights.
        If an error occurs, returns a dictionary with an error message.
        """
        # SQL query to get the airline with the most regional flights per continent
        query = """
            WITH latest_flights AS (
                SELECT DISTINCT ON (f.flight_id) 
                    f.flight_id, 
                    f.airline, 
                    f.origin_airport_continent AS origin_zone, 
                    f.destination_airport_continent AS destination_zone
                FROM flight f
                WHERE f.live = TRUE
                ORDER BY f.flight_id, f.latest_update DESC
            ), regional_flights AS (
                SELECT 
                    origin_zone,
                    airline,
                    COUNT(CASE WHEN origin_zone = destination_zone THEN 1 END) AS regional_flights_count
                FROM latest_flights
                GROUP BY origin_zone, airline
            ), ranked_airlines AS (
                SELECT 
                    origin_zone,
                    airline,
                    regional_flights_count,
                    ROW_NUMBER() OVER (PARTITION BY origin_zone ORDER BY regional_flights_count DESC) AS rn
                FROM regional_flights
            )
            SELECT 
                r.origin_zone AS continent,
                r.airline,
                r.regional_flights_count AS live_flights
            FROM ranked_airlines r
            WHERE rn = 1;
        """

        try:
            self.__cursor.execute(query)
            results = self.__cursor.fetchall()

            # Process results into a dictionary
            continent_airline_dict = {}
            for result in results:
                continent, airline, live_flights = result
                continent_airline_dict[continent] = {
                    "airline": airline,
                    "live_flights": live_flights
                }
                if continent_airline_dict.get('None'):
                    del continent_airline_dict['None']

            self.__indicator_results.append(
                {
                    "computation_timestamp": self.__execution_date,
                    "name": "airline_with_most_regional_flights_per_continent",
                    "result": continent_airline_dict,
                }
            )

            return continent_airline_dict

        except psycopg2.Error as e:
            raise ProcessingException(f"Error during indicator computation: {str(e)}")

    def get_longest_ongoing_flight(self):
        """
        Retrieves the longest ongoing flight based on the distance between the origin and destination airports.

        Returns:
            dict: A dictionary containing details of the longest ongoing flight.
        If an error occurs, returns a dictionary with an error message.
        """
        # SQL query to get the longest ongoing flight
        query = """
            WITH latest_flights AS (
                SELECT DISTINCT ON (f.flight_id)
                    f.flight_id,
                    f.callsign,
                    f.airline,
                    f.origin_airport_name,
                    f.origin_airport_lat,
                    f.origin_airport_long,
                    f.destination_airport_name,
                    f.destination_airport_lat,
                    f.destination_airport_long,
                    f.latest_update,
                    (
                        6371 * acos(
                            cos(radians(f.origin_airport_lat)) * cos(radians(f.destination_airport_lat)) *
                            cos(radians(f.destination_airport_long) - radians(f.origin_airport_long)) +
                            sin(radians(f.origin_airport_lat)) * sin(radians(f.destination_airport_lat))
                        )
                    ) AS distance_km
                FROM flight f
                WHERE f.live = TRUE
                AND f.origin_airport_lat IS NOT NULL
                AND f.origin_airport_long IS NOT NULL
                AND f.destination_airport_lat IS NOT NULL
                AND f.destination_airport_long IS NOT NULL
                ORDER BY f.flight_id, f.latest_update DESC
            )
            SELECT
                flight_id,
                callsign,
                airline,
                origin_airport_name,
                destination_airport_name,
                distance_km
            FROM latest_flights
            ORDER BY distance_km DESC
            LIMIT 1;
        """

        try:
            self.__cursor.execute(query)
            result = self.__cursor.fetchone()
            longest_flight = {}
            if result:
                longest_flight = {
                    col.name: value for col, value in zip(self.__cursor.description, result)
                }

            self.__indicator_results.append(
                {
                    "computation_timestamp": self.__execution_date,
                    "name": "longest_ongoing_flight",
                    "result": longest_flight,
                }
            )

            return longest_flight

        except psycopg2.Error as e:
            raise ProcessingException(f"Error during indicator computation: {str(e)}")

    def get_average_flight_length_per_continent(self):
        """
        Retrieves the average flight length for each continent.

        Returns:
            dict: A dictionary where each key is a continent and the value is the average flight length in kilometers.
        If an error occurs, returns a dictionary with an error message.
        """
        # SQL query for the average flight length by continent
        query = """
            WITH latest_flights AS (
                SELECT DISTINCT ON (f.flight_id)
                    f.flight_id,
                    f.origin_airport_continent,
                    f.destination_airport_continent,
                    (
                        6371 * acos(
                            cos(radians(f.origin_airport_lat)) * cos(radians(f.destination_airport_lat)) *
                            cos(radians(f.destination_airport_long) - radians(f.origin_airport_long)) +
                            sin(radians(f.origin_airport_lat)) * sin(radians(f.destination_airport_lat))
                        )
                    ) AS distance_km
                FROM flight f
                WHERE f.live = TRUE
                AND f.origin_airport_lat IS NOT NULL
                AND f.origin_airport_long IS NOT NULL
                AND f.destination_airport_lat IS NOT NULL
                AND f.destination_airport_long IS NOT NULL
                ORDER BY f.flight_id, f.latest_update DESC
            )
            SELECT
                origin_airport_continent AS continent,
                AVG(distance_km) AS average_flight_length_km
            FROM latest_flights
            GROUP BY origin_airport_continent;
        """
        try:

            self.__cursor.execute(query)
            results = self.__cursor.fetchall()
            continent_avg_length_dict = {}
            for result in results:
                continent, avg_length = result
                continent_avg_length_dict[continent] = avg_length

            self.__indicator_results.append(
                {
                    "computation_timestamp": self.__execution_date,
                    "name": "average_flight_length_per_continent",
                    "result": continent_avg_length_dict,
                }
            )

            return continent_avg_length_dict

        except psycopg2.Error as e:
            raise ProcessingException(f"Error during indicator computation: {str(e)}")

    def get_manufacturer_with_most_active_flights(self):
        """
        Retrieves the aircraft manufacturer with the most active flights.

        Returns:
            dict: A dictionary containing the manufacturer with the most active flights and the count of active flights.
                  If an error occurs, returns a dictionary with an error message.
        """
        # SQL query for aircraft manufacturer with the most active flights

        query = """
            WITH latest_flights AS (
                SELECT DISTINCT ON (f.flight_id)
                    f.flight_id,
                    f.aircraft_manufacturer
                FROM flight f
                WHERE f.live = TRUE
                AND f.aircraft_manufacturer IS NOT NULL
                ORDER BY f.flight_id, f.latest_update DESC
            )
            SELECT
                lf.aircraft_manufacturer,
                COUNT(*) AS active_flights
            FROM latest_flights lf
            GROUP BY lf.aircraft_manufacturer
            ORDER BY active_flights DESC
            LIMIT 1;
        """
        try:
            self.__cursor.execute(query)
            result = self.__cursor.fetchone()
            manufacturer_dict = {}
            if result:
                manufacturer, active_flights = result
                manufacturer_dict = {"manufacturer": manufacturer, "active_flights": active_flights}

            self.__indicator_results.append(
                {
                    "computation_timestamp": self.__execution_date,
                    "name": "manufacturer_with_most_active_flights",
                    "result": manufacturer_dict,
                }
            )

            return manufacturer_dict

        except psycopg2.Error as e:
            return ProcessingException(f"Error during indicator computation: {str(e)}")

    def get_top_aircraft_models_per_airline(self, nb_tops: int = 3):
        """
        Retrieves the top n aircraft models in use for each airline.

        Returns:
            dict: A dictionary where each key is an airline and the value is a list of dictionaries,
              each containing an aircraft model and its usage count.
        """
        # SQL query for top n aircraft models in use for each airline.
        query = """
            WITH latest_flights AS (
                SELECT DISTINCT ON (f.flight_id)
                    f.flight_id,
                    f.aircraft_model_text,
                    f.airline
                FROM flight f
                WHERE f.live = TRUE
                AND f.airline IS NOT NULL
                AND f.aircraft_model_text IS NOT NULL
                ORDER BY f.flight_id, f.latest_update DESC
            ), model_usage AS (
                SELECT
                    lf.airline,
                    lf.aircraft_model_text,
                    COUNT(*) AS usage_count
                FROM latest_flights lf
                GROUP BY lf.airline, lf.aircraft_model_text
            ), ranked_models AS (
                SELECT
                    mu.airline,
                    mu.aircraft_model_text,
                    mu.usage_count,
                    ROW_NUMBER() OVER (PARTITION BY mu.airline ORDER BY mu.usage_count DESC) AS rn
                FROM model_usage mu
            )
            SELECT
                rm.airline,
                rm.aircraft_model_text,
                rm.usage_count
            FROM ranked_models rm
            WHERE rm.rn <= %s;
        """

        try:
            self.__cursor.execute(query, (nb_tops,))
            results = self.__cursor.fetchall()

            airline_models_dict = {}
            for result in results:
                airline, model, usage_count = result
                if airline not in airline_models_dict:
                    airline_models_dict[airline] = []
                airline_models_dict[airline].append({
                    "model": model,
                    "usage_count": usage_count
                })

            self.__indicator_results.append(
                {
                    "computation_timestamp": self.__execution_date,
                    "name": "top_aircraft_models_per_airline",
                    "result": airline_models_dict,
                }
            )

            return airline_models_dict

        except psycopg2.Error as e:
            return ProcessingException(f"Error during indicator computation: {str(e)}")

    def get_airport_with_largest_flights_difference(self):
        """
        Retrieves the airport with the largest difference between outgoing and incoming flights.

        Returns:
            dict: A dictionary containing details of the airport with the largest flights difference.
                  Includes airport name, IATA code, and the flights difference.
        """
        # SQL query for airport with the largest difference between outgoing and incoming flight
        query = """
            WITH departures AS (
            SELECT
                origin_airport_iata AS airport_iata,
                origin_airport_name AS airport_name,
                COUNT(*) AS departure_count
            FROM flight
            WHERE live = TRUE
            AND origin_airport_iata IS NOT NULL
            GROUP BY origin_airport_iata, origin_airport_name
        ), arrivals AS (
            SELECT
                destination_airport_iata AS airport_iata,
                destination_airport_name AS airport_name,
                COUNT(*) AS arrival_count
            FROM flight
            WHERE live = TRUE
            AND destination_airport_iata IS NOT NULL
            GROUP BY destination_airport_iata, destination_airport_name
        )
        SELECT
            COALESCE(dep.airport_iata, arr.airport_iata) AS airport_iata,
            COALESCE(dep.airport_name, arr.airport_name, 'Unknown') AS airport_name,
            COALESCE(dep.departure_count, 0) AS departure_count,
            COALESCE(arr.arrival_count, 0) AS arrival_count,
            COALESCE(dep.departure_count, 0) - COALESCE(arr.arrival_count, 0) AS flights_difference
        FROM departures dep
        FULL OUTER JOIN arrivals arr ON dep.airport_iata = arr.airport_iata
        ORDER BY flights_difference DESC
        LIMIT 1;
        """

        try:
            self.__cursor.execute(query)
            result = self.__cursor.fetchone()
            airport = {}
            if result:
                airport = {
                    col.name: value for col, value in zip(self.__cursor.description, result)
                }

            self.__indicator_results.append(
                {
                    "computation_timestamp": self.__execution_date,
                    "name": "airport_with_largest_flights_difference",
                    "result": airport,
                }
            )

            return airport

        except psycopg2.Error as e:
            return {"error": f"Database error: {str(e)}"}

    def process(self):
        try:
            [getattr(self, f"get_{indicator}")() for indicator in INDICATORS]

            result = self.__exalt_add.process("indicator", self.__indicator_results)

            self.__cursor.close()
            self.__connection.close()

            if result.get("status") == "success":
                return {
                    "status": "success",
                    "message": "indicators successfully processed."
                }
            else:
                return {
                    "status": "error",
                    "message": "Error occurred during indicators processing."
                }
                
        except AddException as e:
            self.__cursor.close()
            self.__connection.close()

            return {"status": "error", "message": str(e)}

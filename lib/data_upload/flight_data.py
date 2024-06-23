from datetime import datetime, timezone

import requests
from FlightRadar24.api import FlightRadar24API
from FlightRadar24.errors import CloudflareError

from lib.data_upload.data_validation import DataValidator
from lib.db_toolkits.exalt_handler import ADMIN_CREDENTIAL
from lib.db_toolkits.exalt_handler.add import ExaltAddHandler
from lib.db_toolkits.utilities import create_connection


class FlightDataUploader:
    def __init__(self):
        self.__fr_api = FlightRadar24API()
        self.__connexion = create_connection(ADMIN_CREDENTIAL)
        self.__cursor = self.__connexion.cursor()
        self.__exalt_add = ExaltAddHandler(self.__connexion, self.__cursor)
        self.__flight_data = self._set_flight_data()

    def _set_flight_data(self):
        flight_data = []
        flights = self.__fr_api.get_flights()
        # flights = [flights[i] for i in range(1100, 1105)]
        for flight in flights:
            try:
                current_flight = self.__fr_api.get_flight_details(flight)
                if current_flight.get("identification"):
                    flight_id = current_flight["identification"].get("id")
                    callsign = current_flight["identification"].get("callsign")
                    live = current_flight.get("status", {}).get("live")

                    aircraft_model = current_flight.get("aircraft", {}).get("model", {})
                    aircraft_model_code = aircraft_model.get("code")
                    aircraft_model_text = aircraft_model.get("text")
                    aircraft_manufacturer = None
                    if aircraft_model_text:
                        aircraft_manufacturer = aircraft_model_text.split(" ")[0]
                    airline = current_flight.get("airline").get("name") if current_flight.get("airline") else None

                    origin_airport = current_flight.get("airport", {}).get("origin", {})
                    origin_name = origin_airport.get("name") if origin_airport else None
                    origin_iata = origin_airport.get("code", {}).get("iata") if origin_airport else None
                    origin_icao = origin_airport.get("code", {}).get("icao") if origin_airport else None
                    origin_lat = origin_airport.get("position", {}).get("latitude") if origin_airport else None
                    origin_long = origin_airport.get("position", {}).get("longitude") if origin_airport else None
                    origin_country = origin_airport.get("position", {}).get("country", {}).get(
                        "name") if origin_airport else None
                    origin_timezone = origin_airport.get("timezone", {}).get("name") if origin_airport else None
                    if timezone:
                        origin_timezone = str(origin_timezone).split("/")[0]
                    origin_continent = origin_timezone

                    destination_airport = current_flight.get("airport", {}).get("destination", {})
                    destination_name = destination_airport.get("name") if destination_airport else None
                    destination_iata = destination_airport.get("code", {}).get("iata") if destination_airport else None
                    destination_icao = destination_airport.get("code", {}).get("icao") if destination_airport else None
                    destination_lat = destination_airport.get("position", {}).get(
                        "latitude") if destination_airport else None
                    destination_long = destination_airport.get("position", {}).get(
                        "longitude") if destination_airport else None
                    destination_country = destination_airport.get("position", {}).get("country", {}).get(
                        "name") if destination_airport else None
                    destination_timezone = destination_airport.get("timezone", {}).get(
                        "name") if destination_airport else None
                    if timezone:
                        destination_timezone = str(destination_timezone).split("/")[0]
                    destination_continent = destination_timezone

                    scheduled_time = current_flight.get("time", {}).get("scheduled", {})
                    scheduled_departure = datetime.fromtimestamp(
                        scheduled_time.get("departure"), timezone.utc
                    ).isoformat() if scheduled_time.get("departure") else None
                    scheduled_arrival = datetime.fromtimestamp(
                        scheduled_time.get("arrival"), timezone.utc
                    ).isoformat() if scheduled_time.get("arrival") else None

                    real_time = current_flight.get("time", {}).get("real", {})
                    real_departure = datetime.fromtimestamp(
                        real_time.get("departure"), timezone.utc
                    ).isoformat() if real_time.get("departure") else None
                    real_arrival = datetime.fromtimestamp(
                        real_time.get("arrival"), timezone.utc
                    ).isoformat() if real_time.get("arrival") else None

                    estimated_time = current_flight.get("time", {}).get("estimated", {})
                    estimated_departure = datetime.fromtimestamp(
                        estimated_time.get("departure"), timezone.utc
                    ).isoformat() if estimated_time.get("departure") else None
                    estimated_arrival = datetime.fromtimestamp(
                        estimated_time.get("arrival"), timezone.utc
                    ).isoformat() if estimated_time.get("arrival") else None
                    first_timestamp = datetime.fromtimestamp(
                        current_flight.get("firstTimestamp"), timezone.utc
                    ).isoformat() if current_flight.get("firstTimestamp") else None

                    # Prepare data for insertion
                    flight_data.append({
                        "flight_id": flight_id,
                        "callsign": callsign,
                        "live": live,
                        "aircraft_model_code": aircraft_model_code,
                        "aircraft_model_text": aircraft_model_text,
                        "aircraft_manufacturer": aircraft_manufacturer,
                        "airline": airline,
                        "origin_airport_name": origin_name,
                        "origin_airport_iata": origin_iata,
                        "origin_airport_icao": origin_icao,
                        "origin_airport_lat": origin_lat,
                        "origin_airport_long": origin_long,
                        "origin_airport_country": origin_country,
                        "origin_airport_continent": origin_continent,
                        "destination_airport_name": destination_name,
                        "destination_airport_iata": destination_iata,
                        "destination_airport_icao": destination_icao,
                        "destination_airport_lat": destination_lat,
                        "destination_airport_long": destination_long,
                        "destination_airport_country": destination_country,
                        "destination_airport_continent": destination_continent,
                        "scheduled_departure": scheduled_departure,
                        "scheduled_arrival": scheduled_arrival,
                        "real_departure": real_departure,
                        "real_arrival": real_arrival,
                        "estimated_departure": estimated_departure,
                        "estimated_arrival": estimated_arrival,
                        "first_timestamp": first_timestamp
                    })
            except requests.exceptions.HTTPError:
                # Log error
                pass
            except CloudflareError:
                # LOG error for flight which required money
                pass

        return flight_data

    def process(self):
        validated_data = DataValidator(self.__flight_data).process()
        result = self.__exalt_add.process(table_name="flight", data=validated_data)

        self.__cursor.close()
        self.__connexion.close()

        if result.get("status") == "success":
            return {
                "status": "success",
                "message": "flight data successfully uploaded.",
                "nb_data": len(result.get("ids"))
            }
        else:
            return {
                "status": "error",
                "message": "Internal error occurred during flight data uploading."
            }


AIRPORT_MAPPING = {
    "id": "VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()",
    "creation_timestamp": "TIMESTAMP WITH TIME ZONE default NOW()",
    "name": "VARCHAR NOT NULL",
    "iata": "VARCHAR NOT NULL",
    "icao": "VARCHAR NOT NULL",
    "lat": "NUMERIC NOT NULL",
    "lon": "NUMERIC NOT NULL",
    "country": "VARCHAR NOT NULL",
    "alt": "NUMERIC NOT NULL"
}

AIRLINE_MAPPING = {
    "id": "VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()",
    "creation_timestamp": "TIMESTAMP WITH TIME ZONE default NOW()",
    "name": "VARCHAR NOT NULL",
    "code": "VARCHAR",
    "icao": "VARCHAR NOT NULL"
}

ZONE_MAPPING = {
    "id": "VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()",
    "creation_timestamp": "TIMESTAMP WITH TIME ZONE default NOW()",
    "name": "VARCHAR NOT NULL",
    "tl_y": "NUMERIC NOT NULL",
    "tl_x": "NUMERIC NOT NULL",
    "br_y": "VARCHAR NOT NULL",
    "br_x": "VARCHAR NOT NULL",
}

COUNTRY_MAPPING = {
    "id": "VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()",
    "creation_timestamp": "TIMESTAMP WITH TIME ZONE default NOW()",
    "name": "VARCHAR NOT NULL",
    "zone": "VARCHAR NOT NULL REFERENCES zone(id) ON DELETE CASCADE",
    "tl_y": "NUMERIC NOT NULL",
    "tl_x": "NUMERIC NOT NULL",
    "br_y": "VARCHAR NOT NULL",
    "br_x": "VARCHAR NOT NULL",
}

SUB_ZONE_MAPPING = {
    "id": "VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()",
    "creation_timestamp": "TIMESTAMP WITH TIME ZONE default NOW()",
    "name": "VARCHAR NOT NULL",
    "zone": "VARCHAR NOT NULL REFERENCES country(id) ON DELETE CASCADE",
    "tl_y": "NUMERIC NOT NULL",
    "tl_x": "NUMERIC NOT NULL",
    "br_y": "VARCHAR NOT NULL",
    "br_x": "VARCHAR NOT NULL",
}

FLIGHT_MAPPING = {
    "id": "SERIAL PRIMARY KEY",
    "latest_update": "TIMESTAMP WITH TIME ZONE default NOW()",
    "data_status": "JSONB",
    "flight_id": "VARCHAR(255)",
    "callsign": "VARCHAR(255)",
    "live": "BOOLEAN",
    "aircraft_model_code": "VARCHAR(50)",
    "aircraft_model_text": "VARCHAR(255)",
    "aircraft_manufacturer": "VARCHAR(255)",
    "airline": "VARCHAR(255)",
    "origin_airport_name": "VARCHAR(255)",
    "origin_airport_iata": "VARCHAR(10)",
    "origin_airport_icao": "VARCHAR(10)",
    "origin_airport_lat": "NUMERIC",
    "origin_airport_long": "NUMERIC",
    "origin_airport_country": "VARCHAR(255)",
    "origin_airport_continent": "VARCHAR(255)",
    "destination_airport_name": "VARCHAR(255)",
    "destination_airport_iata": "VARCHAR(10)",
    "destination_airport_icao": "VARCHAR(10)",
    "destination_airport_lat": "NUMERIC",
    "destination_airport_long": "NUMERIC",
    "destination_airport_country": "VARCHAR(255)",
    "destination_airport_continent": "VARCHAR(255)",
    "scheduled_departure": "TIMESTAMP WITH TIME ZONE",
    "scheduled_arrival": "TIMESTAMP WITH TIME ZONE",
    "real_departure": "TIMESTAMP WITH TIME ZONE",
    "real_arrival": "TIMESTAMP WITH TIME ZONE",
    "estimated_departure": "TIMESTAMP WITH TIME ZONE",
    "estimated_arrival": "TIMESTAMP WITH TIME ZONE",
    "first_timestamp": "TIMESTAMP WITH TIME ZONE"
}

INDICATOR_MAPPING = {
    "id": "SERIAL PRIMARY KEY",
    "computation_timestamp": "TIMESTAMP WITH TIME ZONE default NOW()",
    "name": "VARCHAR(255)",
    "result": "JSONB",
}

MAPPINGS = {
    "airport": AIRPORT_MAPPING,
    "airline": AIRLINE_MAPPING,
    "zone": ZONE_MAPPING,
    "country": COUNTRY_MAPPING,
    "sub_zone": SUB_ZONE_MAPPING,
    "flight": FLIGHT_MAPPING,
    "indicator": INDICATOR_MAPPING

}

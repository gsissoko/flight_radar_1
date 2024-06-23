from flask import jsonify

from backend.app.endpoints import bp
from backend.app.endpoints.utilities import INDICATORS_TO_COMPUTE
from db_toolkits.exalt_handler import ADMIN_CREDENTIAL
from db_toolkits.exalt_handler.get import ExaltGetHandler
from db_toolkits.utilities import create_connection


@bp.route("/indicators/<string:indicator>", methods=["GET"])
def compute(indicator: str):
    try:
        if INDICATORS_TO_COMPUTE.get(indicator):
            connection = create_connection(ADMIN_CREDENTIAL)
            result = ExaltGetHandler(connection, connection.cursor()).get_last_indicator_result(
                indicator_name=INDICATORS_TO_COMPUTE.get(indicator)
            )
            connection.close()

            return jsonify(result), 200

        else:
            return jsonify({"message": "Unknown indicator", "status": "error"}), 501

    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500

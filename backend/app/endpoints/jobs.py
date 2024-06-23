from datetime import datetime, timedelta, timezone

from dateutil import parser
from flask import jsonify, request

from backend import JOB_HANDLER
from backend.app.endpoints import bp
from db_toolkits.exalt_handler.create import ExaltCreateHandler


@bp.route("/start", methods=["POST"])
def start():
    try:
        if JOB_HANDLER.get_jobs():
            return jsonify({"message": "Job already started", "status": "success"}), 200
        else:
            body = request.json
            exalt = ExaltCreateHandler()
            exalt.process()
            default_initial_date = (datetime.utcnow() + timedelta(minutes=2)).replace(tzinfo=timezone.utc)
            default_initial_date = default_initial_date.isoformat(timespec='seconds')
            flight_job_initial_date = body.get("initial_date", default_initial_date)
            indicator_job_initial_date = (parser.parse(flight_job_initial_date) + timedelta(minutes=5))
            indicator_job_initial_date = indicator_job_initial_date.isoformat(timespec='seconds')
            flight_job_frequency = body.get("upload_frequency", 1800)
            indicator_job_frequency = body.get("computation_frequency", 1800)

            flight_job_result = JOB_HANDLER.add_job(
                parameters={
                    "value": flight_job_frequency,
                    "initial_date": flight_job_initial_date,
                    "description": "Flight data upload"
                },
                job_name="data_upload"
            )
            if flight_job_result.get("status") == "success":
                indicator_job_result = JOB_HANDLER.add_job(
                    parameters={
                        "value": indicator_job_frequency,
                        "initial_date": indicator_job_initial_date,
                        "description": "Indicators computation"
                    },
                    job_name="indicator"
                )
                if indicator_job_result.get("status") == "success":
                    return jsonify({"message": "Job successfully started.", "status": "success"}), 201
                else:
                    JOB_HANDLER.remove_all_jobs()
                    return jsonify({"message": "Internal error occurred, try again.", "status": "error"}), 500

            else:
                return jsonify({"message": "Internal error occurred, try again.", "status": "error"}), 500

    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500


@bp.route("/stop", methods=["PUT"])
def stop():
    try:
        result = JOB_HANDLER.remove_all_jobs()
        if result.get("status") == "success":
            return jsonify({"message": "Job successfully stopped.", "status": "success"}), 200
        else:
            return jsonify({"message": "Internal error occurred, try again.", "status": "error"}), 500
    except Exception as e:
        return jsonify({"message": "Internal error occurred, try again.", "status": "error"}), 500


@bp.route("/jobs", methods=["GET"])
def retrieve():
    try:
        return jsonify(JOB_HANDLER.get_jobs()), 200
    except Exception as e:
        return jsonify({"message": "Internal error occurred, try again.", "status": "error"}), 500

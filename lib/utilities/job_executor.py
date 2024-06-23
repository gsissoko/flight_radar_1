import logging
from datetime import datetime

from lib.data_upload.flight_data import FlightDataUploader
from lib.indicators.processor import IndicatorProcessor
from utilities.log_handler import setup_logger


def job_executor(job_name: str):
    info_logger = setup_logger('job_result_logger', 'result.log')
    error_logger = setup_logger('job_error_logger', 'error.log', level=logging.ERROR)
    try:
        if job_name.lower() == "data_upload":
            result = FlightDataUploader().process()
        elif job_name.lower() == "indicator":
            result = IndicatorProcessor().process()
        else:
            result = {
                "status": "error",
                "message": "Unknown job type."
            }

    except Exception as e:
        result = {
            "status": "error",
            "message": f"Job execution interrupted: {str(e)}"
        }

    # Log infos
    if result["status"] == "success":
        info_logger.info(result)
    else:
        error_logger.error(result)

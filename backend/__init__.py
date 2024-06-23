from utilities.exceptions import JobException
from utilities.job_handler import JobHandler

JOB_HANDLER = JobHandler()
try:
    JOB_HANDLER.start_scheduler()
except JobException as e:
    # LOG INFOS
    pass

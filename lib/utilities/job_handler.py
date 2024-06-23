from datetime import datetime, timedelta
from typing import Callable

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import SchedulerAlreadyRunningError, SchedulerNotRunningError
from sqlalchemy import create_engine

from lib.db_toolkits.exalt_handler import ADMIN_CREDENTIAL
from lib.utilities.exceptions import JobException
from lib.utilities.job_executor import job_executor

SCHEDULING_JOB_STORE_TYPE = "default"


class JobHandler:
    def __init__(self):
        self.job_store = SCHEDULING_JOB_STORE_TYPE
        self.scheduler = BackgroundScheduler(
            jobstores={
                self.job_store: SQLAlchemyJobStore(
                    engine=create_engine(
                        (
                            f"postgresql://{ADMIN_CREDENTIAL['user']}:{ADMIN_CREDENTIAL['password']}"
                            f"@{ADMIN_CREDENTIAL['host']}/{ADMIN_CREDENTIAL['name']}"
                        )
                    )
                )
            }
        )

    def start_scheduler(self):
        try:
            self.scheduler.start()
        except SchedulerAlreadyRunningError:
            raise JobException("Scheduler is already running. Cannot start again.")
        except Exception as e:
            raise JobException(str(e))

        return {
            "status": "success",
            'message': "Scheduler successfully started."
        }

    def stop_scheduler(self):
        try:
            self.scheduler.shutdown(wait=True)
        except SchedulerNotRunningError:
            raise JobException("Scheduler is not running. Cannot stop.")
        except Exception as e:
            raise JobException(str(e))

        return {
            "status": "success",
            'message': "Scheduler successfully stopped."
        }

    def add_job(self, parameters: dict, job_name: str, job_func: Callable = job_executor):
        name = parameters.get("description", "exalt_job")
        initial_date = parameters.get("initial_date", datetime.now() + timedelta(seconds=30))
        self.scheduler.add_job(
            job_func, "interval", seconds=parameters["value"],
            name=name, jobstore=self.job_store,
            replace_existing=True, next_run_time=initial_date,
            args=[job_name]
        )

        return {
            "status": "success",
            'message': "New job successfully scheduled",
            "id": job_name
        }

    def pause_job(self, job_id):
        try:
            self.scheduler.pause_job(job_id)
        except Exception as e:
            raise JobException(str(e))

        return {
            "status": "success",
            'message': "Job successfully paused.",
            "id": job_id
        }

    def resume_job(self, job_id):
        try:
            self.scheduler.resume_job(job_id)
        except Exception as e:
            raise JobException(str(e))

        return {
            "status": "success",
            'message': "Job successfully restarted.",
            "id": job_id
        }

    def remove_job(self, job_id):
        try:
            self.scheduler.remove_job(job_id=job_id, jobstore=self.job_store)
        except Exception as e:
            raise JobException(str(e))

        return {
            "status": "success",
            'message': "Job successfully removed.",
            "id": job_id
        }

    def remove_all_jobs(self):
        scheduled_jobs = self.scheduler.get_jobs(jobstore=self.job_store)
        try:
            for job in scheduled_jobs:
                self.scheduler.remove_job(job_id=job.id, jobstore=self.job_store)
        except Exception as e:
            raise JobException(str(e))

        return {
            "status": "success",
            'message': "All jobs Job successfully removed."
        }

    def __get_job(self, job_id):
        job = self.scheduler.get_job(job_id=job_id, jobstore=self.job_store)
        return {
            "id": job.id,
            "next_execution_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "name": job.name
        } if job else {}

    def get_jobs(self):
        jobs = [{
            "id": job.id,
            "next_execution_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "name": job.name
        } for job in self.scheduler.get_jobs(jobstore=self.job_store)
        ]
        return jobs

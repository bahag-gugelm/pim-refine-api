from pydantic import BaseModel, Field
from typing import List


class CurrentScheduledJob(BaseModel):
    job_id: str = Field(title="The Job ID in APScheduler",description="The Job ID in APScheduler")
    run_frequency: str = Field(title="The Job Interval in APScheduler",description="The Job Interval in APScheduler")
    next_run: str = Field(title="Next Scheduled Run for the Job",description="Next Scheduled Run for the Job")
    class Config:
        schema_extra = {
             'example':   {
                "job_id": "periodic_task",
                "run_frequency": "interval[0:05:00]",
                "next_run": "2020-11-10 22:12:09.397935+10:00"
            }
        }

class CurrentScheduledJobsResponse(BaseModel):
    jobs:List[CurrentScheduledJob]       

class JobCreateDeleteResponse(BaseModel):
    scheduled: bool = Field(title="Whether the job was scheduler or not",description="Whether the job was scheduler or not")
    job_id: str = Field(title="The Job ID in APScheduler",description="The Job ID in APScheduler")
    class Config:
        schema_extra = {
                    'example':   {
                    "scheduled": True,
                    "job_id": "periodic_task"
                    }
        }

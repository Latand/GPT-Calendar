import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class ArgsAddTask(BaseModel):
    summary: str
    start: str = Field(..., format="%Y-%m-%d %H:%M:%S")
    end: str = Field(..., format="%Y-%m-%d %H:%M:%S")
    description: Optional[str] = Field(None)
    priority: str = Field(..., regex="^high|medium|low$")

    @validator("start")
    def start_to_datetime(cls, v):
        return datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S")

    @validator("end")
    def end_to_datetime(cls, v):
        return datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S")


class ArgsGetTasks(BaseModel):
    start: str = Field(..., format="%Y-%m-%d")
    end: str = Field(..., format="%Y-%m-%d")

    @validator("start")
    def start_to_datetime(cls, v):
        return datetime.datetime.strptime(v, "%Y-%m-%d").date()

    @validator("end")
    def end_to_datetime(cls, v):
        return datetime.datetime.strptime(v, "%Y-%m-%d").date()


class ArgsRearrangeTask(BaseModel):
    task_id: str
    start: str = Field(..., format="%Y-%m-%d %H:%M:%S")
    end: str = Field(..., format="%Y-%m-%d %H:%M:%S")

    @validator("start")
    def start_to_datetime(cls, v):
        return datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S")

    @validator("end")
    def end_to_datetime(cls, v):
        return datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S")


class ArgsDeleteTask(BaseModel):
    task_id: str

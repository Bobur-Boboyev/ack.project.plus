from datetime import date, datetime

from pydantic import BaseModel, Field


class CreateDailyReport(BaseModel):
    project_id: int
    task_id: int
    text: str = Field(default=None, max_length=5000)


class ReportResponse(BaseModel):
    id: int
    user_id: int
    task_id: int
    project_id: int
    text: str
    report_date: date
    created_at: datetime

    model_config = {"from_attributes": True}

from typing import Optional
from datetime import date, datetime
import enum

from pydantic import BaseModel, Field, ConfigDict
from fastapi import Query

from app.schemas.user import UserResponse
from app.schemas.task import TaskResponse
from app.schemas.project import ProjectResponse
from app.models import MonthlyReportStatus


class CreateDailyReport(BaseModel):
    project_id: int = Field(..., gt=0)
    task_id: int = Field(..., gt=0)
    text: str = Field(default=None, max_length=5000)
    report_date: date = Field(default_factory=date.today)  # ← qo'shing


class ReportResponse(BaseModel):
    id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    task_id: int = Field(..., gt=0)
    project_id: int = Field(..., gt=0)
    text: str
    report_date: date
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportDetailResponse(BaseModel):
    id: int
    user: UserResponse
    task: TaskResponse
    project: ProjectResponse
    text: str | None = None
    report_date: date
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateReportRequest(BaseModel):
    text: Optional[str] = Field(default=None, max_length=5000)


class MonthlyReportItem(BaseModel):
    report_id: int
    report_date: date
    text: Optional[str]


class MonthlyReportResponse(BaseModel):
    user_id: int
    project_id: int
    year: int
    month: int
    total_reports: int
    reports: list[MonthlyReportItem]


class MonthlyReportSubmitResponse(BaseModel):
    id: int
    user_id: int
    project_id: int
    year: int
    month: int
    total_reports: int
    submitted_at: datetime
    status: MonthlyReportStatus

    reports: list[ReportResponse] = []

    model_config = ConfigDict(from_attributes=True)



class DailyReportSortField(str, enum.Enum):
    id = "id"
    report_date = "report_date"
    created_at = "created_at"

class SortOrder(str, enum.Enum):
    asc = "asc"
    desc = "desc"


class DailyReportQueryParams:
    def __init__(
        self,
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1, le=100),
        search: str | None = Query(None),
        ids: list[int] = Query(default_factory=list),
        user_id: int | None = Query(None),
        project_ids: list[int] = Query(default_factory=list),
        task_id: int | None = Query(None),
        report_date: date | None = Query(None),
        report_date_from: date | None = Query(None),
        report_date_to: date | None = Query(None),
        created_from: datetime | None = Query(None),
        created_to: datetime | None = Query(None),
        sort_by: DailyReportSortField = Query(DailyReportSortField.created_at),
        order: SortOrder = Query(SortOrder.desc),
    ):
        self.page = page
        self.limit = limit
        self.search = search
        self.ids = ids
        self.user_id = user_id
        self.project_ids = project_ids
        self.task_id = task_id
        self.report_date = report_date
        self.report_date_from = report_date_from
        self.report_date_to = report_date_to
        self.created_from = created_from
        self.created_to = created_to
        self.sort_by = sort_by
        self.order = order
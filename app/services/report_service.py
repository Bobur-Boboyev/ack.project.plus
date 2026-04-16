from datetime import date
from fastapi import HTTPException, status

from app.repository.report_repo import ReportRepo
from app.repository.task_repo import TaskRepo
from app.repository.project_repo import ProjectRepo
from app.models import User
from app.schemas.report import CreateDailyReport


class ReportService:
    def __init__(self, db):
        self.db = db
        self.repo = ReportRepo(db)
        self.task_repo = TaskRepo(db)
        self.project_repo = ProjectRepo(db)

    def create_daily_report(self, user: User, data: CreateDailyReport):
        task = self.task_repo.get_by_id(data.task_id)

        if not task or task.project_id != data.project_id:
            raise HTTPException(400, "Invalid task for this project")

        if not self.project_repo.is_user_in_project(data.project_id, user.id):
            raise HTTPException(
                403,
                "You are not assigned to this project",
            )

        if not self.task_repo.get_assignment(data.task_id, user.id):
            raise HTTPException(
                403,
                "You are not assigned to this task",
            )

        if self.repo.exists(user.id, data.project_id, data.report_date):
            raise HTTPException(400, "Report already exists for this day")

        return self.repo.create(
            user_id=user.id,
            project_id=data.project_id,
            task_id=data.task_id,
            text=data.text,
        )

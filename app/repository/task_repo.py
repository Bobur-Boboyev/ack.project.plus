from sqlalchemy.orm import Session

from app.models import Task, TaskAssignment



class TaskRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_tasks_by_user(self, user_id: int) -> list[Task]:
        return (
            self.db.query(Task)
            .join(TaskAssignment, Task.id == TaskAssignment.task_id)
            .filter(TaskAssignment.user_id == user_id)
            .all()
        )
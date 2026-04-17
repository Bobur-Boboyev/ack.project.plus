from sqlalchemy.orm import Session

from app.models import Task, TaskAssignment, Project, TaskStatusHistory
from app.schemas.task import CreateTask


class TaskRepo:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs):
        task = Task(**kwargs)

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        return task

    def update(self, task: Task, data: dict):
        for key, value in data.items():
            setattr(task, key, value)

        self.db.commit()
        self.db.refresh(task)
        return task

    def get_tasks_by_user(self, user_id: int) -> list[Task]:
        return (
            self.db.query(Task)
            .join(Task.assignments)
            .filter(TaskAssignment.user_id == user_id)
            .all()
        )

    def get_all_tasks(self) -> list[Task]:
        return self.db.query(Task).all()

    def get_by_manager(self, manager_id: int) -> list[Task]:
        return (
            self.db.query(Task)
            .join(Project, Project.id == Task.project_id)
            .filter(Project.manager_id == manager_id)
            .all()
        )

    def get_by_id(self, task_id: int):
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_assignment(self, task_id: int, user_id: int):
        return (
            self.db.query(TaskAssignment)
            .filter(
                TaskAssignment.task_id == task_id,
                TaskAssignment.user_id == user_id,
            )
            .first()
        )

    def get_assignments(self, task_id: int):
        return (
            self.db.query(TaskAssignment)
            .filter(TaskAssignment.task_id == task_id)
            .all()
        )

    def assign_user(
        self, task_id: int, user_id: int, role_on_task: str, assigned_by: int
    ):
        assignment = TaskAssignment(
            task_id=task_id,
            user_id=user_id,
            role_on_task=role_on_task,
            assigned_by=assigned_by,
        )

        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)

        return assignment

    def unassign_user(self, task_id: int, user_id: int):
        self.db.query(TaskAssignment).filter(
            TaskAssignment.task_id == task_id,
            TaskAssignment.user_id == user_id,
        ).delete()

        self.db.commit()

    def add_status_history(self, task_id, old_status, new_status, changed_by):
        history = TaskStatusHistory(
            task_id=task_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
        )

        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)

    def get_status_history(self, task_id: int):
        return (
            self.db.query(TaskStatusHistory)
            .filter(TaskStatusHistory.task_id == task_id)
            .order_by(TaskStatusHistory.created_at.asc())
            .all()
        )

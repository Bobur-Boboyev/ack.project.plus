from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Task, TaskAssignment, Project, TaskStatusHistory, TaskStatus
from app.schemas.task import CreateTask, TaskSortField


class TaskRepo:
    def __init__(self, db: Session):
        self.db = db

    def filter_tasks(self, params, stmt=None):
        if stmt is None:
            stmt = self.db.query(Task)
        
        if params.search:
            stmt = stmt.filter(
                Task.title.ilike(f"%{params.search}%")
                | Task.description.ilike(f"%{params.search}%")
            )
        
        if params.project_id:
            stmt = stmt.filter(Task.project_id == params.project_id)
        
        if params.manager_id:
            stmt = stmt.join(Project, Project.id == Task.project_id).filter(
                Project.manager_id == params.manager_id
            )
        
        if params.worker_ids:
            stmt = stmt.join(TaskAssignment, TaskAssignment.task_id == Task.id).filter(
                TaskAssignment.user_id.in_(params.worker_ids)
            )
        
        if params.status:
            stmt = stmt.filter(Task.status.in_(params.status))
        
        if params.ids:
            stmt = stmt.filter(Task.id.in_(params.ids))

        if params.created_from:
            stmt = stmt.filter(Task.created_at >= params.created_from)
        
        if params.created_to:
            stmt = stmt.filter(Task.created_at <= params.created_to)
        
        if params.deadline_from:
            stmt = stmt.filter(Task.deadline >= params.deadline_from)
        
        if params.deadline_to:
            stmt = stmt.filter(Task.deadline <= params.deadline_to)
        
        if params.expired is not None:
            if params.expired:
                stmt = stmt.filter(Task.deadline < func.now(), Task.deadline.isnot(None), Task.status.notin_(TaskStatus.final_statuses()))
            else:
                stmt = stmt.filter(Task.deadline >= func.now())
            
        SORT_FIELDS = {
            TaskSortField.id: Task.id,
            TaskSortField.title: Task.title,
            TaskSortField.status: Task.status,
            TaskSortField.deadline: Task.deadline,
            TaskSortField.created_at: Task.created_at,
        }
        column = SORT_FIELDS[params.sort_by.value]

        stmt = stmt.order_by(column.asc() if params.order == "asc" else column.desc())
        stmt = stmt.offset((params.page - 1) * params.limit).limit(params.limit)

        return self.db.execute(stmt).scalars().all()

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

    def get_all_tasks(self, params) -> list[Task]:
        return self.filter_tasks(params)

    def get_by_manager(self, manager_id: int, params) -> list[Task]:
        stmt = (
            self.db.query(Task)
            .join(Project, Project.id == Task.project_id)
            .filter(Project.manager_id == manager_id)
            .all()
        )
        return self.filter_tasks(params, stmt)

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

        return history

    def get_status_history(self, task_id: int):
        return (
            self.db.query(TaskStatusHistory)
            .filter(TaskStatusHistory.task_id == task_id)
            .order_by(TaskStatusHistory.created_at.asc())
            .all()
        )

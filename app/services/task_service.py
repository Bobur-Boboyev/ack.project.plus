from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User, UserRole
from app.schemas.task import CreateTask, UpdateTask, AssignWorkerRequest
from app.repository.task_repo import TaskRepo
from app.repository.project_repo import ProjectRepo


class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.task_repo = TaskRepo(db)
        self.project_repo = ProjectRepo(db)

    def create_task(self, data: CreateTask, project_id: int):
        project = self.project_repo.get_project_by_id(project_id)

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        task = self.task_repo.create(
            project_id=project_id,
            title=data.title,
            description=data.description,
            deadline=data.deadline,
        )
        return task

    def update_task(self, task_id: int, data: UpdateTask, manager):
        task = self.task_repo.get_by_id(task_id)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        if task.project.manager_id != manager.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed",
            )

        update_data = data.model_dump(exclude_unset=True)

        if "status" in update_data:
            new_status = update_data["status"]

            if not task.status.can_transition(new_status):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status transition: {task.status} → {new_status}",
                )

        return self.task_repo.update(task, update_data)

    def update_task_status(self, task_id: int, data, user):
        task = self.task_repo.get_by_id(task_id)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        if not self.task_repo.get_assignment(task_id, user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to this task",
            )

        if task.status.is_final():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task already completed or canceled",
            )

        new_status = data.status

        if not task.status.can_transition(new_status):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status transition: {task.status} → {new_status}",
            )

        old_status = task.status

        task.status = new_status

        self.task_repo.add_status_history(
            task_id=task.id,
            old_status=old_status,
            new_status=new_status,
            changed_by=user.id,
        )

        return self.task_repo.update(task, {"status": new_status})

    def assign_worker(self, task_id: int, data: AssignWorkerRequest, manager: User):
        task = self.task_repo.get_by_id(task_id)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        if task.project.manager_id != manager.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed",
            )

        if self.task_repo.get_assignment(task_id, data.user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already assigned",
            )

        if task.status.is_final():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign worker to final task",
            )

        self.task_repo.assign_user(
            task_id=task_id,
            user_id=data.user_id,
            role_on_task=data.role_on_task,
            assigned_by=manager.id,
        )

        return task

    def unassign_worker(self, task_id: int, user_id: int, manager):
        task = self.task_repo.get_by_id(task_id)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        if task.project.manager_id != manager.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed",
            )

        if task.status.is_final():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify final task",
            )

        if not self.task_repo.get_assignment(task_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not assigned to this task",
            )

        self.task_repo.unassign_user(task_id, user_id)

        return task

    def get_task_assignments(self, task_id: int, user):
        task = self.task_repo.get_by_id(task_id)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        if task.project.manager_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed",
            )

        return self.task_repo.get_assignments(task_id)

    def get_tasks(self, user: User):
        if user.role == "admin":
            return self.task_repo.get_all_tasks()

        if user.role == "manager":
            return self.task_repo.get_by_manager(user.id)

        if user.role == "worker":
            return self.task_repo.get_tasks_by_user(user.id)

        return []

    def get_task(self, task_id: int, user: User):
        task = self.task_repo.get_by_id(task_id)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        if user.role == "admin":
            return task

        if user.role == "manager":
            if task.project.manager_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not allowed",
                )
            return task

        if user.role == "worker":
            is_assigned = self.task_repo.get_assignment(task.id, user.id)

            if not is_assigned:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not allowed",
                )

            return task
        
    def get_task_history(self, task_id: int, user: User):
        task = self.task_repo.get_by_id(task_id)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        if user.role == "admin":
            return self.task_repo.get_status_history(task_id)
        
        if user.role == "manager":
            if task.project.manager_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not allowed",
                )
            return self.task_repo.get_status_history(task_id)
        
        if user.role == "worker":
            if not self.task_repo.get_assignment(task_id, user.id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not allowed"
                )
            return self.task_repo.get_status_history(task_id)
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models import Base
from app.models.task import TaskStatus


class TaskStatusHistory(Base):
    __tablename__ = "task_status_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id"), nullable=False, index=True
    )
    old_status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus))
    new_status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), nullable=False)
    changed_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    task: Mapped["Task"] = relationship("Task", back_populates="status_history")
    changer: Mapped[Optional["User"]] = relationship("User", foreign_keys=[changed_by])

from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models import Base


class TaskAssignment(Base):
    __tablename__ = "task_assignments"

    __table_args__ = (
        UniqueConstraint("task_id", "user_id", name="uq_task_user_assignment"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assigned_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    role_on_task: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )

    task: Mapped["Task"] = relationship("Task", back_populates="assignments")
    user: Mapped["User"] = relationship(
        "User", foreign_keys=[user_id], back_populates="task_assignments"
    )
    assigner: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[assigned_by], back_populates="assigned_tasks"
    )

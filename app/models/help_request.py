from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models import Base
from enum import Enum as PyEnum


class HelpRequestStatus(PyEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


class HelpRequest(Base):
    __tablename__ = "help_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id"), nullable=False, index=True
    )
    requested_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    status: Mapped[HelpRequestStatus] = mapped_column(
        Enum(HelpRequestStatus), nullable=False, default=HelpRequestStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    task: Mapped["Task"] = relationship("Task")
    requester: Mapped["User"] = relationship("User")

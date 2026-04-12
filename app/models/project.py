from datetime import datetime
from typing import Optional, List

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    status: Mapped[Optional[str]] = mapped_column(String)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    manager: Mapped[Optional["User"]] = relationship(
        "User", back_populates="managed_projects"
    )
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="project")
    members: Mapped[List["ProjectMember"]] = relationship(
        "ProjectMember", back_populates="project"
    )

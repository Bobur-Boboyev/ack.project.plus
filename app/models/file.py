from datetime import datetime
from typing import Optional
from enum import Enum as PyEnum

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models import Base


class FileType(str, PyEnum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    OTHER = "other"


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    original_name: Mapped[Optional[str]] = mapped_column(String)
    stored_name: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[Optional[int]] = mapped_column(Integer)
    uploaded_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    uploader: Mapped[Optional["User"]] = relationship("User")

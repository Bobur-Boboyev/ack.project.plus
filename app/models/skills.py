from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, ForeignKey

from app.models import Base, TimestampMixin

class Skill(Base, TimestampMixin):
    __tablename__ = "skills"

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String, unique=True)

    users: Mapped[list["UserSkill"]] = relationship(
        "UserSkill",
        back_populates="skill",
        cascade="all, delete-orphan"
    )


class UserSkill(Base):
    __tablename__ = "user_skills"

    user_id = mapped_column(ForeignKey("users.id"), primary_key=True)
    skill_id = mapped_column(ForeignKey("skills.id"), primary_key=True)

    level = mapped_column(Integer)
    years = mapped_column(Integer)

    user = relationship("User", back_populates="user_skills")
    skill = relationship("Skill", back_populates="user_skills")
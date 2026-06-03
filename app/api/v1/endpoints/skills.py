from typing import Annotated

from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_admin
from app.models import User
from app.schemas.skills import SkillResponse
from app.services.skills_service import SkillService



router = APIRouter(prefix="/skills", tags=["Skills"])


@router.post("/", response_model=SkillResponse, status_code=201)
def create_skill_view(
    data: Annotated[SkillResponse, Body()],
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[User, Depends(get_admin)],
):
    service = SkillService(db)
    skill = service.create_skill(name=data.name, admin=admin)
    
    return skill    
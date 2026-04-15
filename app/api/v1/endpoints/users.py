from typing import Annotated

from fastapi import APIRouter, status, Depends, Body
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from app.models import User
from app.schemas.user import UserResponseDetail, CreateUser, UserResponse
from app.core.deps import get_admin, get_manager, get_db
from app.services.user_service import UserService
from app.repository.user_repo import UserRepo

router = APIRouter(prefix="/users", tags=["User"])


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user_view(
    data: Annotated[CreateUser, Body()],
    manager: Annotated[User, Depends(get_manager)],
    db: Annotated[Session, Depends(get_db)],
):
    service = UserService(db)
    user = service.create_user(data)
    return user


@router.get("/", response_model=list[UserResponse])
async def get_users_view(admin: Annotated[User, Depends(get_admin)], db: Annotated[Session, Depends(get_db)]):
    repository = UserRepo(db)
    users = repository.get_all_users()

    return users
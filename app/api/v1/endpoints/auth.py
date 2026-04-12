from typing import Annotated

from fastapi import APIRouter, status, Depends, Body
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from app.schemas.auth import UserLoginResponse, RefreshRequest
from app.core.deps import get_db
from app.services.user_service import UserService


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=UserLoginResponse, status_code=status.HTTP_200_OK)
async def login_view(
    credentials: Annotated[HTTPBasicCredentials, Depends(HTTPBasic())],
    db: Annotated[Session, Depends(get_db)],
):
    user_service = UserService(db)
    login_response = user_service.authenticate_user(credentials)

    return login_response


@router.post(
    "/refresh", response_model=UserLoginResponse, status_code=status.HTTP_200_OK
)
async def refresh_view(
    data: Annotated[RefreshRequest, Body()], db: Annotated[Session, Depends(get_db)]
):
    user_service = UserService(db)
    refresh_response = user_service.refresh_access_token(data.refresh_token)
    return refresh_response

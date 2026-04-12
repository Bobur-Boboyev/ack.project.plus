from fastapi import HTTPException, status
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session

from app.repository.user_repo import UserRepo
from app.schemas.auth import UserLoginResponse
from app.core.security import (
    generate_token,
    generate_refresh_token,
    verify_refresh_token,
)


class UserService:
    def __init__(self, db):
        self.db = db
        self.repo = UserRepo(db)

    def authenticate_user(self, credentials: HTTPBasicCredentials):
        user = self.repo.get_user_by_username(credentials.username)

        if not user or user.password != credentials.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        token_data = {"sub": f"{user.id}"}

        return UserLoginResponse(
            access_token=generate_token(token_data),
            refresh_token=generate_refresh_token(token_data),
        )

    def refresh_access_token(self, refresh_token: str) -> UserLoginResponse:
        payload = verify_refresh_token(refresh_token)

        user_id = payload.get("sub")

        user = self.repo.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        new_access_token = generate_token({"sub": f"{user.id}"})

        return UserLoginResponse(
            access_token=new_access_token, refresh_token=refresh_token
        )

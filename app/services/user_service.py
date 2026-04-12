from fastapi import HTTPException, status
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session

from app.repository.user_repo import UserRepo
from app.schemas.auth import UserLoginResponse
from app.core.security import  


class UserService:
    def __init__(self, db):
        self.db = db
        self.repo = UserRepo(db)

    def authenticate_user(self, credentials: HTTPBasicCredentials):
        user = self.repo.get_user_by_username(credentials.username)

        if not user or user.password != credentials.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        return 0
from typing import Generator, Annotated, Union, List

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.db.session import SessionLocal
from app.core.security import verify_access_token
from app.models.user import User, UserRole
from app.repository.user_repo import UserRepo

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    payload = verify_access_token(token)

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(401, "Invalid token")

    user = UserRepo(db).get_user_by_id(sub)

    if not user:
        raise HTTPException(401, "User not found")

    return user


def require_role(required_role: Union[UserRole, List[UserRole]]):
    def role_checker(user: Annotated[User, Depends(get_user)]) -> User:

        allowed_roles = (
            required_role if isinstance(required_role, list) else [required_role]
        )

        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {allowed_roles}",
            )

        return user

    return role_checker


get_admin = require_role(UserRole.ADMIN)
get_manager = require_role(UserRole.MANAGER)
get_worker = require_role(UserRole.WORKER)

get_admin_or_manager = require_role([UserRole.ADMIN, UserRole.MANAGER])

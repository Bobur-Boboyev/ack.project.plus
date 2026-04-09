from fastapi import HTTPException, status

from app.schemas.auth import LoginResponse
from app.core.security import generate_token, verify_refresh_token


class AuthService:
    def refresh_access_token(self, refresh_token: str) -> LoginResponse:

        payload = verify_refresh_token(refresh_token)

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        new_access_token = generate_token({"sub": user_id})

        return LoginResponse(access_token=new_access_token, refresh_token=refresh_token)

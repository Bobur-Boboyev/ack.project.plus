from sqlalchemy.orm import Session

from app.models.user import User
from app.models.refresh_token import RefreshToken


class UserRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_id(self, id: int):
        return self.db.query(User).filter(User.id == id).first()

    def get_refresh_token(self, refresh_token: str):
        return self.db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    
    def revoke_refresh_token(self, token: RefreshToken):
        token.is_revoked = True
        self.db.add(token)
        self.db.commit()

    def update_password(self, user: User, new_hash: str):
        user.password_hash = new_hash
        user.is_first_login = False

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
from sqlalchemy.orm import Session
from app.modules.users.model import User
from app.modules.users.schema import UserCreate, UserUpdate

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> User:
        return self.db.query(User).filter(User.id == user_id, User.deleted == False).first()
    
    def get_user_by_username(self, username: str) -> User:
        return self.db.query(User).filter(User.username == username, User.deleted == False).first()
    
    def get_user_by_phone(self, phone: str) -> User:
        return self.db.query(User).filter(User.phone == phone, User.deleted == False).first()
    
    def create_user(self, user_create: UserCreate) -> User:
        user = User(
            username=user_create.username,
            nickname=user_create.nickname,
            phone=user_create.phone,
            email=user_create.email
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        user = self.get_user_by_id(user_id)
        if user:
            if user_update.nickname:
                user.nickname = user_update.nickname
            if user_update.avatar_url:
                user.avatar_url = user_update.avatar_url
            if user_update.email:
                user.email = user_update.email
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: int) -> bool:
        user = self.get_user_by_id(user_id)
        if user:
            user.deleted = True
            self.db.commit()
            return True
        return False
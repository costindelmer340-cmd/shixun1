from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.database import Base

class User(Base):
    __tablename__ = "sys_user"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False)
    password_hash = Column(String(255))
    nickname = Column(String(64), nullable=False)
    avatar_url = Column(String(512))
    phone = Column(String(32), unique=True)
    email = Column(String(128))
    address = Column(String(512))
    bind_platform = Column(String(64))
    status = Column(String(32), default="ACTIVE")
    last_login_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted = Column(Boolean, default=False)
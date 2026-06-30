from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.modules.users.service import UserService
from app.modules.users.schema import UserCreate, UserUpdate, LoginRequest
from app.common.response import APIResponse
import os

router = APIRouter(prefix="/users", tags=["用户管理"])

@router.post("/login", response_model=APIResponse)
def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.login(login_request)

@router.post("/", response_model=APIResponse)
def create_user(user_create: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.create_user(user_create)

@router.get("/{user_id}", response_model=APIResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.get_user(user_id)

@router.put("/{user_id}", response_model=APIResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.update_user(user_id, user_update)

@router.delete("/{user_id}", response_model=APIResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.delete_user(user_id)

@router.post("/{user_id}/avatar", response_model=APIResponse)
async def upload_avatar(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    service = UserService(db)
    return await service.upload_avatar(user_id, file)
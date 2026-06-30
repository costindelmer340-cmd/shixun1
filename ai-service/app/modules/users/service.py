from sqlalchemy.orm import Session
from app.modules.users.repository import UserRepository
from app.modules.users.schema import UserCreate, UserUpdate, UserResponse, LoginRequest, LoginResponse
from app.common.response import APIResponse
import uuid
import os
from fastapi import UploadFile

class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)
    
    def get_user(self, user_id: int):
        user = self.repository.get_user_by_id(user_id)
        if not user:
            return APIResponse.not_found("用户不存在")
        return APIResponse.success(UserResponse.from_orm(user))
    
    def create_user(self, user_create: UserCreate):
        existing = self.repository.get_user_by_username(user_create.username)
        if existing:
            return APIResponse.error(400, "用户名已存在")
        
        user = self.repository.create_user(user_create)
        return APIResponse.success(UserResponse.from_orm(user), "用户创建成功")
    
    def update_user(self, user_id: int, user_update: UserUpdate):
        user = self.repository.update_user(user_id, user_update)
        if not user:
            return APIResponse.not_found("用户不存在")
        return APIResponse.success(UserResponse.from_orm(user), "用户更新成功")
    
    def delete_user(self, user_id: int):
        success = self.repository.delete_user(user_id)
        if not success:
            return APIResponse.not_found("用户不存在")
        return APIResponse.success(message="用户删除成功")
    
    def login(self, login_request: LoginRequest):
        user = self.repository.get_user_by_phone(login_request.phone)
        if not user:
            return APIResponse.error(401, "用户不存在")
        
        if user.status != "ACTIVE":
            return APIResponse.error(401, "用户已禁用")
        
        token = str(uuid.uuid4())
        user_response = UserResponse.from_orm(user)
        login_response = LoginResponse(user=user_response, token=token)
        
        return APIResponse.success(login_response, "登录成功")
    
    async def upload_avatar(self, user_id: int, file: UploadFile):
        user = self.repository.get_user_by_id(user_id)
        if not user:
            return APIResponse.not_found("用户不存在")
        
        allowed_extensions = {"jpg", "jpeg", "png", "gif"}
        file_extension = file.filename.split(".")[-1].lower()
        
        if file_extension not in allowed_extensions:
            return APIResponse.error(400, "不支持的图片格式，仅支持jpg、jpeg、png、gif")
        
        static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "avatars")
        os.makedirs(static_dir, exist_ok=True)
        
        file_name = f"{user_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
        file_path = os.path.join(static_dir, file_name)
        
        try:
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())
            
            avatar_url = f"/static/avatars/{file_name}"
            user.avatar_url = avatar_url
            self.repository.db.commit()
            
            return APIResponse.success({"avatar_url": avatar_url}, "头像上传成功")
        except Exception as e:
            return APIResponse.error(500, f"头像上传失败: {str(e)}")
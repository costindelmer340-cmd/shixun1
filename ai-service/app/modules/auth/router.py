from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.modules.users.service import UserService
from app.modules.users.schema import LoginRequest
from app.common.response import APIResponse

router = APIRouter(prefix="/auth", tags=["认证管理"])

@router.post("/login", response_model=APIResponse)
def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.login(login_request)

@router.get("/user/{user_id}", response_model=APIResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.get_user(user_id)

from pydantic import BaseModel

class BindRequest(BaseModel):
    accountNo: str
    password: str
    role: str = "CONSUMER"

@router.post("/twenty-mall/bind", response_model=APIResponse)
def bind_twenty_mall(bind_request: BindRequest, db: Session = Depends(get_db)):
    from app.modules.twenty_mall.model import TwentyMallAccount
    print(f"Bind request received: accountNo={bind_request.accountNo}, password={bind_request.password}, role={bind_request.role}")
    
    accounts = db.query(TwentyMallAccount).filter(
        TwentyMallAccount.account_role == bind_request.role,
        TwentyMallAccount.status == "ACTIVE",
        TwentyMallAccount.deleted == False
    ).all()
    
    print(f"Available accounts: {[(a.account_no, a.password_plain) for a in accounts]}")
    
    account = db.query(TwentyMallAccount).filter(
        TwentyMallAccount.account_no == bind_request.accountNo,
        TwentyMallAccount.account_role == bind_request.role,
        TwentyMallAccount.status == "ACTIVE",
        TwentyMallAccount.deleted == False
    ).first()
    
    if not account:
        return APIResponse(code=400, message="账号不存在")
    
    if account.password_plain != bind_request.password:
        return APIResponse(code=400, message="账号或密码错误")
    
    return APIResponse(code=200, message="绑定成功", data={
        "accountNo": account.account_no,
        "displayName": account.display_name,
        "role": account.account_role
    })

@router.get("/twenty-mall/profile", response_model=APIResponse)
def get_twenty_mall_profile(accountNo: str, role: str = "CONSUMER", db: Session = Depends(get_db)):
    from app.modules.twenty_mall.model import TwentyMallAccount
    account = db.query(TwentyMallAccount).filter(
        TwentyMallAccount.account_no == accountNo,
        TwentyMallAccount.account_role == role,
        TwentyMallAccount.status == "ACTIVE",
        TwentyMallAccount.deleted == False
    ).first()
    
    if not account:
        return APIResponse(code=400, message="账号不存在")
    
    return APIResponse(code=200, message="success", data={
        "accountNo": account.account_no,
        "displayName": account.display_name,
        "phone": account.phone,
        "address": account.address,
        "role": account.account_role
    })
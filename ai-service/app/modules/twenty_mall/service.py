from sqlalchemy.orm import Session
from app.modules.twenty_mall.repository import TwentyMallRepository
from app.common.response import APIResponse

class TwentyMallService:
    def __init__(self, db: Session):
        self.repository = TwentyMallRepository(db)
    
    def bind_account(self, account_no: str, password: str, role: str):
        account = self.repository.find_account(account_no, role)
        if not account:
            return APIResponse(code=400, message="账号不存在")
        
        if account.password_plain != password:
            return APIResponse(code=400, message="账号或密码错误")
        
        return APIResponse(code=200, message="绑定成功", data={
            "accountNo": account.account_no,
            "displayName": account.display_name,
            "role": account.account_role
        })
    
    def get_profile(self, account_no: str, role: str):
        account = self.repository.get_profile(account_no, role)
        if not account:
            return APIResponse(code=400, message="账号不存在")
        
        return APIResponse(code=200, message="success", data={
            "accountNo": account.account_no,
            "displayName": account.display_name,
            "phone": account.phone,
            "address": account.address,
            "role": account.account_role
        })

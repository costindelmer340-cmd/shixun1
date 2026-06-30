from fastapi import FastAPI, HTTPException, Response, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.db.database import engine, get_db
from app.modules.users.router import router as users_router
from app.modules.orders.router import router as orders_router
from app.modules.after_sale.router import router as after_sale_router
from app.modules.auth.router import router as auth_router
from app.modules.conversation.router import router as conversation_router
from app.modules.ai.router import router as ai_router
from app.modules.rule_engine.router import router as rule_engine_router
from app.modules.ticket.router import router as ticket_router
from app.modules.review.router import router as review_router
from app.modules.twenty_mall.router import router as twenty_mall_router
from app.common.response import APIResponse

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def set_encoding_header(request, call_next):
    response = await call_next(request)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

app.include_router(users_router)
app.include_router(orders_router)
app.include_router(after_sale_router)
app.include_router(conversation_router)
app.include_router(auth_router)
app.include_router(ai_router)
app.include_router(rule_engine_router)
app.include_router(ticket_router)
app.include_router(review_router)

import os
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "static")), name="static")

@app.get("/", response_model=APIResponse)
async def root():
    return APIResponse.success({"message": f"Welcome to {settings.APP_NAME} API", "version": settings.APP_VERSION})

@app.get("/health", response_model=APIResponse)
async def health_check():
    return APIResponse.success({"status": "healthy", "timestamp": __import__('datetime').datetime.now().isoformat()})

from pydantic import BaseModel

class BindRequest(BaseModel):
    accountNo: str
    password: str
    role: str = "CONSUMER"

@app.post("/twenty-mall/bind", response_model=APIResponse)
def bind_twenty_mall(request: BindRequest, db: Session = Depends(get_db)):
    accountNo = request.accountNo
    password = request.password
    role = request.role
    from app.modules.twenty_mall.model import TwentyMallAccount
    account = db.query(TwentyMallAccount).filter(
        TwentyMallAccount.account_no == accountNo,
        TwentyMallAccount.account_role == role,
        TwentyMallAccount.status == "ACTIVE",
        TwentyMallAccount.deleted == False
    ).first()
    
    if not account:
        return APIResponse(code=400, message="账号不存在")
    
    if account.password_plain != password:
        return APIResponse(code=400, message="账号或密码错误")
    
    return APIResponse(code=200, message="绑定成功", data={
        "accountNo": account.account_no,
        "displayName": account.display_name,
        "role": account.account_role
    })

@app.get("/twenty-mall/profile", response_model=APIResponse)
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

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return APIResponse.error(exc.status_code, exc.detail).dict()
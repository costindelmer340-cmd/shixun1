from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.modules.twenty_mall.service import TwentyMallService

router = APIRouter(prefix="/twenty-mall", tags=["20商城"])

@router.post("/bind")
def bind_account(accountNo: str, password: str, role: str = "CONSUMER", db: Session = Depends(get_db)):
    service = TwentyMallService(db)
    return service.bind_account(accountNo, password, role)

@router.get("/profile")
def get_profile(accountNo: str, role: str = "CONSUMER", db: Session = Depends(get_db)):
    service = TwentyMallService(db)
    return service.get_profile(accountNo, role)

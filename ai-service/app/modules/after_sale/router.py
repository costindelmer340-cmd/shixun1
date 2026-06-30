from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.modules.after_sale.service import AfterSaleService
from app.modules.after_sale.schema import AfterSaleCreate, AfterSaleClose
from app.common.response import APIResponse

router = APIRouter(prefix="/after-sale", tags=["售后管理"])

@router.post("/create", response_model=APIResponse)
def create_after_sale(create_data: AfterSaleCreate, db: Session = Depends(get_db)):
    service = AfterSaleService(db)
    return service.create_application(create_data)

@router.get("/list", response_model=APIResponse)
def get_after_sale_list(
    user_id: int = Query(...),
    status: list = Query(None),
    limit: int = Query(20),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    service = AfterSaleService(db)
    return service.get_applications(user_id, status, limit, offset)

@router.get("/detail", response_model=APIResponse)
def get_after_sale_detail(
    after_sale_no: str = Query(...),
    db: Session = Depends(get_db)
):
    service = AfterSaleService(db)
    return service.get_application(after_sale_no)

@router.put("/close", response_model=APIResponse)
def close_after_sale(
    after_sale_no: str = Query(...),
    final_result: str = Query(None),
    db: Session = Depends(get_db)
):
    service = AfterSaleService(db)
    close_data = AfterSaleClose(final_result=final_result or "用户主动取消")
    return service.close_application(after_sale_no, close_data)

@router.post("/review", response_model=APIResponse)
def review_after_sale(
    after_sale_no: str = Query(...),
    decision: str = Query(...),
    remark: str = Query(None),
    db: Session = Depends(get_db)
):
    service = AfterSaleService(db)
    return service.review_application(after_sale_no, decision, remark)
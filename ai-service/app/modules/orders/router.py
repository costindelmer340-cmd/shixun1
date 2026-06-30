from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.modules.orders.service import OrderService
from app.common.response import APIResponse

router = APIRouter(prefix="/order", tags=["订单管理"])

@router.get("/list")
def get_order_list(
    user_id: int = Query(...),
    order_status: str = Query(None),
    limit: int = Query(20),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    service = OrderService(db)
    result = service.get_orders(user_id, order_status, limit, offset)
    return result.dict()

@router.get("/detail", response_model=APIResponse)
def get_order_detail(
    order_no: str = Query(...),
    db: Session = Depends(get_db)
):
    service = OrderService(db)
    return service.get_order(order_no)

@router.get("/{order_no}", response_model=APIResponse)
def get_order_by_no(
    order_no: str,
    db: Session = Depends(get_db)
):
    service = OrderService(db)
    return service.get_order(order_no)

@router.get("/stats", response_model=APIResponse)
def get_order_stats(
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    service = OrderService(db)
    return service.get_order_stats(user_id)
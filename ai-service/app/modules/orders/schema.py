from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class OrderResponse(BaseModel):
    id: int
    external_order_no: str
    platform_code: str
    buyer_masked_name: str
    buyer_masked_phone: str
    order_status: str
    pay_status: str
    logistics_status: str
    after_sale_status: str
    total_amount: float
    payable_amount: float
    ordered_at: Optional[datetime]
    paid_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    total: int
    limit: int
    offset: int
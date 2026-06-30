from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class AfterSaleCreate(BaseModel):
    order_no: str
    user_id: int
    after_sale_type: str
    reason_type: str
    description: Optional[str] = None
    
    class Config:
        allow_population_by_field_name = True

class AfterSaleClose(BaseModel):
    final_result: str

class AfterSaleResponse(BaseModel):
    id: int
    after_sale_no: str
    external_order_id: int
    user_id: int
    merchant_id: int
    after_sale_type: str
    reason_type: str
    problem_description: Optional[str]
    requested_amount: float
    status: str
    priority: str
    ai_category: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AfterSaleListResponse(BaseModel):
    applications: List[AfterSaleResponse]
    total: int
    limit: int
    offset: int

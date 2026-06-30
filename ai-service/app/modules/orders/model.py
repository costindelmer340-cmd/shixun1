from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base

class Order(Base):
    __tablename__ = "external_order"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    shop_binding_id = Column(Integer)
    merchant_id = Column(Integer)
    platform_code = Column(String(32))
    external_order_no = Column(String(64), unique=True)
    buyer_masked_name = Column(String(64))
    buyer_masked_phone = Column(String(32))
    order_status = Column(String(32))
    pay_status = Column(String(32))
    logistics_status = Column(String(32))
    after_sale_status = Column(String(32), default="NONE")
    total_amount = Column(DECIMAL(12, 2))
    payable_amount = Column(DECIMAL(12, 2))
    ordered_at = Column(DateTime)
    paid_at = Column(DateTime)
    completed_at = Column(DateTime)
    raw_data = Column(String(2048))
    last_synced_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted = Column(Boolean, default=False)
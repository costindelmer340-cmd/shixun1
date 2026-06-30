from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base

class AfterSaleApplication(Base):
    __tablename__ = "after_sale_application"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    after_sale_no = Column(String(64), unique=True)
    external_order_id = Column(Integer)
    external_order_item_id = Column(Integer)
    user_id = Column(Integer)
    merchant_id = Column(Integer)
    shop_binding_id = Column(Integer)
    after_sale_type = Column(String(32))
    reason_type = Column(String(32))
    problem_description = Column(String(512))
    requested_amount = Column(DECIMAL(12, 2))
    status = Column(String(32), default="PENDING_REVIEW")
    priority = Column(String(32), default="NORMAL")
    ai_category = Column(String(128))
    reviewer_id = Column(Integer)
    reviewed_at = Column(DateTime)
    review_opinion = Column(String(512))
    final_result = Column(String(512))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted = Column(Boolean, default=False)
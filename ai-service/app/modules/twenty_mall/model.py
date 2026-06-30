from sqlalchemy import Column, Integer, String, DateTime, Boolean, DECIMAL, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class TwentyMallAccount(Base):
    __tablename__ = "twenty_mall_account"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_no = Column(String(64), nullable=False)
    password_plain = Column(String(128), nullable=False)
    account_role = Column(String(32), nullable=False)
    display_name = Column(String(128), nullable=False)
    phone = Column(String(32))
    address = Column(String(512))
    bind_status = Column(String(32), default="UNBOUND")
    status = Column(String(32), default="ACTIVE")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted = Column(Boolean, default=False)

class TwentyMallProduct(Base):
    __tablename__ = "twenty_mall_product"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    merchant_account_id = Column(Integer, ForeignKey("twenty_mall_account.id"))
    product_no = Column(String(64), nullable=False, unique=True)
    product_name = Column(String(255), nullable=False)
    product_image_url = Column(String(512))
    price = Column(DECIMAL(12, 2), default=0.00)
    stock = Column(Integer, default=0)
    category = Column(String(64))
    description = Column(Text)
    status = Column(String(32), default="ON_SALE")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted = Column(Boolean, default=False)

class TwentyMallOrder(Base):
    __tablename__ = "twenty_mall_order"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String(64), nullable=False, unique=True)
    consumer_account_id = Column(Integer, ForeignKey("twenty_mall_account.id"))
    merchant_account_id = Column(Integer, ForeignKey("twenty_mall_account.id"))
    order_status = Column(String(32), nullable=False)
    pay_status = Column(String(32), nullable=False)
    logistics_status = Column(String(32))
    after_sale_status = Column(String(32))
    total_amount = Column(DECIMAL(12, 2), default=0.00)
    paid_at = Column(DateTime)
    ordered_at = Column(DateTime)
    delivered_at = Column(DateTime)
    policy_tags = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted = Column(Boolean, default=False)

class TwentyMallOrderItem(Base):
    __tablename__ = "twenty_mall_order_item"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("twenty_mall_order.id"))
    product_id = Column(Integer, ForeignKey("twenty_mall_product.id"))
    product_name = Column(String(255), nullable=False)
    sku_name = Column(String(255))
    product_image_url = Column(String(512))
    unit_price = Column(DECIMAL(12, 2), default=0.00)
    quantity = Column(Integer, default=1)
    total_amount = Column(DECIMAL(12, 2), default=0.00)
    after_sale_status = Column(String(32))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted = Column(Boolean, default=False)

class TwentyMallAfterSale(Base):
    __tablename__ = "twenty_mall_after_sale"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    after_sale_no = Column(String(64), nullable=False, unique=True)
    order_id = Column(Integer, ForeignKey("twenty_mall_order.id"), nullable=False)
    order_item_id = Column(Integer, ForeignKey("twenty_mall_order_item.id"))
    after_sale_type = Column(String(32), nullable=False)
    reason_type = Column(String(32), nullable=False)
    description = Column(Text)
    requested_amount = Column(DECIMAL(12, 2), default=0.00)
    status = Column(String(32), default="PENDING_REVIEW")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted = Column(Boolean, default=False)

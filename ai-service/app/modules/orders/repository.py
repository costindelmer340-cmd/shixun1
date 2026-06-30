from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.modules.orders.model import Order
from app.modules.twenty_mall.model import TwentyMallOrder, TwentyMallAccount
from typing import Optional, List

class OrderRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        return self.db.query(Order).filter(Order.id == order_id, Order.deleted == False).first()
    
    def get_order_by_no(self, order_no: str) -> Optional[Order]:
        return self.db.query(Order).filter(Order.external_order_no == order_no, Order.deleted == False).first()
    
    def get_orders_by_user(self, user_phone: str, order_status: Optional[str] = None, 
                          limit: int = 20, offset: int = 0) -> List[Order]:
        masked_phone = f"{user_phone[:3]}****{user_phone[-4:]}"
        query = self.db.query(Order).filter(
            Order.buyer_masked_phone == masked_phone,
            Order.deleted == False
        )
        
        if order_status:
            query = query.filter(Order.order_status == order_status)
        
        return query.order_by(Order.ordered_at.desc()).offset(offset).limit(limit).all()
    
    def count_orders_by_user(self, user_phone: str, order_status: Optional[str] = None) -> int:
        masked_phone = f"{user_phone[:3]}****{user_phone[-4:]}"
        query = self.db.query(Order).filter(
            Order.buyer_masked_phone == masked_phone,
            Order.deleted == False
        )
        
        if order_status:
            query = query.filter(Order.order_status == order_status)
        
        return query.count()
    
    def update_after_sale_status(self, order_id: int, status: str) -> bool:
        order = self.get_order_by_id(order_id)
        if order:
            order.after_sale_status = status
            self.db.commit()
            return True
        return False
    
    def get_twenty_mall_orders(self, user_id: int) -> List[TwentyMallOrder]:
        return self.db.query(TwentyMallOrder).filter(
            TwentyMallOrder.deleted == False
        ).order_by(TwentyMallOrder.created_at.desc()).all()
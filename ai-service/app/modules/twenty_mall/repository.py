from sqlalchemy.orm import Session
from app.modules.twenty_mall.model import TwentyMallAccount, TwentyMallOrder, TwentyMallOrderItem

class TwentyMallRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def find_account(self, account_no: str, account_role: str):
        return self.db.query(TwentyMallAccount).filter(
            TwentyMallAccount.account_no == account_no,
            TwentyMallAccount.account_role == account_role,
            TwentyMallAccount.status == "ACTIVE",
            TwentyMallAccount.deleted == False
        ).first()
    
    def get_profile(self, account_no: str, account_role: str):
        return self.db.query(TwentyMallAccount).filter(
            TwentyMallAccount.account_no == account_no,
            TwentyMallAccount.account_role == account_role,
            TwentyMallAccount.status == "ACTIVE",
            TwentyMallAccount.deleted == False
        ).first()
    
    def get_orders_by_consumer(self, consumer_account_id: int):
        return self.db.query(TwentyMallOrder).filter(
            TwentyMallOrder.consumer_account_id == consumer_account_id,
            TwentyMallOrder.deleted == False
        ).order_by(TwentyMallOrder.created_at.desc()).all()
    
    def get_order_items(self, order_id: int):
        return self.db.query(TwentyMallOrderItem).filter(
            TwentyMallOrderItem.order_id == order_id,
            TwentyMallOrderItem.deleted == False
        ).all()

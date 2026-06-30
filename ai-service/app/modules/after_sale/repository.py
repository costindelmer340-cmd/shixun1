from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.modules.after_sale.model import AfterSaleApplication
from typing import Optional, List

class AfterSaleRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, id: int) -> Optional[AfterSaleApplication]:
        return self.db.query(AfterSaleApplication).filter(
            AfterSaleApplication.id == id, 
            AfterSaleApplication.deleted == False
        ).first()
    
    def get_by_no(self, after_sale_no: str) -> Optional[AfterSaleApplication]:
        return self.db.query(AfterSaleApplication).filter(
            AfterSaleApplication.after_sale_no == after_sale_no, 
            AfterSaleApplication.deleted == False
        ).first()
    
    def get_by_user(self, user_id: int, status: Optional[str] = None, 
                    limit: int = 20, offset: int = 0) -> List[AfterSaleApplication]:
        query = self.db.query(AfterSaleApplication).filter(
            AfterSaleApplication.user_id == user_id,
            AfterSaleApplication.deleted == False
        )
        
        if status:
            if isinstance(status, list):
                query = query.filter(AfterSaleApplication.status.in_(status))
            else:
                query = query.filter(AfterSaleApplication.status == status)
        
        return query.order_by(AfterSaleApplication.created_at.desc()).offset(offset).limit(limit).all()
    
    def count_by_user(self, user_id: int, status: Optional[str] = None) -> int:
        query = self.db.query(AfterSaleApplication).filter(
            AfterSaleApplication.user_id == user_id,
            AfterSaleApplication.deleted == False
        )
        
        if status:
            if isinstance(status, list):
                query = query.filter(AfterSaleApplication.status.in_(status))
            else:
                query = query.filter(AfterSaleApplication.status == status)
        
        return query.count()
    
    def create(self, application: AfterSaleApplication) -> AfterSaleApplication:
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application
    
    def update_status(self, id: int, status: str, reviewer_id: Optional[int] = None, 
                      review_opinion: Optional[str] = None) -> bool:
        app = self.get_by_id(id)
        if app:
            app.status = status
            if reviewer_id:
                app.reviewer_id = reviewer_id
            if review_opinion:
                app.review_opinion = review_opinion
            self.db.commit()
            return True
        return False
    
    def close(self, id: int, final_result: str) -> bool:
        app = self.get_by_id(id)
        if app:
            app.status = "CLOSED"
            app.final_result = final_result
            self.db.commit()
            return True
        return False
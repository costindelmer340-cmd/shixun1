from sqlalchemy.orm import Session
from app.modules.after_sale.repository import AfterSaleRepository
from app.modules.after_sale.schema import AfterSaleCreate, AfterSaleClose, AfterSaleResponse, AfterSaleListResponse
from app.modules.after_sale.model import AfterSaleApplication
from app.modules.orders.repository import OrderRepository
from app.modules.twenty_mall.model import TwentyMallOrder, TwentyMallAfterSale
from app.common.response import APIResponse
from datetime import datetime
import uuid
from typing import Optional

class AfterSaleService:
    def __init__(self, db: Session):
        self.repo = AfterSaleRepository(db)
        self.order_repo = OrderRepository(db)
        self.db = db
    
    def create_application(self, create_data: AfterSaleCreate):
        order = self.order_repo.get_order_by_no(create_data.order_no)
        
        if not order:
            if create_data.order_no.startswith('TM'):
                order = self.db.query(TwentyMallOrder).filter(
                    TwentyMallOrder.order_no == create_data.order_no,
                    TwentyMallOrder.deleted == False
                ).first()
                if order:
                    return self.create_twenty_mall_application(create_data, order)
        
        if not order:
            return APIResponse.not_found("订单不存在")
        
        after_sale_no = f"AS-{order.merchant_id}-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
        
        application = AfterSaleApplication(
            after_sale_no=after_sale_no,
            external_order_id=order.id,
            user_id=create_data.user_id,
            merchant_id=order.merchant_id,
            shop_binding_id=order.shop_binding_id or 1,
            after_sale_type=create_data.after_sale_type,
            reason_type=create_data.reason_type,
            problem_description=create_data.description,
            requested_amount=order.total_amount or 0.0
        )
        
        application = self.repo.create(application)
        
        self.order_repo.update_after_sale_status(order.id, "AFTER_SALE")
        
        return APIResponse.success(AfterSaleResponse.from_orm(application), "售后申请创建成功")
    
    def get_applications(self, user_id: int, status: Optional[str] = None, 
                        limit: int = 20, offset: int = 0):
        applications = self.repo.get_by_user(user_id, status, limit, offset)
        
        twenty_mall_apps = self.db.query(TwentyMallAfterSale).filter(
            TwentyMallAfterSale.deleted == False,
            TwentyMallAfterSale.status != 'CLOSED'
        ).all()
        
        result_applications = []
        
        for app in applications:
            if app.status != 'CLOSED':
                order = self.order_repo.get_order_by_id(app.external_order_id)
                order_no = order.external_order_no if order else ''
                result_applications.append({
                    'id': app.id,
                    'after_sale_no': app.after_sale_no,
                    'external_order_id': app.external_order_id,
                    'order_no': order_no,
                    'user_id': app.user_id,
                    'merchant_id': app.merchant_id,
                    'after_sale_type': app.after_sale_type,
                    'reason_type': app.reason_type,
                    'problem_description': app.problem_description,
                    'requested_amount': float(app.requested_amount),
                    'status': app.status,
                    'priority': app.priority,
                    'ai_category': app.ai_category,
                    'created_at': app.created_at.isoformat() if app.created_at else None,
                    'updated_at': app.updated_at.isoformat() if app.updated_at else None
                })
        
        for app in twenty_mall_apps:
            order = self.db.query(TwentyMallOrder).filter(
                TwentyMallOrder.id == app.order_id,
                TwentyMallOrder.deleted == False
            ).first()
            order_no = order.order_no if order else ''
            result_applications.append({
                'id': app.id,
                'after_sale_no': app.after_sale_no,
                'external_order_id': app.order_id,
                'order_no': order_no,
                'user_id': 1,
                'merchant_id': 1,
                'after_sale_type': app.after_sale_type,
                'reason_type': app.reason_type,
                'problem_description': app.description,
                'requested_amount': float(app.requested_amount),
                'status': app.status,
                'priority': 'NORMAL',
                'ai_category': None,
                'created_at': app.created_at.isoformat() if app.created_at else None,
                'updated_at': app.updated_at.isoformat() if app.updated_at else None
            })
        
        result_applications.sort(key=lambda x: x['created_at'], reverse=True)
        total = len(result_applications)
        result_applications = result_applications[offset:offset + limit]
        
        data = {
            'applications': result_applications,
            'total': total,
            'limit': limit,
            'offset': offset
        }
        
        return APIResponse.success(data)
    
    def get_application(self, after_sale_no: str):
        application = self.repo.get_by_no(after_sale_no)
        if not application:
            return APIResponse.not_found("售后申请不存在")
        return APIResponse.success(AfterSaleResponse.from_orm(application))
    
    def close_application(self, after_sale_no: str, close_data: AfterSaleClose):
        app = self.repo.get_by_no(after_sale_no)
        
        if not app:
            if after_sale_no.startswith('TMAS'):
                twenty_mall_app = self.db.query(TwentyMallAfterSale).filter(
                    TwentyMallAfterSale.after_sale_no == after_sale_no,
                    TwentyMallAfterSale.deleted == False
                ).first()
                if twenty_mall_app:
                    return self.close_twenty_mall_application(twenty_mall_app, close_data.final_result)
            return APIResponse.not_found("售后申请不存在")
        
        success = self.repo.close(app.id, close_data.final_result)
        if success:
            self.order_repo.update_after_sale_status(app.external_order_id, "NONE")
            return APIResponse.success(message="售后申请已关闭")
        return APIResponse.error(500, "关闭失败")
    
    def close_twenty_mall_application(self, app: TwentyMallAfterSale, final_result: str):
        app.status = "CLOSED"
        
        order = self.db.query(TwentyMallOrder).filter(
            TwentyMallOrder.id == app.order_id,
            TwentyMallOrder.deleted == False
        ).first()
        if order:
            order.after_sale_status = "NONE"
        
        self.db.commit()
        
        return APIResponse.success(message="售后申请已关闭")
    
    def review_application(self, after_sale_no: str, decision: str, remark: str = None):
        app = self.repo.get_by_no(after_sale_no)
        if not app:
            return APIResponse.not_found("售后申请不存在")
        
        success = self.repo.review(app.id, decision, remark)
        if success:
            if decision == "APPROVED":
                self.order_repo.update_after_sale_status(app.external_order_id, "AFTER_SALE")
            return APIResponse.success(message="审核完成")
        return APIResponse.error(500, "审核失败")
    
    def create_twenty_mall_application(self, create_data: AfterSaleCreate, order: TwentyMallOrder):
        from app.modules.twenty_mall.model import TwentyMallOrderItem
        
        after_sale_no = f"TMAS-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
        
        order_item = self.db.query(TwentyMallOrderItem).filter(
            TwentyMallOrderItem.order_id == order.id,
            TwentyMallOrderItem.deleted == False
        ).first()
        
        order_item_id = order_item.id if order_item else None
        
        after_sale = TwentyMallAfterSale(
            after_sale_no=after_sale_no,
            order_id=order.id,
            order_item_id=order_item_id,
            after_sale_type=create_data.after_sale_type,
            reason_type=create_data.reason_type,
            description=create_data.description,
            requested_amount=order.total_amount or 0.0,
            status="PENDING_REVIEW"
        )
        
        self.db.add(after_sale)
        self.db.commit()
        self.db.refresh(after_sale)
        
        order.after_sale_status = "AFTER_SALE"
        self.db.commit()
        
        return APIResponse.success({
            "after_sale_no": after_sale.after_sale_no,
            "order_no": order.order_no,
            "after_sale_type": after_sale.after_sale_type,
            "reason_type": after_sale.reason_type,
            "status": after_sale.status,
            "requested_amount": float(after_sale.requested_amount),
            "created_at": after_sale.created_at.isoformat() if after_sale.created_at else None
        }, "售后申请创建成功")

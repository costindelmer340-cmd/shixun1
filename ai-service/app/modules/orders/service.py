from sqlalchemy.orm import Session
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schema import OrderResponse, OrderListResponse
from app.modules.users.repository import UserRepository
from app.common.response import APIResponse
from typing import Optional, List

class OrderService:
    def __init__(self, db: Session):
        self.order_repo = OrderRepository(db)
        self.user_repo = UserRepository(db)
    
    def get_order(self, order_no: str):
        order = self.order_repo.get_order_by_no(order_no)
        if not order:
            return APIResponse.not_found("订单不存在")
        return APIResponse.success(OrderResponse.from_orm(order))
    
    def get_orders(self, user_id: int, order_status: Optional[str] = None, 
                   limit: int = 20, offset: int = 0):
        user = self.user_repo.get_user_by_id(user_id)
        if not user or not user.phone:
            return APIResponse.error(400, "用户信息无效")
        
        orders = self.order_repo.get_orders_by_user(user.phone, order_status, limit, offset)
        
        twenty_mall_orders = self.order_repo.get_twenty_mall_orders(user_id)
        
        def _parse_policy_tags(tags):
            if not tags:
                return []
            if isinstance(tags, list):
                return tags
            if isinstance(tags, str):
                return [t.strip() for t in tags.split() if t.strip()]
            return []
        
        all_orders = []
        for order in orders:
            all_orders.append({
                'id': order.id,
                'external_order_no': order.external_order_no,
                'platform_code': order.platform_code,
                'buyer_masked_name': order.buyer_masked_name,
                'buyer_masked_phone': order.buyer_masked_phone,
                'order_status': order.order_status,
                'pay_status': order.pay_status,
                'logistics_status': order.logistics_status,
                'after_sale_status': order.after_sale_status,
                'total_amount': order.total_amount,
                'payable_amount': order.payable_amount,
                'ordered_at': order.ordered_at,
                'paid_at': order.paid_at,
                'completed_at': order.completed_at,
                'created_at': order.created_at,
                'policy_tags': _parse_policy_tags(order.policy_tags if hasattr(order, 'policy_tags') else None)
            })
        
        for order in twenty_mall_orders:
            all_orders.append({
                'id': order.id,
                'external_order_no': order.order_no,
                'platform_code': 'TWENTY_MALL',
                'buyer_masked_name': '20商城用户',
                'buyer_masked_phone': '133****7581',
                'order_status': order.order_status,
                'pay_status': order.pay_status,
                'logistics_status': order.logistics_status or 'DELIVERED',
                'after_sale_status': order.after_sale_status or 'NONE',
                'total_amount': order.total_amount,
                'payable_amount': order.total_amount,
                'ordered_at': order.ordered_at,
                'paid_at': order.paid_at,
                'completed_at': order.delivered_at,
                'created_at': order.created_at,
                'policy_tags': _parse_policy_tags(order.policy_tags)
            })
        
        all_orders.sort(key=lambda x: x['created_at'] if x['created_at'] else 0, reverse=True)
        
        paginated_orders = all_orders[:limit]
        total = len(all_orders)
        
        data = {
            'orders': paginated_orders,
            'total': total,
            'limit': limit,
            'offset': offset
        }
        
        return APIResponse.success(data)
    
    def get_order_stats(self, user_id: int):
        user = self.user_repo.get_user_by_id(user_id)
        if not user or not user.phone:
            return APIResponse.error(400, "用户信息无效")
        
        orders = self.order_repo.get_orders_by_user(user.phone)
        twenty_mall_orders = self.order_repo.get_twenty_mall_orders(user_id)
        
        all_orders = list(orders) + list(twenty_mall_orders)
        
        stats = {
            'total_count': len(all_orders),
            'pending_payment': sum(1 for o in all_orders if getattr(o, 'order_status', '') == 'PENDING_PAYMENT'),
            'shipped': sum(1 for o in all_orders if getattr(o, 'order_status', '') == 'SHIPPED'),
            'completed': sum(1 for o in all_orders if getattr(o, 'order_status', '') == 'COMPLETED'),
            'after_sale': sum(1 for o in all_orders if getattr(o, 'after_sale_status', '') not in ('NONE', None)),
            'total_amount': sum(getattr(o, 'total_amount', 0) for o in all_orders),
            'platform_breakdown': {
                'DOUYIN': sum(1 for o in all_orders if getattr(o, 'platform_code', '') == 'DOUYIN'),
                'TWENTY_MALL': sum(1 for o in twenty_mall_orders)
            }
        }
        
        return APIResponse.success(stats)
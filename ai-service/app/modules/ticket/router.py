from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.common.response import APIResponse
from datetime import datetime
import uuid

router = APIRouter(prefix="/ticket", tags=["工单管理"])

@router.post("/create", response_model=APIResponse)
def create_ticket(
    user_id: int = Query(...),
    type: str = Query(...),
    title: str = Query(...),
    content: str = Query(...),
    order_id: int = Query(None),
    after_sale_no: str = Query(None),
    evidence_urls: str = Query(None),
    db: Session = Depends(get_db)
):
    ticket_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"
    
    return APIResponse.success({
        "ticket_id": ticket_id,
        "user_id": user_id,
        "type": type,
        "title": title,
        "status": "PENDING",
        "created_at": datetime.now().isoformat(),
        "estimated_time": "1-2工作日"
    })

@router.get("/list", response_model=APIResponse)
def get_ticket_list(
    user_id: int = Query(...),
    status: str = Query(None),
    type: str = Query(None),
    limit: int = Query(20),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    mock_tickets = [
        {
            "ticket_id": "T20240115103000ABCD",
            "type": "REFUND",
            "title": "申请退款",
            "status": "PROCESSING",
            "created_at": "2024-01-15T10:30:00",
            "order_id": "ORD20240110001"
        },
        {
            "ticket_id": "T20240114152000EFGH",
            "type": "COMPLAINT",
            "title": "投诉服务",
            "status": "RESOLVED",
            "created_at": "2024-01-14T15:20:00",
            "order_id": "ORD20240112002"
        }
    ]
    
    filtered = mock_tickets
    if status:
        filtered = [t for t in filtered if t["status"] == status]
    if type:
        filtered = [t for t in filtered if t["type"] == type]
    
    return APIResponse.success({
        "list": filtered[offset:offset+limit],
        "total": len(filtered),
        "limit": limit,
        "offset": offset
    })

@router.get("/detail", response_model=APIResponse)
def get_ticket_detail(
    ticket_id: str = Query(...),
    db: Session = Depends(get_db)
):
    mock_detail = {
        "ticket_id": ticket_id,
        "user_id": 1,
        "type": "REFUND",
        "title": "申请退款",
        "content": "商品收到后发现有质量问题，申请退款",
        "status": "PROCESSING",
        "order_id": "ORD20240110001",
        "after_sale_no": "AS20240115001",
        "evidence_urls": ["https://example.com/evidence1.jpg"],
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T11:00:00",
        "assignee": "客服小王",
        "history": [
            {"time": "2024-01-15T10:30:00", "action": "创建工单", "operator": "系统"},
            {"time": "2024-01-15T11:00:00", "action": "客服接单", "operator": "客服小王"}
        ]
    }
    
    return APIResponse.success(mock_detail)

@router.put("/update", response_model=APIResponse)
def update_ticket(
    ticket_id: str = Query(...),
    status: str = Query(None),
    assignee: str = Query(None),
    remark: str = Query(None),
    db: Session = Depends(get_db)
):
    return APIResponse.success({
        "ticket_id": ticket_id,
        "status": status or "PROCESSING",
        "assignee": assignee,
        "remark": remark,
        "updated_at": datetime.now().isoformat()
    })

@router.put("/close", response_model=APIResponse)
def close_ticket(
    ticket_id: str = Query(...),
    close_reason: str = Query("用户主动关闭"),
    db: Session = Depends(get_db)
):
    return APIResponse.success({
        "ticket_id": ticket_id,
        "status": "CLOSED",
        "close_reason": close_reason,
        "closed_at": datetime.now().isoformat()
    })
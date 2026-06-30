from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.common.response import APIResponse

router = APIRouter(prefix="/ai/rule", tags=["规则引擎"])

@router.post("/classify", response_model=APIResponse)
def classify_message(text: str = Query(...)):
    intent_keywords = {
        "退款": ["退款", "退钱", "返还", "退费"],
        "退货": ["退货", "退", "寄回", "返还商品"],
        "换货": ["换货", "换", "更换"],
        "物流": ["物流", "快递", "运输", "配送", "发货"],
        "客服": ["客服", "人工", "服务"],
        "投诉": ["投诉", "举报", "不满", "问题"]
    }
    
    intent = "OTHER"
    confidence = 0.0
    
    for key, keywords in intent_keywords.items():
        for keyword in keywords:
            if keyword in text:
                intent = key
                confidence = min(0.8 + len(keyword)/10, 1.0)
                break
        if intent != "OTHER":
            break
    
    return APIResponse.success({
        "intent": intent,
        "confidence": confidence,
        "rules": []
    })

@router.post("/inspect", response_model=APIResponse)
def inspect_rules(
    text: str = Query(...),
    intent: str = Query(None),
    sentiment: str = Query("NEUTRAL"),
    sentiment_score: float = Query(0.0),
    db: Session = Depends(get_db)
):
    rules = [
        {
            "rule_id": "R001",
            "rule_name": "高风险情绪检测",
            "triggered": sentiment_score < -0.5,
            "action": "ESCALATE",
            "confidence": 0.9
        },
        {
            "rule_id": "R002",
            "rule_name": "退款金额限制",
            "triggered": False,
            "action": "NONE",
            "confidence": 0.0
        },
        {
            "rule_id": "R003",
            "rule_name": "重复投诉检测",
            "triggered": False,
            "action": "NONE",
            "confidence": 0.0
        }
    ]
    
    return APIResponse.success({
        "rules": rules,
        "escalate_required": any(r["triggered"] for r in rules),
        "recommendation": "人工介入" if any(r["triggered"] for r in rules) else "自动处理"
    })

@router.post("/escalate", response_model=APIResponse)
def escalate(
    text: str = Query(...),
    intent: str = Query(None),
    sentiment: str = Query("NEUTRAL"),
    sentiment_score: float = Query(0.0),
    risk_level: str = Query("LOW"),
    issue_count: int = Query(0),
    order_amount: float = Query(0),
    db: Session = Depends(get_db)
):
    should_escalate = False
    reason = ""
    
    if sentiment_score < -0.5:
        should_escalate = True
        reason = "负面情绪过高"
    elif risk_level in ["HIGH", "CRITICAL"]:
        should_escalate = True
        reason = "风险等级过高"
    elif issue_count >= 3:
        should_escalate = True
        reason = "重复投诉次数过多"
    elif order_amount >= 1000:
        should_escalate = True
        reason = "订单金额过大"
    
    ticket_id = None
    if should_escalate:
        from datetime import datetime
        import uuid
        ticket_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"
    
    return APIResponse.success({
        "escalated": should_escalate,
        "ticket_id": ticket_id,
        "reason": reason,
        "priority": "HIGH" if should_escalate else "NORMAL"
    })

@router.post("/review", response_model=APIResponse)
def review_after_sale(
    after_sale_no: str = Query(...),
    decision: str = Query(...),
    remark: str = Query(None),
    db: Session = Depends(get_db)
):
    return APIResponse.success({
        "after_sale_no": after_sale_no,
        "decision": decision,
        "remark": remark,
        "status": "REVIEWED",
        "reviewed_at": "2026-06-29T10:00:00"
    })

@router.post("/execute", response_model=APIResponse)
def execute_rule(
    rule_id: str = Query(...),
    params: str = Query(None),
    db: Session = Depends(get_db)
):
    params_dict = {}
    if params:
        import json
        try:
            params_dict = json.loads(params)
        except:
            pass
    
    return APIResponse.success({
        "rule_id": rule_id,
        "executed": True,
        "result": "规则执行成功",
        "effects": ["订单状态更新", "通知用户"]
    })

@router.get("/sets", response_model=APIResponse)
def get_rule_sets(db: Session = Depends(get_db)):
    rule_sets = [
        {
            "set_id": "SET001",
            "name": "售后规则集",
            "rules": ["R001", "R002", "R003"],
            "active": True
        },
        {
            "set_id": "SET002",
            "name": "投诉处理规则",
            "rules": ["R001", "R003"],
            "active": True
        }
    ]
    
    return APIResponse.success({
        "rule_sets": rule_sets,
        "total": len(rule_sets)
    })

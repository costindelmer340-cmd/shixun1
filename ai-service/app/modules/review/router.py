from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.common.response import APIResponse

router = APIRouter(prefix="/review", tags=["评价管理"])

@router.get("/list", response_model=APIResponse)
def get_review_list(
    merchant_id: int = Query(...),
    user_id: int = Query(None),
    platform_code: str = Query(None),
    sentiment: str = Query(None),
    limit: int = Query(20),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    mock_reviews = [
        {
            "id": 1,
            "external_order_id": 1,
            "user_id": 1,
            "merchant_id": 1,
            "platform_code": "DOUYIN",
            "product_score": 4,
            "service_score": 5,
            "content": "商品质量很好，物流也很快，非常满意！",
            "sentiment": "POSITIVE",
            "sentiment_score": 0.92,
            "reviewed_at": "2026-06-20T10:00:00",
            "created_at": "2026-06-20T10:00:00"
        },
        {
            "id": 2,
            "external_order_id": 2,
            "user_id": 1,
            "merchant_id": 1,
            "platform_code": "DOUYIN",
            "product_score": 2,
            "service_score": 3,
            "content": "商品收到时有破损，希望商家改进包装",
            "sentiment": "NEGATIVE",
            "sentiment_score": 0.25,
            "reviewed_at": "2026-06-18T15:30:00",
            "created_at": "2026-06-18T15:30:00"
        }
    ]
    
    filtered = mock_reviews
    if platform_code:
        filtered = [r for r in filtered if r["platform_code"] == platform_code]
    if sentiment:
        filtered = [r for r in filtered if r["sentiment"] == sentiment]
    
    return APIResponse.success({
        "list": filtered[offset:offset+limit],
        "total": len(filtered),
        "limit": limit,
        "offset": offset
    })

@router.get("/stats", response_model=APIResponse)
def get_review_stats(
    merchant_id: int = Query(...),
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: Session = Depends(get_db)
):
    return APIResponse.success({
        "total_count": 156,
        "positive_count": 120,
        "negative_count": 18,
        "neutral_count": 18,
        "avg_product_score": 4.5,
        "avg_service_score": 4.6,
        "avg_sentiment_score": 0.78,
        "daily_trend": [
            {"date": "2026-06-20", "count": 12, "positive_rate": 0.83},
            {"date": "2026-06-21", "count": 8, "positive_rate": 0.75},
            {"date": "2026-06-22", "count": 15, "positive_rate": 0.93},
            {"date": "2026-06-23", "count": 10, "positive_rate": 0.80},
            {"date": "2026-06-24", "count": 14, "positive_rate": 0.86},
            {"date": "2026-06-25", "count": 9, "positive_rate": 0.78},
            {"date": "2026-06-26", "count": 11, "positive_rate": 0.82}
        ],
        "top_keywords": ["质量", "物流", "客服", "包装", "发货"],
        "risk_issues": ["包装破损", "发货延迟"]
    })
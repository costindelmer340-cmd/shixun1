from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class SendMessageRequest(BaseModel):
    merchant_id: int
    user_id: int
    message: str
    conversation_id: Optional[int] = None
    order_id: Optional[int] = None
    order_no: Optional[str] = None

class MessageResponse(BaseModel):
    conversation_id: int
    response: str
    intent: str
    confidence: float
    sentiment: str
    sentiment_score: float
    topics: List[str]
    escalate: bool = False

class ConversationResponse(BaseModel):
    id: int
    conversation_no: str
    user_id: int
    merchant_id: int
    external_order_id: Optional[int] = None
    status: str
    last_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
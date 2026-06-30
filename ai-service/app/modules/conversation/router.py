from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.modules.conversation.service import ConversationService
from app.modules.conversation.schema import SendMessageRequest
from app.common.response import APIResponse

router = APIRouter(prefix="/conversation", tags=["会话管理"])

@router.post("/send", response_model=APIResponse)
def send_message(request: SendMessageRequest, db: Session = Depends(get_db)):
    service = ConversationService(db)
    return service.send_message(request)

@router.get("/list", response_model=APIResponse)
def get_conversation_list(
    user_id: int = Query(...),
    order_no: str = Query(None),
    db: Session = Depends(get_db)
):
    service = ConversationService(db)
    if order_no:
        return service.get_conversation_by_user_and_order(user_id, order_no)
    return service.get_conversations(user_id)

@router.get("/messages", response_model=APIResponse)
def get_conversation_messages(
    conversation_id: int = Query(...),
    db: Session = Depends(get_db)
):
    service = ConversationService(db)
    return service.get_conversation_messages(conversation_id)

@router.get("/{conversation_no}", response_model=APIResponse)
def get_conversation_detail(
    conversation_no: str,
    db: Session = Depends(get_db)
):
    service = ConversationService(db)
    return service.get_conversation_by_no(conversation_no)

@router.put("/close", response_model=APIResponse)
def close_conversation(
    conversation_id: int = Query(...),
    close_reason: str = Query("用户主动关闭"),
    db: Session = Depends(get_db)
):
    service = ConversationService(db)
    return service.close_conversation(conversation_id, close_reason)
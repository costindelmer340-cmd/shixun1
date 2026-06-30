from sqlalchemy.orm import Session
from app.modules.conversation.model import Conversation, ChatMessage
from typing import Optional, List
from datetime import datetime

class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        return self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.deleted == False
        ).first()
    
    def get_conversation_by_no(self, conversation_no: str) -> Optional[Conversation]:
        return self.db.query(Conversation).filter(
            Conversation.conversation_no == conversation_no,
            Conversation.deleted == False
        ).first()
    
    def get_user_conversations(self, user_id: int, limit: int = 20) -> List[Conversation]:
        return self.db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.deleted == False
        ).order_by(Conversation.updated_at.desc()).limit(limit).all()
    
    def get_conversation_by_user_and_order(self, user_id: int, order_no: str) -> Optional[Conversation]:
        return self.db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.external_order_no == order_no,
            Conversation.deleted == False,
            Conversation.status != "CLOSED"
        ).first()
    
    def create_conversation(self, user_id: int, merchant_id: int, order_id: Optional[int] = None, order_no: Optional[str] = None) -> Conversation:
        conversation_no = f"CV-{merchant_id}-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        conversation = Conversation(
            conversation_no=conversation_no,
            user_id=user_id,
            merchant_id=merchant_id,
            external_order_id=order_id,
            external_order_no=order_no,
            status="AI_SERVING",
            source="MINIAPP"
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation
    
    def update_conversation(self, conversation_id: int, last_message: str) -> bool:
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.last_message = last_message[:512]
            conversation.updated_at = datetime.now()
            self.db.commit()
            return True
        return False
    
    def add_message(self, conversation_id: int, sender_type: str, sender_id: int, content: str,
                   confidence: Optional[str] = None, ai_generated: bool = False) -> ChatMessage:
        message = ChatMessage(
            conversation_id=conversation_id,
            sender_type=sender_type,
            sender_id=sender_id,
            message_type="TEXT",
            content=content,
            ai_confidence=confidence,
            ai_generated=ai_generated
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_conversation_messages(self, conversation_id: int) -> List[ChatMessage]:
        return self.db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id,
            ChatMessage.deleted == False
        ).order_by(ChatMessage.created_at.asc()).all()
    
    def close_conversation(self, conversation_id: int, close_reason: str) -> bool:
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.status = "CLOSED"
            conversation.closed_at = datetime.now()
            self.db.commit()
            return True
        return False
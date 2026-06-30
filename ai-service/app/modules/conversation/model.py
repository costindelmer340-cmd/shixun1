from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base

class Conversation(Base):
    __tablename__ = "customer_conversation"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_no = Column(String(64), unique=True)
    user_id = Column(Integer)
    merchant_id = Column(Integer)
    external_order_id = Column(Integer)
    external_order_no = Column(String(64))
    assigned_staff_id = Column(Integer)
    source = Column(String(32), default="MINIAPP")
    status = Column(String(32), default="AI_SERVING")
    last_message = Column(String(512))
    last_message_at = Column(DateTime)
    ai_intent = Column(String(64))
    ai_summary = Column(String(512))
    transferred_at = Column(DateTime)
    closed_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted = Column(Boolean, default=False)

class ChatMessage(Base):
    __tablename__ = "chat_message"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer)
    sender_id = Column(Integer)
    sender_type = Column(String(32))
    message_type = Column(String(32), default="TEXT")
    content = Column(String(2048))
    media_url = Column(String(512))
    ai_generated = Column(Boolean, default=False)
    ai_confidence = Column(String(32))
    read_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted = Column(Boolean, default=False)
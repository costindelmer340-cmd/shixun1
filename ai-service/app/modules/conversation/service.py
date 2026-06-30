from sqlalchemy.orm import Session
from app.modules.conversation.repository import ConversationRepository
from app.modules.conversation.schema import SendMessageRequest, MessageResponse, ConversationResponse
from app.common.response import APIResponse
from typing import List

try:
    from modules.llm_client import llm_client
except ImportError:
    llm_client = None

class ConversationService:
    def __init__(self, db: Session):
        self.repo = ConversationRepository(db)
    
    def send_message(self, request: SendMessageRequest):
        conversation = None
        
        if request.conversation_id:
            conversation = self.repo.get_conversation(request.conversation_id)
        
        if not conversation and request.order_no:
            conversation = self.repo.get_conversation_by_user_and_order(request.user_id, request.order_no)
        
        if not conversation:
            conversation = self.repo.create_conversation(
                user_id=request.user_id,
                merchant_id=request.merchant_id,
                order_id=request.order_id,
                order_no=request.order_no
            )
        
        self.repo.add_message(
            conversation_id=conversation.id,
            sender_type="user",
            sender_id=request.user_id,
            content=request.message,
            ai_generated=False
        )
        
        message = request.message
        intent = "OTHER"
        confidence = 0.8
        sentiment = "neutral"
        sentiment_score = 0.5
        topics = []
        escalate = False
        response_text = "您好，很高兴为您服务！请问有什么可以帮助您的？"
        
        use_llm = llm_client and llm_client.is_configured()
        
        if use_llm:
            try:
                llm_response = llm_client.chat_completion([
                    {"role": "system", "content": "你是一名专业的电商售后客服智能助手，请根据用户的问题提供友好、专业、准确的回复。"},
                    {"role": "user", "content": message}
                ])
                if llm_response:
                    response_text = llm_response
                else:
                    use_llm = False
            except Exception as e:
                use_llm = False
        
        if not use_llm:
            if "退款" in message or "退货" in message or "售后" in message:
                intent = "REFUND"
                response_text = "关于退款问题，您可以在订单详情页申请售后。审核通过后，按照指引寄回商品即可获得退款。"
            elif "物流" in message or "快递" in message or "到货" in message:
                intent = "LOGISTICS"
                response_text = "关于物流问题，您的订单正在配送中。如需查询具体进度，可以在订单详情页查看物流信息。"
            elif "投诉" in message or "差评" in message or "不好" in message:
                intent = "COMPLAINT"
                sentiment = "negative"
                sentiment_score = 0.8
                escalate = True
                response_text = "检测到您的问题较为复杂，已为您转接人工客服。人工客服将在几分钟内接入，请描述需要处理的问题。"
            elif "人工" in message or "真人客服" in message or "转人工" in message:
                intent = "ESCALATE"
                escalate = True
                response_text = "已为您转接人工客服，人工客服将在几分钟内接入。"
            elif "换货" in message:
                intent = "EXCHANGE"
                response_text = "关于换货问题，请在订单详情页申请售后，选择换货服务，填写换货原因提交即可。"
            elif "发票" in message:
                intent = "INVOICE"
                response_text = "关于发票问题，您可以在订单详情页申请开具发票，电子发票将在1-3个工作日内发送到您的邮箱。"
        
        self.repo.add_message(
            conversation_id=conversation.id,
            sender_type="ai",
            sender_id=0,
            content=response_text,
            confidence=str(confidence),
            ai_generated=True
        )
        
        self.repo.update_conversation(conversation.id, request.message)
        
        response = MessageResponse(
            conversation_id=conversation.id,
            response=response_text,
            intent=intent,
            confidence=confidence,
            sentiment=sentiment,
            sentiment_score=sentiment_score,
            topics=topics,
            escalate=escalate
        )
        
        return APIResponse.success(response)
    
    def get_conversations(self, user_id: int):
        conversations = self.repo.get_user_conversations(user_id)
        response = [ConversationResponse.from_orm(c) for c in conversations]
        return APIResponse.success(response)
    
    def get_conversation_by_user_and_order(self, user_id: int, order_no: str):
        conversation = self.repo.get_conversation_by_user_and_order(user_id, order_no)
        if not conversation:
            return APIResponse.success(None)
        return APIResponse.success(ConversationResponse.from_orm(conversation))
    
    def get_conversation_messages(self, conversation_id: int):
        messages = self.repo.get_conversation_messages(conversation_id)
        response = []
        for msg in messages:
            response.append({
                "id": msg.id,
                "conversation_id": msg.conversation_id,
                "sender_type": msg.sender_type,
                "sender_id": msg.sender_id,
                "content": msg.content,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            })
        return APIResponse.success(response)
    
    def get_conversation_by_no(self, conversation_no: str):
        conversation = self.repo.get_conversation_by_no(conversation_no)
        if not conversation:
            return APIResponse.not_found("会话不存在")
        return APIResponse.success(ConversationResponse.from_orm(conversation))
    
    def close_conversation(self, conversation_id: int, close_reason: str):
        conversation = self.repo.get_conversation(conversation_id)
        if not conversation:
            return APIResponse.not_found("会话不存在")
        
        self.repo.close_conversation(conversation_id, close_reason)
        return APIResponse.success({"conversation_id": conversation_id, "status": "CLOSED", "close_reason": close_reason})

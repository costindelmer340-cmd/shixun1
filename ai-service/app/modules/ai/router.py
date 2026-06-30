from fastapi import APIRouter, Query
from app.modules.ai.intent_recognizer import intent_recognizer
from app.modules.ai.sentiment_analyzer import sentiment_analyzer
from app.modules.ai.rag_generator import rag_generator
from app.common.response import APIResponse

router = APIRouter(prefix="/ai", tags=["AI服务"])

@router.post("/chat", response_model=APIResponse)
def chat(
    merchant_id: int = Query(None),
    user_id: int = Query(None),
    message: str = Query(...),
    conversation_id: str = Query(None),
    order_id: int = Query(None),
    context: str = Query(None)
):
    intent_result = intent_recognizer.recognize(message)
    response_text = rag_generator.generate_response(intent_result.intent, message)
    
    return APIResponse.success({
        "conversation_id": conversation_id,
        "response": response_text,
        "intent": {
            "intent": intent_result.intent,
            "confidence": intent_result.confidence,
            "entities": intent_result.entities
        },
        "context": context,
        "message_id": f"msg_{hash(message)}"
    })

@router.post("/intent", response_model=APIResponse)
def analyze_intent(query: str = Query(...)):
    result = intent_recognizer.recognize(query)
    return APIResponse.success({
        "intent": result.intent,
        "confidence": result.confidence,
        "entities": result.entities
    })

@router.post("/sentiment", response_model=APIResponse)
def analyze_sentiment(text: str = Query(...)):
    result = sentiment_analyzer.analyze(text)
    return APIResponse.success({
        "sentiment": result.sentiment,
        "score": result.score
    })

@router.post("/topic", response_model=APIResponse)
def extract_topic(text: str = Query(...)):
    topics = []
    keywords = ["订单", "退款", "退货", "换货", "物流", "客服", "问题", "投诉"]
    for keyword in keywords:
        if keyword in text:
            topics.append(keyword)
    
    return APIResponse.success({
        "topics": topics if topics else ["其他"],
        "topic_keywords": topics
    })

@router.post("/rag", response_model=APIResponse)
def rag_query(
    question: str = Query(...),
    intent: str = Query(None)
):
    if intent:
        response = rag_generator.generate_response(intent, question)
    else:
        intent_result = intent_recognizer.recognize(question)
        response = rag_generator.generate_response(intent_result.intent, question)
    
    return APIResponse.success({
        "answer": response,
        "source": "faq_knowledge",
        "references": []
    })
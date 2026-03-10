from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.chatbot import ChatbotAskRequest, ChatbotAskResponse, RetrievedContext
from app.services.rag_chatbot import rag_chatbot_service

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


@router.post("/ask", response_model=ChatbotAskResponse)
def ask_chatbot(
    payload: ChatbotAskRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    rag_chatbot_service.sync_knowledge_base(db)
    contexts = rag_chatbot_service.retrieve(payload.question, top_k=payload.top_k)
    answer = rag_chatbot_service.generate_answer(payload.question, contexts)

    return ChatbotAskResponse(
        answer=answer,
        contexts=[
            RetrievedContext(
                id=item["id"],
                title=item["title"],
                source_type=item["source_type"],
                score=item["score"],
            )
            for item in contexts
        ],
    )

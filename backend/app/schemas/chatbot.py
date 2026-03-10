from pydantic import BaseModel


class ChatbotAskRequest(BaseModel):
    question: str
    top_k: int = 3


class RetrievedContext(BaseModel):
    id: int
    title: str
    source_type: str
    score: float


class ChatbotAskResponse(BaseModel):
    answer: str
    contexts: list[RetrievedContext]

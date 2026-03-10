from fastapi import APIRouter

from app.api.v1.endpoints import auth, chatbot, complaints, departments, queries

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(complaints.router)
api_router.include_router(queries.router)
api_router.include_router(departments.router)

api_router.include_router(chatbot.router)

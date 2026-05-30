"""Aggregates all v1 routers."""

from fastapi import APIRouter

from app.api.v1.routes import health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])

# Future routers (added per milestone):
# api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
# api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
# api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

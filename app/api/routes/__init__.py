from fastapi import APIRouter

from app.api.routes.webhook import router as webhook_router

api_router = APIRouter()
api_router.include_router(webhook_router)

__all__ = ["api_router"]

from fastapi import APIRouter
from .endpoints import ai, users, analytics, blockchains, agents, payments, image, voice, documents

api_router = APIRouter()
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(blockchains.router, prefix="/blockchains", tags=["blockchains"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(image.router, prefix="/image", tags=["image"])
api_router.include_router(voice.router, prefix="/voice", tags=["voice"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])

from fastapi import APIRouter, Depends, HTTPException
from app.services.payments import create_subscription_checkout, handle_stripe_webhook
from app.core.config import STRIPE_WEBHOOK_SECRET

router = APIRouter()

@router.post("/subscribe/{plan}")
async def subscribe(telegram_id: int, plan: str):
    checkout_url = await create_subscription_checkout(telegram_id, plan)
    return {"checkout_url": checkout_url}

@router.post("/webhook")
async def stripe_webhook(payload: bytes, sig_header: str):
    await handle_stripe_webhook(payload, sig_header)
    return {"status": "success"}
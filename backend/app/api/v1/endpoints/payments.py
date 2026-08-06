from fastapi import APIRouter, Depends, HTTPException
from app.services.payments import create_subscription_checkout, handle_stripe_webhook
from app.core.config import STRIPE_WEBHOOK_SECRET

router = APIRouter()

@router.post("/subscribe/{plan}")
async def subscribe(telegram_id: int, plan: str):
    try:
        checkout_url = await create_subscription_checkout(telegram_id, plan)
        return {"checkout_url": checkout_url}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Платёжный сервис не настроен: {e}")

@router.post("/webhook")
async def stripe_webhook(payload: bytes, sig_header: str):
    try:
        await handle_stripe_webhook(payload, sig_header)
        return {"status": "success"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Платёжный сервис не настроен: {e}")

import stripe
from app.core.config import STRIPE_API_KEY
from app.models.user import User
from app.core.database import get_db
from fastapi import HTTPException

# Инициализация Stripe
stripe.api_key = STRIPE_API_KEY

# Создание сессии оплаты для подписки
async def create_subscription_checkout(user_id: int, plan: str) -> str:
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Цены для тарифов (тестовые)
    prices = {
        "pro": "price_1P...",  # Замените на реальный ID цены в Stripe
        "enterprise": "price_1P..."
    }
    
    if plan not in prices:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": prices[plan],
                "quantity": 1,
            }],
            mode="subscription",
            success_url="https://t.me/your_bot?success=true",
            cancel_url="https://t.me/your_bot?canceled=true",
            client_reference_id=str(user.telegram_id),
        )
        return checkout_session.url
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Платёжный сервис Stripe не настроен: {e}")

# Обработка вебхука Stripe
async def handle_stripe_webhook(payload: bytes, sig_header: str) -> None:
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    db = next(get_db())
    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = int(session["client_reference_id"])
        user = db.query(User).filter(User.telegram_id == user_id).first()
        
        if user:
            user.subscription_plan = "pro" if "pro" in session["subscription"] else "enterprise"
            db.commit()
    
    elif event["type"] == "invoice.payment_failed":
        session = event["data"]["object"]
        user_id = int(session["client_reference_id"])
        user = db.query(User).filter(User.telegram_id == user_id).first()
        
        if user:
            user.subscription_plan = "free"
            db.commit()
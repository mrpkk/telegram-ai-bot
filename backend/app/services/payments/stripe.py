import stripe
from app.core.config import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY

class StripeClient:
    @staticmethod
    async def create_subscription(user_id: str, plan: str) -> str:
        prices = {
            "pro": "price_123",
            "enterprise": "price_456"
        }
        
        session = stripe.checkout.Session.create(
            customer_email=user_id,
            payment_method_types=["card"],
            line_items=[{
                "price": prices[plan],
                "quantity": 1
            }],
            mode="subscription",
            success_url="https://yourdomain.com/success",
            cancel_url="https://yourdomain.com/cancel"
        )
        
        return session.url
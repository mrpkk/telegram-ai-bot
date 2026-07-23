import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/telegram_ai_bot")

# Stripe
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Crypto Payments
CRYPTO_WALLET_ADDRESS = os.getenv("CRYPTO_WALLET_ADDRESS")

# DeFi
WEB3_PROVIDER_URL = os.getenv("WEB3_PROVIDER_URL", "https://mainnet.infura.io/v3/YOUR_KEY")

# Blockchains
TON_RPC_URL = os.getenv("TON_RPC_URL", "https://toncenter.com/api/v2/jsonRPC")
COSMOS_RPC_URL = os.getenv("COSMOS_RPC_URL", "https://lcd-cosmoshub.keplr.app")
SUI_RPC_URL = os.getenv("SUI_RPC_URL", "https://fullnode.mainnet.sui.io")
APTOS_RPC_URL = os.getenv("APTOS_RPC_URL", "https://fullnode.mainnet.aptoslabs.com")
ROTKI_API_URL = os.getenv("ROTKI_API_URL", "http://localhost:8080")
ROTKI_API_KEY = os.getenv("ROTKI_API_KEY", "your_rotki_api_key")

# Voice & Image
WHISPER_API_KEY = os.getenv("WHISPER_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
DALLE_API_KEY = os.getenv("DALLE_API_KEY")

# Compliance
SUMSUB_API_URL = os.getenv("SUMSUB_API_URL", "https://api.sumsub.com")
SUMSUB_API_KEY = os.getenv("SUMSUB_API_KEY")

# Paths
DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "../../data/documents")
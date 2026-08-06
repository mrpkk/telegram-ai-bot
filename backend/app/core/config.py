import os
from pathlib import Path
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
CHROMA_PATH = Path(os.getenv("CHROMA_PATH", os.path.join(os.path.dirname(__file__), "../../../data/chroma"))).resolve()

# Admin (Basic Auth)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
ADMIN_IDS = [int(x) for x in os.getenv("TELEGRAM_ADMIN_IDS", "").split(",") if x.strip()]
DOCUMENTS_PATH = Path(os.getenv("DOCUMENTS_PATH", os.path.join(os.path.dirname(__file__), "../../../data/documents"))).resolve()

# Public RPC endpoints (без ключей, для демо)
ETH_RPC_URL = os.getenv("ETH_RPC_URL", "https://ethereum-rpc.publicnode.com")
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
TON_API_URL = os.getenv("TON_API_URL", "https://toncenter.com/api/v2")
COSMOS_REST_URL = os.getenv("COSMOS_REST_URL", "https://cosmos-rest.publicnode.com")
SUI_RPC_URL = os.getenv("SUI_RPC_URL", "https://fullnode.mainnet.sui.io")
APTOS_API_URL = os.getenv("APTOS_API_URL", "https://fullnode.mainnet.aptoslabs.com/v1")

# DeFi (для yield-агента)
DEFILLAMA_YIELDS_URL = os.getenv("DEFILLAMA_YIELDS_URL", "https://yields.llama.fi/pools")

# Aave
AAVE_LENDING_POOL_ADDRESS = os.getenv("AAVE_LENDING_POOL_ADDRESS", "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2")
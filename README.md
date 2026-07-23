# Telegram AI Bot

**AI-powered Telegram bot with RAG, DeFi integration, multi-language support, and payment systems.**

## Features
- **Multi-language support** (English, Russian, Spanish, Chinese, and more)
- **RAG system** for document processing (PDF, Excel, DOCX, TXT, MD)
- **DeFi integration** (wallet connection, balance check, swaps, staking)
- **Subscription system** (Free, Pro, Enterprise)
- **Payment integration** (Stripe, Crypto)
- **Admin panel** for user management and analytics
- **Voice messages** (speech-to-text and text-to-speech)
- **Image processing** (OCR, image generation)

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/mrpkk/telegram-ai-bot.git
   cd telegram-ai-bot
   ```

2. Create `.env` file:
   ```ini
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   OPENAI_API_KEY=your_openai_api_key
   DATABASE_URL=postgresql://user:password@localhost:5432/telegram_ai_bot
   STRIPE_API_KEY=your_stripe_api_key
   CRYPTO_WALLET_ADDRESS=your_crypto_wallet_address
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run with Docker:
   ```bash
   docker-compose up --build
   ```

## Usage
### Commands
- `/start` — Show welcome message
- `/ask` — Ask a question to AI
- `/language` — Change language
- `/wallet` — Connect your wallet (MetaMask, WalletConnect)
- `/balance` — Check your balance
- `/swap` — Swap tokens (Uniswap, 1inch)
- `/stake` — Stake tokens (Lido, Aave)
- `/subscribe` — Manage your subscription

### Subscription Plans
| Plan        | Price       | Features                                                                 |
|-------------|-------------|--------------------------------------------------------------------------|
| **Free**    | Free        | 10 requests/day                                                          |
| **Pro**     | $9.99/month | 100 requests/day + DeFi integration                                      |
| **Enterprise** | $49.99/month | Unlimited requests + priority support + custom AI models                |

## Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    Telegram AI Bot                     │
│  (aiogram, FastAPI, SQLAlchemy, PostgreSQL, Redis)     │
└──────────────────────────┬──────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  FastAPI    │
                    │  (Backend)  │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
   ┌──────▼──────┐  ┌─────▼─────┐  ┌──────▼──────┐
   │  AI Agent   │  │ DeFi Agent│  │ Payment Agent│
   │ (RAG, LLM)  │  │ (Web3.py) │  │ (Stripe)    │
   └─────────────┘  └───────────┘  └─────────────┘
                           │
                    ┌──────▼──────┐
                    │  PostgreSQL │
                    │  (Database) │
                    └─────────────┘
```

## Tech Stack
| Component          | Technology                                                                 |
|-------------------|----------------------------------------------------------------------------|
| **Backend**        | FastAPI (Python)                                                          |
| **Telegram Bot**   | aiogram 3.0                                                               |
| **AI**            | OpenAI API (GPT-4o), Whisper (STT), ElevenLabs (TTS)                     |
| **RAG**           | LlamaIndex + ChromaDB                                                     |
| **DeFi**          | Web3.py (Ethereum, Solana, TON)                                          |
| **Payments**      | Stripe (Fiat), Crypto (USDT, ETH)                                        |
| **Database**      | PostgreSQL (Relational), Redis (Caching)                                 |
| **Analytics**     | Prometheus + Grafana, Metabase                                           |
| **CI/CD**         | GitHub Actions                                                            |

## Admin Panel
- **User Management**: View and edit user profiles, block users
- **Subscription Management**: View and manage subscriptions
- **Analytics Dashboard**: Monitor usage, popular queries, response times
- **Document Management**: Upload, delete, and organize documents for RAG
- **System Monitoring**: View logs, errors, and performance metrics

## License
MIT
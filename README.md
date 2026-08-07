# TG RAG Bot — Telegram RAG-бот для корпоративных документов

**Ваш Telegram-бот, который читает документы и отвечает на вопросы.**
Загрузите PDF, Excel, DOCX — и задавайте вопросы на естественном языке.

Бот: **[@TgBotAiQ_bot](https://t.me/TgBotAiQ_bot)**

## ✨ Что умеет

- 🧠 **AI-чат** — свободные вопросы на русском и английском (Mistral AI)
- 📄 **RAG по документам** — PDF, Excel (XLSX/XLS), DOCX, TXT, MD
- 📷 **OCR** — распознавание текста с фотографий (Tesseract rus+eng)
- 🌐 **Блокчейн-модуль** — живые балансы в 6 сетях (ETH, SOL, TON, Cosmos, Sui, Aptos)
- 📈 **Финансовые агенты** — VaR, стресс-тесты, подбор DeFi-доходности (DeFiLlama)
- 🎛️ **Кнопки меню** — возможности, тарифы, примеры вопросов, шаблон договора
- 📊 **Админ-панель** — аналитика, логи, управление документами, экспорт CSV/Excel
- 🔐 **API** — FastAPI бэкенд для интеграций со Swagger-документацией

## 🎮 Команды бота

```
/start      — запустить, главное меню
/ask <вопрос>  — задать вопрос AI
/balance <адрес>  — баланс в сети (автоопределение: ETH/SOL/TON/Cosmos/Sui/Aptos)
/risk [сумма]  — стресс-тест портфеля
/yield [сеть]  — топ DeFi-доходности
/features   — все возможности
/pricing    — тарифы
/about      — о боте
/demo       — шпаргалка для владельца (только админ)
```

Отправьте боту **фото** — распознает текст (OCR).

## 🧠 Технологии

| Компонент | Технология |
|-----------|-----------|
| **Бот** | Aiogram 3.x (Python) |
| **Бэкенд** | FastAPI + SQLAlchemy |
| **RAG** | Гибридный поиск: BM25 + векторный (ChromaDB) |
| **AI** | Mistral AI (бесплатный тариф 500k req/min) |
| **OCR** | Tesseract 5 (локально, rus+eng) |
| **Блокчейн** | RPC-клиенты ETH/SOL/TON/Cosmos/Sui/Aptos |
| **Доходность** | DeFiLlama API (без ключей) |
| **Векторная БД** | ChromaDB (встроенная) |
| **БД** | SQLite |
| **Транспорт** | SOCKS5 через Tor (обход блокировок Telegram в РФ) |

## ⚡ Быстрый запуск

```bash
# 1. Клонировать
git clone <repo-url>
cd telegram-ai-bot

# 2. Установить
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# 3. Настроить .env
cat > .env << EOF
TELEGRAM_BOT_TOKEN=your_bot_token
MISTRAL_API_KEY=your_mistral_key
DATABASE_URL=sqlite:///bot.db
EOF

# 4. Запустить (FastAPI + бот в фоне)
python backend/app/main.py
```

## 📦 Варианты использования

| Сценарий | Пример |
|----------|--------|
| **HR-политики** | «Сколько дней отпуска положено?» |
| **Юридические документы** | «Что сказано в договоре про расторжение?» |
| **База знаний** | «Как настроить VPN по инструкции?» |
| **Техническая документация** | «Какие параметры у API эндпоинта?» |
| **OCR** | Сфотографировать документ → получить текст |
| **Крипто** | /balance 0x... → баланс ETH в реальном времени |

## 🔌 API

```
POST /api/v1/ai/ask     — задать вопрос
POST /api/v1/image/ocr  — распознать текст с изображения
GET  /api/v1/blockchains/{chain}/balance/{address} — баланс (6 сетей)
GET  /api/v1/agents/risk/var — Value at Risk
GET  /api/v1/agents/risk/stress-test — стресс-тест
POST /api/v1/agents/yield/optimize — DeFi-доходность
POST /admin/upload      — загрузить документ в базу знаний
GET  /admin/stats       — статистика
GET  /admin/export      — экспорт логов (CSV/Excel)
```

Полная документация: `/docs` (Swagger) после запуска.

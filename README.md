# 🤖 Telegram AI-Бот с RAG и Админ-панелью

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.39-FF4B4B?style=flat&logo=streamlit)](https://streamlit.io)
[![Mistral AI](https://img.shields.io/badge/Mistral_AI-FREE-orange?style=flat)](https://mistral.ai)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat&logo=docker)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Готовый к продаже Telegram-бот с RAG-системой, админ-панелью и аналитикой

## 🎯 Что это?

Коммерческий IT-продукт — Telegram-бот с ИИ, который:
- Обучается на документах клиента (PDF, DOCX, TXT, веб-страницы)
- Отвечает на вопросы 24/7 с указанием источников
- Имеет админ-панель для управления без программиста
- Содержит систему аналитики

**Цена на фриланс-биржах:** $500–2000 за внедрение + $100–500/мес поддержка

## 🏗 Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                    Telegram Bot                          │
│              (python-telegram-bot v20+)                  │
└──────────────────────────┬──────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  FastAPI    │
                    │  (Бэкенд)   │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
   ┌──────▼──────┐  ┌─────▼─────┐  ┌──────▼──────┐
   │  ChromaDB   │  │  SQLite   │  │  Mistral AI │
   │ (векторная) │  │ (реляц.)  │  │ (LLM+Emb)   │
   └─────────────┘  └───────────┘  └─────────────┘
                           │
                    ┌──────▼──────┐
                    │ Streamlit   │
                    │ (Админка)   │
                    └─────────────┘
```

## 📦 Стек технологий

| Компонент | Технология | Стоимость |
|-----------|-----------|-----------|
| 🧠 LLM | Mistral Small (mistral.ai) | **FREE** 500k req/min |
| 🔢 Эмбеддинги | Mistral Embed (mistral.ai) | **FREE** |
| 🗄️ Векторная БД | ChromaDB | **FREE** |
| 🌐 Бэкенд | FastAPI | **FREE** |
| 🤖 Telegram | python-telegram-bot | **FREE** |
| 📊 Админка | Streamlit | **FREE** |
| 🐳 Контейнеры | Docker Compose | **FREE** |

## 🚀 Быстрый старт

### 1. Клонирование

```bash
git clone https://github.com/mrpkk/telegram-ai-bot.git
cd telegram-ai-bot
```

### 2. Настройка

```bash
cp .env.example .env
```

Заполните в `.env`:
- `TELEGRAM_BOT_TOKEN` — получите у [@BotFather](https://t.me/BotFather)
- `MISTRAL_API_KEY` — ключ Mistral AI (уже настроен)

### 3. Запуск

```bash
docker-compose up -d
```

### 4. Открытие

- **Бот:** t.me/ваш_бот
- **Админка:** http://localhost:8501
- **API:** http://localhost:8000/docs

## 📁 Структура проекта

```
telegram-ai-bot/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI сервер
│   │   ├── bot.py           # Telegram-бот
│   │   ├── rag.py           # RAG-система
│   │   ├── admin.py         # API для админки
│   │   ├── models.py        # Модели данных
│   │   └── config.py        # Конфигурация
│   ├── chroma_db/           # Векторная БД
│   ├── data/                # Документы и SQLite
│   ├── requirements.txt
│   └── Dockerfile
├── admin_panel/
│   ├── streamlit_app.py     # Админ-панель
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🎮 Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Приветствие с меню |
| `/help` | Список команд |
| `/stats` | Статистика (только админы) |
| *текст* | Вопрос к AI |

## 📊 Админ-панель

- 📁 **Документы** — загрузка, просмотр, удаление
- 💬 **FAQ** — добавление вопросов-ответов
- 📈 **Аналитика** — графики, топ вопросов, точность
- 📜 **Логи** — история запросов
- ⚙️ **Настройки** — конфигурация бота

## 💬 Пример диалога

```
Пользователь: Какова политика возврата?

Бот: Согласно политике возврата, вы можете вернуть товар 
в течение 14 дней с момента покупки. Возврат осуществляется 
при наличии чека и сохранённого товарного вида.

📎 Источник: policy_return.pdf
⏱️ Время ответа: 1250ms

[👍 Полезно] [👎 Не полезно]
```

## 💰 Коммерческое использование

### Модель монетизации

| Пакет | Цена | Что входит |
|-------|------|------------|
| **Базовый** | $500 | Telegram-бот + 5 PDF + деплой |
| **Стандарт** | $1000 | + Админка + аналитика + документация |
| **Премиум** | $2000 | + CRM-интеграция + обучение + поддержка 3 мес |
| **Поддержка** | $200/мес | Обновления, техподдержка, новые фичи |

### Клиенты

- Интернет-магазины (ответы про товары, доставку)
- Онлайн-школы (консультации студентов)
- B2B-услуги (обработка заявок)

## ⚙️ Конфигурация

| Переменная | По умолчанию | Описание |
|-----------|-------------|----------|
| `DEFAULT_MODEL` | mistral-small-latest | Модель для генерации |
| `EMBEDDING_MODEL` | mistral-embed | Модель эмбеддингов |
| `COMPANY_NAME` | Моя Компания | Название для приветствия |
| `ADMIN_USERNAME` | admin | Логин админки |

## 📄 Лицензия

MIT License

---

**Создано с помощью:** Mistral AI + FastAPI + LangChain + Streamlit + Docker

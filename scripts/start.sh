#!/usr/bin/env bash
# Единый источник секретов: ~/.env (без полного source — там битая строка 159)
get_env() { grep -m1 "^$1=" /home/iamthat/.env | cut -d= -f2- | sed 's/^"\(.*\)"$/\1/'; }

export TELEGRAM_BOT_TOKEN="$(get_env TG_TGBOTAIQ_BOT)"
export MISTRAL_API_KEY="$(get_env MISTRAL_API_KEY)"
export TG_PROXY="$(get_env TG_PROXY)"

cd "$(dirname "$0")/.."
export PYTHONPATH="$(pwd)/backend:$(pwd)"
# Единая точка: FastAPI-бэкенд сам поднимает бота в lifespan (см. app/main.py)
exec python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8007

#!/bin/bash
# Запуск telegram-ai-bot (порт 8007) — FastAPI + Mistral через Tor
# Секреты НЕ хардкодим: читаются systemd через EnvironmentFile (~/.env + telegram-ai-bot/.env)
cd /home/iamthat/telegram-ai-bot
exec /home/iamthat/telegram-ai-bot/.venv/bin/python3 -c "
import sys
sys.path.insert(0, 'backend')
sys.path.insert(0, '.')
import uvicorn
from app.main import app
uvicorn.run(app, host='127.0.0.1', port=8007)
"

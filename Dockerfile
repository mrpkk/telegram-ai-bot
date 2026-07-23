FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Установить переменные окружения
ENV PYTHONPATH=/app/backend

# Исправить импорты в main.py
RUN sed -i 's/from config import DB_PATH/from app.config import DB_PATH/' /app/backend/app/main.py && \
    sed -i 's/from models import init_db/from app.models import init_db/' /app/backend/app/main.py && \
    sed -i 's/from models import DB_PATH as db_path/from app.config import DB_PATH as db_path/' /app/backend/app/main.py && \
    sed -i 's/import models/import app.models/' /app/backend/app/main.py && \
    sed -i '/DB_PATH = DB_PATH/d' /app/backend/app/main.py && \
    sed -i 's/from admin import router as admin_router/from app.admin import router as admin_router/' /app/backend/app/main.py && \
    sed -i 's/from config import ADMIN_USERNAME, ADMIN_PASSWORD, DOCUMENTS_PATH/from app.config import ADMIN_USERNAME, ADMIN_PASSWORD, DOCUMENTS_PATH/' /app/backend/app/admin.py && \
    sed -i 's/from config import CHROMA_PATH/from app.config import CHROMA_PATH/' /app/backend/app/admin.py && \
    sed -i 's/from models import get_db, FAQCreate/from app.models import get_db, FAQCreate/' /app/backend/app/admin.py

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
from typing import Optional
from llama_index import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.llms import OpenAI
from app.core.config import OPENAI_API_KEY
import os

# Инициализация LLM
llm = OpenAI(api_key=OPENAI_API_KEY, model="gpt-4o")
service_context = ServiceContext.from_defaults(llm=llm)

# Загрузка документов (поддержка PDF, Excel, DOCX)
def load_documents(directory: str = "data/documents"):
    documents = SimpleDirectoryReader(
        input_dir=directory,
        required_exts=[".pdf", ".xlsx", ".docx", ".txt", ".md"],
        recursive=True
    ).load_data()
    return documents

# Создание индекса
def create_index(documents):
    index = VectorStoreIndex.from_documents(documents, service_context=service_context)
    return index

# Запрос к RAG-системе
from app.services.analytics import AnalyticsService
from datetime import datetime

async def ask_rag(question: str, language: str = "en", user_id: Optional[int] = None, db: Optional[Session] = None) -> str:
    start_time = datetime.now()
    documents = load_documents()
    index = create_index(documents)
    query_engine = index.as_query_engine()
    
    # Добавляем контекст языка для более точного ответа
    if language != "en":
        question = f"Answer in {language}: {question}"
    
    response = query_engine.query(question)
    response_time = (datetime.now() - start_time).total_seconds()
    
    # Обновляем аналитику
    if user_id and db:
        AnalyticsService.update_user_analytics(db, user_id, response_time)
        AnalyticsService.update_admin_analytics(db)
    
    return str(response)
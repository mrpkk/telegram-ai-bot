"""RAG-система с Mistral Embeddings API."""

import os
import logging
from pathlib import Path
from typing import Optional

import httpx
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.embeddings import Embeddings
from cachetools import TTLCache
from tenacity import retry, stop_after_attempt, wait_exponential

from config import MISTRAL_API_KEY, MISTRAL_EMBED_URL, CHROMA_PATH, EMBEDDING_MODEL

log = logging.getLogger("rag")


# ── Mistral Embeddings (API) ──────────────────────────────────────────

# Кеширование эмбеддингов (5 минут)
embedding_cache = TTLCache(maxsize=1000, ttl=300)


class MistralEmbeddings(Embeddings):
    """Эмбеддинги через Mistral AI API."""

    def __init__(self, api_key: str, model: str = "mistral-embed"):
        self.api_key = api_key
        self.model = model
        self.api_url = MISTRAL_EMBED_URL
        self.client = httpx.AsyncClient(timeout=60.0)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        all_embeddings = []
        batch_size = 32
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = await self._get_embeddings(batch)
            all_embeddings.extend(embeddings)
        return all_embeddings

    async def embed_query(self, text: str) -> list[float]:
        cache_key = f"embed_query:{text}"
        if cache_key in embedding_cache:
            return embedding_cache[cache_key]
        embeddings = await self._get_embeddings([text])
        embedding_cache[cache_key] = embeddings[0]
        return embeddings[0]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _get_embeddings(self, texts: list[str]) -> list[list[float]]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": self.model, "input": texts}
        try:
            resp = await self.client.post(self.api_url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return [item["embedding"] for item in data["data"]]
        except Exception as e:
            log.error(f"Mistral Embeddings error: {e}")
            raise


# ── RAG-класс ─────────────────────────────────────────────────────────

class RAGSystem:
    """Система RAG для поиска и генерации ответов."""

    def __init__(self):
        self.embeddings = MistralEmbeddings(api_key=MISTRAL_API_KEY, model=EMBEDDING_MODEL)
        self.vectorstore: Optional[Chroma] = None
        asyncio.run(self._init_vectorstore())

    async def _init_vectorstore(self):
        """Инициализация векторной БД."""
        if CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir()):
            log.info("Загружаю существующую Chroma базу...")
            self.vectorstore = Chroma(
                persist_directory=str(CHROMA_PATH),
                embedding_function=self.embeddings
            )
        else:
            log.info("Создаю новую Chroma базу...")
            self.vectorstore = Chroma(
                persist_directory=str(CHROMA_PATH),
                embedding_function=self.embeddings
            )

    async def add_document(self, file_path: Path, filename: str) -> int:
        """Добавляет документ в базу знаний."""
        from langchain_community.document_loaders import (
            PyPDFLoader, TextLoader, CSVLoader, UnstructuredMarkdownLoader
        )
        from langchain_community.document_loaders import Docx2txtLoader

        # Выбор загрузчика по типу файла
        suffix = file_path.suffix.lower()
        loaders = {
            ".pdf": lambda: PyPDFLoader(str(file_path)),
            ".txt": lambda: TextLoader(str(file_path), encoding="utf-8"),
            ".md": lambda: UnstructuredMarkdownLoader(str(file_path)),
            ".csv": lambda: CSVLoader(str(file_path)),
            ".docx": lambda: Docx2txtLoader(str(file_path)),
        }

        loader_fn = loaders.get(suffix)
        if not loader_fn:
            raise ValueError(f"Неподдерживаемый формат: {suffix}")

        try:
            loader = loader_fn()
            documents = loader.load()

            for doc in documents:
                doc.metadata["source"] = filename

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", ". ", " "],
            )
            chunks = splitter.split_documents(documents)

            await self.vectorstore.aadd_documents(chunks)
            log.info(f"Добавлено {len(chunks)} чанков из {filename}")
            return len(chunks)

        except Exception as e:
            log.error(f"Ошибка обработки {filename}: {e}")
            raise

    async def search(self, query: str, k: int = 5) -> list[dict]:
        """Поиск по базе знаний."""
        if not self.vectorstore:
            return []

        try:
            results = await self.vectorstore.asimilarity_search_with_score(query, k=k)
            return [
                {
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "unknown"),
                    "score": float(score),
                }
                for doc, score in results
            ]
        except Exception as e:
            log.error(f"Ошибка поиска: {e}")
            return []

    async def get_context(self, query: str, k: int = 4) -> str:
        """Получить контекст для LLM."""
        results = await self.search(query, k=k)
        if not results:
            return "Нет релевантной информации в базе знаний."

        context_parts = []
        seen = set()
        for r in results:
            source = r["source"]
            snippet = r["content"][:500]
            key = f"{source}:{snippet[:50]}"
            if key not in seen:
                seen.add(key)
                context_parts.append(f"[Источник: {source}]\n{snippet}")

        return "\n\n---\n\n".join(context_parts)


# ── LLM-класс ─────────────────────────────────────────────────────────

# Кеширование ответов LLM (1 час)
llm_cache = TTLCache(maxsize=1000, ttl=3600)


class MistralLLM:
    """Обёртка над Mistral AI."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        self.client = httpx.AsyncClient(timeout=60.0)

    async def generate(self, system_prompt: str, user_message: str, context: str = "") -> str:
        """Генерация ответа."""
        cache_key = f"llm:{system_prompt}:{user_message}:{context[:100]}"
        if cache_key in llm_cache:
            return llm_cache[cache_key]

        full_prompt = user_message
        if context:
            full_prompt = f"Контекст из базы знаний:\n{context}\n\nВопрос: {user_message}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_prompt},
        ]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 1024,
        }

        try:
            resp = await self.client.post(self.api_url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            answer = data["choices"][0]["message"]["content"]
            llm_cache[cache_key] = answer
            return answer
        except Exception as e:
            log.error(f"Mistral API error: {e}")
            return f"Ошибка генерации: {e}"

    async def close(self):
        await self.client.aclose()

"""Тесты для RAG-системы."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path
import os

from app.rag import MistralEmbeddings, MistralLLM, RAGSystem
from app.config import MISTRAL_API_KEY, EMBEDDING_MODEL, DEFAULT_MODEL


@pytest.mark.asyncio
async def test_mistral_embeddings():
    """Тест для MistralEmbeddings."""
    embeddings = MistralEmbeddings(api_key=MISTRAL_API_KEY, model=EMBEDDING_MODEL)
    
    # Mock httpx.AsyncClient.post
    with patch.object(embeddings.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = MagicMock(
            json=lambda: {"data": [{"embedding": [0.1, 0.2, 0.3]}]},
            raise_for_status=lambda: None
        )
        
        result = await embeddings.embed_documents(["test text"])
        assert len(result) == 1
        assert len(result[0]) > 0
        mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_mistral_llm():
    """Тест для MistralLLM."""
    llm = MistralLLM(api_key=MISTRAL_API_KEY, model=DEFAULT_MODEL)
    
    # Mock httpx.AsyncClient.post
    with patch.object(llm.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value = MagicMock(
            json=lambda: {"choices": [{"message": {"content": "test answer"}}]},
            raise_for_status=lambda: None
        )
        
        result = await llm.generate(
            system_prompt="test system", 
            user_message="test user", 
            context="test context"
        )
        assert result == "test answer"
        mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_rag_system():
    """Тест для RAGSystem."""
    rag = RAGSystem()
    
    # Mock Chroma
    with patch('app.rag.Chroma', autospec=True) as mock_chroma:
        mock_instance = mock_chroma.return_value
        mock_instance.asimilarity_search_with_score = AsyncMock(return_value=[])
        
        result = await rag.search("test query")
        assert result == []
        mock_instance.asimilarity_search_with_score.assert_called_once_with("test query", k=5)


@pytest.mark.asyncio
async def test_authentication():
    """Тест для аутентификации пользователей."""
    from app.bot import is_authenticated, ALLOWED_EMAIL_DOMAINS
    
    # Тест для админа
    assert is_authenticated(123, None) is False  # Нет в TELEGRAM_ADMIN_IDS
    
    # Тест для разрешённого домена
    test_user_id = 456
    test_email = "user@company.com"
    assert is_authenticated(test_user_id, test_email) is True
    
    # Тест для запрещённого домена
    test_email = "user@gmail.com"
    assert is_authenticated(test_user_id, test_email) is False
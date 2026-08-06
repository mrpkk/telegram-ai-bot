"""Админ-панель (Streamlit)."""

import os
import streamlit as st
import requests
import json
from datetime import datetime

# ── Конфигурация ──────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Bot Admin Panel",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Тёмная тема
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .stSidebar { background-color: #1a1a2e; }
    h1, h2, h3 { color: #00d4ff; }
    .stMetric { background-color: #1a1a3e; padding: 10px; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

API_BASE = os.getenv("ADMIN_API_BASE", "http://127.0.0.1:8007/api/v1/admin")
AUTH = (os.getenv("ADMIN_USERNAME", "admin"), os.getenv("ADMIN_PASSWORD", ""))


def api_get(endpoint: str):
    """GET-запрос к API."""
    try:
        resp = requests.get(f"{API_BASE}{endpoint}", auth=AUTH, timeout=10)
        return resp.json() if resp.ok else None
    except:
        return None


def api_post(endpoint: str, data: dict = None, files: dict = None):
    """POST-запрос к API."""
    try:
        resp = requests.post(f"{API_BASE}{endpoint}", auth=AUTH, json=data, files=files, timeout=30)
        return resp.json() if resp.ok else None
    except:
        return None


def api_delete(endpoint: str):
    """DELETE-запрос к API."""
    try:
        resp = requests.delete(f"{API_BASE}{endpoint}", auth=AUTH, timeout=10)
        return resp.json() if resp.ok else None
    except:
        return None


# ── Сайдбар ───────────────────────────────────────────────────────────

st.sidebar.title("🤖 AI Bot Admin")
page = st.sidebar.radio(
    "Навигация",
    ["📊 Дашборд", "📁 Документы", "💬 FAQ", "📈 Аналитика", "📜 Логи", "⚙️ Настройки"]
)

# ── Дашборд ───────────────────────────────────────────────────────────

if page == "📊 Дашборд":
    st.title("📊 Дашборд")

    stats = api_get("/stats")
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("👥 Пользователей", stats.get("users_total", 0))
        col2.metric("❓ Вопросов сегодня", stats.get("questions_today", 0))
        col3.metric("📄 Документов", stats.get("documents_count", 0))
        col4.metric("💬 FAQ", stats.get("faq_count", 0))

        col5, col6, col7 = st.columns(3)
        col5.metric("⏱️ Среднее время", f"{stats.get('avg_response_time', 0):.0f}ms")
        col6.metric("🎯 Точность", f"{stats.get('accuracy', 0)}%")
        col7.metric("📈 Всего вопросов", stats.get("questions_total", 0))

        # Топ вопросов
        st.subheader("🔥 Топ-10 вопросов")
        top = stats.get("top_questions", [])
        if top:
            for q in top:
                st.write(f"**{q['count']}x** — {q['question']}")
        else:
            st.info("Пока нет данных")
    else:
        st.warning("API недоступен. Запустите backend: `uvicorn app.main:app`")

# ── Документы ─────────────────────────────────────────────────────────

elif page == "📁 Документы":
    st.title("📁 Управление документами")

    # Загрузка
    st.subheader("Загрузить документ")
    uploaded = st.file_uploader(
        "Выберите файл",
        type=["pdf", "txt", "md", "csv", "docx"],
        help="Поддерживаются: PDF, TXT, MD, CSV, DOCX"
    )
    tags = st.text_input("Теги (через запятую)")

    if uploaded and st.button("📤 Загрузить"):
        with st.spinner("Обработка..."):
            files = {"file": (uploaded.name, uploaded.getvalue())}
            result = api_post("/upload", files=files)
            if result:
                st.success(f"✅ Загружено: {result['filename']} ({result['chunks']} фрагментов)")
                st.rerun()
            else:
                st.error("Ошибка загрузки")

    # Список
    st.subheader("Документы в базе")
    docs = api_get("/documents")
    if docs:
        for doc in docs:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            col1.write(f"📄 {doc['filename']}")
            col2.write(f"{doc['chunks_count']} чанков")
            col3.write(doc['created_at'][:10])
            if col4.button("🗑️", key=f"del_{doc['id']}"):
                api_delete(f"/documents/{doc['id']}")
                st.rerun()
    else:
        st.info("Документов пока нет")

# ── FAQ ───────────────────────────────────────────────────────────────

elif page == "💬 FAQ":
    st.title("💬 Управление FAQ")

    # Добавление
    st.subheader("Добавить вопрос-ответ")
    with st.form("add_faq"):
        question = st.text_input("Вопрос")
        answer = st.text_area("Ответ")
        category = st.selectbox("Категория", ["general", "delivery", "payment", "products", "support"])
        submitted = st.form_submit_button("➕ Добавить")
        if submitted and question and answer:
            result = api_post("/faq", data={"question": question, "answer": answer, "category": category})
            if result:
                st.success("✅ FAQ добавлен")
                st.rerun()

    # Список
    st.subheader("Текущий FAQ")
    faqs = api_get("/faq")
    if faqs:
        for faq in faqs:
            with st.expander(f"❓ {faq['question'][:50]}..."):
                st.write(f"**Ответ:** {faq['answer']}")
                st.write(f"**Категория:** {faq['category']}")
                if st.button("🗑️ Удалить", key=f"del_faq_{faq['id']}"):
                    api_delete(f"/faq/{faq['id']}")
                    st.rerun()
    else:
        st.info("FAQ пока нет")

# ── Аналитика ─────────────────────────────────────────────────────────

elif page == "📈 Аналитика":
    st.title("📈 Аналитика")

    stats = api_get("/stats")
    if stats:
        # График точности
        st.subheader("🎯 Точность ответов")
        accuracy = stats.get("accuracy", 0)
        st.progress(accuracy / 100)
        st.write(f"**{accuracy}%** ответов помечены как полезные")

        # Среднее время
        st.subheader("⏱️ Время ответа")
        avg_time = stats.get("avg_response_time", 0)
        st.metric("Среднее время", f"{avg_time:.0f}ms")

        # Топ тем
        st.subheader("🔥 Популярные темы")
        top = stats.get("top_questions", [])
        if top:
            for i, q in enumerate(top[:5], 1):
                st.write(f"**{i}.** {q['question']} ({q['count']} раз)")
    else:
        st.warning("Нет данных")

# ── Логи ───────────────────────────────────────────────────────────────

elif page == "📜 Логи":
    st.title("📜 Логи запросов")

    logs = api_get("/logs?per_page=100")
    if logs and logs.get("logs"):
        st.write(f"Всего: {logs['total']} записей")

        for log_entry in logs["logs"][:50]:
            with st.expander(f"❓ {log_entry['question'][:60]}..."):
                st.write(f"**Вопрос:** {log_entry['question']}")
                st.write(f"**Ответ:** {log_entry['answer'][:200]}...")
                st.write(f"**Пользователь:** {log_entry.get('username', 'аноним')}")
                st.write(f"**Время:** {log_entry['created_at']}")
                st.write(f"**Источник:** {log_entry.get('source', '?')}")
                helpful = log_entry.get('is_helpful')
                if helpful is not None:
                    st.write(f"**Оценка:** {'👍' if helpful else '👎'}")
    else:
        st.info("Логов пока нет")

# ── Настройки ─────────────────────────────────────────────────────────

elif page == "⚙️ Настройки":
    st.title("⚙️ Настройки")

    st.subheader("📥 Экспорт отчёта")
    st.write("Скачать данные (пользователи + логи запросов) в Excel или CSV.")
    col_a, col_b = st.columns(2)
    if col_a.button("📊 Скачать Excel (.xlsx)"):
        try:
            resp = requests.get(f"{API_BASE}/export?fmt=xlsx", auth=AUTH, timeout=30)
            if resp.ok:
                st.download_button(
                    "💾 Сохранить report.xlsx", resp.content,
                    file_name="report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error(f"Ошибка: HTTP {resp.status_code}")
        except Exception as e:
            st.error(f"API недоступен: {e}")
    if col_b.button("📄 Скачать CSV"):
        try:
            resp = requests.get(f"{API_BASE}/export?fmt=csv", auth=AUTH, timeout=30)
            if resp.ok:
                st.download_button(
                    "💾 Сохранить report.csv", resp.content,
                    file_name="report.csv", mime="text/csv"
                )
            else:
                st.error(f"Ошибка: HTTP {resp.status_code}")
        except Exception as e:
            st.error(f"API недоступен: {e}")

    st.subheader("🤖 Информация о боте")
    st.info("""
    **Название:** Telegram AI Bot
    **Версия:** 1.0.0
    **LLM:** Mistral Small (mistral.ai) — бесплатно
    **Embeddings:** Mistral Embed — бесплатно
    **VectorDB:** ChromaDB
    """)

    st.subheader("🔑 API-ключи")
    st.text_input("Mistral API Key", value="***", disabled=True)
    st.text_input("Telegram Bot Token", value="***", disabled=True)

    st.subheader("📞 Поддержка")
    st.text_input("Email", value="support@company.com")
    st.text_input("Телефон", value="+79001234567")
    st.text_input("Название компании", value="Моя Компания")

import tempfile
from pathlib import Path

import streamlit as st

from src.pipeline import DocumentAssistantPipeline

st.set_page_config(
    page_title="Ассистент по документам",
    page_icon="📄",
    layout="wide",
)

st.title("📄 Ассистент по документам (.txt / .docx)")
st.caption(
    "Поиск и ответы строго по содержимому загруженного документа с указанием источников."
)

# --- Боковая панель с настройками ---
with st.sidebar:
    st.header("Настройки поиска")
    chunk_size = st.slider("Размер чанка (символов)", 150, 1200, 500, step=50)
    overlap = st.slider("Перекрытие чанков", 0, 300, 80, step=10)
    if overlap >= chunk_size:
        overlap = max(0, chunk_size - 50)
        st.warning(f"Перекрытие скорректировано до {overlap}, чтобы оно было меньше размера чанка.")

    top_k = st.slider("Количество фрагментов (top_k)", 1, 6, 3, step=1)
    min_score = st.slider("Порог сходства (min_score)", 0.0, 0.9, 0.25, step=0.05)

# Кэшируем пайплайн между перерисовками страницы, если меняются настройки
@st.cache_resource
def get_pipeline(c_size: int, ov: int, k: int, m_score: float) -> DocumentAssistantPipeline:
    return DocumentAssistantPipeline(
        chunk_size=c_size,
        overlap=ov,
        top_k=k,
        min_score=m_score,
    )

pipeline = get_pipeline(chunk_size, overlap, top_k, min_score)

# --- Выбор или загрузка документа ---
col_left, col_right = st.columns([1, 1.3])

with col_left:
    st.subheader("1. Документ")
    uploaded_file = st.file_uploader(
        "Загрузите файл (.txt или .docx)",
        type=["txt", "docx"],
    )

    sample_files = [
        p for p in [Path("data/sample_notes.txt"), Path("data/sample_lecture.docx")]
        if p.exists()
    ]
    selected_sample = None
    if not uploaded_file and sample_files:
        selected_sample = st.selectbox(
            "Или выберите тестовый файл из папки data/:",
            options=sample_files,
            format_func=lambda p: str(p),
        )

    active_file_path = None
    display_name = None

    if uploaded_file is not None:
        suffix = Path(uploaded_file.name).suffix.lower()
        tmp_path = Path(tempfile.gettempdir()) / f"doc_assistant_upload{suffix}"
        tmp_path.write_bytes(uploaded_file.getvalue())
        active_file_path = str(tmp_path)
        display_name = uploaded_file.name
    elif selected_sample is not None:
        active_file_path = str(selected_sample)
        display_name = selected_sample.name

    if active_file_path:
        if st.button("Проиндексировать документ", type="primary"):
            with st.spinner("Индексируем документ..."):
                num_chunks = pipeline.index_document(active_file_path)
            st.success(f"Готово: файл «{display_name}» разбит на {num_chunks} чанков.")

# --- Вопрос и ответ ---
with col_right:
    st.subheader("2. Вопрос по документу")
    question = st.text_input(
        "Введите ваш вопрос:",
        placeholder="Например: В чем минус индексов при записи?",
    )

    if st.button("Найти ответ"):
        if not active_file_path:
            st.error("Сначала загрузите .txt или .docx файл или выберите тестовый файл.")
        elif not question.strip():
            st.warning("Введите вопрос.")
        else:
            with st.spinner("Ищем ответ в документе..."):
                result = pipeline.ask(active_file_path, question)

            st.markdown("### Ответ")
            if result["found"]:
                st.success("Ответ найден в документе")
            else:
                st.info("Точный ответ в документе не найден")

            st.write(result["answer"])

            if result["sources"]:
                st.markdown("### Источники и цитаты")
                for idx, src in enumerate(result["sources"], start=1):
                    with st.expander(
                        f"Источник #{idx}: {src['location']} (score: {src['score']})"
                    ):
                        st.caption(f"Файл: {src['source']}")
                        st.write(src["quote"])
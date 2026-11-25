from pathlib import Path
from typing import Dict, Optional

from src.chunker import make_chunks
from src.generator import generate_answer
from src.parser import parse_file
from src.retriever import SemanticRetriever


class DocumentAssistantPipeline:
    """
    Сквозной пайплайн: парсинг документа -> нарезка на чанки ->
    семантический поиск -> формирование ответа с источниками.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 80,
        top_k: int = 3,
        min_score: float = 0.25,
        retriever: Optional[SemanticRetriever] = None,
    ) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.top_k = top_k
        self.min_score = min_score
        self.retriever = retriever or SemanticRetriever()
        self._indexed_file: Optional[str] = None

    def index_document(self, file_path: str | Path) -> int:
        """Читает документ, разбивает на чанки и строит векторный индекс."""
        resolved_path = str(Path(file_path).resolve())
        blocks = parse_file(resolved_path)
        chunks = make_chunks(
            blocks,
            chunk_size=self.chunk_size,
            overlap=self.overlap,
        )
        self.retriever.index_chunks(chunks)
        self._indexed_file = resolved_path
        return len(chunks)

    def ask(self, file_path: str | Path, question: str) -> Dict:
        """Отвечает на вопрос по документу, переиндексируя файл при смене."""
        resolved_path = str(Path(file_path).resolve())
        if self._indexed_file != resolved_path:
            self.index_document(resolved_path)

        retrieved = self.retriever.search(question, top_k=self.top_k)
        return generate_answer(
            question=question,
            retrieved_chunks=retrieved,
            min_score=self.min_score,
        )
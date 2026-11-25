from typing import Dict, List
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class SemanticRetriever:
    """
    Выполняет смысловой поиск по фрагментам документа
    с помощью векторных представлений (embeddings).
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    ) -> None:
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.chunks: List[Dict] = []
        self.embeddings = None

    def index_chunks(self, chunks: List[Dict]) -> None:
        """Строит векторный индекс для списка чанков."""
        if not chunks:
            self.chunks = []
            self.embeddings = None
            return

        self.chunks = chunks
        texts = [chunk["text"] for chunk in chunks]
        self.embeddings = self.model.encode(texts, show_progress_bar=False)

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Возвращает top_k наиболее похожих по смыслу фрагментов с оценкой score."""
        if not self.chunks or self.embeddings is None:
            return []

        query = query.strip()
        if not query:
            return []

        query_vec = self.model.encode([query], show_progress_bar=False)
        scores = cosine_similarity(query_vec, self.embeddings)[0]

        ranked_indices = scores.argsort()[::-1][:top_k]

        results: List[Dict] = []
        for idx in ranked_indices:
            item = dict(self.chunks[int(idx)])
            item["score"] = float(scores[int(idx)])
            results.append(item)

        return results
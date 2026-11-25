from typing import Dict, List


def generate_answer(
    question: str,
    retrieved_chunks: List[Dict],
    min_score: float = 0.25,
) -> Dict:
    """
    Формирует ответ исключительно на основе найденных фрагментов документа
    с указанием источников и цитат (без генерации выдуманных фактов).
    """
    clean_question = (question or "").strip()
    if not clean_question:
        return {
            "found": False,
            "answer": "Введите вопрос по содержимому документа.",
            "sources": [],
        }

    if not retrieved_chunks:
        return {
            "found": False,
            "answer": "В загруженном документе не найдено подходящих фрагментов.",
            "sources": [],
        }

    best_score = float(retrieved_chunks[0].get("score", 0.0))
    if best_score < min_score:
        return {
            "found": False,
            "answer": (
                f"В загруженном документе не найден точный ответ на этот вопрос "
                f"(максимальное сходство {best_score:.2f} ниже порога {min_score:.2f})."
            ),
            "sources": [],
        }

    relevant = [c for c in retrieved_chunks if float(c.get("score", 0.0)) >= min_score]
    if not relevant:
        relevant = [retrieved_chunks[0]]

    excerpts: List[str] = []
    sources: List[Dict] = []

    for item in relevant:
        text = item["text"].strip()
        source = item.get("source", "неизвестный файл")
        location = item.get("location", "место не указано")
        score = float(item.get("score", 0.0))

        excerpts.append(f"- [{source} | {location}]: {text}")
        sources.append({
            "source": source,
            "location": location,
            "score": round(score, 3),
            "quote": text,
        })

    answer_text = (
        "На основе найденных фрагментов документа:\n" + "\n".join(excerpts)
    )

    return {
        "found": True,
        "answer": answer_text,
        "sources": sources,
    }
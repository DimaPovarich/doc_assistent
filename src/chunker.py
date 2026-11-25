from typing import Dict, List


def make_chunks(
    blocks: List[Dict],
    chunk_size: int = 500,
    overlap: int = 80,
) -> List[Dict]:
    """
    Разбивает текстовые блоки на фрагменты (чанки) с перекрытием,
    сохраняя информацию о месте в файле.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size должен быть больше 0")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap должен быть >= 0 и меньше chunk_size")

    chunks: List[Dict] = []
    chunk_counter = 0

    for block in blocks:
        text = block["text"].strip()
        if not text:
            continue

        # Если текст помещается в один чанк — не режем его
        if len(text) <= chunk_size:
            chunk_counter += 1
            chunks.append({
                "chunk_id": chunk_counter,
                "source": block["source"],
                "section": block["section"],
                "location": block["location"],
                "text": text,
            })
            continue

        # Нарезка длинного блока с перекрытием
        step = chunk_size - overlap
        start = 0
        part_num = 1

        while start < len(text):
            end = start + chunk_size
            part_text = text[start:end].strip()

            if part_text:
                chunk_counter += 1
                chunks.append({
                    "chunk_id": chunk_counter,
                    "source": block["source"],
                    "section": block["section"],
                    "location": f"{block['location']} (часть {part_num})",
                    "text": part_text,
                })
                part_num += 1

            if end >= len(text):
                break
            start += step

    return chunks
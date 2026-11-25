from pathlib import Path
from typing import Dict, List
from docx import Document


def parse_file(file_path: str | Path) -> List[Dict]:
    """
    Читает .txt или .docx файл и возвращает список текстовых блоков
    с метаданными о месте в документе.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")

    suffix = path.suffix.lower()

    if suffix == ".txt":
        return _parse_txt(path)
    if suffix == ".docx":
        return _parse_docx(path)

    raise ValueError(f"Неподдерживаемый формат файла: {suffix}. Поддерживаются .txt и .docx")


def _parse_txt(path: Path) -> List[Dict]:
    raw_text = path.read_text(encoding="utf-8")
    lines = raw_text.splitlines()

    blocks: List[Dict] = []
    current_section = "Начало документа"
    paragraph_index = 0

    for line_num, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line:
            continue

        # Если строка похожа на заголовок раздела (например, РАЗДЕЛ 1...)
        if line.upper().startswith("РАЗДЕЛ") or line.upper().startswith("ГЛАВА"):
            current_section = line
            continue

        paragraph_index += 1
        blocks.append({
            "source": path.name,
            "section": current_section,
            "location": f"{current_section}, фрагмент/строка №{line_num}",
            "text": line,
        })

    return blocks


def _parse_docx(path: Path) -> List[Dict]:
    doc = Document(path)

    blocks: List[Dict] = []
    current_section = "Введение / без заголовка"
    paragraph_index = 0

    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue

        style_name = (p.style.name or "").lower()
        if "heading" in style_name or "заголовок" in style_name:
            current_section = text
            continue

        paragraph_index += 1
        blocks.append({
            "source": path.name,
            "section": current_section,
            "location": f"{current_section}, абзац №{paragraph_index}",
            "text": text,
        })

    return blocks
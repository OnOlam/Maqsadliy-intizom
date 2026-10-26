"""
document_ingest.py — Tashqi fayllarni (matn/PDF) chunklab xotiraga qo'shish.

Bu modul aynan sinfdoshlaringiz bergan "AI'ga kitob tashlasak, tahlil qila
oladimi?" degan savolga javob beradi. Fayl matnga o'qiladi, kichik
bo'laklarga ("chunk") bo'linadi va har biri MemoryStore'ga qo'shiladi —
shundan keyin foydalanuvchi o'sha kitob haqida savol bersa, RAG orqali
tegishli bo'laklar topilib, LLM'ga kontekst sifatida beriladi.

Hozirgi holat:
    - .txt fayllar uchun TO'LIQ ISHLAYDI
    - .pdf fayllar uchun SKELET (TODO: pypdf yoki pdfplumber kutubxonasi
      kerak bo'ladi — hozircha loyihaga qo'shilmagan, chunki qo'shimcha
      dependency; kerak bo'lsa keyingi bosqichda qo'shiladi)
"""

import os

from .memory_store import MemoryStore

CHUNK_SIZE_CHARS = 800  # har bir bo'lak taxminan shuncha belgidan iborat
CHUNK_OVERLAP = 100  # bo'laklar orasida bog'lanish uzilmasligi uchun


def chunk_text(text, chunk_size=CHUNK_SIZE_CHARS, overlap=CHUNK_OVERLAP):
    """Uzun matnni bir-biriga biroz ustma-ust tushadigan bo'laklarga bo'ladi.

    Oddiy belgi-asosidagi bo'lish ishlatiladi (jumla chegaralarini hurmat
    qilishga harakat qiladi — nuqta yoki yangi qatordan keyin bo'lishga
    intiladi, lekin bu qat'iy qoida emas).
    """
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        # Jumla oxirini topishga harakat qilamiz (ortga qarab)
        if end < n:
            boundary = text.rfind(". ", start, end)
            if boundary != -1 and boundary > start + chunk_size // 2:
                end = boundary + 1
        chunks.append(text[start:end].strip())
        if end >= n:
            break
        start = max(end - overlap, start + 1)

    return [c for c in chunks if c]


def ingest_text_file(path, source_label="document", store=None):
    """.txt faylni o'qib, chunklab, MemoryStore'ga qo'shadi.

    Returns:
        int — qo'shilgan chunk'lar soni
    """
    if store is None:
        store = MemoryStore()

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    base_name = os.path.basename(path)
    chunks = chunk_text(text)
    for i, chunk in enumerate(chunks):
        chunk_id = f"{source_label}:{base_name}:{i}"
        store.add(chunk_id, chunk, source=source_label, ref_id=i)

    return len(chunks)


def ingest_pdf_file(path, source_label="document", store=None):
    """PDF faylni o'qib, chunklab, MemoryStore'ga qo'shadi.

    TODO: hozircha ishlamaydi. Keyingi bosqichda `pypdf` yoki
    `pdfplumber` kutubxonasini qo'shib, matnni ajratib olish kerak:

        from pypdf import PdfReader
        reader = PdfReader(path)
        text = "\\n".join(page.extract_text() or "" for page in reader.pages)

    Shundan keyin yuqoridagi ingest_text_file() bilan bir xil chunk+qo'shish
    logikasi ishlatiladi.
    """
    raise NotImplementedError(
        "PDF o'qish hali ulanmagan — 'pypdf' kutubxonasini qo'shish kerak "
        "(keyingi bosqich)."
    )

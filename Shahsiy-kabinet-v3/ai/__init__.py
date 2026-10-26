"""
ai/ — "Ikkinchi miya" uchun lokal AI qatlami.

Bu paket hozircha SKELET (struktura) holatida: interfeyslar va ishlaydigon
yordamchi funksiyalar tayyor, lekin haqiqiy LLM modeli hali ulanmagan.
Maqsad — keyingi bosqichda llama-cpp-python orqali kichik GGUF modelni
(masalan Qwen2.5-3B-Instruct, Q4_K_M) butunlay offline ishga tushirish va
foydalanuvchining shaxsiy ma'lumotlari (journal, fanlar, maqsadlar va h.k.)
asosida haqiqiy javob beradigan "ikkinchi miya" yaratish.

Modullar:
    llm_engine.py        — modelni yuklash va matn generatsiyasi
    embeddings.py         — matnni vektorga aylantirish
    memory_store.py        — vektorlarni SQLite'da saqlash va qidirish (RAG)
    prompt_templates.py   — tizim promptlari va kontekst formatlash
    document_ingest.py    — tashqi fayllarni (matn/PDF) chunklab index qilish

Muhim eslatma (hardware): foydalanuvchi noutbuklari kuchsiz (4-8GB RAM,
integratsiyalashgan grafika) — shuning uchun faqat 1-3B parametrli, Q4
kvantlangan modellar maqsadga muvofiq. Katta modellarni bu yerda ishlatish
tavsiya etilmaydi.
"""

from .llm_engine import LLMEngine
from .embeddings import embed_text
from .memory_store import MemoryStore
from .prompt_templates import build_prompt

__all__ = ["LLMEngine", "embed_text", "MemoryStore", "build_prompt"]

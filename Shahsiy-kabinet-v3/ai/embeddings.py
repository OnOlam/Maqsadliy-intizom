"""
embeddings.py — Matnni vektorga aylantirish (RAG uchun birinchi qadam).

Hozirgi holat: ISHLAYDIGAN, lekin SODDALASHTIRILGAN versiya. Haqiqiy
embedding modeli (masalan llama.cpp'ning --embedding rejimi yoki kichik
sentence-transformers modeli) hali ulanmagan, chunki bu qo'shimcha ~100-500MB
model talab qiladi — kuchsiz noutbuklar uchun og'ir bo'lishi mumkin.

Shuning uchun hozircha oddiy "hashing trick" + so'z chastotasi asosidagi
vektor ishlatiladi (TF asoslangan, tashqi kutubxonasiz). Bu haqiqiy semantik
tushunish bermaydi (masalan "xursand" va "baxtli" so'zlarini bir xil deb
bilmaydi), lekin:
    - hech qanday qo'shimcha dependency yoki model fayli talab qilmaydi,
    - RAG pipeline'ning qolgan qismini (memory_store, qidirish, prompt
      yig'ish) hozirdanoq qurish va sinash imkonini beradi,
    - keyinroq shu funksiyani almashtirish yetarli — qolgan kod o'zgarmaydi.

TODO (keyingi bosqich): embed_text() ichini llama.cpp embedding chaqiruviga
yoki kichik (masalan all-MiniLM-L6-v2 xalqaro, yoki o'zbekcha/ko'ptillik
qo'llab-quvvatlaydigan) modelga almashtirish. Vektor o'lchami (VECTOR_DIM)
model bilan birga o'zgarishi mumkin.
"""

import hashlib
import math
import re

VECTOR_DIM = 256


def _tokenize(text):
    text = text.lower()
    # Lotin, kiril va tojik-forscha harflarni (ANDOZA sifatida) so'z deb olamiz
    return re.findall(r"[a-zA-Zа-яА-ЯёЁўЎқҚғҒҳҲ0-9']+", text)


def embed_text(text):
    """Matnni VECTOR_DIM o'lchamli raqamlar ro'yxatiga aylantiradi.

    Hozirgi (vaqtinchalik) algoritm: har bir so'z hash orqali vektorning
    bitta o'lchamiga proyeksiya qilinadi va chastotasi qo'shiladi, so'ng
    vektor normallashtiriladi (uzunligi 1 bo'ladi) — cosine similarity
    hisoblashni osonlashtiradi.
    """
    vec = [0.0] * VECTOR_DIM
    tokens = _tokenize(text)
    if not tokens:
        return vec

    for tok in tokens:
        h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
        idx = h % VECTOR_DIM
        sign = 1.0 if (h // VECTOR_DIM) % 2 == 0 else -1.0
        vec[idx] += sign

    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


def cosine_similarity(vec_a, vec_b):
    """Ikki vektor orasidagi cosine o'xshashlikni hisoblaydi (-1 dan 1 gacha,
    1 — bir xil ma'noga yaqin, 0 — bog'liq emas)."""
    if len(vec_a) != len(vec_b):
        raise ValueError("Vektor o'lchamlari mos kelmaydi")
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

"""
prompt_templates.py — LLM uchun tizim promptlari va kontekst formatlash.

Hozirgi holat: TO'LIQ ISHLAYDI (modeldan mustaqil — faqat matn formatlash).
LLM modeli ulanganda, build_prompt() natijasi to'g'ridan-to'g'ri
LLMEngine.generate()'ga context sifatida beriladi.
"""

SYSTEM_PROMPT_UZ = (
    "Sen foydalanuvchining shaxsiy AI yordamchisisan — uning ikkinchi miyasi. "
    "Quyida berilgan KONTEKST — foydalanuvchining o'zi kiritgan haqiqiy "
    "ma'lumotlari (kundalik yozuvlari, fanlari, maqsadlari, byudjeti). "
    "Faqat shu kontekst asosida javob ber. Agar kontekstda javob uchun "
    "yetarli ma'lumot bo'lmasa, buni ochiq ayt — to'qib chiqarma. "
    "Qisqa, samimiy va aniq javob ber, o'zbek tilida."
)


def format_context(search_results):
    """MemoryStore.search() natijasini LLM uchun o'qiladigan matn qiladi.

    Args:
        search_results: list of dict (memory_store.MemoryStore.search() dan)

    Returns:
        str — "- [manba] matn" formatida qatorlar
    """
    if not search_results:
        return "(tegishli ma'lumot topilmadi)"

    lines = []
    for r in search_results:
        source_label = {
            "journal": "Kundalik",
            "subjects": "Fan",
            "goals": "Maqsad",
            "budget": "Byudjet",
            "document": "Hujjat",
        }.get(r["source"], r["source"] or "Ma'lumot")
        lines.append(f"- [{source_label}] {r['text']}")
    return "\n".join(lines)


def build_prompt(user_message, search_results=None, extra_instructions=""):
    """To'liq promptni yig'adi: tizim ko'rsatmasi + kontekst + savol.

    Args:
        user_message: foydalanuvchining savoli
        search_results: memory_store.search() natijasi (RAG konteksti)
        extra_instructions: qo'shimcha, vaziyatga xos ko'rsatma (masalan
            "Javobni 2 jumladan oshirma")

    Returns:
        dict — {"system": ..., "context": ..., "user": ...} — bu LLMEngine
        ichida chat-template formatiga (masalan ChatML) aylantiriladi.
    """
    context_text = format_context(search_results or [])
    system = SYSTEM_PROMPT_UZ
    if extra_instructions:
        system += "\n\n" + extra_instructions

    return {
        "system": system,
        "context": context_text,
        "user": user_message,
    }

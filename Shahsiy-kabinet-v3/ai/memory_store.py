"""
memory_store.py — "Ikkinchi miya" xotirasi: vektorlarni saqlash va qidirish.

Hozirgi holat: TO'LIQ ISHLAYDI (embeddings.py'dagi vaqtinchalik vektorizatsiya
bilan birga). Bu RAG (Retrieval-Augmented Generation) pipeline'ining
"Retrieval" qismi — foydalanuvchi biror narsa so'raganda, uning eski journal
yozuvlari, fanlari, maqsadlari orasidan ENG MOS keladiganlarini topib,
shularni LLM promptiga kontekst sifatida qo'shish uchun ishlatiladi.

Alohida SQLite fayl ishlatiladi (cabinet.db'ga aralashtirilmaydi — AI
qatlami asosiy ma'lumotlar bazasidan mustaqil bo'lishi kerak, shunda uni
butunlay o'chirib tashlash yoki qayta qurish oson bo'ladi).

Ishlatilishi:
    store = MemoryStore()
    store.add("journal:42", "Bugun imtihonga tayyorlanib charchadim",
              source="journal", ref_id=42)
    natijalar = store.search("charchoq haqida nima yozgandim?", top_k=3)
"""

import sqlite3
import json
import os

from .embeddings import embed_text, cosine_similarity

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "ai_memory.db")


class MemoryStore:
    def __init__(self, db_path=None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS memory_chunks (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                vector TEXT NOT NULL,
                source TEXT,
                ref_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        self.conn.commit()

    def add(self, chunk_id, text, source=None, ref_id=None):
        """Bitta matn bo'lagini ("chunk") xotiraga qo'shadi yoki yangilaydi.

        Args:
            chunk_id: noyob identifikator (masalan "journal:42")
            text: saqlanadigan matn
            source: qayerdan kelgani (masalan "journal", "subjects", "goals")
            ref_id: asl ma'lumot bazasidagi yozuv id'si (keyin orqaga
                qaytib to'liq yozuvni topish uchun)
        """
        vec = embed_text(text)
        self.cursor.execute(
            """INSERT INTO memory_chunks (id, text, vector, source, ref_id)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET
                   text=excluded.text, vector=excluded.vector,
                   source=excluded.source, ref_id=excluded.ref_id""",
            (chunk_id, text, json.dumps(vec), source, ref_id),
        )
        self.conn.commit()

    def search(self, query, top_k=5, source_filter=None):
        """Berilgan savolga eng mos keladigan top_k ta matn bo'lagini topadi.

        Returns:
            list of dict: [{"id", "text", "source", "ref_id", "score"}, ...]
            score — cosine o'xshashlik (1.0 ga yaqin = juda mos)
        """
        query_vec = embed_text(query)

        if source_filter:
            self.cursor.execute(
                "SELECT * FROM memory_chunks WHERE source=?", (source_filter,)
            )
        else:
            self.cursor.execute("SELECT * FROM memory_chunks")

        rows = self.cursor.fetchall()
        scored = []
        for row in rows:
            vec = json.loads(row["vector"])
            score = cosine_similarity(query_vec, vec)
            scored.append(
                {
                    "id": row["id"],
                    "text": row["text"],
                    "source": row["source"],
                    "ref_id": row["ref_id"],
                    "score": score,
                }
            )

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def delete(self, chunk_id):
        self.cursor.execute("DELETE FROM memory_chunks WHERE id=?", (chunk_id,))
        self.conn.commit()

    def delete_by_source(self, source, ref_id=None):
        """Masalan bitta journal yozuvi o'chirilganda, unga mos chunk'larni
        ham tozalash uchun."""
        if ref_id is not None:
            self.cursor.execute(
                "DELETE FROM memory_chunks WHERE source=? AND ref_id=?",
                (source, ref_id),
            )
        else:
            self.cursor.execute(
                "DELETE FROM memory_chunks WHERE source=?", (source,)
            )
        self.conn.commit()

    def count(self):
        self.cursor.execute("SELECT COUNT(*) as cnt FROM memory_chunks")
        return self.cursor.fetchone()["cnt"]

    def close(self):
        self.conn.close()

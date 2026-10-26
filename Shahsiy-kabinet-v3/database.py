import sqlite3
import os
import hashlib
import secrets
from datetime import datetime, date, timedelta


def hash_secret(raw, salt=None):
    """Parol/PIN kabi maxfiy qiymatlarni PBKDF2-HMAC-SHA256 bilan hash qiladi.
    Qaytaradi: "salt_hex$hash_hex" formatida string, DB'da shu holda saqlanadi.
    Tashqi kutubxona (bcrypt) shart emas — faqat Python standart kutubxonasi,
    shuning uchun .exe qilib yig'ishda qo'shimcha dependency qo'shilmaydi."""
    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", raw.encode("utf-8"), bytes.fromhex(salt), 100_000
    )
    return f"{salt}${digest.hex()}"


def verify_secret(raw, stored):
    """Berilgan qiymatni (parol/PIN) saqlangan hash bilan solishtiradi."""
    if not stored or "$" not in stored:
        return False
    salt, _, hash_hex = stored.partition("$")
    try:
        digest = hashlib.pbkdf2_hmac(
            "sha256", raw.encode("utf-8"), bytes.fromhex(salt), 100_000
        )
    except ValueError:
        return False
    return secrets.compare_digest(digest.hex(), hash_hex)


def _is_legacy_plaintext(stored):
    """Eski (hash qilinmagan) yozuvlarni aniqlash — bizning formatimizda har doim
    bitta '$' bo'ladi va salt 32 ta hex belgidan iborat bo'ladi."""
    if not stored or "$" not in stored:
        return True
    salt = stored.split("$", 1)[0]
    return not (len(salt) == 32 and all(c in "0123456789abcdef" for c in salt))


class Database:
    
    def migrate_journal(self):
        """Eski journal jadvalini yangi tuzilmaga o'tkazish"""
        try:
            # 1. Eski ma'lumotlarni vaqtincha saqlashga harakat qilamiz
            self.cursor.execute("SELECT id, title, content, date FROM journal")
            old_data = self.cursor.fetchall()
            
            # 2. Eski jadvalni butunlay o'chiramiz
            self.cursor.execute("DROP TABLE IF EXISTS journal")
            
            # 3. Yangi to'liq tuzilmani yaratamiz
            self.cursor.execute("""CREATE TABLE journal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT, 
                content TEXT, 
                date TEXT, 
                created_at TEXT,
                type TEXT DEFAULT 'note',
                is_secret INTEGER DEFAULT 0
            )""")
            
            # 4. Eski ma'lumotlarni qayta joylashtiramiz (default qiymatlar bilan)
            from datetime import datetime
            now_str = datetime.now().isoformat()
            for row in old_data:
                # row: (id, title, content, date)
                self.cursor.execute(
                    "INSERT INTO journal (title, content, date, created_at, type, is_secret) VALUES (?, ?, ?, ?, ?, ?)",
                    (row[1], row[2], row[3], now_str, 'note', 0)
                )
                
            self.conn.commit()
            print("✅ Journal jadvali muvaffaqiyatli yangilandi!")
            
        except Exception as e:
            # Agar yangi jadval bo'lmasa yoki boshqa xato bo'lsa, shunchaki yaratamiz
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS journal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT, 
                content TEXT, 
                date TEXT, 
                created_at TEXT,
                type TEXT DEFAULT 'note',
                is_secret INTEGER DEFAULT 0
            )""")
            self.conn.commit()
            
    def __init__(self, db_name="cabinet.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.migrate_journal()  # ← JADVALNI YANGILASH
        self.ensure_income_table()
        self.fix_journal_types()

    def create_tables(self):
        """Barcha jadvallarni yaratish"""
        tables = [
            # Foydalanuvchi
            """CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY,
                login TEXT UNIQUE,
                password TEXT,
                pin TEXT,
                name TEXT,
                created_at TEXT
            )""",
            # Fanlar
            """CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_uz TEXT,
                name_ru TEXT,
                name_tj TEXT,
                teacher TEXT,
                room TEXT,
                phone TEXT,
                created_at TEXT
            )""",
            # Baholar
            """CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                grade INTEGER,
                date TEXT,
                type TEXT,
                created_at TEXT,
                FOREIGN KEY (subject_id) REFERENCES subjects(id)
            )""",
            # Davomat
            """CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                date TEXT,
                status TEXT,
                FOREIGN KEY (subject_id) REFERENCES subjects(id)
            )""",
            # Leksiyalar
            """CREATE TABLE IF NOT EXISTS lectures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                title_uz TEXT,
                title_ru TEXT,
                title_tj TEXT,
                content_uz TEXT,
                content_ru TEXT,
                content_tj TEXT,
                created_at TEXT,
                FOREIGN KEY (subject_id) REFERENCES subjects(id)
            )""",
            # Do'stlar
            """CREATE TABLE IF NOT EXISTS friends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                birthday TEXT,
                phone TEXT,
                email TEXT,
                telegram TEXT,
                workplace TEXT,
                notes TEXT,
                importance INTEGER DEFAULT 1,
                image_path TEXT,
                created_at TEXT
            )""",
            # Vazifalar
            """CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                due_date TEXT,
                due_time TEXT,
                category TEXT,
                priority INTEGER DEFAULT 1,
                completed INTEGER DEFAULT 0,
                created_at TEXT
            )""",
            # Eslatmalar
            """CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                message TEXT,
                date TEXT,
                time TEXT,
                type TEXT,
                read INTEGER DEFAULT 0,
                created_at TEXT
            )""",
            # Maqsadlar
            """CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                target_date TEXT,
                progress INTEGER DEFAULT 0,
                completed INTEGER DEFAULT 0,
                created_at TEXT
            )""",
            # Kayfiyat
            """CREATE TABLE IF NOT EXISTS moods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                mood INTEGER,
                note TEXT,
                created_at TEXT
            )""",
            # Yutuqlar
            """CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                icon TEXT,
                unlocked INTEGER DEFAULT 0,
                unlocked_at TEXT,
                points INTEGER DEFAULT 0
            )""",
            # Foydalanuvchi yutuqlari
            """CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                achievement_id INTEGER,
                unlocked_at TEXT,
                FOREIGN KEY (achievement_id) REFERENCES achievements(id)
            )""",
            # Ballar
            """CREATE TABLE IF NOT EXISTS points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount INTEGER,
                reason TEXT,
                date TEXT
            )""",
            # Xarajatlar
            """CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL,
                category TEXT,
                description TEXT,
                date TEXT,
                created_at TEXT
            )""",
            # Pomodoro sessiyalari
            """CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                duration INTEGER,
                subject_id INTEGER,
                date TEXT,
                completed INTEGER DEFAULT 1
            )""",
            # Kunlik
            """CREATE TABLE IF NOT EXISTS journal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                title TEXT,
                content TEXT,
                created_at TEXT
            )""",
            # Sozlamalar
            """CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )""",
            # AI xabarlar
            """CREATE TABLE IF NOT EXISTS ai_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT,
                type TEXT,
                date TEXT,
                read INTEGER DEFAULT 0
            )""",
        ]

        for table in tables:
            self.cursor.execute(table)
        self.conn.commit()

        self.insert_defaults()

    def insert_defaults(self):
        """Standart ma'lumotlarni kiritish"""
        # Foydalanuvchi
        self.cursor.execute("SELECT COUNT(*) as cnt FROM user")
        if self.cursor.fetchone()["cnt"] == 0:
            self.cursor.execute(
                "INSERT INTO user (login, password, pin, name, created_at) VALUES (?, ?, ?, ?, ?)",
                (
                    "halimjon",
                    hash_secret("halimjon123"),
                    hash_secret("1234"),
                    "HASANOV HALIMJON",
                    datetime.now().isoformat(),
                ),
            )
            self.conn.commit()

        # Sozlamalar
        self.set_setting("language", "uz")
        self.set_setting("theme", "light")
        self.set_setting("remember_login", "1")

        # Yutuqlar
        self.cursor.execute("SELECT COUNT(*) as cnt FROM achievements")
        if self.cursor.fetchone()["cnt"] == 0:
            achievements = [
                ("Birinchi qadam", "Dasturga birinchi marta kirdingiz", "🎯", 10),
                ("5 kun ketma-ket", "5 kun vazifalarni bajardingiz", "🔥", 50),
                ("10 kun ketma-ket", "10 kun vazifalarni bajardingiz", "💎", 100),
                ("A'lochi", "Barcha fanlardan 90+ ball", "🏆", 200),
                ("Ijtimoiy", "10 ta do'st qo'shdingiz", "👥", 50),
                ("Pomodoro ustasi", "50 ta pomodoro sessiyasi", "🍅", 100),
                ("Maqsad sari", "Birinchi maqsadga erishdingiz", "🎖️", 150),
                ("Moliyaviy savodli", "30 kun byudjetni kuzatdingiz", "💰", 100),
                ("Kunlik yozuvchi", "30 kun kunlik yozdingiz", "📝", 100),
                ("Erta turuvchi", "7 kun ertalab vazifalarni bajardingiz", "⏰", 75),
            ]
            for a in achievements:
                self.cursor.execute(
                    "INSERT INTO achievements (title, description, icon, unlocked, points) VALUES (?, ?, ?, 0, ?)",
                    a,
                )
            self.conn.commit()

        # Standart fanlar
        self.cursor.execute("SELECT COUNT(*) as cnt FROM subjects")
        if self.cursor.fetchone()["cnt"] == 0:
            subjects = [
                ("Matematika", "Математика", "Математика"),
                ("Informatika", "Информатика", "Информатика"),
                ("Sun'iy intellekt", "Искусственный интеллект", "Зеҳни сунъӣ"),
                ("Ingliz tili", "Английский язык", "Забони англисӣ"),
            ]
            for s in subjects:
                self.cursor.execute(
                    "INSERT INTO subjects (name_uz, name_ru, name_tj, created_at) VALUES (?, ?, ?, ?)",
                    (s[0], s[1], s[2], datetime.now().isoformat()),
                )
            self.conn.commit()

    # ============== SOZLAMALAR ==============
    def get_setting(self, key, default=None):
        self.cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = self.cursor.fetchone()
        return row["value"] if row else default

    def set_setting(self, key, value):
        self.cursor.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, str(value)),
        )
        self.conn.commit()

    # ============== FOYDALANUVCHI ==============
    def get_user(self):
        self.cursor.execute("SELECT * FROM user LIMIT 1")
        return self.cursor.fetchone()

    def check_login(self, login, password):
        """Login'ni tekshiradi. Parol hash qilib solishtiriladi.
        Agar DB'da eski (hash qilinmagan) parol topilsa, muvaffaqiyatli
        kirishdan so'ng avtomatik hash'langan holga o'tkaziladi — foydalanuvchi
        buni sezmaydi, eski ma'lumot yo'qolmaydi."""
        self.cursor.execute("SELECT * FROM user WHERE login=?", (login,))
        user = self.cursor.fetchone()
        if not user:
            return None

        stored = user["password"]
        if _is_legacy_plaintext(stored):
            if stored != password:
                return None
            self.cursor.execute(
                "UPDATE user SET password=? WHERE id=?",
                (hash_secret(password), user["id"]),
            )
            self.conn.commit()
            return self.get_user()

        if verify_secret(password, stored):
            return user
        return None

    def check_pin(self, pin):
        """PIN'ni tekshiradi. Xuddi parol kabi, eski (hash qilinmagan)
        PIN avtomatik yangi formatga o'tkaziladi."""
        user = self.get_user()
        if not user:
            return False

        stored = user["pin"]
        if _is_legacy_plaintext(stored):
            if stored != pin:
                return False
            self.cursor.execute(
                "UPDATE user SET pin=? WHERE id=?", (hash_secret(pin), user["id"])
            )
            self.conn.commit()
            return True

        return verify_secret(pin, stored)

    def update_user(self, **kwargs):
        """Foydalanuvchi maydonlarini yangilaydi. password/pin kalitlari
        avtomatik hash qilinadi — chaqiruvchi tomondan oldindan hash qilish
        shart emas."""
        if "password" in kwargs:
            kwargs["password"] = hash_secret(kwargs["password"])
        if "pin" in kwargs:
            kwargs["pin"] = hash_secret(kwargs["pin"])
        sets = ", ".join([f"{k}=?" for k in kwargs.keys()])
        values = list(kwargs.values())
        self.cursor.execute(f"UPDATE user SET {sets} WHERE id=1", values)
        self.conn.commit()

    # ============== FANLAR ==============
    def get_subjects(self):
        self.cursor.execute("SELECT * FROM subjects ORDER BY name_uz")
        return self.cursor.fetchall()

    def get_subject(self, id):
        self.cursor.execute("SELECT * FROM subjects WHERE id=?", (id,))
        return self.cursor.fetchone()

    def add_subject(self, name_uz, name_ru, name_tj, teacher="", room="", phone=""):
        self.cursor.execute(
            "INSERT INTO subjects (name_uz, name_ru, name_tj, teacher, room, phone, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                name_uz,
                name_ru,
                name_tj,
                teacher,
                room,
                phone,
                datetime.now().isoformat(),
            ),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def delete_subject(self, id):
        self.cursor.execute("DELETE FROM subjects WHERE id=?", (id,))
        self.conn.commit()

    def update_subject(
        self, id, name_uz, name_ru, name_tj, teacher="", room="", phone=""
    ):
        self.cursor.execute(
            "UPDATE subjects SET name_uz=?, name_ru=?, name_tj=?, teacher=?, room=?, phone=? WHERE id=?",
            (name_uz, name_ru, name_tj, teacher, room, phone, id),
        )
        self.conn.commit()

    # ============== BAHOLAR ==============
    def get_grades(self, subject_id=None):
        if subject_id:
            self.cursor.execute(
                "SELECT g.*, s.name_uz, s.name_ru, s.name_tj FROM grades g JOIN subjects s ON g.subject_id=s.id WHERE g.subject_id=? ORDER BY g.date DESC",
                (subject_id,),
            )
        else:
            self.cursor.execute(
                "SELECT g.*, s.name_uz, s.name_ru, s.name_tj FROM grades g JOIN subjects s ON g.subject_id=s.id ORDER BY g.date DESC"
            )
        return self.cursor.fetchall()

    def add_grade(self, subject_id, grade, grade_type="Imtihon"):
        self.cursor.execute(
            "INSERT INTO grades (subject_id, grade, date, type, created_at) VALUES (?, ?, ?, ?, ?)",
            (
                subject_id,
                grade,
                date.today().isoformat(),
                grade_type,
                datetime.now().isoformat(),
            ),
        )
        self.conn.commit()

    def get_subject_average(self, subject_id):
        self.cursor.execute(
            "SELECT AVG(grade) as avg FROM grades WHERE subject_id=?", (subject_id,)
        )
        row = self.cursor.fetchone()
        return round(row["avg"]) if row["avg"] else 0

    # ============== DAVOMAT ==============
    def get_attendance(self, subject_id=None):
        if subject_id:
            self.cursor.execute(
                "SELECT * FROM attendance WHERE subject_id=? ORDER BY date DESC",
                (subject_id,),
            )
        else:
            self.cursor.execute("SELECT * FROM attendance ORDER BY date DESC")
        return self.cursor.fetchall()

    def add_attendance(self, subject_id, status="present"):
        self.cursor.execute(
            "INSERT INTO attendance (subject_id, date, status) VALUES (?, ?, ?)",
            (subject_id, date.today().isoformat(), status),
        )
        self.conn.commit()

    def get_attendance_stats(self, subject_id):
        self.cursor.execute(
            "SELECT COUNT(*) as total, SUM(CASE WHEN status='present' THEN 1 ELSE 0 END) as present FROM attendance WHERE subject_id=?",
            (subject_id,),
        )
        return self.cursor.fetchone()

    # ============== LEKSIYALAR ==============
    def get_lectures(self, subject_id):
        self.cursor.execute(
            "SELECT * FROM lectures WHERE subject_id=? ORDER BY created_at DESC",
            (subject_id,),
        )
        return self.cursor.fetchall()

    def add_lecture(
        self,
        subject_id,
        title_uz,
        title_ru,
        title_tj,
        content_uz,
        content_ru,
        content_tj,
    ):
        self.cursor.execute(
            "INSERT INTO lectures (subject_id, title_uz, title_ru, title_tj, content_uz, content_ru, content_tj, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                subject_id,
                title_uz,
                title_ru,
                title_tj,
                content_uz,
                content_ru,
                content_tj,
                datetime.now().isoformat(),
            ),
        )
        self.conn.commit()

    def delete_lecture(self, id):
        self.cursor.execute("DELETE FROM lectures WHERE id=?", (id,))
        self.conn.commit()

    # ============== DO'STLAR ==============
    def get_friends(self):
        self.cursor.execute("SELECT * FROM friends ORDER BY name")
        return self.cursor.fetchall()

    def get_friend(self, id):
        self.cursor.execute("SELECT * FROM friends WHERE id=?", (id,))
        return self.cursor.fetchone()

    def add_friend(
        self,
        name,
        birthday="",
        phone="",
        email="",
        telegram="",
        workplace="",
        notes="",
        importance=1,
        image_path="",
    ):
        self.cursor.execute(
            "INSERT INTO friends (name, birthday, phone, email, telegram, workplace, notes, importance, image_path, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                name,
                birthday,
                phone,
                email,
                telegram,
                workplace,
                notes,
                importance,
                image_path,
                datetime.now().isoformat(),
            ),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def update_friend(self, id, **kwargs):
        sets = ", ".join([f"{k}=?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [id]
        self.cursor.execute(f"UPDATE friends SET {sets} WHERE id=?", values)
        self.conn.commit()

    def delete_friend(self, id):
        self.cursor.execute("DELETE FROM friends WHERE id=?", (id,))
        self.conn.commit()

    def get_upcoming_birthdays(self, days=7):
        """Yaqinlashayotgan tug'ilgan kunlar"""
        today = date.today()
        self.cursor.execute("SELECT * FROM friends WHERE birthday != ''")
        friends = self.cursor.fetchall()
        upcoming = []
        for f in friends:
            try:
                bday_parts = f["birthday"].split("-")
                bday_this_year = date(
                    today.year, int(bday_parts[1]), int(bday_parts[2])
                )
                if bday_this_year < today:
                    bday_this_year = date(
                        today.year + 1, int(bday_parts[1]), int(bday_parts[2])
                    )
                diff = (bday_this_year - today).days
                if diff <= days:
                    upcoming.append((f, diff))
            except:
                pass
        return sorted(upcoming, key=lambda x: x[1])

    # ============== VAZIFALAR ==============
    def get_tasks(self, completed=None, category=None):
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []
        if completed is not None:
            query += " AND completed=?"
            params.append(completed)
        if category:
            query += " AND category=?"
            params.append(category)
        query += " ORDER BY due_date, due_time"
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_today_tasks(self):
        today = date.today().isoformat()
        self.cursor.execute(
            "SELECT * FROM tasks WHERE due_date=? AND completed=0 ORDER BY due_time",
            (today,),
        )
        return self.cursor.fetchall()

    def add_task(
        self,
        title,
        description="",
        due_date="",
        due_time="",
        category="shaxsiy",
        priority=1,
    ):
        self.cursor.execute(
            "INSERT INTO tasks (title, description, due_date, due_time, category, priority, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                title,
                description,
                due_date,
                due_time,
                category,
                priority,
                datetime.now().isoformat(),
            ),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def complete_task(self, id):
        self.cursor.execute("UPDATE tasks SET completed=1 WHERE id=?", (id,))
        self.conn.commit()

    def uncomplete_task(self, id):
        self.cursor.execute("UPDATE tasks SET completed=0 WHERE id=?", (id,))
        self.conn.commit()

    def delete_task(self, id):
        self.cursor.execute("DELETE FROM tasks WHERE id=?", (id,))
        self.conn.commit()

    # ============== ESLATMALAR ==============
    def get_reminders(self, unread_only=False):
        if unread_only:
            self.cursor.execute(
                "SELECT * FROM reminders WHERE read=0 ORDER BY date DESC, time DESC"
            )
        else:
            self.cursor.execute("SELECT * FROM reminders ORDER BY date DESC, time DESC")
        return self.cursor.fetchall()

    def add_reminder(self, title, message, date_str="", time="", type="general"):
        self.cursor.execute(
            "INSERT INTO reminders (title, message, date, time, type, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (title, message, date_str, time, type, datetime.now().isoformat()),
        )
        self.conn.commit()

    def mark_reminder_read(self, id):
        self.cursor.execute("UPDATE reminders SET read=1 WHERE id=?", (id,))
        self.conn.commit()

    def delete_reminder(self, id):
        self.cursor.execute("DELETE FROM reminders WHERE id=?", (id,))
        self.conn.commit()

    # ============== MAQSADLAR ==============
    def get_goals(self, completed=None):
        if completed is not None:
            self.cursor.execute("SELECT * FROM goals WHERE completed=?", (completed,))
        else:
            self.cursor.execute("SELECT * FROM goals ORDER BY target_date")
        return self.cursor.fetchall()

    def add_goal(self, title, description="", target_date=""):
        self.cursor.execute(
            "INSERT INTO goals (title, description, target_date, created_at) VALUES (?, ?, ?, ?)",
            (title, description, target_date, datetime.now().isoformat()),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def update_goal_progress(self, id, progress):
        completed = 1 if progress >= 100 else 0
        self.cursor.execute(
            "UPDATE goals SET progress=?, completed=? WHERE id=?",
            (progress, completed, id),
        )
        self.conn.commit()

    def delete_goal(self, id):
        self.cursor.execute("DELETE FROM goals WHERE id=?", (id,))
        self.conn.commit()

    def update_goal(self, id, title, description, target_date):
        self.cursor.execute(
            "UPDATE goals SET title=?, description=?, target_date=? WHERE id=?",
            (title, description, target_date, id),
        )
        self.conn.commit()

    # ============== KAYFIYAT ==============
    def get_moods(self, days=30):
        self.cursor.execute("SELECT * FROM moods ORDER BY date DESC LIMIT ?", (days,))
        return self.cursor.fetchall()

    def add_mood(self, mood, note=""):
        self.cursor.execute(
            "INSERT INTO moods (date, mood, note, created_at) VALUES (?, ?, ?, ?)",
            (date.today().isoformat(), mood, note, datetime.now().isoformat()),
        )
        self.conn.commit()

    def get_today_mood(self):
        today = date.today().isoformat()
        self.cursor.execute("SELECT * FROM moods WHERE date=?", (today,))
        return self.cursor.fetchone()

    # ============== YUTUQLAR ==============
    def get_achievements(self):
        self.cursor.execute("""
            SELECT a.*, CASE WHEN ua.id IS NOT NULL THEN 1 ELSE 0 END as user_unlocked, ua.unlocked_at
            FROM achievements a
            LEFT JOIN user_achievements ua ON a.id = ua.achievement_id
        """)
        return self.cursor.fetchall()

    def unlock_achievement(self, achievement_id):
        self.cursor.execute(
            "SELECT * FROM user_achievements WHERE achievement_id=?", (achievement_id,)
        )
        if not self.cursor.fetchone():
            self.cursor.execute(
                "INSERT INTO user_achievements (achievement_id, unlocked_at) VALUES (?, ?)",
                (achievement_id, datetime.now().isoformat()),
            )
            self.cursor.execute(
                "SELECT points FROM achievements WHERE id=?", (achievement_id,)
            )
            points = self.cursor.fetchone()["points"]
            self.add_points(points, "Yutuq ochildi")
            self.conn.commit()
            return True
        return False

    # ============== BALLAR ==============
    def get_points(self):
        self.cursor.execute("SELECT SUM(amount) as total FROM points")
        row = self.cursor.fetchone()
        return row["total"] if row["total"] else 0

    def add_points(self, amount, reason=""):
        self.cursor.execute(
            "INSERT INTO points (amount, reason, date) VALUES (?, ?, ?)",
            (amount, reason, date.today().isoformat()),
        )
        self.conn.commit()

    # ============== XARAJATLAR ==============
    def get_expenses(self, month=None):
        if month:
            self.cursor.execute(
                "SELECT * FROM expenses WHERE strftime('%Y-%m', date)=? ORDER BY date DESC",
                (month,),
            )
        else:
            self.cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
        return self.cursor.fetchall()

    def add_expense(self, amount, category, description="", expense_date=None):
        if expense_date is None:
            expense_date = date.today().isoformat()
        self.cursor.execute(
            "INSERT INTO expenses (amount, category, description, date, created_at) VALUES (?, ?, ?, ?, ?)",
            (amount, category, description, expense_date, datetime.now().isoformat()),
        )
        self.conn.commit()

    def get_monthly_expenses(self, month=None):
        if month is None:
            month = date.today().strftime("%Y-%m")
        self.cursor.execute(
            "SELECT category, SUM(amount) as total FROM expenses WHERE strftime('%Y-%m', date)=? GROUP BY category",
            (month,),
        )
        return self.cursor.fetchall()

    def get_monthly_total(self, month=None):
        if month is None:
            month = date.today().strftime("%Y-%m")
        self.cursor.execute(
            "SELECT SUM(amount) as total FROM expenses WHERE strftime('%Y-%m', date)=?",
            (month,),
        )
        row = self.cursor.fetchone()
        return row["total"] if row["total"] else 0

    def delete_expense(self, id):
        self.cursor.execute("DELETE FROM expenses WHERE id=?", (id,))
        self.conn.commit()

    # ============== POMODORO ==============
    def add_pomodoro_session(self, duration, subject_id=None):
        self.cursor.execute(
            "INSERT INTO pomodoro_sessions (duration, subject_id, date) VALUES (?, ?, ?)",
            (duration, subject_id, date.today().isoformat()),
        )
        self.conn.commit()

    def get_pomodoro_stats(self, days=7):
        self.cursor.execute(
            "SELECT SUM(duration) as total, COUNT(*) as sessions FROM pomodoro_sessions WHERE date >= date('now', ?)",
            (f"-{days} days",),
        )
        return self.cursor.fetchone()

    # ============== KUNLIK ==============
    def get_journal_entries(self, limit=50, include_secrets=True):
        if include_secrets:
            self.cursor.execute("SELECT * FROM journal ORDER BY created_at DESC LIMIT ?", (limit,))
        else:
            self.cursor.execute("SELECT * FROM journal WHERE is_secret=0 ORDER BY created_at DESC LIMIT ?", (limit,))
        return self.cursor.fetchall()
    
    def init_journal_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, content TEXT, date TEXT, created_at TEXT,
            type TEXT DEFAULT 'note', -- idea, win, pain, note
            is_secret INTEGER DEFAULT 0
        )""")
        self.conn.commit()

    def add_journal_entry(self, title, content, entry_type="note", is_secret=False):
        d = date.today().isoformat()
        self.cursor.execute(
            "INSERT INTO journal (title, content, date, created_at, type, is_secret) VALUES (?,?,?,?,?,?)",
            (title, content, d, datetime.now().isoformat(), entry_type, int(is_secret))
        )
        self.conn.commit()

    def delete_journal_entry(self, id):
        self.cursor.execute("DELETE FROM journal WHERE id=?", (id,))
        self.conn.commit()
        
    def update_journal_entry(self, id, title, content):
        self.cursor.execute(
            "UPDATE journal SET title=?, content=? WHERE id=?",
            (title, content, id)
        )
        self.conn.commit()
        
    def search_journal(self, query, include_secrets=False):
        like_q = f"%{query}%"
        if include_secrets:
            self.cursor.execute("SELECT * FROM journal WHERE title LIKE ? OR content LIKE ? ORDER BY created_at DESC", (like_q, like_q))
        else:
            self.cursor.execute("SELECT * FROM journal WHERE (title LIKE ? OR content LIKE ?) AND is_secret=0 ORDER BY created_at DESC", (like_q, like_q))
        return self.cursor.fetchall()

    # ============== AI XABARLAR ==============
    def add_ai_message(self, message, type="info"):
        self.cursor.execute(
            "INSERT INTO ai_messages (message, type, date) VALUES (?, ?, ?)",
            (message, type, datetime.now().isoformat()),
        )
        self.conn.commit()

    def get_unread_ai_messages(self):
        self.cursor.execute("SELECT * FROM ai_messages WHERE read=0 ORDER BY date DESC")
        return self.cursor.fetchall()

    def mark_ai_message_read(self, id):
        self.cursor.execute("UPDATE ai_messages SET read=1 WHERE id=?", (id,))
        self.conn.commit()

    # ============== STATISTIKA (AI UCHUN) ==============
    def get_study_stats(self):
        """O'quv statistikasi"""
        stats = {}
        subjects = self.get_subjects()
        for s in subjects:
            avg = self.get_subject_average(s["id"])
            att = self.get_attendance_stats(s["id"])
            stats[s["id"]] = {
                "name_uz": s["name_uz"],
                "name_ru": s["name_ru"],
                "name_tj": s["name_tj"],
                "average": avg,
                "total_lessons": att["total"] if att["total"] else 0,
                "attended": att["present"] if att["present"] else 0,
            }
        return stats

    def get_task_completion_rate(self, days=7):
        """Vazifalarni bajarish darajasi"""
        self.cursor.execute(
            "SELECT COUNT(*) as total, SUM(completed) as completed FROM tasks WHERE due_date >= date('now', ?)",
            (f"-{days} days",),
        )
        row = self.cursor.fetchone()
        total = row["total"] or 0
        completed = row["completed"] or 0
        return {
            "total": total,
            "completed": completed,
            "rate": round(completed / total * 100) if total > 0 else 0,
        }

    def get_streak(self):
        """Ketma-ket kunlar"""
        self.cursor.execute(
            "SELECT DISTINCT due_date FROM tasks WHERE completed=1 AND due_date != '' ORDER BY due_date DESC"
        )
        dates = [row["due_date"] for row in self.cursor.fetchall()]
        if not dates:
            return 0
        streak = 1
        for i in range(len(dates) - 1):
            try:
                d1 = date.fromisoformat(dates[i])
                d2 = date.fromisoformat(dates[i + 1])
                if (d1 - d2).days == 1:
                    streak += 1
                else:
                    break
            except:
                break
        return streak

        # ============== BYUDJET / DAROMAD TIZIMI ==============

    def ensure_income_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL, source TEXT, description TEXT, date TEXT, created_at TEXT
        )""")
        self.conn.commit()

        # ============== VAQT USTASI SOZLAMALARI ==============

    def get_timer_settings(self):
        """Fokus va dam olish vaqtlarini daqiqada qaytaradi"""
        focus = int(self.get_setting("timer_focus_min", "25"))
        break_ = int(self.get_setting("timer_break_min", "5"))
        return {"focus": focus, "break": break_}

    def set_timer_settings(self, focus_min, break_min):
        self.set_setting("timer_focus_min", str(focus_min))
        self.set_setting("timer_break_min", str(break_min))

    def add_income(self, amount, source, description="", date_str=None):
        d = date_str or date.today().isoformat()
        self.cursor.execute(
            "INSERT INTO income (amount, source, description, date, created_at) VALUES (?,?,?,?,?)",
            (amount, source, description, d, datetime.now().isoformat()),
        )
        self.conn.commit()

    def get_incomes(self, month=None):
        if month:
            self.cursor.execute(
                "SELECT * FROM income WHERE date LIKE ? ORDER BY date DESC",
                (f"{month}%",),
            )
        else:
            self.cursor.execute("SELECT * FROM income ORDER BY date DESC")
        return self.cursor.fetchall()

    def get_monthly_income_total(self):
        m = date.today().strftime("%Y-%m")
        self.cursor.execute(
            "SELECT COALESCE(SUM(amount),0) as s FROM income WHERE date LIKE ?",
            (f"{m}%",),
        )
        return self.cursor.fetchone()["s"] or 0

    def delete_income(self, id):
        self.cursor.execute("DELETE FROM income WHERE id=?", (id,))
        self.conn.commit()

    def get_expenses_by_category(self, month=None):
        m = month or date.today().strftime("%Y-%m")
        self.cursor.execute(
            "SELECT category, SUM(amount) as total FROM expenses WHERE date LIKE ? GROUP BY category ORDER BY total DESC",
            (f"{m}%",),
        )
        return self.cursor.fetchall()

    def get_incomes_by_source(self, month=None):
        m = month or date.today().strftime("%Y-%m")
        self.cursor.execute(
            "SELECT source, SUM(amount) as total FROM income WHERE date LIKE ? GROUP BY source ORDER BY total DESC",
            (f"{m}%",),
        )
        return self.cursor.fetchall()

    def get_daily_expenses(self, days=7):
        out = []
        for i in range(days - 1, -1, -1):
            d = date.today() - timedelta(days=i)
            self.cursor.execute(
                "SELECT COALESCE(SUM(amount),0) as s FROM expenses WHERE date=?",
                (d.isoformat(),),
            )
            out.append((d, self.cursor.fetchone()["s"] or 0))
        return out

    def get_expense_limit(self):
        v = self.get_setting("expense_limit", "0")
        try:
            return float(v)
        except Exception:
            return 0.0

    def set_expense_limit(self, amount):
        self.set_setting("expense_limit", str(amount))

    def close(self):
        self.conn.close()
        
    def fix_journal_types(self):
        """Eski 'note' yozuvlarni matniga qarab 'idea', 'win' yoki 'pain' ga o'tkazish"""
        self.cursor.execute("SELECT id, content FROM journal WHERE type='note'")
        rows = self.cursor.fetchall()
        
        for row in rows:
            txt = row["content"].lower()
            new_type = "note" # Default
            
            if any(w in txt for w in ["g'oya", "fikr", "idea", "kelajakda", "orzu"]):
                new_type = "idea"
            elif any(w in txt for w in ["baho", "oylik", "yutdim", "tabrik", "zo'r", "ajoyib"]):
                new_type = "win"
            elif any(w in txt for w in ["dard", "muammo", "yomon", "charchadim", "xafa"]):
                new_type = "pain"
                
            if new_type != "note":
                self.cursor.execute("UPDATE journal SET type=? WHERE id=?", (new_type, row["id"]))
        self.conn.commit()

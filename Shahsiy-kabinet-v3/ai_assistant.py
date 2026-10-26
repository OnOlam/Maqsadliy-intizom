import random
from datetime import datetime, date, timedelta
from translations import tr


class AIAssistant:
    def __init__(self, db, lang):
        self.db = db
        self.lang = lang

    def generate_messages(self):
        messages = []
        today = date.today().isoformat()

        # 1. Vazifalar dinamikasi
        pending = self.db.get_tasks(completed=0)
        completed_today = [
            t for t in self.db.get_tasks(completed=1) if t["due_date"] == today
        ]

        if pending:
            high_prio = [t for t in pending if t["priority"] == 3]
            if high_prio:
                messages.append(
                    f"⚠️ Diqqat! {len(high_prio)} ta YUQORI muhimlikdagi vazifa kutilmoqda."
                )
            else:
                messages.append(
                    f"📋 Bugun {len(pending)} ta vazifa bor. Rejangizni tekshiring."
                )

        if completed_today:
            messages.append(
                f" Ajoyib! Bugun allaqachon {len(completed_today)} ta vazifani yakunlagansiz."
            )

        # 2. Byudjet xavfsizligi (Agar limit belgilangan bo'lsa)
        limit = self.db.get_expense_limit()
        spent = self.db.get_monthly_total()
        if limit > 0:
            pct = (spent / limit) * 100
            if pct >= 90:
                messages.append(
                    f"💸 XAVF! Oylik byudjetingizning {pct:.0f}% i ketdi. Ehtiyot bo'ling."
                )
            elif pct >= 70:
                messages.append(
                    f"📉 Byudjet monitoringi: {pct:.0f}% ishlatilgan. Orta daraja."
                )

        # 3. Fokus odati (Pomodoro/Vaqt ustasi)
        stats = self.db.get_pomodoro_stats(7)
        sessions = stats["sessions"] or 0
        if sessions >= 5:
            messages.append(
                f"🔥 Haftalik rekord! So'nggi 7 kunda {sessions} ta fokus sessiyasi. Tempni tushirmang!"
            )
        elif sessions == 0 and self.db.get_setting("timer_focus_min"):
            messages.append(
                "☕ So'nggi haftada fokus sessiyalari yo'q. Bir muddat dam olish kerakmi?"
            )

        # 4. Ruxiy Miya tahlili (Journal)
        recent_journals = self.db.get_journal_entries(limit=5)
        pains = [j for j in recent_journals if j["type"] == "pain"]
        wins = [j for j in recent_journals if j["type"] == "win"]

        if len(pains) >= 3:
            messages.append(
                "💙 So'nggi kunlarda biroz og'ir kechayotganga o'xshaysiz. Do'stlaringiz bilan suhbatlashing yoki sport qiling."
            )
        elif len(wins) >= 3:
            messages.append(
                "✨ Energiyangiz yuqori! Shu kayfiyatdan foydalanib, qiyin vazifalarni hal qiling."
            )

        # 5. Motivatsiya (Random)
        quotes = tr("ai_motivation", self.lang)
        if quotes:
            messages.append(random.choice(quotes))

        return messages

    def greeting(self):
        """Salomlashish"""
        hour = datetime.now().hour

        if hour < 6:
            time_greeting = {
                "uz": "Tun yarim! Uxlay olmadingizmi?",
                "ru": "Полночь! Не можете уснуть?",
                "tj": "Ними шаб! Хоб рафта намекунед?",
            }
        elif hour < 12:
            time_greeting = {
                "uz": "Xayrli tong!",
                "ru": "Доброе утро!",
                "tj": "Субҳ бахайр!",
            }
        elif hour < 18:
            time_greeting = {
                "uz": "Xayrli kun!",
                "ru": "Добрый день!",
                "tj": "Рӯзи хуш!",
            }
        else:
            time_greeting = {
                "uz": "Xayrli kech!",
                "ru": "Добрый вечер!",
                "tj": "Шоми хуш!",
            }

        return f"👋 {time_greeting[self.lang]} {tr('ai_greeting', self.lang)}"

    def analyze_tasks(self):
        """Vazifalarni tahlil qilish"""
        today_tasks = self.db.get_today_tasks()

        if not today_tasks:
            return None

        # Muhim vazifalar
        high_priority = [t for t in today_tasks if t["priority"] == 3]

        if high_priority:
            msg = {
                "uz": f"🔥 BUGUN {len(high_priority)} ta MUHIM vazifa bor!",
                "ru": f"🔥 СЕГОДНЯ {len(high_priority)} ВАЖНЫХ задач!",
                "tj": f"🔥 ИМРӮЗ {len(high_priority)} ВАЗИФАҲОИ МУҲИМ!",
            }
            return msg[self.lang]

        # Umumiy vazifalar
        msg = tr("ai_task_reminder", self.lang).format(count=len(today_tasks))
        return f"📋 {msg}"

    def analyze_birthdays(self):
        """Tug'ilgan kunlarni tahlil qilish"""
        birthdays = self.db.get_upcoming_birthdays(0)

        if not birthdays:
            return None

        messages = []
        for friend, days in birthdays:
            if days == 0:
                msg = tr("ai_birthday_reminder", self.lang).format(name=friend["name"])
                messages.append(msg)

        return "\n".join(messages) if messages else None

    def analyze_study(self):
        """O'quvni tahlil qilish"""
        stats = self.db.get_study_stats()

        if not stats:
            return None

        # Eng yaxshi va eng yomon fanlar
        best_subjects = []
        worst_subjects = []

        for subj_id, data in stats.items():
            avg = data["average"]
            if avg >= 85:
                best_subjects.append(data[f"name_{self.lang}"])
            elif avg < 60 and avg > 0:
                worst_subjects.append(data[f"name_{self.lang}"])

        messages = []

        # Eng yaxshi fanlar
        if best_subjects:
            msg = {
                "uz": f"🌟 Siz {', '.join(best_subjects[:2])} da a'lochisiz!",
                "ru": f"🌟 Вы отличник по {', '.join(best_subjects[:2])}!",
                "tj": f"🌟 Шумо дар {', '.join(best_subjects[:2])} аълочӣ ҳастед!",
            }
            messages.append(msg[self.lang])

        # Eng yomon fanlar
        if worst_subjects:
            msg = {
                "uz": f"⚠️ {', '.join(worst_subjects[:2])} ga ko'proq vaqt ajrating",
                "ru": f"⚠️ Уделите больше времени {', '.join(worst_subjects[:2])}",
                "tj": f"⚠️ Ба {', '.join(worst_subjects[:2])} бештар вақт ҷудо кунед",
            }
            messages.append(msg[self.lang])

        return "\n".join(messages) if messages else None

    def motivation(self):
        """Motivatsion xabar"""
        motivations = tr("ai_motivation", self.lang)
        return f"💫 {random.choice(motivations)}"

    def analyze_warnings(self):
        """Ogohlantirishlar"""
        warnings = []

        # Davomat past bo'lsa
        stats = self.db.get_study_stats()
        for subj_id, data in stats.items():
            total = data["total_lessons"]
            attended = data["attended"]
            if total > 0:
                percent = (attended / total) * 100
                if percent < 70:
                    msg = {
                        "uz": f"⚠️ {data[f'name_{self.lang}']} davomati {int(percent)}% - ehtiyot bo'ling!",
                        "ru": f"⚠️ Посещаемость {data[f'name_{self.lang}']} {int(percent)}% - осторожно!",
                        "tj": f"⚠️ Ҳозирии {data[f'name_{self.lang}']} {int(percent)}% - эҳтиёт бошед!",
                    }
                    warnings.append(msg[self.lang])
                    break  # Faqat bitta ogohlantirish

        # Vazifalar kechiktirilgan bo'lsa
        overdue_tasks = self.get_overdue_tasks()
        if overdue_tasks:
            msg = {
                "uz": f"⏰ {len(overdue_tasks)} ta vazifa muddati o'tdi!",
                "ru": f"⏰ {len(overdue_tasks)} задач просрочено!",
                "tj": f"⏰ {len(overdue_tasks)} вазифа мӯҳлаташ гузашт!",
            }
            warnings.append(msg[self.lang])

        return "\n".join(warnings) if warnings else None

    def get_overdue_tasks(self):
        """Muddati o'tgan vazifalar"""
        today = date.today().isoformat()
        all_tasks = self.db.get_tasks(completed=0)
        return [t for t in all_tasks if t["due_date"] and t["due_date"] < today]

    def analyze_advice(self):
        """Tavsiyalar"""
        advices = []

        # Ketma-ketlik
        streak = self.db.get_streak()
        if streak >= 5:
            msg = {
                "uz": f"🔥 {streak} kun ketma-ket vazifalarni bajardingiz! Davom eting!",
                "ru": f"🔥 {streak} дней подряд выполняете задачи! Продолжайте!",
                "tj": f"🔥 {streak} рӯз пай дар пай вазифаҳоро иҷро мекунед! Давом диҳед!",
            }
            advices.append(msg[self.lang])

        # Vazifalarni bajarish darajasi
        completion = self.db.get_task_completion_rate(7)
        if completion["total"] > 0:
            rate = completion["rate"]
            if rate >= 80:
                msg = {
                    "uz": f"✅ Oxirgi 7 kunda vazifalarni {rate}% bajardingiz - zo'rsiz!",
                    "ru": f"✅ За последние 7 дней выполнили {rate}% задач - отлично!",
                    "tj": f"✅ Дар 7 рӯзи охир {rate}% вазифаҳоро иҷро кардед - аъло!",
                }
                advices.append(msg[self.lang])
            elif rate < 50:
                msg = {
                    "uz": f"📊 Oxirgi 7 kunda faqat {rate}% vazifani bajardingiz. Ko'proq harakat qiling!",
                    "ru": f"📊 За последние 7 дней выполнили только {rate}% задач. Больше усилий!",
                    "tj": f"📊 Дар 7 рӯзи охир танҳо {rate}% вазифаҳоро иҷро кардед. Бештар кӯшиш кунед!",
                }
                advices.append(msg[self.lang])

        # Pomodoro statistikasi
        pomodoro = self.db.get_pomodoro_stats(7)
        if pomodoro["sessions"] >= 10:
            msg = {
                "uz": f"🍅 Bu hafta {pomodoro['sessions']} ta pomodoro sessiyasi - fokus ustasiz!",
                "ru": f"🍅 На этой неделе {pomodoro['sessions']} сессий помодоро - мастер фокуса!",
                "tj": f"🍅 Дар ин ҳафта {pomodoro['sessions']} сессияи помодоро - устои тамаркуз!",
            }
            advices.append(msg[self.lang])

        return random.choice(advices) if advices else None

    def check_achievements(self):
        """Yutuqlarni tekshirish va ochish"""
        unlocked = []

        # Birinchi qadam
        if self.db.get_points() > 0:
            if self.db.unlock_achievement(1):
                unlocked.append("Birinchi qadam")

        # 5 kun ketma-ket
        streak = self.db.get_streak()
        if streak >= 5:
            if self.db.unlock_achievement(2):
                unlocked.append("5 kun ketma-ket")

        # 10 kun ketma-ket
        if streak >= 10:
            if self.db.unlock_achievement(3):
                unlocked.append("10 kun ketma-ket")

        # A'lochi
        stats = self.db.get_study_stats()
        if stats:
            all_above_90 = all(
                data["average"] >= 90 for data in stats.values() if data["average"] > 0
            )
            if all_above_90 and len(stats) >= 3:
                if self.db.unlock_achievement(4):
                    unlocked.append("A'lochi")

        # Ijtimoiy
        friends_count = len(self.db.get_friends())
        if friends_count >= 10:
            if self.db.unlock_achievement(5):
                unlocked.append("Ijtimoiy")

        # Pomodoro ustasi
        pomodoro = self.db.get_pomodoro_stats(365)
        if pomodoro["sessions"] >= 50:
            if self.db.unlock_achievement(6):
                unlocked.append("Pomodoro ustasi")

        # Maqsad sari
        goals = self.db.get_goals(completed=1)
        if goals:
            if self.db.unlock_achievement(7):
                unlocked.append("Maqsad sari")

        return unlocked

        # ============== JURNAL TAHLILI (MIYA UZOG'I) ==============

    def analyze_new_entry(self, title, content, entry_type):
        """Yangi yozuv kelganda AI darhol javob beradi"""
        resp = ""
        low_content = content.lower()

        if entry_type == "win":
            resp = "🎉 Tabriklayman! Bu g'alabangizni eslab qoling — u sizga keyinroq kuch beradi."
        elif entry_type == "pain":
            resp = "💙 Tushunaman, hayotda shunday damlar ham bor. Nima yordam bera olaman? Dam olishni unutmang."
        elif entry_type == "idea":
            resp = "💡 Qiziqarli fikr! Buni rejangizga aylantirsangiz-chi?"
        else:
            resp = "📝 Yozdingiz. Esda tutaman."

        # Maxfiylik tekshiruvi
        if any(word in low_content for word in ["sir", "maxfiy", "hech kimga aytma"]):
            resp += "\n🔒 *Bu yozuv maxfiy deb belgilandi.*"

        return resp

    def find_related_memories(self, current_text):
        """Eski yozuvlardan mosligini topish"""
        words = [w.strip(".,!?").lower() for w in current_text.split() if len(w) > 3]
        if not words:
            return []

        matches = []
        all_notes = self.db.get_journal_entries(limit=100)
        for note in all_notes:
            score = sum(1 for w in words if w in note["content"].lower())
            if score >= 2:  # Kamida 2 ta umumiy so'z
                matches.append((note, score))

        matches.sort(key=lambda x: x[1], reverse=True)
        return [m[0] for m in matches[:3]]  # Top 3

    def generate_reminders(self):
        """Kechagi/haftadagi muhim narsalarni eslatish"""
        reminders = []
        today = date.today()

        # So'nggi 7 kundagi 'idea' va 'win' larni ko'rish
        recent = self.db.get_journal_entries(limit=20)
        ideas = [e for e in recent if e["type"] == "idea"]
        wins = [e for e in recent if e["type"] == "win"]

        if ideas:
            last_idea = ideas[0]
            days_diff = (today - date.fromisoformat(last_idea["date"])).days
            if days_diff > 2:
                reminders.append(
                    f"💭 {days_diff} kun oldin '{last_idea['title']}' haqida fikr bildirgandingiz. Hali ham dolzarpmi?"
                )

        if wins:
            reminders.append(
                f"🏆 So'nggi haftada {len(wins)} ta g'alabangizni qayd etdingiz. Davom eting!"
            )

        return reminders

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
from datetime import date
from translations import tr
from ui_widgets import (
    ModernEntry,
    ModernButton,
    ChipGroup,
    round_rect,
    RoundedCard,
    lighten_color,
    make_pill_button,
)

COLORS = {
    "coffee_dark": "#3e2723",
    "coffee": "#6f4e37",
    "caramel": "#8b4513",
    "sand": "#d4a574",
    "cream": "#fefae0",
    "milk": "#f5e6d3",
    "gold": "#d4a017",
    "error": "#c62828",
    "success": "#2e7d32",
    "blue": "#2f6f8f",
    "purple": "#7b1fa2",
}


class SettingsScreen:
    def __init__(self, parent, db, lang, on_back=None):
        self.parent = parent
        self.db = db
        self.lang = lang
        self.on_back = on_back
        self.build_ui()

    # ================= UI =================
    def build_ui(self):
        for w in self.parent.winfo_children():
            w.destroy()

        header = tk.Frame(self.parent, bg=COLORS["milk"])
        header.pack(fill="x", padx=20, pady=(18, 10))
        tk.Label(
            header,
            text=f"⚙️ {tr('settings', self.lang)}",
            font=("Segoe UI", 20, "bold"),
            bg=COLORS["milk"],
            fg=COLORS["coffee_dark"],
        ).pack(side="left")
        if self.on_back:
            back_btn = make_pill_button(
                header,
                "← " + self._t("Orqaga", "Назад", "Ба ақиб"),
                COLORS["coffee"],
                self.on_back,
                outer_bg=COLORS["milk"],
                height=36,
                min_width=100,
                font_size=10,
            )
            back_btn.pack(side="right")

        # Scrollable konteyner
        container = tk.Frame(self.parent, bg=COLORS["milk"])
        container.pack(fill="both", expand=True, padx=20, pady=(0, 18))
        canvas = tk.Canvas(container, bg=COLORS["milk"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg=COLORS["milk"])
        win = canvas.create_window((0, 0), window=body, anchor="nw")

        def _conf(e):
            canvas.itemconfig(win, width=e.width)
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<Configure>", _conf)
        body.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _wheel(e):
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _wheel)
        body.bind("<MouseWheel>", _wheel)

        # --- BO'LIMLAR ---
        self._section_lang(body)
        self._section_security(body)
        self._section_data(body)
        self._section_about(body)
        self._section_danger(body)

    # ================= TIL BO'LIMI =================
    def _section_lang(self, parent):
        card = RoundedCard(
            parent, title="🌐 Til va Viloyat", header_bg=COLORS["coffee"]
        )
        card.pack(fill="x", padx=10, pady=8)

        inner = tk.Frame(card.inner, bg=COLORS["cream"])
        inner.pack(fill="x", padx=14, pady=10)

        tk.Label(
            inner,
            text=self._t("Interfeys tili:", "Язык интерфейса:", "Забони интерфейс:"),
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["cream"],
            fg=COLORS["coffee_dark"],
        ).pack(anchor="w")

        # Bayroq chip'lari
        lang_opts = [
            ("uz", "🇺🇿 O'zbek", COLORS["success"]),
            ("ru", "🇷🇺 Русский", COLORS["blue"]),
            ("tj", "🇹🇯 Тоҷикӣ", COLORS["caramel"]),
        ]
        self.lang_group = ChipGroup(
            inner, lang_opts, self.lang, outer_bg=COLORS["cream"]
        )
        self.lang_group.pack(anchor="w", pady=(6, 10))

        tk.Button(
            inner,
            text=self._t("Saqlash", "Сохранить", "Нигоҳ доштан"),
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["caramel"],
            fg=COLORS["cream"],
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=6,
            command=self._change_language,
        ).pack(anchor="w")

    def _change_language(self):
        new_lang = self.lang_group.get()
        if new_lang != self.lang:
            self.db.set_setting("language", new_lang)
            self.lang = new_lang
            messagebox.showinfo(
                self._t("Muvaffaqiyat", "Успех", "Муваффақият"),
                self._t(
                    "Til o'zgardi! Ilovani qayta ishga tushiring.",
                    "Язык изменён! Перезапустите приложение.",
                    "Забон тағйир ёфт! Барнома дубора оғоз кунед.",
                ),
            )
            if self.on_back:
                self.on_back()

    # ================= XAVFSIZLIK BO'LIMI =================
    def _section_security(self, parent):
        card = RoundedCard(parent, title="🔐 Xavfsizlik", header_bg=COLORS["caramel"])
        card.pack(fill="x", padx=10, pady=8)

        inner = tk.Frame(card.inner, bg=COLORS["cream"])
        inner.pack(fill="x", padx=14, pady=10)

        tk.Label(
            inner,
            text=self._t("PIN kodni o'zgartirish", "Изменить PIN", "Тағйири PIN"),
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["cream"],
            fg=COLORS["coffee_dark"],
        ).pack(anchor="w", pady=(0, 8))

        form = tk.Frame(inner, bg=COLORS["cream"])
        form.pack(fill="x")

        def lbl(t):
            tk.Label(
                form,
                text=t,
                font=("Segoe UI", 10),
                bg=COLORS["cream"],
                fg=COLORS["coffee"],
            ).pack(anchor="w", pady=(6, 2))

        lbl(self._t("Joriy PIN", "Текущий PIN", "PIN ҷорӣ"))
        old_pin_e = ModernEntry(
            form, outer_bg=COLORS["cream"], placeholder="****", show="*"
        )
        old_pin_e.pack(fill="x")

        lbl(self._t("Yangi PIN (4 raqam)", "Новый PIN (4 цифры)", "PIN нав (4 рақам)"))
        new_pin_e = ModernEntry(
            form, outer_bg=COLORS["cream"], placeholder="1234", show="*"
        )
        new_pin_e.pack(fill="x")

        lbl(
            self._t(
                "Yangi PIN takrorlang", "Повторите новый PIN", "PIN навро такрор кунед"
            )
        )
        confirm_pin_e = ModernEntry(
            form, outer_bg=COLORS["cream"], placeholder="1234", show="*"
        )
        confirm_pin_e.pack(fill="x")

        def save_pin():
            old = old_pin_e.get().strip()
            new = new_pin_e.get().strip()
            conf = confirm_pin_e.get().strip()

            if not old or not new or not conf:
                messagebox.showerror(
                    tr("error", self.lang),
                    self._t(
                        "Barcha maydonlarni to'ldiring!",
                        "Заполните все поля!",
                        "Ҳама майдонҳоро пур кунед!",
                    ),
                )
                return

            if not self.db.check_pin(old):
                messagebox.showerror(
                    tr("error", self.lang),
                    self._t(
                        "Joriy PIN noto'g'ri!",
                        "Текущий PIN неверный!",
                        "PIN ҷорӣ нодуруст аст!",
                    ),
                )
                return

            if len(new) != 4 or not new.isdigit():
                messagebox.showerror(
                    tr("error", self.lang),
                    self._t(
                        "Yangi PIN 4 ta raqamdan iborat bo'lishi kerak!",
                        "Новый PIN должен состоять из 4 цифр!",
                        "PIN нав бояд аз 4 рақам иборат бошад!",
                    ),
                )
                return

            if new != conf:
                messagebox.showerror(
                    tr("error", self.lang),
                    self._t(
                        "PIN'lar mos kelmadi!",
                        "PIN-коды не совпадают!",
                        "PIN-ҳо мувофиқат намекунанд!",
                    ),
                )
                return

            self.db.update_user(pin=new)
            old_pin_e.clear_text()
            new_pin_e.clear_text()
            confirm_pin_e.clear_text()
            messagebox.showinfo(
                self._t("Muvaffaqiyat", "Успех", "Муваффақият"),
                self._t(
                    "PIN muvaffaqiyatli o'zgartirildi!",
                    "PIN успешно изменён!",
                    "PIN бомуваффақият тағйир дода шуд!",
                ),
            )

        ModernButton(
            inner,
            outer_bg=COLORS["cream"],
            text=self._t("PIN ni saqlash", "Сохранить PIN", "Нигоҳ доштани PIN"),
            command=save_pin,
        ).pack(pady=(10, 0))

    # ================= MA'LUMOTLAR BO'LIMI =================
    def _section_data(self, parent):
        card = RoundedCard(parent, title="📊 Ma'lumotlar", header_bg=COLORS["gold"])
        card.pack(fill="x", padx=10, pady=8)

        inner = tk.Frame(card.inner, bg=COLORS["cream"])
        inner.pack(fill="x", padx=14, pady=10)

        btn_row = tk.Frame(inner, bg=COLORS["cream"])
        btn_row.pack(fill="x", pady=4)

        self._action_btn(
            btn_row, "📤 JSON eksport", COLORS["success"], self._export_json
        ).pack(side="left", padx=4)
        self._action_btn(
            btn_row, "📥 JSON import", COLORS["caramel"], self._import_json
        ).pack(side="left", padx=4)
        self._action_btn(
            btn_row, "📋 CSV vazifalar", COLORS["coffee"], self._export_csv_tasks
        ).pack(side="left", padx=4)

        # Statistika
        stats_frame = tk.Frame(inner, bg=COLORS["milk"], padx=10, pady=8)
        stats_frame.pack(fill="x", pady=(10, 0))

        user = self.db.get_user()
        subjects_count = len(self.db.get_subjects())
        friends_count = len(self.db.get_friends())
        tasks_count = len(self.db.get_tasks())
        points = self.db.get_points()

        stats_data = [
            (
                "👤",
                user["name"] if user else "-",
                self._t("Foydalanuvchi", "Пользователь", "Корбар"),
            ),
            ("📚", str(subjects_count), self._t("Fanlar", "Предметы", "Фаннҳо")),
            ("👥", str(friends_count), self._t("Do'stlar", "Друзья", "Дӯстон")),
            ("✅", str(tasks_count), self._t("Vazifalar", "Задачи", "Вазифаҳо")),
            ("⭐", str(points), self._t("Ball", "Баллы", "Холҳо")),
        ]

        for i, (icon, val, lab) in enumerate(stats_data):
            r, c = divmod(i, 3)
            tile = tk.Frame(stats_frame, bg=COLORS["milk"], padx=8, pady=6)
            tile.grid(row=r, column=c, sticky="nsew", padx=4, pady=2)
            tk.Label(tile, text=icon, font=("Segoe UI", 16), bg=COLORS["milk"]).pack()
            tk.Label(
                tile,
                text=val,
                font=("Segoe UI", 14, "bold"),
                bg=COLORS["milk"],
                fg=COLORS["coffee_dark"],
            ).pack()
            tk.Label(
                tile,
                text=lab,
                font=("Segoe UI", 9),
                bg=COLORS["milk"],
                fg=COLORS["coffee"],
            ).pack()
            stats_frame.grid_columnconfigure(c, weight=1)

    def _action_btn(self, parent, text, color, cmd):
        b = tk.Canvas(
            parent, height=36, highlightthickness=0, bg=COLORS["cream"], cursor="hand2"
        )
        b._text, b._color = text, color
        b.bind("<Configure>", lambda e, bb=b: self._paint_action(bb, False))
        b.bind("<Enter>", lambda e, bb=b: self._paint_action(bb, True))
        b.bind("<Leave>", lambda e, bb=b: self._paint_action(bb, False))
        b.bind("<Button-1>", lambda e: cmd())
        self._paint_action(b, False)
        return b

    def _paint_action(self, b, hover):
        w, h = b.winfo_width(), b.winfo_height()
        if w < 10:
            w = 140
        b.delete("all")
        fill = lighten_color(b._color) if hover else b._color
        round_rect(b, 0, 0, w - 1, h - 1, radius=h / 2, fill=fill, outline="")
        b.create_text(
            w / 2,
            h / 2,
            text=b._text,
            fill=COLORS["cream"],
            font=("Segoe UI", 10, "bold"),
        )

    def _export_json(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"cozy_backup_{date.today().isoformat()}.json",
        )
        if not path:
            return
        try:
            data = {}
            tables = [
                "users",
                "subjects",
                "friends",
                "tasks",
                "goals",
                "expenses",
                "income",
                "journal",
                "pomodoro_sessions",
                "grades",
                "attendance",
                "lectures",
            ]
            for table in tables:
                try:
                    self.db.cursor.execute(f"SELECT * FROM {table}")
                    rows = self.db.cursor.fetchall()
                    data[table] = [dict(r) for r in rows]
                except:
                    pass
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo(
                self._t("Muvaffaqiyat", "Успех", "Муваффақият"),
                self._t(
                    "Backup yaratildi!",
                    "Резервная копия создана!",
                    "Нусхабардорӣ сохта шуд!",
                ),
            )
        except Exception as e:
            messagebox.showerror(tr("error", self.lang), str(e))

    def _import_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path:
            return
        if not messagebox.askyesno(
            self._t("Diqqat", "Внимание", "Эҳтиёт"),
            self._t(
                "Bu am mavjud ma'lumotlarni almashtiradi!\nDavom etasizmi?",
                "Это заменит существующие данные!\nПродолжить?",
                "Ин ам маълумоти мавҷударо иваз мекунад!\nИдома медиҳед?",
            ),
        ):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Oddiy import: har bir jadvalni tozalab, qayta to'ldirish
            for table, rows in data.items():
                if table == "users":
                    continue  # Foydalanuvchini almashtirmaymiz
                try:
                    self.db.cursor.execute(f"DELETE FROM {table}")
                    for row in rows:
                        cols = ", ".join(row.keys())
                        placeholders = ", ".join(["?" for _ in row])
                        vals = list(row.values())
                        self.db.cursor.execute(
                            f"INSERT INTO {table} ({cols}) VALUES ({placeholders})",
                            vals,
                        )
                except:
                    pass
            self.db.conn.commit()
            messagebox.showinfo(
                self._t("Muvaffaqiyat", "Успех", "Муваффақият"),
                self._t(
                    "Ma'lumotlar tiklandi!",
                    "Данные восстановлены!",
                    "Маълумот барқарор карда шуд!",
                ),
            )
            if self.on_back:
                self.on_back()
        except Exception as e:
            messagebox.showerror(tr("error", self.lang), str(e))

    def _export_csv_tasks(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"tasks_{date.today().isoformat()}.csv",
        )
        if not path:
            return
        try:
            tasks = self.db.get_tasks()
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "ID",
                        "Title",
                        "Description",
                        "Due Date",
                        "Time",
                        "Category",
                        "Priority",
                        "Completed",
                    ]
                )
                for t in tasks:
                    writer.writerow(
                        [
                            t["id"],
                            t["title"],
                            t["description"],
                            t["due_date"],
                            t["due_time"],
                            t["category"],
                            t["priority"],
                            t["completed"],
                        ]
                    )
            messagebox.showinfo(
                self._t("Muvaffaqiyat", "Успех", "Муваффақият"),
                self._t(
                    "Vazifalar CSV ga eksport qilindi!",
                    "Задачи экспортированы в CSV!",
                    "Вазифаҳо ба CSV экспорт карда шуданд!",
                ),
            )
        except Exception as e:
            messagebox.showerror(tr("error", self.lang), str(e))

    # ================= ILOVA HAQIDA =================
    def _section_about(self, parent):
        card = RoundedCard(parent, title="ℹ️ Ilova haqida", header_bg=COLORS["sand"])
        card.pack(fill="x", padx=10, pady=8)

        inner = tk.Frame(card.inner, bg=COLORS["cream"])
        inner.pack(fill="x", padx=14, pady=10)

        # Gradient banner
        banner = tk.Canvas(inner, height=80, highlightthickness=0, bg=COLORS["cream"])
        banner.pack(fill="x", pady=(0, 10))
        banner.bind("<Configure>", lambda e: self._draw_about_banner(banner))
        self._draw_about_banner(banner)

        info_lines = [
            ("Nom:", "Cozy Cabinet v2.0"),
            ("Muallif:", "Hasanov Halimjon"),
            ("Til:", "Python 3.12 + Tkinter + SQLite"),
            ("Litsenziya:", "MIT License (Erkin foydalanish)"),
            ("Sana:", date.today().strftime("%d.%m.%Y")),
        ]
        for label, value in info_lines:
            row = tk.Frame(inner, bg=COLORS["cream"])
            row.pack(fill="x", pady=2)
            tk.Label(
                row,
                text=label,
                font=("Segoe UI", 10, "bold"),
                bg=COLORS["cream"],
                fg=COLORS["coffee"],
                width=12,
                anchor="w",
            ).pack(side="left")
            tk.Label(
                row,
                text=value,
                font=("Segoe UI", 10),
                bg=COLORS["cream"],
                fg=COLORS["coffee_dark"],
            ).pack(side="left")

    def _draw_about_banner(self, banner):
        w, h = banner.winfo_width(), banner.winfo_height()
        if w < 20:
            return
        banner.delete("all")
        # Gradient
        c1, c2 = (139, 69, 19), (212, 160, 23)
        for i in range(20):
            r = i / 20
            cr = int(c1[0] + (c2[0] - c1[0]) * r)
            cg = int(c1[1] + (c2[1] - c1[1]) * r)
            cb = int(c1[2] + (c2[2] - c1[2]) * r)
            x1 = int(w * i / 20)
            x2 = int(w * (i + 1) / 20)
            banner.create_rectangle(
                x1, 0, x2, h, fill=f"#{cr:02x}{cg:02x}{cb:02x}", outline=""
            )
        round_rect(
            banner,
            2,
            2,
            w - 3,
            h - 3,
            radius=16,
            fill="",
            outline=COLORS["cream"],
            width=2,
        )
        banner.create_text(
            w / 2,
            h / 2 - 8,
            text="☕ Cozy Cabinet",
            font=("Segoe UI", 18, "bold"),
            fill=COLORS["cream"],
        )
        banner.create_text(
            w / 2,
            h / 2 + 14,
            text="Student → Businessman Edition",
            font=("Segoe UI", 10),
            fill=COLORS["sand"],
        )

    # ================= XAVFLI HUDUD =================
    def _section_danger(self, parent):
        card = RoundedCard(parent, title="⚠️ Xavfli Hudud", header_bg=COLORS["error"])
        card.pack(fill="x", padx=10, pady=8)

        inner = tk.Frame(card.inner, bg="#ffebee")
        inner.pack(fill="x", padx=14, pady=10)

        tk.Label(
            inner,
            text=self._t(
                "Bu amallar qaytarib bo'lmaydi!",
                "Эти действия необратимы!",
                "Ин амалҳо баргардонидананда нестанд!",
            ),
            font=("Segoe UI", 11, "bold"),
            bg="#ffebee",
            fg=COLORS["error"],
        ).pack(anchor="w", pady=(0, 8))

        btn_row = tk.Frame(inner, bg="#ffebee")
        btn_row.pack(fill="x")

        def open_wipe_dialog():
            d = tk.Toplevel(self.parent)
            d.title("🗑 Ma'lumotlarni o'chirish")
            d.configure(bg=COLORS["cream"])
            d.transient(self.parent)
            d.resizable(False, False)
            d.grab_set()

            tk.Label(
                d,
                text="⚠️ DIQQAT!",
                font=("Segoe UI", 16, "bold"),
                bg=COLORS["cream"],
                fg=COLORS["error"],
            ).pack(pady=(16, 4))
            tk.Label(
                d,
                text=self._t(
                    "Barcha ma'lumotlar (fanlar, do'stlar, vazifalar, byudjet, jurnal) abadiy o'chiriladi.\n\nTasdiqlash uchun pastdagi maydonga:\n'BARCHASINI O'CHIR'\ndeb yozing.",
                    "Все данные (предметы, друзья, задачи, бюджет, дневник) будут удалены навсегда.\n\nДля подтверждения введите ниже:\n'УДАЛИТЬ ВСЁ'",
                    "Ҳамаи маълумот (фаннҳо, дӯстон, вазифаҳо, буҷет, рӯзнома) абадан нест карда мешаванд.\n\nБарои тасдиқ дар майдони зерин нависед:\n'НЕСТ КУНИД ҲАМА'",
                ),
                font=("Segoe UI", 10),
                bg=COLORS["cream"],
                fg=COLORS["coffee_dark"],
                wraplength=350,
                justify="center",
            ).pack(pady=8, padx=20)

            e = ModernEntry(d, outer_bg=COLORS["cream"], placeholder="...")
            e.pack(fill="x", padx=24, pady=8)

            correct_word_uz = "BARCHASINI O'CHIR"
            correct_word_ru = "УДАЛИТЬ ВСЁ"
            correct_word_tj = "НЕСТ КУНИД ҲАМА"

            def confirm():
                typed = e.get().strip().upper()
                if (
                    typed == correct_word_uz.upper()
                    or typed == correct_word_ru.upper()
                    or typed == correct_word_tj.upper()
                ):
                    # Haqiqatan ham o'chirish
                    try:
                        tables = [
                            "subjects",
                            "friends",
                            "tasks",
                            "goals",
                            "expenses",
                            "income",
                            "journal",
                            "pomodoro_sessions",
                            "grades",
                            "attendance",
                            "lectures",
                        ]
                        for table in tables:
                            try:
                                self.db.cursor.execute(f"DELETE FROM {table}")
                            except:
                                pass
                        self.db.conn.commit()
                        d.destroy()
                        messagebox.showinfo(
                            self._t("Tamom", "Готово", "Анҷом ёфт"),
                            self._t(
                                "Barcha ma'lumotlar o'chirildi.\nIlovaga qayta kiring.",
                                "Все данные удалены.\nВойдите заново.",
                                "Ҳамаи маълумот нест карда шуд.\\\nБа барнома дубора ворид шавед.",
                            ),
                        )
                        if self.on_back:
                            self.on_back()
                    except Exception as ex:
                        messagebox.showerror(tr("error", self.lang), str(ex))
                else:
                    messagebox.showerror(
                        self._t("Noto'g'ri", "Неверно", "Нодуруст"),
                        self._t(
                            "So'z noto'g'ri yozildi!",
                            "Слово написано неверно!",
                            "Калима нодуруст навишта шуд!",
                        ),
                    )

            ModernButton(
                d,
                outer_bg=COLORS["cream"],
                text=self._t("TASDIQLASH", "ПОДТВЕРДИТЬ", "ТАСДИҚ"),
                command=confirm,
            ).pack(pady=12)
            d.update_idletasks()
            d.geometry(f"400x{max(d.winfo_reqheight(), 300)}")

        self._danger_btn(
            btn_row, "🗑 Barcha ma'lumotlarni o'chirish", open_wipe_dialog
        ).pack(side="left", padx=4)

        def wipe_all():
            if not messagebox.askyesno(
                self._t(
                    "Jiddiy ogohlantirish", "Серьёзное предупреждение", "Огоҳии ҷиддӣ"
                ),
                self._t(
                    "BARCHA ma'lumotlar o'chiriladi!\n\nDavom etasizmi?",
                    "ВСЕ ДАННЫЕ БУДУТ УДАЛЕНЫ!\n\nПродолжить?",
                    "ҲАМАИ МАЪЛУМОТ НЕСТ МЕШАВАД!\n\nИдома медиҳед?",
                ),
            ):
                return
            if not messagebox.askyesno(
                self._t("Oxirgi tasdiq", "Последнее подтверждение", "Тасдиқи ниҳоӣ"),
                self._t(
                    "Haqiqatan ham barcha ma'lumotlarni o'chirmoqchimisiz?\nBu amalni bekor qilib bo'lmaydi!",
                    "Вы действительно хотите удалить ВСЕ данные?\nЭто действие необратимо!",
                    "Шумо воқеан мехоҳед ҲАМАИ маълумотро нест кунед?\nИн амал бебозгашт аст!",
                ),
            ):
                return
            try:
                tables = [
                    "subjects",
                    "friends",
                    "tasks",
                    "goals",
                    "expenses",
                    "income",
                    "journal",
                    "pomodoro_sessions",
                    "grades",
                    "attendance",
                    "lectures",
                ]
                for table in tables:
                    try:
                        self.db.cursor.execute(f"DELETE FROM {table}")
                    except:
                        pass
                self.db.conn.commit()
                messagebox.showinfo(
                    self._t("Tamom", "Готово", "Анҷом ёфт"),
                    self._t(
                        "Barcha ma'lumotlar o'chirildi.",
                        "Все данные удалены.",
                        "Ҳамаи маълумот нест карда шуд.",
                    ),
                )
                if self.on_back:
                    self.on_back()
            except Exception as e:
                messagebox.showerror(tr("error", self.lang), str(e))

        self._danger_btn(btn_row, "🗑 Barcha ma'lumotlarni o'chirish", wipe_all).pack(
            side="left", padx=4
        )

    def _danger_btn(self, parent, text, cmd):
        b = tk.Canvas(
            parent, height=40, highlightthickness=0, bg="#ffebee", cursor="hand2"
        )
        b._text = text
        b.bind("<Configure>", lambda e, bb=b: self._paint_danger(bb, False))
        b.bind("<Enter>", lambda e, bb=b: self._paint_danger(bb, True))
        b.bind("<Leave>", lambda e, bb=b: self._paint_danger(bb, False))
        b.bind("<Button-1>", lambda e: cmd())
        self._paint_danger(b, False)
        return b

    def _paint_danger(self, b, hover):
        w, h = b.winfo_width(), b.winfo_height()
        if w < 10:
            w = 200
        b.delete("all")
        fill = COLORS["error"] if hover else "#ffcdd2"
        fg = COLORS["cream"] if hover else COLORS["error"]
        round_rect(
            b,
            0,
            0,
            w - 1,
            h - 1,
            radius=h / 2,
            fill=fill,
            outline=COLORS["error"] if not hover else "",
        )
        b.create_text(
            w / 2, h / 2, text=b._text, fill=fg, font=("Segoe UI", 10, "bold")
        )

    # ================= YORDAMCHILAR =================
    # (_pill_btn / _paint_pill / _lighten endi ui_widgets.py da umumiy)
    def _t(self, uz, ru, tj):
        return {"uz": uz, "ru": ru, "tj": tj}.get(self.lang, uz)

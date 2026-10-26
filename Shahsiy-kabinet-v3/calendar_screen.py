import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
from translations import tr
from ui_widgets import (
    ModernEntry,
    ModernButton,
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
}


class CalendarScreen:
    def __init__(self, parent, db, lang):
        self.parent = parent
        self.db = db
        self.lang = lang
        self.current_week_start = self._week_start(date.today())
        self.selected_date = date.today()
        self.day_cards = []
        self.build_ui()

    def _week_start(self, d):
        return d - timedelta(days=d.weekday())

    # ================= UI =================
    def build_ui(self):
        for w in self.parent.winfo_children():
            w.destroy()

        header = tk.Frame(self.parent, bg=COLORS["milk"])
        header.pack(fill="x", padx=20, pady=(18, 10))

        tk.Label(
            header,
            text=f"📅 {tr('calendar', self.lang)}",
            font=("Segoe UI", 20, "bold"),
            bg=COLORS["milk"],
            fg=COLORS["coffee_dark"],
        ).pack(side="left")

        add_btn = make_pill_button(
            header,
            "+ " + tr("add", self.lang),
            COLORS["success"],
            self.add_task_dialog,
            outer_bg=COLORS["milk"],
        )
        add_btn.pack(side="right", padx=(8, 0))

        nav = tk.Frame(header, bg=COLORS["milk"])
        nav.pack(side="right", padx=10)
        self._nav_btn(nav, "◀", self.prev_week).pack(side="left")
        self.week_label = tk.Label(
            nav,
            text="",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["milk"],
            fg=COLORS["coffee_dark"],
            padx=14,
        )
        self.week_label.pack(side="left")
        self._update_week_label()
        self._nav_btn(nav, "▶", self.next_week).pack(side="left")

        strip = tk.Frame(self.parent, bg=COLORS["milk"])
        strip.pack(fill="x", padx=20, pady=(4, 12))
        self.day_cards = []
        for i in range(7):
            d = self.current_week_start + timedelta(days=i)
            card = self._day_card(strip, d, i)
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            strip.grid_columnconfigure(i, weight=1)

        self.tasks_holder = tk.Frame(self.parent, bg=COLORS["milk"])
        self.tasks_holder.pack(fill="both", expand=True, padx=20, pady=(0, 18))
        self._fill_tasks()

    # ================= HEADER TUGMALARI =================
    def _nav_btn(self, parent, text, cmd):
        b = tk.Canvas(
            parent,
            width=38,
            height=38,
            highlightthickness=0,
            bg=COLORS["milk"],
            cursor="hand2",
        )
        b.bind("<Configure>", lambda e, bb=b, t=text: self._paint_nav(bb, t, False))
        b.bind("<Enter>", lambda e, bb=b, t=text: self._paint_nav(bb, t, True))
        b.bind("<Leave>", lambda e, bb=b, t=text: self._paint_nav(bb, t, False))
        b.bind("<Button-1>", lambda e: cmd())
        self._paint_nav(b, text, False)
        return b

    def _paint_nav(self, b, text, hover):
        w, h = b.winfo_width(), b.winfo_height()
        if w < 10:
            w = 38
        b.delete("all")
        fill = COLORS["caramel"] if hover else COLORS["cream"]
        outline = "" if hover else COLORS["caramel"]
        round_rect(
            b, 1, 1, w - 2, h - 2, radius=19, fill=fill, outline=outline, width=1
        )
        fg = COLORS["cream"] if hover else COLORS["coffee_dark"]
        b.create_text(w / 2, h / 2, text=text, fill=fg, font=("Segoe UI", 13, "bold"))

    # ================= KUN KARTOCHKALARI =================
    def _day_card(self, parent, day, index):
        c = tk.Canvas(
            parent, height=108, highlightthickness=0, bg=COLORS["milk"], cursor="hand2"
        )
        c._day, c._index = day, index
        c.bind("<Configure>", lambda e, cc=c: self._paint_day(cc))
        c.bind("<Enter>", lambda e, cc=c: self._paint_day(cc, hover=True))
        c.bind("<Leave>", lambda e, cc=c: self._paint_day(cc))
        c.bind("<Button-1>", lambda e, cc=c: self.select_date(cc._day))
        self.day_cards.append(c)
        return c

    def _paint_day(self, c, hover=False):
        w, h = c.winfo_width(), c.winfo_height()
        if w < 20:
            return
        day = c._day
        is_today = day == date.today()
        is_sel = day == self.selected_date
        c.delete("all")

        if is_sel or hover:
            round_rect(c, 3, 5, w - 1, h - 1, radius=16, fill="#cdb496", outline="")

        if is_sel:
            fill, outline, ow = COLORS["caramel"], COLORS["gold"], 2
        elif is_today:
            fill, outline, ow = COLORS["cream"], COLORS["gold"], 2
        else:
            fill, outline, ow = COLORS["cream"], COLORS["sand"], 1
        round_rect(
            c,
            0,
            0,
            w - 4 if (is_sel or hover) else w - 1,
            h - 6 if (is_sel or hover) else h - 1,
            radius=16,
            fill=fill,
            outline=outline,
            width=ow,
        )

        names = {
            "uz": ["DU", "SE", "CHO", "PA", "JU", "SHA", "YA"],
            "ru": ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"],
            "tj": ["ДШ", "СС", "ЧШ", "ПШ", "ҶМ", "ШБ", "ЯШ"],
        }
        name_fg = COLORS["cream"] if is_sel else COLORS["coffee"]
        c.create_text(
            w / 2 - 2,
            22,
            text=names[self.lang][c._index],
            font=("Segoe UI", 9, "bold"),
            fill=name_fg,
        )

        date_fg = COLORS["cream"] if is_sel else COLORS["coffee_dark"]
        c.create_text(
            w / 2 - 2,
            50,
            text=str(day.day),
            font=("Segoe UI", 22, "bold"),
            fill=date_fg,
        )

        # BUGUN chipi (tanlangan bo'lsa ham oltin nuqta bilan)
        if is_today:
            if is_sel:
                c.create_oval(
                    w / 2 - 6, 68, w / 2 + 2, 76, fill=COLORS["gold"], outline=""
                )
            else:
                round_rect(
                    c,
                    w / 2 - 22,
                    66,
                    w / 2 + 18,
                    82,
                    radius=8,
                    fill=COLORS["gold"],
                    outline="",
                )
                c.create_text(
                    w / 2 - 2,
                    74,
                    text="BUGUN",
                    font=("Segoe UI", 7, "bold"),
                    fill=COLORS["coffee_dark"],
                )

        count = self._day_task_count(day)
        if count > 0:
            chip_y = 90 if (is_today and not is_sel) else 74
            cx = w / 2 - 2
            round_rect(
                c,
                cx - 14,
                chip_y - 8,
                cx + 14,
                chip_y + 8,
                radius=8,
                fill=COLORS["success"] if is_sel else COLORS["sand"],
                outline="",
            )
            c.create_text(
                cx,
                chip_y,
                text=str(count),
                font=("Segoe UI", 8, "bold"),
                fill=COLORS["cream"] if is_sel else COLORS["coffee_dark"],
            )

    def _day_task_count(self, day):
        ds = day.isoformat()
        return len([t for t in self.db.get_tasks() if t["due_date"] == ds])

    # ================= NAVIGATSIYA (SINXRONLANGAN) =================
    def _sync_selected_to_week(self):
        """Tanlangan sannni joriy hafta oralig'iga moslashtirish"""
        ws = self.current_week_start
        we = ws + timedelta(days=6)
        if not (ws <= self.selected_date <= we):
            today = date.today()
            self.selected_date = today if (ws <= today <= we) else ws

    def _update_week_label(self):
        we = self.current_week_start + timedelta(days=6)
        self.week_label.config(
            text=f"{self.current_week_start.strftime('%d.%m')} - {we.strftime('%d.%m.%Y')}"
        )

    def prev_week(self):
        self.current_week_start -= timedelta(days=7)
        self._sync_selected_to_week()
        self._update_week_label()
        self._repaint_days()
        self._fill_tasks()  # ← ENDI PAST HAM O'ZGARADI

    def next_week(self):
        self.current_week_start += timedelta(days=7)
        self._sync_selected_to_week()
        self._update_week_label()
        self._repaint_days()
        self._fill_tasks()  # ← ENDI PAST HAM O'ZGARADI

    def select_date(self, day):
        self.selected_date = day
        self._repaint_days()
        self._fill_tasks()

    def _repaint_days(self):
        for i, c in enumerate(self.day_cards):
            if c.winfo_exists():
                # Joriy haftaga moslab sanani yangilaymiz!
                c._day = self.current_week_start + timedelta(days=i)
                self._paint_day(c)

    # ================= VAZIFALAR PANELI =================
    def _fill_tasks(self):
        for w in self.tasks_holder.winfo_children():
            w.destroy()
        ds = self.selected_date.isoformat()
        tasks = [t for t in self.db.get_tasks() if t["due_date"] == ds]
        tasks.sort(key=lambda x: x["due_time"] or "99:99")

        card = RoundedCard(
            self.tasks_holder,
            title=f"📋 {self.selected_date.strftime('%d.%m.%Y')} — {tr('today_tasks', self.lang)}",
            header_bg=COLORS["coffee"],
        )
        card.pack(fill="both", expand=True)

        if not tasks:
            empty = tk.Frame(card.inner, bg=COLORS["cream"])
            empty.pack(expand=True, pady=40)
            tk.Label(empty, text="🌤️", font=("Segoe UI", 40), bg=COLORS["cream"]).pack()
            tk.Label(
                empty,
                text=tr("no_tasks", self.lang),
                font=("Segoe UI", 13, "bold"),
                bg=COLORS["cream"],
                fg=COLORS["coffee"],
            ).pack(pady=(8, 2))
            tk.Label(
                empty,
                text="+ Qo'shish tugmasini bosing",
                font=("Segoe UI", 10),
                bg=COLORS["cream"],
                fg=COLORS["sand"],
            ).pack()
            return

        for t in tasks:
            self._task_row(card.inner, t)

    def _task_row(self, inner, task):
        is_done = task["completed"] == 1
        row = tk.Frame(inner, bg=COLORS["milk"], padx=12, pady=8)
        row.pack(fill="x", pady=4, padx=12)

        # --- 1-qator: checkbox, vaqt, sarlavha, chip'lar, o'chirish ---
        line1 = tk.Frame(row, bg=COLORS["milk"])
        line1.pack(fill="x")

        chk = tk.Button(
            line1,
            text="✓" if is_done else "○",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["success"] if is_done else COLORS["cream"],
            fg=COLORS["cream"] if is_done else COLORS["sand"],
            relief="flat",
            cursor="hand2",
            width=2,
            command=lambda t=task: self.toggle_task(t),
        )
        chk.pack(side="left", padx=(0, 12))

        if task["due_time"]:
            tk.Label(
                line1,
                text=f"⏰ {task['due_time']}",
                font=("Segoe UI", 10, "bold"),
                bg=COLORS["sand"],
                fg=COLORS["coffee_dark"],
                padx=8,
                pady=3,
            ).pack(side="left", padx=(0, 12))

        title_lbl = tk.Label(
            line1,
            text=task["title"],
            font=("Segoe UI", 12, "bold" if not is_done else "normal"),
            bg=COLORS["milk"],
            fg=COLORS["coffee_dark"] if not is_done else COLORS["coffee"],
            anchor="w",
        )
        title_lbl.pack(side="left", fill="x", expand=True)

        cat_colors = {
            "dars": COLORS["caramel"],
            "shaxsiy": COLORS["gold"],
            "do'st": COLORS["success"],
        }
        tk.Label(
            line1,
            text=f"#{task['category']}",
            font=("Segoe UI", 9, "bold"),
            bg=cat_colors.get(task["category"], COLORS["sand"]),
            fg=COLORS["cream"],
            padx=9,
            pady=3,
        ).pack(side="left", padx=(8, 4))

        # Prioritet — alohida rangli chip
        prio_map = {
            1: ("PAST", COLORS["sand"], COLORS["coffee_dark"]),
            2: ("O'RTA", COLORS["gold"], COLORS["coffee_dark"]),
            3: ("YUQORI", COLORS["error"], COLORS["cream"]),
        }
        ptxt, pbg, pfg = prio_map.get(
            task["priority"], ("", COLORS["milk"], COLORS["coffee"])
        )
        if ptxt:
            tk.Label(
                line1,
                text=ptxt,
                font=("Segoe UI", 8, "bold"),
                bg=pbg,
                fg=pfg,
                padx=8,
                pady=3,
            ).pack(side="left", padx=(0, 4))

        tk.Button(
            line1,
            text="🗑",
            font=("Segoe UI", 10),
            bg=COLORS["milk"],
            fg=COLORS["error"],
            relief="flat",
            cursor="hand2",
            command=lambda t=task: self.delete_task(t),
        ).pack(side="right")

        # --- 2-qator: tavsif (alohida, o'ngga surilmaydi) ---
        if task["description"]:
            desc_lbl = tk.Label(
                row,
                text=f"📝 {task['description']}",
                font=("Segoe UI", 10),
                bg=COLORS["milk"],
                fg=COLORS["coffee"],
                anchor="w",
                wraplength=700,
                justify="left",
            )
            desc_lbl.pack(fill="x", padx=38, pady=(4, 0))
        else:
            desc_lbl = None

        def _enter(e):
            row.config(bg=COLORS["cream"])
            title_lbl.config(bg=COLORS["cream"])
            if desc_lbl:
                desc_lbl.config(bg=COLORS["cream"])

        def _leave(e):
            row.config(bg=COLORS["milk"])
            title_lbl.config(bg=COLORS["milk"])
            if desc_lbl:
                desc_lbl.config(bg=COLORS["milk"])

        for wgt in (row, chk, title_lbl):
            wgt.bind("<Enter>", _enter)
            wgt.bind("<Leave>", _leave)
        if desc_lbl:
            desc_lbl.bind("<Enter>", _enter)
            desc_lbl.bind("<Leave>", _leave)

    def toggle_task(self, task):
        if task["completed"] == 1:
            self.db.uncomplete_task(task["id"])
        else:
            self.db.complete_task(task["id"])
            self.db.add_points(10, f"Vazifa bajarildi: {task['title']}")
        self._repaint_days()
        self._fill_tasks()

    def delete_task(self, task):
        if messagebox.askyesno(tr("confirm", self.lang), tr("confirm", self.lang)):
            self.db.delete_task(task["id"])
            self._repaint_days()
            self._fill_tasks()

    # ================= CHIP-TANASH (combobox/radio o'rniga) =================
    def _chip_group(self, parent, options, default):
        """options: [(value, label, active_color), ...]"""
        holder = tk.Frame(parent, bg=COLORS["cream"])
        var = tk.StringVar(value=default)
        labels = {}
        for val, lab, col in options:
            l = tk.Label(
                holder,
                text=lab,
                font=("Segoe UI", 10, "bold"),
                bg=col if val == default else COLORS["milk"],
                fg=COLORS["cream"] if val == default else COLORS["coffee"],
                padx=12,
                pady=6,
                cursor="hand2",
                relief="flat",
            )
            l._val, l._col = val, col
            labels[val] = l
            l.bind("<Button-1>", lambda e, vv=val: self._chip_pick(var, labels, vv))
            l.pack(side="left", padx=4, pady=2)
        return holder, var

    def _chip_pick(self, var, labels, val):
        var.set(val)
        for k, l in labels.items():
            if k == val:
                l.config(bg=l._col, fg=COLORS["cream"])
            else:
                l.config(bg=COLORS["milk"], fg=COLORS["coffee"])

    # ================= QO'SHISH DIALOGI (IXCHAM, QOTITILGAN) =================
    def add_task_dialog(self):
        dialog = tk.Toplevel(self.parent)
        dialog.title("+ " + tr("add", self.lang))
        dialog.configure(bg=COLORS["cream"])
        dialog.transient(self.parent)
        dialog.resizable(False, False)  # ← HAJM O'ZGARMAYDI
        dialog.grab_set()

        tk.Label(
            dialog,
            text="📝 " + tr("add", self.lang),
            font=("Segoe UI", 17, "bold"),
            bg=COLORS["cream"],
            fg=COLORS["coffee_dark"],
        ).pack(pady=(18, 10))

        f = tk.Frame(dialog, bg=COLORS["cream"])
        f.pack(fill="x", padx=28)

        def lbl(txt):
            tk.Label(
                f,
                text=txt,
                font=("Segoe UI", 10, "bold"),
                bg=COLORS["cream"],
                fg=COLORS["coffee"],
            ).pack(anchor="w", pady=(7, 2))

        lbl(tr("task_title", self.lang))
        title_e = ModernEntry(
            f, outer_bg=COLORS["cream"], placeholder="Masalan: Matematika uy vazifasi"
        )
        title_e.pack(fill="x")
        title_e.focus()

        lbl(tr("task_desc", self.lang))
        desc_t = tk.Text(
            f,
            font=("Segoe UI", 10),
            height=2,
            bg=COLORS["milk"],
            fg=COLORS["coffee_dark"],
            relief="flat",
            highlightbackground=COLORS["sand"],
            highlightthickness=1,
        )
        desc_t.pack(fill="x")

        lbl(tr("task_date", self.lang) + " (YYYY-MM-DD)")
        date_e = ModernEntry(
            f, outer_bg=COLORS["cream"], placeholder=self.selected_date.isoformat()
        )
        date_e.pack(fill="x")
        date_e.insert(0, self.selected_date.isoformat())

        lbl(tr("task_time", self.lang) + " (HH:MM)")
        time_e = ModernEntry(f, outer_bg=COLORS["cream"], placeholder="18:00")
        time_e.pack(fill="x")

        lbl(tr("task_category", self.lang))
        cat_opts = [
            ("dars", "📚 Dars", COLORS["caramel"]),
            ("shaxsiy", "👤 Shaxsiy", COLORS["gold"]),
            ("do'st", "🤝 Do'st", COLORS["success"]),
        ]
        cat_holder, cat_var = self._chip_group(f, cat_opts, "shaxsiy")
        cat_holder.pack(fill="x", pady=(2, 4))

        lbl(tr("task_priority", self.lang))
        prio_opts = [
            (1, "⬇ Past", COLORS["sand"]),
            (2, "⬆ O'rtacha", COLORS["gold"]),
            (3, "🔥 Yuqori", COLORS["error"]),
        ]
        prio_holder, prio_var = self._chip_group(f, prio_opts, 1)
        prio_holder.pack(fill="x", pady=(2, 4))

        def save():
            t = title_e.get().strip()
            if not t:
                messagebox.showerror(
                    tr("error", self.lang), "Sarlavha kiriting!", parent=dialog
                )
                return
            dd = date_e.get().strip() or self.selected_date.isoformat()
            if not self._valid_date(dd):
                messagebox.showerror(
                    tr("error", self.lang),
                    "Sana YYYY-MM-DD formatida bo'lsin!",
                    parent=dialog,
                )
                return
            self.db.add_task(
                t,
                desc_t.get("1.0", "end").strip(),
                dd,
                time_e.get().strip(),
                cat_var.get(),
                prio_var.get(),
            )
            dialog.destroy()
            self.selected_date = date.fromisoformat(dd)
            self.current_week_start = self._week_start(self.selected_date)
            self._update_week_label()
            self._repaint_days()
            self._fill_tasks()

        ModernButton(
            dialog, outer_bg=COLORS["cream"], text=tr("save", self.lang), command=save
        ).pack(pady=16)

        # --- AVTOMATIK BALANDLIK: ochilganda hammasi ko'rinadi ---
        dialog.update_idletasks()
        req_h = dialog.winfo_reqheight()
        dialog.geometry(f"440x{max(req_h, 520)}")
        # Markazga joylashtirish
        x = dialog.winfo_rootx() - (440 - dialog.winfo_width()) // 2
        y = max(40, dialog.winfo_rooty() - 40)
        dialog.geometry(f"440x{max(req_h, 520)}+{x}+{y}")

    def _valid_date(self, s):
        try:
            date.fromisoformat(s)
            return True
        except Exception:
            return False

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
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


class GoalsScreen:
    def __init__(self, parent, db, lang):
        self.parent = parent
        self.db = db
        self.lang = lang
        self.build_ui()

    # ================= RANG MANTIĞI =================
    def _pct_color(self, pct):
        if pct >= 80:
            return COLORS["success"]
        if pct >= 40:
            return COLORS["gold"]
        return COLORS["error"]

    # ================= UI =================
    def build_ui(self):
        for w in self.parent.winfo_children():
            w.destroy()

        header = tk.Frame(self.parent, bg=COLORS["milk"])
        header.pack(fill="x", padx=20, pady=(18, 10))
        tk.Label(
            header,
            text=f"🎯 {tr('goals', self.lang)}",
            font=("Segoe UI", 20, "bold"),
            bg=COLORS["milk"],
            fg=COLORS["coffee_dark"],
        ).pack(side="left")
        make_pill_button(
            header,
            "+ " + tr("add", self.lang),
            COLORS["success"],
            lambda: self._goal_dialog(),
            outer_bg=COLORS["milk"],
        ).pack(side="right")

        # --- Statistika ---
        all_goals = self.db.get_goals()
        active = len([g for g in all_goals if g["completed"] == 0])
        done = len([g for g in all_goals if g["completed"] == 1])
        avg_pct = (
            round(sum(g["progress"] for g in all_goals) / len(all_goals))
            if all_goals
            else 0
        )

        stats_row = tk.Frame(self.parent, bg=COLORS["milk"])
        stats_row.pack(fill="x", padx=20, pady=(0, 12))
        for i, (icon, val, lab, col) in enumerate(
            [
                ("🎯", active, "Faol", COLORS["caramel"]),
                ("✅", done, "Bajarilgan", COLORS["success"]),
                ("📈", avg_pct, "O'rtacha %", COLORS["gold"]),
            ]
        ):
            self._stat_tile(stats_row, icon, val, lab, col).grid(
                row=0, column=i, padx=6, sticky="nsew"
            )
            stats_row.grid_columnconfigure(i, weight=1)

        # --- Grid konteyner ---
        container = tk.Frame(self.parent, bg=COLORS["milk"])
        container.pack(fill="both", expand=True, padx=20, pady=(0, 18))
        canvas = tk.Canvas(container, bg=COLORS["milk"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.grid_frame = tk.Frame(canvas, bg=COLORS["milk"])
        self.grid_win = canvas.create_window(
            (0, 0), window=self.grid_frame, anchor="nw"
        )

        def _conf(e):
            canvas.itemconfig(self.grid_win, width=e.width)
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<Configure>", _conf)
        self.grid_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _wheel(e):
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _wheel)
        self.grid_frame.bind("<MouseWheel>", _wheel)

        self._refresh()

    # ================= TUGMA YORDAMCHILARI =================
    def _icon_btn(self, parent, symbol, color, cmd, bg=COLORS["cream"], size=30):
        b = tk.Canvas(
            parent, width=size, height=size, highlightthickness=0, bg=bg, cursor="hand2"
        )

        def paint(hover):
            b.delete("all")
            fill = color if hover else COLORS["milk"]
            round_rect(
                b,
                1,
                1,
                size - 2,
                size - 2,
                radius=size / 2,
                fill=fill,
                outline=color if not hover else "",
            )
            b.create_text(
                size / 2,
                size / 2,
                text=symbol,
                fill=COLORS["cream"] if hover else color,
                font=("Segoe UI", 11, "bold"),
            )

        paint(False)
        b.bind("<Enter>", lambda e: paint(True))
        b.bind("<Leave>", lambda e: paint(False))
        b.bind("<Button-1>", lambda e: cmd())
        return b

    # ================= STAT TILE (count-up) =================
    def _stat_tile(self, parent, icon, value, label, color):
        t = tk.Canvas(
            parent, height=110, highlightthickness=0, bg=COLORS["milk"], cursor="hand2"
        )
        t._icon, t._label, t._color, t._shown = icon, label, color, 0
        t.bind("<Configure>", lambda e, tt=t: self._draw_stat(tt))
        t.bind("<Enter>", lambda e, tt=t: self._draw_stat(tt, True))
        t.bind("<Leave>", lambda e, tt=t: self._draw_stat(tt))
        self._draw_stat(t)
        self._count_up(t, value)
        return t

    def _draw_stat(self, t, hover=False):
        w, h = t.winfo_width(), t.winfo_height()
        if w < 20:
            return
        t.delete("all")
        if hover:
            round_rect(t, 3, 5, w - 1, h - 1, radius=18, fill="#d9c3a5", outline="")
            round_rect(
                t,
                0,
                0,
                w - 4,
                h - 6,
                radius=18,
                fill=COLORS["cream"],
                outline=t._color,
                width=2,
            )
        else:
            round_rect(
                t,
                0,
                0,
                w - 1,
                h - 1,
                radius=18,
                fill=COLORS["cream"],
                outline=COLORS["sand"],
                width=1,
            )
        off = -2 if hover else 0
        t.create_text(w / 2 - 1, 28 + off, text=t._icon, font=("Segoe UI", 22))
        t.create_text(
            w / 2 - 1,
            62 + off,
            text=str(t._shown),
            font=("Segoe UI", 22, "bold"),
            fill=t._color,
        )
        t.create_text(
            w / 2 - 1,
            92 + off,
            text=t._label,
            font=("Segoe UI", 10),
            fill=COLORS["coffee"],
        )

    def _count_up(self, t, target):
        steps = 16

        def tick(i):
            if not t.winfo_exists():
                return
            t._shown = int(target * i / steps)
            try:
                self._draw_stat(t)
            except tk.TclError:
                return
            if i < steps:
                t.after(40, lambda: tick(i + 1))

        tick(0)

    # ================= YANGILASH =================
    def _refresh(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        goals = self.db.get_goals()
        if not goals:
            empty = tk.Frame(self.grid_frame, bg=COLORS["milk"])
            empty.pack(expand=True, pady=60)
            tk.Label(empty, text="🎯", font=("Segoe UI", 50), bg=COLORS["milk"]).pack()
            tk.Label(
                empty,
                text="Hozircha maqsadlar yo'q",
                font=("Segoe UI", 14, "bold"),
                bg=COLORS["milk"],
                fg=COLORS["coffee"],
            ).pack(pady=(10, 2))
            tk.Label(
                empty,
                text="+ Qo'shish tugmasini bosing",
                font=("Segoe UI", 10),
                bg=COLORS["milk"],
                fg=COLORS["sand"],
            ).pack()
            return
        for i, g in enumerate(goals):
            r, c = divmod(i, 2)
            self._goal_card(g).grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
            self.grid_frame.grid_columnconfigure(0, weight=1)
            self.grid_frame.grid_columnconfigure(1, weight=1)

    # ================= MAQSAD KARTASI =================
    def _goal_card(self, g):
        pct = g["progress"]
        is_done = g["completed"] == 1
        col = COLORS["success"] if is_done else self._pct_color(pct)

        card = RoundedCard(self.grid_frame, header_bg=None)

        # --- Yuqori qator: ring + sarlavha + tugmalar ---
        top = tk.Frame(card.inner, bg=COLORS["cream"])
        top.pack(fill="x", padx=12, pady=(12, 6))

        ring = self._progress_ring(top, pct, col, size=64)
        ring.pack(side="left", padx=(0, 12))

        name_wrap = tk.Frame(top, bg=COLORS["cream"])
        name_wrap.pack(side="left", fill="x", expand=True)
        title = ("✓ " if is_done else "") + g["title"]
        tk.Label(
            name_wrap,
            text=title,
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["cream"],
            fg=COLORS["coffee_dark"],
            anchor="w",
        ).pack(fill="x")
        # Countdown
        cd = self._countdown(g["target_date"])
        if cd:
            tk.Label(
                name_wrap,
                text=cd,
                font=("Segoe UI", 9, "bold"),
                bg=COLORS["milk"] if not is_done else COLORS["success"],
                fg=COLORS["coffee_dark"] if not is_done else COLORS["cream"],
                padx=8,
                pady=2,
                anchor="w",
            ).pack(anchor="w", pady=(3, 0))

        btns = tk.Frame(top, bg=COLORS["cream"])
        btns.pack(side="right")
        self._icon_btn(
            btns, "✎", COLORS["gold"], lambda gg=g: self._goal_dialog(gg)
        ).pack(pady=2)
        self._icon_btn(
            btns, "✕", COLORS["error"], lambda gg=g: self._delete_goal(gg)
        ).pack(pady=2)

        # --- Tavsif ---
        if g["description"]:
            tk.Label(
                card.inner,
                text=g["description"],
                font=("Segoe UI", 10),
                bg=COLORS["cream"],
                fg=COLORS["coffee"],
                anchor="w",
                wraplength=340,
                justify="left",
            ).pack(fill="x", padx=14, pady=(0, 6))

        # --- Click-to-set progress bar ---
        bar_wrap = tk.Frame(card.inner, bg=COLORS["cream"])
        bar_wrap.pack(fill="x", padx=14, pady=(4, 10))
        tk.Label(
            bar_wrap,
            text=f"Progress: {pct}%",
            font=("Segoe UI", 9, "bold"),
            bg=COLORS["cream"],
            fg=COLORS["coffee_dark"],
            anchor="w",
        ).pack(anchor="w")
        self._progress_bar(bar_wrap, g, pct, col).pack(fill="x", pady=(3, 0))
        tk.Label(
            bar_wrap,
            text="💡 Barni bosib foizni o'zgartiring",
            font=("Segoe UI", 8),
            bg=COLORS["cream"],
            fg=COLORS["sand"],
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))
        return card

    # ================= PROGRESS RING =================
    def _progress_ring(self, parent, pct, color, size=64):
        r = tk.Canvas(
            parent, width=size, height=size, highlightthickness=0, bg=COLORS["cream"]
        )
        cx = cy = size / 2
        rad = size / 2 - 5
        r.create_oval(5, 5, size - 5, size - 5, outline=COLORS["milk"], width=6)
        if pct > 0:
            r.create_arc(
                5,
                5,
                size - 5,
                size - 5,
                start=90,
                extent=-360 * pct / 100,
                style="arc",
                outline=color,
                width=6,
            )
        r.create_text(
            cx,
            cy,
            text=f"{pct}%",
            font=("Segoe UI", 11, "bold"),
            fill=COLORS["coffee_dark"],
        )
        return r

    # ================= CLICK-TO-SET BAR =================
    def _progress_bar(self, parent, goal, pct, color):
        h = 18
        b = tk.Canvas(
            parent, height=h, highlightthickness=0, bg=COLORS["cream"], cursor="hand2"
        )
        b._goal, b._pct, b._color = goal, pct, color

        def draw():
            w = b.winfo_width()
            if w < 20:
                return
            b.delete("all")
            round_rect(
                b,
                0,
                0,
                w - 1,
                h - 1,
                radius=h / 2,
                fill=COLORS["milk"],
                outline=COLORS["sand"],
                width=1,
            )
            fw = max(h, (w - 2) * b._pct / 100) if b._pct > 0 else 0
            if fw > 0:
                round_rect(b, 1, 1, fw, h - 2, radius=h / 2, fill=b._color, outline="")

        def on_click(e):
            w = b.winfo_width()
            if w < 20:
                return
            new_pct = max(0, min(100, int((e.x / w) * 100)))
            self._set_progress(goal, new_pct)

        b.bind("<Configure>", lambda e: draw())
        b.bind("<Button-1>", on_click)
        b.bind("<Enter>", lambda e: b.config(cursor="hand2"))
        draw()
        return b

    def _set_progress(self, goal, pct):
        was_done = goal["completed"] == 1
        self.db.update_goal_progress(goal["id"], pct)
        if pct >= 100 and not was_done:
            self.db.add_points(50, f"Maqsad bajarildi: {goal['title']}")
        self._refresh()

    # ================= COUNTDOWN =================
    def _countdown(self, target_date):
        if not target_date:
            return ""
        try:
            td = date.fromisoformat(target_date)
        except Exception:
            return f"📅 {target_date}"
        days = (td - date.today()).days
        if days < 0:
            return f"⏰ {abs(days)} kun kechikkan"
        if days == 0:
            return "🔥 BUGUN muddat!"
        if days == 1:
            return "⏳ ERTAGA 1 kun qoldi"
        return f"⏳ {days} kun qoldi"

    # ================= O'CHIRISH =================
    def _delete_goal(self, g):
        if messagebox.askyesno(
            tr("confirm", self.lang), f"'{g['title']}' maqsadni o'chirasizmi?"
        ):
            self.db.delete_goal(g["id"])
            self._refresh()

    # ================= QO'SHISH / TAHRIRLASH DIALOGI =================
    def _goal_dialog(self, g=None):
        is_edit = g is not None
        dialog = tk.Toplevel(self.parent)
        dialog.title(("✎ " if is_edit else "+ ") + tr("goals", self.lang))
        dialog.configure(bg=COLORS["cream"])
        dialog.transient(self.parent)
        dialog.resizable(False, False)
        dialog.grab_set()
        tk.Label(
            dialog,
            text=("✎ " if is_edit else "🎯 ") + tr("add", self.lang),
            font=("Segoe UI", 17, "bold"),
            bg=COLORS["cream"],
            fg=COLORS["coffee_dark"],
        ).pack(pady=(18, 10))
        f = tk.Frame(dialog, bg=COLORS["cream"])
        f.pack(fill="x", padx=28)

        def lbl(txt, req=False):
            tk.Label(
                f,
                text=txt + (" *" if req else ""),
                font=("Segoe UI", 10, "bold"),
                bg=COLORS["cream"],
                fg=COLORS["coffee"],
            ).pack(anchor="w", pady=(7, 2))

        def field(label, val, req=False):
            lbl(label, req)
            e = ModernEntry(f, outer_bg=COLORS["cream"], placeholder=label)
            e.pack(fill="x")
            if val:
                e.insert(0, val)
            return e

        title_e = field(
            tr("goal_title", self.lang), g["title"] if is_edit else "", True
        )
        lbl(tr("description", self.lang))
        desc_t = tk.Text(
            f,
            font=("Segoe UI", 10),
            height=3,
            bg=COLORS["milk"],
            fg=COLORS["coffee_dark"],
            relief="flat",
            highlightbackground=COLORS["sand"],
            highlightthickness=1,
        )
        desc_t.pack(fill="x")
        if is_edit and g["description"]:
            desc_t.insert("1.0", g["description"])
        date_e = field(
            tr("target_date", self.lang) + " (YYYY-MM-DD)",
            g["target_date"] if is_edit else "",
        )

        def save():
            title = title_e.get().strip()
            if not title:
                messagebox.showerror(
                    tr("error", self.lang), "Sarlavha kiriting!", parent=dialog
                )
                return
            dd = date_e.get().strip()
            if dd:
                try:
                    date.fromisoformat(dd)
                except Exception:
                    messagebox.showerror(
                        tr("error", self.lang),
                        "Sana YYYY-MM-DD formatida bo'lsin!",
                        parent=dialog,
                    )
                    return
            desc = desc_t.get("1.0", "end").strip()
            if is_edit:
                self.db.update_goal(g["id"], title, desc, dd)
            else:
                self.db.add_goal(title, desc, dd)
            dialog.destroy()
            self._refresh()

        ModernButton(
            dialog, outer_bg=COLORS["cream"], text=tr("save", self.lang), command=save
        ).pack(pady=16)
        dialog.update_idletasks()
        dialog.geometry(f"440x{max(dialog.winfo_reqheight(), 420)}")

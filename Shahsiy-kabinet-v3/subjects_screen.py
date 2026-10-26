import tkinter as tk
from tkinter import ttk, messagebox
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
}


class SubjectsScreen:
    def __init__(self, parent, db, lang):
        self.parent = parent
        self.db = db
        self.lang = lang
        self.build_ui()

    # ================= RANG MANTIĞI =================
    def _grade_color(self, v):
        if v == 0:
            return COLORS["sand"]
        if v >= 80:
            return COLORS["success"]
        if v >= 60:
            return COLORS["gold"]
        return COLORS["error"]

    def _att_color(self, pct):
        if pct == 0:
            return COLORS["sand"]
        if pct >= 85:
            return COLORS["success"]
        if pct >= 70:
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
            text=f"📚 {tr('subjects', self.lang)}",
            font=("Segoe UI", 20, "bold"),
            bg=COLORS["milk"],
            fg=COLORS["coffee_dark"],
        ).pack(side="left")
        make_pill_button(
            header,
            "+ " + tr("add", self.lang),
            COLORS["success"],
            self._add_subject_dialog,
            outer_bg=COLORS["milk"],
        ).pack(side="right")

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
    def _card_btn(self, parent, text, color, cmd):
        b = tk.Canvas(
            parent, height=34, highlightthickness=0, bg=COLORS["cream"], cursor="hand2"
        )
        b._text, b._color = text, color
        b.bind("<Configure>", lambda e, bb=b: self._paint_card_btn(bb, False))
        b.bind("<Enter>", lambda e, bb=b: self._paint_card_btn(bb, True))
        b.bind("<Leave>", lambda e, bb=b: self._paint_card_btn(bb, False))
        b.bind("<Button-1>", lambda e: cmd())
        self._paint_card_btn(b, False)
        return b

    def _paint_card_btn(self, b, hover):
        w, h = b.winfo_width(), b.winfo_height()
        if w < 10:
            w = 90
        b.delete("all")
        fill = lighten_color(b._color) if hover else b._color
        round_rect(b, 0, 0, w - 1, h - 1, radius=h / 2, fill=fill, outline="")
        b.create_text(
            w / 2,
            h / 2,
            text=b._text,
            fill=COLORS["cream"],
            font=("Segoe UI", 9, "bold"),
        )

    # Kichik ikonka tugma (sarlavha uchun: tahrirlash / o'chirish)
    def _icon_btn(self, parent, symbol, color, cmd, size=30):
        b = tk.Canvas(
            parent,
            width=size,
            height=size,
            highlightthickness=0,
            bg=COLORS["coffee"],
            cursor="hand2",
        )
        b._sym, b._col, b._sz = symbol, color, size

        def paint(hover):
            b.delete("all")
            fill = b._col if hover else COLORS["coffee"]
            round_rect(
                b,
                1,
                1,
                b._sz - 2,
                b._sz - 2,
                radius=b._sz / 2,
                fill=fill,
                outline="" if hover else COLORS["caramel"],
                width=1,
            )
            b.create_text(
                b._sz / 2,
                b._sz / 2,
                text=b._sym,
                fill=COLORS["cream"] if hover else b._col,
                font=("Segoe UI", 11, "bold"),
            )

        paint(False)
        b.bind("<Enter>", lambda e: paint(True))
        b.bind("<Leave>", lambda e: paint(False))
        b.bind("<Button-1>", lambda e: cmd())
        return b

    # ================= FANLARNI YANGILASH =================
    def _refresh(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        subjects = self.db.get_subjects()
        if not subjects:
            empty = tk.Frame(self.grid_frame, bg=COLORS["milk"])
            empty.pack(expand=True, pady=60)
            tk.Label(empty, text="📚", font=("Segoe UI", 50), bg=COLORS["milk"]).pack()
            tk.Label(
                empty,
                text="Hozircha fanlar yo'q",
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
        for i, subj in enumerate(subjects):
            r, c = divmod(i, 2)
            self._subject_card(subj).grid(
                row=r, column=c, padx=6, pady=6, sticky="nsew"
            )
            self.grid_frame.grid_columnconfigure(0, weight=1)
            self.grid_frame.grid_columnconfigure(1, weight=1)

    # ================= FAN KARTASI =================
    def _subject_card(self, subj):
        avg = self.db.get_subject_average(subj["id"])
        att = self.db.get_attendance_stats(subj["id"])
        total = att["total"] or 0
        present = att["present"] or 0
        pct = round(present / total * 100) if total else 0
        lectures = self.db.get_lectures(subj["id"])

        if avg == 0:
            ai_chip, ai_col = "📊 Ma'lumot yo'q", COLORS["sand"]
        elif avg >= 85:
            ai_chip, ai_col = "🌟 Kuchli fan", COLORS["success"]
        elif avg < 60:
            ai_chip, ai_col = "⚠️ E'tibor bering", COLORS["error"]
        else:
            ai_chip, ai_col = "👍 O'rtacha", COLORS["gold"]

        # SARLAVHASIZ RoundedCard — sarlavhani o'zim ichkarida chizaman
        card = RoundedCard(self.grid_frame, header_bg=None)

        # --- Sarlavha qatori (rangli, ichkarida) ---
        head = tk.Frame(card.inner, bg=COLORS["coffee"])
        head.pack(fill="x")
        tk.Label(
            head,
            text=f"📖 {subj[f'name_{self.lang}']}",
            font=("Segoe UI", 13, "bold"),
            bg=COLORS["coffee"],
            fg=COLORS["cream"],
            anchor="w",
            padx=14,
            pady=10,
        ).pack(side="left")
        # O'ngda: o'chirish (✕) va tahrirlash (✎)
        self._icon_btn(
            head, "✕", COLORS["error"], lambda s=subj: self._delete_subject(s)
        ).pack(side="right", padx=(0, 10), pady=6)
        self._icon_btn(
            head, "✎", COLORS["gold"], lambda s=subj: self._edit_subject_dialog(s)
        ).pack(side="right", padx=(0, 2), pady=6)

        # --- AI chip ---
        tk.Label(
            card.inner,
            text=ai_chip,
            font=("Segoe UI", 9, "bold"),
            bg=ai_col,
            fg=COLORS["cream"],
            padx=12,
            pady=4,
        ).pack(anchor="w", padx=14, pady=(10, 4))

        # --- 3 mini-statistika ---
        stats_row = tk.Frame(card.inner, bg=COLORS["cream"])
        stats_row.pack(fill="x", padx=10, pady=4)
        self._mini_stat(
            stats_row, "⭐", avg, tr("average", self.lang), self._grade_color(avg)
        ).pack(side="left", fill="both", expand=True, padx=4)
        self._mini_ring(stats_row, pct, tr("attendance", self.lang)).pack(
            side="left", fill="both", expand=True, padx=4
        )
        self._mini_stat(
            stats_row, "📝", len(lectures), tr("lectures", self.lang), COLORS["caramel"]
        ).pack(side="left", fill="both", expand=True, padx=4)

        # --- Tugmalar: GRID bilan 3 teng ustun (endi hech biri kesilmaydi!) ---
        btn_row = tk.Frame(card.inner, bg=COLORS["cream"])
        btn_row.pack(fill="x", padx=10, pady=(4, 10))
        buttons = [
            (
                "📊 " + tr("grades", self.lang),
                COLORS["caramel"],
                lambda s=subj: self._grades_dialog(s),
            ),
            (
                "✅ " + tr("attendance", self.lang),
                COLORS["success"],
                lambda s=subj: self._attendance_dialog(s),
            ),
            (
                "📖 " + tr("lectures", self.lang),
                COLORS["gold"],
                lambda s=subj: self._lectures_dialog(s),
            ),
        ]
        for i, (txt, col, cmd) in enumerate(buttons):
            self._card_btn(btn_row, txt, col, cmd).grid(
                row=0, column=i, padx=3, sticky="nsew"
            )
            btn_row.grid_columnconfigure(i, weight=1)

        # --- O'qituvchi ma'lumoti ---
        info = []
        if subj["teacher"]:
            info.append(f"👨‍🏫 {subj['teacher']}")
        if subj["room"]:
            info.append(f"📍 {subj['room']}")
        if subj["phone"]:
            info.append(f"📱 {subj['phone']}")
        if info:
            tk.Label(
                card.inner,
                text="  •  ".join(info),
                font=("Segoe UI", 9),
                bg=COLORS["milk"],
                fg=COLORS["coffee"],
                anchor="w",
                padx=12,
                pady=6,
            ).pack(fill="x", padx=10, pady=(0, 8))
        return card

    # ================= MINI-STAT (count-up) =================
    def _mini_stat(self, parent, icon, value, label, color):
        t = tk.Canvas(
            parent, height=92, highlightthickness=0, bg=COLORS["cream"], cursor="hand2"
        )
        t._icon, t._label, t._color, t._shown = icon, label, color, 0
        t.bind("<Configure>", lambda e, tt=t: self._draw_mini(tt))
        t.bind("<Enter>", lambda e, tt=t: self._draw_mini(tt, True))
        t.bind("<Leave>", lambda e, tt=t: self._draw_mini(tt))
        self._draw_mini(t)
        self._count_up(t, value)
        return t

    def _draw_mini(self, t, hover=False):
        w, h = t.winfo_width(), t.winfo_height()
        if w < 20:
            return
        t.delete("all")
        if hover:
            round_rect(t, 2, 4, w - 1, h - 1, radius=14, fill="#e8d5b7", outline="")
            round_rect(
                t,
                0,
                0,
                w - 3,
                h - 5,
                radius=14,
                fill=COLORS["milk"],
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
                radius=14,
                fill=COLORS["milk"],
                outline=COLORS["sand"],
                width=1,
            )
        off = -2 if hover else 0
        t.create_text(w / 2 - 1, 24 + off, text=t._icon, font=("Segoe UI", 16))
        t.create_text(
            w / 2 - 1,
            52 + off,
            text=str(t._shown),
            font=("Segoe UI", 16, "bold"),
            fill=t._color,
        )
        t.create_text(
            w / 2 - 1,
            76 + off,
            text=t._label,
            font=("Segoe UI", 8),
            fill=COLORS["coffee"],
        )

    def _count_up(self, t, target):
        steps = 16

        def tick(i):
            if not t.winfo_exists():
                return
            t._shown = int(target * i / steps)
            try:
                self._draw_mini(t)
            except tk.TclError:
                return
            if i < steps:
                t.after(40, lambda: tick(i + 1))

        tick(0)

    # ================= MINI-RING =================
    def _mini_ring(self, parent, pct, label):
        t = tk.Canvas(
            parent, height=92, highlightthickness=0, bg=COLORS["cream"], cursor="hand2"
        )
        t._pct, t._label, t._shown = pct, label, 0
        t.bind("<Configure>", lambda e, tt=t: self._draw_ring(tt))
        t.bind("<Enter>", lambda e, tt=t: self._draw_ring(tt, True))
        t.bind("<Leave>", lambda e, tt=t: self._draw_ring(tt))
        self._draw_ring(t)
        self._ring_up(t, pct)
        return t

    def _draw_ring(self, t, hover=False):
        w, h = t.winfo_width(), t.winfo_height()
        if w < 20:
            return
        t.delete("all")
        col = self._att_color(t._pct)
        if hover:
            round_rect(t, 2, 4, w - 1, h - 1, radius=14, fill="#e8d5b7", outline="")
            round_rect(
                t,
                0,
                0,
                w - 3,
                h - 5,
                radius=14,
                fill=COLORS["milk"],
                outline=col,
                width=2,
            )
        else:
            round_rect(
                t,
                0,
                0,
                w - 1,
                h - 1,
                radius=14,
                fill=COLORS["milk"],
                outline=COLORS["sand"],
                width=1,
            )
        off = -2 if hover else 0
        cx, cy, r = w / 2 - 1, 38 + off, 16
        t.create_oval(cx - r, cy - r, cx + r, cy + r, outline=COLORS["sand"], width=4)
        if t._shown > 0:
            t.create_arc(
                cx - r,
                cy - r,
                cx + r,
                cy + r,
                start=90,
                extent=-360 * t._shown / 100,
                style="arc",
                outline=col,
                width=4,
            )
        t.create_text(
            cx,
            cy,
            text=f"{t._shown}%",
            font=("Segoe UI", 8, "bold"),
            fill=COLORS["coffee_dark"],
        )
        t.create_text(
            cx, h - 14 + off, text=t._label, font=("Segoe UI", 8), fill=COLORS["coffee"]
        )

    def _ring_up(self, t, target):
        steps = 16

        def tick(i):
            if not t.winfo_exists():
                return
            t._shown = int(target * i / steps)
            try:
                self._draw_ring(t)
            except tk.TclError:
                return
            if i < steps:
                t.after(40, lambda: tick(i + 1))

        tick(0)

    # ================= O'CHIRISH =================
    def _delete_subject(self, subj):
        if messagebox.askyesno(
            tr("confirm", self.lang),
            f"'{subj[f'name_{self.lang}']}' fanni o'chirasizmi?",
        ):
            self.db.delete_subject(subj["id"])
            self._refresh()

    # ================= FAN QO'SHISH =================
    def _add_subject_dialog(self):
        dialog = tk.Toplevel(self.parent)
        dialog.title("+ " + tr("add", self.lang))
        dialog.configure(bg=COLORS["cream"])
        dialog.transient(self.parent)
        dialog.resizable(False, False)
        dialog.grab_set()
        tk.Label(
            dialog,
            text="📚 " + tr("add", self.lang),
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

        lbl("O'zbekcha", True)
        uz = ModernEntry(f, outer_bg=COLORS["cream"], placeholder="Matematika")
        uz.pack(fill="x")
        lbl("Русский", True)
        ru = ModernEntry(f, outer_bg=COLORS["cream"], placeholder="Математика")
        ru.pack(fill="x")
        lbl("Тоҷикӣ", True)
        tj = ModernEntry(f, outer_bg=COLORS["cream"], placeholder="Математика")
        tj.pack(fill="x")
        lbl(tr("teacher", self.lang))
        teacher = ModernEntry(
            f, outer_bg=COLORS["cream"], placeholder="Ism (ixtiyoriy)"
        )
        teacher.pack(fill="x")
        lbl(tr("room", self.lang))
        room = ModernEntry(f, outer_bg=COLORS["cream"], placeholder="305 (ixtiyoriy)")
        room.pack(fill="x")
        lbl(tr("phone", self.lang))
        phone = ModernEntry(
            f, outer_bg=COLORS["cream"], placeholder="+998.. (ixtiyoriy)"
        )
        phone.pack(fill="x")

        def save():
            u, r, t = uz.get().strip(), ru.get().strip(), tj.get().strip()
            if not u or not r or not t:
                messagebox.showerror(
                    tr("error", self.lang),
                    "Barcha 3 tilda nom kiriting!",
                    parent=dialog,
                )
                return
            self.db.add_subject(
                u, r, t, teacher.get().strip(), room.get().strip(), phone.get().strip()
            )
            dialog.destroy()
            self._refresh()

        ModernButton(
            dialog, outer_bg=COLORS["cream"], text=tr("save", self.lang), command=save
        ).pack(pady=16)
        dialog.update_idletasks()
        dialog.geometry(f"440x{max(dialog.winfo_reqheight(), 560)}")

    # ================= FAN TAHRIRLASH (YANGI!) =================
    def _edit_subject_dialog(self, subj):
        dialog = tk.Toplevel(self.parent)
        dialog.title("✎ " + tr("edit", self.lang))
        dialog.configure(bg=COLORS["cream"])
        dialog.transient(self.parent)
        dialog.resizable(False, False)
        dialog.grab_set()
        tk.Label(
            dialog,
            text=f"✎ {subj[f'name_{self.lang}']}",
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

        uz = field("O'zbekcha", subj["name_uz"], True)
        ru = field("Русский", subj["name_ru"], True)
        tj = field("Тоҷикӣ", subj["name_tj"], True)
        teacher = field(tr("teacher", self.lang), subj["teacher"])
        room = field(tr("room", self.lang), subj["room"])
        phone = field(tr("phone", self.lang), subj["phone"])

        def save():
            u, r, t = uz.get().strip(), ru.get().strip(), tj.get().strip()
            if not u or not r or not t:
                messagebox.showerror(
                    tr("error", self.lang),
                    "Barcha 3 tilda nom kiriting!",
                    parent=dialog,
                )
                return
            self.db.update_subject(
                subj["id"],
                u,
                r,
                t,
                teacher.get().strip(),
                room.get().strip(),
                phone.get().strip(),
            )
            dialog.destroy()
            self._refresh()

        ModernButton(
            dialog, outer_bg=COLORS["cream"], text=tr("save", self.lang), command=save
        ).pack(pady=16)
        dialog.update_idletasks()
        dialog.geometry(f"440x{max(dialog.winfo_reqheight(), 560)}")

    # ================= BAHOlar DIALOGI (layout tuzatilgan) =================
    def _grades_dialog(self, subj):
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"📊 {tr('grades', self.lang)}")
        dialog.configure(bg=COLORS["cream"])
        dialog.transient(self.parent)
        dialog.resizable(False, False)
        dialog.grab_set()
        tk.Label(
            dialog,
            text=f"📊 {subj[f'name_{self.lang}']}",
            font=("Segoe UI", 16, "bold"),
            bg=COLORS["cream"],
            fg=COLORS["coffee_dark"],
        ).pack(pady=(16, 8))

        # QATOR 1: input + "+" tugma (sig'adi!)
        row1 = tk.Frame(dialog, bg=COLORS["cream"])
        row1.pack(fill="x", padx=24, pady=(0, 6))
        g_e = ModernEntry(
            row1, outer_bg=COLORS["cream"], placeholder="Baho (0-100)", width=150
        )
        g_e.pack(side="left")

        # QATOR 2: chip'lar (alohida)
        row2 = tk.Frame(dialog, bg=COLORS["cream"])
        row2.pack(fill="x", padx=24, pady=(0, 8))
        type_var = tk.StringVar(value="Imtihon")
        type_g = ChipGroup(
            row2,
            [
                ("Imtihon", "📝 Imtihon", COLORS["caramel"]),
                ("Savol", "🗣 Savol", COLORS["gold"]),
                ("Test", "✅ Test", COLORS["success"]),
            ],
            "Imtihon",
            outer_bg=COLORS["cream"],
        )
        type_g.pack(side="left")

        # Ro'yxat
        list_frame = tk.Frame(dialog, bg=COLORS["cream"])
        list_frame.pack(fill="both", expand=True, padx=24, pady=4)
        cv = tk.Canvas(list_frame, bg=COLORS["cream"], highlightthickness=0)
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=cv.yview)
        lf = tk.Frame(cv, bg=COLORS["cream"])
        lf.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0, 0), window=lf, anchor="nw")
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        def refresh():
            for w in lf.winfo_children():
                w.destroy()
            grades = self.db.get_grades(subj["id"])
            if not grades:
                tk.Label(
                    lf,
                    text="Baholar yo'q",
                    font=("Segoe UI", 11),
                    bg=COLORS["cream"],
                    fg=COLORS["coffee"],
                ).pack(pady=20)
                return
            for g in grades:
                col = self._grade_color(g["grade"])
                row = tk.Frame(lf, bg=COLORS["milk"], padx=8, pady=6)
                row.pack(fill="x", pady=2)
                tk.Label(
                    row,
                    text=str(g["grade"]),
                    font=("Segoe UI", 13, "bold"),
                    bg=col,
                    fg=COLORS["cream"],
                    width=4,
                ).pack(side="left", padx=(0, 10))
                tk.Label(
                    row,
                    text=f"{g['type']} • {g['date']}",
                    font=("Segoe UI", 10),
                    bg=COLORS["milk"],
                    fg=COLORS["coffee_dark"],
                ).pack(side="left")
                tk.Button(
                    row,
                    text="✕",
                    font=("Segoe UI", 9),
                    bg=COLORS["milk"],
                    fg=COLORS["error"],
                    relief="flat",
                    cursor="hand2",
                    command=lambda gid=g["id"]: self._del_grade(gid, subj, dialog),
                ).pack(side="right")

        def add():
            try:
                v = int(g_e.get())
                if not 0 <= v <= 100:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    tr("error", self.lang), "Baho 0-100 bo'lsin!", parent=dialog
                )
                return
            self.db.add_grade(subj["id"], v, type_var.get())
            g_e.clear_text()
            refresh()

        # "+" tugma row1 ning o'ngida (endi ko'rinadi!)
        ModernButton(
            row1,
            outer_bg=COLORS["cream"],
            text="+ Qo'shish",
            width=110,
            bg=COLORS["success"],
            hover_bg=COLORS["coffee"],
            active_bg=COLORS["coffee_dark"],
            command=add,
        ).pack(side="right", padx=(8, 0))

        refresh()
        ModernButton(
            dialog,
            outer_bg=COLORS["cream"],
            text=tr("close", self.lang),
            width=160,
            bg=COLORS["coffee"],
            command=dialog.destroy,
        ).pack(pady=12)
        dialog.update_idletasks()
        dialog.geometry(f"480x{max(dialog.winfo_reqheight(), 420)}")

    def _del_grade(self, gid, subj, parent):
        self.db.cursor.execute("DELETE FROM grades WHERE id=?", (gid,))
        self.db.conn.commit()
        parent.destroy()
        self._grades_dialog(subj)
        self._refresh()

    # ================= DAVOMAT DIALOGI =================
    def _attendance_dialog(self, subj):
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"✅ {tr('attendance', self.lang)}")
        dialog.configure(bg=COLORS["cream"])
        dialog.transient(self.parent)
        dialog.resizable(False, False)
        dialog.grab_set()
        tk.Label(
            dialog,
            text=f"✅ {subj[f'name_{self.lang}']}",
            font=("Segoe UI", 16, "bold"),
            bg=COLORS["cream"],
            fg=COLORS["coffee_dark"],
        ).pack(pady=(16, 8))
        stats = self.db.get_attendance_stats(subj["id"])
        total = stats["total"] or 0
        present = stats["present"] or 0
        pct = round(present / total * 100) if total else 0
        col = self._att_color(pct)
        sf = tk.Frame(dialog, bg=COLORS["cream"])
        sf.pack(fill="x", padx=24, pady=4)
        for lab, val in [
            ("Jami", total),
            ("Keldi", present),
            ("Kelmadi", total - present),
        ]:
            vf = tk.Frame(sf, bg=COLORS["milk"], padx=14, pady=8)
            vf.pack(side="left", expand=True, fill="x", padx=4)
            tk.Label(
                vf,
                text=str(val),
                font=("Segoe UI", 16, "bold"),
                bg=COLORS["milk"],
                fg=col if lab == "Keldi" else COLORS["coffee_dark"],
            ).pack()
            tk.Label(
                vf,
                text=lab,
                font=("Segoe UI", 9),
                bg=COLORS["milk"],
                fg=COLORS["coffee"],
            ).pack()
        tk.Label(
            dialog,
            text=f"Davomat: {pct}%",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["cream"],
            fg=col,
        ).pack(pady=4)
        bf = tk.Frame(dialog, bg=COLORS["cream"])
        bf.pack(pady=8)
        ModernButton(
            bf,
            outer_bg=COLORS["cream"],
            text="✅ Keldi",
            width=130,
            bg=COLORS["success"],
            hover_bg=COLORS["coffee"],
            command=lambda: self._mark(subj, "present", dialog),
        ).pack(side="left", padx=6)
        ModernButton(
            bf,
            outer_bg=COLORS["cream"],
            text="❌ Kelmadi",
            width=130,
            bg=COLORS["error"],
            hover_bg=COLORS["coffee_dark"],
            command=lambda: self._mark(subj, "absent", dialog),
        ).pack(side="left", padx=6)
        lf = tk.Frame(dialog, bg=COLORS["cream"])
        lf.pack(fill="both", expand=True, padx=24, pady=4)
        cv = tk.Canvas(lf, bg=COLORS["cream"], highlightthickness=0)
        sb = ttk.Scrollbar(lf, orient="vertical", command=cv.yview)
        inner = tk.Frame(cv, bg=COLORS["cream"])
        inner.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0, 0), window=inner, anchor="nw")
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        recs = self.db.get_attendance(subj["id"])
        if not recs:
            tk.Label(
                inner,
                text="Yozuvlar yo'q",
                font=("Segoe UI", 11),
                bg=COLORS["cream"],
                fg=COLORS["coffee"],
            ).pack(pady=20)
        for rc in recs[:20]:
            ok = rc["status"] == "present"
            row = tk.Frame(inner, bg=COLORS["milk"], padx=8, pady=5)
            row.pack(fill="x", pady=2)
            tk.Label(
                row, text="✅" if ok else "❌", font=("Segoe UI", 12), bg=COLORS["milk"]
            ).pack(side="left", padx=(0, 8))
            tk.Label(
                row,
                text=rc["date"],
                font=("Segoe UI", 10),
                bg=COLORS["milk"],
                fg=COLORS["coffee_dark"],
            ).pack(side="left")
        ModernButton(
            dialog,
            outer_bg=COLORS["cream"],
            text=tr("close", self.lang),
            width=160,
            bg=COLORS["coffee"],
            command=dialog.destroy,
        ).pack(pady=10)
        dialog.update_idletasks()
        dialog.geometry(f"440x{max(dialog.winfo_reqheight(), 460)}")

    def _mark(self, subj, status, parent):
        self.db.add_attendance(subj["id"], status)
        parent.destroy()
        self._attendance_dialog(subj)
        self._refresh()

    # ================= LEKSIYALAR DIALOGI (endi ko'rinadi!) =================
    def _lectures_dialog(self, subj):
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"📖 {tr('lectures', self.lang)}")
        dialog.configure(bg=COLORS["cream"])
        dialog.transient(self.parent)
        dialog.resizable(False, False)
        dialog.grab_set()
        tk.Label(
            dialog,
            text=f"📖 {subj[f'name_{self.lang}']}",
            font=("Segoe UI", 16, "bold"),
            bg=COLORS["cream"],
            fg=COLORS["coffee_dark"],
        ).pack(pady=(16, 6))
        ModernButton(
            dialog,
            outer_bg=COLORS["cream"],
            text="+ " + tr("add", self.lang),
            width=160,
            bg=COLORS["success"],
            hover_bg=COLORS["coffee"],
            command=lambda: self._add_lecture_dialog(subj, dialog),
        ).pack(pady=4)
        lf = tk.Frame(dialog, bg=COLORS["cream"])
        lf.pack(fill="both", expand=True, padx=24, pady=6)
        cv = tk.Canvas(lf, bg=COLORS["cream"], highlightthickness=0)
        sb = ttk.Scrollbar(lf, orient="vertical", command=cv.yview)
        inner = tk.Frame(cv, bg=COLORS["cream"])
        inner.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0, 0), window=inner, anchor="nw")
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        lecs = self.db.get_lectures(subj["id"])
        if not lecs:
            tk.Label(
                inner,
                text="Leksiyalar yo'q",
                font=("Segoe UI", 11),
                bg=COLORS["cream"],
                fg=COLORS["coffee"],
            ).pack(pady=20)
        for lc in lecs:
            row = tk.Frame(inner, bg=COLORS["milk"], padx=10, pady=8)
            row.pack(fill="x", pady=3)
            tk.Label(
                row,
                text=f"📖 {lc[f'title_{self.lang}']}",
                font=("Segoe UI", 11, "bold"),
                bg=COLORS["milk"],
                fg=COLORS["coffee_dark"],
                anchor="w",
            ).pack(side="left", fill="x", expand=True)
            tk.Button(
                row,
                text="Ko'rish",
                font=("Segoe UI", 9, "bold"),
                bg=COLORS["caramel"],
                fg=COLORS["cream"],
                relief="flat",
                cursor="hand2",
                padx=8,
                command=lambda l=lc: self._view_lecture(l),
            ).pack(side="left", padx=4)
            tk.Button(
                row,
                text="✕",
                font=("Segoe UI", 9),
                bg=COLORS["milk"],
                fg=COLORS["error"],
                relief="flat",
                cursor="hand2",
                command=lambda lid=lc["id"]: self._del_lecture(lid, subj, dialog),
            ).pack(side="left")
        ModernButton(
            dialog,
            outer_bg=COLORS["cream"],
            text=tr("close", self.lang),
            width=160,
            bg=COLORS["coffee"],
            command=dialog.destroy,
        ).pack(pady=10)
        dialog.update_idletasks()
        dialog.geometry(f"520x{max(dialog.winfo_reqheight(), 420)}")

    def _add_lecture_dialog(self, subj, parent):
        dialog = tk.Toplevel(self.parent)
        dialog.title("+ " + tr("lectures", self.lang))
        dialog.configure(bg=COLORS["cream"])
        dialog.transient(self.parent)
        dialog.resizable(False, False)
        dialog.grab_set()
        tk.Label(
            dialog,
            text="📖 " + tr("add", self.lang),
            font=("Segoe UI", 16, "bold"),
            bg=COLORS["cream"],
            fg=COLORS["coffee_dark"],
        ).pack(pady=(16, 8))
        f = tk.Frame(dialog, bg=COLORS["cream"])
        f.pack(fill="x", padx=24)
        titles, contents = {}, {}
        for code, name in [("uz", "O'zbekcha"), ("ru", "Русский"), ("tj", "Тоҷикӣ")]:
            tk.Label(
                f,
                text=f"{name}:",
                font=("Segoe UI", 10, "bold"),
                bg=COLORS["cream"],
                fg=COLORS["coffee"],
            ).pack(anchor="w", pady=(6, 2))
            te = ModernEntry(f, outer_bg=COLORS["cream"], placeholder="Sarlavha")
            te.pack(fill="x")
            titles[code] = te
            ce = tk.Text(
                f,
                font=("Segoe UI", 10),
                height=2,
                bg=COLORS["milk"],
                fg=COLORS["coffee_dark"],
                relief="flat",
                highlightbackground=COLORS["sand"],
                highlightthickness=1,
            )
            ce.pack(fill="x", pady=(2, 4))
            contents[code] = ce

        def save():
            tv = [titles[c].get().strip() for c in ["uz", "ru", "tj"]]
            cv = [contents[c].get("1.0", "end").strip() for c in ["uz", "ru", "tj"]]
            if not all(tv) or not all(cv):
                messagebox.showerror(
                    tr("error", self.lang),
                    "Barcha maydonlarni to'ldiring!",
                    parent=dialog,
                )
                return
            self.db.add_lecture(subj["id"], *tv, *cv)
            dialog.destroy()
            parent.destroy()
            self._lectures_dialog(subj)
            self._refresh()

        ModernButton(
            dialog, outer_bg=COLORS["cream"], text=tr("save", self.lang), command=save
        ).pack(pady=14)
        dialog.update_idletasks()
        dialog.geometry(f"480x{max(dialog.winfo_reqheight(), 560)}")

    def _view_lecture(self, lc):
        dialog = tk.Toplevel(self.parent)
        dialog.title(lc[f"title_{self.lang}"])
        dialog.configure(bg=COLORS["cream"])
        dialog.transient(self.parent)
        dialog.resizable(False, False)
        dialog.grab_set()
        tk.Label(
            dialog,
            text=lc[f"title_{self.lang}"],
            font=("Segoe UI", 15, "bold"),
            bg=COLORS["cream"],
            fg=COLORS["coffee_dark"],
            wraplength=440,
        ).pack(pady=(16, 8), padx=20)
        tw = tk.Text(
            dialog,
            wrap="word",
            font=("Segoe UI", 11),
            bg=COLORS["milk"],
            fg=COLORS["coffee_dark"],
            relief="flat",
            padx=16,
            pady=16,
            height=14,
        )
        tw.pack(fill="both", expand=True, padx=20, pady=4)
        tw.insert("1.0", lc[f"content_{self.lang}"])
        tw.config(state="disabled")
        ModernButton(
            dialog,
            outer_bg=COLORS["cream"],
            text=tr("close", self.lang),
            width=140,
            bg=COLORS["coffee"],
            command=dialog.destroy,
        ).pack(pady=12)
        dialog.update_idletasks()
        dialog.geometry(f"480x{max(dialog.winfo_reqheight(), 460)}")

    def _del_lecture(self, lid, subj, parent):
        if messagebox.askyesno(
            tr("confirm", self.lang), tr("confirm", self.lang), parent=parent
        ):
            self.db.delete_lecture(lid)
            parent.destroy()
            self._lectures_dialog(subj)
            self._refresh()

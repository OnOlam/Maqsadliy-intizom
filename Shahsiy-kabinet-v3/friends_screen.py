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

IMP_COLORS = {3: COLORS["gold"], 2: COLORS["caramel"], 1: COLORS["sand"]}
IMP_LABELS = {3: "⭐⭐⭐ Yaqin do'st", 2: "⭐⭐ Do'st", 1: "⭐ Tanish"}


class FriendsScreen:
    def __init__(self, parent, db, lang):
        self.parent = parent
        self.db = db
        self.lang = lang
        self.search_text = ""
        self.filter_val = None  # None = hammasi
        self.build_ui()

    # ================= UI =================
    def build_ui(self):
        for w in self.parent.winfo_children():
            w.destroy()

        # --- Header ---
        header = tk.Frame(self.parent, bg=COLORS["milk"])
        header.pack(fill="x", padx=20, pady=(18, 8))
        tk.Label(
            header,
            text=f"👥 {tr('friends', self.lang)}",
            font=("Segoe UI", 20, "bold"),
            bg=COLORS["milk"],
            fg=COLORS["coffee_dark"],
        ).pack(side="left")
        make_pill_button(
            header,
            "+ " + tr("add", self.lang),
            COLORS["success"],
            lambda: self._friend_dialog(),
            outer_bg=COLORS["milk"],
        ).pack(side="right")

        # --- Tug'ilgan kun banneri (faqat bor bo'lsa) ---
        self._birthday_banner()

        # --- Qidiruv + filtr paneli ---
        toolbar = tk.Frame(self.parent, bg=COLORS["milk"])
        toolbar.pack(fill="x", padx=20, pady=(4, 10))

        search_wrap = tk.Frame(toolbar, bg=COLORS["cream"], padx=8, pady=4)
        search_wrap.pack(side="left")
        tk.Label(
            search_wrap,
            text="🔍",
            font=("Segoe UI", 11),
            bg=COLORS["cream"],
            fg=COLORS["coffee"],
        ).pack(side="left", padx=(0, 6))
        self.search_entry = tk.Entry(
            search_wrap,
            font=("Segoe UI", 11),
            width=24,
            bg=COLORS["cream"],
            fg=COLORS["coffee_dark"],
            relief="flat",
            insertbackground=COLORS["coffee_dark"],
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self._on_search)

        filt_wrap = tk.Frame(toolbar, bg=COLORS["milk"])
        filt_wrap.pack(side="right")
        filt_opts = [
            (None, "Hammasi", COLORS["coffee"]),
            (3, "⭐⭐⭐", COLORS["gold"]),
            (2, "⭐⭐", COLORS["caramel"]),
            (1, "⭐", COLORS["sand"]),
        ]
        self.filt_holder = tk.Frame(filt_wrap, bg=COLORS["milk"])
        self.filt_holder.pack(side="left")
        self._filt_labels = {}
        for val, lab, col in filt_opts:
            l = tk.Label(
                self.filt_holder,
                text=lab,
                font=("Segoe UI", 10, "bold"),
                bg=col if val is None else COLORS["milk"],
                fg=COLORS["cream"] if val is None else COLORS["coffee"],
                padx=12,
                pady=6,
                cursor="hand2",
            )
            l._val, l._col = val, col
            self._filt_labels[val] = l
            l.bind("<Button-1>", lambda e, vv=val: self._set_filter(vv))
            l.bind("<Enter>", lambda e, ll=l, vv=val: self._filt_hover(ll, vv, True))
            l.bind("<Leave>", lambda e, ll=l, vv=val: self._filt_hover(ll, vv, False))
            l.pack(side="left", padx=3)

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

    # ================= TOOLBAR YORDAMCHILARI =================
    def _on_search(self, e=None):
        self.search_text = self.search_entry.get().strip().lower()
        self._refresh()

    def _set_filter(self, val):
        self.filter_val = val
        for k, l in self._filt_labels.items():
            if k == val:
                l.config(bg=l._col, fg=COLORS["cream"])
            else:
                l.config(bg=COLORS["milk"], fg=COLORS["coffee"])
        self._refresh()

    def _filt_hover(self, l, val, enter):
        if val == self.filter_val:
            return
        l.config(bg=COLORS["sand"] if enter else COLORS["milk"])

    # ================= TUG'ILGAN KUN BANNERI =================
    def _birthday_banner(self):
        bdays = self.db.get_upcoming_birthdays(7)
        if not bdays:
            return
        banner = tk.Canvas(
            self.parent, height=64, highlightthickness=0, bg=COLORS["milk"]
        )
        banner.pack(fill="x", padx=20, pady=(0, 8))
        banner.bind("<Configure>", lambda e, b=banner: self._paint_bday(b, bdays))
        self._paint_bday(banner, bdays)

    def _paint_bday(self, b, bdays):
        w, h = b.winfo_width(), b.winfo_height()
        if w < 20:
            return
        b.delete("all")
        # Gradient
        c1, c2 = (212, 160, 23), (139, 69, 19)
        for i in range(20):
            r = i / 20
            cr = int(c1[0] + (c2[0] - c1[0]) * r)
            cg = int(c1[1] + (c2[1] - c1[1]) * r)
            cb = int(c1[2] + (c2[2] - c1[2]) * r)
            x1 = int(w * i / 20)
            x2 = int(w * (i + 1) / 20)
            b.create_rectangle(
                x1, 0, x2, h, fill=f"#{cr:02x}{cg:02x}{cb:02x}", outline=""
            )
        round_rect(
            b, 2, 2, w - 3, h - 3, radius=18, fill="", outline=COLORS["cream"], width=2
        )
        # Matn
        parts = []
        for f, d in bdays[:3]:
            if d == 0:
                parts.append(f"🎉 {f['name']} BUGUN!")
            else:
                parts.append(f"🎂 {f['name']} — {d} kun")
        b.create_text(
            20,
            h / 2,
            text="  •  ".join(parts),
            anchor="w",
            font=("Segoe UI", 12, "bold"),
            fill=COLORS["cream"],
        )

    # ================= FANLARNI YANGILASH =================
    def _filtered(self):
        friends = self.db.get_friends()
        out = []
        for f in friends:
            if self.filter_val is not None and f["importance"] != self.filter_val:
                continue
            if self.search_text and self.search_text not in f["name"].lower():
                continue
            out.append(f)
        return out

    def _refresh(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        friends = self._filtered()
        if not friends:
            empty = tk.Frame(self.grid_frame, bg=COLORS["milk"])
            empty.pack(expand=True, pady=60)
            tk.Label(empty, text="👥", font=("Segoe UI", 50), bg=COLORS["milk"]).pack()
            msg = (
                "Do'stlar topilmadi"
                if (self.search_text or self.filter_val)
                else "Hozircha do'stlar yo'q"
            )
            tk.Label(
                empty,
                text=msg,
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
        cols = 3
        for i, fr in enumerate(friends):
            r, c = divmod(i, cols)
            self._friend_card(fr).grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
            self.grid_frame.grid_columnconfigure(c, weight=1)
        for c in range(cols, 3):
            self.grid_frame.grid_columnconfigure(c, weight=1)

    # ================= DO'ST KARTASI =================
    def _friend_card(self, fr):
        imp = fr["importance"]
        col = IMP_COLORS.get(imp, COLORS["sand"])
        card = RoundedCard(self.grid_frame, header_bg=None)

        # --- Yuqori qator: avatar + ism + tugmalar ---
        top = tk.Frame(card.inner, bg=COLORS["cream"])
        top.pack(fill="x", padx=12, pady=(12, 6))

        avatar = self._avatar(top, fr["name"], col)
        avatar.pack(side="left", padx=(0, 12))

        name_wrap = tk.Frame(top, bg=COLORS["cream"])
        name_wrap.pack(side="left", fill="x", expand=True)
        tk.Label(
            name_wrap,
            text=fr["name"],
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["cream"],
            fg=COLORS["coffee_dark"],
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            name_wrap,
            text=IMP_LABELS.get(imp, ""),
            font=("Segoe UI", 9, "bold"),
            bg=col,
            fg=COLORS["cream"],
            padx=8,
            pady=2,
            anchor="w",
        ).pack(anchor="w", pady=(3, 0))

        # Tugmalar (o'ngda, vertikal)
        btns = tk.Frame(top, bg=COLORS["cream"])
        btns.pack(side="right")
        self._icon_btn(
            btns, "✎", COLORS["gold"], lambda f=fr: self._friend_dialog(f)
        ).pack(pady=2)
        self._icon_btn(
            btns, "✕", COLORS["error"], lambda f=fr: self._delete_friend(f)
        ).pack(pady=2)

        # --- Kontakt chip'lari ---
        chips = tk.Frame(card.inner, bg=COLORS["cream"])
        chips.pack(fill="x", padx=12, pady=(2, 6))
        contact_rows = [
            ("📱", fr["phone"], COLORS["success"]),
            ("✉️", fr["email"], COLORS["caramel"]),
            ("✈️", fr["telegram"], COLORS["coffee"]),
            ("💼", fr["workplace"], COLORS["gold"]),
        ]
        has_any = False
        for icon, val, ccol in contact_rows:
            if val:
                has_any = True
                row = tk.Frame(chips, bg=COLORS["cream"])
                row.pack(fill="x", pady=1)
                tk.Label(
                    row,
                    text=icon,
                    font=("Segoe UI", 10),
                    bg=ccol,
                    fg=COLORS["cream"],
                    width=3,
                ).pack(side="left", padx=(0, 6))
                tk.Label(
                    row,
                    text=val,
                    font=("Segoe UI", 10),
                    bg=COLORS["cream"],
                    fg=COLORS["coffee_dark"],
                    anchor="w",
                ).pack(side="left", fill="x", expand=True)
        if not has_any:
            tk.Label(
                chips,
                text="📭 Aloqa ma'lumoti yo'q",
                font=("Segoe UI", 9),
                bg=COLORS["cream"],
                fg=COLORS["sand"],
            ).pack(anchor="w")

        # --- Izoh ---
        if fr["notes"]:
            tk.Label(
                card.inner,
                text=f"📝 {fr['notes']}",
                font=("Segoe UI", 9),
                bg=COLORS["milk"],
                fg=COLORS["coffee"],
                anchor="w",
                wraplength=260,
                justify="left",
                padx=10,
                pady=6,
            ).pack(fill="x", padx=12, pady=(0, 10))
        else:
            tk.Frame(card.inner, bg=COLORS["cream"], height=6).pack(fill="x")
        return card

    # ================= AVATAR (yumaloq, harfli) =================
    def _avatar(self, parent, name, color, size=56):
        a = tk.Canvas(
            parent, width=size, height=size, highlightthickness=0, bg=COLORS["cream"]
        )
        letter = name.strip()[0].upper() if name.strip() else "?"
        cx = cy = size / 2
        r = size / 2 - 3
        # Tashqi halqa (muhimlik)
        a.create_oval(2, 2, size - 2, size - 2, outline=color, width=3)
        # Ichki doira
        a.create_oval(6, 6, size - 6, size - 6, fill=color, outline="")
        # Harf
        a.create_text(
            cx,
            cy,
            text=letter,
            font=("Segoe UI", int(size * 0.42), "bold"),
            fill=COLORS["cream"],
        )
        return a

    # ================= IKONKA TUGMA =================
    def _icon_btn(self, parent, symbol, color, cmd, size=30):
        b = tk.Canvas(
            parent,
            width=size,
            height=size,
            highlightthickness=0,
            bg=COLORS["cream"],
            cursor="hand2",
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

    # ================= O'CHIRISH =================
    def _delete_friend(self, fr):
        if messagebox.askyesno(
            tr("confirm", self.lang), f"'{fr['name']}' do'stni o'chirasizmi?"
        ):
            self.db.delete_friend(fr["id"])
            self._refresh()

    # ================= QO'SHISH / TAHRIRLASH DIALOGI =================
    def _friend_dialog(self, fr=None):
        is_edit = fr is not None
        dialog = tk.Toplevel(self.parent)
        dialog.title(("✎ " if is_edit else "+ ") + tr("friends", self.lang))
        dialog.configure(bg=COLORS["cream"])
        dialog.transient(self.parent)
        dialog.resizable(False, False)
        dialog.grab_set()
        tk.Label(
            dialog,
            text=("✎ " if is_edit else "👤 ") + tr("add", self.lang),
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

        name_e = field(
            tr("friend_name", self.lang), fr["name"] if is_edit else "", True
        )
        bday_e = field(
            tr("birthday", self.lang) + " (YYYY-MM-DD)",
            fr["birthday"] if is_edit else "",
        )
        phone_e = field(tr("phone", self.lang), fr["phone"] if is_edit else "")
        email_e = field(tr("email", self.lang), fr["email"] if is_edit else "")
        tg_e = field(tr("telegram", self.lang), fr["telegram"] if is_edit else "")
        work_e = field(tr("workplace", self.lang), fr["workplace"] if is_edit else "")

        lbl(tr("notes", self.lang))
        notes_t = tk.Text(
            f,
            font=("Segoe UI", 10),
            height=2,
            bg=COLORS["milk"],
            fg=COLORS["coffee_dark"],
            relief="flat",
            highlightbackground=COLORS["sand"],
            highlightthickness=1,
        )
        notes_t.pack(fill="x")
        if is_edit and fr["notes"]:
            notes_t.insert("1.0", fr["notes"])

        lbl(tr("importance", self.lang))
        imp_opts = [
            (3, "⭐⭐⭐ Yaqin", COLORS["gold"]),
            (2, "⭐⭐ Do'st", COLORS["caramel"]),
            (1, "⭐ Tanish", COLORS["sand"]),
        ]
        imp_g = ChipGroup(
            f, imp_opts, fr["importance"] if is_edit else 2, outer_bg=COLORS["cream"]
        )
        imp_g.pack(fill="x", pady=(2, 4))

        def save():
            name = name_e.get().strip()
            if not name:
                messagebox.showerror(
                    tr("error", self.lang), "Ism kiriting!", parent=dialog
                )
                return
            data = dict(
                name=name,
                birthday=bday_e.get().strip(),
                phone=phone_e.get().strip(),
                email=email_e.get().strip(),
                telegram=tg_e.get().strip(),
                workplace=work_e.get().strip(),
                notes=notes_t.get("1.0", "end").strip(),
                importance=imp_g.get(),
            )
            if is_edit:
                self.db.update_friend(fr["id"], **data)
            else:
                self.db.add_friend(**data)
            dialog.destroy()
            self._refresh()

        ModernButton(
            dialog, outer_bg=COLORS["cream"], text=tr("save", self.lang), command=save
        ).pack(pady=16)
        dialog.update_idletasks()
        dialog.geometry(f"460x{max(dialog.winfo_reqheight(), 620)}")

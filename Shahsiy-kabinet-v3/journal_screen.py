import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
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
from ai_assistant import AIAssistant

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

TYPE_STYLES = {
    "idea": {"icon": "💡", "label": "G'oya", "color": COLORS["gold"], "bg": "#fff8e1"},
    "win": {
        "icon": "🎉",
        "label": "G'alaba",
        "color": COLORS["success"],
        "bg": "#e8f5e9",
    },
    "pain": {
        "icon": "😔",
        "label": "Dard/Muammo",
        "color": COLORS["error"],
        "bg": "#ffebee",
    },
    "note": {
        "icon": "📌",
        "label": "Eslatma",
        "color": COLORS["coffee"],
        "bg": COLORS["milk"],
    },
}


class JournalScreen:
    def __init__(self, parent, db, lang):
        self.parent = parent
        self.db = db
        self.lang = lang
        self.ai = AIAssistant(db, lang)
        self.secret_mode = False
        self.build_ui()  # UI ni qurish

    def build_ui(self):
        for w in self.parent.winfo_children():
            w.destroy()

        header = tk.Frame(self.parent, bg=COLORS["milk"])
        header.pack(fill="x", padx=20, pady=(18, 10))
        tk.Label(
            header,
            text=f"🧠 Ruxiy Miya",
            font=("Segoe UI", 20, "bold"),
            bg=COLORS["milk"],
            fg=COLORS["coffee_dark"],
        ).pack(side="left")

        sec_btn = make_pill_button(
            header,
            "🔒 Maxfiy",
            COLORS["purple"],
            self._toggle_secret,
            outer_bg=COLORS["milk"],
            height=36,
            min_width=100,
            font_size=10,
        )
        sec_btn.pack(side="right", padx=5)

        # --- TEZKOR YOZUV PANELI (STICKY TOP - DOIM KO'RINADIGAN JOYDA) ---
        quick_card = RoundedCard(self.parent, header_bg=None)
        quick_card.pack(fill="x", padx=20, pady=(0, 10))

        q_inner = tk.Frame(quick_card.inner, bg=COLORS["cream"], padx=14, pady=10)
        q_inner.pack(fill="x")

        cat_opts = [
            ("idea", "💡 G'oya", TYPE_STYLES["idea"]["color"]),
            ("win", "🎉 G'alaba", TYPE_STYLES["win"]["color"]),
            ("pain", "😔 Dard", TYPE_STYLES["pain"]["color"]),
            ("note", "📌 Eslatma", TYPE_STYLES["note"]["color"]),
        ]
        self.cat_group = ChipGroup(q_inner, cat_opts, "note", outer_bg=COLORS["cream"])
        self.cat_group.pack(anchor="w", pady=(0, 6))

        input_wrap = tk.Frame(q_inner, bg=COLORS["milk"], padx=10, pady=8)
        input_wrap.pack(fill="x")

        self.quick_input = tk.Text(
            input_wrap,
            font=("Segoe UI", 12),
            height=2,
            bg=COLORS["milk"],
            fg=COLORS["coffee_dark"],
            relief="flat",
            highlightbackground=COLORS["sand"],
            highlightthickness=1,
        )
        self.quick_input.pack(side="left", fill="x", expand=True)
        self.quick_input.bind("<Return>", lambda e: self._send_message())

        send_btn = ModernButton(
            input_wrap,
            outer_bg=COLORS["milk"],
            text="➤",
            width=40,
            bg=COLORS["caramel"],
            hover_bg=COLORS["coffee"],
            command=self._send_message,
        )
        send_btn.pack(side="right", padx=(8, 0))

        tk.Label(
            q_inner,
            text="💡 Matnni yozing va ENTER bosing. AI darhol javob beradi.",
            font=("Segoe UI", 8),
            bg=COLORS["cream"],
            fg=COLORS["sand"],
        ).pack(anchor="w", pady=(4, 0))

        # --- JONLI SUHBAT MAYDONI (CHAT LOG) ---
        container = tk.Frame(self.parent, bg=COLORS["milk"])
        container.pack(fill="both", expand=True, padx=20, pady=(0, 18))

        self.scroll_canvas = tk.Canvas(
            container, bg=COLORS["milk"], highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            container, orient="vertical", command=self.scroll_canvas.yview
        )
        self.chat_frame = tk.Frame(self.scroll_canvas, bg=COLORS["milk"])
        self.chat_win = self.scroll_canvas.create_window(
            (0, 0), window=self.chat_frame, anchor="nw"
        )

        def _conf(e):
            self.scroll_canvas.itemconfig(self.chat_win, width=e.width)
            self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

        self.scroll_canvas.bind("<Configure>", _conf)
        self.chat_frame.bind(
            "<Configure>",
            lambda e: self.scroll_canvas.configure(
                scrollregion=self.scroll_canvas.bbox("all")
            ),
        )
        self.scroll_canvas.configure(yscrollcommand=scrollbar.set)
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _wheel(e):
            if self.scroll_canvas.winfo_exists():
                self.scroll_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        self.scroll_canvas.bind("<MouseWheel>", _wheel)
        self.chat_frame.bind("<MouseWheel>", _wheel)

        self._load_history()

    # ================= MANTIQ =================
    def _toggle_secret(self):
        self.secret_mode = not self.secret_mode
        self._load_history()

    def _send_message(self):
        text = self.quick_input.get("1.0", "end").strip()
        if not text:
            return

        entry_type = self.cat_group.get()
        is_sec = self.secret_mode

        # Saqlash
        self.db.add_journal_entry("", text, entry_type, is_sec)
        self.db.add_points(5, "Ruxiy miya yangilandi")

        # Tozalash
        self.quick_input.delete("1.0", "end")

        # 1. Avval AI javobini hisoblab olish (simulyatsiya)
        response = self.ai.analyze_new_entry("", text, entry_type)

        # 2. Chat'ga qo'shish (Yangi yozuv tepaga chiqadi!)
        # AI javobi birinchi bo'lib tepaga chiqadi (go'yo u oldindan tayyor bo'lgandek)
        self._append_chat_bubble(response, "ai", False, role="ai")
        # Keyin foydalanuvchi yozuvi chiqadi
        self._append_chat_bubble(text, entry_type, is_sec, role="user")

        # Skroll yuqoriga (yangi yozuvlar tepada bo'lgani uchun)
        self.chat_frame.update_idletasks()
        self.scroll_canvas.yview_moveto(0.0)

    def _load_history(self):
        for w in self.chat_frame.winfo_children():
            w.destroy()

        entries = self.db.get_journal_entries(include_secrets=self.secret_mode)

        # Guruhlash (kunlar bo'yicha) - YENGI TARTIBDA (Yangidan Eskiga)
        current_day = None
        # reversed(entries) o'rniga to'g'ridan-to'g'ri entries (chunki DB DESC tartibda qaytaradi)
        for e in entries:
            try:
                ed = date.fromisoformat(e["date"])
                day_str = ed.strftime("%d.%m.%Y")
            except:
                continue

            if day_str != current_day:
                current_day = day_str
                sep = tk.Label(
                    self.chat_frame,
                    text=f"— {day_str} —",
                    font=("Segoe UI", 9, "bold"),
                    bg=COLORS["milk"],
                    fg=COLORS["sand"],
                )
                sep.pack(pady=8)

            # Foydalanuvchi yozuvi
            self._append_chat_bubble(
                e["content"], e["type"], bool(e["is_secret"]), role="user", silent=True
            )

            # Agar g'oya bo'lsa, AI rivojlantirish taklifi (statik matn sifatida)
            if e["type"] == "idea":
                ai_tip = "💡 Bu g'oyani rivojlantirish uchun quyidagi 'Rivojlantirish' tugmasidan foydalaning."
                self._append_chat_bubble(ai_tip, "ai", False, role="ai", silent=True)

    def _append_chat_bubble(self, text, meta, is_secret, role="user", silent=False):
        # Asosiy konteyner (butun kenglikni egallaydi, lekin ichki elementlar hizalanadi)
        container = tk.Frame(self.chat_frame, bg=COLORS["milk"], padx=5, pady=3)
        container.pack(fill="x")

        # Rang va uslub tanlash
        if role == "ai":
            bg_color = COLORS["milk"]  # Och kulrang fon
            border_color = COLORS["coffee"]  # Qora chegara
            icon_txt = "🤖 AI Yordamchi"
            col = COLORS["coffee"]
            align_side = "w"  # Chapga
        else:
            style = TYPE_STYLES.get(meta, TYPE_STYLES["note"])
            prefix = "🔒 " if is_secret else ""
            icon_txt = f"{prefix}{style['icon']} {style['label']}"
            col = style["color"]
            bg_color = COLORS["cream"]  # Krem rangli fon (foydalanuvchi)
            border_color = style["color"]  # Kategoriya rangida chegara
            align_side = "e"  # O'ngga

        # Bubble frame (Ichki qism - faqat kerakli kenglikda)
        bubble = tk.Frame(
            container,
            bg=bg_color,
            highlightbackground=border_color,
            highlightthickness=1,
            padx=12,
            pady=8,
        )

        # MUHIM: anchor bilan joylashtirish (fill="x" emas!)
        bubble.pack(anchor=align_side, padx=(0, 40) if align_side == "e" else (40, 0))

        # Sarlavha (Icon + Label)
        lbl_header = tk.Label(
            bubble,
            text=icon_txt,
            font=("Segoe UI", 9, "bold"),
            bg=bubble.cget("bg"),
            fg=col,
            anchor="w",
        )
        lbl_header.pack(fill="x")

        # Matn
        lbl_text = tk.Label(
            bubble,
            text=text,
            font=("Segoe UI", 11),
            bg=bubble.cget("bg"),
            fg=COLORS["coffee_dark"],
            wraplength=450,
            justify="left",
            anchor="w",
        )
        lbl_text.pack(fill="x", pady=(2, 0))

        # Agar g'oya bo'lsa va jonli yozilgan bo'lsa, rivojlantirish tugmasi
        if role == "user" and meta == "idea" and not silent:
            dev_btn = tk.Button(
                bubble,
                text="🚀 Rivojlantirish",
                font=("Segoe UI", 8, "bold"),
                bg=COLORS["gold"],
                fg=COLORS["coffee_dark"],
                relief="flat",
                cursor="hand2",
                padx=8,
                pady=2,
                command=lambda t=text: self._develop_idea(t),
            )
            dev_btn.pack(anchor="w", pady=(5, 0))

    def _develop_idea(self, original_text):
        d = tk.Toplevel(self.parent)
        d.title("🚀 G'oyani Rivojlantirish")
        d.configure(bg=COLORS["cream"])
        d.transient(self.parent)
        d.resizable(False, False)
        d.grab_set()

        tk.Label(
            d,
            text="Asl G'oya:",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["cream"],
            fg=COLORS["coffee"],
        ).pack(anchor="w", padx=20, pady=(10, 2))
        tk.Label(
            d,
            text=original_text,
            font=("Segoe UI", 10),
            bg=COLORS["milk"],
            fg=COLORS["coffee_dark"],
            wraplength=400,
            justify="left",
            padx=10,
            pady=5,
        ).pack(anchor="w", padx=20, pady=(0, 10))

        tk.Label(
            d,
            text="Yangi fikr yoki qadam:",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["cream"],
            fg=COLORS["coffee"],
        ).pack(anchor="w", padx=20, pady=(0, 2))

        new_e = tk.Text(
            d,
            font=("Segoe UI", 11),
            height=3,
            bg=COLORS["milk"],
            fg=COLORS["coffee_dark"],
            relief="flat",
            highlightbackground=COLORS["sand"],
            highlightthickness=1,
        )
        new_e.pack(fill="x", padx=20, pady=5)

        def save_dev():
            new_text = new_e.get("1.0", "end").strip()
            if not new_text:
                return
            full_content = (
                f"[RIVOJLANISH]\nAsl: {original_text}\n\nYangi qadam: {new_text}"
            )
            self.db.add_journal_entry("", full_content, "idea", False)
            self.db.add_points(10, "G'oya rivojlantirildi")
            d.destroy()
            self._load_history()  # Tarixni yangilash

        ModernButton(
            d,
            outer_bg=COLORS["cream"],
            text="Saqlash va Rivojlantirish",
            command=save_dev,
        ).pack(pady=15)
        d.update_idletasks()
        d.geometry(f"450x{max(d.winfo_reqheight(), 300)}")

    # ================= YORDAMCHILAR =================
    # (_pill_btn / _paint_pill / _lighten endi ui_widgets.py da umumiy)

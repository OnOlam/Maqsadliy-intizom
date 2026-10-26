import tkinter as tk
from tkinter import ttk, messagebox
from ui_widgets import (
    ModernEntry,
    ModernButton,
    PillToggle,
    round_rect,
    RoundedCard,
    ChipGroup,
)
import math
import random
from datetime import datetime, date
from database import Database
from translations import tr
from ai_assistant import AIAssistant
from calendar_screen import CalendarScreen
from subjects_screen import SubjectsScreen
from friends_screen import FriendsScreen
from goals_screen import GoalsScreen
# from mood_screen import MoodScreen
from budget_screen import BudgetScreen
# from pomodoro_screen import PomodoroScreen
from journal_screen import JournalScreen
# from achievements_screen import AchievementsScreen
from settings_screen import SettingsScreen
from datetime import datetime, date, timedelta

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


class App:
    def __init__(self):
        self.db = Database()
        self.root = tk.Tk()
        self.root.title(tr("app_title", self.get_lang()))
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)
        self.root.configure(bg=COLORS["coffee_dark"])
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 550
        y = (self.root.winfo_screenheight() // 2) - 350
        self.root.geometry(f"1100x700+{x}+{y}")
        self.current_lang = self.get_lang()
        self.active_menu = "dashboard"
        self.show_login_screen()
        self.root.mainloop()

    def get_lang(self):
        return self.db.get_setting("language", "uz")

    # ============== KIRISH EKRANI (ZAMONAVIY) ==============
    def show_login_screen(self):
        for w in self.root.winfo_children():
            w.destroy()
        self._start_fade_in()
        self.canvas = tk.Canvas(
            self.root, highlightthickness=0, bg=COLORS["coffee_dark"]
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self._draw_login_scene())
        self.gradient_step = 0
        self.center_frame = tk.Frame(
            self.canvas, bg=COLORS["cream"], width=460, height=580
        )
        self.center_window = self.canvas.create_window(0, 0, window=self.center_frame)

        self.logo_label = tk.Label(
            self.center_frame,
            text="☕",
            font=("Segoe UI", 10),
            bg=COLORS["cream"],
            fg=COLORS["caramel"],
        )
        self.logo_label.pack(pady=(35, 0))
        self.title_label = tk.Label(
            self.center_frame,
            text="",
            font=("Segoe UI", 24, "bold"),
            bg=COLORS["cream"],
            fg=COLORS["coffee_dark"],
        )
        self.title_label.pack(pady=(5, 0))
        self.subtitle_label = tk.Label(
            self.center_frame,
            text="",
            font=("Segoe UI", 11),
            bg=COLORS["cream"],
            fg=COLORS["coffee"],
        )
        self.subtitle_label.pack(pady=(2, 8))
        tk.Label(
            self.center_frame,
            text="─" * 44,
            font=("Segoe UI", 8),
            bg=COLORS["cream"],
            fg=COLORS["sand"],
        ).pack(pady=(0, 12))
        self.login_entry = ModernEntry(
            self.center_frame,
            outer_bg=COLORS["cream"],
            placeholder=tr("login", self.current_lang),
        )
        self.pass_entry = ModernEntry(
            self.center_frame,
            outer_bg=COLORS["cream"],
            placeholder=tr("password", self.current_lang),
            show="*",
        )
        self.error_label = tk.Label(
            self.center_frame,
            text="",
            font=("Segoe UI", 10),
            bg=COLORS["cream"],
            fg=COLORS["error"],
            height=1,
        )
        self.login_btn = ModernButton(
            self.center_frame,
            outer_bg=COLORS["cream"],
            text=tr("enter", self.current_lang),
            command=self.check_login,
        )
        self.lang_toggle = PillToggle(
            self.center_frame,
            ["uz", "ru", "tj"],
            self.current_lang,
            self._on_lang_change,
            outer_bg=COLORS["cream"],
        )
        self.footer_label = tk.Label(
            self.canvas,
            text="Cozy Cafe Edition • v2.0",
            font=("Segoe UI", 9),
            bg=COLORS["coffee_dark"],
            fg=COLORS["sand"],
        )
        self.footer_window = self.canvas.create_window(0, 0, window=self.footer_label)

        user = self.db.get_user()
        if user and self.db.get_setting("remember_login") == "1":
            # Faqat login eslab qolinadi. Parol endi hash holida saqlanadi
            # (xavfsizlik uchun), shuning uchun uni avtomatik to'ldirib
            # bo'lmaydi — bu aslida yaxshilanish: eski versiyada parol
            # oshkora matn holida maydonga solinardi.
            self.login_entry.insert(0, user["login"])

        self.root.after(50, self._draw_login_scene)
        self._animate_gradient_loop()
        self.root.after(400, self._start_login_sequence)

    def _start_fade_in(self):
        self._alpha = 0.0
        try:
            self.root.attributes("-alpha", 0.0)
            self._fade_step()
        except tk.TclError:
            pass

    def _fade_step(self):
        if self._alpha >= 1.0:
            return
        self._alpha = min(1.0, self._alpha + 0.06)
        try:
            self.root.attributes("-alpha", self._alpha)
            self.root.after(25, self._fade_step)
        except tk.TclError:
            pass

    def _draw_login_scene(self):
        if not hasattr(self, "canvas") or not self.canvas.winfo_exists():
            return
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 50 or h < 50:
            return
        self.canvas.delete("bg")
        t = (math.sin(self.gradient_step * 0.02) + 1) / 2
        r1, g1, b1 = 46, 28, 24
        r2, g2, b2 = 111, 78, 55
        steps = 40
        for i in range(steps):
            ratio = i / steps
            k = 0.6 + 0.4 * t
            r = int(r1 + (r2 - r1) * ratio * k)
            g = int(g1 + (g2 - g1) * ratio * k)
            b = int(b1 + (b2 - b1) * ratio * k)
            y1 = int(h * i / steps)
            y2 = int(h * (i + 1) / steps)
            self.canvas.create_rectangle(
                0, y1, w, y2, fill=f"#{r:02x}{g:02x}{b:02x}", outline="", tags="bg"
            )
        cw, ch = 520, 640
        x1, y1 = (w - cw) // 2, (h - ch) // 2
        x2, y2 = x1 + cw, y1 + ch
        round_rect(
            self.canvas,
            x1 + 8,
            y1 + 10,
            x2 + 8,
            y2 + 10,
            radius=30,
            fill="#1d120c",
            outline="",
            tags="bg",
        )
        round_rect(
            self.canvas,
            x1,
            y1,
            x2,
            y2,
            radius=30,
            fill=COLORS["cream"],
            outline="",
            tags="bg",
        )
        round_rect(
            self.canvas,
            x1 + 3,
            y1 + 3,
            x2 - 3,
            y2 - 3,
            radius=27,
            fill="",
            outline=COLORS["gold"],
            width=2,
            tags="bg",
        )
        self.canvas.coords(self.center_window, w // 2, h // 2)
        if hasattr(self, "footer_window"):
            self.canvas.coords(self.footer_window, w // 2, y2 + 22)

    def _animate_gradient_loop(self):
        if not hasattr(self, "canvas") or not self.canvas.winfo_exists():
            return
        self.gradient_step += 1
        self._draw_login_scene()
        self.root.after(120, self._animate_gradient_loop)

    def _start_login_sequence(self):
        if not hasattr(self, "logo_label") or not self.logo_label.winfo_exists():
            return
        self._logo_size = 10
        self._grow_logo()

    def _grow_logo(self):
        if not self.logo_label.winfo_exists():
            return
        if self._logo_size < 40:
            self._logo_size += 3
            self.logo_label.config(font=("Segoe UI", self._logo_size))
            self.root.after(30, self._grow_logo)
        else:
            self.typing_index = 0
            self.typing_text = tr("login_title", self.current_lang)
            self.subtitle_text = tr("ai_assistant", self.current_lang)
            self.type_title()

    def type_title(self):
        if not self.title_label.winfo_exists():
            return
        if self.typing_index <= len(self.typing_text):
            self.title_label.config(text=self.typing_text[: self.typing_index] + "▌")
            self.typing_index += 1
            self.root.after(70, self.type_title)
        else:
            self.title_label.config(text=self.typing_text)
            self.sub_index = 0
            self.type_sub()

    def type_sub(self):
        if not self.subtitle_label.winfo_exists():
            return
        if self.sub_index <= len(self.subtitle_text):
            self.subtitle_label.config(text=self.subtitle_text[: self.sub_index] + "▌")
            self.sub_index += 1
            self.root.after(40, self.type_sub)
        else:
            self.subtitle_label.config(text=self.subtitle_text)
            self._reveal_widgets()

    def _reveal_widgets(self):
        widgets = [
            self.login_entry,
            self.pass_entry,
            self.error_label,
            self.login_btn,
            self.lang_toggle,
        ]
        for i, wgt in enumerate(widgets):
            self.root.after(i * 130, lambda wg=wgt: self._reveal_one(wg))
        self.root.after(
            len(widgets) * 130 + 300,
            lambda: (
                self.login_btn.start_pulse() if self.login_btn.winfo_exists() else None
            ),
        )

    def _reveal_one(self, wgt):
        if wgt.winfo_exists():
            wgt.pack(pady=8)

    def _on_lang_change(self, lang):
        self.db.set_setting("language", lang)
        self.current_lang = lang
        self.show_login_screen()

    def check_login(self):
        login = self.login_entry.get().strip()
        password = self.pass_entry.get().strip()
        if not login or not password:
            self.show_error(tr("wrong_cred", self.current_lang))
            return
        user = self.db.check_login(login, password)
        if not user:
            self.show_error(tr("wrong_cred", self.current_lang))
            return
        self.show_loading()
        self.root.after(1200, self.show_pin_screen)

    def show_error(self, msg):
        self.error_label.config(text=msg)
        self._shake_card()

    def _shake_card(self):
        if not hasattr(self, "center_window"):
            return
        orig = self.canvas.coords(self.center_window)
        for i in range(6):
            off = 12 if i % 2 == 0 else -12
            self.root.after(
                i * 45,
                lambda o=off: self.canvas.coords(
                    self.center_window, orig[0] + o, orig[1]
                ),
            )
        self.root.after(
            300, lambda: self.canvas.coords(self.center_window, orig[0], orig[1])
        )

    def show_loading(self):
        for w in self.center_frame.winfo_children():
            w.destroy()
        self.loading_label = tk.Label(
            self.center_frame,
            text="◐",
            font=("Segoe UI", 44),
            bg=COLORS["cream"],
            fg=COLORS["caramel"],
        )
        self.loading_label.pack(pady=(200, 10))
        tk.Label(
            self.center_frame,
            text=tr("checking", self.current_lang),
            font=("Segoe UI", 12),
            bg=COLORS["cream"],
            fg=COLORS["coffee"],
        ).pack()
        self.spin_idx = 0
        self.spin_chars = "◐◓◑◒"
        self.spin_loading()

    def spin_loading(self):
        if not hasattr(self, "loading_label") or not self.loading_label.winfo_exists():
            return
        self.spin_idx = (self.spin_idx + 1) % len(self.spin_chars)
        try:
            self.loading_label.config(text=self.spin_chars[self.spin_idx])
            self.root.after(250, self.spin_loading)
        except tk.TclError:
            pass

    # ============== PIN EKRANI ==============
    def show_pin_screen(self):
        for w in self.center_frame.winfo_children():
            w.destroy()
        tk.Label(
            self.center_frame, text="🔐", font=("Segoe UI", 36), bg=COLORS["cream"]
        ).pack(pady=(40, 5))
        tk.Label(
            self.center_frame,
            text=tr("enter_pin", self.current_lang),
            font=("Segoe UI", 15, "bold"),
            bg=COLORS["cream"],
            fg=COLORS["coffee_dark"],
        ).pack(pady=(0, 15))
        self.pin_dots_frame = tk.Frame(self.center_frame, bg=COLORS["cream"])
        self.pin_dots_frame.pack(pady=10)
        self.pin_dots = []
        for i in range(4):
            d = tk.Label(
                self.pin_dots_frame,
                text="○",
                font=("Segoe UI", 30),
                bg=COLORS["cream"],
                fg=COLORS["sand"],
            )
            d.pack(side="left", padx=10)
            self.pin_dots.append(d)
        self.pin_error = tk.Label(
            self.center_frame,
            text="",
            font=("Segoe UI", 10),
            bg=COLORS["cream"],
            fg=COLORS["error"],
            height=1,
        )
        self.pin_error.pack(pady=5)
        self.pin_frame = tk.Frame(self.center_frame, bg=COLORS["cream"])
        self.pin_frame.pack(pady=15)
        self.pin_value = ""
        rows = [("1", "2", "3"), ("4", "5", "6"), ("7", "8", "9"), ("", "0", "⌫")]
        for row in rows:
            rf = tk.Frame(self.pin_frame, bg=COLORS["cream"])
            rf.pack(pady=4)
            for key in row:
                if key == "":
                    tk.Label(rf, text="", width=8, bg=COLORS["cream"]).pack(
                        side="left", padx=4
                    )
                else:
                    b = ModernButton(
                        rf,
                        outer_bg=COLORS["cream"],
                        text=key,
                        width=76,
                        height=52,
                        radius=26,
                        bg=COLORS["milk"],
                        hover_bg=COLORS["sand"],
                        active_bg=COLORS["caramel"],
                        fg=COLORS["coffee_dark"],
                        font=("Segoe UI", 14, "bold"),
                        command=lambda k=key: self.pin_press(k),
                    )
                    b.pack(side="left", padx=4)
        tk.Label(
            self.center_frame,
            text="Cozy Cafe Edition • v2.0",
            font=("Segoe UI", 8),
            bg=COLORS["cream"],
            fg=COLORS["sand"],
        ).pack(pady=(10, 8))

    def pin_press(self, btn):
        if btn == "⌫":
            if self.pin_value:
                self.pin_value = self.pin_value[:-1]
                self.update_pin_dots()
        else:
            if len(self.pin_value) < 4:
                self.pin_value += btn
                self.update_pin_dots()
                if len(self.pin_value) == 4:
                    self.root.after(300, self.check_pin)

    def update_pin_dots(self):
        for i, dot in enumerate(self.pin_dots):
            if i < len(self.pin_value):
                dot.config(text="●", fg=COLORS["caramel"])
            else:
                dot.config(text="○", fg=COLORS["sand"])

    def check_pin(self):
        if self.db.check_pin(self.pin_value):
            self.show_success()
            self.root.after(1500, self.show_dashboard)
        else:
            self.pin_error.config(text=tr("wrong_pin", self.current_lang))
            for d in self.pin_dots:
                d.config(fg=COLORS["error"], text="✕")
            self.pin_value = ""
            self.root.after(600, self._reset_pin_dots)

    def _reset_pin_dots(self):
        if hasattr(self, "pin_dots"):
            for d in self.pin_dots:
                if d.winfo_exists():
                    d.config(text="○", fg=COLORS["sand"])

    def show_success(self):
        for w in self.center_frame.winfo_children():
            w.destroy()
        self.success_label = tk.Label(
            self.center_frame,
            text="✓",
            font=("Segoe UI", 90, "bold"),
            bg=COLORS["cream"],
            fg=COLORS["success"],
        )
        self.success_label.pack(pady=(150, 20))
        tk.Label(
            self.center_frame,
            text=tr("welcome", self.current_lang) + "!",
            font=("Segoe UI", 18, "bold"),
            bg=COLORS["cream"],
            fg=COLORS["coffee_dark"],
        ).pack()
        self.start_confetti()

    def start_confetti(self):
        self.confetti_items = []
        colors = [
            COLORS["gold"],
            COLORS["caramel"],
            COLORS["success"],
            COLORS["sand"],
            "#ff6b9d",
            "#4ecdc4",
        ]
        w = self.canvas.winfo_width() or 1100
        for _ in range(60):
            x = random.randint(0, w)
            y = random.randint(-150, 0)
            color = random.choice(colors)
            size = random.randint(4, 9)
            item = self.canvas.create_oval(
                x, y, x + size, y + size, fill=color, outline=""
            )
            self.confetti_items.append((item, random.uniform(3, 8)))
        self.animate_confetti()

    def animate_confetti(self):
        if not hasattr(self, "canvas") or not self.canvas.winfo_exists():
            self.confetti_items = []
            return
        if not self.confetti_items:
            return
        new_items = []
        for item, speed in self.confetti_items:
            try:
                coords = self.canvas.coords(item)
                if coords:
                    self.canvas.move(item, random.uniform(-2, 2), speed)
                    if coords[1] > 750:
                        self.canvas.delete(item)
                    else:
                        new_items.append((item, speed))
            except tk.TclError:
                pass
        self.confetti_items = new_items
        if self.confetti_items:
            self.root.after(30, self.animate_confetti)

    # ============== DASHBOARD (ZAMONAVIY) ==============
    def show_dashboard(self, menu_key="dashboard"):
        for w in self.root.winfo_children():
            w.destroy()
        self.active_menu = menu_key

        # YUQORI PANEL
        top = tk.Frame(self.root, bg=COLORS["coffee_dark"], height=60)
        top.pack(fill="x")
        top.pack_propagate(False)
        user = self.db.get_user()
        uname = user["name"] if user else ""
        tk.Label(
            top,
            text=f"☕ {tr('welcome', self.current_lang)}, {uname}!",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["coffee_dark"],
            fg=COLORS["cream"],
        ).pack(side="left", padx=20)
        self.dash_lang_toggle = PillToggle(
            top,
            ["uz", "ru", "tj"],
            self.current_lang,
            self._on_dash_lang_change,
            outer_bg=COLORS["coffee_dark"],
            active_bg=COLORS["gold"],
            active_fg=COLORS["coffee_dark"],
            inactive_fg=COLORS["cream"],
        )
        self.dash_lang_toggle.pack(side="right", padx=10)
        self.clock_label = tk.Label(
            top,
            text="",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["coffee_dark"],
            fg=COLORS["gold"],
        )
        self.clock_label.pack(side="right", padx=15)
        self._tick_clock()
        logout_btn = tk.Canvas(
            top,
            width=100,
            height=40,
            highlightthickness=0,
            bg=COLORS["coffee_dark"],
            cursor="hand2",
        )
        logout_btn.pack(side="right", padx=5)
        logout_btn.bind("<Configure>", lambda e, b=logout_btn: self._draw_logout_btn(b))
        logout_btn.bind(
            "<Enter>", lambda e, b=logout_btn: self._draw_logout_btn(b, hover=True)
        )
        logout_btn.bind("<Leave>", lambda e, b=logout_btn: self._draw_logout_btn(b))
        logout_btn.bind("<Button-1>", lambda e: self.logout())

        # ===== SCROLLABLE SIDEBAR =====
        sidebar_outer = tk.Frame(self.root, bg=COLORS["coffee"], width=240)
        sidebar_outer.pack(side="left", fill="y")
        sidebar_outer.pack_propagate(False)

        sb_canvas = tk.Canvas(sidebar_outer, bg=COLORS["coffee"], highlightthickness=0)
        sb_scroll = ttk.Scrollbar(
            sidebar_outer, orient="vertical", command=sb_canvas.yview
        )
        sb_inner = tk.Frame(sb_canvas, bg=COLORS["coffee"])
        sb_inner.bind(
            "<Configure>",
            lambda e: sb_canvas.configure(scrollregion=sb_canvas.bbox("all")),
        )
        sb_win = sb_canvas.create_window((0, 0), window=sb_inner, anchor="nw")
        sb_canvas.bind(
            "<Configure>", lambda e: sb_canvas.itemconfig(sb_win, width=e.width)
        )
        sb_canvas.configure(yscrollcommand=sb_scroll.set)
        sb_canvas.pack(side="left", fill="both", expand=True)
        sb_scroll.pack(side="right", fill="y")

        def _sb_wheel(event):
            if sb_canvas.winfo_exists():
                sb_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        sb_canvas.bind("<MouseWheel>", _sb_wheel)
        sb_inner.bind("<MouseWheel>", _sb_wheel)

        # Sidebar logo
        logo_frame = tk.Frame(sb_inner, bg=COLORS["coffee_dark"], height=80)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)
        tk.Label(
            logo_frame,
            text="☕ Cozy",
            font=("Segoe UI", 20, "bold"),
            bg=COLORS["coffee_dark"],
            fg=COLORS["gold"],
        ).pack(expand=True)
        tk.Frame(sb_inner, bg=COLORS["caramel"], height=2).pack(fill="x", pady=(0, 10))

        # Menu items
        self.menu_buttons = {}
        menu_items = [
            ("🏠", "dashboard", self.show_dashboard),
            ("📅", "calendar", self.show_calendar),
            ("📚", "subjects", self.show_subjects),
            ("👥", "friends", self.show_friends),
            ("🎯", "goals", self.show_goals),
            ("💰", "budget", self.show_budget),
            # ("⏱️", "time_master", self.show_pomodoro),
            ("📝", "journal", self.show_journal),
            ("⚙️", "settings", self.show_settings),
        ]
        for icon, key, cmd in menu_items:
            self._add_menu_item(sb_inner, icon, key, cmd)

        # Progress (ENDI ODDIY PACK, bottom emas!)
        self._add_sidebar_progress(sb_inner)

        # ASOSIY KONTENT
        self.content = tk.Frame(self.root, bg=COLORS["milk"])
        self.content.pack(side="right", fill="both", expand=True)
        self.build_dashboard()

    def _draw_logout_btn(self, btn, hover=False):
        w, h = btn.winfo_width(), btn.winfo_height()
        if w < 20:
            w = 100
        btn.delete("all")
        color = COLORS["error"] if hover else COLORS["caramel"]
        round_rect(btn, 0, 0, w - 1, h - 1, radius=20, fill=color, outline="")
        btn.create_text(
            w / 2,
            h / 2,
            text=f"↩ {tr('logout', self.current_lang)}",
            fill=COLORS["cream"],
            font=("Segoe UI", 10, "bold"),
        )

    def _add_menu_item(self, parent, icon, key, cmd):
        frame = tk.Frame(parent, bg=COLORS["coffee"], height=48, cursor="hand2")
        frame.pack(fill="x", pady=2, padx=10)
        frame.pack_propagate(False)

        # Aktivlik indikatori (chap chiziq)
        indicator = tk.Frame(frame, bg=COLORS["gold"], width=4)
        indicator.pack(side="left", fill="y")
        indicator.pack_propagate(False)

        # Ikonka
        icon_lbl = tk.Label(
            frame,
            text=icon,
            font=("Segoe UI", 16),
            bg=COLORS["coffee"],
            fg=COLORS["cream"],
        )
        icon_lbl.pack(side="left", padx=(15, 10))

        # Matn
        text_lbl = tk.Label(
            frame,
            text=tr(key, self.current_lang),
            font=("Segoe UI", 11, "bold" if key == self.active_menu else "normal"),
            bg=COLORS["coffee"],
            fg=COLORS["gold"] if key == self.active_menu else COLORS["cream"],
        )
        text_lbl.pack(side="left", fill="x", expand=True, anchor="w")

        # Hover va aktivlik
        def on_enter(e):
            if key != self.active_menu:
                frame.config(bg=COLORS["caramel"])
                icon_lbl.config(bg=COLORS["caramel"])
                text_lbl.config(bg=COLORS["caramel"])

        def on_leave(e):
            if key != self.active_menu:
                frame.config(bg=COLORS["coffee"])
                icon_lbl.config(bg=COLORS["coffee"])
                text_lbl.config(bg=COLORS["coffee"])

        def on_click(e):
            cmd()

        for wgt in [frame, icon_lbl, text_lbl]:
            wgt.bind("<Enter>", on_enter)
            wgt.bind("<Leave>", on_leave)
            wgt.bind("<Button-1>", on_click)

        # Aktiv tugma
        if key == self.active_menu:
            indicator.config(bg=COLORS["gold"])
            frame.config(bg=COLORS["caramel"])
            icon_lbl.config(bg=COLORS["caramel"])
            text_lbl.config(bg=COLORS["caramel"], fg=COLORS["gold"])

        self.menu_buttons[key] = frame

    def _tick_clock(self):
        if hasattr(self, "clock_label") and self.clock_label.winfo_exists():
            now = datetime.now()
            time_str = f"{now.hour:02d}:{now.minute:02d}:{now.second:02d}"
            self.clock_label.config(text=f"⏰ {time_str}")
        self.root.after(1000, self._tick_clock)

    def _on_dash_lang_change(self, lang):
        self.db.set_setting("language", lang)
        self.current_lang = lang
        self.show_dashboard(self.active_menu)

    def build_dashboard(self):
        for w in self.content.winfo_children():
            w.destroy()

        canvas = tk.Canvas(self.content, bg=COLORS["milk"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=COLORS["milk"])
        self.dash_window = canvas.create_window(
            (0, 0), window=scroll_frame, anchor="nw"
        )

        def _on_conf(event):
            canvas.itemconfig(self.dash_window, width=event.width)
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<Configure>", _on_conf)
        scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _mw(event):
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _mw)

        # Ketma-ket yuklash
        self._dash_queue = [
            lambda: self._build_motivation(scroll_frame),
            lambda: self._build_ai(scroll_frame),
            lambda: self._build_quick_actions(scroll_frame),
            lambda: self._build_stats(scroll_frame),
            lambda: self._build_week_chart(scroll_frame),
            lambda: self._build_tasks(scroll_frame),
            lambda: self._build_birthdays(scroll_frame),
        ]
        self._dash_idx = 0
        self._run_dash_queue()

    def _run_dash_queue(self):
        if self._dash_idx < len(self._dash_queue):
            fn = self._dash_queue[self._dash_idx]
            self._dash_idx += 1
            fn()
            self.root.after(130, self._run_dash_queue)

    # ----- MOTIVATSIYA (YUQORIDA) -----
    def _daily_motivation(self):
        quotes = tr("ai_motivation", self.current_lang)
        return quotes[date.today().toordinal() % len(quotes)]

    def _build_motivation(self, parent):
        banner = tk.Canvas(parent, height=130, highlightthickness=0, bg=COLORS["milk"])
        banner.pack(fill="x", padx=15, pady=(15, 8))
        self.mot_banner = banner
        self.mot_step = 0
        self.mot_quote = self._daily_motivation()
        self.mot_text_item = banner.create_text(
            34,
            62,
            text="",
            anchor="w",
            font=("Segoe UI", 16, "bold italic"),
            fill=COLORS["cream"],
        )
        banner.create_text(
            34,
            98,
            text="✨ " + date.today().strftime("%d.%m.%Y"),
            anchor="w",
            font=("Segoe UI", 10),
            fill=COLORS["sand"],
        )
        banner.bind("<Configure>", lambda e: self._mot_draw())
        self._mot_draw()
        self._mot_loop()
        self._mot_type(0)

    def _mot_draw(self):
        b = self.mot_banner
        if not b.winfo_exists():
            return
        w, h = b.winfo_width(), b.winfo_height()
        if w < 20:
            return
        b.delete("bg")
        t = (math.sin(self.mot_step * 0.03) + 1) / 2
        c1 = (139, 69, 19)
        c2 = (212, 160, 23)
        steps = 30
        for i in range(steps):
            r = i / steps
            k = 0.5 + 0.5 * t
            cr = int(c1[0] + (c2[0] - c1[0]) * r * k)
            cg = int(c1[1] + (c2[1] - c1[1]) * r * k)
            cb = int(c1[2] + (c2[2] - c1[2]) * r * k)
            x1 = int(w * i / steps)
            x2 = int(w * (i + 1) / steps)
            b.create_rectangle(
                x1, 0, x2, h, fill=f"#{cr:02x}{cg:02x}{cb:02x}", outline="", tags="bg"
            )
        round_rect(
            b,
            2,
            2,
            w - 3,
            h - 3,
            radius=22,
            fill="",
            outline=COLORS["gold"],
            width=2,
            tags="bg",
        )
        b.tag_lower("bg")

    def _mot_loop(self):
        if not hasattr(self, "mot_banner") or not self.mot_banner.winfo_exists():
            return
        self.mot_step += 1
        self._mot_draw()
        self.root.after(140, self._mot_loop)

    def _mot_type(self, i):
        if not hasattr(self, "mot_banner") or not self.mot_banner.winfo_exists():
            return
        if i <= len(self.mot_quote):
            self.mot_banner.itemconfig(
                self.mot_text_item, text="❝ " + self.mot_quote[:i] + "▌"
            )
            self.root.after(35, lambda: self._mot_type(i + 1))
        else:
            self.mot_banner.itemconfig(
                self.mot_text_item, text="❝ " + self.mot_quote + " ❞"
            )

    # ----- JONLI AI KARTA -----
    def _build_ai(self, parent):
        card = RoundedCard(
            parent,
            title=f"🧠 {tr('ai_assistant', self.current_lang)}",
            header_bg=COLORS["coffee"],
            live=True,
        )
        card.pack(fill="x", padx=15, pady=8)
        msgs = self.generate_ai_messages()
        for i, msg in enumerate(msgs):
            lbl = tk.Label(
                card.inner,
                text=msg,
                font=("Segoe UI", 11),
                bg=COLORS["cream"],
                fg=COLORS["coffee_dark"],
                wraplength=760,
                justify="left",
                anchor="w",
            )
            self.root.after(
                200 + i * 180,
                lambda l=lbl: (
                    l.pack(fill="x", pady=4, padx=14) if l.winfo_exists() else None
                ),
            )
        if not msgs:
            tk.Label(card.inner, text="...", bg=COLORS["cream"]).pack(pady=10)

    # ----- STATISTIKA (COUNT-UP) -----
    def _build_stats(self, parent):
        frame = tk.Frame(parent, bg=COLORS["milk"])
        frame.pack(fill="x", padx=15, pady=8)
        stats = [
            ("📚", len(self.db.get_subjects()), tr("subjects", self.current_lang)),
            ("👥", len(self.db.get_friends()), tr("friends", self.current_lang)),
            (
                "✅",
                len(self.db.get_tasks(completed=1)),
                tr("completed", self.current_lang),
            ),
            ("⭐", self.db.get_points(), "Ball"),
        ]
        for i, (icon, value, label) in enumerate(stats):
            tile = self._stat_tile(frame, icon, value, label)
            tile.grid(row=0, column=i, padx=6, sticky="nsew")
            frame.grid_columnconfigure(i, weight=1)

    def _stat_tile(self, parent, icon, value, label):
        tile = tk.Canvas(
            parent, height=120, highlightthickness=0, bg=COLORS["milk"], cursor="hand2"
        )
        tile._shown_value = 0
        tile.bind(
            "<Configure>",
            lambda e, t=tile, ic=icon, lb=label: self._tile_draw(t, ic, lb),
        )
        tile.bind(
            "<Enter>",
            lambda e, t=tile, ic=icon, lb=label: self._tile_draw(t, ic, lb, True),
        )
        tile.bind(
            "<Leave>",
            lambda e, t=tile, ic=icon, lb=label: self._tile_draw(t, ic, lb, False),
        )
        self._tile_draw(tile, icon, label)
        self._count_up(tile, value)
        return tile

    def _tile_draw(self, tile, icon, label, hover=False):
        w, h = tile.winfo_width(), tile.winfo_height()
        if w < 20:
            w = 180
        tile.delete("all")
        if hover:
            round_rect(tile, 3, 5, w - 1, h - 1, radius=18, fill="#d9c3a5", outline="")
            round_rect(
                tile,
                0,
                0,
                w - 4,
                h - 6,
                radius=18,
                fill=COLORS["cream"],
                outline=COLORS["gold"],
                width=2,
            )
        else:
            round_rect(
                tile, 0, 0, w - 1, h - 1, radius=18, fill=COLORS["cream"], outline=""
            )
            round_rect(
                tile,
                2,
                2,
                w - 3,
                h - 3,
                radius=16,
                fill="",
                outline=COLORS["sand"],
                width=1,
            )
        off = -2 if hover else 0
        tile.create_text(w / 2 - 1, 28 + off, text=icon, font=("Segoe UI", 22))
        num = tile.create_text(
            w / 2 - 1,
            66 + off,
            text=str(tile._shown_value),
            font=("Segoe UI", 24, "bold"),
            fill=COLORS["coffee_dark"],
        )
        tile.create_text(
            w / 2 - 1,
            98 + off,
            text=label,
            font=("Segoe UI", 10),
            fill=COLORS["coffee"],
        )
        tile._num_item = num

    def _count_up(self, tile, target):
        steps = 18

        def tick(i):
            if not tile.winfo_exists() or tile._num_item is None:
                return
            val = int(target * i / steps)
            tile._shown_value = val
            try:
                tile.itemconfig(tile._num_item, text=str(val))
            except tk.TclError:
                return
            if i < steps:
                self.root.after(45, lambda: tick(i + 1))

        tick(0)

    # ----- VAZIFALAR -----
    def _build_tasks(self, parent):
        self.tasks_holder = tk.Frame(parent, bg=COLORS["milk"])
        self.tasks_holder.pack(fill="x", padx=15, pady=8)
        self._fill_tasks()

    def _fill_tasks(self):
        for w in self.tasks_holder.winfo_children():
            w.destroy()
        card = RoundedCard(
            self.tasks_holder,
            title=f"📅 {tr('today_tasks', self.current_lang)}",
            header_bg=COLORS["caramel"],
        )
        card.pack(fill="x")
        tasks = self.db.get_today_tasks()
        if not tasks:
            empty = tk.Frame(card.inner, bg=COLORS["cream"])
            empty.pack(fill="x", pady=18)
            tk.Label(empty, text="🌤️", font=("Segoe UI", 30), bg=COLORS["cream"]).pack()
            tk.Label(
                empty,
                text=tr("no_tasks", self.current_lang),
                font=("Segoe UI", 11),
                bg=COLORS["cream"],
                fg=COLORS["coffee"],
            ).pack(pady=(5, 0))
            return
        for task in tasks:
            self._task_row(card.inner, task)

    def _task_row(self, inner, task):
        row = tk.Frame(inner, bg=COLORS["milk"], padx=10, pady=8)
        row.pack(fill="x", pady=3, padx=10)
        is_done = task["completed"] == 1
        chk = tk.Button(
            row,
            text="✓" if is_done else "○",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["success"] if is_done else COLORS["cream"],
            fg=COLORS["cream"] if is_done else COLORS["sand"],
            relief="flat",
            cursor="hand2",
            width=2,
            command=lambda t=task: self._toggle_task(t),
        )
        chk.pack(side="left", padx=(0, 10))
        if task["due_time"]:
            tk.Label(
                row,
                text=f"⏰ {task['due_time']}",
                font=("Segoe UI", 10, "bold"),
                bg=COLORS["sand"],
                fg=COLORS["coffee_dark"],
                padx=8,
                pady=2,
            ).pack(side="left", padx=(0, 10))
        title_lbl = tk.Label(
            row,
            text=task["title"],
            font=("Segoe UI", 11, "bold" if not is_done else "normal"),
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
            row,
            text=f"#{task['category']}",
            font=("Segoe UI", 9),
            bg=cat_colors.get(task["category"], COLORS["sand"]),
            fg=COLORS["cream"],
            padx=8,
            pady=2,
        ).pack(side="left", padx=5)
        tk.Button(
            row,
            text="🗑",
            font=("Segoe UI", 10),
            bg=COLORS["milk"],
            fg=COLORS["error"],
            relief="flat",
            cursor="hand2",
            command=lambda t=task: self._del_task(t),
        ).pack(side="right")

        # HOVER effekti
        def _enter(e):
            row.config(bg=COLORS["cream"])
            title_lbl.config(bg=COLORS["cream"])

        def _leave(e):
            row.config(bg=COLORS["milk"])
            title_lbl.config(bg=COLORS["milk"])

        for wgt in [row, chk, title_lbl]:
            wgt.bind("<Enter>", _enter)
            wgt.bind("<Leave>", _leave)

    def _toggle_task(self, task):
        if task["completed"] == 1:
            self.db.uncomplete_task(task["id"])
        else:
            self.db.complete_task(task["id"])
            self.db.add_points(10, f"Vazifa bajarildi: {task['title']}")
        self._fill_tasks()

    def _del_task(self, task):
        self.db.delete_task(task["id"])
        self._fill_tasks()

    # ----- TUG'ILGAN KUNLAR (FAQAT BOR BO'LSA) -----
    def _build_birthdays(self, parent):
        birthdays = self.db.get_upcoming_birthdays(7)
        if not birthdays:
            return
        card = RoundedCard(
            parent,
            title=f"🎂 {tr('upcoming_bdays', self.current_lang)}",
            header_bg=COLORS["gold"],
        )
        card.pack(fill="x", padx=15, pady=8)
        for friend, days in birthdays:
            row = tk.Frame(card.inner, bg=COLORS["cream"], padx=12, pady=8)
            row.pack(fill="x", pady=3, padx=10)
            tk.Label(
                row,
                text="🎉" if days == 0 else "🎂",
                font=("Segoe UI", 18),
                bg=COLORS["cream"],
            ).pack(side="left", padx=(0, 10))
            if days == 0:
                txt = f"{friend['name']} — {tr('today_birthday', self.current_lang)}"
            else:
                txt = f"{friend['name']} — {days} {tr('days_left', self.current_lang)}"
            tk.Label(
                row,
                text=txt,
                font=("Segoe UI", 11, "bold"),
                bg=COLORS["cream"],
                fg=COLORS["coffee_dark"],
            ).pack(side="left")

        # ============== TEZKOR AMALLAR ==============

    def _build_quick_actions(self, parent):
        frame = tk.Frame(parent, bg=COLORS["milk"])
        frame.pack(fill="x", padx=15, pady=8)
        actions = [
            ("+", "Vazifa", self._quick_add_task, COLORS["success"]),
            ("$", "Xarajat", self._quick_add_expense, COLORS["gold"]),
            # ("▶", "Fokus", self.show_pomodoro, COLORS["error"]),
            ("✎", "Kunlik", self.show_journal, COLORS["caramel"]),
        ]
        for i, (icon, label, cmd, accent) in enumerate(actions):
            btn = self._action_btn(frame, icon, label, cmd, accent)
            btn.grid(row=0, column=i, padx=6, sticky="nsew")
            frame.grid_columnconfigure(i, weight=1)

    def _action_btn(self, parent, icon, label, cmd, accent):
        btn = tk.Canvas(
            parent, height=74, highlightthickness=0, bg=COLORS["milk"], cursor="hand2"
        )
        btn.bind(
            "<Configure>",
            lambda e, b=btn, ic=icon, lb=label, ac=accent: self._action_draw(
                b, ic, lb, False, ac
            ),
        )
        btn.bind(
            "<Enter>",
            lambda e, b=btn, ic=icon, lb=label, ac=accent: self._action_draw(
                b, ic, lb, True, ac
            ),
        )
        btn.bind(
            "<Leave>",
            lambda e, b=btn, ic=icon, lb=label, ac=accent: self._action_draw(
                b, ic, lb, False, ac
            ),
        )
        btn.bind("<Button-1>", lambda e: cmd())
        self._action_draw(btn, icon, label, False, accent)
        return btn

    def _action_draw(self, btn, icon, label, hover, accent):
        w, h = btn.winfo_width(), btn.winfo_height()
        if w < 20:
            w = 160
        btn.delete("all")
        # Kartochka foni
        if hover:
            round_rect(btn, 3, 5, w - 1, h - 1, radius=16, fill="#d9c3a5", outline="")
            round_rect(
                btn,
                0,
                0,
                w - 4,
                h - 6,
                radius=16,
                fill=COLORS["cream"],
                outline=accent,
                width=2,
            )
        else:
            round_rect(
                btn,
                0,
                0,
                w - 1,
                h - 1,
                radius=16,
                fill=COLORS["cream"],
                outline=COLORS["sand"],
                width=1,
            )
        # Chapda rangli doira + ikonka
        cx, cy, r = 34, h / 2 - 2, 17
        btn.create_oval(cx - r, cy - r, cx + r, cy + r, fill=accent, outline="")
        btn.create_text(
            cx, cy, text=icon, font=("Segoe UI", 16, "bold"), fill=COLORS["cream"]
        )
        # O'ngda matn
        btn.create_text(
            cx + r + 12,
            cy,
            text=label,
            anchor="w",
            font=("Segoe UI", 11, "bold"),
            fill=COLORS["coffee_dark"],
        )

    def _quick_add_task(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("+ " + tr("add", self.current_lang))
        dialog.configure(bg=COLORS["cream"])
        dialog.transient(self.root)
        dialog.resizable(False, False)
        dialog.grab_set()
        tk.Label(
            dialog,
            text="📝 " + tr("add", self.current_lang),
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

        lbl(tr("task_title", self.current_lang))
        title_e = ModernEntry(
            f, outer_bg=COLORS["cream"], placeholder="Masalan: Matematika uy vazifasi"
        )
        title_e.pack(fill="x")
        title_e.focus()
        lbl(tr("task_desc", self.current_lang))
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
        lbl(tr("task_date", self.current_lang) + " (YYYY-MM-DD)")
        date_e = ModernEntry(
            f, outer_bg=COLORS["cream"], placeholder=date.today().isoformat()
        )
        date_e.pack(fill="x")
        date_e.insert(0, date.today().isoformat())
        lbl(tr("task_time", self.current_lang) + " (HH:MM)")
        time_e = ModernEntry(f, outer_bg=COLORS["cream"], placeholder="18:00")
        time_e.pack(fill="x")
        lbl(tr("task_category", self.current_lang))
        cat_opts = [
            ("dars", "📚 Dars", COLORS["caramel"]),
            ("shaxsiy", "👤 Shaxsiy", COLORS["gold"]),
            ("do'st", "🤝 Do'st", COLORS["success"]),
        ]
        cat_g = ChipGroup(f, cat_opts, "shaxsiy", outer_bg=COLORS["cream"])
        cat_g.pack(fill="x", pady=(2, 4))
        lbl(tr("task_priority", self.current_lang))
        prio_opts = [
            (1, "⬇ Past", COLORS["sand"]),
            (2, "⬆ O'rtacha", COLORS["gold"]),
            (3, "🔥 Yuqori", COLORS["error"]),
        ]
        prio_g = ChipGroup(f, prio_opts, 1, outer_bg=COLORS["cream"])
        prio_g.pack(fill="x", pady=(2, 4))

        def save():
            t = title_e.get().strip()
            if not t:
                messagebox.showerror(
                    tr("error", self.current_lang), "Sarlavha kiriting!", parent=dialog
                )
                return
            dd = date_e.get().strip() or date.today().isoformat()
            try:
                date.fromisoformat(dd)
            except Exception:
                messagebox.showerror(
                    tr("error", self.current_lang),
                    "Sana YYYY-MM-DD formatida bo'lsin!",
                    parent=dialog,
                )
                return
            self.db.add_task(
                t,
                desc_t.get("1.0", "end").strip(),
                dd,
                time_e.get().strip(),
                cat_g.get(),
                prio_g.get(),
            )
            dialog.destroy()
            self.build_dashboard()

        ModernButton(
            dialog,
            outer_bg=COLORS["cream"],
            text=tr("save", self.current_lang),
            command=save,
        ).pack(pady=16)
        dialog.update_idletasks()
        req_h = dialog.winfo_reqheight()
        dialog.geometry(f"440x{max(req_h, 520)}")

    def _quick_add_expense(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("+ " + tr("add", self.current_lang))
        dialog.configure(bg=COLORS["cream"])
        dialog.transient(self.root)
        dialog.resizable(False, False)
        dialog.grab_set()
        tk.Label(
            dialog,
            text="💸 " + tr("expense", self.current_lang),
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

        lbl(tr("amount", self.current_lang) + " (so'm)")
        amount_e = ModernEntry(f, outer_bg=COLORS["cream"], placeholder="15000")
        amount_e.pack(fill="x")
        amount_e.focus()
        lbl(tr("category", self.current_lang))
        cat_opts = [
            ("Oziq-ovqat", "🍞 Ovqat", COLORS["success"]),
            ("Transport", "🚌 Transport", COLORS["caramel"]),
            ("Kiyim", "👕 Kiyim", COLORS["gold"]),
            ("Ko'ngilochar", "🎮 Ko'ngilochar", COLORS["coffee"]),
            ("Salomatlik", "💊 Salomatlik", COLORS["error"]),
            ("Boshqa", "📦 Boshqa", COLORS["sand"]),
        ]
        cat_g = ChipGroup(f, cat_opts, "Oziq-ovqat", outer_bg=COLORS["cream"])
        cat_g.pack(fill="x", pady=(2, 4))
        lbl(tr("description", self.current_lang))
        desc_e = ModernEntry(f, outer_bg=COLORS["cream"], placeholder="Kofe va non")
        desc_e.pack(fill="x")

        def save():
            try:
                amount = float(amount_e.get().replace(",", "").replace(" ", ""))
            except ValueError:
                messagebox.showerror(
                    tr("error", self.current_lang),
                    "To'g'ri summa kiriting!",
                    parent=dialog,
                )
                return
            self.db.add_expense(amount, cat_g.get(), desc_e.get().strip())
            dialog.destroy()
            self.build_dashboard()

        ModernButton(
            dialog,
            outer_bg=COLORS["cream"],
            text=tr("save", self.current_lang),
            command=save,
        ).pack(pady=16)
        dialog.update_idletasks()
        req_h = dialog.winfo_reqheight()
        dialog.geometry(f"440x{max(req_h, 520)}")

    # ============== HAFTALIK GRAFIK ==============
    def _build_week_chart(self, parent):
        card = RoundedCard(
            parent, title="📊 Haftalik aktivlik", header_bg=COLORS["coffee"]
        )
        card.pack(fill="x", padx=15, pady=8)
        chart = tk.Canvas(
            card.inner, height=150, bg=COLORS["cream"], highlightthickness=0
        )
        chart.pack(fill="x", padx=10, pady=(5, 10))
        self._week_chart = chart
        chart.bind("<Configure>", lambda e: self._animate_week_chart())
        self.root.after(150, self._animate_week_chart)

    def _week_data(self):
        names = {
            "uz": ["Du", "Se", "Cho", "Pa", "Ju", "Sha", "Ya"],
            "ru": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
            "tj": ["Дш", "Сш", "Чш", "Пш", "Ҷм", "Шб", "Яш"],
        }
        data = []
        today = date.today()
        monday = today - timedelta(days=today.weekday())  # Hafta boshi
        for i in range(7):
            d = monday + timedelta(days=i)
            self.db.cursor.execute(
                "SELECT COUNT(*) as c FROM tasks WHERE completed=1 AND due_date=?",
                (d.isoformat(),),
            )
            c = self.db.cursor.fetchone()["c"]
            data.append((names[self.current_lang][i], c, d))
        return data

    def _animate_week_chart(self, p=0.0):
        if not hasattr(self, "_week_chart"):
            return
        if p <= 1.0:
            self._draw_week_chart(p)
            self.root.after(30, lambda: self._animate_week_chart(p + 0.12))

    def _draw_week_chart(self, progress=1.0):
        ch = getattr(self, "_week_chart", None)
        if ch is None or not ch.winfo_exists():
            return
        w, h = ch.winfo_width(), ch.winfo_height()
        if w < 50:
            return
        ch.delete("all")
        data = self._week_data()
        maxv = max([c for _, c, _ in data] + [1])
        bw = w / 7
        for i, (name, c, d) in enumerate(data):
            x1 = i * bw + bw * 0.28
            x2 = i * bw + bw * 0.72
            y2 = h - 25
            bh = (h - 45) * (c / maxv) * progress
            is_today = d == date.today()
            color = COLORS["caramel"] if is_today else COLORS["sand"]
            if c > 0 and bh > 2:
                round_rect(ch, x1, y2 - bh, x2, y2, radius=6, fill=color, outline="")
                ch.create_text(
                    (x1 + x2) / 2,
                    y2 - bh - 10,
                    text=str(c),
                    font=("Segoe UI", 9, "bold"),
                    fill=COLORS["coffee_dark"],
                )
            else:
                round_rect(
                    ch, x1, y2 - 4, x2, y2, radius=2, fill=COLORS["milk"], outline=""
                )
            ch.create_text(
                (x1 + x2) / 2,
                h - 10,
                text=name,
                font=("Segoe UI", 9, "bold" if is_today else "normal"),
                fill=COLORS["caramel"] if is_today else COLORS["coffee"],
            )

    # ============== SIDEBAR PROGRESS ==============
    def _add_sidebar_progress(self, sidebar):
        holder = tk.Frame(sidebar, bg=COLORS["coffee"])
        holder.pack(fill="x", padx=10, pady=(15, 10))  # ← side="bottom" OLIB TASHLANDI
        card = tk.Frame(holder, bg=COLORS["coffee_dark"])
        card.pack(fill="x")
        prog = tk.Canvas(
            card, height=90, bg=COLORS["coffee_dark"], highlightthickness=0
        )
        prog.pack(fill="x")
        self._sidebar_prog = prog
        prog.bind("<Configure>", lambda e: self._draw_sidebar_progress())
        self._draw_sidebar_progress()

    def _draw_sidebar_progress(self):
        c = getattr(self, "_sidebar_prog", None)
        if c is None or not c.winfo_exists():
            returnfА
        w, h = c.winfo_width(), c.winfo_height()
        if w < 60:
            return
        c.delete("all")
        t = date.today().isoformat()
        self.db.cursor.execute(
            "SELECT COUNT(*) as total, SUM(completed) as done FROM tasks WHERE due_date=?",
            (t,),
        )
        row = self.db.cursor.fetchone()
        total = row["total"] or 0
        done = row["done"] or 0
        pct = (done / total) if total else 0
        cx, cy, r = 48, h / 2, 27
        c.create_oval(cx - r, cy - r, cx + r, cy + r, outline=COLORS["coffee"], width=6)
        if pct > 0:
            c.create_arc(
                cx - r,
                cy - r,
                cx + r,
                cy + r,
                start=90,
                extent=-360 * pct,
                style="arc",
                outline=COLORS["gold"],
                width=6,
            )
        c.create_text(
            cx,
            cy,
            text=f"{int(pct * 100)}%",
            font=("Segoe UI", 10, "bold"),
            fill=COLORS["cream"],
        )
        points = self.db.get_points()
        level = points // 100 + 1
        c.create_text(
            cx + r + 14,
            cy - 14,
            text=f"Bugun: {done}/{total}",
            anchor="w",
            font=("Segoe UI", 10),
            fill=COLORS["cream"],
        )
        c.create_text(
            cx + r + 14,
            cy + 10,
            text=f"⭐ Daraja {level}",
            anchor="w",
            font=("Segoe UI", 10, "bold"),
            fill=COLORS["gold"],
        )

    # ============== KAYFIYAT TEZ PANEL ==============
    def _build_mood_quick(self, parent):
        today_mood = self.db.get_today_mood()
        card = RoundedCard(
            parent,
            title="😊 " + tr("how_mood", self.current_lang),
            header_bg=COLORS["sand"],
            header_fg=COLORS["coffee_dark"],
        )
        card.pack(fill="x", padx=15, pady=8)
        row = tk.Frame(card.inner, bg=COLORS["cream"])
        row.pack(pady=10)
        moods = [("😄", 5), ("🙂", 4), ("😐", 3), ("😕", 2), ("😢", 1)]
        for emoji, val in moods:
            is_sel = bool(today_mood) and today_mood["mood"] == val
            b = tk.Label(
                row,
                text=emoji,
                font=("Segoe UI", 26),
                bg=COLORS["gold"] if is_sel else COLORS["cream"],
                padx=10,
                pady=4,
                cursor="hand2",
            )
            b.pack(side="left", padx=6)
            b.bind("<Button-1>", lambda e, v=val: self._set_quick_mood(v))
            b.bind(
                "<Enter>",
                lambda e, bb=b, s=is_sel: bb.config(
                    bg=COLORS["gold"] if s else COLORS["sand"]
                ),
            )
            b.bind(
                "<Leave>",
                lambda e, bb=b, s=is_sel: bb.config(
                    bg=COLORS["gold"] if s else COLORS["cream"]
                ),
            )
        if today_mood:
            tk.Label(
                card.inner,
                text="✅ Bugungi kayfiyat belgilandi",
                font=("Segoe UI", 9),
                bg=COLORS["cream"],
                fg=COLORS["success"],
            ).pack(pady=(0, 8))

    def _set_quick_mood(self, val):
        today_mood = self.db.get_today_mood()
        if today_mood:
            self.db.cursor.execute(
                "UPDATE moods SET mood=? WHERE id=?", (val, today_mood["id"])
            )
            self.db.conn.commit()
        else:
            self.db.add_mood(val, "")
        self.build_dashboard()

    def generate_ai_messages(self):
        ai = AIAssistant(self.db, self.current_lang)
        messages = ai.generate_messages()
        return messages

    # ============== EKRANLARGA O'TISH ==============
    def show_calendar(self):
        self.active_menu = "calendar"
        self._refresh_menu_active()
        for w in self.content.winfo_children():
            w.destroy()
        CalendarScreen(self.content, self.db, self.current_lang)

    def show_subjects(self):
        self.active_menu = "subjects"
        self._refresh_menu_active()
        for w in self.content.winfo_children():
            w.destroy()
        SubjectsScreen(self.content, self.db, self.current_lang)

    def show_friends(self):
        self.active_menu = "friends"
        self._refresh_menu_active()
        for w in self.content.winfo_children():
            w.destroy()
        FriendsScreen(self.content, self.db, self.current_lang)

    def show_goals(self):
        self.active_menu = "goals"
        self._refresh_menu_active()
        for w in self.content.winfo_children():
            w.destroy()
        GoalsScreen(self.content, self.db, self.current_lang)

    def show_budget(self):
        self.active_menu = "budget"
        self._refresh_menu_active()
        for w in self.content.winfo_children():
            w.destroy()
        BudgetScreen(self.content, self.db, self.current_lang)

    # show_mood / show_achievements / show_pomodoro v3'da olib tashlandi:
    # MoodScreen, AchievementsScreen, PomodoroScreen klasslari hech qachon
    # yozilmagan edi (importlari ham kommentariyda turardi), menyudan ham
    # chaqirilmasdi — chaqirilganda NameError berardi. Keyingi versiyada
    # haqiqiy ekran sifatida qo'shilganda shu yerga qaytariladi.

    def show_journal(self):
        self.active_menu = "journal"
        self._refresh_menu_active()
        for w in self.content.winfo_children():
            w.destroy()
        JournalScreen(self.content, self.db, self.current_lang)

    def show_settings(self):
        self.active_menu = "settings"
        self._refresh_menu_active()
        for w in self.content.winfo_children():
            w.destroy()
        SettingsScreen(self.content, self.db, self.current_lang, on_back=self.logout)

    def _refresh_menu_active(self):
        """Sidebar aktiv tugmasini yangilash"""
        if not hasattr(self, "menu_buttons"):
            return
        for key, frame in self.menu_buttons.items():
            if not frame.winfo_exists():
                continue
            # Indikator
            for child in frame.winfo_children():
                if isinstance(child, tk.Frame) and child.winfo_width() <= 4:
                    child.config(
                        bg=(
                            COLORS["gold"]
                            if key == self.active_menu
                            else COLORS["coffee"]
                        )
                    )
                elif isinstance(child, tk.Label):
                    if (
                        child.cget("font").count("bold") > 0
                        or len(child.cget("text")) > 2
                    ):
                        # Matn
                        child.config(
                            bg=(
                                COLORS["caramel"]
                                if key == self.active_menu
                                else COLORS["coffee"]
                            ),
                            fg=(
                                COLORS["gold"]
                                if key == self.active_menu
                                else COLORS["cream"]
                            ),
                            font=(
                                "Segoe UI",
                                11,
                                "bold" if key == self.active_menu else "normal",
                            ),
                        )
                    else:
                        # Ikonka
                        child.config(
                            bg=(
                                COLORS["caramel"]
                                if key == self.active_menu
                                else COLORS["coffee"]
                            )
                        )
            frame.config(
                bg=COLORS["caramel"] if key == self.active_menu else COLORS["coffee"]
            )

    def logout(self):
        self.show_login_screen()


if __name__ == "__main__":
    App()

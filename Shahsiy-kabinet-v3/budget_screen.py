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
    "pink": "#c2185b",
}

CAT_COLORS = {
    "Oziq-ovqat": COLORS["success"],
    "Transport": COLORS["blue"],
    "Kiyim": COLORS["pink"],
    "Ko'ngilochar": COLORS["gold"],
    "Salomatlik": COLORS["error"],
    "Boshqa": COLORS["sand"],
}


class BudgetScreen:
    def __init__(self, parent, db, lang):
        self.parent = parent
        self.db = db
        self.lang = lang
        self.filter_val = "all"
        self.search_text = ""
        self.build_ui()

    # ============== TARJIMA YORDAMCHISI ==============
    def _t(self, uz, ru, tj):
        return {"uz": uz, "ru": ru, "tj": tj}.get(self.lang, uz)

    def _money(self, v):
        return f"{v:,.0f}".replace(",", " ") + " so'm"

    # ============== UI ==============
    def build_ui(self):
        for w in self.parent.winfo_children():
            w.destroy()

        header = tk.Frame(self.parent, bg=COLORS["milk"])
        header.pack(fill="x", padx=20, pady=(18, 8))
        tk.Label(
            header,
            text=f"💰 {tr('budget', self.lang)}",
            font=("Segoe UI", 20, "bold"),
            bg=COLORS["milk"],
            fg=COLORS["coffee_dark"],
        ).pack(side="left")
        make_pill_button(
            header,
            "+ " + self._t("Xarajat", "Расход", "Хароҷот"),
            COLORS["error"],
            lambda: self._tx_dialog("expense"),
            outer_bg=COLORS["milk"],
            min_width=120,
        ).pack(side="right", padx=(6, 0))
        make_pill_button(
            header,
            "+ " + self._t("Daromad", "Доход", "Даромад"),
            COLORS["success"],
            lambda: self._tx_dialog("income"),
            outer_bg=COLORS["milk"],
            min_width=120,
        ).pack(side="right")

        # Scrollable asosiy maydon
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

        # --- Hisob-kitob ---
        inc = self.db.get_monthly_income_total()
        exp = self.db.get_monthly_total()
        net = inc - exp
        limit = self.db.get_expense_limit()
        avg_day = exp / max(1, date.today().day)
        days_left = max(0, (self._month_end() - date.today()).days)
        forecast = exp + avg_day * days_left

        # --- QATOR 1: KPI kartalari ---
        kpi = tk.Frame(body, bg=COLORS["milk"])
        kpi.pack(fill="x", pady=(4, 8))
        tiles = [
            (
                "📈",
                inc,
                self._t("Daromad (oy)", "Доход (мес)", "Даромад (моҳ)"),
                COLORS["success"],
            ),
            (
                "📉",
                exp,
                self._t("Xarajat (oy)", "Расход (мес)", "Хароҷот (моҳ)"),
                COLORS["error"],
            ),
            (
                "⚖️",
                net,
                self._t("Sof balans", "Чистый баланс", "Тавозуни холис"),
                COLORS["success"] if net >= 0 else COLORS["error"],
            ),
            (
                "🔥",
                avg_day,
                self._t("Kuniga o'rtacha", "В среднем/день", "Миёна/рӯз"),
                COLORS["caramel"],
            ),
        ]
        for i, (ic, val, lab, col) in enumerate(tiles):
            self._kpi_tile(kpi, ic, val, lab, col).grid(
                row=0, column=i, padx=5, sticky="nsew"
            )
            kpi.grid_columnconfigure(i, weight=1)

        # --- QATOR 2: Byudjet limiti progress ---
        if limit > 0:
            lp = tk.Frame(body, bg=COLORS["milk"])
            lp.pack(fill="x", pady=(0, 8))
            self._limit_bar(lp, exp, limit, forecast).pack(fill="x")

        # --- QATOR 3: Ikki donut ---
        charts = tk.Frame(body, bg=COLORS["milk"])
        charts.pack(fill="x", pady=(0, 8))
        exp_cats = self.db.get_expenses_by_category()
        inc_srcs = self.db.get_incomes_by_source()
        self._donut_card(
            charts,
            self._t("Xarajat toifalari", "Категории расходов", "Категорияҳои хароҷот"),
            [(r["category"], r["total"]) for r in exp_cats],
            CAT_COLORS,
            COLORS["error"],
        ).grid(row=0, column=0, padx=5, sticky="nsew")
        self._donut_card(
            charts,
            self._t("Daromad manbalari", "Источники дохода", "Манбаҳои даромад"),
            [(r["source"], r["total"]) for r in inc_srcs],
            {r["source"]: COLORS["success"] for r in inc_srcs},
            COLORS["success"],
        ).grid(row=0, column=1, padx=5, sticky="nsew")
        charts.grid_columnconfigure(0, weight=1)
        charts.grid_columnconfigure(1, weight=1)

        # --- QATOR 4: Trend + Murabbiy ---
        row4 = tk.Frame(body, bg=COLORS["milk"])
        row4.pack(fill="x", pady=(0, 8))
        self._trend_card(row4).grid(row=0, column=0, padx=5, sticky="nsew")
        self._coach_card(row4, inc, exp, net, limit, avg_day, forecast, exp_cats).grid(
            row=0, column=1, padx=5, sticky="nsew"
        )
        row4.grid_columnconfigure(0, weight=1)
        row4.grid_columnconfigure(1, weight=1)

        # --- QATOR 5: Tranzaksiyalar ---
        self._tx_section(body).pack(fill="x", pady=(0, 4))

    def _month_end(self):
        today = date.today()
        if today.month == 12:
            return date(today.year + 1, 1, 1) - timedelta(days=1)
        return date(today.year, today.month + 1, 1) - timedelta(days=1)

    # ============== KPI TILE (count-up) ==============
    def _kpi_tile(self, parent, icon, value, label, color):
        t = tk.Canvas(
            parent, height=118, highlightthickness=0, bg=COLORS["milk"], cursor="hand2"
        )
        t._icon, t._label, t._color = icon, label, color
        t._target = value
        t._shown = 0
        t.bind("<Configure>", lambda e, tt=t: self._draw_kpi(tt))
        t.bind("<Enter>", lambda e, tt=t: self._draw_kpi(tt, True))
        t.bind("<Leave>", lambda e, tt=t: self._draw_kpi(tt))
        self._draw_kpi(t)
        self._count_up(t, value)
        return t

    def _fmt_kpi(self, v):
        if abs(v) >= 1000000:
            return f"{v/1000000:.1f}M"
        if abs(v) >= 1000:
            return f"{v/1000:.0f}k"
        return f"{v:.0f}"

    def _draw_kpi(self, t, hover=False):
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
            text=self._fmt_kpi(t._shown),
            font=("Segoe UI", 22, "bold"),
            fill=t._color,
        )
        t.create_text(
            w / 2 - 1,
            94 + off,
            text=t._label,
            font=("Segoe UI", 9),
            fill=COLORS["coffee"],
        )

    def _count_up(self, t, target):
        steps = 18

        def tick(i):
            if not t.winfo_exists():
                return
            t._shown = target * i / steps
            try:
                self._draw_kpi(t)
            except tk.TclError:
                return
            if i < steps:
                t.after(40, lambda: tick(i + 1))

        tick(0)

    # ============== BYUDJET LIMITI ==============
    def _limit_bar(self, parent, exp, limit, forecast):
        card = RoundedCard(parent, header_bg=None)
        inner = card.inner
        h = 26
        bar = tk.Canvas(
            inner,
            height=h + 30,
            highlightthickness=0,
            bg=COLORS["cream"],
            cursor="hand2",
        )
        bar.pack(fill="x", padx=14, pady=10)
        pct = min(100, exp / limit * 100) if limit else 0
        over = exp > limit
        col = (
            COLORS["error"]
            if over
            else (COLORS["gold"] if pct >= 70 else COLORS["success"])
        )

        def draw():
            w = bar.winfo_width()
            if w < 20:
                return
            bar.delete("all")
            round_rect(
                bar,
                0,
                0,
                w - 1,
                h - 1,
                radius=h / 2,
                fill=COLORS["milk"],
                outline=COLORS["sand"],
                width=1,
            )
            fw = max(h, (w - 2) * pct / 100)
            if fw > 0:
                round_rect(bar, 1, 1, fw, h - 2, radius=h / 2, fill=col, outline="")
            # Prognoz belgisi
            fpct = min(100, forecast / limit * 100) if limit else 0
            fx = (w - 2) * fpct / 100
            bar.create_line(fx, -2, fx, h + 2, fill=COLORS["coffee_dark"], width=2)
            bar.create_text(
                fx,
                h + 12,
                text=self._t("prognoz", "прогноз", "пешгӯӣ"),
                font=("Segoe UI", 7),
                fill=COLORS["coffee"],
            )
            bar.create_text(
                w / 2,
                h / 2,
                text=f"{self._money(exp)} / {self._money(limit)}",
                font=("Segoe UI", 10, "bold"),
                fill=COLORS["cream"] if pct > 30 else COLORS["coffee_dark"],
            )
            tk.Label(
                inner,
                text=(
                    "🚨 "
                    + self._t(
                        "Limitdan oshdingiz!", "Превышен лимит!", "Лимит гузаштед!"
                    )
                    if over
                    else self._t("Byudjet limiti", "Бюджетный лимит", "Лимити буҷет")
                ),
                font=("Segoe UI", 10, "bold"),
                bg=COLORS["cream"],
                fg=COLORS["error"] if over else COLORS["coffee_dark"],
            ).pack(anchor="w", padx=14, pady=(0, 8))

        def on_click(e):
            self._set_limit_dialog()

        bar.bind("<Configure>", lambda ev: draw())
        bar.bind("<Button-1>", on_click)
        draw()
        return card

    def _set_limit_dialog(self):
        d = tk.Toplevel(self.parent)
        d.title(self._t("Byudjet limiti", "Лимит бюджета", "Лимити буҷет"))
        d.configure(bg=COLORS["cream"])
        d.transient(self.parent)
        d.resizable(False, False)
        d.grab_set()
        tk.Label(
            d,
            text="🎯 "
            + self._t(
                "Oylik xarajat chegarasi",
                "Месячный лимит расходов",
                "Ҳадди хароҷоти моҳона",
            ),
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["cream"],
            fg=COLORS["coffee_dark"],
        ).pack(pady=(16, 8))
        f = tk.Frame(d, bg=COLORS["cream"])
        f.pack(fill="x", padx=24)
        e = ModernEntry(f, outer_bg=COLORS["cream"], placeholder="2000000")
        e.pack(fill="x")
        cur = self.db.get_expense_limit()
        if cur:
            e.insert(0, f"{cur:.0f}")

        def save():
            try:
                v = float(e.get().replace(",", "").replace(" ", ""))
            except ValueError:
                v = 0
            self.db.set_expense_limit(v)
            d.destroy()
            self.build_ui()

        ModernButton(
            d, outer_bg=COLORS["cream"], text=tr("save", self.lang), command=save
        ).pack(pady=14)
        d.update_idletasks()
        d.geometry(f"380x{max(d.winfo_reqheight(), 200)}")

    # ============== DONUT DIAGRAMMA ==============
    def _donut_card(self, parent, title, data, color_map, accent):
        card = RoundedCard(parent, title=title, header_bg=COLORS["coffee"])
        total = sum(v for _, v in data)
        wrap = tk.Frame(card.inner, bg=COLORS["cream"])
        wrap.pack(fill="x", padx=12, pady=10)

        donut = tk.Canvas(
            wrap, width=150, height=150, highlightthickness=0, bg=COLORS["cream"]
        )
        donut.pack(side="left", padx=(0, 14))

        def draw():
            donut.delete("all")
            cx = cy = 75
            r = 62
            ri = 34
            if total <= 0:
                donut.create_oval(
                    cx - r, cy - r, cx + r, cy + r, outline=COLORS["sand"], width=2
                )
                donut.create_text(
                    cx,
                    cy,
                    text=self._t("Ma'lumot yo'q", "Нет данных", "Маълумот нест"),
                    font=("Segoe UI", 8),
                    fill=COLORS["coffee"],
                )
                return
            start = 90
            palette = [
                accent,
                COLORS["caramel"],
                COLORS["blue"],
                COLORS["pink"],
                COLORS["gold"],
                COLORS["coffee"],
                COLORS["sand"],
            ]
            for idx, (name, val) in enumerate(data):
                frac = val / total
                ext = -360 * frac
                col = color_map.get(name, palette[idx % len(palette)])
                donut.create_arc(
                    cx - r,
                    cy - r,
                    cx + r,
                    cy + r,
                    start=start,
                    extent=ext,
                    style="pie",
                    fill=col,
                    outline=COLORS["cream"],
                    width=2,
                )
                start += ext
            donut.create_oval(
                cx - ri, cy - ri, cx + ri, cy + ri, fill=COLORS["cream"], outline=""
            )
            donut.create_text(
                cx,
                cy - 8,
                text=self._fmt_kpi(total),
                font=("Segoe UI", 14, "bold"),
                fill=COLORS["coffee_dark"],
            )
            donut.create_text(
                cx,
                cy + 10,
                text=self._t("jami", "всего", "ҳамагӣ"),
                font=("Segoe UI", 8),
                fill=COLORS["coffee"],
            )

        donut.bind("<Configure>", lambda e: draw())
        draw()

        # Legend
        leg = tk.Frame(wrap, bg=COLORS["cream"])
        leg.pack(side="left", fill="both", expand=True)
        palette = [
            accent,
            COLORS["caramel"],
            COLORS["blue"],
            COLORS["pink"],
            COLORS["gold"],
            COLORS["coffee"],
            COLORS["sand"],
        ]
        if not data:
            tk.Label(
                leg,
                text=self._t("Hozircha yo'q", "Пока нет", "Ҳозир нест"),
                font=("Segoe UI", 10),
                bg=COLORS["cream"],
                fg=COLORS["coffee"],
            ).pack(anchor="w", pady=20)
        for idx, (name, val) in enumerate(data[:6]):
            col = color_map.get(name, palette[idx % len(palette)])
            pct = val / total * 100 if total else 0
            row = tk.Frame(leg, bg=COLORS["cream"])
            row.pack(fill="x", pady=2)
            tk.Frame(row, bg=col, width=12, height=12).pack(side="left", padx=(0, 6))
            tk.Label(
                row,
                text=f"{name}",
                font=("Segoe UI", 10, "bold"),
                bg=COLORS["cream"],
                fg=COLORS["coffee_dark"],
                anchor="w",
            ).pack(side="left", fill="x", expand=True)
            tk.Label(
                row,
                text=f"{pct:.0f}%",
                font=("Segoe UI", 9),
                bg=col,
                fg=COLORS["cream"],
                padx=6,
            ).pack(side="right")
        return card

    # ============== HAFTALIK TREND ==============
    def _trend_card(self, parent):
        card = RoundedCard(
            parent,
            title=self._t("Haftalik xarajat", "Недельные расходы", "Хароҷоти ҳафтаина"),
            header_bg=COLORS["coffee"],
        )
        ch = tk.Canvas(card.inner, height=150, bg=COLORS["cream"], highlightthickness=0)
        ch.pack(fill="x", padx=12, pady=10)
        data = self.db.get_daily_expenses(7)
        names = {
            "uz": ["Du", "Se", "Cho", "Pa", "Ju", "Sha", "Ya"],
            "ru": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
            "tj": ["Дш", "Сш", "Чш", "Пш", "Ҷм", "Шб", "Яш"],
        }

        def draw():
            w, h = ch.winfo_width(), ch.winfo_height()
            if w < 50:
                return
            ch.delete("all")
            maxv = max([v for _, v in data] + [1])
            bw = w / 7
            for i, (d, v) in enumerate(data):
                x1 = i * bw + bw * 0.26
                x2 = i * bw + bw * 0.74
                y2 = h - 24
                bh = (h - 44) * (v / maxv)
                is_today = d == date.today()
                col = COLORS["error"] if is_today else COLORS["caramel"]
                if v > 0 and bh > 2:
                    round_rect(ch, x1, y2 - bh, x2, y2, radius=6, fill=col, outline="")
                    ch.create_text(
                        (x1 + x2) / 2,
                        y2 - bh - 9,
                        text=self._fmt_kpi(v),
                        font=("Segoe UI", 8, "bold"),
                        fill=COLORS["coffee_dark"],
                    )
                else:
                    round_rect(
                        ch,
                        x1,
                        y2 - 3,
                        x2,
                        y2,
                        radius=2,
                        fill=COLORS["milk"],
                        outline="",
                    )
                ch.create_text(
                    (x1 + x2) / 2,
                    h - 9,
                    text=names[self.lang][d.weekday()],
                    font=("Segoe UI", 8, "bold" if is_today else "normal"),
                    fill=COLORS["error"] if is_today else COLORS["coffee"],
                )

        ch.bind("<Configure>", lambda e: draw())
        draw()
        return card

    # ============== AQILLI MURABBIY (AI COACH) ==============
    def _coach_card(self, parent, inc, exp, net, limit, avg_day, forecast, exp_cats):
        card = RoundedCard(
            parent,
            title="🤖 "
            + self._t("Moliyaviy murabbiy", "Финансовый советник", "Мураббии молиявӣ"),
            header_bg=COLORS["coffee"],
            live=True,
        )
        box = tk.Frame(card.inner, bg=COLORS["cream"])
        box.pack(fill="x", padx=14, pady=10)
        tips = []

        if net < 0:
            tips.append(
                (
                    "🚨",
                    self._t(
                        f"Xavotir! Xarajat daromadning {abs(net):,.0f} so'miga oshdi.",
                        f"Тревога! Расходы превысили доход на {abs(net):,.0f} сум.",
                        f"Ташвиш! Хароҷот аз даромад {abs(net):,.0f} сомонӣ зиёд шуд.",
                    ),
                    COLORS["error"],
                )
            )
        elif inc > 0 and net > 0:
            save_pct = net / inc * 100
            tips.append(
                (
                    "🎉",
                    self._t(
                        f"Ajoyib! Daromadingizning {save_pct:.0f}% ini tejadingiz.",
                        f"Отлично! Вы сэкономили {save_pct:.0f}% дохода.",
                        f"Аъло! Шумо {save_pct:.0f}% даромадро захира кардед.",
                    ),
                    COLORS["success"],
                )
            )

        if limit > 0 and exp > limit:
            tips.append(
                (
                    "⚠️",
                    self._t(
                        f"Byudjetdan {(exp-limit)/limit*100:.0f}% oshdingiz.",
                        f"Превышение бюджета на {(exp-limit)/limit*100:.0f}%.",
                        f"Буҷетро {(exp-limit)/limit*100:.0f}% гузаштед.",
                    ),
                    COLORS["error"],
                )
            )
        elif limit > 0:
            tips.append(
                (
                    "🎯",
                    self._t(
                        f"Limitsizgacha {self._money(limit-exp)} qoldi.",
                        f"До лимита осталось {self._money(limit-exp)}.",
                        f"То лимит {self._money(limit-exp)} монд.",
                    ),
                    COLORS["gold"],
                )
            )

        if avg_day > 0:
            tips.append(
                (
                    "📈",
                    self._t(
                        f"Kuniga ~{self._money(avg_day)}. Oy oxirigacha ~{self._money(forecast)} ketadi.",
                        f"В среднем ~{self._money(avg_day)}/день. К концу месяца ~{self._money(forecast)}.",
                        f"Миёна ~{self._money(avg_day)}/рӯз. То охири моҳ ~{self._money(forecast)}.",
                    ),
                    COLORS["caramel"],
                )
            )

        if exp_cats:
            top = exp_cats[0]
            share = top["total"] / exp * 100 if exp else 0
            tips.append(
                (
                    "🏆",
                    self._t(
                        f"Eng katta xarajat: {top['category']} ({share:.0f}%).",
                        f"Крупнейший расход: {top['category']} ({share:.0f}%).",
                        f"Калонтарин хароҷот: {top['category']} ({share:.0f}%).",
                    ),
                    COLORS["blue"],
                )
            )
            if share >= 50:
                tips.append(
                    (
                        "💡",
                        self._t(
                            f"{top['category']}ga yarmi ketmoqda — rejali xarajat qiling.",
                            f"Половина уходит на {top['category']} — планируйте.",
                            f"Нисфи он ба {top['category']} меравад — нақша кунед.",
                        ),
                        COLORS["gold"],
                    )
                )

        if not tips:
            tips.append(
                (
                    "👋",
                    self._t(
                        "Daromad va xarajatlaringizni qo'shing — tahlil boshlayman!",
                        "Добавьте доход и расходы — начну анализ!",
                        "Даромад ва хароҷот илова кунед — таҳлил оғоз мекунам!",
                    ),
                    COLORS["sand"],
                )
            )

        for icon, txt, col in tips:
            row = tk.Frame(box, bg=COLORS["cream"])
            row.pack(fill="x", pady=3)
            tk.Label(
                row,
                text=icon,
                font=("Segoe UI", 12),
                bg=col,
                fg=COLORS["cream"],
                width=3,
            ).pack(side="left", padx=(0, 8))
            tk.Label(
                row,
                text=txt,
                font=("Segoe UI", 10),
                bg=COLORS["cream"],
                fg=COLORS["coffee_dark"],
                anchor="w",
                wraplength=320,
                justify="left",
            ).pack(side="left", fill="x", expand=True)
        return card

    # ============== TRANZAKSIYALAR BO'LIMI ==============
    def _tx_section(self, parent):
        card = RoundedCard(
            parent,
            title=" " + self._t("Amaliyotlar", "Операции", "Амалиётлар"),
            header_bg=COLORS["caramel"],
        )
        # Toolbar
        tb = tk.Frame(card.inner, bg=COLORS["cream"])
        tb.pack(fill="x", padx=12, pady=(8, 4))
        sw = tk.Frame(tb, bg=COLORS["milk"], padx=6, pady=3)
        sw.pack(side="left")
        tk.Label(
            sw, text="🔍", font=("Segoe UI", 10), bg=COLORS["milk"], fg=COLORS["coffee"]
        ).pack(side="left", padx=(0, 4))
        se = tk.Entry(
            sw,
            font=("Segoe UI", 10),
            width=18,
            bg=COLORS["milk"],
            fg=COLORS["coffee_dark"],
            relief="flat",
            insertbackground=COLORS["coffee_dark"],
        )
        se.pack(side="left")
        se.bind("<KeyRelease>", lambda e: self._set_search(se.get().strip().lower()))
        filt = ChipGroup(
            tb,
            [
                ("all", self._t("Barchasi", "Все", "Ҳама"), COLORS["coffee"]),
                (
                    "income",
                    "⬆ " + self._t("Daromad", "Доход", "Даромад"),
                    COLORS["success"],
                ),
                (
                    "expense",
                    "⬇ " + self._t("Xarajat", "Расход", "Хароҷот"),
                    COLORS["error"],
                ),
            ],
            "all",
            outer_bg=COLORS["cream"],
        )
        filt.pack(side="right")
        self._filt_holder = filt

        self._tx_list_holder = tk.Frame(card.inner, bg=COLORS["cream"])
        self._tx_list_holder.pack(fill="x", padx=12, pady=(4, 10))
        self._render_tx()
        return card

    def _set_search(self, txt):
        self.search_text = txt
        self._render_tx()

    def _render_tx(self):
        for w in self._tx_list_holder.winfo_children():
            w.destroy()
        rows = []
        if self.filter_val in ("all", "income"):
            for r in self.db.get_incomes():
                rows.append(
                    (
                        "income",
                        r["date"],
                        r["source"],
                        r["description"],
                        r["amount"],
                        r["id"],
                    )
                )
        if self.filter_val in ("all", "expense"):
            for r in self.db.get_expenses():
                rows.append(
                    (
                        "expense",
                        r["date"],
                        r["category"],
                        r["description"],
                        r["amount"],
                        r["id"],
                    )
                )
        rows.sort(key=lambda x: x[1], reverse=True)
        if self.search_text:
            rows = [
                r
                for r in rows
                if self.search_text in (str(r[2]) + " " + str(r[3])).lower()
            ]
        if not rows:
            tk.Label(
                self._tx_list_holder,
                text=self._t("Amaliyotlar yo'q", "Операций нет", "Амалиёт нест"),
                font=("Segoe UI", 11),
                bg=COLORS["cream"],
                fg=COLORS["coffee"],
            ).pack(pady=16)
            return
        for typ, dt, src, desc, amt, rid in rows[:40]:
            is_inc = typ == "income"
            col = COLORS["success"] if is_inc else COLORS["error"]
            row = tk.Frame(self._tx_list_holder, bg=COLORS["milk"], padx=10, pady=7)
            row.pack(fill="x", pady=2)
            tk.Label(
                row,
                text="⬆" if is_inc else "⬇",
                font=("Segoe UI", 12, "bold"),
                bg=col,
                fg=COLORS["cream"],
                width=3,
            ).pack(side="left", padx=(0, 10))
            mid = tk.Frame(row, bg=COLORS["milk"])
            mid.pack(side="left", fill="x", expand=True)
            tk.Label(
                mid,
                text=src,
                font=("Segoe UI", 11, "bold"),
                bg=COLORS["milk"],
                fg=COLORS["coffee_dark"],
                anchor="w",
            ).pack(fill="x")
            sub = f"{dt}" + (f"  •  {desc}" if desc else "")
            tk.Label(
                mid,
                text=sub,
                font=("Segoe UI", 9),
                bg=COLORS["milk"],
                fg=COLORS["coffee"],
                anchor="w",
            ).pack(fill="x")
            tk.Label(
                row,
                text=("+" if is_inc else "−") + self._money(amt),
                font=("Segoe UI", 12, "bold"),
                bg=COLORS["milk"],
                fg=col,
            ).pack(side="left", padx=10)
            tk.Button(
                row,
                text="✕",
                font=("Segoe UI", 9),
                bg=COLORS["milk"],
                fg=COLORS["error"],
                relief="flat",
                cursor="hand2",
                command=lambda t=typ, i=rid: self._del_tx(t, i),
            ).pack(side="right")

    def _del_tx(self, typ, rid):
        if not messagebox.askyesno(tr("confirm", self.lang), tr("confirm", self.lang)):
            return
        if typ == "income":
            self.db.delete_income(rid)
        else:
            self.db.delete_expense(rid)
        self.build_ui()

    # ============== QO'SHISH DIALOGI ==============
    def _tx_dialog(self, kind):
        is_inc = kind == "income"
        d = tk.Toplevel(self.parent)
        d.title(
            ("⬆ " if is_inc else "⬇ ") + self._t("Daromad", "Доход", "Даромад")
            if is_inc
            else ("⬇ " + self._t("Xarajat", "Расход", "Хароҷот"))
        )
        d.configure(bg=COLORS["cream"])
        d.transient(self.parent)
        d.resizable(False, False)
        d.grab_set()
        accent = COLORS["success"] if is_inc else COLORS["error"]
        tk.Label(
            d,
            text=("📈 " if is_inc else "📉 ") + d.title(),
            font=("Segoe UI", 16, "bold"),
            bg=COLORS["cream"],
            fg=accent,
        ).pack(pady=(16, 8))
        f = tk.Frame(d, bg=COLORS["cream"])
        f.pack(fill="x", padx=26)

        def lbl(t):
            tk.Label(
                f,
                text=t,
                font=("Segoe UI", 10, "bold"),
                bg=COLORS["cream"],
                fg=COLORS["coffee"],
            ).pack(anchor="w", pady=(6, 2))

        lbl(self._t("Summa (so'm)", "Сумма (сум)", "Маблағ (сом)"))
        amt_e = ModernEntry(f, outer_bg=COLORS["cream"], placeholder="50000")
        amt_e.pack(fill="x")
        amt_e.focus()
        lbl(self._t("Manba / Toifa", "Источник / Категория", "Манбаъ / Категория"))
        if is_inc:
            opts = [
                ("Stipendiya", "🎓 Stipendiya", COLORS["blue"]),
                ("Ish", "💼 Ish", COLORS["success"]),
                ("Qarzdorlik", "🤝 Qarz", COLORS["gold"]),
                ("Sovg'a", "🎁 Sovg'a", COLORS["pink"]),
                ("Boshqa", "📦 Boshqa", COLORS["sand"]),
            ]
        else:
            opts = [
                ("Oziq-ovqat", "🍞 Ovqat", COLORS["success"]),
                ("Transport", "🚌 Transport", COLORS["blue"]),
                ("Kiyim", "👕 Kiyim", COLORS["pink"]),
                ("Ko'ngilochar", "🎮 Ko'ngilochar", COLORS["gold"]),
                ("Salomatlik", "💊 Salomatlik", COLORS["error"]),
                ("Boshqa", "📦 Boshqa", COLORS["sand"]),
            ]
        g = ChipGroup(f, opts, opts[0][0], outer_bg=COLORS["cream"])
        g.pack(fill="x", pady=(2, 4))
        lbl(
            self._t(
                "Tavsif (ixtiyoriy)", "Описание (необязательно)", "Тавсиф (ихтиёрӣ)"
            )
        )
        desc_e = ModernEntry(f, outer_bg=COLORS["cream"], placeholder="...")
        desc_e.pack(fill="x")
        lbl(self._t("Sana (YYYY-MM-DD)", "Дата (ГГГГ-ММ-ДД)", "Сана (СДСС-ММ-ДД)"))
        date_e = ModernEntry(
            f, outer_bg=COLORS["cream"], placeholder=date.today().isoformat()
        )
        date_e.pack(fill="x")
        date_e.insert(0, date.today().isoformat())

        def save():
            try:
                v = float(amt_e.get().replace(",", "").replace(" ", ""))
            except ValueError:
                messagebox.showerror(
                    tr("error", self.lang),
                    self._t(
                        "To'g'ri summa kiriting!",
                        "Введите сумму!",
                        "Маблағро ворид кунед!",
                    ),
                    parent=d,
                )
                return
            dd = date_e.get().strip() or date.today().isoformat()
            try:
                date.fromisoformat(dd)
            except Exception:
                messagebox.showerror(
                    tr("error", self.lang),
                    self._t(
                        "Sana formati xato!",
                        "Неверный формат даты!",
                        "Формати сана нодуруст!",
                    ),
                    parent=d,
                )
                return
            if is_inc:
                self.db.add_income(v, g.get(), desc_e.get().strip(), dd)
            else:
                self.db.add_expense(v, g.get(), desc_e.get().strip(), dd)
            d.destroy()
            self.build_ui()

        ModernButton(
            d, outer_bg=COLORS["cream"], text=tr("save", self.lang), command=save
        ).pack(pady=14)
        d.update_idletasks()
        d.geometry(f"420x{max(d.winfo_reqheight(), 440)}")

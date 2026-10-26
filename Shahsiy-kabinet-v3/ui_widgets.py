import tkinter as tk
import math


def round_rect(canvas, x1, y1, x2, y2, radius=20, **kwargs):
    """Yumaloq burchakli to'rtburchak chizish"""
    points = [
        x1 + radius,
        y1,
        x1 + radius,
        y1,
        x2 - radius,
        y1,
        x2 - radius,
        y1,
        x2,
        y1,
        x2,
        y1 + radius,
        x2,
        y1 + radius,
        x2,
        y2 - radius,
        x2,
        y2 - radius,
        x2,
        y2,
        x2 - radius,
        y2,
        x2 - radius,
        y2,
        x1 + radius,
        y2,
        x1 + radius,
        y2,
        x1,
        y2,
        x1,
        y2 - radius,
        x1,
        y2 - radius,
        x1,
        y1 + radius,
        x1,
        y1 + radius,
        x1,
        y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


def lighten_color(hexc, amount=30):
    """Hex rangni amount qadar ochroq qilib qaytaradi (hover effektlari uchun)"""
    r = min(255, int(hexc[1:3], 16) + amount)
    g = min(255, int(hexc[3:5], 16) + amount)
    b = min(255, int(hexc[5:7], 16) + amount)
    return f"#{r:02x}{g:02x}{b:02x}"


def make_pill_button(
    parent,
    text,
    color,
    cmd,
    outer_bg,
    text_fg="#fefae0",
    height=40,
    min_width=110,
    font_size=11,
):
    """Yumaloq ('pill' shaklidagi) tugma yaratadi — barcha ekranlarda bir xil
    ko'rinish uchun ishlatiladi (oldin har bir screen faylida alohida
    nusxasi bor edi, endi shu yerda birlashtirilgan)."""
    b = tk.Canvas(parent, height=height, highlightthickness=0, bg=outer_bg, cursor="hand2")
    b._text, b._color = text, color

    def _paint(hover):
        w, h = b.winfo_width(), b.winfo_height()
        if w < 10:
            w = min_width
        b.delete("all")
        fill = lighten_color(b._color) if hover else b._color
        round_rect(b, 0, 0, w - 1, h - 1, radius=h / 2, fill=fill, outline="")
        b.create_text(
            w / 2, h / 2, text=b._text, fill=text_fg, font=("Segoe UI", font_size, "bold")
        )

    b.bind("<Configure>", lambda e: _paint(False))
    b.bind("<Enter>", lambda e: _paint(True))
    b.bind("<Leave>", lambda e: _paint(False))
    b.bind("<Button-1>", lambda e: cmd())
    _paint(False)
    return b


class ModernEntry(tk.Canvas):
    """Zamonaviy kiritish maydoni - placeholder va focus effektlari bilan"""

    def __init__(
        self,
        master,
        placeholder="",
        show="",
        width=340,
        height=46,
        radius=23,
        outer_bg="#fefae0",
        bg="#f5e6d3",
        border="#d4a574",
        focus_border="#8b4513",
        text_color="#3e2723",
        placeholder_color="#a98467",
        font=("Segoe UI", 11),
    ):
        super().__init__(
            master, width=width, height=height, highlightthickness=0, bg=outer_bg
        )
        self.w, self.h, self.radius = width, height, radius
        self.bg, self.border, self.focus_border = bg, border, focus_border
        self.placeholder = placeholder
        self._show_char = show
        self._focused = False
        self._show_placeholder = bool(placeholder)
        # Entry AVVAL yaratiladi (fon chizilishidan oldin)
        self.entry = tk.Entry(
            self,
            font=font,
            bg=bg,
            fg=text_color,
            relief="flat",
            highlightthickness=0,
            insertbackground=text_color,
            show="" if placeholder else show,
        )
        self._win = self.create_window(
            width // 2, height // 2, window=self.entry, tags="win"
        )
        self.entry.config(width=int((width - 44) / 7))
        if placeholder:
            self.entry.insert(0, placeholder)
            self.entry.config(fg=placeholder_color)
        self._draw()
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)

    def _draw(self):
        self.delete("bg")  # MUHIM: faqat fon, entry (win) saqlanadi!
        border = self.focus_border if self._focused else self.border
        wd = 2 if self._focused else 1
        round_rect(
            self,
            1,
            1,
            self.w - 2,
            self.h - 2,
            radius=self.radius,
            fill=self.bg,
            outline=border,
            width=wd,
            tags="bg",
        )
        self.tag_lower("bg", "win")  # fon entry OSTIDA qolsin

    def _on_focus_in(self, e):
        self._focused = True
        self._draw()
        if self._show_placeholder:
            self.entry.delete(0, "end")
            self.entry.config(fg="#3e2723", show=self._show_char)
            self._show_placeholder = False

    def _on_focus_out(self, e):
        self._focused = False
        self._draw()
        if not self.entry.get() and self.placeholder:
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg="#a98467", show="")
            self._show_placeholder = True
        else:
            self.entry.config(show=self._show_char)

    def get(self):
        if self._show_placeholder:
            return ""
        return self.entry.get()

    def insert(self, index, text):
        if self._show_placeholder:
            self.entry.delete(0, "end")
            self.entry.config(fg="#3e2723", show=self._show_char)
            self._show_placeholder = False
        self.entry.insert(index, text)

    def clear_text(self):
        self.entry.delete(0, "end")
        if self.placeholder:
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg="#a98467", show="")
            self._show_placeholder = True

    def focus_set(self):
        self.entry.focus_set()


class ModernButton(tk.Canvas):
    """Zamonaviy yumaloq tugma - hover, bosish va pulse effektlari bilan"""

    def __init__(
        self,
        master,
        text,
        command=None,
        width=240,
        height=50,
        radius=25,
        outer_bg="#fefae0",
        bg="#8b4513",
        hover_bg="#6f4e37",
        active_bg="#5d3a1a",
        fg="#fefae0",
        font=("Segoe UI", 12, "bold"),
    ):
        super().__init__(
            master, width=width, height=height, highlightthickness=0, bg=outer_bg
        )
        self.text, self.command = text, command
        self.w, self.h, self.radius = width, height, radius
        self.bg, self.hover_bg, self.active_bg, self.fg = bg, hover_bg, active_bg, fg
        self.font = font
        self._color = bg
        self._pulse_on = False
        self._t = 0
        self._draw()
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        self.bind("<ButtonPress-1>", self._press)
        self.bind("<ButtonRelease-1>", self._release)

    def _draw(self, scale=0):
        self.delete("all")
        s = scale
        round_rect(
            self,
            2 - s,
            2 - s,
            self.w - 3 + s,
            self.h - 3 + s,
            radius=self.radius,
            fill=self._color,
            outline="",
        )
        self.create_text(
            self.w / 2, self.h / 2, text=self.text, fill=self.fg, font=self.font
        )

    def _enter(self, e):
        self._color = self.hover_bg
        self._draw()
        self.config(cursor="hand2")

    def _leave(self, e):
        self._color = self.bg
        self._draw()

    def _press(self, e):
        self._color = self.active_bg
        self._draw(scale=-1)

    def _release(self, e):
        self._color = self.hover_bg
        self._draw()
        if self.command:
            self.command()

    def config_text(self, text):
        self.text = text
        self._draw()

    def start_pulse(self):
        self._pulse_on = True
        self._pulse_loop()

    def stop_pulse(self):
        self._pulse_on = False

    def _pulse_loop(self):
        if not self._pulse_on or not self.winfo_exists():
            return
        self._t += 1
        s = (math.sin(self._t * 0.12) + 1) * 1.5
        self._draw(scale=s)
        self.after(60, self._pulse_loop)


class PillToggle(tk.Frame):
    """Pill-shaklidagi tanlash tugmalari (til tanlash uchun)"""

    def __init__(
        self,
        master,
        options,
        selected,
        on_change,
        outer_bg="#fefae0",
        active_bg="#8b4513",
        active_fg="#fefae0",
        inactive_fg="#8b4513",
    ):
        super().__init__(master, bg=outer_bg)
        self.options, self.selected, self.on_change = options, selected, on_change
        self.outer_bg, self.active_bg = outer_bg, active_bg
        self.active_fg, self.inactive_fg = active_fg, inactive_fg
        self.pills = {}
        for opt in options:
            p = tk.Canvas(
                self,
                width=62,
                height=34,
                highlightthickness=0,
                bg=outer_bg,
                cursor="hand2",
            )
            p.pack(side="left", padx=3)
            p.bind("<Button-1>", lambda e, o=opt: self._select(o))
            self.pills[opt] = p
        self._paint()

    def _paint(self):
        for opt, p in self.pills.items():
            p.delete("all")
            if opt == self.selected:
                round_rect(p, 1, 1, 60, 32, radius=16, fill=self.active_bg, outline="")
                p.create_text(
                    31,
                    17,
                    text=opt.upper(),
                    fill=self.active_fg,
                    font=("Segoe UI", 10, "bold"),
                )
            else:
                round_rect(
                    p, 1, 1, 60, 32, radius=16, fill="", outline=self.active_bg, width=1
                )
                p.create_text(
                    31,
                    17,
                    text=opt.upper(),
                    fill=self.inactive_fg,
                    font=("Segoe UI", 10, "bold"),
                )

    def _select(self, opt):
        if self.selected == opt:
            return
        self.selected = opt
        self._paint()
        if self.on_change:
            self.on_change(opt)

    def get(self):
        return self.selected


class RoundedCard(tk.Canvas):
    """Professional yumaloq kartochka - sarlavha va ichki kontent bilan"""

    def __init__(
        self,
        master,
        title="",
        header_bg=None,
        header_fg="#fefae0",
        outer_bg="#f5e6d3",
        fill="#fefae0",
        radius=20,
        header_h=44,
        live=False,
        **kw
    ):
        super().__init__(master, highlightthickness=0, bg=outer_bg, **kw)
        self.title, self.header_bg, self.header_fg = title, header_bg, header_fg
        self.fill, self.radius, self.header_h = fill, radius, header_h
        if not header_bg:
            self.header_h = 0
        self.live = live
        self._live_on = True
        self._dot_item = None
        self.inner = tk.Frame(self, bg=fill)
        self.win = self.create_window(
            2, 2 + self.header_h, window=self.inner, anchor="nw", tags="win"
        )
        self.bind("<Configure>", self._layout)
        self.inner.bind("<Configure>", self._fit)
        self._draw(self.winfo_width() or 300, self.winfo_height() or 100)
        if live:
            self._live_loop()

    def _layout(self, event):
        w, h = event.width, event.height
        self.coords(self.win, 2, 2 + self.header_h)
        self.itemconfig(self.win, width=max(w - 4, 50))
        self._draw(w, h)

    def _fit(self, event):
        req = self.inner.winfo_reqheight()
        new_h = req + 4 + self.header_h
        if new_h != self.winfo_height():
            self.config(height=new_h)
        self._draw(self.winfo_width(), new_h)

    def _draw(self, w, h):
        if w < 10 or h < 10:
            return
        # MUHIM: faqat "bg" tag'li chizmalarni o'chiramiz,
        # "win" (ichki kontent) omon qoladi!
        self.delete("bg")
        round_rect(
            self,
            0,
            0,
            w - 1,
            h - 1,
            radius=self.radius,
            fill=self.fill,
            outline="",
            tags="bg",
        )
        if self.header_bg:
            round_rect(
                self,
                0,
                0,
                w - 1,
                self.header_h + self.radius,
                radius=self.radius,
                fill=self.header_bg,
                outline="",
                tags="bg",
            )
            self.create_rectangle(
                0,
                self.header_h,
                w - 1,
                self.header_h + self.radius,
                fill=self.header_bg,
                outline="",
                tags="bg",
            )
            self.create_text(
                18,
                self.header_h / 2,
                text=self.title,
                anchor="w",
                fill=self.header_fg,
                font=("Segoe UI", 12, "bold"),
                tags="bg",
            )
            if self.live:
                self._dot_item = self.create_oval(
                    w - 30,
                    self.header_h / 2 - 6,
                    w - 18,
                    self.header_h / 2 + 6,
                    fill="#2e7d32",
                    outline="",
                    tags="bg",
                )
        # Fon chizmalari kontentdan PASTDA bo'lsin
        self.tag_lower("bg", "win")

    def _live_loop(self):
        if not self.winfo_exists():
            return
        self._live_on = not self._live_on
        if self._dot_item:
            try:
                self.itemconfig(
                    self._dot_item, fill="#2e7d32" if self._live_on else "#95a5a6"
                )
            except tk.TclError:
                return
        self.after(900, self._live_loop)


class ChipGroup(tk.Frame):
    """Yumaloq chip-tanlash guruhi (combobox/radio o'rniga)"""

    def __init__(
        self,
        master,
        options,
        default,
        outer_bg="#fefae0",
        inactive_bg="#f5e6d3",
        inactive_fg="#6f4e37",
        active_fg="#fefae0",
        font=("Segoe UI", 10, "bold"),
    ):
        super().__init__(master, bg=outer_bg)
        is_int = isinstance(default, int)
        self.var = tk.IntVar(value=default) if is_int else tk.StringVar(value=default)
        self.labels = {}
        self._inactive_bg, self._inactive_fg, self._active_fg = (
            inactive_bg,
            inactive_fg,
            active_fg,
        )
        for val, lab, col in options:
            active = val == default
            l = tk.Label(
                self,
                text=lab,
                font=font,
                bg=col if active else inactive_bg,
                fg=active_fg if active else inactive_fg,
                padx=12,
                pady=6,
                cursor="hand2",
                relief="flat",
            )
            l._val, l._col = val, col
            self.labels[val] = l
            l.bind("<Button-1>", lambda e, vv=val: self._pick(vv))
            l.pack(side="left", padx=4, pady=2)

    def _pick(self, val):
        self.var.set(val)
        for k, l in self.labels.items():
            if k == val:
                l.config(bg=l._col, fg=self._active_fg)
            else:
                l.config(bg=self._inactive_bg, fg=self._inactive_fg)

    def get(self):
        return self.var.get()

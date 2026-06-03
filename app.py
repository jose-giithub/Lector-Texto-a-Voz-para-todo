import tkinter as tk
from tkinter import ttk
import pyperclip
import time


class LectorVozApp:
    STATE_IDLE = "idle"
    STATE_SPEAKING = "speaking"
    STATE_PAUSED = "paused"

    def __init__(self, root, tts_engine):
        self.root = root
        self.tts = tts_engine
        self.state = self.STATE_IDLE
        self._tooltip_win = None
        self._drag_x = 0
        self._drag_y = 0

        self._build_ui()
        self._poll_tts_state()

    def _build_ui(self):
        self.root.overrideredirect(True)        # Sin barra de título de Windows
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.geometry("300x250") #Tamaño de ventana más pequeño para que se vea bien en pantallas pequeñas

        # ── Barra de título personalizada ──────────────────────────────────
        frame_title = tk.Frame(self.root, bg="#d0d0d0", height=28)
        frame_title.pack(fill="x")
        frame_title.pack_propagate(False)

        lbl_title = tk.Label(
            frame_title, text="LectorVoz",
            bg="#d0d0d0", font=("Segoe UI", 9, "bold"), fg="#333333"
        )
        lbl_title.pack(side="left", padx=8)

        btn_close = tk.Label(
            frame_title, text="×",
            bg="#d0d0d0", font=("Segoe UI", 11, "bold"), fg="#666666",
            cursor="hand2"
        )
        btn_close.pack(side="right", padx=(0, 8))
        btn_close.bind("<Button-1>", lambda e: self.hide())
        btn_close.bind("<Enter>", lambda e: btn_close.config(fg="#cc0000"))
        btn_close.bind("<Leave>", lambda e: btn_close.config(fg="#666666"))

        btn_help = tk.Label(
            frame_title, text="?",
            bg="#d0d0d0", font=("Segoe UI", 9, "bold"), fg="#666666",
            cursor="question_arrow"
        )
        btn_help.pack(side="right", padx=4)
        btn_help.bind("<Enter>", self._show_tooltip)
        btn_help.bind("<Leave>", self._hide_tooltip)
        btn_help.bind("<Button-1>", self._toggle_tooltip)

        # Arrastrar ventana desde la barra de título
        for widget in (frame_title, lbl_title):
            widget.bind("<ButtonPress-1>", self._drag_start)
            widget.bind("<B1-Motion>", self._drag_motion)

        # ── Botón principal ────────────────────────────────────────────────
        self.btn_main = tk.Button(
            self.root,
            text="Iniciar",
            width=18,
            height=2,
            font=("Segoe UI", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            relief="flat",
            command=self.on_main_button,
        )
        self.btn_main.pack(pady=(15, 5))

        # ── Botón finalizar ────────────────────────────────────────────────
        self.btn_stop = tk.Button(
            self.root,
            text="Finalizar",
            width=18,
            height=2,
            font=("Segoe UI", 11, "bold"),
            bg="#f44336",
            fg="white",
            activebackground="#da190b",
            relief="flat",
            command=self.on_stop_button,
        )
        self.btn_stop.pack(pady=5)

        # ── Slider velocidad ───────────────────────────────────────────────
        frame_rate = tk.Frame(self.root)
        frame_rate.pack(fill="x", padx=20, pady=(10, 0))
        tk.Label(frame_rate, text="Velocidad:", font=("Segoe UI", 9)).pack(side="left")
        self.slider_rate = ttk.Scale(
            frame_rate, from_=80, to=300, orient="horizontal", command=self._on_rate_change
        )
        self.slider_rate.set(150)
        self.slider_rate.pack(side="right", fill="x", expand=True)

        # ── Slider volumen ─────────────────────────────────────────────────
        frame_vol = tk.Frame(self.root)
        frame_vol.pack(fill="x", padx=20, pady=(5, 15))
        tk.Label(frame_vol, text="Volumen:  ", font=("Segoe UI", 9)).pack(side="left")
        self.slider_vol = ttk.Scale(
            frame_vol, from_=0, to=100, orient="horizontal", command=self._on_volume_change
        )
        self.slider_vol.set(100)
        self.slider_vol.pack(side="right", fill="x", expand=True)

    # ── Arrastre de ventana ────────────────────────────────────────────────
    def _drag_start(self, event):
        self._drag_x = event.x_root - self.root.winfo_rootx()
        self._drag_y = event.y_root - self.root.winfo_rooty()

    def _drag_motion(self, event):
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.root.geometry(f"+{x}+{y}")

    # ── Sliders ────────────────────────────────────────────────────────────
    def _on_rate_change(self, val):
        self.tts.set_rate(int(float(val)))

    def _on_volume_change(self, val):
        self.tts.set_volume(float(val) / 100)

    # ── Lógica de botones ──────────────────────────────────────────────────
    def on_main_button(self):
        if self.state == self.STATE_IDLE:
            self._start_reading()
        elif self.state == self.STATE_SPEAKING:
            self._pause_reading()
        elif self.state == self.STATE_PAUSED:
            self._resume_reading()

    def on_stop_button(self):
        self._stop_reading()

    def _start_reading(self):
        text = self._get_text_from_clipboard()
        if not text:
            return
        self.tts.speak(text)
        self._set_state(self.STATE_SPEAKING)

    def _pause_reading(self):
        self.tts.pause()
        self._set_state(self.STATE_PAUSED)

    def _resume_reading(self):
        self.tts.resume()
        self._set_state(self.STATE_SPEAKING)

    def _stop_reading(self):
        self.tts.stop()
        self._set_state(self.STATE_IDLE)

    def _get_text_from_clipboard(self):
        import keyboard
        keyboard.send("ctrl+c")
        time.sleep(0.15)
        try:
            text = pyperclip.paste()
            return text.strip() if text else ""
        except Exception:
            return ""

    def _set_state(self, new_state):
        self.state = new_state
        if new_state == self.STATE_IDLE:
            self.btn_main.config(text="Iniciar", bg="#4CAF50", activebackground="#45a049")
        elif new_state == self.STATE_SPEAKING:
            self.btn_main.config(text="Pausar", bg="#FF9800", activebackground="#e68900")
        elif new_state == self.STATE_PAUSED:
            self.btn_main.config(text="Reanudar", bg="#2196F3", activebackground="#1976D2")

    def _poll_tts_state(self):
        if self.state == self.STATE_SPEAKING and not self.tts.is_speaking:
            self._set_state(self.STATE_IDLE)
        self.root.after(300, self._poll_tts_state)

    # ── Tooltip de atajos ──────────────────────────────────────────────────
    def _show_tooltip(self, event=None):
        if self._tooltip_win:
            return
        if event:
            x, y = event.x_root + 5, event.y_root + 5
        else:
            x = self.root.winfo_rootx() + 160
            y = self.root.winfo_rooty() + 5
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.geometry(f"+{x}+{y}")
        win.configure(bg="#2b2b2b")
        tk.Label(
            win, text="Atajos de teclado",
            font=("Segoe UI", 9, "bold"), fg="#ffffff", bg="#2b2b2b",
            padx=10, pady=6,
        ).pack(anchor="w")
        tk.Frame(win, bg="#555555", height=1).pack(fill="x", padx=10)
        tk.Label(
            win,
            text="Alt + G    Iniciar / Pausar / Reanudar\nAlt + F    Finalizar",
            font=("Segoe UI", 9), fg="#dddddd", bg="#2b2b2b",
            justify="left", padx=10, pady=6,
        ).pack(anchor="w")
        self._tooltip_win = win

    def _hide_tooltip(self, event=None):
        if self._tooltip_win:
            self._tooltip_win.destroy()
            self._tooltip_win = None

    def _toggle_tooltip(self, event=None):
        if self._tooltip_win:
            self._hide_tooltip()
        else:
            self._show_tooltip(event)

    # ── Mostrar / ocultar ventana ──────────────────────────────────────────
    def show(self):
        self.root.after(0, self._do_show)

    def _do_show(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide(self):
        self._hide_tooltip()
        self.root.withdraw()

    def show_help(self):
        self.root.after(0, self._do_show_help)

    def _do_show_help(self):
        self._do_show()
        self._show_tooltip()

    # ── Hotkeys (llamados desde hilo distinto) ─────────────────────────────
    def hotkey_toggle(self):
        self.root.after(0, self.on_main_button)

    def hotkey_stop(self):
        self.root.after(0, self.on_stop_button)

import keyboard
import threading


class HotkeyManager:
    def __init__(self):
        self._thread = None
        self._running = False

    def register(self, app):
        self._running = True
        self._thread = threading.Thread(target=self._listen, args=(app,), daemon=True)
        self._thread.start()

    def _listen(self, app):
        keyboard.add_hotkey("alt+g", app.hotkey_toggle, suppress=False)
        keyboard.add_hotkey("alt+f", app.hotkey_stop, suppress=False)
        keyboard.wait()  # Bloquea el hilo hasta que se detenga

    def unregister(self):
        try:
            keyboard.remove_hotkey("alt+g")
            keyboard.remove_hotkey("alt+f")
        except Exception:
            pass

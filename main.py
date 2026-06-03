import os
import tkinter as tk
from tts_engine import TTSEngine
from app import LectorVozApp
from hotkeys import HotkeyManager
from tray import TrayIcon


def main():
    root = tk.Tk()
    root.withdraw()  # Arranca oculta, el tray la mostrará

    tts = TTSEngine()
    app = LectorVozApp(root, tts)

    hotkeys = HotkeyManager()
    hotkeys.register(app)

    def on_quit():
        # Debe ejecutarse en el hilo principal de tkinter
        root.after(0, _do_quit)

    def _do_quit():
        tts.stop()
        hotkeys.unregister()
        tray.stop()
        root.destroy()
        os._exit(0)

    tray = TrayIcon(show_callback=app.show, quit_callback=on_quit, help_callback=app.show_help)
    tray.start()

    root.mainloop()


if __name__ == "__main__":
    main()

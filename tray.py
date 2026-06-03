import os
import sys
import pystray
from PIL import Image


def _resource_path(filename):
    """Resuelve rutas tanto en desarrollo como empaquetado con PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


class TrayIcon:
    def __init__(self, show_callback, quit_callback, help_callback=None):
        self._show_cb = show_callback
        self._quit_cb = quit_callback
        self._help_cb = help_callback
        self._icon = None
        self._image = self._load_image()

    def _load_image(self):
        path = _resource_path("icon.ico")
        if os.path.exists(path):
            return Image.open(path)
        # Fallback: cuadrado verde si no hay icono
        return Image.new("RGB", (64, 64), color=(76, 175, 80))

    def start(self):
        items = [
            pystray.MenuItem("Mostrar ventana", self._on_show, default=True),
        ]
        if self._help_cb:
            items.append(pystray.MenuItem("Atajos de teclado", self._on_help))
        items.append(pystray.MenuItem("Salir", self._on_quit))
        menu = pystray.Menu(*items)
        self._icon = pystray.Icon("LectorVoz", self._image, "LectorVoz", menu)
        self._icon.run_detached()

    def stop(self):
        if self._icon:
            self._icon.stop()
            self._icon = None

    def _on_show(self, icon, item):
        self._show_cb()

    def _on_help(self, icon, item):
        if self._help_cb:
            self._help_cb()

    def _on_quit(self, icon, item):
        self._quit_cb()

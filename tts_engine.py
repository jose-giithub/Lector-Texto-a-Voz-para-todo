import asyncio
import logging
import os
import sys
import tempfile
import threading
import time

import edge_tts
import pygame


VOICE = "es-ES-ElviraNeural"


def _log_dir():
    """Carpeta fija para el log, independiente de dónde esté el .exe.

    Usamos %LOCALAPPDATA%/LectorVoz para que el log no aparezca en el
    escritorio (u otra carpeta) si el ejecutable se mueve o se lanza desde
    un acceso directo.
    """
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    path = os.path.join(base, "LectorVoz")
    os.makedirs(path, exist_ok=True)
    return path


# Log en una carpeta fija para diagnosticar fallos tras días de uptime.
LOG_PATH = os.path.join(_log_dir(), "lectorvoz.log")
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


class TTSEngine:
    def __init__(self):
        pygame.mixer.init()
        self._lock = threading.Lock()
        self._speaking = False
        self._paused = False
        self._rate = "+0%"
        self._volume = 1.0
        self._thread = None

    def set_rate(self, rate):
        # Slider 80-300 → edge-tts rate string (-70% a +150%)
        # 150 = normal (+0%), 80 = muy lento (-70%), 300 = muy rápido (+150%)
        pct = int((float(rate) - 150) / 150 * 150)
        pct = max(-70, min(150, pct))
        self._rate = f"+{pct}%" if pct >= 0 else f"{pct}%"

    def set_volume(self, volume):
        self._volume = float(volume)
        try:
            pygame.mixer.music.set_volume(self._volume)
        except Exception:
            # El mixer puede estar re-inicializándose; se aplicará en la próxima lectura.
            pass

    def _reset_mixer(self):
        """Re-inicializa el mixer para coger el dispositivo de audio actual.

        Tras varios días de uptime (y ciclos de suspensión/reanudación de
        Windows), el handle de audio que capturó pygame.mixer.init() al
        arrancar queda obsoleto: play() deja de sonar aunque no lance ningún
        error. Cerrar y volver a abrir el mixer antes de cada lectura garantiza
        un handle válido sobre el dispositivo por defecto vigente.
        """
        try:
            if pygame.mixer.get_init():
                pygame.mixer.quit()
        except Exception:
            logging.exception("Error cerrando el mixer previo")
        pygame.mixer.init()

    def speak(self, text):
        with self._lock:
            if self._speaking:
                return
            self._speaking = True
            self._paused = False

        self._thread = threading.Thread(target=self._speak_thread, args=(text,), daemon=True)
        self._thread.start()

    def _speak_thread(self, text):
        tmp_path = None
        try:
            tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            tmp.close()
            tmp_path = tmp.name

            logging.info("Generando audio (%d caracteres)", len(text))
            asyncio.run(self._generate(text, tmp_path))

            # Mixer fresco sobre el dispositivo de audio actual (ver _reset_mixer).
            self._reset_mixer()

            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.set_volume(self._volume)
            pygame.mixer.music.play()

            # Espera a que la reproducción arranque de verdad: get_busy() puede
            # devolver False durante un instante justo después de play(), lo que
            # haría salir del bucle de inmediato (botón naranja ~1 s y vuelta).
            start = time.time()
            while not pygame.mixer.music.get_busy() and time.time() - start < 1.0:
                with self._lock:
                    if not self._speaking:
                        break
                time.sleep(0.05)

            if not pygame.mixer.music.get_busy():
                logging.warning(
                    "La reproduccion no arranco; posible dispositivo de audio no disponible"
                )

            while True:
                with self._lock:
                    if not self._speaking:
                        break
                    paused = self._paused
                if not paused and not pygame.mixer.music.get_busy():
                    break
                time.sleep(0.1)

        except Exception:
            logging.exception("Error en la reproduccion de voz")
        finally:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
            with self._lock:
                self._speaking = False
                self._paused = False

    async def _generate(self, text, output_path):
        communicate = edge_tts.Communicate(text, VOICE, rate=self._rate)
        await communicate.save(output_path)

    def pause(self):
        with self._lock:
            if not self._speaking or self._paused:
                return
            self._paused = True
        pygame.mixer.music.pause()

    def resume(self):
        with self._lock:
            if not self._paused:
                return
            self._paused = False
        pygame.mixer.music.unpause()

    def stop(self):
        with self._lock:
            self._speaking = False
            self._paused = False
        pygame.mixer.music.stop()

    @property
    def is_speaking(self):
        with self._lock:
            return self._speaking

    @property
    def is_paused(self):
        with self._lock:
            return self._paused

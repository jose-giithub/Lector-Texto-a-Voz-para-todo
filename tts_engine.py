import asyncio
import os
import tempfile
import threading
import time

import edge_tts
import pygame


VOICE = "es-ES-ElviraNeural"


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
        pygame.mixer.music.set_volume(self._volume)

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

            asyncio.run(self._generate(text, tmp_path))

            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.set_volume(self._volume)
            pygame.mixer.music.play()

            while True:
                with self._lock:
                    if not self._speaking:
                        break
                    paused = self._paused
                if not paused and not pygame.mixer.music.get_busy():
                    break
                time.sleep(0.1)

        finally:
            pygame.mixer.music.stop()
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

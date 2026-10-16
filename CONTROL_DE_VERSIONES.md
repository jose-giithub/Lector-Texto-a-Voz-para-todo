# Control de versiones y actualizaciones

## Instrucciones de este archivo

- **Cada vez que se modifique el programa** (código, dependencias o `.exe`) hay que añadir aquí una entrada nueva.
- Las entradas van **de la más reciente a la más antigua**: la nueva siempre arriba, justo debajo de esta sección.
- Cada entrada lleva **la fecha** (`AAAA-MM-DD`) y un título corto, y después:
  - **Problema:** qué fallaba o qué se quería conseguir (si aplica).
  - **Causa:** por qué ocurría (si se conoce).
  - **Cambios:** qué se ha modificado y en qué archivos.
  - **Cómo aplicarlo:** pasos necesarios para que el cambio llegue al `.exe` (reinstalar dependencias, recompilar…), si los hay.
- Usa el mismo formato que las entradas de abajo para que el historial sea fácil de leer.

---

## 2026-10-16 — Error 403 del servicio de voz y nueva ubicación del log

**Problema:** tras el arreglo anterior, la app seguía sin sonar. Detectaba el texto, pero no se oía nada. Además, al mover el `.exe` al escritorio, el log `lectorvoz.log` se creaba en el escritorio.

**Causa:** la librería `edge-tts` instalada (7.2.8) estaba desactualizada. Microsoft cambia de vez en cuando el "pase" que exige su servicio de voz, y las versiones antiguas reciben un error `403` (`WSServerHandshakeError`). Se reproducía también fuera del `.exe`, así que no era un problema de empaquetado. El log estaba programado para guardarse junto al ejecutable, así que seguía al `.exe` a donde se moviera.

**Cambios:**
- `requirements.txt`: `edge-tts` pasa a `edge-tts>=7.3.1` (versión comprobada que funciona).
- `tts_engine.py`: el log se guarda siempre en `%LOCALAPPDATA%\LectorVoz\lectorvoz.log`, esté donde esté el `.exe`.
- `README.md`: documentada la nueva ruta del log, el consejo de usar un **acceso directo** en lugar de mover el `.exe`, y qué hacer si vuelve a aparecer el error 403.
- Creado este archivo de control de versiones.

**Cómo aplicarlo:** `pip install -U -r requirements.txt` (el `-U` es imprescindible: sin él no se actualiza un paquete que ya está instalado) y `pyinstaller --clean lectorvoz.spec`.

---

## 2026-10-16 — Lectura que dejaba de sonar tras días de uptime

**Problema:** tras varios días con el equipo encendido, el botón pasaba a "Pausar" durante un segundo y volvía a "Iniciar" sin que se oyera nada.

**Causa:** tras ciclos de suspensión y reanudación de Windows, el dispositivo de audio que `pygame.mixer` capturaba al arrancar quedaba obsoleto, y `play()` no sonaba ni daba error.

**Cambios:**
- `tts_engine.py`: `_reset_mixer()` reinicia el dispositivo de audio antes de cada lectura. Además, se espera a que la reproducción arranque de verdad y se añaden un registro de errores (`lectorvoz.log`) y un manejo de excepciones en el hilo de voz.
- `README.md`: nueva sección "Solución de problemas".

**Cómo aplicarlo:** recompilar con `pyinstaller --clean lectorvoz.spec`.

---

## 2026-06-03 — Primera versión publicada

- Publicación inicial del proyecto: lectura en voz alta del portapapeles con voz neural de Microsoft (`edge-tts` + `pygame`), atajos `Alt+G` / `Alt+F`, icono en la bandeja y empaquetado como `.exe` con PyInstaller.
- Ajustes del README con las rutas del proyecto y retoques finales.

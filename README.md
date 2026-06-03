# Lector-Texto-a-Voz-para-todo

Aplicación de escritorio para Windows que lee en voz alta cualquier texto que tengas seleccionado en pantalla. Selecciona texto en el navegador, en un PDF, en Word, o en cualquier otra app, pulsa un atajo y escucha.

---

**Autor**: Jose Rodríguez  + Claude code

## Redes sociales 🌐

**Portfolio**🔗[Enlace portfolio:](https://portfolio.jose-rodriguez-blanco.es)
**LinkedIn**🔗[Enlace LinkedIn:](https://www.linkedin.com/in/joseperfil/)
**GitHub**🔗[Enlace GitHub:](https://github.com/jose-giithub)

---

## Funcionalidades

- Lee en voz alta el texto que tengas seleccionado en cualquier aplicación
- Voz en español de alta calidad (voz neural de Microsoft via internet)
- Control total: Iniciar, Pausar, Reanudar y Finalizar
- Atajos de teclado globales (funcionan aunque la ventana no esté en foco)
- Slider de velocidad y volumen ajustables
- Icono en la bandeja del sistema (System Tray) — no ocupa espacio en la barra de tareas
- Ventana siempre visible y arrastrable

### Atajos de teclado

- `Alt + G` — Iniciar / Pausar / Reanudar
- `Alt + F` — Finalizar lectura

---

## Requisitos

- Windows 10 / 11
- Python 3.12 o superior
- Conexión a internet (para generar el audio con la voz neural)

---

## Instalación y uso

### 1. Clona el repositorio

```bash
git clone https://github.com/tu-usuario/Lector-Texto-a-Voz-para-todo.git
cd Lector-Texto-a-Voz-para-todo
```

### 2. Crea un entorno virtual (recomendado)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instala las dependencias

```bash
pip install edge-tts pygame pystray Pillow pyperclip keyboard
```

### 4. Ejecuta la aplicación

```bash
python main.py
```

> La ventana aparece minimizada en la bandeja del sistema. Haz clic en el icono para mostrarla.

---

## Compilar el ejecutable (.exe)

Si quieres un `.exe` independiente que no necesite Python instalado:

### 1. Instala PyInstaller

```bash
pip install pyinstaller
```

### 2. Compila usando el archivo de configuración incluido

```bash
pyinstaller lectorvoz.spec
```

El ejecutable quedará en `dist/LectorVoz.exe`. Puedes moverlo a cualquier carpeta y ejecutarlo directamente.

> **Nota:** el `.exe` sigue necesitando conexión a internet para generar el audio.

---

## Estructura del proyecto

```text
Lector-Texto-a-Voz-para-todo/
├── main.py           # Punto de entrada, conecta todos los módulos
├── app.py            # Ventana y lógica de la interfaz
├── tts_engine.py     # Motor de voz (edge-tts + pygame)
├── hotkeys.py        # Atajos de teclado globales
├── tray.py           # Icono en la bandeja del sistema
├── lectorvoz.spec    # Configuración de PyInstaller
└── icon.ico          # Icono de la aplicación
```

---

## Cómo funciona

1. Selecciona cualquier texto en cualquier aplicación
2. Pulsa `Alt + G` (o el botón "Iniciar" en la ventana)
3. La app captura el texto del portapapeles y lo envía a la voz neural de Microsoft
4. El audio se reproduce en tu equipo

---

## Guía rápida del código

Para quien quiera modificar o extender el proyecto, aquí está dónde tocar cada cosa:

---

### [main.py](main.py) — Punto de entrada y conexión entre módulos

Es el único archivo que se ejecuta directamente (`python main.py`). No contiene lógica propia: su trabajo es crear todos los demás módulos y conectarlos entre sí. Si añades un módulo nuevo al proyecto, aquí es donde lo instancias y lo enlazas con el resto.

**Contiene:**

- Creación de la ventana tkinter
- Instanciación de `TTSEngine`, `LectorVozApp`, `HotkeyManager` y `TrayIcon`
- La función `on_quit()` — única forma limpia de cerrar la app

---

### [app.py](app.py) — Ventana y lógica de la interfaz

Aquí vive todo lo visual y el comportamiento de los botones. Si quieres cambiar colores, tamaño de la ventana, añadir un botón, mover los sliders o cambiar los textos, es en este archivo.

**Contiene:**

- Construcción de la UI: barra de título, botones, sliders
- Máquina de estados (`IDLE` → `SPEAKING` → `PAUSED`)
- Captura del texto seleccionado vía portapapeles (`Ctrl+C` automático)
- Polling cada 300 ms para detectar cuándo termina el audio
- Métodos que llaman los hotkeys: `hotkey_toggle()` y `hotkey_stop()`

**Si quieres cambiar:** colores → busca `bg=`, tamaño → `geometry("300x250")`, velocidad por defecto → `self.slider_rate.set(150)`, volumen por defecto → `self.slider_vol.set(100)`

---

### [tts_engine.py](tts_engine.py) — Motor de voz

Gestiona toda la generación y reproducción del audio. Usa `edge-tts` para generar un MP3 con la voz neural de Microsoft y `pygame` para reproducirlo.

**Contiene:**

- Generación del audio en un hilo separado (para no bloquear la UI)
- Control de pausa/reanudación con `pygame.mixer`
- Conversión del valor del slider (80-300) al formato de velocidad de edge-tts

**Si quieres cambiar:** la voz → constante `VOICE = "es-ES-ElviraNeural"` en la línea 11, el rango de velocidad → método `set_rate()`

---

### [hotkeys.py](hotkeys.py) — Atajos de teclado globales

Registra combinaciones de teclas que funcionan en todo el sistema, incluso cuando la ventana no está en foco. Corre en un hilo propio para no bloquear la interfaz.

**Contiene:**

- Registro de `Alt+G` → toggle (iniciar/pausar/reanudar)
- Registro de `Alt+F` → finalizar
- Limpieza de atajos al cerrar la app

**Si quieres cambiar los atajos:** líneas 16 y 17, cambia `"alt+g"` y `"alt+f"` por la combinación que prefieras

---

### [tray.py](tray.py) — Icono en la bandeja del sistema

Crea el icono en el área de notificaciones de Windows con un menú contextual. Si no hay `icon.ico`, usa un cuadrado verde como fallback.

**Contiene:**

- Carga del icono (`icon.ico`)
- Menú con tres opciones: Mostrar ventana, Atajos de teclado, Salir
- Compatibilidad con PyInstaller (`_resource_path`)

**Si quieres cambiar:** el icono → reemplaza `icon.ico`, las opciones del menú → método `start()`

---

## Licencia

Este proyecto está publicado bajo la licencia **MIT** — eres libre de:

- Usarlo como quieras (personal, comercial, educativo...)
- Modificarlo y adaptarlo a tus necesidades
- Distribuirlo y compartirlo
- Incluirlo en otros proyectos, incluso cerrados o de pago

La única condición es mantener el aviso de copyright si redistribuyes el código fuente. Ver el archivo [LICENSE](LICENSE) para el texto completo.

> Las librerías de terceros incluidas (edge-tts, pygame, pystray, etc.)
> tienen sus propias licencias permisivas (MIT, LGPL, BSD) que son compatibles.

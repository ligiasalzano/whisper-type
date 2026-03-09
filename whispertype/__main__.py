"""
WhisperType
===========
Segure Ctrl+Space para gravar, solte para transcrever e colar.
Usa ffmpeg para captura de áudio — não depende de PortAudio.

Uso:
    python -m whispertype

Dependências Python:
    Windows: pip install openai-whisper pyperclip keyboard pyautogui
    Linux:   pip install openai-whisper pyperclip pynput

Dependências do sistema:
    Windows: ffmpeg no PATH
    Linux:   sudo apt install ffmpeg pulseaudio-utils xdotool   # X11
             sudo apt install ffmpeg pulseaudio-utils ydotool   # Wayland
"""

import logging
import shutil
import sys

import whisper

from whispertype.config import MODEL_SIZE, LANGUAGE
from whispertype.recorder import Recorder

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("WhisperType")


def _check_dependency(cmd: str, install_hint: str) -> None:
    if not shutil.which(cmd):
        log.error("%s não encontrado. %s", cmd, install_hint)
        sys.exit(1)


def _run_windows(model: whisper.Whisper) -> None:
    import keyboard
    from whispertype.audio.windows import get_mic_name, build_ffmpeg_cmd
    from whispertype.paste.windows import paste_text

    HOTKEY = "ctrl+space"

    _check_dependency("ffmpeg", "Baixe em https://ffmpeg.org e adicione ao PATH.")

    log.info("Detectando microfone...")
    mic_name = get_mic_name()
    if not mic_name:
        log.error("Nenhum microfone encontrado via ffmpeg. Verifique se o ffmpeg está no PATH.")
        sys.exit(1)
    log.info("Microfone: %s", mic_name)

    recorder = Recorder(
        mic_name=mic_name,
        model=model,
        build_ffmpeg_cmd=build_ffmpeg_cmd,
        paste_fn=paste_text,
    )

    def on_space_press(e):
        if keyboard.is_pressed("ctrl"):
            recorder.start()

    def on_space_release(e):
        # Para a gravação se estava gravando — sem checar ctrl,
        # pois ele pode já ter sido solto antes do espaço.
        if recorder.is_recording:
            recorder.stop()

    # suppress=False: espaço normal nunca é bloqueado
    keyboard.on_press_key("space",   on_space_press,   suppress=False)
    keyboard.on_release_key("space", on_space_release, suppress=False)

    log.info("Pronto! Segure %s para ditar. Ctrl+C para sair.", HOTKEY.upper())

    try:
        keyboard.wait()
    except KeyboardInterrupt:
        log.info("Encerrado.")
        sys.exit(0)


def _run_linux(model: whisper.Whisper) -> None:
    from pynput import keyboard
    from whispertype.audio.linux import get_mic_name, build_ffmpeg_cmd, detect_session
    from whispertype.paste.linux import paste_text

    HOTKEY = {keyboard.Key.ctrl_l, keyboard.Key.space}

    _check_dependency("ffmpeg", "Instale com: sudo apt install ffmpeg")
    _check_dependency("pactl",  "Instale com: sudo apt install pulseaudio-utils")

    session = detect_session()
    log.info("Sessão detectada: %s", session.upper())

    log.info("Detectando microfone...")
    mic_name = get_mic_name()
    if not mic_name:
        log.error("Nenhum microfone encontrado via pactl.")
        sys.exit(1)
    log.info("Microfone: %s", mic_name)

    recorder = Recorder(
        mic_name=mic_name,
        model=model,
        build_ffmpeg_cmd=build_ffmpeg_cmd,
        paste_fn=paste_text,
    )

    # Teclas atualmente pressionadas
    pressed = set()

    def on_press(key):
        pressed.add(key)
        if all(k in pressed for k in HOTKEY):
            recorder.start()

    def on_release(key):
        if recorder.is_recording:
            recorder.stop()
        pressed.discard(key)

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        log.info("Pronto! Segure CTRL+SPACE para ditar. Ctrl+C para sair.")
        try:
            listener.join()
        except KeyboardInterrupt:
            log.info("Encerrado.")
            sys.exit(0)


def main() -> None:
    log.info("Carregando modelo Whisper '%s'...", MODEL_SIZE)
    model = whisper.load_model(MODEL_SIZE)
    log.info("Modelo carregado. Idioma: %s", LANGUAGE or "autodetectar")

    if sys.platform == "win32":
        _run_windows(model)
    elif sys.platform.startswith("linux"):
        _run_linux(model)
    else:
        log.error("Sistema operacional não suportado: %s", sys.platform)
        sys.exit(1)


if __name__ == "__main__":
    main()

import logging
import shutil
import subprocess
import time

import pyperclip

from whispertype.config import PASTE_DELAY_SECONDS
from whispertype.audio.linux import detect_session

log = logging.getLogger("WhisperType")


def paste_text(text: str) -> None:
    """Copia o texto e simula Ctrl+V usando a ferramenta adequada à sessão."""
    pyperclip.copy(text)
    time.sleep(PASTE_DELAY_SECONDS)

    session = detect_session()

    if session == "wayland":
        if shutil.which("ydotool"):
            subprocess.run(["ydotool", "key", "29:1", "47:1", "47:0", "29:0"], check=False)
        else:
            log.warning("ydotool não encontrado. Instale com: sudo apt install ydotool")
            log.info("O texto está na área de transferência — cole manualmente com Ctrl+V.")
    else:
        if shutil.which("xdotool"):
            subprocess.run(["xdotool", "key", "ctrl+v"], check=False)
        else:
            log.warning("xdotool não encontrado. Instale com: sudo apt install xdotool")
            log.info("O texto está na área de transferência — cole manualmente com Ctrl+V.")

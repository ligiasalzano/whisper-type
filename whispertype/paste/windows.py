import time

import pyautogui
import pyperclip

from whispertype.config import PASTE_DELAY_SECONDS


def paste_text(text: str) -> None:
    """Copia o texto e simula Ctrl+V via pyautogui."""
    pyperclip.copy(text)
    time.sleep(PASTE_DELAY_SECONDS)
    pyautogui.hotkey("ctrl", "v")

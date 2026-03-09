import logging
import os
import subprocess

log = logging.getLogger("WhisperType")


def detect_session() -> str:
    """Detecta se a sessão gráfica é X11 ou Wayland."""
    session = os.environ.get("XDG_SESSION_TYPE", "").lower()
    if session in ("wayland", "x11"):
        return session
    # Fallback: checa WAYLAND_DISPLAY
    return "wayland" if os.environ.get("WAYLAND_DISPLAY") else "x11"


def get_mic_name() -> str | None:
    """Retorna o nome do microfone padrão via pactl."""
    try:
        # Tenta pegar o source padrão
        result = subprocess.run(
            ["pactl", "get-default-source"],
            capture_output=True, text=True, timeout=5,
        )
        name = result.stdout.strip()
        if name:
            return name
    except FileNotFoundError:
        pass

    # Fallback: pega o primeiro source que não seja monitor
    try:
        result = subprocess.run(
            ["pactl", "list", "sources", "short"],
            capture_output=True, text=True, timeout=5,
        )
        for line in result.stdout.splitlines():
            if "monitor" not in line.lower():
                parts = line.split()
                if len(parts) >= 2:
                    return parts[1]
    except Exception as e:
        log.error("Erro ao listar fontes de áudio: %s", e)

    return None


def build_ffmpeg_cmd(mic_name: str, output_path: str) -> list[str]:
    """Monta o comando ffmpeg usando PulseAudio/PipeWire para Linux."""
    return [
        "ffmpeg", "-y",
        "-f", "pulse",
        "-i", mic_name,
        "-ar", "16000",
        "-ac", "1",
        output_path,
    ]

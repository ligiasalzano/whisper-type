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
    """
    Retorna o nome do microfone para uso no ffmpeg.
    Prefere 'default' (sempre válido no PulseAudio/PipeWire),
    mas verifica primeiro se há algum source de entrada disponível.
    """
    try:
        result = subprocess.run(
            ["pactl", "list", "sources", "short"],
            capture_output=True, text=True, timeout=5,
        )
        for line in result.stdout.splitlines():
            if "monitor" not in line.lower() and line.strip():
                # Fonte de entrada encontrada — usa 'default' como nome ffmpeg,
                # que o PulseAudio/PipeWire mapeia automaticamente para o microfone padrão.
                log.debug("Fonte de áudio disponível: %s", line.split()[1] if len(line.split()) >= 2 else "?")
                return "default"
    except Exception as e:
        log.error("Erro ao listar fontes de áudio: %s", e)

    return None


def build_ffmpeg_cmd(mic_name: str, output_path: str) -> list[str]:
    """Monta o comando ffmpeg usando PulseAudio/PipeWire para Linux."""
    return [
        "ffmpeg", "-y",
        "-f", "pulse",
        "-i", mic_name,   # "default" → microfone padrão do sistema
        "-ar", "16000",
        "-ac", "1",
        output_path,
    ]

import logging
import re
import subprocess

log = logging.getLogger("WhisperType")


def get_mic_name() -> str | None:
    """Lê a saída do ffmpeg -list_devices e retorna o primeiro microfone (audio)."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
        for line in result.stderr.splitlines():
            if "(audio)" in line:
                match = re.search(r'"([^"]+)"', line)
                if match:
                    return match.group(1)
    except Exception as e:
        log.error("Erro ao listar dispositivos de áudio: %s", e)
    return None


def build_ffmpeg_cmd(mic_name: str, output_path: str) -> list[str]:
    """Monta o comando ffmpeg usando DirectShow (dshow) para Windows."""
    return [
        "ffmpeg", "-y",
        "-f", "dshow",
        "-i", f"audio={mic_name}",
        "-ar", "16000",
        "-ac", "1",
        output_path,
    ]

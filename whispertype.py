"""
WhisperType - Ditado por voz com Whisper local para Windows
============================================================
Segure Ctrl+Espaço para gravar, solte para transcrever e colar.
Usa ffmpeg (dshow) para captura — não depende de PortAudio.

Dependências:
    pip install openai-whisper pyperclip keyboard pyautogui
    ffmpeg instalado e no PATH (já é requisito do Whisper)

"""

import logging
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import warnings

import torch
import keyboard
import pyautogui
import pyperclip
import whisper

# ─────────────────────────────────────────────
#  CONFIGURAÇÕES
# ─────────────────────────────────────────────
HOTKEY              = "ctrl+space"
MODEL_SIZE          = "small"   # tiny | base | small | medium | large
LANGUAGE            = "pt"     # "pt", "en", ou None (autodetectar)
PASTE_DELAY_SECONDS = 0.15     # pausa antes de colar para o foco estabilizar
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("WhisperType")

# Evita repetir o aviso do Whisper quando roda em CPU (FP32 em vez de FP16)
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")
warnings.filterwarnings("ignore", message="Performing inference on CPU when CUDA is available")


# ─────────────────────────────────────────────
#  DETECÇÃO DE MICROFONE
# ─────────────────────────────────────────────
def get_default_mic_name() -> str | None:
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


# ─────────────────────────────────────────────
#  CLASSE RECORDER
# ─────────────────────────────────────────────
class Recorder:
    def __init__(self, mic_name: str, model: whisper.Whisper):
        self._mic_name  = mic_name
        self._model     = model
        self._lock      = threading.Lock()
        self._recording = False
        self._process:  subprocess.Popen | None = None
        self._tmp_path: str | None = None

    # ── gravação ──────────────────────────────
    def start(self) -> None:
        with self._lock:
            if self._recording:
                return
            self._recording = True
            self._tmp_path  = self._make_tmp_wav()
            self._process   = self._spawn_ffmpeg(self._tmp_path)

        log.info("● Gravando... (solte para transcrever)")

    def stop(self) -> None:
        with self._lock:
            if not self._recording:
                return
            self._recording = False
            proc     = self._process
            wav_path = self._tmp_path
            self._process  = None
            self._tmp_path = None

        self._stop_ffmpeg(proc)
        threading.Thread(
            target=self._transcribe_and_paste,
            args=(wav_path,),
            daemon=True,
        ).start()

    @property
    def is_recording(self) -> bool:
        return self._recording

    # ── helpers privados ──────────────────────
    @staticmethod
    def _make_tmp_wav() -> str:
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.close()
        return tmp.name

    def _spawn_ffmpeg(self, output_path: str) -> subprocess.Popen:
        return subprocess.Popen(
            [
                "ffmpeg", "-y",
                "-f", "dshow",
                "-i", f"audio={self._mic_name}",
                "-ar", "16000",
                "-ac", "1",
                output_path,
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    @staticmethod
    def _stop_ffmpeg(proc: subprocess.Popen) -> None:
        try:
            proc.stdin.write(b"q")
            proc.stdin.flush()
            proc.wait(timeout=5)
        except Exception as e:
            log.warning("Erro ao parar ffmpeg graciosamente (%s) — forçando kill.", e)
            proc.kill()

    def _transcribe_and_paste(self, wav_path: str | None) -> None:
        if not wav_path or not os.path.exists(wav_path):
            log.warning("Nenhum áudio gravado.")
            return

        log.info("◌ Transcrevendo...")

        try:
            options = {"language": LANGUAGE} if LANGUAGE else {}
            result  = self._model.transcribe(wav_path, **options)
            text    = result["text"].strip()
        except Exception as e:
            log.error("Erro na transcrição: %s", e)
            return
        finally:
            os.unlink(wav_path)

        if not text:
            log.info("Nenhum texto detectado.")
            return

        log.info("✔ Texto: %s", text)
        pyperclip.copy(text)
        time.sleep(PASTE_DELAY_SECONDS)
        pyautogui.hotkey("ctrl", "v")


# ─────────────────────────────────────────────
#  PONTO DE ENTRADA
# ─────────────────────────────────────────────
def main() -> None:
    # Diagnóstico: o PyTorch enxerga a GPU?
    cuda_ok = torch.cuda.is_available()
    cuda_ver = torch.version.cuda if cuda_ok else None
    log.info(
        "PyTorch %s | CUDA disponível: %s%s",
        torch.__version__,
        cuda_ok,
        f" (versão: {cuda_ver})" if cuda_ver else "",
    )

    log.info("Carregando modelo Whisper '%s'...", MODEL_SIZE)
    model = whisper.load_model(MODEL_SIZE)
    device = str(model.device)
    if device == "cpu":
        log.info(
            "Modelo carregado (dispositivo: CPU). "
            "Para usar GPU: instale PyTorch com CUDA (veja README/requirements.txt)."
        )
    else:
        log.info("Modelo carregado (dispositivo: %s).", device)
    log.info("Atalho: %s | Idioma: %s", HOTKEY.upper(), LANGUAGE or "autodetectar")

    log.info("Detectando microfone...")
    mic_name = get_default_mic_name()
    if not mic_name:
        log.error("Nenhum microfone encontrado via ffmpeg. Verifique se o ffmpeg está no PATH.")
        sys.exit(1)
    log.info("Microfone: %s", mic_name)

    recorder = Recorder(mic_name=mic_name, model=model)

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


if __name__ == "__main__":
    main()

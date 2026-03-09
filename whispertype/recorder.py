import logging
import os
import subprocess
import tempfile
import threading
from typing import Callable

import whisper

from whispertype.config import LANGUAGE

log = logging.getLogger("WhisperType")


class Recorder:
    """
    Gerencia o ciclo de gravação → transcrição → colagem.

    Recebe duas funções injetadas para isolar o comportamento específico de cada OS:
      - build_ffmpeg_cmd: monta o comando ffmpeg adequado (dshow no Windows, pulse no Linux)
      - paste_fn:         cola o texto transcrito na janela focada
    """

    def __init__(
        self,
        mic_name: str,
        model: whisper.Whisper,
        build_ffmpeg_cmd: Callable[[str, str], list[str]],
        paste_fn: Callable[[str], None],
    ):
        self._mic_name        = mic_name
        self._model           = model
        self._build_ffmpeg_cmd = build_ffmpeg_cmd
        self._paste_fn        = paste_fn
        self._lock            = threading.Lock()
        self._recording       = False
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
        cmd = self._build_ffmpeg_cmd(self._mic_name, output_path)
        return subprocess.Popen(
            cmd,
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
        self._paste_fn(text)

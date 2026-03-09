import logging
import os
import subprocess
import tempfile
import threading
from typing import Callable

import whisper

from whispertype.config import LANGUAGE

log = logging.getLogger("WhisperType")

MIN_WAV_BYTES = 4096  # arquivos menores que isso indicam gravação vazia


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
        self._mic_name         = mic_name
        self._model            = model
        self._build_ffmpeg_cmd = build_ffmpeg_cmd
        self._paste_fn         = paste_fn
        self._lock             = threading.Lock()
        self._recording        = False
        self._process:  subprocess.Popen | None = None
        self._tmp_path: str | None = None
        self._ffmpeg_log: str | None = None   # arquivo temporário para stderr do ffmpeg

    # ── gravação ──────────────────────────────

    def start(self) -> None:
        with self._lock:
            if self._recording:
                return
            self._recording  = True
            self._tmp_path   = self._make_tmp_wav()
            self._process, self._ffmpeg_log = self._spawn_ffmpeg(self._tmp_path)

        log.info("● Gravando... (solte para transcrever)")

    def stop(self) -> None:
        with self._lock:
            if not self._recording:
                return
            self._recording = False
            proc        = self._process
            wav_path    = self._tmp_path
            ffmpeg_log  = self._ffmpeg_log
            self._process    = None
            self._tmp_path   = None
            self._ffmpeg_log = None

        self._stop_ffmpeg(proc, ffmpeg_log)
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

    def _spawn_ffmpeg(self, output_path: str) -> tuple[subprocess.Popen, str]:
        """Inicia o ffmpeg e retorna o processo e o caminho do log de erros."""
        cmd = self._build_ffmpeg_cmd(self._mic_name, output_path)

        # Stderr capturado em arquivo temporário para diagnóstico
        log_tmp = tempfile.NamedTemporaryFile(
            suffix=".txt", prefix="ffmpeg_", delete=False
        )
        log_tmp.close()

        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=open(log_tmp.name, "w"),
        )
        return proc, log_tmp.name

    def _stop_ffmpeg(self, proc: subprocess.Popen, ffmpeg_log: str | None) -> None:
        try:
            proc.stdin.write(b"q")
            proc.stdin.flush()
            proc.wait(timeout=5)
        except Exception as e:
            log.warning("Erro ao parar ffmpeg graciosamente (%s) — forçando kill.", e)
            proc.kill()
        finally:
            # Loga erros do ffmpeg se houver e apaga o arquivo de log
            if ffmpeg_log and os.path.exists(ffmpeg_log):
                try:
                    with open(ffmpeg_log) as f:
                        content = f.read().strip()
                    # Filtra linhas relevantes (erros e warnings, não o cabeçalho do ffmpeg)
                    errors = [
                        l for l in content.splitlines()
                        if any(tag in l for tag in ("Error", "error", "Invalid", "No such", "failed"))
                    ]
                    if errors:
                        log.warning("ffmpeg: %s", " | ".join(errors))
                except Exception:
                    pass
                finally:
                    os.unlink(ffmpeg_log)

    def _transcribe_and_paste(self, wav_path: str | None) -> None:
        if not wav_path or not os.path.exists(wav_path):
            log.warning("Nenhum áudio gravado.")
            return

        # Verifica se o arquivo tem conteúdo real
        file_size = os.path.getsize(wav_path)
        if file_size < MIN_WAV_BYTES:
            log.warning("Áudio gravado muito curto ou vazio (%d bytes). Verifique o microfone.", file_size)
            os.unlink(wav_path)
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

"""Utilities to bridge speech recognition and synthesis for the assistant."""
from __future__ import annotations

import base64
import tempfile
from pathlib import Path
from typing import Optional

try:
    import speech_recognition as sr
except ImportError:  # pragma: no cover - Optional dependency
    sr = None  # type: ignore

try:
    import pyttsx3
except ImportError:  # pragma: no cover - Optional dependency
    pyttsx3 = None  # type: ignore


class VoiceGateway:
    """Wrapper around third-party speech libraries used by the assistant."""

    def __init__(self) -> None:
        if sr is None or pyttsx3 is None:
            missing = []
            if sr is None:
                missing.append("speech_recognition")
            if pyttsx3 is None:
                missing.append("pyttsx3")
            self.available = False
            self._missing = ", ".join(missing)
        else:
            self.available = True
            self._recognizer = sr.Recognizer()
            self._engine = pyttsx3.init()

    @property
    def missing_dependencies(self) -> Optional[str]:
        if self.available:
            return None
        return self._missing

    def speech_to_text(self, audio_bytes: bytes) -> str:
        """Convert raw audio bytes to text using SpeechRecognition."""

        if not self.available or sr is None:
            raise RuntimeError(
                "Los paquetes de voz no están instalados: {0}".format(
                    self.missing_dependencies
                )
            )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            audio_file = sr.AudioFile(tmp.name)
        with audio_file as source:  # type: ignore[var-annotated]
            audio = self._recognizer.record(source)
        return self._recognizer.recognize_google(audio, language="es-ES")

    def text_to_speech(self, text: str) -> bytes:
        """Convert text to synthesized speech returning WAV bytes."""

        if not self.available or pyttsx3 is None:
            raise RuntimeError(
                "Los paquetes de voz no están instalados: {0}".format(
                    self.missing_dependencies
                )
            )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp_path = Path(tmp.name)
        self._engine.save_to_file(text, str(tmp_path))
        self._engine.runAndWait()
        data = tmp_path.read_bytes()
        tmp_path.unlink(missing_ok=True)
        return data

    def text_to_speech_base64(self, text: str) -> str:
        """Return synthesized speech encoded as base64 string."""

        audio_bytes = self.text_to_speech(text)
        return base64.b64encode(audio_bytes).decode("ascii")


__all__ = ["VoiceGateway"]

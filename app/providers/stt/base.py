from typing import Protocol


class STTResult:
    __slots__ = ("text", "language", "duration")

    def __init__(self, text: str, language: str = "", duration: float = 0.0) -> None:
        self.text = text
        self.language = language
        self.duration = duration


class STTProvider(Protocol):
    async def transcribe(self, audio_path: str) -> STTResult: ...

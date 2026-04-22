import openai

from app.providers.stt.base import STTResult
from app.config import WhisperConfig


class WhisperSTT:
    def __init__(self, config: WhisperConfig) -> None:
        self.config = config
        self._client = openai.AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=120,
        )

    async def transcribe(self, audio_path: str) -> STTResult:
        with open(audio_path, "rb") as audio_file:
            resp = await self._client.audio.transcriptions.create(
                model=self.config.model,
                file=audio_file,
                response_format="verbose_json",
                language="ru",
            )
        text = resp.text if hasattr(resp, "text") else str(resp)
        language = getattr(resp, "language", "") or ""
        duration = getattr(resp, "duration", 0.0) or 0.0
        return STTResult(text=text, language=language, duration=duration)

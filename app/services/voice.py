import logging

from aiogram.types import File

from app.providers.stt.base import STTProvider
from app.services.chat import ChatService
from app.utils.files import download_file, cleanup_file
from app.config import AppConfig
from app.utils.text import split_text

logger = logging.getLogger(__name__)


class VoiceService:
    def __init__(self, stt: STTProvider, chat_service: ChatService, config: AppConfig) -> None:
        self.stt = stt
        self.chat_service = chat_service
        self.config = config

    async def process_voice(
        self,
        user_id: int,
        voice_file: File,
        bot_file_download_url: str,
    ) -> tuple[str, list[str]]:
        audio_path = ""
        try:
            file_url = bot_file_download_url
            audio_path = await download_file(file_url, f"voice_{user_id}_{voice_file.file_id}.ogg")

            result = await self.stt.transcribe(audio_path)
            transcribed = result.text

            if not transcribed.strip():
                return "", ["⚠️ Не удалось распознать речь. Попробуйте ещё раз."]

            responses = await self.chat_service.chat(user_id, transcribed)
            return transcribed, responses

        except Exception as e:
            logger.error("Voice processing failed for user %s: %s", user_id, e)
            return "", ["❌ Что-то пошло не так. Попробуйте ещё раз — я уже разбираюсь."]
        finally:
            if audio_path:
                cleanup_file(audio_path)

    async def process_voice_stream(
        self,
        user_id: int,
        voice_file: File,
        bot_file_download_url: str,
    ) -> tuple[str, list[str]]:
        audio_path = ""
        try:
            file_url = bot_file_download_url
            audio_path = await download_file(file_url, f"voice_{user_id}_{voice_file.file_id}.ogg")

            result = await self.stt.transcribe(audio_path)
            transcribed = result.text

            if not transcribed.strip():
                return "", ["⚠️ Не удалось распознать речь. Попробуйте ещё раз."]

            # Stream the response
            full_response = []
            async for token in self.chat_service.chat_stream(user_id, transcribed):
                full_response.append(token)
                
            complete_text = "".join(full_response)
            responses = split_text(complete_text)
            return transcribed, responses

        except Exception as e:
            logger.error("Voice processing failed for user %s: %s", user_id, e)
            return "", ["❌ Что-то пошло не так. Попробуйте ещё раз — я уже разбираюсь."]
        finally:
            if audio_path:
                cleanup_file(audio_path)
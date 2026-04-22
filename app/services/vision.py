import logging

from app.providers.vision.base import VisionProvider
from app.services.chat import ChatService
from app.config import AppConfig

logger = logging.getLogger(__name__)


class VisionService:
    def __init__(self, vision: VisionProvider, chat_service: ChatService, config: AppConfig) -> None:
        self.vision = vision
        self.chat_service = chat_service
        self.config = config

    async def analyze_and_respond(
        self,
        user_id: int,
        image_path: str,
        caption: str = "",
    ) -> list[str]:
        try:
            prompt = caption if caption else ""
            result = await self.vision.analyze(image_path, prompt=prompt)

            description = result.description
            if not description:
                return ["⚠️ Не удалось проанализировать изображение."]

            if caption:
                combined = f"[Пользователь прислал фото с подписью: {caption}]\n\nОписание изображения:\n{description}\n\nОтветь на подпись или вопрос пользователя."
                responses = await self.chat_service.chat(user_id, combined)
            else:
                combined = f"[Пользователь прислал фото]\n\n{description}"
                responses = await self.chat_service.chat(user_id, combined)

            return responses

        except Exception as e:
            logger.error("Vision processing failed for user %s: %s", user_id, e)
            return ["❌ Что-то пошло не так. Попробуйте ещё раз — я уже разбираюсь."]

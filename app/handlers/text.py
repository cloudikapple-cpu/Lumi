import logging

from aiogram import Router, F
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from app.dependencies import Container
from app.utils.text import split_text

logger = logging.getLogger(__name__)

router = Router()

MENU_BUTTONS = {"🤖 Авто", "🎭 Режим", "⚙️ Настройки", "🗑 Очистить память", "❓ Помощь"}

@router.message(F.text, ~F.text.in_(MENU_BUTTONS))
async def handle_text(message: Message, container: Container) -> None:
    user_id = message.from_user.id
    text = message.text

    await container.user_settings.ensure_user(
        user_id=user_id,
        username=message.from_user.username or "",
        first_name=message.from_user.first_name or "",
        last_name=message.from_user.last_name or "",
    )

    # Send typing action while processing
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        try:
            # Try to stream the response first
            full_response = []
            level = "unknown"
            async for token in container.chat_service.chat_stream(user_id, text):
                full_response.append(token)
                
            complete_text = "".join(full_response)
            if not complete_text:
                await message.answer("Ничего не найдено")
                return
                
            # Split and send the response
            responses = split_text(complete_text)
            for part in responses:
                await message.answer(part, parse_mode="HTML")
                
        except Exception as e:
            logger.error("Text handler error for user %s: %s", user_id, e)
            await message.answer("❌ Что-то пошло не так. Попробуй ещё раз — я уже разбираюсь.", parse_mode="HTML")
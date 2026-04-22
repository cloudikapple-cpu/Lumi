import logging

from aiogram import Router, F
from aiogram.types import Message

from app.dependencies import Container

router = Router()
logger = logging.getLogger(__name__)

# Import MENU_BUTTONS from text handler
from app.handlers.text import MENU_BUTTONS

@router.message(F.voice)
async def handle_voice(message: Message, container: Container) -> None:
    user_id = message.from_user.id

    await container.user_settings.ensure_user(
        user_id=user_id,
        username=message.from_user.username or "",
        first_name=message.from_user.first_name or "",
        last_name=message.from_user.last_name or "",
    )

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        voice = message.voice
        file = await message.bot.get_file(voice.file_id)
        
        file_url = message.bot.session.api.file_url(
            file.file_path,
            bot_token=message.bot.token,
        )

        transcribed, responses = await container.voice_service.process_voice_stream(
            user_id=user_id,
            voice_file=file,
            bot_file_download_url=file_url,
        )

        if transcribed:
            await message.answer(f"🎤 Распознано: {transcribed}")

        for part in responses:
            await message.answer(part, parse_mode="HTML")

    except Exception as e:
        logger.error("Voice handler error for user %s: %s", user_id, e)
        await message.answer("❌ Что-то пошло не так. Попробуй ещё раз — я уже разбираюсь.", parse_mode="HTML")
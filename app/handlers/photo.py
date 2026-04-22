import logging

from aiogram import Router, F
from aiogram.types import Message

from app.dependencies import Container
from app.utils.files import download_file, cleanup_file

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.photo)
async def handle_photo(message: Message, container: Container) -> None:
    user_id = message.from_user.id

    await container.user_settings.ensure_user(
        user_id=user_id,
        username=message.from_user.username or "",
        first_name=message.from_user.first_name or "",
        last_name=message.from_user.last_name or "",
    )

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)

    file_url = message.bot.session.api.file_url(
        file.file_path,
        bot_token=message.bot.token,
    )

    image_path = ""
    try:
        image_path = await download_file(
            file_url,
            f"photo_{user_id}_{photo.file_id}.jpg",
        )

        caption = message.caption or ""
        responses = await container.vision_service.analyze_and_respond(
            user_id=user_id,
            image_path=image_path,
            caption=caption,
        )

        for part in responses:
            await message.answer(part, parse_mode="HTML")

    except Exception as e:
        logger.error("Photo handler error for user %s: %s", user_id, e)
        await message.answer("❌ Что-то пошло не так. Попробуй ещё раз — я уже разбираюсь.", parse_mode="HTML")
    finally:
        if image_path:
            cleanup_file(image_path)

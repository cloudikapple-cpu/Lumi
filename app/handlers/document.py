import logging

from aiogram import Router, F
from aiogram.types import Message

from app.dependencies import Container
from app.utils.files import download_file, cleanup_file, get_file_extension

router = Router()
logger = logging.getLogger(__name__)

TEXT_EXTENSIONS = {".txt", ".md", ".py", ".js", ".ts", ".json", ".csv", ".xml", ".html", ".css", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".log", ".sql", ".sh", ".bat", ".rs", ".go", ".java", ".c", ".cpp", ".h", ".rb", ".php"}

@router.message(F.document)
async def handle_document(message: Message, container: Container) -> None:
    user_id = message.from_user.id

    await container.user_settings.ensure_user(
        user_id=user_id,
        username=message.from_user.username or "",
        first_name=message.from_user.first_name or "",
        last_name=message.from_user.last_name or "",
    )

    doc = message.document
    ext = get_file_extension(doc.file_name or "")

    if ext not in TEXT_EXTENSIONS:
        await message.answer(
            f"📄 Файл <b>{doc.file_name}</b> не является текстовым.\n"
            "Я могу читать текстовые файлы: .txt, .py, .js, .json, .md и другие.",
            parse_mode="HTML",
        )
        return

    max_size = 2 * 1024 * 1024
    if doc.file_size and doc.file_size > max_size:
        await message.answer("📄 Файл слишком большой. Максимум — 2 МБ.")
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    file = await message.bot.get_file(doc.file_id)
    file_url = message.bot.session.api.file_url(
        file.file_path,
        bot_token=message.bot.token,
    )

    doc_path = ""
    try:
        doc_path = await download_file(file_url, f"doc_{user_id}_{doc.file_id}{ext}")

        with open(doc_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        if len(content) > 30000:
            content = content[:30000] + "\n\n[... файл обрезан ...]"

        prompt = (
            f"Пользователь прислал файл <b>{doc.file_name}</b>:\n\n"
            f"```\n{content}\n```\n\n"
            f"Проанализируй содержимое и ответь."
            if not message.caption
            else f"Файл <b>{doc.file_name}</b>:\n\n```\n{content}\n```\n\n{message.caption}"
        )

        responses = await container.chat_service.chat(user_id, prompt)
        for part in responses:
            await message.answer(part, parse_mode="HTML")

    except Exception as e:
        logger.error("Document handler error for user %s: %s", user_id, e)
        await message.answer("❌ Что-то пошло не так. Попробуй ещё раз — я уже разбираюсь.", parse_mode="HTML")
    finally:
        if doc_path:
            cleanup_file(doc_path)

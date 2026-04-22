from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from app.dependencies import Container
from app.keyboards.main import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, container: Container) -> None:
    await container.user_settings.ensure_user(
        user_id=message.from_user.id,
        username=message.from_user.username or "",
        first_name=message.from_user.first_name or "",
        last_name=message.from_user.last_name or "",
    )
    await message.answer(
        "👋 Привет! Я <b>Луми</b> — твой AI-ассистент с интеллектуальными уровнями.\n\n"
        "🧠 <b>Возможности:</b>\n"
        "• 🤖 Авто-режим: Сам выбирает уровень интеллекта\n"
        "• ⚡ Быстрый: Для простых вопросов и приветствий\n"
        "• 🧠 Умный: Для общих вопросов и объяснений\n"
        "• 🔮 Глубокий: Для сложных задач и анализа\n"
        "• 🎭 Режимы: Точный, Писатель, Математик и другие\n\n"
        "🎤 Распознаю голосовые\n"
        "🖼 Анализирую изображения\n"
        "🔍 Ищу информацию в интернете\n"
        "🧠 Запоминаю факты о тебе\n\n"
        "Выбери действие в меню или просто напиши мне!",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "📖 <b>Справка</b>\n\n"
        "💬 Просто напиши мне — я отвечу\n"
        "🎤 Отправь голосовое — я распознаю и отвечу\n"
        "🖼 Отправь фото — я проанализирую\n"
        "📄 Отправь документ — я прочитаю\n"
        "🔍 Начни с «найди» — я поищу в интернете\n\n"
        "<b>Команды:</b>\n"
        "/start — Начать заново\n"
        "/help — Эта справка\n"
        "/mode — Выбрать режим общения\n"
        "/settings — Настройки\n"
        "/clear — Очистить историю\n"
        "/facts — Мои факты о тебе\n",
        parse_mode="HTML",
    )


@router.message(F.text == "❓ Помощь")
async def menu_help(message: Message) -> None:
    await cmd_help(message)


@router.message(Command("mode"))
async def cmd_mode(message: Message, container: Container) -> None:
    from app.keyboards.main import mode_keyboard
    await message.answer("🎭 <b>Выбери режим общения:</b>", reply_markup=mode_keyboard(), parse_mode="HTML")


@router.message(F.text == "🎭 Режим")
async def menu_mode(message: Message, container: Container) -> None:
    await cmd_mode(message, container)


@router.message(Command("settings"))
async def cmd_settings(message: Message, container: Container) -> None:
    settings = await container.user_settings.get_all_settings(message.from_user.id)
    from app.keyboards.main import settings_keyboard
    await message.answer("⚙️ <b>Настройки:</b>", reply_markup=settings_keyboard(settings), parse_mode="HTML")


@router.message(F.text == "⚙️ Настройки")
async def menu_settings(message: Message, container: Container) -> None:
    await cmd_settings(message, container)


@router.message(Command("clear"))
async def cmd_clear(message: Message, container: Container) -> None:
    await container.dialog.clear_history(message.from_user.id)
    await message.answer("🗑 История диалога очищена.")


@router.message(F.text == "🗑 Очистить память")
async def menu_clear(message: Message, container: Container) -> None:
    from app.keyboards.main import confirm_keyboard
    await message.answer(
        "Что именно очистить?",
        reply_markup=confirm_keyboard("memory"),
    )


@router.message(Command("facts"))
async def cmd_facts(message: Message, container: Container) -> None:
    facts = await container.memory.get_all_facts_text(message.from_user.id)
    if not facts:
        await message.answer("Я пока ничего о тебе не запомнил. Общайся со мной — и я буду запоминать!")
    else:
        await message.answer(f"🧠 <b>Что я знаю о тебе:</b>\n\n{facts}", parse_mode="HTML")

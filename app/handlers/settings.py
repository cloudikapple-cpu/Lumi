import logging

from aiogram import Router, F, CallbackQuery

from app.dependencies import Container

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith("mode:"))
async def callback_mode(callback: CallbackQuery, container: Container) -> None:
    mode = callback.data.split(":", 1)[1]
    user_id = callback.from_user.id

    # Set the intelligence level based on the callback
    await container.user_settings.set_intelligence_level(user_id, mode)

    # Update the settings keyboard
    from app.keyboards.main import settings_keyboard
    settings = await container.user_settings.get_all_settings(user_id)
    await callback.message.edit_text("⚙️ Настройки обновлены!", reply_markup=settings_keyboard(settings))
    await callback.answer(f"Режим обновлён: {mode}")


@router.callback_query(F.data == "toggle:search")
async def callback_toggle_search(callback: CallbackQuery, container: Container) -> None:
    user_id = callback.from_user.id
    current = await container.user_settings.get_search_enabled(user_id)
    await container.user_settings.set_search_enabled(user_id, not current)

    from app.keyboards.main import settings_keyboard
    settings = await container.user_settings.get_all_settings(user_id)
    await callback.message.edit_text("⚙️ Настройки:", reply_markup=settings_keyboard(settings))
    status = "включён" if not current else "выключен"
    await callback.answer(f"Поиск {status}")


@router.callback_query(F.data == "toggle:voice")
async def callback_toggle_voice(callback: CallbackQuery, container: Container) -> None:
    user_id = callback.from_user.id
    current = await container.user_settings.get_voice_enabled(user_id)
    await container.user_settings.set_voice_enabled(user_id, not current)

    from app.keyboards.main import settings_keyboard
    settings = await container.user_settings.get_all_settings(user_id)
    await callback.message.edit_text("⚙️ Настройки:", reply_markup=settings_keyboard(settings))
    status = "включён" if not current else "выключен"
    await callback.answer(f"Голос {status}")


@router.callback_query(F.data.startswith("clear:"))
async def callback_clear(callback: CallbackQuery, container: Container) -> None:
    target = callback.data.split(":", 1)[1]

    if target == "history":
        await container.dialog.clear_history(callback.from_user.id)
        await callback.message.edit_text("🗑 История диалога очищена.")
        await callback.answer("История очищена")
    elif target == "facts":
        await container.memory.clear_facts(callback.from_user.id)
        await callback.message.edit_text("🗑 Факты о тебе удалены.")
        await callback.answer("Факты удалены")
    elif target == "all":
        await callback.message.edit_text(
            "⚠️ Удалить <b>все данные</b> (история + факты)?",
            reply_markup=confirm_keyboard("all"),
            parse_mode="HTML",
        )
        await callback.answer()


@router.callback_query(F.data.startswith("confirm:"))
async def callback_confirm(callback: CallbackQuery, container: Container) -> None:
    action = callback.data.split(":", 1)[1]
    user_id = callback.from_user.id

    if action == "all":
        await container.dialog.clear_history(user_id)
        await container.memory.clear_facts(user_id)
        await callback.message.edit_text("🗑 Все данные удалены.")
        await callback.answer("Всё очищено")

    elif action == "memory":
        await container.dialog.clear_history(user_id)
        await container.memory.clear_facts(user_id)
        await callback.message.edit_text("🗑 Вся память очищена.")
        await callback.answer("Память очищена")


@router.callback_query(F.data == "back:settings")
async def callback_back_settings(callback: CallbackQuery, container: Container) -> None:
    from app.keyboards.main import settings_keyboard
    settings = await container.user_settings.get_all_settings(callback.from_user.id)
    await callback.message.edit_text("⚙️ Настройки:", reply_markup=settings_keyboard(settings))
    await callback.answer()

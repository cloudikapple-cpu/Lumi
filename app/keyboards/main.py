from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from app.config import ChatMode, IntelligenceLevel


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="🤖 Авто"), KeyboardButton(text="🎭 Режим"))
    builder.row(KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="🗑 Очистить память"))
    builder.row(KeyboardButton(text="❓ Помощь"))
    return builder.as_markup(resize_keyboard=True)


def mode_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    modes = [
        ("🤖 Авто", "auto"),
        ("🎯 Точный", "precise"),
        ("✍️ Писатель", "tutor"),
        ("🔢 Математик", "coder"),
        ("🌍 Переводчик", "translator"),
        ("🧪 Учёный", "scientist"),
    ]
    for label, mode in modes:
        builder.button(text=f"{label}", callback_data=f"mode:{mode}")
    builder.adjust(2)
    return builder.as_markup()


def settings_keyboard(settings: dict) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⚙️ Настройки", callback_data="settings")
    builder.button(text="❓ Помощь", callback_data="help")
    builder.adjust(2)
    return builder.as_markup()


def confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да", callback_data=f"confirm:{action}")
    builder.button(text="❌ Нет", callback_data="cancel")
    builder.adjust(2)
    return builder.as_markup()


def settings_keyboard(settings: dict) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    search_status = "🟢" if settings.get("search_enabled", True) else "🔴"
    voice_status = "🟢" if settings.get("voice_enabled", True) else "🔴"
    builder.button(text=f"🔍 Поиск: {search_status}", callback_data="toggle:search")
    builder.button(text=f"🎤 Голос: {voice_status}", callback_data="toggle:voice")
    builder.button(text="🗑 Очистить историю", callback_data="clear:history")
    builder.button(text="🗑 Очистить факты", callback_data="clear:facts")
    builder.button(text="🗑 Очистить всё", callback_data="clear:all")
    builder.adjust(2)
    return builder.as_markup()


def search_toggle_keyboard(enabled: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    status = "🟢 Вкл" if enabled else "🔴 Выкл"
    builder.button(text=f"🔍 Поиск: {status}", callback_data="toggle:search")
    builder.button(text="🔙 Назад", callback_data="back:settings")
    builder.adjust(2)
    return builder.as_markup()


def confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да", callback_data=f"confirm:{action}")
    builder.button(text="❌ Нет", callback_data="back:settings")
    builder.adjust(2)
    return builder.as_markup()

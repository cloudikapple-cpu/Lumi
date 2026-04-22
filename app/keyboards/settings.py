from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def language_keyboard(current: str = "ru") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    langs = [("🇷🇺 Русский", "ru"), ("🇬🇧 English", "en"), ("🇺🇦 Українська", "uk")]
    for label, code in langs:
        marker = " ✅" if code == current else ""
        builder.button(text=f"{label}{marker}", callback_data=f"lang:{code}")
    builder.adjust(3)
    return builder.as_markup()

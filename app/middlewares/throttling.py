import logging
import time
from collections import defaultdict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

logger = logging.getLogger(__name__)


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 1.0) -> None:
        self.rate_limit = rate_limit
        self._last_call: dict[int, float] = defaultdict(float)

    async def __call__(self, handler, event: Message | CallbackQuery, data: dict) -> None:
        user_id = event.from_user.id if event.from_user else 0
        now = time.monotonic()

        if now - self._last_call[user_id] < self.rate_limit:
            if isinstance(event, Message):
                await event.answer("⏳ Слишком быстро. Подождите секунду.")
            return

        self._last_call[user_id] = now

        try:
            return await handler(event, data)
        except Exception as e:
            logger.error("Handler error for user %s: %s", user_id, e)
            if isinstance(event, Message):
                await event.answer("⚠️ Произошла ошибка. Попробуйте ещё раз.")
            elif isinstance(event, CallbackQuery):
                await event.answer("⚠️ Ошибка при обработке", show_alert=True)

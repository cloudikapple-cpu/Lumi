import logging
import time

from aiogram import BaseMiddleware
from aiogram.types import Message

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        user = event.from_user
        user_id = user.id if user else 0
        username = user.username if user else "unknown"
        text = event.text or event.caption or "[media]"
        start = time.monotonic()

        logger.info("→ [%s @%s] %s", user_id, username, text[:100])

        result = await handler(event, data)

        elapsed = time.monotonic() - start
        logger.info("← [%s] done in %.2fs", user_id, elapsed)

        return result

import logging
import traceback

from aiogram import Router
from aiogram.types import Update
from aiogram.exceptions import AiogramError

router = Router()
logger = logging.getLogger(__name__)


@router.error()
async def global_error_handler(event: Update, exception: Exception) -> None:
    logger.error(
        "Unhandled exception: %s\n%s",
        str(exception),
        traceback.format_exc(),
    )

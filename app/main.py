import asyncio
import logging
import sys

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from app.config import load_config
from app.dependencies import Container
from app.middlewares.throttling import ThrottlingMiddleware
from app.middlewares.logging import LoggingMiddleware
from app.handlers import start, text, voice, photo, document, settings, errors

class ContainerMiddleware:
    def __init__(self, container: Container) -> None:
        self.container = container

    async def __call__(self, handler, event, data: dict):
        data["container"] = self.container
        return await handler(event, data)

def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

def build_dispatcher(container: Container, config) -> Dispatcher:
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.message.middleware(ThrottlingMiddleware(config.rate_limit_seconds))
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware(config.rate_limit_seconds))

    container_mw = ContainerMiddleware(container)
    dp.message.middleware(container_mw)
    dp.callback_query.middleware(container_mw)

    dp.include_router(start.router)
    dp.include_router(text.router)
    dp.include_router(voice.router)
    dp.include_router(photo.router)
    dp.include_router(document.router)
    dp.include_router(settings.router)
    dp.include_router(errors.router)

    return dp

async def on_startup(bot: Bot, config) -> None:
    webhook_url = f"{config.webhook.base_url}{config.webhook.path}"
    await bot.set_webhook(
        url=webhook_url,
        secret_token=config.webhook.secret,
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True,
    )
    logging.getLogger("lumi").info("Webhook set: %s", webhook_url)

async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    logging.getLogger("lumi").info("Webhook deleted")

async def main() -> None:
    config = load_config()

    setup_logging(config.log_level)
    logger = logging.getLogger("lumi")

    if not config.bot.token:
        logger.critical("BOT_TOKEN is not set!")
        sys.exit(1)

    if not config.llm.nvidia.api_key:
        logger.critical("NVIDIA_API_KEY is not set!")
        sys.exit(1)

    container = Container(config)
    await container.init()
    logger.info("Database initialized")

    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = build_dispatcher(container, config)

    dp.startup.register(lambda b=bot: on_startup(b, config))
    dp.shutdown.register(lambda b=bot: on_shutdown(b))

    app = web.Application()
    handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=config.webhook.secret,
    )
    setup_application(app, dp, bot=bot)
    app.router.add_post(config.webhook.path, handler.handle_request)

    logger.info("Starting webhook server on port %s...", config.webhook.port)
    web.run_app(app, host="0.0.0.0", port=config.webhook.port)

if __name__ == "__main__":
    asyncio.run(main())
import os
import aiofiles
import aiohttp
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

TEMP_DIR = "data/tmp"


def ensure_temp_dir() -> str:
    os.makedirs(TEMP_DIR, exist_ok=True)
    return TEMP_DIR


async def download_file(url: str, filename: str | None = None, timeout: int = 60) -> str:
    ensure_temp_dir()
    if not filename:
        filename = url.split("/")[-1].split("?")[0] or "file"
    filepath = os.path.join(TEMP_DIR, filename)

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            async with aiofiles.open(filepath, "wb") as f:
                async for chunk in resp.content.iter_chunked(8192):
                    await f.write(chunk)

    return filepath


async def save_temp_file(data: bytes, filename: str) -> str:
    ensure_temp_dir()
    filepath = os.path.join(TEMP_DIR, filename)
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(data)
    return filepath


def cleanup_file(filepath: str) -> None:
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except OSError:
        pass


def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower() if filename else ""

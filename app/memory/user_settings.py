import logging

from app.database import Database
from app.config import ChatMode, IntelligenceLevel

logger = logging.getLogger(__name__)


class UserSettingsManager:
    def __init__(self, db: Database) -> None:
        self.db = db

    async def ensure_user(self, user_id: int, username: str = "", first_name: str = "", last_name: str = "") -> None:
        existing = await self.db.fetchone("SELECT user_id FROM users WHERE user_id = $1", user_id)
        if existing:
            await self.db.execute(
                "UPDATE users SET username = $1, first_name = $2, last_name = $3, last_seen = NOW() WHERE user_id = $4",
                username, first_name, last_name, user_id,
            )
        else:
            await self.db.execute(
                "INSERT INTO users (user_id, username, first_name, last_name) VALUES ($1, $2, $3, $4)",
                user_id, username, first_name, last_name,
            )
            await self.db.execute(
                "INSERT INTO user_settings (user_id) VALUES ($1) ON CONFLICT DO NOTHING",
                user_id,
            )

    async def get_chat_mode(self, user_id: int) -> str:
        row = await self.db.fetchone(
            "SELECT chat_mode FROM user_settings WHERE user_id = $1",
            user_id,
        )
        return row["chat_mode"] if row else ChatMode.DEFAULT.value

    async def set_chat_mode(self, user_id: int, mode: str) -> None:
        await self.db.execute(
            "INSERT INTO user_settings (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING",
            user_id,
        )
        await self.db.execute(
            "UPDATE user_settings SET chat_mode = $1 WHERE user_id = $2",
            mode, user_id,
        )

    async def get_intelligence_level(self, user_id: int) -> str:
        row = await self.db.fetchone(
            "SELECT intelligence_level FROM user_settings WHERE user_id = $1",
            user_id,
        )
        return row["intelligence_level"] if row else IntelligenceLevel.AUTO.value

    async def set_intelligence_level(self, user_id: int, level: str) -> None:
        await self.db.execute(
            "INSERT INTO user_settings (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING",
            user_id,
        )
        await self.db.execute(
            "UPDATE user_settings SET intelligence_level = $1 WHERE user_id = $2",
            level, user_id,
        )

    async def get_search_enabled(self, user_id: int) -> bool:
        row = await self.db.fetchone(
            "SELECT search_enabled FROM user_settings WHERE user_id = $1",
            user_id,
        )
        return bool(row["search_enabled"]) if row else True

    async def set_search_enabled(self, user_id: int, enabled: bool) -> None:
        await self.db.execute(
            "INSERT INTO user_settings (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING",
            user_id,
        )
        await self.db.execute(
            "UPDATE user_settings SET search_enabled = $1 WHERE user_id = $2",
            enabled, user_id,
        )

    async def get_voice_enabled(self, user_id: int) -> bool:
        row = await self.db.fetchone(
            "SELECT voice_enabled FROM user_settings WHERE user_id = $1",
            user_id,
        )
        return bool(row["voice_enabled"]) if row else True

    async def set_voice_enabled(self, user_id: int, enabled: bool) -> None:
        await self.db.execute(
            "INSERT INTO user_settings (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING",
            user_id,
        )
        await self.db.execute(
            "UPDATE user_settings SET voice_enabled = $1 WHERE user_id = $2",
            enabled, user_id,
        )

    async def get_language(self, user_id: int) -> str:
        row = await self.db.fetchone(
            "SELECT language FROM user_settings WHERE user_id = $1",
            user_id,
        )
        return row["language"] if row and row["language"] else "ru"

    async def set_language(self, user_id: int, language: str) -> None:
        await self.db.execute(
            "INSERT INTO user_settings (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING",
            user_id,
        )
        await self.db.execute(
            "UPDATE user_settings SET language = $1 WHERE user_id = $2",
            language, user_id,
        )

    async def get_system_prompt(self, user_id: int) -> str:
        row = await self.db.fetchone(
            "SELECT system_prompt FROM user_settings WHERE user_id = $1",
            user_id,
        )
        return row["system_prompt"] if row and row["system_prompt"] else ""

    async def set_system_prompt(self, user_id: int, prompt: str) -> None:
        await self.db.execute(
            "INSERT INTO user_settings (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING",
            user_id,
        )
        await self.db.execute(
            "UPDATE user_settings SET system_prompt = $1 WHERE user_id = $2",
            prompt, user_id,
        )

    async def get_all_settings(self, user_id: int) -> dict:
        row = await self.db.fetchone(
            "SELECT * FROM user_settings WHERE user_id = $1",
            user_id,
        )
        if not row:
            return {
                "chat_mode": ChatMode.DEFAULT.value,
                "search_enabled": True,
                "voice_enabled": True,
                "language": "ru",
                "system_prompt": "",
                "intelligence_level": IntelligenceLevel.AUTO.value,
            }
        return row

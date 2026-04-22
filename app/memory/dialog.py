from app.database import Database
from app.config import MemoryConfig
from app.providers.llm.base import LLMMessage


class DialogManager:
    def __init__(self, db: Database, config: MemoryConfig) -> None:
        self.db = db
        self.config = config

    async def add_message(self, user_id: int, role: str, content: str) -> None:
        await self.db.execute(
            "INSERT INTO dialog_messages (user_id, role, content) VALUES ($1, $2, $3)",
            user_id, role, content,
        )
        await self._trim_dialog(user_id)

    async def _trim_dialog(self, user_id: int) -> None:
        count = await self.db.fetchval(
            "SELECT COUNT(*) FROM dialog_messages WHERE user_id = $1",
            user_id,
        )
        if count and count > self.config.max_dialog_messages:
            excess = count - self.config.max_dialog_messages
            await self.db.execute(
                "DELETE FROM dialog_messages WHERE id IN ("
                "SELECT id FROM dialog_messages WHERE user_id = $1 ORDER BY created_at ASC LIMIT $2"
                ")",
                user_id, excess,
            )

    async def get_history(self, user_id: int, limit: int | None = None) -> list[LLMMessage]:
        effective_limit = limit or self.config.max_dialog_messages
        rows = await self.db.fetchall(
            "SELECT role, content FROM dialog_messages "
            "WHERE user_id = $1 ORDER BY created_at DESC LIMIT $2",
            user_id, effective_limit,
        )
        rows.reverse()
        return [LLMMessage(role=r["role"], content=r["content"]) for r in rows]

    async def clear_history(self, user_id: int) -> None:
        await self.db.execute("DELETE FROM dialog_messages WHERE user_id = $1", user_id)

    async def get_last_messages(self, user_id: int, count: int = 4) -> list[LLMMessage]:
        return await self.get_history(user_id, limit=count)

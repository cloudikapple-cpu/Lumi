import logging

from app.database import Database
from app.config import MemoryConfig

logger = logging.getLogger(__name__)


class MemoryStore:
    def __init__(self, db: Database, config: MemoryConfig) -> None:
        self.db = db
        self.config = config

    async def save_fact(self, user_id: int, fact: str, category: str = "general") -> None:
        existing = await self.db.fetchall(
            "SELECT id, fact FROM user_facts WHERE user_id = $1 AND category = $2",
            user_id, category,
        )
        for row in existing:
            if row["fact"].lower() == fact.lower():
                return

        count = await self.db.fetchval(
            "SELECT COUNT(*) FROM user_facts WHERE user_id = $1",
            user_id,
        )
        if count and count >= self.config.long_term_max_facts:
            await self.db.execute(
                "DELETE FROM user_facts WHERE id = ("
                "SELECT id FROM user_facts WHERE user_id = $1 ORDER BY created_at ASC LIMIT 1"
                ")",
                user_id,
            )

        await self.db.execute(
            "INSERT INTO user_facts (user_id, fact, category) VALUES ($1, $2, $3)",
            user_id, fact, category,
        )

    async def get_facts(self, user_id: int, category: str | None = None) -> list[str]:
        if category:
            rows = await self.db.fetchall(
                "SELECT fact FROM user_facts WHERE user_id = $1 AND category = $2 ORDER BY created_at DESC",
                user_id, category,
            )
        else:
            rows = await self.db.fetchall(
                "SELECT fact FROM user_facts WHERE user_id = $1 ORDER BY created_at DESC",
                user_id,
            )
        return [r["fact"] for r in rows]

    async def get_all_facts_text(self, user_id: int) -> str:
        facts = await self.get_facts(user_id)
        if not facts:
            return ""
        return "\n".join(f"- {f}" for f in facts)

    async def extract_and_save_facts(self, user_id: int, user_message: str, ai_response: str) -> None:
        factual_keywords = [
            "меня зовут", "я из", "я живу", "мне лет", "мой возраст",
            "я работаю", "моя работа", "я учусь", "мой университет",
            "моя профессия", "я люблю", "мне нравится", "мой любимый",
            "у меня есть", "я пишу на", "я программирую", "мой язык",
            "моя жена", "мой муж", "моя девушка", "мой парень",
            "мои дети", "мой ребёнок", "моя семья",
        ]
        msg_lower = user_message.lower()
        for kw in factual_keywords:
            if kw in msg_lower:
                await self.save_fact(user_id, user_message.strip(), "personal")
                break

    async def clear_facts(self, user_id: int) -> None:
        await self.db.execute("DELETE FROM user_facts WHERE user_id = $1", user_id)

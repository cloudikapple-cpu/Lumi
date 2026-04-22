import logging

from app.providers.search.base import SearchProvider
from app.providers.llm.base import LLMProvider, LLMMessage
from app.utils.prompts import build_search_query_prompt
from app.utils.text import format_search_context
from app.config import AppConfig

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(
        self,
        search_provider: SearchProvider,
        llm: LLMProvider,
        config: AppConfig,
    ) -> None:
        self.search_provider = search_provider
        self.llm = llm
        self.config = config

    async def _extract_search_query(self, user_query: str) -> str:
        try:
            prompt = build_search_query_prompt(user_query)
            messages = [LLMMessage(role="user", content=prompt)]
            response = await self.llm.complete(
                messages=messages,
                max_tokens=100,
                temperature=0.1,
                system_prompt="Ты конвертируешь запросы в поисковые. Выведи только поисковый запрос.",
            )
            return response.content.strip().strip('"\'')
        except Exception as e:
            logger.error("Search query extraction error: %s", e)
            return user_query  # Fallback to original query

    async def search(self, query: str, max_results: int | None = None) -> list:
        try:
            search_query = await self._extract_search_query(query)
            limit = max_results or self.config.search.tavily.max_results
            return await self.search_provider.search(search_query, limit)
        except Exception as e:
            logger.error("Search error: %s", e)
            return []

    async def search_and_format(self, query: str) -> str:
        try:
            results = await self.search(query)
            if not results:
                return ""
            return format_search_context(results)
        except Exception as e:
            logger.error("Search and format error: %s", e)
            return ""

    async def search_and_answer(self, query: str) -> str:
        try:
            results = await self.search(query)
            if not results:
                return "⚠️ Не удалось найти информацию по вашему запросу."

            context = format_search_context(results)
            messages = [
                LLMMessage(
                    role="user",
                    content=f"Найди ответ на вопрос, используя результаты поиска.\n\n"
                    f"Вопрос: {query}\n\n"
                    f"Результаты поиска:\n{context}",
                )
            ]
            response = await self.llm.complete(
                messages=messages,
                max_tokens=2048,
                temperature=0.3,
                system_prompt="Ответь на вопрос, используя найденную информацию. Укажи источники. Язык: русский.",
            )
            return response.content
        except Exception as e:
            logger.error("Search and answer error: %s", e)
            return "❌ Что-то пошло не так. Попробуйте ещё раз — я уже разбираюсь."

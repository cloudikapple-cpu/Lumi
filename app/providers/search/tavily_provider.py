import logging

import httpx

from app.providers.search.base import SearchResult
from app.config import TavilyConfig

logger = logging.getLogger(__name__)


class TavilySearch:
    API_URL = "https://api.tavily.com/search"

    def __init__(self, config: TavilyConfig) -> None:
        self.config = config
        self._http = httpx.AsyncClient(timeout=config.timeout)

    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        limit = max_results or self.config.max_results
        payload = {
            "api_key": self.config.api_key,
            "query": query,
            "max_results": limit,
            "search_depth": self.config.search_depth,
            "include_raw_content": self.config.include_raw_content,
        }
        try:
            resp = await self._http.post(self.API_URL, json=payload)
            resp.raise_for_status()
            data = resp.json()
            results = []
            for r in data.get("results", []):
                results.append(SearchResult(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    snippet=r.get("content", ""),
                    raw_content=r.get("raw_content", ""),
                ))
            return results
        except Exception as e:
            logger.error("Tavily search failed for '%s': %s", query, e)
            return []

    async def close(self) -> None:
        await self._http.aclose()

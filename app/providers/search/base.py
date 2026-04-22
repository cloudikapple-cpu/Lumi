from typing import Protocol


class SearchResult:
    __slots__ = ("title", "url", "snippet", "raw_content")

    def __init__(self, title: str, url: str, snippet: str, raw_content: str = "") -> None:
        self.title = title
        self.url = url
        self.snippet = snippet
        self.raw_content = raw_content


class SearchProvider(Protocol):
    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]: ...

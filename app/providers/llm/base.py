from typing import Protocol, AsyncIterator


class LLMMessage:
    __slots__ = ("role", "content")

    def __init__(self, role: str, content: str) -> None:
        self.role = role
        self.content = content

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}


class LLMResponse:
    __slots__ = ("content", "thinking", "usage", "model")

    def __init__(
        self,
        content: str,
        thinking: str = "",
        usage: dict | None = None,
        model: str = "",
    ) -> None:
        self.content = content
        self.thinking = thinking
        self.usage = usage or {}
        self.model = model


class LLMProvider(Protocol):
    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system_prompt: str | None = None,
    ) -> LLMResponse: ...

    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]: ...

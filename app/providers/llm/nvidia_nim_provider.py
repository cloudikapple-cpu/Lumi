from typing import AsyncIterator, List
import logging

import openai

from app.providers.llm.base import LLMProvider, LLMMessage, LLMResponse
from app.config import NvidiaNIMConfig, IntelligenceLevel

logger = logging.getLogger(__name__)


class NvidiaNIMLLM(LLMProvider):
    def __init__(self, config: NvidiaNIMConfig) -> None:
        self.config = config
        self._client = openai.AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
        )
        self.model = config.model

    def _build_messages(
        self,
        messages: list[LLMMessage],
        system_prompt: str | None = None,
    ) -> list[dict]:
        result = []
        if system_prompt:
            result.append({"role": "system", "content": system_prompt})
        result.extend(m.to_dict() for m in messages)
        return result

    def _extract_thinking(self, msg: object) -> str:
        thinking = ""
        if hasattr(msg, "reasoning_content") and msg.reasoning_content:
            thinking = msg.reasoning_content
        elif hasattr(msg, "content") and isinstance(msg.content, list):
            for part in msg.content:
                if isinstance(part, dict) and part.get("type") == "thinking":
                    thinking += part.get("thinking", "")
        return thinking

    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system_prompt: str | None = None,
    ) -> LLMResponse:
        try:
            built = self._build_messages(messages, system_prompt)
            resp = await self._client.chat.completions.create(
                model=self.config.model,
                messages=built,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            choice = resp.choices[0]
            content = choice.message.content or ""
            thinking = self._extract_thinking(choice.message)
            usage = {}
            if resp.usage:
                usage = {
                    "prompt_tokens": resp.usage.prompt_tokens,
                    "completion_tokens": resp.usage.completion_tokens,
                }
            return LLMResponse(
                content=content,
                thinking=thinking,
                usage=usage,
                model=resp.model,
            )
        except Exception as e:
            logger.error("NVIDIA NIM completion error: %s", e)
            raise

    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        try:
            built = self._build_messages(messages, system_prompt)
            stream = await self._client.chat.completions.create(
                model=self.config.model,
                messages=built,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )
            async for chunk in stream:
                choice = chunk.choices[0] if chunk.choices else None
                if not choice:
                    continue
                delta = choice.delta
                if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                    continue
                if delta.content:
                    yield delta.content
        except Exception as e:
            logger.error("NVIDIA NIM stream error: %s", e)
            raise

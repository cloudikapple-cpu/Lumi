import base64

import openai

from app.providers.vision.base import VisionResult
from app.config import VisionConfig


class OpenAIVision:
    def __init__(self, config: VisionConfig) -> None:
        self.config = config
        self._client = openai.AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=120,
        )

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _detect_mime(self, image_path: str) -> str:
        low = image_path.lower()
        if low.endswith(".png"):
            return "image/png"
        if low.endswith(".gif"):
            return "image/gif"
        if low.endswith(".webp"):
            return "image/webp"
        return "image/jpeg"

    async def analyze(self, image_path: str, prompt: str = "") -> VisionResult:
        b64 = self._encode_image(image_path)
        mime = self._detect_mime(image_path)

        default_prompt = (
            "Проанализируй это изображение подробно. "
            "Если на изображении есть текст — извлеки его. "
            "Опиши что ты видишь, выдели ключевые объекты и детали. "
            "Ответ на русском языке."
        )
        user_prompt = prompt or default_prompt

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"},
                    },
                ],
            }
        ]

        resp = await self._client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            max_tokens=2048,
        )
        content = resp.choices[0].message.content or ""
        return VisionResult(description=content)

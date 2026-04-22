from typing import Protocol


class VisionResult:
    __slots__ = ("description", "extracted_text", "objects")

    def __init__(
        self,
        description: str,
        extracted_text: str = "",
        objects: list[str] | None = None,
    ) -> None:
        self.description = description
        self.extracted_text = extracted_text
        self.objects = objects or []


class VisionProvider(Protocol):
    async def analyze(self, image_path: str, prompt: str = "") -> VisionResult: ...

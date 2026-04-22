import logging
from typing import AsyncIterator, List

from app.providers.llm.base import LLMProvider, LLMMessage, LLMResponse
from app.memory.store import MemoryStore
from app.memory.dialog import DialogManager
from app.memory.user_settings import UserSettingsManager
from app.utils.prompts import get_system_prompt
from app.utils.text import split_text
from app.config import AppConfig, IntelligenceLevel

logger = logging.getLogger(__name__)

SEARCH_TRIGGER_PHRASES = [
    "найди", "поиск", "узнай", "какой сейчас", "сколько сейчас",
    "что нового", "посмотри в интернете", "поищи", "найди в сети",
    "актуальная информация", "свежие данные", "latest", "search",
    "find", "look up", "what is the current",
]

DEEP_THINKING_TRIGGERS = [
    "почему", "докажи", "проанализируй", "объясни подробно", "сравни", "реши",
    "analyze", "solve", "compare", "math", "математика", "доказательство"
]

def determine_intelligence_level(text: str, current_level: str) -> str:
    """Determine the appropriate intelligence level based on message content."""
    if current_level != IntelligenceLevel.AUTO.value:
        return current_level
    
    # Auto logic implementation
    if len(text) < 50 and any(word in text.lower() for word in ["привет", "здравствуй", "добрый", "пока", "спасибо"]):
        return IntelligenceLevel.FAST.value  # ⚡ Быстрый
    
    if len(text) < 200 and not any(word in text.lower() for word in DEEP_THINKING_TRIGGERS):
        return IntelligenceLevel.SMART.value  # 🧠 Умный
    
    if len(text) > 200 or any(word in text.lower() for word in DEEP_THINKING_TRIGGERS):
        return IntelligenceLevel.DEEP.value  # 🔮 Глубокий
    
    return IntelligenceLevel.SMART.value  # 🧠 Умный default


class ChatService:
    def __init__(
        self,
        llm: LLMProvider,
        dialog: DialogManager,
        memory: MemoryStore,
        user_settings: UserSettingsManager,
        config: AppConfig,
    ) -> None:
        self.llm = llm
        self.dialog = dialog
        self.memory = memory
        self.user_settings = user_settings
        self.config = config

    def _should_search(self, text: str) -> bool:
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in SEARCH_TRIGGER_PHRASES)

    async def chat(self, user_id: int, text: str) -> tuple[str, List[str]]:
        try:
            # Get user settings
            intelligence_level = await self.user_settings.get_intelligence_level(user_id)
            chat_mode = await self.user_settings.get_chat_mode(user_id)
            facts = await self.memory.get_all_facts_text(user_id)
            
            # Determine actual intelligence level for Auto mode
            actual_level = determine_intelligence_level(text, intelligence_level)
            
            # Add level indicator for Auto mode
            level_indicator = ""
            if intelligence_level == IntelligenceLevel.AUTO.value:
                level_names = {
                    IntelligenceLevel.FAST.value: "⚡ Быстрый режим",
                    IntelligenceLevel.SMART.value: "🧠 Умный режим", 
                    IntelligenceLevel.DEEP.value: "🔮 Глубокий режим"
                }
                level_indicator = f"<i>{level_names.get(actual_level, '🤖 Режим')}</i>\n\n"
            
            system_prompt = get_system_prompt(chat_mode, "", facts)
            
            # Add message to dialog history
            await self.dialog.add_message(user_id, "user", text)
            history = await self.dialog.get_history(user_id)
            
            # Generate response based on intelligence level
            if actual_level == IntelligenceLevel.FAST.value:
                # Fast response - shorter, more direct
                response = await self.llm.complete(
                    messages=history,
                    max_tokens=512,
                    temperature=0.3,
                    system_prompt=system_prompt
                )
            elif actual_level == IntelligenceLevel.SMART.value:
                # Smart response - balanced
                response = await self.llm.complete(
                    messages=history,
                    max_tokens=2048,
                    temperature=0.7,
                    system_prompt=system_prompt
                )
            else:  # Deep/Thinking mode
                response = await self.llm.complete(
                    messages=history,
                    max_tokens=4096,
                    temperature=0.8,
                    system_prompt=system_prompt
                )
            
            # Add response to dialog history
            await self.dialog.add_message(user_id, "assistant", response.content)
            
            # Extract and save facts
            await self.memory.extract_and_save_facts(user_id, text, response.content)
            
            # Add level indicator to response
            full_response = level_indicator + response.content if level_indicator else response.content
            
            return actual_level, split_text(full_response)
            
        except Exception as e:
            logger.error("Chat service error for user %s: %s", user_id, e)
            return "error", ["❌ Что-то пошло не так. Попробуй ещё раз — я уже разбираюсь."]

    async def chat_stream(self, user_id: int, text: str) -> AsyncIterator[str]:
        try:
            # Get user settings
            intelligence_level = await self.user_settings.get_intelligence_level(user_id)
            chat_mode = await self.user_settings.get_chat_mode(user_id)
            facts = await self.memory.get_all_facts_text(user_id)
            
            # Determine actual intelligence level for Auto mode
            actual_level = determine_intelligence_level(text, intelligence_level)
            
            # Add level indicator for Auto mode
            level_indicator = ""
            if intelligence_level == IntelligenceLevel.AUTO.value:
                level_names = {
                    IntelligenceLevel.FAST.value: "⚡ Быстрый режим",
                    IntelligenceLevel.SMART.value: "🧠 Умный режим",
                    IntelligenceLevel.DEEP.value: "🔮 Глубокий режим"
                }
                level_indicator = f"<i>{level_names.get(actual_level, '🤖 Режим')}</i>\n\n"
                yield level_indicator
            
            system_prompt = get_system_prompt(chat_mode, "", facts)
            
            # Add message to dialog history
            await self.dialog.add_message(user_id, "user", text)
            history = await self.dialog.get_history(user_id)
            
            # Generate streaming response based on intelligence level
            if actual_level == IntelligenceLevel.FAST.value:
                # Fast response - shorter, more direct
                async for token in self.llm.stream(
                    messages=history,
                    max_tokens=512,
                    temperature=0.3,
                    system_prompt=system_prompt
                ):
                    yield token
            elif actual_level == IntelligenceLevel.SMART.value:
                # Smart response - balanced
                async for token in self.llm.stream(
                    messages=history,
                    max_tokens=2048,
                    temperature=0.7,
                    system_prompt=system_prompt
                ):
                    yield token
            else:  # Deep/Thinking mode
                async for token in self.llm.stream(
                    messages=history,
                    max_tokens=4096,
                    temperature=0.8,
                    system_prompt=system_prompt
                ):
                    yield token
            
            # Add response to dialog history
            # (We would need to collect the full response for this)
            
        except Exception as e:
            logger.error("Chat service stream error for user %s: %s", user_id, e)
            yield "❌ Что-то пошло не так. Попробуй ещё раз — я уже разбираюсь."

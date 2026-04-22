from app.config import AppConfig
from app.database import Database
from app.redis_client import RedisClient
from app.memory.user_settings import UserSettingsManager
from app.memory.dialog import DialogManager
from app.memory.store import MemoryStore
from app.services.chat import ChatService
from app.services.voice import VoiceService
from app.services.vision import VisionService
from app.services.search import SearchService
from app.providers.llm.nvidia_nim_provider import NvidiaNIMLLM
from app.providers.stt.whisper_provider import WhisperSTT
from app.providers.vision.openai_vision import OpenAIVision
from app.providers.search.tavily_provider import TavilySearch


class Container:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.db = Database(config.db)
        self.redis = RedisClient(config.redis)
        
        # Initialize managers and services as None, they will be created in init()
        self.user_settings = None
        self.dialog = None
        self.memory = None
        self.chat_service = None
        self.voice_service = None
        self.vision_service = None
        self.search_service = None
        self.llm = None
        self.stt = None
        self.vision = None
        self.search = None

    async def init(self) -> None:
        await self.db.init()
        await self.redis.init()
        
        # Initialize managers
        self.user_settings = UserSettingsManager(self.db)
        self.dialog = DialogManager(self.db, self.config.memory)
        self.memory = MemoryStore(self.db, self.config.memory)
        
        # Initialize providers
        self.llm = NvidiaNIMLLM(self.config.llm.nvidia)
        self.stt = WhisperSTT(self.config.whisper)
        self.vision = OpenAIVision(self.config.vision)
        self.search = TavilySearch(self.config.search.tavily) if self.config.search.enabled else None
        
        # Initialize services
        self.chat_service = ChatService(
            self.llm, 
            self.dialog, 
            self.memory, 
            self.user_settings, 
            self.config
        )
        self.voice_service = VoiceService(self.stt, self.chat_service, self.config)
        self.vision_service = VisionService(self.vision, self.chat_service, self.config)
        self.search_service = SearchService(self.search, self.llm, self.config) if self.search else None

    async def close(self) -> None:
        await self.db.close()
        await self.redis.close()
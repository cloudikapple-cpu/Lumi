import os
from dataclasses import dataclass, field
from enum import Enum
from dotenv import load_dotenv


class IntelligenceLevel(str, Enum):
    AUTO = "auto"
    FAST = "fast"  # ⚡ Быстрый
    SMART = "smart"  # 🧠 Умный
    DEEP = "deep"  # 🔮 Глубокий
    THINKING = "thinking"  # 🔮 Глубокий (thinking mode)


class ChatMode(str, Enum):
    DEFAULT = "default"
    CREATIVE = "creative"
    PRECISE = "precise"
    TUTOR = "tutor"
    CODER = "coder"


@dataclass
class BotConfig:
    token: str
    parse_mode: str = "HTML"


@dataclass
class WebhookConfig:
    use_webhook: bool = True
    base_url: str = ""
    path: str = "/webhook"
    port: int = 8000
    secret: str = ""


@dataclass
class NvidiaNIMConfig:
    api_key: str = ""
    model: str = "moonshotai/kimi-k2-thinking"
    base_url: str = "https://integrate.api.nvidia.com/v1"
    max_tokens: int = 16384
    temperature: float = 0.6
    timeout: int = 300


@dataclass
class LLMConfig:
    nvidia: NvidiaNIMConfig = field(default_factory=NvidiaNIMConfig)
    max_tokens: int = 16384
    temperature: float = 0.6
    timeout: int = 300


@dataclass
class WhisperConfig:
    api_key: str = ""
    model: str = "whisper-large-v3-turbo"
    base_url: str | None = "https://api.groq.com/openai/v1"


@dataclass
class VisionConfig:
    api_key: str = ""
    model: str = "gpt-4o"
    base_url: str | None = None
    max_image_size_mb: int = 20


@dataclass
class TavilyConfig:
    api_key: str = ""
    max_results: int = 5
    search_depth: str = "advanced"
    include_raw_content: bool = False
    timeout: int = 30


@dataclass
class SearchConfig:
    enabled: bool = True
    tavily: TavilyConfig = field(default_factory=TavilyConfig)


@dataclass
class MemoryConfig:
    max_dialog_messages: int = 50
    short_term_ttl_hours: int = 24
    long_term_max_facts: int = 100


@dataclass
class DBConfig:
    dsn: str = "postgresql://postgres:postgres@localhost:5432/lumi"
    pool_min: int = 2
    pool_max: int = 10


@dataclass
class RedisConfig:
    url: str = "redis://localhost:6379/0"
    max_connections: int = 20
    ttl_seconds: int = 3600  # 1 hour default cache


@dataclass
class AppConfig:
    bot: BotConfig
    webhook: WebhookConfig
    llm: LLMConfig
    whisper: WhisperConfig
    vision: VisionConfig
    search: SearchConfig
    memory: MemoryConfig
    db: DBConfig
    redis: RedisConfig = field(default_factory=RedisConfig)
    log_level: str = "INFO"
    rate_limit_seconds: float = 1.0


def load_config() -> AppConfig:
    load_dotenv()

    nvidia_key = os.getenv("NVIDIA_API_KEY", "")
    whisper_key = os.getenv("GROQ_API_KEY", "")  # Обновлено на GROQ_API_KEY
    vision_key = os.getenv("VISION_API_KEY", "")

    use_webhook = os.getenv("USE_WEBHOOK", "true").lower() == "true"
    base_url = os.getenv("WEBHOOK_BASE_URL", os.getenv("RAILWAY_PUBLIC_DOMAIN", ""))
    if base_url and not base_url.startswith("http"):
        base_url = f"https://{base_url}"

    webhook_secret = os.getenv("WEBHOOK_SECRET", "")
    if not webhook_secret and nvidia_key:
        webhook_secret = nvidia_key[:16]

    return AppConfig(
        bot=BotConfig(
            token=os.getenv("BOT_TOKEN", ""),
        ),
        webhook=WebhookConfig(
            use_webhook=use_webhook,
            base_url=base_url,
            path=os.getenv("WEBHOOK_PATH", "/webhook"),
            port=int(os.getenv("PORT", "8000")),
            secret=webhook_secret,
        ),
        llm=LLMConfig(
            nvidia=NvidiaNIMConfig(
                api_key=nvidia_key,
                model=os.getenv("NVIDIA_MODEL", "moonshotai/kimi-k2-thinking"),
                base_url=os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"),
                max_tokens=int(os.getenv("NVIDIA_MAX_TOKENS", "16384")),
                temperature=float(os.getenv("NVIDIA_TEMPERATURE", "0.6")),
                timeout=int(os.getenv("NVIDIA_TIMEOUT", "300")),
            ),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "16384")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.6")),
            timeout=int(os.getenv("LLM_TIMEOUT", "300")),
        ),
        whisper=WhisperConfig(
            api_key=whisper_key,
            model=os.getenv("WHISPER_MODEL", "whisper-large-v3-turbo"),
            base_url=os.getenv("WHISPER_BASE_URL", "https://api.groq.com/openai/v1") or None,
        ),
        vision=VisionConfig(
            api_key=vision_key,
            model=os.getenv("VISION_MODEL", "gpt-4o"),
            base_url=os.getenv("VISION_BASE_URL") or None,
            max_image_size_mb=int(os.getenv("MAX_IMAGE_SIZE_MB", "20")),
        ),
        search=SearchConfig(
            enabled=os.getenv("SEARCH_ENABLED", "true").lower() == "true",
            tavily=TavilyConfig(
                api_key=os.getenv("TAVILY_API_KEY", ""),
                max_results=int(os.getenv("TAVILY_MAX_RESULTS", "5")),
                search_depth=os.getenv("TAVILY_SEARCH_DEPTH", "advanced"),
                include_raw_content=os.getenv("TAVILY_INCLUDE_RAW", "false").lower() == "true",
                timeout=int(os.getenv("TAVILY_TIMEOUT", "30")),
            ),
        ),
        memory=MemoryConfig(
            max_dialog_messages=int(os.getenv("MAX_DIALOG_MESSAGES", "50")),
            short_term_ttl_hours=int(os.getenv("SHORT_TERM_TTL_HOURS", "24")),
            long_term_max_facts=int(os.getenv("LONG_TERM_MAX_FACTS", "100")),
        ),
        db=DBConfig(
            dsn=os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/lumi"),
            pool_min=int(os.getenv("DB_POOL_MIN", "2")),
            pool_max=int(os.getenv("DB_POOL_MAX", "10")),
        ),
        redis=RedisConfig(
            url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "20")),
            ttl_seconds=int(os.getenv("REDIS_TTL_SECONDS", "3600")),
        ),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        rate_limit_seconds=float(os.getenv("RATE_LIMIT_SECONDS", "1.0")),
    )
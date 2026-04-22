# Lumi — AI Telegram Bot

Умный Telegram-бот с поддержкой текста, голоса, изображений, поиска и памяти.

## Возможности

- Текстовый чат с Kimi-K2-Thinking через NVIDIA NIM
- Распознавание голосовых сообщений (Whisper)
- Анализ изображений (Vision)
- Интернет-поиск (Tavily)
- Память пользователя (факты, история диалога)
- 5 режимов общения: Обычный, Креативный, Точный, Наставник, Кодер
- Настройки: поиск вкл/выкл, голос вкл/выкл
- Rate limiting, логирование, обработка ошибок

## Запуск локально

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Заполни .env своими ключами

python -m app.main
```

## Запуск через Docker

```bash
cp .env.example .env
# Заполни .env своими ключами

docker compose up -d
```

## Deploy на Railway

1. Создай проект на [railway.app](https://railway.app/)
2. Добавь PostgreSQL из шаблонов Railway
3. В настройках проекта Railway:
   - Укажи переменные окружения из `.env.example`
   - Установи `DATABASE_URL` из PostgreSQL сервиса
   - Установи `WEBHOOK_BASE_URL` на домен Railway
   - Установи `PORT` на 8000
4. Railway автоматически откроет порт 8000 и настроит webhook

## Переменные окружения

| Переменная | Описание | По умолчанию |
|---|---|---|
| `BOT_TOKEN` | Telegram Bot Token | — |
| `NVIDIA_API_KEY` | NVIDIA NIM API Key | — |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` |
| `WEBHOOK_BASE_URL` | URL для webhook (Railway domain) | — |
| `PORT` | Порт сервера | `8000` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |
| `ADMIN_IDS` | ID админов через запятую | — |

## Архитектура

```
Telegram (aiogram 3.x)
    → Handlers (router)
        → Services (ChatService, VoiceService, VisionService, SearchService)
            → Providers (NvidiaNIMLLM, WhisperSTT, OpenAIVision, TavilySearch)
            → Memory (DialogManager, MemoryStore, UserSettingsManager)
                → Database (asyncpg + PostgreSQL)
```

## Что улучшить дальше

- Redis для кэширования и rate limiting
- Админ-панель с аналитикой
- Метрики (Prometheus)
- Очередь задач (Celery/RQ) для тяжёлых операций
- Мультиязычность (i18n)
- Поддержка видеосообщений (кружков)
- TTS — ответы голосом
- RAG — индексация документов пользователя
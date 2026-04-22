-- Init schema for Lumi Bot (PostgreSQL)

CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    language TEXT DEFAULT 'ru',
    chat_mode TEXT DEFAULT 'default',
    search_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dialog_messages (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_facts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    fact TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_settings (
    user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    chat_mode TEXT DEFAULT 'default',
    search_enabled BOOLEAN DEFAULT TRUE,
    voice_enabled BOOLEAN DEFAULT TRUE,
    language TEXT DEFAULT 'ru',
    system_prompt TEXT DEFAULT '',
    intelligence_level TEXT DEFAULT 'auto'
);

CREATE INDEX IF NOT EXISTS idx_dialog_user ON dialog_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_dialog_created ON dialog_messages(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_facts_user ON user_facts(user_id);

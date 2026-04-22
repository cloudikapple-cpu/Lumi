import logging
import asyncio

import asyncpg

from app.config import DBConfig

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, config: DBConfig) -> None:
        self.config = config
        self._pool: asyncpg.Pool | None = None

    @property
    def pool(self) -> asyncpg.Pool:
        if self._pool is None:
            raise RuntimeError("Database not initialized. Call init() first.")
        return self._pool

    async def init(self) -> None:
        self._pool = await asyncpg.create_pool(
            dsn=self.config.dsn,
            min_size=self.config.pool_min,
            max_size=self.config.pool_max,
        )
        await self._run_migrations()
        logger.info("Database pool created and migrations applied")

    async def _run_migrations(self) -> None:
        # Read and execute the init.sql migration file
        try:
            with open("migrations/init.sql", "r", encoding="utf-8") as f:
                migration_sql = f.read()
            
            # Split by semicolon and execute each statement
            statements = [s.strip() for s in migration_sql.split(';') if s.strip()]
            
            async with self.pool.acquire() as conn:
                for statement in statements:
                    if statement.strip():
                        await conn.execute(statement)
                        
            logger.info("Database migrations applied successfully")
        except Exception as e:
            logger.error("Failed to apply database migrations: %s", e)
            raise

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def execute(self, query: str, *args) -> str:
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetchval(self, query: str, *args) -> any:
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    async def fetchone(self, query: str, *args) -> dict | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None

    async def fetchall(self, query: str, *args) -> list[dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(r) for r in rows]
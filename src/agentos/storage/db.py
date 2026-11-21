from psycopg_pool import AsyncConnectionPool

from agentos.config import settings

pool =AsyncConnectionPool(
    conninfo=settings.database_url,
    min_size=1,
    max_size=10,
    open=False,
)

async def open_pool()->None:
    await pool.open()

async def close_pool()->None:
    await pool.close()
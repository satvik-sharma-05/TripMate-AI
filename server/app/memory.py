"""Chooses where LangGraph saves paused conversations (checkpoints).

- DATABASE_URL set -> PostgreSQL (survives restarts, works with many servers).
- not set          -> RAM (simple for local demos; lost on restart).
"""
from contextlib import asynccontextmanager

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool  # reuses DB connections across requests

from app.config import DATABASE_URL


@asynccontextmanager
async def open_checkpointer():
    if not DATABASE_URL:
        yield InMemorySaver()
        return
    kwargs = {"autocommit": True, "row_factory": dict_row, "prepare_threshold": 0}
    async with AsyncConnectionPool(DATABASE_URL, kwargs=kwargs) as pool:
        saver = AsyncPostgresSaver(pool)
        await saver.setup()  # creates the checkpoint tables the first time
        yield saver

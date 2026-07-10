"""
Background cleanup task — runs every 5 minutes and removes expired sessions.
Launched via FastAPI's lifespan context manager in main.py.
"""

import asyncio

from app.config import SESSION_TTL_HOURS
from app.logger import get_logger
from app.session_manager import session_manager

logger = get_logger("cleanup")

_CLEANUP_INTERVAL_SECONDS = 300  # 5 minutes


async def session_cleanup_loop() -> None:
    """
    Indefinitely running coroutine.
    Every _CLEANUP_INTERVAL_SECONDS it evicts sessions older than SESSION_TTL_HOURS.
    """
    logger.info(
        "Session cleanup loop started "
        f"(interval={_CLEANUP_INTERVAL_SECONDS}s, ttl={SESSION_TTL_HOURS}h)"
    )
    while True:
        await asyncio.sleep(_CLEANUP_INTERVAL_SECONDS)
        try:
            removed = session_manager.cleanup_expired(SESSION_TTL_HOURS)
            if removed:
                logger.info(f"Cleanup: evicted {removed} expired session(s)")
            else:
                logger.info("Cleanup: no expired sessions found")
        except Exception as exc:
            logger.error(f"Cleanup error: {exc}")

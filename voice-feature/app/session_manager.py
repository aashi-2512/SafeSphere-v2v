from collections import deque
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from app.config import SESSION_TTL_HOURS, RING_BUFFER_SIZE


class SessionManager:
    """
    In-memory store for all active emergency sessions.

    Each session record:
        created_at        datetime    when the SOS was triggered
        user_id           str | None  who triggered the SOS
        lat / lng         float|None  GPS location of the SOS trigger
        broadcaster       WebSocket   the victim's audio stream socket
        broadcaster_alive bool        True while broadcaster is streaming
        listeners         set         set of active listener WebSockets
        ring_buffer       deque       last N audio chunks (for late joiners)
        status            str         'active' | 'ended'
    """

    def __init__(self):
        self.sessions: dict = {}

    # ── Creation ──────────────────────────────────────────────────────────────

    def create_session(
        self,
        user_id: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        phone: Optional[str] = None,
    ) -> str:
        """Create a new emergency session and return its UUID."""
        session_id = str(uuid4())
        self.sessions[session_id] = {
            "created_at": datetime.utcnow(),
            "user_id": user_id,
            "phone": phone or "",
            "lat": lat,
            "lng": lng,
            "broadcaster": None,
            "broadcaster_alive": False,
            "listeners": set(),
            "ring_buffer": deque(maxlen=RING_BUFFER_SIZE),
            "status": "active",
        }
        return session_id

    # ── Retrieval ─────────────────────────────────────────────────────────────

    def get_session(self, session_id: str) -> Optional[dict]:
        """Return the session dict, or None if it doesn't exist."""
        return self.sessions.get(session_id)

    def session_exists(self, session_id: str) -> bool:
        return session_id in self.sessions

    def get_listener_count(self, session_id: str) -> int:
        session = self.sessions.get(session_id)
        return len(session["listeners"]) if session else 0

    def list_active_sessions(self) -> list:
        """Return a JSON-serialisable summary of every active session."""
        result = []
        for sid, s in self.sessions.items():
            result.append({
                "session_id": sid,
                "user_id": s.get("user_id"),
                "phone": s.get("phone", ""),
                "created_at": s["created_at"].isoformat(),
                "listener_count": len(s["listeners"]),
                "broadcaster_connected": s.get("broadcaster") is not None,
                "broadcaster_alive": s.get("broadcaster_alive", False),
                "lat": s.get("lat"),
                "lng": s.get("lng"),
                "status": s.get("status", "active"),
            })
        return result

    # ── Deletion / cleanup ────────────────────────────────────────────────────

    def delete_session(self, session_id: str) -> None:
        """Remove a session completely."""
        self.sessions.pop(session_id, None)

    def cleanup_expired(self, ttl_hours: Optional[int] = None) -> int:
        """
        Remove sessions older than ttl_hours.
        Returns the number of sessions removed.
        """
        ttl = ttl_hours if ttl_hours is not None else SESSION_TTL_HOURS
        cutoff = datetime.utcnow() - timedelta(hours=ttl)
        expired = [
            sid
            for sid, s in self.sessions.items()
            if s["created_at"] < cutoff
        ]
        for sid in expired:
            del self.sessions[sid]
        return len(expired)


# ── Singleton ─────────────────────────────────────────────────────────────────
session_manager = SessionManager()
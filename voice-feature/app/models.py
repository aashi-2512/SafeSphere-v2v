from pydantic import BaseModel
from typing import Optional, List


# ── Session / SOS models ──────────────────────────────────────────────────────

class SessionResponse(BaseModel):
    """Legacy response model — kept for backward compatibility."""
    session_id: str
    broadcaster_token: str
    listener_token: str


class SOSRequest(BaseModel):
    """
    Payload sent by the victim's device when they trigger an SOS.

    contact_ids: list of user IDs the victim registered as emergency contacts
                 at signup. In a production system these would be looked up
                 in a database and push-notified with the listener_token.
    """
    user_id: str
    lat: float
    lng: float
    contact_ids: Optional[List[str]] = []


class SOSResponse(BaseModel):
    """
    Returned after a successful SOS trigger.

    broadcaster_token  → victim's device uses this to stream audio via WS
    listener_token     → shared token sent to all emergency contacts so they
                         can connect to /ws/listen and hear the audio live
    """
    session_id: str
    broadcaster_token: str
    listener_token: str
    user_id: str
    lat: float
    lng: float
    alert_time: str
    message: str


class SessionStatusResponse(BaseModel):
    """Live status snapshot of an emergency session."""
    session_id: str
    is_live: bool                     # True if broadcaster is currently streaming
    listener_count: int               # Number of contacts actively listening
    broadcaster_connected: bool       # True if broadcaster WebSocket is open
    created_at: str
    user_id: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


# ── Safety-map / route models ─────────────────────────────────────────────────

class RouteRequest(BaseModel):
    """
    Request body for POST /safety/route.

    start / end: either a Mumbai address string ("Andheri Station, Mumbai")
                 or a "lat,lng" coordinate string ("19.119,72.847")
    time_bucket: optional override — 'day' | 'evening' | 'night'
                 defaults to current local time if omitted
    """
    start: str
    end: str
    time_bucket: Optional[str] = None
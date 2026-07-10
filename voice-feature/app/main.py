"""
SafeSphere Emergency Backend — main entry point.

Exposes:
    REST  POST   /sos                       Trigger an SOS emergency session
    REST  GET    /session/{id}/status       Live session status (listener count etc.)
    REST  DELETE /session/{id}              End a session
    REST  GET    /sessions                  List all active sessions (admin)

    REST  GET    /safety/score?lat=&lng=    Safety score for a GPS point
    REST  POST   /safety/route              Safest walking route between two places
    REST  GET    /safety/hexagons           Full hexagon GeoJSON for map rendering

    WS    /ws/broadcast?token=...           Victim streams audio
    WS    /ws/listen?token=...              Emergency contacts receive audio
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.auth import create_token
from app.cleanup import session_cleanup_loop
from app.logger import get_logger
from app.models import (
    SessionResponse,
    SessionStatusResponse,
    SOSRequest,
    SOSResponse,
)
from app.safety_api import router as safety_router
from app.session_manager import session_manager
from app.websocket import router as websocket_router

logger = get_logger("main")


# ── Lifespan: start/stop background tasks ────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    cleanup_task = asyncio.create_task(session_cleanup_loop())
    logger.info("SafeSphere backend started")
    yield
    cleanup_task.cancel()
    logger.info("SafeSphere backend shutting down")


# ── App factory ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="SafeSphere Emergency Backend",
    description=(
        "Real-time emergency voice relay + hexagonal safety map API for SafeSphere. "
        "Trigger an SOS, stream audio to emergency contacts, and query area safety scores."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — open for development; tighten allow_origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(websocket_router)
app.include_router(safety_router)


# ── General endpoints ─────────────────────────────────────────────────────────

@app.get("/", tags=["general"])
def root():
    return {
        "message": "SafeSphere Emergency Backend is running!",
        "version": "2.0.0",
        "docs": "/docs",
        "ui": "/ui",
    }


@app.get("/ui", tags=["general"])
def get_ui():
    """Serve the premium SafeSphere Voice SOS dashboard."""
    ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "index.html")
    return FileResponse(ui_path)


@app.get("/health", tags=["general"])
def health():
    return {
        "status": "healthy",
        "active_sessions": len(session_manager.sessions),
    }


# ── SOS endpoints ─────────────────────────────────────────────────────────────

@app.post("/sos", response_model=SOSResponse, tags=["sos"])
def trigger_sos(body: SOSRequest):
    """
    Trigger an SOS emergency session.

    The victim's device calls this endpoint. The backend:
      1. Creates a new session tied to the victim's user_id and GPS location.
      2. Returns a **broadcaster_token** for the victim's device to stream audio.
      3. Returns a **shared listener_token** to be distributed to the emergency
         contacts listed in contact_ids (push notification / SMS out-of-band).

    Each contact uses the listener_token to connect to `WS /ws/listen` and
    hear the live audio stream.
    """
    session_id = session_manager.create_session(
        user_id=body.user_id,
        lat=body.lat,
        lng=body.lng,
        phone=body.phone,
    )

    broadcaster_token = create_token(session_id=session_id, role="broadcaster")
    listener_token = create_token(session_id=session_id, role="listener")
    alert_time = datetime.utcnow().isoformat()

    logger.info(
        f"SOS triggered | user={body.user_id} | phone={body.phone} | session={session_id} "
        f"| location=({body.lat}, {body.lng}) | contacts={body.contact_ids}"
    )

    contact_list = ", ".join(body.contact_ids) if body.contact_ids else "none"
    return SOSResponse(
        session_id=session_id,
        broadcaster_token=broadcaster_token,
        listener_token=listener_token,
        user_id=body.user_id,
        phone=body.phone,
        lat=body.lat,
        lng=body.lng,
        alert_time=alert_time,
        message=(
            f"SOS session created. Emergency contacts notified: [{contact_list}]. "
            "Share listener_token with contacts to join the live audio stream."
        ),
    )


@app.get("/session/{session_id}/status", response_model=SessionStatusResponse, tags=["sos"])
def session_status(session_id: str):
    """Get the current status of an emergency session."""
    session = session_manager.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionStatusResponse(
        session_id=session_id,
        is_live=session["broadcaster_alive"],
        listener_count=len(session["listeners"]),
        broadcaster_connected=session["broadcaster"] is not None,
        created_at=session["created_at"].isoformat(),
        user_id=session.get("user_id"),
        phone=session.get("phone", ""),
        lat=session.get("lat"),
        lng=session.get("lng"),
    )


@app.delete("/session/{session_id}", tags=["sos"])
def end_session(session_id: str):
    """End an emergency session. Called by the broadcaster (victim) when safe."""
    session = session_manager.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    session_manager.delete_session(session_id)
    logger.info(f"Session manually ended | session={session_id}")
    return {"message": "Session ended", "session_id": session_id}


@app.get("/sessions", tags=["sos"])
def list_sessions():
    """List all active emergency sessions (admin endpoint)."""
    return {"sessions": session_manager.list_active_sessions()}


# ── Legacy test / compatibility endpoints ─────────────────────────────────────

@app.get("/test-session", tags=["debug"])
def test_session():
    session_id = session_manager.create_session()
    return {"session_id": session_id, "session": str(session_manager.get_session(session_id))}


@app.get("/test-token", tags=["debug"])
def test_token():
    token = create_token(session_id="abc123", role="broadcaster")
    return {"token": token}


@app.post("/session", response_model=SessionResponse, tags=["debug"])
def create_session():
    """Legacy generic session creator — use POST /sos instead."""
    session_id = session_manager.create_session()
    return SessionResponse(
        session_id=session_id,
        broadcaster_token=create_token(session_id=session_id, role="broadcaster"),
        listener_token=create_token(session_id=session_id, role="listener"),
    )
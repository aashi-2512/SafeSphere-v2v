"""
WebSocket endpoints for the SafeSphere emergency voice relay.

Audio format
────────────
The backend is a transparent byte relay — it does NOT transcode audio.
The agreed wire format is raw PCM (mono, 16-bit little-endian, 16 kHz).
Each WebSocket message = one audio frame (typically 20 ms = 320 bytes at 16 kHz).
The frontend is responsible for encoding before send and decoding after receive.
If Opus compression is needed in future, wrap each frame as:
    [4-byte little-endian length][opus_encoded_bytes]
and handle it on both sides — no backend change required.

Endpoints
─────────
  WS /ws/broadcast?token=<broadcaster_jwt>
      Victim's device streams raw audio frames.

  WS /ws/listen?token=<listener_jwt>
      Emergency contact receives raw audio frames.
      On connect, receives the last RING_BUFFER_SIZE frames as catch-up.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.auth import verify_token
from app.logger import get_logger
from app.session_manager import session_manager

router = APIRouter()
logger = get_logger("websocket")


# ── Broadcaster ───────────────────────────────────────────────────────────────

@router.websocket("/ws/broadcast")
async def broadcaster_socket(websocket: WebSocket, token: str):
    # ── Auth ──────────────────────────────────────────────────────────────────
    payload = verify_token(token)
    if payload is None or payload.get("role") != "broadcaster":
        await websocket.close(code=1008)
        return

    session_id = payload["session_id"]
    session = session_manager.get_session(session_id)
    if session is None:
        await websocket.close(code=1008)
        return

    # ── Conflict guard — only one broadcaster per session ─────────────────────
    if session["broadcaster"] is not None:
        logger.warning(
            f"Broadcaster conflict | session={session_id} — rejecting duplicate connection"
        )
        await websocket.close(code=1008)
        return

    # ── Accept & register ─────────────────────────────────────────────────────
    await websocket.accept()
    session["broadcaster"] = websocket
    session["broadcaster_alive"] = True

    logger.info(f"Broadcaster connected | session={session_id}")

    # Send a JSON control frame so the client knows it's live
    await websocket.send_json({
        "type": "connected",
        "role": "broadcaster",
        "session_id": session_id,
    })

    try:
        while True:
            # Receive one audio frame (raw PCM bytes)
            data: bytes = await websocket.receive_bytes()

            # Push into ring buffer (auto-evicts oldest when full)
            session["ring_buffer"].append(data)

            # Relay to every active listener
            dead_listeners = set()
            for listener in session["listeners"]:
                try:
                    await listener.send_bytes(data)
                except Exception:
                    dead_listeners.add(listener)

            # Clean up dropped listeners
            if dead_listeners:
                session["listeners"] -= dead_listeners
                logger.info(
                    f"Pruned {len(dead_listeners)} dead listener(s) | session={session_id}"
                )

    except WebSocketDisconnect:
        logger.info(f"Broadcaster disconnected | session={session_id}")
        session["broadcaster"] = None
        session["broadcaster_alive"] = False


# ── Listener ──────────────────────────────────────────────────────────────────

@router.websocket("/ws/listen")
async def listener_socket(websocket: WebSocket, token: str):
    # ── Auth ──────────────────────────────────────────────────────────────────
    payload = verify_token(token)
    if payload is None or payload.get("role") != "listener":
        await websocket.close(code=1008)
        return

    session_id = payload["session_id"]
    session = session_manager.get_session(session_id)
    if session is None:
        await websocket.close(code=1008)
        return

    # ── Accept & register ─────────────────────────────────────────────────────
    await websocket.accept()
    session["listeners"].add(websocket)

    logger.info(
        f"Listener joined | session={session_id} "
        f"| total_listeners={len(session['listeners'])}"
    )

    # JSON control frame
    await websocket.send_json({
        "type": "connected",
        "role": "listener",
        "session_id": session_id,
        "broadcaster_live": session["broadcaster_alive"],
    })

    # ── Ring-buffer catch-up: replay recent frames so late joiners aren't silent
    buffered_frames = list(session["ring_buffer"])
    if buffered_frames:
        logger.info(
            f"Sending {len(buffered_frames)} ring-buffer frame(s) to new listener "
            f"| session={session_id}"
        )
        for chunk in buffered_frames:
            try:
                await websocket.send_bytes(chunk)
            except Exception:
                break  # Listener already gone

    try:
        while True:
            # Keep the connection alive; listeners don't send audio back.
            # We still await recv so we detect clean disconnects.
            await websocket.receive_text()

    except WebSocketDisconnect:
        session["listeners"].discard(websocket)
        logger.info(
            f"Listener left | session={session_id} "
            f"| remaining={len(session['listeners'])}"
        )
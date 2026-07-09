from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.auth import verify_token
from app.session_manager import session_manager

router = APIRouter()


@router.websocket("/ws/broadcast")
async def broadcaster_socket(websocket: WebSocket, token: str):

    payload = verify_token(token)

    if payload is None:
        await websocket.close(code=1008)
        return

    if payload["role"] != "broadcaster":
        await websocket.close(code=1008)
        return

    session_id = payload["session_id"]

    session = session_manager.get_session(session_id)

    if session is None:
        await websocket.close(code=1008)
        return

    await websocket.accept()

    session["broadcaster"] = websocket

    print(f"Broadcaster connected: {session_id}")

    try:
        while True:

            data = await websocket.receive_bytes()

            dead_listeners = set()

            for listener in session["listeners"]:

                try:
                    await listener.send_bytes(data)

                except Exception:
                    dead_listeners.add(listener)

            session["listeners"] -= dead_listeners

    except WebSocketDisconnect:
        print(f"Broadcaster disconnected: {session_id}")

        session["broadcaster"] = None


@router.websocket("/ws/listen")
async def listener_socket(websocket: WebSocket, token: str):

    payload = verify_token(token)

    if payload is None:
        await websocket.close(code=1008)
        return

    if payload["role"] != "listener":
        await websocket.close(code=1008)
        return

    session_id = payload["session_id"]

    session = session_manager.get_session(session_id)

    if session is None:
        await websocket.close(code=1008)
        return

    await websocket.accept()

    session["listeners"].add(websocket)

    print(f"Listener joined: {session_id}")

    try:
        while True:
            # Keep the socket alive.
            # We don't expect listeners to send audio.
            await websocket.receive_text()

    except WebSocketDisconnect:

        print(f"Listener left: {session_id}")

        session["listeners"].discard(websocket)
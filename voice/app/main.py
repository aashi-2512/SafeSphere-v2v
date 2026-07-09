from fastapi import FastAPI

from app.session_manager import session_manager
from app.auth import create_token
from app.models import SessionResponse
from app.websocket import router as websocket_router

app = FastAPI(
    title="Emergency Audio Relay Backend",
    description="Real-time emergency audio relay server",
    version="1.0.0"
)

# Register WebSocket routes
app.include_router(websocket_router)


@app.get("/")
def root():
    return {
        "message": "Emergency Audio Relay Backend is running!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/test-session")
def test_session():
    session_id = session_manager.create_session()

    return {
        "session_id": session_id,
        "session": session_manager.get_session(session_id)
    }


@app.get("/test-token")
def test_token():
    token = create_token(
        session_id="abc123",
        role="broadcaster"
    )

    return {
        "token": token
    }


@app.post("/session", response_model=SessionResponse)
def create_session():

    session_id = session_manager.create_session()

    broadcaster_token = create_token(
        session_id=session_id,
        role="broadcaster"
    )

    listener_token = create_token(
        session_id=session_id,
        role="listener"
    )

    return SessionResponse(
        session_id=session_id,
        broadcaster_token=broadcaster_token,
        listener_token=listener_token
    )
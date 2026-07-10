"""
WebSocket integration tests for SafeSphere emergency voice relay.

Run with:
    cd voice-feature
    pytest test/test_ws_integration.py -v

These tests exercise the full WS handshake, control message flow,
audio relay, ring-buffer catch-up, and duplicate-broadcaster protection.
"""

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.main import app
from app.session_manager import session_manager

client = TestClient(app)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sos_session():
    """
    Create a fresh SOS session before each test and clean it up afterwards.
    Returns the full SOS response dict (session_id, broadcaster_token, listener_token, …).
    """
    r = client.post("/sos", json={
        "user_id": "ws_test_user",
        "lat": 19.076,
        "lng": 72.877,
        "contact_ids": ["contact_ws_1"],
    })
    assert r.status_code == 200
    data = r.json()
    yield data
    # Teardown — remove session so tests don't bleed into each other
    session_manager.delete_session(data["session_id"])


# ── Broadcaster ───────────────────────────────────────────────────────────────

def test_broadcaster_receives_control_message(sos_session):
    """Broadcaster should receive a JSON 'connected' frame immediately on connect."""
    token = sos_session["broadcaster_token"]
    with client.websocket_connect(f"/ws/broadcast?token={token}") as ws:
        msg = ws.receive_json()
        assert msg["type"] == "connected"
        assert msg["role"] == "broadcaster"
        assert msg["session_id"] == sos_session["session_id"]


def test_broadcaster_updates_session_status(sos_session):
    """Session status should reflect broadcaster_alive=True while connected."""
    sid = sos_session["session_id"]
    token = sos_session["broadcaster_token"]

    with client.websocket_connect(f"/ws/broadcast?token={token}") as ws:
        ws.receive_json()  # consume control message

        status = client.get(f"/session/{sid}/status").json()
        assert status["broadcaster_connected"] is True
        assert status["is_live"] is True


def test_duplicate_broadcaster_rejected(sos_session):
    """A second broadcaster on the same session must be rejected (code 1008)."""
    token = sos_session["broadcaster_token"]

    with client.websocket_connect(f"/ws/broadcast?token={token}") as first:
        first.receive_json()  # consume control message

        # Second connection should be refused — starlette raises WebSocketDisconnect
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect(f"/ws/broadcast?token={token}") as second:
                second.receive_json()
        assert exc_info.value.code == 1008


# ── Listener ──────────────────────────────────────────────────────────────────

def test_listener_receives_control_message(sos_session):
    """Listener should receive a JSON 'connected' frame immediately on connect."""
    token = sos_session["listener_token"]
    with client.websocket_connect(f"/ws/listen?token={token}") as ws:
        msg = ws.receive_json()
        assert msg["type"] == "connected"
        assert msg["role"] == "listener"
        assert msg["session_id"] == sos_session["session_id"]


def test_listener_count_in_status(sos_session):
    """Session status should show listener_count=1 while one listener is connected."""
    sid = sos_session["session_id"]
    l_token = sos_session["listener_token"]

    with client.websocket_connect(f"/ws/listen?token={l_token}") as ws:
        ws.receive_json()  # control frame
        status = client.get(f"/session/{sid}/status").json()
        assert status["listener_count"] == 1


# ── Audio relay ───────────────────────────────────────────────────────────────

def test_audio_relay_broadcaster_to_listener(sos_session):
    """
    Broadcaster sends audio bytes → listener receives the exact same bytes.
    This verifies the core relay pipeline end-to-end.
    """
    b_token = sos_session["broadcaster_token"]
    l_token = sos_session["listener_token"]

    fake_audio = bytes(range(256)) * 2  # 512 bytes of deterministic fake PCM

    with client.websocket_connect(f"/ws/broadcast?token={b_token}") as broadcaster:
        broadcaster.receive_json()  # control frame

        with client.websocket_connect(f"/ws/listen?token={l_token}") as listener:
            listener.receive_json()  # control frame

            broadcaster.send_bytes(fake_audio)
            received = listener.receive_bytes()
            assert received == fake_audio, (
                f"Relay mismatch: sent {len(fake_audio)} bytes, "
                f"received {len(received)} bytes"
            )


def test_ring_buffer_catchup_for_late_listener(sos_session):
    """
    Listener joining *after* broadcaster has already sent frames should receive
    the buffered frames as a catch-up stream.
    """
    b_token = sos_session["broadcaster_token"]
    l_token = sos_session["listener_token"]

    sentinel = b"\xDE\xAD\xBE\xEF" * 80  # 320 bytes — one fake audio frame

    with client.websocket_connect(f"/ws/broadcast?token={b_token}") as broadcaster:
        broadcaster.receive_json()  # control frame

        # Send audio BEFORE the listener connects
        broadcaster.send_bytes(sentinel)

        # Listener joins late — should still receive the buffered frame
        with client.websocket_connect(f"/ws/listen?token={l_token}") as listener:
            listener.receive_json()  # control frame
            buffered = listener.receive_bytes()
            assert buffered == sentinel, "Ring buffer catch-up failed"


# ── Role enforcement ──────────────────────────────────────────────────────────

def test_listener_token_rejected_on_broadcast(sos_session):
    """A listener token must NOT be accepted on the /ws/broadcast endpoint."""
    l_token = sos_session["listener_token"]
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect(f"/ws/broadcast?token={l_token}") as ws:
            ws.receive_json()
    assert exc_info.value.code == 1008


def test_broadcaster_token_rejected_on_listen(sos_session):
    """A broadcaster token must NOT be accepted on the /ws/listen endpoint."""
    b_token = sos_session["broadcaster_token"]
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect(f"/ws/listen?token={b_token}") as ws:
            ws.receive_json()
    assert exc_info.value.code == 1008

"""
REST API tests for SafeSphere Emergency Backend.

Run with:
    cd voice-feature
    pytest test/test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.main import app

client = TestClient(app)


# ── General ───────────────────────────────────────────────────────────────────

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert "SafeSphere" in data["message"]
    assert data["version"] == "2.0.0"


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert "active_sessions" in data


# ── Legacy session endpoint ───────────────────────────────────────────────────

def test_legacy_create_session():
    r = client.post("/session")
    assert r.status_code == 200
    data = r.json()
    assert "session_id" in data
    assert "broadcaster_token" in data
    assert "listener_token" in data


# ── SOS trigger ───────────────────────────────────────────────────────────────

def _make_sos_payload(user_id="test_user", contacts=None):
    return {
        "user_id": user_id,
        "lat": 19.076,
        "lng": 72.877,
        "contact_ids": contacts or [],
    }


def test_trigger_sos_basic():
    r = client.post("/sos", json=_make_sos_payload("user_001"))
    assert r.status_code == 200
    data = r.json()
    assert data["user_id"] == "user_001"
    assert data["lat"] == 19.076
    assert data["lng"] == 72.877
    assert "session_id" in data
    assert "broadcaster_token" in data
    assert "listener_token" in data
    assert "alert_time" in data


def test_trigger_sos_with_contacts():
    r = client.post("/sos", json=_make_sos_payload(
        "user_002",
        contacts=["contact_A", "contact_B"],
    ))
    assert r.status_code == 200
    data = r.json()
    assert "contact_A" in data["message"]
    assert "contact_B" in data["message"]


def test_trigger_sos_missing_fields():
    # Missing required fields (user_id, lat, lng)
    r = client.post("/sos", json={"user_id": "x"})
    assert r.status_code == 422  # FastAPI validation error


# ── Session status ────────────────────────────────────────────────────────────

def test_session_status_fresh():
    sos = client.post("/sos", json=_make_sos_payload("user_status"))
    session_id = sos.json()["session_id"]

    r = client.get(f"/session/{session_id}/status")
    assert r.status_code == 200
    data = r.json()
    assert data["session_id"] == session_id
    assert data["is_live"] is False           # broadcaster not yet connected
    assert data["listener_count"] == 0
    assert data["broadcaster_connected"] is False
    assert data["user_id"] == "user_status"
    assert data["lat"] == 19.076


def test_session_status_not_found():
    r = client.get("/session/does-not-exist/status")
    assert r.status_code == 404


# ── Session deletion ──────────────────────────────────────────────────────────

def test_delete_session():
    sos = client.post("/sos", json=_make_sos_payload("user_del"))
    session_id = sos.json()["session_id"]

    r = client.delete(f"/session/{session_id}")
    assert r.status_code == 200
    assert r.json()["session_id"] == session_id

    # Confirm session is gone
    r2 = client.get(f"/session/{session_id}/status")
    assert r2.status_code == 404


def test_delete_nonexistent_session():
    r = client.delete("/session/ghost-session-id")
    assert r.status_code == 404


# ── Session list ──────────────────────────────────────────────────────────────

def test_list_sessions():
    # Create at least one session so the list is non-trivially testable
    client.post("/sos", json=_make_sos_payload("user_list"))

    r = client.get("/sessions")
    assert r.status_code == 200
    data = r.json()
    assert "sessions" in data
    assert isinstance(data["sessions"], list)
    assert len(data["sessions"]) >= 1


# ── WebSocket auth rejection ──────────────────────────────────────────────────

def test_broadcast_invalid_token():
    # Server should close with code 1008 (policy violation)
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws/broadcast?token=totally_invalid") as ws:
            ws.receive_json()
    assert exc_info.value.code == 1008


def test_listen_invalid_token():
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws/listen?token=bad_token") as ws:
            ws.receive_json()
    assert exc_info.value.code == 1008

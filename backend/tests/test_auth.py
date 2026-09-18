import uuid
import pytest
from fastapi.testclient import TestClient


def test_register_success(client: TestClient):
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+9198{uuid.uuid4().int % 100000000:08d}"
    payload = {
        "email": email,
        "password": "Password123!",
        "full_name": "Test User",
        "phone": phone,
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert "user" in data
    assert data["user"]["email"] == email
    assert "tokens" in data
    assert "access_token" in data["tokens"]
    assert "refresh_token" in data["tokens"]
    assert data["tokens"]["expires_in"] == 900


def test_register_duplicate_email(client: TestClient):
    email = f"dup_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "email": email,
        "password": "Password123!",
        "full_name": "Test User",
    }
    r1 = client.post("/api/v1/auth/register", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/api/v1/auth/register", json=payload)
    assert r2.status_code == 409
    err = r2.json()
    assert err["code"] == "AUTH_EMAIL_EXISTS"
    assert "already exists" in err["message"]


def test_login_success(client: TestClient):
    email = f"login_{uuid.uuid4().hex[:8]}@example.com"
    phone = f"+9199{uuid.uuid4().int % 100000000:08d}"
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "SecretPassword123!",
            "full_name": "Login User",
            "phone": phone,
        },
    )

    # Login with email
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": email, "password": "SecretPassword123!"},
    )
    assert resp.status_code == 200
    tokens = resp.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    # Login with phone
    resp_phone = client.post(
        "/api/v1/auth/login",
        json={"username": phone, "password": "SecretPassword123!"},
    )
    assert resp_phone.status_code == 200


def test_login_invalid_credentials(client: TestClient):
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": "nonexistent@example.com", "password": "WrongPassword"},
    )
    assert resp.status_code == 401
    err = resp.json()
    assert err["code"] == "AUTH_INVALID_CREDENTIALS"
    assert "Invalid username or password" in err["message"]


def test_refresh_token_rotation_and_replay_detection(client: TestClient):
    email = f"rotate_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Rotation User",
        },
    )
    original_refresh_token = reg.json()["tokens"]["refresh_token"]

    # First refresh: should succeed and issue a new pair
    ref1 = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": original_refresh_token},
    )
    assert ref1.status_code == 200
    new_tokens = ref1.json()
    assert new_tokens["refresh_token"] != original_refresh_token

    # Replay attack: trying to use the old refresh token again must fail
    replay = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": original_refresh_token},
    )
    assert replay.status_code == 401
    err = replay.json()
    assert err["code"] == "AUTH_REFRESH_TOKEN_REVOKED"


def test_logout(client: TestClient):
    email = f"logout_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Logout User",
        },
    )
    access_token = reg.json()["tokens"]["access_token"]
    refresh_token = reg.json()["tokens"]["refresh_token"]

    # Logout
    logout_resp = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"refresh_token": refresh_token},
    )
    assert logout_resp.status_code == 200

    # Refresh after logout should fail
    ref = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert ref.status_code == 401


def test_rate_limiting_login(client: TestClient):
    # Attempt 5 failed logins
    for i in range(5):
        resp = client.post(
            "/api/v1/auth/login",
            json={"username": "ratelimit_user@example.com", "password": "wrong"},
        )
        assert resp.status_code == 401

    # 6th attempt should be blocked by rate limiting (429)
    blocked_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "ratelimit_user@example.com", "password": "wrong"},
    )
    assert blocked_resp.status_code == 429
    err = blocked_resp.json()
    assert err["code"] == "AUTH_RATE_LIMIT_EXCEEDED"
    assert "Too many failed login attempts" in err["message"]

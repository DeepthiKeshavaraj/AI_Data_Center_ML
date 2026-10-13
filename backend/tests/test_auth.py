import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Ensure backend directory is in python path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app
from app.services.db import get_db, reset_test_db
from app.services.auth_service import COOKIE_NAME

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    reset_test_db()
    client.cookies.clear()
    yield
    reset_test_db()
    client.cookies.clear()


def test_auth_register_success():
    payload = {
        "name": "Alex Chen",
        "email": "alex.chen@datacenter.ai",
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["user"]["name"] == "Alex Chen"
    assert data["user"]["email"] == "alex.chen@datacenter.ai"
    assert "user_id" in data["user"]
    # Password must not be exposed
    assert "password" not in data["user"]
    assert "password_hash" not in data["user"]

    # Cookie must be set
    assert COOKIE_NAME in response.cookies


def test_auth_register_duplicate_email_rejection():
    payload = {
        "name": "Alex Chen",
        "email": "duplicate@datacenter.ai",
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!",
    }
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 200

    # Attempt second registration with same email (case-insensitive)
    payload2 = {
        "name": "Another User",
        "email": "DUPLICATE@datacenter.ai",
        "password": "DifferentPassword999!",
        "confirm_password": "DifferentPassword999!",
    }
    res2 = client.post("/api/auth/register", json=payload2)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"].lower()


def test_auth_register_password_mismatch_and_validation():
    # Mismatched confirmation password
    mismatch_payload = {
        "name": "Alex Chen",
        "email": "mismatch@datacenter.ai",
        "password": "SecurePassword123!",
        "confirm_password": "WrongPassword456!",
    }
    res = client.post("/api/auth/register", json=mismatch_payload)
    assert res.status_code == 422

    # Password too short (< 8 chars)
    short_payload = {
        "name": "Alex Chen",
        "email": "short@datacenter.ai",
        "password": "short",
        "confirm_password": "short",
    }
    res2 = client.post("/api/auth/register", json=short_payload)
    assert res2.status_code == 422

    # Invalid email
    bad_email_payload = {
        "name": "Alex Chen",
        "email": "not-an-email",
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!",
    }
    res3 = client.post("/api/auth/register", json=bad_email_payload)
    assert res3.status_code == 422


def test_auth_login_success_and_me():
    # 1. Register account
    client.post(
        "/api/auth/register",
        json={
            "name": "Elena Vance",
            "email": "elena.vance@datacenter.ai",
            "password": "ResearcherPassword2026!",
            "confirm_password": "ResearcherPassword2026!",
        },
    )

    # 2. Login
    login_res = client.post(
        "/api/auth/login",
        json={
            "email": "ELENA.VANCE@datacenter.ai",  # Test case-normalization
            "password": "ResearcherPassword2026!",
        },
    )
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert login_data["status"] == "success"
    assert login_data["user"]["name"] == "Elena Vance"
    assert COOKIE_NAME in login_res.cookies

    # 3. Test /api/auth/me with session cookie
    me_res = client.get("/api/auth/me", cookies=login_res.cookies)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["name"] == "Elena Vance"
    assert me_data["email"] == "elena.vance@datacenter.ai"
    assert "user_id" in me_data


def test_auth_login_incorrect_password():
    client.post(
        "/api/auth/register",
        json={
            "name": "Test User",
            "email": "test.user@datacenter.ai",
            "password": "CorrectPassword123!",
            "confirm_password": "CorrectPassword123!",
        },
    )

    # Incorrect password
    bad_login = client.post(
        "/api/auth/login",
        json={
            "email": "test.user@datacenter.ai",
            "password": "WrongPassword999!",
        },
    )
    assert bad_login.status_code == 401
    assert "invalid email or password" in bad_login.json()["detail"].lower()


def test_protected_routes_reject_unauthenticated():
    # /api/auth/me without cookies
    res_me = client.get("/api/auth/me")
    assert res_me.status_code == 401
    assert "authentication required" in res_me.json()["detail"].lower()

    # /api/dashboard/protected-data without cookies
    res_data = client.get("/api/dashboard/protected-data")
    assert res_data.status_code == 401


def test_auth_logout_invalidates_session():
    # Register & Login
    reg_res = client.post(
        "/api/auth/register",
        json={
            "name": "Session Tester",
            "email": "session.tester@datacenter.ai",
            "password": "PasswordToLogout123!",
            "confirm_password": "PasswordToLogout123!",
        },
    )
    cookies = reg_res.cookies

    # Confirm session is valid
    me_res = client.get("/api/auth/me", cookies=cookies)
    assert me_res.status_code == 200

    # Logout
    logout_res = client.post("/api/auth/logout", cookies=cookies)
    assert logout_res.status_code == 200

    # Subsequent /api/auth/me request must fail with 401
    me_after = client.get("/api/auth/me", cookies=cookies)
    assert me_after.status_code == 401


def test_passwords_never_stored_as_plaintext():
    db = get_db()
    plain_pw = "SuperSecretPlainText123!"

    client.post(
        "/api/auth/register",
        json={
            "name": "Security Audit",
            "email": "audit@datacenter.ai",
            "password": plain_pw,
            "confirm_password": plain_pw,
        },
    )

    # Query directly from MongoDB collection
    user_doc = db.users.find_one({"email": "audit@datacenter.ai"})
    assert user_doc is not None

    # Plaintext password must NOT appear anywhere in document
    assert plain_pw not in str(user_doc)
    assert "password_hash" in user_doc

    # Must be valid Argon2id hash
    hash_str = user_doc["password_hash"]
    assert hash_str.startswith("$argon2id$")


def test_existing_ml_endpoints_continue_functioning():
    # Health
    health_res = client.get("/api/health")
    assert health_res.status_code == 200

    # Security predict
    sec_payload = {
        "protocol": "tcp",
        "flow_duration": 0.125,
        "src_packets": 10.0,
        "dst_packets": 8.0,
        "src_bytes": 540.0,
        "dst_bytes": 320.0,
        "connection_state": "fin",
        "service": "http",
    }
    sec_res = client.post("/api/security/predict", json=sec_payload)
    assert sec_res.status_code == 200
    assert sec_res.json()["label"] == "Normal"

    # Simulation presets
    presets_res = client.get("/api/simulation/presets")
    assert presets_res.status_code == 200
    assert len(presets_res.json()) >= 3

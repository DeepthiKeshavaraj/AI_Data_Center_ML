import os
import uuid
import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, Dict, Any

from fastapi import HTTPException, Request, Response
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

from app.schemas.auth import UserRegisterRequest, UserLoginRequest, UserResponse
from app.services.db import get_db

logger = logging.getLogger("ai_data_center.auth")

# Argon2id password hasher (RFC 9106 recommended parameters)
_hasher = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=1,
    hash_len=32,
)

COOKIE_NAME = "datacenter_session_token"
SESSION_DURATION_HOURS = 24


def hash_password(plaintext: str) -> str:
    """Hash password using Argon2id."""
    return _hasher.hash(plaintext)


def verify_password(hash_value: str, plaintext: str) -> bool:
    """Verify password against Argon2id hash without exposing internal exceptions."""
    try:
        return _hasher.verify(hash_value, plaintext)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False
    except Exception as e:
        logger.error(f"Unexpected error during password verification: {e}")
        return False


def register_user(req: UserRegisterRequest) -> Tuple[UserResponse, str]:
    db = get_db()
    email = req.email.strip().lower()

    # Check for duplicate email
    existing_user = db.users.find_one({"email": email})
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="An account with this email address already exists. Please log in.",
        )

    user_id = f"usr_{uuid.uuid4().hex[:12]}"
    pw_hash = hash_password(req.password)
    created_at_iso = datetime.now(timezone.utc).isoformat()

    user_doc = {
        "user_id": user_id,
        "name": req.name.strip(),
        "email": email,
        "password_hash": pw_hash,
        "created_at": created_at_iso,
    }

    try:
        db.users.insert_one(user_doc)
        logger.info(f"Registered new user: {email} ({user_id})")
    except Exception as e:
        # Check for duplicate key race condition from unique index
        if "duplicate key" in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail="An account with this email address already exists.",
            )
        logger.error(f"Failed to register user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database registration failed.")

    # Create active session upon successful registration
    session_token = create_user_session(user_id)
    user_resp = UserResponse(
        user_id=user_id,
        name=req.name.strip(),
        email=email,
        created_at=created_at_iso,
    )
    return user_resp, session_token


def authenticate_user(req: UserLoginRequest) -> Tuple[UserResponse, str]:
    db = get_db()
    email = req.email.strip().lower()

    user_doc = db.users.find_one({"email": email})
    if not user_doc:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    # Verify password with Argon2id
    stored_hash = user_doc.get("password_hash", "")
    if not verify_password(stored_hash, req.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    # Rehash check: if Argon2 parameters were updated, update hash seamlessly
    try:
        if _hasher.check_needs_rehash(stored_hash):
            new_hash = _hasher.hash(req.password)
            db.users.update_one({"_id": user_doc["_id"]}, {"$set": {"password_hash": new_hash}})
    except Exception:
        pass

    session_token = create_user_session(user_doc["user_id"])
    user_resp = UserResponse(
        user_id=user_doc["user_id"],
        name=user_doc["name"],
        email=user_doc["email"],
        created_at=user_doc.get("created_at"),
    )
    return user_resp, session_token


def create_user_session(user_id: str) -> str:
    db = get_db()
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=SESSION_DURATION_HOURS)

    session_doc = {
        "session_token": token,
        "user_id": user_id,
        "created_at": now,
        "expires_at": expires_at,
    }

    db.sessions.insert_one(session_doc)
    return token


def get_current_user_from_token(session_token: str) -> Optional[UserResponse]:
    if not session_token:
        return None

    db = get_db()
    session_doc = db.sessions.find_one({"session_token": session_token})
    if not session_doc:
        return None

    # Check expiry
    expires_at = session_doc.get("expires_at")
    if isinstance(expires_at, datetime):
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            db.sessions.delete_one({"_id": session_doc["_id"]})
            return None

    user_doc = db.users.find_one({"user_id": session_doc["user_id"]})
    if not user_doc:
        return None

    return UserResponse(
        user_id=user_doc["user_id"],
        name=user_doc["name"],
        email=user_doc["email"],
        created_at=user_doc.get("created_at"),
    )


def invalidate_user_session(session_token: str):
    if session_token:
        db = get_db()
        db.sessions.delete_one({"session_token": session_token})


def set_auth_cookie(response: Response, session_token: str):
    is_prod = os.getenv("ENVIRONMENT", "development").lower() == "production"
    response.set_cookie(
        key=COOKIE_NAME,
        value=session_token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        max_age=SESSION_DURATION_HOURS * 3600,
        path="/",
    )


def clear_auth_cookie(response: Response):
    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
        httponly=True,
        samesite="lax",
    )

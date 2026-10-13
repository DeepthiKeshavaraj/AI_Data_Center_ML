import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path

# Load environment variables from backend/.env or root .env
try:
    from dotenv import load_dotenv
    _backend_env = Path(__file__).resolve().parent.parent.parent / ".env"
    _root_env = Path(__file__).resolve().parent.parent.parent.parent / ".env"
    if _backend_env.exists():
        load_dotenv(_backend_env)
    elif _root_env.exists():
        load_dotenv(_root_env)
    else:
        load_dotenv()
except ImportError:
    pass

import re
import urllib.parse

logger = logging.getLogger("ai_data_center.db")

_client = None
_db = None
_using_mock = False
_last_error_message: Optional[str] = None


def _sanitize_mongodb_uri(uri: str) -> str:
    """Ensure raw special characters (like '@') in username or password are percent-encoded."""
    if not uri:
        return uri
    match = re.match(r"^(mongodb(?:\+srv)?://)([^:]+):(.*)@([^@/]+(?:/.*)?)$", uri)
    if match:
        scheme, user, password, rest = match.groups()
        safe_user = urllib.parse.quote_plus(urllib.parse.unquote_plus(user))
        safe_pass = urllib.parse.quote_plus(urllib.parse.unquote_plus(password))
        return f"{scheme}{safe_user}:{safe_pass}@{rest}"
    return uri


def get_db():
    global _client, _db, _using_mock, _last_error_message
    if _db is not None:
        return _db

    mongodb_uri = os.getenv("MONGODB_URI", "").strip()
    db_name = os.getenv("MONGODB_DATABASE", "ai_datacenter_ml").strip()

    if mongodb_uri:
        sanitized_uri = _sanitize_mongodb_uri(mongodb_uri)
        try:
            import pymongo
            logger.info(f"Connecting to MongoDB Atlas (database: {db_name})...")
            client = pymongo.MongoClient(
                sanitized_uri,
                maxPoolSize=10,
                minPoolSize=1,
                maxIdleTimeMS=30000,
                socketTimeoutMS=5000,
                connectTimeoutMS=3000,
                serverSelectionTimeoutMS=3000,
                appname="ai_data_center_app",
            )
            # Verify connection with ping
            client.admin.command("ping")
            logger.info("Successfully connected to live MongoDB Atlas cluster.")
            _client = client
            _db = client[db_name]
            _using_mock = False
            _last_error_message = None
        except Exception as e:
            raw_err = str(e)
            if "Authentication failed" in raw_err or "bad auth" in raw_err:
                _last_error_message = "Authentication failed: verify MongoDB Atlas Database User & Password under 'Database Access'."
            elif "ServerSelectionTimeoutError" in raw_err or "timed out" in raw_err:
                _last_error_message = "Network timeout: check MongoDB Atlas 'Network Access' (ensure IP access allows 0.0.0.0/0 or your current IP)."
            elif "Username and password must be escaped" in raw_err or "InvalidURI" in raw_err:
                _last_error_message = "URI format error: password contains special characters (e.g. '@') that must be percent-encoded as '%40'."
            else:
                _last_error_message = f"Connection error: {type(e).__name__}"

            logger.warning(
                f"Could not connect to live MongoDB Atlas URI ({raw_err}). Falling back to mock database for resilience."
            )
            _db = _init_mock_db(db_name)
    else:
        logger.info("No MONGODB_URI configured. Initializing test/mock in-memory MongoDB database.")
        _db = _init_mock_db(db_name)

    _ensure_indexes(_db)
    return _db


def _init_mock_db(db_name: str):
    global _client, _using_mock
    try:
        import mongomock
        _client = mongomock.MongoClient()
        _using_mock = True
        logger.info(f"Initialized mongomock in-memory database handle: {db_name}")
        return _client[db_name]
    except ImportError:
        import pymongo
        logger.warning("mongomock not found. Attempting localhost fallback.")
        _client = pymongo.MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=1000)
        _using_mock = False
        return _client[db_name]


def _ensure_indexes(db):
    try:
        # Unique index on normalized email address
        db.users.create_index("email", unique=True)
        # Unique index on session tokens
        db.sessions.create_index("session_token", unique=True)
        # TTL index on expires_at for automated session cleanup
        db.sessions.create_index("expires_at", expireAfterSeconds=0)
        logger.info("Database indexes verified: users.email (unique), sessions.session_token (unique), sessions.expires_at (TTL).")
    except Exception as e:
        logger.warning(f"Index creation warning: {e}")


def is_using_mock() -> bool:
    global _using_mock
    return _using_mock


def get_db_status() -> Dict[str, Any]:
    global _using_mock, _last_error_message
    db = get_db()
    uri_configured = bool(os.getenv("MONGODB_URI", "").strip())
    db_name = os.getenv("MONGODB_DATABASE", "ai_datacenter_ml")

    return {
        "connected": True,
        "is_mock": _using_mock,
        "uri_configured": uri_configured,
        "database_name": db_name,
        "engine": "mongomock (testing/offline)" if _using_mock else "PyMongo -> MongoDB Atlas (live)",
        "details": _last_error_message,
    }


def reset_test_db():
    """Helper for automated unit tests to clear test collections."""
    db = get_db()
    db.users.delete_many({})
    db.sessions.delete_many({})

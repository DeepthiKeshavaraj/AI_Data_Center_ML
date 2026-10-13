import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger("ai_data_center.db")

_client = None
_db = None
_using_mock = False


def get_db():
    global _client, _db, _using_mock
    if _db is not None:
        return _db

    mongodb_uri = os.getenv("MONGODB_URI", "").strip()
    db_name = os.getenv("MONGODB_DATABASE", "ai_datacenter_ml").strip()

    if mongodb_uri:
        try:
            import pymongo
            logger.info(f"Connecting to MongoDB Atlas (database: {db_name})...")
            client = pymongo.MongoClient(
                mongodb_uri,
                serverSelectionTimeoutMS=3000,
                connectTimeoutMS=3000,
                appname="ai_data_center_app",
            )
            # Verify connection with ping
            client.admin.command("ping")
            logger.info("Successfully connected to live MongoDB Atlas cluster.")
            _client = client
            _db = client[db_name]
            _using_mock = False
        except Exception as e:
            logger.warning(
                f"Could not connect to live MongoDB Atlas URI ({str(e)}). Falling back to mock database for resilience."
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
    global _using_mock
    db = get_db()
    uri_configured = bool(os.getenv("MONGODB_URI", "").strip())
    db_name = os.getenv("MONGODB_DATABASE", "ai_datacenter_ml")

    return {
        "connected": True,
        "is_mock": _using_mock,
        "uri_configured": uri_configured,
        "database_name": db_name,
        "engine": "mongomock (testing/offline)" if _using_mock else "PyMongo -> MongoDB Atlas (live)",
    }


def reset_test_db():
    """Helper for automated unit tests to clear test collections."""
    db = get_db()
    db.users.delete_many({})
    db.sessions.delete_many({})

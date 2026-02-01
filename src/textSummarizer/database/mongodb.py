"""
MongoDB connection manager with connection pooling and singleton pattern.
Provides health checks, graceful closure, and prediction logging.
"""

import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from textSummarizer.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)

try:
    from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

    MOTOR_AVAILABLE = True
except ImportError:
    MOTOR_AVAILABLE = False
    AsyncIOMotorClient = None
    AsyncIOMotorDatabase = None


class MongoDBManager:
    """Singleton MongoDB connection manager with pooling.

    Uses motor (async MongoDB driver) for non-blocking database operations.
    Implements connection pooling with configurable min/max connections.
    """

    _instance: Optional["MongoDBManager"] = None
    _client: Any = None
    _database: Any = None

    def __new__(cls) -> "MongoDBManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self, settings: Settings = None) -> None:
        """Establish MongoDB connection with pooling.

        Args:
            settings: Application settings. Uses defaults if not provided.
        """
        if not MOTOR_AVAILABLE:
            logger.warning("motor package not installed, MongoDB features disabled")
            return

        if self._client is not None:
            return

        if settings is None:
            settings = get_settings()

        try:
            self._client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
                maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
                connectTimeoutMS=settings.MONGODB_CONNECT_TIMEOUT_MS,
                serverSelectionTimeoutMS=settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
            )
            self._database = self._client[settings.MONGODB_DB_NAME]
            # Verify connection
            await self._client.admin.command("ping")
            logger.info(
                "Connected to MongoDB at %s (pool: %d-%d)",
                settings.MONGODB_URL,
                settings.MONGODB_MIN_POOL_SIZE,
                settings.MONGODB_MAX_POOL_SIZE,
            )
        except Exception as e:
            logger.error("Failed to connect to MongoDB: %s", str(e))
            self._client = None
            self._database = None

    async def close(self) -> None:
        """Gracefully close the MongoDB connection."""
        if self._client is not None:
            self._client.close()
            self._client = None
            self._database = None
            logger.info("MongoDB connection closed")

    async def health_check(self) -> Dict[str, Any]:
        """Check MongoDB connection health.

        Returns:
            Dictionary with status and latency information.
        """
        if self._client is None:
            return {"status": "disconnected", "latency_ms": None}

        try:
            start = time.perf_counter()
            await self._client.admin.command("ping")
            latency = (time.perf_counter() - start) * 1000
            return {"status": "connected", "latency_ms": round(latency, 2)}
        except Exception as e:
            return {"status": "error", "error": str(e), "latency_ms": None}

    @property
    def database(self) -> Any:
        """Get the database instance."""
        return self._database

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._client is not None

    async def log_prediction(
        self,
        request_id: str,
        input_text: str,
        output_summary: str,
        duration_ms: float,
        user_id: Optional[str] = None,
    ) -> None:
        """Log a prediction to the database for audit purposes.

        Args:
            request_id: Unique request identifier.
            input_text: The original input text.
            output_summary: The generated summary.
            duration_ms: Processing duration in milliseconds.
            user_id: Optional user identifier.
        """
        if self._database is None:
            return

        try:
            collection = self._database["predictions"]
            await collection.insert_one(
                {
                    "request_id": request_id,
                    "input_text": input_text[:500],
                    "output_summary": output_summary,
                    "input_length": len(input_text),
                    "output_length": len(output_summary),
                    "duration_ms": round(duration_ms, 2),
                    "user_id": user_id,
                    "created_at": datetime.now(timezone.utc),
                }
            )
        except Exception as e:
            logger.warning("Failed to log prediction to database: %s", str(e))


_db_manager: Optional[MongoDBManager] = None


def get_db_manager() -> MongoDBManager:
    """Get the singleton MongoDBManager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = MongoDBManager()
    return _db_manager

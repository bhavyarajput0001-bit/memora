"""Base connector class for all MEMORA data sources."""
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ConnectorResult:
    """Result from a connector run."""
    success: bool
    items_ingested: int = 0
    items_skipped: int = 0
    errors: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    last_run: Optional[datetime] = None
    status: str = "idle"  # idle, running, error, success


class BaseConnector(ABC):
    """Base class for all connectors."""

    name: str = "base"
    description: str = ""

    @abstractmethod
    def connect(self, **kwargs) -> bool:
        """Establish connection. Returns True if successful."""
        pass

    @abstractmethod
    def fetch(self, since: Optional[datetime] = None, limit: int = 100) -> list[dict]:
        """Fetch new items. Returns list of document-like dicts."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Clean up connection."""
        pass

    def run(self, since: Optional[datetime] = None, limit: int = 100) -> ConnectorResult:
        """Execute a full connector run."""
        start = time.time()
        result = ConnectorResult(success=False, last_run=datetime.utcnow())

        try:
            if not self.connect():
                result.errors.append("Connection failed")
                result.status = "error"
                return result

            items = self.fetch(since=since, limit=limit)
            result.items_ingested = len(items)
            result.success = True
            result.status = "success"
            logger.info(f"Connector {self.name}: ingested {len(items)} items")

        except Exception as e:
            result.errors.append(str(e))
            result.status = "error"
            logger.error(f"Connector {self.name} error: {e}")

        result.duration_seconds = time.time() - start
        return result

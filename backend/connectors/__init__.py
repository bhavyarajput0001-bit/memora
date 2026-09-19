"""Connectors package for MEMORA — auto-ingest from external sources."""
from backend.connectors.base import BaseConnector, ConnectorResult
from backend.connectors.gmail import GmailConnector
from backend.connectors.calendar import CalendarConnector
from backend.connectors.notes import AppleNotesConnector

__all__ = [
    "BaseConnector",
    "ConnectorResult",
    "GmailConnector",
    "CalendarConnector",
    "AppleNotesConnector",
]

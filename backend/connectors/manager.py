"""Connector orchestration and scheduling for MEMORA."""
import logging
import time
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field

from backend.connectors.gmail import GmailConnector
from backend.connectors.calendar import CalendarConnector
from backend.connectors.notes import AppleNotesConnector

logger = logging.getLogger(__name__)


@dataclass
class ConnectorConfig:
    """Configuration for a connector."""
    enabled: bool = False
    # Gmail
    gmail_email: Optional[str] = None
    gmail_app_password: Optional[str] = None
    gmail_folder: str = "INBOX"
    gmail_unread_only: bool = False
    gmail_limit: int = 50
    # Calendar
    calendar_days_back: int = 30
    calendar_days_forward: int = 30
    # Notes
    notes_notebook: Optional[str] = None
    notes_days_back: int = 365
    notes_limit: int = 50


class ConnectorManager:
    """Manage all connectors and their runs."""

    def __init__(self, config: Optional[ConnectorConfig] = None):
        self.config = config or ConnectorConfig()
        self._gmail: Optional[GmailConnector] = None
        self._calendar: Optional[CalendarConnector] = None
        self._notes: Optional[AppleNotesConnector] = None
        self._last_run_times: dict[str, datetime] = {}
        self._stats: dict[str, dict] = {}

    def get_gmail(self) -> Optional[GmailConnector]:
        if not self.config.enabled or not self.config.gmail_email:
            return None
        if self._gmail is None:
            self._gmail = GmailConnector(
                self.config.gmail_email,
                self.config.gmail_app_password or "",
            )
        return self._gmail

    def get_calendar(self) -> Optional[CalendarConnector]:
        if not self.config.enabled:
            return None
        if self._calendar is None:
            self._calendar = CalendarConnector(
                self.config.calendar_days_back,
                self.config.calendar_days_forward,
            )
        return self._calendar

    def get_notes(self) -> Optional[AppleNotesConnector]:
        if not self.config.enabled:
            return None
        if self._notes is None:
            self._notes = AppleNotesConnector(
                self.config.notes_notebook,
                self.config.notes_days_back,
            )
        return self._notes

    def run_all(self) -> dict[str, dict]:
        """Run all enabled connectors and return results."""
        results = {}

        gmail = self.get_gmail()
        if gmail:
            t0 = time.time()
            items = gmail.fetch(limit=self.config.gmail_limit)
            results["gmail"] = {
                "items": len(items),
                "duration_s": round(time.time() - t0, 2),
                "status": "success" if items else "empty",
            }
            self._last_run_times["gmail"] = datetime.utcnow()

        calendar = self.get_calendar()
        if calendar:
            t0 = time.time()
            items = calendar.fetch()
            results["calendar"] = {
                "items": len(items),
                "duration_s": round(time.time() - t0, 2),
                "status": "success" if items else "empty",
            }
            self._last_run_times["calendar"] = datetime.utcnow()

        notes = self.get_notes()
        if notes:
            t0 = time.time()
            items = notes.fetch(limit=self.config.notes_limit)
            results["notes"] = {
                "items": len(items),
                "duration_s": round(time.time() - t0, 2),
                "status": "success" if items else "empty",
            }
            self._last_run_times["notes"] = datetime.utcnow()

        self._stats = results
        logger.info(f"Connector run complete: {results}")
        return results

    def get_stats(self) -> dict:
        """Get connector statistics."""
        stats = {
            "enabled": self.config.enabled,
            "last_runs": self._last_run_times,
            "results": self._stats,
            "connectors": {
                "gmail": {
                    "connected": bool(self._gmail and self._gmail._mail),
                    "email": self.config.gmail_email,
                },
                "calendar": {
                    "connected": bool(self._calendar and self._calendar._connected),
                },
                "notes": {
                    "connected": bool(self._notes and self._notes._connected),
                },
            },
        }
        return stats

    def ingest_from_connectors(self, connector_manager=None) -> int:
        """Run connectors and ingest all fetched items. Returns total items ingested."""
        if connector_manager is None:
            connector_manager = self
        total = 0
        for source, items in self.run_all().items():
            total += items.get("items", 0)
        return total

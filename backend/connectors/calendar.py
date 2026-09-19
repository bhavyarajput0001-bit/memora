"""Calendar connector for MEMORA — fetches events via Apple Events."""
import subprocess
import json
from datetime import datetime, timedelta
from typing import Optional
import logging

from backend.connectors.base import BaseConnector, ConnectorResult

logger = logging.getLogger(__name__)


class CalendarConnector(BaseConnector):
    """Fetch calendar events using macOS Calendar/Events."""

    name = "calendar"
    description = "Fetch calendar events from macOS Calendar"

    def __init__(self, days_back: int = 30, days_forward: int = 30):
        self.days_back = days_back
        self.days_forward = days_forward
        self._connected = False

    def connect(self, **kwargs) -> bool:
        """Check if Calendar is accessible."""
        try:
            result = subprocess.run(
                ["osascript", "-e", "tell application \"Calendar\" to get name of every calendar"],
                capture_output=True, text=True, timeout=10
            )
            self._connected = result.returncode == 0
            return self._connected
        except Exception:
            self._connected = False
            return False

    def disconnect(self) -> None:
        """No cleanup needed."""
        self._connected = False

    def fetch(self, since: Optional[datetime] = None, limit: int = 100) -> list[dict]:
        """Fetch calendar events via AppleScript."""
        if not self._connected and not self.connect():
            logger.warning("Calendar not accessible, using fallback")
            return self._fallback_fetch()

        end_date = (datetime.utcnow() + timedelta(days=self.days_forward)).strftime("%Y-%m-%d")
        start_date = (datetime.utcnow() - timedelta(days=self.days_back)).strftime("%Y-%m-%d")

        script = f'''
tell application "Calendar"
    set output to ""
    repeat with cal in calendars
        try
            set evts to (every event of cal whose start date is greater than or equal to date "{start_date}" and start date is less than or equal to date "{end_date}")
            repeat with evt in evts
                set output to output & "|" & title of evt
                set output to output & "|" & start date of evt as string
                set output to output & "|" & end date of evt as string
                set output to output & "|" & description of evt
                set output to output & "|" & location of evt
                set output to output & "||"
            end repeat
        end try
    end repeat
    return output
end tell
'''
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                logger.error(f"Calendar fetch failed: {result.stderr}")
                return self._fallback_fetch()

            events = []
            raw = result.stdout.strip()
            if not raw:
                return []

            entries = raw.split("||")
            for entry in entries:
                entry = entry.strip()
                if not entry:
                    continue
                lines = entry.split("|")
                if len(lines) < 5:
                    continue

                title = lines[0] or "(no title)"
                start_str = lines[1] or ""
                end_str = lines[2] or ""
                desc = lines[3] or ""
                location = lines[4] or ""

                try:
                    start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError):
                    start_dt = datetime.utcnow()

                try:
                    end_dt = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError):
                    end_dt = start_dt

                # Extract participants from attendees field if present
                participants = []
                if len(lines) > 5 and lines[5]:
                    participants = [p.strip() for p in lines[5].split(",") if p.strip()]

                events.append({
                    "source_type": "calendar",
                    "filename": f"event_{title[:30].replace(' ', '_')}.ics",
                    "title": title,
                    "full_text": f"Event: {title}\nStart: {start_dt}\nEnd: {end_dt}\nLocation: {location}\nDescription: {desc}",
                    "metadata": {
                        "start_at": start_dt.isoformat(),
                        "end_at": end_dt.isoformat(),
                        "location": location,
                        "description": desc,
                        "participants": participants,
                    },
                })

                if len(events) >= limit:
                    break

            logger.info(f"Calendar: fetched {len(events)} events")
            return events

        except Exception as e:
            logger.error(f"Calendar fetch error: {e}")
            return self._fallback_fetch()

    def _fallback_fetch(self) -> list[dict]:
        """Return empty list if Calendar not accessible."""
        logger.info("Calendar not available, returning empty")
        return []

    def get_stats(self) -> dict:
        """Get calendar stats."""
        if not self._connected:
            self.connect()
        return {
            "connected": self._connected,
            "days_back": self.days_back,
            "days_forward": self.days_forward,
        }

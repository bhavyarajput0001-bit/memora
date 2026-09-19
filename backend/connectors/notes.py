"""Apple Notes connector for MEMORA."""
import subprocess
import json
from datetime import datetime
from typing import Optional
import logging

from backend.connectors.base import BaseConnector, ConnectorResult

logger = logging.getLogger(__name__)


class AppleNotesConnector(BaseConnector):
    """Fetch notes from Apple Notes via AppleScript."""

    name = "apple_notes"
    description = "Fetch notes from Apple Notes app"

    def __init__(self, notebook: Optional[str] = None, days_back: int = 365):
        self.notebook = notebook
        self.days_back = days_back
        self._connected = False

    def connect(self, **kwargs) -> bool:
        """Check if Notes is accessible."""
        try:
            result = subprocess.run(
                ["osascript", "-e", "tell application \"Notes\" to get name of every account"],
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
        """Fetch notes from Apple Notes."""
        if not self._connected and not self.connect():
            logger.warning("Apple Notes not accessible")
            return []

        notebook_filter = ""
        if self.notebook:
            notebook_filter = f'whose name is "{self.notebook}"'

        script = f'''
tell application "Notes"
    set output to ""
    set {notebook_filter if notebook_filter else "theNotebooks"} to notebooks
    repeat with nb in theNotebooks
        set notesList to every note of nb
        repeat with n in notesList
            set noteName to name of n
            set noteBody to body of n
            set noteDate to modification date of n
            set output to output & "|" & noteName
            set output to output & "|" & noteBody
            set output to output & "|" & noteDate as string
            set output to output & "|" & (name of parent of n)
            set output to output & "||"
        end repeat
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
                logger.error(f"Notes fetch failed: {result.stderr}")
                return []

            notes = []
            raw = result.stdout.strip()
            if not raw:
                return []

            entries = raw.split("||")
            for entry in entries:
                entry = entry.strip()
                if not entry:
                    continue
                lines = entry.split("|")
                if len(lines) < 3:
                    continue

                title = lines[0] or "(no title)"
                body = lines[1] or ""
                date_str = lines[2] or ""
                notebook_name = lines[3] if len(lines) > 3 else "Unknown"

                try:
                    mod_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError):
                    mod_date = datetime.utcnow()

                # Skip old notes if since is specified
                if since and mod_date < since:
                    continue

                notes.append({
                    "source_type": "note",
                    "filename": f"note_{title[:30].replace(' ', '_')}.txt",
                    "title": title,
                    "full_text": f"{title}\n\n{body}",
                    "metadata": {
                        "notebook": notebook_name,
                        "modified_at": mod_date.isoformat(),
                        "created_at": mod_date.isoformat(),
                    },
                })

                if len(notes) >= limit:
                    break

            logger.info(f"Apple Notes: fetched {len(notes)} notes")
            return notes

        except Exception as e:
            logger.error(f"Notes fetch error: {e}")
            return []

    def get_stats(self) -> dict:
        """Get notes stats."""
        if not self._connected:
            self.connect()
        return {
            "connected": self._connected,
            "notebook": self.notebook,
            "days_back": self.days_back,
        }

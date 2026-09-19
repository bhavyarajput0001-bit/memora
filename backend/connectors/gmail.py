"""Gmail connector for MEMORA — fetches emails via IMAP."""
import imaplib
import email
from email.header import decode_header
from datetime import datetime
from typing import Optional
import logging

from backend.connectors.base import BaseConnector, ConnectorResult
from backend.config import EMBEDDING_ENABLED

logger = logging.getLogger(__name__)


class GmailConnector(BaseConnector):
    """Connect to Gmail via IMAP and fetch emails for ingestion."""

    name = "gmail"
    description = "Fetch emails from Gmail via IMAP"

    def __init__(self, email_addr: str, app_password: str):
        self.email_addr = email_addr
        self.app_password = app_password
        self._mail: Optional[imaplib.IMAP4_SSL] = None

    def connect(self, **kwargs) -> bool:
        """Connect to Gmail via IMAP SSL."""
        try:
            self._mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
            self._mail.login(self.email_addr, self.app_password)
            self._mail.select("INBOX")
            logger.info(f"Gmail connector connected: {self.email_addr}")
            return True
        except Exception as e:
            logger.error(f"Gmail connection failed: {e}")
            return False

    def disconnect(self) -> None:
        """Close IMAP connection."""
        if self._mail:
            try:
                self._mail.close()
                self._mail.logout()
            except Exception:
                pass
            self._mail = None

    def fetch(
        self,
        since: Optional[datetime] = None,
        limit: int = 100,
        folder: str = "INBOX",
        unread_only: bool = False,
    ) -> list[dict]:
        """Fetch emails from Gmail."""
        if not self._mail:
            raise RuntimeError("Not connected. Call connect() first.")

        messages = []
        try:
            # Search criteria
            search_criteria = ["ALL"]
            if unread_only:
                search_criteria = ["UNSEEN"]
            if since:
                date_str = since.strftime("%d-%b-%Y")
                search_criteria = [f"SINCE {date_str}"]

            status, data = self._mail.search(None, *search_criteria)
            if status != "OK":
                logger.error(f"Gmail search failed: {status}")
                return []

            msg_ids = data[0].split()
            # Fetch latest N messages
            msg_ids = msg_ids[-limit:]

            for msg_id in msg_ids:
                status, msg_data = self._mail.fetch(msg_id, "(RFC822)")
                if status != "OK":
                    continue

                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)

                # Decode subject
                subject, encoding = decode_header(email_message["Subject"] or "")[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8", errors="replace")

                # Get sender
                sender = email_message["From"] or "unknown"

                # Get body
                body = ""
                if email_message.is_multipart():
                    for part in email_message.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/plain":
                            try:
                                body = part.get_payload(decode=True).decode(
                                    part.get_content_charset() or "utf-8", errors="replace"
                                )
                                break
                            except Exception:
                                continue
                else:
                    try:
                        body = email_message.get_payload(decode=True).decode(
                            email_message.get_content_charset() or "utf-8", errors="replace"
                        )
                    except Exception:
                        body = str(email_message.get_payload())

                # Get date
                date_str = email_message.get("Date", "")
                try:
                    msg_date = datetime.fromisoformat(
                        date_str.replace("Z", "+00:00")
                    )
                except (ValueError, AttributeError):
                    msg_date = datetime.utcnow()

                messages.append({
                    "source_type": "email",
                    "filename": f"email_{msg_id.decode()}.eml",
                    "title": subject or "(no subject)",
                    "full_text": f"Subject: {subject}\nFrom: {sender}\nDate: {date_str}\n\n{body}",
                    "metadata": {
                        "sender": sender,
                        "subject": subject,
                        "date": msg_date.isoformat(),
                        "message_id": msg_id.decode(),
                        "is_unread": email_message.get("Unread", "No").lower() == "yes",
                    },
                })

            logger.info(f"Gmail: fetched {len(messages)} emails")
            return messages

        except Exception as e:
            logger.error(f"Gmail fetch error: {e}")
            return []

    def get_stats(self) -> dict:
        """Get connection stats."""
        if not self._mail:
            return {"connected": False, "messages_count": 0}
        try:
            status, data = self._mail.select("INBOX")
            count = int(data[0]) if data[0] else 0
            return {"connected": True, "messages_count": count}
        except Exception:
            return {"connected": False, "messages_count": 0}

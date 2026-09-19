"""MEMORA connector API routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.connectors.manager import ConnectorManager, ConnectorConfig

router = APIRouter(prefix="/api/v1/connectors", tags=["connectors"])

# Global connector manager instance
_connectors: Optional[ConnectorManager] = None


def get_connector_manager() -> ConnectorManager:
    global _connectors
    if _connectors is None:
        _connectors = ConnectorManager()
    return _connectors


class GmailConfig(BaseModel):
    email: str
    app_password: str
    folder: str = "INBOX"
    unread_only: bool = False
    limit: int = 50


class CalendarConfig(BaseModel):
    days_back: int = 30
    days_forward: int = 30


class NotesConfig(BaseModel):
    notebook: Optional[str] = None
    days_back: int = 365
    limit: int = 50


class ConnectorRunRequest(BaseModel):
    gmail: Optional[GmailConfig] = None
    calendar: Optional[CalendarConfig] = None
    notes: Optional[NotesConfig] = None


@router.get("/status")
async def get_connector_status():
    """Get connector status and last run times."""
    mgr = get_connector_manager()
    return mgr.get_stats()


@router.post("/run")
async def run_connectors(request: ConnectorRunRequest):
    """Run connectors and return results."""
    mgr = get_connector_manager()
    if request.gmail:
        mgr.config.gmail_email = request.gmail.email
        mgr.config.gmail_app_password = request.gmail.app_password
        mgr.config.gmail_folder = request.gmail.folder
        mgr.config.gmail_unread_only = request.gmail.unread_only
        mgr.config.gmail_limit = request.gmail.limit
    if request.calendar:
        mgr.config.calendar_days_back = request.calendar.days_back
        mgr.config.calendar_days_forward = request.calendar.days_forward
    if request.notes:
        mgr.config.notes_notebook = request.notes.notebook
        mgr.config.notes_days_back = request.notes.days_back
        mgr.config.notes_limit = request.notes.limit

    mgr.config.enabled = True
    results = mgr.run_all()
    return {"success": True, "results": results}


@router.post("/ingest")
async def ingest_from_connectors(request: ConnectorRunRequest):
    """Run connectors and ingest all fetched items into MEMORA."""
    mgr = get_connector_manager()
    if request.gmail:
        mgr.config.gmail_email = request.gmail.email
        mgr.config.gmail_app_password = request.gmail.app_password
        mgr.config.gmail_folder = request.gmail.folder
        mgr.config.gmail_unread_only = request.gmail.unread_only
        mgr.config.gmail_limit = request.gmail.limit
    if request.calendar:
        mgr.config.calendar_days_back = request.calendar.days_back
        mgr.config.calendar_days_forward = request.calendar.days_forward
    if request.notes:
        mgr.config.notes_notebook = request.notes.notebook
        mgr.config.notes_days_back = request.notes.days_back
        mgr.config.notes_limit = request.notes.limit

    mgr.config.enabled = True
    results = mgr.run_all()

    # Ingest all fetched items
    from backend.services import ingestion
    total_ingested = 0
    errors = []

    for source, items in results.items():
        count = items.get("items", 0)
        if count > 0:
            # Get the connector and ingest items
            if source == "gmail":
                gmail = mgr.get_gmail()
                if gmail:
                    emails = gmail.fetch(limit=count)
                    for email_data in emails:
                        try:
                            parsed = ingestion.ingest(
                                email_data["full_text"].encode(),
                                email_data["filename"]
                            )
                            doc_id = ingestion.persist_document(parsed)
                            total_ingested += 1
                        except Exception as e:
                            errors.append(f"Gmail ingest error: {e}")
            elif source == "calendar":
                calendar = mgr.get_calendar()
                if calendar:
                    events = calendar.fetch()
                    for evt in events:
                        try:
                            parsed = ingestion.ingest(
                                evt["full_text"].encode(),
                                evt["filename"]
                            )
                            doc_id = ingestion.persist_document(parsed)
                            total_ingested += 1
                        except Exception as e:
                            errors.append(f"Calendar ingest error: {e}")
            elif source == "notes":
                notes = mgr.get_notes()
                if notes:
                    note_items = notes.fetch(limit=count)
                    for note in note_items:
                        try:
                            parsed = ingestion.ingest(
                                note["full_text"].encode(),
                                note["filename"]
                            )
                            doc_id = ingestion.persist_document(parsed)
                            total_ingested += 1
                        except Exception as e:
                            errors.append(f"Notes ingest error: {e}")

    return {
        "success": True,
        "total_ingested": total_ingested,
        "errors": errors,
        "connector_results": results,
    }

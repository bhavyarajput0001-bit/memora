"""MEMORA timeline API route."""
from fastapi import APIRouter

from backend.services import retrieval

router = APIRouter(prefix="/api/v1/timeline", tags=["timeline"])


@router.get("/")
async def get_timeline(days: int = 30, limit: int = 50):
    """Get timeline events."""
    events = retrieval.get_timeline(days=days, limit=limit)
    return {"events": events, "count": len(events), "days": days}


@router.get("/summary")
async def get_timeline_summary(days: int = 30):
    """Get timeline summary."""
    events = retrieval.get_timeline(days=days, limit=100)
    monthly_counts = {}
    for evt in events:
        date_str = evt.get("start_at", "")[:7]
        monthly_counts[date_str] = monthly_counts.get(date_str, 0) + 1
    return {
        "total_events": len(events),
        "monthly_counts": monthly_counts,
        "days_covered": days,
    }

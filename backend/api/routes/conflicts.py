"""MEMORA conflicts API route."""
from fastapi import APIRouter, HTTPException

from backend.services import conflict as conflict_service

router = APIRouter(prefix="/api/v1/conflicts", tags=["conflicts"])


@router.get("/")
async def get_conflicts(status: str = "unresolved"):
    """Get conflicts."""
    conflicts = conflict_service.get_conflicts(status=status)
    return {"conflicts": conflicts, "count": len(conflicts), "status": status}


@router.post("/detect")
async def detect_conflicts():
    """Run conflict detection."""
    conflicts = conflict_service.detect_conflicts()
    return {"new_conflicts_detected": len(conflicts), "conflicts": conflicts}


@router.post("/{conflict_id}/resolve")
async def resolve_conflict(conflict_id: str, resolution: str, explanation: str = ""):
    """Resolve a conflict."""
    success = conflict_service.resolve_conflict(conflict_id, resolution, explanation)
    if not success:
        raise HTTPException(status_code=404, detail="Conflict not found")
    return {"success": True, "conflict_id": conflict_id, "resolution": resolution}

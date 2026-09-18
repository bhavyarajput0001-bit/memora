"""MEMORA actions API route."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.services import actions as action_service

router = APIRouter(prefix="/api/v1/actions", tags=["actions"])


class ProposeActionRequest(BaseModel):
    type: str
    description: str
    parameters: Optional[dict] = None


@router.post("/propose")
async def propose(request: ProposeActionRequest):
    """Propose a new action."""
    action = action_service.propose_action(
        action_type=request.type,
        description=request.description,
        parameters=request.parameters,
    )
    return {"success": True, "action": action}


@router.post("/{action_id}/approve")
async def approve(action_id: str):
    """Approve an action."""
    action = action_service.approve_action(action_id)
    return {"success": True, "action": action}


@router.post("/{action_id}/execute")
async def execute(action_id: str):
    """Execute an approved action."""
    action = action_service.execute_action(action_id)
    return {"success": True, "action": action}


@router.get("/")
async def list_actions(status: Optional[str] = None):
    """List actions."""
    actions_list = action_service.get_actions(status=status)
    return {"actions": actions_list, "count": len(actions_list)}

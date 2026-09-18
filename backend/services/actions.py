"""MEMORA action system — propose/approve/execute actions."""
from datetime import datetime, timezone
from typing import Optional

from backend.db import get_session
from backend.models import Action
from backend.utils import generate_id, utcnow


def propose_action(
    action_type: str,
    description: str,
    parameters: Optional[dict] = None,
) -> dict:
    """Create a proposed action."""
    with get_session() as db:
        action = Action(
            id=generate_id("act_"),
            type=action_type,
            description=description,
            parameters_json=parameters or {},
            status="proposed",
            user_approval=False,
            created_at=utcnow(),
        )
        db.add(action)
        db.commit()
        db.refresh(action)
        
        return {
            "id": action.id,
            "type": action.type,
            "description": action.description,
            "parameters": action.parameters_json,
            "status": action.status,
            "created_at": action.created_at.isoformat(),
        }


def approve_action(action_id: str) -> dict:
    """Approve a proposed action."""
    with get_session() as db:
        action = db.query(Action).filter(Action.id == action_id).first()
        if not action:
            raise ValueError(f"Action not found: {action_id}")
        
        action.user_approval = True
        action.status = "approved"
        db.commit()
        db.refresh(action)
        
        return {
            "id": action.id,
            "status": "approved",
        }


def execute_action(action_id: str) -> dict:
    """Execute an approved action."""
    with get_session() as db:
        action = db.query(Action).filter(Action.id == action_id).first()
        if not action:
            raise ValueError(f"Action not found: {action_id}")
        
        if action.status != "approved":
            raise ValueError(f"Action not approved: {action_id}")
        
        # Execute based on type
        result = _execute_by_type(action.type, action.parameters_json)
        
        action.status = "executed"
        action.result_json = result
        action.executed_at = utcnow()
        db.commit()
        db.refresh(action)
        
        return {
            "id": action.id,
            "type": action.type,
            "status": "executed",
            "result": result,
        }


def _execute_by_type(action_type: str, parameters: dict) -> dict:
    """Execute an action based on its type."""
    if action_type == "create_reminder":
        return {
            "type": "reminder",
            "scheduled_for": parameters.get("scheduled_for"),
            "message": parameters.get("message"),
        }
    elif action_type == "create_task":
        return {
            "type": "task",
            "title": parameters.get("title"),
            "description": parameters.get("description"),
        }
    elif action_type == "draft_email":
        return {
            "type": "email",
            "to": parameters.get("to"),
            "subject": parameters.get("subject"),
            "body": parameters.get("body"),
        }
    elif action_type == "generate_summary":
        return {
            "type": "summary",
            "content": parameters.get("content", "Summary generated"),
        }
    else:
        return {"type": action_type, "status": "executed"}


def get_actions(status: Optional[str] = None) -> list[dict]:
    """Get actions, optionally filtered by status."""
    with get_session() as db:
        query = db.query(Action)
        if status:
            query = query.filter(Action.status == status)
        actions = query.order_by(Action.created_at.desc()).limit(50).all()
        
        return [
            {
                "id": a.id,
                "type": a.type,
                "description": a.description,
                "parameters": a.parameters_json,
                "status": a.status,
                "user_approval": a.user_approval,
                "created_at": a.created_at.isoformat(),
                "executed_at": a.executed_at.isoformat() if a.executed_at else None,
            }
            for a in actions
        ]

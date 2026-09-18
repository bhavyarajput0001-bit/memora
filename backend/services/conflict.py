"""MEMORA conflict detection engine.

Detects conflicts between facts about the same subject/predicate but different objects.
Does NOT silently overwrite conflicts.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import text

from backend.db import get_session
from backend.models import Fact, Conflict


CONFLICT_FIELDS = ["object", "status", "confidence"]


def detect_conflicts() -> list[dict]:
    """Detect all conflicts in the knowledge base."""
    with get_session() as db:
        # Find facts with same subject + predicate but different objects
        results = db.execute(text("""
            SELECT 
                f1.id as fact_a_id,
                f1.subject as subject,
                f1.predicate as predicate,
                f1.object as object_a,
                f2.id as fact_b_id,
                f2.object as object_b,
                f1.observed_at as observed_a,
                f2.observed_at as observed_b,
                f1.source_id as source_a_id,
                f2.source_id as source_b_id,
                f1.confidence as confidence_a,
                f2.confidence as confidence_b
            FROM facts f1
            JOIN facts f2 ON f1.subject = f2.subject 
                AND f1.predicate = f2.predicate 
                AND f1.id < f2.id
                AND f1.object != f2.object
                AND f2.status NOT IN ('outdated', 'superseded')
                AND f1.status NOT IN ('outdated', 'superseded')
            ORDER BY f1.subject, f1.predicate
        """))
        
        conflicts = []
        for row in results:
            # Check if this conflict already exists
            existing = db.query(Conflict).filter(
                ((Conflict.fact_a_id == row[0] and Conflict.fact_b_id == row[1]) |
                 (Conflict.fact_a_id == row[1] and Conflict.fact_b_id == row[0]))
            ).first()
            
            if not existing:
                new_conflict = Conflict(
                    fact_a_id=row[0],
                    fact_b_id=row[1],
                    field="object",
                    resolution="unresolved",
                    explanation=_generate_explanation(row),
                    status="unresolved",
                )
                db.add(new_conflict)
                conflicts.append({
                    "id": "conflict_" + str(len(conflicts)),
                    "fact_a_id": row[0],
                    "fact_b_id": row[1],
                    "subject": row[1],
                    "predicate": row[2],
                    "object_a": row[3],
                    "object_b": row[5],
                    "observed_a": row[6],
                    "observed_b": row[7],
                    "source_a_id": row[8],
                    "source_b_id": row[9],
                    "confidence_a": row[10],
                    "confidence_b": row[11],
                    "resolution": "unresolved",
                })
        
        db.commit()
        return conflicts


def _generate_explanation(row) -> str:
    """Generate a human-readable explanation of the conflict."""
    return (
        f"Facts about '{row[1]}' '{row[2]}' conflict:\n"
        f"  - Value A: '{row[3]}' (observed: {row[6]}, confidence: {row[10]})\n"
        f"  - Value B: '{row[5]}' (observed: {row[7]}, confidence: {row[11]})"
    )


def get_conflicts(status: Optional[str] = None) -> list[dict]:
    """Get all conflicts, optionally filtered by status."""
    with get_session() as db:
        query = db.query(Conflict)
        if status:
            query = query.filter(Conflict.status == status)
        conflicts = query.order_by(Conflict.created_at.desc()).all()
        
        results = []
        for c in conflicts:
            fact_a = db.query(Fact).filter(Fact.id == c.fact_a_id).first()
            fact_b = db.query(Fact).filter(Fact.id == c.fact_b_id).first()
            doc_a = db.query(type('D', (), {'filename': None})).filter(type('D', (), {'id': fact_a.source_id})).first() if fact_a else None
            doc_b = db.query(type('D', (), {'filename': None})).filter(type('D', (), {'id': fact_b.source_id})).first() if fact_b else None
            
            results.append({
                "id": c.id,
                "subject": fact_a.subject if fact_a else None,
                "predicate": fact_a.predicate if fact_a else None,
                "fact_a": {
                    "id": fact_a.id,
                    "object": fact_a.object,
                    "observed_at": fact_a.observed_at.isoformat() if fact_a and fact_a.observed_at else None,
                    "confidence": fact_a.confidence if fact_a else None,
                    "source_id": fact_a.source_id if fact_a else None,
                },
                "fact_b": {
                    "id": fact_b.id,
                    "object": fact_b.object,
                    "observed_at": fact_b.observed_at.isoformat() if fact_b and fact_b.observed_at else None,
                    "confidence": fact_b.confidence if fact_b else None,
                    "source_id": fact_b.source_id if fact_b else None,
                },
                "resolution": c.resolution,
                "explanation": c.explanation,
                "status": c.status,
                "created_at": c.created_at.isoformat(),
            })
        
        return results


def resolve_conflict(conflict_id: str, resolution: str, explanation: str = "") -> bool:
    """Mark a conflict as resolved."""
    with get_session() as db:
        conflict = db.query(Conflict).filter(Conflict.id == conflict_id).first()
        if not conflict:
            return False
        
        conflict.resolution = resolution
        conflict.status = "resolved"
        if explanation:
            conflict.explanation = explanation
        
        db.commit()
        return True

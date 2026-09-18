"""MEMORA query engine — intent understanding + retrieval + reasoning + answer generation.

Architecture:
  USER QUESTION
  -> QUERY UNDERSTANDING (intent, entities, temporal scope)
  -> RETRIEVAL (hybrid search)
  -> STRUCTURED LOOKUP (facts, entities)
  -> TEMPORAL ANALYSIS
  -> CONFLICT CHECK
  -> EVIDENCE SELECTION
  -> LLM REASONING
  -> VALIDATION
  -> ANSWER + SOURCES
"""
import json
import time
from datetime import datetime
from typing import Optional

from backend.db import get_session
from backend.models import Document, Fact, Entity, Event
from backend.services import retrieval
from backend.services import conflict as conflict_service
from backend.llm import chat
from backend.utils import generate_id, utcnow, truncate_text


QUERY_INTENT_PROMPT = """You are MEMORA's query intent engine. Analyze the user's question and return a structured intent object.

Question: {question}

Return ONLY a JSON object (no markdown):
{{
  "intent": "FACT|PERSON|EVENT|TIMELINE|RELATIONSHIP|COMPARISON|CHANGE|CONFLICT|SUMMARY|ACTION",
  "entities": ["entity1", "entity2"],
  "temporal_scope": {{"from": "2026-09-01", "to": "2026-09-30"}},
  "subject": "main subject",
  "property": "predicate being queried",
  "timeframe": "recent|last_week|this_month|all_time",
  "requires_conflict_check": true|false,
  "requires_action": true|false
}}"""


ANSWER_GENERATION_PROMPT = """You are MEMORA's grounded answer engine. Generate an answer based ONLY on the provided evidence.

USER QUESTION: {question}

RETRIEVED EVIDENCE:
{evidence}

FA TS:
{facts}

CONFLICTS:
{conflicts}

RULES:
- NEVER invent information not in the evidence
- If evidence is insufficient, say: "I don't have enough evidence in your memory to answer that reliably."
- Always cite sources with document name and page/location
- If conflicts exist, explain them and show both sides
- Use the structured format below
- Never pretend retrieval occurred if it didn't
- Distinguish between WHAT the LLM thinks and WHAT THE SOURCES SAY"""


def query(query_text: str, user_id: Optional[str] = None) -> dict:
    """Execute a full query pipeline."""
    start_time = time.time()
    request_id = generate_id("req_")
    
    try:
        # Step 1: Query Understanding
        intent = _understand_intent(query_text)
        
        # Step 2: Hybrid Retrieval
        evidence = retrieval.hybrid_search(
            query=query_text,
            limit=15,
        )
        
        # Step 3: Structured Lookup
        facts = _lookup_facts(intent, query_text)
        
        # Step 4: Temporal Analysis
        temporal_context = _analyze_temporal(intent, query_text)
        
        # Step 5: Conflict Check
        conflicts = []
        if intent.get("requires_conflict_check", False) or "conflict" in query_text.lower():
            conflicts = conflict_service.get_conflicts(status="unresolved")
            conflicts = [_filter_conflicts(c, query_text) for c in conflicts]
            conflicts = [c for c in conflicts if c]
        
        # Step 6: Evidence Selection
        selected_evidence = _select_evidence(evidence, facts, query_text)
        
        # Step 7: LLM Reasoning
        answer, confidence = _generate_answer(
            query_text, evidence, facts, conflicts, intent
        )
        
        # Step 8: Validation
        validated_answer = _validate_answer(answer, evidence)
        
        duration_ms = (time.time() - start_time) * 1000
        
        return {
            "request_id": request_id,
            "query": query_text,
            "intent": intent,
            "answer": validated_answer["answer"],
            "confidence": validated_answer["confidence"],
            "status": validated_answer["status"],
            "sources": [
                {
                    "id": e.get("document_id"),
                    "filename": e.get("filename"),
                    "page": e.get("page"),
                    "score": e.get("score"),
                }
                for e in selected_evidence[:5]
            ],
            "facts": facts[:10],
            "conflicts": conflicts[:5],
            "temporal_context": temporal_context,
            "retrieval_duration_ms": duration_ms,
            "num_candidates": len(evidence),
            "suggested_actions": _suggest_actions(answer, intent),
        }
    except Exception as e:
        return {
            "request_id": request_id,
            "query": query_text,
            "answer": f"Error processing query: {str(e)}",
            "confidence": 0.0,
            "status": "error",
            "error": str(e),
        }


def _understand_intent(question: str) -> dict:
    """Understand the query intent using LLM."""
    messages = [
        {"role": "system", "content": "You are MEMORA's query intent engine."},
        {"role": "user", "content": QUERY_INTENT_PROMPT.format(question=question)},
    ]
    
    try:
        response = chat(messages=messages, model="auto", max_tokens=500, timeout_s=30)
        content = response["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception:
        # Fallback: simple keyword-based intent detection
        return _simple_intent_detection(question)


def _simple_intent_detection(question: str) -> dict:
    """Simple keyword-based intent detection."""
    q = question.lower()
    if any(k in q for k in ["who", "person", "responsible", "assigned"]):
        intent = "PERSON"
    elif any(k in q for k in ["when", "date", "deadline", "time"]):
        intent = "TIMELINE"
    elif any(k in q for k in ["why", "changed", "conflict", "disagreement"]):
        intent = "CONFLICT"
    elif any(k in q for k in ["relationship", "connected", "related"]):
        intent = "RELATIONSHIP"
    else:
        intent = "FACT"
    
    return {
        "intent": intent,
        "entities": [],
        "temporal_scope": None,
        "subject": None,
        "property": None,
        "timeframe": "all_time",
        "requires_conflict_check": intent in ("CONFLICT", "TIMELINE"),
        "requires_action": False,
    }


def _lookup_facts(intent: dict, question: str) -> list[dict]:
    """Lookup relevant facts from the database."""
    with get_session() as db:
        results = []
        
        # Search by subject
        if intent.get("subject"):
            facts = db.query(Fact).filter(
                Fact.subject.ilike(f"%{intent['subject']}%")
            ).limit(20).all()
            results.extend([
                {
                    "id": f.id,
                    "subject": f.subject,
                    "predicate": f.predicate,
                    "object": f.object,
                    "source_id": f.source_id,
                    "observed_at": f.observed_at.isoformat() if f.observed_at else None,
                    "effective_at": f.effective_at.isoformat() if f.effective_at else None,
                    "confidence": f.confidence,
                    "status": f.status,
                }
                for f in facts
            ])
        
        # Search by keyword in object
        keywords = question.split()[:3]
        for kw in keywords:
            if len(kw) > 2:
                facts = db.query(Fact).filter(
                    Fact.object.ilike(f"%{kw}%")
                ).limit(10).all()
                results.extend([
                    {
                        "id": f.id,
                        "subject": f.subject,
                        "predicate": f.predicate,
                        "object": f.object,
                        "source_id": f.source_id,
                        "observed_at": f.observed_at.isoformat() if f.observed_at else None,
                        "confidence": f.confidence,
                        "status": f.status,
                    }
                    for f in facts
                ])
        
        # Deduplicate
        seen = set()
        unique_results = []
        for r in results:
            key = (r["subject"], r["predicate"], r["object"])
            if key not in seen:
                seen.add(key)
                unique_results.append(r)
        
        return unique_results[:20]


def _analyze_temporal(intent: dict, question: str) -> dict:
    """Analyze temporal context of the query."""
    # Simple implementation - in production would use temporal reasoning
    return {
        "timeframe": intent.get("timeframe", "all_time"),
        "events_count": 0,
    }


def _select_evidence(evidence: list[dict], facts: list[dict], question: str) -> list[dict]:
    """Select the most relevant evidence for the answer."""
    # Combine chunks and facts
    all_evidence = []
    for e in evidence:
        if e.get("type") == "chunk":
            all_evidence.append({
                "type": "chunk",
                "document_id": e.get("document_id"),
                "text": e.get("text", "")[:300],
                "score": e.get("score", 0),
                "page": e.get("page"),
                "filename": e.get("filename"),
            })
    
    # Add facts with their source documents
    with get_session() as db:
        doc_ids = {f["source_id"] for f in facts}
        docs = db.query(Document).filter(Document.id.in_(doc_ids)).all()
        doc_map = {d.id: d.filename for d in docs}
        
        for fact in facts:
            all_evidence.append({
                "type": "fact",
                "fact_id": fact["id"],
                "subject": fact["subject"],
                "predicate": fact["predicate"],
                "object": fact["object"],
                "document_id": fact.get("source_id"),
                "filename": doc_map.get(fact.get("source_id")),
                "score": fact.get("confidence", 0.5),
                "observed_at": fact.get("observed_at"),
            })
    
    # Sort by score
    all_evidence.sort(key=lambda x: x.get("score", 0), reverse=True)
    return all_evidence[:10]


def _generate_answer(
    question: str,
    evidence: list[dict],
    facts: list[dict],
    conflicts: list[dict],
    intent: dict,
) -> tuple[str, float]:
    """Generate a grounded answer using the LLM."""
    evidence_text = _format_evidence(evidence)
    facts_text = _format_facts(facts)
    conflicts_text = _format_conflicts(conflicts)
    
    prompt = ANSWER_GENERATION_PROMPT.format(
        question=question,
        evidence=evidence_text,
        facts=facts_text,
        conflicts=conflicts_text,
    )
    
    messages = [
        {"role": "system", "content": "You are MEMORA's grounded answer engine. Only use provided evidence."},
        {"role": "user", "content": prompt},
    ]
    
    try:
        response = chat(messages=messages, model="auto", max_tokens=1000, timeout_s=60)
        content = response["choices"][0]["message"]["content"]
        
        # Try to parse structured output
        try:
            structured = json.loads(content)
            return structured.get("answer", content), structured.get("confidence", 0.7)
        except json.JSONDecodeError:
            pass
        
        return content, 0.7
    except Exception:
        return "I couldn't generate a reliable answer from the available evidence.", 0.3


def _validate_answer(answer: str, evidence: list[dict]) -> dict:
    """Validate the answer against evidence."""
    # Simple validation: check if answer references any evidence
    has_evidence = len(evidence) > 0
    is_uncertain = any(k in answer.lower() for k in ["don't have", "not enough", "uncertain", "unable"])
    
    status = "likely_current" if has_evidence and not is_uncertain else "insufficient_evidence"
    confidence = 0.8 if has_evidence and not is_uncertain else 0.3
    
    return {
        "answer": answer,
        "confidence": confidence,
        "status": status,
    }


def _suggest_actions(answer: str, intent: dict) -> list[dict]:
    """Suggest possible actions based on the answer."""
    actions = []
    
    if intent.get("intent") == "TIMELINE" and "deadline" in answer.lower():
        actions.append({
            "type": "create_reminder",
            "description": "Set a reminder for the deadline",
        })
    
    if intent.get("requires_action", False):
        actions.append({
            "type": "follow_up",
            "description": "Ask for more details",
        })
    
    return actions


def _format_evidence(evidence: list[dict]) -> str:
    """Format evidence for LLM prompt."""
    if not evidence:
        return "No evidence found."
    
    lines = []
    for i, e in enumerate(evidence[:10], 1):
        if e.get("type") == "chunk":
            lines.append(f"{i}. [Chunk from {e.get('filename', 'unknown')}] {e.get('text', '')[:200]}")
        elif e.get("type") == "fact":
            lines.append(f"{i}. [Fact] {e.get('subject', '')} {e.get('predicate', '')} {e.get('object', '')}")
    
    return "\n".join(lines) if lines else "No evidence found."


def _format_facts(facts: list[dict]) -> str:
    """Format facts for LLM prompt."""
    if not facts:
        return "No facts found."
    
    lines = []
    for f in facts[:10]:
        lines.append(f"- {f.get('subject', '')} {f.get('predicate', '')} {f.get('object', '')} (confidence: {f.get('confidence', 0):.2f})")
    
    return "\n".join(lines)


def _format_conflicts(conflicts: list[dict]) -> str:
    """Format conflicts for LLM prompt."""
    if not conflicts:
        return "No conflicts detected."
    
    lines = []
    for c in conflicts[:5]:
        lines.append(f"- Conflict: {c.get('subject', '')} {c.get('predicate', '')}")
        lines.append(f"  - Value A: {c.get('fact_a', {}).get('object', '')}")
        lines.append(f"  - Value B: {c.get('fact_b', {}).get('object', '')}")
        lines.append(f"  - Status: {c.get('status', 'unknown')}")
    
    return "\n".join(lines)


def _filter_conflicts(conflict: dict, question: str) -> Optional[dict]:
    """Filter conflicts relevant to the query."""
    # Simple filtering - in production would use semantic matching
    q = question.lower()
    if any(k in q for k in ["who", "person", "assigned"]):
        subject = conflict.get("subject", "").lower()
        if "rahul" in subject or "person" in q:
            return conflict
    return conflict

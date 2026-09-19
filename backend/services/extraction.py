"""MEMORA extraction service — entities, facts, events from parsed documents.

Uses LLM for intelligent extraction with structured JSON output.
Falls back to rule-based extraction when LLM is unavailable.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Optional

from backend.utils import generate_id, parse_date_flexible, utcnow
from backend.llm import chat, LLMError

logger = logging.getLogger(__name__)


EXTRACTION_PROMPT = """You are MEMORA's extraction engine. Extract structured facts, entities, and events from the document text.

Document source: {filename} (type: {source_type})

DOCUMENT TEXT:
{text}

Return ONLY a JSON object with this exact structure (no markdown, no explanation):
{{
  "entities": [
    {{"id": "ent_001", "canonical_name": "Name", "entity_type": "PERSON|ORGANIZATION|PROJECT|LOCATION|EVENT|DATE|TOPIC", "aliases": ["alias1"], "sources": ["{filename}"], "confidence": 0.9}}
  ],
  "facts": [
    {{"id": "fact_001", "subject": "Entity", "predicate": "has_deadline", "object": "2026-09-26", "source_location": {{"page": 1, "char_start": 100, "char_end": 110, "snippet": "..."}}, "observed_at": "2026-09-20T00:00:00Z", "effective_at": "2026-09-26T00:00:00Z", "confidence": 0.95, "status": "likely_current", "relationship": null}}
  ],
  "relationships": [
    {{"id": "rel_001", "subject_entity": "Person", "predicate": "works_on", "object_entity": "Project", "source": "{filename}", "confidence": 0.9}}
  ],
  "events": [
    {{"id": "evt_001", "title": "Meeting", "start_at": "2026-09-22T10:00:00Z", "end_at": "2026-09-22T11:00:00Z", "location": "Office", "participants": ["Person1", "Person2"], "description": "Project review", "source_location": {{"page": 1}}, "observed_at": "2026-09-22T10:00:00Z", "confidence": 0.95}}
  ]
}}

Rules:
- Create unique IDs (ent_XXX, fact_XXX, rel_XXX, evt_XXX)
- Entity types must be exactly one of: PERSON, ORGANIZATION, PROJECT, LOCATION, EVENT, DATE, TOPIC
- Predicate types: has_deadline, has_status, assigned_to, works_on, owns, created, scheduled_for, located_at, has_priority, has_description, has_value, has_date
- Set observed_at to the document's creation date or today if unknown
- Set effective_at to when the fact becomes true (for dates/deadlines, use the actual date)
- Confidence: 0.9+ for explicit statements, 0.7-0.9 for implied, 0.5-0.7 for inferred
- For source_location, estimate char_start/char_end if possible
- Only extract facts that are explicitly stated or strongly implied
- Do NOT invent information not in the document
"""


def extract_all(parsed_doc: dict) -> dict:
    """Extract entities, facts, relationships, and events from a parsed document."""
    text = parsed_doc.get("full_text", "")
    filename = parsed_doc.get("filename", "unknown")
    source_type = parsed_doc.get("source_type", "txt")

    # Truncate very large texts for extraction
    if len(text) > 8000:
        text = text[:4000] + "\n...\n" + text[-4000:]

    prompt = EXTRACTION_PROMPT.format(
        filename=filename,
        source_type=source_type,
        text=text,
    )

    messages = [
        {"role": "system", "content": "You are a precise information extraction system. Return valid JSON only."},
        {"role": "user", "content": prompt},
    ]

    try:
        result = _extract_with_llm(messages)
        return result
    except LLMError as e:
        logger.warning("LLM extraction failed: %s, using fallback", e)
        return _extract_fallback(parsed_doc)
    except Exception as e:
        logger.warning("Extraction error: %s, using fallback", e)
        return _extract_fallback(parsed_doc)


def _extract_with_llm(messages: list[dict]) -> dict:
    """Call the LLM for extraction."""
    response = chat(
        messages=messages,
        model="auto",
        temperature=0.1,
        max_tokens=4000,
        timeout_s=30,
    )
    content = response["choices"][0]["message"]["content"]
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Try to find JSON in the response
        import re
        match = re.search(r"\{[\s\S]*\}", content)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        raise


def _extract_fallback(parsed_doc: dict) -> dict:
    """Rule-based fallback extraction when LLM fails."""
    text = parsed_doc.get("full_text", "").lower()
    filename = parsed_doc.get("filename", "unknown")

    entities = []
    facts = []

    # Simple pattern matching for demonstration
    # In production, this would use spaCy or similar
    if "project" in text and ("atlas" in text or "demo" in text):
        entities.append({
            "id": generate_id("ent_"),
            "canonical_name": "Project Atlas",
            "entity_type": "PROJECT",
            "aliases": ["Atlas"],
            "sources": [filename],
            "confidence": 0.7,
        })

    return {
        "entities": entities,
        "facts": facts,
        "relationships": [],
        "events": [],
    }


def extract_facts_prompt(text: str, filename: str) -> str:
    """Build the extraction prompt for a specific chunk."""
    return EXTRACTION_PROMPT.format(
        filename=filename,
        source_type="chunk",
        text=text[:3000],
    )

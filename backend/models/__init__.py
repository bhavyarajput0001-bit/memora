"""MEMORA SQLAlchemy models — the memory schema.

Every meaningful fact is representable as:
FACT, SUBJECT, PREDICATE, OBJECT, SOURCE, SOURCE LOCATION,
OBSERVED TIME, EFFECTIVE TIME, CONFIDENCE, STATUS, RELATIONSHIP, CONFLICT STATE
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Float, Integer, Boolean, DateTime,
    ForeignKey, Index, JSON, UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship as orm_relationship


class Base(DeclarativeBase):
    pass


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Document(Base):
    """A user-provided source file (PDF, image, note, email, calendar, etc.)."""
    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    source_type = Column(String, nullable=False)  # pdf, png, txt, md, csv, json, eml, calendar
    file_hash = Column(String, nullable=False, unique=True)
    title = Column(Text)
    upload_time = Column(DateTime, default=utcnow)
    extraction_method = Column(String)
    original_location = Column(String)  # storage path
    metadata_json = Column(JSON)  # extra metadata (sender, subject, page count, etc.)
    page_count = Column(Integer)

    chunks = orm_relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
    facts = orm_relationship("Fact", back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    """A semantic/document-aware chunk of a document."""
    __tablename__ = "chunks"

    id = Column(String, primary_key=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    page = Column(Integer)
    section = Column(String)
    position = Column(Integer)
    text = Column(Text, nullable=False)
    metadata_json = Column(JSON)

    document = orm_relationship("Document", back_populates="chunks")


class Entity(Base):
    """A normalized person, organization, project, location, event, etc."""
    __tablename__ = "entities"

    id = Column(String, primary_key=True)
    canonical_name = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)  # PERSON, ORGANIZATION, PROJECT, LOCATION, EVENT, DATE, DOCUMENT, TOPIC, TASK
    aliases_json = Column(JSON, default=list)
    sources_json = Column(JSON, default=list)
    confidence = Column(Float, default=0.5)
    created_at = Column(DateTime, default=utcnow)

    __table_args__ = (
        Index("ix_entities_name_type", "canonical_name", "entity_type"),
    )


class Fact(Base):
    """A structured fact: SUBJECT PREDICATE OBJECT with full provenance."""
    __tablename__ = "facts"

    id = Column(String, primary_key=True)
    subject = Column(String, nullable=False)
    predicate = Column(String, nullable=False)
    object = Column(Text, nullable=False)
    source_id = Column(String, ForeignKey("documents.id"), nullable=False)
    source_location = Column(JSON)  # {page, char_start, char_end, snippet}
    observed_at = Column(DateTime)  # when the info was written/observed
    effective_at = Column(DateTime)  # when the info applies
    confidence = Column(Float, default=0.8)
    status = Column(String, default="likely_current")  # confirmed, likely_current, conflicting, outdated, unknown
    relationship = Column(String)  # e.g. works_on, owns, supersedes, etc.
    conflict_state = Column(String, default="none")  # none, conflicting, superseded, superseding
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow)

    document = orm_relationship("Document", back_populates="facts")

    __table_args__ = (
        Index("ix_facts_subject", "subject"),
        Index("ix_facts_predicate", "predicate"),
        Index("ix_facts_source", "source_id"),
        Index("ix_facts_observed", "observed_at"),
        Index("ix_facts_effective", "effective_at"),
    )


class Relationship(Base):
    """An edge between two entities with provenance."""
    __tablename__ = "relationships"

    id = Column(String, primary_key=True)
    subject_entity_id = Column(String, ForeignKey("entities.id"), nullable=False)
    predicate = Column(String, nullable=False)  # works_on, owns, attends, etc.
    object_entity_id = Column(String, ForeignKey("entities.id"), nullable=False)
    source_id = Column(String, ForeignKey("documents.id"), nullable=False)
    source_location = Column(JSON)
    observed_at = Column(DateTime)
    confidence = Column(Float, default=0.8)
    created_at = Column(DateTime, default=utcnow)


class Event(Base):
    """A temporal event with participants and context."""
    __tablename__ = "events"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime)
    location = Column(String)
    participants_json = Column(JSON, default=list)
    description = Column(Text)
    source_id = Column(String, ForeignKey("documents.id"), nullable=False)
    source_location = Column(JSON)
    observed_at = Column(DateTime)
    confidence = Column(Float, default=0.8)
    created_at = Column(DateTime, default=utcnow)


class Conflict(Base):
    """A detected conflict between two or more facts."""
    __tablename__ = "conflicts"

    id = Column(String, primary_key=True)
    fact_a_id = Column(String, ForeignKey("facts.id"), nullable=False)
    fact_b_id = Column(String, ForeignKey("facts.id"), nullable=False)
    field = Column(String, nullable=False)  # what field conflicts
    resolution = Column(String)  # likely_superseded, unresolved, resolved
    explanation = Column(Text)
    status = Column(String, default="unresolved")  # unresolved, acknowledged, resolved
    created_at = Column(DateTime, default=utcnow)


class Action(Base):
    """A proposed/executed autonomous action."""
    __tablename__ = "actions"

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)  # create_reminder, create_task, draft_email, generate_summary
    description = Column(Text, nullable=False)
    parameters_json = Column(JSON)
    status = Column(String, default="proposed")  # proposed, approved, executed, rejected, failed
    result_json = Column(JSON)
    user_approval = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
    executed_at = Column(DateTime)


class Trace(Base):
    """Lightweight internal tracing for every query."""
    __tablename__ = "traces"

    id = Column(String, primary_key=True)
    request_id = Column(String, nullable=False)
    query = Column(Text)
    retrieval_duration_ms = Column(Float)
    num_candidates = Column(Integer)
    selected_evidence_json = Column(JSON)
    model_used = Column(String)
    model_latency_ms = Column(Float)
    token_usage_json = Column(JSON)
    final_status = Column(String)
    created_at = Column(DateTime, default=utcnow)
# MEMORA Architecture

## System Overview

MEMORA is a personal AI memory system that transforms scattered information into connected, searchable memory with evidence-backed answers.

```
USER QUESTION
    ↓
QUERY UNDERSTANDING
    ↓
RETRIEVAL (TF-IDF + Metadata)
    ↓
STRUCTURED LOOKUP
    ↓
TEMPORAL ANALYSIS
    ↓
CONFLICT CHECK
    ↓
EVIDENCE SELECTION
    ↓
LLM REASONING
    ↓
VALIDATION
    ↓
ANSWER + SOURCES
```

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: SQLite (local) / PostgreSQL (production)
- **Vector Search**: TF-IDF via scikit-learn
- **LLM Router**: Hermes proxy at :31416
- **Document Parsing**: pdfplumber, python-docx, email

### Frontend
- **Framework**: Next.js 16 + React 19
- **Styling**: Tailwind CSS v4
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Font**: Plus Jakarta Sans

## Core Components

### 1. Ingestion Pipeline
```
FILE → TYPE DETECTION → PARSING → NORMALIZATION → CHUNKING → EXTRACTION → INDEXING
```

**Supported Formats:**
- PDF (.pdf)
- Images (.png, .jpg, .jpeg)
- Text (.txt, .md)
- Emails (.eml)
- Calendars (.ics)
- Structured data (.csv, .json)

### 2. Memory Model

Every fact is represented as:
```json
{
  "subject": "Project Atlas",
  "predicate": "has_demo_date",
  "object": "2026-09-26",
  "source_id": "doc_018",
  "source_location": {"page": 2, "char_start": 410, "char_end": 475},
  "observed_at": "2026-09-22",
  "confidence": 0.92,
  "status": "likely_current"
}
```

### 3. Retrieval Engine

**Hybrid Search Strategy:**
1. **Semantic Retrieval**: TF-IDF vector search
2. **Metadata Filtering**: source_type, entity, date range
3. **Temporal Filtering**: Time-based queries
4. **Exact Matching**: Entity and fact lookup
5. **Relationship Lookup**: Graph traversal
6. **Reranking**: LLM-based relevance scoring

### 4. Conflict Engine

**Conflict Detection:**
- Same subject + predicate + different objects
- Temporal contradictions
- Source credibility assessment

**Resolution Strategies:**
- Recency bias (newer wins)
- Source trust ranking
- Explicit supersession relationships
- User acknowledgment

### 5. Entity System

**Entity Types:**
- PERSON (with aliases)
- ORGANIZATION
- PROJECT
- LOCATION
- EVENT
- DATE/TIME
- DOCUMENT
- TOPIC

**Entity Resolution:**
- Alias normalization
- Confidence-based merging
- Provenance tracking

## Database Schema

```sql
documents (
  id, filename, source_type, file_hash, title,
  upload_time, extraction_method, page_count, metadata_json
)

chunks (
  id, document_id, page, section, position,
  text, metadata_json, embedding_id
)

entities (
  id, canonical_name, entity_type, aliases_json,
  sources_json, confidence, created_at
)

facts (
  id, subject, predicate, object, source_id,
  source_location_json, observed_at, confidence, status
)

relationships (
  id, subject_entity_id, predicate, object_entity_id,
  source_id, source_location_json, observed_at, confidence
)

events (
  id, title, start_at, end_at, location,
  participants_json, description, source_id,
  source_location_json, observed_at, confidence
)

conflicts (
  id, fact_a_id, fact_b_id, field, resolution,
  explanation, status, created_at
)

actions (
  id, type, description, parameters_json,
  status, created_at, approved_at, executed_at
)
```

## API Design

### RESTful Endpoints
- `POST /api/v1/ingest/file` - Upload document
- `POST /api/v1/ingest/text` - Ingest text
- `GET /api/v1/memory/` - Memory statistics
- `GET /api/v1/memory/entities` - List entities
- `GET /api/v1/memory/facts` - List facts
- `GET /api/v1/timeline/` - Get timeline events
- `GET /api/v1/conflicts/` - List conflicts
- `POST /api/v1/conflicts/detect` - Detect new conflicts
- `GET /api/v1/sources/` - List sources
- `POST /api/v1/query/` - Ask question
- `GET /api/v1/actions/` - List actions
- `POST /api/v1/actions/propose` - Propose action
- `POST /api/v1/actions/{id}/approve` - Approve action
- `POST /api/v1/actions/{id}/execute` - Execute action

### Response Format
```json
{
  "answer": "...",
  "status": "likely_current",
  "confidence": 0.91,
  "sources": [...],
  "conflicts": [...],
  "related_entities": [...],
  "timeline_events": [...],
  "suggested_actions": [...]
}
```

## Security Model

### Input Validation
- File type whitelisting
- Path traversal prevention
- Size limits (50MB max)
- Malware scanning

### Data Protection
- No PII in logs
- Encrypted storage (optional)
- Multi-tenant isolation
- Rate limiting

### API Security
- JWT authentication (future)
- CORS configuration
- Request validation
- Error sanitization

## Performance Optimization

### Caching Strategy
- Query result caching (TTL: 5min)
- Entity lookup caching
- Conflict detection caching

### Resource Management
- Streaming document processing
- Lazy loading of chunks
- Background indexing

### Memory Constraints (8GB RAM)
- No local embeddings model
- TF-IDF instead of vector DB
- SQLite instead of Postgres (local)
- Async processing

## Extensibility

### Adding New Parsers
1. Create parser in `backend/parsers/`
2. Register in `PARSER_REGISTRY`
3. Add MIME type mapping
4. Update allowed_extensions

### Adding New Entity Types
1. Add to Entity enum
2. Update extraction logic
3. Add UI components
4. Update tests

### Custom Actions
1. Define action schema
2. Implement executor
3. Add approval workflow
4. Update frontend

## Development Workflow

```bash
# 1. Start backend
cd backend && python -m uvicorn app:app --reload

# 2. Start frontend
cd frontend && npm run dev

# 3. Run tests
pytest tests/ -v

# 4. Load demo data
curl -X POST http://127.0.0.1:8000/api/v1/demo/reset
```

## Future Roadmap

### Phase 1 (Current)
- [x] Basic ingestion pipeline
- [x] TF-IDF retrieval
- [x] Conflict detection
- [x] Frontend UI
- [x] Demo dataset

### Phase 2
- [ ] Vector embeddings (API-based)
- [ ] PostgreSQL migration
- [ ] Real-time sync
- [ ] Mobile app

### Phase 3
- [ ] Multi-user support
- [ ] Collaborative memory
- [ ] Advanced NLP
- [ ] Integration ecosystem

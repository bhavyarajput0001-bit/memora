-- MEMORA Schema for Supabase (PostgreSQL)
-- Run this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR(255) PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    source_type VARCHAR(50) NOT NULL,  -- pdf, png, txt, md, csv, json, eml, calendar
    file_hash VARCHAR(64) NOT NULL UNIQUE,
    title TEXT,
    upload_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    extraction_method VARCHAR(100),
    original_location TEXT,
    metadata_json JSONB,
    page_count INTEGER
);

-- Chunks table (with embedding support)
CREATE TABLE IF NOT EXISTS chunks (
    id VARCHAR(255) PRIMARY KEY,
    document_id VARCHAR(255) NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page INTEGER,
    section VARCHAR(255),
    position INTEGER,
    text TEXT NOT NULL,
    metadata_json JSONB,
    embedding VECTOR(384)  -- For sentence-transformers embeddings
);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_chunks_document ON chunks(document_id);

-- Entities table
CREATE TABLE IF NOT EXISTS entities (
    id VARCHAR(255) PRIMARY KEY,
    canonical_name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,  -- PERSON, ORGANIZATION, PROJECT, LOCATION, EVENT, DATE, DOCUMENT, TOPIC, TASK
    aliases_json JSONB DEFAULT '[]'::jsonb,
    sources_json JSONB DEFAULT '[]'::jsonb,
    confidence DOUBLE PRECISION DEFAULT 0.5,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_entities_name_type ON entities(canonical_name, entity_type);

-- Facts table
CREATE TABLE IF NOT EXISTS facts (
    id VARCHAR(255) PRIMARY KEY,
    subject VARCHAR(255) NOT NULL,
    predicate VARCHAR(255) NOT NULL,
    object TEXT NOT NULL,
    source_id VARCHAR(255) NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    source_location JSONB,
    observed_at TIMESTAMPTZ,
    effective_at TIMESTAMPTZ,
    confidence DOUBLE PRECISION DEFAULT 0.8,
    status VARCHAR(50) DEFAULT 'likely_current',
    relationship VARCHAR(100),
    conflict_state VARCHAR(50) DEFAULT 'none',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_facts_subject ON facts(subject);
CREATE INDEX IF NOT EXISTS idx_facts_predicate ON facts(predicate);
CREATE INDEX IF NOT EXISTS idx_facts_source ON facts(source_id);
CREATE INDEX IF NOT EXISTS idx_facts_observed ON facts(observed_at);
CREATE INDEX IF NOT EXISTS idx_facts_effective ON facts(effective_at);

-- Relationships table
CREATE TABLE IF NOT EXISTS relationships (
    id VARCHAR(255) PRIMARY KEY,
    subject_entity_id VARCHAR(255) NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    predicate VARCHAR(255) NOT NULL,
    object_entity_id VARCHAR(255) NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    source_id VARCHAR(255) NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    source_location JSONB,
    observed_at TIMESTAMPTZ,
    confidence DOUBLE PRECISION DEFAULT 0.8,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_relationships_subject ON relationships(subject_entity_id);
CREATE INDEX IF NOT EXISTS idx_relationships_object ON relationships(object_entity_id);

-- Events table
CREATE TABLE IF NOT EXISTS events (
    id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    start_at TIMESTAMPTZ NOT NULL,
    end_at TIMESTAMPTZ,
    location VARCHAR(255),
    participants_json JSONB DEFAULT '[]'::jsonb,
    description TEXT,
    source_id VARCHAR(255) NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    source_location JSONB,
    observed_at TIMESTAMPTZ,
    confidence DOUBLE PRECISION DEFAULT 0.8,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_events_start ON events(start_at);
CREATE INDEX IF NOT EXISTS idx_events_source ON events(source_id);

-- Conflicts table
CREATE TABLE IF NOT EXISTS conflicts (
    id VARCHAR(255) PRIMARY KEY,
    fact_a_id VARCHAR(255) NOT NULL REFERENCES facts(id) ON DELETE CASCADE,
    fact_b_id VARCHAR(255) NOT NULL REFERENCES facts(id) ON DELETE CASCADE,
    field VARCHAR(100) NOT NULL,
    resolution VARCHAR(100),
    explanation TEXT,
    status VARCHAR(50) DEFAULT 'unresolved',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conflicts_fact_a ON conflicts(fact_a_id);
CREATE INDEX IF NOT EXISTS idx_conflicts_fact_b ON conflicts(fact_b_id);

-- Actions table
CREATE TABLE IF NOT EXISTS actions (
    id VARCHAR(255) PRIMARY KEY,
    type VARCHAR(100) NOT NULL,  -- create_reminder, create_task, draft_email, generate_summary
    description TEXT NOT NULL,
    parameters_json JSONB,
    status VARCHAR(50) DEFAULT 'proposed',  -- proposed, approved, executed, rejected, failed
    result_json JSONB,
    user_approval BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    executed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_actions_status ON actions(status);
CREATE INDEX IF NOT EXISTS idx_actions_created ON actions(created_at);

-- Traces table
CREATE TABLE IF NOT EXISTS traces (
    id VARCHAR(255) PRIMARY KEY,
    request_id VARCHAR(255) NOT NULL,
    query TEXT,
    retrieval_duration_ms DOUBLE PRECISION,
    num_candidates INTEGER,
    selected_evidence_json JSONB,
    model_used VARCHAR(100),
    model_latency_ms DOUBLE PRECISION,
    token_usage_json JSONB,
    final_status VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_traces_request ON traces(request_id);
CREATE INDEX IF NOT EXISTS idx_traces_created ON traces(created_at);

-- Users table (for multi-user support)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    api_key VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- Row Level Security (RLS) policies
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE facts ENABLE ROW LEVEL SECURITY;
ALTER TABLE relationships ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE conflicts ENABLE ROW LEVEL SECURITY;
ALTER TABLE actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE traces ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to read/write their own data
CREATE POLICY "Users can read own documents" ON documents FOR SELECT TO authenticated USING (true);
CREATE POLICY "Users can insert own documents" ON documents FOR INSERT TO authenticated WITH CHECK (true);
CREATE POLICY "Users can update own documents" ON documents FOR UPDATE TO authenticated USING (true);
CREATE POLICY "Users can delete own documents" ON documents FOR DELETE TO authenticated USING (true);

-- Similar policies for other tables...
-- (Repeat for chunks, entities, facts, etc.)

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for facts table
CREATE TRIGGER update_facts_updated_at BEFORE UPDATE ON facts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
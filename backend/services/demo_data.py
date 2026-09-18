"""MEMORA demo data — realistic fictional dataset for the Atlas project."""
import asyncio
from datetime import datetime, timezone, timedelta
import uuid

from backend.db import get_session
from backend.models import Document, Chunk, Entity, Fact, Relationship, Event
from backend.utils import utcnow, generate_id


def generate_demo_data() -> dict:
    """Generate the Atlas project demo dataset."""
    now = utcnow()
    
    # Dates for the demo story
    sep_18 = now - timedelta(days=0)
    sep_20 = now - timedelta(days=2)
    sep_22 = now - timedelta(days=4)
    sep_23 = now - timedelta(days=5)
    sep_24 = now - timedelta(days=6)
    sep_25 = now - timedelta(days=7)
    sep_26 = now - timedelta(days=8)
    
    doc_ids = {}
    entity_ids = {}
    fact_ids = {}
    
    # ==========================================
    # DOCUMENT 1: Project Notes PDF
    # ==========================================
    doc1_id = generate_id("doc_")
    doc1_text = """PROJECT ATLAS — INITIAL NOTES
Date: September 20, 2026
Author: Aditi Sharma

PROJECT OVERVIEW
Project Atlas is a cross-functional initiative to deliver a new analytics platform by end of quarter.

TEAM ASSIGNMENTS
- Backend Development: Rahul Verma
- Frontend Development: Priya Patel
- QA Lead: Karan Mehta
- Product Owner: Neha Gupta

INITIAL DEADLINE
The project demo is scheduled for September 24, 2026.
All deliverables must be completed by September 23.

RISK FACTORS
- Backend API integration is still in progress
- Third-party vendor delay possible
- Team availability during holiday week

NEXT STEPS
1. Complete backend API by Sep 22
2. Begin integration testing Sep 23
3. Final review Sep 24 morning"""
    
    doc1 = Document(
        id=doc1_id,
        filename="project_notes_atlas.pdf",
        source_type="pdf",
        file_hash="demo_hash_doc1",
        title="Project Atlas Notes",
        upload_time=sep_20,
        extraction_method="pypdf",
        page_count=1,
        metadata_json={"author": "Aditi Sharma", "page_count": 1},
    )
    doc_ids["project_notes"] = doc1_id
    
    chunk1 = Chunk(
        id=generate_id("chk_"),
        document_id=doc1_id,
        page=1,
        section="INITIAL DEADLINE",
        position=0,
        text=doc1_text,
    )
    
    entity_rahul = Entity(
        id=generate_id("ent_"),
        canonical_name="Rahul Verma",
        entity_type="PERSON",
        aliases_json=["Rahul", "R. Verma"],
        sources_json=[doc1_id],
        confidence=0.95,
    )
    entity_ids["rahul"] = entity_rahul.id
    
    entity_priya = Entity(
        id=generate_id("ent_"),
        canonical_name="Priya Patel",
        entity_type="PERSON",
        aliases_json=["Priya"],
        sources_json=[doc1_id],
        confidence=0.95,
    )
    entity_ids["priya"] = entity_priya.id
    
    entity_karan = Entity(
        id=generate_id("ent_"),
        canonical_name="Karan Mehta",
        entity_type="PERSON",
        aliases_json=["Karan"],
        sources_json=[doc1_id],
        confidence=0.95,
    )
    entity_ids["karan"] = entity_karan.id
    
    entity_aditi = Entity(
        id=generate_id("ent_"),
        canonical_name="Aditi Sharma",
        entity_type="PERSON",
        aliases_json=["Aditi"],
        sources_json=[doc1_id],
        confidence=0.95,
    )
    entity_ids["aditi"] = entity_aditi.id
    
    entity_neha = Entity(
        id=generate_id("ent_"),
        canonical_name="Neha Gupta",
        entity_type="PERSON",
        aliases_json=["Neha"],
        sources_json=[doc1_id],
        confidence=0.95,
    )
    entity_ids["neha"] = entity_neha.id
    
    entity_atlas = Entity(
        id=generate_id("ent_"),
        canonical_name="Project Atlas",
        entity_type="PROJECT",
        aliases_json=["Atlas"],
        sources_json=[doc1_id],
        confidence=0.98,
    )
    entity_ids["atlas"] = entity_atlas.id
    
    fact_backend_rahul = Fact(
        id=generate_id("fact_"),
        subject="Rahul Verma",
        predicate="assigned_to",
        object="Backend Development",
        source_id=doc1_id,
        source_location={"page": 1, "char_start": 150, "char_end": 200},
        observed_at=sep_20,
        effective_at=sep_20,
        confidence=0.95,
        status="likely_current",
        relationship="works_on",
    )
    fact_ids["backend_rahul"] = fact_backend_rahul.id
    
    fact_deadline_24 = Fact(
        id=generate_id("fact_"),
        subject="Project Atlas",
        predicate="has_demo_date",
        object="2026-09-24",
        source_id=doc1_id,
        source_location={"page": 1, "char_start": 280, "char_end": 310},
        observed_at=sep_20,
        effective_at=datetime(2026, 9, 24, tzinfo=timezone.utc),
        confidence=0.92,
        status="likely_current",
    )
    fact_ids["deadline_24"] = fact_deadline_24.id
    
    fact_team_rahul = Fact(
        id=generate_id("fact_"),
        subject="Project Atlas",
        predicate="has_member",
        object="Rahul Verma",
        source_id=doc1_id,
        observed_at=sep_20,
        effective_at=sep_20,
        confidence=0.95,
    )
    
    fact_team_priya = Fact(
        id=generate_id("fact_"),
        subject="Project Atlas",
        predicate="has_member",
        object="Priya Patel",
        source_id=doc1_id,
        observed_at=sep_20,
        effective_at=sep_20,
        confidence=0.95,
    )
    
    fact_team_karan = Fact(
        id=generate_id("fact_"),
        subject="Project Atlas",
        predicate="has_member",
        object="Karan Mehta",
        source_id=doc1_id,
        observed_at=sep_20,
        effective_at=sep_20,
        confidence=0.95,
    )
    
    # ==========================================
    # DOCUMENT 2: Rahul's Email
    # ==========================================
    doc2_id = generate_id("doc_")
    doc2_text = """From: rahul.verma@company.com
To: team@company.com
Subject: Re: Project Atlas Timeline Update
Date: September 22, 2026

Hi team,

Following up on yesterday's discussion, I wanted to confirm that 
the backend API integration has hit an unexpected blocker with 
the third-party vendor. Their delivery is now expected by Sep 23 
evening instead of Sep 22.

Given this, I recommend we move the demo date to September 26, 
2026. This gives us:
- Sep 23-24: Integration and testing
- Sep 25: Final review and preparation
- Sep 26: Demo day

Please confirm if this works for everyone.

Thanks,
Rahul"""
    
    doc2 = Document(
        id=doc2_id,
        filename="rahul_email_atlas_update.eml",
        source_type="eml",
        file_hash="demo_hash_doc2",
        title="Re: Project Atlas Timeline Update",
        upload_time=sep_22,
        extraction_method="email-parser",
        page_count=1,
        metadata_json={
            "sender": "rahul.verma@company.com",
            "recipient": "team@company.com",
            "subject": "Re: Project Atlas Timeline Update",
            "date": "September 22, 2026",
        },
    )
    doc_ids["rahul_email"] = doc2_id
    
    fact_new_deadline = Fact(
        id=generate_id("fact_"),
        subject="Project Atlas",
        predicate="has_demo_date",
        object="2026-09-26",
        source_id=doc2_id,
        source_location={"page": 1, "char_start": 250, "char_end": 280},
        observed_at=sep_22,
        effective_at=datetime(2026, 9, 26, tzinfo=timezone.utc),
        confidence=0.97,
        status="likely_current",
        relationship="supersedes",
    )
    fact_ids["deadline_26"] = fact_new_deadline.id
    
    fact_vendor_delay = Fact(
        id=generate_id("fact_"),
        subject="Project Atlas",
        predicate="has_blocker",
        object="Third-party vendor delay",
        source_id=doc2_id,
        observed_at=sep_22,
        effective_at=sep_22,
        confidence=0.94,
        status="likely_current",
    )
    
    # ==========================================
    # DOCUMENT 3: Meeting Notes
    # ==========================================
    doc3_id = generate_id("doc_")
    doc3_text = """MEETING NOTES — Project Atlas Sync
Date: September 22, 2026, 2:00 PM
Attendees: Rahul Verma, Priya Patel, Karan Mehta, Aditi Sharma

AGENDA:
1. Backend progress update (Rahul)
2. Frontend status (Priya)
3. QA planning (Karan)
4. Timeline adjustment discussion

KEY DECISIONS:
- Demo moved from Sep 24 to Sep 26 (approved by all)
- Presentation prep assigned to Priya for Sep 25
- Karan to begin smoke testing Sep 24

ACTION ITEMS:
- Rahul: Complete API integration by EOD Sep 23
- Priya: Finalize frontend by Sep 24
- Karan: Begin QA on Sep 24
- Aditi: Schedule final review Sep 25"""
    
    doc3 = Document(
        id=doc3_id,
        filename="meeting_notes_sep22.md",
        source_type="md",
        file_hash="demo_hash_doc3",
        title="Project Atlas Sync Meeting",
        upload_time=sep_22,
        extraction_method="utf-8-decode",
        page_count=1,
    )
    doc_ids["meeting_notes"] = doc3_id
    
    event_meeting = Event(
        id=generate_id("evt_"),
        title="Project Atlas Sync Meeting",
        start_at=datetime(2026, 9, 22, 14, 0, tzinfo=timezone.utc),
        end_at=datetime(2026, 9, 22, 15, 0, tzinfo=timezone.utc),
        participants_json=["Rahul Verma", "Priya Patel", "Karan Mehta", "Aditi Sharma"],
        description="Weekly sync to discuss timeline changes",
        source_id=doc3_id,
        observed_at=sep_22,
        confidence=0.95,
    )
    
    # ==========================================
    # DOCUMENT 4: Team Email
    # ==========================================
    doc4_id = generate_id("doc_")
    doc4_text = """From: neha.gupta@company.com
To: atlas-team@company.com
Subject: Project Atlas - Presentation Prep
Date: September 23, 2026

Hi team,

Quick reminder that we have the demo on Sep 26. 
Priya, could you prepare the presentation deck by end of day 
Sep 25? We need:
- Executive summary
- Technical architecture overview
- Demo flow
- Q&A preparation

Let me know if you need any support.

Best,
Neha"""
    
    doc4 = Document(
        id=doc4_id,
        filename="neha_email_presentation.eml",
        source_type="eml",
        file_hash="demo_hash_doc4",
        title="Project Atlas - Presentation Prep",
        upload_time=sep_23,
        extraction_method="email-parser",
        page_count=1,
        metadata_json={
            "sender": "neha.gupta@company.com",
            "subject": "Project Atlas - Presentation Prep",
            "date": "September 23, 2026",
        },
    )
    doc_ids["neha_email"] = doc4_id
    
    fact_presentation_priya = Fact(
        id=generate_id("fact_"),
        subject="Project Atlas",
        predicate="has_presenter",
        object="Priya Patel",
        source_id=doc4_id,
        observed_at=sep_23,
        effective_at=sep_25,
        confidence=0.90,
    )
    
    # ==========================================
    # DOCUMENT 5: Calendar Entry
    # ==========================================
    doc5_id = generate_id("doc_")
    doc5_text = """Calendar Event: Project Atlas Demo
Start: September 26, 2026, 10:00 AM IST
End: September 26, 2026, 11:30 AM IST
Location: Conference Room B / Virtual
Attendees: Stakeholders, Leadership Team
Description: Final demo of Project Atlas analytics platform"""
    
    doc5 = Document(
        id=doc5_id,
        filename="calendar_atlas_demo.ics",
        source_type="txt",
        file_hash="demo_hash_doc5",
        title="Project Atlas Demo",
        upload_time=sep_26,
        extraction_method="utf-8-decode",
        page_count=1,
    )
    doc_ids["calendar"] = doc5_id
    
    event_demo = Event(
        id=generate_id("evt_"),
        title="Project Atlas Demo",
        start_at=datetime(2026, 9, 26, 4, 30, tzinfo=timezone.utc),  # 10 AM IST = 4:30 UTC
        end_at=datetime(2026, 9, 26, 6, 0, tzinfo=timezone.utc),
        location="Conference Room B",
        participants_json=["Stakeholders", "Leadership Team"],
        description="Final demo of Project Atlas analytics platform",
        source_id=doc5_id,
        observed_at=sep_26,
        confidence=0.99,
    )
    
    return {
        "documents": [doc1, doc2, doc3, doc4, doc5],
        "chunks": [chunk1],
        "entities": [entity_rahul, entity_priya, entity_karan, entity_aditi, entity_neha, entity_atlas],
        "facts": [
            fact_backend_rahul,
            fact_deadline_24,
            fact_team_rahul,
            fact_team_priya,
            fact_team_karan,
            fact_new_deadline,
            fact_vendor_delay,
            fact_presentation_priya,
        ],
        "events": [event_meeting, event_demo],
        "relationships": [],
    }


async def seed_demo_data():
    """Seed the database with demo data."""
    from backend.db import engine
    from backend.models import Base
    
    # Initialize DB if not already done
    Base.metadata.create_all(bind=engine)
    
    with get_session() as db:
        # Check if data already exists
        if db.query(Document).count() > 0:
            print("Demo data already exists, skipping seed")
            return
        
        print("Seeding demo data...")
        data = generate_demo_data()
        
        # Add documents
        for doc in data["documents"]:
            db.add(doc)
        db.flush()
        
        # Add chunks
        for chunk in data["chunks"]:
            db.add(chunk)
        
        # Add entities
        for ent in data["entities"]:
            db.add(ent)
        
        # Add facts
        for fact in data["facts"]:
            db.add(fact)
        
        # Add events
        for evt in data["events"]:
            db.add(evt)
        
        db.commit()
        print(f"Demo data seeded: {len(data['documents'])} docs, {len(data['entities'])} entities, {len(data['facts'])} facts, {len(data['events'])} events")

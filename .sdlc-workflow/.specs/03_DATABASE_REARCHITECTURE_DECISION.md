# Database Re-Architecture Decision — User Story

**Status:** ✅ DECIDED - Option C (PostgreSQL + pgvector)
**Created:** 2025-11-06
**Decided:** 2025-11-06
**Priority:** HIGH (Blocks property implementation)

---

## Executive Summary

**Situation:** Architecture specs specify MongoDB + Qdrant, but current implementation uses PostgreSQL + pgvector. With minimal property code implemented, this is the optimal decision point for database architecture.

**Decision Required:** Choose between:
1. **Option A:** Switch to MongoDB Atlas + separate vector DB (Qdrant/Pinecone)
2. **Option B:** Hybrid approach - Keep Postgres for vectors/roles/stable data + MongoDB for properties/dynamic data
3. **Option C:** Stay with PostgreSQL + pgvector for everything

**Recommendation:** See [Final Recommendation](#final-recommendation) section

---

## Current State Analysis

### What's Specified (Architecture Docs)

**Reference:** `.sdlc-workflow/.specs/01_ARCHITECTURE.md`

- **Primary DB:** MongoDB (self-hosted dev, Atlas production)
  - Reason: Flexible schema for polymorphic entities (rental, sale, business, investment properties)
- **Vector DB:** Qdrant (self-hosted in Docker)
  - Reason: Lightweight, easy VPS deployment, semantic search
- **Cache:** Redis (sessions, locks, pub/sub)
- **Target:** 4GB VPS footprint
- **Goal:** Fast iteration, modular monolith → microservices path

**Reference:** `.sdlc-workflow/.specs/02_PROPERTIES_SCHEMA.md`

MongoDB collections designed:
- `properties` (base)
- `rental_details`, `sale_details`, `business_details`, `investment_details`
- `availability` (booking calendar)
- `leads`, `agents`, `companies`, `media`

### What's Implemented (Current Codebase)

**Database Setup:**
- PostgreSQL 16 with pgvector extension
- Docker container: `bestays-db-dev` on port 5433
- Connection: `postgresql+asyncpg://bestays_user:bestays_password@postgres:5432/bestays_dev`

**Existing Models:** (`.../apps/server/src/server/models/`)
- ✅ `User` - Clerk auth sync, role-based access (admin/agent/user)
- ✅ `WebhookEvent` - Event tracking
- ✅ `FAQDocument`, `FAQCategory`, `FAQEmbedding`, `FAQAnalytic`, `FAQRelated` - Full FAQ RAG system
- ✅ `ChatPrompt`, `ChatTool`, `ChatPromptHistory` - LLM chat configuration
- ❌ **NO property models yet** (critical gap)

**Vector Infrastructure:** (`docker/postgres/init-pgvector.sql`)

Comprehensive pgvector setup with:
- `content_embeddings` table - for properties (1536-dim vectors)
- `faq_embeddings` table - FAQ semantic search
- `search_history_embeddings` table - query analytics
- `conversation_embeddings` table - chat context
- PostgreSQL functions: `search_similar_content()`, `search_similar_faqs()`
- IVFFlat indexes optimized for ~100k vectors

**Technology Stack:**
- FastAPI + SQLAlchemy 2.0 (async)
- Redis for caching
- Clerk for authentication
- OpenRouter for LLM

### Gap Analysis

| Aspect | Spec Says | Implementation Has | Status |
|--------|-----------|-------------------|--------|
| Primary DB | MongoDB | PostgreSQL | ⚠️ Mismatch |
| Vector DB | Qdrant | pgvector (integrated) | ⚠️ Mismatch |
| Property Models | MongoDB collections | None | ❌ Not implemented |
| User/Auth | Not detailed | PostgreSQL User model | ✅ Working |
| FAQ System | MongoDB | PostgreSQL FAQ models | ✅ Working |
| Chat System | Not detailed | PostgreSQL Chat models | ✅ Working |
| Migrations | Not detailed | None (using create_all) | ⚠️ Missing |

**Key Insight:** Since properties aren't implemented yet, this is the perfect time to decide architecture without painful migrations.

---

## Architecture Options Evaluation

### Option A: MongoDB + Separate Vector DB (Per Original Spec)

**Implementation:**
- MongoDB Atlas (production) / Self-hosted (dev) for all data
- Qdrant or Pinecone for all vector embeddings
- Redis for cache/sessions
- Migrate existing User/FAQ/Chat models to MongoDB

**Technology Changes:**
```yaml
From:
  - PostgreSQL 16 + pgvector
  - SQLAlchemy ORM
To:
  - MongoDB Atlas 7.x
  - Motor (async MongoDB driver) or Beanie ODM
  - Qdrant/Pinecone client SDK
```

**Pros:**
- ✅ **Schema flexibility** for polymorphic properties (rental vs sale vs business)
- ✅ **Document-oriented** matches real estate entity complexity naturally
- ✅ **Horizontal scaling** easier with MongoDB sharding
- ✅ **Faster iteration** - no schema migrations, add fields freely
- ✅ **Atlas features** - automated backups, point-in-time recovery, global clusters
- ✅ **Separate vector DB** - specialized performance, can swap providers easily
- ✅ **Better alignment** with spec for future team/contractor onboarding

**Cons:**
- ❌ **More moving parts** - 3 data stores (Mongo + Vector + Redis) vs 2
- ❌ **Data consistency** - no ACID across MongoDB + vector DB (eventual consistency)
- ❌ **Rewrite effort** - Migrate existing User/FAQ/Chat from Postgres models
- ❌ **Cost** - MongoDB Atlas pricing ($0.08/hr for M10 = ~$60/month minimum)
- ❌ **Learning curve** - Team needs MongoDB + Qdrant experience
- ❌ **Vector DB management** - Qdrant adds operational overhead (backups, monitoring)
- ❌ **No relational integrity** - Must handle foreign keys in application code

**VPS Footprint (4GB target):**
```
MongoDB (self-hosted):     ~800MB
Qdrant:                    ~400MB
Redis:                     ~200MB
FastAPI:                   ~300MB
SvelteKit:                 ~300MB
-------------------------
Total:                     ~2.0GB (within budget)
```

**Best For:**
- Teams prioritizing flexibility and scale
- Properties with highly varied schemas
- Microservices-first architecture
- Budget allows MongoDB Atlas ($720+/year)

---

### Option B: Hybrid PostgreSQL + MongoDB

**Implementation:**
- **PostgreSQL** for:
  - User accounts (Clerk sync)
  - Roles & permissions (relational integrity critical)
  - Vector embeddings (pgvector for ALL content)
  - Chat history (transactional consistency)
  - Analytics (SQL aggregations)

- **MongoDB** for:
  - Properties (all types - rental, sale, business, investment)
  - Availability calendars (frequent updates, flexible structure)
  - FAQs (if migrated - though currently in Postgres)
  - Media metadata (flexible attributes)
  - Leads & inquiries (varying data structures)

**Sync Strategy:**
```python
# Property document references User in Postgres
{
  "_id": ObjectId("..."),
  "title": "Luxury Villa",
  "type": "rental",
  "owner_user_id": 123,  # References postgres.users.id
  "agent_clerk_id": "user_xxx",  # References postgres.users.clerk_user_id
  # ... flexible property data
}
```

**Pros:**
- ✅ **Best of both worlds** - Relational for critical data, flexible for properties
- ✅ **Gradual migration** - Keep working User/FAQ in Postgres, only properties to Mongo
- ✅ **Unified vector search** - pgvector handles all embeddings (properties + FAQs + chat)
- ✅ **Cost effective** - Self-host MongoDB in dev, smaller Atlas tier for production
- ✅ **Property flexibility** - Easy schema evolution without Postgres migrations
- ✅ **Proven stack** - Many companies run Postgres + MongoDB successfully
- ✅ **Incremental adoption** - Start with properties in Mongo, evaluate later

**Cons:**
- ❌ **Complexity** - Dual database architecture increases operational burden
- ❌ **Data synchronization** - Must keep property references to users in sync
- ❌ **Transaction boundaries** - Can't use DB transactions across Postgres + MongoDB
- ❌ **Two query languages** - SQL + MongoDB aggregation pipeline
- ❌ **Backup strategy** - Must coordinate backups across two databases
- ❌ **More dependencies** - Both psycopg2/asyncpg AND motor/pymongo
- ❌ **Split embeddings?** - Confusing to have vectors in Postgres but properties in Mongo

**VPS Footprint:**
```
PostgreSQL:                ~600MB (users, vectors, chat)
MongoDB:                   ~600MB (properties, availability)
Redis:                     ~200MB
FastAPI:                   ~300MB
SvelteKit:                 ~300MB
-------------------------
Total:                     ~2.0GB (within budget, but tight)
```

**Best For:**
- Teams wanting flexibility for properties specifically
- Preserving investment in Postgres infrastructure
- Organizations with existing MongoDB expertise
- Gradual transition strategy

---

### Option C: Full PostgreSQL + pgvector (Current Direction)

**Implementation:**
- PostgreSQL for ALL data (users, properties, FAQs, chat, analytics)
- pgvector for ALL embeddings (already configured)
- JSONB columns for flexible property attributes
- SQLAlchemy models for type safety
- Alembic for schema migrations

**Property Schema (PostgreSQL approach):**
```sql
-- Base property table
CREATE TABLE properties (
    id UUID PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('rental', 'sale', 'lease', 'business', 'investment')),
    status VARCHAR(20) DEFAULT 'draft',

    -- Location
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    location_address TEXT,
    location_city VARCHAR(100),
    location_country VARCHAR(100),

    -- References
    company_id UUID REFERENCES companies(id),
    agent_id UUID REFERENCES users(id),

    -- Flexible attributes (JSON)
    attributes JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Type-specific details (polymorphic approach)
CREATE TABLE rental_details (
    id UUID PRIMARY KEY,
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    price_per_night DECIMAL(10, 2),
    price_per_month DECIMAL(10, 2),
    amenities JSONB DEFAULT '[]',
    booking_policy TEXT,
    -- ... rental-specific fields
);

CREATE TABLE sale_details (
    id UUID PRIMARY KEY,
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    price DECIMAL(15, 2),
    ownership_type VARCHAR(50),
    land_size DECIMAL(10, 2),
    -- ... sale-specific fields
);
```

**Pros:**
- ✅ **Simplicity** - Single database, one query language, one backup strategy
- ✅ **ACID transactions** - Guaranteed consistency across users/properties/bookings
- ✅ **Referential integrity** - Foreign keys enforced at DB level (agent_id → users)
- ✅ **No rewrite needed** - Keep existing User/FAQ/Chat models as-is
- ✅ **Mature tooling** - SQLAlchemy, Alembic, pgAdmin, extensive monitoring
- ✅ **Unified vector search** - All embeddings in one place (already configured!)
- ✅ **JSONB flexibility** - Postgres JSONB nearly as flexible as MongoDB for property attributes
- ✅ **Lower operational cost** - One database to manage, backup, monitor
- ✅ **Full-text search** - Built-in pg_trgm extension (already enabled)
- ✅ **PostGIS option** - Can add geospatial queries later if needed

**Cons:**
- ❌ **Schema migrations** - Adding property fields requires Alembic migrations
- ❌ **Less flexible** - JSONB is powerful but not as native as MongoDB documents
- ❌ **Vertical scaling** - Postgres scales up (bigger server) vs MongoDB scales out (sharding)
- ❌ **ORM overhead** - SQLAlchemy models more verbose than MongoDB documents
- ❌ **Diverges from spec** - Team/contractors expect MongoDB per original architecture doc
- ❌ **Polymorphism complexity** - Handling rental/sale/business types in relational model trickier
- ❌ **Vector scaling limits** - pgvector IVFFlat works to ~1M vectors, then needs tuning

**VPS Footprint:**
```
PostgreSQL:                ~800MB (all data + vectors)
Redis:                     ~200MB
FastAPI:                   ~300MB
SvelteKit:                 ~300MB
-------------------------
Total:                     ~1.6GB (best for 4GB target)
```

**Best For:**
- Teams prioritizing stability and ACID guarantees
- Small to medium scale (< 1M properties)
- Organizations with deep PostgreSQL expertise
- Budget-conscious deployments (lowest hosting cost)
- Preference for type-safe ORM patterns

---

## Decision Matrix

| Criteria | MongoDB + Qdrant (A) | Hybrid (B) | PostgreSQL Only (C) |
|----------|---------------------|------------|---------------------|
| **Schema Flexibility** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Operational Simplicity** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Data Consistency** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Development Speed** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Horizontal Scalability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Cost (Dev + Prod)** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Vector Search Performance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Learning Curve** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Alignment with Spec** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Migration Effort** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **VPS Footprint (4GB)** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Type Safety** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **TOTAL SCORE** | **44/60** | **42/60** | **50/60** |

---

## Final Recommendation

### Primary Recommendation: **Option C - Full PostgreSQL + pgvector**

**Rationale:**

1. **Current Investment:** You already have a sophisticated PostgreSQL + pgvector setup with vector search functions, indexes, and working models. Throwing this away means wasted effort.

2. **ACID for Bookings:** Real estate bookings require transactional integrity. Double-booking prevention, payment → availability updates MUST be atomic. Postgres transactions guarantee this; MongoDB + Qdrant requires complex distributed saga patterns.

3. **4GB VPS Reality:** You specifically called out 4GB footprint. Adding MongoDB + Qdrant increases memory pressure and operational complexity. Postgres-only gives the most headroom.

4. **JSONB is Powerful:** Modern PostgreSQL JSONB handles 90% of MongoDB use cases. For property `attributes`, `amenities`, `metadata` - JSONB is perfect. You get flexibility + relational constraints.

5. **Team Velocity:** Staying with Postgres means:
   - No rewrite of User/FAQ/Chat models
   - No learning curve for Motor/Beanie/Qdrant
   - Alembic migrations are well-understood
   - Single backup/restore strategy

6. **Vector Search:** The pgvector setup is ALREADY production-ready with:
   - IVFFlat indexes
   - Stored procedures for semantic search
   - Analytics tracking
   - Sufficient for 100k-1M vectors (years of growth)

7. **Microservices Path:** You can still extract microservices later:
   - Property Service: Reads from Postgres replica
   - Booking Service: Writes to Postgres primary
   - Each service gets its own DB schema
   - Later migrate specific schemas to MongoDB if truly needed

**When to Reconsider:**
- Property count exceeds 500k (vector search becomes slow)
- Schema changes happen multiple times per week (migrations become burden)
- Need multi-region writes (Postgres replication complex, MongoDB Atlas shines)
- Raised significant funding (can afford MongoDB Atlas + Qdrant managed services)

---

### Alternative Recommendation: **Option A - MongoDB + Qdrant** (If spec alignment critical)

**When to Choose This:**

1. **Team Agreement:** Original spec said MongoDB for a reason. If team/stakeholders committed to that vision, honor it.

2. **Contractor Onboarding:** If hiring external developers, MongoDB in spec = easier to find contractors who match stack.

3. **Property-First Platform:** If properties are 80%+ of your data model and high schema variance expected, MongoDB document model shines.

4. **Budget Available:** Can afford MongoDB Atlas M10+ ($60/month min) and Qdrant Cloud/managed vector DB.

**Migration Path (If Choosing MongoDB):**

```markdown
Phase 1: Add MongoDB (Keep Postgres)
- Install MongoDB container
- Implement property models in MongoDB (Motor + Beanie)
- Reference Postgres users by clerk_user_id
- Test property CRUD operations

Phase 2: Add Vector DB (Qdrant)
- Install Qdrant container
- Migrate content_embeddings from pgvector to Qdrant
- Update search functions to query Qdrant
- Keep FAQ embeddings in Postgres (low volume)

Phase 3: Migrate Remaining Models (Optional)
- Evaluate if User/FAQ should move to MongoDB
- If yes, migrate incrementally
- If no, keep hybrid architecture

Phase 4: Sunset Postgres (Optional)
- Only if ALL data moved to MongoDB
- Otherwise keep Postgres for users/auth
```

**Estimated Migration Effort:**
- Phase 1: 2-3 days (property models + CRUD)
- Phase 2: 3-4 days (Qdrant integration + testing)
- Phase 3: 5-7 days (model migration + data sync)
- **Total: 10-14 days**

---

## Implementation Paths

### Path C1: Enhance PostgreSQL (Recommended)

**Step 1: Create Property Models (SQLAlchemy)**

File: `apps/server/src/server/models/property.py`

```python
from sqlalchemy import JSON, String, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import uuid4

class Property(Base):
    __tablename__ = "properties"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # rental, sale, business, etc.
    status: Mapped[str] = mapped_column(String(20), default="draft")

    # Location (could add PostGIS later)
    location_data: Mapped[dict] = mapped_column(JSONB, default=dict)

    # References
    agent_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Flexible attributes
    attributes: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Relationships
    agent: Mapped["User"] = relationship("User", back_populates="properties")
    rental_details: Mapped["RentalDetails"] = relationship("RentalDetails", back_populates="property")

    __table_args__ = (
        CheckConstraint("type IN ('rental', 'sale', 'lease', 'business', 'investment')"),
    )
```

**Step 2: Setup Alembic Migrations**

```bash
# Initialize Alembic
cd apps/server
alembic init migrations

# Edit alembic.ini - set sqlalchemy.url
# Edit migrations/env.py - import models

# Create first migration
alembic revision --autogenerate -m "Add property models"

# Apply migration
alembic upgrade head
```

**Step 3: Add Property Endpoints**

File: `apps/server/src/server/api/v1/properties.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from server.core.database import get_db
from server.models.property import Property

router = APIRouter(prefix="/properties", tags=["properties"])

@router.post("/")
async def create_property(
    property_data: PropertyCreate,
    db: AsyncSession = Depends(get_db)
):
    # Create property with rental/sale/business details
    pass
```

**Step 4: Integrate Vector Search**

```python
# Use existing content_embeddings table from init-pgvector.sql
from pgvector.sqlalchemy import Vector

# When creating property, also create embedding:
async def create_property_with_embedding(property: Property, db: AsyncSession):
    # Insert into properties table
    db.add(property)

    # Generate embedding
    embedding = await generate_embedding(property.title + " " + property.description)

    # Insert into content_embeddings (table already exists!)
    content_emb = ContentEmbedding(
        content_type="property",
        content_id=property.id,
        embedding=embedding,
        title=property.title,
        # ... other fields
    )
    db.add(content_emb)
    await db.commit()
```

**Timeline:** 3-5 days for full property CRUD + vector search

---

### Path A1: Switch to MongoDB + Qdrant

**Step 1: Add MongoDB to Docker Compose**

File: `docker-compose.dev.yml`

```yaml
  mongodb:
    image: mongo:7
    container_name: bestays-mongo-dev
    environment:
      MONGO_INITDB_ROOT_USERNAME: bestays_user
      MONGO_INITDB_ROOT_PASSWORD: bestays_password
      MONGO_INITDB_DATABASE: bestays_dev
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    networks:
      - bestays-network

  qdrant:
    image: qdrant/qdrant:latest
    container_name: bestays-qdrant-dev
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    networks:
      - bestays-network
```

**Step 2: Install MongoDB ODM**

```bash
poetry add motor beanie  # Async MongoDB ODM
poetry add qdrant-client  # Vector DB client
```

**Step 3: Create MongoDB Models**

File: `apps/server/src/server/models_mongo/property.py`

```python
from beanie import Document
from pydantic import Field
from typing import Literal
from uuid import uuid4

class Property(Document):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    slug: str
    type: Literal["rental", "sale", "lease", "business", "investment"]
    location: dict  # Full flexibility
    agent_clerk_id: str  # Reference to Postgres User.clerk_user_id
    attributes: dict = {}  # Any extra fields

    class Settings:
        name = "properties"  # Collection name
        indexes = [
            "type",
            "slug",
            "agent_clerk_id"
        ]

class RentalDetails(Document):
    property_id: str
    price_per_night: float
    amenities: list[str] = []
    # ... all rental fields

    class Settings:
        name = "rental_details"
```

**Step 4: Setup MongoDB Connection**

File: `apps/server/src/server/core/mongodb.py`

```python
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

async def init_mongodb():
    client = AsyncIOMotorClient("mongodb://bestays_user:bestays_password@mongodb:27017")
    await init_beanie(
        database=client.bestays_dev,
        document_models=[Property, RentalDetails, ...]
    )
```

**Step 5: Setup Qdrant Collections**

```python
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams

async def init_qdrant():
    client = AsyncQdrantClient(host="qdrant", port=6333)

    # Create collection for property embeddings
    await client.create_collection(
        collection_name="property_embeddings",
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
    )
```

**Step 6: Migrate Existing Data**

```python
# Migration script: postgres_to_mongo.py
async def migrate_users():
    # Keep users in Postgres (auth/roles)
    # OR copy to MongoDB for reference
    pass

async def migrate_faqs():
    # Option 1: Keep in Postgres
    # Option 2: Migrate to MongoDB
    pass
```

**Timeline:** 10-14 days for full migration + testing

---

## Data Consistency Patterns

### If Choosing Hybrid (Option B)

**Problem:** Property in MongoDB references User in PostgreSQL

**Solution 1: Reference by Clerk ID (Recommended)**
```python
# MongoDB property document
{
    "_id": "prop_123",
    "title": "Luxury Villa",
    "agent_clerk_id": "user_2abc123"  # Clerk ID (immutable)
}

# Query pattern
async def get_property_with_agent(property_id: str):
    # Get property from MongoDB
    property = await Property.get(property_id)

    # Get agent from Postgres
    agent = await db.execute(
        select(User).where(User.clerk_user_id == property.agent_clerk_id)
    )

    return {**property.dict(), "agent": agent}
```

**Solution 2: Event-Driven Sync**
```python
# When user changes in Postgres, emit event
await redis.publish("user.updated", json.dumps({
    "clerk_user_id": "user_abc",
    "email": "new@email.com"
}))

# MongoDB listener updates denormalized data
async def on_user_updated(event):
    await Property.find(
        {"agent_clerk_id": event["clerk_user_id"]}
    ).update({
        "$set": {"agent_email": event["email"]}  # Denormalized cache
    })
```

---

## Testing Strategy

### Acceptance Criteria (All Options)

1. **Property Creation**
   - [ ] Can create property of each type (rental, sale, business, investment, lease)
   - [ ] Type-specific details stored correctly
   - [ ] Semantic search returns newly created property within 1 second
   - [ ] Agent can only edit their own properties (authorization)

2. **Property Search**
   - [ ] Semantic search: "luxury villa with pool near beach" returns relevant results
   - [ ] Filter by type, location, price range works
   - [ ] Results sorted by similarity score
   - [ ] Search handles 10k+ properties in < 500ms

3. **Availability Management**
   - [ ] Can create availability calendar for rental property
   - [ ] Booking updates availability atomically (no double-booking)
   - [ ] Concurrent booking attempts handled correctly (1 succeeds, others get 409)

4. **Data Integrity** (Critical for Option B/C)
   - [ ] Deleting agent fails if they have properties (foreign key constraint or check)
   - [ ] Property references valid agent
   - [ ] Property update triggers embedding re-indexing

5. **Performance**
   - [ ] Property create: < 200ms
   - [ ] Property read: < 50ms
   - [ ] Semantic search: < 500ms (10k properties)
   - [ ] VPS memory usage: < 3.5GB under load

---

## Migration Checklist (If Choosing Option A)

### Pre-Migration
- [ ] Backup Postgres database
- [ ] Document current schema
- [ ] Create MongoDB test environment
- [ ] Setup Qdrant test instance
- [ ] Write integration tests for property CRUD

### Migration Phase
- [ ] Add MongoDB to docker-compose
- [ ] Install Motor + Beanie
- [ ] Create property models (MongoDB)
- [ ] Implement property endpoints (FastAPI + Beanie)
- [ ] Setup Qdrant collection
- [ ] Migrate vector search functions
- [ ] Test semantic search against Qdrant
- [ ] Decision: Keep User in Postgres OR migrate to MongoDB
- [ ] If migrating User: Write migration script + test sync
- [ ] Update authentication to work with new User location

### Post-Migration
- [ ] Run full integration test suite
- [ ] Performance benchmarking (vs Postgres baseline)
- [ ] Update architecture docs
- [ ] Update team onboarding docs
- [ ] Schedule Postgres data retention (if hybrid) or sunset (if full migration)

---

## Cost Analysis (Annual Estimates)

### Option A: MongoDB + Qdrant

**Development:**
- MongoDB: Self-hosted in Docker (free)
- Qdrant: Self-hosted in Docker (free)
- **Total: $0/year**

**Production (Single Region):**
- MongoDB Atlas M10 (2GB RAM, ~10GB storage): $57/month = **$684/year**
- Qdrant Cloud Starter (1GB vectors): $25/month = **$300/year**
- Redis (Managed): $20/month = **$240/year**
- **Total: $1,224/year**

**Production (VPS Self-Hosted):**
- VPS 8GB RAM (Digital Ocean, Hetzner): $40/month = **$480/year**
- MongoDB + Qdrant + Redis self-managed
- Backup storage (100GB): $5/month = **$60/year**
- **Total: $540/year** (requires ops expertise)

### Option B: Hybrid

**Production (Managed):**
- PostgreSQL (Supabase/Render 4GB): $25/month = **$300/year**
- MongoDB Atlas M10: $57/month = **$684/year**
- Redis: $20/month = **$240/year**
- **Total: $1,224/year**

### Option C: PostgreSQL Only

**Production (Managed):**
- PostgreSQL (Render/Railway 8GB with pgvector): $65/month = **$780/year**
- Redis: $20/month = **$240/year**
- **Total: $1,020/year**

**Production (VPS Self-Hosted):**
- VPS 8GB RAM: $40/month = **$480/year**
- Postgres + Redis self-managed
- Backup storage: $5/month = **$60/year**
- **Total: $540/year**

**Winner: Option C** ($1,020 managed, $540 self-hosted)

---

## References

### Internal Documentation
- **Architecture Spec:** `.sdlc-workflow/.specs/01_ARCHITECTURE.md`
- **Property Schema:** `.sdlc-workflow/.specs/02_PROPERTIES_SCHEMA.md`
- **Database Setup:** `apps/server/src/server/core/database.py`
- **Existing Models:** `apps/server/src/server/models/`
- **pgvector Init:** `docker/postgres/init-pgvector.sql`
- **Docker Compose:** `docker-compose.dev.yml`

### External Resources
- [PostgreSQL JSONB](https://www.postgresql.org/docs/current/datatype-json.html)
- [pgvector Performance](https://github.com/pgvector/pgvector#performance)
- [MongoDB Polymorphic Patterns](https://www.mongodb.com/docs/manual/data-modeling/design-patterns/polymorphic-pattern/)
- [Beanie ODM](https://beanie-odm.dev/)
- [Qdrant Cloud](https://qdrant.tech/documentation/cloud/)

---

## Decision Log

| Date | Decision | Rationale | Decided By |
|------|----------|-----------|------------|
| 2025-11-06 | Document created | Align spec vs implementation | Claude (Analysis) |
| 2025-11-06 | **Option C chosen: PostgreSQL + pgvector** | Simplicity, ACID transactions, existing infrastructure, lowest cost, best VPS footprint | Project Owner |
| 2025-11-06 | Architecture docs updated | Specs now reflect PostgreSQL decision | Claude |
| 2025-11-06 | Property schema redesigned | MongoDB collections → PostgreSQL tables with JSONB | Claude |

---

## Next Steps

1. **Review this document** with team/stakeholders
2. **Make decision:** Option A, B, or C?
3. **If Option C (Postgres):**
   - Setup Alembic migrations (`.../apps/server/migrations/`)
   - Create property models in SQLAlchemy
   - Implement property CRUD endpoints
   - Integrate with existing pgvector setup
4. **If Option A (MongoDB):**
   - Follow Migration Checklist above
   - Add MongoDB + Qdrant to docker-compose
   - Implement property models in Beanie
   - Migrate vector search to Qdrant
5. **If Option B (Hybrid):**
   - Add MongoDB for properties only
   - Keep Postgres for users/vectors/chat
   - Document reference pattern (Clerk ID)
   - Test data consistency scenarios

---

**Prepared by:** Claude Code
**Review Required:** Tech Lead, DevOps, Product Owner
**Target Decision Date:** TBD
**Blocking:** Property implementation (US-002, US-003, etc.)

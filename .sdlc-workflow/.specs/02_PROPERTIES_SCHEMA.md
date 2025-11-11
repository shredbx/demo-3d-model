# Properties Data Model & Guidelines

## Design goals

- Shared identity for every real estate asset.
- Independent evolution for each property type (rental, sale, lease, business, investment).
- Minimal duplication, fast lookups for browsing, and strong separation for management UI.
- ACID transactions for booking operations (prevent double-booking).
- Type safety via SQLAlchemy ORM with async support.

## Database: PostgreSQL 16 + pgvector

**Rationale:** Single database for data + vectors reduces operational complexity, ACID guarantees for bookings, JSONB provides schema flexibility where needed.

**Key Features Used:**
- UUID primary keys (`gen_random_uuid()`)
- JSONB columns for flexible attributes
- Foreign key constraints for referential integrity
- pgvector extension for semantic search (1536-dim embeddings)
- Full-text search via `pg_trgm` extension
- GIN indexes for JSONB and array columns

---

## Tables Schema

### Core Tables

1. **properties** (base table)
2. **rental_details**
3. **sale_details**
4. **business_details**
5. **investment_details**
6. **availability** (booking calendar)
7. **leads** (inquiries & booking requests)
8. **agents** (extends users table)
9. **companies**
10. **media** (references to Cloudflare R2)

### Vector Tables (Already Implemented)

Reference: `docker/postgres/init-pgvector.sql`

- **content_embeddings** - Unified table for all searchable content (properties, FAQs, etc.)
- **faq_embeddings** - FAQ-specific semantic search
- **search_history_embeddings** - Query analytics
- **conversation_embeddings** - Chat context

---

## Table Definitions

### `properties` (base table)

```sql
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Basic info
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    short_description TEXT,

    -- Property classification
    type VARCHAR(50) NOT NULL CHECK (type IN ('rental', 'sale', 'lease', 'business', 'investment')),
    primary_type VARCHAR(50) NOT NULL CHECK (primary_type IN ('rental', 'sale', 'business', 'investment')),
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived', 'sold', 'rented')),

    -- Location
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    location_address TEXT,
    location_city VARCHAR(100),
    location_country VARCHAR(100),
    location_data JSONB DEFAULT '{}', -- Additional location metadata (neighborhood, landmarks, etc.)

    -- Ownership
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    agent_id INTEGER REFERENCES users(id) ON DELETE SET NULL,

    -- Pricing (for quick browse filtering)
    price_min DECIMAL(15, 2),
    price_max DECIMAL(15, 2),
    currency VARCHAR(3) DEFAULT 'AED',

    -- Metadata
    tags TEXT[] DEFAULT '{}',
    attributes JSONB DEFAULT '{}', -- Flexible storage for type-specific flags

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ,

    -- Indexes
    CONSTRAINT properties_pkey PRIMARY KEY (id)
);

CREATE INDEX idx_properties_type ON properties(type);
CREATE INDEX idx_properties_status ON properties(status);
CREATE INDEX idx_properties_location ON properties(location_country, location_city);
CREATE INDEX idx_properties_slug ON properties(slug);
CREATE INDEX idx_properties_agent ON properties(agent_id);
CREATE INDEX idx_properties_company ON properties(company_id);
CREATE INDEX idx_properties_price_range ON properties(price_min, price_max);
CREATE INDEX idx_properties_tags ON properties USING GIN(tags);
CREATE INDEX idx_properties_attributes ON properties USING GIN(attributes);
CREATE INDEX idx_properties_updated ON properties(updated_at DESC);

-- Full-text search index (requires pg_trgm extension)
CREATE INDEX idx_properties_title_trgm ON properties USING GIN(title gin_trgm_ops);
CREATE INDEX idx_properties_description_trgm ON properties USING GIN(short_description gin_trgm_ops);

-- Trigger to update updated_at
CREATE TRIGGER update_properties_updated_at
    BEFORE UPDATE ON properties
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

**SQLAlchemy Model Preview:**

```python
class Property(Base):
    __tablename__ = "properties"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft")

    # Location (structured)
    location_lat: Mapped[Decimal | None] = mapped_column(Numeric(10, 8))
    location_lng: Mapped[Decimal | None] = mapped_column(Numeric(11, 8))
    location_city: Mapped[str | None] = mapped_column(String(100))
    location_data: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Relationships
    agent: Mapped["User"] = relationship("User", back_populates="properties")
    company: Mapped["Company"] = relationship("Company", back_populates="properties")
    rental_details: Mapped["RentalDetails"] = relationship("RentalDetails", back_populates="property", uselist=False)
    sale_details: Mapped["SaleDetails"] = relationship("SaleDetails", back_populates="property", uselist=False)

    # Flexible attributes
    attributes: Mapped[dict] = mapped_column(JSONB, default=dict)
```

---

### `rental_details`

```sql
CREATE TABLE rental_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,

    -- Pricing
    price_per_night DECIMAL(10, 2),
    price_per_month DECIMAL(10, 2),
    price_per_week DECIMAL(10, 2),
    cleaning_fee DECIMAL(10, 2),
    security_deposit DECIMAL(10, 2),

    -- Stay rules
    min_stay_nights INTEGER,
    max_stay_nights INTEGER,

    -- Amenities & features
    amenities JSONB DEFAULT '[]', -- ["wifi", "pool", "parking", ...]
    house_rules TEXT,

    -- Policies
    booking_policy TEXT,
    cancellation_policy VARCHAR(50) DEFAULT 'moderate', -- flexible, moderate, strict

    -- Availability
    availability_calendar_ref UUID REFERENCES availability(id),
    instant_booking BOOLEAN DEFAULT false,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    UNIQUE(property_id)
);

CREATE INDEX idx_rental_details_property ON rental_details(property_id);
CREATE INDEX idx_rental_details_price_night ON rental_details(price_per_night);
CREATE INDEX idx_rental_details_price_month ON rental_details(price_per_month);
CREATE INDEX idx_rental_details_amenities ON rental_details USING GIN(amenities);
```

---

### `sale_details`

```sql
CREATE TABLE sale_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,

    -- Pricing
    price DECIMAL(15, 2) NOT NULL,
    price_negotiable BOOLEAN DEFAULT true,

    -- Ownership
    ownership_type VARCHAR(50) CHECK (ownership_type IN ('freehold', 'leasehold', 'sharehold')),

    -- Dimensions
    land_size DECIMAL(10, 2), -- in sqm
    built_up_area DECIMAL(10, 2), -- in sqm

    -- Property details
    bedrooms INTEGER,
    bathrooms INTEGER,
    floors INTEGER,
    year_built INTEGER,

    -- Legal
    legal_docs UUID[], -- Array of media IDs
    zoning VARCHAR(100),
    title_deed_number VARCHAR(100),

    -- Additional features
    features JSONB DEFAULT '{}', -- {"parking_spaces": 2, "garden": true, ...}

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    UNIQUE(property_id)
);

CREATE INDEX idx_sale_details_property ON sale_details(property_id);
CREATE INDEX idx_sale_details_price ON sale_details(price);
CREATE INDEX idx_sale_details_ownership ON sale_details(ownership_type);
CREATE INDEX idx_sale_details_bedrooms ON sale_details(bedrooms);
```

---

### `business_details`

```sql
CREATE TABLE business_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,

    -- Business info
    business_type VARCHAR(100) NOT NULL, -- restaurant, cafe, retail, hotel, etc.
    business_name VARCHAR(200),

    -- Financials
    asking_price DECIMAL(15, 2),
    annual_revenue DECIMAL(15, 2),
    annual_profit DECIMAL(15, 2),
    ebitda DECIMAL(15, 2),

    -- Operations
    staff_count INTEGER,
    years_established INTEGER,
    operating_hours VARCHAR(100),

    -- Lease terms (if property is leased)
    lease_terms TEXT,
    lease_expiry_date DATE,
    monthly_rent DECIMAL(10, 2),

    -- Inventory & assets
    inventory_included BOOLEAN DEFAULT false,
    equipment_included BOOLEAN DEFAULT false,
    assets_description TEXT,

    -- Additional info
    reason_for_sale TEXT,
    business_details JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    UNIQUE(property_id)
);

CREATE INDEX idx_business_details_property ON business_details(property_id);
CREATE INDEX idx_business_details_type ON business_details(business_type);
CREATE INDEX idx_business_details_price ON business_details(asking_price);
```

---

### `investment_details`

```sql
CREATE TABLE investment_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,

    -- Investment type
    investment_type VARCHAR(50) CHECK (investment_type IN ('fractional', 'joint_venture', 'funding_round', 'development')),

    -- Project info
    project_stage VARCHAR(50) CHECK (project_stage IN ('concept', 'planning', 'construction', 'completed')),
    project_name VARCHAR(200),
    developer_name VARCHAR(200),

    -- Investment details
    minimum_investment DECIMAL(15, 2),
    maximum_investment DECIMAL(15, 2),
    total_project_value DECIMAL(15, 2),
    raised_amount DECIMAL(15, 2) DEFAULT 0,
    target_amount DECIMAL(15, 2),

    -- Returns
    expected_roi_percentage DECIMAL(5, 2), -- e.g., 12.50 for 12.5%
    expected_roi_timeframe VARCHAR(50), -- "12 months", "3 years"
    dividend_policy TEXT,

    -- Timeline
    construction_start_date DATE,
    expected_completion_date DATE,

    -- Legal
    documents UUID[], -- Array of media IDs (prospectus, contracts, etc.)
    legal_structure VARCHAR(100), -- LLC, partnership, etc.

    -- Additional info
    investment_highlights TEXT,
    risk_factors TEXT,
    investment_details JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    UNIQUE(property_id)
);

CREATE INDEX idx_investment_details_property ON investment_details(property_id);
CREATE INDEX idx_investment_details_type ON investment_details(investment_type);
CREATE INDEX idx_investment_details_stage ON investment_details(project_stage);
CREATE INDEX idx_investment_details_min_investment ON investment_details(minimum_investment);
```

---

### `availability` (booking calendar & lock store)

```sql
CREATE TABLE availability (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('rental', 'lease')),

    -- Date-based availability (for short-term rentals)
    date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available', 'booked', 'blocked', 'maintenance')),
    price DECIMAL(10, 2), -- Can vary by date (seasonal pricing)

    -- Booking lock (for preventing double-booking)
    locked_at TIMESTAMPTZ,
    locked_by_session VARCHAR(100), -- Session ID that holds the lock
    lock_expires_at TIMESTAMPTZ,
    booking_id UUID, -- Reference to actual booking once confirmed

    -- Metadata
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    UNIQUE(property_id, date),
    CHECK ((status = 'booked' AND booking_id IS NOT NULL) OR (status != 'booked'))
);

CREATE INDEX idx_availability_property ON availability(property_id);
CREATE INDEX idx_availability_date ON availability(date);
CREATE INDEX idx_availability_status ON availability(status);
CREATE INDEX idx_availability_property_date ON availability(property_id, date);
CREATE INDEX idx_availability_booking ON availability(booking_id) WHERE booking_id IS NOT NULL;
CREATE INDEX idx_availability_locks ON availability(lock_expires_at) WHERE locked_at IS NOT NULL;
```

**Important:** Use PostgreSQL advisory locks or Redis distributed locks for atomic booking operations.

---

### `leads` (inquiries & booking requests)

```sql
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Lead source
    property_id UUID REFERENCES properties(id) ON DELETE SET NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,

    -- Lead info
    lead_type VARCHAR(50) CHECK (lead_type IN ('inquiry', 'viewing_request', 'booking_request', 'offer')),
    status VARCHAR(50) DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'qualified', 'converted', 'closed', 'spam')),

    -- Contact details (if user not registered)
    contact_name VARCHAR(200),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),

    -- Message & details
    message TEXT,
    lead_data JSONB DEFAULT '{}', -- Flexible storage for viewing dates, offer amounts, etc.

    -- Assignment
    assigned_to INTEGER REFERENCES users(id) ON DELETE SET NULL, -- Agent handling this lead

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_contacted_at TIMESTAMPTZ,

    -- Source tracking
    source VARCHAR(50), -- website, chat, phone, referral
    utm_source VARCHAR(100),
    utm_campaign VARCHAR(100)
);

CREATE INDEX idx_leads_property ON leads(property_id);
CREATE INDEX idx_leads_user ON leads(user_id);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_assigned ON leads(assigned_to);
CREATE INDEX idx_leads_created ON leads(created_at DESC);
CREATE INDEX idx_leads_type ON leads(lead_type);
```

---

### `companies`

```sql
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Basic info
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,

    -- Contact
    email VARCHAR(255),
    phone VARCHAR(50),
    website VARCHAR(255),

    -- Address
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),

    -- Branding
    logo_url TEXT, -- Cloudflare R2 URL

    -- Settings
    is_active BOOLEAN DEFAULT true,
    company_settings JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_companies_slug ON companies(slug);
CREATE INDEX idx_companies_active ON companies(is_active);
```

---

### `media`

```sql
CREATE TABLE media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- File info
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255),
    mime_type VARCHAR(100),
    file_size BIGINT, -- in bytes

    -- Storage (Cloudflare R2)
    storage_key TEXT NOT NULL, -- R2 object key
    storage_url TEXT NOT NULL, -- CDN URL
    thumbnail_url TEXT,

    -- Classification
    media_type VARCHAR(50) CHECK (media_type IN ('image', 'video', 'document', 'other')),
    media_category VARCHAR(50), -- property_photo, floor_plan, legal_doc, etc.

    -- Associations (polymorphic - can attach to any entity)
    entity_type VARCHAR(50), -- 'property', 'user', 'company', etc.
    entity_id UUID,

    -- Metadata
    width INTEGER,
    height INTEGER,
    duration INTEGER, -- For videos (in seconds)
    alt_text TEXT,
    display_order INTEGER DEFAULT 0,
    is_primary BOOLEAN DEFAULT false, -- For property main image

    -- Uploaded by
    uploaded_by INTEGER REFERENCES users(id) ON DELETE SET NULL,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_media_entity ON media(entity_type, entity_id);
CREATE INDEX idx_media_type ON media(media_type);
CREATE INDEX idx_media_uploaded_by ON media(uploaded_by);
CREATE INDEX idx_media_created ON media(created_at DESC);
```

---

## Integration with Vector Search

Properties automatically get embeddings in the existing `content_embeddings` table:

```sql
-- When creating/updating a property, insert/update embedding:
INSERT INTO content_embeddings (
    content_type,
    content_id,
    embedding,  -- Generated via OpenRouter API
    title,
    description,
    location_country,
    location_city,
    price_min,
    price_max,
    tags,
    is_active,
    is_public
) VALUES (
    'property',
    property.id,
    generate_embedding(property.title || ' ' || property.short_description),
    property.title,
    property.short_description,
    property.location_country,
    property.location_city,
    property.price_min,
    property.price_max,
    property.tags,
    true,
    property.status = 'published'
);
```

**Semantic Search Query:**

```sql
SELECT
    p.*,
    1 - (ce.embedding <=> query_embedding) as similarity
FROM properties p
JOIN content_embeddings ce ON ce.content_id = p.id AND ce.content_type = 'property'
WHERE
    p.status = 'published'
    AND 1 - (ce.embedding <=> query_embedding) > 0.7
ORDER BY ce.embedding <=> query_embedding
LIMIT 10;
```

Or use the existing stored function:

```sql
SELECT * FROM search_similar_content(
    query_embedding := generate_embedding('luxury villa with sea view'),
    p_content_types := ARRAY['property'],
    p_limit := 10
);
```

---

## UI & Form Strategy

When creating a new listing, ask first: **What type of listing?** → show type-specific form.

**Form Flow:**

1. **Step 1: Property Type Selection**
   - Radio buttons: Rental | Sale | Lease | Business | Investment

2. **Step 2: Basic Information** (all types)
   - Title, slug, description, location, images

3. **Step 3: Type-Specific Details**
   - **Rental:** pricing, amenities, booking policies
   - **Sale:** price, ownership, dimensions, features
   - **Business:** financials, staff, operations
   - **Investment:** ROI, project stage, minimum investment

4. **Step 4: Review & Publish**
   - Preview, status selection (draft/published)

Keep common fields in a single form panel. Validate type-specific rules on server via Pydantic schemas + SQLAlchemy constraints.

---

## Query Patterns & Performance

### Common Queries

**Browse properties by type:**
```sql
SELECT * FROM properties
WHERE type = 'rental' AND status = 'published'
ORDER BY updated_at DESC
LIMIT 20;
```

**Search with filters:**
```sql
SELECT p.*, rd.price_per_night
FROM properties p
JOIN rental_details rd ON rd.property_id = p.id
WHERE
    p.type = 'rental'
    AND p.status = 'published'
    AND p.location_city = 'Dubai'
    AND rd.price_per_night BETWEEN 100 AND 500
    AND p.tags && ARRAY['beach', 'pool']  -- Overlaps with array
ORDER BY p.updated_at DESC;
```

**Get property with all details (polymorphic):**
```sql
SELECT
    p.*,
    CASE
        WHEN p.type = 'rental' THEN row_to_json(rd)
        WHEN p.type = 'sale' THEN row_to_json(sd)
        WHEN p.type = 'business' THEN row_to_json(bd)
        WHEN p.type = 'investment' THEN row_to_json(id)
    END as details
FROM properties p
LEFT JOIN rental_details rd ON rd.property_id = p.id
LEFT JOIN sale_details sd ON sd.property_id = p.id
LEFT JOIN business_details bd ON bd.property_id = p.id
LEFT JOIN investment_details id ON id.property_id = p.id
WHERE p.slug = 'luxury-villa-dubai-marina';
```

**Check availability (atomic booking):**
```sql
BEGIN;

-- Lock specific date
SELECT * FROM availability
WHERE property_id = 'prop-uuid' AND date = '2025-12-25'
FOR UPDATE NOWAIT; -- Fail fast if already locked

-- Update if available
UPDATE availability
SET
    status = 'booked',
    booking_id = 'booking-uuid',
    locked_at = NOW(),
    locked_by_session = 'session-abc',
    lock_expires_at = NOW() + INTERVAL '15 minutes'
WHERE property_id = 'prop-uuid'
  AND date = '2025-12-25'
  AND status = 'available';

COMMIT;
```

---

## Backwards Compatibility & Migrations

**Migration Strategy:** Use Alembic for all schema changes.

**Initial Migration:**
```bash
# Create first migration with all property tables
alembic revision --autogenerate -m "Add property tables (rental, sale, business, investment)"
alembic upgrade head
```

**Adding Fields:**
```python
# Add new field with default value (backwards compatible)
op.add_column('properties',
    sa.Column('featured', sa.Boolean(), server_default='false'))
```

**Breaking Changes:**
- Always provide a data migration script
- Include rollback strategy
- Test against sample database
- Use blue-green deployment for zero downtime

---

## Acceptance & Integration Test Plan

### Principles

Integration tests must run against an ephemeral Postgres container.

Tests should cover: auth, create property (all subtypes), availability check, booking flow, lead creation.

Each test must include a cleanup step (transaction rollback or `TRUNCATE`).

---

### User Stories + Acceptance Criteria

#### Story 1: Create rental listing

**As an agent**, I want to create a rental listing so that users can book short stays.

**Acceptance:**
- POST `/properties` (auth: agent) with `type=rental` returns 201 + property ID
- POST `/rental_details` with `property_id` returns 201
- GET `/properties/{slug}` returns combined view (base + rental_details)
- Property appears in semantic search within 5 seconds

**Integration Test:**
```python
async def test_create_rental_property():
    # Create property
    response = await client.post("/api/v1/properties", json={
        "title": "Beach Villa",
        "type": "rental",
        "location_city": "Dubai"
    }, headers=agent_auth_headers)
    assert response.status_code == 201
    property_id = response.json()["id"]

    # Add rental details
    response = await client.post("/api/v1/rental_details", json={
        "property_id": property_id,
        "price_per_night": 500.00,
        "amenities": ["wifi", "pool"]
    })
    assert response.status_code == 201

    # Verify combined view
    response = await client.get(f"/api/v1/properties/{property_id}")
    data = response.json()
    assert data["rental_details"]["price_per_night"] == 500.00
```

---

#### Story 2: Availability + booking (critical)

**As a user**, I can check availability and attempt booking; system must prevent double-booking.

**Acceptance:**
- GET `/properties/{id}/availability?date=YYYY-MM-DD` returns `status: available|booked`
- POST `/bookings/reserve` with `property_id`, `date`, `user_id` must lock slot (atomic)
- After reservation, another attempt for same slot returns 409 Conflict
- On confirm (payment success), DB write committed and availability updated

**Integration Test:**
```python
async def test_concurrent_booking_prevention():
    # Create property with availability
    property_id = await create_rental_property()
    await create_availability(property_id, "2025-12-25", "available")

    # Concurrent booking attempts (5 clients)
    tasks = [
        attempt_booking(property_id, "2025-12-25", f"session-{i}")
        for i in range(5)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Exactly 1 success, 4 conflicts
    success_count = sum(1 for r in results if r.status_code == 200)
    conflict_count = sum(1 for r in results if r.status_code == 409)

    assert success_count == 1
    assert conflict_count == 4

    # Verify DB state
    availability = await get_availability(property_id, "2025-12-25")
    assert availability["status"] == "booked"
```

---

#### Story 3: Sale listing workflow

**As an agent**, create a sale property, attach legal docs, and mark status 'published'.

**Acceptance:**
- POST `/properties` (type=sale)
- POST `/sale_details` with price, ownership_type
- POST `/media` to attach legal documents
- PATCH `/properties/{id}` to publish
- GET `/properties?type=sale` returns listing in paginated results

---

### Test Tooling

- **Framework:** pytest + pytest-asyncio
- **Database:** Ephemeral Postgres container (Docker Compose test fixture)
- **Fixtures:** `async_client`, `db_session`, `auth_headers`
- **Factories:** `PropertyFactory`, `UserFactory` (using `factory_boy`)

```bash
# Run integration tests
docker-compose -f docker-compose.test.yml up -d
pytest tests/integration/ -v
docker-compose -f docker-compose.test.yml down -v
```

---

### Test Matrix (Minimal)

| Test Category | Coverage |
|---------------|----------|
| **Smoke** | Service starts, health endpoints respond |
| **Auth** | Clerk webhook creates user, roles enforced |
| **CRUD** | Create/read/update/delete properties for each type |
| **Booking** | Concurrent attempts → 1 success + others 409 |
| **Search** | Text + geo + price filtering returns correct results |
| **Vector Search** | Semantic search returns relevant properties |

---

## Docker Compose Skeleton

```yaml
version: "3.8"
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: bestays_user
      POSTGRES_PASSWORD: bestays_password
      POSTGRES_DB: bestays_dev
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/01-init.sql
      - ./docker/postgres/init-pgvector.sql:/docker-entrypoint-initdb.d/02-init-pgvector.sql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  fastapi:
    build: .
    environment:
      DATABASE_URL: postgresql+asyncpg://bestays_user:bestays_password@postgres:5432/bestays_dev
      REDIS_URL: redis://redis:6379
    ports:
      - "8011:8011"
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
```

---

## Summary

This schema provides:
- ✅ Type-safe SQLAlchemy models with async support
- ✅ ACID transactions for bookings (no double-booking)
- ✅ Flexible JSONB columns for type-specific attributes
- ✅ Unified vector search via pgvector (already configured)
- ✅ Foreign key constraints for referential integrity
- ✅ Performance indexes on common query patterns
- ✅ Alembic migration support for schema evolution
- ✅ Polymorphic pattern for different property types

**Next Steps:**
1. Implement SQLAlchemy models in `apps/server/src/server/models/property.py`
2. Setup Alembic migrations in `apps/server/migrations/`
3. Create Pydantic schemas for API validation
4. Implement property CRUD endpoints
5. Write integration tests per acceptance criteria above

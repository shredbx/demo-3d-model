# Research Findings: US-023 Property Import & Display

**Research Date:** 2025-11-09  
**Task:** TASK-013  
**Researcher:** Claude Code (Coordinator)  
**Thoroughness Level:** Medium

---

## 1. i18n Implementation (US-021)

### Current Status: NOT YET IMPLEMENTED

**Discovery:**
- US-021 (Thai Localization & Locale Switching) is **fully documented** but **NOT implemented** yet
- TASK-010 shows status as COMPLETED, but the i18n implementation files do not exist in the codebase
- This is a **critical blocker** for US-023 if we want multi-language property display

### Documented i18n Approach (from US-021)

**Library:** Custom i18n implementation (NO external library like paraglide/inlang)
- **Why custom?** ~50 lines of code, Svelte 5 runes compatible, SSR-safe

**Locale Storage Strategy:**
```
URL Parameter: /[lang]/
- /en → English
- /th → Thai
- Root / → Redirects to /en (default)
```

**Implementation Pattern (from US-021 docs):**
```typescript
// lib/i18n/context.svelte.ts
interface I18nContext {
  locale: string;
  setLocale: (newLocale: string) => void;
}

function createI18nContext(initialLocale: string): I18nContext {
  let locale = $state(initialLocale);
  
  function setLocale(newLocale: string) {
    locale = newLocale;
    goto(`/${newLocale}`);
  }
  
  return { get locale() { return locale }, setLocale };
}
```

**Translation Storage:**
- **Backend:** `content_dictionary` table with `(key, locale, value)` composite key
- **API:** `GET /api/v1/content/{key}?locale=en|th`
- **Cache:** Redis with locale-specific keys: `content:en:homepage.title`, `content:th:homepage.title`

**Files (Documented but DO NOT exist):**
- `/Users/solo/Projects/_repos/bestays/apps/frontend/src/lib/i18n/context.svelte.ts` ❌
- `/Users/solo/Projects/_repos/bestays/apps/frontend/src/lib/i18n/types.ts` ❌
- `/Users/solo/Projects/_repos/bestays/apps/frontend/src/lib/components/LocaleSwitcher.svelte` ❌
- `/Users/solo/Projects/_repos/bestays/apps/frontend/src/routes/[lang]/+layout.svelte` ❌
- `/Users/solo/Projects/_repos/bestays/apps/frontend/src/routes/[lang]/+page.svelte` ❌

**Current Routes Structure:**
```
routes/
  +layout.svelte       (Root layout)
  +page.svelte         (Homepage - no locale support)
  login/
  dashboard/
  me/
```

### Recommendations for US-023

**Option A: Implement i18n FIRST (Recommended)**
- Complete US-021 implementation before US-023
- Benefits: Full multi-language support from day 1
- Timeline: +2 days (US-021 implementation)

**Option B: Skip i18n for MVP (Faster)**
- Display properties in English only initially
- Add Thai translations later via separate task
- Benefits: Faster to market
- Risks: Rework required for localization

**Critical Decision Point:** Ask user which approach to take before planning phase.

---

## 2. Old Database Structure

### Schema Location
**Path:** `/Users/solo/Projects/_repos/react-workspace/src/apps/bestays-web/db/sql-2/2.property2-tables.sql`

### Property V2 Schema (Exact Structure)

**Table:** `bestays_properties_v2`

**Core Fields:**
```sql
id UUID PRIMARY KEY
title TEXT (max 200 chars)
description TEXT (max 5000 chars)
title_deed TEXT
```

**Pricing:**
```sql
sale_price BIGINT (≥ 0)
rent_price BIGINT (≥ 0)
lease_price BIGINT (≥ 0)
currency bestays_currency_type DEFAULT 'THB'
price_per_unit NUMERIC(15,2)
```

**Classification:**
```sql
transaction_type bestays_property2_transaction_type NOT NULL
  -- Enum values: 'sale', 'rent', 'lease', 'sale-lease'
property_type bestays_property2_type NOT NULL
  -- Enum values: 'land', 'house', 'villa', 'pool-villa', 'apartment', 'condo',
  --              'townhouse', 'penthouse', 'office', 'shop', 'warehouse',
  --              'business', 'resort', 'hotel', 'other'
```

**JSONB Fields (THE KEY DIFFERENCE):**
```sql
physical_specs JSONB
  -- Structure: { rooms: { bedrooms, bathrooms }, sizes: { living_area, land_area, ... }, ... }

location_details JSONB
  -- Structure: { coordinates: { lat, lon }, address: { ... }, region, district, ... }

amenities JSONB
  -- Structure: { interior: [], exterior: [], building: [], neighborhood: [] }
  -- 150+ predefined amenity IDs

policies JSONB
  -- Structure: { inclusions: [], restrictions: [], house_rules: [] }

contact_info JSONB
  -- Structure: { agent_name, agent_phone, agent_email, languages_spoken, ... }
```

**Media:**
```sql
cover_image JSONB      -- { url, alt, width, height }
images JSONB           -- Array of image objects (max 30)
virtual_tour_url TEXT
video_url TEXT
```

**System Fields:**
```sql
is_published BOOLEAN DEFAULT FALSE NOT NULL
is_featured BOOLEAN DEFAULT FALSE NOT NULL
listing_priority INTEGER DEFAULT 0

created_by UUID REFERENCES auth.users(id)
updated_by UUID REFERENCES auth.users(id)
created_at TIMESTAMP WITH TIME ZONE
updated_at TIMESTAMP WITH TIME ZONE
deleted_at TIMESTAMP WITH TIME ZONE  -- Soft delete
```

**SEO:**
```sql
seo_title TEXT (max 60 chars)
seo_description TEXT (max 160 chars)
tags TEXT[]
```

**Investment:**
```sql
rental_yield NUMERIC(5,2)
price_trend bestays_property2_price_trend  -- 'rising', 'stable', 'falling'
```

### Indexes (Performance Critical)

**Standard Indexes:**
```sql
idx_bestays_properties_v2_is_published (is_published)
idx_bestays_properties_v2_transaction_type (transaction_type)
idx_bestays_properties_v2_property_type (property_type)
idx_bestays_properties_v2_deleted_at (deleted_at)
idx_bestays_properties_v2_featured (is_featured)
idx_bestays_properties_v2_listing_priority (listing_priority DESC)
```

**GIN Indexes (JSONB Queries):**
```sql
idx_bestays_properties_v2_location_details USING GIN (location_details)
idx_bestays_properties_v2_physical_specs USING GIN (physical_specs)
idx_bestays_properties_v2_amenities USING GIN (amenities)
idx_bestays_properties_v2_tags USING GIN (tags)
```

### Translation Table

**Table:** `bestays_property_translations`

**Schema:**
```sql
id BIGINT PRIMARY KEY
property_id UUID REFERENCES bestays_properties_v2(id) ON DELETE CASCADE
lang_code CHAR(2)  -- 'en', 'th', 'ru', 'zh', 'de', 'fr'
field TEXT  -- 'title', 'description', 'location_region', ...
value TEXT
created_at TIMESTAMP WITH TIME ZONE

UNIQUE(property_id, lang_code, field)
```

**Supported Languages:** EN, TH, RU, ZH, DE, FR (6 languages)

**Translatable Fields (13 total):**
- title
- description
- location_region
- location_district
- amenities_interior
- amenities_exterior
- amenities_building
- amenities_neighborhood
- policies_inclusions
- policies_restrictions
- policies_house_rules
- seo_title
- seo_description

### Property Count

**Status:** Cannot determine exact count (database not accessible from development environment)

**Estimation Strategy for Planning Phase:**
- Query production Supabase database during planning
- Expected range: 50-200 properties (based on typical vacation rental startup)
- Critical for determining import batch size and timeline

---

## 3. Import Script Design

### Current State: NO IMPORT SCRIPTS EXIST

**Search Results:**
- No migration scripts in `/Users/solo/Projects/_repos/bestays/apps/server/src/server/scripts/`
- No seed scripts for properties
- Only found generic npm scripts (unrelated)

### Existing Patterns in Codebase

**Database Connection:**
```python
# Current pattern (from server config)
DATABASE_URL = "postgresql://user:password@localhost:5433/bestays_dev"

# Connection via SQLAlchemy (async)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
engine = create_async_engine(DATABASE_URL)
```

**Batch Processing Pattern:**
- US-016 documents comprehensive migration strategy
- Recommended batch size: 500 properties/batch
- Uses `asyncpg` for async batch insert

### Recommended Import Strategy (from US-016)

**Phase 1: Development/Testing (Export → Transform → Import)**

**Script 1: `supabase_export.py`**
- Export via Supabase REST API (paginated)
- Output: JSON files (properties_batch_001.json, etc.)
- Include translations
- Tech: `supabase-py` client

**Script 2: `transform_properties.py`**
- Transform old schema → new schema
- Map JSONB structures
- Handle locale data
- Tech: Python + Pydantic validation

**Script 3: `import_properties.py`**
- Batch insert to PostgreSQL
- Transaction-wrapped (rollback on error)
- Tech: `asyncpg` + SQLAlchemy

**Phase 2: Production (Direct Database Connection)**

**Script 4: `supabase_direct.py`**
- Direct PostgreSQL connection (Supabase → Bestays)
- Server-side cursors (memory efficient)
- Resume capability (migration_state table)
- Inline transformation
- Tech: `psycopg2` + `asyncpg`

### Critical Files to Create

**Migration Scripts:**
```
apps/server/scripts/migration/
  ├── supabase_export.py       (REST API export)
  ├── transform_properties.py  (Schema transformation)
  ├── import_properties.py     (Batch import)
  └── supabase_direct.py       (Production migration)
```

**Config:**
```
config/migration.yaml
  - Supabase credentials
  - Batch sizes
  - Default values (admin_user_id, commission_rate)
  - Company contact info (for contact_info JSONB transformation)
```

**State Tracking:**
```sql
CREATE TABLE migration_state (
    id SERIAL PRIMARY KEY,
    migration_name VARCHAR(100) UNIQUE,
    status VARCHAR(20),  -- 'running', 'completed', 'failed', 'paused'
    last_processed_id UUID,
    total_count INTEGER,
    processed_count INTEGER,
    failed_count INTEGER,
    error_log JSONB
);
```

### Technology Recommendations

**Python (Recommended) ✅**
- Pros: Matches backend stack, `asyncpg` performance, Pydantic validation
- Cons: None significant
- **Use for:** All migration scripts

**TypeScript/Node.js (Not Recommended) ❌**
- Pros: Familiar to frontend team
- Cons: Slower for bulk operations, no Pydantic equivalent
- **Use for:** None (avoid for data migration)

---

## 4. Property V2 JSONB Structure (US-016)

### Current Property Model: BASIC (Needs Migration)

**File:** `/Users/solo/Projects/_repos/bestays/apps/server/src/server/models/property.py`

**Current Schema (VERY LIMITED):**
```python
class Property(Base):
    __tablename__ = "properties"
    
    id: UUID
    title: str (max 255)
    description: Optional[str]
    is_published: bool
    created_by: Optional[int] → FK to users
    updated_by: Optional[int]
    published_by: Optional[int]
    created_at: datetime
    updated_at: datetime
```

**Missing from Current Schema:**
- ❌ ALL JSONB fields (physical_specs, location_details, amenities, policies, contact_info)
- ❌ Pricing fields (sale_price, rent_price, lease_price, currency)
- ❌ Classification (transaction_type, property_type)
- ❌ Media (cover_image, images, virtual_tour_url, video_url)
- ❌ SEO fields (seo_title, seo_description, tags)
- ❌ Soft delete (deleted_at)
- ❌ Translation support

### Required Migration: V1 → V2

**Alembic Migration Needed:**
```python
# alembic/versions/xxx_upgrade_to_property_v2.py

def upgrade():
    # Add new columns
    op.add_column('properties', sa.Column('sale_price', sa.BIGINT))
    op.add_column('properties', sa.Column('rent_price', sa.BIGINT))
    # ... (50+ new columns)
    
    # Add JSONB columns
    op.add_column('properties', sa.Column('physical_specs', postgresql.JSONB))
    op.add_column('properties', sa.Column('location_details', postgresql.JSONB))
    op.add_column('properties', sa.Column('amenities', postgresql.JSONB))
    op.add_column('properties', sa.Column('policies', postgresql.JSONB))
    op.add_column('properties', sa.Column('contact_info', postgresql.JSONB))
    
    # Create GIN indexes for JSONB
    op.create_index('idx_properties_location', 'properties', ['location_details'], postgresql_using='gin')
    # ... (more indexes)
    
    # Create translation table
    op.create_table('bestays_property_translations', ...)
```

**Timeline:** ~0.5 days (migration creation + testing)

### JSONB Structure Details

**1. physical_specs:**
```json
{
  "rooms": {
    "bedrooms": 3,
    "bathrooms": 2,
    "living_rooms": 1,
    "kitchens": 1,
    "dining_rooms": 1,
    "office_rooms": 0,
    "storage_rooms": 1
  },
  "sizes": {
    "living_area": { "value": 150, "unit": "sqm" },
    "land_area": { "value": 200, "unit": "sqm" },
    "balcony_area": { "value": 20, "unit": "sqm" }
  },
  "floors": {
    "total_floors": 2,
    "property_floor": null
  },
  "parking": {
    "spaces": 2,
    "type": "covered"
  }
}
```

**2. location_details:**
```json
{
  "coordinates": { "lat": 13.7563, "lon": 100.5018 },
  "address": {
    "street": "123 Sukhumvit Rd",
    "district": "Watthana",
    "province": "Bangkok",
    "postal_code": "10110",
    "country": "Thailand"
  },
  "region": "Central Bangkok",
  "district": "Watthana",
  "neighborhood": "Asoke"
}
```

**3. amenities:**
```json
{
  "interior": [
    { "id": "air_conditioning", "label": "Air Conditioning" },
    { "id": "wifi", "label": "WiFi" },
    { "id": "kitchen_appliances", "label": "Kitchen Appliances" }
  ],
  "exterior": [
    { "id": "private_pool", "label": "Private Pool" },
    { "id": "garden", "label": "Garden" }
  ],
  "building": [
    { "id": "elevator", "label": "Elevator" },
    { "id": "security_24h", "label": "24/7 Security" },
    { "id": "gym", "label": "Gym" }
  ],
  "neighborhood": [
    { "id": "near_bts", "label": "Near BTS" },
    { "id": "shopping_mall", "label": "Shopping Mall Nearby" }
  ]
}
```

**4. policies:**
```json
{
  "inclusions": ["Utilities", "Internet", "Cable TV"],
  "restrictions": ["No pets", "No smoking"],
  "house_rules": ["Quiet hours 10pm-7am", "Maximum 4 guests"],
  "lease_terms": {
    "min_lease_months": 12,
    "deposit_months": 2,
    "advance_rent_months": 1
  }
}
```

**5. contact_info (OLD - Agent-Centric):**
```json
{
  "agent_name": "John Doe",
  "agent_phone": "+66812345678",
  "agent_email": "john@agency.com",
  "languages_spoken": ["English", "Thai"],
  "preferred_contact": "whatsapp"
}
```

**Note:** US-016 specifies transformation to **company-centric** model for new system.

### GIN Indexes and Query Patterns

**Why GIN Indexes?**
- Enable fast JSONB queries (containment, existence, path)
- Required for filtering by amenities, location, room count

**Example Queries Enabled:**
```sql
-- Find properties with private pool
SELECT * FROM bestays_properties_v2
WHERE amenities->'exterior' @> '[{"id": "private_pool"}]'::jsonb;

-- Find 3-bedroom properties
SELECT * FROM bestays_properties_v2
WHERE physical_specs->'rooms'->>'bedrooms' = '3';

-- Find properties in Bangkok
SELECT * FROM bestays_properties_v2
WHERE location_details->'address'->>'province' = 'Bangkok';
```

**Performance Impact:**
- Without GIN: Full table scan (slow)
- With GIN: Index scan (fast, even for 10k+ properties)

### Localization Strategy for JSONB

**Option A: Store translations in `bestays_property_translations` table ✅**
- Pros: Clean separation, easy to query by locale
- Cons: More complex queries (JOIN required)
- **Recommended by US-016**

**Option B: Store translations inline in JSONB ❌**
```json
{
  "title": { "en": "Beautiful Villa", "th": "วิลล่าสวยงาม" }
}
```
- Pros: Single query
- Cons: Bloated JSONB, harder to validate, harder to edit specific locales
- **NOT recommended**

**Conclusion:** Use separate translation table (already exists in old schema).

---

## 5. Grid Performance Patterns

### Current State: NO GRID COMPONENTS EXIST

**Search Results:**
- Found generic UI components: `MessageList.svelte`, `Card` components
- NO property-specific grid/list components
- NO pagination components
- NO infinite scroll implementations

### Existing UI Component Patterns

**File:** `/Users/solo/Projects/_repos/bestays/apps/frontend/src/lib/components/chat/MessageList.svelte`

**Pattern Observed:**
```svelte
<script lang="ts">
  let { messages } = $props();
  
  // Simple list rendering (no pagination)
</script>

<div class="message-list">
  {#each messages as message}
    <Message {message} />
  {/each}
</div>
```

**Assessment:** Basic list pattern, NOT suitable for large property datasets.

### Grid Layout Recommendations

**Option A: Grid with Pagination (Traditional) ✅**
- Display: 12-24 properties per page
- Navigation: Page numbers (1, 2, 3, ..., 10)
- Tech: SvelteKit server-side pagination (`+page.server.ts` with `?page=` param)
- Pros: SEO-friendly, works without JS, fast initial load
- Cons: Full page reload on navigation (mitigated by SvelteKit)

**Implementation Pattern:**
```typescript
// routes/properties/+page.server.ts
export async function load({ url, fetch }) {
  const page = parseInt(url.searchParams.get('page') || '1');
  const perPage = 24;
  
  const response = await fetch(
    `/api/v1/properties?page=${page}&per_page=${perPage}&locale=en`
  );
  
  const { properties, total, pages } = await response.json();
  
  return { properties, total, pages, currentPage: page };
}
```

```svelte
<!-- routes/properties/+page.svelte -->
<script lang="ts">
  let { data } = $props();
</script>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
  {#each data.properties as property}
    <PropertyCard {property} />
  {/each}
</div>

<Pagination currentPage={data.currentPage} totalPages={data.pages} />
```

**Option B: Infinite Scroll (Modern) ⚠️**
- Display: Load 24 properties initially, +24 on scroll
- Navigation: Scroll to bottom → auto-load more
- Tech: Intersection Observer API + client-side fetch
- Pros: Smooth UX, no page reloads
- Cons: SEO challenges, requires JS, harder to link to specific page

**Recommendation for US-023:** Start with **Option A (Pagination)** for MVP, add infinite scroll later if needed.

### Image Lazy Loading

**Strategy:** Intersection Observer (native browser lazy loading)

```svelte
<script lang="ts">
  let { property } = $props();
</script>

<img 
  src={property.cover_image.url} 
  alt={property.title}
  loading="lazy"  <!-- Native lazy loading -->
  class="w-full h-48 object-cover"
/>
```

**Fallback for Older Browsers:**
```svelte
<script>
  import { onMount } from 'svelte';
  
  let imgElement;
  let loaded = $state(false);
  
  onMount(() => {
    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        loaded = true;
        observer.disconnect();
      }
    });
    
    observer.observe(imgElement);
  });
</script>

<img 
  bind:this={imgElement}
  src={loaded ? property.cover_image.url : '/placeholder.jpg'}
  alt={property.title}
/>
```

### Backend Pagination API

**Recommended Pattern (from FastAPI best practices):**

```python
# server/api/v1/endpoints/properties.py

@router.get("/properties")
async def list_properties(
    page: int = Query(1, ge=1),
    per_page: int = Query(24, ge=1, le=100),
    locale: str = Query('en', regex='^(en|th)$'),
    transaction_type: Optional[str] = None,
    property_type: Optional[str] = None,
    service: PropertyService = Depends(get_property_service)
):
    """
    List properties with pagination.
    
    Query Parameters:
      - page: Page number (1-indexed)
      - per_page: Items per page (max 100)
      - locale: Language (en, th)
      - transaction_type: Filter by sale/rent/lease
      - property_type: Filter by villa/condo/etc
    
    Returns:
      {
        properties: [...],
        total: 150,
        page: 1,
        per_page: 24,
        pages: 7
      }
    """
    skip = (page - 1) * per_page
    
    properties, total = await service.list_properties(
        skip=skip,
        limit=per_page,
        locale=locale,
        transaction_type=transaction_type,
        property_type=property_type
    )
    
    return {
        "properties": properties,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page  # Ceiling division
    }
```

**Database Query (with GIN indexes):**
```python
# service layer
async def list_properties(
    self,
    skip: int,
    limit: int,
    locale: str,
    transaction_type: Optional[str] = None,
    property_type: Optional[str] = None
):
    query = select(Property).where(
        Property.is_published == True,
        Property.deleted_at.is_(None)
    )
    
    if transaction_type:
        query = query.where(Property.transaction_type == transaction_type)
    
    if property_type:
        query = query.where(Property.property_type == property_type)
    
    # Order by priority, then created_at
    query = query.order_by(
        Property.listing_priority.desc(),
        Property.created_at.desc()
    )
    
    # Pagination
    query = query.offset(skip).limit(limit)
    
    properties = await self.db.execute(query)
    
    # Count total (for pagination metadata)
    count_query = select(func.count(Property.id)).where(...)
    total = await self.db.scalar(count_query)
    
    return properties.scalars().all(), total
```

**Index Usage:**
- `idx_properties_is_published` → Fast filter on is_published=true
- `idx_properties_transaction_type` → Fast filter on transaction_type
- `idx_properties_listing_priority` → Fast ORDER BY

**Performance Target:**
- Response time: < 200ms for 24 properties
- Database query: < 50ms (with indexes)
- Image CDN: < 100ms per image

### Caching Strategy

**Redis Caching for Property Lists:**
```python
# Cache key pattern
cache_key = f"properties:list:page={page}:per_page={per_page}:locale={locale}:tx={transaction_type}"

# Try cache first
cached = await redis.get(cache_key)
if cached:
    return json.loads(cached)

# Cache miss - query database
properties, total = await service.list_properties(...)

# Cache for 5 minutes (properties change infrequently)
await redis.set(cache_key, json.dumps(result), ex=300)
```

**Cache Invalidation:**
- Invalidate on property create/update/delete
- Pattern: `redis.delete_pattern('properties:list:*')`

---

## Recommendations

### Overall Strategy for US-023

**1. Pre-Requisites (MUST complete first):**
- ✅ Decide on i18n approach (implement US-021 or skip for MVP)
- ✅ Create Property V2 migration (TASK-XXX: Migrate to Property V2 schema)
- ✅ Build import scripts (TASK-YYY: Import properties from old database)

**2. Implementation Order:**
```
TASK-013 (US-023):
  Phase 1: Backend
    - Property V2 API endpoint (GET /api/v1/properties with pagination)
    - PropertyService with pagination logic
    - Redis caching
  
  Phase 2: Frontend
    - PropertyCard component (display single property)
    - PropertyGrid component (responsive grid layout)
    - Pagination component (page numbers)
    - Homepage integration
  
  Phase 3: Import
    - Run import script (import all properties from old DB)
    - Verify data integrity
    - Test performance with real data
  
  Phase 4: Testing
    - E2E tests (property listing, pagination, filtering)
    - Performance tests (response time, cache hit ratio)
    - Cross-browser tests
```

### Import Script Recommendations

**Preferred Approach:** Direct database migration (Phase 2 from US-016)
- **Why?** Faster, no intermediate JSON files, built-in resume capability
- **When?** Production-ready after testing with export/import approach

**Development/Testing Approach:** Export → Transform → Import (Phase 1 from US-016)
- **Why?** Safer, easier to debug, repeatable
- **When?** During TASK-013 development

**Script Stack:**
```python
# Technology choices
asyncpg        # Async PostgreSQL driver (fast bulk insert)
supabase-py    # Supabase REST API client (export)
pydantic       # Data validation (transformation)
psycopg2       # Sync PostgreSQL driver (server-side cursors)
click          # CLI interface (script arguments)
PyYAML         # Config file parsing
```

### JSONB Localization Recommendations

**Strategy:** Hybrid approach
- **Main content (title, description):** Store in `bestays_property_translations` table
- **JSONB structured data (amenities, policies):** Store IDs only, translate in frontend

**Example:**
```json
// Database (JSONB) - Store IDs only
{
  "amenities": {
    "interior": ["air_conditioning", "wifi", "kitchen_appliances"],
    "exterior": ["private_pool", "garden"]
  }
}

// Frontend translation catalogue
const amenityLabels = {
  en: {
    "air_conditioning": "Air Conditioning",
    "wifi": "WiFi",
    "private_pool": "Private Pool"
  },
  th: {
    "air_conditioning": "เครื่องปรับอากาศ",
    "wifi": "ไวไฟ",
    "private_pool": "สระว่ายน้ำส่วนตัว"
  }
};

// Render with locale
{property.amenities.interior.map(id => amenityLabels[locale][id])}
```

**Benefits:**
- Smaller database size (IDs vs full text)
- Consistent translations across properties
- Easy to add new languages (just update frontend catalogue)

**Trade-offs:**
- Requires frontend translation catalogue
- Slightly more complex rendering logic

### Grid Performance Recommendations

**For Homepage (US-023):**
```
Display: 24 properties (4 cols × 6 rows on desktop)
Pagination: 1, 2, 3, ... 10 (max 10 pages = 240 properties)
Filters: transaction_type (sale/rent), property_type (villa/condo/etc.)
Sort: listing_priority DESC, created_at DESC
```

**Responsive Grid:**
```css
/* Tailwind CSS classes */
grid grid-cols-1        /* Mobile: 1 column */
md:grid-cols-2          /* Tablet: 2 columns */
lg:grid-cols-3          /* Desktop: 3 columns */
xl:grid-cols-4          /* Large desktop: 4 columns */
gap-6                   /* Spacing between cards */
```

**Image Optimization:**
```
Format: WebP (with JPEG fallback)
Sizes: 
  - Thumbnail: 400x300 (property card)
  - Medium: 800x600 (property detail)
  - Large: 1200x900 (lightbox)
CDN: Cloudflare R2 (low cost, fast)
Lazy Loading: Native browser (loading="lazy")
```

---

## Constraints & Gotchas

### Critical Blockers

**1. i18n Implementation NOT Done**
- US-021 is documented but NOT implemented
- Frontend routing structure needs refactor (/ → /[lang]/)
- Backend content API needs locale parameter
- Decision required: Skip i18n for US-023 MVP or implement US-021 first?

**2. Property V2 Schema NOT Migrated**
- Current property model is basic (no JSONB fields)
- Alembic migration required (50+ new columns)
- Indexes must be created (especially GIN for JSONB)
- Timeline: ~0.5 days

**3. No Import Scripts Yet**
- Must create all 4 migration scripts (export, transform, import, direct)
- Config file required (Supabase credentials, batch sizes)
- Testing required (validate transformation correctness)
- Timeline: ~2 days

### Technical Gotchas

**1. JSONB Query Performance**
- ❌ **Wrong:** `WHERE physical_specs::text LIKE '%bedrooms%'` (full table scan)
- ✅ **Right:** `WHERE physical_specs->'rooms'->>'bedrooms' = '3'` (uses GIN index)

**2. Translation Table JOINs**
```sql
-- SLOW: N+1 queries
SELECT * FROM bestays_properties_v2;
-- Then for each property:
SELECT * FROM bestays_property_translations WHERE property_id = ?

-- FAST: Single query with JSON aggregation
SELECT 
  p.*,
  json_object_agg(
    t.field || '_' || t.lang_code, t.value
  ) as translations
FROM bestays_properties_v2 p
LEFT JOIN bestays_property_translations t ON t.property_id = p.id
WHERE p.is_published = true
GROUP BY p.id;
```

**3. Image URLs from Old System**
- Old system uses Supabase Storage (URLs: `https://xxx.supabase.co/storage/v1/...`)
- Options:
  - Keep Supabase storage active (pay subscription)
  - Migrate images to Cloudflare R2 first (2-4 hours for 1000 images)
- **Recommendation:** Keep Supabase storage for US-023, migrate images later

**4. Soft Delete Handling**
- Old schema has `deleted_at` column (soft delete)
- Import scripts MUST filter: `WHERE deleted_at IS NULL`
- New API MUST always filter: `WHERE deleted_at IS NULL`

**5. User ID Migration**
- Old: `created_by UUID REFERENCES auth.users(id)` (Supabase Auth)
- New: `created_by INTEGER REFERENCES users(id)` (Clerk)
- **Resolution:** Map all old properties to default admin user during import

### Data Integrity Risks

**1. Missing Required Fields**
- Not all properties may have `title` (nullable in old schema)
- Not all properties may have `transaction_type` (required in new schema)
- **Mitigation:** Validation script before import, provide defaults

**2. Invalid JSONB Structures**
- Old data may have inconsistent JSONB schemas
- **Mitigation:** Pydantic validation during transformation, log errors

**3. Broken Image URLs**
- Some images may have been deleted from Supabase storage
- **Mitigation:** Validate URLs during import, use placeholder for broken images

---

## File Paths Summary

### Old Database Schema (Reference)
- **Property V2 DDL:** `/Users/solo/Projects/_repos/react-workspace/src/apps/bestays-web/db/sql-2/2.property2-tables.sql`
- **Property V2 Types:** `/Users/solo/Projects/_repos/react-workspace/src/apps/bestays-web/entities/property2/types/property.ts`
- **Enums:** `/Users/solo/Projects/_repos/react-workspace/src/apps/bestays-web/db/sql-2/1.property2-enums.sql`

### Current Codebase (New System)
- **Property Model (Basic):** `/Users/solo/Projects/_repos/bestays/apps/server/src/server/models/property.py`
- **US-021 Spec (i18n):** `/Users/solo/Projects/_repos/bestays/.sdlc-workflow/stories/homepage/US-021-locale-switching.md`
- **US-016 Spec (Property V2 Migration):** `/Users/solo/Projects/_repos/bestays/.sdlc-workflow/stories/properties/US-016-property-migration-design.md`

### Files to Create (TASK-013 Planning Phase)
```
apps/server/scripts/migration/
  ├── __init__.py
  ├── supabase_export.py       (Export from old DB)
  ├── transform_properties.py  (Transform schema)
  ├── import_properties.py     (Import to new DB)
  └── supabase_direct.py       (Production migration)

apps/server/alembic/versions/
  └── xxx_upgrade_to_property_v2.py  (Schema migration)

apps/frontend/src/lib/components/
  ├── PropertyCard.svelte      (Single property card)
  ├── PropertyGrid.svelte      (Grid layout)
  └── Pagination.svelte        (Pagination controls)

apps/frontend/src/routes/
  └── properties/
      ├── +page.server.ts      (SSR data loading)
      └── +page.svelte         (Property listing page)

config/
  └── migration.yaml           (Migration config)
```

---

**End of Research Findings**

**Next Steps:**
1. Review findings with user
2. Decide on i18n approach (implement US-021 or skip)
3. Create TASK-013 planning document based on these findings
4. Estimate timeline with dependencies

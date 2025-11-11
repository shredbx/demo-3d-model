# Trade-offs Analysis: Property V2 Architecture

**TASK:** TASK-013
**Story:** US-023
**Date:** 2025-11-09
**Author:** Claude Code (Coordinator)

---

## Overview

This document analyzes all major architectural decisions for Property V2 schema, documenting trade-offs, alternatives considered, and conditions for re-evaluation. This serves as the "memory print" for future decisions.

---

## Decision 1: Hybrid Localization Strategy

### Decision Made

**Three-layer hybrid approach:**
1. **Properties table** - Queryable data (prices, types) in columns + JSONB
2. **property_translations table** - Localized text (title, description)
3. **Frontend dictionaries** - Static labels (amenity names, UI text)

### Alternatives Considered

#### Alternative A: Full JSONB Localization

```json
{
  "title": {
    "en": "Modern Villa",
    "th": "วิลล่าโมเดิร์น"
  },
  "description": {
    "en": "Beautiful villa...",
    "th": "วิลล่าสวยงาม..."
  },
  "amenities": {
    "en": ["Swimming Pool", "WiFi"],
    "th": ["สระว่ายน้ำ", "ไวไฟ"]
  }
}
```

**Pros:**
- ✅ Simple: All data in one table
- ✅ No JOINs needed
- ✅ Easy to add locale (just add key to JSONB)

**Cons:**
- ❌ Bloated JSONB (duplicate structure per locale)
- ❌ Hard to query across locales (no partial indexes on nested JSONB)
- ❌ Hard to validate (Pydantic schemas complex)
- ❌ Harder to manage translations (no dedicated translation UI)
- ❌ Amenity labels duplicated per property (not DRY)

**Why Rejected:**
- JSONB size grows linearly with locales (3 locales = 3× data)
- Can't efficiently query "all properties with Thai translations"
- Translation management becomes app logic, not database feature

---

#### Alternative B: Full Relational (No JSONB)

```sql
CREATE TABLE property_rooms (
    property_id UUID,
    bedrooms INTEGER,
    bathrooms INTEGER,
    ...
);

CREATE TABLE property_sizes (
    property_id UUID,
    usable_area_sqm DECIMAL,
    land_area_sqm DECIMAL,
    ...
);

CREATE TABLE property_amenities (
    property_id UUID,
    amenity_id VARCHAR,
    PRIMARY KEY (property_id, amenity_id)
);

-- 10+ more tables for policies, images, etc.
```

**Pros:**
- ✅ Fully normalized
- ✅ Schema enforced at database level
- ✅ Easy to query individual fields
- ✅ Best for complex relationships

**Cons:**
- ❌ Too many tables (10+)
- ❌ Too many JOINs per query (10+ JOINs for full property)
- ❌ Rigid schema (adding new property attribute = migration)
- ❌ Overkill for startup scale (< 100k properties)
- ❌ Poor fit for semi-structured data (property specs vary by type)

**Why Rejected:**
- Property data is semi-structured (villa has land_area, condo has floor number)
- Adding new attribute (e.g., "smart_home_features") requires migration
- Query complexity explodes (10+ JOINs + subqueries)
- Maintenance burden high for small team

---

### Chosen Approach: Hybrid

**Why This Works:**

1. **Queryable Data → Columns**
   - Prices, types, publication status in dedicated columns
   - Fast B-tree indexes for exact matches
   - Efficient sorting (listing_priority, created_at)

2. **Semi-Structured Data → JSONB**
   - Flexible schema (add new specs without migration)
   - GIN indexes for containment queries
   - Native validation via JSON Schema (future)

3. **Translatable Text → Translation Table**
   - Normalized (no duplication)
   - Efficient JOINs (1 LEFT JOIN, not 10+)
   - Easy to manage (dedicated translation UI)
   - Extensible (add locale = add rows, not schema change)

4. **Static Labels → Frontend**
   - Amenity/policy names rarely change
   - Frontend caches translations
   - No database queries for UI labels

**When This Breaks Down:**

1. **Scale > 100k properties**
   - Consider partitioning (by transaction_type or country)
   - Consider caching layer (Redis)

2. **Locales > 10**
   - Translation table grows large (10k props × 10 locales × 6 fields = 600k rows)
   - Consider translation service (e.g., Phrase, Lokalise)

3. **Complex Geospatial Queries**
   - Need PostGIS extension
   - Store coordinates in dedicated GEOGRAPHY column

4. **Real-Time Collaboration**
   - Need OT/CRDT for concurrent editing
   - Current architecture has last-write-wins

---

## Decision 2: Separate Translation Tables vs JSONB Localization

### Decision Made

**Separate `property_translations` table:**

```sql
CREATE TABLE property_translations (
    property_id UUID,
    locale VARCHAR(5),
    field VARCHAR(100),  -- 'title', 'description', etc.
    value TEXT,
    UNIQUE (property_id, locale, field)
);
```

### Alternatives Considered

#### Alternative: JSONB Column in Properties Table

```sql
ALTER TABLE properties ADD COLUMN translations JSONB;

-- Data:
{
  "th": {
    "title": "วิลล่าโมเดิร์น",
    "description": "..."
  },
  "ja": {
    "title": "モダンヴィラ",
    "description": "..."
  }
}
```

**Pros:**
- ✅ No JOIN needed
- ✅ Simpler queries (single table)
- ✅ Flexible structure

**Cons:**
- ❌ Hard to query "all properties missing Thai title"
- ❌ Hard to enforce required fields per locale
- ❌ Can't index specific translation fields
- ❌ Translation management harder (nested JSONB updates)

### Why Separate Table Wins

1. **Queryability:**
   ```sql
   -- Find properties missing Thai translation
   SELECT p.id FROM properties p
   LEFT JOIN property_translations t ON t.property_id = p.id AND t.locale = 'th' AND t.field = 'title'
   WHERE t.id IS NULL;
   ```

2. **Indexing:**
   ```sql
   -- Index on (property_id, locale) for fast lookups
   CREATE INDEX idx_property_translations_lookup ON property_translations (property_id, locale);
   ```

3. **Validation:**
   ```sql
   -- Enforce locale format with CHECK constraint
   CHECK (locale ~ '^[a-z]{2}(-[A-Z]{2})?$')
   ```

4. **Management:**
   - Dedicated translation UI can query table directly
   - Easy bulk updates (UPDATE property_translations WHERE locale = 'th')
   - Clear audit trail (updated_at per translation)

**When to Revisit:**

- If JOINs become bottleneck (> 500ms)
- If translation management moves to external service
- If locales become deeply nested (e.g., regional dialects)

---

## Decision 3: Store Amenity IDs vs Full Text

### Decision Made

**Store amenity IDs in JSONB:**

```json
{
  "amenities": {
    "interior": ["air_conditioning", "wifi"],
    "exterior": ["pool", "garden"]
  }
}
```

**Translate IDs in service layer:**

```python
amenity_labels = {
    "air_conditioning": {"en": "Air Conditioning", "th": "เครื่องปรับอากาศ"},
    "wifi": {"en": "WiFi", "th": "ไวไฟ"}
}
```

### Alternative: Store Full Text

```json
{
  "amenities": {
    "interior": ["Air Conditioning", "WiFi"],
    "exterior": ["Swimming Pool", "Garden"]
  }
}
```

**Pros:**
- ✅ No translation lookup needed
- ✅ Simpler queries

**Cons:**
- ❌ Not localized (always EN)
- ❌ Typos ("Air Conditioner" vs "Air Conditioning")
- ❌ Hard to change labels globally (update 10k properties)
- ❌ Bloated storage (full text vs short ID)

### Why IDs Win

1. **DRY Principle:**
   - Amenity label stored once in `amenity_translations`
   - Update label = update 1 row (not 10k properties)

2. **Localization:**
   - Frontend translates based on user locale
   - No duplicate amenity text per locale

3. **Consistency:**
   - Enforced by foreign key (can't use invalid amenity ID)
   - No typos

4. **Storage:**
   - "air_conditioning" = 17 bytes
   - "Air Conditioning" = 17 bytes (EN) + "เครื่องปรับอากาศ" = 51 bytes (TH)
   - 3× savings with ID approach

**When to Revisit:**

- If frontend translation becomes bottleneck (cache in Redis)
- If amenities become user-generated (need full-text search)

---

## Decision 4: Add Embedding Columns Now (Unused)

### Decision Made

**Add `description_embedding_en` and `description_embedding_th` columns in initial migration:**

```sql
description_embedding_en vector(1536),
description_embedding_th vector(1536)
```

**But DON'T create HNSW indexes yet (reserved for US-024).**

### Alternative: Add Columns Later

**Wait until semantic search is implemented, then:**

```sql
ALTER TABLE properties ADD COLUMN description_embedding_en vector(1536);
CREATE INDEX idx_properties_embedding_en ON properties USING hnsw (description_embedding_en vector_cosine_ops);
```

**Pros:**
- ✅ Don't add unused columns
- ✅ Migration is smaller/faster now

**Cons:**
- ❌ Future migration required (ALTER TABLE + backfill embeddings)
- ❌ Downtime during backfill (10k properties × 2 locales × API calls)
- ❌ Two separate migrations to track

### Why Add Now

1. **Future-Ready:**
   - Schema prepared for semantic search
   - No migration needed when feature is ready

2. **Backfill Strategy:**
   - Columns nullable → can be populated incrementally
   - Generate embeddings async (background job)
   - No downtime

3. **Storage Cost:**
   - Empty vector columns cost minimal space (nullable)
   - With data: 1536 × 4 bytes × 2 = 12 KB per property
   - 10k properties = 120 MB (acceptable)

4. **Migration Simplicity:**
   - One migration adds everything
   - Easier to rollback (drop all at once)

**When to Revisit:**

- If storage cost becomes issue (unlikely, vectors compress well)
- If embedding strategy changes (e.g., use 768-dim model instead of 1536)

---

## Decision 5: Specific Indexes Chosen

### Decision Made

**Create these indexes:**

1. **Composite:** `(transaction_type, rent_price, sale_price, lease_price)`
2. **GIN:** `amenities jsonb_path_ops`
3. **GIN:** `physical_specs jsonb_path_ops`
4. **Partial:** `is_published = true AND deleted_at IS NULL`

**NOT create:**
- Individual indexes on `rent_price`, `sale_price` (composite is sufficient)
- Full-text search index (wait for user feedback)
- Geospatial index (PostGIS not needed yet)

### Rationale

#### Composite Index on Prices

**Why:**
- Most queries filter by transaction_type + price range
- Single composite index covers both

**Alternative:** Separate indexes

```sql
CREATE INDEX idx_properties_rent_price ON properties (rent_price);
CREATE INDEX idx_properties_sale_price ON properties (sale_price);
```

**Rejected:**
- PostgreSQL can't use multiple indexes efficiently for OR queries
- Composite index is more selective (transaction_type filters first)

---

#### GIN `jsonb_path_ops` vs `jsonb_ops`

**Chosen:** `jsonb_path_ops`

**Why:**
- Smaller index (30% less space)
- Faster for containment queries (`@>` operator)
- We only use containment (no key existence checks)

**Alternative:** `jsonb_ops`

**When to use:**
- If we need `?` operator (key existence)
- If we need `?|` operator (any key exists)

**Current usage:**

```sql
-- Supported by jsonb_path_ops
WHERE amenities->'interior' @> '["wifi"]'

-- NOT supported by jsonb_path_ops (would need jsonb_ops)
WHERE amenities ? 'interior'
```

---

#### Partial Indexes

**Why:**
- 80% of queries filter published, non-deleted properties
- Partial index is smaller (only indexes subset)
- Faster queries (smaller index to scan)

**Alternative:** Full indexes

```sql
CREATE INDEX idx_properties_transaction_price ON properties (transaction_type, rent_price, ...);
-- Without WHERE clause
```

**Trade-off:**
- Admin queries for unpublished/deleted properties won't use index
- Acceptable: Admin queries are infrequent, can scan full table

---

## Decision 6: Soft Delete vs Hard Delete

### Decision Made

**Soft delete with `deleted_at` column:**

```sql
deleted_at TIMESTAMP WITH TIME ZONE
```

**Delete operation:**

```python
property.deleted_at = datetime.utcnow()
db.commit()
```

### Alternative: Hard Delete

```python
db.delete(property)
db.commit()
```

**Pros:**
- ✅ Truly removes data (GDPR compliance)
- ✅ Simpler queries (no need to filter deleted_at)
- ✅ Smaller table size

**Cons:**
- ❌ No recovery (accidental delete = data loss)
- ❌ No audit trail (who deleted? when?)
- ❌ Breaks foreign keys (need ON DELETE CASCADE everywhere)

### Why Soft Delete Wins

1. **Recoverability:**
   - User can "undelete" property
   - Admin can audit deleted properties

2. **Audit Trail:**
   - See when property was deleted
   - See who deleted (if we track deleted_by)

3. **Data Integrity:**
   - Bookings/inquiries still reference property
   - Historical data preserved

4. **Query Impact:**
   - Add `WHERE deleted_at IS NULL` to all queries
   - Mitigated by partial indexes

**When to Hard Delete:**

- Scheduled cleanup job (delete properties older than 1 year)
- User requests data deletion (GDPR right to be forgotten)

---

## Decision 7: Price Storage as BIGINT (Satang/Cents)

### Decision Made

**Store prices in smallest currency unit (satang for THB, cents for USD):**

```sql
rent_price BIGINT  -- 3000000 = 30,000 THB
```

**Display:**

```python
display_price = rent_price / 100  # 3000000 / 100 = 30000 THB
```

### Alternative: DECIMAL/NUMERIC

```sql
rent_price DECIMAL(12, 2)  -- 30000.00 THB
```

**Pros:**
- ✅ Matches display format
- ✅ No division needed

**Cons:**
- ❌ Floating-point errors in calculations
- ❌ Harder to work with in most languages (Decimal type vs int)
- ❌ Larger storage (12 bytes vs 8 bytes)

### Why BIGINT Wins

1. **Precision:**
   - No rounding errors (integer arithmetic)
   - Consistent with payment APIs (Stripe, PayPal use cents)

2. **Performance:**
   - Integer comparisons faster than decimal
   - Smaller indexes

3. **Range Queries:**
   ```sql
   WHERE rent_price BETWEEN 2000000 AND 5000000
   -- Integer comparison (fast)
   ```

4. **Multi-Currency:**
   - Japanese Yen has no subunit (¥1000 = 1000 smallest unit)
   - BIGINT handles all currencies consistently

**Conversion:**

```python
# Backend → Frontend
def to_display_price(satang: int, currency: str) -> float:
    if currency == 'JPY':
        return satang  # No subunit
    return satang / 100  # THB, USD, EUR, etc.

# Frontend → Backend
def to_satang(price: float, currency: str) -> int:
    if currency == 'JPY':
        return int(price)
    return int(price * 100)
```

---

## Decision 8: JSONB Structure for Physical Specs

### Decision Made

**Nested JSONB with categories:**

```json
{
  "rooms": {"bedrooms": 3, "bathrooms": 2},
  "sizes": {"usable_area_sqm": 180.5},
  "floors": {"total_floors": 2}
}
```

### Alternative: Flat JSONB

```json
{
  "bedrooms": 3,
  "bathrooms": 2,
  "usable_area_sqm": 180.5,
  "total_floors": 2
}
```

**Pros:**
- ✅ Simpler queries: `physical_specs->>'bedrooms'`
- ✅ Flatter structure

**Cons:**
- ❌ No categorization (rooms vs sizes)
- ❌ Name collisions (what if we add "rooms" as count of total rooms?)
- ❌ Harder to validate (no clear groups)

### Why Nested Wins

1. **Clarity:**
   - `rooms.bedrooms` vs `bedrooms` (more descriptive)
   - Clear groups (rooms, sizes, floors)

2. **Extensibility:**
   - Add new room type: `rooms.storage_rooms`
   - Add new size: `sizes.balcony_area_sqm`
   - No name collisions

3. **Validation:**
   ```python
   class PhysicalSpecs(BaseModel):
       rooms: Optional[Rooms]
       sizes: Optional[Sizes]
       floors: Optional[Floors]
   ```

4. **Frontend Rendering:**
   - Group fields by category in UI
   - "Rooms" section, "Sizes" section

**Query Impact:**

```sql
-- Flat
WHERE physical_specs->>'bedrooms' = '3'

-- Nested
WHERE physical_specs->'rooms'->>'bedrooms' = '3'
-- Only 1 extra operator, negligible performance difference
```

---

## When to Revisit This Architecture

### Triggers for Re-evaluation

| Trigger | Threshold | Action |
|---------|-----------|--------|
| Property count | > 100k | Consider partitioning |
| Query time | > 500ms consistently | Add caching layer (Redis) |
| Locale count | > 10 | Consider translation service (Phrase, Lokalise) |
| Database size | > 100 GB | Review JSONB vs relational |
| Translation management | Becomes bottleneck | Build dedicated translation UI |
| Geospatial queries | Needed | Add PostGIS extension |
| Real-time collaboration | Needed | Implement OT/CRDT |
| Multi-tenancy | Needed | Schema-per-tenant or row-level security |

### Metrics to Monitor

**Weekly:**
```sql
-- Average query time
SELECT mean_exec_time FROM pg_stat_statements WHERE query LIKE '%properties%';

-- Index usage
SELECT idx_scan FROM pg_stat_user_indexes WHERE tablename = 'properties';

-- Table size
SELECT pg_size_pretty(pg_total_relation_size('properties'));
```

**Monthly:**
```sql
-- Index bloat
SELECT * FROM pgstattuple('idx_properties_amenities');

-- Cache hit ratio
SELECT * FROM pg_statio_user_tables WHERE relname = 'properties';
```

---

## Summary of Trade-offs

| Decision | Chosen | Alternative | Why Chosen | When to Revisit |
|----------|--------|-------------|------------|-----------------|
| Localization | Hybrid (table + JSONB) | Full JSONB | Balance query speed + flexibility | > 10 locales |
| Translations | Separate table | JSONB column | Better queryability | JOINs > 500ms |
| Amenity Storage | IDs | Full text | DRY, localized, consistent | User-generated amenities |
| Embedding Columns | Add now (nullable) | Add later | Future-ready, no backfill | Storage cost issue |
| Indexes | Composite + GIN | Individual B-tree | Optimized for query patterns | Query patterns change |
| Delete Strategy | Soft delete | Hard delete | Recoverability, audit | GDPR requests |
| Price Storage | BIGINT (satang) | DECIMAL | Precision, performance | Never (standard) |
| JSONB Structure | Nested | Flat | Clarity, extensibility | Name collisions |

---

## References

- System Design: `system-design.md`
- Data Model: `data-model-spec.md`
- Indexing Strategy: `indexing-strategy.md`
- PostgreSQL JSONB Best Practices: https://www.postgresql.org/docs/current/datatype-json.html
- Localization Patterns: https://www.postgresql.org/docs/current/locale.html

---

**This document is living documentation. Update when:**
- New architectural decisions are made
- Performance issues trigger changes
- Scale thresholds are crossed
- User feedback changes requirements

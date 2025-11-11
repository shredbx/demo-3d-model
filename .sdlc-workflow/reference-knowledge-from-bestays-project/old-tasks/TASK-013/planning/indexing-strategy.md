# Indexing Strategy: Property V2 Schema

**TASK:** TASK-013
**Story:** US-023
**Date:** 2025-11-09
**Author:** Claude Code (Coordinator)

---

## Overview

This document defines all indexes for the Property V2 schema, optimized for common query patterns. All indexes are production-ready and designed for 10k-100k property scale.

**Index Types:**
1. **B-tree** - Exact matches, range queries, sorting
2. **GIN** - JSONB containment, array operations
3. **HNSW** - Vector similarity (pgvector, future)
4. **Composite** - Multi-column queries

---

## Index Definitions

### Properties Table Indexes

#### 1. Primary Key Index (Automatic)

```sql
-- Created automatically with PRIMARY KEY constraint
CREATE UNIQUE INDEX properties_pkey ON properties USING btree (id);
```

**Purpose:** Point lookups by UUID
**Query Pattern:** `WHERE id = 'uuid'`
**Expected Performance:** < 5ms

---

#### 2. Transaction Type + Price Index

```sql
CREATE INDEX idx_properties_transaction_price ON properties USING btree (
    transaction_type,
    rent_price,
    sale_price,
    lease_price
) WHERE is_published = true AND deleted_at IS NULL;
```

**Purpose:** Filter by transaction type and price range
**Query Pattern:**
```sql
WHERE transaction_type = 'rent'
  AND rent_price BETWEEN 2000000 AND 5000000
  AND is_published = true
  AND deleted_at IS NULL
```

**Expected Performance:** < 50ms for 24 results
**Partial Index:** Only published, non-deleted properties
**Size Estimate:** ~2 MB for 10k properties

---

#### 3. Property Type Index

```sql
CREATE INDEX idx_properties_type ON properties USING btree (property_type)
WHERE is_published = true AND deleted_at IS NULL;
```

**Purpose:** Filter by property type (villa, condo, etc.)
**Query Pattern:** `WHERE property_type = 'villa'`
**Expected Performance:** < 20ms
**Size Estimate:** ~500 KB

---

#### 4. Publication Status + Priority Index

```sql
CREATE INDEX idx_properties_listing ON properties USING btree (
    is_published,
    listing_priority DESC,
    created_at DESC
) WHERE deleted_at IS NULL;
```

**Purpose:** Default listing order (featured first, then newest)
**Query Pattern:**
```sql
WHERE is_published = true AND deleted_at IS NULL
ORDER BY listing_priority DESC, created_at DESC
```

**Expected Performance:** < 100ms for first page
**Size Estimate:** ~1 MB
**Note:** DESC index for efficient reverse sorting

---

#### 5. Created By Index

```sql
CREATE INDEX idx_properties_created_by ON properties USING btree (created_by)
WHERE deleted_at IS NULL;
```

**Purpose:** Find all properties created by a user
**Query Pattern:** `WHERE created_by = user_id`
**Use Case:** User dashboard (my listings)
**Expected Performance:** < 50ms
**Size Estimate:** ~500 KB

---

#### 6. Soft Delete Index

```sql
CREATE INDEX idx_properties_deleted_at ON properties USING btree (deleted_at)
WHERE deleted_at IS NOT NULL;
```

**Purpose:** Find soft-deleted properties (admin cleanup)
**Query Pattern:** `WHERE deleted_at IS NOT NULL`
**Partial Index:** Only deleted properties (small)
**Expected Performance:** < 10ms
**Size Estimate:** < 100 KB (few deleted properties)

---

### JSONB Indexes (GIN)

#### 7. Physical Specs Index

```sql
CREATE INDEX idx_properties_physical_specs ON properties USING gin (physical_specs jsonb_path_ops);
```

**Purpose:** Query room counts, sizes, furnishing
**Query Patterns:**
```sql
-- Bedroom count
WHERE physical_specs->'rooms'->>'bedrooms' = '3'

-- Usable area range
WHERE (physical_specs->'sizes'->>'usable_area_sqm')::numeric >= 100

-- Fully furnished
WHERE physical_specs @> '{"furnishing": "fully_furnished"}'
```

**Expected Performance:** < 100ms
**Index Size:** ~5 MB for 10k properties
**Operator:** `jsonb_path_ops` (smaller, faster for containment)

---

#### 8. Amenities Index

```sql
CREATE INDEX idx_properties_amenities ON properties USING gin (amenities jsonb_path_ops);
```

**Purpose:** Find properties with specific amenities
**Query Patterns:**
```sql
-- Has WiFi
WHERE amenities->'interior' @> '["wifi"]'

-- Has both pool and garden
WHERE amenities->'exterior' @> '["pool", "garden"]'

-- Has any interior amenity
WHERE amenities ? 'interior'
```

**Expected Performance:** < 80ms
**Index Size:** ~4 MB
**Note:** Most common filter after price

---

#### 9. Policies Index

```sql
CREATE INDEX idx_properties_policies ON properties USING gin (policies jsonb_path_ops);
```

**Purpose:** Filter by lease terms, house rules
**Query Patterns:**
```sql
-- Pets allowed
WHERE policies->'house_rules' @> '{"pets_allowed": true}'

-- Lease duration exactly 12 months
WHERE policies->'lease_terms' @> '{"lease_duration_months": 12}'
```

**Expected Performance:** < 100ms
**Index Size:** ~3 MB

---

#### 10. Location Details Index

```sql
CREATE INDEX idx_properties_location_details ON properties USING gin (location_details jsonb_path_ops);
```

**Purpose:** Filter by province, district, postal code
**Query Patterns:**
```sql
-- Properties in Bangkok
WHERE location_details->'administrative' @> '{"province_id": "bangkok"}'

-- Properties near BTS
WHERE location_details->'nearby_landmarks' @> '[{"type": "bts"}]'
```

**Expected Performance:** < 80ms
**Index Size:** ~4 MB

---

### Array Indexes

#### 11. Tags Index

```sql
CREATE INDEX idx_properties_tags ON properties USING gin (tags);
```

**Purpose:** Filter by tags (pet-friendly, near-bts, luxury)
**Query Patterns:**
```sql
-- Has "pet-friendly" tag
WHERE 'pet-friendly' = ANY(tags)

-- Has multiple tags
WHERE tags @> ARRAY['luxury', 'near-bts']
```

**Expected Performance:** < 50ms
**Index Size:** ~2 MB

---

### Vector Indexes (Future - Reserved)

#### 12. English Description Embedding Index

```sql
-- DO NOT CREATE YET - Reserved for US-024 (Semantic Search)
CREATE INDEX idx_properties_embedding_en ON properties USING hnsw (description_embedding_en vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**Purpose:** Semantic search in English
**Query Pattern:**
```sql
ORDER BY description_embedding_en <=> query_embedding
LIMIT 24
```

**Expected Performance:** < 200ms for similarity search
**Index Size:** ~60 MB for 10k properties
**Parameters:**
- `m = 16` - Connections per layer (balance quality/speed)
- `ef_construction = 64` - Index build quality
- `vector_cosine_ops` - Cosine similarity (normalized embeddings)

**When to Create:** After semantic search implementation (US-024)

---

#### 13. Thai Description Embedding Index

```sql
-- DO NOT CREATE YET - Reserved for US-024
CREATE INDEX idx_properties_embedding_th ON properties USING hnsw (description_embedding_th vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**Purpose:** Semantic search in Thai
**Same parameters as English index**

---

### Property Translations Table Indexes

#### 14. Translation Lookup Index

```sql
CREATE INDEX idx_property_translations_lookup ON property_translations USING btree (
    property_id,
    locale
);
```

**Purpose:** Fetch all translations for a property + locale
**Query Pattern:**
```sql
WHERE property_id = 'uuid' AND locale = 'th'
```

**Expected Performance:** < 10ms
**Size Estimate:** ~3 MB for 30k translations (10k × 3 locales)
**Note:** Unique constraint also creates index, but composite is faster

---

#### 15. Locale Index

```sql
CREATE INDEX idx_property_translations_locale ON property_translations USING btree (locale);
```

**Purpose:** Find all properties with translations in a locale
**Query Pattern:** `WHERE locale = 'th'`
**Use Case:** Admin - check translation coverage
**Expected Performance:** < 50ms
**Size Estimate:** ~1 MB

---

### Amenities Table Indexes

#### 16. Amenity Category Index

```sql
CREATE INDEX idx_amenities_category ON amenities USING btree (category)
WHERE is_active = true;
```

**Purpose:** List amenities by category (interior, exterior)
**Query Pattern:** `WHERE category = 'interior' AND is_active = true`
**Expected Performance:** < 5ms
**Size Estimate:** < 100 KB (small table)

---

### Policies Table Indexes

#### 17. Policy Category Index

```sql
CREATE INDEX idx_policies_category ON policies USING btree (category)
WHERE is_active = true;
```

**Purpose:** List policies by category (lease_terms, house_rules)
**Query Pattern:** `WHERE category = 'lease_terms' AND is_active = true`
**Expected Performance:** < 5ms
**Size Estimate:** < 100 KB (small table)

---

## Index Usage Patterns

### Most Common Queries

#### 1. Property Listing (Homepage/Search)

```sql
-- Indexes Used:
-- - idx_properties_transaction_price (filter)
-- - idx_properties_physical_specs (bedroom count)
-- - idx_properties_amenities (WiFi, pool)
-- - idx_properties_listing (sort)
-- - idx_property_translations_lookup (translations)

SELECT p.*, json_object_agg(t.field, t.value) as translations
FROM properties p
LEFT JOIN property_translations t ON t.property_id = p.id AND t.locale = 'th'
WHERE
    p.is_published = true
    AND p.deleted_at IS NULL
    AND p.transaction_type = 'rent'
    AND p.rent_price BETWEEN 2000000 AND 5000000
    AND p.physical_specs->'rooms'->>'bedrooms' = '3'
    AND p.amenities->'interior' @> '["wifi"]'
GROUP BY p.id
ORDER BY p.listing_priority DESC, p.created_at DESC
LIMIT 24 OFFSET 0;
```

**Expected Performance:** < 200ms
**Indexes Hit:** 4-5 indexes
**Optimization:** Composite index on (transaction_type, rent_price) is most selective

---

#### 2. Property Detail Page

```sql
-- Indexes Used:
-- - properties_pkey (primary lookup)
-- - idx_property_translations_lookup (translations)

SELECT p.*, json_object_agg(t.field, t.value) as translations
FROM properties p
LEFT JOIN property_translations t ON t.property_id = p.id AND t.locale = 'th'
WHERE p.id = 'uuid'
GROUP BY p.id;
```

**Expected Performance:** < 50ms
**Indexes Hit:** 2 indexes
**Optimization:** Simple point lookup

---

#### 3. User's Listings (My Properties)

```sql
-- Indexes Used:
-- - idx_properties_created_by (filter)
-- - idx_properties_listing (sort)

SELECT * FROM properties
WHERE created_by = user_id AND deleted_at IS NULL
ORDER BY listing_priority DESC, created_at DESC;
```

**Expected Performance:** < 50ms
**Indexes Hit:** 2 indexes

---

## Performance Expectations

### Query Performance Targets

| Query Type | Target | Acceptable | Investigate |
|------------|--------|------------|-------------|
| Point lookup (by ID) | < 10ms | < 50ms | > 100ms |
| Property listing (24 results) | < 100ms | < 200ms | > 500ms |
| Filtered search (3+ filters) | < 200ms | < 500ms | > 1000ms |
| User's properties | < 50ms | < 100ms | > 200ms |
| Translation fetch | < 10ms | < 50ms | > 100ms |

### Index Size Estimates

| Index | Size (10k props) | Size (100k props) | Type |
|-------|------------------|-------------------|------|
| B-tree (single column) | 500 KB | 5 MB | Small |
| B-tree (composite) | 1-2 MB | 10-20 MB | Medium |
| GIN (JSONB) | 3-5 MB | 30-50 MB | Large |
| HNSW (vector) | 60 MB | 600 MB | Very Large |
| **Total (no vectors)** | ~25 MB | ~250 MB | - |
| **Total (with vectors)** | ~145 MB | ~1.5 GB | - |

### Database Size Breakdown (10k properties)

```
Tables:          ~70 MB
Indexes:         ~25 MB (without vectors)
                ~145 MB (with vectors)
Total:          ~215 MB (production-ready)
```

---

## Index Maintenance Strategy

### Automatic Maintenance

```sql
-- Enable autovacuum (default: enabled)
ALTER TABLE properties SET (
    autovacuum_vacuum_scale_factor = 0.1,  -- Vacuum when 10% changed
    autovacuum_analyze_scale_factor = 0.05 -- Analyze when 5% changed
);

ALTER TABLE property_translations SET (
    autovacuum_vacuum_scale_factor = 0.2,
    autovacuum_analyze_scale_factor = 0.1
);
```

**Rationale:**
- Properties change frequently → aggressive autovacuum
- Translations are more stable → less aggressive

---

### Manual Maintenance

#### Weekly ANALYZE (Production)

```sql
-- Update query planner statistics
ANALYZE properties;
ANALYZE property_translations;
ANALYZE amenities;
ANALYZE policies;
```

**When to Run:** After bulk imports, schema changes
**Duration:** < 1 minute for 10k properties

---

#### Monthly REINDEX (If Needed)

```sql
-- Rebuild bloated indexes
REINDEX TABLE CONCURRENTLY properties;
```

**When to Run:**
- Index bloat > 30% (check with `pgstattuple`)
- Query performance degradation
- After major data churn

**Duration:** 5-10 minutes (CONCURRENTLY = no downtime)

---

### Monitoring Queries

#### Index Usage Statistics

```sql
-- Which indexes are actually used?
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,  -- Number of index scans
    idx_tup_read,  -- Tuples read from index
    idx_tup_fetch  -- Tuples fetched from table
FROM pg_stat_user_indexes
WHERE tablename IN ('properties', 'property_translations')
ORDER BY idx_scan DESC;
```

**Action:** Drop unused indexes (idx_scan = 0 after 1 month)

---

#### Index Bloat Check

```sql
-- Install pgstattuple extension first
CREATE EXTENSION IF NOT EXISTS pgstattuple;

-- Check index bloat
SELECT
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
    100 - avg_leaf_density as bloat_pct
FROM pg_statistic, pg_index, pgstatindex(indexrelid::text)
WHERE schemaname = 'public' AND tablename = 'properties';
```

**Action:** REINDEX if bloat > 30%

---

#### Cache Hit Ratio

```sql
-- Should be > 99% in production
SELECT
    'properties' as table,
    heap_blks_read + idx_blks_read as total_reads,
    heap_blks_hit + idx_blks_hit as cache_hits,
    ROUND(
        100.0 * (heap_blks_hit + idx_blks_hit) /
        NULLIF(heap_blks_hit + idx_blks_hit + heap_blks_read + idx_blks_read, 0),
        2
    ) as cache_hit_ratio
FROM pg_statio_user_tables
WHERE relname = 'properties';
```

**Action:** If < 95%, increase `shared_buffers` in PostgreSQL config

---

## Index Creation Order (For Migration)

**Create indexes AFTER inserting data for better performance:**

```sql
-- 1. Create tables (see migration-spec.md)

-- 2. Insert seed data (amenities, policies)

-- 3. Create indexes (in this order)
--    a. Small tables first (amenities, policies)
--    b. B-tree indexes (fast to build)
--    c. GIN indexes (slow to build)
--    d. Partial indexes (smaller, faster)

-- Estimated total build time: 5-10 minutes for 10k properties
```

---

## When to Add More Indexes

### Add Index If:

1. **Query appears in slow query log** (> 500ms)
2. **Sequential scans on large tables**
   ```sql
   -- Check with EXPLAIN ANALYZE
   EXPLAIN ANALYZE SELECT ...;
   -- If you see "Seq Scan on properties (cost=...)", add index
   ```
3. **New feature requires different query pattern**
4. **Cache hit ratio drops** (indicates too many disk reads)

### Don't Add Index If:

1. **Table is small** (< 1000 rows) - seq scan is fine
2. **Column has low cardinality** (few unique values)
3. **Index size > table size** (GIN indexes can be huge)
4. **Write performance is critical** (indexes slow INSERT/UPDATE)

---

## Future Optimizations

### When Properties > 100k

1. **Partitioning by transaction_type**
   ```sql
   -- Partition properties into rent, sale, lease tables
   CREATE TABLE properties_rent PARTITION OF properties FOR VALUES IN ('rent');
   ```

2. **Materialized views for common queries**
   ```sql
   CREATE MATERIALIZED VIEW properties_listing_cache AS
   SELECT p.*, json_object_agg(t.field, t.value) as translations
   FROM properties p
   LEFT JOIN property_translations t ON t.property_id = p.id
   GROUP BY p.id;

   REFRESH MATERIALIZED VIEW CONCURRENTLY properties_listing_cache;
   ```

3. **Full-text search index**
   ```sql
   -- For search by title/description
   CREATE INDEX idx_properties_fts ON properties USING gin (
       to_tsvector('english', title || ' ' || description)
   );
   ```

---

## Success Criteria

**Index Performance:**
- ✅ Property listing query < 200ms (24 results, 3+ filters)
- ✅ Point lookup < 50ms
- ✅ Translation fetch < 50ms
- ✅ All indexes used (verified via pg_stat_user_indexes)

**Index Health:**
- ✅ Index bloat < 20%
- ✅ Cache hit ratio > 95%
- ✅ No unused indexes (idx_scan > 0)
- ✅ Total index size < 30% of table size (excluding vectors)

**Monitoring:**
- ✅ Slow query log enabled
- ✅ pg_stat_statements extension installed
- ✅ Weekly ANALYZE scheduled
- ✅ Monthly bloat check scheduled

---

## References

- PostgreSQL Indexes: https://www.postgresql.org/docs/current/indexes.html
- GIN Indexes: https://www.postgresql.org/docs/current/gin.html
- pgvector HNSW: https://github.com/pgvector/pgvector#hnsw
- Index Maintenance: https://www.postgresql.org/docs/current/routine-reindex.html

---

**Next Document:** migration-spec.md (Alembic migration implementation)

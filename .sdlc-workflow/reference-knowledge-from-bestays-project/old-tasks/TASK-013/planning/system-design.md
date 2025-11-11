# System Design: Property V2 Schema with Hybrid Localization

**TASK:** TASK-013  
**Story:** US-023  
**Date:** 2025-11-09  
**Author:** Claude Code (Coordinator)

---

## Executive Summary

This document defines the system architecture for Property V2 schema migration, implementing a hybrid localization strategy that balances query performance, maintainability, and scalability.

**Key Architectural Decision:** Three-layer hybrid approach
1. **Properties table** - Queryable data (numbers, IDs) in columns and JSONB
2. **property_translations table** - Localized text (title, description, location names)
3. **Frontend dictionaries** - Static label translations (amenity names, field labels)

---

## Architecture Overview

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (SvelteKit)                  │
│  ┌────────────────┐  ┌──────────────────┐ ┌───────────────┐ │
│  │ Property Grid  │  │ Property Detail  │ │ LocaleSwitcher│ │
│  └────────┬───────┘  └────────┬─────────┘ └───────┬───────┘ │
│           │                   │                    │          │
│           └───────────────────┴────────────────────┘          │
│                               │                               │
│                    GET /api/v1/properties?locale=en          │
└───────────────────────────────┼───────────────────────────────┘
                                │
┌───────────────────────────────┼───────────────────────────────┐
│                        Backend (FastAPI)                      │
│                               │                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              PropertyService (Service Layer)           │  │
│  │  ┌────────────────────────────────────────────────┐   │  │
│  │  │ merge_property_with_translations(prop, locale) │   │  │
│  │  └────────────────────────────────────────────────┘   │  │
│  └───────────────┬──────────────────────┬────────────────┘  │
│                  │                      │                    │
│      ┌───────────▼────────┐  ┌─────────▼──────────┐        │
│      │   Property Model   │  │PropertyTranslation │         │
│      │   (SQLAlchemy)     │  │    Model           │         │
│      └───────────┬────────┘  └─────────┬──────────┘        │
└──────────────────┼──────────────────────┼────────────────────┘
                   │                      │
┌──────────────────┼──────────────────────┼────────────────────┐
│                Database (PostgreSQL + pgvector)              │
│                  │                      │                     │
│  ┌───────────────▼────────┐  ┌─────────▼──────────┐        │
│  │   properties table      │  │ property_          │         │
│  │   - id, rent_price      │  │  translations      │         │
│  │   - physical_specs JSONB│  │ - property_id      │         │
│  │   - amenities JSONB     │  │ - locale           │         │
│  │   - embeddings vector   │  │ - field, value     │         │
│  └─────────────────────────┘  └────────────────────┘        │
│                                                               │
│  Indexes: B-tree (rent_price), GIN (amenities),              │
│           HNSW (embeddings - future)                         │
└───────────────────────────────────────────────────────────────┘
```

---

## Entity-Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        properties                            │
├─────────────────────────────────────────────────────────────┤
│ id                    UUID (PK)                             │
│ title                 VARCHAR(255)  -- Fallback             │
│ description           TEXT          -- Fallback             │
│                                                              │
│ transaction_type      VARCHAR(20)   -- rent, sale, lease    │
│ property_type         VARCHAR(50)   -- villa, condo, etc.   │
│                                                              │
│ rent_price            BIGINT        -- Queryable            │
│ sale_price            BIGINT                                │
│ lease_price           BIGINT                                │
│ currency              VARCHAR(3)                            │
│                                                              │
│ physical_specs        JSONB         -- {rooms, sizes, ...}  │
│ location_details      JSONB         -- {coordinates, ...}   │
│ amenities             JSONB         -- {interior: [...]}    │
│ policies              JSONB         -- {lease_terms: {...}}│
│ contact_info          JSONB         -- {phone, email, ...}  │
│                                                              │
│ cover_image           JSONB                                 │
│ images                JSONB[]                               │
│ tags                  TEXT[]                                │
│                                                              │
│ is_published          BOOLEAN                               │
│ is_featured           BOOLEAN                               │
│ listing_priority      INTEGER                               │
│ deleted_at            TIMESTAMP TZ                          │
│                                                              │
│ description_embedding_en  vector(1536)  -- Future           │
│ description_embedding_th  vector(1536)  -- Future           │
│                                                              │
│ created_by            INTEGER FK → users.id                 │
│ updated_by            INTEGER FK → users.id                 │
│ created_at            TIMESTAMP TZ                          │
│ updated_at            TIMESTAMP TZ                          │
└────────┬────────────────────────────────────────────────────┘
         │
         │ 1:N
         │
         ▼
┌────────────────────────────────────────────────────────────┐
│                 property_translations                       │
├────────────────────────────────────────────────────────────┤
│ id                INTEGER (PK)                              │
│ property_id       UUID (FK → properties.id) ON DELETE CASCADE│
│ locale            VARCHAR(5)    -- 'en', 'th', 'en-US'     │
│ field             VARCHAR(100)  -- 'title', 'description'   │
│ value             TEXT           -- Localized text          │
│ created_at        TIMESTAMP TZ                             │
│ updated_at        TIMESTAMP TZ                             │
│                                                             │
│ UNIQUE(property_id, locale, field)                         │
└────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Property Listing with Localization

### Request Flow (GET /api/v1/properties?locale=th)

```
1. Frontend Request
   ↓
   GET /api/v1/properties?locale=th&page=1&per_page=24
   
2. FastAPI Endpoint
   ↓
   - Validate query parameters
   - Extract locale ('th')
   - Call PropertyService.list_properties(locale='th', ...)
   
3. PropertyService Layer
   ↓
   - Query properties table with filters
   - LEFT JOIN property_translations ON (property_id, locale='th')
   - Aggregate translations into single row per property
   - Apply pagination (LIMIT 24 OFFSET 0)
   
4. Database Query
   ↓
   SELECT 
     p.*,
     json_object_agg(
       t.field, t.value
     ) FILTER (WHERE t.locale = 'th') as translations
   FROM properties p
   LEFT JOIN property_translations t 
     ON t.property_id = p.id AND t.locale = 'th'
   WHERE p.is_published = true 
     AND p.deleted_at IS NULL
   GROUP BY p.id
   ORDER BY p.listing_priority DESC, p.created_at DESC
   LIMIT 24;
   
5. Service Layer (Merge Translations)
   ↓
   for property in properties:
       property.title = translations.get('title', property.title)  # Fallback to EN
       property.description = translations.get('description', property.description)
       property.location_province = translations.get('location_province')
       
6. Response Serialization
   ↓
   {
     "properties": [
       {
         "id": "uuid",
         "title": "วิลล่าสวยงาม",  # Thai from translations
         "description": "...",       # Thai from translations
         "rent_price": 30000,
         "currency": "THB",
         "physical_specs": {
           "rooms": {"bedrooms": 3, "bathrooms": 2}
         },
         "amenities": {
           "interior": ["air_conditioning", "wifi"]  # IDs only
         }
       }
     ],
     "total": 150,
     "page": 1,
     "pages": 7
   }
   
7. Frontend Processing
   ↓
   - Receive property list
   - Translate amenity IDs using frontend dictionary:
       amenityLabels.th["air_conditioning"] → "เครื่องปรับอากาศ"
   - Render PropertyCard components
```

---

## Component Diagram

### Backend Architecture Layers

```
┌──────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                    │
│  /api/v1/properties/                                     │
│    - GET /          (list with locale)                   │
│    - GET /{id}      (get with locale)                    │
│    - POST /         (create - admin only)                │
│    - PUT /{id}      (update - admin only)                │
│    - DELETE /{id}   (soft delete - admin only)           │
└───────────────────────┬──────────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────────┐
│              Service Layer (Business Logic)               │
│                                                           │
│  PropertyService:                                        │
│    - list_properties(locale, filters, pagination)       │
│    - get_property_with_translations(id, locale)         │
│    - create_property(data, translations)                │
│    - update_property(id, data, translations)            │
│    - delete_property(id)                                │
│                                                           │
│  PropertyTranslationService:                            │
│    - get_translations(property_id, locale)              │
│    - upsert_translation(property_id, locale, field, value)│
│    - get_all_locales_for_property(property_id)          │
└───────────────────────┬──────────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────────┐
│              Repository Layer (Data Access)               │
│                                                           │
│  PropertyRepository:                                     │
│    - query_with_filters(filters) → Query                │
│    - merge_translations(properties, locale) → List      │
│    - create(property) → Property                        │
│    - update(id, data) → Property                        │
│                                                           │
│  Uses SQLAlchemy ORM                                     │
└───────────────────────┬──────────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────────┐
│                   Model Layer (ORM)                       │
│                                                           │
│  Property (SQLAlchemy Model)                             │
│  PropertyTranslation (SQLAlchemy Model)                  │
│                                                           │
│  Relationships: Property.translations → [Translation]    │
└───────────────────────┬──────────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────────┐
│                  Database Layer (PostgreSQL)              │
│                                                           │
│  Tables: properties, property_translations               │
│  Indexes: B-tree, GIN, HNSW (future)                     │
│  Extensions: pgvector                                    │
└──────────────────────────────────────────────────────────┘
```

---

## Technology Choices

### Database
- **PostgreSQL 14+** with pgvector extension
- **Rationale:** 
  - JSONB support for flexible property data
  - GIN indexes for fast JSONB queries
  - pgvector for future semantic search
  - Industry-standard for multi-language applications

### Backend
- **FastAPI** with async/await
- **SQLAlchemy 2.0** with async ORM
- **Pydantic v2** for validation
- **Rationale:** Existing stack, async-first architecture

### Indexes
- **B-tree:** Exact matches (rent_price, property_type)
- **GIN:** JSONB queries (amenities, physical_specs)
- **HNSW (future):** Vector similarity (pgvector embeddings)
- **Rationale:** Optimized for specific query patterns

### Localization
- **Hybrid Strategy:** Database + Frontend dictionaries
- **Rationale:** Balance between flexibility and performance

---

## Key Design Principles

1. **Separation of Concerns**
   - Queryable data → dedicated columns/JSONB
   - Translatable text → property_translations table
   - Static labels → frontend dictionaries

2. **Performance First**
   - GIN indexes for all queryable JSONB fields
   - Single-query translation merging (no N+1)
   - Efficient storage (IDs for amenities, not full text)

3. **Future-Ready**
   - pgvector columns reserved (semantic search)
   - Schema supports unlimited locales
   - Extensible JSONB for new property attributes

4. **Safety & Reversibility**
   - Migration adds columns (doesn't remove)
   - All new columns nullable
   - Transaction-wrapped migration
   - Comprehensive rollback plan

---

## Trade-offs & Alternatives Considered

### Alternative 1: Full JSONB Localization
```json
{
  "title": {"en": "Villa", "th": "วิลล่า"},
  "amenities": {
    "en": ["Pool", "WiFi"],
    "th": ["สระว่ายน้ำ", "ไวไฟ"]
  }
}
```

**Rejected Because:**
- ❌ Bloated JSONB (duplicate structure per locale)
- ❌ Harder to query across locales
- ❌ Harder to validate
- ❌ Not extensible (adding locale requires JSONB migration)

### Alternative 2: Full Relational (No JSONB)
```sql
CREATE TABLE property_amenities (...);
CREATE TABLE property_rooms (...);
CREATE TABLE property_policies (...);
```

**Rejected Because:**
- ❌ Too many tables (10+ joins per query)
- ❌ Rigid schema (adding new property attribute requires migration)
- ❌ Poor fit for semi-structured data
- ❌ Overkill for startup scale

### Chosen: Hybrid Approach ✅
- ✅ Fast queries (GIN indexes)
- ✅ Clean translations (normalized table)
- ✅ Flexible schema (JSONB for semi-structured data)
- ✅ Scalable (10k+ properties)
- ✅ Maintainable (clear separation of concerns)

---

## When to Revisit This Architecture

**Triggers for Re-evaluation:**

1. **Performance Degradation**
   - Property listing query > 500ms consistently
   - Database size > 100GB
   - Property count > 100k

2. **Localization Complexity**
   - Need to support > 10 locales
   - Translation management becomes bottleneck
   - SEO requirements change dramatically

3. **Feature Requirements**
   - Advanced geospatial queries (need PostGIS)
   - Real-time collaborative editing (need different concurrency model)
   - Multi-tenancy (need schema per customer)

4. **Metrics to Monitor:**
   - Average query time for property listing
   - Cache hit ratio for translations
   - Database storage growth rate
   - Index usage statistics (pg_stat_user_indexes)

---

## Success Criteria

**Technical:**
- ✅ All indexes created successfully
- ✅ Property listing query < 200ms (24 properties)
- ✅ Migration runs without errors
- ✅ Rollback tested and functional

**Functional:**
- ✅ CRUD operations work with translations
- ✅ Locale switching returns correct data
- ✅ Fallback to EN when TH missing

**Quality:**
- ✅ Unit tests for all models
- ✅ Integration tests for service layer
- ✅ Load tests with 10k properties

---

**Next Document:** data-model-spec.md (Detailed SQL schema)

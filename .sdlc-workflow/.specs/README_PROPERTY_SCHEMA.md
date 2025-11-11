# Property Schema Documentation Suite

Complete reference documentation for the Bestays property schema migration from NextJS (V2 schema).

---

## Overview

This documentation suite provides comprehensive analysis and reference materials for the **Property2 (V2) schema** from the old Bestays NextJS codebase. The V2 schema is a production-ready, globally-designed real estate marketplace schema that supports:

- 15 property types (residential, commercial, land, hospitality)
- 4 transaction types (sale, rent, lease, sale-lease)
- 6 supported languages
- 150+ amenity options
- Advanced location hierarchy and proximity data
- Multi-language translation support
- Investment metrics (rental yield, price trends)
- Legal/ownership tracking
- Complete pricing flexibility

---

## Documentation Files

### 1. PROPERTY_SCHEMA_ANALYSIS.md (20 KB, 745 lines)

**Comprehensive technical analysis** of the property schema for architects and backend developers.

**Contents:**
- Executive summary and recommendations
- V1 vs V2 schema comparison
- Complete V2 schema reference
  - Core fields
  - JSONB structures (physical specs, location, amenities, policies, contact)
  - Translation table structure
  - System fields
  - Legal and ownership fields
  - SEO and investment metrics
- All enumerated values (150+ total)
- Room counts and area measurements
- Field size constraints
- Database indexes (12 strategic indexes)
- Migration path from V1 to V2
- Data integrity features
- Implementation recommendations
- Implementation status checklist
- Statistics and usage guidelines

**Best For:**
- Architecture decisions
- Database design review
- Backend API specification
- Migration planning
- Understanding design rationale

**Key Insights:**
- V2 is production-ready with ~40 improvements over V1
- Hierarchical location data (region→district→sub_district)
- 5 structured JSONB fields for complex data
- Soft delete implementation
- Multi-language translations via separate table
- 12 carefully selected indexes for query performance

---

### 2. PROPERTY_SCHEMA_QUICK_REFERENCE.md (12 KB, 490 lines)

**Fast lookup reference** for developers writing queries and building forms.

**Contents:**
- Core fields at a glance (table format)
- JSONB field structures with example JSON
- Enumeration quick lists
- Amenities quick count (153 total)
- Field groups for UI organization
- Translatable fields (13 fields × 6 languages)
- Database indexes with query examples
- Size limits and constraints
- Foreign keys and relationships
- Translation table structure
- System fields (auto-managed)
- Common SQL/query patterns
- Implementation checklist

**Best For:**
- Quick lookups while coding
- Form design and UI organization
- Query writing
- Field validation rules
- Copy-paste reference for enums

**Key Quick Lists:**
- Transaction types (4)
- Property types (15)
- Furnished levels (3)
- Property conditions (5)
- Directions (8)
- Ownership types (3)
- Currencies (3)
- Land size units (5)
- Distance units (3)
- Amenities by category (153 total)

---

### 3. PROPERTY_SCHEMA_EXAMPLES.md (28 KB, 1000+ lines)

**Real-world property examples** showing how to structure data in practice.

**Contents:**
- 4 complete property examples:
  1. **Luxury Beach Villa (Phuket)** - Rent, pool-villa, full amenities
  2. **Bangkok Condo** - Sale, luxury investment, high-rise
  3. **Chiang Mai Land** - Development land, 5-rai, mountain view
  4. **Commercial Office** - Lease, business park, 500 sqm
- Field mapping notes by property type
- Translation examples (Thai)
- Data validation examples (valid/invalid)
- Common patterns for specific property types
- Best practices for each property category

**Best For:**
- Understanding how to populate each field
- Testing data structure validation
- Frontend form design reference
- Database seeding scripts
- Acceptance testing scenarios

**Key Examples Show:**
- When to include/exclude certain fields
- How to structure complex JSONB objects
- Translation patterns for multi-language support
- Proper enumeration usage
- Asset/image referencing
- Contact information formatting

---

## File Organization

```
.sdlc-workflow/.specs/
├── README_PROPERTY_SCHEMA.md          ← You are here
├── PROPERTY_SCHEMA_ANALYSIS.md        ← Technical deep dive
├── PROPERTY_SCHEMA_QUICK_REFERENCE.md ← Fast lookup
└── PROPERTY_SCHEMA_EXAMPLES.md        ← Real examples
```

---

## How to Use This Documentation

### For Architects
1. Read **ANALYSIS.md** - Understand design decisions
2. Review **EXAMPLES.md** - See real-world usage
3. Check implementation checklist in **ANALYSIS.md**

### For Backend Developers
1. Start with **QUICK_REFERENCE.md** - Understand the shape of data
2. Read **ANALYSIS.md** - Understand indexing and relationships
3. Use **EXAMPLES.md** - See complete object structures
4. Reference **QUICK_REFERENCE.md** while coding

### For Frontend Developers
1. Start with **QUICK_REFERENCE.md** - Understand field organization
2. Read field groups section - Plan your form layout
3. Check **EXAMPLES.md** - See real data structures
4. Reference amenities section - Build selection components

### For Database/DevOps
1. Read database sections in **ANALYSIS.md**
2. Check indexes in **QUICK_REFERENCE.md**
3. Review migration path in **ANALYSIS.md**
4. Reference SQL files in react-workspace:
   - `/src/apps/bestays-web/db/sql-2/1.property2-enums.sql`
   - `/src/apps/bestays-web/db/sql-2/2.property2-tables.sql`

---

## Key Statistics

| Metric | Count | Details |
|--------|-------|---------|
| **Core Fields** | 30+ | title, description, pricing, classification |
| **JSONB Fields** | 5 | Structured complex data |
| **Total Enumerated Values** | 150+ | All options across all enums |
| **Amenity Options** | 108 | Interior(47) + Exterior(24) + Building(24) + Utilities(13) |
| **Location Advantages** | 45 | Waterfront, proximity, lifestyle features |
| **Property Types** | 15 | All categories |
| **Transaction Types** | 4 | sale, rent, lease, sale-lease |
| **Supported Languages** | 6 | en, th, ru, zh, de, fr |
| **Translatable Fields** | 13 | Core + location + amenities + policies + SEO |
| **Database Indexes** | 12 | 7 B-tree + 4 GIN (JSONB) + 1 DESC |
| **Max Images** | 30 | Per property |
| **Max Image Size** | Not specified | Should be defined in API |

---

## Database Schema Quick Reference

### Main Table: `bestays_properties_v2`
- **Type:** PostgreSQL Table
- **Key:** UUID (auto-generated)
- **Size:** ~60 columns + 5 JSONB columns
- **Soft Delete:** Yes (deleted_at)
- **Indexing:** 12 strategic indexes

### Translation Table: `bestays_property_translations`
- **Type:** PostgreSQL Table
- **Key:** Auto-increment ID
- **FK:** property_id → bestays_properties_v2
- **Unique:** (property_id, lang_code, field)
- **Languages:** 6 supported

### Key Enumerations (22 total)
- Currencies (3)
- Transaction types (4)
- Property types (15)
- And 18+ more...

---

## Important Notes for Migration

### Critical Issue Found
**SQL Bug:** The `transaction_type` enum is missing `"sale-lease"` option in SQL:
```sql
-- CURRENT (incomplete)
CREATE TYPE bestays_property2_transaction_type AS ENUM ('sale', 'rent', 'lease');

-- SHOULD BE (add sale-lease)
ALTER TYPE bestays_property2_transaction_type ADD VALUE 'sale-lease';
```

The TypeScript schemas support "sale-lease", but the database doesn't. This must be fixed before implementation.

### Legacy Compatibility
The V2 schema includes fields for migration from V1:
- `legacy_land_size`
- `legacy_land_size_unit`
- `legacy_metadata`

Use these to gradually migrate V1 properties.

### Soft Deletes
Properties use soft deletes via `deleted_at` field:
- Set `deleted_at` to mark as deleted
- Filter `WHERE deleted_at IS NULL` in queries
- Never actually delete records (audit trail)

---

## Implementation Checklist

### Database (Completed)
- [x] Main table created
- [x] Translation table created
- [x] All enums created (missing "sale-lease")
- [x] Indexes created
- [x] RLS policies configured
- [ ] Fix enum (add "sale-lease")

### Backend (FastAPI)
- [ ] Create Pydantic models
- [ ] Implement CRUD endpoints
- [ ] Add translation management
- [ ] Implement filtering/search
- [ ] Add image upload
- [ ] Add soft delete logic

### Frontend (SvelteKit)
- [ ] Build property forms
- [ ] Create amenity selectors
- [ ] Add location hierarchy
- [ ] Implement multi-image upload
- [ ] Add translation UI
- [ ] Build property cards/listing
- [ ] Create detail pages
- [ ] Implement search filters

---

## Source Files in React Workspace

All source material came from:
```
/Users/solo/Projects/_repos/react-workspace/
├── src/apps/bestays-web/entities/property2/types/
│   ├── property.ts (main schema)
│   ├── property-create.ts
│   ├── property-listing.ts
│   ├── physical-specs.ts
│   ├── location-details.ts
│   ├── amenity.ts
│   ├── policies.ts
│   ├── contact-info.ts
│   ├── rooms-count.ts
│   ├── area-measurment.ts
│   └── catalogue/ (45+ enumeration files)
└── src/apps/bestays-web/db/sql-2/
    ├── 1.property2-enums.sql
    ├── 2.property2-tables.sql
    ├── 3.property2-rls.sql
    ├── 4.property2-views.sql
    └── 5.property2-triggers.sql
```

---

## Related Documentation

- **Bestays CLAUDE.md** - Project guidelines and SDLC workflow
- **MILESTONE_01_WEBSITE_REPLICATION.md** - Feature requirements
- **Git workflow** - How to branch and commit
- **Task folder system** - How to organize work

---

## Document Maintenance

These documents should be updated when:
1. New enumeration values are added
2. Database schema changes
3. New JSONB structures are introduced
4. Translation language support expands
5. Property types are added/removed
6. Implementation patterns change

Last updated: **2025-11-06**

---

## Support & Questions

For questions about:
- **Schema design**: See PROPERTY_SCHEMA_ANALYSIS.md
- **Quick lookup**: See PROPERTY_SCHEMA_QUICK_REFERENCE.md
- **Implementation**: See PROPERTY_SCHEMA_EXAMPLES.md
- **Original source**: Check react-workspace

---

## Quick Start

**I want to:**
- **Understand the schema** → Read ANALYSIS.md (Sections: Executive Summary + V2 Schema Complete Reference)
- **Build a form** → Use QUICK_REFERENCE.md (Field Groups for UI)
- **Write a query** → Use QUICK_REFERENCE.md (Common Patterns)
- **Create test data** → Copy from EXAMPLES.md (4 full property objects)
- **Implement API** → Read ANALYSIS.md (section: Usage Recommendations for FastAPI/SvelteKit)
- **Check field limits** → See QUICK_REFERENCE.md (Size Limits table)

---

**Total Documentation:** 60+ KB | 1,230+ lines | 3 detailed guides | 4 complete examples


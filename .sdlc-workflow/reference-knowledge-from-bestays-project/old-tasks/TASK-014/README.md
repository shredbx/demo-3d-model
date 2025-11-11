# TASK-014: Manual Property Import for Development

**Story:** US-023 (Property Import & Display with Localization)
**Type:** feat
**Status:** IN_PROGRESS
**Branch:** feat/TASK-014-US-023

---

## Objective

Manually import 3-5 rental properties from the old bestays.app database to provide test data for frontend development. This is a **temporary development task** - full automated import will come later via LLM pipeline.

---

## Context

**Why Manual Import?**
- Frontend team needs real property data to build listing/detail pages
- Full automated import requires LLM endpoint (future work)
- 3-5 properties enough for development/testing purposes

**Future LLM Pipeline (Not This Task):**
- Accept: property details + images
- Output: fully converted Property V2 JSON with all fields
- Support: any system language (EN/TH/etc.)
- Use: for bulk import of all properties

---

## Requirements

### 1. Source Data

**Old Database:** Old bestays.app Supabase database (read-only access)
- Need credentials to connect
- Extract 3-5 rental properties (diverse examples)
- Should include: different locations, prices, amenities

### 2. Data Transformation

Transform old format → Property V2 schema:

**Required Fields:**
- `title` (string, 10-255 chars)
- `description` (string, 50-5000 chars)
- `transaction_type` = "rent" (all properties are rentals)
- `property_type` (villa, condo, apartment, house, etc.)
- `rent_price` (BigInt, in satang)
- `currency` = "THB"

**JSONB Fields (5 fields):**
1. `physical_specs` - Bedrooms, bathrooms, area, furnishing, etc.
2. `location_details` - Coordinates, province, district, etc.
3. `amenities` - Array of amenity IDs (reference `amenities` table)
4. `policies` - Policies object (pets, smoking, etc.)
5. `contact_info` - Phone, LINE, email, etc.

**Translation Strategy:**
- EN values: Use original English data
- TH values: Copy English for now (placeholders)
- Frontend will display "[TH]" prefix to indicate placeholder
- Admins will translate later via inline editing

**Images:**
- Keep Supabase Storage URLs as-is (no R2 migration yet)
- Store in `cover_image` and `images` JSONB fields

### 3. Insertion Method

**Option A: Direct SQL Insert**
```sql
INSERT INTO properties (
    title, description, transaction_type, property_type,
    rent_price, currency, physical_specs, location_details,
    amenities, policies, contact_info, cover_image, images,
    is_published, created_by, updated_by
) VALUES (...);
```

**Option B: Use API Endpoint**
```bash
curl -X POST http://localhost:8011/api/v1/properties \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{ ... property data ... }'
```

Choose whichever is faster for manual import.

### 4. Validation

After import:
- Verify properties exist: `SELECT * FROM properties;`
- Test API endpoint: `curl http://localhost:8011/api/v1/properties?locale=en`
- Check translations work: `curl http://localhost:8011/api/v1/properties?locale=th`
- Verify images load (Supabase URLs still valid)

---

## Success Criteria

✅ 3-5 properties inserted into `properties` table
✅ All required fields populated correctly
✅ All 5 JSONB fields have valid structure
✅ Properties accessible via `GET /api/v1/properties`
✅ Properties display in both EN and TH locales (TH = placeholders)
✅ Images load correctly (Supabase URLs working)

---

## Implementation Notes

**Script Location:** `apps/server/app/scripts/manual_import_properties.py`

**Script Structure:**
```python
# 1. Connect to old Supabase database (read-only)
# 2. SELECT 3-5 rental properties with diverse examples
# 3. Transform each property to Property V2 schema
# 4. Map amenities to amenity IDs from `amenities` table
# 5. Insert via SQL or API endpoint
# 6. Print summary (IDs, titles, URLs)
```

**Example Properties to Import:**
- Luxury villa in Phuket (high-end, pool, 4BR)
- Budget condo in Bangkok (affordable, BTS access, 1BR)
- Beachfront house in Koh Samui (beach, garden, 3BR)

**Diversity Criteria:**
- Different property types (villa, condo, house)
- Different price ranges (budget, mid-range, luxury)
- Different locations (Bangkok, Phuket, Samui, etc.)
- Different amenities (pool, gym, beach access, etc.)

---

## Time Estimate

**Total:** 2-3 hours

- Script creation: 1 hour
- Data transformation: 30 minutes
- Import execution: 15 minutes
- Validation: 30 minutes
- Documentation: 15 minutes

---

## Dependencies

- Old bestays.app Supabase credentials (need from user)
- Property V2 backend API (TASK-013 - COMPLETED)
- Amenities seed data (TASK-013 - COMPLETED)
- Admin authentication token (for API insertion method)

---

## Future Work (Not This Task)

- LLM endpoint for automated property conversion
- Bulk import script using LLM pipeline
- Image migration to R2 storage
- Thai translation via LLM or human editors
- Automated import CI/CD pipeline

---

## Questions for User

1. Do you have old bestays.app Supabase credentials?
2. Which insertion method preferred (SQL or API)?
3. Any specific properties you want imported first?
4. Should we migrate images to R2 now or keep Supabase URLs?

---

**Next Steps:**
1. Get old database credentials from user
2. Create import script
3. Run import
4. Verify via API
5. Commit and move to frontend tasks

# Property Import Script Implementation Report

**Story:** US-023 - Property Import & Display
**Task:** TASK-014 - Create Import Script
**Date:** 2025-11-09
**Status:** ✅ Complete

---

## Overview

Created two property import scripts for populating the Property V2 database:

1. **import_sample_properties.py** - Recommended for development (sample data)
2. **import_live_properties.py** - Advanced web scraping (real data)

## Implementation Details

### 1. Sample Data Import Script

**File:** `apps/server/app/scripts/import_sample_properties.py`

**Features:**
- 10 realistic sample properties based on live bestays.app structure
- No external dependencies required
- Fast and reliable execution
- Dry-run mode for testing
- Full Property V2 schema compliance

**Sample Properties:**

| Title | Type | Price | Beds | Baths | Tags |
|-------|------|-------|------|-------|------|
| Quiet 1-Bedroom Home Near Secret Beach | Villa | ฿35,000 | 1 | 1 | beach, quiet, pool |
| Modern 2-Bedroom Villa with Sea View | Villa | ฿45,000 | 2 | 2 | seaview, modern, luxury |
| Luxury 3-Bedroom Beachfront Villa | Villa | ฿75,000 | 3 | 3 | beach, luxury, pool, seaview |
| Cozy 1-Bedroom Apartment in Baan Tai | Apartment | ฿28,000 | 1 | 1 | quiet, affordable |
| Spacious 2-Bedroom House with Garden | House | ฿38,000 | 2 | 2 | garden, quiet, family |
| Modern Studio with Pool Access | Apartment | ฿22,000 | 1 | 1 | modern, pool, affordable |
| Elegant 3-Bedroom Villa with Private Pool | Villa | ฿85,000 | 3 | 3 | luxury, pool, seaview |
| Traditional Thai House in Thong Sala | House | ฿32,000 | 2 | 1 | traditional, central |
| Beachside 2-Bedroom Condo with Amenities | Condo | ฿52,000 | 2 | 2 | beach, luxury, modern, seaview |
| Hillside 1-Bedroom Villa with Panoramic Views | Villa | ฿42,000 | 1 | 1 | seaview, quiet, pool, luxury |

**Data Structure:**
```python
{
    "title": "...",
    "description": "...",  # 200+ chars, realistic content
    "transaction_type": "rent",
    "property_type": "villa",
    "rent_price": 3500000,  # In satang (฿35,000)
    "currency": "THB",
    "physical_specs": {
        "rooms": {"bedrooms": 1, "bathrooms": 1},
        "sizes": {"usable_area_sqm": 45.0},
        "furnishing": "fully_furnished",
        "condition": "excellent"
    },
    "location_details": {
        "administrative": {
            "province_id": "surat_thani",
            "province_name": "Surat Thani",
            "district_id": "koh_phangan",
            "district_name": "Koh Phangan",
            "postal_code": "84280"
        }
    },
    "amenities": {
        "interior": ["wifi", "air_conditioning"],
        "exterior": ["pool", "garden"],
        "building": ["security_24h"]
    },
    "policies": {
        "lease_terms": {
            "lease_duration_months": 12,
            "deposit_months": 2,
            "advance_payment_months": 1
        },
        "house_rules": {
            "pets_allowed": false,
            "smoking_allowed": false,
            "guests_allowed": true
        },
        "payment": {
            "utility_bills_included": false,
            "internet_included": true
        }
    },
    "contact_info": {
        "phone": "+66 77 123 456",
        "email": "info@bestays.app",
        "preferred_contact": "phone"
    },
    "cover_image": {
        "url": "https://images.unsplash.com/photo-...",
        "alt": "...",
        "width": 1200,
        "height": 800,
        "format": "jpg"
    },
    "images": [...],
    "tags": ["beach", "quiet", "pool"],
    "is_published": true,
    "is_featured": false,
    "listing_priority": 0
}
```

### 2. Web Scraping Import Script

**File:** `apps/server/app/scripts/import_live_properties.py`

**Features:**
- Playwright-based web scraping
- Supports JavaScript-heavy sites (NextJS)
- Multiple scraping strategies:
  1. Extract from `__NEXT_DATA__` JSON payload
  2. Fallback to DOM scraping
- Dry-run mode for testing
- Price extraction and normalization

**Dependencies:**
```bash
pip install playwright
playwright install chromium
```

**Scraping Strategies:**

**Strategy 1 - NextJS Data Extraction:**
```javascript
// Extract from <script id="__NEXT_DATA__">
const nextData = JSON.parse(document.getElementById('__NEXT_DATA__').textContent);
const properties = nextData.props.pageProps.properties;
```

**Strategy 2 - DOM Scraping:**
```python
# Find property cards
cards = await page.query_selector_all("a[href*='/properties/']")

# Extract from each card
title = await card.query_selector("h2, h3")
price = await card.query_selector("text=/฿|THB/")
image = await card.query_selector("img")
```

### 3. Documentation

**File:** `apps/server/app/scripts/README_PROPERTY_IMPORT.md`

**Contents:**
- Usage instructions for both scripts
- Authentication notes
- Troubleshooting guide
- TASK-014 specific instructions
- Verification commands

## Usage

### Development (Recommended)

```bash
# Start environment
make dev

# Shell into server
make shell-server

# Dry run (test transformation)
python app/scripts/import_sample_properties.py --dry-run

# Import 5 properties
python app/scripts/import_sample_properties.py

# Import 10 properties
python app/scripts/import_sample_properties.py --limit 10
```

### Web Scraping (Advanced)

```bash
# Install dependencies
pip install playwright
playwright install chromium

# Dry run
python apps/server/app/scripts/import_live_properties.py --dry-run

# Import
python apps/server/app/scripts/import_live_properties.py --limit 5
```

## Technical Details

### API Integration

**Endpoint:** `POST /api/v1/properties`

**Request:**
```python
headers = {"Content-Type": "application/json"}
response = await client.post(
    f"{api_url}/api/v1/properties",
    json=property_data,
    headers=headers
)
```

**Response:**
```json
{
  "message": "Property created successfully",
  "property": {
    "id": "uuid-here",
    "title": "...",
    "rent_price": 35000,  // Converted back to THB
    ...
  },
  "locale": "en"
}
```

### Amenity Mapping

**Process:**
1. Fetch amenities from API: `GET /api/v1/amenities`
2. Build mapping dict: `{"wifi": "wifi", "pool": "pool", ...}`
3. Validate amenity IDs during transformation
4. Only include amenities that exist in database

**Default Amenities:**
```python
{
    "interior": ["wifi", "air_conditioning"],
    "exterior": ["pool", "garden"],
    "building": ["security_24h"]
}
```

### Price Conversion

**Important:** Property V2 stores prices in **satang** (smallest currency unit):

```python
# Input: ฿35,000 THB
price_thb = 35000

# Convert to satang
rent_price = price_thb * 100  # = 3,500,000 satang

# API returns in THB
{
  "rent_price": 35000  # Converted back by service layer
}
```

### Image URLs

**Source:** Unsplash placeholder images

**Structure:**
```python
{
    "url": "https://images.unsplash.com/photo-...",
    "alt": "Property title - cover image",
    "width": 1200,
    "height": 800,
    "format": "jpg"
}
```

## Validation

### Pre-Import Checks

**1. Amenities Seeded:**
```bash
make shell-server
python app/scripts/seed_amenities_policies.py
```

**2. API Health:**
```bash
curl http://localhost:8011/health
```

**3. Database Connection:**
```bash
make shell-db
\dt  # List tables
SELECT COUNT(*) FROM amenities;
```

### Post-Import Verification

**1. List Properties:**
```bash
curl http://localhost:8011/api/v1/properties | jq
```

**2. Count Properties:**
```bash
curl http://localhost:8011/api/v1/properties | jq '.pagination.total'
```

**3. View Specific Property:**
```bash
# Get ID from list response
curl http://localhost:8011/api/v1/properties/{property-id} | jq
```

**4. Database Verification:**
```bash
make shell-db
SELECT COUNT(*) FROM properties;
SELECT title, rent_price, property_type FROM properties LIMIT 5;
```

## Test Results

### Sample Data Import (Dry Run)

```
📦 Selected 5 sample properties
🏷️  Fetching amenity mapping from API...
✓ Loaded 34 amenity mappings
✅ Transformed 5 properties

🔍 DRY RUN MODE - Not inserting to database

[Property 1]
Title: Quiet 1-Bedroom Home Near Secret Beach
Type: villa
Price: ฿35,000/month
Bedrooms: 1
Bathrooms: 1
Amenities: 5 items
Tags: beach, quiet, pool
Cover Image: https://images.unsplash.com/photo-1582268611958-ebfd161ef9cf...
```

### Expected Database State

After importing 5 properties:

```sql
SELECT
    id,
    title,
    property_type,
    rent_price / 100 as price_thb,
    physical_specs->'rooms'->>'bedrooms' as bedrooms,
    is_published
FROM properties
ORDER BY created_at DESC
LIMIT 5;
```

## Files Created

1. **`apps/server/app/scripts/import_sample_properties.py`** (382 lines)
   - Sample data import script
   - 10 realistic properties
   - Full schema compliance

2. **`apps/server/app/scripts/import_live_properties.py`** (625 lines)
   - Web scraping script
   - Playwright integration
   - Multiple scraping strategies

3. **`apps/server/app/scripts/README_PROPERTY_IMPORT.md`** (220 lines)
   - Usage documentation
   - Troubleshooting guide
   - Verification commands

## Recommendations

### For TASK-014 (Frontend Development)

**Use `import_sample_properties.py`:**
- ✅ Fast and reliable
- ✅ No external dependencies
- ✅ Consistent data structure
- ✅ Perfect for development

### For Production Data Migration

**Use `import_live_properties.py`:**
- Real property data
- Up-to-date information
- Requires Playwright setup

## Next Steps

### Immediate (TASK-014)

1. Start development environment: `make dev`
2. Seed amenities: `python app/scripts/seed_amenities_policies.py`
3. Import sample properties: `python app/scripts/import_sample_properties.py`
4. Verify: `curl http://localhost:8011/api/v1/properties | jq`

### Future Enhancements

1. **Authentication Integration**
   - Add Clerk JWT token generation
   - Support admin-only endpoints

2. **Image Upload**
   - Download and store images locally
   - Upload to S3/CDN
   - Update image URLs in database

3. **Batch Import**
   - Support CSV/JSON file input
   - Bulk insert with transaction handling
   - Progress tracking

4. **Deduplication**
   - Check for existing properties
   - Update instead of insert
   - Handle conflicts

5. **Validation**
   - Pre-import data validation
   - Schema compliance checks
   - Error reporting

## Trade-offs

### Sample Data vs Web Scraping

**Sample Data (Chosen for TASK-014):**
- ✅ Fast execution
- ✅ Reliable structure
- ✅ No external dependencies
- ✅ Predictable results
- ❌ Not real data
- ❌ Limited variety

**Web Scraping:**
- ✅ Real property data
- ✅ Up-to-date information
- ❌ Requires Playwright
- ❌ Slower execution
- ❌ Site-dependent (fragile)
- ❌ Complex setup

### Direct DB Insert vs API Endpoint

**API Endpoint (Chosen):**
- ✅ Validates data
- ✅ Uses service layer
- ✅ Consistent with production
- ✅ Tests API endpoints
- ❌ Slower than direct insert

**Direct DB Insert:**
- ✅ Faster
- ❌ Bypasses validation
- ❌ Skips business logic
- ❌ Doesn't test API

## Conclusion

**Status:** ✅ Complete

Successfully created two property import scripts:

1. **Development Script:** Simple, fast, reliable sample data import
2. **Production Script:** Advanced web scraping for real data

Both scripts:
- ✅ Support dry-run mode
- ✅ Validate amenity IDs
- ✅ Transform to Property V2 schema
- ✅ Insert via API endpoints
- ✅ Provide detailed output and error handling

**Recommended for TASK-014:** Use `import_sample_properties.py` to import 5 realistic properties for frontend development.

---

**Next Task:** TASK-015 - Frontend Property List Component

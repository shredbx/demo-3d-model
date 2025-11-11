# Property Rental Listings - Web Scraping Findings

**Date:** 2025-11-09
**Source:** https://bestays.app/listings/properties-for-rent
**Purpose:** Research for US-022 (AI-Powered Property Management)

---

## Executive Summary

Scraped 16 rental properties from Koh Phangan to understand current data structure and identify gaps for AI-powered property management system.

**Key Findings:**
- Current structure is **simple/flat** (property/ model) - NOT extended property2/ model
- Minimal amenities (5-10 per property, unstructured)
- No property dictionary references
- No AI-generated highlights or tags
- Images stored on Supabase (`/bestays-images/properties/`)
- Contact info embedded per property
- No policies, no coordinates, no room-by-room descriptions

**Conclusion:** Need to implement property2/ extended model with:
- Property dictionary (amenity categories, highlights, JSON schemas)
- AI-powered image analysis (mountain view, sea view, pool, etc.)
- Structured JSONB fields for rich presentation
- Multi-language support
- MCP integration for dictionary access

---

## 1. Listing Page Structure

**URL:** https://bestays.app/listings/properties-for-rent

### 1.1 Grid Layout
```html
<div class="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
  {/* 16 property cards */}
</div>
```

### 1.2 Property Card Data
Each card displays:
- **Title**: Truncated (e.g., "Quiet 1-Bedroom Home Near Secr...")
- **Price**: Monthly rental in Thai Baht (฿17,000 - ฿150,000)
- **Location**: `{area}, {region}` (e.g., "Baan Tai, Koh Phangan")
- **Cover Image**: Single optimized image via Next.js

### 1.3 URL Pattern
Individual properties: `/p/{uuid}`

Example: `/p/de6c6dda-6f23-41b6-a882-0ce5e06ad297`

---

## 2. Individual Property Structure

**Sample Property ID:** `de6c6dda-6f23-41b6-a882-0ce5e06ad297`

### 2.1 Complete JSON Structure

```json
{
  "id": "de6c6dda-6f23-41b6-a882-0ce5e06ad297",
  "title": "Quiet 1-Bedroom Home Near Secret Mountain",
  "description": "Stylish, modern home with premium furniture, washing machine & complete kitchenware — ready to move in! Perfect for singles or couples who love calm island living.",
  "transaction_type": "rent",
  "property_type": "house",
  "price": 3500000,
  "price_formatted": "฿35,000.00",
  "currency": "THB",
  "location": {
    "region": "Koh Phangan",
    "area": "Baan Tai",
    "country": "Thailand"
  },
  "specifications": {
    "bedrooms": 1,
    "land_size": 60,
    "land_size_unit": null
  },
  "amenities": [
    "Premium furniture",
    "Washing machine",
    "Complete kitchenware",
    "Free Wi-Fi",
    "Free water"
  ],
  "utilities": {
    "electricity": "7 THB/unit"
  },
  "terms": {
    "contract_length": "1-year",
    "deposit": "1 month"
  },
  "images": [
    {
      "url": "https://mtctlgbvwpssxqakyvoc.supabase.co/storage/v1/object/sign/bestays-images/properties/...",
      "alt": null,
      "order": 0
    }
  ],
  "cover_image": {
    "url": "https://mtctlgbvwpssxqakyvoc.supabase.co/storage/v1/object/sign/bestays-images/properties/...",
    "alt": null
  },
  "contact": {
    "phone": "+66983480288",
    "whatsapp": "+66983480288",
    "email": "beststaysinfo@gmail.com"
  },
  "timestamps": {
    "created_at": "2025-10-30T19:23:06.726864+00:00",
    "updated_at": "2025-10-30T19:23:06.726864+00:00"
  },
  "status": {
    "is_published": true
  }
}
```

### 2.2 Image Storage
- **Provider:** Supabase Storage
- **Bucket:** `bestays-images`
- **Path Pattern:** `/properties/{property_id}/{timestamp}-{hash}.{ext}`
- **Optimization:** Next.js Image API with width/quality params
- **Security:** Signed URLs with tokens

---

## 3. Data Analysis

### 3.1 Current Model: property/ (Simple)

**Strengths:**
- Easy agent input (minimal fields)
- Quick property creation
- No complex validation

**Limitations:**
- Unstructured amenities (just strings)
- No categorization (comfort, security, outdoor, etc.)
- No AI-generated highlights
- No property dictionary
- No policies (pet, smoking, parties)
- No coordinates for maps
- No room-by-room descriptions
- No multi-language support

### 3.2 Missing Fields (Compared to property2/)

**From User Screenshots:**
1. **Property Dictionary**
   - Amenity categories (comfort, security, outdoor, kitchen, bathroom, etc.)
   - Highlight categories (views, proximity, unique features)
   - JSON schemas for validation

2. **AI-Generated Data**
   - Image analysis tags (mountain view, sea view, pool, garden, etc.)
   - Extracted highlights from text
   - Suggested amenities from images

3. **Rich Presentation**
   - Structured highlights array
   - Categorized amenities
   - Room-by-room descriptions
   - Virtual tour metadata

4. **Policies**
   - Pet policy (allowed, not allowed, negotiable)
   - Smoking policy
   - Party policy
   - Children policy

5. **Location Details**
   - Coordinates (lat/lng)
   - Full address breakdown
   - District, sub-district, province
   - Nearby landmarks

### 3.3 Missing Fields (Compared to US-016 Property V2)

**JSONB Fields:**
1. `physical_specs` (60+ fields)
   - Bedrooms, bathrooms, floors, living_area, land_area
   - Building age, renovation year
   - Parking spaces, balconies, terraces
   - Energy rating, construction quality

2. `location_details`
   - Full address (street, district, sub-district, province, postal_code)
   - Coordinates (latitude, longitude)
   - Nearby facilities (schools, hospitals, markets)
   - Transportation access

3. `amenities` (150+ amenities)
   - General (air conditioning, heating, fireplace)
   - Kitchen (dishwasher, oven, microwave)
   - Bathroom (bathtub, shower, bidet)
   - Safety (alarm, fire extinguisher, safe)
   - Outdoor (pool, garden, BBQ, parking)
   - Entertainment (TV, sound system, game room)

4. `policies`
   - Pets, smoking, children, parties
   - Check-in/out times
   - Cancellation policy
   - House rules

5. `contact_info`
   - Agent/owner details
   - Phone, email, WhatsApp, Line
   - Preferred contact method
   - Office hours

**Additional Fields:**
- Multi-language support (title_translations, description_translations)
- Company model (created_by, department, commission_rate)
- Workflow status (draft, pending, published, archived)
- SEO fields (meta_title, meta_description, slug)

---

## 4. Gap Analysis: Simple vs Extended Model

| Feature | Current (property/) | Needed (property2/) | US-016 Property V2 |
|---------|---------------------|---------------------|-------------------|
| **Amenities** | Unstructured list | Categorized + dictionary | 150+ amenities in JSONB |
| **Highlights** | None | AI-generated + dictionary | Not specified |
| **Location** | Region + area only | Full address + coordinates | location_details JSONB |
| **Policies** | None | Pet, smoking, parties | policies JSONB |
| **Images** | Basic URLs | AI-analyzed tags | Multiple images with metadata |
| **Specifications** | 2 fields (bedrooms, land_size) | 10+ fields | physical_specs JSONB (60+ fields) |
| **Multi-language** | None | Required for Thai/English | title/description translations |
| **Contact** | Simple object | Structured + preferences | contact_info JSONB |
| **Company Model** | None | Not required | created_by, department, commission |
| **Validation** | None | JSON schemas | Zod validation |

---

## 5. Storage Strategy Comparison

### 5.1 Option A: Normalized (Multiple Tables)

**Pros:**
- Strong referential integrity
- Easy joins and queries
- Standard SQL operations

**Cons:**
- 150+ amenities = 150 rows per property
- Complex queries (10+ joins)
- Slower writes (multiple tables)
- Schema changes require migrations

**Example:**
```sql
-- 1 property = 150+ rows across 5 tables
properties (1 row)
property_amenities (150 rows)
property_highlights (10 rows)
property_images (20 rows)
property_policies (5 rows)
```

### 5.2 Option B: JSONB + Zod (Recommended)

**Pros:**
- 1 row per property (simple)
- Flexible schema (no migrations for field additions)
- Fast writes (single row)
- Type safety with Zod
- GIN indexes for JSONB queries
- PostgreSQL JSON operators (fast)

**Cons:**
- Complex validation required
- Need Zod schemas
- JSON operator learning curve

**Example:**
```sql
-- 1 property = 1 row
properties (1 row with 5 JSONB columns)
  - physical_specs JSONB
  - location_details JSONB
  - amenities JSONB
  - policies JSONB
  - contact_info JSONB
```

**Recommendation:** **Option B (JSONB + Zod)** - Already implemented in US-016, proven pattern, scales better for rich properties.

---

## 6. AI-Powered Property Creation Workflow

### 6.1 Agent Input Flow

```
Agent uploads to chat:
├── Images (5-20 photos)
│   └── Stored on Cloudflare R2
└── Text description (freeform)
    └── Agent just describes the property naturally

↓

LLM (OpenRouter) analyzes:
├── Text → JSON fields
│   ├── Extract: bedrooms, bathrooms, price, location
│   ├── Extract: amenities from description
│   └── Generate: highlights based on keywords
└── Images → Tags via MCP dictionary
    ├── Detect: mountain view, sea view, pool
    ├── Detect: modern style, rustic style
    └── Tag: outdoor spaces, indoor features

↓

LLM outputs structured JSON:
{
  "physical_specs": {...},
  "location_details": {...},
  "amenities": {...},
  "highlights": [...],
  "image_tags": [...]
}

↓

Agent reviews & confirms → Property created
```

### 6.2 Required Components

1. **Property Dictionary (MCP)**
   - Amenity categories (150+ amenities)
   - Highlight categories (views, proximity, features)
   - JSON schemas for validation
   - Multi-language labels (EN/TH)

2. **Image Analysis (OpenRouter + MCP)**
   - Vision model (GPT-4V, Claude 3.5 Sonnet)
   - Dictionary lookup for tags
   - Confidence scoring

3. **Text Analysis (OpenRouter)**
   - Field extraction (bedrooms, bathrooms, price)
   - Amenity detection (pool, parking, Wi-Fi)
   - Highlight generation (mountain view, near beach)

4. **Cloudflare R2 Integration**
   - Image upload endpoint
   - Signed URLs for frontend
   - Thumbnail generation

5. **Agent Chat Interface**
   - File upload (images + text)
   - Real-time LLM streaming
   - Confirmation modal before creation

---

## 7. Multi-Product Architecture Decisions

### 7.1 Shared vs Domain-Specific

**User Requirements:**
- Bestays: Vacation rentals (properties for rent)
- Real Estate: Properties for sale + rent

**Shared Code:**
- Property V2 schema (database)
- AI-powered creation workflow
- Property dictionary (MCP)
- Image analysis
- JSONB validation (Zod)

**Domain-Specific:**
- Frontend routes (`/listings/properties-for-rent` vs `/listings/properties-for-sale`)
- Filters (monthly rent vs sale price)
- Redirect URLs after creation
- Branding (Bestays vs Real Estate logos)

**Architecture Pattern:**
```
apps/
├── server/
│   └── api/v1/properties/  (SHARED - both products use same API)
└── frontend/
    └── src/
        ├── lib/components/property/  (SHARED - components)
        ├── lib/api/property.ts       (SHARED - API client)
        └── routes/
            ├── (bestays)/listings/properties-for-rent/
            └── (realestate)/listings/properties-for-sale/
```

**Recommendation:** **Shared API + Domain-specific routes** - Maximizes code reuse while allowing product customization.

---

## 8. Recommended Implementation Phases

### Phase 1: Property V2 Schema + Basic CRUD (US-016 already done)
- [x] Property V2 database schema with 5 JSONB fields
- [x] Alembic migration
- [x] Company model adaptations

### Phase 2: Property Dictionary (US-022 Part 1)
- [ ] MCP server for property dictionary
- [ ] Amenity categories (150+ amenities)
- [ ] Highlight categories
- [ ] JSON schemas for validation
- [ ] Multi-language labels (EN/TH)

### Phase 3: AI-Powered Creation Backend (US-022 Part 2)
- [ ] OpenRouter integration for text analysis
- [ ] OpenRouter integration for image analysis
- [ ] Cloudflare R2 integration
- [ ] Property creation API endpoint
- [ ] Zod validation for JSONB fields

### Phase 4: Agent Chat Interface Frontend (US-022 Part 3)
- [ ] Chat UI with file upload
- [ ] Real-time LLM streaming
- [ ] Property preview modal
- [ ] Confirmation before creation

### Phase 5: Property Listings Frontend (US-023)
- [ ] Property list page (grid view)
- [ ] Property detail page
- [ ] Filters and search
- [ ] Multi-product routing (bestays vs realestate)

### Phase 6: Porting to Real Estate (US-024)
- [ ] Port property listings to Real Estate
- [ ] Add "Properties for Sale" filter
- [ ] Update branding and routes

---

## 9. Key Decisions to Make in US-022 RESEARCH

1. **MCP Architecture**
   - New MCP server or extend existing?
   - Dictionary storage: database vs JSON files?
   - How to version property dictionary?

2. **Image Storage Migration**
   - Keep Supabase or migrate to Cloudflare R2?
   - Migration strategy for existing images?
   - Thumbnail generation approach?

3. **LLM Model Selection**
   - GPT-4V vs Claude 3.5 Sonnet for image analysis?
   - Cost vs accuracy trade-off?
   - Fallback strategy if LLM fails?

4. **Agent Experience**
   - Chat-first or form-first?
   - Allow manual field editing after LLM analysis?
   - Confirmation flow design?

5. **Multi-Product Routing**
   - SvelteKit route groups?
   - Shared layouts vs product-specific?
   - SEO considerations?

---

## 10. Next Steps

1. **Create US-022 (AI-Powered Property Management)**
   - Story description
   - Acceptance criteria
   - Link to this findings document

2. **Start RESEARCH phase (TASK-012)**
   - Review US-016 Property V2 schema
   - Design property dictionary structure
   - Research MCP server patterns
   - Design AI-powered creation flow
   - Evaluate image storage options

3. **Create substories (US-023, US-024, US-025)**
   - US-023: Property Listings Frontend
   - US-024: Porting to Real Estate
   - US-025: Advanced Property Search/Filters

---

## Appendix: Sample Properties

### A.1 Property 1
- **ID:** `de6c6dda-6f23-41b6-a882-0ce5e06ad297`
- **Title:** Quiet 1-Bedroom Home Near Secret Mountain
- **Price:** ฿35,000/month
- **Type:** House
- **Location:** Baan Tai, Koh Phangan
- **Amenities:** Premium furniture, washing machine, complete kitchenware, Wi-Fi, free water

### A.2 Property 2
- **ID:** `7e4d2f8a-9b1c-4e6d-8f2a-3c5d9e7f1a4b` (example)
- **Title:** Modern Villa with Pool
- **Price:** ฿150,000/month
- **Type:** Villa
- **Location:** Thong Sala, Koh Phangan
- **Amenities:** Private pool, sea view, 3 bedrooms, fully furnished

---

**End of Report**

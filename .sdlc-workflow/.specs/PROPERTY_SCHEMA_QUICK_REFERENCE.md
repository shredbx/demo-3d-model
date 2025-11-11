# Property Schema Quick Reference

For fast lookup of property field definitions and enumeration values.

---

## Core Fields at a Glance

| Field | Type | Max Length | Notes |
|-------|------|-----------|-------|
| `id` | UUID | - | Auto-generated primary key |
| `title` | TEXT | 200 | Property name/headline |
| `description` | TEXT | 5000 | Full property description |
| `title_deed` | TEXT | - | Legal reference document |
| `sale_price` | BIGINT | - | Price if sold |
| `rent_price` | BIGINT | - | Monthly rent |
| `lease_price` | BIGINT | - | Long-term lease price |
| `currency` | ENUM | - | THB, USD, EUR |
| `price_per_unit` | DECIMAL | - | e.g., per sqm |
| `transaction_type` | ENUM | - | sale, rent, lease |
| `property_type` | ENUM | - | 15 options |
| `is_published` | BOOLEAN | - | Visible to public |
| `is_featured` | BOOLEAN | - | Featured listing |
| `listing_priority` | INT | - | Sort order |
| `ownership_type` | ENUM | - | freehold, leasehold, company |
| `foreign_quota` | BOOLEAN | - | Can foreigner buy? |
| `rental_yield` | DECIMAL | - | Annual % yield |
| `price_trend` | ENUM | - | rising, stable, falling |
| `seo_title` | TEXT | 60 | SEO title |
| `seo_description` | TEXT | 160 | SEO meta description |
| `tags` | TEXT[] | - | Search tags |
| `created_at` | TIMESTAMP | - | Auto-set |
| `updated_at` | TIMESTAMP | - | Auto-set |
| `deleted_at` | TIMESTAMP | - | Soft delete |

---

## JSONB Fields Structure

### 1. `physical_specs` - Building Physical Characteristics
```json
{
  "rooms": {
    "bedrooms": 3,
    "bathrooms": 2,
    "living_rooms": 1,
    "kitchens": 1,
    "dining_rooms": 1,
    "offices": 0,
    "storage_rooms": 1,
    "maid_rooms": 0,
    "guest_rooms": 0
  },
  "dimensions": {
    "total_area": { "value": 250, "unit": "sqm" },
    "living_area": { "value": 200, "unit": "sqm" },
    "usable_area": { "value": 220, "unit": "sqm" },
    "land_area": { "value": 500, "unit": "sqm" },
    "balcony_area": { "value": 20, "unit": "sqm" },
    "floor_area": { "value": 250, "unit": "sqm" }
  },
  "building_specs": {
    "floors": 2,
    "floor_level": 0,
    "parking_spaces": 2,
    "year_built": 2020,
    "last_renovated": 2023,
    "facing_direction": "south",
    "condition": "excellent",
    "furnished": "fully"
  }
}
```

### 2. `location_details` - Location and Proximity Information
```json
{
  "region": "Phuket",
  "district": "Patong",
  "sub_district": "Patong",
  "location_advantages": ["beachfront", "near_airport", "gated_community"],
  "location_advantages_additional": ["Peaceful area", "Good investment"],
  "proximity": {
    "beach_distance": { "value": 100, "unit": "m" },
    "road_access": "private_road",
    "nearest_town": { "name": "Patong Town", "distance": 2, "unit": "km" }
  },
  "transportation": {
    "nearest_airport": { "name": "Phuket Airport", "distance": 45, "unit": "km" },
    "public_transport": ["Songthaew", "Taxi"],
    "parking_available": true
  }
}
```

### 3. `amenities` - Property Features and Services
```json
{
  "interior": [
    { "id": "air_conditioning", "name": "Air Conditioning", "icon": "Snowflake" },
    { "id": "kitchen_island", "name": "Kitchen Island", "icon": "ChefHat" }
  ],
  "exterior": [
    { "id": "private_pool", "name": "Private Swimming Pool", "icon": "Waves" }
  ],
  "building": [
    { "id": "24h_security", "name": "24h Security", "icon": "Shield" }
  ],
  "neighborhood": ["Quiet area", "Family friendly"],
  "special_features": [],
  "utilities": [
    { "id": "fiber_internet", "name": "Fiber Internet", "icon": "Wifi" }
  ]
}
```

### 4. `policies` - Rules, Terms, and Additional Costs
```json
{
  "inclusions": ["Utilities", "WiFi", "Cable TV"],
  "restrictions": ["No smoking", "No pets"],
  "house_rules": ["Quiet hours 10pm-8am", "Guests must register"],
  "additional_fees": [
    {
      "type": "Service charge",
      "amount": 5000,
      "currency": "THB",
      "frequency": "monthly",
      "description": "Maintenance and utilities"
    }
  ],
  "lease_terms": {
    "minimum_lease_months": 12,
    "maximum_lease_months": 36,
    "notice_period_days": 30,
    "security_deposit_months": 1,
    "advance_payment_months": 1
  }
}
```

### 5. `contact_info` - Agent and Agency Contact Details
```json
{
  "agent_name": "John Doe",
  "agent_phone": "+66812345678",
  "agent_email": "john@bestays.app",
  "agent_line_id": "johnagent",
  "agent_whatsapp_id": "+66812345678",
  "agency_name": "Bestays Realty",
  "languages_spoken": ["English", "Thai", "Russian"],
  "preferred_contact": "whatsapp",
  "availability_hours": "24h"
}
```

### 6. `cover_image` - Primary Property Image
```json
{
  "url": "https://cdn.bestays.app/properties/123/cover.jpg",
  "color": "#e8d7c3",
  "path": "properties/123/cover.jpg",
  "alt": "Modern villa with pool view"
}
```

### 7. `images` - Additional Property Images
```json
[
  { "url": "...", "color": "#...", "path": "...", "alt": "..." },
  { "url": "...", "color": "#...", "path": "...", "alt": "..." }
]
```
Max: 30 images

---

## Enumeration Quick Lists

### Transaction Types (4)
```
sale       For Sale
rent       For Rent
lease      For Lease
sale-lease For Sale & Lease
```

### Property Types (15)
```
Land & Development:  land, house, villa, pool-villa
Residential:         apartment, condo, townhouse, penthouse
Commercial:          office, shop, warehouse, business
Hospitality:         resort, hotel
Other:               other
```

### Furnished Levels (3)
```
fully        Fully Furnished
partially    Partially Furnished
unfurnished  Unfurnished
```

### Property Conditions (5)
```
new                New
excellent          Excellent
good               Good
fair               Fair
needs_renovation   Needs Renovation
```

### Directions (8)
```
Cardinal:      north, south, east, west
Intercardinal: northeast, northwest, southeast, southwest
```

### Ownership Types (3)
```
freehold   Freehold (own building & land)
leasehold  Leasehold (time-limited)
company    Company Ownership
```

### Currencies (3)
```
THB  Thai Baht
USD  US Dollar
EUR  Euro
```

### Price Trends (3)
```
rising  Rising prices
stable  Stable prices
falling Falling prices
```

### Area Units (5)
```
sqm   Square Meters (international)
sqft  Square Feet (international)
rai   Rai (Thai: 1600 sqm)
ngan  Ngan (Thai: 400 sqm)
wah   Wah (Thai: 4 sqm)
```

### Road Access (4)
```
main_road         On Main Road
private_road      Private Road Access
paved_road        Paved Road Access
quiet_cul_de_sac  Quiet Cul-de-sac
```

### Distance Units (3)
```
km   Kilometers
m    Meters
mi   Miles
```

---

## Amenities Quick Count

| Category | Count | Examples |
|----------|-------|----------|
| Interior | 47 | AC, kitchen island, dishwasher, sauna |
| Exterior | 24 | Pool, terrace, garden, garage |
| Building | 24 | 24h security, gym, elevator, concierge |
| Utilities | 13 | WiFi, water, electricity, generator |
| Location Advantages | 45 | Beachfront, near school, gated community |
| **TOTAL** | **153** | - |

---

## Field Groups for UI

### Basic Information
- title, description, title_deed

### Pricing
- sale_price, rent_price, lease_price, currency, price_per_unit

### Classification
- transaction_type, property_type

### Physical Information
- physical_specs (entire JSONB object)

### Location
- location_details (entire JSONB object)

### Features
- amenities (entire JSONB object)

### Legal
- ownership_type, foreign_quota

### Terms & Conditions
- policies (entire JSONB object)

### Contact
- contact_info (entire JSONB object)

### Media
- cover_image, images, virtual_tour_url, video_url

### Visibility
- is_published, is_featured, listing_priority

### Investment
- rental_yield, price_trend

### SEO
- seo_title, seo_description, tags

---

## Translatable Fields (13)

Language codes: `en`, `th`, `ru`, `zh`, `de`, `fr`

Can be translated:
1. `title`
2. `description`
3. `location_region`
4. `location_district`
5. `amenities_interior`
6. `amenities_exterior`
7. `amenities_building`
8. `amenities_neighborhood`
9. `policies_inclusions`
10. `policies_restrictions`
11. `policies_house_rules`
12. `seo_title`
13. `seo_description`

---

## Database Indexes

Quick reference for performance-critical queries:

```
is_published          SELECT * FROM properties WHERE is_published = true
transaction_type      SELECT * FROM properties WHERE transaction_type = 'sale'
property_type         SELECT * FROM properties WHERE property_type = 'villa'
created_by            SELECT * FROM properties WHERE created_by = user_id
deleted_at            SELECT * FROM properties WHERE deleted_at IS NULL
is_featured           SELECT * FROM properties WHERE is_featured = true
listing_priority      SELECT * FROM properties ORDER BY listing_priority DESC
location_details      JSONB queries on location (beachfront, region, etc.)
physical_specs        JSONB queries on rooms, area, etc.
amenities             JSONB queries on amenity selection
tags                  JSONB queries on tag-based search
```

---

## Size Limits

```
title:                200 chars
description:          5000 chars
seo_title:           60 chars
seo_description:     160 chars
images:              30 max per property
price_trend:         3 options (rising, stable, falling)
rental_yield:        5 digits, 2 decimals (max 999.99%)
```

---

## Foreign Keys & Relationships

```
created_by → auth.users.id
updated_by → auth.users.id
property_translations.property_id → bestays_properties_v2.id
```

---

## Translation Table Structure

```
property_id    UUID (FK to properties)
lang_code      CHAR(2) (en, th, ru, zh, de, fr)
field          TEXT (13 translatable fields)
value          TEXT (translated content)
created_at     TIMESTAMP (auto)
UNIQUE (property_id, lang_code, field)
```

---

## System Fields (Auto-managed)

```
created_at     TIMESTAMP - Set on insert
updated_at     TIMESTAMP - Updated on every change
created_by     UUID - Set by application
updated_by     UUID - Updated by application
deleted_at     TIMESTAMP - Set on soft delete (NULL = active)
```

---

## Common Patterns

### Mark property as published
```
is_published = true
```

### Mark as featured with priority
```
is_featured = true
listing_priority = 100
```

### Soft delete property
```
deleted_at = NOW()
```

### Filter by room count (via JSONB)
```
physical_specs->'rooms'->>'bedrooms' = '3'
```

### Filter by location advantages
```
location_details->'location_advantages' @> '"beachfront"'
```

### Get all amenities for property
```
amenities->>'interior' 
amenities->>'exterior'
amenities->>'building'
amenities->>'utilities'
```

### Multiple languages for title
```
SELECT title FROM properties WHERE lang_code = 'th'
FROM property_translations
WHERE property_id = :id AND field = 'title'
```

---

## Implementation Checklist

### Database Setup
- [x] Create main table (bestays_properties_v2)
- [x] Create translation table (bestays_property_translations)
- [x] Create all ENUMs
- [x] Create indexes (12 total)
- [x] Set up RLS policies
- [ ] Add "sale-lease" to transaction_type enum

### Backend (FastAPI)
- [ ] Create Pydantic models for each JSONB section
- [ ] Implement CRUD endpoints
- [ ] Add translation endpoints
- [ ] Add filtering and search
- [ ] Implement soft delete logic
- [ ] Add image upload handling

### Frontend (SvelteKit)
- [ ] Build property form (all fields)
- [ ] Create amenity selector (150+ options)
- [ ] Add location hierarchy selector
- [ ] Implement multi-image upload
- [ ] Add translation UI
- [ ] Create property listing cards
- [ ] Build property detail page
- [ ] Add search filters

---

**Version:** 1.0  
**Last Updated:** 2025-11-06  
**Source:** React Workspace Property2 Schema (property2/types/ + db/sql-2/)


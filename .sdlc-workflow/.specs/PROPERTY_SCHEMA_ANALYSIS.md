# Property Schema Analysis Report

**Date:** 2025-11-06  
**Source:** Old NextJS Codebase Analysis (React Workspace)  
**Status:** Complete

---

## Executive Summary

The old Bestays NextJS codebase contains two property schemas:

1. **Property (V1)** - Simple, legacy schema in `bestays_properties` table
2. **Property2 (V2)** - Enhanced, comprehensive schema in `bestays_properties_v2` table (NEW)

The V2 schema is production-ready and designed specifically for a global real estate marketplace. It features:
- **Structured data** for complex property attributes (physical specs, location details, amenities)
- **Multi-language support** via separate translations table
- **Comprehensive amenities** (interior, exterior, building, neighborhood, special features, utilities)
- **Advanced location data** (region, district, sub-district, proximity, transportation)
- **Financial flexibility** (multiple pricing types, currency support, rental yields)
- **Investment metrics** (price trends, rental yield tracking)
- **15 property types** across residential, commercial, and hospitality

**Recommendation:** Migrate to Property2 (V2) schema for the new SvelteKit/FastAPI stack. It's more comprehensive and better designed.

---

## Schema Comparison

### V1 (Legacy) vs V2 (Current)

| Aspect | V1 | V2 | Notes |
|--------|----|----|-------|
| **Table Name** | `bestays_properties` | `bestays_properties_v2` | Complete redesign |
| **Core Fields** | Basic (title, description) | Same + title_deed | V2 adds legal reference |
| **Pricing** | Single price field | sale_price, rent_price, lease_price | V2 supports multiple transaction types |
| **Property Classification** | Simple enum | Enum (15 types) | V2 more comprehensive |
| **Structured Data** | Metadata JSONB only | Multiple JSONB objects | V2 separates concerns |
| **Translations** | None | Dedicated table | V2 supports 6 languages |
| **Amenities** | Embedded in metadata | Categorized (6 types) | V2 has 150+ amenity options |
| **Location** | Simple JSONB | Structured schema | V2 has region/district/sub_district |
| **SEO** | None | seo_title, seo_description | V2 adds SEO optimization |
| **Media** | cover_image, images | Same + video_url, virtual_tour_url | V2 adds video/VR support |
| **Legal/Ownership** | None | ownership_type, foreign_quota | V2 adds legal dimensions |
| **Investment Metrics** | None | rental_yield, price_trend | V2 for investor features |

---

## V2 (Current) Schema - Complete Reference

### Core Table: `bestays_properties_v2`

#### Core Fields
```
id: UUID (Primary Key, Auto-generated)
title: TEXT (Max 200 chars, nullable)
description: TEXT (Max 5000 chars, nullable)
title_deed: TEXT (For legal reference, nullable)
```

#### Pricing Fields
```
sale_price: BIGINT (sale transaction price)
rent_price: BIGINT (monthly rent)
lease_price: BIGINT (long-term lease price)
currency: ENUM (THB, USD, EUR) - Default: THB
price_per_unit: NUMERIC(15,2) (e.g., price per sqm)
```

#### Classification Fields
```
transaction_type: ENUM
  - "sale"
  - "rent"
  - "lease"
  (Note: "sale-lease" in TS but NOT in SQL - may need update)

property_type: ENUM (15 options)
  - "land"
  - "house", "villa", "pool-villa"
  - "apartment", "condo", "townhouse", "penthouse"
  - "office", "shop", "warehouse", "business"
  - "resort", "hotel"
  - "other"
```

#### Structured Data (JSONB)
```
physical_specs JSONB:
  - rooms: { bedrooms, bathrooms, living_rooms, kitchens, dining_rooms, offices, storage_rooms, maid_rooms, guest_rooms }
  - dimensions: { total_area, living_area, usable_area, land_area, balcony_area, floor_area }
    * Each with: { value: number, unit: "sqm"|"sqft"|"rai"|"ngan"|"wah" }
  - building_specs: { floors, floor_level, parking_spaces, year_built, last_renovated, facing_direction, condition, furnished }

location_details JSONB:
  - region, district, sub_district (Thai administrative hierarchy)
  - location_advantages: string[] (45+ options like "beachfront", "near_airport", etc.)
  - location_advantages_additional: string[] (custom advantages)
  - proximity:
    * beach_distance: { value: number, unit: "km"|"m"|"mi" }
    * road_access: ENUM (main_road, private_road, paved_road, quiet_cul_de_sac)
    * nearest_town: { name, distance, unit }
  - transportation:
    * nearest_airport: { name, distance, unit }
    * public_transport: string[]
    * parking_available: boolean

amenities JSONB:
  - interior: [{ id, name, icon, description }] (47 options)
  - exterior: [{ id, name, icon, description }] (24 options)
  - building: [{ id, name, icon, description }] (24 options)
  - neighborhood: string[] (for custom neighborhood amenities)
  - special_features: [{ id, name, icon, description }]
  - utilities: [{ id, name, icon, description }] (13 options)

policies JSONB:
  - inclusions: string[] (what's included)
  - restrictions: string[] (property restrictions)
  - house_rules: string[] (tenant rules)
  - additional_fees: [{ type, amount, currency, frequency, description }]
  - lease_terms:
    * minimum_lease_months, maximum_lease_months
    * notice_period_days
    * security_deposit_months, advance_payment_months

contact_info JSONB:
  - agent_name, agent_phone, agent_email
  - agent_line_id, agent_whatsapp_id
  - agency_name
  - languages_spoken: string[]
  - preferred_contact: ENUM (phone, email, line, whatsapp, etc.)
  - availability_hours: ENUM (9am-5pm, 24h, weekdays, weekends, etc.)
```

#### Media Fields
```
cover_image JSONB:
  - url: string (required)
  - color: string (dominant color)
  - path: string (file path)
  - alt: string (alt text)

images JSONB[]:
  - Array of up to 30 images (same structure as cover_image)

virtual_tour_url: TEXT (URL to 3D/360 tour)
video_url: TEXT (Property video URL)
```

#### Legacy Compatibility
```
legacy_land_size: NUMERIC(15,2) (for migration)
legacy_land_size_unit: ENUM (sqm, sqft, rai, ngan, wah)
legacy_metadata: JSONB (for V1 data preservation)
```

#### System Fields
```
is_published: BOOLEAN (Default: false)
is_featured: BOOLEAN (Default: false) 
listing_priority: INTEGER (Default: 0, for sorting)
created_by: UUID (FK to auth.users)
updated_by: UUID (FK to auth.users)
created_at: TIMESTAMP (Auto-set)
updated_at: TIMESTAMP (Auto-set)
deleted_at: TIMESTAMP (Soft delete)
```

#### Legal & Ownership
```
ownership_type: ENUM
  - "freehold" (owns land + building)
  - "leasehold" (long-term lease)
  - "company" (company ownership)

foreign_quota: BOOLEAN (if foreign buyer can own)
```

#### SEO & Marketing
```
seo_title: TEXT (Max 60 chars)
seo_description: TEXT (Max 160 chars)
tags: TEXT[] (Array of tags for filtering/search)
```

#### Investment Metrics
```
rental_yield: NUMERIC(5,2) (annual % yield)
price_trend: ENUM
  - "rising"
  - "stable"
  - "falling"
```

### Translation Table: `bestays_property_translations`

Supports multi-language translations for common fields:

```
id: BIGINT (Auto-generated PK)
property_id: UUID (FK to bestays_properties_v2)
lang_code: CHAR(2) (e.g., 'en', 'th', 'ru', 'zh', 'de', 'fr')
field: TEXT (field name - see below)
value: TEXT (translated content)
created_at: TIMESTAMP
UNIQUE(property_id, lang_code, field)
```

**Translatable Fields:**
- Core: `title`, `description`
- Location: `location_region`, `location_district`
- Amenities: `amenities_interior`, `amenities_exterior`, `amenities_building`, `amenities_neighborhood`
- Policies: `policies_inclusions`, `policies_restrictions`, `policies_house_rules`
- SEO: `seo_title`, `seo_description`

---

## Enumerated Values - Complete Reference

### Transaction Types (4 options)
```
sale         "For Sale"
rent         "For Rent"
lease        "For Lease"
sale-lease   "For Sale & Lease"
```
**Note:** SQL currently has only 3 (sale, rent, lease) - missing "sale-lease"

### Property Types (15 options)
```
Land & Development:
  land              "Land"
  house             "House"
  villa             "Villa"
  pool-villa        "Pool Villa"

Residential:
  apartment         "Apartment"
  condo             "Condominium"
  townhouse         "Townhouse"
  penthouse         "Penthouse"

Commercial:
  office            "Office"
  shop              "Shop"
  warehouse         "Warehouse"
  business          "Business"

Hospitality:
  resort            "Resort"
  hotel             "Hotel"

Other:
  other             "Other"
```

### Land Size Units (5 options)
```
sqm               "Square Meters" (International)
sqft              "Square Feet" (International)
rai               "Rai" (Thai: 1 rai = 1600 sqm)
ngan              "Ngan" (Thai: 1 ngan = 400 sqm)
wah               "Wah" (Thai: 1 wah = 4 sqm)
```

### Property Furnished (3 options)
```
fully             "Fully Furnished"
partially         "Partially Furnished"
unfurnished       "Unfurnished"
```

### Property Condition (5 options)
```
new               "New"
excellent         "Excellent"
good              "Good"
fair              "Fair"
needs_renovation  "Needs Renovation"
```

### Property Directions (8 options)
```
Cardinal:
  north             "North"
  south             "South"
  east              "East"
  west              "West"

Intercardinal:
  northeast         "Northeast"
  northwest         "Northwest"
  southeast         "Southeast"
  southwest         "Southwest"
```

### Currencies (3 options)
```
THB               "Thai Baht"
USD               "US Dollar"
EUR               "Euro"
```

### Ownership Types (3 options)
```
freehold          "Freehold"
leasehold         "Leasehold"
company           "Company Ownership"
```

### Price Trends (3 options)
```
rising            "Rising"
stable            "Stable"
falling           "Falling"
```

### Distance Units (3 options)
```
km                "Kilometers"
m                 "Meters"
mi                "Miles"
```

### Road Access (4 options)
```
main_road         "On Main Road"
private_road      "Private Road Access"
paved_road        "Paved Road Access"
quiet_cul_de_sac  "Quiet Cul-de-sac"
```

### Contact Preferences (5+ options)
```
phone             "Phone"
email             "Email"
line              "Line"
whatsapp          "WhatsApp"
telegram          "Telegram"
```

### Fee Frequencies (4 options)
```
monthly           "Monthly"
quarterly         "Quarterly"
yearly            "Yearly"
one_time          "One Time"
```

### Amenities

#### Interior Amenities (47 options)
```
Climate Control:
  air_conditioning, ceiling_fans, central_heating, underfloor_heating

Storage & Furniture:
  built_in_wardrobes, walk_in_closet, storage_room, wine_cellar

Kitchen Features:
  kitchen_island, european_kitchen, dishwasher, microwave, oven, wine_fridge

Appliances:
  washing_machine, dryer, coffee_machine

Flooring & Features:
  hardwood_floors, marble_floors, terrazzo_floors, fireplace, high_ceilings

Entertainment:
  cinema_room, smart_tv, sound_system

Wellness:
  sauna, jacuzzi_indoor, yoga_room
```

#### Exterior Amenities (24 options)
```
Pool & Water Features:
  private_pool, infinity_pool, saltwater_pool, pool_heating, jacuzzi_outdoor, plunge_pool

Outdoor Living:
  terrace, balcony, rooftop_terrace, outdoor_dining, bbq_area, outdoor_kitchen, cabana

Gardens & Landscaping:
  private_garden, tropical_garden, landscaped_garden, herb_garden

Parking & Storage:
  garage, carport, parking_space, boat_mooring

Recreation:
  tennis_court_private, yoga_deck, outdoor_gym, putting_green
```

#### Building Amenities (24 options)
```
Security & Access:
  24h_security, security_cameras, gated_community, key_card_access, intercom_system

Building Features:
  elevator, concierge, reception, valet_parking

Shared Recreation:
  swimming_pool_shared, fitness_center, spa_facilities, tennis_court, squash_court, sauna_shared

Business & Social:
  business_center, meeting_rooms, conference_room, library, co_working_space

Lifestyle:
  rooftop_garden, rooftop_bar, restaurant_onsite, kids_playground, pet_area
```

#### Utilities (13 options)
```
Basic Utilities:
  electricity, water_supply, gas_connection, sewage_system

Internet & Communication:
  fiber_internet, cable_tv, satellite_tv, landline_phone

Climate & Comfort:
  central_air, hot_water, water_heater

Security & Safety:
  alarm_system, fire_safety, backup_generator
```

#### Location Advantages (45 options)
```
Waterfront & Views:
  beachfront, beach_access_private, near_beach_walkable, sea_view, mountain_view, 
  jungle_view, lakefront, riverfront, sunset_view, sunrise_view

Road Access & Site Placement:
  on_main_road, private_road_access, paved_road_access, quiet_cul_de_sac, 
  corner_plot, gated_community

Proximity Highlights:
  near_pier_ferry, near_marina, near_airport, near_town_center, near_night_market, 
  near_beach_club

Daily Convenience:
  near_convenience_store, near_supermarket, near_international_school, 
  near_hospital_clinic

Nature & Leisure:
  near_national_park_waterfall, near_hiking_trails, near_yoga_wellness

Lifestyle:
  near_cafes_restaurants, near_nightlife, family_friendly_neighborhood
```

---

## Room Counts Schema

Granular room tracking for detailed property specifications:

```
bedrooms: number
bathrooms: number
living_rooms: number
kitchens: number
dining_rooms: number
offices: number
storage_rooms: number
maid_rooms: number
guest_rooms: number
```

---

## Field Size Constraints

```
title: 200 characters max
description: 5000 characters max
seo_title: 60 characters max
seo_description: 160 characters max
images: 30 maximum
languages: ["en", "th", "ru", "zh", "de", "fr"]
```

---

## Database Indexes

The V2 schema includes 12 strategic indexes:

**Primary Indexes:**
- `is_published` - For published listings queries
- `transaction_type` - For filtering by sale/rent/lease
- `property_type` - For filtering by property category
- `created_by` - For user's properties queries
- `deleted_at` - For soft delete queries
- `is_featured` - For featured listings
- `listing_priority DESC` - For sorting featured properties

**JSONB Indexes (GIN):**
- `location_details` - For location-based searches
- `physical_specs` - For room/size based searches
- `amenities` - For amenity filtering
- `tags` - For tag-based searches

---

## Key Differences: Property V1 vs V2

### Data Flexibility
- **V1**: Simple flat structure, everything in metadata
- **V2**: Structured JSONB with clear organization

### Amenities Management
- **V1**: Hard to query, custom list in metadata
- **V2**: Pre-defined catalogues (150+ options), easy to filter/search

### Location Data
- **V1**: Simple region/area in JSONB
- **V2**: Hierarchical (region→district→sub-district) + proximity details + transportation info

### Multi-language Support
- **V1**: None (single language)
- **V2**: 6 languages via dedicated translation table

### Legal Compliance
- **V1**: No ownership/legal tracking
- **V2**: Ownership type, foreign quota flags

### Investment Features
- **V1**: None
- **V2**: Rental yield, price trends for investor targeting

### Pricing
- **V1**: Single price for all transaction types
- **V2**: Separate prices for sale/rent/lease + price_per_unit

---

## Category Distribution

### By Property Type
```
Residential (6 types):
  - house, villa, pool-villa, apartment, condo, townhouse, penthouse

Commercial (4 types):
  - office, shop, warehouse, business

Land & Development (1):
  - land

Hospitality (2):
  - resort, hotel

Other (1):
  - other
```

### By Transaction Type
```
Primary (3):
  - sale (buy/ownership)
  - rent (short-term, furnished)
  - lease (long-term, unfurnished)

Hybrid (1 - in TS, not SQL):
  - sale-lease (can do both)
```

### By Ownership Model
```
Individual:
  - freehold (full ownership)

Rental/Time-bound:
  - leasehold (time-limited)

Corporate:
  - company (company ownership structure)
```

---

## Migration Path: V1 → V2

### Legacy Compatibility Fields
```
legacy_land_size: NUMERIC(15,2)
legacy_land_size_unit: ENUM
legacy_metadata: JSONB
```

These fields allow gradual migration from V1. The `legacy_metadata` can store V1's entire metadata object while new V2 data is being populated.

### Missing SQL Field
**Note:** `transaction_type` enum in SQL is missing `"sale-lease"` option. TypeScript supports it, but database doesn't. This should be added:
```sql
ALTER TYPE bestays_property2_transaction_type ADD VALUE 'sale-lease';
```

---

## Data Integrity Features

### Checks & Constraints
```
title: max 200 chars
description: max 5000 chars
seo_title: max 60 chars
seo_description: max 160 chars
sale_price, rent_price, lease_price: >= 0
price_per_unit: >= 0
listing_priority: >= 0
rental_yield: >= 0
```

### Foreign Keys
```
created_by → auth.users.id
updated_by → auth.users.id
property_id (translations) → bestays_properties_v2.id
```

### Unique Constraints
```
Translations table: UNIQUE(property_id, lang_code, field)
```

---

## Usage Recommendations for FastAPI/SvelteKit

### Backend (FastAPI)

1. **Use Pydantic models** for each JSONB section:
   ```python
   class PhysicalSpecs(BaseModel):
       rooms: Optional[RoomCounts]
       dimensions: Optional[Dimensions]
       building_specs: Optional[BuildingSpecs]
   ```

2. **Create serialization helpers** for JSONB fields

3. **Implement soft deletes** - check `deleted_at` in queries

4. **Use transaction filters** - separate endpoints for sale/rent/lease

5. **Leverage indexes** - sort by listing_priority, filter by is_published

### Frontend (SvelteKit)

1. **Build component library** for amenity selection (150+ options)

2. **Implement location hierarchies** (region → district → sub-district)

3. **Support multi-image upload** (max 30)

4. **Add translation UI** for 6 languages

5. **Create filtered search** - property type, transaction type, amenities

---

## Statistics

- **Total Enumerated Values:** 150+
- **Amenity Options:** 108 (interior: 47, exterior: 24, building: 24, utilities: 13)
- **Location Advantages:** 45
- **Property Types:** 15
- **JSONB Fields:** 5 (physical_specs, location_details, amenities, policies, contact_info)
- **Indexable Fields:** 12
- **Translatable Fields:** 13
- **Supported Languages:** 6
- **Max Images:** 30
- **Max Image Size Limit:** Not specified in schema

---

## Schema Validation

TypeScript schemas are defined in:
```
/src/apps/bestays-web/entities/property2/types/
├── property.ts (main schema)
├── property-create.ts (creation schema)
├── property-listing.ts (listing view)
├── physical-specs.ts
├── location-details.ts
├── amenity.ts
├── policies.ts
├── contact-info.ts
├── rooms-count.ts
├── area-measurment.ts
└── catalogue/ (45+ files with enumerations)
```

All use Zod for runtime validation.

---

## Implementation Status

- [x] TypeScript schemas defined (property2/types/)
- [x] SQL schema implemented (2.property2-tables.sql)
- [x] Enums created (1.property2-enums.sql)
- [x] Views created (4.property2-views.sql)
- [x] RLS policies configured (3.property2-rls.sql)
- [x] Catalogues with 150+ values
- [x] Translation table for 6 languages
- [ ] **SQL needs update** - Add "sale-lease" to transaction_type enum
- [ ] Sample migration scripts (V1 → V2)
- [ ] API endpoint specifications
- [ ] Frontend UI components

---

## Related Files in Bestays Project

Once you start implementation, reference these files:
- `/Users/solo/Projects/_repos/react-workspace/src/apps/bestays-web/entities/property2/` - All TypeScript schemas
- `/Users/solo/Projects/_repos/react-workspace/src/apps/bestays-web/db/sql-2/` - All SQL schemas
- `/Users/solo/Projects/_repos/react-workspace/src/apps/bestays-web/entities/properties/` - V1 reference

---

## Conclusion

The Property2 (V2) schema is comprehensive, well-designed, and production-ready. It supports:
- Global property marketplace features
- Multi-language content
- Complex property attributes
- Investment analytics
- Legal/ownership tracking
- Flexible pricing models

**Next Steps for FastAPI/SvelteKit Migration:**
1. Review and update SQL enum (add "sale-lease")
2. Create Pydantic models from Zod schemas
3. Build API endpoints (CRUD operations)
4. Create SvelteKit forms and search filters
5. Implement property listing views
6. Add translation management UI
7. Build admin dashboard for property management


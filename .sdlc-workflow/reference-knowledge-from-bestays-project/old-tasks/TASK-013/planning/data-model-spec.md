# Data Model Specification: Property V2 Schema

**TASK:** TASK-013
**Story:** US-023
**Date:** 2025-11-09
**Author:** Claude Code (Coordinator)

---

## Overview

This document defines the complete database schema for Property V2 with hybrid localization. All SQL is production-ready and executable.

**Tables:**
1. `properties` - Main property data with JSONB fields
2. `property_translations` - Localized text (title, description, location)
3. `amenities` - Master amenity list
4. `amenity_translations` - Amenity names per locale
5. `policies` - Master policy list
6. `policy_translations` - Policy names/descriptions per locale

---

## Table Definitions

### 1. Properties Table

```sql
CREATE TABLE properties (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Fallback Content (EN)
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,

    -- Transaction & Type
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('rent', 'sale', 'lease')),
    property_type VARCHAR(50) NOT NULL CHECK (property_type IN (
        'villa', 'condo', 'apartment', 'townhouse', 'house',
        'commercial', 'land', 'office', 'retail', 'warehouse'
    )),

    -- Pricing (stored as smallest unit: satang for THB, cents for USD)
    rent_price BIGINT,  -- Monthly rent
    sale_price BIGINT,  -- One-time sale price
    lease_price BIGINT, -- Lease agreement price
    currency VARCHAR(3) NOT NULL DEFAULT 'THB' CHECK (currency IN ('THB', 'USD', 'EUR', 'GBP', 'JPY')),

    -- Physical Specifications (JSONB)
    physical_specs JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Structure: See "JSONB Structures" section below

    -- Location Details (JSONB)
    location_details JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Structure: See "JSONB Structures" section below

    -- Amenities (JSONB - references amenities.id)
    amenities JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Structure: {"interior": ["air_conditioning", "wifi"], "exterior": ["pool", "garden"]}

    -- Policies (JSONB - references policies.id + custom data)
    policies JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Structure: See "JSONB Structures" section below

    -- Contact Information (JSONB)
    contact_info JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Structure: {"phone": "+66812345678", "email": "owner@example.com", "line_id": "@bestays"}

    -- Media
    cover_image JSONB,  -- {"url": "https://...", "alt": "...", "width": 1200, "height": 800}
    images JSONB[] DEFAULT ARRAY[]::JSONB[],  -- Array of image objects

    -- Tags & Search
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],  -- ["pet-friendly", "near-bts", "luxury"]

    -- Future: Semantic Search (pgvector)
    description_embedding_en vector(1536),  -- OpenAI text-embedding-3-small
    description_embedding_th vector(1536),

    -- Publication Status
    is_published BOOLEAN NOT NULL DEFAULT false,
    is_featured BOOLEAN NOT NULL DEFAULT false,
    listing_priority INTEGER NOT NULL DEFAULT 0,  -- Higher = shown first

    -- Soft Delete
    deleted_at TIMESTAMP WITH TIME ZONE,

    -- Audit Trail
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    updated_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT valid_price_for_transaction CHECK (
        (transaction_type = 'rent' AND rent_price IS NOT NULL) OR
        (transaction_type = 'sale' AND sale_price IS NOT NULL) OR
        (transaction_type = 'lease' AND lease_price IS NOT NULL)
    ),
    CONSTRAINT positive_prices CHECK (
        (rent_price IS NULL OR rent_price > 0) AND
        (sale_price IS NULL OR sale_price > 0) AND
        (lease_price IS NULL OR lease_price > 0)
    ),
    CONSTRAINT valid_priority CHECK (listing_priority >= 0 AND listing_priority <= 999)
);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_properties_updated_at
    BEFORE UPDATE ON properties
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE properties IS 'Main properties table with hybrid localization (JSONB + translations table)';
COMMENT ON COLUMN properties.rent_price IS 'Monthly rent in smallest currency unit (satang/cents)';
COMMENT ON COLUMN properties.physical_specs IS 'JSONB: rooms, sizes, floors, year_built, etc.';
COMMENT ON COLUMN properties.amenities IS 'JSONB: amenity IDs categorized by type (interior/exterior/building/area)';
COMMENT ON COLUMN properties.description_embedding_en IS 'Future: vector embedding for semantic search (English)';
```

---

### 2. Property Translations Table

```sql
CREATE TABLE property_translations (
    id SERIAL PRIMARY KEY,
    property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    locale VARCHAR(5) NOT NULL,  -- 'en', 'th', 'en-US', 'th-TH'
    field VARCHAR(100) NOT NULL,  -- 'title', 'description', 'location_province', etc.
    value TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT unique_translation UNIQUE (property_id, locale, field),
    CONSTRAINT valid_locale CHECK (locale ~ '^[a-z]{2}(-[A-Z]{2})?$'),  -- en, th, en-US, th-TH
    CONSTRAINT valid_field CHECK (field IN (
        'title',
        'description',
        'location_province',
        'location_district',
        'location_subdistrict',
        'location_address'
    ))
);

CREATE TRIGGER update_property_translations_updated_at
    BEFORE UPDATE ON property_translations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE property_translations IS 'Localized text for properties (title, description, location names)';
COMMENT ON COLUMN property_translations.field IS 'Which property field is being translated';
COMMENT ON COLUMN property_translations.value IS 'Translated text content';
```

---

### 3. Amenities Table

```sql
CREATE TABLE amenities (
    id VARCHAR(100) PRIMARY KEY,  -- 'air_conditioning', 'wifi', 'pool'
    category VARCHAR(50) NOT NULL CHECK (category IN ('interior', 'exterior', 'building', 'area')),
    icon VARCHAR(100),  -- 'mdi:air-conditioner', 'mdi:wifi', etc.
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER update_amenities_updated_at
    BEFORE UPDATE ON amenities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE amenities IS 'Master list of all available amenities (reusable across properties)';
COMMENT ON COLUMN amenities.id IS 'Snake_case identifier used in properties.amenities JSONB';
COMMENT ON COLUMN amenities.category IS 'Amenity grouping for UI display';
```

---

### 4. Amenity Translations Table

```sql
CREATE TABLE amenity_translations (
    id SERIAL PRIMARY KEY,
    amenity_id VARCHAR(100) NOT NULL REFERENCES amenities(id) ON DELETE CASCADE,
    locale VARCHAR(5) NOT NULL,
    name VARCHAR(255) NOT NULL,  -- Translated amenity name
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT unique_amenity_translation UNIQUE (amenity_id, locale),
    CONSTRAINT valid_locale_amenity CHECK (locale ~ '^[a-z]{2}(-[A-Z]{2})?$')
);

CREATE TRIGGER update_amenity_translations_updated_at
    BEFORE UPDATE ON amenity_translations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE amenity_translations IS 'Translated names for amenities (displayed in frontend)';
```

---

### 5. Policies Table

```sql
CREATE TABLE policies (
    id VARCHAR(100) PRIMARY KEY,  -- 'lease_duration', 'deposit_months', 'pets_allowed'
    category VARCHAR(50) NOT NULL CHECK (category IN ('lease_terms', 'house_rules', 'payment')),
    data_type VARCHAR(20) NOT NULL CHECK (data_type IN ('boolean', 'integer', 'text', 'select')),
    is_active BOOLEAN NOT NULL DEFAULT true,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER update_policies_updated_at
    BEFORE UPDATE ON policies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE policies IS 'Master list of policy types (reusable across properties)';
COMMENT ON COLUMN policies.data_type IS 'Expected value type in properties.policies JSONB';
```

---

### 6. Policy Translations Table

```sql
CREATE TABLE policy_translations (
    id SERIAL PRIMARY KEY,
    policy_id VARCHAR(100) NOT NULL REFERENCES policies(id) ON DELETE CASCADE,
    locale VARCHAR(5) NOT NULL,
    name VARCHAR(255) NOT NULL,  -- Translated policy name
    description TEXT,  -- Optional description/help text
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT unique_policy_translation UNIQUE (policy_id, locale),
    CONSTRAINT valid_locale_policy CHECK (locale ~ '^[a-z]{2}(-[A-Z]{2})?$')
);

CREATE TRIGGER update_policy_translations_updated_at
    BEFORE UPDATE ON policy_translations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE policy_translations IS 'Translated names and descriptions for policies';
```

---

## JSONB Structures

### physical_specs

```json
{
  "rooms": {
    "bedrooms": 3,
    "bathrooms": 2,
    "living_rooms": 1,
    "kitchens": 1,
    "dining_rooms": 1,
    "maid_rooms": 1,
    "parking_spaces": 2
  },
  "sizes": {
    "usable_area_sqm": 180.5,
    "land_area_sqm": 250.0,
    "building_area_sqm": 200.0
  },
  "floors": {
    "total_floors": 2,
    "property_floor": null
  },
  "year_built": 2020,
  "furnishing": "fully_furnished",
  "condition": "excellent"
}
```

**Field Descriptions:**
- `rooms` - Room counts (all integers, nullable)
- `sizes` - Areas in square meters (float, nullable)
- `floors.total_floors` - Total floors in building (for houses/villas)
- `floors.property_floor` - Which floor unit is on (for condos)
- `furnishing` - Enum: `unfurnished`, `partially_furnished`, `fully_furnished`
- `condition` - Enum: `excellent`, `good`, `fair`, `needs_renovation`

---

### location_details

```json
{
  "coordinates": {
    "latitude": 13.7563,
    "longitude": 100.5018
  },
  "administrative": {
    "province_id": "bangkok",
    "district_id": "phaya_thai",
    "subdistrict_id": "sam_sen_nai",
    "postal_code": "10400"
  },
  "address": {
    "house_number": "123/45",
    "street": "Phahonyothin Road",
    "soi": "Ari 1",
    "moo": null
  },
  "nearby_landmarks": [
    {"type": "bts", "name": "Ari Station", "distance_km": 0.5},
    {"type": "mall", "name": "Central Ladprao", "distance_km": 2.0},
    {"type": "hospital", "name": "Phyathai 2 Hospital", "distance_km": 1.5}
  ]
}
```

**Field Descriptions:**
- `coordinates` - GPS coordinates (WGS84)
- `administrative` - Thai administrative divisions (IDs reference master data)
- `address` - Street address components
- `nearby_landmarks` - Points of interest with distances

---

### amenities

```json
{
  "interior": ["air_conditioning", "wifi", "kitchen_appliances", "washing_machine"],
  "exterior": ["pool", "garden", "balcony"],
  "building": ["elevator", "security_24h", "fitness_center", "parking"],
  "area": ["near_bts", "near_mall", "near_school"]
}
```

**Field Descriptions:**
- Each category contains array of amenity IDs (references `amenities.id`)
- Frontend translates IDs using `amenity_translations` table
- Empty categories can be omitted or set to `[]`

---

### policies

```json
{
  "lease_terms": {
    "lease_duration_months": 12,
    "deposit_months": 2,
    "advance_payment_months": 1,
    "minimum_lease_months": 6
  },
  "house_rules": {
    "pets_allowed": false,
    "smoking_allowed": false,
    "guests_allowed": true,
    "parties_allowed": false
  },
  "payment": {
    "payment_methods": ["bank_transfer", "cash", "check"],
    "utility_bills_included": false,
    "internet_included": true
  }
}
```

**Field Descriptions:**
- Each category contains key-value pairs matching `policies.id`
- Values match `policies.data_type` (boolean, integer, text, select)
- Frontend translates policy names using `policy_translations` table

---

### contact_info

```json
{
  "phone": "+66812345678",
  "email": "owner@example.com",
  "line_id": "@bestays",
  "whatsapp": "+66812345678",
  "wechat": null,
  "preferred_contact": "line",
  "available_hours": "09:00-18:00 Mon-Fri"
}
```

---

### cover_image / images

```json
{
  "url": "https://cdn.bestays.app/properties/uuid/cover.jpg",
  "alt": "Beautiful villa with pool",
  "width": 1200,
  "height": 800,
  "format": "jpg",
  "size_bytes": 245678
}
```

**Note:** `images` column is `JSONB[]` (array of image objects)

---

## Sample Data

### Properties (EN fallback + Thai translations)

```sql
-- Insert property
INSERT INTO properties (
    id,
    title,
    description,
    transaction_type,
    property_type,
    rent_price,
    currency,
    physical_specs,
    location_details,
    amenities,
    policies,
    contact_info,
    cover_image,
    tags,
    is_published,
    is_featured,
    listing_priority
) VALUES (
    'e3b0c442-98fc-4c83-b3e5-f1c6e2d3a4b5',
    'Modern Villa with Private Pool',  -- EN fallback
    'Beautiful 3-bedroom villa in Ari area. Fully furnished with modern appliances.',
    'rent',
    'villa',
    3000000,  -- 30,000 THB (stored as satang)
    'THB',
    '{
        "rooms": {"bedrooms": 3, "bathrooms": 2, "parking_spaces": 2},
        "sizes": {"usable_area_sqm": 180.5, "land_area_sqm": 250.0},
        "floors": {"total_floors": 2},
        "year_built": 2020,
        "furnishing": "fully_furnished"
    }'::jsonb,
    '{
        "coordinates": {"latitude": 13.7563, "longitude": 100.5018},
        "administrative": {"province_id": "bangkok", "district_id": "phaya_thai", "postal_code": "10400"}
    }'::jsonb,
    '{
        "interior": ["air_conditioning", "wifi", "kitchen_appliances"],
        "exterior": ["pool", "garden"],
        "building": ["security_24h", "parking"]
    }'::jsonb,
    '{
        "lease_terms": {"lease_duration_months": 12, "deposit_months": 2},
        "house_rules": {"pets_allowed": false, "smoking_allowed": false}
    }'::jsonb,
    '{
        "phone": "+66812345678",
        "line_id": "@bestays",
        "preferred_contact": "line"
    }'::jsonb,
    '{
        "url": "https://cdn.bestays.app/villa-123/cover.jpg",
        "alt": "Modern villa exterior",
        "width": 1200,
        "height": 800
    }'::jsonb,
    ARRAY['pet-friendly', 'near-bts', 'luxury'],
    true,
    true,
    10
);

-- Insert Thai translations
INSERT INTO property_translations (property_id, locale, field, value) VALUES
    ('e3b0c442-98fc-4c83-b3e5-f1c6e2d3a4b5', 'th', 'title', 'วิลล่าโมเดิร์นพร้อมสระส่วนตัว'),
    ('e3b0c442-98fc-4c83-b3e5-f1c6e2d3a4b5', 'th', 'description', 'วิลล่า 3 ห้องนอนสวยงามในย่านอารีย์ ครบครันด้วยเครื่องใช้ไฟฟ้าทันสมัย'),
    ('e3b0c442-98fc-4c83-b3e5-f1c6e2d3a4b5', 'th', 'location_province', 'กรุงเทพมหานคร'),
    ('e3b0c442-98fc-4c83-b3e5-f1c6e2d3a4b5', 'th', 'location_district', 'พญาไท');
```

### Amenities with Translations

```sql
-- Insert amenities
INSERT INTO amenities (id, category, icon, sort_order) VALUES
    ('air_conditioning', 'interior', 'mdi:air-conditioner', 1),
    ('wifi', 'interior', 'mdi:wifi', 2),
    ('pool', 'exterior', 'mdi:pool', 1),
    ('garden', 'exterior', 'mdi:flower', 2),
    ('security_24h', 'building', 'mdi:security', 1);

-- Insert translations
INSERT INTO amenity_translations (amenity_id, locale, name) VALUES
    ('air_conditioning', 'en', 'Air Conditioning'),
    ('air_conditioning', 'th', 'เครื่องปรับอากาศ'),
    ('wifi', 'en', 'WiFi'),
    ('wifi', 'th', 'ไวไฟ'),
    ('pool', 'en', 'Swimming Pool'),
    ('pool', 'th', 'สระว่ายน้ำ'),
    ('garden', 'en', 'Garden'),
    ('garden', 'th', 'สวน'),
    ('security_24h', 'en', '24/7 Security'),
    ('security_24h', 'th', 'รักษาความปลอดภัย 24 ชม.');
```

### Policies with Translations

```sql
-- Insert policies
INSERT INTO policies (id, category, data_type, sort_order) VALUES
    ('pets_allowed', 'house_rules', 'boolean', 1),
    ('smoking_allowed', 'house_rules', 'boolean', 2),
    ('lease_duration_months', 'lease_terms', 'integer', 1),
    ('deposit_months', 'lease_terms', 'integer', 2);

-- Insert translations
INSERT INTO policy_translations (policy_id, locale, name, description) VALUES
    ('pets_allowed', 'en', 'Pets Allowed', 'Whether pets are allowed in the property'),
    ('pets_allowed', 'th', 'อนุญาตให้เลี้ยงสัตว์', 'อนุญาตให้เลี้ยงสัตว์ในทรัพย์สินหรือไม่'),
    ('smoking_allowed', 'en', 'Smoking Allowed', 'Whether smoking is allowed in the property'),
    ('smoking_allowed', 'th', 'อนุญาตให้สูบบุหรี่', 'อนุญาตให้สูบบุหรี่ในทรัพย์สินหรือไม่'),
    ('lease_duration_months', 'en', 'Lease Duration', 'Contract duration in months'),
    ('lease_duration_months', 'th', 'ระยะเวลาการเช่า', 'ระยะเวลาสัญญาเช่าเป็นเดือน'),
    ('deposit_months', 'en', 'Security Deposit', 'Security deposit in months of rent'),
    ('deposit_months', 'th', 'เงินประกัน', 'เงินประกันเป็นจำนวนเดือนของค่าเช่า');
```

---

## Query Examples

### Get Property with Thai Translations

```sql
SELECT
    p.*,
    json_object_agg(
        t.field, t.value
    ) FILTER (WHERE t.locale = 'th') as translations_th
FROM properties p
LEFT JOIN property_translations t
    ON t.property_id = p.id AND t.locale = 'th'
WHERE p.id = 'e3b0c442-98fc-4c83-b3e5-f1c6e2d3a4b5'
GROUP BY p.id;
```

### Search Properties with Filters

```sql
SELECT p.*,
    json_object_agg(t.field, t.value) FILTER (WHERE t.locale = 'th') as translations_th
FROM properties p
LEFT JOIN property_translations t ON t.property_id = p.id AND t.locale = 'th'
WHERE
    p.is_published = true
    AND p.deleted_at IS NULL
    AND p.transaction_type = 'rent'
    AND p.rent_price BETWEEN 2000000 AND 5000000  -- 20k-50k THB
    AND p.physical_specs->'rooms'->>'bedrooms' = '3'
    AND p.amenities->'interior' @> '["wifi", "air_conditioning"]'  -- Has both
GROUP BY p.id
ORDER BY p.listing_priority DESC, p.created_at DESC
LIMIT 24;
```

---

## Validation Rules

### Application-Level Validation

**Properties:**
- Title: 10-255 chars, required
- Description: 50-5000 chars, required
- Rent price: > 0 if transaction_type = 'rent'
- Physical specs: Must have at least `rooms.bedrooms` or `sizes.usable_area_sqm`
- Amenities: Each category array must contain valid amenity IDs
- Policies: Values must match policy.data_type

**Translations:**
- Locale: Must be ISO 639-1 (2 letters) or ISO 639-1 + ISO 3166-1 (en-US, th-TH)
- Value: Non-empty for required fields (title, description)

---

## Storage Estimates

**Assumptions:**
- 10,000 properties
- Average 3 locales per property (EN, TH, + 1 more)
- Average 10 amenities per property
- Average 8 policies per property

**Estimated Sizes:**
- `properties`: ~50 MB (5 KB per row)
- `property_translations`: ~15 MB (30 translations × 500 bytes)
- `amenities`: < 1 MB (100 amenities)
- `amenity_translations`: < 1 MB (100 × 10 locales)
- `policies`: < 1 MB (50 policies)
- `policy_translations`: < 1 MB (50 × 10 locales)
- **Indexes**: ~20 MB (GIN indexes are large)
- **Embeddings** (future): ~120 MB (2 × 1536 × 4 bytes × 10k)

**Total:** ~200 MB for 10k properties (excluding embeddings)

---

## Next Steps

1. ✅ Data model defined
2. → Create indexing strategy (indexing-strategy.md)
3. → Create migration spec (migration-spec.md)
4. → Create API design (api-design.md)

---

**References:**
- System Design: `system-design.md`
- PostgreSQL JSONB: https://www.postgresql.org/docs/current/datatype-json.html
- pgvector: https://github.com/pgvector/pgvector

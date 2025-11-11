# Property Modernization & Migration Plan

**Status:** 📝 DRAFT - Ready for Review
**Created:** 2025-11-06
**Purpose:** Plan migration from monolithic property structure to PostgreSQL subdomain architecture

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)
3. [Target Architecture](#target-architecture)
4. [Data Model Design](#data-model-design)
5. [Catalogue System](#catalogue-system)
6. [Migration Strategy](#migration-strategy)
7. [API Design](#api-design)
8. [Implementation Roadmap](#implementation-roadmap)

---

## Executive Summary

### Objective
Migrate from the legacy monolithic property structure (single property type with combined transaction types) to a modern PostgreSQL-based subdomain architecture with:
- **Separated subdomains:** rental, sale, lease, business, investment
- **Structured data:** Replace unstructured JSON with typed components
- **Catalogue-driven:** Type-safe dictionary values with metadata
- **Multi-pricing:** Separate price fields per transaction type
- **Internationalization:** Built-in translation support
- **Rich search:** Advanced filtering with 165+ amenity options

### Key Innovations from Property2
1. **Catalogue System** - 24 catalogues with 165+ amenity options
2. **Structured Components** - physical_specs, location_details, amenities, policies, contact_info
3. **Multi-Pricing** - Separate sale_price, rent_price, lease_price fields
4. **Room Breakdown** - 9 room types with flexible counts
5. **Location Advantages** - 81 structured location benefits
6. **Translations Table** - Field-level i18n support

### Migration Approach
**Shared Core + Subdomain Extensions** - Base `properties` table with subdomain-specific detail tables (rental_details, sale_details, etc.)

---

## Current State Analysis

### Legacy Implementation (`properties/`)

**Schema Limitations:**
```typescript
Property {
  // Unstructured data
  text?: string                    // Free-form description
  metadata?: string                // JSON string (unstructured)

  // Single pricing
  price?: { amount: number }       // Cannot distinguish sale vs rent price

  // Combined transactions
  transaction_type?: 'sale' | 'rent' | 'lease' | 'sale-lease'  // Problem: combined types

  // Basic property type
  property_type?: 'land' | 'house' | ... | 'other'

  // Limited structure
  location?: { region: string, area: string }
  land_size?: number
  land_size_unit?: 'sqm' | 'rai' | 'ngan' | 'wah'

  // No amenities, no rooms, no specs
}
```

**Key Problems:**
1. ❌ **Transaction Mixing** - "sale-lease" prevents subdomain separation
2. ❌ **Single Price** - Cannot store both sale and rent prices
3. ❌ **Unstructured Data** - metadata is JSON string, hard to query
4. ❌ **No Amenities** - Cannot filter by features
5. ❌ **No Room Counts** - No bedroom/bathroom filtering
6. ❌ **Limited Location** - Only region + area
7. ❌ **No Policies** - Missing lease terms, fees, rules
8. ❌ **No Contact Info** - No agent details
9. ❌ **No i18n** - Single language only
10. ❌ **No SEO** - Missing meta tags

### Refactored Approach (`property2/`)

**Structured Schema:**
```typescript
Property2 {
  // Multi-pricing
  sale_price?: number
  rent_price?: number
  lease_price?: number
  currency: 'THB' | 'USD' | 'EUR'

  // Structured components
  physical_specs?: PhysicalSpecs {
    rooms: { bedrooms: 3, bathrooms: 2, ... }
    dimensions: { total_area, living_area, land_area, ... }
    building_specs: { floors, year_built, condition, furnished, ... }
  }

  location_details?: LocationDetails {
    region, district, sub_district
    location_advantages: ['beachfront', 'sea_view', ...]
    proximity: { beach_distance, road_access, nearest_town, ... }
    transportation: { nearest_airport, public_transport, ... }
  }

  amenities?: Amenities {
    interior: [...],      // 47 options
    exterior: [...],      // 44 options
    building: [...],      // 44 options
    utilities: [...]      // 27 options
  }

  policies?: Policies {
    inclusions, restrictions, house_rules
    additional_fees: [...],
    lease_terms: { minimum_lease_months, security_deposit_months, ... }
  }

  contact_info?: ContactInfo {
    agent_name, agent_phone, agent_email, languages_spoken, ...
  }

  // Investment metrics
  rental_yield?: number
  price_trend?: 'rising' | 'stable' | 'falling'

  // SEO
  seo_title?: string
  seo_description?: string
  tags?: string[]
}
```

**Key Improvements:**
1. ✅ **Multi-Pricing** - Separate fields for each transaction type
2. ✅ **Structured Components** - Type-safe nested objects
3. ✅ **165+ Amenities** - Categorized, filterable
4. ✅ **Room Breakdown** - 9 room types
5. ✅ **Rich Location** - 81 location advantages
6. ✅ **Policies & Fees** - Complete lease terms
7. ✅ **Contact Details** - Full agent information
8. ✅ **SEO Ready** - Meta tags and keywords
9. ✅ **Investment Metrics** - Yield and trends
10. ✅ **Translation Ready** - Separate translations table

---

## Target Architecture

### Subdomain Model

```
PostgreSQL Database (bestays_production)
│
├── Core Tables (Shared)
│   ├── properties                  # Base property information
│   ├── property_images             # Media attachments
│   ├── property_translations       # i18n support
│   ├── users                       # Agents and owners
│   └── companies                   # Agencies
│
├── Catalogue Tables (Dictionary Values)
│   ├── cat_property_types
│   ├── cat_property_conditions
│   ├── cat_amenities_building
│   ├── cat_amenities_interior
│   ├── cat_amenities_exterior
│   ├── cat_utilities
│   ├── cat_location_advantages
│   └── ... (24 catalogue tables total)
│
└── Subdomain Tables (Transaction-Specific)
    ├── rental_details              # Short-term/long-term rentals
    ├── sale_details                # Properties for sale
    ├── lease_details               # Long-term leases
    ├── business_details            # Business-for-sale
    └── investment_details          # Investment projects
```

### Core Properties Table

**Purpose:** Shared base information for ALL property types and transactions

```sql
CREATE TABLE properties (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(250) UNIQUE NOT NULL,

    -- Basic Info
    title VARCHAR(200) NOT NULL,
    short_description VARCHAR(500),
    description TEXT,

    -- Classification
    property_type VARCHAR(50) NOT NULL,  -- From cat_property_types
    status VARCHAR(20) DEFAULT 'draft',  -- draft, active, inactive, sold, rented

    -- Physical Specs (JSONB for flexibility)
    physical_specs JSONB DEFAULT '{}',
    /*
    {
      "rooms": {
        "bedrooms": 3,
        "bathrooms": 2,
        "living_rooms": 1,
        "kitchens": 1,
        "dining_rooms": 1,
        "offices": 0,
        "storage_rooms": 1,
        "maid_rooms": 1,
        "guest_rooms": 0
      },
      "dimensions": {
        "total_area": { "value": 250, "unit": "sqm" },
        "living_area": { "value": 180, "unit": "sqm" },
        "usable_area": { "value": 220, "unit": "sqm" },
        "land_area": { "value": 600, "unit": "sqm" },
        "balcony_area": { "value": 30, "unit": "sqm" },
        "floor_area": { "value": 250, "unit": "sqm" }
      },
      "building_specs": {
        "floors": 2,
        "floor_level": null,
        "parking_spaces": 2,
        "year_built": 2018,
        "last_renovated": 2023,
        "facing_direction": "south",
        "condition": "excellent",
        "furnished": "fully"
      }
    }
    */

    -- Location
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    location_address TEXT,
    location_details JSONB DEFAULT '{}',
    /*
    {
      "region": "Phuket",
      "province": "Phuket",
      "district": "Kathu",
      "sub_district": "Kathu",
      "postal_code": "83120",
      "country": "TH",
      "location_advantages": ["beachfront", "sea_view", "near_beach"],
      "location_advantages_additional": ["quiet_area"],
      "proximity": {
        "beach_distance": { "value": 50, "unit": "m" },
        "road_access": "paved_access",
        "nearest_town": { "name": "Patong", "distance": 5, "unit": "km" }
      },
      "transportation": {
        "nearest_airport": { "name": "Phuket International", "distance": 30, "unit": "km" },
        "public_transport": ["songthaew", "taxi"],
        "parking_available": true
      }
    }
    */

    -- Amenities (Array of catalogue IDs)
    amenities_interior VARCHAR(50)[],       -- References cat_amenities_interior.id
    amenities_exterior VARCHAR(50)[],       -- References cat_amenities_exterior.id
    amenities_building VARCHAR(50)[],       -- References cat_amenities_building.id
    amenities_neighborhood VARCHAR(50)[],   -- References cat_location_advantages.id
    utilities VARCHAR(50)[],                -- References cat_utilities.id
    special_features TEXT[],                -- Free-form features

    -- Policies & Rules (JSONB)
    policies JSONB DEFAULT '{}',
    /*
    {
      "inclusions": ["utilities", "internet", "cable_tv"],
      "restrictions": ["no_pets", "no_smoking"],
      "house_rules": ["quiet_hours_22_08", "no_parties"],
      "additional_fees": [
        {
          "type": "maintenance_fee",
          "amount": 5000,
          "currency": "THB",
          "frequency": "monthly",
          "description": "Common area maintenance"
        }
      ]
    }
    */

    -- Contact Info (JSONB)
    contact_info JSONB DEFAULT '{}',
    /*
    {
      "agent_name": "John Smith",
      "agent_phone": "+66812345678",
      "agent_email": "john@agency.com",
      "agent_line_id": "johnsmith",
      "agent_whatsapp_id": "+66812345678",
      "agency_name": "Premium Real Estate",
      "languages_spoken": ["en", "th"],
      "preferred_contact": "phone",
      "availability_hours": "business_hours"
    }
    */

    -- Media
    cover_image_id UUID REFERENCES property_images(id),
    video_url VARCHAR(500),
    virtual_tour_url VARCHAR(500),

    -- Ownership & Legal
    title_deed VARCHAR(100),
    ownership_type VARCHAR(20),              -- freehold, leasehold, company
    foreign_quota BOOLEAN DEFAULT false,

    -- Business Metrics
    rental_yield DECIMAL(5, 2),              -- Percentage
    price_trend VARCHAR(20),                 -- rising, stable, falling

    -- SEO & Marketing
    seo_title VARCHAR(60),
    seo_description VARCHAR(160),
    tags VARCHAR(50)[],
    is_featured BOOLEAN DEFAULT false,
    listing_priority INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    inquiry_count INTEGER DEFAULT 0,

    -- Legacy Compatibility
    legacy_property_id VARCHAR(50),          -- Old Supabase ID
    legacy_land_size DECIMAL(10, 2),
    legacy_land_size_unit VARCHAR(10),
    legacy_metadata TEXT,                    -- Old JSON dump

    -- References
    agent_id UUID REFERENCES users(id) ON DELETE SET NULL,
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,

    -- System Fields
    is_published BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

-- Indexes
CREATE INDEX idx_properties_property_type ON properties(property_type);
CREATE INDEX idx_properties_status ON properties(status);
CREATE INDEX idx_properties_location ON properties USING GIST(
    ll_to_earth(location_lat, location_lng)
);
CREATE INDEX idx_properties_location_details ON properties USING GIN(location_details);
CREATE INDEX idx_properties_physical_specs ON properties USING GIN(physical_specs);
CREATE INDEX idx_properties_amenities_interior ON properties USING GIN(amenities_interior);
CREATE INDEX idx_properties_amenities_exterior ON properties USING GIN(amenities_exterior);
CREATE INDEX idx_properties_tags ON properties USING GIN(tags);
CREATE INDEX idx_properties_is_featured ON properties(is_featured, listing_priority DESC);
```

### Subdomain: Rental Details

**Purpose:** Short-term and long-term rental properties

```sql
CREATE TABLE rental_details (
    property_id UUID PRIMARY KEY REFERENCES properties(id) ON DELETE CASCADE,

    -- Rental Type
    rental_type VARCHAR(20) NOT NULL,        -- short_term, long_term, vacation

    -- Pricing
    price_daily DECIMAL(12, 2),
    price_weekly DECIMAL(12, 2),
    price_monthly DECIMAL(12, 2),
    price_yearly DECIMAL(12, 2),
    currency VARCHAR(3) DEFAULT 'THB',
    price_per_sqm DECIMAL(10, 2),

    -- Lease Terms
    minimum_stay_days INTEGER,
    maximum_stay_days INTEGER,
    minimum_lease_months INTEGER,
    maximum_lease_months INTEGER,
    notice_period_days INTEGER DEFAULT 30,
    security_deposit_months DECIMAL(4, 2),   -- Can be 1.5 months
    advance_payment_months INTEGER,

    -- Availability
    available_from DATE,
    available_until DATE,
    check_in_time TIME DEFAULT '14:00',
    check_out_time TIME DEFAULT '12:00',
    instant_booking BOOLEAN DEFAULT false,

    -- Additional Fees
    cleaning_fee DECIMAL(10, 2),
    utility_deposit DECIMAL(10, 2),
    key_deposit DECIMAL(10, 2),

    -- Occupancy
    max_guests INTEGER,
    extra_guest_fee DECIMAL(10, 2),

    -- System
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_rental_details_rental_type ON rental_details(rental_type);
CREATE INDEX idx_rental_details_price_monthly ON rental_details(price_monthly);
CREATE INDEX idx_rental_details_available_from ON rental_details(available_from);
```

### Subdomain: Sale Details

**Purpose:** Properties for sale (land, houses, condos, etc.)

```sql
CREATE TABLE sale_details (
    property_id UUID PRIMARY KEY REFERENCES properties(id) ON DELETE CASCADE,

    -- Pricing
    sale_price DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'THB',
    price_per_sqm DECIMAL(10, 2),

    -- Negotiation
    price_negotiable BOOLEAN DEFAULT false,
    minimum_offer DECIMAL(12, 2),

    -- Financing
    financing_available BOOLEAN DEFAULT false,
    down_payment_percentage DECIMAL(5, 2),
    installment_years INTEGER,

    -- Sale Status
    sale_status VARCHAR(20) DEFAULT 'available',  -- available, under_offer, sold, withdrawn
    listed_date DATE DEFAULT CURRENT_DATE,
    sold_date DATE,
    days_on_market INTEGER GENERATED ALWAYS AS (
        CASE WHEN sold_date IS NULL
        THEN CURRENT_DATE - listed_date
        ELSE sold_date - listed_date
        END
    ) STORED,

    -- Transfer & Legal
    transfer_fee_responsibility VARCHAR(20),      -- buyer, seller, split_50_50
    ready_for_transfer BOOLEAN DEFAULT true,
    possession_date DATE,

    -- System
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sale_details_sale_price ON sale_details(sale_price);
CREATE INDEX idx_sale_details_sale_status ON sale_details(sale_status);
CREATE INDEX idx_sale_details_days_on_market ON sale_details(days_on_market);
```

### Subdomain: Lease Details

**Purpose:** Long-term leases (typically commercial or long-term residential)

```sql
CREATE TABLE lease_details (
    property_id UUID PRIMARY KEY REFERENCES properties(id) ON DELETE CASCADE,

    -- Lease Type
    lease_type VARCHAR(20) NOT NULL,         -- residential, commercial, industrial

    -- Pricing
    lease_price_monthly DECIMAL(12, 2) NOT NULL,
    lease_price_yearly DECIMAL(12, 2),
    currency VARCHAR(3) DEFAULT 'THB',
    price_per_sqm DECIMAL(10, 2),

    -- Lease Terms
    minimum_lease_years INTEGER NOT NULL,
    maximum_lease_years INTEGER,
    lease_renewal_option BOOLEAN DEFAULT false,
    lease_renewal_terms TEXT,
    escalation_clause BOOLEAN DEFAULT false,
    escalation_percentage DECIMAL(5, 2),     -- Annual price increase %

    -- Deposits & Payments
    security_deposit_months DECIMAL(4, 2) NOT NULL,
    advance_payment_months INTEGER NOT NULL,
    key_money DECIMAL(12, 2),                -- One-time key money payment

    -- Responsibilities
    maintenance_responsibility VARCHAR(20),   -- landlord, tenant, shared
    repair_responsibility VARCHAR(20),
    insurance_required BOOLEAN DEFAULT false,

    -- Commercial Specific
    operating_hours VARCHAR(100),
    signage_allowed BOOLEAN DEFAULT true,
    modifications_allowed BOOLEAN DEFAULT false,
    sublease_allowed BOOLEAN DEFAULT false,

    -- Availability
    available_from DATE,

    -- System
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_lease_details_lease_type ON lease_details(lease_type);
CREATE INDEX idx_lease_details_lease_price_monthly ON lease_details(lease_price_monthly);
```

### Subdomain: Business Details

**Purpose:** Businesses for sale (restaurants, hotels, shops, etc.)

```sql
CREATE TABLE business_details (
    property_id UUID PRIMARY KEY REFERENCES properties(id) ON DELETE CASCADE,

    -- Business Type
    business_type VARCHAR(50) NOT NULL,      -- restaurant, hotel, shop, resort, etc.
    business_category VARCHAR(50),

    -- Business Info
    business_name VARCHAR(200),
    established_year INTEGER,
    license_number VARCHAR(100),
    licenses_included TEXT[],                -- List of included licenses

    -- Pricing
    sale_price DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'THB',
    price_negotiable BOOLEAN DEFAULT false,

    -- Financials
    annual_revenue DECIMAL(12, 2),
    annual_profit DECIMAL(12, 2),
    monthly_expenses DECIMAL(12, 2),
    revenue_trend VARCHAR(20),               -- growing, stable, declining

    -- Assets Included
    inventory_included BOOLEAN DEFAULT false,
    inventory_value DECIMAL(12, 2),
    equipment_included BOOLEAN DEFAULT false,
    equipment_value DECIMAL(12, 2),
    furniture_included BOOLEAN DEFAULT false,
    furniture_value DECIMAL(12, 2),

    -- Operations
    employees_count INTEGER,
    employees_included BOOLEAN DEFAULT false,
    operating_hours VARCHAR(100),
    seasonal_business BOOLEAN DEFAULT false,
    peak_season VARCHAR(50),

    -- Lease/Ownership
    property_included BOOLEAN DEFAULT false,  -- Is property ownership included?
    lease_remaining_years INTEGER,
    lease_monthly_cost DECIMAL(12, 2),

    -- Reason for Sale
    reason_for_sale TEXT,

    -- Handover
    training_included BOOLEAN DEFAULT false,
    training_days INTEGER,
    handover_period_days INTEGER DEFAULT 30,

    -- System
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_business_details_business_type ON business_details(business_type);
CREATE INDEX idx_business_details_sale_price ON business_details(sale_price);
CREATE INDEX idx_business_details_annual_revenue ON business_details(annual_revenue);
```

### Subdomain: Investment Details

**Purpose:** Investment projects and opportunities

```sql
CREATE TABLE investment_details (
    property_id UUID PRIMARY KEY REFERENCES properties(id) ON DELETE CASCADE,

    -- Investment Type
    investment_type VARCHAR(50) NOT NULL,    -- development, flip, rental_income, mixed_use
    project_stage VARCHAR(20) NOT NULL,      -- planning, construction, completed

    -- Pricing
    total_investment DECIMAL(12, 2) NOT NULL,
    minimum_investment DECIMAL(12, 2),
    currency VARCHAR(3) DEFAULT 'THB',

    -- Investment Structure
    investment_structure VARCHAR(50),        -- equity, debt, joint_venture, crowdfunding
    ownership_percentage DECIMAL(5, 2),
    number_of_units INTEGER,
    units_available INTEGER,

    -- Returns
    projected_roi DECIMAL(5, 2),             -- Percentage
    projected_annual_yield DECIMAL(5, 2),
    projected_capital_appreciation DECIMAL(5, 2),
    payback_period_years DECIMAL(4, 1),

    -- Timeline
    project_start_date DATE,
    project_completion_date DATE,
    estimated_construction_months INTEGER,

    -- Development Details
    developer_name VARCHAR(200),
    developer_track_record TEXT,
    architect_name VARCHAR(200),
    construction_company VARCHAR(200),

    -- Financials
    total_project_cost DECIMAL(12, 2),
    construction_cost DECIMAL(12, 2),
    land_cost DECIMAL(12, 2),
    soft_costs DECIMAL(12, 2),
    financing_secured BOOLEAN DEFAULT false,
    financing_amount DECIMAL(12, 2),

    -- Exit Strategy
    exit_strategy VARCHAR(50),               -- sell, hold, develop_further
    expected_exit_year INTEGER,

    -- Risk Assessment
    risk_level VARCHAR(20),                  -- low, medium, high
    risk_factors TEXT[],

    -- Documentation
    business_plan_url VARCHAR(500),
    financial_projections_url VARCHAR(500),
    legal_documents_url VARCHAR(500),

    -- System
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_investment_details_investment_type ON investment_details(investment_type);
CREATE INDEX idx_investment_details_project_stage ON investment_details(project_stage);
CREATE INDEX idx_investment_details_projected_roi ON investment_details(projected_roi);
```

---

## Catalogue System

### Catalogue Architecture

**Core Catalogue Table:**

```sql
CREATE TABLE catalogues (
    id VARCHAR(50) PRIMARY KEY,              -- e.g., 'amenities_interior'
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    icon VARCHAR(50),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE catalogue_options (
    id VARCHAR(50) PRIMARY KEY,              -- e.g., 'am_int_air_conditioning'
    catalogue_id VARCHAR(50) REFERENCES catalogues(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}',             -- Region-specific, property-type-specific
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(catalogue_id, id)
);

CREATE INDEX idx_catalogue_options_catalogue_id ON catalogue_options(catalogue_id);
CREATE INDEX idx_catalogue_options_is_active ON catalogue_options(is_active);
```

### 24 Catalogues to Implement

#### 1. Property Classification
```sql
-- Property Types
INSERT INTO catalogues VALUES ('property_types', 'Property Types', 'Core property classifications', 'classification', 'home', '{}');
INSERT INTO catalogue_options VALUES
  ('pt_land', 'property_types', 'Land', 'Vacant land plot', 'terrain', 10, true, '{}'),
  ('pt_house', 'property_types', 'House', 'Detached house', 'home', 20, true, '{}'),
  ('pt_villa', 'property_types', 'Villa', 'Luxury villa', 'villa', 30, true, '{}'),
  ('pt_pool_villa', 'property_types', 'Pool Villa', 'Villa with private pool', 'pool', 40, true, '{}'),
  ('pt_apartment', 'property_types', 'Apartment', 'Apartment unit', 'apartment', 50, true, '{}'),
  ('pt_condo', 'property_types', 'Condo', 'Condominium unit', 'domain', 60, true, '{}'),
  ('pt_townhouse', 'property_types', 'Townhouse', 'Townhouse unit', 'holiday_village', 70, true, '{}'),
  ('pt_penthouse', 'property_types', 'Penthouse', 'Luxury penthouse', 'stairs', 80, true, '{}'),
  ('pt_office', 'property_types', 'Office', 'Office space', 'business_center', 90, true, '{}'),
  ('pt_shop', 'property_types', 'Shop', 'Retail shop', 'storefront', 100, true, '{}'),
  ('pt_warehouse', 'property_types', 'Warehouse', 'Storage facility', 'warehouse', 110, true, '{}'),
  ('pt_business', 'property_types', 'Business', 'Operating business', 'business', 120, true, '{}'),
  ('pt_resort', 'property_types', 'Resort', 'Resort property', 'beach_access', 130, true, '{}'),
  ('pt_hotel', 'property_types', 'Hotel', 'Hotel property', 'hotel', 140, true, '{}'),
  ('pt_other', 'property_types', 'Other', 'Other property type', 'category', 150, true, '{}');

-- Property Conditions
INSERT INTO catalogues VALUES ('property_conditions', 'Property Conditions', 'Physical condition states', 'classification', 'build', '{}');
INSERT INTO catalogue_options VALUES
  ('pc_new', 'property_conditions', 'New', 'Brand new, never occupied', 'fiber_new', 10, true, '{}'),
  ('pc_excellent', 'property_conditions', 'Excellent', 'Like new, excellent maintenance', 'verified', 20, true, '{}'),
  ('pc_good', 'property_conditions', 'Good', 'Well maintained, minor wear', 'thumb_up', 30, true, '{}'),
  ('pc_fair', 'property_conditions', 'Fair', 'Shows wear, functional', 'info', 40, true, '{}'),
  ('pc_needs_renovation', 'property_conditions', 'Needs Renovation', 'Requires repairs or updates', 'handyman', 50, true, '{}');

-- Furnished Types
INSERT INTO catalogues VALUES ('property_furnished', 'Furnished Types', 'Furnishing levels', 'classification', 'chair', '{}');
INSERT INTO catalogue_options VALUES
  ('pf_fully', 'property_furnished', 'Fully Furnished', 'Move-in ready with all furniture', 'living', 10, true, '{}'),
  ('pf_partially', 'property_furnished', 'Partially Furnished', 'Basic furniture included', 'chair', 20, true, '{}'),
  ('pf_unfurnished', 'property_furnished', 'Unfurnished', 'No furniture included', 'disabled_by_default', 30, true, '{}');

-- Directions
INSERT INTO catalogues VALUES ('property_directions', 'Directions', 'Property orientations', 'classification', 'explore', '{}');
INSERT INTO catalogue_options VALUES
  ('pd_north', 'property_directions', 'North', 'Faces north', 'north', 10, true, '{}'),
  ('pd_south', 'property_directions', 'South', 'Faces south', 'south', 20, true, '{}'),
  ('pd_east', 'property_directions', 'East', 'Faces east', 'east', 30, true, '{}'),
  ('pd_west', 'property_directions', 'West', 'Faces west', 'west', 40, true, '{}'),
  ('pd_northeast', 'property_directions', 'Northeast', 'Faces northeast', 'north_east', 50, true, '{}'),
  ('pd_northwest', 'property_directions', 'Northwest', 'Faces northwest', 'north_west', 60, true, '{}'),
  ('pd_southeast', 'property_directions', 'Southeast', 'Faces southeast', 'south_east', 70, true, '{}'),
  ('pd_southwest', 'property_directions', 'Southwest', 'Faces southwest', 'south_west', 80, true, '{}');
```

#### 2. Amenities (165+ Options)

**Interior Amenities (47 options)**
```sql
INSERT INTO catalogues VALUES ('amenities_interior', 'Interior Amenities', 'Indoor features and appliances', 'amenities', 'living', '{}');

-- Climate Control
INSERT INTO catalogue_options VALUES
  ('am_int_air_conditioning', 'amenities_interior', 'Air Conditioning', 'Air conditioning units', 'ac_unit', 10, true, '{"category":"climate"}'),
  ('am_int_ceiling_fans', 'amenities_interior', 'Ceiling Fans', 'Ceiling fans installed', 'mode_fan', 20, true, '{"category":"climate"}'),
  ('am_int_heating', 'amenities_interior', 'Heating', 'Heating system', 'local_fire_department', 30, true, '{"category":"climate"}');

-- Kitchen
INSERT INTO catalogue_options VALUES
  ('am_int_kitchen', 'amenities_interior', 'Fully Equipped Kitchen', 'Complete kitchen with appliances', 'countertops', 40, true, '{"category":"kitchen"}'),
  ('am_int_refrigerator', 'amenities_interior', 'Refrigerator', 'Fridge/freezer', 'kitchen', 50, true, '{"category":"kitchen"}'),
  ('am_int_oven', 'amenities_interior', 'Oven', 'Cooking oven', 'oven_gen', 60, true, '{"category":"kitchen"}'),
  ('am_int_microwave', 'amenities_interior', 'Microwave', 'Microwave oven', 'microwave_gen', 70, true, '{"category":"kitchen"}'),
  ('am_int_dishwasher', 'amenities_interior', 'Dishwasher', 'Automatic dishwasher', 'dishwasher_gen', 80, true, '{"category":"kitchen"}'),
  ('am_int_washing_machine', 'amenities_interior', 'Washing Machine', 'Clothes washer', 'local_laundry_service', 90, true, '{"category":"appliances"}'),
  ('am_int_dryer', 'amenities_interior', 'Dryer', 'Clothes dryer', 'dry', 100, true, '{"category":"appliances"}');

-- Living
INSERT INTO catalogue_options VALUES
  ('am_int_wardrobes', 'amenities_interior', 'Built-in Wardrobes', 'Closet storage', 'checkroom', 110, true, '{"category":"storage"}'),
  ('am_int_tv', 'amenities_interior', 'TV', 'Television', 'tv', 120, true, '{"category":"entertainment"}'),
  ('am_int_wifi', 'amenities_interior', 'WiFi', 'Wireless internet', 'wifi', 130, true, '{"category":"connectivity"}');

-- ... (remaining 34 interior amenities)
```

**Exterior Amenities (44 options)**
```sql
INSERT INTO catalogues VALUES ('amenities_exterior', 'Exterior Amenities', 'Outdoor features', 'amenities', 'yard', '{}');

-- Pool & Water Features
INSERT INTO catalogue_options VALUES
  ('am_ext_private_pool', 'amenities_exterior', 'Private Pool', 'Private swimming pool', 'pool', 10, true, '{"category":"pool"}'),
  ('am_ext_jacuzzi', 'amenities_exterior', 'Jacuzzi', 'Hot tub/jacuzzi', 'hot_tub', 20, true, '{"category":"pool"}'),
  ('am_ext_pool_heating', 'amenities_exterior', 'Pool Heating', 'Heated pool', 'water_heater', 30, true, '{"category":"pool"}');

-- Outdoor Living
INSERT INTO catalogue_options VALUES
  ('am_ext_garden', 'amenities_exterior', 'Garden', 'Private garden', 'forest', 40, true, '{"category":"garden"}'),
  ('am_ext_terrace', 'amenities_exterior', 'Terrace', 'Outdoor terrace', 'balcony', 50, true, '{"category":"outdoor"}'),
  ('am_ext_balcony', 'amenities_exterior', 'Balcony', 'Balcony', 'balcony', 60, true, '{"category":"outdoor"}'),
  ('am_ext_bbq_area', 'amenities_exterior', 'BBQ Area', 'Barbecue facilities', 'outdoor_grill', 70, true, '{"category":"outdoor"}'),
  ('am_ext_outdoor_dining', 'amenities_exterior', 'Outdoor Dining', 'Outdoor dining area', 'deck', 80, true, '{"category":"outdoor"}');

-- ... (remaining 36 exterior amenities)
```

**Building Amenities (44 options)**
```sql
INSERT INTO catalogues VALUES ('amenities_building', 'Building Amenities', 'Building/complex facilities', 'amenities', 'apartment', '{}');

-- Security
INSERT INTO catalogue_options VALUES
  ('am_bld_24h_security', 'amenities_building', '24h Security', 'Round-the-clock security', 'shield', 10, true, '{"category":"security"}'),
  ('am_bld_cctv', 'amenities_building', 'CCTV', 'Surveillance cameras', 'videocam', 20, true, '{"category":"security"}'),
  ('am_bld_security_gate', 'amenities_building', 'Security Gate', 'Gated entry', 'gate', 30, true, '{"category":"security"}'),
  ('am_bld_key_card_access', 'amenities_building', 'Key Card Access', 'Electronic access control', 'key', 40, true, '{"category":"security"}');

-- Common Facilities
INSERT INTO catalogue_options VALUES
  ('am_bld_elevator', 'amenities_building', 'Elevator', 'Passenger lift', 'elevator', 50, true, '{"category":"facilities"}'),
  ('am_bld_gym', 'amenities_building', 'Gym', 'Fitness center', 'fitness_center', 60, true, '{"category":"facilities"}'),
  ('am_bld_communal_pool', 'amenities_building', 'Communal Pool', 'Shared swimming pool', 'pool', 70, true, '{"category":"facilities"}'),
  ('am_bld_spa', 'amenities_building', 'Spa', 'Spa facilities', 'spa', 80, true, '{"category":"facilities"}'),
  ('am_bld_restaurant', 'amenities_building', 'Restaurant', 'On-site restaurant', 'restaurant', 90, true, '{"category":"facilities"}');

-- ... (remaining 35 building amenities)
```

**Utilities (27 options)**
```sql
INSERT INTO catalogues VALUES ('utilities', 'Utilities', 'Basic utilities and services', 'amenities', 'bolt', '{}');

INSERT INTO catalogue_options VALUES
  ('ut_electricity', 'utilities', 'Electricity', 'Electrical power', 'bolt', 10, true, '{}'),
  ('ut_water', 'utilities', 'Water', 'Municipal water supply', 'water_drop', 20, true, '{}'),
  ('ut_internet', 'utilities', 'Internet', 'Broadband internet', 'language', 30, true, '{}'),
  ('ut_cable_tv', 'utilities', 'Cable TV', 'Cable television', 'tv', 40, true, '{}'),
  ('ut_phone_line', 'utilities', 'Phone Line', 'Landline telephone', 'call', 50, true, '{}'),
  ('ut_gas', 'utilities', 'Gas', 'Natural gas supply', 'local_gas_station', 60, true, '{}'),
  ('ut_sewage', 'utilities', 'Sewage', 'Sewage system', 'plumbing', 70, true, '{}'),
  ('ut_garbage_collection', 'utilities', 'Garbage Collection', 'Waste management', 'delete', 80, true, '{}');
  -- ... (remaining 19 utilities)
```

#### 3. Location Advantages (81 options)

```sql
INSERT INTO catalogues VALUES ('location_advantages', 'Location Advantages', 'Location benefits and proximity features', 'location', 'location_on', '{}');

-- Waterfront
INSERT INTO catalogue_options VALUES
  ('loc_beachfront', 'location_advantages', 'Beachfront', 'Direct beach access', 'beach_access', 10, true, '{"category":"waterfront"}'),
  ('loc_sea_view', 'location_advantages', 'Sea View', 'Ocean/sea views', 'water', 20, true, '{"category":"waterfront"}'),
  ('loc_near_beach', 'location_advantages', 'Near Beach', 'Walking distance to beach', 'directions_walk', 30, true, '{"category":"waterfront"}'),
  ('loc_lake_view', 'location_advantages', 'Lake View', 'Lake views', 'water', 40, true, '{"category":"waterfront"}'),
  ('loc_river_view', 'location_advantages', 'River View', 'River views', 'water', 50, true, '{"category":"waterfront"}');

-- Mountain & Nature
INSERT INTO catalogue_options VALUES
  ('loc_mountain_view', 'location_advantages', 'Mountain View', 'Mountain views', 'landscape', 60, true, '{"category":"nature"}'),
  ('loc_forest_view', 'location_advantages', 'Forest View', 'Forest/jungle views', 'park', 70, true, '{"category":"nature"}'),
  ('loc_near_national_park', 'location_advantages', 'Near National Park', 'Close to national park', 'nature_people', 80, true, '{"category":"nature"}');

-- Urban & Amenities
INSERT INTO catalogue_options VALUES
  ('loc_city_center', 'location_advantages', 'City Center', 'Central location', 'location_city', 90, true, '{"category":"urban"}'),
  ('loc_near_shopping', 'location_advantages', 'Near Shopping', 'Close to shopping centers', 'shopping_cart', 100, true, '{"category":"urban"}'),
  ('loc_near_restaurants', 'location_advantages', 'Near Restaurants', 'Dining options nearby', 'restaurant', 110, true, '{"category":"urban"}'),
  ('loc_near_nightlife', 'location_advantages', 'Near Nightlife', 'Bars and clubs nearby', 'nightlife', 120, true, '{"category":"urban"}');

-- Transportation
INSERT INTO catalogue_options VALUES
  ('loc_near_airport', 'location_advantages', 'Near Airport', 'Close to airport', 'local_airport', 130, true, '{"category":"transport"}'),
  ('loc_near_public_transport', 'location_advantages', 'Near Public Transport', 'Easy access to buses/trains', 'directions_bus', 140, true, '{"category":"transport"}'),
  ('loc_main_road_access', 'location_advantages', 'Main Road Access', 'Direct main road access', 'add_road', 150, true, '{"category":"transport"}');

-- Services
INSERT INTO catalogue_options VALUES
  ('loc_near_hospital', 'location_advantages', 'Near Hospital', 'Medical facilities nearby', 'local_hospital', 160, true, '{"category":"services"}'),
  ('loc_near_school', 'location_advantages', 'Near School', 'Schools nearby', 'school', 170, true, '{"category":"services"}'),
  ('loc_near_golf_course', 'location_advantages', 'Near Golf Course', 'Golf facilities nearby', 'golf_course', 180, true, '{"category":"lifestyle"}');

-- Character
INSERT INTO catalogue_options VALUES
  ('loc_quiet_area', 'location_advantages', 'Quiet Area', 'Peaceful neighborhood', 'self_improvement', 190, true, '{"category":"character"}'),
  ('loc_private_location', 'location_advantages', 'Private Location', 'Secluded and private', 'lock', 200, true, '{"category":"character"}'),
  ('loc_gated_community', 'location_advantages', 'Gated Community', 'Secure gated area', 'fence', 210, true, '{"category":"character"}');

-- ... (remaining 60 location advantages)
```

#### 4. Financial & Legal

```sql
-- Currencies
INSERT INTO catalogues VALUES ('currencies', 'Currencies', 'Supported currencies', 'financial', 'payments', '{}');
INSERT INTO catalogue_options VALUES
  ('cur_thb', 'currencies', 'THB', 'Thai Baht', '฿', 10, true, '{"symbol":"฿","code":"THB"}'),
  ('cur_usd', 'currencies', 'USD', 'US Dollar', '$', 20, true, '{"symbol":"$","code":"USD"}'),
  ('cur_eur', 'currencies', 'EUR', 'Euro', '€', 30, true, '{"symbol":"€","code":"EUR"}');

-- Ownership Types
INSERT INTO catalogues VALUES ('ownership_types', 'Ownership Types', 'Property ownership structures', 'legal', 'gavel', '{}');
INSERT INTO catalogue_options VALUES
  ('own_freehold', 'ownership_types', 'Freehold', 'Full ownership', 'verified_user', 10, true, '{}'),
  ('own_leasehold', 'ownership_types', 'Leasehold', 'Lease agreement', 'schedule', 20, true, '{}'),
  ('own_company', 'ownership_types', 'Company', 'Owned through company', 'business', 30, true, '{}');

-- Fee Frequencies
INSERT INTO catalogues VALUES ('fee_frequencies', 'Fee Frequencies', 'Payment frequencies', 'financial', 'event_repeat', '{}');
INSERT INTO catalogue_options VALUES
  ('freq_monthly', 'fee_frequencies', 'Monthly', 'Per month', 'event', 10, true, '{}'),
  ('freq_quarterly', 'fee_frequencies', 'Quarterly', 'Every 3 months', 'event_repeat', 20, true, '{}'),
  ('freq_yearly', 'fee_frequencies', 'Yearly', 'Per year', 'event_available', 30, true, '{}'),
  ('freq_one_time', 'fee_frequencies', 'One Time', 'Single payment', 'event_note', 40, true, '{}');

-- Price Trends
INSERT INTO catalogues VALUES ('price_trends', 'Price Trends', 'Market price trends', 'financial', 'trending_up', '{}');
INSERT INTO catalogue_options VALUES
  ('trend_rising', 'price_trends', 'Rising', 'Prices increasing', 'trending_up', 10, true, '{}'),
  ('trend_stable', 'price_trends', 'Stable', 'Prices stable', 'trending_flat', 20, true, '{}'),
  ('trend_falling', 'price_trends', 'Falling', 'Prices declining', 'trending_down', 30, true, '{}');
```

#### 5. Measurements

```sql
-- Land Size Units
INSERT INTO catalogues VALUES ('land_size_units', 'Land Size Units', 'Area measurement units', 'measurement', 'square_foot', '{}');
INSERT INTO catalogue_options VALUES
  ('unit_sqm', 'land_size_units', 'Square Meters', 'm²', 'square_foot', 10, true, '{"conversion_to_sqm":1}'),
  ('unit_sqft', 'land_size_units', 'Square Feet', 'ft²', 'square_foot', 20, true, '{"conversion_to_sqm":0.092903}'),
  ('unit_rai', 'land_size_units', 'Rai', 'ไร่ (Thai)', 'landscape', 30, true, '{"conversion_to_sqm":1600}'),
  ('unit_ngan', 'land_size_units', 'Ngan', 'งาน (Thai)', 'landscape', 40, true, '{"conversion_to_sqm":400}'),
  ('unit_wah', 'land_size_units', 'Wah', 'ตร.ว. (Thai)', 'landscape', 50, true, '{"conversion_to_sqm":4}');

-- Distance Units
INSERT INTO catalogues VALUES ('distance_units', 'Distance Units', 'Distance measurement units', 'measurement', 'straighten', '{}');
INSERT INTO catalogue_options VALUES
  ('dist_m', 'distance_units', 'Meters', 'm', 'straighten', 10, true, '{"conversion_to_m":1}'),
  ('dist_km', 'distance_units', 'Kilometers', 'km', 'straighten', 20, true, '{"conversion_to_m":1000}'),
  ('dist_mi', 'distance_units', 'Miles', 'mi', 'straighten', 30, true, '{"conversion_to_m":1609.34}');
```

#### 6. Contact & Availability

```sql
-- Contact Preferences
INSERT INTO catalogues VALUES ('contact_preferences', 'Contact Preferences', 'Preferred contact methods', 'contact', 'contact_phone', '{}');
INSERT INTO catalogue_options VALUES
  ('contact_phone', 'contact_preferences', 'Phone', 'Phone call', 'call', 10, true, '{}'),
  ('contact_email', 'contact_preferences', 'Email', 'Email message', 'email', 20, true, '{}'),
  ('contact_line', 'contact_preferences', 'LINE', 'LINE messenger', 'chat', 30, true, '{}'),
  ('contact_whatsapp', 'contact_preferences', 'WhatsApp', 'WhatsApp', 'message', 40, true, '{}');

-- Availability Hours
INSERT INTO catalogues VALUES ('availability_hours', 'Availability Hours', 'Agent availability times', 'contact', 'schedule', '{}');
INSERT INTO catalogue_options VALUES
  ('avail_business', 'availability_hours', 'Business Hours', '9AM - 6PM weekdays', 'schedule', 10, true, '{}'),
  ('avail_extended', 'availability_hours', 'Extended Hours', '8AM - 8PM daily', 'access_time', 20, true, '{}'),
  ('avail_24_7', 'availability_hours', '24/7', 'Anytime', 'schedule', 30, true, '{}'),
  ('avail_by_appointment', 'availability_hours', 'By Appointment', 'Schedule in advance', 'event', 40, true, '{}');
```

#### 7. Localization

```sql
-- Language Codes
INSERT INTO catalogues VALUES ('language_codes', 'Languages', 'Supported languages', 'localization', 'language', '{}');
INSERT INTO catalogue_options VALUES
  ('lang_en', 'language_codes', 'English', 'English', 'language', 10, true, '{"code":"en"}'),
  ('lang_th', 'language_codes', 'Thai', 'ไทย', 'language', 20, true, '{"code":"th"}'),
  ('lang_ru', 'language_codes', 'Russian', 'Русский', 'language', 30, true, '{"code":"ru"}'),
  ('lang_zh', 'language_codes', 'Chinese', '中文', 'language', 40, true, '{"code":"zh"}'),
  ('lang_de', 'language_codes', 'German', 'Deutsch', 'language', 50, true, '{"code":"de"}'),
  ('lang_fr', 'language_codes', 'French', 'Français', 'language', 60, true, '{"code":"fr"}');

-- Translation Fields
INSERT INTO catalogues VALUES ('translation_fields', 'Translation Fields', 'Translatable property fields', 'localization', 'translate', '{}');
INSERT INTO catalogue_options VALUES
  ('trans_title', 'translation_fields', 'Title', 'Property title', 'title', 10, true, '{}'),
  ('trans_short_description', 'translation_fields', 'Short Description', 'Brief description', 'short_text', 20, true, '{}'),
  ('trans_description', 'translation_fields', 'Description', 'Full description', 'description', 30, true, '{}'),
  ('trans_seo_title', 'translation_fields', 'SEO Title', 'SEO meta title', 'title', 40, true, '{}'),
  ('trans_seo_description', 'translation_fields', 'SEO Description', 'SEO meta description', 'description', 50, true, '{}');
```

### Catalogue Management API

**Endpoints:**

```typescript
// Get all catalogues
GET /api/catalogues

// Get single catalogue with options
GET /api/catalogues/{catalogue_id}

// Get options for specific catalogue
GET /api/catalogues/{catalogue_id}/options

// Get filtered options (by metadata)
GET /api/catalogues/{catalogue_id}/options?region=phuket&property_type=villa

// Admin: Create catalogue option
POST /api/admin/catalogues/{catalogue_id}/options

// Admin: Update catalogue option
PUT /api/admin/catalogues/{catalogue_id}/options/{option_id}

// Admin: Delete catalogue option
DELETE /api/admin/catalogues/{catalogue_id}/options/{option_id}
```

**Frontend Usage:**

```typescript
// Load amenities for property form
const interiorAmenities = await getCatalogueOptions('amenities_interior');

// Load filtered location advantages (Thailand-specific)
const locationAdvantages = await getCatalogueOptions('location_advantages', {
  metadata: { region: ['phuket', 'krabi', 'samui'] }
});

// Render checkbox list
interiorAmenities.options.map(option => (
  <Checkbox
    value={option.id}
    label={option.name}
    icon={option.icon}
    description={option.description}
  />
));
```

---

## Migration Strategy

### Phase 1: Database Setup (Week 1)

**Tasks:**
1. Create Alembic migration for new schema
2. Set up catalogue tables and seed data
3. Create core properties table
4. Create subdomain detail tables
5. Set up indexes and constraints

**Migration File:** `alembic/versions/001_property_modernization.py`

```python
"""Property modernization - Core tables

Revision ID: 001
Revises: previous_revision
Create Date: 2025-11-06
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create catalogues table
    op.create_table(
        'catalogues',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('category', sa.String(50)),
        sa.Column('icon', sa.String(50)),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'))
    )

    # Create catalogue_options table
    op.create_table(
        'catalogue_options',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('catalogue_id', sa.String(50), sa.ForeignKey('catalogues.id', ondelete='CASCADE')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('icon', sa.String(50)),
        sa.Column('sort_order', sa.Integer, server_default='0'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.UniqueConstraint('catalogue_id', 'id')
    )

    # Create properties table (see schema above)
    op.create_table('properties', ...)

    # Create subdomain tables
    op.create_table('rental_details', ...)
    op.create_table('sale_details', ...)
    op.create_table('lease_details', ...)
    op.create_table('business_details', ...)
    op.create_table('investment_details', ...)

    # Create indexes
    op.create_index('idx_properties_property_type', 'properties', ['property_type'])
    # ... (all indexes)

def downgrade():
    op.drop_table('investment_details')
    op.drop_table('business_details')
    op.drop_table('lease_details')
    op.drop_table('sale_details')
    op.drop_table('rental_details')
    op.drop_table('properties')
    op.drop_table('catalogue_options')
    op.drop_table('catalogues')
```

### Phase 2: Data Migration (Week 2)

**Strategy:** Migrate in batches, dual-write during transition

**Migration Script:** `scripts/migrate_legacy_properties.py`

```python
"""
Migrate legacy properties to new schema
"""

import asyncio
from typing import Dict, Any, List
from sqlalchemy import select, insert
from server.core.database import async_session
from server.models.property import Property, RentalDetails, SaleDetails
import json
import re

class PropertyMigrator:
    def __init__(self):
        self.batch_size = 100
        self.dry_run = False

    async def migrate_all(self):
        """Migrate all legacy properties"""
        # Get legacy properties
        legacy_properties = await self.fetch_legacy_properties()

        print(f"Found {len(legacy_properties)} legacy properties to migrate")

        for i in range(0, len(legacy_properties), self.batch_size):
            batch = legacy_properties[i:i + self.batch_size]
            await self.migrate_batch(batch)
            print(f"Migrated batch {i//self.batch_size + 1}")

    async def migrate_batch(self, batch: List[Dict]):
        """Migrate a batch of properties"""
        for legacy_prop in batch:
            try:
                # Transform legacy to new schema
                new_prop = await self.transform_property(legacy_prop)

                # Insert into new tables
                if not self.dry_run:
                    await self.insert_property(new_prop)
                else:
                    print(f"[DRY RUN] Would migrate: {legacy_prop['title']}")
            except Exception as e:
                print(f"Error migrating {legacy_prop['id']}: {e}")

    async def transform_property(self, legacy: Dict) -> Dict:
        """Transform legacy property to new schema"""

        # Extract transaction types
        transaction_types = self.parse_transaction_type(legacy['transaction_type'])

        # Parse metadata
        metadata = json.loads(legacy.get('metadata', '{}')) if isinstance(legacy.get('metadata'), str) else legacy.get('metadata', {})

        # Build base property
        new_prop = {
            'core': {
                'legacy_property_id': legacy['id'],
                'title': legacy.get('title', 'Untitled Property'),
                'short_description': self.extract_short_description(legacy.get('text', '')),
                'description': legacy.get('text', ''),
                'property_type': self.map_property_type(legacy.get('property_type')),
                'status': 'active' if legacy.get('is_published') else 'draft',

                # Location
                'location_lat': metadata.get('location', {}).get('lat'),
                'location_lng': metadata.get('location', {}).get('lng'),
                'location_details': self.build_location_details(legacy),

                # Physical specs
                'physical_specs': self.build_physical_specs(legacy, metadata),

                # Amenities (parse from text/metadata)
                'amenities_interior': self.extract_amenities(legacy, 'interior'),
                'amenities_exterior': self.extract_amenities(legacy, 'exterior'),
                'amenities_building': self.extract_amenities(legacy, 'building'),

                # Legacy fields
                'legacy_land_size': legacy.get('land_size'),
                'legacy_land_size_unit': legacy.get('land_size_unit'),
                'legacy_metadata': json.dumps(metadata),

                # System
                'created_at': legacy.get('created_at'),
                'updated_at': legacy.get('updated_at'),
                'agent_id': self.map_user_id(legacy.get('created_by')),
            },
            'transaction_types': transaction_types,
            'price': legacy.get('price', {}).get('amount', 0),
        }

        return new_prop

    def parse_transaction_type(self, transaction_type: str) -> List[str]:
        """Parse combined transaction types"""
        if not transaction_type:
            return ['sale']  # Default

        # Handle "sale-lease" -> ['sale', 'lease']
        if transaction_type == 'sale-lease':
            return ['sale', 'lease']

        return [transaction_type]

    def map_property_type(self, legacy_type: str) -> str:
        """Map legacy property types to new catalogues"""
        mapping = {
            'land': 'pt_land',
            'house': 'pt_house',
            'villa': 'pt_villa',
            'pool-villa': 'pt_pool_villa',
            'appartment': 'pt_apartment',  # Fix typo
            'apartment': 'pt_apartment',
            'condo': 'pt_condo',
            'townhouse': 'pt_townhouse',
            'penthouse': 'pt_penthouse',
            'office': 'pt_office',
            'shop': 'pt_shop',
            'warehouse': 'pt_warehouse',
            'business': 'pt_business',
            'resort': 'pt_resort',
            'hotel': 'pt_hotel',
            'other': 'pt_other',
        }
        return mapping.get(legacy_type, 'pt_other')

    def build_location_details(self, legacy: Dict) -> Dict:
        """Build location_details JSONB"""
        location = legacy.get('location', {})

        return {
            'region': location.get('region', ''),
            'district': location.get('area', ''),
            'location_advantages': self.extract_location_advantages(legacy),
        }

    def build_physical_specs(self, legacy: Dict, metadata: Dict) -> Dict:
        """Build physical_specs JSONB"""
        specs = {
            'dimensions': {},
            'building_specs': {}
        }

        # Land size
        if legacy.get('land_size'):
            specs['dimensions']['land_area'] = {
                'value': legacy['land_size'],
                'unit': legacy.get('land_size_unit', 'sqm')
            }

        # Extract from metadata or text
        # This is a best-effort extraction
        specs['rooms'] = self.extract_room_counts(legacy.get('text', ''))

        return specs

    def extract_room_counts(self, text: str) -> Dict:
        """Extract room counts from description text"""
        rooms = {}

        # Regex patterns for common formats
        bedroom_patterns = [
            r'(\d+)\s*bedroom',
            r'(\d+)\s*bed\s',
            r'(\d+)BR',
        ]

        for pattern in bedroom_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                rooms['bedrooms'] = int(match.group(1))
                break

        bathroom_patterns = [
            r'(\d+)\s*bathroom',
            r'(\d+)\s*bath\s',
            r'(\d+)BA',
        ]

        for pattern in bathroom_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                rooms['bathrooms'] = int(match.group(1))
                break

        return rooms

    def extract_amenities(self, legacy: Dict, category: str) -> List[str]:
        """Extract amenities from text description"""
        text = legacy.get('text', '').lower()
        amenities = []

        # Define keyword mappings
        if category == 'interior':
            keywords = {
                'am_int_air_conditioning': ['air conditioning', 'a/c', 'aircon'],
                'am_int_wifi': ['wifi', 'wi-fi', 'internet'],
                'am_int_kitchen': ['kitchen', 'kitchenette'],
                'am_int_washing_machine': ['washing machine', 'washer'],
                # ... more mappings
            }
        elif category == 'exterior':
            keywords = {
                'am_ext_private_pool': ['private pool', 'swimming pool'],
                'am_ext_garden': ['garden', 'landscaped'],
                'am_ext_terrace': ['terrace', 'patio'],
                # ... more mappings
            }
        elif category == 'building':
            keywords = {
                'am_bld_24h_security': ['24h security', '24 hour security', 'security guard'],
                'am_bld_elevator': ['elevator', 'lift'],
                'am_bld_gym': ['gym', 'fitness'],
                # ... more mappings
            }
        else:
            keywords = {}

        # Match keywords in text
        for amenity_id, keyword_list in keywords.items():
            if any(keyword in text for keyword in keyword_list):
                amenities.append(amenity_id)

        return amenities

    def extract_location_advantages(self, legacy: Dict) -> List[str]:
        """Extract location advantages from text"""
        text = legacy.get('text', '').lower()
        advantages = []

        keywords = {
            'loc_beachfront': ['beachfront', 'beach front', 'on the beach'],
            'loc_sea_view': ['sea view', 'ocean view', 'seaview'],
            'loc_near_beach': ['near beach', 'close to beach'],
            'loc_mountain_view': ['mountain view', 'mountainview'],
            'loc_quiet_area': ['quiet', 'peaceful', 'tranquil'],
            # ... more mappings
        }

        for advantage_id, keyword_list in keywords.items():
            if any(keyword in text for keyword in keyword_list):
                advantages.append(advantage_id)

        return advantages

    def extract_short_description(self, text: str) -> str:
        """Extract first 500 chars as short description"""
        if not text:
            return ''

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Truncate to 500 chars at word boundary
        if len(text) <= 500:
            return text

        return text[:497] + '...'

    async def insert_property(self, new_prop: Dict):
        """Insert property into new tables"""
        async with async_session() as session:
            # Insert core property
            property_id = await session.execute(
                insert(Property).values(**new_prop['core']).returning(Property.id)
            )
            property_id = property_id.scalar_one()

            # Insert subdomain records
            for transaction_type in new_prop['transaction_types']:
                if transaction_type == 'sale':
                    await session.execute(
                        insert(SaleDetails).values(
                            property_id=property_id,
                            sale_price=new_prop['price'],
                            currency='THB',
                            sale_status='available',
                        )
                    )
                elif transaction_type == 'rent':
                    await session.execute(
                        insert(RentalDetails).values(
                            property_id=property_id,
                            rental_type='short_term',
                            price_monthly=new_prop['price'],
                            currency='THB',
                        )
                    )
                elif transaction_type == 'lease':
                    await session.execute(
                        insert(LeaseDetails).values(
                            property_id=property_id,
                            lease_type='residential',
                            lease_price_monthly=new_prop['price'],
                            currency='THB',
                            minimum_lease_years=1,
                            security_deposit_months=2,
                            advance_payment_months=1,
                        )
                    )

            await session.commit()

    async def fetch_legacy_properties(self) -> List[Dict]:
        """Fetch all legacy properties from Supabase"""
        # This would connect to your legacy Supabase instance
        # For now, placeholder
        return []

# Run migration
if __name__ == '__main__':
    migrator = PropertyMigrator()
    asyncio.run(migrator.migrate_all())
```

**Usage:**

```bash
# Dry run (test transformation)
python scripts/migrate_legacy_properties.py --dry-run

# Real migration
python scripts/migrate_legacy_properties.py

# Migrate specific property
python scripts/migrate_legacy_properties.py --property-id abc123
```

### Phase 3: Dual-Write Period (Week 3-4)

**Strategy:** Write to both old and new schemas during transition

```python
# In property service
async def create_property(data: PropertyCreate):
    # Write to new schema
    new_property = await new_property_repo.create(data)

    # Also write to legacy schema (for backward compatibility)
    try:
        legacy_property = transform_to_legacy(new_property)
        await legacy_property_repo.create(legacy_property)
    except Exception as e:
        logger.warning(f"Failed to write to legacy schema: {e}")

    return new_property
```

### Phase 4: Frontend Updates (Week 3-5)

**Tasks:**
1. Update property forms to use new structured fields
2. Implement catalogue-driven amenity selectors
3. Update search filters
4. Update property display components

### Phase 5: API Migration (Week 4-6)

**Tasks:**
1. Create new property endpoints
2. Maintain backward-compatible legacy endpoints
3. Add deprecation warnings to old endpoints
4. Update API documentation

### Phase 6: Cleanup (Week 7+)

**Tasks:**
1. Verify all data migrated successfully
2. Stop dual-writing
3. Remove legacy endpoints
4. Archive legacy tables

---

## API Design

### Core Property Endpoints

```typescript
// List properties with filters
GET /api/v2/properties
  ?property_type=pt_villa
  &min_price=5000000
  &max_price=20000000
  &currency=THB
  &bedrooms=3
  &amenities=am_ext_private_pool,am_int_air_conditioning
  &location_advantages=loc_beachfront
  &page=1
  &limit=20

// Get single property
GET /api/v2/properties/{property_id}

// Create property
POST /api/v2/properties
Content-Type: application/json
{
  "title": "Luxury Beachfront Villa",
  "short_description": "...",
  "description": "...",
  "property_type": "pt_pool_villa",
  "physical_specs": { ... },
  "location_details": { ... },
  "amenities_interior": ["am_int_air_conditioning", ...],
  "amenities_exterior": ["am_ext_private_pool", ...],
  ...
}

// Update property
PUT /api/v2/properties/{property_id}

// Delete property (soft delete)
DELETE /api/v2/properties/{property_id}
```

### Subdomain-Specific Endpoints

```typescript
// Rental properties only
GET /api/v2/rentals
  ?rental_type=short_term
  &min_price_monthly=30000
  &max_price_monthly=100000

// Sale properties only
GET /api/v2/sales
  ?sale_status=available
  &min_price=5000000

// Business properties only
GET /api/v2/businesses
  ?business_type=restaurant
  &min_annual_revenue=2000000

// Investment properties only
GET /api/v2/investments
  ?project_stage=construction
  &min_projected_roi=15
```

### Catalogue Endpoints

```typescript
// Get all catalogues
GET /api/v2/catalogues

// Get catalogue options
GET /api/v2/catalogues/amenities_interior
GET /api/v2/catalogues/location_advantages?region=phuket

// Admin: Manage catalogues
POST /api/v2/admin/catalogues/{catalogue_id}/options
PUT /api/v2/admin/catalogues/{catalogue_id}/options/{option_id}
DELETE /api/v2/admin/catalogues/{catalogue_id}/options/{option_id}
```

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Week 1: Database Setup**
- [ ] Create Alembic migration for new schema
- [ ] Set up catalogue tables
- [ ] Seed catalogue data (24 catalogues, 400+ options)
- [ ] Create core properties table
- [ ] Create subdomain detail tables
- [ ] Set up all indexes and constraints
- [ ] Test schema in dev environment

**Week 2: Data Migration**
- [ ] Write data transformation scripts
- [ ] Test migration on dev/staging with sample data
- [ ] Validate transformed data
- [ ] Set up dual-write mechanism
- [ ] Create rollback procedures

### Phase 2: Backend Implementation (Weeks 3-5)

**Week 3: Models & Repositories**
- [ ] Create SQLAlchemy models for all tables
- [ ] Create Pydantic schemas (Create, Update, Response)
- [ ] Implement property repository (CRUD)
- [ ] Implement subdomain repositories
- [ ] Implement catalogue repository
- [ ] Write unit tests

**Week 4: API Endpoints**
- [ ] Implement core property endpoints
- [ ] Implement subdomain endpoints
- [ ] Implement catalogue endpoints
- [ ] Implement search/filter logic
- [ ] Add pagination
- [ ] Write integration tests

**Week 5: Services & Business Logic**
- [ ] Implement property service layer
- [ ] Implement validation logic
- [ ] Implement authorization (agent can edit own properties)
- [ ] Implement media upload handling
- [ ] Implement slug generation
- [ ] Write service tests

### Phase 3: Frontend Implementation (Weeks 5-7)

**Week 5-6: Forms & Components**
- [ ] Create property form (multi-step wizard)
- [ ] Create catalogue-driven amenity selectors
- [ ] Create location selector with map
- [ ] Create room count inputs
- [ ] Create physical specs inputs
- [ ] Create policy inputs
- [ ] Create media uploader

**Week 6-7: Listing & Display**
- [ ] Create property list component
- [ ] Create property card component
- [ ] Create property detail page
- [ ] Create advanced search filters
- [ ] Create map view
- [ ] Create comparison tool

### Phase 4: Migration & Testing (Weeks 7-8)

**Week 7: Data Migration**
- [ ] Run migration on staging
- [ ] Validate all migrated data
- [ ] Fix any migration issues
- [ ] Update frontend to use new API
- [ ] Test all user flows

**Week 8: Testing & QA**
- [ ] End-to-end testing
- [ ] Performance testing
- [ ] Security audit
- [ ] Accessibility testing
- [ ] Cross-browser testing
- [ ] Mobile testing

### Phase 5: Launch & Monitoring (Week 9+)

**Week 9: Launch**
- [ ] Deploy to production
- [ ] Monitor for errors
- [ ] Collect user feedback
- [ ] Fix critical bugs

**Week 10+: Optimization**
- [ ] Performance optimization
- [ ] Query optimization
- [ ] Index tuning
- [ ] Cache strategy
- [ ] Documentation

---

## Success Criteria

1. **Data Integrity**
   - ✅ 100% of legacy properties migrated
   - ✅ No data loss during migration
   - ✅ All relationships maintained

2. **Performance**
   - ✅ Property list loads in < 500ms
   - ✅ Property detail loads in < 300ms
   - ✅ Search returns results in < 1s
   - ✅ All queries optimized with proper indexes

3. **User Experience**
   - ✅ Intuitive property creation flow
   - ✅ Rich filtering capabilities
   - ✅ Mobile-responsive design
   - ✅ Accessible (WCAG 2.1 AA)

4. **Developer Experience**
   - ✅ Type-safe schemas
   - ✅ Comprehensive API documentation
   - ✅ 80%+ test coverage
   - ✅ Clear migration path

5. **Business Metrics**
   - ✅ Support for all 5 subdomains (rental, sale, lease, business, investment)
   - ✅ 165+ amenity options
   - ✅ 81 location advantages
   - ✅ Multi-currency support (THB, USD, EUR)
   - ✅ Multi-language support (EN, TH, RU, ZH, DE, FR)

---

## Next Steps

1. **Review this plan** with stakeholders
2. **Create user story** for Phase 1 (Database Setup)
3. **Update `.specs/02_PROPERTIES_SCHEMA.md`** with final schema
4. **Begin implementation** following roadmap

---

## Appendices

### A. Property Type Mapping

| Legacy Type   | New Catalogue ID | Notes                |
| ------------- | ---------------- | -------------------- |
| land          | pt_land          | No change            |
| house         | pt_house         | No change            |
| villa         | pt_villa         | No change            |
| pool-villa    | pt_pool_villa    | No change            |
| appartment    | pt_apartment     | Fixed typo           |
| apartment     | pt_apartment     | Normalized           |
| condo         | pt_condo         | No change            |
| townhouse     | pt_townhouse     | New type added       |
| penthouse     | pt_penthouse     | New type added       |
| office        | pt_office        | No change            |
| shop          | pt_shop          | No change            |
| warehouse     | pt_warehouse     | New type added       |
| business      | pt_business      | No change            |
| resort        | pt_resort        | New type added       |
| hotel         | pt_hotel         | New type added       |
| other         | pt_other         | No change            |

### B. Transaction Type Migration

| Legacy Transaction | New Subdomain Tables  | Notes                               |
| ------------------ | --------------------- | ----------------------------------- |
| sale               | sale_details          | Single record                       |
| rent               | rental_details        | Single record                       |
| lease              | lease_details         | Single record                       |
| sale-lease         | sale_details + lease_details | Split into two records              |

### C. Amenity Categories

| Category         | Count | Examples                                  |
| ---------------- | ----- | ----------------------------------------- |
| Interior         | 47    | AC, kitchen, WiFi, wardrobes              |
| Exterior         | 44    | Private pool, garden, terrace, parking    |
| Building         | 44    | Security, gym, elevator, communal pool    |
| Neighborhood     | TBD   | Near beach, near shops, quiet area        |
| Utilities        | 27    | Electricity, water, internet, gas         |
| **Total**        | **162+** |                                           |

### D. Estimated Database Sizes

**For 10,000 properties:**

| Table                 | Avg Row Size | Total Size | Notes                        |
| --------------------- | ------------ | ---------- | ---------------------------- |
| properties            | 5 KB         | 50 MB      | Core data + JSONB            |
| rental_details        | 500 B        | 2 MB       | ~40% of properties           |
| sale_details          | 400 B        | 2 MB       | ~50% of properties           |
| lease_details         | 600 B        | 1 MB       | ~10% of properties           |
| business_details      | 800 B        | 500 KB     | ~5% of properties            |
| investment_details    | 700 B        | 300 KB     | ~3% of properties            |
| property_images       | 300 B        | 6 MB       | ~20 images per property      |
| catalogues            | 200 B        | 5 KB       | 24 catalogues                |
| catalogue_options     | 250 B        | 100 KB     | ~400 options                 |
| content_embeddings    | 6 KB         | 60 MB      | Vector embeddings            |
| **Total Estimated**   |              | **~120 MB** | Excluding images (R2)        |

**Image Storage (Cloudflare R2):**
- 10,000 properties × 20 images × 500 KB avg = ~100 GB
- Cost: ~$1.50/month

### E. Performance Benchmarks

**Target Performance (95th percentile):**

| Operation              | Target | Notes                          |
| ---------------------- | ------ | ------------------------------ |
| Property list (20)     | 300ms  | With filters                   |
| Property detail        | 200ms  | Including all subdomain data   |
| Search with filters    | 500ms  | Full-text + amenities + location |
| Property create        | 800ms  | Including image upload         |
| Property update        | 500ms  | Single field                   |
| Catalogue load         | 100ms  | Cached aggressively            |

---

**Document Version:** 1.0
**Last Updated:** 2025-11-06
**Authors:** Claude Code
**Status:** Ready for Implementation

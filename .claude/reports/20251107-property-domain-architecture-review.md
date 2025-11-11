# Property Domain Architecture Review

**Date:** 2025-11-07
**Project:** Bestays Real Estate Platform
**Author:** Claude Code (Architectural Analysis)
**Status:** Recommendation - Awaiting Decision

---

## Executive Summary

**RECOMMENDATION: Implement Bounded Contexts with Phased Rollout**

After comprehensive analysis of industry standards, business requirements, and technical trade-offs, I recommend implementing **three bounded contexts** (Rentals, Listings, Businesses) using a **modular monolith** approach, starting with **Listings context only** for Milestone 01.

### Key Decisions

1. **Separate Rentals from Listings NOW** - Different business models require different domain models
2. **Start with Listings context only** - Milestone 01 is 100% listings domain, proving architecture without complexity
3. **Use PostgreSQL schemas for separation** - `listings`, `rentals`, `businesses`, `shared` schemas in same database
4. **Defer rentals implementation** - Add in Phase 2 after core functionality validated
5. **Enable future microservice extraction** - Architecture supports separate hosting (rentals.bestays.app) when needed

### Implementation Impact

**For US-002 (Homepage - Immediate):**
- Create `listings` schema with properties table
- Create `shared` schema for media, locations, agents
- Implement `/api/v1/listings/*` endpoints
- Frontend routes: `/listings/*`
- **No change** to frontend components (PropertyCard works same way)
- **Timeline impact:** +2 days for schema setup (worth the investment)

**For Milestone 01 (US-002 to US-020):**
- All user stories are listings domain (sale/lease properties)
- No rentals features in scope
- Single context implementation = low complexity
- Validates architecture before expanding

**For Future (Phase 2+):**
- Add rentals context without touching listings code
- Extract rentals to separate deployment when ready
- Add businesses context if market demands

---

## 1. Industry Analysis

### 1.1 How Major Platforms Structure Property Data

#### **Zillow / Realtor.com (Sale Listings)**

**Business Model:** Real estate transactions (sale, long-term lease)

**Domain Structure:**
- Single domain: Real estate marketplace
- Focus: Investment value, legal status, neighborhood data
- Rich media: Virtual tours, floor plans, price history

**Content Emphasis:**
- Property details: Size, rooms, age, condition
- Financial: Price per sqm, property tax, HOA fees
- Legal: Ownership type, deed info, zoning
- Neighborhood: Schools, crime stats, walkability
- History: Price trends, days on market, previous sales

**Schema Characteristics:**
- Property-centric (not booking-centric)
- Deep ownership and legal data
- Investment metrics (ROI, appreciation, rental yield potential)
- Long-form descriptions, detailed specifications

**Technology:**
- Separate databases for listings vs agent CRM
- Heavy use of GIS (geospatial indexing) for location search
- Integration with MLS (Multiple Listing Service)

---

#### **Airbnb / Vrbo (Short-term Rentals)**

**Business Model:** Vacation rental marketplace with booking platform

**Domain Structure:**
- Completely separate from real estate sales
- Focus: Guest experience, instant booking, reviews
- Rich media: Professional photography, virtual tours

**Content Emphasis:**
- Guest-centric: House rules, check-in process, amenities
- Booking: Availability calendar, dynamic pricing, instant booking
- Social proof: Guest reviews, host response time, cancellation policy
- Experience: What makes this stay special, neighborhood guide

**Schema Characteristics:**
- Booking-centric (availability, pricing rules)
- Guest review system (ratings, comments, host reputation)
- Flexible pricing (nightly, weekly, seasonal, dynamic)
- Detailed amenity checklist (kitchen equipment, WiFi speed, linens)

**Technology:**
- Booking engine (calendar, reservations, payments)
- Review system
- Dynamic pricing algorithms
- Separate from long-term real estate

**KEY INSIGHT:** Airbnb does NOT mix long-term real estate sales with vacation rentals. Completely different platforms, different domains, different user journeys.

---

#### **Booking.com (Hospitality)**

**Business Model:** Hotel and vacation rental bookings

**Domain Structure:**
- Hospitality marketplace (hotels + vacation properties)
- Inventory management focused
- Integration with property management systems (PMS)

**Content Emphasis:**
- Room types and availability
- Amenities per room category
- Policies (check-in/out, cancellation, payment)
- Location convenience (transport, attractions)

**Schema Characteristics:**
- Room inventory (multiple units of same type)
- Real-time availability
- Integration with channel managers
- Review system with verified stays

---

#### **Rightmove (UK Real Estate)**

**Business Model:** UK's largest property portal (sale + rental listings)

**Domain Structure:**
- **TWO separate marketplaces:** "For Sale" and "To Rent"
- Different user journeys, different filters, different expectations
- Rentals = long-term residential (not vacation)

**Content Emphasis (Sale):**
- Property ownership details
- Council tax band
- EPC (Energy Performance Certificate)
- Tenure (freehold, leasehold)
- Chain status (chain-free properties preferred)

**Content Emphasis (Rental):**
- Deposit amount
- Tenant preferences (families, professionals, students)
- Furnished vs unfurnished
- Let agreed date
- Availability date

**KEY INSIGHT:** Even long-term rentals are treated as separate domain from sales. Different content requirements, different user expectations.

---

### 1.2 Industry Best Practices Summary

**✅ VALIDATED PATTERN: Domain Separation by Transaction Type**

All major platforms separate property domains by business model:
- **Sales:** Investment-focused, legal-heavy, transaction-based
- **Short-term Rentals:** Guest experience, booking-centric, review-driven
- **Long-term Rentals:** Tenant-focused, availability-based, tenancy rules

**✅ VALIDATED PATTERN: Rich Media by Price Point**

Premium listings have higher content expectations:
- **Standard listings (<$500k USD):** 10-15 photos, basic description
- **Luxury listings (>$1M USD):** 20-30 photos, virtual tour, video, drone footage, floor plans, architectural plans
- **Vacation rentals:** 20-30 photos (required), floor plan (standard), virtual tour (expected)

**✅ VALIDATED PATTERN: Context-Specific Search**

Users don't search across domains:
- Vacation renters search Airbnb (not Zillow)
- Property buyers search Zillow (not Airbnb)
- Different filters, different expectations, different user personas

**✅ EMERGING TREND: Virtual Tours Standard by 2025**

- 360° virtual tours becoming standard (not premium)
- Third-party embeds: Matterport, Kuula, CloudPano
- Not stored locally (embed URLs only)
- Expected for properties >$300k USD or luxury rentals

**✅ EMERGING TREND: New Property Categories**

Missing from Bestays V2 schema:
- **Co-living spaces** (shared housing with private rooms)
- **Serviced apartments** (hotel-like services, monthly rental)
- **Co-working spaces** (commercial real estate)
- **Build-to-rent** (purpose-built rental developments)
- **Data centers** (emerging real estate class)

---

## 2. Domain Model Recommendation

### 2.1 Recommended Architecture: Bounded Contexts (Modular Monolith)

**Three Bounded Contexts:**

```
┌─────────────────────────────────────────────────────────────┐
│                     BESTAYS PLATFORM                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────┐  │
│  │   RENTALS     │  │   LISTINGS    │  │  BUSINESSES  │  │
│  │   Context     │  │   Context     │  │   Context    │  │
│  ├───────────────┤  ├───────────────┤  ├──────────────┤  │
│  │ Vacation      │  │ Sale          │  │ Business     │  │
│  │ rentals       │  │ Long-term     │  │ sales with   │  │
│  │ Guest-focused │  │ lease         │  │ operations   │  │
│  │               │  │ Investment    │  │              │  │
│  │ Properties:   │  │               │  │ Properties:  │  │
│  │ • Villa       │  │ Properties:   │  │ • Restaurant │  │
│  │ • Pool villa  │  │ • Land        │  │ • Hotel ops  │  │
│  │ • Apartment   │  │ • House       │  │ • Shop+biz   │  │
│  │ • Condo       │  │ • Townhouse   │  │              │  │
│  │ • Resort      │  │ • Penthouse   │  │              │  │
│  │ • Hotel       │  │ • Apartment   │  │              │  │
│  │               │  │ • Condo       │  │              │  │
│  │               │  │ • Office      │  │              │  │
│  │               │  │ • Shop        │  │              │  │
│  │               │  │ • Warehouse   │  │              │  │
│  └───────────────┘  └───────────────┘  └──────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              SHARED KERNEL                           │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │ • Media Storage (images, videos, tours)             │  │
│  │ • Locations (regions, districts, proximity)         │  │
│  │ • Agents (user management, profiles)                │  │
│  │ • Amenities Catalog (150+ amenities)                │  │
│  │ • Translation Infrastructure (6 languages)          │  │
│  │ • Search Infrastructure (pgvector)                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 2.2 Context Definitions

#### **RENTALS Context (Short-term Vacation Rentals)**

**Purpose:** Vacation rental marketplace with booking infrastructure

**Property Types:**
- villa, pool-villa (vacation homes)
- apartment, condo (short-term rental units)
- resort, hotel (hospitality properties)

**Unique Characteristics:**
- Booking-centric (availability calendar, reservations)
- Guest-focused (reviews, house rules, instant booking)
- Nightly pricing (dynamic pricing, seasonal rates)
- Short-term stays (1-30 days typical)

**Unique Data Requirements:**
```
guest_capacity: INT (required)
check_in_time: TIME (e.g., 3:00 PM)
check_out_time: TIME (e.g., 11:00 AM)
cleaning_fee: BIGINT
minimum_nights: INT
maximum_nights: INT
instant_booking: BOOLEAN
cancellation_policy: ENUM (flexible, moderate, strict)
house_rules: TEXT[] (no smoking, no pets, no parties)
booking_details: JSONB (pricing rules, fees)
guest_amenities: JSONB (linens provided, toiletries, welcome basket)
```

**Future Features:**
- Booking engine (calendar, reservations, payments)
- Guest review system
- Dynamic pricing
- Channel manager integration (Airbnb, Booking.com sync)

**Deployment:**
- Phase 1: Part of main app (bestays.app/rentals)
- Phase 2: Separate deployment (rentals.bestays.app)

---

#### **LISTINGS Context (Sale, Long-term Lease, Investment)**

**Purpose:** Real estate marketplace for property transactions

**Property Types:**
- land (all types: residential, commercial, agricultural)
- house, townhouse, penthouse (residential sale)
- apartment, condo (sale or long-term lease)
- office, shop, warehouse (commercial real estate)

**Unique Characteristics:**
- Transaction-centric (sale, long-term lease)
- Investment-focused (ROI, yields, price trends)
- Legal-heavy (ownership, title deed, foreign quota)
- Long-term commitment (sale = ownership, lease = years)

**Unique Data Requirements:**
```
sale_price: BIGINT
lease_price: BIGINT (long-term lease)
ownership_type: ENUM (freehold, leasehold, company)
foreign_quota: BOOLEAN
title_deed: TEXT
rental_yield: NUMERIC(5,2) (% annual)
price_trend: ENUM (rising, stable, falling)
price_per_sqm: NUMERIC(15,2)
investment_metrics: JSONB (ROI, appreciation, market analysis)
legal_details: JSONB (zoning, permits, restrictions)
```

**Features:**
- Lead generation (contact agent, inquire)
- Investment analysis tools
- Mortgage calculator
- Property comparison

**Deployment:**
- Core business at bestays.app

---

#### **BUSINESSES Context (Operating Business + Property)**

**Purpose:** Business sales marketplace (restaurant, hotel, shop with operations)

**Property Types:**
- business (operating business with property)

**Unique Characteristics:**
- Business operations-focused (revenue, customers, employees)
- Asset-centric (equipment, inventory, IP included)
- Financial due diligence required
- Transition/training support needed

**Unique Data Requirements:**
```
business_type: ENUM (restaurant, hotel, shop, manufacturing, service)
revenue: BIGINT (annual)
profit: BIGINT (annual)
customer_base: TEXT
employee_count: INT
included_assets: JSONB (equipment, inventory, IP, contracts)
reason_for_sale: TEXT
training_support: BOOLEAN
transition_period: TEXT
business_financials: JSONB (P&L, balance sheet, cash flow)
operations_data: JSONB (opening hours, suppliers, processes)
```

**Features:**
- Financial document uploads (P&L, tax returns)
- NDA requirements
- Qualified buyer verification
- Business broker integration

**Deployment:**
- Part of listings or separate (TBD based on market demand)

---

### 2.3 Shared Kernel (Common Infrastructure)

**Media Storage:**
```sql
CREATE TABLE shared.media_files (
  id UUID PRIMARY KEY,
  property_id UUID NOT NULL,
  property_context TEXT NOT NULL,  -- 'rental', 'listing', 'business'
  media_type ENUM ('photo', 'floor_plan', 'video', 'virtual_tour', 'document'),
  storage_url TEXT NOT NULL,  -- Cloudflare R2
  thumbnail_url TEXT,
  display_order INT,
  metadata JSONB  -- dimensions, file_size, mime_type, alt_text
);
```

**Locations:**
```sql
CREATE TABLE shared.locations (
  id UUID PRIMARY KEY,
  region TEXT NOT NULL,
  district TEXT,
  sub_district TEXT,
  coordinates POINT,  -- PostGIS
  metadata JSONB  -- proximity data, transportation
);
```

**Agents:**
```sql
CREATE TABLE shared.agents (
  id UUID PRIMARY KEY,
  clerk_user_id TEXT NOT NULL,  -- Clerk auth
  name TEXT,
  email TEXT,
  phone TEXT,
  languages TEXT[],
  contexts TEXT[]  -- ['listings', 'rentals', 'businesses']
);
```

**Amenities Catalog:**
```sql
CREATE TABLE shared.amenities_catalog (
  id TEXT PRIMARY KEY,  -- 'air_conditioning'
  category TEXT NOT NULL,  -- 'interior', 'exterior', 'building', 'utilities'
  name JSONB,  -- { "en": "Air Conditioning", "th": "เครื่องปรับอากาศ" }
  icon TEXT,
  applicable_contexts TEXT[]  -- ['rental', 'listing']
);
```

---

### 2.4 Context Map (Relationships Between Contexts)

```
┌──────────────┐
│   RENTALS    │
└──────┬───────┘
       │ uses
       ├────────────> shared.media_files
       ├────────────> shared.locations
       ├────────────> shared.agents
       └────────────> shared.amenities_catalog

┌──────────────┐
│   LISTINGS   │
└──────┬───────┘
       │ uses
       ├────────────> shared.media_files
       ├────────────> shared.locations
       ├────────────> shared.agents
       └────────────> shared.amenities_catalog

┌──────────────┐
│  BUSINESSES  │
└──────┬───────┘
       │ uses
       ├────────────> shared.media_files
       ├────────────> shared.locations
       └────────────> shared.agents
```

**Relationship Rules:**
1. Contexts NEVER reference each other's tables directly
2. All common data goes in shared kernel
3. If contexts need same data, duplicate it (each context owns its copy)
4. Communication between contexts via events (future) or API calls

---

## 3. Property Type Taxonomy

### 3.1 Industry Standard Classification

**RESIDENTIAL (For Living):**
- Single Family: house, villa, pool-villa
- Multi-Family: apartment, condo, townhouse, penthouse
- Specialized: serviced apartment, co-living, student housing

**COMMERCIAL (For Business):**
- Office: office space, co-working
- Retail: shop, shopping center
- Industrial: warehouse, factory, logistics
- Hospitality: hotel, resort, hostel

**LAND (Undeveloped):**
- Residential land
- Commercial land
- Agricultural land
- Mixed-use land

**SPECIAL PURPOSE:**
- Business opportunity (operating business)
- Development project (under construction)
- Build-to-rent (new category)

---

### 3.2 Bestays Property Types Mapped to Contexts

**RENTALS Context (6 types):**
- villa
- pool-villa
- apartment (short-term rental)
- condo (short-term rental)
- resort
- hotel

**LISTINGS Context (9 types):**
- land
- house
- townhouse
- penthouse
- apartment (sale/long-term lease)
- condo (sale/long-term lease)
- office
- shop
- warehouse

**BUSINESSES Context (1 type):**
- business (operating business with property)

**"other" type:** Deprecated - force specific classification

---

### 3.3 Emerging Property Types (Add in Phase 2)

**Missing from V2 Schema:**
1. **Serviced Apartment** - Hotel-like services, monthly rental (rentals context)
2. **Co-living Space** - Shared housing with private rooms (rentals context)
3. **Co-working Space** - Flexible office space (listings context)
4. **Student Housing** - Purpose-built student accommodation (rentals context)
5. **Build-to-Rent** - Purpose-built rental developments (listings context)
6. **Mixed-Use** - Residential + commercial combined (listings context)

**Recommendation:** Add based on Thailand market demand after MVP launch.

---

## 4. Content Requirements Matrix

### 4.1 Rentals Context (Vacation Properties)

| Property Type | Must-Have Content | Rich Media | Selling Points |
|---------------|-------------------|------------|----------------|
| **Villa / Pool Villa** | • 20-30 professional photos<br>• Floor plan<br>• Exact guest capacity<br>• Amenity details (kitchen equipment, A/C, WiFi speed)<br>• House rules (smoking, pets, parties)<br>• Check-in/out times<br>• Cleaning fee | • 360° virtual tour (expected)<br>• Video walkthrough<br>• Drone footage (if views) | • Pool size and features<br>• Privacy level<br>• Beach/town distance<br>• Staff included (maid, chef)<br>• Guest reviews<br>• Instant booking |
| **Apartment / Condo** | • 15-20 photos<br>• Guest capacity<br>• Amenities per room<br>• Building facilities<br>• Parking details<br>• House rules | • Floor plan (standard)<br>• Building tour | • Location convenience<br>• Building amenities (gym, pool)<br>• Public transport access<br>• Security features |
| **Resort / Hotel** | • 25-40 photos (property + rooms)<br>• Room types and capacities<br>• On-site facilities<br>• Services included<br>• F&B options | • Virtual property tour<br>• Room type videos | • All-inclusive options<br>• Activities included<br>• Staff services<br>• Event hosting |

**Content Maturity Levels (Rentals):**
- **Basic:** 8-10 photos, basic description, amenities list (LOW conversion)
- **Standard:** 15-20 photos, floor plan, detailed amenities, house rules (MEDIUM conversion)
- **Premium:** 25-30 photos, virtual tour, video, guest reviews, instant booking (HIGH conversion)

---

### 4.2 Listings Context (Sale / Long-term Lease)

| Property Type | Must-Have Content | Rich Media | Selling Points |
|---------------|-------------------|------------|----------------|
| **Land** | • 8-10 photos (site, access, surroundings)<br>• Exact size with unit<br>• Zoning information<br>• Road access type<br>• Utilities availability<br>• Title deed status | • Drone footage (standard)<br>• Site survey map | • Development potential<br>• Location advantages<br>• Price per sqm<br>• Infrastructure nearby<br>• Investment opportunity |
| **House / Villa (Sale)** | • 15-20 photos<br>• Floor plan<br>• Land size + built area<br>• Year built + renovations<br>• Ownership type<br>• Legal status (title deed) | • Virtual tour (luxury >10M THB)<br>• Video walkthrough<br>• Drone footage | • Freehold vs leasehold<br>• Foreign ownership quota<br>• Rental yield potential<br>• Neighborhood quality<br>• Resale value trends |
| **Apartment / Condo (Sale)** | • 12-15 photos<br>• Floor plan (required)<br>• Unit size (sqm)<br>• Floor level<br>• Building age<br>• Common area fees<br>• Foreign quota | • Floor plan (required)<br>• Building virtual tour | • Price per sqm comparison<br>• Building facilities<br>• Location/transport<br>• Capital appreciation<br>• Rental demand |
| **Office / Shop / Warehouse** | • 10-15 photos<br>• Floor plan / layout<br>• Usable area<br>• Zoning compliance<br>• Lease terms (if leasehold)<br>• Parking spaces | • Floor plan<br>• Site layout | • Business suitability<br>• Foot traffic (retail)<br>• Loading access (warehouse)<br>• Expansion potential<br>• Tenant demand |

**Content Maturity Levels (Listings):**
- **Basic:** 8-10 photos, basic specs, location (LOW quality listing)
- **Standard:** 15 photos, floor plan, detailed specs, legal status (COMPETITIVE)
- **Premium:** 20+ photos, virtual tour, investment analysis, professional staging (HIGH-END)

---

### 4.3 Businesses Context (Operating Business + Property)

| Business Type | Must-Have Content | Documents | Selling Points |
|---------------|-------------------|-----------|----------------|
| **Restaurant** | • 12-15 photos (interior, kitchen, seating)<br>• Layout diagram<br>• Seating capacity<br>• Kitchen equipment list<br>• Annual revenue/profit<br>• Customer base description<br>• Reason for sale | • P&L statement (3 years)<br>• Lease agreement<br>• Equipment inventory<br>• Licenses/permits | • Established clientele<br>• Location foot traffic<br>• Equipment included<br>• Lease terms<br>• Training/transition support |
| **Hotel / Guesthouse** | • 20-30 photos (rooms, common areas, exterior)<br>• Number of rooms<br>• Occupancy rates<br>• Annual revenue/profit<br>• Staff count<br>• Booking history | • Financial statements<br>• Occupancy data<br>• Staff contracts<br>• Property lease/ownership | • Booking platform presence<br>• Repeat customer rate<br>• Growth potential<br>• Management systems<br>• Online reviews |

**Due Diligence Requirements:**
- NDA before financial disclosure
- Verified financial statements
- Qualified buyer verification
- On-site business inspection

---

## 5. Schema Design Recommendation

### 5.1 Recommended Approach: Bounded Context Tables

**Why NOT Monolithic V2:**
1. ❌ Unclear what fields are required vs optional per context
2. ❌ Schema bloat (50+ fields, most nullable)
3. ❌ Business logic scattered (if rental then... if listing then...)
4. ❌ Difficult to extract rentals later (all properties in one table)
5. ❌ Violates Single Responsibility Principle

**Why YES Bounded Contexts:**
1. ✅ Each context has appropriate fields (clear requirements)
2. ✅ Can evolve independently (add rental features without touching listings)
3. ✅ Aligns with business strategy (separate hosting for rentals)
4. ✅ Easier to reason about (rental properties have rental schema)
5. ✅ Enables future microservice extraction

---

### 5.2 Listings Schema (Implement NOW for Milestone 01)

```sql
CREATE SCHEMA listings;

CREATE TYPE listings.property_type AS ENUM (
  'land',
  'house',
  'villa',
  'pool_villa',
  'townhouse',
  'penthouse',
  'apartment',
  'condo',
  'office',
  'shop',
  'warehouse'
);

CREATE TYPE listings.transaction_type AS ENUM (
  'sale',
  'lease'  -- Long-term lease only (not short-term rental)
);

CREATE TYPE listings.ownership_type AS ENUM (
  'freehold',
  'leasehold',
  'company'
);

CREATE TYPE listings.property_condition AS ENUM (
  'new',
  'excellent',
  'good',
  'fair',
  'needs_renovation'
);

CREATE TYPE listings.furnished_level AS ENUM (
  'fully',
  'partially',
  'unfurnished'
);

CREATE TABLE listings.properties (
  -- Identity
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Core Information
  title TEXT NOT NULL,
  description TEXT,
  title_deed TEXT,  -- Legal reference

  -- Classification
  property_type listings.property_type NOT NULL,
  transaction_type listings.transaction_type NOT NULL,

  -- Pricing
  sale_price BIGINT CHECK (sale_price >= 0),
  lease_price BIGINT CHECK (lease_price >= 0),  -- Long-term lease (annual or monthly)
  currency TEXT DEFAULT 'THB',  -- THB, USD, EUR
  price_per_sqm NUMERIC(15,2),

  -- Physical Specifications (JSONB for flexibility)
  physical_specs JSONB,
  -- {
  --   "rooms": { "bedrooms": 3, "bathrooms": 2, ... },
  --   "dimensions": { "total_area": { "value": 250, "unit": "sqm" }, ... },
  --   "building_specs": { "floors": 2, "parking_spaces": 2, "year_built": 2020, ... }
  -- }

  -- Location Details
  location_details JSONB,
  -- {
  --   "region": "Phuket",
  --   "district": "Patong",
  --   "sub_district": "Patong",
  --   "location_advantages": ["beachfront", "near_airport"],
  --   "proximity": { "beach_distance": { "value": 100, "unit": "m" }, ... },
  --   "transportation": { "nearest_airport": { "name": "Phuket Airport", "distance": 45, "unit": "km" } }
  -- }

  -- Amenities (reference shared.amenities_catalog)
  amenities JSONB,
  -- {
  --   "interior": ["air_conditioning", "kitchen_island"],
  --   "exterior": ["private_pool", "garden"],
  --   "building": ["24h_security", "elevator"],
  --   "utilities": ["fiber_internet", "water_supply"]
  -- }

  -- Legal & Ownership
  ownership_type listings.ownership_type,
  foreign_quota BOOLEAN DEFAULT false,  -- Can foreigner buy?

  -- Investment Metrics
  rental_yield NUMERIC(5,2),  -- Annual % yield
  price_trend TEXT,  -- 'rising', 'stable', 'falling'
  investment_metrics JSONB,
  -- {
  --   "roi_estimate": 8.5,
  --   "appreciation_rate": 5.0,
  --   "market_analysis": "Strong rental demand in area"
  -- }

  -- Policies & Terms (for long-term lease)
  policies JSONB,
  -- {
  --   "lease_terms": { "minimum_lease_months": 12, "security_deposit_months": 2 },
  --   "inclusions": ["Water", "Internet"],
  --   "restrictions": ["No pets", "No sublease"]
  -- }

  -- Agent Contact
  contact_info JSONB,
  -- {
  --   "agent_name": "John Doe",
  --   "agent_phone": "+66812345678",
  --   "agent_email": "john@bestays.app",
  --   "preferred_contact": "whatsapp"
  -- }

  -- Media (references shared.media_files)
  cover_image_id UUID,
  virtual_tour_url TEXT,
  virtual_tour_provider TEXT,  -- 'matterport', 'kuula', 'cloudpano'
  video_url TEXT,

  -- SEO
  seo_title TEXT CHECK (length(seo_title) <= 60),
  seo_description TEXT CHECK (length(seo_description) <= 160),
  tags TEXT[],

  -- Visibility
  is_published BOOLEAN DEFAULT false,
  is_featured BOOLEAN DEFAULT false,
  listing_priority INT DEFAULT 0 CHECK (listing_priority >= 0),

  -- System Fields
  created_by UUID NOT NULL REFERENCES shared.agents(id),
  updated_by UUID REFERENCES shared.agents(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);

-- Indexes for performance
CREATE INDEX idx_listings_published ON listings.properties(is_published) WHERE deleted_at IS NULL;
CREATE INDEX idx_listings_transaction_type ON listings.properties(transaction_type);
CREATE INDEX idx_listings_property_type ON listings.properties(property_type);
CREATE INDEX idx_listings_created_by ON listings.properties(created_by);
CREATE INDEX idx_listings_featured ON listings.properties(is_featured) WHERE is_published = true AND deleted_at IS NULL;
CREATE INDEX idx_listings_priority ON listings.properties(listing_priority DESC) WHERE is_published = true AND deleted_at IS NULL;

-- JSONB indexes for search
CREATE INDEX idx_listings_location_details ON listings.properties USING GIN(location_details);
CREATE INDEX idx_listings_physical_specs ON listings.properties USING GIN(physical_specs);
CREATE INDEX idx_listings_amenities ON listings.properties USING GIN(amenities);

-- Full-text search on title and description
CREATE INDEX idx_listings_search ON listings.properties USING GIN(to_tsvector('english', title || ' ' || COALESCE(description, '')));
```

---

### 5.3 Rentals Schema (Implement in Phase 2)

```sql
CREATE SCHEMA rentals;

CREATE TYPE rentals.property_type AS ENUM (
  'villa',
  'pool_villa',
  'apartment',
  'condo',
  'resort',
  'hotel'
);

CREATE TYPE rentals.cancellation_policy AS ENUM (
  'flexible',    -- Full refund up to 24 hours before check-in
  'moderate',    -- Full refund 5 days before check-in
  'strict'       -- Full refund 14 days before check-in
);

CREATE TABLE rentals.properties (
  -- Identity
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Core Information
  title TEXT NOT NULL,
  description TEXT NOT NULL,

  -- Classification
  property_type rentals.property_type NOT NULL,

  -- Pricing (short-term rental)
  nightly_rate BIGINT NOT NULL CHECK (nightly_rate >= 0),
  weekly_rate BIGINT,
  monthly_rate BIGINT,
  cleaning_fee BIGINT DEFAULT 0,
  currency TEXT DEFAULT 'THB',

  -- Guest Information
  guest_capacity INT NOT NULL CHECK (guest_capacity > 0),
  bedrooms INT NOT NULL,
  bathrooms INT NOT NULL,
  beds INT NOT NULL,

  -- Booking Rules
  minimum_nights INT DEFAULT 1 CHECK (minimum_nights >= 1),
  maximum_nights INT DEFAULT 90,
  check_in_time TIME DEFAULT '15:00',
  check_out_time TIME DEFAULT '11:00',
  instant_booking BOOLEAN DEFAULT false,
  cancellation_policy rentals.cancellation_policy DEFAULT 'moderate',

  -- Physical Specifications
  physical_specs JSONB,

  -- Location
  location_details JSONB,

  -- Amenities (guest-focused)
  amenities JSONB,
  -- Rental-specific amenities: linens provided, toiletries, welcome basket, etc.

  -- House Rules
  house_rules TEXT[],  -- ["No smoking", "No pets", "No parties", "Quiet hours 10PM-8AM"]

  -- Booking Details
  booking_details JSONB,
  -- {
  --   "additional_guest_fee": 500,  -- THB per guest above base capacity
  --   "security_deposit": 5000,
  --   "weekend_rate_multiplier": 1.2,
  --   "seasonal_pricing": [...]
  -- }

  -- Media
  cover_image_id UUID,
  virtual_tour_url TEXT,
  video_url TEXT,

  -- Contact
  contact_info JSONB,

  -- SEO
  seo_title TEXT,
  seo_description TEXT,
  tags TEXT[],

  -- Visibility
  is_published BOOLEAN DEFAULT false,
  is_featured BOOLEAN DEFAULT false,

  -- System Fields
  created_by UUID NOT NULL REFERENCES shared.agents(id),
  updated_by UUID REFERENCES shared.agents(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);

-- Booking availability calendar (future)
CREATE TABLE rentals.availability (
  property_id UUID NOT NULL REFERENCES rentals.properties(id),
  date DATE NOT NULL,
  available BOOLEAN DEFAULT true,
  price_override BIGINT,  -- Override nightly_rate for this date
  PRIMARY KEY (property_id, date)
);

-- Guest reviews (future)
CREATE TABLE rentals.reviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id UUID NOT NULL REFERENCES rentals.properties(id),
  guest_id UUID NOT NULL REFERENCES shared.agents(id),
  rating INT CHECK (rating BETWEEN 1 AND 5),
  comment TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

### 5.4 Shared Schema (Implement NOW)

```sql
CREATE SCHEMA shared;

-- Agents (users who create properties)
CREATE TABLE shared.agents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clerk_user_id TEXT UNIQUE NOT NULL,  -- Clerk authentication
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  phone TEXT,
  languages TEXT[] DEFAULT '{}',
  contexts TEXT[] DEFAULT '{}',  -- ['listings', 'rentals', 'businesses']
  profile_image_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Media files (photos, videos, documents)
CREATE TABLE shared.media_files (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id UUID NOT NULL,
  property_context TEXT NOT NULL,  -- 'listing', 'rental', 'business'
  media_type TEXT NOT NULL,  -- 'photo', 'floor_plan', 'video', 'virtual_tour', 'document'
  storage_url TEXT NOT NULL,  -- Cloudflare R2 URL
  thumbnail_url TEXT,
  display_order INT DEFAULT 0,
  metadata JSONB,
  -- {
  --   "width": 1920,
  --   "height": 1080,
  --   "file_size": 2048576,
  --   "mime_type": "image/jpeg",
  --   "alt_text": "Modern villa pool view",
  --   "color": "#e8d7c3"
  -- }
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_media_property ON shared.media_files(property_id, property_context);
CREATE INDEX idx_media_type ON shared.media_files(media_type);

-- Locations (regions, districts, areas)
CREATE TABLE shared.locations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  region TEXT NOT NULL,
  district TEXT,
  sub_district TEXT,
  coordinates POINT,  -- PostGIS for geospatial queries
  metadata JSONB,
  -- {
  --   "name_th": "ภูเก็ต",
  --   "name_en": "Phuket",
  --   "province": "Phuket",
  --   "postal_code": "83000"
  -- }
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_locations_region ON shared.locations(region);
CREATE INDEX idx_locations_district ON shared.locations(region, district);

-- Amenities catalog
CREATE TABLE shared.amenities_catalog (
  id TEXT PRIMARY KEY,  -- 'air_conditioning'
  category TEXT NOT NULL,  -- 'interior', 'exterior', 'building', 'utilities'
  name JSONB NOT NULL,  -- { "en": "Air Conditioning", "th": "เครื่องปรับอากาศ" }
  icon TEXT,
  applicable_contexts TEXT[] DEFAULT '{listing,rental}',
  display_order INT DEFAULT 0
);

-- Translations (multi-language support)
CREATE TABLE shared.translations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id UUID NOT NULL,
  property_context TEXT NOT NULL,  -- 'listing', 'rental', 'business'
  lang_code CHAR(2) NOT NULL,  -- 'en', 'th', 'ru', 'zh', 'de', 'fr'
  field TEXT NOT NULL,  -- 'title', 'description', 'seo_title', etc.
  value TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (property_id, property_context, lang_code, field)
);

CREATE INDEX idx_translations_property ON shared.translations(property_id, property_context);
```

---

### 5.5 JSONB Strategy

**Use JSONB for:**
- ✅ Truly flexible fields (physical_specs, amenities, metadata)
- ✅ Nested structures (location proximity, dimensions with units)
- ✅ Fields that vary by property type (villa has pool specs, land doesn't)
- ✅ Third-party data (virtual tour metadata, booking platform IDs)

**DO NOT use JSONB for:**
- ❌ Core business fields (price, title, property_type)
- ❌ Fields used in WHERE clauses frequently (use indexed columns)
- ❌ Fields with strong type requirements (use enums, numeric types)
- ❌ Relationships (use foreign keys)

**Performance Considerations:**
- GIN indexes on JSONB columns for search
- Avoid deep nesting (max 3 levels)
- Extract frequently queried JSONB fields to columns
- Use JSONB for flexibility, not as catch-all

---

## 6. Migration Strategy

### 6.1 Phased Implementation Approach

**Phase 1: Listings Context (Milestone 01 - NOW)**

**Goal:** Unblock US-002 and implement core real estate marketplace

**Timeline:** Week 1-2 (before starting US-002 implementation)

**Tasks:**
1. ✅ Create database schemas (listings, shared)
2. ✅ Implement listings.properties table
3. ✅ Implement shared.media_files table
4. ✅ Implement shared.agents table
5. ✅ Implement shared.locations table
6. ✅ Implement shared.amenities_catalog table
7. ✅ Seed amenities catalog (150+ amenities from V2 analysis)
8. ✅ Create FastAPI models (Pydantic for listings context)
9. ✅ Implement API endpoints (/api/v1/listings/*)
10. ✅ Update Alembic migrations

**Deliverables:**
- Listings context fully functional
- US-002 through US-011 implementable
- API documentation (Swagger)
- Database migration scripts

**Success Criteria:**
- Can create listing property via API
- Can query listings with filters (property_type, transaction_type, location)
- Can upload media and associate with listing
- Agent authentication integrated (Clerk)

---

**Phase 2: Rentals Context (Post-Milestone 01)**

**Goal:** Add vacation rental marketplace

**Timeline:** Week 13-16 (after Milestone 01 complete)

**Prerequisites:**
- Listings context validated in production
- User feedback on core features
- Market demand for rentals confirmed

**Tasks:**
1. Create rentals schema
2. Implement rentals.properties table
3. Implement rentals.availability table
4. Implement rentals.reviews table
5. Create FastAPI models for rentals context
6. Implement API endpoints (/api/v1/rentals/*)
7. Build frontend routes (/rentals/*)
8. Implement booking calendar UI
9. Integrate payment gateway (Stripe or local)

**Deliverables:**
- Rentals context functional
- Booking infrastructure (calendar, reservations)
- Guest review system
- Separate frontend section for rentals

**Success Criteria:**
- Can create rental property
- Can manage availability calendar
- Can view/filter vacation rentals
- Guest reviews working

---

**Phase 3: Businesses Context (Future)**

**Goal:** Add business sales marketplace (if market demands)

**Timeline:** TBD (based on market research)

**Decision Point:**
- Validate demand for business sales in Thailand
- Assess competition (existing business brokers)
- Determine if worth building vs focusing on core

**If approved:**
- Create businesses schema
- Implement business-specific fields (revenue, financials)
- Add NDA requirements and qualified buyer verification
- Integrate business broker workflows

---

### 6.2 Data Migration from V2 (If Needed)

**Scenario:** Existing V2 properties need to be migrated to bounded contexts

**Migration Script:**
```python
async def migrate_v2_to_bounded_contexts():
    """
    Migrate existing V2 properties to appropriate bounded contexts
    """
    v2_properties = await db.execute(
        "SELECT * FROM bestays_properties_v2 WHERE deleted_at IS NULL"
    )

    for prop in v2_properties:
        # Determine context based on transaction_type and property_type
        if prop.transaction_type == 'rent' and prop.property_type in ['villa', 'pool_villa', 'resort', 'hotel']:
            # Short-term rental → Rentals context
            await create_rental_property_from_v2(prop)

        elif prop.transaction_type in ['sale', 'lease']:
            # Sale or long-term lease → Listings context
            await create_listing_property_from_v2(prop)

        elif prop.property_type == 'business':
            # Business sale → Businesses context
            await create_business_property_from_v2(prop)

        else:
            # Log ambiguous cases for manual review
            logger.warning(f"Ambiguous property: {prop.id} - {prop.property_type} {prop.transaction_type}")

    logger.info(f"Migration complete. Migrated {len(v2_properties)} properties")

async def create_listing_property_from_v2(v2_prop):
    """
    Transform V2 property to Listings context property
    """
    listing = {
        "id": v2_prop.id,  # Keep same UUID
        "title": v2_prop.title,
        "description": v2_prop.description,
        "title_deed": v2_prop.title_deed,
        "property_type": v2_prop.property_type,
        "transaction_type": v2_prop.transaction_type,  # 'sale' or 'lease'
        "sale_price": v2_prop.sale_price,
        "lease_price": v2_prop.lease_price,
        "currency": v2_prop.currency,
        "physical_specs": v2_prop.physical_specs,
        "location_details": v2_prop.location_details,
        "amenities": v2_prop.amenities,
        "ownership_type": v2_prop.ownership_type,
        "foreign_quota": v2_prop.foreign_quota,
        "rental_yield": v2_prop.rental_yield,
        "price_trend": v2_prop.price_trend,
        "policies": v2_prop.policies,
        "contact_info": v2_prop.contact_info,
        "seo_title": v2_prop.seo_title,
        "seo_description": v2_prop.seo_description,
        "tags": v2_prop.tags,
        "is_published": v2_prop.is_published,
        "is_featured": v2_prop.is_featured,
        "listing_priority": v2_prop.listing_priority,
        "created_by": v2_prop.created_by,
        "updated_by": v2_prop.updated_by,
        "created_at": v2_prop.created_at,
        "updated_at": v2_prop.updated_at
    }

    await db.execute(
        "INSERT INTO listings.properties (...) VALUES (...)",
        listing
    )

    # Migrate media files
    await migrate_media_files(v2_prop.id, 'listing')
```

**Migration Phases:**
1. **Week 1:** Schema creation (no data migration)
2. **Week 2-4:** Dual-write period (write to both V2 and new schemas)
3. **Week 5:** Data migration script (copy V2 → bounded contexts)
4. **Week 6:** Validation (compare V2 vs new schemas, fix discrepancies)
5. **Week 7:** Cutover (read from new schemas only)
6. **Week 8+:** Keep V2 as read-only archive

**Rollback Plan:**
- V2 schema remains intact during migration
- Can revert to V2 queries if issues found
- Gradual cutover (listings first, then rentals)

---

### 6.3 Risk Mitigation

**Risk: Schema design doesn't fit real properties**
- Mitigation: Review with 10 sample properties (land, villa, condo, business)
- Validation: Can all V2 fields map cleanly to new schemas?
- Fallback: Keep JSONB fields flexible for edge cases

**Risk: Performance degradation**
- Mitigation: Benchmark queries before/after migration
- Validation: Test with 10k+ properties
- Fallback: Add indexes, use database views, implement caching

**Risk: Breaking changes to API**
- Mitigation: Version API (keep /api/v1/properties for backward compat, add /api/v1/listings)
- Validation: Parallel API versions during transition
- Fallback: Proxy old API to new schemas

**Risk: Frontend routing changes confuse users**
- Mitigation: Implement redirects (/p/{id} → /listings/{id})
- Validation: Keep old routes working during transition
- Fallback: Gradual rollout, monitor 404s

---

## 7. Implementation Impact

### 7.1 Impact on US-002 (Homepage)

**Original Plan:**
- Fetch from bestays_properties_v2 table
- Categories: "Freehold & Leasehold", "Land For Sale", etc.

**New Plan:**
- Fetch from listings.properties table
- Same categories (all are listings domain)
- API endpoint: `GET /api/v1/listings/featured`

**Frontend Changes:**
- **NO CHANGE** to PropertyCard component (data structure same)
- **NO CHANGE** to category sections (same UI)
- **ONLY CHANGE:** API endpoint URL

**API Implementation:**
```python
# apps/server/api/v1/listings/endpoints.py

@router.get("/featured")
async def get_featured_listings(
    category: Optional[str] = None,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """
    Get featured listings for homepage

    Categories:
    - freehold-leasehold: land with sale or lease
    - land-for-sale: land with sale
    - land-for-lease: land with lease
    - business-for-sale: business type
    - properties-for-rent: N/A (future: rentals context)
    - properties-for-sale: house, villa, condo, etc. with sale
    """
    query = db.query(ListingProperty).filter(
        ListingProperty.is_published == true,
        ListingProperty.deleted_at == null
    )

    # Category filters (same logic as before)
    if category == 'land-for-sale':
        query = query.filter(
            ListingProperty.property_type == 'land',
            ListingProperty.transaction_type == 'sale'
        )
    elif category == 'properties-for-sale':
        query = query.filter(
            ListingProperty.property_type.in_([
                'house', 'villa', 'pool_villa', 'condo', 'apartment', 'townhouse'
            ]),
            ListingProperty.transaction_type == 'sale'
        )
    # ... other categories

    return query.order_by(
        ListingProperty.listing_priority.desc(),
        ListingProperty.updated_at.desc()
    ).limit(limit).all()
```

**Timeline Impact:**
- Schema setup: +1 day (create schemas, tables)
- API implementation: 0 days (same logic, just different table)
- Frontend: 0 days (no changes)
- Testing: +0.5 days (verify queries work)

**Total Impact: +1.5 days to US-002 timeline**

---

### 7.2 Impact on US-003 to US-005 (Listings Pages)

**Original Plan:**
- Query bestays_properties_v2
- Filter by property_type, transaction_type, location

**New Plan:**
- Query listings.properties
- Same filters

**Impact: ZERO** (just different table name, same query logic)

---

### 7.3 Impact on US-006 to US-011 (Agent CMS)

**Original Plan:**
- CRUD operations on bestays_properties_v2
- Image upload and association

**New Plan:**
- CRUD operations on listings.properties
- Image upload to shared.media_files with context='listing'

**Changes Needed:**
1. Property creation form knows to create in listings context
2. Image upload associates with property_context='listing'
3. Property table shows only listings.properties

**Future Enhancement:**
- Agent can choose context (listing vs rental) during creation
- CMS shows tabs: "My Listings" | "My Rentals" | "My Businesses"

**Timeline Impact:** +1 day (context selection logic)

---

### 7.4 Impact on US-016 (Schema Migration Story)

**Original Story:** "Migrate property schema to subdomain model"

**Updated Story:**
- Title: "Implement Bounded Contexts Architecture"
- Scope:
  - Create listings, rentals, businesses, shared schemas
  - Implement listings context for Milestone 01
  - Implement shared kernel (media, locations, agents, amenities)
  - Defer rentals context to Phase 2
  - Document architecture decisions

**Tasks:**
1. Design database schemas (listings, shared)
2. Create Alembic migrations
3. Implement Pydantic models
4. Create API endpoints
5. Seed amenities catalog
6. Write architecture documentation
7. Update US-002 through US-020 implementation plans

**Timeline Impact:** +2 weeks (architectural work, but unblocks future scaling)

---

### 7.5 API Structure Changes

**Old Structure (Monolithic):**
```
/api/v1/properties/
├── public/           # Guest queries
│   ├── GET /         # List all properties
│   └── GET /{id}     # Property detail
└── cms/              # Agent CRUD
    ├── GET /
    ├── POST /
    ├── PUT /{id}
    └── DELETE /{id}
```

**New Structure (Bounded Contexts):**
```
/api/v1/listings/     # Listings context
├── public/
│   ├── GET /featured
│   ├── GET /
│   └── GET /{id}
└── cms/
    ├── GET /
    ├── POST /
    ├── PUT /{id}
    └── DELETE /{id}

/api/v1/rentals/      # Rentals context (Phase 2)
├── public/
└── cms/

/api/v1/shared/       # Shared resources
├── media/
│   ├── POST /upload
│   └── DELETE /{id}
├── locations/
│   └── GET /
└── amenities/
    └── GET /

/api/v1/search/       # Cross-context search
└── GET /global       # Homepage aggregate search
```

---

### 7.6 Frontend Routing Changes

**Old Routes:**
```
/                     # Homepage
/p/{id}               # Property detail
/listings/{category}  # Category listings
/locations/{region}   # Location listings
/cms/properties       # Agent CMS
```

**New Routes:**
```
/                      # Homepage (aggregates all contexts)
/listings/{id}         # Listing detail (sale/lease)
/listings/{category}   # Category listings
/locations/{region}    # Location listings
/rentals/{id}          # Rental detail (Phase 2)
/rentals/              # Vacation rentals browse (Phase 2)
/businesses/{id}       # Business detail (Phase 3)
/cms/listings          # Agent CMS (listings)
/cms/rentals           # Agent CMS (rentals, Phase 2)
```

**Backward Compatibility:**
- Keep `/p/{id}` route working (redirect to `/listings/{id}`)
- Or: Keep `/p/{id}` as universal detail page that detects context

---

## 8. Risk Assessment

### 8.1 Risk: Over-Engineering (Bounded Contexts Too Early)

**Symptoms:**
- Complexity slows development
- Feature delivery delayed (Milestone 01 takes 16 weeks instead of 12)
- Team confusion (if had multiple developers)

**Impact:** MEDIUM

**Mitigation:**
1. **Start with listings context only** (Phase 1)
2. **Defer rentals to Phase 2** (after MVP validated)
3. **Use modular monolith** (not microservices - same deployment)
4. **Leverage JSONB** for flexibility within context
5. **Don't implement businesses context** unless market demands

**Probability:** LOW (if we implement listings only first)

**Cost if happens:** +4 weeks to Milestone 01

---

### 8.2 Risk: Under-Engineering (Monolithic V2 Schema)

**Symptoms:**
- Rental features don't fit schema (booking calendar, reviews)
- Schema bloat with optional fields (50+ columns, most nullable)
- Business logic scattered (if rental then... if listing then...)
- Difficult to extract rentals later (separate hosting)

**Impact:** HIGH

**Mitigation:**
- None (accepting this approach means accepting future refactor cost)

**Probability:** HIGH (project owner already identified this concern)

**Cost if happens:**
- **4-6 weeks refactor** when separating rentals
- **Data migration complexity**
- **API breaking changes**
- **Frontend routing changes**
- **Lost opportunity cost** (could have been adding features)
- **Technical debt interest** (compound complexity over time)

**CONCLUSION:** Under-engineering is HIGHER RISK than over-engineering in this case.

---

### 8.3 Risk: Wrong Domain Boundaries

**Symptoms:**
- Properties need to exist in multiple contexts (villa for rent AND sale)
- Data duplication and sync issues

**Impact:** MEDIUM

**Mitigation:**
- **Allow same physical property to have multiple listings** (industry standard)
- Example: Villa can have listing in rentals context (vacation rental) AND listings context (for sale)
- These are separate listings with different content (rental has house rules, sale has legal status)

**Probability:** LOW

**Industry Validation:** Zillow and Airbnb both allow same property to be listed for rent AND sale (separate listings).

---

### 8.4 Risk: Search Performance Degradation

**Symptoms:**
- Homepage slow (aggregating across contexts)
- Cross-context queries expensive

**Impact:** LOW

**Mitigation:**
1. **Homepage doesn't need cross-context search** (shows separate sections)
2. **Use database views** for common aggregations
3. **Implement caching layer** (Redis) for featured properties
4. **Proper indexing** on all query fields
5. **Optimize queries** (pagination, limit, select only needed fields)

**Performance Targets:**
- Homepage load: <2 seconds
- Listing query: <500ms
- Property detail: <300ms

**Validation:** Benchmark with 10k+ properties

**Probability:** VERY LOW (proper indexing + caching solves this)

---

### 8.5 Risk: Team Confusion (Boundary Violations)

**Symptoms:**
- Developers violate bounded context rules (cross-context queries, shared state)
- Coupling between contexts (lose benefits of separation)

**Impact:** LOW (for this project)

**Why Low:** Single developer + LLM team with clear SDLC workflow

**Mitigation:**
- **Enforced by schema** (can't accidentally query wrong context)
- **Clear documentation** (this report + architecture diagrams)
- **Code reviews** (LLM follows patterns, human reviews decisions)

**Probability:** VERY LOW

---

### 8.6 BIGGEST RISK: Monolithic V2 Approach

**Why it's the biggest risk:**

1. **Project owner explicit concern:** Rentals may be separate hosting (rentals.bestays.app)
2. **Future refactor cost:** 4-6 weeks of lost development time
3. **Breaking changes:** API and frontend routing changes
4. **Data migration:** Complex, error-prone, requires downtime
5. **Lost opportunity cost:** Could be building features instead of refactoring
6. **Architectural mismatch:** Business model (rentals ≠ listings) doesn't match code model

**Probability: HIGH**

**Cost: HIGH**

**Recommendation: Avoid this risk by implementing bounded contexts now**

---

### 8.7 SMALLEST RISK: Bounded Contexts (Listings Only First)

**Why it's the smallest risk:**

1. **Milestone 01 is 100% listings** (validated by US-002 to US-020)
2. **Can add rentals later** without breaking listings code
3. **Aligns with business strategy** (separate hosting plan)
4. **Modular monolith = low overhead** (not microservices complexity)
5. **Demonstrates architectural vision** to stakeholders
6. **Small investment upfront** (+1.5 days to US-002, +2 weeks overall)
7. **Large payoff later** (avoid 4-6 week refactor)

**Probability: LOW**

**Cost: LOW**

**Recommendation: This is the pragmatic choice**

---

## 9. Recommendations Summary

### 9.1 Architectural Decision

**DECISION: Implement Bounded Contexts with Phased Rollout**

**Phase 1 (Milestone 01 - NOW):**
- ✅ Listings context only
- ✅ Shared kernel (media, locations, agents, amenities)
- ✅ PostgreSQL schemas: listings, shared
- ✅ API: /api/v1/listings/*
- ✅ Frontend: /listings/*

**Phase 2 (Post-MVP):**
- ✅ Rentals context
- ✅ Booking infrastructure
- ✅ API: /api/v1/rentals/*
- ✅ Frontend: /rentals/*

**Phase 3 (Future):**
- ✅ Businesses context (if market demands)
- ✅ Extract rentals to separate deployment (rentals.bestays.app)

---

### 9.2 What to Implement NOW (for US-002)

**Database:**
1. Create `listings` schema with properties table (see Section 5.2)
2. Create `shared` schema with media_files, agents, locations, amenities_catalog
3. Seed amenities catalog (150+ amenities from V2 analysis)

**Backend:**
1. Implement FastAPI models (Pydantic for listings context)
2. Implement API endpoints: /api/v1/listings/featured, /api/v1/listings/public, /api/v1/listings/cms
3. Implement media upload: /api/v1/shared/media/upload
4. Implement Clerk authentication integration

**Frontend:**
- **NO CHANGES** to components (PropertyCard works same way)
- Update API endpoint URLs (from /properties to /listings)

**Timeline:**
- Database setup: 1 day
- API implementation: 2 days (adapting existing V2 logic)
- Clerk integration: 1 day (already done in US-001)
- Testing: 1 day

**Total: +5 days before US-002 implementation starts**

**ROI:** Avoid 4-6 week refactor later, enable future separate hosting

---

### 9.3 What to DEFER (Phase 2+)

**Defer to Phase 2:**
- Rentals context implementation
- Booking calendar infrastructure
- Guest review system
- Dynamic pricing
- Payment gateway integration

**Defer to Phase 3:**
- Businesses context
- Financial document uploads
- NDA requirements
- Business broker workflows

**Defer indefinitely:**
- Microservice extraction (unless proven necessary)
- Complex domain events (simple function calls sufficient)
- Distributed transactions (not needed with modular monolith)

---

### 9.4 Priority Action Items

**IMMEDIATE (Week 1-2 - before US-002):**
1. ✅ Review this architectural recommendation with stakeholder
2. ✅ Get approval on bounded contexts approach
3. ✅ Create database schemas (listings, shared)
4. ✅ Implement listings.properties table
5. ✅ Implement shared kernel tables
6. ✅ Seed amenities catalog
7. ✅ Update Alembic migrations
8. ✅ Create Pydantic models for listings
9. ✅ Implement API endpoints for listings
10. ✅ Update API documentation (Swagger)

**SHORT-TERM (Milestone 01 - Week 3-12):**
1. ✅ Implement US-002 through US-020 using listings context
2. ✅ Validate architecture with real data
3. ✅ Monitor performance (query times, page load)
4. ✅ Gather user feedback
5. ✅ Document lessons learned

**MEDIUM-TERM (Post-Milestone 01):**
1. ✅ Assess market demand for vacation rentals
2. ✅ Plan rentals context implementation
3. ✅ Design booking infrastructure
4. ✅ Implement Phase 2 (rentals)

**LONG-TERM (Phase 3+):**
1. ✅ Evaluate businesses context need
2. ✅ Consider microservice extraction (if traffic demands)
3. ✅ Implement advanced search (ML-powered, vector search)
4. ✅ Add emerging property types (co-living, serviced apartments)

---

### 9.5 Decision Timeline

**DECIDE NOW:**
- ✅ Bounded contexts architecture (YES)
- ✅ Start with listings context only (YES)
- ✅ Shared kernel design (YES)
- ✅ Phase 1 scope (listings + shared)

**DECIDE LATER (Post-Milestone 01):**
- ⏳ When to implement rentals context
- ⏳ Businesses context (yes/no)
- ⏳ Microservice extraction timeline
- ⏳ International expansion (beyond Thailand)

**DECIDE NEVER:**
- ❌ Monolithic V2 schema (REJECTED - too risky)
- ❌ Premature microservices (REJECTED - unnecessary complexity)
- ❌ Complex domain events (REJECTED - simple calls sufficient)

---

## 10. Conclusion

### 10.1 Final Recommendation

**Implement Bounded Contexts (Listings Only First) for Bestays Real Estate Platform**

This recommendation provides:

**1. Strategic Alignment**
- Respects project owner's vision (separate hosting for rentals)
- Aligns with business reality (rentals ≠ listings)
- Enables future independent scaling and deployment

**2. Technical Soundness**
- Based on Domain-Driven Design best practices
- Validated by industry leaders (Zillow, Airbnb, Booking.com)
- Modular monolith = benefits of separation without microservice complexity

**3. Pragmatic MVP Approach**
- Starts with listings only (Milestone 01 scope)
- Low initial complexity (single context)
- Proves architecture before expanding
- Small investment upfront (+5 days) vs large payoff later (avoid 4-6 week refactor)

**4. Risk Mitigation**
- Avoids biggest risk (monolithic schema future refactor)
- Enables phased rollout (validate before expanding)
- Provides rollback options (keep architecture flexible)

**5. Developer Experience**
- Clear domain boundaries (easier to reason about)
- Context-specific schemas (appropriate fields per domain)
- Single developer + LLM can manage (no team coordination needed)

---

### 10.2 Success Metrics

**Phase 1 (Milestone 01) Success Criteria:**
- ✅ Listings context implemented and functional
- ✅ US-002 through US-020 delivered on schedule
- ✅ API response times meet targets (<500ms for queries)
- ✅ Zero cross-context coupling (clean separation validated)
- ✅ User feedback positive on core features

**Phase 2 (Rentals) Success Criteria:**
- ✅ Rentals context added without breaking listings
- ✅ Booking infrastructure functional
- ✅ Separate deployment proven (rentals.bestays.app)
- ✅ Performance maintained across both contexts

---

### 10.3 Next Steps

**Immediate Action (Now):**
1. **Stakeholder review** - Present this recommendation to project owner
2. **Get approval** - Confirm bounded contexts approach
3. **Create user story** - US-016 updated to "Implement Bounded Contexts Architecture"
4. **Start implementation** - Week 1-2 before US-002

**Questions for Stakeholder:**
1. ❓ Do you agree with bounded contexts approach?
2. ❓ Are you comfortable with +5 days upfront for architecture setup?
3. ❓ Do you want rentals in Phase 2 (post-MVP) or later?
4. ❓ Should we implement businesses context at all?

**Decision Required:**
- ✅ Approve bounded contexts approach → Proceed with Phase 1
- ❌ Reject bounded contexts → Accept V2 monolithic schema (with future refactor risk)

---

**This architectural review provides the foundation for building a scalable, maintainable real estate platform that can grow with Bestays' business vision.**

---

## Appendix A: Database Schema Diagrams

### Listings Context Schema

```
┌─────────────────────────────────────────────────────────────────┐
│                    listings.properties                         │
├─────────────────────────────────────────────────────────────────┤
│ id (UUID, PK)                                                  │
│ title (TEXT, NOT NULL)                                         │
│ description (TEXT)                                             │
│ title_deed (TEXT)                                              │
│                                                                 │
│ property_type (ENUM: land, house, villa, ...)                 │
│ transaction_type (ENUM: sale, lease)                          │
│                                                                 │
│ sale_price (BIGINT)                                            │
│ lease_price (BIGINT)                                           │
│ currency (TEXT)                                                │
│ price_per_sqm (NUMERIC)                                        │
│                                                                 │
│ physical_specs (JSONB)                                         │
│ location_details (JSONB)                                       │
│ amenities (JSONB)                                              │
│                                                                 │
│ ownership_type (ENUM: freehold, leasehold, company)           │
│ foreign_quota (BOOLEAN)                                        │
│ rental_yield (NUMERIC)                                         │
│ price_trend (TEXT)                                             │
│                                                                 │
│ cover_image_id (UUID) → shared.media_files                    │
│ virtual_tour_url (TEXT)                                        │
│ video_url (TEXT)                                               │
│                                                                 │
│ is_published (BOOLEAN)                                         │
│ is_featured (BOOLEAN)                                          │
│ listing_priority (INT)                                         │
│                                                                 │
│ created_by (UUID) → shared.agents                             │
│ created_at, updated_at, deleted_at (TIMESTAMPTZ)              │
└─────────────────────────────────────────────────────────────────┘
```

### Shared Kernel Schema

```
┌──────────────────────┐     ┌─────────────────────────┐
│  shared.agents       │     │  shared.media_files     │
├──────────────────────┤     ├─────────────────────────┤
│ id (UUID, PK)        │     │ id (UUID, PK)           │
│ clerk_user_id (TEXT) │     │ property_id (UUID)      │
│ email (TEXT)         │     │ property_context (TEXT) │
│ name (TEXT)          │     │ media_type (TEXT)       │
│ phone (TEXT)         │     │ storage_url (TEXT)      │
│ languages (TEXT[])   │     │ thumbnail_url (TEXT)    │
│ contexts (TEXT[])    │     │ display_order (INT)     │
└──────────────────────┘     │ metadata (JSONB)        │
                              └─────────────────────────┘

┌────────────────────────┐   ┌──────────────────────────┐
│  shared.locations      │   │  shared.amenities_catalog│
├────────────────────────┤   ├──────────────────────────┤
│ id (UUID, PK)          │   │ id (TEXT, PK)            │
│ region (TEXT)          │   │ category (TEXT)          │
│ district (TEXT)        │   │ name (JSONB)             │
│ sub_district (TEXT)    │   │ icon (TEXT)              │
│ coordinates (POINT)    │   │ applicable_contexts[]    │
│ metadata (JSONB)       │   │ display_order (INT)      │
└────────────────────────┘   └──────────────────────────┘
```

---

## Appendix B: API Endpoint Reference

### Listings Context Endpoints

**Public Endpoints (Guest Access):**
```
GET /api/v1/listings/public
  Query params: property_type, transaction_type, location_region, min_price, max_price
  Response: { properties: [...], total: N }

GET /api/v1/listings/public/{id}
  Response: { property: {...} }

GET /api/v1/listings/featured
  Query params: category, limit
  Response: { properties: [...] }
```

**CMS Endpoints (Agent Access - Auth Required):**
```
GET /api/v1/listings/cms
  Headers: Authorization: Bearer {token}
  Response: { properties: [...] }

POST /api/v1/listings/cms
  Headers: Authorization: Bearer {token}
  Body: { title, property_type, transaction_type, ... }
  Response: { property: {...} }

PUT /api/v1/listings/cms/{id}
  Headers: Authorization: Bearer {token}
  Body: { title, description, ... }
  Response: { property: {...} }

DELETE /api/v1/listings/cms/{id}
  Headers: Authorization: Bearer {token}
  Response: { success: true }
```

**Shared Endpoints:**
```
POST /api/v1/shared/media/upload
  Headers: Authorization: Bearer {token}
  Body: FormData { file, property_id, property_context, media_type }
  Response: { media_file: {...} }

GET /api/v1/shared/locations
  Query params: region, district
  Response: { locations: [...] }

GET /api/v1/shared/amenities
  Query params: category, context
  Response: { amenities: [...] }
```

---

## Appendix C: Frontend Route Structure

```
bestays.app/
├── /                              # Homepage (aggregate all contexts)
│   ├── Hero section
│   ├── Featured listings section
│   ├── Categories navigation
│   └── Top locations
│
├── /listings/                     # Listings context routes
│   ├── /listings/{id}             # Property detail
│   ├── /listings/land-for-sale    # Category: Land For Sale
│   ├── /listings/land-for-lease   # Category: Land For Lease
│   ├── /listings/properties-for-sale  # Category: Houses/Villas/Condos For Sale
│   └── /listings/business-for-sale    # Category: Businesses For Sale
│
├── /locations/                    # Location-based browsing
│   ├── /locations/{region}        # All properties in region
│   └── /locations/{region}/{area} # All properties in specific area
│
├── /cms/                          # Agent dashboard (auth required)
│   ├── /cms/listings              # Manage listing properties
│   │   ├── /cms/listings/new      # Create new listing
│   │   └── /cms/listings/{id}     # Edit listing
│   │
│   └── /cms/rentals               # Manage rental properties (Phase 2)
│       ├── /cms/rentals/new
│       └── /cms/rentals/{id}
│
└── /rentals/                      # Rentals context routes (Phase 2)
    ├── /rentals/{id}              # Rental detail
    └── /rentals/search            # Search vacation rentals
```

---

**END OF REPORT**

**File saved to:** `.claude/reports/20251107-property-domain-architecture-review.md`

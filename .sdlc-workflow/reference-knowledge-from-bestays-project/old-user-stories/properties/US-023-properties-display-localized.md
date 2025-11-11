# US-023: Property Import & Display with Localization

**Domain:** properties
**Feature:** display
**Scope:** localized
**Status:** READY
**Created:** 2025-11-09
**Default Product:** bestays
**Portable:** true
**Ported To:** []

---

## Description

Import existing rental properties from old bestays.app database and display them on the new SvelteKit homepage with full multi-language support. Users can browse all available rental properties in a responsive grid layout with locale switching (EN/TH).

**User Story:**
As a user visiting bestays.app, I want to see all available rental properties on the homepage in my preferred language (English or Thai), so that I can browse and explore rental options.

**Key Features:**
- Data import from old bestays.app Supabase database
- Property grid display on homepage (below hero section)
- Property detail pages with image gallery
- Multi-language support (EN/TH) for all property data
- Field names AND values localized
- Locale switcher in header
- Responsive design (grid adapts to screen size)
- Future-ready for infinite scroll/pagination

**Context:**
- Old bestays.app was REAL ESTATE site (6 categories: freehold, land-for-sale, business-for-sale, properties-for-rent, etc.)
- Old site has ONLY English values in database
- New bestays.app is RENTALS ONLY site (simpler, focused)
- Building on US-016 (Property V2 schema with 5 JSONB fields)
- Building on US-018 (Infrastructure with i18n support)
- Reference old site structure: `/Users/solo/Projects/_repos/react-workspace/src/apps/bestays-web`

---

## Acceptance Criteria

### Phase 1: Data Import & Transformation
- [ ] AC-1: Import script extracts rental properties from old bestays.app Supabase database
- [ ] AC-2: Script transforms plain English data → localized JSONB format (`{ en: "value", th: "placeholder" }`)
- [ ] AC-3: Script populates all 5 JSONB fields (physical_specs, location_details, amenities, policies, contact_info)
- [ ] AC-4: Field names stored with localizations (`{ en: "Bedrooms", th: "ห้องนอน" }`)
- [ ] AC-5: Images remain as Supabase Storage URLs (no migration to R2 yet)
- [ ] AC-6: Import validation ensures data integrity (required fields, valid enums)

### Phase 2: Localized Homepage with Property Grid
- [ ] AC-7: Homepage displays hero section (header, background image, tagline) with localized text
- [ ] AC-8: Property grid displays below hero with all imported properties
- [ ] AC-9: Grid layout: 3 columns (desktop), 2 columns (tablet), 1 column (mobile)
- [ ] AC-10: Property cards show: primary image, title, price, bedrooms, bathrooms, location (all localized)
- [ ] AC-11: Locale switcher in header toggles between EN/TH
- [ ] AC-12: All property data updates when locale changes (no page reload)
- [ ] AC-13: Grid uses infinite scroll or "Load More" button (limit N items initially)

### Phase 3: Localized Property Detail Page
- [ ] AC-14: Detail page URL: `/properties/[id]`
- [ ] AC-15: Image gallery with carousel (multiple property images)
- [ ] AC-16: Property information sections display all JSONB fields (localized)
- [ ] AC-17: Amenities displayed as categorized list (comfort, security, outdoor, etc.) - localized
- [ ] AC-18: Policies displayed (pets, smoking, house rules) - localized
- [ ] AC-19: Location details (proximity to beach, mountain view, etc.) - localized
- [ ] AC-20: Contact information displayed - localized
- [ ] AC-21: SEO meta tags (title, description) generated from localized property data

### Phase 4: Localization Infrastructure
- [ ] AC-22: i18n library integrated (paraglide-js from US-018 or similar)
- [ ] AC-23: Locale context provider wraps app
- [ ] AC-24: Translation helper functions for JSONB fields (`getLocalizedValue(field, locale)`)
- [ ] AC-25: Field name dictionary created (150+ field labels in EN/TH)
- [ ] AC-26: URL locale parameter (`/en/properties`, `/th/properties`) OR cookie-based
- [ ] AC-27: Locale preference persisted across sessions

### Phase 5: Testing & Validation
- [ ] AC-28: E2E test: Homepage loads with property grid in EN
- [ ] AC-29: E2E test: Locale switcher changes all content to TH
- [ ] AC-30: E2E test: Property detail page displays localized data
- [ ] AC-31: E2E test: Grid responsive layout (desktop, tablet, mobile)
- [ ] AC-32: Unit tests for localization helpers
- [ ] AC-33: Import script validation tests

---

## Technical Notes

### Architecture Decisions

**1. Localization Strategy: Structured JSONB with Locale Keys**

Old structure (English only):
```json
{
  "amenities": ["Pool", "WiFi", "Air Conditioning"]
}
```

New structure (Localized):
```json
{
  "amenities": {
    "en": ["Pool", "WiFi", "Air Conditioning"],
    "th": ["สระว่ายน้ำ", "ไวไฟ", "เครื่องปรับอากาศ"]
  },
  "physical_specs": {
    "bedrooms": {
      "value": 3,
      "label": {
        "en": "Bedrooms",
        "th": "ห้องนอน"
      }
    }
  }
}
```

**Rationale:**
- Field names AND values both localized
- Admins can edit labels and values per locale
- Future-proof for additional locales (JA, ZH, etc.)
- PostgreSQL JSONB efficiently stores nested structures

**2. Translation Strategy: English First, Thai Placeholders**

Import process:
1. Extract English values from old DB
2. Generate Thai placeholders (copy English or use "[TH]" prefix)
3. Agents/admins edit Thai translations later via inline editing (Phase 2 - US-022)

**Future Enhancement:**
- Auto-translate using OpenRouter LLM during import (optional)
- Translation management UI for bulk updates

**3. Image Storage: Keep Supabase URLs (R2 Migration Deferred)**

Current approach:
- Import script stores existing Supabase Storage URLs
- Property model references URLs as-is
- R2 migration happens in future story (US-024 or similar)

**Rationale:**
- Faster implementation (no image migration)
- Supabase Storage working fine currently
- Can migrate later without affecting property data structure

**4. Homepage Structure: Hero + Grid (No Categories)**

Old site: 6 categories (freehold, land-for-sale, properties-for-rent, etc.)
New site: Single grid (all rentals)

**Rationale:**
- Simpler UX (users don't need to choose category)
- All properties are rentals (no need for categorization)
- Matches user requirement: "homepage with grid of all properties"

**5. Property Grid Component: Reuse Old Site Patterns**

Reuse from old site:
- `PropertyListing` component structure (server component fetches data)
- `PropertyListingClient` component (client-side grid rendering)
- `PropertyListingCard` component (individual property card)

Adapt for:
- Svelte 5 instead of React
- Localization support
- Property V2 schema (JSONB fields)

### Dependencies

**External:**
- Old bestays.app Supabase database (read access for import)
- Paraglide-js or similar i18n library (from US-018)
- TanStack Query (data fetching)
- Svelte 5 (component framework)

**Internal:**
- US-016: Property V2 schema (COMPLETED)
- US-018: Infrastructure setup (i18n support implemented)
- US-020: Inline editing patterns (for future Phase 2)

### Constraints

- Old database has ONLY English values (must generate Thai placeholders)
- Property V2 schema must support nested localization structure
- Image URLs must remain valid after import (no broken links)
- Locale switching must be performant (< 200ms to update UI)
- Grid must handle large datasets (500+ properties) efficiently

### Technical Risks

**High Risk:**
- Import script data mapping errors → Mitigate with validation and dry-run mode
- JSONB localization structure too complex → Mitigate with helper functions
- Performance issues with large localized JSONB → Mitigate with GIN indexes (already implemented in US-016)

**Medium Risk:**
- Broken image URLs after import → Mitigate with URL validation
- i18n library not supporting JSONB → Mitigate with custom translation helpers
- SEO issues with localized URLs → Mitigate with proper hreflang tags

**Low Risk:**
- Responsive grid layout issues → Well-established pattern from old site
- Locale switching bugs → E2E tests cover all scenarios

### Research Questions (TASK-023-01 RESEARCH Phase)

1. **i18n Implementation**
   - Which i18n library is used in US-018?
   - How are locales stored (URL param, cookie, localStorage)?
   - What's the current locale switching implementation?

2. **Old Database Structure**
   - What's the exact schema of old bestays.app properties table?
   - How are amenities stored (array, JSON, separate table)?
   - How many rental properties exist?
   - Are there any existing Thai translations?

3. **Import Script Design**
   - Python script or TypeScript/Node.js?
   - Direct database access or API endpoint?
   - Batch import or one-by-one?
   - How to generate Thai placeholders?

4. **Property V2 JSONB Structure**
   - How to nest localization in existing JSONB fields?
   - Do we need schema migration for localization support?
   - How to query localized fields efficiently?

5. **Grid Performance**
   - Pagination strategy (offset-based or cursor-based)?
   - How many properties to load initially?
   - Infinite scroll or "Load More" button?
   - Image lazy loading strategy?

---

## Related Stories

- **US-016:** Property Migration Design (Property V2 schema) - COMPLETED
- **US-018:** Infrastructure Setup (i18n, Docker, database) - COMPLETED
- **US-020:** Inline Content Editing (pattern for future editing) - COMPLETED
- **US-022:** AI-Powered Property Management (DEFERRED to Phase 2)
- **US-024:** Property Porting to Real Estate (TBD)
- **US-025:** Advanced Property Search/Filters (TBD)

---

## Implementation Phases (Recommended Task Breakdown)

### TASK-023-01: RESEARCH (i18n + Import Strategy)
- Review US-018 i18n implementation
- Analyze old bestays.app database structure
- Design localized JSONB schema
- Design import script architecture
- Research grid performance patterns
- Create implementation plan

### TASK-023-02: PLANNING (Localization Architecture + Import Design)
- Define localized JSONB structure for all 5 fields
- Design field name dictionary (150+ labels in EN/TH)
- Design import script workflow (ETL pipeline)
- Design homepage layout (hero + grid)
- Design property detail page layout
- Design locale switching UX
- Create quality gate checklist

### TASK-023-03: IMPLEMENTATION - Data Import Script (Backend)
- Create import script (Python or TypeScript)
- Extract properties from old Supabase DB
- Transform to localized JSONB format
- Generate Thai placeholders
- Validate data integrity
- Dry-run mode for testing
- Execute import to production database
- Write unit tests

### TASK-023-04: IMPLEMENTATION - Localized Homepage with Grid (Frontend)
- Create hero section component (localized)
- Create PropertyGrid component (Svelte 5)
- Create PropertyCard component (localized data)
- Implement locale switcher
- Implement pagination or infinite scroll
- Implement responsive grid layout
- Write Storybook stories

### TASK-023-05: IMPLEMENTATION - Localized Property Detail Page (Frontend)
- Create property detail page route (`/properties/[id]`)
- Create image gallery component
- Create property info sections (all JSONB fields)
- Implement localization for all sections
- Add SEO meta tags (localized)
- Write Storybook stories

### TASK-023-06: IMPLEMENTATION - Localization Helpers (Frontend/Backend)
- Create translation helper functions
- Create field name dictionary
- Implement locale context provider
- Implement locale persistence (cookie/localStorage)
- Write unit tests

### TASK-023-07: TESTING (E2E + Integration Tests)
- E2E test: Homepage grid loads in EN
- E2E test: Locale switcher changes to TH
- E2E test: Property detail page displays localized data
- E2E test: Responsive layout (desktop, tablet, mobile)
- Integration test: Import script with sample data
- Unit test: Localization helpers

### TASK-023-08: VALIDATION (User Testing + Deployment)
- User testing with EN/TH speakers
- Verify Thai translations quality (placeholders acceptable)
- Performance testing (grid load time, locale switching)
- Deploy to staging
- Deploy to production (feature flag)

---

## Tasks

[Automatically populated by system - do not edit manually]

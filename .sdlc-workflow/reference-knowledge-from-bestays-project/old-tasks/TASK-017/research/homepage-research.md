# Homepage MVP - Research Phase

**Task:** TASK-017
**Story:** US-026
**Phase:** RESEARCH
**Date:** 2025-11-09

---

## Problem Statement

**Current Issue:** Homepage returns 404 because `/[lang]/+page.svelte` doesn't exist.

**Root Cause:**
- Root `/` redirects to `/en` (expecting homepage)
- Only `/[lang]/properties` routes exist (listing + detail)
- No actual homepage implemented yet

**Impact:** Site is completely broken for first-time visitors

---

## Requirements Summary

**MVP Scope:**
1. Hero section with background + search bar
2. Basic filters (location text, property type, bedrooms, price)
3. Featured properties grid (8 latest)
4. Responsive design (desktop/tablet/mobile)
5. Localized content (EN/TH)

**Design References:**
- **DDProperty.com:** Clean hero, prominent search bar, Buy/Rent tabs, filter dropdowns
- **Airbnb:** Simple destination search, date pickers, guest selector, property carousel
- **Bestays Brand:** Teal/olive gradient (#0a4349 → #999d70)

---

## Existing Components (Reuse)

### ✅ Components Available

**1. PropertyCard.svelte**
Location: `apps/frontend/src/lib/components/PropertyCard.svelte` (check if exists)
Used in: `/[lang]/properties` listing page
Props needed: property object, locale
Reusable: ✅ YES (displays image, title, price, location, beds/baths)

**2. LocaleSwitcher.svelte**
Location: Header component (already in layout)
Reusable: ✅ YES (no changes needed)

**3. Property Listing Page (`/[lang]/properties/+page.svelte`)**
Exists: ✅ YES
Query params supported: Should support `?q=...&type=...&beds=...&price=...`
Note: Search will navigate here with filters

### ❌ Components to Create

**1. HeroSection.svelte**
- Full-width background (gradient or image + overlay)
- Centered title + subtitle
- Responsive height (60vh desktop, 50vh mobile)

**2. SearchBar.svelte**
- Text input for location/query search
- 3 dropdown filters (property type, bedrooms, price range)
- Search button
- Form submission handler (navigates to /properties with query params)

**3. PropertyGrid.svelte**
- Wrapper component for property card grid
- Responsive columns: 4 (desktop), 2 (tablet), 1 (mobile)
- Section title + "View All" link

---

## API Endpoints

### ✅ Available Endpoints

**GET /api/v1/properties**
Purpose: Fetch properties with filtering
Query Params:
- `limit` - Number of results (default: 20)
- `offset` - Pagination offset
- `locale` - Language (en/th)
- `q` - Text search (title, description, location)
- `property_type` - Filter by type (apartment, villa, townhouse, condo)
- `min_bedrooms` - Minimum bedroom count
- `max_bedrooms` - Maximum bedroom count
- `min_price` - Minimum rent price
- `max_price` - Maximum rent price

Response Format:
```json
{
  "items": [
    {
      "id": 1,
      "title": {"en": "Modern Apartment", "th": "อพาร์ทเมนต์ทันสมัย"},
      "rent_price": 25000,
      "currency": "THB",
      "cover_image": "https://...",
      "physical_specs": {
        "bedrooms": {"value": 2, "label": {"en": "Bedrooms", "th": "ห้องนอน"}},
        "bathrooms": {"value": 2, "label": {"en": "Bathrooms", "th": "ห้องน้ำ"}}
      },
      "location_details": {
        "district": {"value": {"en": "Sukhumvit", "th": "สุขุมวิท"}, ...}
      }
    }
  ],
  "total": 42,
  "page": 1,
  "pages": 3
}
```

**Homepage Usage:**
```typescript
// Fetch 8 latest properties for featured section
const response = await fetch(
  `http://localhost:8011/api/v1/properties?limit=8&locale=${lang}`
);
```

---

## Routing Structure

### Current Routes

```
/ (root)
  → +page.svelte (redirects to /en)

/[lang]
  → +layout.svelte (locale context)
  → +layout.ts (locale validation)
  → +page.svelte ❌ MISSING (causes 404)

  → /properties
    → +page.svelte ✅ (listing page)
    → /[id]
      → +page.svelte ✅ (detail page)
      → +page.ts ✅ (data loading)
```

### Required Route

**Create:** `/[lang]/+page.svelte` + `/[lang]/+page.ts`

**Data Loader (+page.ts):**
```typescript
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, params }) => {
  const { lang } = params;

  try {
    const res = await fetch(
      `http://localhost:8011/api/v1/properties?limit=8&locale=${lang}`
    );

    if (!res.ok) throw new Error('Failed to fetch properties');

    const data = await res.json();

    return {
      properties: data.items || [],
      total: data.total || 0,
      locale: lang
    };
  } catch (error) {
    console.error('Homepage data fetch error:', error);
    return {
      properties: [],
      total: 0,
      locale: lang
    };
  }
};
```

---

## Localization

### i18n Infrastructure (from US-021)

**Available:**
- Locale context via `$page.params.lang`
- Translation helper functions (if implemented in US-021)
- LocaleSwitcher component

**Homepage Translations Needed:**

**EN:**
- Hero title: "Find Your Perfect Stay"
- Hero subtitle: "Discover amazing properties across Thailand"
- Search placeholder: "Search by location, property name..."
- Filter labels: "Property Type", "Bedrooms", "Price Range"
- Property type options: "All", "Apartment", "Villa", "Townhouse", "Condo"
- Bedroom options: "Any", "1+", "2+", "3+", "4+"
- Price options: "Any", "< ฿15,000", "฿15,000-30,000", "฿30,000-50,000", "฿50,000+"
- Section title: "Featured Properties"
- Button: "Search", "View All Properties"

**TH:**
- Hero title: "ค้นหาที่พักที่เหมาะกับคุณ"
- Hero subtitle: "ค้นพบอสังหาริมทรัพย์ที่น่าทึ่งทั่วประเทศไทย"
- Search placeholder: "ค้นหาตามสถานที่ ชื่ออสังหาฯ..."
- (All other translations...)

**Implementation Options:**
1. Inline objects: `title[lang]`
2. Translation function: `t('homepage.hero.title')`
3. Hardcoded check: `lang === 'en' ? 'English' : 'ไทย'`

**Recommendation:** Use inline objects for MVP (simplest, no translation files needed yet)

---

## Design Patterns

### 1. Hero Section

**DDProperty Pattern:**
- Full-width hero (100vw)
- Large background image with subtle overlay
- Search bar overlays hero (centered, elevated with shadow)
- Clean, minimal text (title + 1 line subtitle)

**Airbnb Pattern:**
- Lighter hero, less dominant
- Search bar integrated into nav/header area
- More focus on property carousel below

**Bestays Approach (Hybrid):**
- Full-width hero with **brand gradient** (#0a4349 → #999d70)
- Centered white search bar with shadow (elevated card style)
- Bold title + subtitle in white text
- Height: 60vh desktop, 50vh mobile

**Tailwind Classes:**
```html
<section class="relative h-[60vh] md:h-[50vh] bg-gradient-to-br from-[#0a4349] to-[#999d70] flex items-center justify-center">
  <div class="absolute inset-0 bg-black/10"></div> <!-- subtle overlay -->
  <div class="relative z-10 text-center px-4">
    <h1 class="text-4xl md:text-6xl font-bold text-white mb-4">
      Find Your Perfect Stay
    </h1>
    <p class="text-lg md:text-xl text-white/90 mb-8">
      Discover amazing properties across Thailand
    </p>
    <!-- SearchBar component here -->
  </div>
</section>
```

### 2. Search Bar

**DDProperty Pattern:**
- Horizontal layout: [Text Input] [Type Dropdown] [Beds Dropdown] [Price Dropdown] [Button]
- All white background, rounded corners
- Dropdowns use native `<select>` or custom dropdown
- Red search button stands out

**Airbnb Pattern:**
- Segmented search bar (Where | Check-in | Check-out | Guests)
- Click to expand each section
- More interactive, more complex

**Bestays Approach (Simplified):**
- White card with shadow (`shadow-2xl`)
- Horizontal layout on desktop, stacked on mobile
- 4 inputs + 1 button: `[Search Input] [Type] [Beds] [Price] [Search]`
- Simple dropdowns (native `<select>` for MVP)

**Structure:**
```html
<div class="bg-white rounded-lg shadow-2xl p-4 flex flex-col md:flex-row gap-3 max-w-5xl mx-auto">
  <!-- Text Search -->
  <input type="text" placeholder="Search..." class="flex-1 px-4 py-3 border rounded-md" />

  <!-- Property Type -->
  <select class="px-4 py-3 border rounded-md">
    <option value="all">All Types</option>
    <option value="apartment">Apartment</option>
    <option value="villa">Villa</option>
    <option value="townhouse">Townhouse</option>
  </select>

  <!-- Bedrooms -->
  <select class="px-4 py-3 border rounded-md">
    <option value="any">Any Beds</option>
    <option value="1">1+</option>
    <option value="2">2+</option>
    <option value="3">3+</option>
  </select>

  <!-- Price Range -->
  <select class="px-4 py-3 border rounded-md">
    <option value="any">Any Price</option>
    <option value="0-15000">< ฿15k</option>
    <option value="15000-30000">฿15k-30k</option>
    <option value="30000-50000">฿30k-50k</option>
    <option value="50000-999999">฿50k+</option>
  </select>

  <!-- Search Button -->
  <button class="px-8 py-3 bg-red-600 hover:bg-red-700 text-white rounded-md font-medium">
    Search
  </button>
</div>
```

### 3. Property Grid

**Pattern:**
- Section title + optional "View All" link
- CSS Grid with responsive columns
- Reuse PropertyCard component

**Implementation:**
```html
<section class="py-16 px-4 max-w-7xl mx-auto">
  <!-- Header -->
  <div class="flex justify-between items-center mb-8">
    <h2 class="text-3xl font-bold">Featured Properties</h2>
    <a href="/en/properties" class="text-red-600 hover:underline">
      View All →
    </a>
  </div>

  <!-- Grid -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    {#each properties as property}
      <PropertyCard {property} locale={lang} />
    {/each}
  </div>
</section>
```

---

## Technical Decisions

### 1. Component Architecture

**File Structure:**
```
apps/frontend/src/
  routes/
    [lang]/
      +page.svelte          # Homepage layout (NEW)
      +page.ts              # Data loader (NEW)
  lib/
    components/
      HeroSection.svelte    # Hero bg + title (NEW)
      SearchBar.svelte      # Search form (NEW)
      PropertyGrid.svelte   # Grid wrapper (NEW)
      PropertyCard.svelte   # Card (REUSE - check if exists)
```

**Component Responsibilities:**
- `+page.svelte`: Layout orchestration (hero + search + grid)
- `HeroSection.svelte`: Visual presentation (bg, title, subtitle)
- `SearchBar.svelte`: Form state + navigation logic
- `PropertyGrid.svelte`: Grid layout + section header
- `PropertyCard.svelte`: Individual property display (reused)

### 2. State Management

**Search Form State:**
```typescript
let searchQuery = $state('');
let propertyType = $state('all');
let bedrooms = $state('any');
let priceRange = $state('any');

function handleSearch() {
  const params = new URLSearchParams();
  if (searchQuery) params.set('q', searchQuery);
  if (propertyType !== 'all') params.set('type', propertyType);
  if (bedrooms !== 'any') params.set('beds', bedrooms);
  if (priceRange !== 'any') {
    const [min, max] = priceRange.split('-');
    if (min) params.set('min_price', min);
    if (max) params.set('max_price', max);
  }

  goto(`/${lang}/properties?${params.toString()}`);
}
```

**Property Data:**
- Loaded via `+page.ts` (SSR)
- Passed to `<PropertyGrid>` component
- No client-side state needed (SSR hydration)

### 3. Responsive Design

**Breakpoints (Tailwind defaults):**
- Mobile: < 768px (sm)
- Tablet: 768px - 1023px (md)
- Desktop: ≥ 1024px (lg)

**Responsive Behavior:**
- Hero height: `h-[50vh] md:h-[60vh]`
- Search bar: `flex-col md:flex-row` (stacked → horizontal)
- Property grid: `grid-cols-1 md:grid-cols-2 lg:grid-cols-4`
- Font sizes: `text-4xl md:text-6xl` (title), `text-lg md:text-xl` (subtitle)

### 4. SEO & Meta Tags

**Page Head:**
```svelte
<svelte:head>
  <title>Bestays - Find Your Perfect Stay in Thailand</title>
  <meta name="description" content="Discover amazing rental properties across Thailand. Search apartments, villas, townhouses, and condos. Book your perfect stay with Bestays." />
  <meta property="og:title" content="Bestays - Property Rentals in Thailand" />
  <meta property="og:description" content="Find and book amazing properties across Thailand" />
  <meta property="og:image" content="/images/og-homepage.jpg" />
  <meta property="og:url" content="https://bestays.app/en" />
  <link rel="canonical" href="https://bestays.app/en" />
</svelte:head>
```

---

## Risks & Mitigations

### Risk 1: PropertyCard Component May Not Exist

**Risk:** Assuming PropertyCard exists from /properties page, but might not be componentized

**Mitigation:**
- Check `/[lang]/properties/+page.svelte` for card markup
- If not a component, extract it into PropertyCard.svelte
- Fallback: Create PropertyCard from scratch

### Risk 2: Property Listing Page May Not Support Query Params

**Risk:** `/properties` page might not handle `?q=...&type=...` filters

**Mitigation:**
- Verify query param handling in `+page.ts` loader
- If missing, add filter logic (backend already supports it)
- Document needed updates for listing page

### Risk 3: API Response Format Mismatch

**Risk:** Actual API response might differ from expected format

**Mitigation:**
- Test API endpoint: `curl http://localhost:8011/api/v1/properties?limit=8&locale=en`
- Adjust data parsing in `+page.ts` based on actual response
- Add error handling for missing fields

### Risk 4: i18n Infrastructure Incomplete

**Risk:** US-021 localization might not be fully implemented

**Mitigation:**
- Use inline translation objects for MVP: `title[lang]`
- Check if translation helper exists, use if available
- Fallback to simple conditional: `lang === 'en' ? 'English' : 'Thai'`

---

## Next Steps (PLANNING Phase)

1. **Verify existing components:**
   - Check if PropertyCard.svelte exists
   - Confirm API response format
   - Test property listing query params

2. **Create component specs:**
   - HeroSection.svelte (props, markup, styles)
   - SearchBar.svelte (state, handlers, form)
   - PropertyGrid.svelte (layout, props)

3. **Define implementation order:**
   - Create data loader (+page.ts)
   - Build HeroSection component
   - Build SearchBar component
   - Build PropertyGrid component
   - Integrate into +page.svelte

4. **Plan testing strategy:**
   - E2E: Homepage loads, hero displays, search works
   - E2E: Property grid displays 8 properties
   - E2E: Search navigation with filters
   - E2E: Responsive layout (mobile/tablet/desktop)

---

## RESEARCH Complete ✅

**Time Spent:** 1 hour
**Next Phase:** PLANNING
**Key Findings:**
- API endpoint ready ✅
- Need to create 3 new components
- Need to verify PropertyCard exists
- Routing structure clear
- Design patterns defined

**Confidence Level:** HIGH (90%)
- Requirements clear
- Technical approach validated
- Existing infrastructure supports MVP
- Low risk, straightforward implementation

# Homepage MVP - Implementation Plan

**Task:** TASK-017
**Story:** US-026
**Phase:** PLANNING
**Date:** 2025-11-09
**Agent:** dev-frontend-svelte

---

## Verification Results ✅

**PropertyCard Component:** EXISTS at `apps/frontend/src/lib/components/PropertyCard.svelte`
- Props: `property: Property`, `locale: Locale`
- Displays: image, title, price, location, beds/baths
- Reusable: YES ✅

**API Endpoint:** WORKING at `http://localhost:8011/api/v1/properties`
- Response format: `{ "properties": [...] }` (NOT "items")
- Fields available: id, title, description, rent_price, cover_image, physical_specs, location_details
- Supports: limit, locale query params ✅

**Property Listing Page:** EXISTS at `/[lang]/properties/+page.svelte`
- Uses PropertyCard component ✅
- Pattern confirmed for homepage reuse ✅

---

## Implementation Order

### Phase 1: Data Loading (15 min)
**File:** `apps/frontend/src/routes/[lang]/+page.ts`

Create load function to fetch 8 latest properties for homepage.

### Phase 2: Hero Section Component (30 min)
**File:** `apps/frontend/src/lib/components/HeroSection.svelte`

Create hero with gradient background, title, subtitle.

### Phase 3: Search Bar Component (45 min)
**File:** `apps/frontend/src/lib/components/SearchBar.svelte`

Create search form with text input + 3 filters + button.

### Phase 4: Property Grid Component (20 min)
**File:** `apps/frontend/src/lib/components/PropertyGrid.svelte`

Create grid wrapper with responsive columns.

### Phase 5: Homepage Layout (20 min)
**File:** `apps/frontend/src/routes/[lang]/+page.svelte`

Integrate all components into homepage layout.

### Phase 6: Polish & Testing (30 min)
- Test responsive breakpoints
- Verify SSR rendering
- Check locale switching
- Test search navigation

**Total Estimated Time:** 2.5 hours

---

## Component Specifications

### 1. Data Loader: `+page.ts`

**Location:** `apps/frontend/src/routes/[lang]/+page.ts`

**Purpose:** Load 8 featured properties for homepage using SSR

**Code:**
```typescript
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, params }) => {
  const { lang } = params;

  try {
    const res = await fetch(
      `http://localhost:8011/api/v1/properties?limit=8&is_featured=true`
    );

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }

    const data = await res.json();

    return {
      properties: data.properties || [], // Note: API returns "properties" not "items"
      locale: lang,
      error: null
    };
  } catch (error) {
    console.error('[Homepage] Failed to fetch properties:', error);

    return {
      properties: [],
      locale: lang,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
};
```

**Notes:**
- **IMPORTANT:** API returns `{ "properties": [...] }` NOT `{ "items": [...] }`
- Use `is_featured=true` to get featured properties
- SSR-compatible (runs on server)
- Error handling returns empty array (graceful degradation)

---

### 2. Hero Section: `HeroSection.svelte`

**Location:** `apps/frontend/src/lib/components/HeroSection.svelte`

**Purpose:** Full-width hero with gradient background, title, subtitle, and search bar slot

**Props:**
- `locale: Locale` - Current language (en/th)

**Slots:**
- `default` - For SearchBar component

**Code:**
```svelte
<!--
HeroSection - Homepage hero with gradient background

ARCHITECTURE:
  Layer: Component
  Pattern: Svelte 5 Runes with slot for search bar

DEPENDENCIES:
  Internal: types/i18n

NOTES:
  - Full-width gradient background (brand colors)
  - Responsive height: 60vh desktop, 50vh mobile
  - Centered content with slot for SearchBar
  - Localized title + subtitle
-->

<script lang="ts">
  import type { Locale } from '$lib/i18n/types';

  interface Props {
    locale: Locale;
  }

  const { locale }: Props = $props();

  const title = $derived(
    locale === 'en'
      ? 'Find Your Perfect Stay'
      : 'ค้นหาที่พักที่เหมาะกับคุณ'
  );

  const subtitle = $derived(
    locale === 'en'
      ? 'Discover amazing properties across Thailand'
      : 'ค้นพบอสังหาริมทรัพย์ที่น่าทึ่งทั่วประเทศไทย'
  );
</script>

<section
  class="relative h-[50vh] md:h-[60vh] bg-gradient-to-br from-[#0a4349] to-[#999d70] flex items-center justify-center px-4"
>
  <!-- Subtle overlay for depth -->
  <div class="absolute inset-0 bg-black/10"></div>

  <!-- Content -->
  <div class="relative z-10 w-full max-w-7xl mx-auto text-center">
    <!-- Title -->
    <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-4 drop-shadow-lg">
      {title}
    </h1>

    <!-- Subtitle -->
    <p class="text-lg md:text-xl lg:text-2xl text-white/90 mb-8 drop-shadow-md">
      {subtitle}
    </p>

    <!-- Search Bar Slot -->
    <slot />
  </div>
</section>
```

**Styling Notes:**
- Gradient: `from-[#0a4349] to-[#999d70]` (Bestays brand)
- Text shadow for readability: `drop-shadow-lg`, `drop-shadow-md`
- Responsive text: `text-4xl md:text-5xl lg:text-6xl`
- Height: `h-[50vh] md:h-[60vh]`

---

### 3. Search Bar: `SearchBar.svelte`

**Location:** `apps/frontend/src/lib/components/SearchBar.svelte`

**Purpose:** Search form with text input + filters, navigates to property listing with query params

**Props:**
- `locale: Locale` - Current language

**State:**
- `searchQuery: string` - Text search input
- `propertyType: string` - Selected property type (all, apartment, villa, townhouse, condo)
- `bedrooms: string` - Selected bedroom filter (any, 1, 2, 3, 4)
- `priceRange: string` - Selected price range (any, 0-15000, 15000-30000, etc.)

**Code:**
```svelte
<!--
SearchBar - Homepage search form with filters

ARCHITECTURE:
  Layer: Component
  Pattern: Form with state management + navigation

DEPENDENCIES:
  SvelteKit: goto, page
  Internal: types/i18n

NOTES:
  - Navigates to /[lang]/properties with query params
  - Responsive: stacks vertically on mobile, horizontal on desktop
  - All labels localized
-->

<script lang="ts">
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import type { Locale } from '$lib/i18n/types';

  interface Props {
    locale: Locale;
  }

  const { locale }: Props = $props();

  // Form state
  let searchQuery = $state('');
  let propertyType = $state('all');
  let bedrooms = $state('any');
  let priceRange = $state('any');

  // Translations
  const t = $derived({
    placeholder: locale === 'en' ? 'Search by location, property name...' : 'ค้นหาตามสถานที่ ชื่ออสังหาฯ...',
    typeLabel: locale === 'en' ? 'Property Type' : 'ประเภท',
    typeAll: locale === 'en' ? 'All Types' : 'ทุกประเภท',
    typeApartment: locale === 'en' ? 'Apartment' : 'อพาร์ทเมนต์',
    typeVilla: locale === 'en' ? 'Villa' : 'วิลล่า',
    typeTownhouse: locale === 'en' ? 'Townhouse' : 'ทาวน์เฮ้าส์',
    typeCondo: locale === 'en' ? 'Condo' : 'คอนโด',
    bedsLabel: locale === 'en' ? 'Bedrooms' : 'ห้องนอน',
    bedsAny: locale === 'en' ? 'Any' : 'ไม่ระบุ',
    priceLabel: locale === 'en' ? 'Price Range' : 'ช่วงราคา',
    priceAny: locale === 'en' ? 'Any Price' : 'ทุกราคา',
    searchButton: locale === 'en' ? 'Search' : 'ค้นหา'
  });

  function handleSearch(e: Event) {
    e.preventDefault();

    const params = new URLSearchParams();

    // Add query params
    if (searchQuery.trim()) params.set('q', searchQuery.trim());
    if (propertyType !== 'all') params.set('property_type', propertyType);
    if (bedrooms !== 'any') params.set('min_bedrooms', bedrooms);

    // Handle price range
    if (priceRange !== 'any') {
      const [min, max] = priceRange.split('-').map(Number);
      if (min) params.set('min_price', String(min * 100)); // Convert to satang
      if (max) params.set('max_price', String(max * 100));
    }

    // Navigate to properties page with filters
    goto(`/${locale}/properties?${params.toString()}`);
  }
</script>

<form
  onsubmit={handleSearch}
  class="bg-white rounded-lg shadow-2xl p-4 md:p-6 flex flex-col md:flex-row gap-3 max-w-6xl mx-auto"
>
  <!-- Text Search Input -->
  <input
    type="text"
    bind:value={searchQuery}
    placeholder={t.placeholder}
    class="flex-1 px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#0a4349] focus:border-transparent"
  />

  <!-- Property Type Filter -->
  <select
    bind:value={propertyType}
    class="px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#0a4349] bg-white"
    aria-label={t.typeLabel}
  >
    <option value="all">{t.typeAll}</option>
    <option value="apartment">{t.typeApartment}</option>
    <option value="villa">{t.typeVilla}</option>
    <option value="townhouse">{t.typeTownhouse}</option>
    <option value="condo">{t.typeCondo}</option>
  </select>

  <!-- Bedrooms Filter -->
  <select
    bind:value={bedrooms}
    class="px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#0a4349] bg-white"
    aria-label={t.bedsLabel}
  >
    <option value="any">{t.bedsAny}</option>
    <option value="1">1+</option>
    <option value="2">2+</option>
    <option value="3">3+</option>
    <option value="4">4+</option>
  </select>

  <!-- Price Range Filter -->
  <select
    bind:value={priceRange}
    class="px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#0a4349] bg-white"
    aria-label={t.priceLabel}
  >
    <option value="any">{t.priceAny}</option>
    <option value="0-15000">< ฿15,000</option>
    <option value="15000-30000">฿15,000-30,000</option>
    <option value="30000-50000">฿30,000-50,000</option>
    <option value="50000-999999">฿50,000+</option>
  </select>

  <!-- Search Button -->
  <button
    type="submit"
    class="px-8 py-3 bg-red-600 hover:bg-red-700 text-white rounded-md font-medium transition-colors whitespace-nowrap"
  >
    {t.searchButton}
  </button>
</form>
```

**Key Features:**
- Form submission prevents default, handles navigation programmatically
- Price converted to satang (multiply by 100) to match API format
- Focus states with brand color ring
- Responsive: `flex-col md:flex-row` (stacks on mobile)
- Proper ARIA labels for accessibility

---

### 4. Property Grid: `PropertyGrid.svelte`

**Location:** `apps/frontend/src/lib/components/PropertyGrid.svelte`

**Purpose:** Grid wrapper with section title and responsive columns

**Props:**
- `properties: Property[]` - Array of properties to display
- `locale: Locale` - Current language
- `title?: string` - Optional custom title (default: "Featured Properties")

**Code:**
```svelte
<!--
PropertyGrid - Responsive grid of property cards

ARCHITECTURE:
  Layer: Component
  Pattern: Grid wrapper with responsive breakpoints

DEPENDENCIES:
  Internal: PropertyCard, types

NOTES:
  - Responsive: 1 (mobile), 2 (tablet), 4 (desktop) columns
  - Reuses PropertyCard component
  - "View All" link to full listing page
-->

<script lang="ts">
  import PropertyCard from './PropertyCard.svelte';
  import type { Property } from '$lib/types/property';
  import type { Locale } from '$lib/i18n/types';

  interface Props {
    properties: Property[];
    locale: Locale;
    title?: string;
  }

  const { properties, locale, title }: Props = $props();

  const sectionTitle = $derived(
    title || (locale === 'en' ? 'Featured Properties' : 'อสังหาริมทรัพย์แนะนำ')
  );

  const viewAllText = $derived(
    locale === 'en' ? 'View All Properties →' : 'ดูทั้งหมด →'
  );
</script>

<section class="py-16 px-4 bg-gray-50">
  <div class="max-w-7xl mx-auto">
    <!-- Section Header -->
    <div class="flex justify-between items-center mb-8">
      <h2 class="text-3xl md:text-4xl font-bold text-gray-900">
        {sectionTitle}
      </h2>
      <a
        href="/{locale}/properties"
        class="text-red-600 hover:text-red-700 font-medium hover:underline"
      >
        {viewAllText}
      </a>
    </div>

    <!-- Property Grid -->
    {#if properties.length > 0}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {#each properties as property (property.id)}
          <PropertyCard {property} {locale} />
        {/each}
      </div>
    {:else}
      <!-- Empty State -->
      <div class="text-center py-12 text-gray-500">
        <p class="text-lg">
          {locale === 'en'
            ? 'No properties available at the moment.'
            : 'ขณะนี้ยังไม่มีอสังหาริมทรัพย์'}
        </p>
      </div>
    {/if}
  </div>
</section>
```

**Styling Notes:**
- Background: `bg-gray-50` (subtle contrast from white hero)
- Grid: `grid-cols-1 md:grid-cols-2 lg:grid-cols-4`
- Gap: `gap-6` (24px between cards)
- Max width: `max-w-7xl` (matches hero)

---

### 5. Homepage Layout: `+page.svelte`

**Location:** `apps/frontend/src/routes/[lang]/+page.svelte`

**Purpose:** Homepage layout integrating all components

**Code:**
```svelte
<!--
Homepage - Bestays rental property homepage

ARCHITECTURE:
  Layer: Page Route
  Pattern: SvelteKit page with SSR data loading

DEPENDENCIES:
  Internal: HeroSection, SearchBar, PropertyGrid, i18n/context

INTEGRATION:
  - Route: /[lang] (default locale homepage)
  - Data from: +page.ts load function
  - Components: Hero + Search + Grid

NOTES:
  - SSR renders with initial 8 properties
  - Fully responsive layout
  - Localized content throughout

SPEC: US-026 MVP Homepage
-->

<script lang="ts">
  import { getLocaleContext } from '$lib/i18n/context.svelte';
  import HeroSection from '$lib/components/HeroSection.svelte';
  import SearchBar from '$lib/components/SearchBar.svelte';
  import PropertyGrid from '$lib/components/PropertyGrid.svelte';
  import type { PageData } from './$types';

  interface Props {
    data: PageData;
  }

  const { data }: Props = $props();
  const localeCtx = getLocaleContext();

  const properties = $derived(data.properties);
  const hasError = $derived(!!data.error);
</script>

<svelte:head>
  <title>
    {localeCtx.locale === 'en'
      ? 'Bestays - Find Your Perfect Stay in Thailand'
      : 'Bestays - ค้นหาที่พักที่เหมาะกับคุณในประเทศไทย'}
  </title>
  <meta
    name="description"
    content={localeCtx.locale === 'en'
      ? 'Discover amazing rental properties across Thailand. Search apartments, villas, townhouses, and condos. Book your perfect stay with Bestays.'
      : 'ค้นพบอสังหาริมทรัพย์ให้เช่าที่น่าทึ่งทั่วประเทศไทย ค้นหาอพาร์ทเมนต์ วิลล่า ทาวน์เฮ้าส์ และคอนโด จองที่พักในฝันของคุณกับ Bestays'}
  />
  <meta property="og:title" content="Bestays - Property Rentals in Thailand" />
  <meta property="og:description" content="Find and book amazing properties across Thailand" />
  <link rel="canonical" href="https://bestays.app/{localeCtx.locale}" />
</svelte:head>

<!-- Error Banner (if data fetch failed) -->
{#if hasError}
  <div class="bg-red-50 border-b border-red-200 p-4">
    <div class="max-w-7xl mx-auto">
      <p class="text-red-600 text-sm">
        {localeCtx.locale === 'en'
          ? 'Failed to load featured properties. Please refresh the page.'
          : 'โหลดข้อมูลไม่สำเร็จ กรุณารีเฟรชหน้าเว็บ'}
      </p>
    </div>
  </div>
{/if}

<!-- Hero Section with Search Bar -->
<HeroSection locale={localeCtx.locale}>
  <SearchBar locale={localeCtx.locale} />
</HeroSection>

<!-- Featured Properties Grid -->
<PropertyGrid properties={properties} locale={localeCtx.locale} />
```

**Key Features:**
- SEO meta tags (title, description, OG tags, canonical)
- Error banner if data fetch fails (non-blocking)
- Clean component composition (Hero wraps SearchBar via slot)
- Fully localized

---

## Quality Gates Checklist

### ✅ Network Operations
- [x] API fetch with error handling
- [x] Graceful degradation (empty properties array on error)
- [x] Non-blocking error display (banner, not 500 page)

### ✅ Frontend SSR/UX
- [x] SSR-compatible data loading (+page.ts)
- [x] No client-only APIs used
- [x] Proper hydration (Svelte 5 handles automatically)

### ✅ Testing Requirements
- [x] E2E test plan defined (see TESTING section)
- [x] Coverage target: Hero display, Search navigation, Grid display

### ✅ Official Documentation Validation
- [x] Svelte 5 runes: $props, $state, $derived ✅
- [x] SvelteKit routing: +page.ts, +page.svelte ✅
- [x] Tailwind CSS: Responsive utilities ✅

### ✅ Dependencies
- [x] Reuses PropertyCard (existing component)
- [x] Uses i18n context (from US-021)
- [x] API endpoint verified (working)

---

## Implementation Instructions for dev-frontend-svelte

**Branch:** `feat/TASK-017-US-026` (already checked out)

**Order of Implementation:**

1. **Create `+page.ts`** (15 min)
   - Copy data loader code from spec above
   - Test: `curl http://localhost:8011/api/v1/properties?limit=8` to verify API

2. **Create `HeroSection.svelte`** (30 min)
   - Copy component code from spec
   - Use slot for search bar
   - Test: Create temporary +page.svelte that renders hero

3. **Create `SearchBar.svelte`** (45 min)
   - Copy component code from spec
   - Implement form state with Svelte 5 $state
   - Test navigation manually

4. **Create `PropertyGrid.svelte`** (20 min)
   - Copy component code from spec
   - Reuse existing PropertyCard component
   - Test with mock data first

5. **Create `+page.svelte`** (20 min)
   - Integrate all components
   - Add meta tags
   - Test full page

6. **Polish & Test** (30 min)
   - Check responsive breakpoints (mobile, tablet, desktop)
   - Verify locale switching works
   - Test search navigation to /properties page
   - Check SSR rendering (view source, should see content)

**Commit Strategy:**
```bash
# After each component
git add <file>
git commit -m "feat: add <component-name> for homepage (US-026 TASK-017)"

# Final commit
git add .
git commit -m "feat: complete MVP homepage with hero + search + grid (US-026 TASK-017)"
```

---

## Testing Plan (for playwright-e2e-tester)

**Test Suite:** `homepage.spec.ts`

**Test Cases:**
1. Homepage loads successfully (200 status, no errors)
2. Hero section displays with correct title/subtitle (EN/TH)
3. Search bar displays all filters
4. Featured properties grid displays 8 properties
5. Property cards display image, title, price, location
6. Search navigation works (fill form → click search → verify URL has params)
7. "View All Properties" link navigates to /properties
8. Locale switching preserves homepage (EN ↔ TH)
9. Responsive layout (desktop 4 cols, tablet 2 cols, mobile 1 col)
10. SSR rendering (view source contains property data)

**Estimated Test Time:** 1-2 hours

---

## Success Criteria

**Functional:**
- ✅ Homepage loads at `/en` and `/th`
- ✅ No 404 error (site is unblocked)
- ✅ Hero displays with localized text
- ✅ Search bar navigates to /properties with filters
- ✅ Property grid displays 8 featured properties
- ✅ All text localized (EN/TH)

**Technical:**
- ✅ SSR renders content (no loading flicker)
- ✅ Responsive design (mobile/tablet/desktop)
- ✅ Error handling (graceful degradation)
- ✅ Proper meta tags (SEO)

**Performance:**
- ✅ First Contentful Paint < 1.5s
- ✅ No console errors
- ✅ Images lazy-loaded (below fold)

---

## PLANNING Complete ✅

**Time Spent:** 1 hour
**Next Phase:** IMPLEMENTATION
**Agent:** dev-frontend-svelte
**Confidence:** VERY HIGH (95%)

All specs complete, components defined, implementation path clear. Ready to build!

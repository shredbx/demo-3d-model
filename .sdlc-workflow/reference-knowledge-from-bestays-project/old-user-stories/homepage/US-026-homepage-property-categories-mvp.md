# US-026: MVP Homepage with Hero Section & Search

**Domain:** homepage
**Feature:** property-categories
**Scope:** mvp
**Status:** IN PROGRESS
**Created:** 2025-11-09
**Priority:** P0 (URGENT - Homepage is currently 404)
**Default Product:** bestays
**Portable:** true
**Ported To:** []

---

## Description

Create a minimal viable homepage at `/[lang]/+page.svelte` with hero section, search bar, and property grid. Inspired by DDProperty.com and Airbnb's clean hero design. This unblocks the site (currently 404) and provides a functional starting point for future enhancements.

**User Story:**
As a visitor, I want to land on a homepage with a beautiful hero section and search functionality, so that I can quickly search for properties or browse featured listings.

**Why MVP?**
- Homepage currently returns 404 (site is broken)
- Need functional page ASAP
- Can enhance to full US-002 (categories, locations) later

**Design References:**
1. **DDProperty.com** - Clean hero with large search bar, Buy/Rent tabs, filters
2. **Airbnb** - Hero with destination search, date pickers, guest selector
3. **Bestays Brand** - Teal/olive gradient (#0a4349 → #999d70)

---

## Acceptance Criteria

### Phase 1: Hero Section (Priority 1)
- [ ] AC-1: Hero section displays full-width with background gradient or image
- [ ] AC-2: Hero title: "Find Your Perfect Stay" (localized EN/TH)
- [ ] AC-3: Hero subtitle: "Discover amazing properties across Thailand" (localized)
- [ ] AC-4: Background uses Bestays brand colors (teal-to-olive gradient)
- [ ] AC-5: Responsive height: 60vh desktop, 50vh mobile

### Phase 2: Search Bar UI (Priority 1)
- [ ] AC-6: Search bar overlays hero (centered, prominent)
- [ ] AC-7: Search input: "Search by location, property name..."
- [ ] AC-8: Filter dropdown: Property Type (All, Apartment, Villa, Townhouse)
- [ ] AC-9: Filter dropdown: Bedrooms (Any, 1+, 2+, 3+, 4+)
- [ ] AC-10: Filter dropdown: Price Range (Any, <15k, 15k-30k, 30k-50k, 50k+)
- [ ] AC-11: Search button (red/brand color) triggers search
- [ ] AC-12: All labels localized (EN/TH)

### Phase 3: Search Functionality (Priority 1)
- [ ] AC-13: Search button navigates to `/[lang]/properties?q=...&type=...&beds=...&price=...`
- [ ] AC-14: Query params passed to existing property listing page
- [ ] AC-15: Text search filters by title + location (basic substring match)
- [ ] AC-16: Property type filter works (matches property_type field)
- [ ] AC-17: Bedroom filter works (matches physical_specs.bedrooms)
- [ ] AC-18: Price filter works (rent_price range)

### Phase 4: Property Grid Section (Priority 2)
- [ ] AC-19: Section title: "Featured Properties" (localized)
- [ ] AC-20: Grid displays 8 latest properties (reuse PropertyCard from listing page)
- [ ] AC-21: Grid layout: 4 columns (desktop), 2 columns (tablet), 1 column (mobile)
- [ ] AC-22: "View All Properties" button links to `/[lang]/properties`
- [ ] AC-23: Cards show image, title, location, price, beds/baths

### Phase 5: Responsive Design (Priority 2)
- [ ] AC-24: Desktop (≥1024px): Full hero + 4-column grid
- [ ] AC-25: Tablet (768-1023px): Medium hero + 2-column grid
- [ ] AC-26: Mobile (<768px): Compact hero + 1-column grid
- [ ] AC-27: Search bar stacks vertically on mobile
- [ ] AC-28: All touch targets ≥44px for mobile usability

### Phase 6: SEO & Performance (Priority 3)
- [ ] AC-29: Page title: "Bestays - Find Your Perfect Stay in Thailand"
- [ ] AC-30: Meta description with keywords
- [ ] AC-31: Open Graph tags for social sharing
- [ ] AC-32: SSR renders hero + initial 8 properties (no loading flicker)
- [ ] AC-33: Images lazy-loaded below fold
- [ ] AC-34: First Contentful Paint < 1.5s

---

## Technical Notes

**Route:** `/[lang]/+page.svelte` (currently missing - causing 404)

**Components to Create:**
```
apps/frontend/src/routes/[lang]/+page.svelte           # Homepage layout
apps/frontend/src/routes/[lang]/+page.ts              # Load initial properties
apps/frontend/src/lib/components/HeroSection.svelte   # Hero with bg + title
apps/frontend/src/lib/components/SearchBar.svelte     # Search input + filters
apps/frontend/src/lib/components/PropertyGrid.svelte  # Reusable grid wrapper
```

**Components to Reuse:**
- `PropertyCard.svelte` (from /properties page) - already exists ✅
- `LocaleSwitcher.svelte` (in header) - already exists ✅

**Data Loading (+page.ts):**
```typescript
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, params }) => {
  const { lang } = params;

  // Fetch 8 latest properties for featured section
  const res = await fetch(`http://localhost:8011/api/v1/properties?limit=8&locale=${lang}`);
  const data = await res.json();

  return {
    properties: data.items || [],
    locale: lang
  };
};
```

**Search Bar Logic:**
```svelte
<script lang="ts">
  import { goto } from '$app/navigation';

  let searchQuery = '';
  let propertyType = 'all';
  let bedrooms = 'any';
  let priceRange = 'any';

  function handleSearch() {
    const params = new URLSearchParams();
    if (searchQuery) params.set('q', searchQuery);
    if (propertyType !== 'all') params.set('type', propertyType);
    if (bedrooms !== 'any') params.set('beds', bedrooms);
    if (priceRange !== 'any') params.set('price', priceRange);

    goto(`/${$page.params.lang}/properties?${params.toString()}`);
  }
</script>
```

**Hero Background Options:**
1. **Gradient** (easiest): `bg-gradient-to-br from-[#0a4349] to-[#999d70]`
2. **Image** (better): Unsplash Thailand property image with overlay
3. **Hybrid** (best): Image + gradient overlay for brand consistency

**Filters (Basic → Enhanced):**

MVP (Basic):
- Text search: substring match on title + location
- Property type: apartment | villa | townhouse | condo
- Bedrooms: 1+ | 2+ | 3+ | 4+
- Price: <15k | 15k-30k | 30k-50k | 50k+

Future Enhancements (US-024, US-025):
- Semantic search (natural language)
- Date range picker (booking system)
- Guest count selector
- Amenity filters (pool, gym, parking)
- Location autocomplete with map

**API Endpoint Updates:**
Existing `/api/v1/properties` already supports query params:
- `?q=search` - Search in title/description
- `?property_type=apartment` - Filter by type
- `?min_bedrooms=2` - Minimum bedrooms
- `?min_price=15000&max_price=30000` - Price range

**Styling (Tailwind):**
- Hero gradient: `bg-gradient-to-br from-[#0a4349] to-[#999d70]`
- Search bar bg: `bg-white shadow-2xl rounded-lg`
- Brand red button: `bg-red-600 hover:bg-red-700`
- Section padding: `py-16 px-4`

**Estimated Effort:** 1 day (8 hours)
- Research: 30 min
- Planning: 1 hour
- Implementation: 4 hours
- Testing: 2 hours
- Polish: 30 min

---

## Related Stories

- US-023: Property Display (provides data + components to reuse) - COMPLETED ✅
- US-021: Thai Localization (provides i18n infrastructure) - COMPLETED ✅
- US-024: Semantic Search (future enhancement for search bar) - READY
- US-025: Booking System (future enhancement for date pickers) - READY
- US-002: Full Homepage with Categories (this is MVP, US-002 is complete version)

---

## Tasks

[Automatically populated by system - do not edit manually]

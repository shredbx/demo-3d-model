# TASK-015: Property Listing Page Frontend

**Story:** US-023 (Property Import & Display with Localization)
**Type:** feat
**Status:** PLANNING
**Branch:** feat/TASK-015-US-023

---

## Objective

Build the property listing page at `/[lang]/properties` with a responsive grid of property cards that displays all imported rental properties with full locale support (EN/TH).

---

## Context

**What Exists:**
- ✅ Property V2 Backend API (TASK-013)
  - `GET /api/v1/properties` - List properties with pagination
  - `GET /api/v1/properties/{id}` - Get single property
  - `GET /api/v1/amenities` - List all amenities
  - `GET /api/v1/policies` - List all policies
- ✅ 5 Sample Properties in Database (TASK-014)
- ✅ i18n Infrastructure (US-021 TASK-010)
  - Locale routing: `/[lang]/` pattern
  - i18n context: `lib/i18n/context.svelte.ts`
  - LocaleSwitcher component working
- ✅ Tailwind CSS 4 configured
- ✅ SvelteKit 5 with runes

**What's Missing:**
- ❌ Property listing page
- ❌ PropertyCard component
- ❌ Property data fetching logic
- ❌ Grid layout implementation

---

## Requirements

### 1. Page Structure

**Route:** `apps/frontend/src/routes/[lang]/properties/+page.svelte`

**Layout:**
```
┌─────────────────────────────────┐
│ Header (with LocaleSwitcher)    │
├─────────────────────────────────┤
│ Hero Section (optional)         │
├─────────────────────────────────┤
│ Property Grid                   │
│ ┌────┐ ┌────┐ ┌────┐           │
│ │Card│ │Card│ │Card│           │
│ └────┘ └────┘ └────┘           │
│ ┌────┐ ┌────┐ ┌────┐           │
│ │Card│ │Card│ │Card│           │
│ └────┘ └────┘ └────┘           │
└─────────────────────────────────┘
```

**Responsive Grid:**
- Desktop (≥1024px): 3 columns
- Tablet (640px-1023px): 2 columns
- Mobile (<640px): 1 column

### 2. PropertyCard Component

**Location:** `apps/frontend/src/lib/components/PropertyCard.svelte`

**Display Fields:**
- Cover image (clickable, links to detail page)
- Title (localized)
- Price (formatted with currency)
- Bedrooms count
- Bathrooms count
- Location (province + district)
- Property type badge (villa/condo/apartment/house)

**Example:**
```
┌────────────────────┐
│                    │
│   [Cover Image]    │
│                    │
├────────────────────┤
│ Modern Villa       │
│ ฿45,000/month      │
├────────────────────┤
│ 🛏️ 2 🚿 2          │
│ 📍 Koh Phangan     │
│ [Villa]            │
└────────────────────┘
```

### 3. Data Fetching

**Load Function:** `apps/frontend/src/routes/[lang]/properties/+page.ts`

```typescript
export async function load({ params, fetch }) {
  const locale = params.lang; // 'en' or 'th'

  const response = await fetch(`/api/v1/properties?locale=${locale}&limit=20`);
  const properties = await response.json();

  return {
    properties,
    locale
  };
}
```

**API Response Shape:**
```typescript
interface PropertyResponse {
  properties: Property[];
  total: number;
  page: number;
  limit: number;
}

interface Property {
  id: string;
  title: string; // Already localized by backend
  rent_price: number; // In satang
  currency: string; // "THB"
  property_type: string;
  cover_image: string | null;
  physical_specs: {
    bedrooms?: number;
    bathrooms?: number;
    // ... other fields
  };
  location_details: {
    province?: string;
    district?: string;
    // ... other fields
  };
}
```

### 4. Localization Integration

**Use existing i18n context:**
```svelte
<script>
  import { getI18nContext } from '$lib/i18n/context.svelte';

  const i18n = getI18nContext();
  const currentLocale = $derived(i18n.locale);
</script>
```

**Locale-aware rendering:**
- Page title: "Properties" (EN) / "อสังหาริมทรัพย์" (TH)
- Price formatting: ฿45,000 (both locales)
- Property type labels: "Villa" / "วิลล่า"

### 5. Error Handling & Loading States

**Loading State:**
```svelte
{#if loading}
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {#each Array(6) as _}
      <PropertyCardSkeleton />
    {/each}
  </div>
{/if}
```

**Error State:**
```svelte
{#if error}
  <div class="text-center py-12">
    <p class="text-red-600">Failed to load properties</p>
    <button onclick={retry}>Retry</button>
  </div>
{/if}
```

**Empty State:**
```svelte
{#if properties.length === 0}
  <div class="text-center py-12">
    <p class="text-gray-600">No properties available</p>
  </div>
{/if}
```

---

## Success Criteria

✅ Property listing page displays at `/[lang]/properties`
✅ All 5 imported properties render in grid
✅ Grid responsive: 3 cols (desktop), 2 (tablet), 1 (mobile)
✅ Property cards show: image, title, price, beds, baths, location
✅ Clicking card navigates to `/[lang]/properties/[id]` (future TASK)
✅ Locale switcher changes displayed language
✅ Loading state displays while fetching
✅ Error state displays on API failure
✅ No SSR hydration errors
✅ Type-safe with TypeScript

---

## Implementation Notes

**Component Structure:**
```
apps/frontend/src/
├── routes/
│   └── [lang]/
│       └── properties/
│           ├── +page.svelte (listing page)
│           └── +page.ts (data loader)
└── lib/
    └── components/
        ├── PropertyCard.svelte (card component)
        └── PropertyCardSkeleton.svelte (loading skeleton)
```

**Styling Approach:**
- Use Tailwind CSS 4
- Follow existing brand colors from homepage
- Mobile-first responsive design
- Use aspect-ratio for images

**Performance:**
- Images lazy-loaded (Svelte default)
- No virtualization needed (only 5 properties)
- Future: Add pagination when > 20 properties

**Testing:**
- Manual testing in Chrome, Firefox, Safari
- Mobile testing (responsive design)
- Locale switching test
- Future: E2E tests in TASK-015-testing

---

## Dependencies

**API Endpoints:**
- `GET /api/v1/properties?locale={locale}&limit={limit}` ✅ Ready

**Frontend Infrastructure:**
- i18n context (`lib/i18n/context.svelte.ts`) ✅ Ready
- Locale routing (`/[lang]/`) ✅ Ready
- Tailwind CSS 4 ✅ Ready

**External:**
- Property V2 backend (TASK-013) ✅ Complete
- Sample data (TASK-014) ✅ Complete

---

## Time Estimate

**Total:** 2-3 hours

- Component creation: 1 hour
- Data fetching: 30 minutes
- Styling: 1 hour
- Testing: 30 minutes

---

## Next Steps

1. Launch dev-frontend-svelte agent with this spec
2. Agent implements page + component
3. Manual testing (EN/TH, responsive)
4. Commit to feat/TASK-015-US-023
5. Move to TASK-016 (Property Detail Page)

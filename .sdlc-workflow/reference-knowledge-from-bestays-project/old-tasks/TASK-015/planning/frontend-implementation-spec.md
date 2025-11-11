# Frontend Implementation Specification: Property Listing Page

**TASK:** TASK-015
**Story:** US-023
**Agent:** dev-frontend-svelte
**Date:** 2025-11-09

---

## 1. Component Architecture

### 1.1 Page Component

**File:** `apps/frontend/src/routes/[lang]/properties/+page.svelte`

**Responsibilities:**
- Render property grid
- Handle loading/error states
- Integrate with i18n context
- Responsive layout

**Structure:**
```svelte
<script lang="ts">
  import { getI18nContext } from '$lib/i18n/context.svelte';
  import PropertyCard from '$lib/components/PropertyCard.svelte';
  import PropertyCardSkeleton from '$lib/components/PropertyCardSkeleton.svelte';

  const { data } = $props();
  const i18n = getI18nContext();

  const properties = $derived(data.properties);
</script>

<div class="container mx-auto px-4 py-8">
  <h1 class="text-3xl font-bold mb-8">
    {i18n.locale === 'en' ? 'Properties' : 'อสังหาริมทรัพย์'}
  </h1>

  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {#each properties as property}
      <PropertyCard {property} locale={i18n.locale} />
    {/each}
  </div>
</div>
```

### 1.2 Load Function

**File:** `apps/frontend/src/routes/[lang]/properties/+page.ts`

**Responsibilities:**
- Fetch properties from API
- Handle locale parameter
- Type-safe response

**Implementation:**
```typescript
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch }) => {
  const locale = params.lang;

  try {
    const response = await fetch(
      `http://localhost:8011/api/v1/properties?locale=${locale}&limit=20`
    );

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();

    return {
      properties: data.properties || data, // Handle both response formats
      locale
    };
  } catch (error) {
    console.error('Failed to fetch properties:', error);
    return {
      properties: [],
      locale,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
};
```

### 1.3 PropertyCard Component

**File:** `apps/frontend/src/lib/components/PropertyCard.svelte`

**Props:**
```typescript
interface Props {
  property: Property;
  locale: 'en' | 'th';
}
```

**Responsibilities:**
- Display property summary
- Navigate to detail page on click
- Format price with currency
- Show property type badge
- Responsive image

**Structure:**
```svelte
<script lang="ts">
  import type { Property } from '$lib/types/property';

  const { property, locale }: Props = $props();

  const formattedPrice = $derived(() => {
    const price = property.rent_price / 100; // Convert satang to THB
    return new Intl.NumberFormat('th-TH', {
      style: 'currency',
      currency: property.currency || 'THB'
    }).format(price);
  });

  const bedrooms = $derived(property.physical_specs?.bedrooms || 0);
  const bathrooms = $derived(property.physical_specs?.bathrooms || 0);
  const province = $derived(property.location_details?.province || '');
  const district = $derived(property.location_details?.district || '');
  const location = $derived(`${district}, ${province}`.replace(/^,\s*/, ''));
</script>

<a
  href="/{locale}/properties/{property.id}"
  class="group block bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden"
>
  <!-- Cover Image -->
  <div class="aspect-[16/9] bg-gray-200 overflow-hidden">
    {#if property.cover_image}
      <img
        src={property.cover_image}
        alt={property.title}
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
      />
    {:else}
      <div class="w-full h-full flex items-center justify-center text-gray-400">
        No Image
      </div>
    {/if}
  </div>

  <!-- Property Info -->
  <div class="p-4">
    <!-- Title -->
    <h3 class="text-lg font-semibold text-gray-900 line-clamp-2 mb-2">
      {property.title}
    </h3>

    <!-- Price -->
    <p class="text-2xl font-bold text-blue-600 mb-3">
      {formattedPrice()}/
      {locale === 'en' ? 'month' : 'เดือน'}
    </p>

    <!-- Specs -->
    <div class="flex items-center gap-4 text-gray-600 mb-2">
      {#if bedrooms > 0}
        <span class="flex items-center gap-1">
          <span>🛏️</span>
          <span>{bedrooms}</span>
        </span>
      {/if}
      {#if bathrooms > 0}
        <span class="flex items-center gap-1">
          <span>🚿</span>
          <span>{bathrooms}</span>
        </span>
      {/if}
    </div>

    <!-- Location -->
    {#if location}
      <p class="text-sm text-gray-500 mb-2">
        📍 {location}
      </p>
    {/if}

    <!-- Property Type Badge -->
    <span class="inline-block px-3 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
      {property.property_type}
    </span>
  </div>
</a>
```

### 1.4 PropertyCardSkeleton Component

**File:** `apps/frontend/src/lib/components/PropertyCardSkeleton.svelte`

**Purpose:** Loading placeholder

**Structure:**
```svelte
<div class="bg-white rounded-lg shadow-md overflow-hidden animate-pulse">
  <!-- Image skeleton -->
  <div class="aspect-[16/9] bg-gray-200"></div>

  <!-- Content skeleton -->
  <div class="p-4">
    <div class="h-6 bg-gray-200 rounded mb-2"></div>
    <div class="h-8 bg-gray-200 rounded w-1/2 mb-3"></div>
    <div class="flex gap-4 mb-2">
      <div class="h-5 bg-gray-200 rounded w-12"></div>
      <div class="h-5 bg-gray-200 rounded w-12"></div>
    </div>
    <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
    <div class="h-6 bg-gray-200 rounded w-20"></div>
  </div>
</div>
```

---

## 2. TypeScript Types

**File:** `apps/frontend/src/lib/types/property.ts`

```typescript
export interface Property {
  id: string;
  title: string;
  description: string;
  transaction_type: 'rent' | 'sale';
  property_type: 'villa' | 'condo' | 'apartment' | 'house' | 'townhouse';
  rent_price: number; // In satang
  sale_price: number | null;
  currency: string;
  cover_image: string | null;
  images: string[] | null;

  // JSONB Fields
  physical_specs: {
    bedrooms?: number;
    bathrooms?: number;
    area_sqm?: number;
    furnishing?: string;
    floors?: number;
  } | null;

  location_details: {
    province?: string;
    district?: string;
    sub_district?: string;
    address?: string;
    latitude?: number;
    longitude?: number;
  } | null;

  amenities: number[] | null; // Array of amenity IDs
  policies: {
    pets_allowed?: boolean;
    smoking_allowed?: boolean;
    lease_term_months?: number;
  } | null;

  contact_info: {
    phone?: string;
    line_id?: string;
    email?: string;
  } | null;

  is_published: boolean;
  is_featured: boolean;
  created_at: string;
  updated_at: string;
}

export interface PropertyListResponse {
  properties: Property[];
  total: number;
  page: number;
  limit: number;
}
```

---

## 3. SSR Considerations

### 3.1 SSR-Safe Patterns

**✅ Use SvelteKit load function** (runs on server)
```typescript
export const load: PageLoad = async ({ fetch }) => {
  // Fetch runs on server during SSR
  const response = await fetch(API_URL);
  return await response.json();
};
```

**✅ Use $derived for reactive values**
```svelte
const formattedPrice = $derived(/* ... */);
```

**❌ Avoid browser-only APIs in component body**
```svelte
// BAD - window is undefined on server
const width = window.innerWidth;

// GOOD - Use $effect for browser-only code
$effect(() => {
  if (typeof window !== 'undefined') {
    // Browser-only code
  }
});
```

### 3.2 Image Handling

**Use Svelte's default lazy loading:**
```svelte
<img
  src={property.cover_image}
  alt={property.title}
  loading="lazy"
/>
```

---

## 4. Responsive Design

### 4.1 Grid Breakpoints

```css
/* Mobile: 1 column */
grid-cols-1

/* Tablet (md: 768px): 2 columns */
md:grid-cols-2

/* Desktop (lg: 1024px): 3 columns */
lg:grid-cols-3
```

### 4.2 Container

```html
<div class="container mx-auto px-4 py-8">
  <!-- Max-width container, auto margin, padding -->
</div>
```

### 4.3 Gap Spacing

```html
<div class="gap-6">
  <!-- 1.5rem (24px) gap between cards -->
</div>
```

---

## 5. Error Handling

### 5.1 API Errors

```svelte
{#if data.error}
  <div class="container mx-auto px-4 py-12 text-center">
    <div class="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md mx-auto">
      <p class="text-red-600 font-semibold mb-2">
        {i18n.locale === 'en' ? 'Failed to load properties' : 'โหลดข้อมูลไม่สำเร็จ'}
      </p>
      <p class="text-red-500 text-sm">
        {data.error}
      </p>
    </div>
  </div>
{/if}
```

### 5.2 Empty State

```svelte
{#if properties.length === 0 && !data.error}
  <div class="container mx-auto px-4 py-12 text-center">
    <p class="text-gray-600 text-lg">
      {i18n.locale === 'en' ? 'No properties available' : 'ไม่มีอสังหาริมทรัพย์'}
    </p>
  </div>
{/if}
```

---

## 6. Quality Gates

### 6.1 Network Resilience

**✅ Error handling in load function**
```typescript
try {
  const response = await fetch(API_URL);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return await response.json();
} catch (error) {
  return { properties: [], error: error.message };
}
```

**✅ Display error state to user**

### 6.2 SSR/UX

**✅ No hydration mismatches**
- Use load function for data fetching (server + client)
- Avoid browser-only APIs in component body

**✅ Loading states**
- Show skeleton cards while loading

### 6.3 Official Documentation

**✅ Use Svelte 5 runes:**
- `$props()` for component props
- `$derived()` for computed values
- `$effect()` for side effects (if needed)

**✅ Use SvelteKit patterns:**
- `+page.svelte` for page component
- `+page.ts` for load function
- Type-safe with `$types`

---

## 7. Testing Checklist

### Manual Testing

- [ ] Page loads at `/en/properties` with 5 properties
- [ ] Page loads at `/th/properties` with Thai content
- [ ] Grid responsive on mobile/tablet/desktop
- [ ] Images load correctly (Supabase URLs)
- [ ] Clicking card navigates to detail page (404 expected for now)
- [ ] Price formatted correctly (฿45,000/month)
- [ ] Bedrooms/bathrooms display correctly
- [ ] Location displays correctly
- [ ] Property type badge displays
- [ ] No console errors
- [ ] No hydration warnings

### Browser Testing

- [ ] Chrome (desktop + mobile)
- [ ] Firefox
- [ ] Safari

---

## 8. Implementation Steps (Agent Instructions)

1. **Create TypeScript types:**
   - Create `apps/frontend/src/lib/types/property.ts`
   - Define `Property` and `PropertyListResponse` interfaces

2. **Create PropertyCard component:**
   - Create `apps/frontend/src/lib/components/PropertyCard.svelte`
   - Implement with Svelte 5 runes
   - Use Tailwind CSS for styling
   - Handle hover effects
   - Make clickable (link to detail page)

3. **Create PropertyCardSkeleton component:**
   - Create `apps/frontend/src/lib/components/PropertyCardSkeleton.svelte`
   - Match PropertyCard layout
   - Use animate-pulse for loading effect

4. **Create load function:**
   - Create `apps/frontend/src/routes/[lang]/properties/+page.ts`
   - Fetch from Property V2 API
   - Handle errors gracefully
   - Return type-safe data

5. **Create page component:**
   - Create `apps/frontend/src/routes/[lang]/properties/+page.svelte`
   - Import PropertyCard and i18n context
   - Render responsive grid
   - Handle error/empty states

6. **Test manually:**
   - Start dev server: `make dev`
   - Navigate to `/en/properties`
   - Test responsive design (resize browser)
   - Switch locale and verify content updates
   - Check all 5 properties display

7. **Verify SSR:**
   - Check no hydration warnings in console
   - Verify page works with JavaScript disabled (content renders)

---

## 9. File Checklist

**New Files to Create:**
- ✅ `apps/frontend/src/lib/types/property.ts`
- ✅ `apps/frontend/src/lib/components/PropertyCard.svelte`
- ✅ `apps/frontend/src/lib/components/PropertyCardSkeleton.svelte`
- ✅ `apps/frontend/src/routes/[lang]/properties/+page.svelte`
- ✅ `apps/frontend/src/routes/[lang]/properties/+page.ts`

**Files to Reference (Don't Modify):**
- `apps/frontend/src/lib/i18n/context.svelte.ts` (i18n context)
- `apps/frontend/src/routes/[lang]/+layout.svelte` (existing layout)

---

## 10. Acceptance Criteria

- [ ] Property listing page renders at `/[lang]/properties`
- [ ] All 5 properties display in grid
- [ ] Grid responsive (3/2/1 columns)
- [ ] Property cards show all required fields
- [ ] Locale switching works (EN/TH)
- [ ] Clicking card navigates (even if 404)
- [ ] No SSR hydration errors
- [ ] No TypeScript errors
- [ ] No console warnings
- [ ] Loading state displays (skeleton)
- [ ] Error state displays on API failure

---

**Ready for Implementation! 🚀**

Launch dev-frontend-svelte agent with this spec.

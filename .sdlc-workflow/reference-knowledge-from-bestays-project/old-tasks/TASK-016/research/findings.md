# TASK-016 Research Findings: Property Detail Page

**Research Date:** 2025-11-09  
**Story:** US-023 Property V2 Implementation  
**Task:** TASK-016 Property Detail Page Frontend  
**Researcher:** Claude Code (Coordinator)

---

## Executive Summary

This research analyzed existing codebase patterns for implementing a property detail page at `/[lang]/properties/[id]`. The investigation covered 7 areas: image galleries, detail page patterns, SEO/meta tags, component reusability, locale/i18n, error states, and existing property implementation.

**Key Finding:** The codebase has solid foundations from TASK-015 (property listing), excellent SSR/data loading patterns, and comprehensive i18n infrastructure. However, we need to implement an image gallery component (no existing solution) and add structured data for SEO.

**Recommendation:** Build on TASK-015 patterns, create custom image gallery with bits-ui dialog, implement schema.org structured data, and extract reusable components from PropertyCard.

---

## 1. Image Gallery Patterns

### Findings

**No existing image gallery/lightbox implementation found in codebase.**

#### Searched For
- Keywords: `lightbox`, `gallery`, `carousel`, `slider`, `swiper`, `embla`, `photoswipe`, `fancybox`
- Locations: All Svelte components, package.json
- Result: No matches

#### Available Dialog/Modal Components
**Location:** `/apps/frontend/src/lib/components/ui/dialog/`

```typescript
// dialog.svelte - bits-ui based dialog (Svelte 5 runes)
<DialogPrimitive.Root bind:open {onOpenChange} {...restProps}>
  {@render children?.()}
</DialogPrimitive.Root>

// dialog-content.svelte - Modal with overlay, backdrop blur, close button
<DialogPrimitive.Portal>
  <DialogPrimitive.Overlay class="..." /> <!-- Backdrop -->
  <DialogPrimitive.Content class="...">
    {@render children?.()}
    <DialogPrimitive.Close> <!-- X button -->
  </DialogPrimitive.Content>
</DialogPrimitive.Portal>
```

**Characteristics:**
- Based on `bits-ui` library (already in dependencies)
- Svelte 5 runes compatible ($bindable, $props)
- Portal-based rendering (overlay outside DOM hierarchy)
- Backdrop blur effect
- Keyboard/click to close
- Accessible (focus trap, ARIA)

#### Touch Gesture Handling
**No existing touch gesture implementations found.**
- No `touchstart`, `touchmove`, `touchend` handlers in codebase
- No gesture libraries (hammer.js, etc.) in package.json
- Touch handling will need to be implemented for mobile swipe gestures

### Gaps

1. **No image gallery component** - Need to build from scratch
2. **No lightbox/fullscreen image viewer** - Can use dialog as base
3. **No touch swipe gestures** - Need native event handlers or library
4. **No image lazy loading beyond `loading="lazy"`** - Current approach sufficient
5. **No image optimization** - Using raw Supabase URLs (acceptable for MVP)

### Recommendations

**Option 1: Custom Gallery with bits-ui Dialog (Recommended)**
- Build custom `ImageGallery.svelte` component using existing dialog primitives
- Implement left/right navigation with keyboard arrows + click
- Add touch swipe support with native `touchstart`/`touchmove` events
- Use existing Property.images array from TASK-015
- Pros: No new dependencies, full control, lightweight, Svelte 5 native
- Cons: More implementation work (~100-150 lines)

**Option 2: Add External Library**
- Options: `svelte-carousel`, `embla-carousel`, `swiper`
- Pros: Feature-rich, tested, mobile-optimized
- Cons: External dependency, bundle size, may not be Svelte 5 compatible

**Decision:** Go with Option 1 (custom implementation) for control and consistency.

---

## 2. Detail Page Implementation Patterns

### Findings

#### Example: FAQ Detail Page
**Location:** `/apps/frontend/src/routes/dashboard/faqs/[id]/+page.svelte`

**Pattern: SSR Data Loading with Error Handling**

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  
  let isLoadingFAQ = $state(false);
  let faq = $state<FAQDetail | null>(null);
  let loadError = $state<string | null>(null);
  const faqId = $state($page.params.id);
  
  onMount(async () => {
    await loadFAQ();
  });
  
  async function loadFAQ() {
    try {
      faq = await faqsApi.getById(faqId);
    } catch (error: any) {
      if (error.status === 404) {
        loadError = 'FAQ not found';
      }
    }
  }
</script>

{#if isLoadingFAQ}
  <div>Loading FAQ...</div>
{:else if loadError}
  <div>Error: {loadError}</div>
{:else if faq}
  <!-- Render content -->
{/if}
```

**Key Patterns:**
1. Extract `id` from `$page.params.id`
2. Load data in `onMount` (client-side)
3. Use `$state` runes for reactive state
4. Handle 404 errors specifically
5. Conditional rendering based on loading/error/success states

#### Property Listing Load Function
**Location:** `/apps/frontend/src/routes/[lang]/properties/+page.ts`

```typescript
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
    const properties = Array.isArray(data) ? data : data.properties || [];
    
    return { properties, locale };
  } catch (error) {
    return { properties: [], locale, error: error.message };
  }
};
```

**Key Patterns:**
1. SSR-compatible (runs on server and client)
2. Extract params from `{ params, fetch }`
3. Use SvelteKit's `fetch` (works in SSR)
4. Graceful error handling (return error in data)
5. Type-safe with `PageLoad` type

### Recommendations

**For Property Detail Page:**

Use **+page.ts load function** (SSR) instead of `onMount` (client-only):

```typescript
// +page.ts
export const load: PageLoad = async ({ params, fetch }) => {
  const { id, lang } = params;
  
  try {
    const response = await fetch(
      `http://localhost:8011/api/v1/properties/${id}`
    );
    
    if (!response.ok) {
      if (response.status === 404) {
        throw error(404, 'Property not found');
      }
      throw new Error('Failed to load property');
    }
    
    const property = await response.json();
    return { property, locale: lang };
  } catch (err) {
    throw error(500, 'Internal server error');
  }
};
```

**Advantages of +page.ts:**
- SSR-friendly (faster initial render, better SEO)
- SvelteKit's `error()` helper for proper 404 handling
- Data available immediately (no loading spinner)
- Better user experience

---

## 3. SEO & Meta Tags

### Findings

#### Basic Meta Tags
**Location:** `/apps/frontend/src/routes/[lang]/properties/+page.svelte`

```svelte
<svelte:head>
  <title>
    {localeCtx.locale === 'en' ? 'Properties' : 'อสังหาริมทรัพย์'} | BeStays
  </title>
  <meta
    name="description"
    content={localeCtx.locale === 'en'
      ? 'Browse available rental properties in Thailand'
      : 'เรียกดูอสังหาริมทรัพย์ให้เช่าในประเทศไทย'}
  />
</svelte:head>
```

**Pattern:**
- `svelte:head` for meta tags
- Locale-aware title and description
- Static meta tags (not dynamic per property)

#### Structured Data (Schema.org)
**No structured data found in codebase.**
- Searched for: `schema.org`, `application/ld+json`, `@type`, `@context`
- Result: Only false positives (package-lock.json, svelte.config.js)
- **Gap:** No JSON-LD structured data for SEO

### Gaps

1. **No dynamic meta tags** - Need property-specific title, description, og:image
2. **No Open Graph tags** - Missing `og:title`, `og:description`, `og:image`, `og:url`
3. **No Twitter Card tags** - Missing `twitter:card`, `twitter:title`, `twitter:image`
4. **No structured data** - Missing schema.org `Product` or `Accommodation` JSON-LD
5. **No canonical URL** - Should include for locale variants

### Recommendations

**Implement dynamic meta tags in +page.svelte:**

```svelte
<svelte:head>
  <title>{property.title} | BeStays</title>
  <meta name="description" content={property.description.slice(0, 160)} />
  
  <!-- Open Graph -->
  <meta property="og:type" content="product" />
  <meta property="og:title" content={property.title} />
  <meta property="og:description" content={property.description} />
  <meta property="og:image" content={property.cover_image?.url} />
  <meta property="og:url" content={`https://bestays.app/${locale}/properties/${property.id}`} />
  
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content={property.title} />
  <meta name="twitter:description" content={property.description} />
  <meta name="twitter:image" content={property.cover_image?.url} />
  
  <!-- Canonical -->
  <link rel="canonical" href={`https://bestays.app/${locale}/properties/${property.id}`} />
  
  <!-- Structured Data -->
  {@html `
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Accommodation",
      "name": "${property.title}",
      "description": "${property.description}",
      "image": "${property.cover_image?.url}",
      "address": {
        "@type": "PostalAddress",
        "addressLocality": "${property.location_details?.administrative?.district_name}",
        "addressRegion": "${property.location_details?.administrative?.province_name}"
      },
      "offers": {
        "@type": "Offer",
        "price": "${property.rent_price / 100}",
        "priceCurrency": "${property.currency}"
      }
    }
    </script>
  `}
</svelte:head>
```

**Priority:** High - Critical for SEO and social sharing

---

## 4. Component Reusability

### Findings

#### PropertyCard Component Analysis
**Location:** `/apps/frontend/src/lib/components/PropertyCard.svelte`

**Current Structure:**
```svelte
<a href="/{locale}/properties/{property.id}" class="...">
  <!-- Image -->
  <div class="aspect-[16/9]">
    <img src={property.cover_image.url} loading="lazy" />
  </div>
  
  <!-- Content -->
  <div class="p-4">
    <h3>{property.title}</h3>
    <p>{formattedPrice()}/month</p>
    <div>{bedrooms} 🛏️ {bathrooms} 🚿</div>
    <p>{location()}</p>
    <span>{propertyTypeLabel()}</span>
  </div>
</a>
```

**Reusable Logic:**
- `formattedPrice()` - Formats satang → THB with Intl.NumberFormat
- `propertyTypeLabel()` - Translates property type (villa → Villa/วิลล่า)
- `location()` - Formats district, province
- Bedroom/bathroom extraction from JSONB

#### Extractable Components

**1. PropertyImage Component**
```svelte
<!-- Reusable image with aspect ratio, loading, fallback -->
<script lang="ts">
  interface Props {
    src: string | null;
    alt: string;
    aspectRatio?: string; // "16/9" | "4/3" | "1/1"
    loading?: "lazy" | "eager";
  }
</script>
```

**2. PropertyPrice Component**
```svelte
<!-- Price formatting with locale support -->
<script lang="ts">
  interface Props {
    price: number; // In satang
    currency: string;
    locale: Locale;
    period?: "month" | "year" | null;
  }
</script>
```

**3. PropertySpecs Component**
```svelte
<!-- Bedroom/bathroom/parking display -->
<script lang="ts">
  interface Props {
    bedrooms?: number;
    bathrooms?: number;
    parkingSpaces?: number;
  }
</script>
```

**4. PropertyLocation Component**
```svelte
<!-- Location string formatter -->
<script lang="ts">
  interface Props {
    district?: string;
    province?: string;
    locale: Locale;
  }
</script>
```

### Recommendations

**For Detail Page:**
1. **Extract price formatting utility** (`lib/utils/price.ts`) - Reuse in card + detail
2. **Extract property type translation** (`lib/utils/property.ts`) - Reuse in card + detail
3. **Consider extracting image component** - Reusable across pages
4. **Keep specs/location inline** - Not complex enough to extract

**Priority:** Medium - Extract during implementation for DRY code

---

## 5. Locale & i18n Patterns

### Findings

**i18n Infrastructure Fully Implemented (TASK-015)**

#### Locale Context
**Location:** `/apps/frontend/src/lib/i18n/context.svelte.ts`

```typescript
class LocaleContext {
  locale = $state<Locale>('en');
  
  constructor(initialLocale: Locale) {
    this.locale = initialLocale;
  }
  
  setLocale(newLocale: Locale) {
    this.locale = newLocale;
  }
}

export function setLocaleContext(initialLocale: Locale): LocaleContext;
export function getLocaleContext(): LocaleContext;
```

**Pattern:** Svelte 5 runes-based context with `$state`

#### Layout Implementation
**Location:** `/apps/frontend/src/routes/[lang]/+layout.svelte`

```svelte
<script lang="ts">
  import { setLocaleContext } from '$lib/i18n/context.svelte';
  
  let { data, children }: Props = $props();
  const localeCtx = setLocaleContext(data.locale);
</script>

<header>
  <LocaleSwitcher currentLocale={data.locale} />
</header>

<main>
  {@render children()}
</main>
```

**Pattern:** Context provider in layout, consumed in all child routes

#### Usage in Components
```svelte
<script lang="ts">
  import { getLocaleContext } from '$lib/i18n/context.svelte';
  const localeCtx = getLocaleContext();
</script>

{#if localeCtx.locale === 'en'}
  Properties
{:else}
  อสังหาริมทรัพย์
{/if}
```

### Recommendations

**For Property Detail Page:**
1. **Use `getLocaleContext()`** - Already available in all `/[lang]/*` routes
2. **Translate UI strings** - Buttons, labels, sections (bed/bath labels, contact, etc.)
3. **Format currency with locale** - `Intl.NumberFormat('th-TH', ...)`
4. **Format dates with locale** - `Intl.DateTimeFormat` for created_at
5. **Handle property description** - Display based on locale (if multilingual in future)

**No additional work needed** - Infrastructure ready to use

---

## 6. Error States & Loading

### Findings

#### Loading Skeleton
**Location:** `/apps/frontend/src/lib/components/PropertyCardSkeleton.svelte`

```svelte
<div class="bg-white rounded-lg shadow-md overflow-hidden animate-pulse">
  <div class="aspect-[16/9] bg-gray-200"></div> <!-- Image -->
  <div class="p-4">
    <div class="h-6 bg-gray-200 rounded mb-2"></div> <!-- Title -->
    <div class="h-8 bg-gray-200 rounded w-1/2 mb-3"></div> <!-- Price -->
    <div class="flex gap-4 mb-2">
      <div class="h-5 bg-gray-200 rounded w-12"></div> <!-- Specs -->
    </div>
  </div>
</div>
```

**Pattern:** Tailwind `animate-pulse`, matches component layout exactly

#### Error State (Listing Page)
**Location:** `/apps/frontend/src/routes/[lang]/properties/+page.svelte`

```svelte
{#if hasError}
  <div class="bg-red-50 border border-red-200 rounded-lg p-6">
    <p class="text-red-600 font-semibold">
      {localeCtx.locale === 'en' ? 'Failed to load properties' : 'โหลดข้อมูลไม่สำเร็จ'}
    </p>
    <p class="text-red-500 text-sm">{data.error}</p>
  </div>
{/if}
```

**Pattern:** Red banner with error message, locale-aware

#### 404 Error Handling (FAQ Page)
**Location:** `/apps/frontend/src/routes/dashboard/faqs/[id]/+page.svelte`

```svelte
{:else if loadError}
  <div class="bg-white rounded-lg shadow p-8 text-center">
    <div class="text-red-600 text-xl mb-4">⚠️</div>
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Error Loading FAQ</h2>
    <p class="text-gray-600 mb-6">{loadError}</p>
    <button onclick={goBackToList}>Back to FAQ List</button>
    <button onclick={loadFAQ}>Retry</button>
  </div>
{/if}
```

**Pattern:** Centered error card with icon, message, actions (back/retry)

#### SvelteKit Error Pages
**No custom +error.svelte pages found in `/routes`**
- SvelteKit provides default error page
- Can customize with `src/routes/+error.svelte`

### Recommendations

**For Property Detail Page:**

1. **Loading State (SSR - minimal)**
   - With +page.ts SSR, loading state rarely visible
   - Add simple "Loading property..." text for client-side navigation
   
2. **404 Not Found**
   - Use SvelteKit's `throw error(404, 'Property not found')` in +page.ts
   - Create custom error page with:
     - "Property not found" message (locale-aware)
     - Back to properties button
     - Search box (optional)
   
3. **Network Error**
   - Display error banner similar to listing page
   - Include retry mechanism
   - Log error to console
   
4. **Skeleton (Optional)**
   - For client-side navigation, show PropertyDetailSkeleton
   - Match detail page layout (hero image, title, specs grid)

**Priority:** High for 404, Medium for others

---

## 7. Existing Property Implementation

### Findings

#### Property Type Definition
**Location:** `/apps/frontend/src/lib/types/property.ts`

**Complete JSONB Structure:**

```typescript
export interface Property {
  // Core fields
  id: string;
  title: string;
  description: string;
  transaction_type: 'rent' | 'sale';
  property_type: 'villa' | 'condo' | 'apartment' | 'house' | 'townhouse';
  rent_price: number; // In satang
  currency: string;
  
  // Images
  cover_image: {
    url: string;
    alt?: string;
    width?: number;
    height?: number;
  } | null;
  images: Array<{
    url: string;
    alt?: string;
    width?: number;
    height?: number;
  }> | null;
  
  tags: string[] | null;
  
  // JSONB: Physical specs
  physical_specs: {
    rooms?: {
      bedrooms?: number;
      bathrooms?: number;
      parking_spaces?: number;
    };
    sizes?: {
      land_area_sqm?: number;
      usable_area_sqm?: number;
    };
    condition?: string; // "new", "excellent", "good", "fair"
    furnishing?: string; // "fully_furnished", "semi_furnished", "unfurnished"
  } | null;
  
  // JSONB: Location
  location_details: {
    administrative?: {
      province_id?: string;
      province_name?: string;
      district_id?: string;
      district_name?: string;
      postal_code?: string;
    };
    coordinates?: {
      latitude?: number;
      longitude?: number;
    };
  } | null;
  
  // JSONB: Amenities
  amenities: {
    interior?: string[]; // ["air_conditioning", "wifi", "kitchen"]
    exterior?: string[]; // ["pool", "gym", "parking"]
  } | null;
  
  // JSONB: Policies
  policies: {
    house_rules?: {
      pets_allowed?: boolean;
      smoking_allowed?: boolean;
    };
    lease_terms?: {
      minimum_lease_months?: number;
    };
  } | null;
  
  // Contact
  contact_info: {
    phone?: string;
    line_id?: string;
    email?: string;
  } | null;
  
  // Metadata
  is_published: boolean;
  is_featured: boolean;
  listing_priority: number;
  created_at: string;
  updated_at: string;
}
```

**Richness:**
- ✅ Multiple images (gallery-ready)
- ✅ Comprehensive location data (map-ready)
- ✅ Amenities (interior/exterior)
- ✅ Policies (house rules, lease terms)
- ✅ Contact info (phone, Line, email)
- ✅ Flexible JSONB structure

#### API Endpoint
**Expected:** `GET /api/v1/properties/{id}`
- Similar to `/api/v1/admin/faqs/{id}` pattern
- Returns single Property object
- 404 if not found
- Supports locale parameter

#### PropertyCard Component
**Location:** `/apps/frontend/src/lib/components/PropertyCard.svelte`

**Used Fields:**
- `property.id` - Link target
- `property.cover_image.url` - Cover image
- `property.title` - Title
- `property.rent_price` - Price
- `property.currency` - Currency
- `property.physical_specs.rooms.bedrooms` - Bedroom count
- `property.physical_specs.rooms.bathrooms` - Bathroom count
- `property.location_details.administrative.province_name` - Province
- `property.location_details.administrative.district_name` - District
- `property.property_type` - Type badge

**Unused Fields (Detail Page Opportunities):**
- `description` - Full description text
- `images` - **Image gallery**
- `physical_specs.sizes.*` - Land/usable area
- `physical_specs.condition` - Condition badge
- `physical_specs.furnishing` - Furnishing badge
- `amenities.*` - **Amenity list with icons**
- `policies.*` - **House rules section**
- `contact_info.*` - **Contact section with buttons**
- `location_details.coordinates.*` - **Map integration**
- `tags` - Tag badges
- `created_at` - Listed date

### Recommendations

**Detail Page Content Structure:**

```
┌─────────────────────────────────────────────┐
│  Hero Section                                │
│  - Cover image (clickable → gallery)        │
│  - Back button, Share button                │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Header Section                              │
│  - Title (h1)                                │
│  - Location (province, district)             │
│  - Price (large, prominent)                  │
│  - Property type badge                       │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Quick Info Grid                             │
│  - Bedrooms 🛏️                              │
│  - Bathrooms 🚿                              │
│  - Parking 🚗                                │
│  - Land area 📏                              │
│  - Usable area 📐                            │
│  - Furnishing 🪑                             │
│  - Condition ⭐                              │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Description                                 │
│  - Full property description                 │
│  - Tags (if available)                       │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Image Gallery                               │
│  - Thumbnail grid (all images)               │
│  - Click to open lightbox                    │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Amenities                                   │
│  - Interior (2-column grid with icons)       │
│  - Exterior (2-column grid with icons)       │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Location & Map (Future)                     │
│  - Address                                   │
│  - Map (coordinates)                         │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Policies & Rules                            │
│  - Pets allowed/not allowed                  │
│  - Smoking allowed/not allowed               │
│  - Minimum lease (months)                    │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Contact Section                             │
│  - Phone (click to call)                     │
│  - Line (click to open Line)                 │
│  - Email (click to email)                    │
│  - "Contact Owner" button                    │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Footer Info                                 │
│  - Listed date (created_at)                  │
│  - Last updated (updated_at)                 │
│  - Property ID                               │
└─────────────────────────────────────────────┘
```

**Priority:** Use all available JSONB fields - rich data available

---

## Integration Points

### 1. API Integration

**Backend Endpoint (Expected):**
```
GET /api/v1/properties/{id}?locale={locale}
```

**Response:** Single `Property` object (matches type definition)

**Error Handling:**
- 404: Property not found
- 500: Internal server error

**Implementation:**
```typescript
// lib/api/properties.ts (NEW)
export const propertiesApi = {
  getById: (id: string, locale: Locale) =>
    apiClient.get<Property>(`/api/v1/properties/${id}?locale=${locale}`)
};
```

### 2. Routing

**Route:** `/[lang]/properties/[id]/+page.svelte`  
**Load Function:** `/[lang]/properties/[id]/+page.ts`

**Parameters:**
- `lang` - Locale from route (en/th)
- `id` - Property UUID

### 3. Component Hierarchy

```
[lang]/properties/[id]/+page.svelte (Detail page)
├── PropertyDetailHero.svelte (Hero image + back button)
├── PropertyDetailHeader.svelte (Title, location, price)
├── PropertyDetailSpecs.svelte (Grid of specs)
├── PropertyDetailDescription.svelte (Description + tags)
├── PropertyImageGallery.svelte (Thumbnail grid + lightbox)
├── PropertyAmenities.svelte (Interior/exterior amenities)
├── PropertyPolicies.svelte (House rules, lease terms)
├── PropertyContact.svelte (Contact buttons)
└── PropertyDetailFooter.svelte (Metadata)
```

### 4. Locale Context

**Already Available:**
```svelte
import { getLocaleContext } from '$lib/i18n/context.svelte';
const localeCtx = getLocaleContext();
```

**Usage:** All child components can access current locale

---

## Dependencies & Constraints

### Dependencies

**Existing (No Installation Required):**
1. `bits-ui` - Dialog/modal primitives ✅
2. `lucide-svelte` - Icons ✅
3. Tailwind CSS - Styling ✅
4. SvelteKit - Routing, SSR ✅
5. i18n context - Locale management ✅

**Optional (Consider Adding):**
1. Image gallery library (OR build custom - Recommended: custom)
2. Map library for location (Leaflet, Mapbox) - Future enhancement

### Constraints

1. **Svelte 5 Compatibility**
   - Must use runes ($state, $props, $derived)
   - No Svelte 4 stores
   - Snippets instead of slots

2. **SSR Requirements**
   - +page.ts must be SSR-safe
   - No browser-only APIs in load function
   - Use SvelteKit's `fetch`

3. **Performance**
   - Image lazy loading
   - Optimize large image gallery (thumbnails)
   - Consider pagination for amenities (if many)

4. **Mobile Responsiveness**
   - Touch gestures for image gallery
   - Responsive grid layouts
   - Mobile-first design

5. **SEO**
   - Dynamic meta tags (Open Graph, Twitter Card)
   - Structured data (schema.org)
   - Canonical URLs

---

## Recommendations Summary

### High Priority

1. **Build Custom Image Gallery** (No external library)
   - Use bits-ui dialog as base
   - Add left/right navigation (arrows, keyboard)
   - Touch swipe support (native events)
   - Thumbnail grid + fullscreen view

2. **Implement SSR Data Loading** (+page.ts)
   - Use PageLoad pattern from listing page
   - Proper 404 handling with SvelteKit error()
   - Type-safe with Property type

3. **Add Dynamic SEO Meta Tags**
   - Property-specific title, description
   - Open Graph tags (og:image critical)
   - Twitter Card tags
   - Schema.org JSON-LD (Accommodation type)

4. **Extract Reusable Utilities**
   - Price formatting (satang → THB)
   - Property type translation
   - Location formatter

### Medium Priority

1. **Create PropertyDetailSkeleton** (Loading state)
2. **Extract Shared Components** (Image, Price, Specs)
3. **Add Error Boundary** (Custom +error.svelte)
4. **Implement Amenity Icons** (Map strings to Lucide icons)

### Future Enhancements

1. **Map Integration** (Leaflet/Mapbox for coordinates)
2. **Share Functionality** (Share button → Web Share API)
3. **Print Styles** (Print-friendly property details)
4. **Favorite/Save** (User can save properties)
5. **Related Properties** (Show similar listings)

---

## Next Steps

1. **PLANNING Phase**
   - Design component structure
   - Define API contract (confirm with backend)
   - Create implementation spec
   - Design image gallery component
   - Plan SEO strategy (meta tags + structured data)

2. **IMPLEMENTATION Phase**
   - Create +page.ts (SSR load function)
   - Create +page.svelte (detail page layout)
   - Build ImageGallery component
   - Extract utility functions
   - Add dynamic meta tags
   - Create error page

3. **TESTING Phase**
   - E2E tests (view property, image gallery)
   - Mobile responsiveness
   - SEO validation (meta tags, structured data)
   - Error scenarios (404, network error)

4. **VALIDATION Phase**
   - Accessibility audit
   - Performance check (Lighthouse)
   - Cross-browser testing
   - Mobile touch gesture testing

---

## Appendix: File References

### Analyzed Files

**Property Implementation (TASK-015):**
- `/apps/frontend/src/routes/[lang]/properties/+page.svelte` (L1-104)
- `/apps/frontend/src/routes/[lang]/properties/+page.ts` (L1-69)
- `/apps/frontend/src/lib/components/PropertyCard.svelte` (L1-141)
- `/apps/frontend/src/lib/components/PropertyCardSkeleton.svelte` (L1-54)
- `/apps/frontend/src/lib/types/property.ts` (L1-112)

**i18n Infrastructure:**
- `/apps/frontend/src/lib/i18n/context.svelte.ts` (L1-75)
- `/apps/frontend/src/routes/[lang]/+layout.svelte` (L1-63)

**API Patterns:**
- `/apps/frontend/src/lib/api/client.ts` (L1-185)
- `/apps/frontend/src/lib/api/faqs.ts` (L1-230)

**UI Components:**
- `/apps/frontend/src/lib/components/ui/dialog/dialog.svelte` (L1-22)
- `/apps/frontend/src/lib/components/ui/dialog/dialog-content.svelte` (L1-40)
- `/apps/frontend/src/lib/components/admin/FAQToolConfigModal.svelte` (L1-100+)

**Detail Page Example:**
- `/apps/frontend/src/routes/dashboard/faqs/[id]/+page.svelte` (L1-208)

### Key Patterns

1. **SSR Data Loading:** `PageLoad` type with `{ params, fetch }`
2. **Svelte 5 Runes:** `$state`, `$props`, `$derived`, `$bindable`
3. **Context API:** `setContext`/`getContext` with class-based state
4. **Error Handling:** Graceful fallback, 404 detection, locale-aware messages
5. **Component Structure:** Header comments with architecture info
6. **Type Safety:** Explicit TypeScript types, no generic `<T>` guessing

---

**End of Research Findings**

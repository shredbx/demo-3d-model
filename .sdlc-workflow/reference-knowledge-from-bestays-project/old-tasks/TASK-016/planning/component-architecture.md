# Component Architecture - TASK-016 Property Detail Page

**Task:** TASK-016 Property Detail Page Frontend  
**Story:** US-023 Property Import & Display with Localization  
**Date:** 2025-11-09

---

## Overview

This document defines the complete component architecture for the property detail page, including file structure, component hierarchy, data flow, and reusable utilities.

**Design Pattern:** Server-Side Rendering (SSR) with Progressive Enhancement  
**Architecture Layer:** Presentation Layer (Frontend)

---

## File Structure

```
apps/frontend/src/
├── routes/
│   └── [lang]/
│       └── properties/
│           ├── [id]/
│           │   ├── +page.svelte          # Main detail page component
│           │   ├── +page.ts              # SSR data loading
│           │   └── +error.svelte         # Custom 404/error page
│           ├── +page.svelte              # Listing page (existing)
│           └── +page.ts                  # Listing load (existing)
│
├── lib/
│   ├── components/
│   │   ├── PropertyCard.svelte           # ✅ Existing (reuse)
│   │   ├── PropertyCardSkeleton.svelte   # ✅ Existing (reuse)
│   │   ├── PropertyImageGallery.svelte   # 🆕 NEW - Image lightbox
│   │   ├── PropertyAmenities.svelte      # 🆕 NEW - Amenity display
│   │   ├── PropertyPolicies.svelte       # 🆕 NEW - Policies display
│   │   ├── PropertyContact.svelte        # 🆕 NEW - Contact section
│   │   └── PropertyDetailSkeleton.svelte # 🆕 NEW - Loading skeleton
│   │
│   ├── utils/
│   │   ├── format-price.ts               # 🆕 NEW - Price formatting
│   │   ├── property-type.ts              # 🆕 NEW - Type translation
│   │   └── seo.ts                        # 🆕 NEW - SEO utilities
│   │
│   ├── api/
│   │   ├── client.ts                     # ✅ Existing (reuse)
│   │   └── properties.ts                 # ✅ Existing (extend)
│   │
│   ├── i18n/
│   │   └── context.svelte.ts             # ✅ Existing (reuse)
│   │
│   └── types/
│       └── property.ts                   # ✅ Existing (complete)
│
└── tests/
    └── e2e/
        ├── test_property_detail_display.spec.ts      # 🆕 NEW
        ├── test_property_detail_navigation.spec.ts   # 🆕 NEW
        ├── test_property_detail_locale.spec.ts       # 🆕 NEW
        ├── test_property_detail_error_states.spec.ts # 🆕 NEW
        └── test_property_detail_image_gallery.spec.ts # 🆕 NEW
```

**Summary:**
- **7 new components** (page, error, gallery, amenities, policies, contact, skeleton)
- **3 new utility modules** (price, property type, SEO)
- **5 new E2E test files**
- **Reuses:** PropertyCard, i18n context, API client, Property types

---

## Component Hierarchy

```
[id]/+page.svelte (Main Detail Page)
├── <svelte:head>                        # SEO meta tags
│   └── Dynamic title, description, OG tags, schema.org
│
├── PropertyDetailSkeleton               # Loading state (SSR fallback)
│   └── Skeleton for hero, title, specs
│
└── Main Content (when loaded)
    ├── Hero Section
    │   ├── Back Button (<a> link)
    │   ├── Cover Image (clickable → gallery)
    │   └── Share Button (future)
    │
    ├── Header Section
    │   ├── Property Title (h1)
    │   ├── Location (district, province)
    │   ├── Price (formatted)
    │   └── Property Type Badge
    │
    ├── Quick Info Grid
    │   ├── Bedrooms (icon + count)
    │   ├── Bathrooms (icon + count)
    │   ├── Parking Spaces (icon + count)
    │   ├── Land Area (if available)
    │   ├── Usable Area (if available)
    │   ├── Furnishing Status
    │   └── Condition Badge
    │
    ├── Description Section
    │   ├── Full Description Text
    │   └── Tags (if available)
    │
    ├── PropertyImageGallery              # 🆕 NEW Component
    │   ├── Thumbnail Grid
    │   │   └── Click → opens lightbox
    │   └── Lightbox Modal (when open)
    │       ├── bits-ui Dialog
    │       ├── Full-size Image
    │       ├── Left/Right Navigation
    │       ├── Image Counter (1/10)
    │       ├── Close Button
    │       └── Keyboard Support (Arrow keys, Escape)
    │
    ├── PropertyAmenities                 # 🆕 NEW Component
    │   ├── Interior Amenities
    │   │   └── 2-column grid with icons
    │   └── Exterior Amenities
    │       └── 2-column grid with icons
    │
    ├── Location Section (Future: Phase 2)
    │   ├── Address
    │   └── Map (coordinates)
    │
    ├── PropertyPolicies                  # 🆕 NEW Component
    │   ├── House Rules
    │   │   ├── Pets Allowed/Not
    │   │   └── Smoking Allowed/Not
    │   └── Lease Terms
    │       └── Minimum Lease Duration
    │
    ├── PropertyContact                   # 🆕 NEW Component
    │   ├── Phone (click to call)
    │   ├── Line ID (click to open Line)
    │   ├── Email (click to email)
    │   └── "Contact Owner" Button
    │
    └── Footer Section
        ├── Listed Date
        ├── Last Updated
        └── Property ID
```

---

## Component Specifications

### 1. `[id]/+page.svelte` (Main Page)

**Purpose:** Display comprehensive property details with all sections

**Props:**
```typescript
interface PageProps {
  data: {
    property: Property;
    locale: Locale;
  };
}
```

**State:**
```typescript
let galleryOpen = $state(false);
let selectedImageIndex = $state(0);
```

**Dependencies:**
- `getLocaleContext()` from `$lib/i18n/context.svelte`
- `page` from `$app/state`
- `PropertyImageGallery`, `PropertyAmenities`, `PropertyPolicies`, `PropertyContact` components
- `formatPrice()`, `propertyTypeLabel()` utilities

**Responsibilities:**
- Render all property information
- Handle gallery state (shallow routing)
- Apply SEO meta tags
- Coordinate child components
- ~400-500 lines

---

### 2. `[id]/+page.ts` (Load Function)

**Purpose:** Server-side data loading for property details

**Type:**
```typescript
export const load: PageLoad = async ({ params, fetch }) => {
  // Returns: { property: Property, locale: Locale }
};
```

**Logic:**
```typescript
1. Extract params.id and params.lang
2. Fetch property from API: GET /api/v1/properties/{id}
3. Handle errors:
   - 404 → throw error(404, 'Property not found')
   - 500 → throw error(500, 'Failed to load property')
4. Return { property, locale }
```

**Dependencies:**
- `error` from `@sveltejs/kit`
- `PageLoad` type from `./$types`

**Responsibilities:**
- SSR data loading
- Error handling
- Type-safe parameter extraction
- ~30-40 lines

---

### 3. `[id]/+error.svelte` (Error Page)

**Purpose:** Custom 404 and error handling for property detail

**State:**
```typescript
import { page } from '$app/state';
// Access: page.status, page.error.message
```

**Layout:**
```svelte
<div class="error-container">
  {#if page.status === 404}
    <!-- Property not found -->
    <h1>Property Not Found</h1>
    <p>The property you're looking for doesn't exist or has been removed.</p>
    <a href="/{locale}/properties">← Back to Properties</a>
  {:else}
    <!-- Generic error -->
    <h1>Error {page.status}</h1>
    <p>{page.error.message}</p>
    <button onclick={retry}>Retry</button>
  {/if}
</div>
```

**Dependencies:**
- `page` from `$app/state`
- `getLocaleContext()` for navigation

**Responsibilities:**
- Display user-friendly error messages
- Provide navigation back to listing
- Retry functionality
- ~60-80 lines

---

### 4. `PropertyImageGallery.svelte` 🆕 NEW

**Purpose:** Display property images with thumbnail grid and lightbox modal

**Props:**
```typescript
interface Props {
  images: Array<{
    url: string;
    alt?: string;
    width?: number;
    height?: number;
  }>;
  coverImage?: {
    url: string;
    alt?: string;
  };
}
```

**State:**
```typescript
let open = $state(false);
let currentIndex = $state(0);
let currentImage = $derived(images[currentIndex]);
```

**Layout:**
```svelte
<!-- Thumbnail Grid -->
<div class="grid grid-cols-3 gap-2">
  {#each images as image, i}
    <button onclick={() => openGallery(i)}>
      <img src={image.url} alt={image.alt} loading="lazy" />
    </button>
  {/each}
</div>

<!-- Lightbox Modal (bits-ui Dialog) -->
{#if open}
  <Dialog.Root bind:open>
    <Dialog.Portal>
      <Dialog.Overlay class="fixed inset-0 bg-black/90" />
      <Dialog.Content class="fixed inset-0 flex items-center justify-center">
        <button onclick={previousImage}>←</button>
        <img src={currentImage.url} alt={currentImage.alt} />
        <button onclick={nextImage}>→</button>
        <Dialog.Close>×</Dialog.Close>
      </Dialog.Content>
    </Dialog.Portal>
  </Dialog.Root>
{/if}
```

**Features:**
- Thumbnail grid (responsive: 2 cols mobile, 3 cols tablet, 4 cols desktop)
- Click thumbnail → open lightbox at that image
- Keyboard navigation (Arrow Left/Right, Escape)
- Touch swipe support (mobile)
- Image counter (e.g., "3 / 10")
- Smooth transitions

**Dependencies:**
- `Dialog` from `bits-ui`
- Touch event handlers for mobile swipe

**Responsibilities:**
- Image display and navigation
- Keyboard and touch interactions
- Accessible (ARIA labels, focus trap)
- ~120-150 lines

---

### 5. `PropertyAmenities.svelte` 🆕 NEW

**Purpose:** Display property amenities with icons

**Props:**
```typescript
interface Props {
  amenities: {
    interior?: string[];   // ["air_conditioning", "wifi", "kitchen"]
    exterior?: string[];   // ["pool", "gym", "parking"]
  } | null;
  locale: Locale;
}
```

**State:**
```typescript
// No local state (pure presentation)
```

**Layout:**
```svelte
{#if amenities}
  <section>
    <h2>Amenities</h2>
    
    {#if amenities.interior?.length}
      <h3>Interior</h3>
      <div class="grid grid-cols-2 gap-4">
        {#each amenities.interior as amenity}
          <div class="flex items-center gap-2">
            <Icon name={getAmenityIcon(amenity)} />
            <span>{translateAmenity(amenity, locale)}</span>
          </div>
        {/each}
      </div>
    {/if}
    
    {#if amenities.exterior?.length}
      <h3>Exterior</h3>
      <div class="grid grid-cols-2 gap-4">
        {#each amenities.exterior as amenity}
          <div class="flex items-center gap-2">
            <Icon name={getAmenityIcon(amenity)} />
            <span>{translateAmenity(amenity, locale)}</span>
          </div>
        {/each}
      </div>
    {/if}
  </section>
{/if}
```

**Amenity Icon Mapping:**
```typescript
const amenityIcons: Record<string, string> = {
  air_conditioning: 'wind',
  wifi: 'wifi',
  kitchen: 'utensils',
  pool: 'waves',
  gym: 'dumbbell',
  parking: 'car',
  // ... etc
};
```

**Dependencies:**
- `lucide-svelte` icons
- Translation utility for amenity labels

**Responsibilities:**
- Map amenity strings to icons
- Translate amenity labels
- Responsive 2-column grid
- ~80-100 lines

---

### 6. `PropertyPolicies.svelte` 🆕 NEW

**Purpose:** Display property policies (house rules, lease terms)

**Props:**
```typescript
interface Props {
  policies: {
    house_rules?: {
      pets_allowed?: boolean;
      smoking_allowed?: boolean;
    };
    lease_terms?: {
      minimum_lease_months?: number;
    };
  } | null;
  locale: Locale;
}
```

**Layout:**
```svelte
{#if policies}
  <section>
    <h2>Policies & Rules</h2>
    
    {#if policies.house_rules}
      <h3>House Rules</h3>
      <ul>
        <li>
          {#if policies.house_rules.pets_allowed}
            ✅ Pets allowed
          {:else}
            ❌ No pets
          {/if}
        </li>
        <li>
          {#if policies.house_rules.smoking_allowed}
            ✅ Smoking allowed
          {:else}
            ❌ No smoking
          {/if}
        </li>
      </ul>
    {/if}
    
    {#if policies.lease_terms?.minimum_lease_months}
      <h3>Lease Terms</h3>
      <p>Minimum lease: {policies.lease_terms.minimum_lease_months} months</p>
    {/if}
  </section>
{/if}
```

**Dependencies:**
- None (pure presentation)

**Responsibilities:**
- Display policies clearly
- Locale-aware labels
- ~50-60 lines

---

### 7. `PropertyContact.svelte` 🆕 NEW

**Purpose:** Display contact information with interactive buttons

**Props:**
```typescript
interface Props {
  contactInfo: {
    phone?: string;
    line_id?: string;
    email?: string;
  } | null;
  locale: Locale;
}
```

**Layout:**
```svelte
{#if contactInfo}
  <section>
    <h2>Contact</h2>
    
    {#if contactInfo.phone}
      <a href="tel:{contactInfo.phone}" class="contact-button">
        <Icon name="phone" />
        {contactInfo.phone}
      </a>
    {/if}
    
    {#if contactInfo.line_id}
      <a href="https://line.me/ti/p/{contactInfo.line_id}" class="contact-button">
        <Icon name="message-circle" />
        Line: {contactInfo.line_id}
      </a>
    {/if}
    
    {#if contactInfo.email}
      <a href="mailto:{contactInfo.email}" class="contact-button">
        <Icon name="mail" />
        {contactInfo.email}
      </a>
    {/if}
    
    <button class="primary-button">Contact Owner</button>
  </section>
{/if}
```

**Dependencies:**
- `lucide-svelte` icons

**Responsibilities:**
- Clickable phone/email/Line buttons
- Format contact info
- ~40-50 lines

---

### 8. `PropertyDetailSkeleton.svelte` 🆕 NEW

**Purpose:** Loading skeleton matching detail page layout

**Props:**
```typescript
// No props (static skeleton)
```

**Layout:**
```svelte
<div class="animate-pulse">
  <!-- Hero skeleton -->
  <div class="aspect-video bg-gray-200"></div>
  
  <!-- Title skeleton -->
  <div class="h-8 bg-gray-200 w-3/4 my-4"></div>
  
  <!-- Price skeleton -->
  <div class="h-10 bg-gray-200 w-1/2 mb-4"></div>
  
  <!-- Specs grid skeleton -->
  <div class="grid grid-cols-2 gap-4">
    <div class="h-6 bg-gray-200"></div>
    <div class="h-6 bg-gray-200"></div>
  </div>
  
  <!-- Description skeleton -->
  <div class="space-y-2 my-4">
    <div class="h-4 bg-gray-200"></div>
    <div class="h-4 bg-gray-200"></div>
    <div class="h-4 bg-gray-200 w-2/3"></div>
  </div>
</div>
```

**Dependencies:**
- Tailwind CSS (animate-pulse)

**Responsibilities:**
- Match actual layout exactly
- Pulse animation
- ~40-50 lines

---

## Utility Modules

### 1. `lib/utils/format-price.ts` 🆕 NEW

**Purpose:** Format prices from satang to THB with locale support

```typescript
/**
 * Format price from satang to THB
 * @param satang - Price in satang (1 THB = 100 satang)
 * @param currency - Currency code (default: "THB")
 * @param locale - Locale for formatting (default: "en")
 * @returns Formatted price string
 */
export function formatPrice(
  satang: number,
  currency: string = "THB",
  locale: Locale = "en"
): string {
  const thb = satang / 100;
  
  return new Intl.NumberFormat(locale === "th" ? "th-TH" : "en-US", {
    style: "currency",
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(thb);
}

// Example usage:
// formatPrice(1500000, "THB", "en") → "฿15,000"
// formatPrice(1500000, "THB", "th") → "฿15,000"
```

**Tests:**
```typescript
expect(formatPrice(1500000, "THB", "en")).toBe("฿15,000");
expect(formatPrice(0, "THB", "en")).toBe("฿0");
expect(formatPrice(100, "THB", "en")).toBe("฿1");
```

---

### 2. `lib/utils/property-type.ts` 🆕 NEW

**Purpose:** Translate property type to localized label

```typescript
type PropertyType = 'villa' | 'condo' | 'apartment' | 'house' | 'townhouse';

const propertyTypeLabels: Record<PropertyType, Record<Locale, string>> = {
  villa: { en: "Villa", th: "วิลล่า" },
  condo: { en: "Condo", th: "คอนโด" },
  apartment: { en: "Apartment", th: "อพาร์ทเมนท์" },
  house: { en: "House", th: "บ้าน" },
  townhouse: { en: "Townhouse", th: "ทาวน์เฮาส์" },
};

/**
 * Get localized property type label
 * @param type - Property type
 * @param locale - Locale (en/th)
 * @returns Localized label
 */
export function propertyTypeLabel(type: PropertyType, locale: Locale): string {
  return propertyTypeLabels[type]?.[locale] ?? type;
}

// Example usage:
// propertyTypeLabel("villa", "en") → "Villa"
// propertyTypeLabel("villa", "th") → "วิลล่า"
```

---

### 3. `lib/utils/seo.ts` 🆕 NEW

**Purpose:** Generate SEO meta tags and structured data

```typescript
import type { Property, Locale } from '$lib/types/property';

/**
 * Generate schema.org structured data for property
 */
export function generatePropertySchema(property: Property): string {
  const schema = {
    "@context": "https://schema.org",
    "@type": "Accommodation",
    "name": property.title,
    "description": property.description,
    "image": property.cover_image?.url,
    "address": {
      "@type": "PostalAddress",
      "addressLocality": property.location_details?.administrative?.district_name,
      "addressRegion": property.location_details?.administrative?.province_name,
      "postalCode": property.location_details?.administrative?.postal_code,
    },
    "offers": {
      "@type": "Offer",
      "price": property.rent_price / 100,
      "priceCurrency": property.currency,
    },
  };
  
  return JSON.stringify(schema, null, 2);
}

/**
 * Generate meta description from property description
 */
export function generateMetaDescription(description: string): string {
  return description.slice(0, 160);
}
```

---

## Data Flow

### SSR Flow (Initial Page Load)

```
1. User navigates to /en/properties/123

2. Server executes +page.ts load function
   ├── Extract params: id="123", lang="en"
   ├── Fetch: GET /api/v1/properties/123
   ├── Handle errors (404, 500)
   └── Return: { property, locale: "en" }

3. Server renders +page.svelte with data
   ├── Generate <svelte:head> meta tags
   ├── Render property details
   └── Return HTML to browser

4. Browser receives HTML
   ├── Display content immediately (SSR)
   └── Hydrate interactive features

5. Client-side JavaScript runs
   ├── onMount: Setup gallery event listeners
   └── Ready for interactions
```

### Client-Side Navigation Flow

```
1. User clicks property card on listing page
   ├── Navigate to /en/properties/456

2. SvelteKit executes +page.ts load function (client-side)
   ├── Show loading skeleton (optional)
   ├── Fetch: GET /api/v1/properties/456
   └── Return: { property, locale: "en" }

3. SvelteKit updates +page.svelte with new data
   ├── Update meta tags
   ├── Replace content
   └── No page reload (SPA navigation)

4. Component state preserved
   ├── Scroll position reset
   └── Gallery state reset
```

### Gallery Interaction Flow (Shallow Routing)

```
1. User clicks image thumbnail

2. Component calls openGallery(imageIndex)
   ├── pushState('', { galleryOpen: true, imageIndex })
   └── Creates history entry (back button support)

3. page.state updates
   ├── page.state.galleryOpen = true
   ├── page.state.imageIndex = 2

4. Conditional render triggers
   {#if page.state.galleryOpen}
     <PropertyImageGallery />
   {/if}

5. Gallery modal opens
   ├── bits-ui Dialog renders
   ├── Display image at index 2
   └── Focus trap activated

6. User presses back button or Escape
   ├── history.back() or close()
   ├── page.state.galleryOpen = false
   └── Modal closes
```

---

## Component Reusability

### Extracted from PropertyCard

**Reusable patterns from TASK-015:**

```typescript
// Price formatting (now in lib/utils/format-price.ts)
formatPrice(property.rent_price, property.currency, locale)

// Property type translation (now in lib/utils/property-type.ts)
propertyTypeLabel(property.property_type, locale)

// Location formatting (inline, not complex enough to extract)
{property.location_details?.administrative?.district_name},
{property.location_details?.administrative?.province_name}
```

### Shared Components

**Components used by both listing and detail:**

1. **PropertyCard** - Used on listing page
2. **i18n context** - Used everywhere
3. **API client** - Used for all API calls
4. **Property types** - Used throughout

---

## Responsive Design

### Breakpoints

```typescript
Mobile:    < 640px  (sm)
Tablet:    640px+   (md)
Desktop:   1024px+  (lg)
Wide:      1280px+  (xl)
```

### Layout Adaptations

**Mobile (< 640px):**
```
- Single column layout
- Hero image: full width
- Gallery: 2 columns
- Specs: 1 column
- Amenities: 1 column
```

**Tablet (640px - 1024px):**
```
- Two column layout (content + sidebar)
- Gallery: 3 columns
- Specs: 2 columns
- Amenities: 2 columns
```

**Desktop (1024px+):**
```
- Two column layout (wide content + narrow sidebar)
- Gallery: 4 columns
- Specs: 3 columns
- Amenities: 2 columns
```

---

## Integration Points

### API Integration

```typescript
// Endpoint
GET /api/v1/properties/{id}

// Request
fetch(`/api/v1/properties/123`, {
  headers: { 'Accept-Language': 'en' }
})

// Response
{
  id: "123",
  title: "Luxury Villa in Phuket",
  description: "...",
  rent_price: 150000000, // satang
  currency: "THB",
  cover_image: { url: "...", alt: "..." },
  images: [...],
  // ... all Property fields
}
```

### Locale Integration

```svelte
<script>
  import { getLocaleContext } from '$lib/i18n/context.svelte';
  
  const localeCtx = getLocaleContext();
  // localeCtx.locale → "en" | "th"
</script>

<!-- Use throughout component -->
<h1>{localeCtx.locale === 'en' ? 'Properties' : 'อสังหาริมทรัพย์'}</h1>
```

### Navigation Integration

```svelte
<!-- Back to listing -->
<a href="/{locale}/properties">
  ← Back to Properties
</a>

<!-- Breadcrumbs -->
<nav>
  <a href="/{locale}">Home</a> /
  <a href="/{locale}/properties">Properties</a> /
  <span>{property.title}</span>
</nav>
```

---

## Performance Considerations

### Image Optimization

```svelte
<!-- Lazy loading for images below fold -->
<img src={image.url} alt={image.alt} loading="lazy" />

<!-- Eager loading for cover image (LCP) -->
<img src={coverImage.url} alt={coverImage.alt} loading="eager" fetchpriority="high" />

<!-- Width/height to prevent layout shift -->
<img 
  src={image.url} 
  width={image.width} 
  height={image.height}
  alt={image.alt} 
/>
```

### Code Splitting

```typescript
// PropertyImageGallery only loaded when needed
{#if page.state.galleryOpen}
  <PropertyImageGallery />
{/if}

// Future: Dynamic import for large components
const PropertyImageGallery = await import('./PropertyImageGallery.svelte');
```

### SSR Benefits

- Instant content display (no loading spinner)
- SEO-friendly (crawlers see full content)
- Better Core Web Vitals (FCP, LCP)

---

## Accessibility

### ARIA Labels

```svelte
<!-- Gallery navigation -->
<button aria-label="Previous image" onclick={previousImage}>
  ←
</button>

<!-- Close button -->
<button aria-label="Close gallery" onclick={close}>
  ×
</button>

<!-- Image counter -->
<span aria-live="polite">
  Image {currentIndex + 1} of {images.length}
</span>
```

### Keyboard Navigation

```typescript
Escape → Close gallery
Arrow Left → Previous image
Arrow Right → Next image
Tab → Navigate interactive elements
Enter → Activate buttons
```

### Focus Management

```typescript
onMount(() => {
  // Trap focus in modal
  const firstFocusable = modal.querySelector('button');
  firstFocusable?.focus();
});
```

---

## File Headers (Memory Print)

**Example header for PropertyImageGallery.svelte:**

```svelte
<!--
Design Pattern: Modal with Shallow Routing
Architecture: Presentation Layer - Image Gallery Component
Dependencies: 
  - bits-ui (Dialog primitives)
  - lucide-svelte (icons)
  - SvelteKit shallow routing (pushState)
Trade-offs:
  - Pro: Native history integration (back button works)
  - Pro: Full control over gallery UX
  - Con: Custom implementation (vs library)
  - When to revisit: If Svelte 5 gallery library emerges
Integration Points:
  - Parent: [id]/+page.svelte
  - Uses: page.state for gallery open/close
  - Events: Keyboard (arrows, escape), Touch (swipe)
Testing: E2E test_property_detail_image_gallery.spec.ts
-->
```

---

## Summary

**Total Components:** 8 (7 new + 1 error page)  
**Total Utilities:** 3 (price, property type, SEO)  
**Total Tests:** 5 E2E suites  
**Lines of Code (Estimated):** ~1,200-1,500 lines total

**Key Architectural Decisions:**
1. ✅ SSR-first approach for performance and SEO
2. ✅ Shallow routing for gallery (back button support)
3. ✅ Custom gallery (no Svelte 5 library available)
4. ✅ Reusable utilities extracted (DRY principle)
5. ✅ Progressive enhancement (works without JS)
6. ✅ Mobile-first responsive design
7. ✅ Type-safe with TypeScript throughout

**Ready for Implementation:** Yes ✅

---

**Created By:** Coordinator (Claude Code)  
**Date:** 2025-11-09  
**Design Pattern:** SSR + Progressive Enhancement  
**Architecture Review:** Complete

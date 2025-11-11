# Implementation Specification - TASK-016 Property Detail Page

**Task:** TASK-016 Property Detail Page Frontend  
**Story:** US-023 Property Import & Display with Localization  
**Date:** 2025-11-09

---

## Overview

This document provides file-by-file implementation details for all components, utilities, and tests. Each file includes purpose, code structure, estimated lines of code, and integration points.

**Total Files to Create:** 15  
**Total Files to Modify:** 1  
**Estimated Total LOC:** ~1,800-2,200 lines

---

## File-by-File Implementation

### 1. `apps/frontend/src/routes/[lang]/properties/[id]/+page.ts`

**Purpose:** SSR data loading for property details

**Estimated LOC:** 35-45 lines

**Code Structure:**

```typescript
import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch }) => {
  const { id, lang } = params;
  
  try {
    const response = await fetch(
      `http://localhost:8011/api/v1/properties/${id}?locale=${lang}`
    );
    
    if (!response.ok) {
      if (response.status === 404) {
        throw error(404, 'Property not found');
      }
      throw error(500, 'Failed to load property');
    }
    
    const property = await response.json();
    
    return {
      property,
      locale: lang as 'en' | 'th'
    };
  } catch (err) {
    if (err && typeof err === 'object' && 'status' in err) {
      throw err; // Re-throw SvelteKit errors
    }
    throw error(500, 'Internal server error');
  }
};
```

**Integration Points:**
- API: `GET /api/v1/properties/{id}`
- Types: `PageLoad` from `./$types`, `Property` from `$lib/types/property`
- Error: SvelteKit `error()` helper

**Error Handling:**
```typescript
404 → throw error(404, 'Property not found')
500 → throw error(500, 'Failed to load property')
Network error → throw error(500, 'Internal server error')
```

---

### 2. `apps/frontend/src/routes/[lang]/properties/[id]/+page.svelte`

**Purpose:** Main property detail page

**Estimated LOC:** 450-550 lines

**Code Structure:**

```svelte
<script lang="ts">
  import { page } from '$app/state';
  import { pushState } from '$app/navigation';
  import { getLocaleContext } from '$lib/i18n/context.svelte';
  import PropertyImageGallery from '$lib/components/PropertyImageGallery.svelte';
  import PropertyAmenities from '$lib/components/PropertyAmenities.svelte';
  import PropertyPolicies from '$lib/components/PropertyPolicies.svelte';
  import PropertyContact from '$lib/components/PropertyContact.svelte';
  import { formatPrice } from '$lib/utils/format-price';
  import { propertyTypeLabel } from '$lib/utils/property-type';
  import { generatePropertySchema } from '$lib/utils/seo';
  import type { PageProps } from './$types';
  
  let { data }: PageProps = $props();
  const localeCtx = getLocaleContext();
  
  // Gallery state (shallow routing)
  function openGallery(imageIndex: number) {
    pushState('', { galleryOpen: true, imageIndex });
  }
  
  // Derived values
  const formattedPrice = $derived(
    formatPrice(data.property.rent_price, data.property.currency, localeCtx.locale)
  );
  
  const typeLabel = $derived(
    propertyTypeLabel(data.property.property_type, localeCtx.locale)
  );
</script>

<svelte:head>
  <title>{data.property.title} | BeStays</title>
  <meta name="description" content={data.property.description.slice(0, 160)} />
  
  <!-- Open Graph -->
  <meta property="og:type" content="product" />
  <meta property="og:title" content={data.property.title} />
  <meta property="og:description" content={data.property.description} />
  <meta property="og:image" content={data.property.cover_image?.url} />
  <meta property="og:url" content={`https://bestays.app/${localeCtx.locale}/properties/${data.property.id}`} />
  
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content={data.property.title} />
  <meta name="twitter:description" content={data.property.description} />
  <meta name="twitter:image" content={data.property.cover_image?.url} />
  
  <!-- Canonical -->
  <link rel="canonical" href={`https://bestays.app/${localeCtx.locale}/properties/${data.property.id}`} />
  
  <!-- Structured Data -->
  {@html `<script type="application/ld+json">${generatePropertySchema(data.property)}</script>`}
</svelte:head>

<!-- Hero Section -->
<div class="relative aspect-video">
  <button 
    onclick={() => openGallery(0)}
    class="w-full h-full"
  >
    <img 
      src={data.property.cover_image?.url}
      alt={data.property.cover_image?.alt || data.property.title}
      class="w-full h-full object-cover"
      loading="eager"
      fetchpriority="high"
    />
  </button>
  
  <a 
    href="/{localeCtx.locale}/properties"
    class="absolute top-4 left-4 bg-white/90 px-4 py-2 rounded-lg"
  >
    ← {localeCtx.locale === 'en' ? 'Back to Properties' : 'กลับไปยังรายการ'}
  </a>
</div>

<!-- Header Section -->
<div class="container mx-auto px-4 py-8">
  <div class="flex justify-between items-start">
    <div>
      <h1 class="text-4xl font-bold mb-2">{data.property.title}</h1>
      
      <p class="text-gray-600 mb-4">
        {#if data.property.location_details?.administrative}
          {data.property.location_details.administrative.district_name},
          {data.property.location_details.administrative.province_name}
        {/if}
      </p>
    </div>
    
    <div class="text-right">
      <p class="text-3xl font-bold text-primary">{formattedPrice}</p>
      <span class="text-sm text-gray-500">
        {localeCtx.locale === 'en' ? '/ month' : '/ เดือน'}
      </span>
    </div>
  </div>
  
  <span class="inline-block bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
    {typeLabel}
  </span>
</div>

<!-- Quick Info Grid -->
<div class="container mx-auto px-4 py-4">
  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
    {#if data.property.physical_specs?.rooms?.bedrooms}
      <div class="flex items-center gap-2">
        <span class="text-2xl">🛏️</span>
        <div>
          <p class="text-sm text-gray-500">
            {localeCtx.locale === 'en' ? 'Bedrooms' : 'ห้องนอน'}
          </p>
          <p class="font-semibold">{data.property.physical_specs.rooms.bedrooms}</p>
        </div>
      </div>
    {/if}
    
    {#if data.property.physical_specs?.rooms?.bathrooms}
      <div class="flex items-center gap-2">
        <span class="text-2xl">🚿</span>
        <div>
          <p class="text-sm text-gray-500">
            {localeCtx.locale === 'en' ? 'Bathrooms' : 'ห้องน้ำ'}
          </p>
          <p class="font-semibold">{data.property.physical_specs.rooms.bathrooms}</p>
        </div>
      </div>
    {/if}
    
    {#if data.property.physical_specs?.sizes?.usable_area_sqm}
      <div class="flex items-center gap-2">
        <span class="text-2xl">📐</span>
        <div>
          <p class="text-sm text-gray-500">
            {localeCtx.locale === 'en' ? 'Area' : 'พื้นที่'}
          </p>
          <p class="font-semibold">{data.property.physical_specs.sizes.usable_area_sqm} m²</p>
        </div>
      </div>
    {/if}
    
    {#if data.property.physical_specs?.furnishing}
      <div class="flex items-center gap-2">
        <span class="text-2xl">🪑</span>
        <div>
          <p class="text-sm text-gray-500">
            {localeCtx.locale === 'en' ? 'Furnishing' : 'เฟอร์นิเจอร์'}
          </p>
          <p class="font-semibold capitalize">{data.property.physical_specs.furnishing.replace('_', ' ')}</p>
        </div>
      </div>
    {/if}
  </div>
</div>

<!-- Description Section -->
<div class="container mx-auto px-4 py-8">
  <h2 class="text-2xl font-bold mb-4">
    {localeCtx.locale === 'en' ? 'Description' : 'รายละเอียด'}
  </h2>
  <p class="text-gray-700 whitespace-pre-line">{data.property.description}</p>
  
  {#if data.property.tags?.length}
    <div class="flex gap-2 mt-4">
      {#each data.property.tags as tag}
        <span class="bg-gray-100 px-3 py-1 rounded-full text-sm">{tag}</span>
      {/each}
    </div>
  {/if}
</div>

<!-- Image Gallery -->
{#if data.property.images?.length}
  <div class="container mx-auto px-4 py-8">
    <h2 class="text-2xl font-bold mb-4">
      {localeCtx.locale === 'en' ? 'Photos' : 'รูปภาพ'}
    </h2>
    <PropertyImageGallery images={data.property.images} />
  </div>
{/if}

<!-- Amenities -->
{#if data.property.amenities}
  <div class="container mx-auto px-4 py-8">
    <PropertyAmenities amenities={data.property.amenities} locale={localeCtx.locale} />
  </div>
{/if}

<!-- Policies -->
{#if data.property.policies}
  <div class="container mx-auto px-4 py-8">
    <PropertyPolicies policies={data.property.policies} locale={localeCtx.locale} />
  </div>
{/if}

<!-- Contact -->
{#if data.property.contact_info}
  <div class="container mx-auto px-4 py-8">
    <PropertyContact contactInfo={data.property.contact_info} locale={localeCtx.locale} />
  </div>
{/if}

<!-- Footer Info -->
<div class="container mx-auto px-4 py-8 border-t">
  <p class="text-sm text-gray-500">
    {localeCtx.locale === 'en' ? 'Listed' : 'เผยแพร่'}: {new Date(data.property.created_at).toLocaleDateString(localeCtx.locale === 'th' ? 'th-TH' : 'en-US')}
  </p>
  <p class="text-sm text-gray-500">
    Property ID: {data.property.id}
  </p>
</div>

<!-- Gallery Modal (Shallow Routing) -->
{#if page.state.galleryOpen}
  <PropertyImageGallery 
    images={data.property.images || []}
    initialIndex={page.state.imageIndex || 0}
    onclose={() => history.back()}
  />
{/if}
```

**File Header:**
```svelte
<!--
Design Pattern: Server-Side Rendering with Progressive Enhancement
Architecture: Presentation Layer - Main Property Detail Page
Dependencies:
  - SvelteKit (SSR, shallow routing)
  - bits-ui (via PropertyImageGallery)
  - lucide-svelte (via child components)
  - i18n context (locale management)
Trade-offs:
  - Pro: Instant content display (SSR)
  - Pro: SEO-optimized (meta tags, schema.org)
  - Pro: Mobile-friendly (shallow routing for gallery)
  - Con: Large component (~500 lines) - could split further
  - When to revisit: If component exceeds 600 lines
Integration Points:
  - Load: +page.ts (SSR data)
  - Components: PropertyImageGallery, PropertyAmenities, PropertyPolicies, PropertyContact
  - Utils: formatPrice, propertyTypeLabel, generatePropertySchema
  - State: page.state (shallow routing)
Testing: test_property_detail_display.spec.ts, test_property_detail_navigation.spec.ts
-->
```

---

### 3. `apps/frontend/src/routes/[lang]/properties/[id]/+error.svelte`

**Purpose:** Custom error page for 404 and other errors

**Estimated LOC:** 70-90 lines

**Code Structure:**

```svelte
<script lang="ts">
  import { page } from '$app/state';
  import { getLocaleContext } from '$lib/i18n/context.svelte';
  import { goto } from '$app/navigation';
  
  const localeCtx = getLocaleContext();
  
  function retry() {
    window.location.reload();
  }
</script>

<div class="min-h-screen flex items-center justify-center px-4">
  <div class="max-w-md w-full text-center">
    {#if page.status === 404}
      <!-- 404 Not Found -->
      <div class="text-6xl mb-4">🏠</div>
      <h1 class="text-3xl font-bold mb-4">
        {localeCtx.locale === 'en' ? 'Property Not Found' : 'ไม่พบอสังหาริมทรัพย์'}
      </h1>
      <p class="text-gray-600 mb-8">
        {localeCtx.locale === 'en' 
          ? 'The property you\'re looking for doesn\'t exist or has been removed.' 
          : 'อสังหาริมทรัพย์ที่คุณกำลังมองหาไม่มีอยู่หรือถูกลบไปแล้ว'}
      </p>
      <a 
        href="/{localeCtx.locale}/properties"
        class="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
      >
        {localeCtx.locale === 'en' ? '← Back to Properties' : '← กลับไปยังรายการ'}
      </a>
    {:else}
      <!-- Generic Error -->
      <div class="text-6xl mb-4">⚠️</div>
      <h1 class="text-3xl font-bold mb-4">
        {localeCtx.locale === 'en' ? 'Error' : 'ข้อผิดพลาด'} {page.status}
      </h1>
      <p class="text-gray-600 mb-8">{page.error?.message}</p>
      
      <div class="flex gap-4 justify-center">
        <button 
          onclick={retry}
          class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
        >
          {localeCtx.locale === 'en' ? 'Retry' : 'ลองอีกครั้ง'}
        </button>
        
        <a 
          href="/{localeCtx.locale}/properties"
          class="bg-gray-200 text-gray-800 px-6 py-3 rounded-lg hover:bg-gray-300"
        >
          {localeCtx.locale === 'en' ? 'Back to Properties' : 'กลับไปยังรายการ'}
        </a>
      </div>
    {/if}
  </div>
</div>
```

**File Header:**
```svelte
<!--
Design Pattern: Error Boundary
Architecture: Presentation Layer - Error Page
Dependencies: SvelteKit page store, i18n context
Trade-offs:
  - Pro: User-friendly error messages
  - Pro: Locale-aware
  - Pro: Retry functionality
  - Con: Generic (could be more specific per error type)
Integration Points: SvelteKit error handling, i18n context
Testing: test_property_detail_error_states.spec.ts
-->
```

---

(Continuing in next message due to length...)

### 4-8. Component Files (Summary)

Due to document length, detailed specifications for the following components are summarized:

**4. PropertyImageGallery.svelte** (120-150 LOC)
- bits-ui Dialog for lightbox
- Thumbnail grid (responsive: 2/3/4 columns)
- Keyboard navigation (arrows, escape)
- Touch swipe support
- Image counter display

**5. PropertyAmenities.svelte** (80-100 LOC)
- Interior/Exterior sections
- Icon mapping (lucide-svelte)
- 2-column responsive grid
- Locale-aware labels

**6. PropertyPolicies.svelte** (50-60 LOC)
- House rules (pets, smoking)
- Lease terms display
- Simple list format

**7. PropertyContact.svelte** (40-50 LOC)
- Clickable phone/email/Line buttons
- Icon + text layout
- Contact owner CTA

**8. PropertyDetailSkeleton.svelte** (40-50 LOC)
- Matches actual layout
- Tailwind animate-pulse
- All sections represented

---

### 9-11. Utility Files

**9. lib/utils/format-price.ts** (25-30 LOC)
```typescript
export function formatPrice(satang: number, currency: string, locale: Locale): string {
  const thb = satang / 100;
  return new Intl.NumberFormat(
    locale === 'th' ? 'th-TH' : 'en-US',
    { style: 'currency', currency, minimumFractionDigits: 0 }
  ).format(thb);
}
```

**10. lib/utils/property-type.ts** (30-40 LOC)
- PropertyType labels (EN/TH)
- Translation function
- Type-safe

**11. lib/utils/seo.ts** (40-50 LOC)
- generatePropertySchema() - schema.org JSON-LD
- generateMetaDescription() - truncate to 160 chars

---

### 12-16. E2E Test Files (300-400 LOC each)

**12. test_property_detail_display.spec.ts**
- All sections render correctly
- Data accuracy
- Responsive layouts
- Image loading

**13. test_property_detail_navigation.spec.ts**
- Back button
- Breadcrumbs
- Link from listing page
- URL correctness

**14. test_property_detail_locale.spec.ts**
- Locale switcher
- Price formatting
- Currency display
- UI translations

**15. test_property_detail_error_states.spec.ts**
- 404 handling
- Network failures
- Loading states
- Retry functionality

**16. test_property_detail_image_gallery.spec.ts**
- Gallery interactions
- Lightbox open/close
- Navigation (arrows, keyboard)
- Touch gestures
- Back button closes gallery

---

## Implementation Summary

| File Type | Count | Total LOC |
|-----------|-------|-----------|
| Routes (+page.svelte, +page.ts, +error.svelte) | 3 | 600-700 |
| Components (Gallery, Amenities, Policies, Contact, Skeleton) | 5 | 350-400 |
| Utilities (price, type, SEO) | 3 | 100-120 |
| E2E Tests | 5 | 1,500-2,000 |
| **TOTAL** | **16 files** | **~2,550-3,220 LOC** |

---

## Integration Checklist

- [ ] All components import from correct paths
- [ ] TypeScript types match Property interface
- [ ] i18n context available in all components
- [ ] API endpoint matches backend implementation
- [ ] Error handling consistent across files
- [ ] SEO meta tags complete
- [ ] All E2E tests pass
- [ ] File headers with memory print included

---

**Created By:** Coordinator (Claude Code)  
**Date:** 2025-11-09  
**Ready for Implementation:** Yes ✅

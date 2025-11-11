# TASK-016: Property Detail Page Frontend

**Story:** US-023 (Property Import & Display with Localization)
**Type:** feat
**Branch:** feat/TASK-016-US-023
**Created:** 2025-11-09

---

## 📋 Objective

Implement a comprehensive property detail page at `/[lang]/properties/[id]` that displays all property information with full locale support (EN/TH).

---

## 🎯 Requirements

### Functional Requirements

**FR-1: Route and Data Loading**
- Route: `/[lang]/properties/[id]` (dynamic property ID)
- Fetch property details from Property V2 API: `GET /api/v1/properties/{id}?locale={lang}`
- Handle 404 for non-existent properties
- SSR-compatible data loading via SvelteKit load function
- Loading state while fetching
- Error state for API failures

**FR-2: Property Information Display**

Display all property data in organized sections:

1. **Hero Section**
   - Property title (localized)
   - Property type badge
   - Location (district, province, country)
   - Cover image (hero size, 16:9 aspect ratio)

2. **Key Information**
   - Rental price (with "Price on request" fallback)
   - Bedrooms count
   - Bathrooms count
   - Property size (if available)
   - Year built (if available)

3. **Description**
   - Full property description (localized)
   - Expandable if long text

4. **Image Gallery**
   - All property images (not just cover)
   - Clickable thumbnails
   - Lightbox/modal view for full-size images
   - Navigation between images

5. **Amenities**
   - Display all amenities from `amenities[]` JSONB array
   - Grouped by category (if categories exist)
   - Icons or badges for visual appeal

6. **Policies**
   - Display all policies from `policies[]` JSONB array
   - Grouped by category (check-in, check-out, cancellation, house rules)
   - Clear, scannable format

7. **Location Details**
   - Detailed address (if available)
   - Map integration (future: Phase 2)

8. **Contact/Booking CTA**
   - Prominent "Contact Owner" or "Book Now" button
   - Links to booking flow (future implementation)

**FR-3: Locale Support**
- All content localized (EN/TH)
- LocaleSwitcher maintains current property in URL
- Price formatting based on locale (฿ for TH, ฿ or THB for EN)

**FR-4: Navigation**
- Back to listing button
- Breadcrumbs: Home > Properties > [Property Title]

### Non-Functional Requirements

**NFR-1: Performance**
- SSR for instant content display
- Progressive image loading
- No hydration errors

**NFR-2: Responsiveness**
- Mobile-first design
- Works on all screen sizes (320px to 2560px)
- Touch-friendly gallery on mobile

**NFR-3: SEO**
- Dynamic meta tags (title, description, og:image)
- Structured data for rich snippets (schema.org Property)

**NFR-4: Accessibility**
- ARIA labels for images
- Keyboard navigation for gallery
- Semantic HTML

**NFR-5: Code Quality**
- TypeScript type safety
- File header with design pattern and memory print
- Component reusability (extract shared components)
- Error boundaries

---

## 🧪 Testing Requirements (CRITICAL - Full SDLC Compliance)

**E2E Tests Required** (Playwright):

1. **test_property_detail_display.spec.ts**
   - Navigate to property detail page
   - Verify all sections render (title, price, description, amenities, policies)
   - Verify images load correctly
   - Test responsive layout (desktop, tablet, mobile viewports)

2. **test_property_detail_navigation.spec.ts**
   - Click property card from listing page → navigates to detail
   - Back button returns to listing
   - Breadcrumbs work correctly

3. **test_property_detail_locale.spec.ts**
   - Switch locale on detail page → content updates
   - Price formatting changes based on locale
   - Property title/description localized

4. **test_property_detail_error_states.spec.ts**
   - Invalid property ID → 404 page
   - API failure → error message displayed
   - Loading state shows while fetching

5. **test_property_detail_image_gallery.spec.ts**
   - Click thumbnail → opens lightbox
   - Navigate between images in gallery
   - Close lightbox → returns to page
   - Gallery works on mobile (touch gestures)

**Unit Tests** (Vitest - optional for complex logic):
- PropertyDetailPage component rendering
- Data transformation logic (if any)
- Price formatting utilities

**Coverage Target:** 80%+ for critical paths

---

## 📦 Deliverables

### Frontend Components
1. `apps/frontend/src/routes/[lang]/properties/[id]/+page.svelte` - Detail page
2. `apps/frontend/src/routes/[lang]/properties/[id]/+page.ts` - Load function
3. `apps/frontend/src/lib/components/PropertyImageGallery.svelte` - Image gallery
4. `apps/frontend/src/lib/components/PropertyAmenities.svelte` - Amenities list
5. `apps/frontend/src/lib/components/PropertyPolicies.svelte` - Policies list
6. `apps/frontend/src/lib/utils/formatPrice.ts` - Price formatting utility
7. `apps/frontend/src/lib/utils/seo.ts` - SEO meta tags utility

### Tests
8. `apps/frontend/tests/e2e/property-detail-display.spec.ts`
9. `apps/frontend/tests/e2e/property-detail-navigation.spec.ts`
10. `apps/frontend/tests/e2e/property-detail-locale.spec.ts`
11. `apps/frontend/tests/e2e/property-detail-error-states.spec.ts`
12. `apps/frontend/tests/e2e/property-detail-image-gallery.spec.ts`

### Documentation
13. `.claude/tasks/TASK-016/planning/frontend-implementation-spec.md`
14. `.claude/tasks/TASK-016/planning/component-architecture.md`
15. `.claude/tasks/TASK-016/planning/quality-gates.md`
16. `.claude/tasks/TASK-016/implementation/implementation-report.md`
17. `.claude/tasks/TASK-016/testing/test-results.md`
18. `.claude/tasks/TASK-016/COMPLETION-SUMMARY.md`

---

## ✅ Acceptance Criteria

**AC-1:** Property detail page displays at `/[lang]/properties/[id]` ✅
**AC-2:** All property data renders correctly (title, price, description, amenities, policies, images) ✅
**AC-3:** Image gallery allows viewing all property photos ✅
**AC-4:** Locale switcher changes displayed content ✅
**AC-5:** 404 shown for invalid property IDs ✅
**AC-6:** Loading state displays while fetching ✅
**AC-7:** Error state displays on API failure ✅
**AC-8:** No SSR hydration errors ✅
**AC-9:** Type-safe with TypeScript ✅
**AC-10:** **All 5 E2E test suites pass** ✅ (CRITICAL)
**AC-11:** Responsive on all screen sizes ✅
**AC-12:** SEO meta tags included ✅
**AC-13:** Back to listing navigation works ✅

---

## 🔗 Dependencies

**Depends On:**
- ✅ TASK-013 (Property V2 API) - COMPLETED
- ✅ TASK-014 (Sample Data Import) - COMPLETED
- ✅ TASK-015 (Property Listing Page) - COMPLETED

**Blocks:**
- Future tasks for booking/contact flow
- Future tasks for map integration

---

## 📚 Reference

**API Endpoint:**
```
GET /api/v1/properties/{id}?locale=en
```

**Response Structure:**
```typescript
{
  id: string;
  title: string;
  description: string;
  property_type: string;
  rent_price: number;
  cover_image: {url: string, alt: string, width: number, height: number};
  images: Array<{url: string, alt: string, width: number, height: number}>;
  physical_specs: {
    rooms: {bedrooms: number, bathrooms: number},
    size: {value: number, unit: string}
  };
  location_details: {
    address: string,
    district: string,
    province: string,
    country: string
  };
  amenities: Array<{name: string, category: string, icon: string}>;
  policies: Array<{name: string, description: string, category: string}>;
  created_at: string;
  updated_at: string;
}
```

**Existing Implementation Reference:**
- Property V2 API: `apps/server/src/server/api/v1/endpoints/properties.py:97`
- PropertyCard component: `apps/frontend/src/lib/components/PropertyCard.svelte`
- Property types: `apps/frontend/src/lib/types/property.ts`

---

## 🚀 SDLC Phases

**Current Phase:** RESEARCH

**Next Steps:**
1. ✅ `/task-research` - Research existing patterns (image galleries, detail pages)
2. ⏭️ `/task-plan` - Create comprehensive implementation plan (apply 7 quality gates)
3. ⏭️ `/task-implement` - Delegate to `dev-frontend-svelte` subagent
4. ⏭️ **TESTING** - Run E2E tests, fix any failures
5. ⏭️ **VALIDATION** - Verify acceptance criteria, update STATE.json

---

## 💡 Good Practices for This Task

1. **Research Phase:**
   - Check existing gallery components in codebase
   - Review Svelte 5 best practices for image handling
   - Research SEO meta tags for SvelteKit

2. **Planning Phase:**
   - Apply all 7 quality gates (especially Network Operations, Frontend SSR/UX, Testing Requirements)
   - Design component hierarchy (reusable components)
   - Plan E2E test scenarios upfront
   - Validate with official Svelte/SvelteKit docs (use Svelte MCP)

3. **Implementation Phase:**
   - Use `dev-frontend-svelte` subagent (NEVER implement directly as coordinator)
   - Follow file header pattern with memory print
   - Extract reusable components (DRY principle)

4. **Testing Phase:**
   - Use `playwright-e2e-tester` subagent for E2E tests
   - Verify all 5 test suites pass
   - Test on multiple browsers (Chromium, Firefox, WebKit)
   - Test responsive breakpoints

5. **Validation Phase:**
   - Verify all acceptance criteria met
   - Update STATE.json to completed
   - Create COMPLETION-SUMMARY.md
   - Commit with proper message format

---

**Created By:** Coordinator (Claude Code)
**Assigned To:** dev-frontend-svelte (implementation), playwright-e2e-tester (testing)
**Story:** US-023 Property Import & Display
**Priority:** HIGH (completes core property viewing feature)

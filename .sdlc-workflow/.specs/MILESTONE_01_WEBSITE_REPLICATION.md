# Milestone 01: Website Replication with New Tech Stack

**Project:** Bestays RealEstate Platform
**Goal:** Replicate existing NextJS website functionality using SvelteKit + FastAPI
**Date:** 2025-11-06
**Status:** Planning Phase

---

## Executive Summary

This milestone focuses on replicating the core functionality of the existing NextJS bestays-web application using our new tech stack (SvelteKit 2 + Svelte 5 + FastAPI). The goal is to achieve feature parity with the current production site while:

1. **Maintaining all existing functionality** for guests and agents
2. **Modernizing the property data model** (from monolithic to subdomain-based)
3. **Improving code maintainability** with new architecture patterns
4. **Postponing chat-as-CMS** implementation (keep code but don't use)
5. **Removing Three.js** from homepage (simplify initial load)

---

## Source of Truth

**Old NextJS Application:**
`/Users/solo/Projects/_repos/react-workspace/src/apps/bestays-web`

**Key Findings from Analysis:**
- **Tech Stack:** Next.js 15, React 19, Supabase, Radix UI, Tailwind CSS
- **Database:** Single `bestays_properties` table with Supabase
- **Pages:** Homepage, listings (6 categories), property details, CMS dashboard
- **Features:**
  - Guest: Browse properties by category/location, view details
  - Agent: Manage properties (CRUD), drag-drop image upload
  - Auth: Supabase email/password authentication

---

## New Tech Stack

**Frontend:**
- SvelteKit 2 + Svelte 5 (runes)
- Tailwind CSS 4
- Melt UI or shadcn-svelte (Radix UI equivalent)
- TanStack Query (data fetching)

**Backend:**
- FastAPI (Python)
- PostgreSQL 16 + pgvector
- SQLAlchemy + Alembic (migrations)
- Redis (caching)

**Storage:**
- Cloudflare R2 (images)

**Auth:**
- Clerk (replacing Supabase Auth)

---

## High-Level User Stories

### Epic 1: Guest User Experience
**As a guest user, I want to browse properties on the new website**

- US-002: View homepage with property categories
- US-003: Browse property listings by category
- US-004: View property details
- US-005: Browse properties by location (region/area)

### Epic 2: Agent Property Management
**As an agent, I want to manage properties in a modern dashboard**

- US-006: View all my properties in a table
- US-007: Create new property
- US-008: Edit existing property
- US-009: Upload and manage property images
- US-010: Publish/unpublish properties
- US-011: Delete properties (soft delete)

### Epic 3: Authentication & Authorization
**As a system, I need secure authentication**

- US-012: User login/logout
- US-013: User registration
- US-014: Password reset
- US-015: Protected routes (CMS dashboard)

### Epic 4: Backend & Data Migration
**As a system, I need robust backend infrastructure**

- US-016: Migrate property schema to subdomain model
- US-017: Create FastAPI endpoints for properties
- US-018: Implement image upload to Cloudflare R2
- US-019: Set up Clerk authentication
- US-020: Create API endpoints for locations/catalogues

---

## Detailed User Stories

### US-002: Homepage with Property Categories

**User Story:**
> As a guest user, I want to see a homepage with property categories so I can quickly find properties I'm interested in.

**Acceptance Criteria:**
- [ ] Homepage displays at `/` route
- [ ] Hero section with background image and title
  - Title: "Best Stays - Your Real Estate Destination in Thailand"
  - Single static background image (no Three.js)
- [ ] 6 property category sections displayed:
  1. Freehold & Leasehold
  2. Land For Sale
  3. Land For Lease
  4. Business For Sale
  5. Properties For Rent
  6. Properties For Sale
- [ ] Each section shows:
  - Section title
  - 5 latest properties (horizontal scroll on mobile)
  - "View More" button linking to full listing page
- [ ] Region & Area navigation section:
  - Top 12 regions displayed as clickable cards
  - 24 area links (region + area combinations)
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] No Three.js scenes (removed from old implementation)
- [ ] Page loads in < 2 seconds

**Technical Details:**
```typescript
// Route: src/routes/+page.svelte
// Load function: src/routes/+page.server.ts

// Fetch latest properties per category
const categories = [
  { id: 'freehold-leasehold', types: ['land'], transactions: ['sale', 'lease'] },
  { id: 'land-for-sale', types: ['land'], transactions: ['sale'] },
  // ... 4 more
];

for (const category of categories) {
  const properties = await fetchProperties({
    property_types: category.types,
    transaction_types: category.transactions,
    limit: 5,
    order_by: 'updated_at'
  });
}

// Fetch top locations
const locations = await fetchTopLocations(12);
```

**API Endpoints:**
- `GET /api/v1/properties/public` - List properties with filters
- `GET /api/v1/locations/top` - Get top N regions/areas

**UI Components:**
- `PropertyCard.svelte` - Property display card
- `PropertySection.svelte` - Category section with horizontal scroll
- `LocationCard.svelte` - Region/area navigation card
- `HeroSection.svelte` - Hero with background image

**Design Reference:**
- Current NextJS: `app/(public)/page.tsx`
- Components: `components/properties/property-listing.tsx`

**Dependencies:**
- None (first user story)

**Estimated Effort:** 3 days

---

### US-003: Property Listings by Category

**User Story:**
> As a guest user, I want to browse property listings filtered by category so I can see all available properties of a specific type.

**Acceptance Criteria:**
- [ ] Listing pages display at `/listings/{category}` routes:
  - `/listings/freehold-leasehold`
  - `/listings/land-for-sale`
  - `/listings/land-for-lease`
  - `/listings/business-for-sale`
  - `/listings/properties-for-rent`
  - `/listings/properties-for-sale`
- [ ] Each listing page shows:
  - Page title (e.g., "Land For Sale")
  - Grid of property cards (1 col mobile, 2 col tablet, 3 col desktop)
  - All published properties matching category filters
- [ ] Properties filtered by:
  - Property type(s)
  - Transaction type(s)
- [ ] Properties sorted by `updated_at` descending (newest first)
- [ ] Responsive grid layout
- [ ] Pagination or infinite scroll (if > 50 properties)
- [ ] Empty state message if no properties

**Technical Details:**
```typescript
// Route: src/routes/listings/[category]/+page.svelte
// Load: src/routes/listings/[category]/+page.server.ts

// Category configurations
const CATEGORY_CONFIGS = {
  'land-for-sale': {
    title: 'Land For Sale',
    property_types: ['land'],
    transaction_types: ['sale']
  },
  'properties-for-rent': {
    title: 'Properties For Rent',
    property_types: ['apartment', 'condo', 'house', 'villa', 'pool_villa'],
    transaction_types: ['rent', 'lease']
  },
  // ... more configs
};

export async function load({ params }) {
  const config = CATEGORY_CONFIGS[params.category];
  const properties = await fetchProperties({
    property_types: config.property_types,
    transaction_types: config.transaction_types,
    is_published: true
  });

  return { properties, title: config.title };
}
```

**API Endpoints:**
- `GET /api/v1/properties/public?property_types=land&transaction_types=sale`

**UI Components:**
- `PropertyGrid.svelte` - Responsive grid container
- `PropertyCard.svelte` - Reused from US-002
- `EmptyState.svelte` - No properties message

**Design Reference:**
- Current NextJS: `app/(public)/listings/[id]/page.tsx`

**Dependencies:**
- US-002 (PropertyCard component)

**Estimated Effort:** 2 days

---

### US-004: Property Detail Page

**User Story:**
> As a guest user, I want to view detailed information about a property so I can decide if I'm interested.

**Acceptance Criteria:**
- [ ] Detail page displays at `/p/{property_id}` route
- [ ] Page layout (2-column on desktop, stacked on mobile):
  - **Left Column (2/3 width):**
    - Large hero image (cover image)
    - Thumbnail gallery (up to 8 additional images, 3x3 mobile, 4-col desktop)
    - Click thumbnail to view fullscreen
    - Fullscreen modal with navigation arrows
    - Property description (full text, preserved whitespace)
  - **Right Column (1/3 width):**
    - **Key Facts Card:**
      - Transaction type badge (Sale/Rent/Lease)
      - Property type badge
      - Land size with unit (sqm, rai, ngan, wah)
      - Price (formatted with ฿ symbol, or "Ask for price" button)
    - **Agent Contact Card:**
      - WhatsApp contact button
      - "Ask for price" button (if no price shown)
    - **Location Card:**
      - Clickable region/area links
- [ ] Below grid:
  - Property description
  - Related properties section (5 similar properties)
- [ ] Dynamic page metadata for SEO:
  - Title: `{property.title} - Best Stays`
  - Description: First 160 chars of description
  - OG image: Cover image
- [ ] 404 page if property not found or not published
- [ ] Responsive layout

**Technical Details:**
```typescript
// Route: src/routes/p/[id]/+page.svelte
// Load: src/routes/p/[id]/+page.server.ts

export async function load({ params }) {
  const property = await fetchPropertyDetails(params.id);

  if (!property || !property.is_published) {
    throw error(404, 'Property not found');
  }

  // Fetch related properties (same type, same region)
  const related = await fetchProperties({
    property_types: [property.property_type],
    location_region: property.location.region,
    exclude_id: params.id,
    limit: 5
  });

  return { property, related };
}

// SEO metadata
export function generateMetadata({ data }) {
  return {
    title: `${data.property.title} - Best Stays`,
    description: data.property.text?.substring(0, 160),
    openGraph: {
      images: [data.property.cover_image?.url]
    }
  };
}
```

**API Endpoints:**
- `GET /api/v1/properties/public/{id}` - Get property details
- `GET /api/v1/properties/public/related?type={type}&region={region}&exclude={id}`

**UI Components:**
- `PropertyDetailLayout.svelte` - Two-column layout
- `ImageGallery.svelte` - Hero + thumbnails + fullscreen modal
- `KeyFactsCard.svelte` - Property details card
- `ContactCard.svelte` - Agent contact info
- `LocationCard.svelte` - Location links
- `RelatedProperties.svelte` - Similar properties section

**Design Reference:**
- Current NextJS: `app/(public)/p/[id]/page.tsx`
- Components: `components/property/property-details.tsx`

**Dependencies:**
- US-002 (PropertyCard for related properties)

**Estimated Effort:** 4 days

---

### US-005: Location-Based Property Listings

**User Story:**
> As a guest user, I want to browse properties by location (region or area) so I can find properties in my preferred location.

**Acceptance Criteria:**
- [ ] Location pages display at:
  - `/locations/{region}` - All properties in a region
  - `/locations/{region}/{area}` - All properties in a specific area
- [ ] Each location page shows:
  - Page title: "{Region Name}" or "{Area Name}, {Region Name}"
  - Grid of property cards (same as US-003)
  - All published properties in that location
- [ ] Properties sorted by `updated_at` descending
- [ ] Responsive grid layout
- [ ] Breadcrumb navigation:
  - Region page: `Home > {Region}`
  - Area page: `Home > {Region} > {Area}`
- [ ] Empty state if no properties in location
- [ ] 404 if location doesn't exist

**Technical Details:**
```typescript
// Routes:
// src/routes/locations/[region]/+page.svelte
// src/routes/locations/[region]/[area]/+page.svelte

// Load function (region page)
export async function load({ params }) {
  const properties = await fetchProperties({
    location_region: params.region,
    is_published: true
  });

  if (properties.length === 0) {
    // Check if region exists at all
    const regionExists = await checkRegionExists(params.region);
    if (!regionExists) {
      throw error(404, 'Region not found');
    }
  }

  return { properties, region: params.region };
}

// Load function (area page)
export async function load({ params }) {
  const properties = await fetchProperties({
    location_region: params.region,
    location_area: params.area,
    is_published: true
  });

  if (properties.length === 0) {
    const areaExists = await checkAreaExists(params.region, params.area);
    if (!areaExists) {
      throw error(404, 'Area not found');
    }
  }

  return {
    properties,
    region: params.region,
    area: params.area
  };
}
```

**API Endpoints:**
- `GET /api/v1/properties/public?location_region={region}`
- `GET /api/v1/properties/public?location_region={region}&location_area={area}`
- `GET /api/v1/locations/regions` - List all regions
- `GET /api/v1/locations/regions/{region}/areas` - List areas in region

**UI Components:**
- `PropertyGrid.svelte` - Reused from US-003
- `Breadcrumb.svelte` - Navigation breadcrumbs
- `EmptyState.svelte` - Reused

**Design Reference:**
- Current NextJS: `app/locations/[region]/page.tsx`

**Dependencies:**
- US-003 (PropertyGrid component)

**Estimated Effort:** 2 days

---

### US-006: Agent Property List Table

**User Story:**
> As an agent, I want to view all my properties in a table so I can manage them efficiently.

**Acceptance Criteria:**
- [ ] Property list displays at `/cms/properties` route
- [ ] Requires authentication (redirect to login if not authenticated)
- [ ] Table shows only properties created by logged-in agent
- [ ] Table columns:
  1. **Title** - Thumbnail (64x64) + title text (truncated to 30 chars)
  2. **Location** - "{Region}, {Area}"
  3. **Price** - Formatted with ฿ symbol (empty if no price)
  4. **Transaction** - Badge (color-coded: Green=Sale, Blue=Rent, Yellow=Lease)
  5. **Type** - Property type badge
  6. **Published** - Status badge (Green="Published", Gray="Draft")
  7. **Last Update** - Relative time (e.g., "2 hours ago")
- [ ] Sorting:
  - Click column header to sort (ascending/descending)
  - Default sort: `updated_at` descending (newest first)
  - Sort indicators (up/down arrows)
- [ ] Row actions:
  - Click row to navigate to edit page (`/cms/properties/{id}`)
- [ ] Toolbar:
  - "New Property" button (creates empty property, redirects to edit)
- [ ] Table features:
  - Responsive (stack on mobile)
  - Loading state while fetching
  - Empty state if no properties ("Create your first property")
- [ ] Performance:
  - Only fetch properties owned by user
  - Use database view for optimized query

**Technical Details:**
```typescript
// Route: src/routes/cms/properties/+page.svelte
// Load: src/routes/cms/properties/+page.server.ts

export async function load({ locals }) {
  // Require auth
  if (!locals.session) {
    throw redirect(303, '/auth/login');
  }

  // Fetch user's properties
  const properties = await fetchCMSProperties(locals.session.user.id);

  return { properties };
}

// Create new property action
export const actions = {
  create: async ({ locals }) => {
    const newProperty = await createEmptyProperty(locals.session.user.id);
    throw redirect(303, `/cms/properties/${newProperty.id}`);
  }
};
```

**API Endpoints:**
- `GET /api/v1/properties/cms?created_by={user_id}` - List agent's properties
- `POST /api/v1/properties` - Create empty property

**UI Components:**
- `PropertyTable.svelte` - Table component (TanStack Table or custom)
- `PropertyTableColumns.svelte` - Column definitions
- `Badge.svelte` - Status badges
- `Button.svelte` - Action buttons

**Database:**
```sql
-- View: cms_property_listings (optimized for table)
CREATE VIEW cms_property_listings AS
SELECT
  id,
  COALESCE(title, LEFT(text, 50)) as title,
  location,
  price,
  cover_image,
  transaction_type,
  property_type,
  is_published,
  updated_at,
  created_by
FROM properties
WHERE deleted_at IS NULL;
```

**Design Reference:**
- Current NextJS: `app/(protected)/cms/properties/page.tsx`
- Components: `app/(protected)/cms/properties/data-table.tsx`

**Dependencies:**
- US-012 (Authentication)

**Estimated Effort:** 3 days

---

### US-007: Create New Property

**User Story:**
> As an agent, I want to create a new property so I can add it to the platform.

**Acceptance Criteria:**
- [ ] "New Property" button in toolbar (from US-006)
- [ ] Click button:
  - Creates empty property in database (draft state)
  - Property auto-assigned to logged-in agent (`created_by`)
  - Redirects to edit page `/cms/properties/{new_id}`
- [ ] New property defaults:
  - `is_published: false` (draft)
  - `title: null`
  - All other fields empty/null
  - `created_at`, `updated_at` set to now
- [ ] Action completes in < 500ms
- [ ] Error handling:
  - Show toast notification if creation fails
  - Stay on property list page

**Technical Details:**
```typescript
// Action in: src/routes/cms/properties/+page.server.ts

export const actions = {
  create: async ({ locals }) => {
    try {
      const newProperty = await fetch('/api/v1/properties', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${locals.session.token}`
        },
        body: JSON.stringify({
          created_by: locals.session.user.id,
          is_published: false
        })
      });

      const data = await newProperty.json();
      throw redirect(303, `/cms/properties/${data.id}`);
    } catch (error) {
      return fail(500, { error: 'Failed to create property' });
    }
  }
};
```

**API Endpoints:**
- `POST /api/v1/properties` - Create empty property
  - Request body: `{ created_by: string, is_published: false }`
  - Response: `{ id, created_at, updated_at, ... }`

**Design Reference:**
- Current NextJS: `app/(protected)/cms/properties/[id]/actions.tsx`

**Dependencies:**
- US-006 (Property list table)

**Estimated Effort:** 0.5 days (simple action)

---

### US-008: Edit Property Details

**User Story:**
> As an agent, I want to edit property details so I can keep property information up-to-date.

**Acceptance Criteria:**
- [ ] Edit page displays at `/cms/properties/{id}` route
- [ ] Requires authentication + ownership check
  - If not owner, show 403 error
  - If not authenticated, redirect to login
- [ ] Form layout (2-column on desktop, stacked on mobile):
  - **Left Column:**
    1. **Title** (required)
       - Text input, max 200 characters
       - Character counter (e.g., "45/200")
    2. **Location** (required)
       - Region dropdown (searchable)
       - Area dropdown (filtered by region, searchable)
       - "Create new" option in both dropdowns
       - Selecting region resets area
    3. **Transaction Type** (required)
       - Dropdown: Sale, Rent, Lease, Sale-Lease
    4. **Property Type** (required)
       - Dropdown: Land, House, Villa, Pool Villa, Apartment, Condo, Office, Shop, Business, Other
    5. **Price** (optional)
       - Number input
       - Currency: THB (฿ symbol prefix)
    6. **Land Size** (optional)
       - Number input + unit dropdown (sqm, rai, ngan, wah)
    7. **Title Deed** (optional)
       - Dropdown with existing deeds + "Create new" option
  - **Right Column:**
    1. **Images** (required, min 1, max 20)
       - See US-009 for details
    2. **Description** (optional)
       - Textarea, max 5000 characters
       - Character counter
       - Min height 30vh, expands with content
- [ ] Toolbar (top of page):
  - **Back button** - Returns to property list
  - **Published toggle** - Only enabled if all required fields filled
  - **Save button** - Saves property, uploads images if needed
  - **Restore button** (only if soft-deleted) - Undeletes property
- [ ] Bottom actions:
  - **Delete button** - Soft deletes property (sets `deleted_at`)
  - Delete confirmation dialog
- [ ] Form validation:
  - Client-side: Show inline errors for invalid fields
  - Server-side: Validate with Pydantic schemas
  - Required fields: title, location (region + area), transaction type, property type, at least 1 image
- [ ] Save behavior:
  - On save, validate all fields
  - If validation fails, show errors inline
  - If validation passes, update database
  - Show success toast notification
  - Stay on edit page (don't redirect)
- [ ] Deleted state:
  - If property is deleted (`deleted_at` not null), show "DELETED" overlay
  - All fields read-only except "Restore" button
- [ ] Auto-save: NO auto-save (only on explicit "Save" click)
- [ ] Unsaved changes warning:
  - If user tries to leave page with unsaved changes, show confirmation dialog

**Technical Details:**
```typescript
// Route: src/routes/cms/properties/[id]/+page.svelte
// Load: src/routes/cms/properties/[id]/+page.server.ts

export async function load({ params, locals }) {
  const property = await fetchCMSProperty(params.id);

  // Check ownership
  if (property.created_by !== locals.session.user.id) {
    throw error(403, 'Not authorized');
  }

  // Fetch dropdown options
  const locations = await fetchLocations();
  const titleDeeds = await fetchTitleDeeds();

  return { property, locations, titleDeeds };
}

// Save action
export const actions = {
  save: async ({ request, params, locals }) => {
    const formData = await request.formData();

    // Validate
    const validationResult = validateProperty(formData);
    if (!validationResult.success) {
      return fail(400, { errors: validationResult.errors });
    }

    // Update property
    await updateProperty(params.id, formData);

    return { success: true };
  },

  delete: async ({ params }) => {
    await softDeleteProperty(params.id);
    throw redirect(303, '/cms/properties');
  },

  restore: async ({ params }) => {
    await restoreProperty(params.id);
    return { success: true };
  }
};
```

**API Endpoints:**
- `GET /api/v1/properties/cms/{id}` - Get property for editing
- `PATCH /api/v1/properties/{id}` - Update property
- `DELETE /api/v1/properties/{id}` - Soft delete (set `deleted_at`)
- `POST /api/v1/properties/{id}/restore` - Undelete (clear `deleted_at`)
- `GET /api/v1/locations` - Get all regions/areas
- `GET /api/v1/catalogues/title-deeds` - Get title deed options

**UI Components:**
- `PropertyForm.svelte` - Main form container
- `FormTextInput.svelte` - Text input with validation
- `FormDropdown.svelte` - Dropdown with search
- `FormNumberInput.svelte` - Number input with formatting
- `FormTextarea.svelte` - Textarea with character counter
- `FormImageInput.svelte` - Image upload (see US-009)
- `ConfirmDialog.svelte` - Delete confirmation

**Design Reference:**
- Current NextJS: `app/(protected)/cms/properties/[id]/PropertyForm.tsx`
- Components: `components/property-form/*`

**Dependencies:**
- US-006 (Property list for navigation)
- US-009 (Image upload component)

**Estimated Effort:** 5 days

---

### US-009: Property Image Upload & Management

**User Story:**
> As an agent, I want to upload and manage property images so I can showcase properties effectively.

**Acceptance Criteria:**
- [ ] Image upload section in property edit form (right column)
- [ ] Layout:
  - **Cover area** (left side, large preview)
    - Shows current cover image
    - Drop zone to set new cover (drag image from thumbnails)
    - "Cover" label badge
  - **Thumbnails** (right side, vertical list)
    - Shows all other images (not cover)
    - Drag handles for reordering
    - Delete button (X) on each image
    - Image count indicator (e.g., "8/20 images")
- [ ] Upload methods:
  - Click "Upload Images" button → file picker
  - Drag & drop files onto upload area
  - Paste from clipboard
- [ ] File validation:
  - Supported formats: JPG, PNG, WebP
  - Max file size: 10MB per image
  - Max total images: 20
  - Show error toast for invalid files
- [ ] Image processing:
  - Client-side preview (local URL)
  - Upload to Cloudflare R2 immediately on selection
  - Show upload progress (0-100%)
  - Show checkmark when uploaded
- [ ] Drag & drop features:
  - Reorder thumbnails (drag up/down)
  - Set cover image (drag to cover area)
  - Smooth animations
- [ ] Delete images:
  - Click X button → confirmation dialog
  - Image marked for deletion (still visible, grayed out)
  - Actual deletion happens on "Save"
  - Can undo deletion before saving
- [ ] State management:
  - Use Svelte store for image state
  - Track: images, order (imageIds), cover (first in order), deleted (marked for deletion)
- [ ] Persistence:
  - Images uploaded to R2 immediately
  - Database updated with image URLs on "Save"
  - Deleted images removed from R2 on "Save"
- [ ] Required validation:
  - At least 1 image required to publish
  - Show error if try to publish with 0 images
- [ ] Loading states:
  - Show spinner during upload
  - Disable "Save" while images uploading

**Technical Details:**
```typescript
// Component: src/lib/components/property-form/ImageUpload.svelte

// Image store (Svelte store)
import { writable, derived } from 'svelte/store';

type ImageState = {
  images: Record<number, MutableImage>;
  imageIds: number[];  // Ordered, first = cover
  deletedIds: number[];
  uploadingIds: number[];
};

export const imageStore = writable<ImageState>({
  images: {},
  imageIds: [],
  deletedIds: [],
  uploadingIds: []
});

// Derived: Cover image
export const coverImage = derived(imageStore, $store => {
  const coverId = $store.imageIds[0];
  return coverId ? $store.images[coverId] : null;
});

// Actions
export function addImage(file: File) {
  const id = Date.now();
  imageStore.update(state => ({
    ...state,
    images: { ...state.images, [id]: { id, file, url: null, uploading: true } },
    imageIds: [...state.imageIds, id],
    uploadingIds: [...state.uploadingIds, id]
  }));

  // Upload to R2
  uploadToR2(file, id);
}

export function deleteImage(id: number) {
  imageStore.update(state => ({
    ...state,
    deletedIds: [...state.deletedIds, id]
  }));
}

export function reorderImages(newOrder: number[]) {
  imageStore.update(state => ({
    ...state,
    imageIds: newOrder
  }));
}

export function setCoverImage(id: number) {
  imageStore.update(state => {
    const newOrder = [id, ...state.imageIds.filter(i => i !== id)];
    return { ...state, imageIds: newOrder };
  });
}

// Upload to Cloudflare R2
async function uploadToR2(file: File, imageId: number) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('/api/v1/images/upload', {
    method: 'POST',
    body: formData
  });

  const { url, path } = await response.json();

  // Update store with uploaded URL
  imageStore.update(state => ({
    ...state,
    images: {
      ...state.images,
      [imageId]: { ...state.images[imageId], url, path, uploading: false }
    },
    uploadingIds: state.uploadingIds.filter(id => id !== imageId)
  }));
}

// On form save, persist to database
async function saveImages(propertyId: string) {
  const state = imageStore.getState();

  // Delete marked images from R2
  for (const id of state.deletedIds) {
    const image = state.images[id];
    if (image.path) {
      await fetch(`/api/v1/images/${image.path}`, { method: 'DELETE' });
    }
  }

  // Get final image order
  const images = state.imageIds
    .filter(id => !state.deletedIds.includes(id))
    .map(id => state.images[id]);

  // Update property with image URLs
  await updateProperty(propertyId, { images, cover_image: images[0] });
}
```

**API Endpoints:**
- `POST /api/v1/images/upload` - Upload image to Cloudflare R2
  - Request: `multipart/form-data` with file
  - Response: `{ url: string, path: string }`
- `DELETE /api/v1/images/{path}` - Delete image from R2

**Cloudflare R2 Integration:**
```python
# FastAPI endpoint
from fastapi import UploadFile
import boto3

s3_client = boto3.client(
    's3',
    endpoint_url='https://<account-id>.r2.cloudflarestorage.com',
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY
)

@app.post("/api/v1/images/upload")
async def upload_image(file: UploadFile):
    # Generate unique filename
    filename = f"{uuid.uuid4()}-{file.filename}"
    path = f"properties/{filename}"

    # Upload to R2
    s3_client.upload_fileobj(
        file.file,
        'bestays-images',
        path,
        ExtraArgs={'ContentType': file.content_type}
    )

    # Return public URL
    url = f"https://images.bestays.com/{path}"
    return {"url": url, "path": path}
```

**UI Libraries:**
- Drag & Drop: `svelte-dnd-action` or `@dnd-kit/svelte`
- Image Preview: Native `<img>` with object-fit

**Design Reference:**
- Current NextJS: `components/property-form/image-input/*`
- Store: `entities/image/stores/images.store.ts`

**Dependencies:**
- US-008 (Property edit form)

**Estimated Effort:** 4 days

---

### US-010: Publish/Unpublish Properties

**User Story:**
> As an agent, I want to publish or unpublish properties so I can control which properties are visible to guests.

**Acceptance Criteria:**
- [ ] "Published" toggle in property edit form toolbar (from US-008)
- [ ] Toggle states:
  - **ON (Published):** Property visible to guests
  - **OFF (Draft):** Property hidden from guests
- [ ] Toggle only enabled if:
  - All required fields filled (title, location, transaction type, property type)
  - At least 1 image uploaded
  - If not valid, toggle disabled with tooltip explaining why
- [ ] Toggle changes:
  - Clicking toggle immediately updates `is_published` field in database
  - No need to click "Save" (instant update)
  - Show success toast: "Property published" or "Property unpublished"
  - Update property list table (if navigating back)
- [ ] Visual feedback:
  - Toggle shows loading spinner during update
  - Toggle color: Green (published), Gray (draft)
- [ ] Property list table reflects status:
  - "Published" badge (green) if published
  - "Draft" badge (gray) if not published

**Technical Details:**
```typescript
// In property edit form: src/routes/cms/properties/[id]/+page.svelte

let isPublished = $state(data.property.is_published);
let canPublish = $derived(
  formData.title?.length > 0 &&
  formData.location?.region &&
  formData.location?.area &&
  formData.transaction_type &&
  formData.property_type &&
  $imageStore.imageIds.length > 0
);

async function togglePublished() {
  const newState = !isPublished;

  try {
    await fetch(`/api/v1/properties/${propertyId}/publish`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_published: newState })
    });

    isPublished = newState;
    showToast(newState ? 'Property published' : 'Property unpublished');
  } catch (error) {
    showToast('Failed to update publish status', 'error');
  }
}
```

**API Endpoints:**
- `PATCH /api/v1/properties/{id}/publish` - Toggle publish status
  - Request body: `{ is_published: boolean }`
  - Response: `{ success: true, is_published: boolean }`

**UI Components:**
- `Switch.svelte` - Toggle switch component
- `Tooltip.svelte` - Tooltip for disabled state

**Design Reference:**
- Current NextJS: `app/(protected)/cms/properties/[id]/PropertyForm.tsx` (published toggle)

**Dependencies:**
- US-008 (Property edit form)

**Estimated Effort:** 1 day

---

### US-011: Delete Properties (Soft Delete)

**User Story:**
> As an agent, I want to delete properties so I can remove listings I no longer need.

**Acceptance Criteria:**
- [ ] "Delete" button at bottom of property edit form (from US-008)
- [ ] Click "Delete" button:
  - Show confirmation dialog
  - Dialog message: "Are you sure you want to delete this property? This action can be undone."
  - Dialog buttons: "Cancel", "Delete" (red/destructive style)
- [ ] Confirm delete:
  - Soft delete property (set `deleted_at` timestamp)
  - Do NOT remove from database
  - Property still appears in property list table (for now)
  - Show "DELETED" overlay on edit form
  - All form fields become read-only
  - "Delete" button hidden
  - "Restore" button shown
- [ ] "Restore" button (only visible if deleted):
  - Undeletes property (clear `deleted_at`)
  - Remove "DELETED" overlay
  - Form fields become editable again
  - Show success toast: "Property restored"
- [ ] Deleted properties behavior:
  - Hidden from public listings (guests cannot see)
  - Still visible in CMS property list table (with "Deleted" badge)
  - Can be restored or permanently deleted (future enhancement)
- [ ] Permanently delete (future):
  - Admin-only action (not in MVP)
  - Hard delete from database
  - Delete all images from R2

**Technical Details:**
```typescript
// Action in: src/routes/cms/properties/[id]/+page.server.ts

export const actions = {
  delete: async ({ params, locals }) => {
    const now = new Date().toISOString();

    await fetch(`/api/v1/properties/${params.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ deleted_at: now })
    });

    return { success: true, deleted: true };
  },

  restore: async ({ params }) => {
    await fetch(`/api/v1/properties/${params.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ deleted_at: null })
    });

    return { success: true, deleted: false };
  }
};
```

**API Endpoints:**
- `PATCH /api/v1/properties/{id}` - Update `deleted_at` field
  - Request body: `{ deleted_at: string | null }`
  - Response: `{ success: true }`

**UI Components:**
- `ConfirmDialog.svelte` - Confirmation dialog
- `Button.svelte` - Delete/Restore buttons
- `DeletedOverlay.svelte` - "DELETED" stamp overlay

**Database:**
```sql
-- Properties table already has deleted_at column
-- Add index for soft delete queries
CREATE INDEX idx_properties_deleted_at ON properties (deleted_at)
WHERE deleted_at IS NOT NULL;

-- Update public views to exclude deleted
CREATE OR REPLACE VIEW public_property_listings AS
SELECT * FROM properties
WHERE is_published = true AND deleted_at IS NULL;
```

**Design Reference:**
- Current NextJS: `app/(protected)/cms/properties/[id]/PropertyForm.tsx` (delete button)

**Dependencies:**
- US-008 (Property edit form)

**Estimated Effort:** 1 day

---

### US-012: User Login & Logout

**User Story:**
> As an agent, I want to log in and log out so I can access my dashboard securely.

**Acceptance Criteria:**
- [ ] Login page displays at `/auth/login` route
- [ ] Login form:
  - Email input (required, validated)
  - Password input (required, min 8 characters)
  - "Remember me" checkbox (optional)
  - "Log In" button
  - "Forgot password?" link → `/auth/forgot-password`
  - "Don't have an account? Sign up" link → `/auth/sign-up`
- [ ] Form validation:
  - Show inline errors for invalid email
  - Show error for empty password
  - Client-side validation before submit
- [ ] Login flow:
  - Submit credentials to Clerk API
  - On success:
    - Store session token in cookie (httpOnly, secure)
    - Redirect to `/cms/properties` (or original destination if redirected from protected page)
  - On failure:
    - Show error message: "Invalid email or password"
    - Keep form filled (don't clear password)
- [ ] Logout:
  - "Logout" button in CMS navigation bar
  - Click logout:
    - Clear session cookie
    - Redirect to `/` (homepage)
    - Show success toast: "Logged out successfully"
- [ ] Session persistence:
  - If "Remember me" checked, session lasts 30 days
  - If not checked, session lasts 7 days
  - Session automatically renewed on activity
- [ ] Protected route redirect:
  - If user tries to access `/cms/*` without login, redirect to `/auth/login?redirect=/cms/...`
  - After login, redirect back to original destination

**Technical Details:**
```typescript
// Route: src/routes/auth/login/+page.svelte

<script>
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';

  let email = $state('');
  let password = $state('');
  let rememberMe = $state(false);
  let error = $state('');

  async function handleLogin(event: SubmitEvent) {
    event.preventDefault();

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, remember_me: rememberMe })
      });

      if (!response.ok) {
        const data = await response.json();
        error = data.error || 'Invalid email or password';
        return;
      }

      // Redirect to original destination or dashboard
      const redirectTo = $page.url.searchParams.get('redirect') || '/cms/properties';
      goto(redirectTo);
    } catch (err) {
      error = 'An error occurred. Please try again.';
    }
  }
</script>

<form onsubmit={handleLogin}>
  <input type="email" bind:value={email} required />
  <input type="password" bind:value={password} required minlength={8} />
  <label>
    <input type="checkbox" bind:checked={rememberMe} />
    Remember me
  </label>
  <button type="submit">Log In</button>
</form>
```

**API Endpoints:**
- `POST /api/auth/login` - Authenticate user with Clerk
  - Request body: `{ email: string, password: string, remember_me: boolean }`
  - Response: `{ success: true, session_token: string }`
  - Sets httpOnly cookie with session token
- `POST /api/auth/logout` - Clear session
  - Response: `{ success: true }`
  - Clears session cookie

**Clerk Integration:**
```python
# FastAPI backend
from clerk_backend_api import Clerk

clerk = Clerk(bearer_auth=CLERK_SECRET_KEY)

@app.post("/api/auth/login")
async def login(credentials: LoginRequest, response: Response):
    try:
        # Authenticate with Clerk
        session = clerk.client.sessions.create(
            email_address=credentials.email,
            password=credentials.password
        )

        # Set session cookie
        max_age = 30 * 24 * 60 * 60 if credentials.remember_me else 7 * 24 * 60 * 60
        response.set_cookie(
            key="session_token",
            value=session.id,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=max_age
        )

        return {"success": True, "session_token": session.id}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid email or password")
```

**Middleware (Protected Routes):**
```typescript
// src/hooks.server.ts

import { redirect } from '@sveltejs/kit';

export async function handle({ event, resolve }) {
  const sessionToken = event.cookies.get('session_token');

  // Verify session with Clerk
  if (sessionToken) {
    try {
      const user = await verifySession(sessionToken);
      event.locals.user = user;
    } catch {
      event.cookies.delete('session_token', { path: '/' });
    }
  }

  // Protect /cms routes
  if (event.url.pathname.startsWith('/cms')) {
    if (!event.locals.user) {
      throw redirect(303, `/auth/login?redirect=${event.url.pathname}`);
    }
  }

  return resolve(event);
}
```

**UI Components:**
- `LoginForm.svelte` - Login form
- `Button.svelte` - Submit button
- `Input.svelte` - Email/password inputs
- `Checkbox.svelte` - Remember me

**Design Reference:**
- Current NextJS: `app/auth/login/page.tsx`
- Components: `components/auth/LoginForm.tsx`

**Dependencies:**
- None (foundational)

**Estimated Effort:** 2 days

---

### US-013: User Registration

**User Story:**
> As a new agent, I want to sign up for an account so I can start managing properties.

**Acceptance Criteria:**
- [ ] Sign-up page displays at `/auth/sign-up` route
- [ ] Sign-up form:
  - Email input (required, validated)
  - Password input (required, min 8 characters)
  - Confirm password input (must match password)
  - "Sign Up" button
  - "Already have an account? Log in" link → `/auth/login`
- [ ] Form validation:
  - Email format validation
  - Password strength: min 8 chars, must include letter + number
  - Passwords match
  - Show inline errors
- [ ] Sign-up flow:
  - Submit to Clerk API
  - On success:
    - Send verification email
    - Redirect to `/auth/sign-up-success` page
    - Show message: "Please check your email to verify your account"
  - On failure:
    - Show error: "Email already exists" or "Sign up failed"
- [ ] Email verification:
  - User receives email with verification link
  - Click link → Verify email with Clerk
  - Redirect to `/auth/login` with success message
- [ ] Post-verification:
  - User can log in
  - User has agent role by default

**Technical Details:**
```typescript
// Route: src/routes/auth/sign-up/+page.svelte

let email = $state('');
let password = $state('');
let confirmPassword = $state('');
let error = $state('');

async function handleSignUp(event: SubmitEvent) {
  event.preventDefault();

  // Client-side validation
  if (password !== confirmPassword) {
    error = 'Passwords do not match';
    return;
  }

  if (password.length < 8) {
    error = 'Password must be at least 8 characters';
    return;
  }

  try {
    const response = await fetch('/api/auth/sign-up', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      const data = await response.json();
      error = data.error || 'Sign up failed';
      return;
    }

    // Redirect to success page
    goto('/auth/sign-up-success');
  } catch (err) {
    error = 'An error occurred. Please try again.';
  }
}
```

**API Endpoints:**
- `POST /api/auth/sign-up` - Create new user with Clerk
  - Request body: `{ email: string, password: string }`
  - Response: `{ success: true, user_id: string }`
  - Clerk sends verification email automatically

**Clerk Integration:**
```python
@app.post("/api/auth/sign-up")
async def sign_up(data: SignUpRequest):
    try:
        user = clerk.users.create(
            email_address=data.email,
            password=data.password,
            # Clerk sends verification email automatically
        )

        return {"success": True, "user_id": user.id}
    except Exception as e:
        if "email_exists" in str(e):
            raise HTTPException(status_code=400, detail="Email already exists")
        raise HTTPException(status_code=500, detail="Sign up failed")
```

**Design Reference:**
- Current NextJS: `app/auth/sign-up/page.tsx`

**Dependencies:**
- US-012 (Login page for navigation)

**Estimated Effort:** 1.5 days

---

### US-014: Password Reset

**User Story:**
> As an agent who forgot my password, I want to reset it so I can regain access to my account.

**Acceptance Criteria:**
- [ ] Forgot password page displays at `/auth/forgot-password` route
- [ ] Forgot password form:
  - Email input (required)
  - "Send Reset Link" button
  - "Remember your password? Log in" link → `/auth/login`
- [ ] Submit flow:
  - Send email to Clerk API
  - On success:
    - Show success message: "If an account exists with this email, you'll receive a password reset link"
    - Don't reveal if email exists (security)
  - On failure:
    - Show generic error: "An error occurred. Please try again."
- [ ] Password reset email:
  - Clerk sends email with reset link
  - Link contains token: `/auth/reset-password?token={token}`
- [ ] Reset password page displays at `/auth/reset-password` route
- [ ] Reset password form:
  - New password input (required, min 8 characters)
  - Confirm new password input (must match)
  - "Reset Password" button
- [ ] Submit new password:
  - Verify token with Clerk
  - Update password
  - On success:
    - Show success message
    - Redirect to `/auth/login` with message: "Password reset successfully. Please log in."
  - On failure:
    - Show error: "Reset link expired or invalid"

**Technical Details:**
```typescript
// Forgot password: src/routes/auth/forgot-password/+page.svelte

async function handleForgotPassword(event: SubmitEvent) {
  event.preventDefault();

  try {
    await fetch('/api/auth/forgot-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });

    // Always show success (don't reveal if email exists)
    success = true;
  } catch {
    error = 'An error occurred. Please try again.';
  }
}

// Reset password: src/routes/auth/reset-password/+page.svelte

let token = $derived($page.url.searchParams.get('token'));

async function handleResetPassword(event: SubmitEvent) {
  event.preventDefault();

  if (password !== confirmPassword) {
    error = 'Passwords do not match';
    return;
  }

  try {
    await fetch('/api/auth/reset-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, password })
    });

    goto('/auth/login?message=password_reset_success');
  } catch {
    error = 'Reset link expired or invalid';
  }
}
```

**API Endpoints:**
- `POST /api/auth/forgot-password` - Request password reset
  - Request body: `{ email: string }`
  - Response: `{ success: true }` (always, for security)
- `POST /api/auth/reset-password` - Reset password with token
  - Request body: `{ token: string, password: string }`
  - Response: `{ success: true }`

**Design Reference:**
- Current NextJS: `app/auth/forgot-password/page.tsx`

**Dependencies:**
- US-012 (Login page)

**Estimated Effort:** 1.5 days

---

### US-015: Protected Routes Middleware

**User Story:**
> As a system, I need to protect CMS routes so only authenticated agents can access them.

**Acceptance Criteria:**
- [ ] All routes under `/cms/*` require authentication
- [ ] Unauthenticated users redirected to `/auth/login?redirect={original_path}`
- [ ] After login, user redirected back to original destination
- [ ] Session verification:
  - Check for session cookie on every request
  - Verify session token with Clerk
  - If valid, attach user to request (`event.locals.user`)
  - If invalid, clear cookie and redirect to login
- [ ] Public routes (no auth required):
  - `/` (homepage)
  - `/listings/*`
  - `/p/*` (property details)
  - `/locations/*`
  - `/auth/*`
- [ ] Protected routes:
  - `/cms/*` (all CMS pages)
- [ ] API route protection:
  - `/api/v1/properties/cms/*` - Requires auth
  - `/api/v1/properties/public/*` - Public (no auth)
- [ ] Error handling:
  - 401 error if trying to access protected API without auth
  - 403 error if trying to access someone else's property

**Technical Details:**
```typescript
// src/hooks.server.ts

import { redirect } from '@sveltejs/kit';

export async function handle({ event, resolve }) {
  // Get session token from cookie
  const sessionToken = event.cookies.get('session_token');

  // Verify session with Clerk
  if (sessionToken) {
    try {
      const response = await fetch('https://api.clerk.com/v1/sessions/verify', {
        headers: {
          'Authorization': `Bearer ${CLERK_SECRET_KEY}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ session_id: sessionToken })
      });

      if (response.ok) {
        const session = await response.json();
        event.locals.session = session;
        event.locals.user = session.user;
      } else {
        // Invalid session, clear cookie
        event.cookies.delete('session_token', { path: '/' });
      }
    } catch (error) {
      // Error verifying session
      console.error('Session verification failed:', error);
      event.cookies.delete('session_token', { path: '/' });
    }
  }

  // Protect /cms routes
  if (event.url.pathname.startsWith('/cms')) {
    if (!event.locals.user) {
      throw redirect(303, `/auth/login?redirect=${encodeURIComponent(event.url.pathname)}`);
    }
  }

  return resolve(event);
}
```

**FastAPI Middleware:**
```python
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get session token from cookie or header
        session_token = request.cookies.get('session_token') or \
                       request.headers.get('Authorization', '').replace('Bearer ', '')

        # Verify with Clerk
        if session_token:
            try:
                user = await verify_session_with_clerk(session_token)
                request.state.user = user
            except Exception:
                pass

        # Protect /api/v1/properties/cms/* routes
        if request.url.path.startswith('/api/v1/properties/cms/'):
            if not hasattr(request.state, 'user'):
                raise HTTPException(status_code=401, detail="Unauthorized")

        response = await call_next(request)
        return response

app.add_middleware(AuthMiddleware)
```

**Design Reference:**
- Current NextJS: `middleware.ts`

**Dependencies:**
- US-012 (Login/logout)

**Estimated Effort:** 1 day

---

### US-016: Migrate Property Schema to Subdomain Model

**User Story:**
> As a system, I need to migrate the property data model from a monolithic table to a subdomain-based architecture.

**Acceptance Criteria:**
- [ ] New database schema:
  - Core `properties` table with shared fields
  - Subdomain tables: `rental_details`, `sale_details`, `lease_details`, `business_details`, `investment_details`
  - Catalogue tables for amenities, location advantages, etc.
  - Many-to-many junction tables for catalogues
- [ ] Migration script:
  - Alembic migration to create new tables
  - Data migration script to transform old data to new schema
  - Preserve all existing property data (no data loss)
  - Map old property types to new subdomain tables
- [ ] New schema supports:
  - Multiple property types per property (e.g., villa for both sale and rent)
  - Flexible amenities (catalogues)
  - Location metadata (region, area, district, coordinates)
  - Price information per transaction type
  - Physical specs (bedrooms, bathrooms, living area, land area)
- [ ] Backward compatibility:
  - Old API endpoints still work (deprecated but functional)
  - New API endpoints use new schema
  - Frontend uses new API endpoints only
- [ ] Validation:
  - All existing properties migrated successfully
  - No broken references or data corruption
  - Property counts match before/after migration

**Technical Details:**

**Core Properties Table:**
```sql
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_type VARCHAR(50) NOT NULL,  -- 'rental', 'sale', 'lease', 'business', 'investment'
    title VARCHAR(200),
    description TEXT,

    -- Location
    location_address TEXT,
    location_province VARCHAR(100),
    location_district VARCHAR(100),
    location_coordinates JSONB,  -- {lat, lng}

    -- Physical specs
    bedrooms SMALLINT,
    bathrooms NUMERIC(3,1),
    living_area_sqm NUMERIC(10,2),
    land_area_sqm NUMERIC(10,2),

    -- Images
    cover_image_url TEXT,
    images JSONB,  -- [{url, alt}]

    -- Flexible attributes
    additional_attributes JSONB DEFAULT '{}',

    -- Metadata
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ,
    is_published BOOLEAN DEFAULT FALSE,

    CONSTRAINT valid_property_type CHECK (property_type IN ('rental', 'sale', 'lease', 'business', 'investment'))
);

-- Subdomain tables
CREATE TABLE rental_details (
    property_id UUID PRIMARY KEY REFERENCES properties(id) ON DELETE CASCADE,
    rental_period VARCHAR(20),  -- 'daily', 'monthly', 'yearly'
    price_per_period NUMERIC(12,2),
    currency VARCHAR(3) DEFAULT 'THB',
    deposit_amount NUMERIC(12,2),
    minimum_stay_days INTEGER,
    utilities_included BOOLEAN
);

CREATE TABLE sale_details (
    property_id UUID PRIMARY KEY REFERENCES properties(id) ON DELETE CASCADE,
    sale_price NUMERIC(14,2),
    currency VARCHAR(3) DEFAULT 'THB',
    ownership_type VARCHAR(50),  -- 'freehold', 'leasehold'
    transfer_fees VARCHAR(100)
);

CREATE TABLE lease_details (
    property_id UUID PRIMARY KEY REFERENCES properties(id) ON DELETE CASCADE,
    lease_term_years INTEGER,
    lease_price_per_year NUMERIC(12,2),
    currency VARCHAR(3) DEFAULT 'THB',
    renewable BOOLEAN
);

CREATE TABLE business_details (
    property_id UUID PRIMARY KEY REFERENCES properties(id) ON DELETE CASCADE,
    business_type VARCHAR(100),
    asking_price NUMERIC(14,2),
    currency VARCHAR(3) DEFAULT 'THB',
    revenue_per_year NUMERIC(14,2),
    established_year INTEGER
);

CREATE TABLE investment_details (
    property_id UUID PRIMARY KEY REFERENCES properties(id) ON DELETE CASCADE,
    investment_type VARCHAR(100),
    minimum_investment NUMERIC(14,2),
    expected_roi_percent NUMERIC(5,2),
    investment_term_years INTEGER
);

-- Catalogues
CREATE TABLE catalogues (
    id VARCHAR(50) PRIMARY KEY,
    name_en VARCHAR(100),
    name_th VARCHAR(100),
    description TEXT,
    icon VARCHAR(50),
    sort_order INTEGER
);

CREATE TABLE catalogue_options (
    id VARCHAR(50) PRIMARY KEY,
    catalogue_id VARCHAR(50) REFERENCES catalogues(id),
    name_en VARCHAR(100),
    name_th VARCHAR(100),
    icon VARCHAR(50),
    sort_order INTEGER
);

-- Many-to-many junction
CREATE TABLE property_catalogue_options (
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    option_id VARCHAR(50) REFERENCES catalogue_options(id),
    PRIMARY KEY (property_id, option_id)
);
```

**Migration Script:**
```python
# alembic migration

def upgrade():
    # 1. Create new tables
    # ... (see schema above)

    # 2. Migrate data from old bestays_properties table
    conn = op.get_bind()

    # Fetch old properties
    old_properties = conn.execute("""
        SELECT * FROM bestays_properties WHERE deleted_at IS NULL
    """).fetchall()

    for old_prop in old_properties:
        # Determine property type (map old to new)
        new_type = map_old_type_to_new(old_prop['property_type'], old_prop['transaction_type'])

        # Insert into core properties table
        property_id = conn.execute("""
            INSERT INTO properties (
                id, property_type, title, description,
                location_address, bedrooms, bathrooms,
                cover_image_url, images,
                created_by, created_at, updated_at, is_published
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id
        """, (
            old_prop['id'], new_type, old_prop['title'], old_prop['text'],
            json.dumps(old_prop['location']), old_prop.get('bedrooms'),
            old_prop.get('bathrooms'), old_prop['cover_image'],
            json.dumps(old_prop['images']), old_prop['created_by'],
            old_prop['created_at'], old_prop['updated_at'], old_prop['is_published']
        )).fetchone()[0]

        # Insert into subdomain table
        if new_type == 'sale':
            conn.execute("""
                INSERT INTO sale_details (property_id, sale_price, currency)
                VALUES (%s, %s, %s)
            """, (property_id, old_prop['price'], 'THB'))
        elif new_type == 'rental':
            conn.execute("""
                INSERT INTO rental_details (property_id, price_per_period, currency, rental_period)
                VALUES (%s, %s, %s, %s)
            """, (property_id, old_prop['price'], 'THB', 'monthly'))
        # ... handle other types

    # 3. Create indexes
    op.create_index('idx_properties_type', 'properties', ['property_type'])
    op.create_index('idx_properties_published', 'properties', ['is_published'])

    # 4. Drop old table (after verification)
    # op.drop_table('bestays_properties')  # Keep for now, drop later

def downgrade():
    # Reverse migration if needed
    pass
```

**Mapping Old to New:**
```python
def map_old_type_to_new(old_property_type: str, old_transaction_type: str) -> str:
    """
    Map old monolithic types to new subdomain types

    Old property_type: land, house, villa, pool-villa, apartment, condo, etc.
    Old transaction_type: sale, rent, lease, sale-lease

    New property_type: rental, sale, lease, business, investment
    """
    if old_transaction_type in ('rent', 'sale-lease'):
        return 'rental'
    elif old_transaction_type == 'sale':
        if old_property_type == 'business':
            return 'business'
        else:
            return 'sale'
    elif old_transaction_type == 'lease':
        return 'lease'
    else:
        return 'sale'  # Default
```

**Design Reference:**
- Schema: `.sdlc-workflow/.specs/04_PROPERTY_MODERNIZATION_PLAN.md`
- Old schema: `/Users/solo/Projects/_repos/react-workspace/src/apps/bestays-web/db/sql/1.properties.sql`

**Dependencies:**
- None (backend infrastructure)

**Estimated Effort:** 4 days

---

### US-017: Create FastAPI Endpoints for Properties

**User Story:**
> As a system, I need RESTful API endpoints to manage properties.

**Acceptance Criteria:**
- [ ] Public endpoints (no auth):
  - `GET /api/v1/properties/public` - List published properties with filters
  - `GET /api/v1/properties/public/{id}` - Get property details
  - `GET /api/v1/properties/public/related` - Get related properties
- [ ] CMS endpoints (auth required):
  - `GET /api/v1/properties/cms` - List agent's properties
  - `GET /api/v1/properties/cms/{id}` - Get property for editing
  - `POST /api/v1/properties` - Create new property
  - `PATCH /api/v1/properties/{id}` - Update property
  - `PATCH /api/v1/properties/{id}/publish` - Toggle publish status
  - `DELETE /api/v1/properties/{id}` - Soft delete property
  - `POST /api/v1/properties/{id}/restore` - Restore deleted property
- [ ] Location endpoints:
  - `GET /api/v1/locations/regions` - List all regions
  - `GET /api/v1/locations/regions/{region}/areas` - List areas in region
  - `GET /api/v1/locations/top` - Get top N locations
- [ ] Catalogue endpoints:
  - `GET /api/v1/catalogues` - List all catalogues
  - `GET /api/v1/catalogues/{catalogue_id}/options` - List options in catalogue
  - `GET /api/v1/catalogues/title-deeds` - List title deed options
- [ ] All endpoints return JSON
- [ ] Consistent error responses:
  - 400: Bad request (validation error)
  - 401: Unauthorized (not logged in)
  - 403: Forbidden (not owner)
  - 404: Not found
  - 500: Internal server error
- [ ] Pagination support for list endpoints:
  - Query params: `limit`, `offset`, `page`
  - Response includes: `data`, `total`, `page`, `limit`
- [ ] Filtering support:
  - `property_types[]` - Filter by property type (can be multiple)
  - `transaction_types[]` - Filter by transaction type
  - `location_region` - Filter by region
  - `location_area` - Filter by area
  - `is_published` - Filter by publish status (CMS only)
- [ ] Sorting support:
  - Query param: `sort_by` (e.g., `updated_at`, `price`, `title`)
  - Query param: `sort_order` (asc/desc)
  - Default: `updated_at desc`

**Technical Details:**

**FastAPI App Structure:**
```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Bestays API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5183"],  # SvelteKit dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from app.routers import properties, locations, catalogues
app.include_router(properties.router, prefix="/api/v1/properties", tags=["properties"])
app.include_router(locations.router, prefix="/api/v1/locations", tags=["locations"])
app.include_router(catalogues.router, prefix="/api/v1/catalogues", tags=["catalogues"])
```

**Property Router:**
```python
# app/routers/properties.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

router = APIRouter()

# Public endpoints
@router.get("/public", response_model=PropertyListResponse)
async def list_public_properties(
    property_types: Optional[List[str]] = Query(None),
    transaction_types: Optional[List[str]] = Query(None),
    location_region: Optional[str] = None,
    location_area: Optional[str] = None,
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("updated_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db)
):
    """
    List published properties with filters
    """
    query = db.query(Property).filter(
        Property.is_published == True,
        Property.deleted_at.is_(None)
    )

    # Apply filters
    if property_types:
        query = query.filter(Property.property_type.in_(property_types))
    if location_region:
        query = query.filter(Property.location_province == location_region)
    if location_area:
        query = query.filter(Property.location_district == location_area)

    # Count total
    total = query.count()

    # Apply sorting
    if sort_order == "desc":
        query = query.order_by(desc(getattr(Property, sort_by)))
    else:
        query = query.order_by(asc(getattr(Property, sort_by)))

    # Apply pagination
    properties = query.offset(offset).limit(limit).all()

    return PropertyListResponse(
        data=properties,
        total=total,
        limit=limit,
        offset=offset
    )

@router.get("/public/{property_id}", response_model=PropertyDetailResponse)
async def get_public_property(
    property_id: str,
    db: Session = Depends(get_db)
):
    """
    Get property details (public)
    """
    property = db.query(Property).filter(
        Property.id == property_id,
        Property.is_published == True,
        Property.deleted_at.is_(None)
    ).first()

    if not property:
        raise HTTPException(status_code=404, detail="Property not found")

    return property

# CMS endpoints (require auth)
@router.get("/cms", response_model=PropertyListResponse)
async def list_cms_properties(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List agent's properties (CMS)
    """
    properties = db.query(Property).filter(
        Property.created_by == user.id
    ).order_by(desc(Property.updated_at)).all()

    return PropertyListResponse(data=properties, total=len(properties))

@router.post("", response_model=PropertyResponse)
async def create_property(
    data: PropertyCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new property
    """
    property = Property(
        created_by=user.id,
        is_published=False
    )
    db.add(property)
    db.commit()
    db.refresh(property)

    return property

@router.patch("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: str,
    data: PropertyUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update property
    """
    property = db.query(Property).filter(Property.id == property_id).first()

    if not property:
        raise HTTPException(status_code=404, detail="Property not found")

    if property.created_by != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Update fields
    for key, value in data.dict(exclude_unset=True).items():
        setattr(property, key, value)

    property.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(property)

    return property

@router.delete("/{property_id}")
async def delete_property(
    property_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete property
    """
    property = db.query(Property).filter(Property.id == property_id).first()

    if not property:
        raise HTTPException(status_code=404, detail="Property not found")

    if property.created_by != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    property.deleted_at = datetime.utcnow()
    db.commit()

    return {"success": True}
```

**Pydantic Schemas:**
```python
# app/schemas/property.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PropertyBase(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    property_type: str
    location_province: Optional[str]
    location_district: Optional[str]
    bedrooms: Optional[int] = Field(None, ge=0, le=20)
    bathrooms: Optional[float] = Field(None, ge=0, le=10)
    living_area_sqm: Optional[float] = Field(None, ge=0)
    land_area_sqm: Optional[float] = Field(None, ge=0)

class PropertyCreateRequest(PropertyBase):
    pass

class PropertyUpdateRequest(PropertyBase):
    pass

class PropertyResponse(PropertyBase):
    id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    is_published: bool
    deleted_at: Optional[datetime]

    class Config:
        from_attributes = True

class PropertyListResponse(BaseModel):
    data: List[PropertyResponse]
    total: int
    limit: Optional[int] = 20
    offset: Optional[int] = 0
```

**Design Reference:**
- Current NextJS: `entities/properties/libs/property_requests.ts`

**Dependencies:**
- US-016 (Database schema)

**Estimated Effort:** 4 days

---

### US-018: Image Upload to Cloudflare R2

**User Story:**
> As a system, I need to upload property images to Cloudflare R2 for storage.

**Acceptance Criteria:**
- [ ] Image upload endpoint:
  - `POST /api/v1/images/upload` - Upload single image
  - Accepts `multipart/form-data` with file
  - Returns `{ url: string, path: string }`
- [ ] Image delete endpoint:
  - `DELETE /api/v1/images/{path}` - Delete image from R2
  - Returns `{ success: true }`
- [ ] File validation:
  - Supported formats: JPG, PNG, WebP
  - Max file size: 10MB
  - Reject other formats with 400 error
- [ ] Image processing:
  - No server-side resizing (handle client-side or CDN)
  - Generate unique filename: `{uuid}-{original_filename}`
  - Store in R2 bucket: `bestays-images/properties/{filename}`
- [ ] Public URL:
  - Images accessible via: `https://images.bestays.com/{path}`
  - Configure R2 custom domain
- [ ] Error handling:
  - 400: Invalid file format or size
  - 500: Upload failed

**Technical Details:**

**FastAPI Endpoint:**
```python
# app/routers/images.py
from fastapi import APIRouter, UploadFile, File, HTTPException
import boto3
import uuid
from pathlib import Path

router = APIRouter()

# Configure R2 client
s3_client = boto3.client(
    's3',
    endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY,
    region_name='auto'
)

BUCKET_NAME = 'bestays-images'
PUBLIC_URL_BASE = 'https://images.bestays.com'

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload image to Cloudflare R2
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read file
    contents = await file.read()

    # Validate file size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: 10MB"
        )

    # Generate unique filename
    unique_id = uuid.uuid4().hex[:8]
    filename = f"{unique_id}-{file.filename}"
    path = f"properties/{filename}"

    try:
        # Upload to R2
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=path,
            Body=contents,
            ContentType=file.content_type,
            ACL='public-read'  # Make publicly accessible
        )

        # Return public URL
        url = f"{PUBLIC_URL_BASE}/{path}"

        return {"url": url, "path": path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.delete("/{path:path}")
async def delete_image(path: str):
    """
    Delete image from Cloudflare R2
    """
    try:
        s3_client.delete_object(
            Bucket=BUCKET_NAME,
            Key=path
        )

        return {"success": True}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
```

**Environment Variables:**
```bash
# .env
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY=your_access_key
R2_SECRET_KEY=your_secret_key
R2_BUCKET_NAME=bestays-images
R2_PUBLIC_URL=https://images.bestays.com
```

**Cloudflare R2 Setup:**
1. Create R2 bucket: `bestays-images`
2. Enable public access
3. Configure custom domain: `images.bestays.com`
4. Generate API tokens (access key + secret)

**Design Reference:**
- Current NextJS: `entities/image/libs/client-upload.ts`

**Dependencies:**
- US-017 (FastAPI app structure)

**Estimated Effort:** 2 days

---

### US-019: Set Up Clerk Authentication

**User Story:**
> As a system, I need Clerk authentication integrated with the backend.

**Acceptance Criteria:**
- [ ] Clerk account created and configured
- [ ] Clerk API keys added to environment variables
- [ ] Backend Clerk SDK installed and configured
- [ ] Session verification function implemented
- [ ] User creation on sign-up
- [ ] Email verification flow working
- [ ] Password reset flow working
- [ ] Session management (cookies)
- [ ] Middleware for protected routes

**Technical Details:**

**Install Clerk SDK:**
```bash
pip install clerk-backend-api
```

**Configure Clerk:**
```python
# app/config.py
from clerk_backend_api import Clerk

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY")

clerk = Clerk(bearer_auth=CLERK_SECRET_KEY)
```

**Auth Utilities:**
```python
# app/auth.py
from fastapi import HTTPException, Request
from clerk_backend_api import Clerk

clerk = Clerk(bearer_auth=CLERK_SECRET_KEY)

async def verify_session(session_token: str):
    """
    Verify session token with Clerk
    Returns user object if valid, raises exception if invalid
    """
    try:
        session = clerk.sessions.verify_token(session_token)
        user = clerk.users.get(session.user_id)
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid session")

async def get_current_user(request: Request):
    """
    FastAPI dependency to get current user from session cookie
    """
    session_token = request.cookies.get('session_token')

    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = await verify_session(session_token)
    return user
```

**Auth Endpoints:**
```python
# app/routers/auth.py
from fastapi import APIRouter, HTTPException, Response
from clerk_backend_api import Clerk

router = APIRouter()

clerk = Clerk(bearer_auth=CLERK_SECRET_KEY)

@router.post("/login")
async def login(data: LoginRequest, response: Response):
    """
    Authenticate user with Clerk
    """
    try:
        # Create session with Clerk
        session = clerk.client.sign_in.create(
            identifier=data.email,
            password=data.password
        )

        # Set session cookie
        max_age = 30 * 24 * 60 * 60 if data.remember_me else 7 * 24 * 60 * 60
        response.set_cookie(
            key="session_token",
            value=session.id,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=max_age
        )

        return {"success": True, "session_token": session.id}

    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid email or password")

@router.post("/sign-up")
async def sign_up(data: SignUpRequest):
    """
    Create new user with Clerk
    """
    try:
        user = clerk.users.create(
            email_address=[data.email],
            password=data.password
        )

        # Clerk automatically sends verification email

        return {"success": True, "user_id": user.id}

    except Exception as e:
        if "email_address_exists" in str(e):
            raise HTTPException(status_code=400, detail="Email already exists")
        raise HTTPException(status_code=500, detail="Sign up failed")

@router.post("/logout")
async def logout(response: Response):
    """
    Clear session cookie
    """
    response.delete_cookie(key="session_token")
    return {"success": True}

@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest):
    """
    Send password reset email via Clerk
    """
    try:
        # Clerk handles sending email
        clerk.users.send_password_reset_email(
            email_address=data.email
        )

        # Always return success (don't reveal if email exists)
        return {"success": True}

    except:
        # Return success even on error (security)
        return {"success": True}

@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest):
    """
    Reset password with token
    """
    try:
        clerk.client.sign_in.reset_password(
            token=data.token,
            password=data.password
        )

        return {"success": True}

    except Exception as e:
        raise HTTPException(status_code=400, detail="Reset link expired or invalid")
```

**Environment Variables:**
```bash
# .env
CLERK_SECRET_KEY=sk_test_...
CLERK_PUBLISHABLE_KEY=pk_test_...
```

**Design Reference:**
- Current NextJS: Uses Supabase Auth, migrate to Clerk

**Dependencies:**
- None (foundational)

**Estimated Effort:** 2 days

---

### US-020: Location & Catalogue API Endpoints

**User Story:**
> As a system, I need API endpoints for locations and catalogues.

**Acceptance Criteria:**
- [ ] Location endpoints:
  - `GET /api/v1/locations/regions` - List all regions
  - `GET /api/v1/locations/regions/{region}/areas` - List areas in region
  - `GET /api/v1/locations/top?limit=12` - Get top N locations (most properties)
- [ ] Catalogue endpoints:
  - `GET /api/v1/catalogues` - List all catalogues
  - `GET /api/v1/catalogues/{catalogue_id}/options` - List options in catalogue
  - `GET /api/v1/catalogues/title-deeds` - List title deed options (for dropdown)
- [ ] All endpoints return JSON
- [ ] Locations cached (Redis, 1 hour TTL)
- [ ] Catalogues cached (Redis, 24 hour TTL)
- [ ] Response format:
  ```json
  {
    "regions": ["Bangkok", "Phuket", ...],
    "areas_by_region": {
      "Phuket": ["Patong", "Rawai", "Kamala", ...]
    }
  }
  ```

**Technical Details:**

**Location Router:**
```python
# app/routers/locations.py
from fastapi import APIRouter, Depends
from sqlalchemy import func
from app.cache import cache

router = APIRouter()

@router.get("/regions")
@cache(expire=3600)  # Cache for 1 hour
async def list_regions(db: Session = Depends(get_db)):
    """
    List all regions (provinces) from properties
    """
    regions = db.query(Property.location_province)\
        .filter(Property.location_province.isnot(None))\
        .distinct()\
        .order_by(Property.location_province)\
        .all()

    return {"regions": [r[0] for r in regions]}

@router.get("/regions/{region}/areas")
@cache(expire=3600)
async def list_areas(region: str, db: Session = Depends(get_db)):
    """
    List all areas (districts) in a region
    """
    areas = db.query(Property.location_district)\
        .filter(
            Property.location_province == region,
            Property.location_district.isnot(None)
        )\
        .distinct()\
        .order_by(Property.location_district)\
        .all()

    return {"areas": [a[0] for a in areas]}

@router.get("/top")
@cache(expire=3600)
async def top_locations(limit: int = 12, db: Session = Depends(get_db)):
    """
    Get top N locations by property count
    """
    top_regions = db.query(
        Property.location_province,
        func.count(Property.id).label('count')
    )\
    .filter(Property.is_published == True)\
    .group_by(Property.location_province)\
    .order_by(func.count(Property.id).desc())\
    .limit(limit)\
    .all()

    return {
        "top_regions": [
            {"region": r[0], "count": r[1]}
            for r in top_regions
        ]
    }

@router.get("")
@cache(expire=3600)
async def all_locations(db: Session = Depends(get_db)):
    """
    Get all regions and areas (hierarchical)
    """
    # Get all locations
    locations = db.query(
        Property.location_province,
        Property.location_district
    )\
    .filter(
        Property.location_province.isnot(None),
        Property.location_district.isnot(None)
    )\
    .distinct()\
    .all()

    # Group by region
    regions = set()
    areas_by_region = {}

    for province, district in locations:
        regions.add(province)
        if province not in areas_by_region:
            areas_by_region[province] = set()
        areas_by_region[province].add(district)

    # Convert to sorted lists
    return {
        "regions": sorted(list(regions)),
        "areas_by_region": {
            region: sorted(list(areas))
            for region, areas in areas_by_region.items()
        }
    }
```

**Catalogue Router:**
```python
# app/routers/catalogues.py
from fastapi import APIRouter, Depends
from app.cache import cache

router = APIRouter()

@router.get("")
@cache(expire=86400)  # Cache for 24 hours
async def list_catalogues(db: Session = Depends(get_db)):
    """
    List all catalogues
    """
    catalogues = db.query(Catalogue)\
        .order_by(Catalogue.sort_order)\
        .all()

    return {"catalogues": catalogues}

@router.get("/{catalogue_id}/options")
@cache(expire=86400)
async def list_options(catalogue_id: str, db: Session = Depends(get_db)):
    """
    List options in a catalogue
    """
    options = db.query(CatalogueOption)\
        .filter(CatalogueOption.catalogue_id == catalogue_id)\
        .order_by(CatalogueOption.sort_order)\
        .all()

    return {"options": options}

@router.get("/title-deeds")
@cache(expire=86400)
async def list_title_deeds(db: Session = Depends(get_db)):
    """
    List all unique title deeds (for dropdown)
    """
    # Assuming title deeds are stored in a catalogue
    options = db.query(CatalogueOption)\
        .filter(CatalogueOption.catalogue_id == 'title_deeds')\
        .order_by(CatalogueOption.name_en)\
        .all()

    return {"title_deeds": [opt.name_en for opt in options]}
```

**Redis Caching:**
```python
# app/cache.py
import redis
import json
from functools import wraps

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

def cache(expire: int = 3600):
    """
    Cache decorator for FastAPI routes
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Check cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Call function
            result = await func(*args, **kwargs)

            # Store in cache
            redis_client.setex(
                cache_key,
                expire,
                json.dumps(result)
            )

            return result

        return wrapper
    return decorator
```

**Design Reference:**
- Current NextJS: `entities/properties/libs/locations.ts`

**Dependencies:**
- US-016 (Database schema)
- US-017 (FastAPI app)

**Estimated Effort:** 2 days

---

## Implementation Timeline

### Week 1-2: Backend Infrastructure
- US-016: Migrate property schema (4 days)
- US-017: Create FastAPI endpoints (4 days)
- US-019: Set up Clerk authentication (2 days)

### Week 3: Image & Locations
- US-018: Image upload to R2 (2 days)
- US-020: Location & catalogue endpoints (2 days)
- Buffer (1 day)

### Week 4-5: Authentication & Protected Routes
- US-012: Login/logout (2 days)
- US-013: User registration (1.5 days)
- US-014: Password reset (1.5 days)
- US-015: Protected routes middleware (1 day)
- Buffer (1 day)

### Week 6-7: Guest Pages (Frontend)
- US-002: Homepage (3 days)
- US-003: Property listings (2 days)
- US-004: Property details (4 days)
- US-005: Location-based listings (2 days)
- Buffer (1 day)

### Week 8-9: Agent Dashboard (Frontend)
- US-006: Property list table (3 days)
- US-007: Create property (0.5 days)
- US-008: Edit property form (5 days)
- US-010: Publish/unpublish (1 day)
- US-011: Delete properties (1 day)
- Buffer (1 day)

### Week 10: Image Upload (Frontend)
- US-009: Image upload component (4 days)
- Integration testing (1 day)

### Week 11-12: Testing & Polish
- End-to-end testing (3 days)
- Bug fixes (3 days)
- Performance optimization (2 days)
- Documentation (2 days)

**Total Estimated Duration:** 12 weeks

---

## Dependencies Graph

```
US-016 (Database schema)
  ├─> US-017 (FastAPI endpoints)
  │     ├─> US-018 (Image upload)
  │     └─> US-020 (Locations/catalogues)
  └─> US-019 (Clerk auth)
        ├─> US-012 (Login/logout)
        │     ├─> US-013 (Registration)
        │     ├─> US-014 (Password reset)
        │     └─> US-015 (Protected routes)
        │           └─> US-006 (Property list)
        │                 ├─> US-007 (Create property)
        │                 └─> US-008 (Edit property)
        │                       ├─> US-009 (Image upload UI)
        │                       ├─> US-010 (Publish/unpublish)
        │                       └─> US-011 (Delete)
        └─> US-002 (Homepage)
              ├─> US-003 (Listings)
              ├─> US-004 (Details)
              └─> US-005 (Location pages)

Critical Path: US-016 → US-017 → US-019 → US-012 → US-015 → US-006 → US-008 → US-009
```

---

## Success Criteria

- [ ] All guest pages functional (homepage, listings, details, locations)
- [ ] All agent dashboard pages functional (property list, edit form)
- [ ] Authentication working (login, logout, registration, password reset)
- [ ] Image upload working (drag & drop, reorder, delete)
- [ ] Database migration successful (all old data preserved)
- [ ] API endpoints documented (OpenAPI/Swagger)
- [ ] E2E tests passing (critical flows)
- [ ] Performance:
  - Homepage loads in < 2 seconds
  - Property detail page loads in < 1.5 seconds
  - Image upload completes in < 3 seconds per image
- [ ] Mobile responsive (all pages work on mobile)
- [ ] No data loss (all existing properties migrated)
- [ ] Feature parity with old NextJS site (100% functionality replicated)

---

## Risks & Mitigation

| **Risk**                          | **Likelihood** | **Impact** | **Mitigation**                                     |
| --------------------------------- | -------------- | ---------- | -------------------------------------------------- |
| Database migration data loss      | Low            | Critical   | Test migration on staging, backup production DB    |
| Clerk integration issues          | Medium         | High       | Use Clerk documentation, test early                |
| Cloudflare R2 upload failures     | Low            | Medium     | Implement retry logic, error handling              |
| Frontend complexity (Svelte 5)    | Medium         | Medium     | Follow Svelte 5 docs, use community resources      |
| Image upload performance          | Medium         | Medium     | Client-side compression, parallel uploads          |
| Timeline underestimation          | High           | Medium     | Add 20% buffer time, prioritize critical features  |
| Third-party API downtime (Clerk)  | Low            | High       | Implement fallback, graceful degradation           |

---

## Out of Scope (Future Milestones)

- Chat-as-CMS for property creation (postponed, see `property-chat-cms/` specs)
- Three.js homepage effects (removed)
- Advanced search (filters, autocomplete)
- Property favorites/bookmarks
- Email notifications (contact forms, inquiries)
- Analytics dashboard
- SEO optimizations (sitemap, structured data)
- Multi-language support (Thai/English)
- Dynamic property types (see `04_DYNAMIC_SCHEMA_ARCHITECTURE_ANALYSIS.md`)

---

## References

- **Old NextJS Codebase:** `/Users/solo/Projects/_repos/react-workspace/src/apps/bestays-web`
- **Codebase Analysis Report:** (Explore agent output from this session)
- **Property Modernization Plan:** `.sdlc-workflow/.specs/04_PROPERTY_MODERNIZATION_PLAN.md`
- **Tech Stack:** `CLAUDE.md` (project root)
- **SDLC Workflow:** `.sdlc-workflow/.plan/03-workflow-diagrams.md`

---

**Document Status:** ✅ Planning Complete - Ready for User Story Implementation
**Last Updated:** 2025-11-06
**Next Steps:**
1. Review and approve milestone plan
2. Create individual user story files in `.sdlc-workflow/user-stories/`
3. Set up project board (GitHub Projects or similar)
4. Begin Sprint 1 (Backend infrastructure)

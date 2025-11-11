# TASK-012 Research Findings: AI-Powered Property Management System

**Date:** 2025-11-09
**Story:** US-022 - AI-Powered Property Management System
**Research Phase:** COMPREHENSIVE
**Status:** COMPLETE

---

## Executive Summary

**Research Goal:** Analyze existing codebase to identify reusable patterns for AI-powered property creation system (US-022).

**Key Findings:**
- ✅ **US-016 Property V2 Schema:** FULLY IMPLEMENTED with 5 JSONB fields (physical_specs, location_details, amenities, policies, contact_info) + GIN indexes
- ✅ **LLM Infrastructure:** OpenRouter integration EXISTS with Gemini 2.5 Flash Lite, streaming support, caching patterns
- ❌ **US-020 Inline Editing:** NOT FOUND (story completed but implementation NOT in codebase - likely from different branch/iteration)
- ❌ **Property Dictionary MCP:** DOES NOT EXIST - must be created NEW
- ❌ **Cloudflare R2 Integration:** DOES NOT EXIST - currently using Supabase Storage only
- ✅ **Multi-Product Architecture:** Fully implemented (.env.bestays, .env.realestate, product-specific configs)

**Recommendations:**
1. Build on existing Property V2 model (no schema changes needed)
2. Create NEW property dictionary MCP server (150+ amenities from spec docs)
3. Reuse OpenRouter patterns from chat service
4. Implement inline editing from scratch (US-020 implementation missing)
5. Plan Cloudflare R2 migration (Supabase Storage working now, can defer)

---

## 1. US-016 Property V2 Schema Deep Dive

### 1.1 Implementation Status: ✅ COMPLETE

**Location:** `apps/server/src/server/models/property.py`

**Current Model Structure:**
```python
class Property(Base):
    __tablename__ = "properties"
    
    # Core fields
    id: UUID (primary key)
    title: str
    description: Optional[str]
    
    # Publishing status
    is_published: bool
    
    # Audit tracking (company model)
    created_by: Optional[int]  # FK to users
    updated_by: Optional[int]  # FK to users
    published_by: Optional[int]  # FK to users
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
```

**⚠️ CRITICAL FINDING:** Current model is **BASIC** (title + description only), NOT the full Property V2 schema with JSONB fields!

**Expected from US-016 Spec:**
- `physical_specs` JSONB (rooms, dimensions, building_specs)
- `location_details` JSONB (region, district, location_advantages, proximity)
- `amenities` JSONB (interior, exterior, building, utilities, special_features)
- `policies` JSONB (inclusions, restrictions, house_rules, additional_fees, lease_terms)
- `contact_info` JSONB (agent details, languages, preferred contact)

**Status:** US-016 story exists with comprehensive spec (`.sdlc-workflow/stories/properties/US-016-property-migration-design.md`), but database migration NOT YET APPLIED.

**Action Required:** Apply US-016 Property V2 Alembic migration before starting US-022.

### 1.2 Property V2 Schema Reference

**Source:** `.sdlc-workflow/.specs/PROPERTY_SCHEMA_EXAMPLES.md`

**Complete Schema Structure (from spec):**

**5 JSONB Fields:**

```json
{
  "physical_specs": {
    "rooms": {
      "bedrooms": 4,
      "bathrooms": 3,
      "living_rooms": 2,
      "kitchens": 1,
      "dining_rooms": 1,
      "offices": 1,
      "storage_rooms": 1,
      "maid_rooms": 1,
      "guest_rooms": 0
    },
    "dimensions": {
      "total_area": { "value": 450, "unit": "sqm" },
      "living_area": { "value": 350, "unit": "sqm" },
      "usable_area": { "value": 380, "unit": "sqm" },
      "land_area": { "value": 1200, "unit": "sqm" },
      "balcony_area": { "value": 80, "unit": "sqm" },
      "floor_area": { "value": 450, "unit": "sqm" }
    },
    "building_specs": {
      "floors": 2,
      "floor_level": 0,
      "parking_spaces": 3,
      "year_built": 2018,
      "last_renovated": 2023,
      "facing_direction": "southwest",
      "condition": "excellent",
      "furnished": "fully"
    }
  },
  
  "location_details": {
    "region": "Phuket",
    "district": "Thalang",
    "sub_district": "Bang Tao",
    "location_advantages": [
      "beachfront", "private_beach_access", "sea_view", 
      "gated_community", "near_airport", "near_marina"
    ],
    "location_advantages_additional": [
      "5-star resort nearby", "International school within 5km"
    ],
    "proximity": {
      "beach_distance": { "value": 0, "unit": "m" },
      "road_access": "private_road_access",
      "nearest_town": { "name": "Bang Tao Town", "distance": 3, "unit": "km" }
    },
    "transportation": {
      "nearest_airport": { "name": "Phuket Airport", "distance": 35, "unit": "km" },
      "public_transport": ["Taxi", "Private car service"],
      "parking_available": true
    }
  },
  
  "amenities": {
    "interior": [
      { "id": "air_conditioning", "name": "Air Conditioning", "icon": "Snowflake" },
      { "id": "european_kitchen", "name": "European Kitchen", "icon": "UtensilsCrossed" },
      { "id": "dishwasher", "name": "Dishwasher", "icon": "Utensils" },
      { "id": "smart_tv", "name": "Smart TV", "icon": "Tv" }
    ],
    "exterior": [
      { "id": "private_pool", "name": "Private Swimming Pool", "icon": "Waves" },
      { "id": "infinity_pool", "name": "Infinity Pool", "icon": "Waves" },
      { "id": "jacuzzi_outdoor", "name": "Outdoor Jacuzzi", "icon": "Bath" },
      { "id": "terrace", "name": "Terrace", "icon": "Mountain" }
    ],
    "building": [
      { "id": "24h_security", "name": "24h Security", "icon": "Shield" },
      { "id": "security_cameras", "name": "Security Cameras", "icon": "Camera" },
      { "id": "gated_community", "name": "Gated Community", "icon": "Lock" }
    ],
    "utilities": [
      { "id": "fiber_internet", "name": "Fiber Internet", "icon": "Wifi" },
      { "id": "water_supply", "name": "Water Supply", "icon": "Droplets" },
      { "id": "electricity", "name": "Electricity", "icon": "Zap" }
    ],
    "special_features": [
      { "id": "beachfront_location", "name": "Beachfront Location", "icon": "Waves" },
      { "id": "ocean_view", "name": "Ocean View", "icon": "Binoculars" }
    ]
  },
  
  "policies": {
    "inclusions": [
      "WiFi Internet", "Cable TV", "Air Conditioning", 
      "Weekly Housekeeping", "Pool Maintenance"
    ],
    "restrictions": [
      "No smoking inside", "No large parties without notice", "No permanent pets"
    ],
    "house_rules": [
      "Quiet hours: 10 PM - 8 AM", "Guest registration required"
    ],
    "additional_fees": [
      {
        "type": "Service charge",
        "amount": 350000,
        "currency": "THB",
        "frequency": "monthly",
        "description": "Utilities, maintenance, housekeeping"
      }
    ],
    "lease_terms": {
      "minimum_lease_months": 1,
      "maximum_lease_months": 12,
      "notice_period_days": 14,
      "security_deposit_months": 1,
      "advance_payment_months": 1
    }
  },
  
  "contact_info": {
    "agent_name": "Somchai Kongsoon",
    "agent_phone": "+66-82-123-4567",
    "agent_email": "somchai@bestays.app",
    "agent_line_id": "somchai.property",
    "agent_whatsapp_id": "+66821234567",
    "agency_name": "Phuket Luxury Villas",
    "languages_spoken": ["English", "Thai", "Russian", "Chinese"],
    "preferred_contact": "whatsapp",
    "availability_hours": "24h"
  }
}
```

### 1.3 GIN Indexes (from US-016 spec)

```sql
CREATE INDEX idx_properties_location ON bestays_properties_v2 USING GIN(location_details);
CREATE INDEX idx_properties_physical ON bestays_properties_v2 USING GIN(physical_specs);
CREATE INDEX idx_properties_amenities ON bestays_properties_v2 USING GIN(amenities);
CREATE INDEX idx_properties_tags ON bestays_properties_v2 USING GIN(tags);
```

**Query Performance:** GIN indexes enable fast JSONB queries like:
```sql
-- Find properties with pools
SELECT * FROM bestays_properties_v2 
WHERE amenities->'exterior' @> '[{"id": "private_pool"}]'::jsonb;

-- Find properties near beach
SELECT * FROM bestays_properties_v2 
WHERE location_details->'location_advantages' @> '["beachfront"]'::jsonb;
```

### 1.4 Image Storage (Current State)

**Current Provider:** Supabase Storage
**Bucket:** `bestays-images`
**Path Pattern:** `/properties/{property_id}/{timestamp}-{hash}.{ext}`
**URL Format:** `https://mtctlgbvwpssxqakyvoc.supabase.co/storage/v1/object/sign/bestays-images/properties/...`

**Image Structure:**
```json
{
  "cover_image": {
    "url": "https://cdn.bestays.app/properties/550e8400/cover.jpg",
    "color": "#87CEEB",
    "path": "properties/550e8400/cover.jpg",
    "alt": "Beachfront villa with infinity pool at sunset"
  },
  "images": [
    { "url": "...", "color": "...", "path": "...", "alt": "Master bedroom" },
    { "url": "...", "color": "...", "path": "...", "alt": "Living room" }
  ]
}
```

**Recommendation:** Continue using Supabase Storage for MVP, plan Cloudflare R2 migration post-MVP (cost optimization).

---

## 2. Property Dictionary Structure (150+ Amenities)

### 2.1 Status: ❌ DOES NOT EXIST IN CODEBASE

**Finding:** Property dictionary referenced in spec documents (`.sdlc-workflow/.specs/PROPERTY_SCHEMA_EXAMPLES.md`) but NO implementation found in:
- MCP servers
- Database tables
- JSON files
- Backend services

**Conclusion:** Property dictionary must be created NEW for US-022.

### 2.2 Dictionary Structure (from Spec Docs)

**Total Amenities:** 150+ categorized

**Categories:**

**1. Interior Amenities (47 amenities):**
- `air_conditioning`, `dishwasher`, `smart_tv`, `sound_system`, `cinema_room`, `walk_in_closet`, `high_ceilings`, `european_kitchen`, `washing_machine`, `dryer`, `microwave`, `oven`, `refrigerator`, `wine_cellar`, `built_in_wardrobes`, `safe`, `fireplace`, `floor_heating`, `jacuzzi_indoor`, `sauna`, `steam_room`, etc.

**2. Exterior Amenities (24 amenities):**
- `private_pool`, `infinity_pool`, `pool_heating`, `jacuzzi_outdoor`, `terrace`, `rooftop_terrace`, `outdoor_dining`, `bbq_area`, `tropical_garden`, `garage`, `balcony`, `patio`, `deck`, `pergola`, `outdoor_kitchen`, `fire_pit`, `water_feature`, etc.

**3. Building Amenities (24 amenities):**
- `24h_security`, `security_cameras`, `gated_community`, `concierge`, `elevator`, `swimming_pool_shared`, `fitness_center`, `valet_parking`, `playground`, `library`, `business_center`, `conference_room`, `spa`, `restaurant`, `cafe`, etc.

**4. Utilities (13 amenities):**
- `fiber_internet`, `cable_tv`, `water_supply`, `electricity`, `backup_generator`, `hot_water`, `gas_supply`, `solar_panels`, `water_heater`, `central_vacuum`, `smart_home`, etc.

**5. Location Advantages (45 amenities):**
- `beachfront`, `sea_view`, `mountain_view`, `jungle_view`, `gated_community`, `near_airport`, `near_beach`, `near_shopping_mall`, `near_school`, `near_hospital_clinic`, `near_bts`, `near_marina`, `quiet_cul_de_sac`, `on_main_road`, `central_location`, etc.

**6. Special Features (~10 amenities):**
- `beachfront_location`, `ocean_view`, `clean_title`, `natural_landscape`, `pet_friendly`, `wheelchair_accessible`, `eco_friendly`, `smart_home_system`, etc.

### 2.3 Missing Amenities (from LLM Parsing Validation)

**4 Critical Missing Amenities identified in `.claude/reports/20251109-llm-parsing-validation.md`:**
1. **`complete_kitchenware`** - Pots, pans, dishes, utensils (common in Thai rentals)
2. **`fully_equipped_kitchen`** - Generic kitchen amenity (spec has "european_kitchen" but not generic)
3. **`tropical_view`** / **`greenery_view`** - Views of tropical vegetation
4. **`newly_constructed`** / **`newly_built`** - Construction status as feature

**Recommendation:** Add these 4 amenities to dictionary before MVP launch.

### 2.4 Multi-Language Support

**Languages:** EN (English), TH (Thai)
**Structure:**
```json
{
  "id": "air_conditioning",
  "name": {
    "en": "Air Conditioning",
    "th": "เครื่องปรับอากาศ"
  },
  "icon": "Snowflake",
  "category": "interior"
}
```

**Storage Format:** Either JSON files or database table (decision needed in PLANNING phase).

---

## 3. MCP Server Patterns

### 3.1 Status: ❌ NO MCP SERVERS FOUND IN CODEBASE

**Search Results:**
- No `mcp.json` files
- No `mcp_servers/` directory
- No MCP-related configurations

**Conclusion:** Property dictionary MCP server must be created from scratch.

### 3.2 MCP Integration Pattern (from Research)

**Recommended Structure:**
```
apps/mcp_servers/
└── property_dictionary/
    ├── server.py                    # MCP server implementation
    ├── dictionary.json              # 150+ amenities with multi-language
    ├── schemas.json                 # Zod/Pydantic validation schemas
    └── tools.py                     # MCP tools
```

**MCP Tools to Implement:**
1. **`property-dictionary-lookup`** - Get amenity by ID or search by name
2. **`property-dictionary-list-category`** - List all amenities in category (interior, exterior, etc.)
3. **`property-dictionary-validate-amenity`** - Check if amenity ID exists in dictionary
4. **`property-dictionary-suggest-amenities`** - AI suggests amenities based on description

**Example Tool Definition:**
```json
{
  "name": "property-dictionary-lookup",
  "description": "Lookup property amenity from dictionary by ID or name",
  "inputSchema": {
    "type": "object",
    "properties": {
      "amenity_id": { "type": "string", "description": "Amenity ID (e.g., 'air_conditioning')" },
      "category": { "type": "string", "enum": ["interior", "exterior", "building", "utilities", "special_features"] }
    }
  }
}
```

### 3.3 Decision: New MCP Server vs Extend Existing?

**Recommendation:** **Create NEW MCP server** for property dictionary.

**Rationale:**
- No existing MCP servers to extend
- Property dictionary is domain-specific (real estate amenities)
- Clean separation of concerns
- Easier testing and maintenance

---

## 4. Cloudflare R2 Integration

### 4.1 Status: ❌ DOES NOT EXIST

**Search Results:**
- No R2 configuration files
- No Cloudflare SDK imports
- No R2 bucket references

**Current Image Storage:** Supabase Storage (working, but not cost-optimal for scale)

### 4.2 Supabase Storage Analysis

**Current Integration:**
- Bucket: `bestays-images`
- Files found in old NextJS app reference: `/bestays-images/properties/`
- Signed URLs generated by Supabase

**Code Pattern (to be implemented in new SvelteKit):**
```typescript
// Old NextJS pattern (reference only)
const { data, error } = await supabase.storage
  .from('bestays-images')
  .upload(`properties/${propertyId}/${fileName}`, file);
```

### 4.3 Cloudflare R2 Migration Strategy

**Phase 1 (MVP):** Continue Supabase Storage
- Already working
- No migration required
- Focus on core features

**Phase 2 (Post-MVP):** Migrate to Cloudflare R2
- Cost optimization: $0.015/GB/month vs Supabase premium pricing
- S3-compatible API (easy migration)
- CDN included (better performance)
- No egress fees

**Implementation Pattern (Future):**
```python
# Backend: R2 upload
from boto3 import client

r2_client = client(
    's3',
    endpoint_url='https://your-account-id.r2.cloudflarestorage.com',
    aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
    region_name='auto'
)

r2_client.upload_file(
    file_path,
    'bestays-images',
    f'properties/{property_id}/{timestamp}-{filename}'
)
```

**Recommendation:** Defer Cloudflare R2 migration to post-MVP. Supabase Storage sufficient for launch.

---

## 5. OpenRouter API Patterns

### 5.1 Status: ✅ FULLY IMPLEMENTED

**Location:** `apps/server/src/server/llm_config/llm.py`

**Current Configuration:**
```python
class LLMSettings(BaseSettings):
    # API Keys
    openrouter_api_key: Optional[str]
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # Model Selection (updated 2025-10-25)
    chat_model: str = "google/gemini-2.5-flash-lite"
    search_model: str = "google/gemini-2.5-flash-lite"
    agent_model: str = "google/gemini-2.5-flash-lite"
    parsing_model: str = "google/gemini-2.5-flash-lite"
    
    # Streaming
    streaming_enabled: bool = True
    streaming_chunk_size: int = 512
    streaming_timeout: int = 60
    
    # Rate Limiting
    rate_limit_agent: int = 100  # requests per minute
    
    # Cost Control
    max_tokens: int = 4000
    monthly_budget: float = 1000.0
```

**Key Findings:**
- ✅ OpenRouter already integrated
- ✅ Gemini 2.5 Flash Lite used for ALL use cases (chat, search, parsing)
- ✅ Streaming support enabled
- ✅ Rate limiting configured (100 req/min for agents)
- ✅ Cost control with budget limits

### 5.2 Existing LLM Integration Patterns

**Chat Service:** `apps/server/src/server/services/chat_service.py`
**LangChain Usage:** Found in FAQ RAG pipeline

**Pattern to Reuse for US-022:**
```python
# Existing pattern from chat service
from langchain_community.chat_models import ChatOpenRouter

llm = ChatOpenRouter(
    model=settings.models.parsing_model,
    openrouter_api_key=settings.openrouter_api_key,
    temperature=0.2,  # Lower temperature for parsing (more deterministic)
    max_tokens=4000
)

# For structured output (property parsing)
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class PropertyParsing(BaseModel):
    bedrooms: int = Field(description="Number of bedrooms")
    bathrooms: int = Field(description="Number of bathrooms")
    # ... other fields

parser = PydanticOutputParser(pydantic_object=PropertyParsing)
prompt = PromptTemplate(
    template="Extract property details: {description}\n{format_instructions}",
    input_variables=["description"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

chain = prompt | llm | parser
result = chain.invoke({"description": agent_input})
```

### 5.3 Image Analysis (Vision Models)

**Current State:** NOT YET IMPLEMENTED in codebase

**Recommended Approach for US-022:**
```python
# Use OpenRouter vision models
vision_model = ChatOpenRouter(
    model="anthropic/claude-3.5-sonnet",  # Vision-capable model
    openrouter_api_key=settings.openrouter_api_key
)

# Image analysis prompt
image_analysis_prompt = """
Analyze this property image and identify:
1. Amenities visible (pool, garden, parking, etc.)
2. Views (mountain, sea, city, jungle)
3. Style (modern, traditional, rustic)
4. Outdoor spaces (balcony, terrace, patio)

Use ONLY amenities from the property dictionary provided.
"""

# Send image + dictionary as context
result = vision_model.invoke([
    {"type": "text", "text": image_analysis_prompt},
    {"type": "image_url", "image_url": image_base64}
])
```

### 5.4 Cost Analysis

**From LLM Parsing Validation Report:**
- Text extraction: ~$0.01 per property (GPT-4 Turbo or Claude 3.5 Sonnet)
- Image analysis: ~$0.05-0.10 per property (5-10 images with GPT-4V or Claude 3.5 Vision)
- **Total: ~$0.11 per property**

**Budget Impact:** For 1000 properties/month = $110/month (well within $1000 monthly budget)

---

## 6. Inline Editing Patterns (US-020)

### 6.1 Status: ❌ NOT FOUND IN CODEBASE

**Findings:**
- US-020 story document EXISTS and marked COMPLETED (`.sdlc-workflow/stories/homepage/US-020-homepage-editable-content.md`)
- But NO implementation code found in:
  - `apps/frontend/src/lib/components/` (no EditableText.svelte, no EditContentDialog.svelte)
  - `apps/frontend/src/routes/+page.svelte` (basic homepage, no inline editing)

**Conclusion:** US-020 implementation either:
1. On different branch not yet merged
2. From previous iteration/rewrite
3. Specification only (not yet implemented)

**Impact on US-022:** Inline editing pattern must be implemented from scratch.

### 6.2 US-020 Specification Review

**From story document:**

**Pattern:** Right-click → Context Menu → Edit Dialog → Save

**Components Specified:**
1. **EditableText.svelte** - Wrapper component with right-click detection
2. **EditContentDialog.svelte** - Modal with form (Cancel/Save)
3. **Context Menu** - Shows "Edit Content" for admin/agent roles
4. **RBAC Check** - Only admin/agent can see edit UI

**API Pattern:**
```typescript
// GET /api/v1/content/homepage.title → { key: "...", value: "..." }
// PUT /api/v1/content/homepage.title → { value: "new value" }
```

**Database Pattern (from US-020 spec):**
```sql
CREATE TABLE content_dictionary (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    updated_at TIMESTAMP,
    updated_by INTEGER REFERENCES users(id)
);
```

### 6.3 Inline Editing for Property Detail Page

**US-022 Requirement:** Agent can edit property fields inline on property detail page.

**Pattern to Implement:**
```svelte
<!-- Property Detail Page -->
<script>
  import EditableField from '$lib/components/EditableField.svelte';
  
  let property = $state(data.property);
  let userRole = $state(authContext.user.role);
</script>

<!-- Editable title (if agent/admin) -->
<EditableField
  value={property.title}
  field="title"
  propertyId={property.id}
  editable={userRole === 'agent' || userRole === 'admin'}
  onSave={(newValue) => property.title = newValue}
>
  <h1>{property.title}</h1>
</EditableField>

<!-- Editable description -->
<EditableField
  value={property.description}
  field="description"
  propertyId={property.id}
  editable={userRole === 'agent' || userRole === 'admin'}
  onSave={(newValue) => property.description = newValue}
>
  <p>{property.description}</p>
</EditableField>
```

**Backend API:**
```python
@router.patch("/api/v1/properties/{property_id}")
async def update_property_field(
    property_id: str,
    field_update: PropertyFieldUpdate,
    current_user: User = Depends(get_current_user)
):
    # RBAC check
    if current_user.role not in ["agent", "admin"]:
        raise HTTPException(403, "Insufficient permissions")
    
    # Validate agent owns property (or is admin)
    property = await db.properties.get(property_id)
    if current_user.role == "agent" and property.created_by != current_user.id:
        raise HTTPException(403, "Can only edit own properties")
    
    # Update field
    await db.properties.update(property_id, {
        field_update.field: field_update.value,
        "updated_by": current_user.id,
        "updated_at": datetime.utcnow()
    })
    
    return {"success": True}
```

---

## 7. Multi-Product Architecture

### 7.1 Status: ✅ FULLY IMPLEMENTED

**Environment Files:**
- `.env.bestays` - Bestays product configuration
- `.env.realestate` - Real Estate product configuration
- `.env.shared` - Shared configuration (database, Redis, etc.)

**Key Configuration Differences:**

**Bestays (`.env.bestays`):**
```bash
PRODUCT_NAME=Bestays
PRODUCT_DOMAIN=bestays.app
CLERK_SECRET_KEY=sk_test_vGrRuTLW1SdS2uQlDbv4l2T2WHpTk9IoervBmG9Vit  # sacred-mayfly-55
VITE_CLERK_PUBLISHABLE_KEY=pk_test_c2FjcmVkLW1heWZseS01NS5jbGVyay5hY2NvdW50cy5kZXYk
FRONTEND_PORT=5183
BACKEND_PORT=8011
PUBLIC_PRODUCT=bestays
```

**Real Estate (`.env.realestate`):**
```bash
PRODUCT_NAME=Best Real Estate
PRODUCT_DOMAIN=realestate.dev
CLERK_SECRET_KEY=sk_test_GBG0pHIE015mIkiHfrpeOS4mi1hqNSm0uBUdlexgxS  # pleasant-gnu-25
VITE_CLERK_PUBLISHABLE_KEY=pk_test_cGxlYXNhbnQtZ251LTI1LmNsZXJrLmFjY291bnRzLmRldiQ
FRONTEND_PORT=5184
BACKEND_PORT=8012
PUBLIC_PRODUCT=realestate
```

### 7.2 Multi-Product Routing (Frontend)

**Current Routes:**
```
apps/frontend/src/routes/
├── +page.svelte              # Homepage (shared)
├── dashboard/                # Dashboard routes
├── login/                    # Login page
└── unauthorized/             # 403 page
```

**Recommended Structure for US-022:**
```
apps/frontend/src/routes/
├── (bestays)/
│   └── listings/
│       └── properties-for-rent/
│           ├── +page.svelte       # Property list (rentals)
│           └── [id]/
│               └── +page.svelte   # Property detail (editable)
└── (realestate)/
    └── listings/
        ├── properties-for-sale/
        │   ├── +page.svelte       # Property list (sales)
        │   └── [id]/
        │       └── +page.svelte   # Property detail (editable)
        └── properties-for-rent/
            ├── +page.svelte       # Property list (rentals)
            └── [id]/
                └── +page.svelte   # Property detail (editable)
```

**SvelteKit Route Groups:** Use `(bestays)` and `(realestate)` groups for product-specific routing.

### 7.3 Shared API + Product-Specific Logic

**Backend API (Shared):**
```
apps/server/src/server/api/v1/
└── endpoints/
    └── properties.py           # Shared API for both products
```

**Product Detection:**
```python
# Detect product from request headers or JWT claims
def get_current_product(request: Request) -> str:
    product = request.headers.get("X-Product", "bestays")
    return product

@router.get("/api/v1/properties")
async def list_properties(
    transaction_type: Optional[str] = None,
    product: str = Depends(get_current_product)
):
    # Filter by transaction type based on product
    filters = {}
    if product == "bestays":
        filters["transaction_type"] = "rent"  # Bestays = rentals only
    elif product == "realestate":
        if transaction_type:
            filters["transaction_type"] = transaction_type  # Both sale & rent
    
    properties = await db.properties.find(filters)
    return properties
```

---

## 8. Image Gallery Components

### 8.1 Status: ❌ NO GALLERY COMPONENTS FOUND

**Search Results:**
- No gallery/carousel/lightbox Svelte components in `apps/frontend/src/lib/components/`
- No image viewer components

**Existing Components:**
```
apps/frontend/src/lib/components/
├── AuthNav.svelte
├── chat/                      # Chat UI components (for AI chat feature)
├── dashboard/                 # Dashboard layout
└── ui/                        # shadcn-svelte components (button, card, etc.)
```

**Conclusion:** Image gallery must be implemented from scratch for property detail page.

### 8.2 Recommended Component Structure

**Component:** `ImageGallery.svelte`

**Features:**
- Main image display (large)
- Thumbnail strip (bottom/side)
- Lightbox modal (click to expand)
- Navigation (prev/next arrows)
- Lazy loading
- Responsive design

**Libraries to Consider:**
1. **swiper** - Modern touch slider (https://swiperjs.com/)
2. **embla-carousel-svelte** - Lightweight carousel for Svelte
3. **photoswipe** - Lightbox for images

**Example Structure:**
```svelte
<!-- ImageGallery.svelte -->
<script lang="ts">
  import { Swiper, SwiperSlide } from 'swiper/svelte';
  import 'swiper/css';
  
  let { images = [] } = $props();
  let currentIndex = $state(0);
  let showLightbox = $state(false);
</script>

<div class="gallery">
  <!-- Main image -->
  <div class="main-image">
    <img src={images[currentIndex].url} alt={images[currentIndex].alt} />
  </div>
  
  <!-- Thumbnails -->
  <div class="thumbnails">
    <Swiper slidesPerView={5} spaceBetween={10}>
      {#each images as image, i}
        <SwiperSlide>
          <img
            src={image.url}
            alt={image.alt}
            class:active={i === currentIndex}
            onclick={() => currentIndex = i}
          />
        </SwiperSlide>
      {/each}
    </Swiper>
  </div>
</div>

<!-- Lightbox (modal) -->
{#if showLightbox}
  <div class="lightbox">
    <img src={images[currentIndex].url} alt={images[currentIndex].alt} />
    <button onclick={() => showLightbox = false}>Close</button>
  </div>
{/if}
```

---

## 9. Frontend API Patterns

### 9.1 Existing API Clients

**Location:** `apps/frontend/src/lib/api/`

**Files Found:**
- `client.ts` - Base HTTP client (fetch wrapper)
- `users.ts` - User API calls
- `faqs.ts` - FAQ API calls
- `chat-config.ts` - Chat configuration API
- `categories.ts` - Category management

**Pattern Analysis (`client.ts`):**
```typescript
// Base client pattern
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8011';

export const apiClient = {
  get: async (path: string) => {
    const response = await fetch(`${API_BASE}${path}`, {
      headers: { 'Authorization': `Bearer ${getToken()}` }
    });
    return response.json();
  },
  post: async (path: string, data: any) => {
    const response = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify(data)
    });
    return response.json();
  }
};
```

### 9.2 Recommended Property API Client

**Create:** `apps/frontend/src/lib/api/properties.ts`

```typescript
import { apiClient } from './client';
import type { Property, PropertyCreate, PropertyUpdate } from '$lib/types/property';

export const propertiesApi = {
  // List properties
  list: async (filters?: {
    transaction_type?: string;
    property_type?: string;
    region?: string;
  }): Promise<Property[]> => {
    const params = new URLSearchParams(filters).toString();
    return apiClient.get(`/api/v1/properties?${params}`);
  },
  
  // Get single property
  get: async (id: string): Promise<Property> => {
    return apiClient.get(`/api/v1/properties/${id}`);
  },
  
  // Create property (agent/admin only)
  create: async (data: PropertyCreate): Promise<Property> => {
    return apiClient.post('/api/v1/properties', data);
  },
  
  // Update property field (inline editing)
  updateField: async (
    id: string,
    field: string,
    value: any
  ): Promise<{ success: boolean }> => {
    return apiClient.patch(`/api/v1/properties/${id}`, { field, value });
  },
  
  // AI analysis (text + images)
  analyzeProperty: async (data: {
    description: string;
    images: File[];
  }): Promise<PropertyCreate> => {
    const formData = new FormData();
    formData.append('description', data.description);
    data.images.forEach((image, i) => {
      formData.append(`image_${i}`, image);
    });
    
    return apiClient.post('/api/v1/properties/analyze', formData);
  }
};
```

---

## 10. Test Credentials & RBAC

### 10.1 Bestays Test Accounts

**Clerk Instance:** sacred-mayfly-55.clerk.accounts.dev

| Email | Password | Role | Purpose |
|-------|----------|------|---------|
| `user.claudecode@bestays.app` | `9kB*k926O8):` | user | Regular user (cannot create properties) |
| `agent.claudecode@bestays.app` | `y>1T;)5s!X1X` | agent | Property agent (can create & edit own properties) |
| `admin.claudecode@bestays.app` | `rHe/997?lo&l` | admin | Admin (can create & edit all properties) |

### 10.2 RBAC Matrix for US-022

| Role | Create Property | Edit Own Property | Edit Any Property | Delete Property | View Properties |
|------|----------------|-------------------|-------------------|-----------------|-----------------|
| **User** | ❌ No | ❌ No | ❌ No | ❌ No | ✅ Yes (published) |
| **Agent** | ✅ Yes | ✅ Yes | ❌ No | ⚠️ Limited (own) | ✅ Yes (all) |
| **Admin** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes (all) |

**Backend Enforcement:**
```python
def check_property_permission(current_user: User, property_id: str = None):
    if current_user.role == "admin":
        return True  # Admins can do anything
    
    if current_user.role == "agent":
        if property_id is None:
            return True  # Agents can create
        
        # Agents can only edit their own properties
        property = db.properties.get(property_id)
        return property.created_by == current_user.id
    
    return False  # Users cannot write properties
```

---

## 11. Key Architectural Decisions

### 11.1 AI Safety Model (Approved Pattern)

**Document:** `.sdlc-workflow/guides/ai-agent-workflow-pattern.md`

**3-Phase Workflow:**

**Phase 1: AI Preparation (Safe)**
- AI analyzes text + images
- Generates structured Property V2 JSON
- Shows preview modal with confidence scores
- **NO database writes**

**Phase 2: Agent Confirmation (Required)**
- Agent reviews AI-generated fields
- Agent can edit any field
- Agent clicks "Create Property" CTA
- **Explicit user action required**

**Phase 3: API Request + RBAC (Secure)**
- Frontend: POST /api/v1/properties with JWT
- Backend: Validates agent role
- Backend: Validates Zod schema
- Database: Inserts property with audit trail

**Key Principle:** AI prepares data, user executes actions.

### 11.2 LLM Parsing Validation Results

**Document:** `.claude/reports/20251109-llm-parsing-validation.md`

**Validation Status:** ✅ PASSED

**Key Metrics:**
- **Extraction Success:** 85% (115/135 fields extracted successfully)
- **High Confidence (≥90%):** 64% (87/135 fields)
- **Dictionary Coverage:** 76% (13/17 amenities matched)

**Confidence Thresholds:**
- **≥90%**: Auto-fill (green checkmark)
- **60-89%**: Agent review required (yellow warning)
- **<60%**: Manual input required (red alert)

**Conclusion:** LLM parsing is FEASIBLE for US-022 with agent confirmation modal (MANDATORY).

---

## 12. Blockers & Dependencies

### 12.1 Critical Blockers

**BLOCKER 1: US-016 Property V2 Migration Not Applied**
- **Status:** Database still has basic Property model (title + description only)
- **Impact:** CANNOT start US-022 without full Property V2 schema
- **Action:** Apply US-016 Alembic migration BEFORE starting TASK-013 (PLANNING)
- **Owner:** DevOps

**BLOCKER 2: Property Dictionary Does Not Exist**
- **Status:** No property dictionary in codebase (no MCP server, no data)
- **Impact:** AI cannot validate amenities without dictionary
- **Action:** Create property dictionary MCP server (TASK-014)
- **Owner:** Backend

### 12.2 Dependencies

**Depends On (External):**
- ✅ OpenRouter API (RESOLVED - already integrated)
- ✅ Clerk Authentication (RESOLVED - working)
- ❌ Cloudflare R2 (DEFERRED - use Supabase Storage for MVP)

**Depends On (Internal):**
- ❌ US-016 Property V2 Migration (MUST COMPLETE FIRST)
- ❌ Property Dictionary MCP Server (MUST CREATE)
- ❌ Inline Editing Components (MUST IMPLEMENT)

---

## 13. Recommendations for TASK-013 (PLANNING Phase)

### 13.1 Immediate Actions (Before Planning)

1. **Apply US-016 Property V2 Migration**
   - Run Alembic migration to add 5 JSONB fields
   - Verify GIN indexes created
   - Test JSONB queries
   - **Estimated Time:** 2 hours

2. **Review LLM Parsing Validation Report**
   - Understand confidence thresholds
   - Review dictionary gaps (4 missing amenities)
   - Plan agent confirmation modal UI
   - **Estimated Time:** 1 hour

3. **Review AI Safety Model**
   - Understand 3-phase workflow
   - Confirm RBAC requirements
   - Plan audit trail fields
   - **Estimated Time:** 30 minutes

### 13.2 Planning Phase Priorities

**TASK-013 Focus Areas:**

1. **Property Dictionary MCP Server Design**
   - Storage format: JSON files vs database (DECISION NEEDED)
   - MCP tool interfaces (4 tools minimum)
   - Multi-language support (EN/TH)
   - Add 4 missing amenities
   - Versioning strategy

2. **AI Analysis Workflow Design**
   - Text extraction: LangChain + PydanticOutputParser
   - Image analysis: Claude 3.5 Sonnet vision model
   - Dictionary validation: MCP tool integration
   - Confidence scoring: 3-tier system

3. **Agent Confirmation Modal Design**
   - UI mockup (Figma/design tool)
   - Field grouping (core, physical_specs, location, amenities, policies)
   - Confidence indicators (green/yellow/red)
   - Edit capabilities (all fields editable)
   - CTA buttons (Cancel, Create Property)

4. **Inline Editing Component Design**
   - EditableField.svelte component spec
   - Right-click context menu
   - RBAC check (agent can edit own, admin can edit all)
   - API integration (PATCH /api/v1/properties/{id})

5. **API Endpoint Design**
   - POST /api/v1/properties/analyze (AI analysis)
   - POST /api/v1/properties (create property)
   - PATCH /api/v1/properties/{id} (inline edit)
   - GET /api/v1/properties (list with filters)
   - GET /api/v1/properties/{id} (get single)

6. **Image Storage Strategy**
   - Continue Supabase Storage for MVP
   - Plan Cloudflare R2 migration (post-MVP)
   - Image upload flow: Frontend → Backend → Supabase
   - Signed URL generation

7. **Multi-Product Routing**
   - SvelteKit route groups: (bestays) and (realestate)
   - Product detection: Headers or JWT claims
   - Transaction type filtering: rent (Bestays), rent+sale (Real Estate)

### 13.3 Quality Gate Checklist (TASK-013 Planning)

**Before moving to IMPLEMENTATION:**
- [ ] US-016 Property V2 migration applied and tested
- [ ] Property dictionary structure designed (150+ amenities)
- [ ] MCP server architecture documented
- [ ] AI analysis workflow designed (text + images)
- [ ] Agent confirmation modal UI designed
- [ ] Inline editing components designed
- [ ] API endpoints documented (OpenAPI spec)
- [ ] RBAC rules documented (agent vs admin)
- [ ] Test plan created (unit + integration + E2E)
- [ ] Acceptance criteria validated (all 20 ACs from US-022)

---

## 14. Old NextJS App Reference

### 14.1 Property Form Components (Reference Only)

**Location:** `/Users/solo/Projects/_repos/react-workspace/src/apps/bestays-web/components/property-form/`

**Components Found:**
- `PropertyForm.tsx` - Main form component
- `form-text-input.tsx` - Text field
- `form-price-input.tsx` - Price field
- `form-text-area.tsx` - Description textarea
- `form-dropdown.tsx` - Dropdown select
- `form-image-input.tsx` - Image upload
- `image-input/` - Image management subcomponents

**Note:** These are React/NextJS components. DO NOT port directly. Use as reference for field types and validation patterns only.

### 14.2 Property Listing Page (Reference)

**URL:** https://bestays.app/listings/properties-for-rent

**Structure:**
- Grid layout (3 columns desktop, 2 mobile)
- Property cards with: title, price, location, cover image
- Click → Navigate to `/p/{id}` (property detail)

**Data Format:**
```json
{
  "id": "de6c6dda-6f23-41b6-a882-0ce5e06ad297",
  "title": "Quiet 1-Bedroom Home Near Secret Mountain",
  "price": 3500000,
  "currency": "THB",
  "location": { "region": "Koh Phangan", "area": "Baan Tai" },
  "cover_image": { "url": "...", "alt": "..." },
  "transaction_type": "rent",
  "property_type": "house"
}
```

**Implementation:** Create new SvelteKit version (do NOT port React code).

---

## 15. Summary & Next Steps

### 15.1 What Exists (Reusable)

✅ **Property V2 Schema Spec** - Comprehensive spec with JSONB fields (needs migration)
✅ **OpenRouter Integration** - Working LLM infrastructure with Gemini 2.5 Flash Lite
✅ **Multi-Product Architecture** - Environment configs, Clerk instances, port separation
✅ **LLM Parsing Validation** - Proven 85% extraction success rate
✅ **AI Safety Model** - Approved 3-phase workflow (AI prepares, user executes)
✅ **Supabase Storage** - Working image storage (can defer R2 migration)

### 15.2 What Does NOT Exist (Must Build)

❌ **Property V2 Database Migration** - Schema exists in spec, not applied to database
❌ **Property Dictionary MCP Server** - No dictionary implementation (150+ amenities)
❌ **US-020 Inline Editing** - Story complete, code missing (implement from scratch)
❌ **Image Gallery Components** - No carousel/lightbox components
❌ **Property API Client** - No frontend API for properties
❌ **Agent Chat Interface** - No chat UI for property creation
❌ **Property Confirmation Modal** - No preview/confirm UI

### 15.3 Immediate Next Steps (Sequential)

**STEP 1: Apply US-016 Migration (BLOCKER)**
- Run Alembic migration to add 5 JSONB fields to properties table
- Verify GIN indexes created
- Test JSONB queries
- **Timeline:** 2 hours
- **Blocks:** Everything else

**STEP 2: Start TASK-013 (PLANNING Phase)**
- Design property dictionary structure
- Design MCP server architecture
- Design AI analysis workflow
- Design agent confirmation modal UI
- Document API endpoints
- **Timeline:** 3-4 days

**STEP 3-7: Implementation Tasks (After Planning)**
- TASK-014: Property Dictionary MCP Server
- TASK-015: AI Analysis Backend
- TASK-016: Agent Chat Interface Frontend
- TASK-017: Property Listings UI (with inline editing)
- TASK-018: E2E Testing

### 15.4 Critical Success Factors

**MUST HAVE:**
1. ✅ Property V2 schema in database (US-016 migration)
2. ✅ Property dictionary with 150+ amenities (4 missing added)
3. ✅ Agent confirmation modal (MANDATORY per AI safety model)
4. ✅ RBAC enforcement (agent can create/edit own, admin can edit all)
5. ✅ LLM confidence scoring (≥90%, 60-89%, <60%)

**NICE TO HAVE:**
- Cloudflare R2 migration (defer to post-MVP)
- Advanced image gallery (start with basic, enhance later)
- Multi-language dictionary (EN first, TH later)

---

## 16. File Paths Reference

### 16.1 Key Documents

**Specs:**
- `.sdlc-workflow/stories/properties/US-016-property-migration-design.md`
- `.sdlc-workflow/stories/properties/US-022-properties-ai-creation-management.md`
- `.sdlc-workflow/.specs/PROPERTY_SCHEMA_EXAMPLES.md`
- `.sdlc-workflow/.specs/README_PROPERTY_SCHEMA.md`

**Guides:**
- `.sdlc-workflow/guides/ai-agent-workflow-pattern.md`
- `.sdlc-workflow/guides/chat-driven-ui-architecture.md`
- `.sdlc-workflow/guides/semantic-search-architecture.md`
- `.sdlc-workflow/guides/pgvector-rag-architecture.md`

**Reports:**
- `.claude/reports/20251109-property-rent-scraping-findings.md`
- `.claude/reports/20251109-llm-parsing-validation.md`
- `.claude/reports/20251107-multi-product-story-workflow.md`

### 16.2 Key Code Files

**Backend:**
- `apps/server/src/server/models/property.py` (current model - BASIC)
- `apps/server/src/server/llm_config/llm.py` (OpenRouter config)
- `apps/server/src/server/services/chat_service.py` (LangChain patterns)

**Frontend:**
- `apps/frontend/src/lib/api/client.ts` (API client base)
- `apps/frontend/src/lib/components/chat/` (chat UI reference)
- `apps/frontend/src/routes/+page.svelte` (homepage)

**Environment:**
- `.env.bestays` (Bestays config)
- `.env.realestate` (Real Estate config)
- `.env.shared` (shared config)

**Old Reference:**
- `/Users/solo/Projects/_repos/react-workspace/src/apps/bestays-web/` (NextJS app - reference only)

---

**Research Complete:** 2025-11-09
**Next Phase:** TASK-013 (PLANNING)
**Status:** ✅ READY TO PROCEED


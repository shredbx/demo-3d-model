# Phase 6: Service Layer and API Endpoints Implementation Spec

**TASK:** TASK-013
**Phase:** IMPLEMENTATION - Phase 6
**Date:** 2025-11-09
**Subagent:** dev-backend-fastapi

---

## Objective

Implement complete service layer and API endpoints for Property V2 schema with hybrid localization support.

---

## Context

**Completed:**
- ✅ Phase 1-3: Database migration with amenities, policies, properties tables
- ✅ Phase 4: SQLAlchemy models (Property, PropertyTranslation, Amenity, Policy)
- ✅ Phase 5: Pydantic schemas (PropertyCreate, PropertyUpdate, PropertyResponse, etc.)

**Current Phase:**
- Implement 3 service classes (PropertyService, AmenityService, PolicyService)
- Implement 3 API routers (properties, amenities, policies)
- Register routers in main API router

---

## Files to Create

### Service Layer (apps/server/src/server/services/)

1. **property_service.py** - PropertyService class
2. **amenity_service.py** - AmenityService class
3. **policy_service.py** - PolicyService class

### API Endpoints (apps/server/src/server/api/v1/endpoints/)

4. **properties.py** - Property endpoints (7 endpoints)
5. **amenities.py** - Amenity endpoints (1 endpoint)
6. **policies.py** - Policy endpoints (1 endpoint)

### Files to Modify

7. **apps/server/src/server/api/v1/router.py** - Register 3 new routers

---

## Implementation Requirements

### A. PropertyService (property_service.py)

**Location:** `apps/server/src/server/services/property_service.py`

**Methods Required:**

```python
class PropertyService:
    """Service for property CRUD operations with hybrid localization."""

    async def list_properties(
        self,
        db: AsyncSession,
        query: PropertyListQuery,
        locale: str = "en"
    ) -> tuple[list[Property], int]:
        """
        List properties with filters, pagination, and translations.

        IMPLEMENTATION STEPS:
        1. Build base query: SELECT * FROM properties WHERE deleted_at IS NULL
        2. Apply filters:
           - transaction_type (if provided)
           - property_type (if provided)
           - Price range: rent_price/sale_price/lease_price BETWEEN min_price AND max_price
           - bedrooms: physical_specs->'rooms'->>'bedrooms' = ?
           - bathrooms: physical_specs->'rooms'->>'bathrooms' = ?
           - min_area: physical_specs->'sizes'->>'usable_area_sqm' >= ?
           - province: location_details->'administrative'->>'province_id' = ?
           - district: location_details->'administrative'->>'district_id' = ?
           - amenities: Check if ALL amenity IDs exist in amenities JSONB arrays
           - tags: Check if ANY tag exists in tags array
           - is_featured (if provided)
        3. Get total count (before pagination)
        4. Apply sorting:
           - priority: ORDER BY listing_priority DESC, created_at DESC
           - price_asc: ORDER BY COALESCE(rent_price, sale_price, lease_price) ASC
           - price_desc: ORDER BY COALESCE(rent_price, sale_price, lease_price) DESC
           - newest: ORDER BY created_at DESC
           - oldest: ORDER BY created_at ASC
        5. Apply pagination: LIMIT per_page OFFSET (page - 1) * per_page
        6. LEFT JOIN property_translations and aggregate:
           json_object_agg(field, value) FILTER (WHERE locale = ?)
        7. For each property, call _merge_translations()
        8. Return (properties, total)

        Returns:
            (properties, total_count)
        """
        pass

    async def get_property_by_id(
        self,
        db: AsyncSession,
        property_id: UUID,
        locale: str = "en",
        include_deleted: bool = False
    ) -> Property | None:
        """
        Get single property with translations.

        IMPLEMENTATION:
        1. SELECT * FROM properties WHERE id = ? [AND deleted_at IS NULL]
        2. If not found, return None
        3. LEFT JOIN property_translations
        4. Aggregate translations: json_object_agg(field, value) FILTER (WHERE locale IN (?, 'en'))
        5. Call _merge_translations()
        6. Return property
        """
        pass

    async def create_property(
        self,
        db: AsyncSession,
        data: PropertyCreate,
        created_by: int
    ) -> Property:
        """
        Create property with optional translations.

        IMPLEMENTATION:
        1. Validate amenity IDs exist (query amenities table)
        2. Validate policy IDs exist (query policies table)
        3. Validate business rules:
           - If transaction_type = 'rent', rent_price must be set
           - If transaction_type = 'sale', sale_price must be set
           - If transaction_type = 'lease', lease_price must be set
        4. Create Property instance (set created_by, updated_by)
        5. db.add(property)
        6. If data.translations provided:
           For each (locale, fields) in translations:
             For each (field, value) in fields:
               Create PropertyTranslation(property_id, locale, field, value)
               db.add(translation)
        7. await db.commit()
        8. await db.refresh(property)
        9. Return property

        Raises:
            HTTPException(400): Invalid amenity/policy IDs or business rule violation
        """
        pass

    async def update_property(
        self,
        db: AsyncSession,
        property_id: UUID,
        data: PropertyUpdate,
        updated_by: int
    ) -> Property:
        """
        Update property (partial update with translations).

        IMPLEMENTATION:
        1. Get existing property (raise 404 if not found)
        2. Check ownership or admin (raise 403 if unauthorized)
        3. Update fields (only if provided in data):
           for field, value in data.model_dump(exclude_unset=True).items():
             if field != 'translations':
               setattr(property, field, value)
        4. Set updated_by
        5. If data.translations provided:
           For each (locale, fields) in translations:
             For each (field, value) in fields:
               Upsert PropertyTranslation:
                 - Try UPDATE WHERE property_id=? AND locale=? AND field=?
                 - If no rows affected, INSERT
        6. await db.commit()
        7. await db.refresh(property)
        8. Return property
        """
        pass

    async def delete_property(
        self,
        db: AsyncSession,
        property_id: UUID,
        user: User
    ) -> bool:
        """
        Soft delete property.

        IMPLEMENTATION:
        1. Get property (raise 404 if not found)
        2. Check ownership or admin (raise 403)
        3. Set deleted_at = func.now()
        4. await db.commit()
        5. Return True
        """
        pass

    async def get_all_translations(
        self,
        db: AsyncSession,
        property_id: UUID
    ) -> dict[str, dict[str, str]]:
        """
        Get all translations for a property grouped by locale.

        IMPLEMENTATION:
        1. SELECT locale, field, value FROM property_translations WHERE property_id = ?
        2. Group by locale:
           result = {}
           for row in rows:
             if row.locale not in result:
               result[row.locale] = {}
             result[row.locale][row.field] = row.value
        3. Return result

        Returns:
            {"en": {"title": "...", "description": "..."}, "th": {...}}
        """
        pass

    async def update_translations(
        self,
        db: AsyncSession,
        property_id: UUID,
        locale: str,
        translations: dict[str, str]
    ) -> list[str]:
        """
        Upsert translations for a specific locale.

        IMPLEMENTATION:
        1. Verify property exists (raise 404)
        2. For each (field, value) in translations.items():
             Upsert PropertyTranslation
        3. await db.commit()
        4. Return list of updated fields
        """
        pass

    def _merge_translations(
        self,
        property: Property,
        translations_dict: dict[str, str],
        locale: str
    ) -> Property:
        """
        Merge translations into property object with fallback chain.

        FALLBACK CHAIN:
        1. Requested locale translation
        2. English (en) translation
        3. Original property field value

        TRANSLATABLE FIELDS:
        - title
        - description
        - location_province (from location_details)
        - location_district (from location_details)

        IMPLEMENTATION:
        1. For each translatable field:
             # Try requested locale
             if f"{field}_{locale}" in translations_dict:
               setattr(property, field, translations_dict[f"{field}_{locale}"])
             # Try EN fallback
             elif f"{field}_en" in translations_dict:
               setattr(property, field, translations_dict[f"{field}_en"])
             # Keep original value
        2. Return property
        """
        pass
```

**Key Patterns:**
- Use SQLAlchemy `select()` with async/await
- Use JSONB operators: `->`, `->>`, `@>`, `?`
- Use `func.json_object_agg()` for translation aggregation
- Follow existing service patterns (see user_service.py)

---

### B. AmenityService (amenity_service.py)

**Location:** `apps/server/src/server/services/amenity_service.py`

```python
class AmenityService:
    """Service for amenity operations with localization."""

    async def list_amenities(
        self,
        db: AsyncSession,
        locale: str = "en",
        category: str | None = None
    ) -> list[Amenity]:
        """
        List amenities with translations.

        IMPLEMENTATION:
        1. SELECT * FROM amenities [WHERE category = ?]
        2. ORDER BY category, sort_order, id
        3. LEFT JOIN amenity_translations WHERE locale = ?
        4. For each amenity, merge translation (name field only)
        5. Return amenities
        """
        pass
```

---

### C. PolicyService (policy_service.py)

**Location:** `apps/server/src/server/services/policy_service.py`

```python
class PolicyService:
    """Service for policy operations with localization."""

    async def list_policies(
        self,
        db: AsyncSession,
        locale: str = "en",
        category: str | None = None
    ) -> list[Policy]:
        """
        List policies with translations.

        IMPLEMENTATION:
        1. SELECT * FROM policies [WHERE category = ?]
        2. ORDER BY category, sort_order, id
        3. LEFT JOIN policy_translations WHERE locale = ?
        4. For each policy, merge translations (name, description fields)
        5. Return policies
        """
        pass
```

---

### D. Properties Router (properties.py)

**Location:** `apps/server/src/server/api/v1/endpoints/properties.py`

**Endpoints (7 total):**

```python
router = APIRouter(prefix="/properties", tags=["properties"])

@router.get("", response_model=PropertyListResponse)
async def list_properties(
    query: PropertyListQuery = Depends(),
    locale: str = Query("en"),
    db: AsyncSession = Depends(get_db)
):
    """
    List properties with filters, sorting, and pagination.

    IMPLEMENTATION:
    1. Call PropertyService.list_properties()
    2. Build PropertyListResponse with pagination metadata
    3. Return response
    """
    pass

@router.get("/{id}", response_model=PropertyDetailResponse)
async def get_property(
    id: UUID = Path(...),
    locale: str = Query("en"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get property detail with translations.

    IMPLEMENTATION:
    1. Call PropertyService.get_property_by_id()
    2. Raise HTTPException(404) if not found
    3. Get available locales via get_all_translations()
    4. Return PropertyDetailResponse
    """
    pass

@router.post("", response_model=PropertyResponse, status_code=201)
async def create_property(
    data: PropertyCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Create property (admin only).

    IMPLEMENTATION:
    1. Call PropertyService.create_property(data, current_user.id)
    2. Return PropertyResponse
    """
    pass

@router.put("/{id}", response_model=PropertyResponse)
async def update_property(
    id: UUID = Path(...),
    data: PropertyUpdate,
    current_user: User = Depends(get_clerk_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update property (admin or owner).

    IMPLEMENTATION:
    1. Call PropertyService.update_property(id, data, current_user.id)
    2. Return PropertyResponse
    """
    pass

@router.delete("/{id}", response_model=MessageResponse)
async def delete_property(
    id: UUID = Path(...),
    current_user: User = Depends(get_clerk_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete property (admin or owner).

    IMPLEMENTATION:
    1. Call PropertyService.delete_property(id, current_user)
    2. Return success message
    """
    pass

@router.get("/{id}/translations", response_model=dict)
async def get_property_translations(
    id: UUID = Path(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all translations for a property.

    IMPLEMENTATION:
    1. Verify property exists
    2. Call PropertyService.get_all_translations(id)
    3. Return translations dict
    """
    pass

@router.put("/{id}/translations/{locale}", response_model=MessageResponse)
async def update_property_translations(
    id: UUID = Path(...),
    locale: str = Path(...),
    translations: dict[str, str],
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update translations for a specific locale (admin only).

    IMPLEMENTATION:
    1. Call PropertyService.update_translations(id, locale, translations)
    2. Return success message with fields_updated
    """
    pass
```

---

### E. Amenities Router (amenities.py)

**Location:** `apps/server/src/server/api/v1/endpoints/amenities.py`

```python
router = APIRouter(prefix="/amenities", tags=["amenities"])

@router.get("", response_model=list[AmenityResponse])
async def list_amenities(
    locale: str = Query("en"),
    category: str | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    List amenities with translations.

    IMPLEMENTATION:
    1. Call AmenityService.list_amenities(locale, category)
    2. Return list[AmenityResponse]
    """
    pass
```

---

### F. Policies Router (policies.py)

**Location:** `apps/server/src/server/api/v1/endpoints/policies.py`

```python
router = APIRouter(prefix="/policies", tags=["policies"])

@router.get("", response_model=list[PolicyResponse])
async def list_policies(
    locale: str = Query("en"),
    category: str | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    List policies with translations.

    IMPLEMENTATION:
    1. Call PolicyService.list_policies(locale, category)
    2. Return list[PolicyResponse]
    """
    pass
```

---

### G. Router Registration (router.py)

**File:** `apps/server/src/server/api/v1/router.py`

**Add these imports and registrations:**

```python
from server.api.v1.endpoints import properties, amenities, policies

# Register property endpoints
api_router.include_router(properties.router)

# Register amenity endpoints
api_router.include_router(amenities.router)

# Register policy endpoints
api_router.include_router(policies.router)
```

---

## Critical Implementation Details

### Translation Fallback Logic

```python
# Example for "title" field with locale="th":
# 1. Try Thai translation
translations = {"title": "วิลล่า", "description": "..."}  # from DB
property.title = translations.get("title")  # "วิลล่า"

# 2. If Thai missing, try EN
translations = {"description": "..."}  # No Thai title
property.title = translations_en.get("title", property.title)

# 3. If both missing, keep original
property.title = property.title  # Original from properties table
```

### JSONB Query Examples

```python
# Filter by bedrooms
stmt = stmt.where(
    Property.physical_specs['rooms']['bedrooms'].astext.cast(Integer) == bedrooms
)

# Filter by amenities (contains ALL)
for amenity_id in amenity_ids:
    stmt = stmt.where(
        Property.amenities.contains({"interior": [amenity_id]})
        | Property.amenities.contains({"exterior": [amenity_id]})
        | Property.amenities.contains({"building": [amenity_id]})
    )

# Filter by province
stmt = stmt.where(
    Property.location_details['administrative']['province_id'].astext == province
)
```

### Error Handling

```python
# 404 - Resource not found
if not property:
    raise HTTPException(status_code=404, detail="Property not found")

# 403 - Forbidden (ownership check)
if property.created_by != user.id and user.role != "admin":
    raise HTTPException(status_code=403, detail="Insufficient permissions")

# 400 - Business logic error
if data.transaction_type == "rent" and not data.rent_price:
    raise HTTPException(
        status_code=400,
        detail="Rent price is required when transaction_type is 'rent'"
    )

# 422 - Validation error (handled by Pydantic automatically)
```

---

## Testing Requirements

After implementation, test with these curl commands:

```bash
# 1. List amenities (should return seed data)
curl http://localhost:8011/api/v1/amenities?locale=en

# 2. List policies
curl http://localhost:8011/api/v1/policies?locale=th

# 3. List properties (empty initially)
curl http://localhost:8011/api/v1/properties?locale=en

# 4. Create property (requires admin token)
curl -X POST http://localhost:8011/api/v1/properties \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Villa with Private Pool",
    "description": "Beautiful 3-bedroom villa in Ari area with modern amenities and private swimming pool...",
    "transaction_type": "rent",
    "property_type": "villa",
    "rent_price": 30000,
    "currency": "THB",
    "physical_specs": {"rooms": {"bedrooms": 3, "bathrooms": 2}},
    "location_details": {"coordinates": {"latitude": 13.7563, "longitude": 100.5018}},
    "amenities": {"interior": ["air_conditioning", "wifi"]},
    "policies": {},
    "contact_info": {},
    "translations": {
      "th": {
        "title": "วิลล่าพร้อมสระส่วนตัว",
        "description": "วิลล่า 3 ห้องนอนสวยงามในย่านอารีย์..."
      }
    }
  }'

# 5. Get property detail
curl http://localhost:8011/api/v1/properties/<id>?locale=th

# 6. List properties with filters
curl "http://localhost:8011/api/v1/properties?transaction_type=rent&min_price=20000&max_price=50000&locale=en"
```

---

## File Header Template

Use this header for all service files:

```python
"""
<Service Name> - Property V2 Hybrid Localization

ARCHITECTURE:
  Layer: Service (Business Logic)
  Pattern: Service Layer
  Task: TASK-013 (US-023)

PATTERNS USED:
  - Service Layer: Encapsulates business logic
  - Repository Pattern: Database access abstraction
  - Hybrid Localization: DB translations + fallback chain

DEPENDENCIES:
  External: sqlalchemy, uuid
  Internal: server.models.property_v2, server.schemas.property_v2

INTEGRATION:
  - Database: PostgreSQL with JSONB and pgvector
  - Localization: property_translations table
  - Spec: .claude/tasks/TASK-013/planning/api-design.md

TESTING:
  - Coverage Target: 85%
  - Test File: tests/services/test_property_service.py
"""
```

---

## References

- **API Design:** `.claude/tasks/TASK-013/planning/api-design.md`
- **Data Model:** `.claude/tasks/TASK-013/planning/data-model-spec.md`
- **Implementation Plan:** `.claude/tasks/TASK-013/planning/implementation-plan.md`
- **Existing Patterns:** `apps/server/src/server/services/user_service.py`
- **Existing Router:** `apps/server/src/server/api/v1/endpoints/users.py`

---

## Success Criteria

✅ All 3 service files created with all methods implemented
✅ All 3 router files created with all endpoints implemented
✅ Routers registered in api/v1/router.py
✅ Translation fallback logic works correctly
✅ JSONB filtering works for all query parameters
✅ Error handling implemented (404, 403, 400, 422)
✅ All curl tests return correct responses
✅ OpenAPI docs auto-generated at http://localhost:8011/docs

---

## Next Steps After Completion

1. Create unit tests (Phase 7)
2. Create integration tests (Phase 7)
3. Performance testing with 10k properties
4. Document any issues encountered
5. Report completion with files created and test results

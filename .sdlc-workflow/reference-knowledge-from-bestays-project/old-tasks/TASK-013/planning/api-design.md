# API Design: Property V2 Endpoints

**TASK:** TASK-013
**Story:** US-023
**Date:** 2025-11-09
**Author:** Claude Code (Coordinator)

---

## Overview

This document specifies all FastAPI endpoints for Property V2 with hybrid localization support. All endpoints support multi-language responses via `Accept-Language` header or `?locale` query parameter.

**Base Path:** `/api/v1/properties`

**Localization Strategy:**
- Accept both `Accept-Language` header and `?locale` query param
- Query param takes precedence
- Fallback chain: requested locale → EN → property fallback
- Supported locales: `en`, `th` (extensible)

---

## Endpoints Summary

| Method | Endpoint | Auth Required | Purpose |
|--------|----------|---------------|---------|
| GET | `/properties` | No | List/search properties |
| GET | `/properties/{id}` | No | Get property detail |
| POST | `/properties` | Yes (Admin) | Create property |
| PUT | `/properties/{id}` | Yes (Admin/Owner) | Update property |
| DELETE | `/properties/{id}` | Yes (Admin/Owner) | Soft delete property |
| GET | `/properties/{id}/translations` | No | Get all translations |
| PUT | `/properties/{id}/translations/{locale}` | Yes (Admin) | Update translations |
| GET | `/amenities` | No | List all amenities |
| GET | `/policies` | No | List all policies |

---

## Common Headers

### Request Headers

```
Accept-Language: th-TH,th;q=0.9,en;q=0.8
Authorization: Bearer <jwt_token>  # For protected endpoints
Content-Type: application/json
```

### Response Headers

```
Content-Type: application/json
Content-Language: th  # Language of response
X-Total-Count: 150    # Total results (for pagination)
X-Page: 1             # Current page
X-Per-Page: 24        # Items per page
```

---

## 1. List Properties (GET /properties)

### Description
List and search properties with filtering, sorting, and pagination. Returns properties with translations merged based on requested locale.

### Request

```http
GET /api/v1/properties?locale=th&transaction_type=rent&min_price=20000&max_price=50000&bedrooms=3&amenities=wifi,pool&page=1&per_page=24
```

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `locale` | string | No | `en` | Locale for translations (en, th) |
| `transaction_type` | string | No | All | Filter: rent, sale, lease |
| `property_type` | string | No | All | Filter: villa, condo, apartment, etc. |
| `min_price` | integer | No | 0 | Minimum price (THB, not satang) |
| `max_price` | integer | No | ∞ | Maximum price (THB, not satang) |
| `bedrooms` | integer | No | - | Number of bedrooms |
| `bathrooms` | integer | No | - | Number of bathrooms |
| `min_area` | float | No | - | Minimum usable area (sqm) |
| `province` | string | No | - | Province ID (e.g., "bangkok") |
| `district` | string | No | - | District ID |
| `amenities` | string | No | - | Comma-separated amenity IDs |
| `tags` | string | No | - | Comma-separated tags |
| `is_featured` | boolean | No | - | Filter featured properties |
| `sort_by` | string | No | `priority` | Sort: priority, price_asc, price_desc, newest, oldest |
| `page` | integer | No | 1 | Page number (1-indexed) |
| `per_page` | integer | No | 24 | Items per page (max 100) |

### Response (200 OK)

```json
{
  "properties": [
    {
      "id": "e3b0c442-98fc-4c83-b3e5-f1c6e2d3a4b5",
      "title": "วิลล่าโมเดิร์นพร้อมสระส่วนตัว",
      "description": "วิลล่า 3 ห้องนอนสวยงามในย่านอารีย์...",
      "transaction_type": "rent",
      "property_type": "villa",
      "rent_price": 30000,
      "currency": "THB",
      "physical_specs": {
        "rooms": {
          "bedrooms": 3,
          "bathrooms": 2,
          "parking_spaces": 2
        },
        "sizes": {
          "usable_area_sqm": 180.5,
          "land_area_sqm": 250.0
        },
        "floors": {
          "total_floors": 2
        },
        "year_built": 2020,
        "furnishing": "fully_furnished",
        "condition": "excellent"
      },
      "location_details": {
        "coordinates": {
          "latitude": 13.7563,
          "longitude": 100.5018
        },
        "administrative": {
          "province_id": "bangkok",
          "province_name": "กรุงเทพมหานคร",
          "district_id": "phaya_thai",
          "district_name": "พญาไท",
          "postal_code": "10400"
        }
      },
      "amenities": {
        "interior": ["air_conditioning", "wifi", "kitchen_appliances"],
        "exterior": ["pool", "garden"],
        "building": ["security_24h", "parking"]
      },
      "policies": {
        "lease_terms": {
          "lease_duration_months": 12,
          "deposit_months": 2
        },
        "house_rules": {
          "pets_allowed": false,
          "smoking_allowed": false
        }
      },
      "contact_info": {
        "phone": "+66812345678",
        "line_id": "@bestays",
        "preferred_contact": "line"
      },
      "cover_image": {
        "url": "https://cdn.bestays.app/properties/e3b0.../cover.jpg",
        "alt": "Modern villa exterior",
        "width": 1200,
        "height": 800
      },
      "tags": ["pet-friendly", "near-bts", "luxury"],
      "is_published": true,
      "is_featured": true,
      "listing_priority": 10,
      "created_at": "2025-11-01T10:00:00Z",
      "updated_at": "2025-11-08T15:30:00Z"
    }
  ],
  "pagination": {
    "total": 150,
    "page": 1,
    "per_page": 24,
    "pages": 7
  },
  "locale": "th"
}
```

### Pydantic Models

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

# Request (Query Parameters)
class PropertyListQuery(BaseModel):
    locale: str = "en"
    transaction_type: Optional[str] = None
    property_type: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    min_area: Optional[float] = None
    province: Optional[str] = None
    district: Optional[str] = None
    amenities: Optional[str] = None  # "wifi,pool,garden"
    tags: Optional[str] = None  # "luxury,pet-friendly"
    is_featured: Optional[bool] = None
    sort_by: str = "priority"
    page: int = Field(1, ge=1)
    per_page: int = Field(24, ge=1, le=100)

# Response
class PhysicalSpecs(BaseModel):
    rooms: Optional[Dict[str, int]] = None
    sizes: Optional[Dict[str, float]] = None
    floors: Optional[Dict[str, int]] = None
    year_built: Optional[int] = None
    furnishing: Optional[str] = None
    condition: Optional[str] = None

class LocationDetails(BaseModel):
    coordinates: Optional[Dict[str, float]] = None
    administrative: Optional[Dict[str, str]] = None
    address: Optional[Dict[str, str]] = None
    nearby_landmarks: Optional[List[Dict[str, Any]]] = None

class ImageObject(BaseModel):
    url: str
    alt: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    size_bytes: Optional[int] = None

class PropertyResponse(BaseModel):
    id: UUID
    title: str
    description: str
    transaction_type: str
    property_type: str
    rent_price: Optional[int] = None
    sale_price: Optional[int] = None
    lease_price: Optional[int] = None
    currency: str
    physical_specs: PhysicalSpecs
    location_details: LocationDetails
    amenities: Dict[str, List[str]]
    policies: Dict[str, Dict[str, Any]]
    contact_info: Dict[str, Any]
    cover_image: Optional[ImageObject] = None
    images: List[ImageObject] = []
    tags: List[str] = []
    is_published: bool
    is_featured: bool
    listing_priority: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int
    pages: int

class PropertyListResponse(BaseModel):
    properties: List[PropertyResponse]
    pagination: PaginationMeta
    locale: str
```

### Error Responses

```json
// 400 Bad Request - Invalid parameters
{
  "detail": "Invalid sort_by value. Must be one of: priority, price_asc, price_desc, newest, oldest"
}

// 422 Validation Error
{
  "detail": [
    {
      "loc": ["query", "per_page"],
      "msg": "ensure this value is less than or equal to 100",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

## 2. Get Property Detail (GET /properties/{id})

### Description
Get single property with full details and translations for specified locale.

### Request

```http
GET /api/v1/properties/e3b0c442-98fc-4c83-b3e5-f1c6e2d3a4b5?locale=th
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | UUID | Yes | Property UUID |

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `locale` | string | No | `en` | Locale for translations |

### Response (200 OK)

```json
{
  "property": {
    "id": "e3b0c442-98fc-4c83-b3e5-f1c6e2d3a4b5",
    "title": "วิลล่าโมเดิร์นพร้อมสระส่วนตัว",
    "description": "วิลล่า 3 ห้องนอนสวยงามในย่านอารีย์...",
    "transaction_type": "rent",
    "property_type": "villa",
    "rent_price": 30000,
    "currency": "THB",
    "physical_specs": { /* ... */ },
    "location_details": { /* ... */ },
    "amenities": { /* ... */ },
    "policies": { /* ... */ },
    "contact_info": { /* ... */ },
    "cover_image": { /* ... */ },
    "images": [ /* ... */ ],
    "tags": ["pet-friendly", "near-bts", "luxury"],
    "is_published": true,
    "is_featured": true,
    "listing_priority": 10,
    "created_at": "2025-11-01T10:00:00Z",
    "updated_at": "2025-11-08T15:30:00Z"
  },
  "locale": "th",
  "available_locales": ["en", "th"]
}
```

### Pydantic Models

```python
class PropertyDetailResponse(BaseModel):
    property: PropertyResponse
    locale: str
    available_locales: List[str]
```

### Error Responses

```json
// 404 Not Found
{
  "detail": "Property not found"
}

// 410 Gone - Soft deleted
{
  "detail": "Property has been removed"
}
```

---

## 3. Create Property (POST /properties)

### Description
Create new property with optional translations. Admin only.

### Request

```http
POST /api/v1/properties
Authorization: Bearer <admin_token>
Content-Type: application/json
```

```json
{
  "title": "Modern Villa with Private Pool",
  "description": "Beautiful 3-bedroom villa in Ari area...",
  "transaction_type": "rent",
  "property_type": "villa",
  "rent_price": 30000,
  "currency": "THB",
  "physical_specs": {
    "rooms": {"bedrooms": 3, "bathrooms": 2, "parking_spaces": 2},
    "sizes": {"usable_area_sqm": 180.5, "land_area_sqm": 250.0},
    "floors": {"total_floors": 2},
    "year_built": 2020,
    "furnishing": "fully_furnished",
    "condition": "excellent"
  },
  "location_details": {
    "coordinates": {"latitude": 13.7563, "longitude": 100.5018},
    "administrative": {
      "province_id": "bangkok",
      "district_id": "phaya_thai",
      "postal_code": "10400"
    }
  },
  "amenities": {
    "interior": ["air_conditioning", "wifi", "kitchen_appliances"],
    "exterior": ["pool", "garden"],
    "building": ["security_24h", "parking"]
  },
  "policies": {
    "lease_terms": {"lease_duration_months": 12, "deposit_months": 2},
    "house_rules": {"pets_allowed": false, "smoking_allowed": false}
  },
  "contact_info": {
    "phone": "+66812345678",
    "line_id": "@bestays",
    "preferred_contact": "line"
  },
  "cover_image": {
    "url": "https://cdn.bestays.app/properties/uuid/cover.jpg",
    "alt": "Modern villa exterior",
    "width": 1200,
    "height": 800
  },
  "tags": ["pet-friendly", "near-bts", "luxury"],
  "is_published": false,
  "is_featured": false,
  "listing_priority": 0,
  "translations": {
    "th": {
      "title": "วิลล่าโมเดิร์นพร้อมสระส่วนตัว",
      "description": "วิลล่า 3 ห้องนอนสวยงามในย่านอารีย์...",
      "location_province": "กรุงเทพมหานคร",
      "location_district": "พญาไท"
    }
  }
}
```

### Pydantic Models

```python
class PropertyCreate(BaseModel):
    title: str = Field(..., min_length=10, max_length=255)
    description: str = Field(..., min_length=50, max_length=5000)
    transaction_type: str  # Validated in service layer
    property_type: str
    rent_price: Optional[int] = Field(None, gt=0)
    sale_price: Optional[int] = Field(None, gt=0)
    lease_price: Optional[int] = Field(None, gt=0)
    currency: str = "THB"
    physical_specs: PhysicalSpecs
    location_details: LocationDetails
    amenities: Dict[str, List[str]]
    policies: Dict[str, Dict[str, Any]]
    contact_info: Dict[str, Any]
    cover_image: Optional[ImageObject] = None
    images: List[ImageObject] = []
    tags: List[str] = []
    is_published: bool = False
    is_featured: bool = False
    listing_priority: int = Field(0, ge=0, le=999)
    translations: Optional[Dict[str, Dict[str, str]]] = None  # {locale: {field: value}}
```

### Response (201 Created)

```json
{
  "property": { /* PropertyResponse */ },
  "message": "Property created successfully"
}
```

### Error Responses

```json
// 401 Unauthorized
{
  "detail": "Not authenticated"
}

// 403 Forbidden
{
  "detail": "Insufficient permissions. Admin role required."
}

// 422 Validation Error
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at least 10 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}

// 400 Bad Request - Business logic
{
  "detail": "Rent price is required when transaction_type is 'rent'"
}
```

---

## 4. Update Property (PUT /properties/{id})

### Description
Update existing property. Admin or property owner only.

### Request

```http
PUT /api/v1/properties/e3b0c442-98fc-4c83-b3e5-f1c6e2d3a4b5
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "rent_price": 35000,
  "is_published": true,
  "listing_priority": 10,
  "translations": {
    "th": {
      "title": "วิลล่าโมเดิร์นพร้อมสระส่วนตัว (อัปเดต)"
    }
  }
}
```

### Pydantic Models

```python
class PropertyUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=10, max_length=255)
    description: Optional[str] = Field(None, min_length=50, max_length=5000)
    transaction_type: Optional[str] = None
    property_type: Optional[str] = None
    rent_price: Optional[int] = Field(None, gt=0)
    sale_price: Optional[int] = Field(None, gt=0)
    lease_price: Optional[int] = Field(None, gt=0)
    currency: Optional[str] = None
    physical_specs: Optional[PhysicalSpecs] = None
    location_details: Optional[LocationDetails] = None
    amenities: Optional[Dict[str, List[str]]] = None
    policies: Optional[Dict[str, Dict[str, Any]]] = None
    contact_info: Optional[Dict[str, Any]] = None
    cover_image: Optional[ImageObject] = None
    images: Optional[List[ImageObject]] = None
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None
    listing_priority: Optional[int] = Field(None, ge=0, le=999)
    translations: Optional[Dict[str, Dict[str, str]]] = None
```

### Response (200 OK)

```json
{
  "property": { /* PropertyResponse */ },
  "message": "Property updated successfully"
}
```

### Error Responses

```json
// 404 Not Found
{
  "detail": "Property not found"
}

// 403 Forbidden
{
  "detail": "You don't have permission to edit this property"
}
```

---

## 5. Delete Property (DELETE /properties/{id})

### Description
Soft delete property (sets `deleted_at`). Admin or property owner only.

### Request

```http
DELETE /api/v1/properties/e3b0c442-98fc-4c83-b3e5-f1c6e2d3a4b5
Authorization: Bearer <token>
```

### Response (200 OK)

```json
{
  "message": "Property deleted successfully",
  "property_id": "e3b0c442-98fc-4c83-b3e5-f1c6e2d3a4b5"
}
```

### Error Responses

```json
// 404 Not Found
{
  "detail": "Property not found"
}

// 403 Forbidden
{
  "detail": "You don't have permission to delete this property"
}
```

---

## 6. Get All Translations (GET /properties/{id}/translations)

### Description
Get all available translations for a property. Useful for admin translation management.

### Request

```http
GET /api/v1/properties/e3b0c442-98fc-4c83-b3e5-f1c6e2d3a4b5/translations
```

### Response (200 OK)

```json
{
  "property_id": "e3b0c442-98fc-4c83-b3e5-f1c6e2d3a4b5",
  "translations": {
    "en": {
      "title": "Modern Villa with Private Pool",
      "description": "Beautiful 3-bedroom villa in Ari area...",
      "location_province": "Bangkok",
      "location_district": "Phaya Thai"
    },
    "th": {
      "title": "วิลล่าโมเดิร์นพร้อมสระส่วนตัว",
      "description": "วิลล่า 3 ห้องนอนสวยงามในย่านอารีย์...",
      "location_province": "กรุงเทพมหานคร",
      "location_district": "พญาไท"
    }
  },
  "available_locales": ["en", "th"],
  "missing_locales": []
}
```

---

## 7. Update Translations (PUT /properties/{id}/translations/{locale})

### Description
Update or create translations for a specific locale. Admin only.

### Request

```http
PUT /api/v1/properties/e3b0c442-98fc-4c83-b3e5-f1c6e2d3a4b5/translations/th
Authorization: Bearer <admin_token>
Content-Type: application/json
```

```json
{
  "title": "วิลล่าโมเดิร์นพร้อมสระส่วนตัว",
  "description": "วิลล่า 3 ห้องนอนสวยงามในย่านอารีย์...",
  "location_province": "กรุงเทพมหานคร",
  "location_district": "พญาไท"
}
```

### Response (200 OK)

```json
{
  "message": "Translations updated successfully",
  "property_id": "e3b0c442-98fc-4c83-b3e5-f1c6e2d3a4b5",
  "locale": "th",
  "fields_updated": ["title", "description", "location_province", "location_district"]
}
```

---

## 8. List Amenities (GET /amenities)

### Description
Get all available amenities with translations.

### Request

```http
GET /api/v1/amenities?locale=th&category=interior
```

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `locale` | string | No | `en` | Locale for translations |
| `category` | string | No | All | Filter: interior, exterior, building, area |

### Response (200 OK)

```json
{
  "amenities": [
    {
      "id": "air_conditioning",
      "name": "เครื่องปรับอากาศ",
      "category": "interior",
      "icon": "mdi:air-conditioner",
      "sort_order": 1
    },
    {
      "id": "wifi",
      "name": "ไวไฟ",
      "category": "interior",
      "icon": "mdi:wifi",
      "sort_order": 2
    }
  ],
  "locale": "th"
}
```

---

## 9. List Policies (GET /policies)

### Description
Get all available policies with translations.

### Request

```http
GET /api/v1/policies?locale=th&category=lease_terms
```

### Response (200 OK)

```json
{
  "policies": [
    {
      "id": "lease_duration_months",
      "name": "ระยะเวลาการเช่า",
      "description": "ระยะเวลาสัญญาเช่าเป็นเดือน",
      "category": "lease_terms",
      "data_type": "integer",
      "sort_order": 1
    },
    {
      "id": "deposit_months",
      "name": "เงินประกัน",
      "description": "เงินประกันเป็นจำนวนเดือนของค่าเช่า",
      "category": "lease_terms",
      "data_type": "integer",
      "sort_order": 2
    }
  ],
  "locale": "th"
}
```

---

## Service Layer Structure

```python
# apps/server/app/services/property_service.py

from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.property import Property, PropertyTranslation
from app.schemas.property import PropertyCreate, PropertyUpdate, PropertyListQuery

class PropertyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_properties(
        self,
        query: PropertyListQuery,
        locale: str = "en"
    ) -> tuple[List[Property], int]:
        """
        List properties with filters, pagination, and translations.

        Returns:
            (properties, total_count)
        """
        # Build base query with filters
        # Apply pagination
        # JOIN translations
        # Merge translations into property objects
        # Return (properties, total)
        pass

    async def get_property_by_id(
        self,
        property_id: UUID,
        locale: str = "en"
    ) -> Optional[Property]:
        """Get single property with translations."""
        pass

    async def create_property(
        self,
        data: PropertyCreate,
        created_by: int
    ) -> Property:
        """Create property with optional translations."""
        pass

    async def update_property(
        self,
        property_id: UUID,
        data: PropertyUpdate,
        updated_by: int
    ) -> Property:
        """Update property and translations."""
        pass

    async def delete_property(
        self,
        property_id: UUID
    ) -> bool:
        """Soft delete property."""
        pass

    async def get_all_translations(
        self,
        property_id: UUID
    ) -> Dict[str, Dict[str, str]]:
        """Get all translations for a property."""
        pass

    async def update_translations(
        self,
        property_id: UUID,
        locale: str,
        translations: Dict[str, str]
    ) -> None:
        """Upsert translations for a locale."""
        pass

    def _merge_translations(
        self,
        property: Property,
        translations: Dict[str, str],
        locale: str
    ) -> Property:
        """Merge translations into property object (fallback to EN)."""
        pass
```

---

## Authentication & Authorization

### Roles

| Endpoint | Public | User | Agent | Admin |
|----------|--------|------|-------|-------|
| GET /properties | ✅ | ✅ | ✅ | ✅ |
| GET /properties/{id} | ✅ | ✅ | ✅ | ✅ |
| POST /properties | ❌ | ❌ | ❌ | ✅ |
| PUT /properties/{id} | ❌ | Owner only | Owner only | ✅ |
| DELETE /properties/{id} | ❌ | Owner only | Owner only | ✅ |
| GET /properties/{id}/translations | ✅ | ✅ | ✅ | ✅ |
| PUT /properties/{id}/translations/{locale} | ❌ | ❌ | ❌ | ✅ |
| GET /amenities | ✅ | ✅ | ✅ | ✅ |
| GET /policies | ✅ | ✅ | ✅ | ✅ |

---

## Rate Limiting

```python
# Apply rate limits per endpoint
from slowapi import Limiter

# List endpoint (high traffic)
@limiter.limit("100/minute")
async def list_properties():
    pass

# Create endpoint (admin only, stricter)
@limiter.limit("10/minute")
async def create_property():
    pass
```

---

## Caching Strategy

### Cache Keys

```python
# Property detail (cache 5 minutes)
cache_key = f"property:{property_id}:{locale}"

# Property list (cache 1 minute)
cache_key = f"properties:list:{hash(query_params)}:{locale}"

# Amenities/Policies (cache 1 hour - rarely change)
cache_key = f"amenities:{category}:{locale}"
```

### Cache Invalidation

```python
# On property update/delete
await redis.delete(f"property:{property_id}:*")  # All locales
await redis.delete("properties:list:*")  # All list queries
```

---

## Future: Semantic Search Endpoint (Reserved)

**Reserved for US-024:**

```http
GET /api/v1/properties/search/semantic?q=modern+villa+near+BTS&locale=th
```

Response includes similarity scores and is sorted by relevance using pgvector embeddings.

---

## References

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Pydantic V2: https://docs.pydantic.dev/latest/
- SQLAlchemy 2.0: https://docs.sqlalchemy.org/en/20/

---

**Next Document:** implementation-plan.md (Step-by-step execution plan)

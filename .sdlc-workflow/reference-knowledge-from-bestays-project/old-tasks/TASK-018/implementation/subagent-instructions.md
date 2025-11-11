# Subagent Implementation Instructions - TASK-018

**Task:** Semantic Property Search - Phase 1A (Filter Extraction)
**Story:** US-027
**Subagent:** dev-backend-fastapi
**Estimated Time:** ~1 hour

---

## Objective

Implement natural language filter extraction service that converts queries like "big space for gf and dog, mountains" into structured property filters using OpenRouter LLM API.

---

## Complete File Specifications

### READ FIRST

The complete implementation code is in `.claude/tasks/TASK-018/planning/implementation-spec.md`. This document provides the file list and additional context.

---

## Files to Create

### 1. Config Updates

**File:** `apps/server/src/server/config.py`

**Add these fields to Settings class (after OPENAI settings, around line 83):**

```python
# OpenRouter (for semantic search filter extraction)
OPENROUTER_API_KEY: str = "change-me-in-production"
OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
```

---

### 2. Schema Updates

**File:** `apps/server/src/server/schemas/property_v2.py`

**Add this schema after PropertyListQuery (around line 113):**

```python
class PropertySearchQuery(BaseModel):
    """
    Extracted search filters from natural language query.

    Used by semantic search filter extraction service.
    All fields are optional as they are inferred from natural language.
    """

    transaction_type: str | None = None  # rent, sale, lease
    property_type: str | None = None  # villa, condo, apartment, house, townhouse
    bedrooms: int | None = None
    bathrooms: int | None = None
    min_area: float | None = None  # Square meters
    min_price: int | None = None  # THB/USD
    max_price: int | None = None
    province: str | None = None
    district: str | None = None
    amenities: list[str] = []  # Extracted amenity keywords
    tags: list[str] = []  # Extracted lifestyle/location tags
```

---

### 3. Service Layer - Search Package

**Folder:** Create `apps/server/src/server/services/search/`

#### File: `apps/server/src/server/services/search/__init__.py`

```python
"""Search services package."""
from .orchestrator import PropertySearchOrchestrator
from .filter_extraction_service import FilterExtractionService

__all__ = ["PropertySearchOrchestrator", "FilterExtractionService"]
```

#### File: `apps/server/src/server/services/search/filter_extraction_service.py`

**COMPLETE CODE:** See `.claude/tasks/TASK-018/planning/implementation-spec.md` lines 30-241

#### File: `apps/server/src/server/services/search/orchestrator.py`

**COMPLETE CODE:** See `.claude/tasks/TASK-018/planning/implementation-spec.md` lines 249-445

---

### 4. API Endpoint

#### File: `apps/server/src/server/api/v1/endpoints/search.py`

**COMPLETE CODE:** See `.claude/tasks/TASK-018/planning/implementation-spec.md` lines 453-576

---

### 5. Router Update

**File:** `apps/server/src/server/api/v1/router.py`

**Add import (near other endpoint imports):**

```python
from server.api.v1.endpoints import search
```

**Add router inclusion (where other routers are included):**

```python
api_router.include_router(search.router, prefix="/properties")
```

---

### 6. Test File

**File:** `apps/server/tests/api/v1/test_search.py`

**Create comprehensive tests covering:**

1. Filter extraction from simple query ("2BR condo")
2. Filter extraction from complex query ("big space for gf and dog, mountains")
3. Empty query returns all properties
4. Invalid query returns empty filters (graceful degradation)
5. Pagination works correctly
6. Locale affects results
7. Metadata includes extracted filters

**Test Structure:**

```python
"""
Tests for semantic search API endpoints.

ARCHITECTURE:
  Layer: API Test
  Pattern: Integration Testing
  Task: TASK-018 (US-027)
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestSemanticSearch:
    """Test suite for semantic search endpoint."""

    @pytest.mark.asyncio
    async def test_simple_query_extraction(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test filter extraction from simple query."""
        response = await client.post(
            "/api/v1/properties/search/semantic",
            json={"query": "2BR condo", "locale": "en"}
        )

        assert response.status_code == 200
        data = response.json()

        # Should extract bedrooms and property_type
        assert "metadata" in data
        assert "extracted_filters" in data["metadata"]
        filters = data["metadata"]["extracted_filters"]

        assert filters.get("bedrooms") == 2
        assert filters.get("property_type") == "condo"

    @pytest.mark.asyncio
    async def test_complex_query_extraction(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test filter extraction from complex natural language."""
        response = await client.post(
            "/api/v1/properties/search/semantic",
            json={
                "query": "big space for gf and dog, mountains",
                "locale": "en"
            }
        )

        assert response.status_code == 200
        data = response.json()

        filters = data["metadata"]["extracted_filters"]

        # Should infer couple = 2BR
        assert filters.get("bedrooms") == 2

        # Should extract pet amenity
        assert "pets_allowed" in filters.get("amenities", [])

        # Should extract location tag
        assert "mountain" in filters.get("tags", [])

    @pytest.mark.asyncio
    async def test_empty_query(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test empty query returns all properties."""
        response = await client.post(
            "/api/v1/properties/search/semantic",
            json={"query": "", "locale": "en"}
        )

        assert response.status_code == 200
        data = response.json()

        # Should return properties (empty filters)
        assert "properties" in data
        assert "pagination" in data

    @pytest.mark.asyncio
    async def test_pagination(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test pagination works correctly."""
        response = await client.post(
            "/api/v1/properties/search/semantic",
            json={
                "query": "villa",
                "locale": "en",
                "page": 1,
                "per_page": 10
            }
        )

        assert response.status_code == 200
        data = response.json()

        pagination = data["pagination"]
        assert pagination["page"] == 1
        assert pagination["per_page"] == 10
        assert "total" in pagination
        assert "pages" in pagination
```

---

## Implementation Order

1. ✅ Update `config.py` (add OpenRouter settings)
2. ✅ Update `property_v2.py` (add PropertySearchQuery schema)
3. ✅ Create `services/search/` folder
4. ✅ Implement `filter_extraction_service.py`
5. ✅ Implement `orchestrator.py`
6. ✅ Implement `search.py` API endpoint
7. ✅ Update `router.py`
8. ✅ Create `test_search.py`
9. ✅ Run tests

---

## Key Implementation Notes

### OpenRouter Integration

- Model: `meta-llama/llama-3.3-70b-instruct`
- Temperature: 0.1 (consistent extraction)
- Timeout: 10 seconds
- Graceful failure: Return empty filters if LLM fails

### Filter Extraction Logic

- **Bedrooms:** Infer from context
  - "couple" / "gf" / "boyfriend" → 2 bedrooms
  - "family" → 3+ bedrooms
  - "solo" / "alone" → 1 bedroom

- **Amenities:** Extract from keywords
  - "dog" / "cat" / "pet" → `pets_allowed`
  - "pool" → `pool`
  - "gym" / "fitness" → `gym`
  - "parking" → `parking`

- **Tags:** Extract location/lifestyle
  - "mountain" / "mountains" → `mountain`
  - "beach" / "seaside" → `beach`
  - "city" / "urban" → `city`
  - "quiet" → `quiet`
  - "family" → `family_friendly`

### Error Handling

- LLM API failure → Return empty `PropertySearchQuery()`
- JSON parse error → Return empty filters
- Invalid filters → Validate via Pydantic, ignore invalid fields
- Database errors → Let FastAPI exception handlers deal with it

### Response Format

```json
{
  "properties": [...],
  "pagination": {
    "total": 100,
    "page": 1,
    "per_page": 20,
    "pages": 5
  },
  "metadata": {
    "query": "big space for gf and dog, mountains",
    "components_used": ["filter_extraction"],
    "ranking_strategy": "basic",
    "extracted_filters": {
      "bedrooms": 2,
      "amenities": ["pets_allowed"],
      "tags": ["mountain"]
    }
  }
}
```

---

## Testing Requirements

### Manual Testing Command

```bash
# Start services
make dev

# Test endpoint
curl -X POST http://localhost:8011/api/v1/properties/search/semantic \
  -H "Content-Type: application/json" \
  -d '{"query": "big space for gf and dog, mountains", "locale": "en"}'
```

### Expected Response

- Response time: < 3 seconds
- Status: 200 OK
- Properties: Array of matching properties
- Metadata: Shows extracted filters
- Pagination: Correct page info

### Unit Tests

```bash
cd apps/server
pytest tests/api/v1/test_search.py -v
```

**Target:** >90% coverage

---

## Success Criteria

✅ FilterExtractionService extracts filters from natural language
✅ Orchestrator coordinates search (Phase 1A: filter extraction only)
✅ POST /properties/search/semantic endpoint works
✅ Tests pass with >90% coverage
✅ Response time < 3 seconds
✅ Metadata shows extracted filters
✅ Graceful error handling (LLM failures)

---

## Future Extensions (NOT in this task)

**Phase 1B:** Vector search with pgvector
**Phase 2:** Availability checking with booking calendar
**Phase 3:** Personalization based on user history

The orchestrator is designed to support these future components without re-architecture. Just add new services and append to `components=[]` array.

---

## References

- **Complete Code:** `.claude/tasks/TASK-018/planning/implementation-spec.md`
- **Architecture:** `.claude/tasks/TASK-018/planning/architecture-design.md`
- **Story:** `.sdlc-workflow/stories/US-027/STORY.md`

---

**READY FOR IMPLEMENTATION**

Launch command: `@subagent dev-backend-fastapi`

# Implementation Specification: Semantic Search

**Task:** TASK-018
**Story:** US-027
**Subagent:** dev-backend-fastapi
**Estimated Time:** 2.5 hours

---

## Phase 1A: Filter Extraction Service (1 hour)

### Files to Create

#### 1. `apps/server/src/server/services/search/__init__.py`

```python
"""Search services package."""
from .orchestrator import PropertySearchOrchestrator
from .filter_extraction_service import FilterExtractionService

__all__ = ["PropertySearchOrchestrator", "FilterExtractionService"]
```

---

#### 2. `apps/server/src/server/services/search/filter_extraction_service.py`

**Full File Content:**

```python
"""
Filter Extraction Service - Natural Language to Structured Filters

ARCHITECTURE:
  Layer: Service Layer
  Pattern: LLM-based extraction via OpenRouter
  Task: TASK-018 (US-027)

PATTERNS USED:
  - Service Layer: Business logic for filter extraction
  - LLM Integration: OpenRouter API for natural language understanding
  - JSON Schema: Structured output from LLM

DEPENDENCIES:
  External: httpx, pydantic
  Internal: server.schemas.property_v2 (PropertySearchQuery)

INTEGRATION:
  - OpenRouter: LLM-based filter extraction
  - Used by: PropertySearchOrchestrator

TESTING:
  - Coverage Target: 90%
  - Test File: tests/services/search/test_filter_extraction.py

FUTURE ENHANCEMENTS:
  - Date extraction: "november to january" → check_in/check_out dates
  - Budget extraction: "under 30000 baht" → max_price
  - Preference extraction: "quiet area" → tags/lifestyle keywords
"""

import json
from typing import Any

import httpx
from pydantic import BaseModel, ValidationError

from server.config import settings
from server.schemas.property_v2 import PropertySearchQuery


class FilterExtractionService:
    """
    Extract structured filters from natural language queries.

    Uses OpenRouter LLM API to understand user intent and extract
    searchable filters like bedrooms, amenities, location preferences.

    Example:
        service = FilterExtractionService()
        filters = await service.extract(
            "big space for gf and dog, mountains",
            locale="en"
        )
        # Returns: PropertySearchQuery(bedrooms=2, amenities=["pets_allowed"], ...)
    """

    def __init__(self):
        self.openrouter_api_key = settings.OPENROUTER_API_KEY
        self.openrouter_base_url = settings.OPENROUTER_BASE_URL or "https://openrouter.ai/api/v1"
        self.model = "meta-llama/llama-3.3-70b-instruct"  # Fast and accurate

    async def extract(self, query: str, locale: str = "en") -> PropertySearchQuery:
        """
        Extract structured filters from natural language query.

        Args:
            query: Natural language search query
            locale: Locale for context (en, th)

        Returns:
            PropertySearchQuery with extracted filters

        Example:
            >>> await service.extract("2BR condo with pool", "en")
            PropertySearchQuery(property_type="condo", bedrooms=2, amenities=["pool"])
        """

        # Build LLM prompt
        prompt = self._build_extraction_prompt(query, locale)

        # Call OpenRouter
        extracted_data = await self._call_llm(prompt)

        # Parse to PropertySearchQuery
        return self._parse_to_query(extracted_data)

    def _build_extraction_prompt(self, query: str, locale: str) -> str:
        """Build prompt for LLM filter extraction."""

        return f"""You are a real estate search assistant. Extract structured filters from this property search query.

Query: "{query}"
Locale: {locale}

Extract these optional fields and return ONLY valid JSON:

{{
  "transaction_type": "rent" | "sale" | "lease" | null,
  "property_type": "villa" | "condo" | "apartment" | "house" | "townhouse" | null,
  "bedrooms": integer (inferred from context, e.g., "couple" = 2) | null,
  "bathrooms": integer | null,
  "min_area": integer (square meters) | null,
  "min_price": integer (THB for th locale, USD for en) | null,
  "max_price": integer (THB for th locale, USD for en) | null,
  "province": string (Thailand province name) | null,
  "district": string | null,
  "amenities": array of amenity names like "pool", "gym", "parking", "pets_allowed" | null,
  "tags": array of lifestyle tags like "mountain", "beach", "city", "quiet", "family_friendly" | null
}}

IMPORTANT:
- Infer bedrooms from context: "couple" = 2, "family" = 3+, "solo" = 1
- Amenities: Extract from words like "pool", "gym", "parking", "pet", "dog", "cat"
- Tags: Extract location types (mountain, beach, city) and lifestyle (quiet, family)
- Return ONLY the JSON object, no explanations or markdown
- Use null for fields that cannot be determined

Examples:

Query: "big space for gf and dog, near markets, mountains"
{{
  "bedrooms": 2,
  "amenities": ["pets_allowed"],
  "tags": ["mountain", "local_market"]
}}

Query: "modern condo for remote work, quiet area, under 30000"
{{
  "property_type": "condo",
  "max_price": 30000,
  "amenities": ["home_office"],
  "tags": ["quiet", "modern"]
}}

Query: "villa with pool for family vacation in Phuket"
{{
  "property_type": "villa",
  "bedrooms": 3,
  "province": "Phuket",
  "amenities": ["pool"],
  "tags": ["family_friendly"]
}}

Now extract from: "{query}"
Return ONLY the JSON object:"""

    async def _call_llm(self, prompt: str) -> dict[str, Any]:
        """Call OpenRouter API for filter extraction."""

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.openrouter_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_api_key}",
                        "HTTP-Referer": "https://bestays.app",
                        "X-Title": "Bestays Property Search",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ],
                        "temperature": 0.1,  # Low temperature for consistent extraction
                        "max_tokens": 500,
                    },
                    timeout=10.0,
                )
                response.raise_for_status()

                data = response.json()
                content = data["choices"][0]["message"]["content"].strip()

                # Parse JSON from LLM response
                # Remove markdown code blocks if present
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]

                return json.loads(content)

            except (httpx.HTTPError, json.JSONDecodeError, KeyError) as e:
                # If LLM fails, return empty filters
                return {}

    def _parse_to_query(self, data: dict[str, Any]) -> PropertySearchQuery:
        """Parse extracted data to PropertySearchQuery."""

        try:
            return PropertySearchQuery(
                transaction_type=data.get("transaction_type"),
                property_type=data.get("property_type"),
                bedrooms=data.get("bedrooms"),
                bathrooms=data.get("bathrooms"),
                min_area=data.get("min_area"),
                min_price=data.get("min_price"),
                max_price=data.get("max_price"),
                province=data.get("province"),
                district=data.get("district"),
                amenities=data.get("amenities") or [],
                tags=data.get("tags") or [],
            )
        except ValidationError:
            # If validation fails, return empty query
            return PropertySearchQuery()
```

---

#### 3. `apps/server/src/server/services/search/orchestrator.py`

**Full File Content:**

```python
"""
Property Search Orchestrator - Composable Search System

ARCHITECTURE:
  Layer: Service Layer / Orchestrator
  Pattern: Strategy Pattern + Dependency Injection
  Task: TASK-018 (US-027)

PATTERNS USED:
  - Orchestrator Pattern: Coordinates multiple search components
  - Strategy Pattern: Pluggable ranking strategies
  - Dependency Injection: Components injected at runtime

DEPENDENCIES:
  External: sqlalchemy
  Internal: filter_extraction_service, property_service

INTEGRATION:
  - API: Used by POST /properties/search/semantic endpoint
  - Components: FilterExtractionService, VectorSearchService (Phase 1B)
  - Future: AvailabilityService, PersonalizationService

TESTING:
  - Coverage Target: 90%
  - Test File: tests/services/search/test_orchestrator.py

EXTENSIBILITY:
  - Add new components by passing to components=[] array
  - Add new ranking strategies in ranking/ module
  - No code changes needed for new features
"""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from server.schemas.property_v2 import (
    PropertyListQuery,
    PropertyListResponse,
    PropertyResponse,
)
from server.services.property_service import property_service
from server.services.search.filter_extraction_service import FilterExtractionService


class PropertySearchOrchestrator:
    """
    Orchestrates modular property search components.

    Coordinates filter extraction, vector search, availability checking,
    and personalization in a composable, extensible architecture.

    Components are enabled dynamically based on query type and available features.

    Example:
        orchestrator = PropertySearchOrchestrator(db_session)

        # Phase 1A: Filter extraction only
        results = await orchestrator.search(
            query="big space for gf and dog",
            components=["filter_extraction"],
            locale="en"
        )

        # Phase 1B: Hybrid (filter + semantic)
        results = await orchestrator.search(
            query="big space for gf and dog",
            components=["filter_extraction", "vector"],
            ranking="hybrid",
            locale="en"
        )

        # Phase 2 (future): Add availability
        results = await orchestrator.search(
            query="mountains, november to january",
            components=["filter_extraction", "vector", "availability"],
            ranking="availability_weighted",
            locale="en"
        )
    """

    def __init__(self, db: AsyncSession):
        self.db = db

        # Phase 1A: Initialize filter extraction
        self.filter_extractor = FilterExtractionService()

        # Phase 1B: Vector search (to be initialized)
        self.vector_search = None  # VectorSearchService(db) when implemented

        # Phase 2: Availability service (future)
        self.availability = None  # AvailabilityService(db) when ready

        # Phase 3: Personalization service (future)
        self.personalization = None  # PersonalizationService(db) when ready

    async def search(
        self,
        query: str,
        components: list[str] = ["filter_extraction"],
        ranking: str = "basic",
        locale: str = "en",
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[PropertyResponse], int, dict[str, Any]]:
        """
        Execute property search with specified components.

        Args:
            query: Natural language search query
            components: List of components to use:
                - "filter_extraction": LLM extracts filters from query (Phase 1A)
                - "vector": Semantic vector search (Phase 1B)
                - "availability": Date availability checking (Phase 2)
                - "personalization": User history ranking (Phase 3)
            ranking: Ranking strategy ("basic", "hybrid", "availability", "ml")
            locale: Locale for translations (en, th)
            page: Page number (1-indexed)
            per_page: Items per page

        Returns:
            Tuple of (properties, total_count, metadata)

        Example:
            >>> results, total, meta = await orchestrator.search(
            ...     query="2BR with pool",
            ...     components=["filter_extraction"],
            ...     locale="en"
            ... )
        """

        metadata: dict[str, Any] = {
            "query": query,
            "components_used": components,
            "ranking_strategy": ranking,
        }

        # Step 1: Extract filters from natural language (if enabled)
        filters = None
        if "filter_extraction" in components:
            filters = await self.filter_extractor.extract(query, locale)
            metadata["extracted_filters"] = filters.model_dump(exclude_none=True)

        # Step 2: Build PropertyListQuery
        list_query = PropertyListQuery(
            transaction_type=filters.transaction_type if filters else None,
            property_type=filters.property_type if filters else None,
            bedrooms=filters.bedrooms if filters else None,
            bathrooms=filters.bathrooms if filters else None,
            min_area=filters.min_area if filters else None,
            min_price=filters.min_price if filters else None,
            max_price=filters.max_price if filters else None,
            province=filters.province if filters else None,
            district=filters.district if filters else None,
            amenities=",".join(filters.amenities) if filters and filters.amenities else None,
            tags=",".join(filters.tags) if filters and filters.tags else None,
            page=page,
            per_page=per_page,
        )

        # Step 3: Get properties from database
        properties, total = await property_service.list_properties(
            db=self.db,
            query=list_query,
            locale=locale,
        )

        # Step 4: Vector search (Phase 1B - not implemented yet)
        if "vector" in components and self.vector_search:
            # properties = await self.vector_search.rank_by_similarity(
            #     query=query,
            #     candidates=properties,
            #     locale=locale
            # )
            pass

        # Step 5: Availability filtering (Phase 2 - future)
        if "availability" in components and self.availability:
            # properties = await self.availability.filter_available(
            #     properties=properties,
            #     check_in=filters.check_in,
            #     check_out=filters.check_out
            # )
            pass

        # Step 6: Personalization ranking (Phase 3 - future)
        if "personalization" in components and self.personalization:
            # properties = await self.personalization.rerank(
            #     properties=properties,
            #     user_id=filters.user_id
            # )
            pass

        return properties, total, metadata
```

---

#### 4. `apps/server/src/server/api/v1/endpoints/search.py`

**Full File Content:**

```python
"""
Search API Endpoints - Natural Language Property Search

ARCHITECTURE:
  Layer: API Endpoint
  Pattern: RESTful API with Natural Language Processing
  Task: TASK-018 (US-027)

PATTERNS USED:
  - REST Pattern: Resource-based URL design
  - Dependency Injection: FastAPI Depends for DB
  - Async/Await: Non-blocking search operations

DEPENDENCIES:
  External: fastapi, sqlalchemy
  Internal: server.services.search.orchestrator

INTEGRATION:
  - Search Service: PropertySearchOrchestrator
  - Database: Property queries via orchestrator

TESTING:
  - Coverage Target: 90%
  - Test File: tests/api/v1/test_search.py

Endpoints:
  - POST /search/semantic - Natural language property search
"""

import math
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from server.api.deps import get_db
from server.schemas.property_v2 import PaginationMeta, PropertyResponse
from server.services.search.orchestrator import PropertySearchOrchestrator

router = APIRouter(prefix="/search", tags=["search"])


class SemanticSearchRequest(BaseModel):
    """Natural language search request."""

    query: str
    locale: str = "en"
    page: int = 1
    per_page: int = 20


class SemanticSearchResponse(BaseModel):
    """Natural language search response with metadata."""

    properties: list[PropertyResponse]
    pagination: PaginationMeta
    metadata: dict[str, Any]


@router.post("/semantic", response_model=SemanticSearchResponse)
async def semantic_search(
    request: SemanticSearchRequest,
    db: AsyncSession = Depends(get_db),
) -> SemanticSearchResponse:
    """
    Natural language property search.

    Public endpoint - no authentication required.
    Uses LLM to extract filters from natural language queries.

    Request Body:
        SemanticSearchRequest:
            - query: Natural language search (e.g., "2BR with pool near beach")
            - locale: Language code (en, th)
            - page: Page number (1-indexed)
            - per_page: Items per page (max 100)

    Returns:
        SemanticSearchResponse:
            - properties: Matching properties
            - pagination: Pagination metadata
            - metadata: Query understanding and extracted filters

    Example:
        POST /api/v1/search/semantic
        {
            "query": "big space for gf and dog, mountains",
            "locale": "en",
            "page": 1,
            "per_page": 20
        }
    """

    # Initialize orchestrator
    orchestrator = PropertySearchOrchestrator(db)

    # Execute search (Phase 1A: filter extraction only)
    properties, total, metadata = await orchestrator.search(
        query=request.query,
        components=["filter_extraction"],  # Phase 1B: add "vector"
        ranking="basic",  # Phase 1B: change to "hybrid"
        locale=request.locale,
        page=request.page,
        per_page=request.per_page,
    )

    # Calculate pagination
    pages = math.ceil(total / request.per_page) if total > 0 else 0

    pagination = PaginationMeta(
        total=total,
        page=request.page,
        per_page=request.per_page,
        pages=pages,
    )

    return SemanticSearchResponse(
        properties=[PropertyResponse.model_validate(p) for p in properties],
        pagination=pagination,
        metadata=metadata,
    )
```

---

#### 5. Update `apps/server/src/server/api/v1/router.py`

Add search router:

```python
from server.api.v1.endpoints import search

# Add to router includes
api_router.include_router(search.router, prefix="/properties")
```

---

### Testing Requirements

Create test file: `apps/server/tests/api/v1/test_search.py`

**Test Cases:**
1. Test filter extraction from simple query ("2BR condo")
2. Test filter extraction from complex query ("big space for gf and dog, mountains")
3. Test empty query returns all properties
4. Test invalid query returns empty filters
5. Test pagination works correctly
6. Test locale affects results

---

## Phase 1B: Vector Search (1.5 hours)

**NOTE:** Phase 1B implementation will be in a separate planning session after Phase 1A is complete and tested.

**Overview:**
1. Create PropertyEmbeddingService (similar to FAQEmbeddingService)
2. Create migration to enable vector columns
3. Create backfill script
4. Create VectorSearchService
5. Update orchestrator to use vector search

---

## Implementation Order

1. Create folder structure: `services/search/`, `services/embeddings/`
2. Implement FilterExtractionService
3. Implement PropertySearchOrchestrator (basic, Phase 1A only)
4. Implement search API endpoint
5. Update router to include search endpoint
6. Write tests
7. Test manually with example queries
8. Document API in Swagger

---

## Testing Commands

```bash
# Run tests
cd apps/server
pytest tests/api/v1/test_search.py -v

# Test manually
curl -X POST http://localhost:8011/api/v1/properties/search/semantic \
  -H "Content-Type: application/json" \
  -d '{"query": "2BR condo with pool", "locale": "en"}'
```

---

## Success Criteria

- [ ] FilterExtractionService extracts correct filters from natural language
- [ ] Orchestrator coordinates search components
- [ ] API endpoint returns results with metadata
- [ ] Tests pass with > 90% coverage
- [ ] Manual testing shows correct filter extraction
- [ ] Response time < 3 seconds
- [ ] OpenRouter API integration works

---

**Status:** Ready for implementation
**Next:** Launch dev-backend-fastapi subagent

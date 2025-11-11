# Testing Phase - Subagent Instructions
## TASK-018 (US-027 Semantic Property Search)

**Agent:** dev-backend-fastapi
**Phase:** TESTING
**Coverage Target:** ≥80% line, ≥75% branch
**Execution Time Target:** < 30 seconds

---

## Mission

Implement comprehensive test suite for semantic property search implementation (Phase 1A + Phase 1B).

**Current Status:**
- ✅ Phase 1A implemented: FilterExtractionService, PropertySearchOrchestrator (filter extraction)
- ✅ Phase 1B implemented: PropertyEmbeddingService, VectorSearchService, hybrid ranking
- ✅ API endpoint implemented: POST /api/v1/properties/search/semantic
- ⚠️ Test coverage: 0% (only API integration tests exist)

**Goal:** Achieve ≥80% test coverage with comprehensive unit and integration tests.

---

## Files Requiring Tests

### Phase 1A Components
1. `apps/server/src/server/services/search/filter_extraction_service.py`
2. `apps/server/src/server/services/search/orchestrator.py` (Phase 1A parts)
3. `apps/server/src/server/api/v1/endpoints/search.py`

### Phase 1B Components
4. `apps/server/src/server/services/search/embedding_service.py`
5. `apps/server/src/server/services/search/vector_search_service.py`
6. `apps/server/src/server/services/search/orchestrator.py` (Phase 1B parts)
7. `apps/server/scripts/backfill_property_embeddings.py`

### Existing Test File (EXPAND)
- `apps/server/tests/api/v1/test_search.py` (currently has Phase 1A integration tests)

---

## Test Files to Create

### 1. Unit Tests for FilterExtractionService

**File:** `apps/server/tests/services/search/test_filter_extraction_service.py`

**Required Test Cases:**

```python
import pytest
from unittest.mock import AsyncMock, patch
from server.services.search.filter_extraction_service import FilterExtractionService
from server.schemas.property_v2 import PropertySearchQuery


class TestFilterExtractionService:
    """Unit tests for FilterExtractionService."""

    @pytest.mark.asyncio
    async def test_extract_simple_query(self):
        """Test basic filter extraction (2BR condo)."""
        # Mock OpenRouter API response
        # Expected filters: property_type="condo", bedrooms=2
        pass

    @pytest.mark.asyncio
    async def test_extract_complex_query(self):
        """Test complex natural language (big space for gf and dog)."""
        # Mock OpenRouter API response
        # Expected: bedrooms=2, amenities=["pets_allowed"], tags=["mountain"]
        pass

    @pytest.mark.asyncio
    async def test_extract_empty_query(self):
        """Test empty string returns empty filters."""
        # Should return PropertySearchQuery() with no filters
        pass

    @pytest.mark.asyncio
    async def test_extract_with_amenities(self):
        """Test amenity extraction (pool, gym, parking)."""
        # Query: "condo with pool and gym"
        # Expected: amenities=["pool", "gym"]
        pass

    @pytest.mark.asyncio
    async def test_extract_with_location(self):
        """Test location tag extraction (beach, mountain, city)."""
        # Query: "villa near beach"
        # Expected: tags=["beach"], property_type="villa"
        pass

    @pytest.mark.asyncio
    async def test_extract_bedrooms_inference(self):
        """Test bedroom inference (couple→2BR, family→3BR)."""
        # Query: "apartment for family"
        # Expected: bedrooms=3
        pass

    @pytest.mark.asyncio
    async def test_llm_failure_graceful_degradation(self):
        """Test graceful failure when LLM API fails."""
        # Mock httpx.HTTPError
        # Should return empty PropertySearchQuery()
        pass

    @pytest.mark.asyncio
    async def test_invalid_json_response(self):
        """Test handling of malformed LLM responses."""
        # Mock invalid JSON from LLM
        # Should return empty PropertySearchQuery()
        pass

    @pytest.mark.asyncio
    async def test_markdown_code_block_stripping(self):
        """Test LLM response with markdown code blocks is parsed."""
        # Mock response: "```json\n{...}\n```"
        # Should parse correctly
        pass
```

**Mocking Strategy:**
```python
@pytest.fixture
def mock_openrouter():
    """Mock OpenRouter API calls."""
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": '{"bedrooms": 2, "property_type": "condo"}'
                }
            }]
        }
        mock_post.return_value = mock_response
        yield mock_post
```

---

### 2. Unit Tests for PropertyEmbeddingService

**File:** `apps/server/tests/services/search/test_embedding_service.py`

**Required Test Cases:**

```python
import pytest
import numpy as np
from server.services.search.embedding_service import PropertyEmbeddingService
from server.models.property_v2 import PropertyV2


class TestPropertyEmbeddingService:
    """Unit tests for PropertyEmbeddingService."""

    @pytest.mark.asyncio
    async def test_generate_embedding_mock_mode(self):
        """Test mock embedding generation (OPENAI_API_KEY not set)."""
        # Service should use mock mode by default in tests
        # Verify embedding is 1536 dimensions
        pass

    @pytest.mark.asyncio
    async def test_generate_embedding_deterministic(self):
        """Test same text produces same mock embedding."""
        # Generate twice with same text
        # Should return identical vectors
        pass

    @pytest.mark.asyncio
    async def test_generate_embedding_normalized(self):
        """Test mock embeddings are normalized (length ~1.0)."""
        # Calculate L2 norm: np.linalg.norm(embedding)
        # Should be close to 1.0
        pass

    @pytest.mark.asyncio
    async def test_generate_property_embedding_combines_text(self):
        """Test property embedding combines title+desc+amenities+tags."""
        # Create property with all fields
        # Verify embedding generated from combined text
        pass

    @pytest.mark.asyncio
    async def test_empty_text_returns_none(self):
        """Test empty text returns None."""
        # Call with ""
        # Should return None
        pass

    @pytest.mark.asyncio
    async def test_property_with_amenities_list(self):
        """Test property amenities are included in embedding text."""
        # Property with amenities: {"interior": ["wifi"], "exterior": ["pool"]}
        # Verify amenities appear in combined text
        pass

    @pytest.mark.asyncio
    async def test_property_with_tags(self):
        """Test property tags are included in embedding text."""
        # Property with tags: ["luxury", "mountain"]
        # Verify tags appear in combined text
        pass

    @pytest.mark.asyncio
    async def test_property_without_description_returns_none(self):
        """Test property with no text returns None."""
        # Property with empty title, description, no amenities/tags
        # Should return None (warning logged)
        pass
```

**Note:** These tests should run in mock mode (without OPENAI_API_KEY). Real OpenAI tests can be skipped.

---

### 3. Unit Tests for VectorSearchService

**File:** `apps/server/tests/services/search/test_vector_search_service.py`

**Required Test Cases:**

```python
import pytest
from server.services.search.vector_search_service import VectorSearchService
from server.models.property_v2 import PropertyV2


class TestVectorSearchService:
    """Unit tests for VectorSearchService."""

    @pytest.mark.asyncio
    async def test_search_by_similarity_returns_sorted(self, db_session):
        """Test results sorted by similarity score (descending)."""
        # Create 3 properties with embeddings
        # Query should return sorted by cosine similarity
        pass

    @pytest.mark.asyncio
    async def test_search_by_similarity_filters_threshold(self, db_session):
        """Test similarity threshold filtering."""
        # Create properties with varying similarity scores
        # threshold=0.7 should filter out low scores
        pass

    @pytest.mark.asyncio
    async def test_search_by_similarity_no_embeddings(self, db_session):
        """Test graceful handling when no properties have embeddings."""
        # Create properties without embeddings
        # Should return empty list
        pass

    @pytest.mark.asyncio
    async def test_search_by_similarity_respects_locale(self, db_session):
        """Test EN vs TH embedding column selection."""
        # Create property with both EN and TH embeddings
        # locale="en" uses description_embedding_en
        # locale="th" uses description_embedding_th
        pass

    @pytest.mark.asyncio
    async def test_search_by_similarity_returns_active_only(self, db_session):
        """Test only published, non-deleted properties returned."""
        # Create: published, unpublished, deleted properties
        # Only published should be returned
        pass

    @pytest.mark.asyncio
    async def test_cosine_distance_calculation(self, db_session):
        """Test cosine distance formula (1 - distance = similarity)."""
        # Verify similarity scores are in range [0, 1]
        pass

    @pytest.mark.asyncio
    async def test_empty_query_returns_empty(self):
        """Test empty query returns empty results."""
        # Call with query=""
        # Should return []
        pass
```

**Setup:** Tests need properties with embeddings. Use fixtures:

```python
@pytest.fixture
async def properties_with_embeddings(db_session, customer_user):
    """Create test properties with mock embeddings."""
    from server.services.search.embedding_service import PropertyEmbeddingService

    service = PropertyEmbeddingService()

    properties = [
        PropertyV2(
            title="Modern Villa",
            description="Luxury villa with pool",
            property_type="villa",
            is_published=True,
            created_by=customer_user.id,
            updated_by=customer_user.id,
        ),
        # ... more properties
    ]

    for prop in properties:
        db_session.add(prop)
        await db_session.flush()

        # Generate embeddings
        embedding = await service.generate_property_embedding(prop, "en")
        prop.description_embedding_en = embedding

    await db_session.commit()
    return properties
```

---

### 4. Unit Tests for PropertySearchOrchestrator

**File:** `apps/server/tests/services/search/test_orchestrator.py`

**Required Test Cases:**

```python
import pytest
from server.services.search.orchestrator import PropertySearchOrchestrator


class TestPropertySearchOrchestrator:
    """Unit tests for PropertySearchOrchestrator."""

    # Phase 1A tests
    @pytest.mark.asyncio
    async def test_search_filter_extraction_only(self, db_session):
        """Test filter extraction without vector search."""
        # components=["filter_extraction"]
        # Should call filter_extractor.extract()
        pass

    @pytest.mark.asyncio
    async def test_search_basic_ranking(self, db_session):
        """Test basic ranking (Phase 1A behavior)."""
        # ranking="basic"
        # Results sorted by default property_service ordering
        pass

    @pytest.mark.asyncio
    async def test_search_with_filters_applied(self, db_session):
        """Test SQL filters applied correctly."""
        # Query: "2BR condo"
        # Verify PropertyListQuery has bedrooms=2, property_type="condo"
        pass

    # Phase 1B tests
    @pytest.mark.asyncio
    async def test_search_vector_only(self, db_session):
        """Test vector search without filter extraction."""
        # components=["vector_search"]
        # ranking="vector"
        pass

    @pytest.mark.asyncio
    async def test_search_hybrid_ranking(self, db_session):
        """Test hybrid ranking combines filters + vectors."""
        # components=["filter_extraction", "vector_search"]
        # ranking="hybrid"
        # Properties matching both get boosted scores
        pass

    @pytest.mark.asyncio
    async def test_search_component_selection(self, db_session):
        """Test enabling/disabling components."""
        # Test with different component combinations
        pass

    @pytest.mark.asyncio
    async def test_search_pagination(self, db_session):
        """Test page/per_page parameters."""
        # page=2, per_page=10
        # Verify correct subset returned
        pass

    @pytest.mark.asyncio
    async def test_search_graceful_degradation(self, db_session):
        """Test fallback when vector search fails."""
        # Mock vector_search to raise exception
        # Should still return filter results
        pass

    @pytest.mark.asyncio
    async def test_search_metadata_structure(self, db_session):
        """Test metadata includes all required fields."""
        # Verify metadata has: query, components_used, ranking_strategy, extracted_filters
        pass
```

---

### 5. Integration Tests - Expand test_search.py

**File:** `apps/server/tests/api/v1/test_search.py` (ADD to existing)

**Add These Test Cases:**

```python
class TestSemanticSearchAPI:
    # ... existing tests ...

    # Phase 1B additions
    @pytest.mark.asyncio
    async def test_vector_search_component(self, client, db_session):
        """Test components=["vector_search"]."""
        # Request with vector_search component
        # Verify metadata shows vector_search used
        pass

    @pytest.mark.asyncio
    async def test_hybrid_search_components(self, client, db_session):
        """Test components=["filter_extraction", "vector_search"]."""
        # Both components enabled
        # Verify metadata shows both
        pass

    @pytest.mark.asyncio
    async def test_ranking_strategy_basic(self, client, db_session):
        """Test ranking="basic"."""
        # Default ranking
        pass

    @pytest.mark.asyncio
    async def test_ranking_strategy_vector(self, client, db_session):
        """Test ranking="vector"."""
        # Vector-only ranking
        pass

    @pytest.mark.asyncio
    async def test_ranking_strategy_hybrid(self, client, db_session):
        """Test ranking="hybrid"."""
        # Hybrid ranking (filter + semantic)
        pass

    @pytest.mark.asyncio
    async def test_vector_search_metadata(self, client, db_session):
        """Test vector search metadata in response."""
        # Verify metadata.vector_search exists with results_count, top_score
        pass

    @pytest.mark.asyncio
    async def test_hybrid_ranking_metadata(self, client, db_session):
        """Test hybrid ranking metadata structure."""
        # Verify metadata.ranking has strategy, counts
        pass

    @pytest.mark.asyncio
    async def test_vector_search_with_no_embeddings(self, client, db_session):
        """Test graceful degradation when no embeddings exist."""
        # No properties with embeddings
        # Should still work (empty vector results)
        pass
```

---

### 6. Script Tests for Backfill

**File:** `apps/server/tests/scripts/test_backfill_embeddings.py`

**Required Test Cases:**

```python
import pytest
from server.scripts.backfill_property_embeddings import backfill_embeddings
from server.models.property_v2 import PropertyV2


class TestBackfillEmbeddings:
    """Tests for backfill_property_embeddings.py script."""

    @pytest.mark.asyncio
    async def test_backfill_dry_run(self, db_session, test_property):
        """Test --dry-run mode doesn't modify database."""
        # Run with dry_run=True
        # Verify property embeddings are still None
        pass

    @pytest.mark.asyncio
    async def test_backfill_locale_en(self, db_session, test_property):
        """Test locale="en" generates EN embeddings only."""
        # Run with locale="en"
        # Verify description_embedding_en is set
        # Verify description_embedding_th is still None
        pass

    @pytest.mark.asyncio
    async def test_backfill_locale_th(self, db_session, test_property):
        """Test locale="th" generates TH embeddings only."""
        # Run with locale="th"
        # Verify description_embedding_th is set
        # Verify description_embedding_en is still None
        pass

    @pytest.mark.asyncio
    async def test_backfill_locale_both(self, db_session, test_property):
        """Test locale="both" generates both embeddings."""
        # Run with locale="both"
        # Verify both embeddings are set
        pass

    @pytest.mark.asyncio
    async def test_backfill_skips_existing(self, db_session, test_property):
        """Test doesn't regenerate existing embeddings."""
        # Set description_embedding_en manually
        # Run backfill
        # Verify existing embedding unchanged
        pass

    @pytest.mark.asyncio
    async def test_backfill_only_published_properties(self, db_session):
        """Test only processes published, non-deleted properties."""
        # Create published and unpublished properties
        # Only published should get embeddings
        pass

    @pytest.mark.asyncio
    async def test_backfill_continues_on_error(self, db_session):
        """Test continues on individual property errors."""
        # Mock embedding_service to fail for one property
        # Other properties should still be processed
        pass

    @pytest.mark.asyncio
    async def test_backfill_counts_summary(self, db_session, caplog):
        """Test success/error counts in output."""
        # Run backfill
        # Verify log output has success/error counts
        pass
```

**Note:** Import the script's `backfill_embeddings` function directly for testing.

---

## Testing Guidelines

### Fixtures and Setup

Use existing fixtures from `conftest.py`:
- `db_session` - Test database session
- `client` - AsyncClient for API tests
- `customer_user` - Test user
- `test_property` - Sample property

Create new fixtures as needed:
```python
@pytest_asyncio.fixture
async def properties_with_embeddings(db_session, customer_user):
    """Create properties with mock embeddings for vector search tests."""
    # Implementation...
```

### Mocking External APIs

**OpenRouter (LLM):**
```python
@pytest.fixture
def mock_openrouter():
    with patch('httpx.AsyncClient.post') as mock:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{...}'}}]
        }
        mock.return_value = mock_response
        yield mock
```

**OpenAI (Embeddings):**
- Tests should use mock mode (default behavior without API key)
- No need to mock - service already handles this

### Test Isolation

- Each test should be independent (can run in any order)
- Use `db_session` fixture (auto-rollback after test)
- Don't rely on test execution order

### Performance

- Target: All tests run in < 30 seconds
- Use in-memory operations where possible
- Mock external APIs (no real network calls)
- Keep test data small (3-5 properties per test max)

---

## Coverage Requirements

### Target Metrics
- **Line Coverage:** ≥80%
- **Branch Coverage:** ≥75%

### Files to Cover
1. `services/search/filter_extraction_service.py`
2. `services/search/embedding_service.py`
3. `services/search/vector_search_service.py`
4. `services/search/orchestrator.py`
5. `api/v1/endpoints/search.py`
6. `scripts/backfill_property_embeddings.py`

### Verification Command
```bash
docker exec bestays-server-dev pytest \
    tests/services/search/ \
    tests/api/v1/test_search.py \
    tests/scripts/test_backfill_embeddings.py \
    --cov=src/server/services/search \
    --cov=src/server/api/v1/endpoints/search.py \
    --cov=scripts/backfill_property_embeddings.py \
    --cov-report=term-missing \
    --cov-fail-under=80
```

---

## Acceptance Criteria

### Functional Requirements
- ✅ All test files created (6 new files + expand 1 existing)
- ✅ All tests passing
- ✅ Coverage ≥80% line, ≥75% branch
- ✅ Tests run in < 30 seconds
- ✅ No external API calls (all mocked)

### Test Quality
- ✅ Clear test names (describe what is tested)
- ✅ Each test has docstring
- ✅ Tests are independent (no shared state)
- ✅ Good mocking practices
- ✅ Edge cases covered (empty inputs, errors, etc.)

---

## Deliverables

### 1. Test Files
- `tests/services/search/test_filter_extraction_service.py`
- `tests/services/search/test_embedding_service.py`
- `tests/services/search/test_vector_search_service.py`
- `tests/services/search/test_orchestrator.py`
- `tests/scripts/test_backfill_embeddings.py`
- `tests/api/v1/test_search.py` (expanded)

### 2. Test Execution Report

Run these commands and capture output:

**Test 1: Run All Tests**
```bash
docker exec bestays-server-dev pytest tests/ -v
```

**Test 2: Coverage Report**
```bash
docker exec bestays-server-dev pytest \
    tests/services/search/ \
    tests/api/v1/test_search.py \
    tests/scripts/test_backfill_embeddings.py \
    --cov=src/server/services/search \
    --cov=src/server/api/v1/endpoints/search.py \
    --cov=scripts/backfill_property_embeddings.py \
    --cov-report=term-missing
```

**Test 3: Individual Test Files**
```bash
docker exec bestays-server-dev pytest tests/services/search/test_filter_extraction_service.py -v
docker exec bestays-server-dev pytest tests/services/search/test_embedding_service.py -v
docker exec bestays-server-dev pytest tests/services/search/test_vector_search_service.py -v
docker exec bestays-server-dev pytest tests/services/search/test_orchestrator.py -v
docker exec bestays-server-dev pytest tests/api/v1/test_search.py -v
docker exec bestays-server-dev pytest tests/scripts/test_backfill_embeddings.py -v
```

**Test 4: Performance**
```bash
time docker exec bestays-server-dev pytest tests/services/search/ tests/api/v1/test_search.py tests/scripts/test_backfill_embeddings.py -q
```

### 3. Implementation Report

Create: `.claude/tasks/TASK-018/subagent-reports/testing-phase-report.md`

Must include:
1. **Test Files Created** (with line counts)
2. **Test Results** (pass/fail for each test case)
3. **Coverage Report** (line/branch percentages)
4. **EXTERNAL VALIDATION** (all 4 test commands with outputs)
5. **Known Issues** (if any)
6. **Performance Metrics** (execution time)

---

## Important Notes

### DO NOT Skip Tests

Every test case listed above is required. If you think a test is unnecessary:
1. Document why in the report
2. Still implement it (for completeness)

### Use Existing Patterns

Follow patterns from existing tests:
- `tests/api/v1/test_search.py` - API testing patterns
- `tests/conftest.py` - Fixture patterns
- Other service tests - Unit testing patterns

### Mock Everything External

- OpenRouter API calls (LLM)
- OpenAI API calls (embeddings - use mock mode)
- No real network calls in tests

### Test Coverage != Test Quality

High coverage is good, but tests must also:
- Test edge cases
- Test error handling
- Test boundary conditions
- Be readable and maintainable

---

## Estimated Time

**Total:** 1.5-2 hours

**Breakdown:**
- Filter extraction tests: 20 min
- Embedding service tests: 20 min
- Vector search tests: 20 min
- Orchestrator tests: 25 min
- API integration tests: 15 min
- Script tests: 15 min
- Coverage verification: 10 min
- Report writing: 15 min

---

## Questions?

If you encounter:
- **Unclear requirements:** Document assumption and proceed
- **Technical blockers:** Note in report, implement what you can
- **Coverage gaps:** Identify which lines/branches are uncovered

---

**Begin implementation. All tests must pass and coverage must reach ≥80%.**

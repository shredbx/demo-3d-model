# Semantic Search Architecture Design

**Task:** TASK-018
**Story:** US-027
**Phase:** PLANNING → IMPLEMENTATION
**Date:** 2025-11-09

---

## Overview

Build modular, extensible semantic search system for property discovery using natural language queries. Architecture designed for future booking calendar and CRM integration without re-engineering.

---

## Architecture Principles

###1. **Modular & Composable**
- Each search component is independent service
- Orchestrator dynamically composes components
- Add new features without breaking existing code

### 2. **Extension-Friendly**
- JSONB for flexible future data
- Nullable columns for backward compatibility
- Pluggable ranking strategies

### 3. **Agile-Ready**
- Each phase delivers working features
- No big refactors needed for future features
- Progressive enhancement pattern

---

## Component Architecture

```
PropertySearchOrchestrator (Main Coordinator)
├── FilterExtractionService (Phase 1A - NOW)
│   ├── Extract structured filters from natural language
│   ├── Future: Extract dates ("november to january")
│   └── Future: Extract budget ranges, preferences
│
├── VectorSearchService (Phase 1B - NOW)
│   ├── Generate query embeddings via OpenRouter
│   ├── Search property embeddings (pgvector)
│   └── Future: Hybrid with user preference embeddings
│
├── AvailabilityService (Phase 2 - FUTURE PLACEHOLDER)
│   ├── Parse semantic date ranges
│   ├── Check booking calendar
│   └── Apply booking rules (min nights, check-in days)
│
├── PersonalizationService (Phase 3 - FUTURE PLACEHOLDER)
│   ├── User search history analysis
│   ├── Preference learning
│   └── Custom ranking based on past behavior
│
└── ResultRanker (Combines all signals)
    ├── Semantic similarity score (0.0-1.0)
    ├── Filter match score
    ├── Future: Availability score, price score
    └── Weighted final ranking
```

---

## Service Layer Structure

```
apps/server/src/server/services/
├── property_service.py (existing - basic CRUD) ✅
│
├── search/  🆕 NEW - Modular Search System
│   ├── __init__.py
│   ├── orchestrator.py
│   │   └── PropertySearchOrchestrator
│   │       - search() method with dynamic components
│   │       - Configurable ranking strategies
│   │
│   ├── filter_extraction_service.py (Phase 1A - IMPLEMENT NOW)
│   │   └── FilterExtractionService
│   │       - extract(query: str, locale: str) -> PropertySearchQuery
│   │       - LLM-based filter extraction via OpenRouter
│   │       - Future: Also extracts dates, budgets
│   │
│   ├── vector_search_service.py (Phase 1B - IMPLEMENT NOW)
│   │   └── VectorSearchService
│   │       - rank_by_similarity(query, candidates, locale)
│   │       - Cosine similarity search via pgvector
│   │
│   ├── availability_service.py (Phase 2 - PLACEHOLDER ONLY)
│   │   └── # Placeholder for future booking integration
│   │
│   ├── personalization_service.py (Phase 3 - PLACEHOLDER ONLY)
│   │   └── # Placeholder for future CRM integration
│   │
│   └── ranking/
│       ├── base_ranker.py (IMPLEMENT NOW)
│       │   └── Abstract BaseRanker class
│       │
│       ├── hybrid_ranker.py (IMPLEMENT NOW)
│       │   └── Combines filter + semantic scores
│       │
│       ├── availability_ranker.py (FUTURE)
│       └── ml_ranker.py (FUTURE)
│
├── embeddings/  🆕 NEW - Reusable Embedding Services
│   ├── __init__.py
│   ├── base_embedding_service.py (IMPLEMENT NOW)
│   │   └── Abstract BaseEmbeddingService
│   │
│   ├── property_embedding_service.py (Phase 1B - IMPLEMENT NOW)
│   │   └── PropertyEmbeddingService
│   │       - generate_embeddings(property_id)
│   │       - backfill_embeddings()
│   │
│   └── faq_embedding_service.py (existing - refactor to base)
│
└── booking/  (Phase 2 - FUTURE, empty placeholder)
```

---

## API Endpoints

### Phase 1 (NOW) - Semantic Search

```python
POST /api/v1/properties/search/semantic
```

**Request:**
```json
{
  "query": "big space for gf and dog, near markets, mountains",
  "locale": "en",
  "page": 1,
  "per_page": 20
}
```

**Response:**
```json
{
  "results": [
    {
      "property": {...},
      "relevance_score": 0.92,
      "match_explanation": "2+ bedrooms, pet-friendly, mountain location, near local markets"
    }
  ],
  "pagination": {...},
  "query_understanding": {
    "extracted_filters": {
      "bedrooms": 2,
      "amenities": ["pets_allowed"],
      "location_type": "mountain"
    },
    "semantic_intent": "couples-friendly space with pet accommodation in mountain area with market access"
  }
}
```

---

## Database Schema

### Phase 1 (NOW) - Enable Vector Search

```sql
-- Migration: 20251109_enable_property_vector_search.py

-- Change TEXT to vector (columns already exist)
ALTER TABLE properties
  ALTER COLUMN description_embedding_en TYPE vector(1536),
  ALTER COLUMN description_embedding_th TYPE vector(1536);

-- Create HNSW indexes for fast similarity search
CREATE INDEX idx_property_embedding_en ON properties
  USING ivfflat (description_embedding_en vector_cosine_ops)
  WITH (lists = 100);

CREATE INDEX idx_property_embedding_th ON properties
  USING ivfflat (description_embedding_th vector_cosine_ops)
  WITH (lists = 100);
```

### Phase 2 (FUTURE) - Booking Integration

```sql
-- Add nullable columns (backward compatible)
ALTER TABLE properties ADD COLUMN IF NOT EXISTS
  booking_rules JSONB DEFAULT NULL;
  -- Example: {"min_nights": 3, "check_in_days": [0, 6], "instant_booking": false}

-- New tables (created when booking is implemented)
CREATE TABLE bookings (...);
CREATE TABLE property_availability_calendar (...);
```

### Phase 3 (FUTURE) - CRM/Personalization

```sql
CREATE TABLE user_search_history (...);
CREATE TABLE user_property_interactions (...);
```

---

## Data Flow

### Phase 1A: Filter Extraction Only

```
User Query: "big space for gf and dog, mountains"
    ↓
[FilterExtractionService]
- LLM extracts: {bedrooms: 2, amenities: [pets_allowed], location: mountain}
    ↓
[PropertyService.list_properties(filters)]
- Standard database query
    ↓
Results (20 properties)
```

**Latency:** ~1.5 seconds (LLM extraction + DB query)

---

### Phase 1B: Hybrid Search (Filter + Semantic)

```
User Query: "big space for gf and dog, mountains"
    ↓
[FilterExtractionService]
- Extract structured filters
    ↓
[PropertyService.list_properties(filters)]
- Get candidate properties (200 matches)
    ↓
[VectorSearchService]
- Generate query embedding
- Search against property embeddings
- Rank by cosine similarity
    ↓
[HybridRanker]
- Combine filter match + semantic score
- Weight: 40% filters + 60% semantic
    ↓
Top 20 Results (sorted by relevance)
```

**Latency:** ~2.5 seconds (LLM + DB + vector search)

---

### Phase 2 (FUTURE): Availability-Aware Search

```
User Query: "big space for gf and dog, mountains, november to january"
    ↓
[FilterExtractionService]
- Extract: filters + dates {check_in: "2025-11-01", check_out: "2026-01-31"}
    ↓
[PropertyService.list_properties(filters)]
- Get 200 candidates
    ↓
[AvailabilityService]
- Filter by date availability
- Check booking rules
- Reduce to 50 available properties
    ↓
[VectorSearchService]
- Semantic ranking on available properties
    ↓
[AvailabilityRanker]
- Combine: availability + semantic + price
    ↓
Top 20 Results
```

**Latency:** ~3.5 seconds (adds availability check)

---

## Extension Points

### 1. Orchestrator Component System

```python
# Current (Phase 1)
await orchestrator.search(
    query=query,
    components=["filter_extraction", "vector"],
    ranking="hybrid"
)

# Future (Phase 2) - Just add "availability"!
await orchestrator.search(
    query=query,
    components=["filter_extraction", "vector", "availability"],
    ranking="availability_weighted"
)

# Future (Phase 3) - Just add "personalization"!
await orchestrator.search(
    query=query,
    user_id=user_id,
    components=["filter_extraction", "vector", "availability", "personalization"],
    ranking="ml"
)
```

### 2. Ranking Strategy Pluggability

```python
# Base ranker interface
class BaseRanker(ABC):
    @abstractmethod
    def rank(self, properties: list[Property]) -> list[RankedProperty]:
        pass

# Easy to add new strategies
class AvailabilityRanker(BaseRanker):
    def rank(self, properties):
        # Prioritize instant-booking, flexible check-in
        ...

class MLRanker(BaseRanker):
    def rank(self, properties):
        # ML model based on user history
        ...
```

### 3. Schema Extensibility

```python
# PropertySearchQuery - add fields without breaking changes
class PropertySearchQuery(BaseModel):
    # Current fields
    bedrooms: int | None
    amenities: list[str] | None

    # Future fields (ignored if None)
    check_in: date | None = None  # Phase 2
    check_out: date | None = None  # Phase 2
    user_id: UUID | None = None    # Phase 3
```

---

## Implementation Phases

### Phase 1A: Filter Extraction (1 hour)
- ✅ Create search/ folder structure
- ✅ Implement FilterExtractionService
- ✅ Implement basic orchestrator
- ✅ Add POST /properties/search/semantic endpoint
- ✅ Test with natural language queries

### Phase 1B: Vector Search (1.5 hours)
- ✅ Implement BaseEmbeddingService
- ✅ Implement PropertyEmbeddingService
- ✅ Create migration for vector columns
- ✅ Backfill embeddings for existing properties
- ✅ Implement VectorSearchService
- ✅ Implement HybridRanker
- ✅ Update orchestrator for hybrid search

### Phase 2: Availability Integration (FUTURE)
- Add AvailabilityService
- Extend FilterExtractionService for date parsing
- Add AvailabilityRanker
- Update orchestrator: append "availability" to components

### Phase 3: Personalization (FUTURE)
- Add PersonalizationService
- Create user history tables
- Add MLRanker
- Update orchestrator: append "personalization" to components

---

## Design Decisions & Trade-offs

### Decision 1: LLM Filter Extraction vs Rule-Based Parsing

**Chosen:** LLM-based extraction via OpenRouter

**Pros:**
- Handles complex, nuanced natural language
- Extensible to dates, budgets, preferences
- Learns from examples (few-shot prompting)

**Cons:**
- ~1-2 second latency
- OpenRouter API cost (~$0.001 per query)
- Non-deterministic

**When to Revisit:** If cost exceeds $100/month or latency > 3 seconds

---

### Decision 2: pgvector vs Pinecone/Weaviate

**Chosen:** pgvector (PostgreSQL extension)

**Pros:**
- Already installed and enabled ✅
- No external service needed
- Same database for data + embeddings
- Fast enough for < 100K properties

**Cons:**
- Slower than specialized vector DBs at scale
- Limited to Euclidean/Cosine distance

**When to Revisit:** If property count > 100K or search latency > 1 second

---

### Decision 3: Hybrid Ranking vs Pure Semantic

**Chosen:** Hybrid (filters + semantic)

**Pros:**
- Fast hard filtering reduces search space
- Semantic matching for nuanced queries
- Best of both worlds

**Cons:**
- More complex implementation
- Two-stage ranking

**When to Revisit:** If users prefer pure semantic (no hard filters)

---

### Decision 4: Orchestrator Pattern vs Direct Service Calls

**Chosen:** Orchestrator with dynamic component composition

**Pros:**
- Easy to add new search components
- Centralized search logic
- Consistent API across all search types

**Cons:**
- Extra abstraction layer
- Slightly more complex than direct calls

**When to Revisit:** Never (this is a sound pattern for extensibility)

---

## Success Metrics

### Performance
- Filter extraction: < 2 seconds
- Vector search: < 500ms
- Total search response: < 3 seconds
- Embedding generation: < 1 second per property

### Quality
- Relevance score > 0.7 for 80% of results
- User satisfaction (qualitative feedback)
- Click-through rate on top 3 results

### Extensibility
- Add booking integration without re-architecture
- Add personalization without breaking existing search

---

## Testing Strategy

### Unit Tests
- FilterExtractionService: Mock LLM responses
- VectorSearchService: Mock embeddings
- HybridRanker: Test score combination logic

### Integration Tests
- End-to-end search flow
- Database vector search performance
- OpenRouter API integration

### E2E Tests
- Natural language queries return relevant results
- Filter extraction accuracy
- Response time < 3 seconds

---

## Deployment Checklist

- [ ] Migration applied (vector columns enabled)
- [ ] Embeddings backfilled for all properties
- [ ] OpenRouter API key configured
- [ ] New endpoint registered in router
- [ ] Tests passing (unit + integration)
- [ ] Performance benchmarks met
- [ ] Documentation updated

---

**Status:** Ready for implementation
**Estimated Effort:** ~2.5 hours backend + 1 hour frontend
**Next Step:** Launch dev-backend-fastapi subagent

# TASK-018: Semantic Property Search - Phase 1A

**Story:** US-027
**Branch:** feat/TASK-018-US-027
**Phase:** IMPLEMENTATION
**Status:** in_progress
**Created:** 2025-11-09

---

## Objective

Implement natural language property search using LLM-based filter extraction and semantic vector matching. Build modular, extensible architecture for future booking calendar and CRM integration.

---

## Scope

### Phase 1A: Filter Extraction (THIS TASK)
- Natural language → structured filters via LLM
- POST /properties/search/semantic endpoint
- Orchestrator with modular component system
- Response time < 2 seconds

### Phase 1B: Vector Search (NEXT TASK)
- Property embeddings generation
- pgvector migration and backfill
- Semantic similarity ranking
- Hybrid ranking (filters + semantic)

---

## Technical Approach

### Architecture: Modular Search System

```
PropertySearchOrchestrator (Coordinator)
├── FilterExtractionService (Phase 1A - NOW)
├── VectorSearchService (Phase 1B - NEXT)
├── AvailabilityService (Phase 2 - FUTURE PLACEHOLDER)
└── PersonalizationService (Phase 3 - FUTURE PLACEHOLDER)
```

### Files to Create

```
apps/server/src/server/services/search/
├── __init__.py
├── orchestrator.py (PropertySearchOrchestrator)
├── filter_extraction_service.py (FilterExtractionService)
└── [vector_search_service.py] (Phase 1B)

apps/server/src/server/api/v1/endpoints/
└── search.py (POST /search/semantic)

apps/server/tests/api/v1/
└── test_search.py
```

---

## Acceptance Criteria

- [ ] FilterExtractionService extracts filters from natural language
- [ ] Orchestrator coordinates search components (modular design)
- [ ] POST /properties/search/semantic endpoint works
- [ ] Tests pass with > 90% coverage
- [ ] Response includes extracted filters in metadata
- [ ] Response time < 3 seconds
- [ ] Works in both EN and TH locales

---

## Example Queries

| Query | Expected Extraction |
|-------|---------------------|
| "big space for gf and dog, mountains" | bedrooms=2, amenities=["pets_allowed"], tags=["mountain"] |
| "modern condo for remote work, quiet" | property_type="condo", amenities=["home_office"], tags=["quiet", "modern"] |
| "villa with pool for family vacation in Phuket" | property_type="villa", bedrooms=3, province="Phuket", amenities=["pool"], tags=["family_friendly"] |

---

## Dependencies

### External
- OpenRouter API (LLM filter extraction)
- FastAPI, SQLAlchemy, httpx

### Internal
- property_service (list_properties)
- PropertySearchQuery schema

### Stories
- US-023 (Property Display) - provides property data model

---

## Testing Strategy

### Unit Tests
- FilterExtractionService.extract() with mock LLM
- Orchestrator.search() with mock components
- Edge cases: empty query, invalid JSON, LLM timeout

### Integration Tests
- End-to-end search flow
- OpenRouter API integration
- Database query performance

### Manual Testing
```bash
curl -X POST http://localhost:8011/api/v1/properties/search/semantic \
  -H "Content-Type: application/json" \
  -d '{"query": "2BR condo with pool", "locale": "en"}'
```

---

## Performance Metrics

- **Filter Extraction:** < 2 seconds (LLM call)
- **Database Query:** < 500ms
- **Total Response:** < 3 seconds
- **API Cost:** ~$0.001 per query (OpenRouter)

---

## Extension Points (Future)

### Phase 1B: Vector Search
- Add VectorSearchService to orchestrator
- Enable semantic ranking
- Change ranking="hybrid"

### Phase 2: Booking Integration
- Add AvailabilityService to orchestrator
- Extract dates from query
- Filter by availability

### Phase 3: CRM Personalization
- Add PersonalizationService to orchestrator
- User search history
- ML-based ranking

---

## Design Decisions

### Decision 1: LLM Filter Extraction vs Rule-Based
- **Chosen:** LLM (OpenRouter)
- **Why:** Handles nuanced language, extensible to dates/budgets
- **Trade-off:** 1-2s latency, $0.001/query cost
- **Revisit if:** Cost > $100/month OR latency > 3s

### Decision 2: Orchestrator Pattern
- **Chosen:** Modular component composition
- **Why:** Easy to add new features without refactoring
- **Trade-off:** Extra abstraction layer
- **Revisit:** Never (sound extensibility pattern)

---

## Related Tasks

- TASK-019: Phase 1B - Vector Search (NEXT)
- TASK-020: Frontend Search UI Integration (AFTER 1B)

---

## Progress

### Planning ✅
- [x] Architecture design complete
- [x] Implementation spec ready
- [x] Quality gates validated

### Implementation 🟡
- [ ] FilterExtractionService implemented
- [ ] PropertySearchOrchestrator implemented
- [ ] Search API endpoint created
- [ ] Router updated
- [ ] Tests written

### Testing ⏳
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing complete
- [ ] Performance benchmarks met

---

**Status:** Ready for subagent implementation
**Next:** Launch dev-backend-fastapi subagent
**Estimated Time:** 1 hour

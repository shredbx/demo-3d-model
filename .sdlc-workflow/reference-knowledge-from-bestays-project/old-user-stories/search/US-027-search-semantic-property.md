# US-027: Semantic Property Search

**Domain:** search
**Feature:** semantic
**Scope:** property
**Status:** READY
**Created:** 2025-11-09
**Default Product:** bestays
**Portable:** true
**Ported To:** []

---

## Description

As a **guest user**, I want to **search for properties using natural language** like "big space for my girlfriend and dog, near markets and mountains" so that I can **find properties that match my lifestyle needs** without having to understand complex filters.

**User Journey:**
1. Guest types natural language query in search bar
2. System extracts intent and structured filters (bedrooms, amenities, location type)
3. System performs semantic matching against property descriptions
4. Results are ranked by relevance with explanations
5. Guest sees properties that match their lifestyle needs

**Example Queries:**
- "big space for gf and dog, near markets, mountains" → 2BR, pet-friendly, mountain location
- "modern condo for remote work, quiet area" → condo, home office amenity, residential area
- "villa with pool for family vacation" → villa, pool amenity, family-friendly

---

## Acceptance Criteria

### Phase 1A: Natural Language Filter Extraction
- [ ] POST /properties/search/semantic endpoint accepts natural language queries
- [ ] LLM extracts structured filters (transaction_type, property_type, bedrooms, amenities, etc.)
- [ ] Extracted filters are merged with existing filter system
- [ ] Results show "Understanding your search: 2BR, pet-friendly, mountain location"
- [ ] Response time < 2 seconds for filter extraction

### Phase 1B: Vector Semantic Search
- [ ] Property embeddings generated for all properties (EN + TH)
- [ ] Migration enables pgvector for description_embedding_en/th columns
- [ ] Vector search ranks results by semantic similarity (score > 0.6)
- [ ] Hybrid ranking combines filter matches + semantic similarity
- [ ] Results show relevance scores and match explanations

### Frontend Integration
- [ ] Homepage search bar uses semantic endpoint
- [ ] Property listing page accepts natural language queries
- [ ] Loading state shows "Understanding your search..."
- [ ] Results display match explanations
- [ ] Works in both EN and TH locales

### Performance
- [ ] Filter extraction: < 2 seconds
- [ ] Vector search: < 500ms
- [ ] Total search response: < 3 seconds
- [ ] Embedding generation: < 1 second per property

---

## Technical Notes

### Architecture: Modular Search System

**Service Layer:**
```
apps/server/src/server/services/search/
├── orchestrator.py (PropertySearchOrchestrator)
├── filter_extraction_service.py (Phase 1A - LLM extraction)
├── vector_search_service.py (Phase 1B - Semantic matching)
├── availability_service.py (Future - date availability)
├── personalization_service.py (Future - user history)
└── ranking/
    ├── base_ranker.py
    └── hybrid_ranker.py (Phase 1)
```

**Extension Points:**
- JSONB booking_rules column (nullable, for future booking system)
- Semantic date extraction ("november to january") → future AvailabilityService
- User history tracking → future PersonalizationService
- Pluggable ranking strategies

**Infrastructure:**
- pgvector extension: Already enabled ✅
- OpenRouter API: For LLM extraction + embeddings ✅
- Existing FAQ RAG pattern: Reuse for property embeddings ✅

### Dependencies
- External: OpenRouter API, pgvector
- Internal: property_service, faq_embedding_service (pattern reference)
- Stories: US-023 (Property Display) - provides property data model

### Future Enhancements (Not in Scope)
- Availability-aware search: "want to stay november to january"
- CRM personalization: User search history and preferences
- ML-based ranking: Learn from booking conversions
- Multi-modal search: Image + text combined search

---

## Related Stories

- US-023: Property Detail Page Display (provides property data)
- US-026: MVP Homepage (provides search UI)
- Future: US-XXX Booking System (will add availability to search)
- Future: US-XXX CRM System (will add personalization)

---

## Tasks

[Automatically populated by system - do not edit manually]

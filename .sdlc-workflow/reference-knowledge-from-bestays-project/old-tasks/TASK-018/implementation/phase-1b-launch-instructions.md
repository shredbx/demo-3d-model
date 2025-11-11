# Phase 1B Launch Instructions - Backend Subagent

**Task:** TASK-018 (US-027)
**Subagent:** dev-backend-fastapi
**Date:** 2025-11-10
**Status:** Ready to launch

---

## Executive Summary

Infrastructure is ✅ **READY**. Launch dev-backend-fastapi subagent to implement Phase 1B components.

**Infrastructure Status:**
- ✅ pgvector extension v0.8.1 installed
- ✅ Migration applied: `description_embedding_en/th` are `vector(1536)` columns
- ✅ ivfflat indexes created for cosine similarity search
- ✅ Table name confirmed: `properties` (NOT properties_v2)
- ⚠️ OpenAI API key needs verification in .env file

**What to Implement:**
1. PropertyEmbeddingService - Generate embeddings via OpenAI
2. VectorSearchService - Semantic search using pgvector
3. Update orchestrator for hybrid ranking
4. Backfill script for existing properties
5. Tests with ≥80% coverage
6. **MANDATORY:** External validation with curl (4 tests)

---

## Subagent Launch Command

```bash
@.claude/subagents/dev-backend-fastapi
```

---

## Context to Provide

**Phase 1A Completed (✅):**
- FilterExtractionService - LLM-based filter extraction
- PropertySearchOrchestrator - Modular search coordinator
- Tests with 88% coverage

**Phase 1B Requirements:**
Read: `.claude/tasks/TASK-018/implementation/phase-1b-subagent-instructions.md`

**Critical Infrastructure Notes:**
1. **Table name:** `properties` (NOT `properties_v2`)
2. **Database:** `bestays_dev` (verified)
3. **pgvector columns:** Already exist as `vector(1536)`
4. **Indexes:** Already created (`idx_properties_embedding_en_cosine`, `idx_properties_embedding_th_cosine`)
5. **Model field:** Check `apps/server/src/server/models/property_v2.py` for actual field names

---

## Pre-Implementation Checklist

**Coordinator verifies:**
- [x] pgvector extension installed (v0.8.1)
- [x] Migration applied successfully
- [x] Vector columns exist in database
- [x] Indexes created
- [ ] OpenAI API key configured in .env (needs verification)

**Subagent MUST verify:**
- [ ] Model fields match database schema
- [ ] OpenAI API key is actually set in environment
- [ ] Property model uses Vector(1536) type from pgvector.sqlalchemy

---

## Implementation Order

**Recommended sequence:**

### Step 1: Configuration (5 min)
- Verify OPENAI_API_KEY is set in config.py and .env
- Update OPENAI_EMBEDDING_MODEL if needed (currently: text-embedding-ada-002)

### Step 2: Property Model Update (5 min)
- File: `apps/server/src/server/models/property_v2.py`
- Import: `from pgvector.sqlalchemy import Vector`
- Update columns: `description_embedding_en/th` to use `Vector(1536)`
- Remove TODO comments

### Step 3: PropertyEmbeddingService (20 min)
- File: `apps/server/src/server/services/search/embedding_service.py`
- Implement `generate_embedding()` - OpenAI API call
- Implement `generate_property_embedding()` - Combine property text
- Error handling for API failures

### Step 4: VectorSearchService (20 min)
- File: `apps/server/src/server/services/search/vector_search_service.py`
- Implement `search_by_similarity()` - pgvector cosine distance query
- Return (property, score) tuples
- Filter by similarity threshold

### Step 5: Update Orchestrator (15 min)
- File: `apps/server/src/server/services/search/orchestrator.py`
- Add vector_search service to __init__
- Update search() method signature (components, ranking)
- Implement hybrid ranking logic

### Step 6: Update Exports (2 min)
- File: `apps/server/src/server/services/search/__init__.py`
- Add PropertyEmbeddingService and VectorSearchService exports

### Step 7: Backfill Script (15 min)
- File: `apps/server/scripts/backfill_property_embeddings.py`
- Standalone script to generate embeddings
- Progress tracking and error handling
- Dry-run mode

### Step 8: Tests (25 min)
- File: `apps/server/tests/api/v1/test_search.py`
- Test vector search only
- Test hybrid ranking
- Test graceful degradation
- Test backfill script
- Target: ≥80% coverage

### Step 9: External Validation (15 min) **MANDATORY**
Run these curl commands and capture output:

**Test 1: Vector Search Only**
```bash
curl -X POST http://localhost:8011/api/v1/properties/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "romantic getaway for couples",
    "locale": "en",
    "components": ["vector_search"],
    "ranking": "vector"
  }'
```

**Test 2: Hybrid Search**
```bash
curl -X POST http://localhost:8011/api/v1/properties/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "spacious villa near beach",
    "locale": "en",
    "components": ["filter_extraction", "vector_search"],
    "ranking": "hybrid"
  }'
```

**Test 3: Backfill Script**
```bash
docker exec -i bestays-server-dev python scripts/backfill_property_embeddings.py both
```

**Test 4: Performance**
```bash
time curl -X POST http://localhost:8011/api/v1/properties/search/semantic \
  -H "Content-Type: application/json" \
  -d '{"query": "family villa", "locale": "en"}' \
  -o /dev/null -s
```

### Step 10: Implementation Report (10 min)
Create: `.claude/tasks/TASK-018/subagent-reports/backend-phase-1b-report.md`

**Must include:**
1. External Validation Section (all 4 curl commands with responses)
2. Files created/modified with line counts
3. Test results and coverage
4. Migration verification
5. Backfill results
6. Deviations from spec (if any)

---

## Known Constraints

### From Phase 1A
- Tags filter has known issue (PostgreSQL ARRAY overlap)
- Phase 1B does NOT fix tags issue
- Focus on vector search only

### OpenAI Configuration
- Current model: `text-embedding-ada-002` (config.py line 81)
- Consider updating to: `text-embedding-3-small` (better performance)
- Dimensions: 1536 (fixed, matches migration)

### Property Model
- Check actual field names in property_v2.py
- Verify is_active vs is_published field exists
- Table name is `properties` (confirmed via psql)

---

## Success Criteria

Phase 1B complete when:
1. ✅ All 7 files created/modified
2. ✅ All tests passing
3. ✅ Coverage ≥ 80%
4. ✅ Migration already applied
5. ✅ All properties have embeddings (via backfill)
6. ✅ External validation passed (4/4 tests)
7. ✅ Response time < 3s
8. ✅ Report includes external validation proof

---

## Estimated Time

**Total:** ~2 hours

Breakdown:
- Configuration: 5 min
- Model update: 5 min
- PropertyEmbeddingService: 20 min
- VectorSearchService: 20 min
- Orchestrator update: 15 min
- Exports: 2 min
- Backfill script: 15 min
- Tests: 25 min
- External validation: 15 min
- Report: 10 min
- Buffer: 13 min

---

## Launch Now

**Command:**
```
Launch dev-backend-fastapi subagent with context from:
- .claude/tasks/TASK-018/implementation/phase-1b-subagent-instructions.md
- .claude/tasks/TASK-018/implementation/phase-1b-launch-instructions.md (this file)
```

**First Task:** Verify OpenAI API key is configured, then proceed with Step 1 (Configuration)

---

**Prepared by:** SDLC Coordinator
**Date:** 2025-11-10
**Status:** ✅ Ready to Launch

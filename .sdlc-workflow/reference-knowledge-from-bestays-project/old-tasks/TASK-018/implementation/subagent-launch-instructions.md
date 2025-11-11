# Backend Subagent Launch Instructions - Phase 1A

**Subagent:** dev-backend-fastapi
**Task:** TASK-018 Phase 1A - Filter Extraction Service
**Story:** US-027
**Estimated Time:** ~1 hour

---

## Mission

Implement natural language filter extraction service for property search. Convert queries like "big space for gf and dog, mountains" into structured filters using OpenRouter LLM API.

---

## Critical Requirements

### 1. READ SPECIFICATIONS FIRST

All complete code specifications are in:
- `/Users/solo/Projects/_repos/bestays/.claude/tasks/TASK-018/planning/implementation-spec.md`
- Lines 30-241: FilterExtractionService (complete code)
- Lines 249-445: PropertySearchOrchestrator (complete code)
- Lines 453-576: Search API endpoint (complete code)

### 2. EXTERNAL VALIDATION IS MANDATORY

After implementation, you MUST:
1. Start dev server: `make dev`
2. Test with curl commands (see below)
3. Capture actual responses
4. Include results in report

**This is NOT optional. Your report will be rejected without external validation.**

---

## Implementation Files

### 1. Config Update
**File:** `apps/server/src/server/config.py`

**Action:** Add after line 82 (after OpenAI settings):

```python
# OpenRouter (for semantic search filter extraction)
OPENROUTER_API_KEY: str = "change-me-in-production"
OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
```

---

### 2. Schema Update
**File:** `apps/server/src/server/schemas/property_v2.py`

**Action:** Add PropertySearchQuery schema after PropertyListQuery

**See:** implementation-spec.md lines 46-66

---

### 3. Search Services Package
**Folder:** `apps/server/src/server/services/search/`

**Create these files:**
- `__init__.py`
- `filter_extraction_service.py` (COMPLETE CODE: spec lines 30-241)
- `orchestrator.py` (COMPLETE CODE: spec lines 249-445)

---

### 4. Search API Endpoint
**File:** `apps/server/src/server/api/v1/endpoints/search.py`

**COMPLETE CODE:** spec lines 453-576

---

### 5. Router Update
**File:** `apps/server/src/server/api/v1/router.py`

**Add:**
```python
from server.api.v1.endpoints import search

api_router.include_router(search.router, prefix="/properties")
```

---

### 6. Test Suite
**File:** `apps/server/tests/api/v1/test_search.py`

**Requirements:**
- Test simple query extraction ("2BR condo")
- Test complex query extraction ("big space for gf and dog, mountains")
- Test empty query handling
- Test pagination
- Test metadata structure
- Coverage target: >90%

**See:** subagent-instructions.md lines 136-242 for complete test structure

---

## LLM Integration Details

### OpenRouter Configuration
- **Model:** `meta-llama/llama-3.3-70b-instruct`
- **Temperature:** 0.1 (consistent extraction)
- **Timeout:** 10 seconds
- **Max Tokens:** 500

### Filter Extraction Logic

**Bedrooms (infer from context):**
- "couple"/"gf"/"boyfriend" → 2 bedrooms
- "family" → 3+ bedrooms
- "solo"/"alone" → 1 bedroom

**Amenities:**
- "dog"/"cat"/"pet" → `pets_allowed`
- "pool" → `pool`
- "gym"/"fitness" → `gym`
- "parking" → `parking`

**Tags:**
- "mountain"/"mountains" → `mountain`
- "beach"/"seaside" → `beach`
- "city"/"urban" → `city`
- "quiet" → `quiet`

### Error Handling
- LLM API failure → Return empty `PropertySearchQuery()`
- JSON parse error → Return empty filters
- Pydantic validation error → Return empty query
- Graceful degradation always

---

## External Validation Commands

After implementation, you MUST run these curl commands and capture responses:

### Success Case
```bash
curl -X POST http://localhost:8011/api/v1/properties/search/semantic \
  -H "Content-Type: application/json" \
  -d '{"query": "big space for gf and dog, mountains", "locale": "en"}'
```

**Expected:**
- Status: 200 OK
- Response time: < 3 seconds
- Metadata includes extracted_filters
- Filters: bedrooms=2, amenities=["pets_allowed"], tags=["mountain"]

### Simple Case
```bash
curl -X POST http://localhost:8011/api/v1/properties/search/semantic \
  -H "Content-Type: application/json" \
  -d '{"query": "2BR condo with pool", "locale": "en"}'
```

**Expected:**
- Filters: bedrooms=2, property_type="condo", amenities=["pool"]

### Empty Query
```bash
curl -X POST http://localhost:8011/api/v1/properties/search/semantic \
  -H "Content-Type: application/json" \
  -d '{"query": "", "locale": "en"}'
```

**Expected:**
- Returns all properties (no filters)

### Error Case (malformed JSON)
```bash
curl -X POST http://localhost:8011/api/v1/properties/search/semantic \
  -H "Content-Type: application/json" \
  -d '{"invalid"}'
```

**Expected:**
- Status: 422 Unprocessable Entity
- Proper error message

---

## Testing Commands

### Unit Tests
```bash
cd apps/server
pytest tests/api/v1/test_search.py -v
```

### Coverage
```bash
pytest tests/api/v1/test_search.py --cov=server.services.search --cov-report=term
```

### Linting
```bash
cd apps/server
ruff check src/server/services/search/
ruff check src/server/api/v1/endpoints/search.py
```

### Type Checking
```bash
cd apps/server
mypy src/server/services/search/
mypy src/server/api/v1/endpoints/search.py
```

---

## Success Criteria

- [ ] All files created and properly structured
- [ ] FilterExtractionService extracts filters from natural language
- [ ] Orchestrator coordinates search (modular design)
- [ ] POST /properties/search/semantic endpoint works
- [ ] Tests pass with >90% coverage
- [ ] No linting or type errors
- [ ] **External validation complete with curl (ALL 4 test cases)**
- [ ] Response time < 3 seconds
- [ ] Implementation report created

---

## Report Requirements

**Create:** `.claude/tasks/TASK-018/subagent-reports/backend-phase-1a-report.md`

**Must include these sections:**

### 1. Files Created/Modified
List all files with brief description

### 2. Implementation Notes
Key decisions, code structure, patterns used

### 3. Test Results
- Coverage percentage
- All tests passing
- Test output

### 4. External Validation (MANDATORY SECTION)
**This section is REQUIRED. Report will be rejected without it.**

For each curl command:
- Command executed
- Full response (pretty-printed JSON)
- Status code
- Response time
- Validation: Pass/Fail with explanation

Example format:
```markdown
#### Test 1: Complex Query
**Command:**
curl -X POST http://localhost:8011/api/v1/properties/search/semantic \
  -H "Content-Type: application/json" \
  -d '{"query": "big space for gf and dog, mountains", "locale": "en"}'

**Response:**
Status: 200 OK
Response Time: 2.1 seconds

{
  "properties": [...],
  "pagination": {...},
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

**Validation:** PASS
- Correctly inferred bedrooms from "gf" (couple = 2BR)
- Extracted "pets_allowed" from "dog"
- Extracted "mountain" tag
- Response time acceptable (< 3s)
```

### 5. Deviations
Any changes from spec with justification

### 6. Next Steps
Brief notes for Phase 1B

---

## Environment Setup

### Check .env File
Ensure these variables are set:
```bash
OPENROUTER_API_KEY=<your-key>
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

### Start Services
```bash
make dev
```

### Verify Services Running
```bash
curl http://localhost:8011/api/health
```

---

## Important Notes

1. **Copy code from spec** - Don't rewrite, use the provided implementations
2. **External validation is NOT optional** - This is a hard requirement
3. **Test all error cases** - Graceful degradation is critical
4. **Performance matters** - Response time must be < 3 seconds
5. **Documentation** - Add proper docstrings to all functions

---

**Ready to implement!**

Launch command: `@subagent dev-backend-fastapi`

Read this file first, then read the spec files, then implement.

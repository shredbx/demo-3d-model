# Backend External Validation Requirements

**Version:** 1.0
**Last Updated:** 2025-11-09
**Status:** MANDATORY - NO EXCEPTIONS

---

## Overview

**ALL backend API implementations MUST be validated with external tools before claiming completion.**

This is a **mandatory quality gate** that prevents frontend developers from discovering backend issues that should have been caught during implementation.

---

## Why This Is Critical

### Problem
- Backend developers claim "it works" based only on unit tests
- Frontend integration reveals bugs in actual HTTP requests/responses
- Wasted frontend developer time discovering backend issues
- Multiple iteration loops between backend and frontend

### Solution
- **External validation** using real HTTP clients (curl, httpie, Postman)
- **Before** claiming implementation complete
- **Required proof** in subagent implementation report

---

## Mandatory Requirements

### 1. External Tool Testing

**MUST use external HTTP clients:**
- ✅ `curl` (command line)
- ✅ `httpie` (command line)
- ✅ Postman (GUI)
- ✅ Thunder Client (VS Code)
- ✅ REST Client (any)

**NOT sufficient:**
- ❌ Unit tests only
- ❌ "It works in my IDE"
- ❌ Internal test client
- ❌ Unverified claims

---

### 2. Test Coverage Requirements

**MUST test ALL these scenarios:**

#### Success Cases
- Valid request with expected data
- Edge cases (empty values, optional fields)
- Different locales (en, th)
- Pagination (page 1, page 2, last page)

#### Error Cases
- Malformed JSON
- Missing required fields
- Invalid data types
- 400 Bad Request
- 404 Not Found
- 500 Internal Server Error (if applicable)

#### Performance
- Response time measurement
- Acceptable latency verification

---

### 3. Response Validation

**MUST verify:**
- ✅ Response structure matches schema
- ✅ Status codes correct (200, 400, 404, etc.)
- ✅ Headers present (Content-Type: application/json)
- ✅ Response fields match API specification
- ✅ Error messages are user-friendly
- ✅ Pagination metadata correct

**MUST compare:**
- Actual response vs expected response (from acceptance criteria)
- Document any deviations

---

### 4. Documentation in Report

**Subagent MUST include in implementation report:**

```markdown
## External Validation

### Test Environment
- Server: http://localhost:8011
- Started: make dev
- Verified: All services running

### Success Cases

#### Test 1: Simple Query
**Command:**
```bash
curl -X POST http://localhost:8011/api/v1/properties/search/semantic \
  -H "Content-Type: application/json" \
  -d '{"query": "2BR condo with pool", "locale": "en"}'
```

**Response (200 OK):**
```json
{
  "properties": [...],
  "pagination": {
    "total": 15,
    "page": 1,
    "per_page": 20,
    "pages": 1
  },
  "metadata": {
    "query": "2BR condo with pool",
    "components_used": ["filter_extraction"],
    "extracted_filters": {
      "bedrooms": 2,
      "property_type": "condo",
      "amenities": ["pool"]
    }
  }
}
```

**Validation:**
- ✅ Status: 200 OK
- ✅ Response matches schema
- ✅ Extracted filters correct
- ✅ Response time: 1.8s (< 3s target)

#### Test 2: Complex Query
[... similar format]

### Error Cases

#### Test 1: Malformed JSON
**Command:**
```bash
curl -X POST http://localhost:8011/api/v1/properties/search/semantic \
  -H "Content-Type: application/json" \
  -d '{"invalid"'
```

**Response (400 Bad Request):**
```json
{
  "detail": "Invalid JSON"
}
```

**Validation:**
- ✅ Status: 400 Bad Request
- ✅ Error message present

### Performance Metrics
- Average response time: 1.9s
- P95 response time: 2.4s
- Target: < 3s ✅ PASS

### Deviations from Spec
- None

### Conclusion
All acceptance criteria met. External validation complete.
```

---

## Enforcement Process

### 1. Subagent Claims Completion
Backend subagent finishes implementation and submits report.

### 2. Coordinator Reviews Report
Coordinator checks for external validation section.

### 3. Decision

#### ✅ ACCEPT (if report includes)
- External tool commands (curl/httpie/etc.)
- Actual responses captured
- Success AND error cases tested
- Expected vs actual comparison
- Performance metrics

#### ❌ REJECT (if report missing)
- No external validation section
- Only unit tests mentioned
- No curl commands shown
- No actual responses
- No error case testing

### 4. If Rejected
Coordinator instructs subagent:
1. Start dev server (`make dev`)
2. Run curl commands for all test cases
3. Capture actual responses
4. Compare with acceptance criteria
5. Update report with proof
6. Resubmit

---

## Example Test Script Template

**For subagents to use:**

```bash
#!/bin/bash
# External Validation Test Script
# Run this before claiming implementation complete

BASE_URL="http://localhost:8011/api/v1"

echo "=== SUCCESS CASES ==="

echo "Test 1: Simple query"
curl -X POST "$BASE_URL/properties/search/semantic" \
  -H "Content-Type: application/json" \
  -d '{"query": "2BR condo", "locale": "en"}' \
  | jq .

echo "\nTest 2: Complex query"
curl -X POST "$BASE_URL/properties/search/semantic" \
  -H "Content-Type: application/json" \
  -d '{"query": "big space for gf and dog, mountains", "locale": "en"}' \
  | jq .

echo "\n=== ERROR CASES ==="

echo "Test 3: Malformed JSON"
curl -X POST "$BASE_URL/properties/search/semantic" \
  -H "Content-Type: application/json" \
  -d '{"invalid"' \
  -w "\nStatus: %{http_code}\n"

echo "Test 4: Missing required field"
curl -X POST "$BASE_URL/properties/search/semantic" \
  -H "Content-Type: application/json" \
  -d '{"locale": "en"}' \
  -w "\nStatus: %{http_code}\n"

echo "\n=== PERFORMANCE ==="

echo "Test 5: Response time measurement"
time curl -X POST "$BASE_URL/properties/search/semantic" \
  -H "Content-Type: application/json" \
  -d '{"query": "villa with pool", "locale": "en"}' \
  -o /dev/null -s
```

---

## Quick Reference

### Checklist for Backend Subagents

Before submitting implementation report:

- [ ] Dev server running (`make dev`)
- [ ] curl commands executed for success cases
- [ ] curl commands executed for error cases
- [ ] All responses captured and documented
- [ ] Expected vs actual comparison done
- [ ] Response times measured
- [ ] Schema validation verified
- [ ] Status codes verified
- [ ] External validation section in report
- [ ] No "it should work" claims without proof

---

## Integration with SDLC

This requirement is part of:
- **Planning Quality Gates** - Testing Requirements (Gate 3)
- **Implementation Phase** - Completion criteria
- **Task Folder System** - Subagent report requirements
- **Coordinator Role** - Validation enforcement

---

## Related Documents

- **Testing Strategy:** `.sdlc-workflow/guides/testing-strategy.md`
- **Planning Quality Gates:** `.claude/skills/planning-quality-gates/SKILL.md`
- **Backend FastAPI Skill:** `.claude/skills/backend-fastapi/SKILL.md`
- **Memory MCP Entity:** "Backend Implementation Validation Gate"

---

## Remember

> **"If it's not tested with curl, it's not ready for frontend."**

**No exceptions. No excuses. Always validate externally.**

---

**Version History:**
- 1.0 (2025-11-09): Initial mandatory requirement established

# Backend External Validation Requirement - MANDATORY

**Date:** 2025-11-09
**Type:** SDLC Policy Addition
**Status:** ✅ Implemented and Permanent
**Scope:** All backend API implementations

---

## Summary

Established **mandatory external validation requirement** for all backend API implementations. Backend subagents must now validate endpoints with external tools (curl, httpie, Postman) before claiming completion.

**Key Change:** Backend work is NO LONGER accepted based on unit tests alone. External HTTP validation is now MANDATORY.

---

## Problem Addressed

### Before This Change
- Backend developers claimed "it works" based only on unit tests
- Frontend integration revealed bugs in actual HTTP requests/responses
- Frontend developers wasted time discovering backend issues
- Multiple iteration loops between backend and frontend
- "Works on my machine" syndrome

### After This Change
- ✅ Backend validates with real HTTP clients before handoff
- ✅ Frontend can trust backend API contracts are verified
- ✅ Bugs caught during backend implementation phase
- ✅ Reduced iteration loops
- ✅ Proof required in implementation reports

---

## What Was Implemented

### 1. Comprehensive SDLC Guide
**File:** `.sdlc-workflow/guides/backend-validation-requirements.md`

**Contents:**
- Why this is critical
- Mandatory requirements (tools, coverage, documentation)
- Test script template for subagents
- Report format requirements
- Enforcement process
- Examples and checklists

**Key Sections:**
- External tool testing (curl, httpie, Postman)
- Test coverage (success + error + performance)
- Response validation (schema, status codes, timing)
- Documentation requirements
- Enforcement rules

---

### 2. Backend FastAPI Skill Update
**File:** `.claude/skills/backend-fastapi/SKILL.md`

**Added Section:** "MANDATORY: External Validation Before Completion"

**Location:** Before "MANDATORY: Read Before Implementation" section

**Contents:**
- ⚠️ CRITICAL REQUIREMENT warning
- Required external testing tools
- Test coverage checklist (success, error, performance)
- Documentation format required in reports
- Why this matters (prevents/ensures)
- Enforcement rules
- Reference to full guide

---

### 3. CLAUDE.md Core Rules Update
**File:** `CLAUDE.md`

**Added Section:** "Backend External Validation (MANDATORY)"

**Location:** In "2️⃣ CORE RULES" section, after "Planning Quality Gates"

**Contents:**
- Why critical (prevents frontend bugs, reduces loops)
- Requirements (5-point checklist)
- Enforcement rules (coordinator rejection criteria)
- Example report section format
- References to full guide and Memory MCP entity

---

### 4. Memory MCP Entity Update
**Entity:** "Backend Implementation Validation Gate"

**New Observations:**
- Documentation locations (.sdlc-workflow, .claude/skills, CLAUDE.md)
- Enforcement mechanism (coordinator review)
- Permanent status (checked into git)
- Template availability
- Update history

---

## Enforcement Mechanism

### Coordinator Review Process

When backend subagent claims completion:

1. **Coordinator reads implementation report**
2. **Check for External Validation section**
3. **Decision:**
   - ✅ **ACCEPT** if report includes:
     - External tool commands (curl/httpie/etc.)
     - Actual responses captured
     - Success AND error cases tested
     - Expected vs actual comparison
     - Performance metrics
   - ❌ **REJECT** if report missing:
     - No external validation section
     - Only unit tests shown
     - No curl commands
     - No actual responses
     - No error case testing

4. **If rejected:** Coordinator instructs subagent to add external validation and resubmit

---

## Required Report Format

Backend subagents MUST include this section:

```markdown
## External Validation

### Test Environment
- Server: http://localhost:8011
- Started: make dev
- Verified: All services running

### Success Cases

#### Test 1: [Description]
**Command:**
```bash
curl -X POST http://localhost:8011/api/v1/endpoint \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

**Response (200 OK):**
```json
{
  "field": "value"
}
```

**Validation:**
- ✅ Status: 200 OK
- ✅ Response matches schema
- ✅ Response time: X.Xs (< target)

### Error Cases

#### Test 1: Malformed JSON
[... similar format ...]

### Performance Metrics
- Average: X.Xs
- P95: X.Xs
- Target: < Y.Ys ✅ PASS

### Deviations from Spec
- [List any deviations or "None"]

### Conclusion
All acceptance criteria met. External validation complete.
```

---

## Test Script Template

Provided in guide for subagents to use:

```bash
#!/bin/bash
# External Validation Test Script

BASE_URL="http://localhost:8011/api/v1"

echo "=== SUCCESS CASES ==="
curl -X POST "$BASE_URL/endpoint" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}' | jq .

echo "\n=== ERROR CASES ==="
curl -X POST "$BASE_URL/endpoint" \
  -H "Content-Type: application/json" \
  -d '{"invalid"' \
  -w "\nStatus: %{http_code}\n"

echo "\n=== PERFORMANCE ==="
time curl -X POST "$BASE_URL/endpoint" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}' -o /dev/null -s
```

---

## Benefits

### Immediate
- ✅ Frontend receives verified API contracts
- ✅ Bugs caught before frontend integration
- ✅ Reduced back-and-forth iterations
- ✅ Clear completion criteria

### Long-term
- ✅ Higher quality backend implementations
- ✅ Faster feature delivery (fewer loops)
- ✅ Better documentation (actual curl examples)
- ✅ Trust between backend and frontend teams

---

## Scope

### Applies To
- ✅ All FastAPI endpoint implementations
- ✅ All GraphQL resolver implementations
- ✅ Any backend API exposed to frontend
- ✅ All backend subagent tasks

### Does NOT Apply To
- ❌ Internal service functions (not exposed as API)
- ❌ Database models (unless tested via API)
- ❌ Pure business logic (unless accessed via API)
- ❌ Unit test implementations

---

## Integration with SDLC

This requirement is now part of:

1. **Planning Quality Gates** - Testing Requirements (Gate 3)
2. **Implementation Phase** - Completion criteria for backend tasks
3. **Task Folder System** - Subagent report requirements
4. **Coordinator Role** - Validation enforcement responsibility
5. **Testing Strategy** - External validation as mandatory step

---

## Documentation Locations

| Document | Purpose |
|----------|---------|
| `.sdlc-workflow/guides/backend-validation-requirements.md` | Comprehensive guide (master reference) |
| `.claude/skills/backend-fastapi/SKILL.md` | Mandatory section for backend subagents |
| `CLAUDE.md` | Core rule for coordinator enforcement |
| Memory MCP: "Backend Implementation Validation Gate" | Context for future sessions |

---

## Next Steps

### For Current Task (TASK-018)
When dev-backend-fastapi subagent reports completion, coordinator will:
1. Check for External Validation section
2. Review curl commands and responses
3. Verify all test cases covered
4. Accept or reject based on this guide

### For Future Tasks
- All backend implementations automatically subject to this requirement
- No manual reminder needed (documented in skill and CLAUDE.md)
- Future sessions will load from Memory MCP
- Requirement is permanent (checked into git)

---

## Version History

- **1.0 (2025-11-09):** Initial mandatory requirement established
  - Created comprehensive guide
  - Updated backend-fastapi skill
  - Updated CLAUDE.md core rules
  - Added Memory MCP observations
  - Documented in this report

---

## Conclusion

External validation is now a **permanent, mandatory requirement** for all backend API implementations. This requirement is:

- ✅ Documented in multiple locations
- ✅ Enforced by coordinator review
- ✅ Required in all subagent reports
- ✅ Checked into git (permanent)
- ✅ Loaded from Memory MCP (future sessions)
- ✅ Clear enforcement criteria
- ✅ Template provided for easy adoption

**No backend API implementation is complete without external validation. No exceptions.**

---

**Status:** ✅ Implemented and Active
**Effective Date:** 2025-11-09
**Applies To:** All backend API implementations from this point forward

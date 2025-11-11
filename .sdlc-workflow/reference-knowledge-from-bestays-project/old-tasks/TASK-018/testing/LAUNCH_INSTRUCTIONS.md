# Launch Instructions - Backend Testing Subagent
## TASK-018 Testing Phase

**To User:** Please launch the backend testing subagent with these instructions.

---

## Subagent Configuration

**Agent Name:** dev-backend-fastapi
**Task:** TASK-018 Testing Phase
**Phase:** TESTING
**Estimated Time:** 1.5-2 hours

---

## Launch Command

```
@dev-backend-fastapi

You are implementing the TESTING phase for TASK-018 (US-027 Semantic Property Search).

**Context:**
- Phase 1A ✅: FilterExtractionService, PropertySearchOrchestrator (filter extraction)
- Phase 1B ✅: PropertyEmbeddingService, VectorSearchService, hybrid ranking
- Current test coverage: 0% (only API integration tests exist)

**Mission:**
Implement comprehensive test suite to achieve ≥80% test coverage.

**Instructions:**
Read the detailed instructions in:
/Users/solo/Projects/_repos/bestays/.claude/tasks/TASK-018/testing/subagent-instructions.md

**Key Deliverables:**
1. Create 5 new test files (unit tests for services)
2. Expand existing API integration test file
3. Create script tests for backfill_embeddings
4. Achieve ≥80% line coverage, ≥75% branch coverage
5. All tests must pass in < 30 seconds
6. Create implementation report with external validation

**Critical Requirements:**
- Mock all external APIs (OpenRouter, OpenAI)
- No real network calls in tests
- Tests must be independent (can run in any order)
- Use existing fixtures from conftest.py
- Follow existing test patterns

**Report:**
Create detailed report at:
.claude/tasks/TASK-018/subagent-reports/testing-phase-report.md

Must include:
- Test files created (with line counts)
- Test results (pass/fail for each)
- Coverage report (≥80% proof)
- **MANDATORY:** 4 external validation tests with full outputs
- Performance metrics (< 30 seconds)

**Start by reading the subagent-instructions.md file, then implement all tests.**
```

---

## What to Expect

The subagent will:
1. Read detailed instructions
2. Create 6 test files (5 new + expand 1 existing)
3. Implement ~60-70 test cases total
4. Run coverage verification
5. Perform external validation
6. Create comprehensive report

**Timeline:** 1.5-2 hours

---

## Success Criteria

Testing phase complete when:
- ✅ All test files created
- ✅ All tests passing
- ✅ Coverage ≥80% (proven with report)
- ✅ External validation passed (4/4 tests)
- ✅ Tests run in < 30 seconds
- ✅ Report includes coverage proof

---

## Next Steps After Subagent Completes

1. Review testing phase report
2. Verify coverage meets requirements
3. Run external validation myself to confirm
4. Move to VALIDATION phase (final QA)

---

**Ready to launch subagent!**

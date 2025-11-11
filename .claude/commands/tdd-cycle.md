Execute a comprehensive Test-Driven Development (TDD) workflow with strict red-green-refactor discipline (project)

[Extended thinking: Orchestrate complete TDD cycle enforcing test-first development through coordinated workflow.]

## TDD Cycle Overview

**RED → GREEN → REFACTOR**

This command orchestrates the complete TDD workflow for a feature or task, enforcing test-first discipline.

## Prerequisites

Before starting TDD cycle:
- ✅ Requirements are clear (from PLANNING phase)
- ✅ Test scenarios identified (in quality gates)
- ✅ Success criteria defined
- ✅ Appropriate agents identified (playwright-e2e-tester, dev-backend-fastapi, dev-frontend-svelte)

## Phase 1: RED - Write Failing Tests

### Objective
Write comprehensive tests that fail for the right reasons

### Process

1. **Use `/tdd-red` command** to write failing tests
2. **Verify tests fail** with meaningful error messages
3. **Ensure failures** are due to missing implementation, not test errors

### Validation Checkpoint

- [ ] All tests written before implementation
- [ ] All tests fail with meaningful error messages
- [ ] Test failures are due to missing implementation
- [ ] No test passes accidentally
- [ ] Test coverage plan identifies: unit, integration, E2E tests

### Example Output

```bash
❌ should_display_property_details_when_valid_id_provided
   Error: Unable to find element with heading "Property Title"

❌ should_show_error_when_property_not_found
   Error: Expected status 404, got 200

Tests: 0 passed, 2 failed
```

**Status: RED ✅** - Tests fail as expected

---

## Phase 2: GREEN - Make Tests Pass

### Objective
Implement minimal code to make all tests pass

### Process

1. **Use `/tdd-green` command** to implement minimal code
2. **Run tests** to verify they pass
3. **Check coverage** meets thresholds (80% line, 75% branch)

### Implementation Strategies

Choose the simplest approach:
- **Fake It**: Hard-coded values for first test
- **Obvious Implementation**: When solution is trivial
- **Triangulation**: Generalize when multiple tests require it

### Validation Checkpoint

- [ ] All tests pass (100% green)
- [ ] No extra code beyond test requirements
- [ ] Coverage meets minimum thresholds (80/75)
- [ ] No test was modified to make it pass
- [ ] Implementation is minimal and readable

### Example Output

```bash
✅ should_display_property_details_when_valid_id_provided
✅ should_show_error_when_property_not_found

Tests: 2 passed, 0 failed
Coverage: 85% lines, 80% branches
```

**Status: GREEN ✅** - All tests pass

---

## Phase 3: REFACTOR - Improve Code Quality

### Objective
Improve code quality while keeping tests green

### Process

1. **Use `/tdd-refactor` command** to refactor safely
2. **Apply SOLID principles** and design patterns
3. **Reduce complexity** (cyclomatic ≤ 10)
4. **Run tests after each refactoring** to ensure they remain green

### Refactoring Targets

Address these code smells:
- Cyclomatic complexity > 10
- Method length > 20 lines
- Class length > 200 lines
- Duplicate code blocks > 3 lines
- Magic numbers
- Poor naming

### Validation Checkpoint

- [ ] All tests still pass after refactoring
- [ ] Code complexity reduced (cyclomatic ≤ 10)
- [ ] Duplication eliminated (< 3 lines)
- [ ] Performance improved or maintained
- [ ] Test readability improved
- [ ] SOLID principles applied

### Example Output

```bash
✅ should_display_property_details_when_valid_id_provided
✅ should_show_error_when_property_not_found

Tests: 2 passed, 0 failed
Coverage: 90% lines, 85% branches
Complexity: Max 8 (target: ≤10)
```

**Status: REFACTOR ✅** - Code improved, tests still green

---

## Coverage Thresholds

All phases must meet these thresholds:

| Metric | Minimum | Critical Path |
|--------|---------|---------------|
| **Line Coverage** | 80% | 100% |
| **Branch Coverage** | 75% | 100% |
| **Function Coverage** | 80% | 100% |
| **Statement Coverage** | 80% | 100% |

**Critical paths** include:
- Authentication flows
- Payment processing
- Data loss prevention
- Security controls

## Refactoring Triggers

Refactor when code exceeds these limits:

| Metric | Threshold |
|--------|-----------|
| Cyclomatic Complexity | > 10 |
| Method Length | > 20 lines |
| Class Length | > 200 lines |
| Code Duplication | > 3 lines |

## Complete TDD Cycle Example

### Scenario: Implement Property Search Feature

**PLANNING Phase Output:**
- User story: "As a user, I want to search properties by location"
- Test scenarios: valid search, empty results, invalid location
- Success criteria: Results displayed, filters work, loading states

---

### RED Phase

```bash
# Use /tdd-red command
> /tdd-red Implement property search with location filter

# Agent creates: apps/frontend/tests/e2e/property-search.spec.ts
# Tests fail as expected
❌ should_display_results_when_valid_location_searched
❌ should_show_empty_state_when_no_results
❌ should_show_error_when_invalid_location

Tests: 0 passed, 3 failed
```

**Checkpoint:** ✅ Tests written and failing

---

### GREEN Phase

```bash
# Use /tdd-green command
> /tdd-green Implement minimal property search

# Agent creates:
# - apps/frontend/src/routes/search/+page.svelte
# - apps/frontend/src/routes/search/+page.server.ts
# - apps/server/src/server/api/v1/properties/search.py (if needed)

# Tests now pass
✅ should_display_results_when_valid_location_searched
✅ should_show_empty_state_when_no_results
✅ should_show_error_when_invalid_location

Tests: 3 passed, 0 failed
Coverage: 82% lines, 76% branches
```

**Checkpoint:** ✅ Tests pass, coverage met

---

### REFACTOR Phase

```bash
# Use /tdd-refactor command
> /tdd-refactor Improve property search code quality

# Agent refactors:
# - Extract SearchFilters component
# - Extract PropertySearchService
# - Apply Repository pattern
# - Add loading states
# - Improve accessibility

# Tests still pass
✅ should_display_results_when_valid_location_searched
✅ should_show_empty_state_when_no_results
✅ should_show_error_when_invalid_location

Tests: 3 passed, 0 failed
Coverage: 90% lines, 85% branches
Complexity: Max 8
```

**Checkpoint:** ✅ Code improved, tests still green

---

### Final Result

```
✅ Property search feature complete
✅ TDD cycle followed (RED → GREEN → REFACTOR)
✅ All tests passing
✅ Coverage: 90% lines, 85% branches
✅ Complexity: ≤ 10
✅ Code quality: High
✅ Ready for deployment
```

## Integration with SDLC

### PLANNING Phase
Quality Gate 3 (Testing Requirements) ensures:
- Test scenarios identified
- RED-GREEN-REFACTOR planned
- Coverage strategy defined

### IMPLEMENTATION Phase
`/tdd-cycle` orchestrates:
1. Write tests (RED)
2. Implement code (GREEN)
3. Refactor (REFACTOR)

### TESTING Phase
Validates:
- All tests pass
- Coverage thresholds met
- Complexity within limits

### VALIDATION Phase
Confirms:
- Feature works as expected
- Tests serve as documentation
- Code quality maintained

## Success Criteria

A complete TDD cycle is successful when:

- ✅ 100% of code written test-first (RED phase)
- ✅ All tests pass continuously (GREEN phase)
- ✅ Coverage exceeds thresholds (80/75/100)
- ✅ Code complexity within limits (≤ 10)
- ✅ Zero defects in covered code
- ✅ Clear test documentation (test names explain behavior)
- ✅ Fast test execution (< 5 seconds for unit tests)

## Anti-Patterns to Avoid

### ❌ Writing Implementation Before Tests

```typescript
// Bad: Implementation first
function searchProperties(location) {
  return db.query('SELECT * FROM properties WHERE location = ?', [location]);
}

// Then write tests (not TDD!)
it('should search properties', () => {
  expect(searchProperties('Miami')).toBeDefined();
});
```

### ❌ Writing Tests That Already Pass

```typescript
// Bad: Test passes immediately (not RED phase)
it('should return empty array', () => {
  const result = searchProperties('Nonexistent');
  expect(result).toEqual([]); // Passes without implementation!
});
```

### ❌ Skipping Refactor Phase

```typescript
// Bad: Leaving messy code after tests pass
function search(q, l, p, s, f, o) {  // What are these?
  let r = [];
  for(let i=0; i<db.length; i++) {  // Inefficient
    if(db[i].l === l) r.push(db[i]); // Hard to read
  }
  return r;
}
// Tests pass but code is unmaintainable
```

### ❌ Modifying Tests to Make Them Pass

```typescript
// Bad: Changed test expectation instead of fixing implementation
it('should return user details', () => {
  const user = getUser('123');
  expect(user).toBeUndefined(); // Changed from expecting user object!
});
```

## Failure Recovery

### If Tests Won't Fail (RED Phase Issue)

**Problem:** Tests pass immediately
**Solution:**
1. Review test assertions - are they testing the right thing?
2. Ensure implementation doesn't exist yet
3. Add more specific assertions
4. Test edge cases that aren't implemented

### If Tests Won't Pass (GREEN Phase Issue)

**Problem:** Can't get tests to green
**Solution:**
1. Review test requirements carefully
2. Implement one failing test at a time
3. Use "Fake It" strategy initially
4. Ask if tests are testing the right behavior

### If Refactoring Breaks Tests (REFACTOR Phase Issue)

**Problem:** Tests fail after refactoring
**Solution:**
1. **Immediately revert:** `git checkout .`
2. Make smaller incremental changes
3. Run tests after each change
4. Commit successful refactorings immediately

## TDD Metrics Tracking

Track these metrics in `.claude/tasks/TASK-XXX/STATE.json`:

```json
{
  "tdd_metrics": {
    "red_phase_duration": "15 minutes",
    "green_phase_duration": "20 minutes",
    "refactor_phase_duration": "10 minutes",
    "test_count": 12,
    "initial_coverage": "82%",
    "final_coverage": "90%",
    "complexity_max": 8,
    "cycles_count": 1,
    "tests_modified": 0
  }
}
```

## Commands Summary

| Phase | Command | Purpose |
|-------|---------|---------|
| **RED** | `/tdd-red` | Write failing tests |
| **GREEN** | `/tdd-green` | Implement minimal code |
| **REFACTOR** | `/tdd-refactor` | Improve code quality |
| **FULL CYCLE** | `/tdd-cycle` | Orchestrate all phases |

## Quick Reference

### RED Phase Checklist
- [ ] Tests written before code
- [ ] All tests fail
- [ ] Failures are meaningful
- [ ] Coverage plan defined

### GREEN Phase Checklist
- [ ] All tests pass
- [ ] Minimal implementation
- [ ] Coverage ≥ 80/75
- [ ] No tests modified

### REFACTOR Phase Checklist
- [ ] Tests still pass
- [ ] Complexity ≤ 10
- [ ] Duplication removed
- [ ] SOLID applied
- [ ] Performance OK

## Integration with Task System

```bash
# Start a new task with TDD
/task-new US-XXX "Implement property search"

# Planning phase defines test scenarios
/task-plan TASK-XXX

# Implementation phase uses TDD cycle
/tdd-cycle "property search with location filter"

# Validation phase confirms TDD compliance
/task-validate TASK-XXX
```

## Notes

- TDD is **mandatory** for all feature development
- Each phase must be completed before moving to next
- Tests are the **specification** of behavior
- If a test is hard to write, the **design** needs improvement
- Refactoring is **NOT optional**
- Keep test execution **fast** (< 5 seconds for unit tests)
- Tests should be **independent** and **isolated**
- Commit after each successful phase

## Resources

- **TDD Integration Report:** `.claude/reports/20251109-tdd-workflows-plugin-review.md`
- **Quality Gates:** `.claude/skills/planning-quality-gates/SKILL.md` (Gate 3)
- **CI/CD Workflow:** `.github/workflows/ci.yml`
- **Coverage Thresholds:** `pytest.ini`, `vitest.config.ts`

---

**Remember:** RED → GREEN → REFACTOR. Always in that order. No exceptions.

# Testing Strategy Guide

**Version:** 1.0  
**Last Updated:** 2025-11-09  
**Status:** Active

---

## Overview

This document defines the comprehensive testing strategy for the Bestays platform, integrating Test-Driven Development (TDD) workflows, coverage requirements, and quality gates.

**Philosophy:** Tests are not just validation - they are **specifications**, **documentation**, and **safety nets** for refactoring.

---

## TDD Workflow: RED-GREEN-REFACTOR

**All feature development MUST follow the TDD cycle:**

### Phase 1: RED - Write Failing Tests
- Write tests before implementation  
- Verify tests fail meaningfully  
- Coverage plan defined  

**Command:** `/tdd-red`

### Phase 2: GREEN - Make Tests Pass
- Implement minimal code  
- All tests pass  
- Coverage ≥ 80/75  

**Command:** `/tdd-green`

### Phase 3: REFACTOR - Improve Quality
- Apply SOLID principles  
- Reduce complexity (≤ 10)  
- Tests still pass  

**Command:** `/tdd-refactor`

**Full Cycle:** `/tdd-cycle`

---

## Coverage Thresholds

| Metric | Minimum | Critical Path |
|--------|---------|---------------|
| **Line Coverage** | 80% | 100% |
| **Branch Coverage** | 75% | 100% |
| **Function Coverage** | 80% | 100% |

**Critical paths:** Authentication, payments, data modification, security

---

## Test Types

### Unit Tests (Most Tests)
- **What:** Individual functions/components in isolation  
- **Tools:** Vitest (frontend), pytest (backend)  
- **Target:** 80% line, 75% branch coverage

### Integration Tests (Some Tests)  
- **What:** Component interactions, API + database  
- **Tools:** Vitest, pytest  
- **Target:** 75% branch coverage

### E2E Tests (Few Tests)
- **What:** Complete user journeys  
- **Tools:** Playwright (Chromium, Firefox, WebKit)  
- **Target:** 100% critical paths

---

## TDD Commands

| Command | Purpose |
|---------|---------|
| `/tdd-red` | Write failing tests first |
| `/tdd-green` | Implement minimal code |
| `/tdd-refactor` | Improve code quality safely |
| `/tdd-cycle` | Full RED-GREEN-REFACTOR workflow |

**See:** `.claude/commands/tdd-*.md` for details

---

## CI/CD Integration

Tests run automatically on:
- Every push
- Every pull request
- Before merging

**Enforcement:**
- ✅ All tests must pass
- ✅ Coverage ≥ 80/75
- ✅ Blocks merge if tests fail

**Workflow:** `.github/workflows/ci.yml`

---

## Best Practices

### 1. Test-First Development
Always write tests before implementation

### 2. Arrange-Act-Assert Pattern
Structure tests consistently:
```typescript
it('should_X_when_Y', () => {
  // ARRANGE: Setup
  // ACT: Execute
  // ASSERT: Verify
});
```

### 3. One Behavior Per Test
Don't test multiple things in one test

### 4. Test Isolation
Tests should not depend on each other

### 5. Descriptive Names
Use `should_X_when_Y` pattern

### 6. Fast Execution
- Unit tests: < 5 seconds
- Integration: < 30 seconds  
- E2E: < 5 minutes

---

## Anti-Patterns to Avoid

❌ Testing implementation details (test behavior)  
❌ Writing tests after code (TDD requires tests first)  
❌ Complex test setup (keep simple)  
❌ Testing multiple behaviors (one per test)  
❌ Ignoring failing tests (fix or remove)

---

## Quick Reference

### Run Tests
```bash
# Frontend
npm run test:unit
npm run test:coverage
npm run test:e2e

# Backend
pytest
pytest --cov
```

### Coverage Thresholds
- **Lines:** 80% minimum
- **Branches:** 75% minimum
- **Critical paths:** 100%

---

## Resources

- **TDD Integration:** `.claude/reports/20251109-tdd-workflows-plugin-review.md`
- **TDD Commands:** `.claude/commands/tdd-*.md`
- **Quality Gates:** `.claude/skills/planning-quality-gates/SKILL.md` (Gate 3)
- **CI/CD:** `.github/workflows/ci.yml`

---

**Remember:** RED → GREEN → REFACTOR. Always in that order. No exceptions.

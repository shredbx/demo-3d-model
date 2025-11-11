# Quality Gate Enforcement

**Automated enforcement of TDD workflow, external validation, and Storybook usage.**

---

## Overview

This document describes the automated quality gate enforcement mechanisms that ensure:

1. **TDD Workflow** - Test files exist before implementation (RED-GREEN-REFACTOR)
2. **Backend External Validation** - APIs tested from external client perspective (curl)
3. **Frontend Storybook** - Component library usage and documentation
4. **Coverage Thresholds** - 80% line coverage, 75% branch coverage

**Enforcement Layers:**
- **Pre-commit hooks** - Fast local feedback (< 30s)
- **CI/CD pipeline** - Comprehensive validation on push/PR
- **Makefile targets** - Manual quality checks

---

## Enforcement Mechanisms

### 1. Pre-Commit Hook (Local)

**Location:** `.sdlc-workflow/templates/git-hooks/pre-commit-tdd`

**When it runs:** Before `git commit` (local machine)

**What it checks:**
1. ✅ Test files exist for modified implementation files
2. ✅ TypeScript type checking passes
3. ✅ Frontend linting passes (warnings only)
4. ✅ Unit tests pass
5. ✅ Coverage thresholds met

**Target execution time:** < 30 seconds

**Installation:**
```bash
# Install via setup script (recommended)
bash .sdlc-workflow/scripts/setup-git-hooks.sh

# Or use Makefile
make install-hooks

# Or manually
cp .sdlc-workflow/templates/git-hooks/pre-commit-tdd .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Bypass (emergency only):**
```bash
# Skip pre-commit checks (NOT RECOMMENDED)
git commit --no-verify -m "WIP: emergency fix"

# Only bypass for:
# - WIP commits on feature branches
# - Experimental work
# - NEVER for PRs or production
```

**Example output:**
```
🔍 Running TDD quality gates...

[1/5] Checking TDD compliance (test files exist)...
  ✓ TDD compliance check passed
[2/5] TypeScript type checking...
  ✓ TypeScript check passed
[3/5] Linting frontend code...
  ✓ Linting passed
[4/5] Running unit tests...
  ✓ Unit tests passed (42 tests)
[5/5] Validating coverage thresholds...
  ✓ Coverage thresholds checked in test run

✅ All TDD quality gates passed!
   Execution time: 18s
```

---

### 2. CI/CD Pipeline (GitHub Actions)

**Location:** `.github/workflows/ci.yml`

**When it runs:** On push to branches or pull requests

**Jobs:**

#### A. Backend External Validation Job

**Purpose:** Test backend APIs using curl (external client perspective)

**What it does:**
1. Starts Docker services (server, postgres, redis)
2. Waits for backend to be ready (health check)
3. Tests success cases (200 OK)
4. Tests error handling (400/422 for invalid input)
5. Validates response structure

**Script:** `scripts/external-validation.sh`

**Example tests:**
```bash
# Health endpoint
curl -f http://localhost:8011/api/health

# Semantic search (success)
curl -X POST http://localhost:8011/api/v1/properties/search/semantic \
  -H "Content-Type: application/json" \
  -d '{"query": "2BR condo", "locale": "en"}' \
  --fail

# Error handling (expect 400/422)
curl -X POST http://localhost:8011/api/v1/properties/search/semantic \
  -H "Content-Type: application/json" \
  -d '{"invalid": "data"}'
```

**Why external validation matters:**
- Tests API from client perspective (not internal tests)
- Validates actual HTTP behavior (status codes, headers)
- Catches integration issues (database, Redis, services)
- Ensures API contract compliance

#### B. Frontend Storybook Build Job

**Purpose:** Ensure components have Storybook stories and build succeeds

**What it does:**
1. Installs dependencies
2. Builds Storybook for production
3. Checks Storybook coverage (≥ 50% of components)
4. Uploads build artifacts

**Script:** `scripts/check-storybook-coverage.sh`

**Coverage threshold:** 50% (minimum)

**Why Storybook enforcement matters:**
- Prevents non-reusable components
- Forces good component API design
- Provides visual documentation
- Enables visual regression testing
- Improves developer onboarding

#### C. TDD Coverage Check Job

**Purpose:** Verify test files exist for modified implementation files

**What it does:**
1. Checks out code with git history (fetch-depth: 2)
2. Compares HEAD with HEAD~1 (last commit)
3. Verifies test files exist for:
   - Backend: `apps/server/src/**/*.py` → `apps/server/tests/**/*_test.py`
   - Frontend: `apps/frontend/src/lib/components/**/*.svelte` → `.test.ts` OR `.stories.svelte`

**Script:** `scripts/check-tdd-compliance.sh`

**Example output:**
```
🧪 Checking TDD compliance...

Backend files:
  ✓ apps/server/src/api/routes.py (test exists: apps/server/tests/api/routes_test.py)
  ✗ apps/server/src/services/new_service.py (missing test: apps/server/tests/services/new_service_test.py)

Frontend components:
  ✓ apps/frontend/src/lib/components/Button.svelte (story exists: Button.stories.svelte)

❌ TDD compliance check FAILED

Missing tests for:
  apps/server/src/services/new_service.py -> apps/server/tests/services/new_service_test.py

TDD Workflow:
  1. Write test first:  /tdd-red
  2. Make it pass:      /tdd-green
  3. Refactor:          /tdd-refactor
```

---

### 3. Makefile Targets (Manual)

**Purpose:** Run quality checks manually during development

**Available targets:**

```bash
# Check TDD compliance
make check-tdd

# Run external validation (requires services running)
make check-validation

# Check Storybook coverage
make check-storybook

# Run all quality gates
make check-quality-gates

# Pre-commit checks (TDD + fast tests)
make pre-commit

# Install git hooks
make install-hooks
```

**When to use:**
- Before committing (if hooks not installed)
- Debugging failing CI/CD
- Manual verification
- Local development workflow

---

## Quality Gate Scripts

### 1. check-tdd-compliance.sh

**Location:** `scripts/check-tdd-compliance.sh`

**Usage:**
```bash
# Check last commit
bash scripts/check-tdd-compliance.sh

# Check specific range
bash scripts/check-tdd-compliance.sh HEAD~5
```

**Exit codes:**
- `0` - All tests exist
- `1` - Missing tests found

**Rules:**
- Backend `.py` files (except `__init__.py`) require `_test.py` files
- Frontend `.svelte` components require `.test.ts` OR `.stories.svelte`

### 2. external-validation.sh

**Location:** `scripts/external-validation.sh`

**Usage:**
```bash
# Default (localhost:8011)
bash scripts/external-validation.sh

# Custom URL
BACKEND_URL=http://localhost:8012 bash scripts/external-validation.sh
```

**Prerequisites:**
- Services must be running (`make up`)
- Backend must be accessible

**Exit codes:**
- `0` - All validation tests pass
- `1` - Validation failed

**Tests:**
1. Health endpoint (200 OK)
2. Semantic search success case (200 OK)
3. Error handling (400/422 for invalid input)

### 3. check-storybook-coverage.sh

**Location:** `scripts/check-storybook-coverage.sh`

**Usage:**
```bash
bash scripts/check-storybook-coverage.sh
```

**Coverage calculation:**
```
Coverage = (Total Stories / Total Components) * 100
Threshold = 50%
```

**Exit codes:**
- `0` - Coverage ≥ threshold
- `1` - Coverage < threshold

---

## Developer Workflow

### Local Development (with hooks)

```bash
# 1. Install hooks (one-time)
make install-hooks

# 2. Write test first (TDD RED)
# Create test file before implementation

# 3. Make changes
# Edit implementation files

# 4. Commit (hooks run automatically)
git add .
git commit -m "feat: add new feature (US-XXX TASK-YYY)"

# Hook output:
# 🔍 Running TDD quality gates...
# [1/5] Checking TDD compliance...
#   ✓ TDD compliance check passed
# [2/5] TypeScript type checking...
#   ✓ TypeScript check passed
# ...
# ✅ All TDD quality gates passed!
```

### Local Development (without hooks)

```bash
# 1. Run pre-commit checks manually
make pre-commit

# 2. If checks pass, commit
git add .
git commit -m "feat: add new feature (US-XXX TASK-YYY)"

# 3. Push (CI/CD runs full validation)
git push
```

### CI/CD Workflow

```bash
# 1. Push to branch
git push origin feat/TASK-XXX-US-YYY

# 2. GitHub Actions runs:
#    - Frontend type check
#    - Frontend unit tests
#    - Frontend E2E tests
#    - Backend tests (with coverage ≥ 80%)
#    - Backend external validation ← NEW
#    - Frontend Storybook build ← NEW
#    - TDD coverage check ← NEW

# 3. If any job fails → PR blocked
# 4. If all pass → PR can be merged
```

---

## Bypass Procedures (Emergency Only)

### When to Bypass

**ONLY in these scenarios:**
- ❌ Critical production hotfix (deploy immediately)
- ❌ Infrastructure emergency (restore service)
- ❌ CI/CD pipeline broken (fix pipeline itself)

**NEVER bypass for:**
- ❌ "I'll add tests later"
- ❌ Time pressure
- ❌ "It's just a small change"
- ❌ Refactoring

### How to Bypass

#### Pre-commit Hook (Local)
```bash
# Skip pre-commit checks
git commit --no-verify -m "hotfix: critical bug (bypassed hooks)"

# Document reason in commit message
git commit --no-verify -m "hotfix: production down, restore service

BYPASSED HOOKS: TDD check, tests
REASON: Production outage, immediate fix required
FOLLOW-UP: Create TASK-XXX to add tests"
```

#### CI/CD (GitHub)

**Cannot bypass CI/CD checks** - this is by design. If CI/CD fails:

1. **Fix the issue** (add tests, fix errors)
2. **OR push to separate branch** and merge later
3. **OR request admin override** (document reason)

#### Quality Gate Scripts (Manual)

**No bypass needed** - these are informational only, don't block commits.

---

## Troubleshooting

### Pre-commit Hook Fails

**Problem:** "TDD compliance check failed"

**Solution:**
```bash
# See which tests are missing
git diff --cached --name-only

# Create test files
# Backend: apps/server/tests/**/*_test.py
# Frontend: apps/frontend/src/lib/components/**/*.test.ts

# Retry commit
git commit
```

**Problem:** "Unit tests failed"

**Solution:**
```bash
# Run tests locally
cd apps/frontend && npm run test:unit

# Fix failing tests
# Retry commit
git commit
```

### CI/CD Job Fails

**Problem:** "Backend external validation failed"

**Solution:**
```bash
# Run validation locally
make up  # Start services
make check-validation

# Check logs
make logs-server

# Fix API issues
# Retry push
git push
```

**Problem:** "Frontend Storybook build failed"

**Solution:**
```bash
# Build Storybook locally
cd apps/frontend && npm run build-storybook

# Check coverage
make check-storybook

# Add missing stories
# Retry push
git push
```

**Problem:** "TDD coverage check failed"

**Solution:**
```bash
# Check which files are missing tests
make check-tdd

# Add test files
# Retry push
git push
```

### Slow Pre-commit Hooks

**Problem:** Hooks take > 30s

**Target:** < 30s execution time

**Solutions:**
1. **Optimize tests** - Use `it.concurrent` in Vitest
2. **Cache dependencies** - Node modules, Python venv
3. **Disable slow checks** - Edit `.git/hooks/pre-commit`
4. **Use CI/CD only** - Remove local hooks

---

## Configuration

### Coverage Thresholds

**Backend (pytest):**
```python
# apps/server/pytest.ini or vitest.config.ts
[tool:pytest]
cov_fail_under = 80  # 80% line coverage required
```

**Frontend (Vitest):**
```typescript
// apps/frontend/vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      lines: 80,      // 80% line coverage
      branches: 75,   // 75% branch coverage
      functions: 80,
      statements: 80,
    }
  }
})
```

### Storybook Coverage Threshold

**Script:** `scripts/check-storybook-coverage.sh`

```bash
# Line 15
COVERAGE_THRESHOLD=50  # 50% of components must have stories
```

**To change:**
```bash
# Edit threshold
vim scripts/check-storybook-coverage.sh

# Update line 15:
COVERAGE_THRESHOLD=75  # New threshold
```

### External Validation Tests

**Script:** `scripts/external-validation.sh`

**To add new tests:**
```bash
# Edit scripts/external-validation.sh
# Add new test sections after line 70

# Example: Test new endpoint
echo -e "${BLUE}[5/5]${NC} Testing new endpoint..."

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/v1/new-endpoint")

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "  ${GREEN}✓${NC} New endpoint returned 200 OK"
else
    echo -e "  ${RED}✗${NC} New endpoint returned $HTTP_CODE (expected 200)"
    exit 1
fi
```

---

## Metrics and Monitoring

### CI/CD Dashboard

**View pipeline status:**
- **GitHub Actions:** https://github.com/OWNER/REPO/actions
- **Branch protection:** Settings → Branches → main

**Key metrics:**
- Pass rate (target: ≥ 95%)
- Average execution time (target: < 15 minutes)
- Failure reasons (top 3)

### Local Metrics

**Check TDD compliance:**
```bash
make check-tdd
# Output: X/Y files have tests (Z% coverage)
```

**Check Storybook coverage:**
```bash
make check-storybook
# Output: Coverage: X% (threshold: Y%)
```

**Check test coverage:**
```bash
make test-coverage
# Output: Frontend and backend coverage reports
```

---

## Integration with SDLC Workflow

### Phase: IMPLEMENTATION

**Before starting:**
1. ✅ Run `make pre-commit` to verify baseline
2. ✅ Ensure hooks installed (`make install-hooks`)

**During development:**
1. ✅ Write test first (TDD RED)
2. ✅ Implement feature (TDD GREEN)
3. ✅ Refactor (TDD REFACTOR)
4. ✅ Commit (hooks enforce quality)

**Before pushing:**
1. ✅ Run `make check-quality-gates`
2. ✅ Fix any issues
3. ✅ Push to remote

### Phase: TESTING

**E2E tests:**
- Run via `make test-all` or `cd apps/frontend && npm run test:e2e`
- Not enforced in pre-commit (too slow)
- Enforced in CI/CD

**External validation:**
- Run via `make check-validation`
- Requires services running (`make up`)
- Enforced in CI/CD

### Phase: VALIDATION

**PR review checklist:**
- ✅ All CI/CD jobs pass
- ✅ TDD compliance check pass
- ✅ External validation pass
- ✅ Storybook coverage ≥ threshold
- ✅ Code coverage ≥ 80/75

---

## Future Enhancements

### Planned Improvements

1. **Performance profiling** - Add benchmark tests in CI/CD
2. **Visual regression testing** - Storybook + Chromatic
3. **Security scanning** - SAST/DAST in pipeline
4. **Mutation testing** - Verify test quality
5. **Accessibility checks** - Axe in Storybook

### Configuration Options

**Feature flags (future):**
```bash
# .env or CI/CD environment variables
ENFORCE_TDD_STRICT=true          # Fail on any missing test
ENFORCE_STORYBOOK_STRICT=true    # Fail on any missing story
ENFORCE_EXTERNAL_VALIDATION=true # Fail on any validation error
COVERAGE_THRESHOLD_BACKEND=85    # Increase backend threshold
COVERAGE_THRESHOLD_FRONTEND=85   # Increase frontend threshold
```

---

## Summary

**Quality gates ensure:**
- ✅ TDD workflow enforced (tests first, always)
- ✅ Backend APIs validated externally (real HTTP tests)
- ✅ Frontend components documented (Storybook)
- ✅ Coverage thresholds met (80/75)

**Enforcement layers:**
- **Pre-commit hooks** - Fast local feedback (< 30s)
- **CI/CD pipeline** - Comprehensive validation
- **Makefile targets** - Manual checks

**Developer workflow:**
1. Install hooks (`make install-hooks`)
2. Follow TDD (test first)
3. Commit (hooks enforce)
4. Push (CI/CD validates)
5. Merge (all checks pass)

**Bypass only for emergencies** - Document reason, add follow-up task.

---

**Last Updated:** 2025-11-09
**Version:** 1.0.0
**See Also:**
- `.sdlc-workflow/guides/testing-strategy.md` - TDD requirements
- `.sdlc-workflow/guides/backend-validation-requirements.md` - External validation
- `.github/workflows/ci.yml` - CI/CD pipeline
- `Makefile` - Quality gate targets

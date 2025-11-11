# Test Artifacts Policy

**Purpose:** Define what test artifacts are committed to version control and what is excluded.

**Created:** 2025-11-08
**Last Updated:** 2025-11-08

---

## Overview

Test artifacts include reports, screenshots, videos, and cache files generated during test execution. This policy ensures a clean repository while maintaining test reproducibility.

## What Gets Committed

**Test Code & Configuration:**
- ✅ Test files (`*.spec.ts`, `*.test.py`)
- ✅ Test configuration (`playwright.config.ts`, `pytest.ini`)
- ✅ Test fixtures and utilities
- ✅ Test data (small JSON/CSV files for test scenarios)
- ✅ Storybook stories (`*.stories.ts`)

**Documentation:**
- ✅ Test plans and strategies
- ✅ Test coverage reports (summary metrics in markdown)
- ✅ Known issues and test skip justifications

## What Gets Ignored

**Playwright Artifacts:**
- ❌ `playwright-report/` - HTML reports
- ❌ `test-results/` - Test execution results
- ❌ `.playwright/` - Browser cache and state
- ❌ `screenshots/` - Runtime screenshots
- ❌ `videos/` - Test execution videos

**Python Test Artifacts:**
- ❌ `.pytest_cache/` - Pytest cache
- ❌ `htmlcov/` - Coverage HTML reports
- ❌ `.coverage` - Coverage data files
- ❌ `coverage.xml` - Coverage XML reports

**Other Test Artifacts:**
- ❌ `*.log` - Test execution logs
- ❌ `*.tmp` - Temporary files

## .gitignore Rules

**Current configuration in `/Users/solo/Projects/_repos/bestays/.gitignore`:**

```gitignore
# Playwright test artifacts
**/playwright-report/
**/test-results/
**/.playwright/
**/playwright/.cache/

# Test screenshots and videos
**/screenshots/
**/videos/

# Testing (Python)
coverage
coverage.xml
.coverage
htmlcov/
.pytest_cache/
```

**Pattern explanation:**
- `**/` matches in any directory depth
- Covers both frontend (Playwright) and backend (pytest) artifacts
- Prevents accidental commits across the monorepo

## Cleanup Strategy

### Manual Cleanup

**Using git clean (recommended):**
```bash
# Preview what would be deleted
git clean -dn apps/frontend/playwright-report/ apps/frontend/test-results/

# Actually delete
git clean -df apps/frontend/playwright-report/ apps/frontend/test-results/
```

**Using Makefile:**
```bash
# Clean all test artifacts
make clean-test
```

**Manual deletion:**
```bash
rm -rf apps/frontend/playwright-report/
rm -rf apps/frontend/test-results/
rm -rf apps/frontend/.playwright/
```

### Automated Cleanup

**Makefile target:**
```makefile
make clean-test  # Removes all test artifacts
```

**CI/CD:** Test artifacts are regenerated on each run, no cleanup needed.

## Local Development Workflow

**Best practices:**

1. **Run tests locally:**
   ```bash
   cd apps/frontend
   npm run test:e2e
   ```

2. **Review reports locally:**
   - Playwright HTML report opens automatically after test run
   - Manual access: `npx playwright show-report`

3. **Clean up after debugging:**
   ```bash
   make clean-test
   ```

4. **Before committing:**
   ```bash
   git status  # Should NOT show test artifacts
   ```

## CI/CD Artifact Retention

**GitHub Actions / CI environments:**

- Test artifacts are generated during CI runs
- Artifacts are uploaded as build artifacts (retention: 30-90 days)
- Screenshots/videos help debug failures
- Artifacts are NOT committed to repository

**Retention policy:**
- CI artifacts: 30 days (GitHub Actions default)
- Local artifacts: Clean up manually or via `make clean-test`

## Troubleshooting

### Test artifacts appear in git status

**Problem:** `git status` shows untracked files in `playwright-report/` or `test-results/`

**Solution:**
```bash
# Check if .gitignore patterns work
git check-ignore -v apps/frontend/playwright-report/index.html

# If not matched, update .gitignore
# If matched but still showing, they were previously tracked
git rm -r --cached apps/frontend/playwright-report/
git rm -r --cached apps/frontend/test-results/
```

### Previously tracked files

**Problem:** Files were committed before .gitignore rules existed

**Solution:**
```bash
# Remove from git index (keeps local files)
git rm -r --cached apps/frontend/playwright-report/
git rm -r --cached apps/frontend/test-results/

# Commit the removal
git commit -m "chore: remove test artifacts from version control"
```

### Verify .gitignore rules

**Test patterns:**
```bash
# Should output the matching .gitignore rule
git check-ignore -v apps/frontend/playwright-report/index.html
git check-ignore -v apps/frontend/test-results/some-test/
git check-ignore -v apps/frontend/.playwright/cache.db
```

## When to Review/Update

**Review this policy when:**
- Adding new test frameworks
- Changing test artifact locations
- Adding new types of test reports
- Team feedback on repository clutter
- CI/CD changes affect artifact generation

**Update .gitignore when:**
- New test artifact directories are created
- New test frameworks are added
- Test tools change their output locations

## Related Documentation

- **Test Strategy:** `.sdlc-workflow/guides/testing-strategy.md` (if exists)
- **CI/CD Pipeline:** `.github/workflows/` (if exists)
- **Playwright Config:** `apps/frontend/playwright.config.ts`
- **Pytest Config:** `apps/server/pytest.ini` (if exists)

---

**Version:** 1.0
**Status:** Active

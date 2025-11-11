# TASK-003: Test Strategy

**Task:** Enhance pre-tool-use hook
**Testing Framework:** pytest + subprocess

---

## Test Categories

### 1. Unit Tests - Command Detection

| Test | Input | Expected |
|------|-------|----------|
| `test_detects_checkout_b` | `git checkout -b feat/TASK-001-US-001` | True |
| `test_detects_checkout_branch` | `git checkout --branch feat/TASK-001-US-001` | True |
| `test_ignores_checkout_existing` | `git checkout main` | False |
| `test_ignores_git_status` | `git status` | False |
| `test_ignores_non_git` | `npm install` | False |

### 2. Unit Tests - Branch Name Extraction

| Test | Command | Expected Branch |
|------|---------|----------------|
| `test_extract_basic` | `git checkout -b feat/TASK-001-US-001` | `feat/TASK-001-US-001` |
| `test_extract_quoted_double` | `git checkout -b "feat/TASK-001-US-001"` | `feat/TASK-001-US-001` |
| `test_extract_quoted_single` | `git checkout -b 'feat/TASK-001-US-001'` | `feat/TASK-001-US-001` |
| `test_extract_with_track` | `git checkout -b feat/TASK-001-US-001 --track` | `feat/TASK-001-US-001` |
| `test_extract_with_and` | `git checkout -b feat/TASK-001-US-001 && git push` | `feat/TASK-001-US-001` |

### 3. Integration Tests - Hook Behavior

| Test | Command | Expected Exit Code |
|------|---------|-------------------|
| `test_allows_valid_branch` | `git checkout -b feat/TASK-001-US-001` | 0 (allow) |
| `test_blocks_invalid_branch` | `git checkout -b feature/US-001` | 2 (block) |
| `test_allows_non_git` | `npm install` | 0 (allow) |
| `test_allows_git_status` | `git status` | 0 (allow) |

### 4. Fail-Safe Tests

| Test | Scenario | Expected |
|------|----------|----------|
| `test_allow_if_script_missing` | Validation script not found | Exit 0 (allow) |
| `test_allow_if_script_timeout` | Validation script times out | Exit 0 (allow) |
| `test_allow_if_cant_parse_json` | Invalid JSON input | Exit 0 (allow) |
| `test_allow_if_cant_extract_branch` | Malformed command | Exit 0 (allow) |

### 5. Error Message Tests

| Test | Validation |
|------|-----------|
| `test_error_shows_invalid_branch` | Contains branch name |
| `test_error_shows_pattern` | Contains expected pattern |
| `test_error_shows_examples` | Contains valid examples |
| `test_error_references_docs` | Contains GIT_WORKFLOW.md reference |

### 6. Performance Tests

| Test | Action | Expected |
|------|--------|----------|
| `test_performance_overhead` | Time hook execution | < 100ms |
| `test_no_slowdown_non_git` | Non-git commands fast | < 10ms overhead |

---

## Manual Testing Checklist

- [ ] Create valid branch → succeeds
- [ ] Create invalid branch → blocked with error
- [ ] Non-git commands → no interference
- [ ] Git status/commit → no interference
- [ ] All current branches → work correctly
- [ ] Fail-safe: rename validation script → still allows
- [ ] Error message → clear and actionable

---

**Success:** All tests pass + no false positives/negatives

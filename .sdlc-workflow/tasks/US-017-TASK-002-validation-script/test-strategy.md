# TASK-002: Test Strategy

**Task:** Create branch validation script
**Testing Framework:** pytest

---

## Test Coverage Goals

- **Target:** >90% code coverage
- **Focus Areas:**
  - Regex pattern validation (all valid and invalid patterns)
  - Error message generation
  - Exit code behavior
  - Edge cases and boundary conditions
  - Performance characteristics

---

## Test Categories

### 1. Valid Branch Names Tests

**Purpose:** Verify all valid branch patterns are accepted

**Test Cases:**

| Test Name | Input | Expected | Rationale |
|-----------|-------|----------|-----------|
| `test_valid_feat_branch` | `feat/TASK-001-US-001` | Valid | Basic feat pattern |
| `test_valid_fix_branch` | `fix/TASK-042-US-001` | Valid | Basic fix pattern |
| `test_valid_refactor_branch` | `refactor/TASK-005-US-001B` | Valid | Refactor with letter suffix |
| `test_valid_test_branch` | `test/TASK-010-US-002` | Valid | Test branch type |
| `test_valid_docs_branch` | `docs/TASK-020-US-005` | Valid | Docs branch type |
| `test_valid_chore_branch` | `chore/TASK-030-US-010` | Valid | Chore branch type |
| `test_main_branch` | `main` | Valid | Special case |

**Implementation:**
```python
import pytest
from validate_branch import validate_branch_name

def test_valid_feat_branch():
    is_valid, msg = validate_branch_name("feat/TASK-001-US-001")
    assert is_valid
    assert msg == ""

def test_all_valid_types():
    """Test all 6 valid branch types."""
    valid_types = ['feat', 'fix', 'refactor', 'test', 'docs', 'chore']
    for branch_type in valid_types:
        branch = f"{branch_type}/TASK-001-US-001"
        is_valid, msg = validate_branch_name(branch)
        assert is_valid, f"{branch} should be valid, got: {msg}"
```

---

### 2. Edge Cases Tests

**Purpose:** Verify edge cases and boundary conditions are handled correctly

**Test Cases:**

| Test Name | Input | Expected | Rationale |
|-----------|-------|----------|-----------|
| `test_story_letter_suffix_single` | `feat/TASK-001-US-001B` | Valid | Single letter suffix |
| `test_story_letter_suffix_z` | `feat/TASK-001-US-001Z` | Valid | Letter Z suffix |
| `test_with_description` | `feat/TASK-001-US-001-login` | Valid | Optional description |
| `test_long_description` | `feat/TASK-001-US-001-very-long-description-here` | Valid | Long description |
| `test_description_underscore` | `feat/TASK-001-US-001-login_flow` | Valid | Underscore in description |
| `test_description_numbers` | `feat/TASK-001-US-001-v2-update` | Valid | Numbers in description |
| `test_large_task_number` | `feat/TASK-999-US-001` | Valid | Large task number |
| `test_large_story_number` | `feat/TASK-001-US-999` | Valid | Large story number |

**Implementation:**
```python
def test_edge_cases():
    """Test edge cases."""
    edge_cases = [
        "feat/TASK-001-US-001B",
        "feat/TASK-001-US-001Z",
        "feat/TASK-001-US-001-login-flow",
        "feat/TASK-001-US-001-login_flow",
        "feat/TASK-999-US-999Z",
    ]
    for branch in edge_cases:
        is_valid, msg = validate_branch_name(branch)
        assert is_valid, f"{branch} should be valid, got: {msg}"
```

---

### 3. Invalid Branch Names Tests

**Purpose:** Verify invalid patterns are correctly rejected

**Test Cases:**

| Test Name | Input | Expected Error | Rationale |
|-----------|-------|----------------|-----------|
| `test_invalid_old_pattern` | `feature/US-001` | "old story-based" | Old pattern from docs |
| `test_invalid_old_with_desc` | `feature/US-001-login` | "old story-based" | Old pattern with description |
| `test_invalid_no_task` | `feat/US-001` | "missing task reference" | Missing TASK- prefix |
| `test_invalid_no_story` | `feat/TASK-001` | Invalid | Missing US- reference |
| `test_invalid_wrong_type` | `feature/TASK-001-US-001` | Invalid | Wrong type (feature vs feat) |
| `test_invalid_malformed_separator` | `feat-TASK-001-US-001` | Invalid | Wrong separator |
| `test_invalid_no_slash` | `featTASK-001-US-001` | Invalid | Missing slash |
| `test_invalid_uppercase_type` | `FEAT/TASK-001-US-001` | Invalid | Uppercase type |
| `test_invalid_random_string` | `random-branch-name` | Invalid | Random string |
| `test_invalid_empty` | `` | Invalid | Empty string |

**Implementation:**
```python
def test_invalid_old_pattern():
    """Test old story-based pattern is rejected."""
    is_valid, msg = validate_branch_name("feature/US-001")
    assert not is_valid
    assert "old story-based naming" in msg

def test_invalid_patterns():
    """Test various invalid patterns."""
    invalid_branches = [
        "feature/US-001",
        "feat/US-001",
        "feat/TASK-001",
        "feature/TASK-001-US-001",
        "FEAT/TASK-001-US-001",
        "random-branch",
    ]
    for branch in invalid_branches:
        is_valid, msg = validate_branch_name(branch)
        assert not is_valid, f"{branch} should be invalid"
        assert msg != "", f"Error message should be provided for {branch}"
```

---

### 4. Error Message Quality Tests

**Purpose:** Verify error messages are helpful and actionable

**Test Cases:**

| Test Name | Validation | Rationale |
|-----------|------------|-----------|
| `test_error_msg_old_pattern_specific` | Contains "old story-based naming" | Identifies specific problem |
| `test_error_msg_shows_examples` | Contains "feat/TASK-001-US-001" | Shows correct example |
| `test_error_msg_shows_valid_types` | Contains all 6 valid types | Lists valid options |
| `test_error_msg_missing_task` | Contains "missing task reference" | Specific guidance |
| `test_error_msg_not_empty` | Message length > 50 chars | Sufficiently detailed |

**Implementation:**
```python
def test_error_message_for_old_pattern():
    """Test error message for old pattern is helpful."""
    is_valid, msg = validate_branch_name("feature/US-001-login")
    assert not is_valid
    assert "old story-based naming" in msg
    assert "feat/TASK-001-US-001" in msg  # Shows correct example
    assert "Valid types:" in msg  # Shows valid options

def test_error_message_shows_all_types():
    """Test error message shows all valid types."""
    _, msg = validate_branch_name("invalid-branch")
    valid_types = ['feat', 'fix', 'refactor', 'test', 'docs', 'chore']
    for branch_type in valid_types:
        assert branch_type in msg

def test_error_message_quality():
    """Test error messages are sufficiently detailed."""
    invalid_branches = [
        "feature/US-001",
        "feat/US-001",
        "random-branch",
    ]
    for branch in invalid_branches:
        _, msg = validate_branch_name(branch)
        assert len(msg) > 50, f"Error message too short for {branch}"
        assert "Expected pattern:" in msg or "Example:" in msg
```

---

### 5. Integration Tests

**Purpose:** Verify script works with actual git repository

**Test Cases:**

| Test Name | Action | Expected | Rationale |
|-----------|--------|----------|-----------|
| `test_get_current_branch` | Call get_current_branch() | Returns branch name | Git integration works |
| `test_validates_all_current_branches` | Validate all existing branches | All valid | No false positives |
| `test_script_exit_codes` | Run script via subprocess | Correct exit codes | CLI interface works |

**Implementation:**
```python
import subprocess

def test_validates_current_branches():
    """Test that all current branches in repo are valid."""
    # These are the actual branches in our repo (from research)
    current_branches = [
        "main",
        "feat/TASK-001-US-001",
        "feat/TASK-002-US-001B",
        "feat/TASK-003-US-001B",
        "feat/TASK-004-US-001B",
        "refactor/TASK-005-US-001B",
        "test/TASK-006-US-001B",
    ]

    for branch in current_branches:
        is_valid, msg = validate_branch_name(branch)
        assert is_valid, f"Current branch '{branch}' should be valid but got: {msg}"

def test_script_exit_codes():
    """Test script returns correct exit codes."""
    # Test valid branch
    result = subprocess.run(
        [".sdlc-workflow/scripts/validate_branch.py", "feat/TASK-001-US-001"],
        capture_output=True
    )
    assert result.returncode == 0

    # Test invalid branch
    result = subprocess.run(
        [".sdlc-workflow/scripts/validate_branch.py", "feature/US-001"],
        capture_output=True
    )
    assert result.returncode == 1
```

---

### 6. Performance Tests

**Purpose:** Verify script meets performance requirements (< 100ms)

**Test Cases:**

| Test Name | Action | Expected | Rationale |
|-----------|--------|----------|-----------|
| `test_single_validation_fast` | Validate 1 branch | < 10ms | Individual calls are fast |
| `test_batch_validation_fast` | Validate 100 branches | < 100ms total | Meets performance SLA |
| `test_regex_compiled` | Check regex compilation | Compiled at module level | Optimization verification |

**Implementation:**
```python
import time

def test_validation_performance():
    """Test validation is fast enough."""
    start = time.time()
    for i in range(100):
        validate_branch_name(f"feat/TASK-{i}-US-001")
    elapsed = time.time() - start

    assert elapsed < 0.1, f"100 validations took {elapsed}s (should be < 0.1s)"

def test_single_validation_performance():
    """Test single validation is very fast."""
    start = time.time()
    validate_branch_name("feat/TASK-001-US-001")
    elapsed = time.time() - start

    assert elapsed < 0.01, f"Single validation took {elapsed}s (should be < 0.01s)"
```

---

## Test Execution

### Running Tests

```bash
# Run all tests
pytest tests/test_validate_branch.py -v

# Run with coverage
pytest tests/test_validate_branch.py --cov=.sdlc-workflow/scripts/validate_branch --cov-report=html

# Run specific test category
pytest tests/test_validate_branch.py::test_valid_feat_branch -v

# Run performance tests only
pytest tests/test_validate_branch.py -k performance -v
```

### Coverage Requirements

```bash
# Generate coverage report
pytest tests/test_validate_branch.py --cov=validate_branch --cov-report=term-missing

# Expected output:
# Name                            Stmts   Miss  Cover   Missing
# -------------------------------------------------------------
# validate_branch.py                 45      2    95%    78-79
# -------------------------------------------------------------
# TOTAL                              45      2    95%

# Minimum acceptable: 90%
```

---

## Test Data

### Valid Branch Examples (from actual repo)
```python
VALID_BRANCHES = [
    "main",
    "feat/TASK-001-US-001",
    "feat/TASK-002-US-001B",
    "feat/TASK-003-US-001B",
    "feat/TASK-004-US-001B",
    "refactor/TASK-005-US-001B",
    "test/TASK-006-US-001B",
    "fix/TASK-042-US-001B",
    "docs/TASK-020-US-005",
    "chore/TASK-030-US-010",
]
```

### Invalid Branch Examples
```python
INVALID_BRANCHES = [
    "feature/US-001",  # Old pattern
    "feature/US-001-login",  # Old pattern with description
    "feat/US-001",  # Missing TASK
    "feat/TASK-001",  # Missing US
    "feature/TASK-001-US-001",  # Wrong type prefix
    "FEAT/TASK-001-US-001",  # Uppercase type
    "feat-TASK-001-US-001",  # Wrong separator
    "random-branch-name",  # Random string
    "",  # Empty string
]
```

---

## Acceptance Criteria Validation

| AC | Test Coverage | Verification Method |
|----|---------------|-------------------|
| AC-1 | - | File exists check |
| AC-2 | `test_all_valid_types` | Tests all 6 types |
| AC-3 | `test_main_branch` | Tests main branch |
| AC-4 | `test_invalid_old_pattern` | Tests rejection |
| AC-5 | `test_script_exit_codes` | Tests exit codes |
| AC-6 | `test_error_message_*` | Tests error messages |
| AC-7 | `test_validation_performance` | Benchmark test |
| AC-8 | Coverage report | pytest-cov |
| AC-9 | `test_validates_current_branches` | Integration test |

---

## Testing Checklist

Before marking task complete:

- [ ] All valid branch tests pass
- [ ] All invalid branch tests pass
- [ ] All edge case tests pass
- [ ] Error message quality tests pass
- [ ] Performance tests pass (< 100ms)
- [ ] Integration tests pass (current branches valid)
- [ ] Code coverage > 90%
- [ ] No false positives (valid branches rejected)
- [ ] No false negatives (invalid branches accepted)
- [ ] Exit codes work correctly (0, 1, 2)
- [ ] Script executable and has shebang
- [ ] Manual testing completed

---

## Manual Testing

After automated tests pass, perform manual verification:

```bash
# 1. Test valid branch
.sdlc-workflow/scripts/validate_branch.py feat/TASK-001-US-001
# Expected: ✅ Branch name valid

# 2. Test invalid branch
.sdlc-workflow/scripts/validate_branch.py feature/US-001
# Expected: ❌ Error message with guidance

# 3. Test current branch
git checkout main
.sdlc-workflow/scripts/validate_branch.py
# Expected: ✅ Branch name valid: main

# 4. Test all current branches
git branch | sed 's/^[* ]*//' | while read branch; do
  echo "Testing: $branch"
  .sdlc-workflow/scripts/validate_branch.py "$branch"
done
# Expected: All branches valid

# 5. Verify exit codes
.sdlc-workflow/scripts/validate_branch.py feat/TASK-001-US-001
echo "Exit code: $?"  # Should be 0

.sdlc-workflow/scripts/validate_branch.py invalid-branch
echo "Exit code: $?"  # Should be 1
```

---

## Test Maintenance

As branch naming requirements evolve:

1. **Adding new branch type:**
   - Update `VALID_TYPES` in script
   - Update regex pattern
   - Add test case to `test_all_valid_types`

2. **Changing pattern:**
   - Update regex in script
   - Update all test expectations
   - Update error message examples

3. **Adding new validation:**
   - Add test case first (TDD)
   - Implement validation logic
   - Verify all existing tests still pass

---

## Success Criteria

✅ **Test suite is comprehensive:**
- Covers all valid branch types
- Covers all edge cases
- Covers all invalid patterns
- Tests error message quality
- Tests performance
- Tests integration with git

✅ **All tests pass:**
- 100% of unit tests passing
- Integration tests passing
- Performance benchmarks met
- Manual testing successful

✅ **Coverage goal met:**
- >90% code coverage
- No critical paths untested
- All branches tested

✅ **Quality verified:**
- No false positives
- No false negatives
- Error messages helpful
- Exit codes correct

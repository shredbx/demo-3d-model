# TASK-003: Enhance Pre-Tool-Use Hook

**Story:** US-017 - SDLC Branch Naming Validation
**Status:** NOT_STARTED
**Assigned To:** devops-infra subagent
**Estimated Effort:** 2-3 hours
**Priority:** HIGH

---

## Objective

Enhance `.claude/hooks/pre_tool_use.py` to validate git branch names before branch creation operations, integrating with the validation script created in TASK-002.

---

## Context

The pre-tool-use hook currently exists as a placeholder that allows all tool calls without validation. This task adds branch name validation logic that:

1. Detects git branch creation commands (`git checkout -b`)
2. Extracts the branch name from the command
3. Calls the validation script (TASK-002)
4. Blocks invalid branch names with clear error messages
5. Allows valid branch names to proceed

**Current Hook:** `.claude/hooks/pre_tool_use.py` (placeholder, lines 1-23)
**Research:** `.claude/reports/20251107-git-branching-audit.md`

---

## What Needs to Be Done

1. Read current hook implementation (understand structure)
2. Add branch name validation logic
3. Integrate with `validate_branch.py` script
4. Parse git commands to extract branch names
5. Implement fail-safe behavior (allow if script missing)
6. Provide clear, actionable error messages
7. Ensure minimal performance impact (< 100ms overhead)
8. Create integration tests

---

## Valid vs Invalid Branch Creation

**Should Validate:**
```bash
git checkout -b feat/TASK-001-US-001         # Valid - should allow
git checkout -b feature/US-001-login         # Invalid - should block
git checkout -b some-random-branch           # Invalid - should block
```

**Should NOT Validate:**
```bash
git status                                   # Not branch creation - allow
git commit -m "message"                      # Not branch creation - allow
git checkout main                            # Switching branches - allow
npm install                                  # Not git - allow
```

---

## Acceptance Criteria

- [ ] **AC-1:** Hook detects `git checkout -b` commands
- [ ] **AC-2:** Hook extracts branch name from command correctly
- [ ] **AC-3:** Hook calls `validate_branch.py` for validation
- [ ] **AC-4:** Hook exits with code 2 (blocks) for invalid branches
- [ ] **AC-5:** Hook exits with code 0 (allows) for valid branches
- [ ] **AC-6:** Hook has fail-safe: allows if validation script missing
- [ ] **AC-7:** Hook has fail-safe: allows if validation script crashes
- [ ] **AC-8:** Error messages are clear and actionable
- [ ] **AC-9:** Error messages include correct pattern examples
- [ ] **AC-10:** Hook adds < 100ms overhead to git operations
- [ ] **AC-11:** Hook doesn't interfere with non-git operations
- [ ] **AC-12:** Integration tests verify blocking behavior
- [ ] **AC-13:** No false positives (valid branches blocked)
- [ ] **AC-14:** No false negatives (invalid branches allowed)

---

## Exit Code Specification

The hook must return specific exit codes:

```python
EXIT_ALLOW = 0      # Allow tool execution (valid branch OR not branch creation)
EXIT_BLOCK = 2      # Block tool execution (invalid branch name)
```

**Important:** Exit code 2 blocks tool execution in Claude's hook system.

---

## Hook Integration Architecture

```
User → Claude → Tool Call → Pre-Tool-Use Hook
                                 ↓
                    Is it "git checkout -b"?
                         ↓           ↓
                       Yes          No → Exit 0 (allow)
                         ↓
                Extract branch name
                         ↓
              Call validate_branch.py
                         ↓
                  Valid? Invalid?
                   ↓         ↓
                Exit 0    Exit 2
                (allow)   (block)
```

---

## Command Parsing Requirements

Must handle various command formats:

```bash
# Basic format
git checkout -b feat/TASK-001-US-001

# With quotes
git checkout -b "feat/TASK-001-US-001"
git checkout -b 'feat/TASK-001-US-001'

# With additional flags
git checkout -b feat/TASK-001-US-001 --track origin/main

# Multiple spaces
git  checkout   -b   feat/TASK-001-US-001

# Combined with other commands (sequential)
git checkout -b feat/TASK-001-US-001 && git push
```

**Extraction Strategy:**
1. Detect `git checkout -b` or `git checkout --branch`
2. Find argument after `-b` or `--branch` flag
3. Strip quotes if present
4. Stop at next flag or &&/;/|

---

## Error Message Requirements

When blocking invalid branch name, show:

```
❌ BLOCKED: Invalid branch name 'feature/US-001-login'

The branch name doesn't follow the SDLC naming convention.

Expected pattern: {type}/TASK-{number}-US-{story}[-description]

Valid examples:
  feat/TASK-001-US-001
  fix/TASK-042-US-001B
  refactor/TASK-005-US-001B-cleanup

Valid types: feat, fix, refactor, test, docs, chore

To fix:
  git checkout -b feat/TASK-XXX-US-XXX

For more information, see: .sdlc-workflow/GIT_WORKFLOW.md
```

---

## Fail-Safe Behavior

**Critical:** Hook must be fail-safe to avoid breaking workflow

**Fail-Safe Rules:**

1. **If validation script not found** → Allow (exit 0)
   - Don't block work due to missing script
   - Log warning

2. **If validation script crashes** → Allow (exit 0)
   - Don't block work due to script bugs
   - Log error

3. **If unable to parse command** → Allow (exit 0)
   - Don't block work due to parsing errors
   - Log warning

4. **If in doubt** → Allow (exit 0)
   - Better to allow potentially invalid than block valid work

**Rationale:** Development workflow must not break due to validation tooling.

---

## Technical Constraints

- **Language:** Python 3.10+
- **Dependencies:** Standard library only
- **Performance:** < 100ms overhead per git operation
- **Compatibility:** Must work on macOS, Linux
- **Hook Version:** Preserve existing hook structure

---

## Implementation Details

See `implementation-spec.md` for detailed technical specification.

---

## Test Strategy

See `test-strategy.md` for comprehensive test plan.

---

## Dependencies

**Requires:**
- ✅ TASK-002 completed (validation script exists)
- Python 3.10+ (already available)
- `.claude/hooks/` infrastructure (already exists)

**Blocks:**
- Documentation tasks can proceed in parallel
- This task doesn't block TASK-004, TASK-005, TASK-006

---

## Risk Assessment

**Risk Level:** MEDIUM-HIGH ⚠️

**Why Medium-High:**
- Modifies critical infrastructure (runs on EVERY tool call)
- Could block valid branches if regex/parsing is wrong
- Could break workflow if hook crashes
- Difficult to debug (runs before tools execute)

**Mitigation:**
- ✅ Comprehensive testing before deployment
- ✅ Fail-safe behavior (allow on errors)
- ✅ Integration tests with all current branches
- ✅ Manual testing required
- ✅ Keep backup of original hook
- ✅ Easy rollback (revert to placeholder)

---

## Rollback Plan

**If issues occur after deployment:**

1. **Immediate rollback** (< 1 minute):
   ```bash
   # Revert hook to placeholder version
   git checkout HEAD~1 .claude/hooks/pre_tool_use.py
   ```

2. **Temporary disable** (< 30 seconds):
   ```bash
   # Make hook always allow
   echo "import sys; sys.exit(0)" > .claude/hooks/pre_tool_use.py
   ```

3. **Debug mode:**
   ```bash
   # Add debug logging to understand issue
   # Test manually before re-enabling
   ```

**Rollback Risk:** LOW (simple file revert)

---

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Integration tests passing
- [ ] All current branches allowed (no false positives)
- [ ] Invalid branches blocked (no false negatives)
- [ ] Performance overhead < 100ms
- [ ] Fail-safe behavior tested
- [ ] Error messages clear and actionable
- [ ] Manual testing completed
- [ ] Backup of original hook saved
- [ ] Subagent report saved to task folder

---

## Files to Create/Modify

**Modified Files:**
- `.claude/hooks/pre_tool_use.py` (enhance from placeholder)

**New Files:**
- `tests/integration/test_pre_tool_use_hook.py` (integration tests)
- `.claude/hooks/pre_tool_use.py.backup` (backup of original)

---

## Related Documentation

- Current Hook: `.claude/hooks/pre_tool_use.py`
- Hook System: `.claude/hooks/README.md`
- Validation Script: TASK-002 artifacts
- Research: `.claude/reports/20251107-git-branching-audit.md`
- Story: `.sdlc-workflow/stories/infrastructure/US-017-infrastructure-sdlc-branch-naming-validation.md`

---

**Created:** 2025-11-07
**Last Updated:** 2025-11-07

# Task: [Short Description]

**Story:** US-XXX - [Story Name]
**Task ID:** TASK-YYY-semantic-name
**Created:** YYYY-MM-DD
**Status:** NOT_STARTED

**Semantic Name:** `semantic-name` (2-3 words describing task purpose)

---

## Objective

[Clear description of what needs to be accomplished]

**Choosing Semantic Name:**
1. Extract 2-3 key words from task description
2. Use lowercase with hyphens (e.g., `clerk-mounting`, `login-tests`)
3. Focus on task purpose, not full description
4. This name will appear in:
   - Branch name: `feat/TASK-YYY-semantic-name-US-XXX`
   - Commit messages: `(US-XXX TASK-YYY-semantic-name)`
   - Git history for self-documenting context

---

## Scope

### Files to Modify

**Backend:**
- `apps/server/path/to/file1.py`
- `apps/server/path/to/file2.py`

**Frontend:**
- `apps/frontend/src/path/to/file1.svelte`
- `apps/frontend/src/path/to/file2.ts`

**Tests:**
- `apps/frontend/tests/e2e/test-name.spec.ts`

### Subagents Needed

- [ ] `dev-backend-fastapi` for backend files
- [ ] `dev-frontend-svelte` for frontend files
- [ ] `playwright-e2e-tester` for E2E tests
- [ ] `qa-code-auditor` for code review

---

## Acceptance Criteria

- [ ] AC-1: [Specific criterion]
- [ ] AC-2: [Specific criterion]
- [ ] AC-3: [Specific criterion]

---

## Implementation Notes

### Pattern to Follow

[Describe the pattern/approach to use, reference existing examples]

### Dependencies

- Depends on: [Other tasks if any]
- Blocks: [Tasks blocked by this one]

### References

- User Story: `.sdlc-workflow/stories/[domain]/US-XXX-[name].md`
- Existing Examples: [List files with similar patterns]
- Related Specs: [Any relevant spec documents]

---

## Estimated Effort

**Time Estimate:** X hours

**Breakdown:**
- Backend work: Y hours
- Frontend work: Z hours
- Testing: W hours
- Review: V hours

---

## Context

[Additional context, background, or constraints that affect this task]

---

## Related Links

- GitHub Issue: #XXX
- Design Doc: [link]
- API Spec: [link]

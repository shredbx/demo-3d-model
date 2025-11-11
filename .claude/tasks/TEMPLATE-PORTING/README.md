# Task: {task_id} - Port {feature} to {target_product}

**Type:** PORTING
**Story:** {story_id}
**Source Product:** {source_product}
**Target Product:** {target_product}
**Source Task:** {source_task_id}
**Status:** {status}
**Phase:** {phase}
**Created:** {date}

---

## Purpose

Port the implementation of {feature} from {source_product} to {target_product}, adapting product-specific elements while maintaining core functionality.

---

## Source Implementation

**Original Task:** {source_task_id}
**Location:** `.claude/tasks/{source_task_id}/`

**Key Files Implemented:**
- {file1}
- {file2}
- {file3}

**Design Decisions:** See `.claude/tasks/{source_task_id}/planning/decisions.md`

---

## Porting Scope

### Portable Elements (Copy/Adapt)

Elements that can be ported with minimal changes:

- **Core Logic:**
  - {describe core logic that's product-agnostic}
  - {e.g., validation rules, API integration, data models}

- **UI Components:**
  - {list reusable UI components}
  - {e.g., form fields, buttons, layouts}

- **Tests:**
  - {list test scenarios that apply to both products}

### Product-Specific Adaptations

Elements that require adaptation for {target_product}:

- **Configuration:**
  - Environment variables
  - API endpoints
  - Feature flags

- **Business Logic:**
  - {describe product-specific rules}
  - {e.g., role mappings, workflow differences}

- **UI/UX:**
  - Branding (colors, logos, fonts)
  - Copy/messaging
  - Navigation structure

- **Data:**
  - Database schema differences
  - Product-specific fields

---

## Implementation Checklist

See `planning/porting-checklist.md` for detailed checklist.

**High-Level Steps:**
1. [ ] Review source implementation
2. [ ] Identify product-specific adaptations needed
3. [ ] Copy portable files to {target_product} codebase
4. [ ] Adapt configuration and environment variables
5. [ ] Update business logic for {target_product} requirements
6. [ ] Adapt UI/UX (branding, navigation, copy)
7. [ ] Update tests for {target_product} context
8. [ ] Manual QA on {target_product} domain
9. [ ] Deploy to {target_product} staging
10. [ ] Validate in production

---

## Success Criteria

This porting task is complete when:

- [ ] All portable functionality works in {target_product}
- [ ] All product-specific elements adapted correctly
- [ ] All tests passing for {target_product}
- [ ] Manual QA completed and approved
- [ ] Deployed to {target_product} production
- [ ] No regressions in {source_product}

---

## Subagent Assignment

**Primary Subagent:** {subagent_type}

**Instructions for Subagent:**
1. Read source implementation: `.claude/tasks/{source_task_id}/`
2. Read porting checklist: `planning/porting-checklist.md`
3. Copy portable files and adapt for {target_product}
4. Document adaptations in `subagent-reports/{subagent}-report.md`
5. Note any unexpected challenges or trade-offs

---

## Timeline

**Estimated Effort:** {estimate} hours/days
**Started:** {start_date}
**Completed:** {completion_date}

---

## References

- **Source Task:** `.claude/tasks/{source_task_id}/`
- **User Story:** `.sdlc-workflow/stories/{domain}/{story_id}.md`
- **Porting Decision:** `.claude/reports/20251107-multi-product-story-workflow.md`

---

**Template Version:** 1.0
**Last Updated:** 2025-11-07

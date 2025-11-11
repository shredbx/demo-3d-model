# User Story: {story_id} - {title}

**Status:** READY
**Domain:** {domain}
**Type:** {type}
**Priority:** {priority}
**Created:** {date}
**Estimated Complexity:** [To be determined during planning]

### Multi-Product Fields
**Default Product:** bestays
**Portable:** true
**Ported To:** []

---

## Story

**As a** [role/persona - e.g., user, admin, agent, developer]
**I want** [goal/objective - what they want to accomplish]
**So that** [benefit/value - why this matters]

---

## Background

[Provide context and motivation for this story]

- Why is this needed?
- What's the current state?
- What problems does this solve?
- What's the business value?

---

## Current Implementation

[If this is a validation/refactor story, describe what currently exists]

### Architecture

```
[Describe the current architecture/flow]
```

### Key Files

| File | Purpose | Layer |
|------|---------|-------|
| `path/to/file.ts` | [Description] | [Layer] |

---

## Identified Issues

[If applicable, list known issues or areas for improvement]

### 1. **[Issue Name]**

**Location:** `file.ts:line`

**Problem:**
[Detailed description of the issue]

**Severity:** [High/Medium/Low]

**Hypothesis:**
[Your theory about the root cause]

---

## Acceptance Criteria

### Functional Requirements

- [ ] **AC-1:** [Specific, testable functional requirement]
- [ ] **AC-2:** [Another functional requirement]
- [ ] **AC-3:** [Another functional requirement]

### Technical Requirements

- [ ] **AC-4:** [Technical implementation requirement]
- [ ] **AC-5:** [Architecture/design requirement]
- [ ] **AC-6:** [Integration requirement]

### Quality Gates

- [ ] **AC-7:** [Testing requirement - unit, integration, e2e]
- [ ] **AC-8:** [Code quality requirement - lint, type check, etc.]
- [ ] **AC-9:** [Documentation requirement]
- [ ] **AC-10:** [Performance/security requirement]

---

## Technical Notes

### Technologies Used

- **Framework:** [e.g., SvelteKit, FastAPI]
- **Libraries:** [List key libraries]
- **Patterns:** [List architectural patterns used]

### Integration Points

- **Service A:** [How this integrates]
- **Service B:** [How this integrates]
- **External API:** [If applicable]

### Backend Endpoints (if applicable)

- **Endpoint:** `GET/POST /api/v1/resource`
- **Purpose:** [What it does]
- **Request:** [Request format]
- **Response:** [Response format]

---

## Porting Notes

**Portable Elements:**
- [List features/logic that can be ported to other products]
- [e.g., Authentication logic, validation rules, UI components]

**Product-Specific Elements:**
- [List features that need adaptation per product]
- [e.g., Redirect URLs, branding, role mappings, domain-specific business logic]

**Porting Considerations:**
- [Any known challenges when porting to other products]
- [Configuration differences to be aware of]

**Related Porting Tasks:**
- TASK-XXX-port-{feature}-{target-product} (if porting tasks exist)

---

## Testing Strategy

### Unit Tests

- [ ] Test [component/function name]
- [ ] Test [another component/function]
- [ ] Mock external dependencies

### Integration Tests

- [ ] Test [integration scenario]
- [ ] Test error handling
- [ ] Test edge cases

### E2E Tests (Playwright)

- [ ] Test [user flow end-to-end]
- [ ] Test [error scenarios]
- [ ] Visual regression testing

---

## Documentation Requirements

### 1. [Documentation Type - e.g., Integration Spec]

**Location:** `.claude/docs/[category]/[name].md`

**Contents:**
- [What should be documented]
- [Diagrams needed]
- [Examples needed]

### 2. [Another Documentation Type]

**Location:** `path/to/README.md`

**Contents:**
- [What should be documented]

---

## Dependencies

### External Dependencies

- [Library name]: [Version] - [Purpose]

### Internal Dependencies

- [Other service/module] - [How it's used]

### Blocked By

- [US-XXX]: [Why this blocks us]

### Blocks

- [US-XXX]: [What depends on this story]

---

## Tasks Breakdown

This user story will be broken down into tasks:

1. **TASK-XXX:** [Task description]
2. **TASK-XXX:** [Task description]
3. **TASK-XXX:** [Task description]

[Tasks will be created after story is approved and planning is complete]

---

## Definition of Done

- [ ] All acceptance criteria met and verified
- [ ] All tests passing (unit, integration, e2e)
- [ ] Code review completed
- [ ] Documentation complete and reviewed
- [ ] No critical bugs or security issues
- [ ] Performance benchmarks met (if applicable)
- [ ] Manual testing completed across browsers/devices
- [ ] Deployed to staging and validated

---

## Notes

[Additional notes, considerations, or future improvements]

### Future Improvements

- [Ideas for later iterations]
- [Known limitations to address in future stories]

### References

- [Link to related design docs]
- [Link to mockups/wireframes]
- [Link to external resources]

---

**Template Version:** 1.0
**Last Updated:** {date}

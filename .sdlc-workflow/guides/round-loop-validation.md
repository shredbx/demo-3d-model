# Round-Loop Validation Workflow

**Purpose:** Ensure all architectural decisions are validated by domain experts AND strategic CTO review before implementation.

**Philosophy:** "Collective intelligence prevents costly mistakes. Every agent sees the complete picture."

**Status:** ACTIVE - Mandatory for all major architectural decisions
**Created:** 2025-11-08
**Last Updated:** 2025-11-08

---

## Overview

This workflow ensures that:
1. ✅ All agents understand the complete system architecture (no silos)
2. ✅ Domain experts validate decisions from their perspective
3. ✅ Technical debt and trade-offs are identified early
4. ✅ Strategic CTO validation ensures alignment with business goals
5. ✅ All decisions documented for instant context retrieval

**When to Use:**
- New user stories with cross-cutting architecture changes
- Database schema changes affecting multiple services
- API contract changes affecting frontend/backend integration
- Infrastructure changes affecting deployment or monitoring
- Security or performance critical features

**When NOT to Use:**
- Bug fixes (single component)
- UI-only changes (no backend impact)
- Documentation updates
- Minor refactoring (no API changes)

---

## The Complete Flow

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: COORDINATOR CREATES INITIAL SPECS                  │
│                                                               │
│ Coordinator (Claude Code) creates:                           │
│ - User stories (US-XXX)                                      │
│ - Architecture diagrams (data flow, system context)          │
│ - Database schema design                                     │
│ - API contracts                                              │
│ - Agent responsibilities with integration points             │
│                                                               │
│ Output: US-020.md, US-021.md, etc.                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: AGENT CHAIN VALIDATION (Round 1)                   │
│                                                               │
│ Launch 4 agents IN PARALLEL for speed:                       │
│                                                               │
│ 1. devops-infra                                              │
│    - Infrastructure, deployment, migrations, monitoring      │
│    - Database migration safety, rollback strategy           │
│    - Service orchestration, environment variables           │
│                                                               │
│ 2. dev-backend-fastapi                                       │
│    - API design, database schema, cache strategy            │
│    - Security (auth, RBAC, CSRF, XSS)                       │
│    - Performance (query optimization, connection pooling)   │
│                                                               │
│ 3. dev-frontend-svelte                                       │
│    - SSR compatibility, hydration issues                     │
│    - UX patterns, accessibility, responsiveness             │
│    - Performance (bundle size, lazy loading)                │
│                                                               │
│ 4. playwright-e2e-tester                                     │
│    - Testability of acceptance criteria                      │
│    - Test scenario coverage (happy path, edge cases)        │
│    - Browser compatibility, flakiness risks                 │
│                                                               │
│ Each agent provides:                                         │
│ - ✅ APPROVE (optional suggestions)                          │
│ - 🟡 APPROVE WITH CONCERNS (must address before impl)       │
│ - ❌ REJECT (blockers that must be fixed)                    │
│                                                               │
│ Output: 4 review reports with feedback                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: COORDINATOR AGGREGATES FEEDBACK                     │
│                                                               │
│ Coordinator:                                                  │
│ 1. Collects all 4 agent reviews                              │
│ 2. Creates aggregated feedback document                      │
│ 3. Shares with all agents (transparency)                     │
│ 4. Identifies conflicts or consensus                         │
│                                                               │
│ Decision Logic:                                               │
│ - ALL ✅ APPROVE → Proceed to Phase 4 (CTO validation)       │
│ - ANY ❌ REJECT → Go to Phase 3B (revision loop)             │
│ - ANY 🟡 CONCERNS → Go to Phase 3B (revision loop)           │
│                                                               │
│ Output: Aggregated feedback report                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3B: REVISION LOOP (if needed)                          │
│                                                               │
│ Coordinator:                                                  │
│ 1. Addresses all ❌ REJECT blockers                          │
│ 2. Addresses all 🟡 CONCERNS                                 │
│ 3. Updates specs with changes                                │
│ 4. Documents why changes were made (or not made)             │
│                                                               │
│ Then: Go back to Phase 2 (re-run agent validation)           │
│                                                               │
│ Continue until: ALL agents ✅ APPROVE                         │
│                                                               │
│ Output: Revised specs + revision log                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: CTO STRATEGIC VALIDATION                            │
│                                                               │
│ Coordinator spawns: specialist-cto-startup agent             │
│                                                               │
│ CTO reviews:                                                  │
│ - Complete specs (US-020, US-021, etc.)                      │
│ - Agent approval chain (all 4 agent reviews)                 │
│ - Decision log (trade-offs, alternatives considered)         │
│                                                               │
│ CTO evaluates:                                                │
│ - Strategic alignment (does this support business goals?)    │
│ - Technical debt implications (will this bite us later?)     │
│ - Scalability (will this work at 10x scale?)                 │
│ - Maintainability (can team understand this in 6 months?)    │
│ - Security & compliance (any regulatory issues?)             │
│                                                               │
│ CTO Decision:                                                 │
│ - 🟢 GREEN LIGHT → Proceed to Phase 5 (implementation)       │
│ - 🔴 RED LIGHT + rejection comments → Back to Phase 3B       │
│                                                               │
│ Output: CTO approval decision + rationale                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 5: DOCUMENTATION & MEMORY SNAPSHOTS                    │
│                                                               │
│ Coordinator:                                                  │
│ 1. Creates memory snippets for key decisions                 │
│ 2. Documents trade-offs (pros, cons, when to revisit)        │
│ 3. Updates specs with "APPROVED BY" sections                 │
│ 4. Archives validation artifacts in task folders             │
│                                                               │
│ Memory snippets include:                                     │
│ - Decision: What was chosen                                  │
│ - Alternatives: What was NOT chosen and why                  │
│ - Trade-offs: Pros/cons of chosen approach                   │
│ - Triggers: When to revisit this decision                    │
│ - Context: Links to specs, reviews, CTO approval             │
│                                                               │
│ Output: Memory snippets, approval stamps, decision log       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 6: IMPLEMENTATION                                      │
│                                                               │
│ Proceed with implementation following milestone order        │
│                                                               │
│ Example:                                                      │
│ - Milestone 1: Fix US-019 tests (100% passing)               │
│ - Milestone 2: Implement US-020 (homepage editable content)  │
│ - Milestone 3: Implement US-021 (Thai localization)          │
│                                                               │
│ Each milestone has full agent approval + CTO green light     │
└─────────────────────────────────────────────────────────────┘
```

---

## Agent Review Template

Each agent uses this template when reviewing specs:

```markdown
# [Agent Name] Review: [Story ID]

**Reviewer:** [Agent Name]
**Date:** [YYYY-MM-DD]
**Story:** [US-XXX Story Title]

## Overall Decision

- [ ] ✅ APPROVE (ready to implement, optional suggestions below)
- [ ] 🟡 APPROVE WITH CONCERNS (must address concerns before implementation)
- [ ] ❌ REJECT (blockers that must be fixed, cannot proceed)

## Domain-Specific Review

### 1. [Domain Area 1]
**Reviewed:** [What I checked]
**Findings:** [What I found]
**Recommendation:** [What to do]

### 2. [Domain Area 2]
**Reviewed:** [What I checked]
**Findings:** [What I found]
**Recommendation:** [What to do]

## Blockers (❌ REJECT only)

1. **[Blocker Title]**
   - Issue: [What's wrong]
   - Impact: [Why this blocks implementation]
   - Fix: [How to resolve]

## Concerns (🟡 APPROVE WITH CONCERNS)

1. **[Concern Title]**
   - Issue: [What might be problematic]
   - Risk: [What could go wrong]
   - Mitigation: [How to reduce risk]

## Suggestions (✅ APPROVE)

1. **[Suggestion Title]**
   - Current: [What spec says now]
   - Improvement: [How to make it better]
   - Benefit: [Why this helps]

## Questions for Coordinator

1. [Question 1]
2. [Question 2]

## Sign-Off

**Agent:** [Agent Name]
**Decision:** [✅ APPROVE | 🟡 APPROVE WITH CONCERNS | ❌ REJECT]
**Confidence:** [High | Medium | Low]
**Date:** [YYYY-MM-DD]
```

---

## CTO Review Template

```markdown
# CTO Strategic Review: [Story ID]

**Reviewer:** specialist-cto-startup
**Date:** [YYYY-MM-DD]
**Stories:** [US-020, US-021, etc.]

## Strategic Alignment

**Business Goals:** [How this supports company objectives]
**User Value:** [What users gain]
**Competitive Advantage:** [How this differentiates us]

## Technical Assessment

### 1. Scalability
- Current plan supports: [X users, Y requests/sec]
- Breaks at: [Z scale]
- Migration path: [How to scale when needed]

### 2. Maintainability
- Code complexity: [High | Medium | Low]
- Team can understand: [Yes | With training | No]
- Documentation quality: [Excellent | Good | Needs work]

### 3. Technical Debt
- Debt introduced: [What shortcuts we're taking]
- Acceptable because: [Why it's OK for now]
- Payback plan: [When/how to address later]

### 4. Security & Compliance
- Security risks: [Identified risks]
- Mitigation: [How we're addressing them]
- Compliance: [Any regulatory concerns]

### 5. Dependencies & Risks
- External dependencies: [Third-party services, libraries]
- Risk: [What could fail]
- Mitigation: [Fallback plans]

## Agent Consensus Review

**DevOps:** [✅ APPROVE | 🟡 CONCERNS | ❌ REJECT] - [Summary]
**Backend:** [✅ APPROVE | 🟡 CONCERNS | ❌ REJECT] - [Summary]
**Frontend:** [✅ APPROVE | 🟡 CONCERNS | ❌ REJECT] - [Summary]
**E2E:** [✅ APPROVE | 🟡 CONCERNS | ❌ REJECT] - [Summary]

**Consensus:** [All approved | Concerns addressed | Rejected items outstanding]

## Final Decision

- [ ] 🟢 GREEN LIGHT - Proceed to implementation
- [ ] 🔴 RED LIGHT - Send back to revision loop

**Rationale:** [Why this decision]

**If RED LIGHT, must address:**
1. [Blocker 1]
2. [Blocker 2]

**If GREEN LIGHT, proceed with:**
- Milestone order: [M1 → M2 → M3]
- Timeline: [X weeks]
- Success criteria: [How we know it worked]

## Sign-Off

**CTO:** specialist-cto-startup
**Decision:** [🟢 GREEN LIGHT | 🔴 RED LIGHT]
**Date:** [YYYY-MM-DD]
```

---

## Artifacts & Documentation

### File Structure

```
.sdlc-workflow/
├── stories/
│   └── homepage/
│       ├── US-020-homepage-editable-content.md (specs)
│       └── US-021-locale-switching.md (specs)
│
├── reviews/
│   ├── US-020-validation-round-1/
│   │   ├── devops-review.md
│   │   ├── backend-review.md
│   │   ├── frontend-review.md
│   │   ├── e2e-review.md
│   │   ├── aggregated-feedback.md (coordinator summary)
│   │   └── cto-review.md (final approval)
│   │
│   └── US-021-validation-round-1/
│       ├── devops-review.md
│       ├── backend-review.md
│       ├── frontend-review.md
│       ├── e2e-review.md
│       ├── aggregated-feedback.md
│       └── cto-review.md
│
├── decisions/
│   └── 2025-11-08-us-020-021-decision-log.md
│
└── guides/
    └── round-loop-validation.md (this document)
```

### Memory Snippets (mcp__memory)

After CTO approval, create memory entities:

```typescript
// Example memory snippet
{
  entityType: "Technical Decision",
  name: "US-020 Cache Strategy",
  observations: [
    "Decision: Cache-aside pattern with Redis 1hr TTL",
    "Alternative: Cache stampede prevention with locks (deferred)",
    "Trade-off: Simple implementation vs potential stampede at scale",
    "Trigger: Revisit when concurrent requests > 1000/sec",
    "Approved by: DevOps, Backend, Frontend, E2E, CTO",
    "Context: .sdlc-workflow/reviews/US-020-validation-round-1/",
    "Risk: Acceptable for Phase 1 traffic (< 100 req/sec)"
  ]
}
```

---

## Example Validation Round

### US-020: Homepage Editable Content

**Round 1: Agent Validation**

| Agent | Decision | Key Feedback |
|-------|----------|--------------|
| DevOps | ✅ APPROVE | Alembic migration looks good, add seed data validation |
| Backend | 🟡 CONCERNS | Cache invalidation needs error handling for Redis failures |
| Frontend | ✅ APPROVE | SSR pattern solid, suggest adding loading states for optimistic UI |
| E2E | ❌ REJECT | Missing test scenario for admin role validation |

**Coordinator Action:** Address Backend concern + E2E blocker

**Round 2: Re-validation**

| Agent | Decision | Key Feedback |
|-------|----------|--------------|
| DevOps | ✅ APPROVE | No changes needed from me |
| Backend | ✅ APPROVE | Error handling added, looks good |
| Frontend | ✅ APPROVE | No changes needed from me |
| E2E | ✅ APPROVE | Test scenario added, ready to implement |

**CTO Validation:**

- Strategic alignment: ✅ Agile delivery matches business goals
- Technical debt: ✅ Acceptable (documented deferred optimizations)
- Scalability: ✅ Migration path defined (see DEFERRED-OPTIMIZATIONS.md)
- Security: ✅ RBAC enforcement validated by Backend agent

**Decision:** 🟢 GREEN LIGHT - Proceed to Milestone 2 (after M1 complete)

---

## Benefits of This Workflow

### For Coordinator
- ✅ Catches mistakes before implementation
- ✅ Learns from domain expert feedback
- ✅ Builds comprehensive documentation
- ✅ Reduces rework and technical debt

### For Agents
- ✅ Clear understanding of complete system
- ✅ No silos (all agents see each other's feedback)
- ✅ Integration points validated before coding
- ✅ Confidence that implementation will succeed

### For CTO
- ✅ Strategic oversight of technical decisions
- ✅ Early identification of business risks
- ✅ Documentation of trade-offs for future
- ✅ Final gate before resource investment

### For User
- ✅ Transparent decision-making process
- ✅ High confidence in implementation plans
- ✅ Reduced bugs and rework
- ✅ Clear audit trail for all decisions

---

## Enforcement

### Mandatory For:
- New user stories with multi-agent implementation
- Database schema changes
- API contract changes
- Security or performance critical features
- Infrastructure changes

### Optional For:
- Bug fixes (single component)
- UI-only changes (no backend impact)
- Documentation updates
- Minor refactoring

### Bypass Criteria:
- User explicitly requests to skip validation (document in deviation log)
- Emergency hotfix (document and retrospective review after)
- Prototype/spike (not production code)

---

## Timeline Expectations

**Typical validation round:**
- Agent reviews (parallel): 30-60 minutes (4 agents running simultaneously)
- Coordinator aggregation: 15 minutes
- Revision (if needed): 30-60 minutes
- CTO review: 20-30 minutes
- Documentation: 20 minutes

**Total time:** 2-3 hours for complete validation (including one revision round)

**Trade-off:** 2-3 hours upfront prevents 1-2 days of rework

---

## Revision History

| Date | Change | Reason |
|------|--------|--------|
| 2025-11-08 | Initial creation | User requested round-loop validation workflow |

---

**Document Status:** ACTIVE
**Owner:** Coordinator
**Review Frequency:** After each major validation round
**Last Updated:** 2025-11-08

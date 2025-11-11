# Multi-Product User Story Workflow Decision

**Date:** 2025-11-07
**Decision Type:** SDLC Workflow Architecture
**Status:** Approved
**Affects:** All future user stories and tasks

---

## Context

Bestays project maintains two products simultaneously:
1. **bestays.app** - Primary vacation rental platform
2. **Real Estate product** - Property sales/rental platform

**Challenge:** How to track user stories and tasks across both products while maintaining:
- Single source of truth
- Clear traceability
- Efficient "build once, port later" workflow
- No documentation duplication

---

## Decision

**Adopted: Option 4 - Hybrid (Default Product + Porting Tasks)**

User stories have a **default product** (usually `bestays`) and are **ported via dedicated tasks** to other products.

---

## Implementation

### 1. Story Metadata Fields (Added to Template)

```yaml
---
default_product: bestays | realestate
portable: true | false
ported_to: []  # Updated after porting: [realestate]
---
```

**Fields:**
- `default_product`: Which product this story is primarily built for
- `portable`: Whether this feature can be ported to other products
- `ported_to`: Array of products this story has been ported to (updated after porting)

---

### 2. Story Structure Example

```markdown
.sdlc-workflow/stories/auth/US-001-login-flow.md
---
default_product: bestays
portable: true
ported_to: []
---

# User Story: Login Flow

## Acceptance Criteria (Bestays)
AC-1: Users can log in with email/password
AC-2: Redirect to /home after successful login
...

## Porting Notes
**Portable Elements:**
- Authentication logic (Clerk SDK integration)
- Login form validation
- Error handling patterns

**Product-Specific Elements:**
- Redirect URLs (bestays: /home, realestate: /dashboard)
- Branding and styling
- Role mappings (bestays: user/admin/agent, realestate: buyer/seller/agent)

**Porting Task:** TASK-050-port-login-realestate

## Implementation Tasks
- TASK-001-login-bestays (✅ bestays implementation)
- TASK-050-port-login-realestate (⏳ realestate porting)
```

---

### 3. Porting Task Structure

Porting tasks follow standard task folder structure with additional sections:

```
.claude/tasks/TASK-050-port-login-realestate/
├── STATE.json
│   {
│     "story": "US-001",
│     "semantic_name": "port-login-realestate",
│     "type": "PORTING",  # New field
│     "source_product": "bestays",
│     "target_product": "realestate",
│     "source_task": "TASK-001-login-bestays"
│   }
├── README.md
├── planning/
│   ├── porting-checklist.md  # What needs adaptation
│   └── product-specific-requirements.md
└── subagent-reports/
```

**Porting Checklist Template:**
```markdown
# Porting Checklist: US-001 Login Flow (Bestays → Real Estate)

## Files to Port
- [ ] apps/frontend/src/routes/login/+page.svelte
- [ ] apps/server/api/auth.py
- [ ] apps/frontend/tests/e2e/login.spec.ts

## Product-Specific Adaptations
- [ ] Update redirect URL: /home → /dashboard
- [ ] Update branding colors and logo
- [ ] Map roles: bestays roles → realestate roles
- [ ] Update test credentials (use realestate Clerk instance)

## Configuration Changes
- [ ] Environment variables (.env.realestate)
- [ ] Clerk webhook URLs
- [ ] Database connection (if separate)

## Testing
- [ ] Unit tests pass for realestate product
- [ ] E2E tests pass for realestate product
- [ ] Manual QA on realestate domain
```

---

### 4. Git Commit Format (Multi-Product)

**Initial Implementation:**
```
feat: implement login flow (US-001 TASK-001-login-bestays)

Subagent: dev-frontend-svelte
Product: bestays
Files: apps/frontend/src/routes/login/+page.svelte

Implemented Clerk authentication with email/password login.
Redirects to /home after successful authentication.

Story: US-001
Task: TASK-001-login-bestays
```

**Porting Implementation:**
```
feat: port login flow to real estate (US-001 TASK-050-port-login-realestate)

Subagent: dev-frontend-svelte
Product: realestate
Source: TASK-001-login-bestays
Files: apps/frontend/src/routes/login/+page.svelte

Ported login flow from bestays with adaptations:
- Changed redirect: /home → /dashboard
- Updated branding for realestate product
- Mapped roles: bestays → realestate

Story: US-001
Task: TASK-050-port-login-realestate
```

---

### 5. Workflow

**Step 1: Create Story (Default Product)**
```bash
python .claude/skills/docs-stories/scripts/story_create.py auth login flow
# Creates US-XXX with default_product: bestays, portable: true
```

**Step 2: Implement for Default Product**
```bash
python .claude/skills/docs-stories/scripts/task_create.py US-XXX 1 login-bestays
# Implement via dev-frontend-svelte subagent
# Commit with TASK-001-login-bestays reference
```

**Step 3: Mark Story for Porting (Update Metadata)**
```bash
# Manually update story file:
# ported_to: []  →  ported_to: []  (still empty until ported)
```

**Step 4: Create Porting Task**
```bash
python .claude/skills/docs-stories/scripts/task_create.py US-XXX 50 port-login-realestate
# Manually update TASK-050 STATE.json with type: PORTING, target_product: realestate
```

**Step 5: Execute Porting**
```bash
# Subagent reads TASK-050 planning/porting-checklist.md
# Adapts files for realestate product
# Commits with TASK-050-port-login-realestate reference
```

**Step 6: Update Story Metadata**
```bash
# After successful porting, update story:
# ported_to: [realestate]
```

---

## Alternatives Considered

### Option 1: Story Metadata (Frontmatter)
**Rejected:** Product-specific acceptance criteria hard to separate.

### Option 2: Product-Scoped Directories
**Rejected:** Documentation duplication, sync drift risk.

### Option 3: Product Suffix in Story ID
**Rejected:** Still duplicates documentation, manual sync needed.

---

## Trade-offs

**Pros:**
✅ Single story file (no duplication)
✅ Aligns with "build bestays first, port later" workflow
✅ Porting is explicit, trackable task
✅ Product-specific notes in porting task folder
✅ Works with existing task folder system
✅ Clear git history (one story, multiple tasks)

**Cons:**
⚠️ Must create porting tasks (minor overhead)
⚠️ Manual metadata updates (ported_to field)
⚠️ Story file mixes product contexts if heavily customized

---

## When to Revisit

**Conditions that would invalidate this decision:**
1. **Heavy product divergence** - If bestays and realestate become radically different, separate story files may be clearer
2. **Porting becomes majority of work** - If >50% of stories require significant porting effort, reconsider workflow
3. **Team scaling** - If team grows beyond single developer + LLM, may need product-specific story ownership

---

## DevOps Implications

**Deployment Tracking:**
- Each task deploys to specific product
- Git commits reference task (which references product)
- CI/CD pipelines filter by product tag (TASK-XXX-*-bestays vs TASK-XXX-*-realestate)

**Infrastructure:**
- Separate containers per product (already planned)
- Shared database with product isolation (already planned)
- Product-specific environment variables (.env.bestays, .env.realestate)

**Monitoring:**
- Tag metrics by product
- Separate error tracking per product
- Deployment logs reference task ID (includes product context)

---

## Documentation Updates Required

**Immediate (Today):**
- [x] Document decision in `.claude/reports/20251107-multi-product-story-workflow.md`
- [ ] Update story template (`.sdlc-workflow/stories/TEMPLATE.md`) with metadata fields
- [ ] Create porting task template (`.claude/tasks/TEMPLATE-PORTING/`)
- [ ] Update docs-stories scripts to handle metadata
- [ ] Update CLAUDE.md with multi-product workflow

**Soon (This Week):**
- [ ] Get DevOps perspective on deployment tracking
- [ ] Update GIT_WORKFLOW.md with multi-product examples
- [ ] Create first porting task as example

---

## Success Criteria

**This decision is successful if:**
1. ✅ All stories clearly indicate default product
2. ✅ Porting tasks are easy to create and track
3. ✅ No documentation duplication
4. ✅ Git history clearly shows product context
5. ✅ DevOps can deploy per product without ambiguity
6. ✅ Context restoration includes product information

---

**Approved By:** User (Product Owner)
**Implemented By:** Coordinator (Claude Code)
**Next Review:** After first 3 porting tasks completed

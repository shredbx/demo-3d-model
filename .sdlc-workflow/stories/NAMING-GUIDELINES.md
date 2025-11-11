# User Story Naming Guidelines

**Version:** 1.0
**Date:** 2025-11-07

This document provides clear guidelines for naming user stories to avoid ID conflicts and maintain consistency.

---

## Story ID Format

```
US-{ID}[{SUFFIX}]-{domain}-{short-description}.md
```

**Components:**
- `US-` - Fixed prefix
- `{ID}` - 3-digit base ID (001, 002, ..., 999)
- `[{SUFFIX}]` - Optional single letter (A, B, C, ...)
- `{domain}` - Story domain (auth, property, booking, etc.)
- `{short-description}` - Slugified title

**Examples:**
- `US-001-auth-login-flow-validation.md`
- `US-001B-auth-rbac-and-audit-logging.md`
- `US-042-property-homepage.md`

---

## When to Use Letter Suffixes

### ✅ USE Suffix (US-001B) When:

1. **Directly related to original story**
   - Discovered during implementation of base story
   - Extends or enhances base story functionality
   - Shares same epic/domain

2. **Small scope addition**
   - Not large enough to warrant separate ID
   - Builds on base story's context
   - Uses same dependencies/infrastructure

3. **Follow-up work**
   - Refinement of base story
   - Additional testing/validation
   - Performance optimization

**Examples:**
```
US-001: Login flow validation (original)
US-001B: Add RBAC + audit logging (discovered during US-001)
US-001C: Add MFA support (follow-up enhancement)
```

### ❌ USE New ID (US-042) When:

1. **Independent story**
   - Can stand alone without base story
   - Different epic or domain
   - No direct dependency on base story

2. **Major feature**
   - Significant scope (multiple epics)
   - Different user persona/workflow
   - Would be confusing as suffix

3. **Planned from start**
   - Part of original milestone plan
   - Not discovered during implementation
   - Has its own set of requirements

**Examples:**
```
US-042: Property homepage (independent feature)
US-103: Admin user management (different domain)
US-016: Property schema migration (major feature)
```

---

## Current ID Status

### Existing Stories

| ID | Title | Domain | Status |
|----|-------|--------|--------|
| US-001 | Login flow validation | auth | ✅ COMPLETED |
| US-001B | RBAC & audit logging | auth | 🔄 IN PROGRESS |
| US-016 | Property migration design | properties | 📋 CREATED |
| US-017 | Branch naming validation | infrastructure | ✅ COMPLETED |

### Reserved IDs

**US-002 to US-015:** Reserved for MILESTONE_01 stories
- Homepage, listings, property details, CRUD operations
- Allows milestone plan to map cleanly to story IDs

### Next Available

- **Auto-generated:** US-018 (next sequential)
- **Gap filling:** US-002 to US-015 (milestone stories)
- **Suffix:** US-001C, US-001D, etc. (if related to login)

---

## Creating Stories

### Using the Script (Recommended)

**Auto-generate next ID:**
```bash
python .sdlc-workflow/scripts/story_create.py \
  --domain property \
  --title "Homepage" \
  --type feature \
  --priority high
# Creates: US-018-property-homepage.md
```

**Fill a gap (milestone story):**
```bash
python .sdlc-workflow/scripts/story_create.py \
  --domain property \
  --title "Homepage" \
  --type feature \
  --priority high \
  --story-id US-002
# Creates: US-002-property-homepage.md
```

**Create related story with suffix:**
```bash
python .sdlc-workflow/scripts/story_create.py \
  --domain auth \
  --title "MFA support" \
  --type feature \
  --priority high \
  --story-id US-001 \
  --suffix C
# Creates: US-001C-auth-mfa-support.md
```

### Validation Built-in

The script automatically:
- ✅ Checks for duplicate IDs
- ✅ Validates ID format
- ✅ Detects existing suffixes (US-001, US-001B)
- ✅ Suggests alternatives if ID exists
- ✅ Shows all existing IDs

**Example validation error:**
```
❌ Error creating story: Story ID US-001 already exists: ['US-001', 'US-001B']

Existing story IDs:
  - 001: US-001, US-001B
  - 016: US-016
  - 017: US-017

Suggestions:
  - Use next sequential ID: US-018
  - Add suffix to related story: US-001C
  - Fill a gap: US-002 to US-015 are available
```

---

## Decision Tree

```
┌─ Need new story?
│
├─ Is it related to existing story? ────────────┐
│  (Same epic, discovered during work,          │
│   builds on same context)                     │
│                                               │
│  YES ─────────────────────────────────────────┤
│                                               │
│  Check existing suffixes:                     │
│  US-001, US-001B exist                       │
│  → Create US-001C                            │
│                                               │
│  NO ──────────────────────────────────────────┤
│                                               │
│  Is it part of MILESTONE_01? ─────────────────┤
│  (Homepage, listings, CRUD, etc.)             │
│                                               │
│  YES ─────────────────────────────────────────┤
│  → Fill gap: US-002 to US-015                │
│                                               │
│  NO ──────────────────────────────────────────┤
│  → Use next ID: US-018                       │
│                                               │
└───────────────────────────────────────────────┘
```

---

## Why This Matters

**Without clear guidelines:**
- ❌ Duplicate IDs (US-017 for different stories)
- ❌ Gaps with no explanation (where is US-002?)
- ❌ Inconsistent suffixes (why US-001B but not US-016A?)
- ❌ Confusion about which stories relate

**With clear guidelines:**
- ✅ Unique IDs enforced by validation
- ✅ Clear rationale for gaps (milestone reserved)
- ✅ Suffixes used consistently (related stories only)
- ✅ Easy to understand story relationships

---

## Rationale for Current IDs

### US-001, US-001B (Auth)
- **US-001:** Original login validation story
- **US-001B:** RBAC + audit discovered during US-001 work
- **Why suffix?** Directly related, same epic, discovered during implementation

### US-016 (Properties)
- **Why jump to 016?** Property schema is critical infrastructure
- **Why not US-002?** Reserving US-002 to US-015 for milestone guest/agent stories
- **Why not suffix?** Independent feature, different domain from auth

### US-017 (Infrastructure)
- **Why 017?** Next sequential after US-016
- **Not in milestone?** Correct - this is SDLC infrastructure work
- **Conflict with milestone US-017?** Will use suffix or skip when creating milestone story

---

## Best Practices

1. **Use the script** - Automatic validation prevents mistakes
2. **Consult this guide** - When in doubt about suffix vs new ID
3. **Document rationale** - If breaking pattern, explain why
4. **Keep IDs sequential** - Don't skip unless reserving for milestone
5. **Group related work** - Use suffixes to show relationships

---

## References

- **Story Creation Script:** `.sdlc-workflow/scripts/story_create.py`
- **Story README:** `.sdlc-workflow/stories/README.md`
- **Milestone Plan:** `.sdlc-workflow/.specs/MILESTONE_01_WEBSITE_REPLICATION.md`

---

**Last Updated:** 2025-11-07

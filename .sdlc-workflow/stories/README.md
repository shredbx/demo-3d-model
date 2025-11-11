# User Stories

This directory contains all user stories for the Bestays project, organized by domain.

## Structure

```
stories/
├── README.md              (this file)
├── TEMPLATE.md           (template for new stories)
├── auth/                 (authentication domain)
│   └── US-001-login-flow-validation.md
├── booking/              (booking domain)
├── property/             (property management domain)
├── payment/              (payment domain)
└── admin/                (admin features domain)
```

## User Story Format

Each user story follows a standardized format defined in `TEMPLATE.md`:

### Required Sections

1. **Header Metadata**
   - Status (READY, IN_PROGRESS, BLOCKED, COMPLETED)
   - Domain (auth, booking, property, etc.)
   - Type (feature, validation, bugfix, refactor)
   - Priority (high, medium, low)
   - Dates (created, estimated complexity)

2. **Story Statement**
   - As a [role]
   - I want [goal]
   - So that [benefit]

3. **Background**
   - Context and motivation
   - Current state (for validation stories)

4. **Acceptance Criteria**
   - Functional requirements (AC-1, AC-2, ...)
   - Technical requirements (AC-X, ...)
   - Quality gates (AC-Y, ...)

5. **Technical Notes**
   - Architecture details
   - Integration points
   - Dependencies

6. **Testing Strategy**
   - Unit tests
   - Integration tests
   - E2E tests

7. **Documentation Requirements**
   - What docs need to be created/updated

8. **Tasks Breakdown**
   - List of tasks (TASK-XXX) for this story

9. **Definition of Done**
   - Checklist of completion criteria

## Naming Convention

User stories follow this naming pattern:

```
US-{ID}[{SUFFIX}]-{domain}-{short-description}.md
```

**Examples:**
- `US-001-auth-login-flow-validation.md`
- `US-001B-auth-rbac-and-audit-logging.md` (related to US-001)
- `US-042-booking-reservation-flow.md`
- `US-103-admin-user-management.md`

### ID Format Rules

**Base ID:**
- 3-digit zero-padded number (001, 002, ..., 999)
- Sequential within the entire project (not per domain)
- Generated automatically by `story_create.py` script
- **Each base ID must be unique** (enforced by validation)

**Suffix (Optional):**
- Single uppercase letter: A, B, C, D, etc.
- Used for related/follow-up stories to same base ID
- Example: US-001, US-001B, US-001C

### When to Use Suffixes vs New IDs

**Use Letter Suffix (US-001B) when:**
- ✅ Story is directly related to original (US-001)
- ✅ Same epic/domain as original
- ✅ Discovered during implementation of original
- ✅ Shares context/dependencies with original
- ✅ Small enough that separate ID feels like overkill

**Examples:**
- US-001: Login flow validation
- US-001B: Add RBAC + audit logging (discovered during US-001 work)
- US-001C: Add MFA support (follow-up to US-001)

**Use New ID (US-042) when:**
- ✅ Independent story (can stand alone)
- ✅ Different epic/domain
- ✅ Major feature (not a small follow-up)
- ✅ Planned from start (not discovered during work)
- ✅ Would be confusing to attach to existing ID

**Examples:**
- US-042: Booking reservation flow (completely independent)
- US-103: Admin user management (different domain)

### Current ID Status

**Existing Stories:**
- `US-001` - Login flow validation (auth)
- `US-001B` - RBAC & audit logging (auth, follow-up to US-001)
- `US-016` - Property migration design (properties)
- `US-017` - Branch naming validation (infrastructure)

**Why gaps (US-002 to US-015)?**
- Reserved for MILESTONE_01 stories (guest/agent features)
- Will be filled as we create homepage, listings, property CRUD stories
- Allows milestone plan to map cleanly to story IDs

**Next ID:**
- Script will generate: `US-018` (next sequential)
- Or manually create: `US-002` (fill milestone gap)
- Or use suffix: `US-001C` (if related to login)

## Creating New Stories

### Option 1: Using Automation (Recommended)

```bash
# Using the slash command (in Claude Code session)
/story-new

# Or directly with the script
python .sdlc-workflow/scripts/story_create.py \
  --domain auth \
  --title "Password reset flow" \
  --type feature \
  --priority high
```

This will:
1. Generate the next US-XXX ID
2. Create the file from template
3. Fill in metadata (domain, title, type, priority, date)
4. Open for you to add content (story, acceptance criteria, etc.)

### Option 2: Manual Creation

1. Copy `TEMPLATE.md`
2. Find the next available US-XXX ID (check existing stories)
3. Rename to `US-XXX-domain-title.md`
4. Fill in all placeholders
5. Save in appropriate domain directory

## Story Types

- **feature**: New functionality
- **validation**: Validate/document/test existing code
- **bugfix**: Fix identified issues
- **refactor**: Code quality improvements
- **spike**: Research or investigation

## Story Statuses

- **READY**: Story is defined and ready to be worked on
- **IN_PROGRESS**: Currently being implemented (has active tasks)
- **BLOCKED**: Cannot proceed (waiting on dependencies)
- **COMPLETED**: All acceptance criteria met, all tasks done
- **ARCHIVED**: Completed and moved to archive

## Story Lifecycle

```
1. Story Created (READY)
   ↓
2. Tasks Created (TASK-XXX for each implementation unit)
   ↓
3. Work Begins (IN_PROGRESS)
   ↓
4. All Tasks Completed
   ↓
5. Story Validation (all AC verified)
   ↓
6. Story Completed (COMPLETED)
   ↓
7. Story Archived (moved to archive/)
```

## Acceptance Criteria Guidelines

**Good AC (Specific, Testable, Clear):**
- ✅ AC-1: Login form loads within 2 seconds on all browsers
- ✅ AC-2: User can reset password via email link
- ✅ AC-3: Invalid credentials show error message "Invalid email or password"

**Bad AC (Vague, Untestable):**
- ❌ Login should be fast
- ❌ User can reset password
- ❌ Errors are handled

**AC Naming:**
- **AC-1, AC-2, ...**: Functional requirements
- **AC-X**: Technical requirements (architecture, patterns, etc.)
- **AC-Y**: Quality gates (tests, linting, performance, etc.)

## Dependencies

Stories can reference dependencies:

```markdown
### Dependencies

**Blocked By:**
- US-042: User authentication must be implemented first

**Blocks:**
- US-103: Admin user management depends on this story
```

## Integration with Tasks

Each story is broken down into tasks:

```markdown
### Tasks Breakdown

1. **TASK-001:** Investigate and fix Clerk mounting issue
2. **TASK-002:** Add E2E tests for login flow
3. **TASK-003:** Create documentation
```

Tasks are tracked separately in `.claude/tasks/` with their own STATE.json.

## Documentation Links

Related documentation:
- SDLC Workflow: `.sdlc-workflow/.plan/03-workflow-diagrams.md`
- Task Management: `.claude/tasks/README.md` (to be created)
- Git Workflow: `.sdlc-workflow/.plan/02-hooks-specification.md`

## Tips

1. **Start Small**: First story should be simple (validation or small feature)
2. **Be Specific**: Acceptance criteria should be testable
3. **Document Existing Code First**: Before adding new features, validate what exists
4. **Link Everything**: Reference related stories, tasks, and documentation
5. **Update Status**: Keep status current as work progresses

---

**Last Updated:** 2025-11-05
**Version:** 1.0

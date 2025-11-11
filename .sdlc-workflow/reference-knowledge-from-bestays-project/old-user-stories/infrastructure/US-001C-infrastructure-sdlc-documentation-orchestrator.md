# User Story: US-001C - SDLC Documentation Orchestrator

**Status:** READY
**Domain:** infrastructure
**Type:** feature
**Priority:** high
**Created:** 2025-11-07
**Updated:** 2025-11-07 (Added AC-16, strengthened AC-3/AC-6/AC-13 per devops validation)
**Estimated Complexity:** Medium (4 days)

---

## Story

**As a** LLM (Claude Code) or subagent working on Bestays SDLC
**I want** a single, authoritative skill that orchestrates all SDLC documentation workflows
**So that** I can efficiently create/update/find documentation without searching multiple scattered locations

---

## Background

### Why is this needed?

During the SDLC traceability audit (part of US-001B planning), we discovered that while our Story → Task → Commit → Files traceability is excellent (100%), the **documentation about how to use the SDLC system** is scattered across multiple locations:

- `.sdlc-workflow/` (stories, tasks, scripts, templates, GIT_WORKFLOW.md)
- `.claude/` (skills, hooks, reports, CLAUDE.md)
- Multiple README files in various subdirectories
- Validation scripts with embedded documentation
- No centralized guidance for LLMs/subagents

### Current Problems

1. **Information Scatter:** LLMs must search 5+ locations to understand a single workflow (e.g., "how to create a story")
2. **No Single Source of Truth:** Contradictions exist between documents (GIT_WORKFLOW.md was documenting wrong branch pattern)
3. **Duplication:** `story_create.py` exists in TWO locations (`.sdlc-workflow/scripts/` and `.claude/skills/docs-stories/scripts/`)
4. **Maintenance Burden:** Updating a pattern requires changes in multiple files
5. **Subagent Confusion:** Subagents lack clear guidance on documentation requirements
6. **Lost Context:** Design decisions (trade-offs) not documented, leading to "helpful" LLMs breaking intentional choices
7. **Incomplete Skill:** `.claude/skills/docs-stories/` has scripts but no `skill.md` (LLMs can't use it)

### What's the business value?

- **Faster Development:** LLMs spend less time searching for documentation
- **Consistency:** All LLMs/subagents follow same patterns
- **Maintainability:** Single place to update when patterns change
- **Knowledge Preservation:** Trade-offs documented so future LLMs understand "why"
- **Reduced Errors:** Clear guidance prevents mistakes
- **Onboarding:** New LLM sessions can quickly understand SDLC workflow

### Project Mottos (From User)

1. **SINGLE AND CLEAR SOURCE OF TRUTH** - Consolidate scattered documentation
2. **DOCUMENTED TRADE-OFFS** - Explain why we chose X over Y, so LLMs can judge if trade-off is still valid

---

## Current Implementation

### What Exists Today

**`.claude/skills/docs-stories/`**
- Directory exists with Python scripts (task_create.py, story_create.py, etc.)
- NO skill.md file (LLMs can't use it as a skill)
- Empty references/ directory (no documentation)
- Scripts provide MECHANISMS but no GUIDANCE

**`.sdlc-workflow/`**
- stories/ (user stories organized by domain)
- tasks/ (task folders with implementation artifacts)
- scripts/ (story_create.py, validate_branch.py, validate_sdlc.py)
- GIT_WORKFLOW.md, various READMEs
- Authoritative source for workflow artifacts

**`.claude/`**
- skills/ (dev-philosophy, dev-code-quality, planning-quality-gates)
- hooks/ (sdlc_guardian.py, pre_tool_use.py)
- reports/ (audit reports)
- CLAUDE.md (main project instructions)

### Current Architecture

```
Documentation Flow (SCATTERED):

LLM needs to create story
  ├─ Check CLAUDE.md (high-level workflow)
  ├─ Check .sdlc-workflow/stories/README.md (story format)
  ├─ Check .sdlc-workflow/stories/NAMING-GUIDELINES.md (naming rules)
  ├─ Check .sdlc-workflow/scripts/story_create.py (how to use script)
  └─ Check story template (actual format)

LLM needs to create task
  ├─ Check CLAUDE.md (task folder system)
  ├─ Check .sdlc-workflow/tasks/README.md (structure)
  ├─ Check .sdlc-workflow/tasks/TEMPLATE/ (example)
  └─ Check .claude/skills/docs-stories/scripts/ (maybe scripts exist?)

LLM needs commit format
  ├─ Check CLAUDE.md (brief mention)
  ├─ Check .sdlc-workflow/GIT_WORKFLOW.md (detailed format)
  └─ Check validate_sdlc.py (actual enforcement rules)

PROBLEM: No navigation hub, must know where to look
```

### Key Files

| File | Purpose | Status |
|------|---------|--------|
| `.claude/skills/docs-stories/` | Operational scripts | Incomplete (no skill.md) |
| `.sdlc-workflow/stories/README.md` | Story system docs | Complete |
| `.sdlc-workflow/stories/NAMING-GUIDELINES.md` | Naming conventions | Complete |
| `.sdlc-workflow/GIT_WORKFLOW.md` | Git workflow | Complete (just updated in US-017) |
| `CLAUDE.md` | Main instructions | Complete but scattered references |
| `.sdlc-workflow/scripts/README.md` | Script documentation | Complete (created in US-017) |

---

## Identified Issues

### 1. **No LLM Entry Point for SDLC Documentation**

**Location:** `.claude/skills/docs-stories/` (missing skill.md)

**Problem:**
LLMs cannot use docs-stories as a skill because skill.md doesn't exist. Even though operational scripts exist, there's no guidance on WHEN to use them, HOW to use them, or WHAT patterns to follow.

**Severity:** High

**Impact:**
- LLMs search randomly for documentation
- Inconsistent usage of scripts
- Subagents don't know documentation requirements

### 2. **Scattered Documentation (No Single Source of Truth)**

**Location:** Multiple (CLAUDE.md, .sdlc-workflow/, various READMEs)

**Problem:**
Same information exists in multiple places, sometimes with contradictions. Example: GIT_WORKFLOW.md was documenting story-based branching when we actually use task-based branching.

**Severity:** High

**Impact:**
- Contradictions cause confusion
- Updates must happen in multiple files
- Easy to miss updating one location

### 3. **No Trade-offs Documentation**

**Location:** Design decisions exist only in git history/task folders

**Problem:**
When LLM sees a pattern that seems "wrong" (e.g., filesystem-based ID validation instead of database), there's no explanation of WHY we chose this approach. Future LLMs may try to "fix" intentional trade-offs.

**Severity:** Medium

**Impact:**
- Repeated discussions about same decisions
- Risk of breaking working patterns
- Lost context over time

### 4. **Duplicate Scripts Without Rationale**

**Location:** `story_create.py` in TWO places

**Problem:**
- `.sdlc-workflow/scripts/story_create.py` (authoritative)
- `.claude/skills/docs-stories/scripts/story_create.py` (purpose unclear)

No documentation explaining if these should stay in sync, which is canonical, or if duplication is intentional.

**Severity:** Low (not causing issues yet)

**Impact:**
- Future maintenance confusion
- Risk of divergence

### 5. **Subagents Lack Documentation Guidance**

**Location:** Subagent skill definitions (backend-fastapi, frontend-svelte)

**Problem:**
When subagents create/modify files, they don't know:
- File header requirements
- README expectations
- How to document decisions
- Where to find documentation standards

**Severity:** Medium

**Impact:**
- Inconsistent file headers (40% coverage)
- Inconsistent folder READMEs (30% coverage)
- Missing documentation

---

## Acceptance Criteria

### Functional Requirements

- [ ] **AC-1: Single Entry Point**
  - `skill.md` exists and provides comprehensive navigation to all SDLC documentation patterns
  - LLM can find guidance for any common task (create story, create task, commit format) via skill.md
  - Verification: Fresh LLM session can complete common tasks using only skill.md

- [ ] **AC-2: All Documentation Patterns Consolidated**
  - Every SDLC pattern is documented in appropriate references/ file
  - Stories: references/stories-guide.md
  - Tasks: references/tasks-guide.md
  - Commits: references/commit-guide.md
  - Branches: references/branch-guide.md
  - File headers/READMEs: references/documentation-standards.md
  - Traceability chain: references/traceability-guide.md
  - Validation rules: references/validation-rules.md
  - Verification: Cross-reference check finds no missing patterns

- [ ] **AC-3: Trade-offs Documented**
  - references/trade-offs.md exists with all major design decisions
  - Each trade-off includes: decision made, alternatives considered, rationale, sacrifices, when to revisit
  - Minimum documented trade-offs:
    - Filesystem-based story ID validation (not registry)
    - Task-based branching (not story-based)
    - Reference files (not inline in skill.md)
    - Explicit trade-offs documentation (not just "how-to")
    - Script consolidation strategy (single location vs duplication)
  - Verification: LLM reads trade-offs.md, understands rationale without asking user

- [ ] **AC-4: Integration with CLAUDE.md**
  - CLAUDE.md has new section in "Core Directives" mandating skill usage
  - Clear directive explaining WHEN to use skill, WHAT it provides
  - Pattern documented: Load skill → Follow guidance → Use scripts
  - Verification: CLAUDE.md section exists and is clear

- [ ] **AC-5: Subagent Awareness**
  - Key subagent skills reference sdlc-docs-orchestrator
  - Backend-fastapi, frontend-svelte, playwright-e2e-tester all mention documentation requirements
  - Subagents know to check documentation-standards.md for file headers
  - Verification: Subagent skill files contain references to orchestrator

- [ ] **AC-6: Script Integration & Documentation**
  - Audit all duplicate scripts across .sdlc-workflow/ and .claude/
  - Consolidate where appropriate (single source of truth)
  - Document consolidation decision in trade-offs.md (alternatives, rationale, when to revisit)
  - Document any remaining duplication with explicit justification
  - All scripts have clear ownership documented
  - Verification: Audit finds zero undocumented duplicates

- [ ] **AC-7: Examples Match Current Patterns**
  - examples/ directory exists with working templates
  - Example story creation passes validation
  - Example task folder matches current structure
  - Example commit messages pass validate_sdlc.py
  - Example branch names pass validate_branch.py
  - Verification: Test all examples against validation scripts

- [ ] **AC-8: Clear Scope Boundaries**
  - skill.md defines what belongs in orchestrator vs elsewhere
  - Clear distinction: .sdlc-workflow/ = artifacts, .claude/skills/ = LLM instructions
  - No ambiguity about where new documentation should live
  - Verification: Can answer "where does X documentation go?" for any X

### Technical Requirements

- [ ] **AC-9: Skill Directory Structure**
  - Directory renamed: `.claude/skills/docs-stories/` → `.claude/skills/sdlc-docs-orchestrator/`
  - Structure created:
    ```
    sdlc-docs-orchestrator/
    ├── skill.md
    ├── references/
    │   ├── stories-guide.md
    │   ├── tasks-guide.md
    │   ├── commit-guide.md
    │   ├── branch-guide.md
    │   ├── documentation-standards.md
    │   ├── traceability-guide.md
    │   ├── validation-rules.md
    │   └── trade-offs.md
    ├── scripts/
    │   └── (existing operational scripts)
    └── examples/
        ├── story-example.md
        ├── task-folder-example/
        └── commit-message-examples.txt
    ```

- [ ] **AC-10: All File References Valid**
  - Every link in skill.md points to existing file
  - Every referenced script exists and is executable
  - No broken references to .sdlc-workflow/ files
  - Verification: Automated check passes (or manual verification)

- [ ] **AC-11: Consistent Formatting**
  - All guides follow same structure: Purpose → Content → Examples → References
  - Each guide has "Last Updated" date
  - Each guide has "Version" number
  - Consistent markdown formatting across all files

### Quality Gates

- [ ] **AC-12: LLM Comprehension Test**
  - Fresh Claude session can read skill.md
  - Can complete: "Create user story for property search feature" without additional guidance
  - Can complete: "Create task folder for API endpoint" without additional guidance
  - Can answer: "What's the commit message format?" without searching
  - Verification: Actual test with fresh session

- [ ] **AC-13: Validation & Cross-Reference Checks**
  - All examples in examples/ directory pass existing validation scripts
  - story_create.py validates example story files
  - validate_branch.py validates example branch names
  - validate_sdlc.py validates example commit messages
  - validate_links.py validates all file references in skill.md and guides/
  - No contradictions found between guides (stories-guide vs NAMING-GUIDELINES, tasks-guide vs task README, commit-guide vs GIT_WORKFLOW)
  - Verification: All validation scripts exit 0 (no broken links, no invalid examples, no contradictions)

- [ ] **AC-14: Trade-offs Still Valid**
  - For each documented trade-off, verify decision still applies
  - Filesystem-based ID validation (we have ~4 stories, performance OK) ✓
  - Task-based branching (still LLM-only workflow) ✓
  - Reference files over inline (context not an issue) ✓
  - Verification: Review and confirm each trade-off

- [ ] **AC-15: Documentation Complete**
  - All sections in skill.md filled (no TODOs)
  - All references/ files complete (no placeholders)
  - All examples work correctly
  - README in scripts/ directory explains ownership

- [ ] **AC-16: Coordinator Validation Process**
  - Coordinator reviews all guides for completeness and accuracy
  - Coordinator verifies skill.md provides effective navigation
  - Coordinator validates trade-offs documentation is comprehensive
  - Coordinator confirms integration points work as designed
  - Coordinator tests LLM comprehension (AC-12 fresh session test)
  - Verification: Coordinator sign-off documented in task folder

---

## Technical Notes

### Technologies Used

- **Format:** Markdown (for all documentation)
- **Scripts:** Python 3 (existing operational scripts)
- **Validation:** Regex patterns (existing in validate_branch.py, validate_sdlc.py)
- **Structure:** Skill-based organization (Claude Code skill system)

### Integration Points

- **CLAUDE.md:** Main project instructions file that references this skill
- **Subagent Skills:** backend-fastapi, frontend-svelte, playwright-e2e-tester
- **Validation Scripts:** validate_branch.py, validate_sdlc.py, story_create.py
- **Task System:** Task folder structure, STATE.json tracking
- **Git Workflow:** Branch naming, commit messages, traceability chain
- **Existing Documentation:** .sdlc-workflow/ files (stories/, tasks/, GIT_WORKFLOW.md)

### Skill Structure Rationale

**Why skill.md as entry point?**
- Provides navigation and context
- Keeps detailed guides separate (maintainability)
- LLMs can reference specific guides (references/commit-guide.md)
- Matches existing skill pattern (dev-philosophy, planning-quality-gates)

**Why references/ directory?**
- Detailed guides can be comprehensive without overwhelming
- Easier to maintain (update one guide vs entire skill)
- Can reference specific guide for specific need
- Clear organization (stories-guide, tasks-guide, etc.)

**Why trade-offs.md?**
- Prevents future LLMs from "fixing" intentional choices
- Enables informed decisions about when to change
- Documents context that would otherwise be lost
- Aligns with "trust but verify" principle from CLAUDE.md

**Why examples/?**
- Working templates validate documentation accuracy
- LLMs can copy-paste working examples
- Examples serve as automated tests (run through validation scripts)

### Design Decisions

**Decision 1: Rename to sdlc-docs-orchestrator**
- More descriptive than "docs-stories"
- Emphasizes orchestration role (navigation hub, not just storage)
- Aligns with purpose: orchestrate access to all SDLC docs

**Decision 2: Keep scripts in .claude/skills/**
- Operational scripts stay with skill
- Avoid filesystem scatter (scripts in one place)
- If duplication exists, handle via symlinks or documentation

**Decision 3: Reference authoritative sources, don't duplicate**
- Guides REFERENCE .sdlc-workflow/ files as authoritative
- Don't copy entire GIT_WORKFLOW.md into commit-guide.md
- Provide summary + link to authoritative source
- Reduces maintenance burden

---

## Testing Strategy

### LLM Comprehension Testing

**Test 1: Story Creation**
- Give fresh Claude session only skill.md
- Scenario: "Create a new user story for property search feature"
- Expected: LLM follows stories-guide.md, uses story_create.py correctly
- Success: Story created with valid ID, proper naming, correct structure

**Test 2: Task Creation**
- Give fresh Claude session only skill.md
- Scenario: "Create a task folder for implementing API endpoint"
- Expected: LLM follows tasks-guide.md, creates proper folder structure
- Success: Task folder matches TEMPLATE structure

**Test 3: Commit Format**
- Give fresh Claude session only skill.md
- Scenario: "What's the commit message format for task-based work?"
- Expected: LLM references commit-guide.md, provides correct pattern
- Success: Answer includes task reference format

### Validation Testing

**Test 4: Example Validation**
- Run example branch name through validate_branch.py
- Run example commit message through validate_sdlc.py
- Run example story creation through story_create.py
- Success: All examples pass validation

### Cross-Reference Testing

**Test 5: Contradiction Detection**
- Manual review: stories-guide.md vs NAMING-GUIDELINES.md
- Manual review: tasks-guide.md vs task folder README.md
- Manual review: commit-guide.md vs GIT_WORKFLOW.md
- Success: No contradictions found

**Test 6: File Reference Validation**
- Check every link in skill.md points to existing file
- Check every referenced script exists
- Check every referenced .sdlc-workflow/ file exists
- Success: Zero broken references

### Integration Testing

**Test 7: Real Workflow**
- Create actual story using skill guidance
- Create actual task using skill guidance
- Make actual commit using skill guidance
- Success: Real workflow works smoothly

**Test 8: Trade-offs Validity**
- Review each trade-off in trade-offs.md
- Verify decision still applies to current state
- Filesystem validation: we have ~4 stories (performance OK)
- Task-based branching: still LLM-only workflow
- Success: All trade-offs valid for current state

---

## Documentation Requirements

### 1. skill.md - Main Orchestrator Instructions

**Location:** `.claude/skills/sdlc-docs-orchestrator/skill.md`

**Contents:**
- Overview: What this skill does, when to use it
- Core Concepts: Stories, Tasks, Git workflow (brief summary)
- Quick Reference: Common operations with direct links
- Detailed Guides: Links to references/ files
- Validation Rules: What's enforced and why
- Trade-offs: Link to trade-offs.md
- Integration Points: How this relates to other skills/hooks
- Maintenance: How to update this skill

### 2. references/stories-guide.md

**Location:** `.claude/skills/sdlc-docs-orchestrator/references/stories-guide.md`

**Contents:**
- When to create stories vs tasks
- Story ID format and naming conventions
- Suffix usage (US-001B) vs new ID (US-042)
- Using story_create.py script
- Story template sections
- Validation rules (link to authoritative NAMING-GUIDELINES.md)
- Examples

### 3. references/tasks-guide.md

**Location:** `.claude/skills/sdlc-docs-orchestrator/references/tasks-guide.md`

**Contents:**
- Task folder structure (README.md, progress.md, decisions.md, subagent-reports/)
- What goes in each file
- Task lifecycle (NOT_STARTED → IN_PROGRESS → COMPLETED)
- How to use task scripts (task_create.py, task_update_phase.py, etc.)
- Preservation strategy (why task folders never get deleted)
- Examples

### 4. references/commit-guide.md

**Location:** `.claude/skills/sdlc-docs-orchestrator/references/commit-guide.md`

**Contents:**
- Commit message format with task references
- Conventional commits types (feat, fix, docs, etc.)
- Story and task references in message
- Subagent marker in commit body
- Examples (valid and invalid)
- Validation enforcement (validate_sdlc.py)

### 5. references/branch-guide.md

**Location:** `.claude/skills/sdlc-docs-orchestrator/references/branch-guide.md`

**Contents:**
- Task-based branch naming pattern: {type}/TASK-{number}-US-{story}
- Why task-based (not story-based)
- Valid branch types
- Validation enforcement (validate_branch.py, pre_tool_use.py hook)
- Examples
- Troubleshooting invalid branch names

### 6. references/documentation-standards.md

**Location:** `.claude/skills/sdlc-docs-orchestrator/references/documentation-standards.md`

**Contents:**
- **File Header Requirements (Memory Print Chain):**
  - **Design Pattern:** Name of pattern used (e.g., "Repository Pattern", "Factory", "Singleton")
  - **Architecture Layer:** API, Service, Model, Component, Store, etc.
  - **Dependencies:** External packages and internal module dependencies
  - **Trade-offs:** Known cons, potential issues, limitations of current implementation
  - **Integration Points:** How this file connects to other system parts
  - **Testing Notes:** How to test, what to watch for, edge cases
- **Example:** apps/server/src/server/core/clerk.py (excellent file header)
- **Folder README requirements:**
  - Purpose of folder
  - Structure and organization
  - Key conventions
  - Entry points
- **When to create documentation:**
  - Every implementation file needs header
  - Every folder with code needs README
  - Complex logic needs inline comments
- **Documentation quality standards:**
  - Headers must enable instant context restoration
  - Trade-offs must explain "why" not just "what"
  - Future LLMs should understand rationale without asking
- **Templates for:**
  - Python files (backend)
  - TypeScript files (frontend)
  - Svelte components
  - Folder READMEs

### 7. references/traceability-guide.md

**Location:** `.claude/skills/sdlc-docs-orchestrator/references/traceability-guide.md`

**Contents:**
- Story → Task → Commit → Files chain
- How to trace from story to all commits
- How to trace from commit back to story
- STATE.json tracking system
- Information gathering process (manual, ~15-30 min per story)
- Examples of tracing workflows

### 8. references/validation-rules.md

**Location:** `.claude/skills/sdlc-docs-orchestrator/references/validation-rules.md`

**Contents:**
- All validation patterns enforced
- Branch naming regex
- Commit message regex
- Story ID validation logic
- Hook enforcement (sdlc_guardian.py, pre_tool_use.py)
- What happens when validation fails
- How to fix validation errors

### 9. references/trade-offs.md

**Location:** `.claude/skills/sdlc-docs-orchestrator/references/trade-offs.md`

**Contents:**
- Trade-off 1: Filesystem-based story ID validation
  - Decision, alternatives, rationale, sacrifices, when to revisit
- Trade-off 2: Task-based branching
- Trade-off 3: Reference files over inline
- Trade-off 4: Explicit trade-offs documentation
- Trade-off 5: Skill in .claude/skills/ (not .sdlc-workflow/)
- Template for documenting future trade-offs

### 10. examples/ Directory

**Location:** `.claude/skills/sdlc-docs-orchestrator/examples/`

**Contents:**
- story-example.md (complete example story)
- task-folder-example/ (complete example task folder)
- commit-message-examples.txt (valid commit messages)
- branch-name-examples.txt (valid branch names)

### 11. Update CLAUDE.md

**Location:** `CLAUDE.md`

**Contents:**
Add new section in "Core Directives":
```markdown
### SDLC Documentation Orchestrator Skill

**MANDATORY:** Use @.claude/skills/sdlc-docs-orchestrator/ skill for ALL SDLC documentation operations.

**When to Use:**
- Creating or modifying user stories
- Creating or managing task folders
- Understanding commit message patterns
- Understanding branch naming conventions
- Documenting design decisions
- Finding existing stories/tasks
- Understanding traceability chain

**What This Skill Provides:**
- Single source of truth for SDLC documentation workflow
- Comprehensive guidance on all documentation patterns
- Validation rules and enforcement mechanisms
- Trade-off documentation (why we chose X over Y)
- Examples and templates

**Pattern:**
1. Load skill: @.claude/skills/sdlc-docs-orchestrator/
2. Follow guidance from skill.md
3. Use scripts provided by skill for operations
4. Document decisions in appropriate locations per skill guidance
```

### 12. Update Subagent Skills

**Location:**
- `.claude/skills/dev-backend-fastapi/skill.md`
- `.claude/skills/dev-frontend-svelte/skill.md`
- `.claude/skills/playwright-e2e-tester/skill.md`

**Contents:**
Add documentation requirements section:
```markdown
### Documentation Requirements

Before creating/modifying implementation files:
- Check @.claude/skills/sdlc-docs-orchestrator/references/documentation-standards.md for file header requirements
- Document architectural decisions in task folder decisions.md
- Update task folder progress.md with your work
- Save your subagent report to task folder subagent-reports/
```

---

## Dependencies

### External Dependencies

None (documentation work only)

### Internal Dependencies

- Existing validation scripts (validate_branch.py, validate_sdlc.py, story_create.py)
- Existing .sdlc-workflow/ structure (stories/, tasks/, GIT_WORKFLOW.md)
- Existing CLAUDE.md (will be updated)
- Existing subagent skills (will be updated)

### Blocked By

None (can start immediately)

### Blocks

- **US-001D:** Code Review Checklist (will reference documentation-standards.md)
- **US-001E:** File Header Systematization (will use documentation-standards.md)
- **US-001F:** Testing Documentation (will follow same consolidation pattern)
- **All future SDLC improvements** (this becomes foundation)

---

## Tasks Breakdown

This user story will be broken down into 5 tasks:

1. **TASK-001: Skill Structure & Core Guides**
   - Rename skill directory (docs-stories → sdlc-docs-orchestrator)
   - Create skill.md (main orchestrator instructions)
   - Create references/stories-guide.md
   - Create references/tasks-guide.md
   - Create references/validation-rules.md
   - Estimated: 1 day

2. **TASK-002: Reference Documentation**
   - Create references/commit-guide.md
   - Create references/branch-guide.md
   - Create references/traceability-guide.md
   - Create references/documentation-standards.md
   - Estimated: 1 day

3. **TASK-003: Trade-offs & Examples**
   - Create references/trade-offs.md with all major design decisions
   - Create examples/ directory with templates
   - Add story example, task folder example, commit examples
   - Estimated: 0.5 day

4. **TASK-004: Integration & Consolidation**
   - Update CLAUDE.md with mandatory skill directive
   - Update subagent skill references
   - Audit and consolidate duplicate scripts
   - Update existing documentation to reference skill
   - Estimated: 1 day

5. **TASK-005: Validation & Testing**
   - Test all examples against validation scripts
   - Cross-check for contradictions
   - Verify all file references are accurate
   - Test LLM comprehension (fresh session test)
   - Estimated: 0.5 day

**Total Estimate:** 4 days

---

## Definition of Done

- [ ] All acceptance criteria met and verified (AC-1 through AC-16)
- [ ] skill.md complete with comprehensive navigation
- [ ] All 8 references/ guides complete (stories, tasks, commit, branch, docs-standards, traceability, validation, trade-offs)
- [ ] examples/ directory with working templates
- [ ] CLAUDE.md updated with mandatory directive
- [ ] Subagent skills updated with documentation references
- [ ] No undocumented script duplication
- [ ] All file references validated (no broken links)
- [ ] All examples pass validation scripts
- [ ] No contradictions between guides
- [ ] Trade-offs validated for current state
- [ ] LLM comprehension test passed (fresh session can use skill)
- [ ] Code review completed (coordinator review)
- [ ] Documentation complete (all sections filled, no TODOs)
- [ ] No critical issues
- [ ] All changes committed with proper task reference
- [ ] Branch name valid: feat/TASK-XXX-US-001C

---

## Notes

### Why This Matters

This story is foundational for all future SDLC work. By creating a single source of truth for documentation workflows, we:

1. **Reduce cognitive load:** LLMs don't waste time searching
2. **Enable consistency:** All LLMs follow same patterns
3. **Preserve knowledge:** Trade-offs documented, context not lost
4. **Prevent rework:** Clear guidance prevents mistakes
5. **Enable scaling:** More subagents can be added with clear documentation requirements

### Connection to US-001 Series

- **US-001:** Login flow validation (original) - exposed need for better testing/validation
- **US-001B:** RBAC + audit logging (follow-up) - planning revealed SDLC documentation gaps
- **US-001C:** SDLC docs orchestrator (this story) - addresses gaps found in US-001B audit
- **US-001D:** Code review checklist (next) - will use documentation-standards.md from this story
- **US-001E:** File header systematization (next) - will use documentation-standards.md from this story

All infrastructure work building on foundation established in US-001.

### Relationship to User's Mottos

**Motto 1: SINGLE AND CLEAR SOURCE OF TRUTH**
- ✅ This story creates that single source (skill.md as navigation hub)
- ✅ Consolidates scattered documentation
- ✅ Clear ownership and boundaries

**Motto 2: DOCUMENTED TRADE-OFFS**
- ✅ trade-offs.md documents all major decisions
- ✅ Explains WHY we chose X over Y
- ✅ Enables LLMs to judge if trade-off still valid
- ✅ Prevents "helpful" breaking of intentional choices

**Motto 3: Speed of Delivery with Guardrails**
- ✅ Faster work delivery (clear documentation, less searching)
- ✅ Guardrails in place (validation rules documented)
- ✅ Process enables speed (efficient access to information)

### Future Improvements

- **Automated validation of file references** (script to check all links in skill.md)
- **Session start hook** (automatically remind LLM about orchestrator skill)
- **Visual documentation map** (diagram showing all documentation locations)
- **Metrics tracking** (how often skill is referenced, which guides most used)
- **Automated trade-off review** (quarterly check if trade-offs still valid)

### References

- **Related Stories:**
  - US-001: Login flow validation
  - US-001B: RBAC & audit logging
  - US-017: Branch naming validation
  - US-001D: Code review checklist (future)
  - US-001E: File header systematization (future)

- **Related Reports:**
  - `.claude/reports/20251107-sdlc-traceability-audit.md` (identified gaps)
  - `.claude/reports/20251107-upcoming-work-report.md` (milestone planning)

- **Related Documentation:**
  - `.sdlc-workflow/stories/NAMING-GUIDELINES.md` (story naming rules)
  - `.sdlc-workflow/GIT_WORKFLOW.md` (git workflow)
  - `CLAUDE.md` (main project instructions)

---

**Template Version:** 1.0
**Last Updated:** 2025-11-07 (Enhanced with AC-16, link checker, script documentation per devops validation)

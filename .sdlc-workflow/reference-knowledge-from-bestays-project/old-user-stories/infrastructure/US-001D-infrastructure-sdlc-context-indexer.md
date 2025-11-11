# User Story: US-001D - Extend docs-stories Skill with Context Indexing

**Status:** READY
**Domain:** infrastructure
**Type:** feature
**Priority:** high
**Created:** 2025-11-07
**Updated:** 2025-11-07 (Revised to extend existing docs-stories skill)
**Estimated Complexity:** Medium (3 days)

---

## Story

**As a** LLM (Claude Code) working on Bestays
**I want** the docs-stories skill to index and retrieve complete context for any user story
**So that** I can restore full understanding of any code/decision in under 3 minutes (vs hours of manual archaeology)

---

## Background

### Why is this needed?

The **Memory Print Chain** philosophy states: *"Every line of code, every decision, every artifact must leave a 'memory print' that enables instant context restoration."*

We've built the chain:
- User Story → Task → README → File Header → Comments → Git History

But we lack **tooling to efficiently traverse this chain**. Currently, to understand US-001 (login flow validation), you must:
1. Manually find the story file
2. Manually search for task folders
3. Manually grep git log for commits
4. Manually read each file header
5. Manually piece together decisions from multiple sources

**Time to context: 30-60 minutes** (unacceptable)

### What's the business value?

**Goal:** Reduce time to full context from 30-60 minutes → **under 3 minutes**

**Benefits:**
- **Instant Onboarding:** New LLM sessions understand any story instantly
- **Faster Debugging:** Quickly understand "why" a decision was made
- **Trade-off Validation:** Check if historical trade-offs are still valid
- **Audit Trail:** Compliance teams can instantly reconstruct decision chain
- **Knowledge Preservation:** Nothing is lost across sessions
- **Reduced Repetition:** Don't re-discuss already-made decisions

### Memory Print Chain - The Philosophy

From CLAUDE.md:

> Choose solutions that maximize "memory print" for minimal cost. The goal is to restore complete context about any code at any point in time, close to instant (2-5 minutes).

**The Chain:**
```
User Story (why)
  → Task Folder (how, decisions, trade-offs)
    → Git Commits (when, who)
      → Implementation Files (what, design patterns, architecture)
        → File Headers (context, integration, testing)
```

**This story creates the tooling to traverse the chain efficiently.**

---

## Current Implementation

### What Exists Today

**`.claude/skills/docs-stories/` (Incomplete Skill)**
- ✅ `scripts/` with 10 Python scripts:
  - `story_create.py`, `story_find.py` - Story management
  - `task_create.py`, `task_list.py`, `task_update_state.py`, etc. - Task management
  - All scripts work but lack LLM guidance
- ❌ NO `SKILL.md` (LLMs can't discover or use the skill properly)
- ❌ Empty `references/` folder
- ❌ No context indexing functionality
- ❌ No retrieval guidance

**Documentation Artifacts (Created):**
- `.sdlc-workflow/stories/` - User stories with acceptance criteria
- `.sdlc-workflow/tasks/` - Task folders with decisions, reports, context
- Git history with semantic commit messages `(US-XXX TASK-YYY-semantic-name)`
- File headers (some files, standardization in progress via US-001C)
- Reports (`.claude/reports/`)

**What's Missing:**
- ❌ No SKILL.md to make docs-stories discoverable (overlaps with US-001C)
- ❌ No index of artifacts (must manually search filesystem)
- ❌ No context_index.py script to build index
- ❌ No quick way to find all files for a story
- ❌ No quick way to see all decisions for a story
- ❌ No way to reconstruct timeline for a story
- ❌ No automated extraction of design patterns/trade-offs
- ❌ No retrieval instructions in skill

### Example: Current Manual Process for US-001 Context

```bash
# 1. Find story file (manual search)
find .sdlc-workflow/stories -name "*US-001*"

# 2. Find task folders (manual search)
ls .sdlc-workflow/tasks/ | grep US-001

# 3. Find commits (complex git command)
git log --all --grep="US-001" --oneline

# 4. Find modified files (parse git log output)
git log --all --grep="US-001" --name-only --pretty=format:""

# 5. Read each file header (manual)
# 6. Read each task decisions.md (manual)
# 7. Read story acceptance criteria (manual)
# 8. Synthesize all information (mental work)

# Time: 30-60 minutes
```

---

## Proposed Solution

### Architecture

**Extend `.claude/skills/docs-stories/` with indexing and retrieval:**

**1. Create/Update SKILL.md** (`.claude/skills/docs-stories/SKILL.md`)
- Add YAML frontmatter (name, description)
- Document existing scripts (story/task creation)
- **Add new section: Context Indexing and Retrieval**
- Include query templates and usage examples
- Follow claude-skill-manager guidelines

**2. Add Indexer Script** (`.claude/skills/docs-stories/scripts/context_index.py`)
- Scans filesystem (source of truth): stories, tasks, git commits, files
- Builds structured JSON index with bidirectional cross-references
- Extracts metadata: design patterns, trade-offs, decisions
- Output: `.sdlc-workflow/.index/sdlc-index.json`
- Python 3.10+, standard lib only (no external deps)
- Run: On-demand via CLI

**3. Add references/ (optional)**
- Could add `references/index-schema.md` explaining index structure
- Keep lean - prefer putting instructions in SKILL.md
- Only if SKILL.md becomes too large (>5k words)

**Unified Skill:** docs-stories handles both:
- Creating/managing stories and tasks (existing functionality)
- Indexing and retrieving context (new functionality)

### Index Schema

```json
{
  "metadata": {
    "generated": "2025-11-07T10:30:00Z",
    "total_stories": 5,
    "total_tasks": 12,
    "total_commits": 45
  },
  "stories": {
    "US-001": {
      "id": "US-001",
      "title": "Login Flow Validation",
      "file": ".sdlc-workflow/stories/auth/US-001-login-flow-validation.md",
      "category": "auth",
      "status": "COMPLETED",
      "priority": "high",
      "tasks": ["TASK-001-file-headers", "TASK-002-login-tests"],
      "commits": ["461dd1e", "c257631"],
      "implementation_files": ["apps/frontend/tests/e2e/login.spec.ts"],
      "acceptance_criteria": ["Valid credentials authenticate", "Invalid credentials rejected"],
      "created": "2025-10-15",
      "completed": "2025-10-20"
    }
  },
  "tasks": {
    "TASK-001-file-headers": {
      "id": "TASK-001",
      "semantic_name": "file-headers",
      "full_id": "TASK-001-file-headers",
      "story": "US-001",
      "folder": ".sdlc-workflow/tasks/US-001-TASK-001-file-headers/",
      "status": "COMPLETED",
      "subagents": ["dev-backend-fastapi"],
      "files_modified": ["apps/server/core/clerk.py"],
      "decisions": {
        "file": "decisions.md",
        "summary": "Chose file headers with design patterns for instant context",
        "trade_offs": ["Pro: Instant clarity", "Con: Maintenance overhead"]
      },
      "commits": ["abc123"],
      "branch": "feat/TASK-001-file-headers-US-001"
    }
  },
  "commits": {
    "abc123": {
      "hash": "abc123",
      "short_hash": "abc123",
      "message": "feat: add file headers to backend deps (US-001 TASK-001-file-headers)",
      "story": "US-001",
      "task": "TASK-001-file-headers",
      "subagent": "dev-backend-fastapi",
      "files": ["apps/server/core/clerk.py", "apps/server/api/deps.py"],
      "date": "2025-10-16T14:30:00Z",
      "author": "Claude <noreply@anthropic.com>"
    }
  },
  "files": {
    "apps/server/core/clerk.py": {
      "path": "apps/server/core/clerk.py",
      "type": "backend",
      "stories": ["US-001"],
      "tasks": ["TASK-001-file-headers"],
      "design_pattern": "Singleton",
      "architecture_layer": "Core Service",
      "trade_offs": ["Vendor lock-in vs faster development"],
      "last_modified": "2025-10-16T14:30:00Z",
      "last_commit": "abc123"
    }
  },
  "reports": {
    "20251107-sdlc-traceability-audit.md": {
      "file": ".claude/reports/20251107-sdlc-traceability-audit.md",
      "title": "SDLC Traceability Audit",
      "date": "2025-11-07",
      "stories": ["US-001", "US-001B"],
      "completeness_score": 70
    }
  }
}
```

### Retrieval Skill - Common Queries

**1. Full Context for Story**
```
Query: "full context for US-001"
Output:
  - Story: Title, acceptance criteria, background
  - Tasks: All tasks with semantic names, decisions
  - Timeline: Commits in chronological order
  - Files: All files modified with design patterns
  - Trade-offs: All documented trade-offs
  - Reports: Related audit/analysis reports
  - Time: < 3 minutes
```

**2. Files Changed**
```
Query: "files changed in US-001"
Output: List of all files with paths, design patterns, architecture layers
```

**3. Decisions Made**
```
Query: "decisions for US-001"
Output: All decisions.md content from task folders
```

**4. Trade-offs**
```
Query: "trade-offs for authentication"
Output: All trade-offs sections from file headers related to auth
```

**5. Timeline**
```
Query: "timeline for US-001"
Output: Chronological list of commits with descriptions
```

---

## Acceptance Criteria

### AC-1: Indexer Script Scans Stories
**Given:** `.sdlc-workflow/stories/` contains US-001 and other stories
**When:** Run `python .sdlc-workflow/scripts/index_sdlc.py`
**Then:**
- Index contains all stories with metadata (id, title, status, category, priority)
- Index contains acceptance criteria for each story
- Index contains file paths to story markdown files

### AC-2: Indexer Script Scans Tasks
**Given:** `.sdlc-workflow/tasks/` contains task folders for US-001
**When:** Indexer runs
**Then:**
- Index contains all tasks with semantic names (e.g., TASK-001-file-headers)
- Index links tasks to parent stories
- Index extracts decisions.md summaries
- Index identifies subagents used
- Index lists files modified by each task

### AC-3: Indexer Script Scans Git Commits
**Given:** Git history contains commits with story/task references
**When:** Indexer runs with `git log` parsing
**Then:**
- Index contains all commits with US-XXX or TASK-YYY references
- Index extracts story ID, task ID, subagent from commit messages
- Index links commits to stories and tasks
- Index lists files modified in each commit
- Index includes commit metadata (hash, date, author, message)

### AC-4: Indexer Script Parses File Headers
**Given:** Implementation files have headers with design patterns and trade-offs
**When:** Indexer parses file headers
**Then:**
- Index extracts design pattern names (e.g., "Singleton", "Repository Pattern")
- Index extracts architecture layer (e.g., "Core Service", "API Layer")
- Index extracts trade-offs sections
- Index links files to stories and tasks that modified them

### AC-5: Index Contains Complete Cross-References
**Given:** Index is generated
**When:** Reviewing index structure
**Then:**
- Stories reference their tasks (list of task IDs)
- Stories reference their commits (list of commit hashes)
- Stories reference their implementation files (list of file paths)
- Tasks reference their commits
- Tasks reference their files modified
- Files reference their stories and tasks
- Commits reference their stories, tasks, and files
- All references are bidirectional (can traverse in any direction)

### AC-6: Index Output is Well-Formatted JSON
**Given:** Indexer completes successfully
**When:** Check output file `.sdlc-workflow/.index/sdlc-index.json`
**Then:**
- File is valid JSON (parseable)
- File is formatted with indentation (human-readable)
- File includes metadata (generation timestamp, counts)
- File size is reasonable (< 5MB for 50 stories)
- Schema matches documented structure

### AC-7: Indexer Has Comprehensive CLI
**Given:** Indexer script exists
**When:** Run `python index_sdlc.py --help`
**Then:**
- Shows usage instructions
- Shows available options (--output, --story-id, --verbose, etc.)
- Shows examples for common use cases
- Exit code 0

**When:** Run `python index_sdlc.py --story-id US-001`
**Then:** Generates index for US-001 only (filtered output)

### AC-8: Indexer Handles Edge Cases
**Given:** Various filesystem states
**When:** Indexer runs
**Then:**
- Handles missing task folders gracefully (logs warning, continues)
- Handles files without headers gracefully (includes in index with null metadata)
- Handles malformed commit messages gracefully (best-effort extraction)
- Handles empty .sdlc-workflow/stories/ (empty index, no error)
- Returns exit code 0 on success, non-zero on fatal errors

### AC-9: Retrieval Skill Exists and is Loadable
**Given:** Skill structure at `.claude/skills/research-sdlc-context/`
**When:** LLM tries to load skill
**Then:**
- `skill.json` exists with valid structure
- `instructions.md` exists with prompt guidance
- Skill is listed in available skills
- Skill description is clear: "Retrieve full context for user stories via SDLC index"

### AC-10: Retrieval Skill Provides Query Templates
**Given:** Skill instructions.md
**When:** LLM reads skill instructions
**Then:**
- Instructions include template for "full context for US-XXX"
- Instructions include template for "files changed in US-XXX"
- Instructions include template for "decisions for US-XXX"
- Instructions include template for "trade-offs for [topic]"
- Instructions include template for "timeline for US-XXX"
- Each template includes expected output format

### AC-11: Retrieval Skill Guides Index Reading
**Given:** Skill is invoked
**When:** LLM needs to query index
**Then:**
- Instructions explain how to read `.sdlc-workflow/.index/sdlc-index.json`
- Instructions explain index schema structure
- Instructions show how to extract specific data
- Instructions show how to traverse cross-references
- Instructions show how to format output for user

### AC-12: Test Case - Full Context for US-001 (PRIMARY TEST)
**Given:** US-001 story exists with tasks, commits, files
**When:** Run indexer + use retrieval skill with query "full context for US-001"
**Then:**
- Returns story title: "Login Flow Validation"
- Returns acceptance criteria (all 3 criteria)
- Returns all tasks with semantic names
- Returns all commits in chronological order
- Returns all files modified with design patterns (if available)
- Returns all decisions from task folders
- Returns trade-offs (from file headers or decisions.md)
- **Time to complete: < 3 minutes** (manual stopwatch)
- Output is formatted and readable (not raw JSON dump)

### AC-13: Test Case - Files Changed in US-001
**Given:** Index exists
**When:** Query "files changed in US-001"
**Then:**
- Returns complete list of files
- Includes file paths
- Includes design patterns (where available)
- Includes architecture layers (where available)
- Time: < 30 seconds

### AC-14: Test Case - Timeline for US-001
**Given:** Index exists
**When:** Query "timeline for US-001"
**Then:**
- Returns commits in chronological order (oldest first)
- Shows commit date, message, files changed
- Shows which task each commit belongs to
- Time: < 30 seconds

### AC-15: Documentation - Indexer README
**Given:** Indexer implementation complete
**When:** Check `.sdlc-workflow/scripts/README.md` or indexer docstring
**Then:**
- Explains purpose of indexer
- Shows installation/dependencies (if any)
- Shows usage examples (basic and advanced)
- Shows index schema structure
- Shows how to integrate with git hooks (optional)
- Shows troubleshooting common issues

### AC-16: Documentation - Retrieval Skill README
**Given:** Retrieval skill complete
**When:** Check `.claude/skills/research-sdlc-context/README.md`
**Then:**
- Explains purpose of skill
- Shows common queries with examples
- Shows expected output format
- Shows how skill integrates with Memory Print Chain
- Shows performance expectations (< 3 min for full context)

### AC-17: Integration - Update CLAUDE.md
**Given:** Indexer + skill are complete
**When:** Review CLAUDE.md
**Then:**
- Memory Print Chain section references new tooling
- Mentions indexer script in "Tools That Support Memory Print"
- Mentions retrieval skill in skill list
- Shows example: "How to get full context for US-001"

### AC-18: Performance - Index Generation Time
**Given:** Project with 20 stories, 50 tasks, 150 commits
**When:** Run indexer
**Then:**
- Completes in < 10 seconds
- Memory usage < 500MB
- Output file size < 2MB

### AC-19: Validation - Index Accuracy for US-001
**Given:** US-001 manual review completed
**When:** Compare indexer output to manual findings
**Then:**
- Story metadata matches (title, status, category)
- Task count matches
- Commit count matches (all commits with US-001 reference)
- File count matches (all files modified in US-001 commits)
- No false positives (no incorrect links)
- No false negatives (no missing links)

### AC-20: User Acceptance - Context Restoration Speed
**Given:** Fresh LLM session (no prior context)
**When:** LLM needs to understand US-001 implementation
**Then:**
- Using retrieval skill, LLM gets full context in < 3 minutes
- Manual stopwatch verification
- Context includes: story goals, decisions made, trade-offs, files changed, design patterns
- LLM can answer: "Why was Clerk chosen?", "What files implement auth?", "What are the trade-offs?"

---

## Technical Design

### Indexer Implementation (Python)

**Location:** `.claude/skills/docs-stories/scripts/context_index.py`

**Dependencies:**
- Python 3.10+
- Standard library only (json, pathlib, subprocess, re, argparse)
- No external packages (keep it simple)

**Architecture:**
```python
# Main components
class SDLCIndexer:
    def __init__(self, root_path: Path):
        self.root = root_path
        self.index = {
            "metadata": {},
            "stories": {},
            "tasks": {},
            "commits": {},
            "files": {},
            "reports": {}
        }

    def scan_stories(self) -> None:
        """Scan .sdlc-workflow/stories/ for story files"""
        pass

    def scan_tasks(self) -> None:
        """Scan .sdlc-workflow/tasks/ for task folders"""
        pass

    def scan_commits(self) -> None:
        """Parse git log for commits with story/task refs"""
        pass

    def parse_file_headers(self) -> None:
        """Extract metadata from implementation file headers"""
        pass

    def build_cross_references(self) -> None:
        """Link stories ↔ tasks ↔ commits ↔ files"""
        pass

    def write_index(self, output_path: Path) -> None:
        """Write JSON index to disk"""
        pass

# CLI
def main():
    parser = argparse.ArgumentParser(description="Index SDLC artifacts")
    parser.add_argument("--output", default=".sdlc-workflow/.index/sdlc-index.json")
    parser.add_argument("--story-id", help="Index specific story only")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    indexer = SDLCIndexer(root_path=Path.cwd())
    indexer.scan_stories()
    indexer.scan_tasks()
    indexer.scan_commits()
    indexer.parse_file_headers()
    indexer.build_cross_references()
    indexer.write_index(Path(args.output))
```

**Git Log Parsing Strategy:**
```bash
# Extract commits with story/task references
git log --all --pretty=format:'%H|%h|%ad|%an|%s' --date=iso --name-only \
  | grep -E "(US-[0-9]+|TASK-[0-9]+)"
```

**File Header Parsing Strategy:**
```python
# Look for structured comments at top of file
# Example header format:
"""
Architecture: Core Service / Singleton Pattern
Dependencies: fastapi, clerk-sdk
Trade-offs:
  - Pro: Shared Clerk client reduces memory
  - Con: Vendor lock-in to Clerk
Integration: Used by API layer (clerk_deps.py)
Testing: Mock Clerk SDK in tests
"""

# Parse with regex or simple line-by-line parser
```

### SKILL.md Structure

**Location:** `.claude/skills/docs-stories/SKILL.md`

**YAML Frontmatter:**
```yaml
---
name: docs-stories
description: Manage SDLC documentation (stories, tasks) and retrieve complete context for any user story in <3min. Use when creating/managing stories, creating/managing tasks, or retrieving full context via index.
---
```

**Content Structure:**
```markdown
# docs-stories Skill

## Purpose
[Brief description of skill covering both creation and retrieval]

## When to Use This Skill
- Creating new user stories
- Creating new tasks for stories
- Managing task state and progress
- **Retrieving full context for a user story**
- **Finding all files/decisions/commits for a story**

## Story and Task Management
[Instructions for existing scripts: story_create.py, task_create.py, etc.]

## Context Indexing and Retrieval

### Indexing Artifacts
To build the index, run:
```bash
python .claude/skills/docs-stories/scripts/context_index.py
```

### Retrieving Context
Read the index:
```python
import json
with open('.sdlc-workflow/.index/sdlc-index.json') as f:
    index = json.load(f)
```

Query by story ID:
```python
story = index['stories']['US-001']
# Returns: title, file, tasks, commits, files, acceptance_criteria
```

### Common Query Templates
[Templates for: full context, files changed, timeline, decisions, trade-offs]
```

---

## Implementation Plan

### Phase 1: Indexer Core (Day 1)
- Create `index_sdlc.py` script
- Implement story scanning
- Implement task scanning
- Implement basic cross-referencing
- Test on US-001

### Phase 2: Git Integration (Day 1)
- Implement git log parsing
- Extract story/task references from commit messages
- Link commits to stories and tasks
- Test on US-001 commit history

### Phase 3: File Header Parsing (Day 2)
- Implement file header parser
- Extract design patterns and trade-offs
- Link files to stories/tasks
- Handle files without headers gracefully

### Phase 4: Retrieval Skill (Day 2)
- Create skill structure
- Write instructions.md with query templates
- Create example outputs
- Test skill with real queries

### Phase 5: Testing & Validation (Day 3)
- Test AC-12: Full context for US-001 (< 3 min)
- Test AC-13: Files changed
- Test AC-14: Timeline
- Test AC-19: Index accuracy
- Test AC-20: User acceptance (stopwatch)

### Phase 6: Documentation (Day 3)
- Write indexer README
- Write skill README
- Update CLAUDE.md
- Create usage examples

---

## Dependencies

**Prerequisites:**
- US-001 story completed (exists as test case)
- Git history with semantic commit messages
- At least one task folder with decisions.md

**Related Stories:**
- US-001C (Documentation Orchestrator) - Can improve index quality if file headers standardized, but NOT blocking
- US-001B (Traceability Audit) - Identified need for better tooling, provides baseline metrics

**Blocks:**
- None (this is self-contained)

---

## Success Metrics

**Primary Metric:**
- **Context restoration time: < 3 minutes** (currently 30-60 minutes)

**Secondary Metrics:**
- Index generation time: < 10 seconds
- Index accuracy: 100% (no false positives/negatives for US-001)
- Skill usage: LLMs use skill successfully without manual intervention
- User satisfaction: "I can understand US-001 quickly now" (qualitative)

---

## Test Data

**Primary Test Case:** US-001 (Login Flow Validation)

**Why US-001:**
- Completed story (real artifacts exist)
- Has tasks, commits, files, decisions
- Representative of typical story complexity
- Good test for trade-offs documentation (Clerk vs alternatives)

**Expected Index Data for US-001:**
- Story file: `.sdlc-workflow/stories/auth/US-001-login-flow-validation.md`
- Tasks: At least TASK-001 (file headers)
- Commits: Multiple commits with US-001 reference
- Files: At least `apps/frontend/tests/e2e/login.spec.ts`
- Decisions: Clerk chosen over alternatives
- Trade-offs: Vendor lock-in documented

---

## Risk Assessment

**Risk:** Git log parsing fails on non-standard commit messages
**Mitigation:** Use best-effort parsing, log warnings for unparseable commits

**Risk:** File headers not standardized (US-001C not done yet)
**Mitigation:** Handle missing headers gracefully, document "N/A" for design pattern/trade-offs

**Risk:** Index becomes too large (> 10MB)
**Mitigation:** Implement --story-id filter, optimize JSON structure

**Risk:** < 3 min target not met
**Mitigation:** Index pre-aggregates data (no need to read files during retrieval), optimize skill instructions

---

## Future Enhancements (Out of Scope)

- Web UI for browsing index (interactive)
- Incremental indexing (only scan changed files)
- Git hook integration (auto-index on commit)
- Full-text search across decisions and reports
- Visualization of story relationships (graph)
- Export to other formats (HTML, Markdown, PDF)

---

## References

- **CLAUDE.md:** Memory Print Chain philosophy
- **GIT_WORKFLOW.md:** Commit message format with story/task references
- **Task Folder System:** `.sdlc-workflow/tasks/README.md`
- **US-001B Report:** `.claude/reports/20251107-sdlc-traceability-audit.md` (identified this need)

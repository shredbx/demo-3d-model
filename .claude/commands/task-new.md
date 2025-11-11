---
description: Create new task for a user story
---

Create a new task for an existing user story and set up git branch.

**Usage:** `/task-new <story-id> <type>`

**Arguments:**
- `story-id`: User story ID (e.g., US-001)
- `type`: Task type (feat | fix | refactor | test | docs)

**Workflow:**

1. **Validate story exists:**
   ```bash
   python3 .claude/skills/docs-stories/scripts/story_find.py <story-id>
   ```

2. **Create task:**
   ```bash
   python3 .claude/skills/docs-stories/scripts/task_create.py <story-id> <type>
   ```

3. **Load story context:**
   - Read story file
   - Display story description and acceptance criteria
   - Show task ID and branch created

4. **Display success:**
   ```
   ✓ Task created: TASK-001
   ✓ Branch created: feature/US-001-TASK-001
   ✓ Branch checked out
   ✓ Current task: TASK-001

   Story: US-001 - Login Flow Validation

   Next steps:
   - Use /task-research to start research phase
   - Or jump to /task-plan if no research needed
   ```

**Error Handling:**
- Story doesn't exist → Show error, list available stories
- Task creation fails → Show error details

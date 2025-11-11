---
description: Implementation phase - spawn dev agents to write code
---

Implementation phase: Spawn dev-backend-fastapi and/or dev-frontend-svelte to implement the plan.

**Usage:** `/task-implement`

**Requires:** Active task with PLANNING phase complete

**Workflow:**

1. **Validate active task:**
   ```bash
   task_id=$(cat .claude/tasks/current.txt)
   if [ "$task_id" = "none" ]; then
     echo "❌ No active task. Use /task-new first."
     exit 1
   fi
   ```

2. **Update phase:**
   ```bash
   python3 .claude/skills/docs-stories/scripts/task_update_phase.py $task_id IMPLEMENTATION start
   ```

3. **Load context:**
   - Read STATE.json
   - Read planning/implementation-plan.md
   - Determine which subagents needed (backend, frontend, both)

4. **Spawn appropriate dev subagent(s):**

   **If backend work needed:**
   ```
   Use Task tool with subagent_type="dev-backend-fastapi"

   Prompt:
   "Implement backend changes for TASK-{task_id}:

   Plan: {implementation_plan}

   Files to modify/create:
   {backend_files_list}

   Requirements:
   - Follow dev-philosophy skill
   - Follow dev-code-quality skill
   - Write tests for all new functionality
   - Add file headers to all modified files
   - Commit work when done

   Save implementation report to:
   .claude/tasks/{task_id}/subagent-reports/backend-report.md
   ```

   **If frontend work needed:**
   ```
   Use Task tool with subagent_type="dev-frontend-svelte"

   Prompt:
   "Implement frontend changes for TASK-{task_id}:

   Plan: {implementation_plan}

   Files to modify/create:
   {frontend_files_list}

   Requirements:
   - Follow dev-philosophy skill
   - Follow dev-code-quality skill
   - Use Svelte 5 runes (no legacy syntax)
   - Create Storybook stories for new components
   - Add file headers to all modified files
   - Commit work when done

   Save implementation report to:
   .claude/tasks/{task_id}/subagent-reports/frontend-report.md
   ```

5. **After subagent(s) complete:**
   - SubagentStop hook validates completeness
   - Hooks have tracked commits and file modifications in STATE.json

6. **Present results to user (FEEDBACK LOOP):**
   - Display what was implemented
   - Show commits made
   - Show files modified
   - IF user wants changes:
     - Discuss requirements
     - Respawn subagent with refinement context
     - LOOP back to step 6
   - IF user approves:
     - Continue to step 7

7. **Update phase:**
   ```bash
   python3 .claude/skills/docs-stories/scripts/task_update_phase.py $task_id IMPLEMENTATION complete
   ```

8. **Display next steps:**
   ```
   ✓ Implementation complete
   ✓ Commits: {commit_count}
   ✓ Files modified: {file_count}

   Next: /task-test to run tests and validation
   ```

**Error Handling:**
- No active task → Show error
- No plan found → Suggest /task-plan first
- Subagent fails → Display error, allow retry

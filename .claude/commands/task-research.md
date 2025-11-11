---
description: Research phase - analyze existing code and patterns
---

Research phase: Analyze existing code, find patterns, understand dependencies.

**Usage:** `/task-research`

**Requires:** Active task (current.txt must contain task ID)

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
   python3 .claude/skills/docs-stories/scripts/task_update_phase.py $task_id RESEARCH start
   ```

3. **Load story and task context:**
   - Read `.claude/tasks/$task_id/STATE.json`
   - Get story_id from STATE.json
   - Read story file
   - Display what needs to be researched

4. **Spawn Explore agent:**
   ```
   Use Task tool with subagent_type="Explore"

   Prompt for Explore agent:
   "Research the following for TASK-{task_id} ({story_id}):

   Story: {story_description}

   Research Goals:
   - Find existing similar implementations in the codebase
   - Identify relevant files and patterns
   - Understand dependencies and integration points
   - Document any constraints or gotchas

   Use medium thoroughness.

   Save findings to: .claude/tasks/{task_id}/research/findings.md
   ```

5. **After agent completes:**
   ```bash
   python3 .claude/skills/docs-stories/scripts/task_update_phase.py $task_id RESEARCH complete
   ```

6. **Save agent report:**
   ```bash
   # Save Explore agent's final report to:
   .claude/tasks/$task_id/research/agent-report.md
   ```

7. **Commit research artifacts:**
   ```bash
   git add .claude/tasks/$task_id/research/
   git commit -m "research: complete research phase (TASK-$task_id/US-XXX)"
   ```

8. **Display next steps:**
   ```
   ✓ Research phase complete

   Next: /task-plan to design implementation
   ```

**Error Handling:**
- No active task → Show error, suggest /task-new
- Explore agent fails → Save partial results, allow retry

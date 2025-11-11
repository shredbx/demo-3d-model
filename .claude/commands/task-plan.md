---
description: Planning phase - design implementation architecture
---

Planning phase: Design implementation approach using Plan agent.

**Usage:** `/task-plan`

**Requires:** Active task with RESEARCH phase complete (or can skip research)

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
   python3 .claude/skills/docs-stories/scripts/task_update_phase.py $task_id PLANNING start
   ```

3. **Load context:**
   - Read STATE.json
   - Read story file
   - Read research findings (if exist)
   - Prepare context for Plan agent

4. **Spawn Plan agent:**
   ```
   Use Task tool with subagent_type="Plan"

   Prompt for Plan agent:
   "Create implementation plan for TASK-{task_id} ({story_id}):

   Story: {story_description}

   Acceptance Criteria:
   {acceptance_criteria}

   Research Findings:
   {research_findings}

   Design:
   - Architecture approach
   - Which files to modify/create
   - Which subagents to use (dev-backend-fastapi, dev-frontend-svelte, both)
   - Implementation steps
   - Testing strategy
   - Complexity estimate

   Save plan to: .claude/tasks/{task_id}/planning/implementation-plan.md
   ```

5. **Present plan to user (ITERATIVE REFINEMENT):**
   - Display Plan agent's proposal
   - Ask user for feedback
   - IF user has concerns:
     - Discuss with user
     - Respawn Plan agent with refinement context
     - LOOP back to step 5
   - IF user approves:
     - Continue to step 6

6. **After plan approved:**
   ```bash
   python3 .claude/skills/docs-stories/scripts/task_update_phase.py $task_id PLANNING complete
   ```

7. **Save agent report:**
   ```bash
   # Save Plan agent's report to:
   .claude/tasks/$task_id/planning/agent-report.md
   ```

8. **Commit planning artifacts:**
   ```bash
   git add .claude/tasks/$task_id/planning/
   git commit -m "plan: complete planning phase (TASK-$task_id/US-XXX)"
   ```

9. **Display next steps:**
   ```
   ✓ Planning phase complete
   ✓ Plan approved

   Implementation Plan Summary:
   - Files to modify: {count}
   - Subagents needed: {agents}
   - Estimated complexity: {complexity}

   Next: /task-implement to start coding
   ```

**Error Handling:**
- No active task → Show error
- Plan agent fails → Allow retry
- User rejects plan → Allow re-planning

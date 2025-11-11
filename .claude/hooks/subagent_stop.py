#!/usr/bin/env python3
"""
SubagentStop Hook - Validate subagent completeness

Runs when: Subagent task completes and returns to main LLM
Purpose: Validate work completeness based on agent type

Input: JSON with subagent type and context
Exit codes:
- 0: Validation passed (always - warnings only, never blocks)
"""
import json
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Find project root."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".claude").exists():
            return current
        current = current.parent
    return Path.cwd()


def get_current_task() -> str | None:
    """Get current task ID."""
    try:
        project_root = get_project_root()
        current_file = project_root / ".claude" / "tasks" / "current.txt"
        if not current_file.exists():
            return None
        task_id = current_file.read_text().strip()
        return task_id if task_id and task_id != "none" else None
    except Exception:
        return None


def validate_backend_agent(task_id: str):
    """Validate dev-backend agent completeness."""
    warnings = []

    try:
        project_root = get_project_root()
        state_file = project_root / ".claude" / "tasks" / task_id / "STATE.json"

        if not state_file.exists():
            return

        state = json.loads(state_file.read_text())

        # Check commits made
        commits = state.get("commits", [])
        if not commits:
            warnings.append("⚠️  No commits made - implementation not saved")

        # Check backend files modified
        files_modified = state.get("files_modified", [])
        backend_files = [f for f in files_modified if f.startswith("apps/server/")]
        if not backend_files:
            warnings.append("⚠️  No backend files modified")

        # Check test files created
        test_files = [f for f in files_modified if "test" in f.lower()]
        if not test_files:
            warnings.append("⚠️  No test files created - add tests for new code")

        # Print warnings
        if warnings:
            print("\n🔍 Backend Agent Validation:")
            for warning in warnings:
                print(f"   {warning}")
            print()

    except Exception as e:
        print(f"⚠️  Validation error: {e}", file=sys.stderr)


def validate_frontend_agent(task_id: str):
    """Validate dev-frontend agent completeness."""
    warnings = []

    try:
        project_root = get_project_root()
        state_file = project_root / ".claude" / "tasks" / task_id / "STATE.json"

        if not state_file.exists():
            return

        state = json.loads(state_file.read_text())

        # Check commits made
        commits = state.get("commits", [])
        if not commits:
            warnings.append("⚠️  No commits made - implementation not saved")

        # Check frontend files modified
        files_modified = state.get("files_modified", [])
        frontend_files = [f for f in files_modified if f.startswith("apps/frontend/")]
        if not frontend_files:
            warnings.append("⚠️  No frontend files modified")

        # Check test files created
        test_files = [f for f in files_modified if "test" in f.lower() or "spec" in f.lower()]
        if not test_files:
            warnings.append("⚠️  No test files created - add E2E or component tests")

        # Print warnings
        if warnings:
            print("\n🔍 Frontend Agent Validation:")
            for warning in warnings:
                print(f"   {warning}")
            print()

    except Exception as e:
        print(f"⚠️  Validation error: {e}", file=sys.stderr)


def validate_explore_agent(task_id: str):
    """Validate Explore agent completeness."""
    warnings = []

    try:
        project_root = get_project_root()
        research_dir = project_root / ".claude" / "tasks" / task_id / "research"

        if not research_dir.exists():
            warnings.append("⚠️  Research directory not found")
        else:
            research_files = list(research_dir.glob("*.md"))
            if not research_files:
                warnings.append("⚠️  No research findings saved")

        # Print warnings
        if warnings:
            print("\n🔍 Explore Agent Validation:")
            for warning in warnings:
                print(f"   {warning}")
            print()

    except Exception as e:
        print(f"⚠️  Validation error: {e}", file=sys.stderr)


def validate_plan_agent(task_id: str):
    """Validate Plan agent completeness."""
    warnings = []

    try:
        project_root = get_project_root()
        planning_dir = project_root / ".claude" / "tasks" / task_id / "planning"

        if not planning_dir.exists():
            warnings.append("⚠️  Planning directory not found")
        else:
            planning_files = list(planning_dir.glob("*.md"))
            if not planning_files:
                warnings.append("⚠️  No planning artifacts saved")

            # Check for agent assignments
            for plan_file in planning_files:
                content = plan_file.read_text()
                if "dev-backend" not in content and "dev-frontend" not in content:
                    warnings.append("⚠️  Plan missing agent assignments")
                    break

        # Print warnings
        if warnings:
            print("\n🔍 Plan Agent Validation:")
            for warning in warnings:
                print(f"   {warning}")
            print()

    except Exception as e:
        print(f"⚠️  Validation error: {e}", file=sys.stderr)


def update_agents_used(task_id: str, agent_type: str):
    """Update STATE.json agents_used array."""
    try:
        project_root = get_project_root()
        state_file = project_root / ".claude" / "tasks" / task_id / "STATE.json"

        if not state_file.exists():
            return

        state = json.loads(state_file.read_text())

        # Add to agents_used if not already there
        if "agents_used" not in state:
            state["agents_used"] = []

        if agent_type not in state["agents_used"]:
            state["agents_used"].append(agent_type)

        # Write atomically
        temp_file = state_file.with_suffix('.tmp')
        temp_file.write_text(json.dumps(state, indent=2))
        temp_file.replace(state_file)

    except Exception as e:
        print(f"⚠️  Failed to update agents_used: {e}", file=sys.stderr)


def main():
    """Hook entry point."""
    try:
        # Read hook input
        input_data = json.load(sys.stdin)
        agent_type = input_data.get("subagent_type", "")

        # Get current task
        task_id = get_current_task()
        if not task_id:
            # No active task, skip validation
            sys.exit(0)

        # Validate based on agent type
        if agent_type == "dev-backend" or agent_type == "dev-backend-fastapi":
            validate_backend_agent(task_id)
            update_agents_used(task_id, "dev-backend")

        elif agent_type == "dev-frontend" or agent_type == "dev-frontend-svelte":
            validate_frontend_agent(task_id)
            update_agents_used(task_id, "dev-frontend")

        elif agent_type == "Explore":
            validate_explore_agent(task_id)
            update_agents_used(task_id, "Explore")

        elif agent_type == "Plan":
            validate_plan_agent(task_id)
            update_agents_used(task_id, "Plan")

        # Always succeed (warnings only, never block)
        sys.exit(0)

    except json.JSONDecodeError:
        # Invalid input, skip validation
        sys.exit(0)
    except Exception as e:
        # On error, log but don't fail
        print(f"⚠️  SubagentStop hook error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()

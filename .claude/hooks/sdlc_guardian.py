#!/usr/bin/env python3
"""
SDLC Guardian Hook - Enforces Coordinator vs Implementer Roles

This PreToolUse hook prevents the coordinator (main Claude) from directly
modifying implementation files. All implementation work MUST go through
specialized subagents.

Why this matters:
- Preserves context in task folders (subagent reports saved)
- Enforces code consistency (subagents know their domain patterns)
- Maintains audit trail (clear who did what)
- Prevents workflow violations before they happen

Exit codes:
- 0: Allow tool use (coordinator-allowed file)
- 2: Block tool use (implementation file, need subagent)
"""

import json
import sys
from pathlib import Path


# Paths that coordinator (main Claude) CAN modify
COORDINATOR_ALLOWED = [
    ".claude/",
    ".sdlc-workflow/",
    "CLAUDE.md",
    "README.md",
    ".gitignore",
    ".env.example",
]

# Paths that require subagent (implementation code)
IMPLEMENTATION_PATHS = [
    "apps/server/src/",
    "apps/frontend/src/",
    "tests/",
]

# Subagent mapping for helpful error messages
SUBAGENT_MAP = {
    "apps/server/src/": "dev-backend-fastapi",
    "apps/frontend/src/": "dev-frontend-svelte",
    "tests/e2e/": "playwright-e2e-tester",
    "tests/": "playwright-e2e-tester",  # fallback for tests/
}


def is_coordinator_allowed(file_path: str) -> bool:
    """Check if file can be modified by coordinator."""
    for allowed in COORDINATOR_ALLOWED:
        if file_path.startswith(allowed):
            return True
    return False


def is_implementation_file(file_path: str) -> bool:
    """Check if file is implementation code requiring subagent."""
    for impl_path in IMPLEMENTATION_PATHS:
        if file_path.startswith(impl_path):
            return True
    return False


def get_subagent_for_path(file_path: str) -> str:
    """Determine which subagent should handle this file."""
    for path_prefix, subagent in SUBAGENT_MAP.items():
        if file_path.startswith(path_prefix):
            return subagent
    return "appropriate subagent"


def main():
    """Run SDLC guardian check."""
    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")

        # Only check Edit and Write tools
        if tool_name not in ["Edit", "Write"]:
            sys.exit(0)

        # Empty path - allow (shouldn't happen but be safe)
        if not file_path:
            sys.exit(0)

        # Normalize path (remove leading ./)
        file_path = file_path.lstrip("./")

        # Check if coordinator is allowed to modify this file
        if is_coordinator_allowed(file_path):
            sys.exit(0)  # ✅ Allow

        # Check if this is an implementation file
        if is_implementation_file(file_path):
            # 🚨 BLOCK with helpful message
            subagent = get_subagent_for_path(file_path)

            print("\n" + "=" * 70)
            print("🚨 SDLC WORKFLOW VIOLATION")
            print("=" * 70)
            print(f"\n❌ Coordinator cannot modify implementation files!")
            print(f"\n📄 File: {file_path}")
            print(f"\n🤖 Use: Task(subagent_type=\"{subagent}\", ...)")
            print("\n💡 Remember: You are COORDINATOR only.")
            print("   - Launch subagents for ALL implementation work")
            print("   - Save subagent reports in task folder")
            print("   - Maintain audit trail")
            print(f"\n📖 See: CLAUDE.md section 'Coordinator vs Implementer Roles'")
            print("=" * 70 + "\n")

            sys.exit(2)  # Block the tool call

        # Unknown path (not explicitly allowed, not implementation)
        # Allow but could add warning if needed
        sys.exit(0)

    except Exception as e:
        # On error, log but don't block (fail open)
        print(f"⚠️  SDLC Guardian error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()

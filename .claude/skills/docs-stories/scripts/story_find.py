#!/usr/bin/env python3
"""
Find story by ID or validate story exists.

Usage:
    story_find.py <story-id>

Arguments:
    story-id: US-001 or US-001-auth-login-admin (flexible)

Examples:
    story_find.py US-001
    → .sdlc-workflow/stories/auth/US-001-auth-login-admin.md

    story_find.py US-001-auth-login-admin
    → .sdlc-workflow/stories/auth/US-001-auth-login-admin.md
"""
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Find project root (where .claude/ exists)."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".claude").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Not in a project with .claude/")


def find_story(story_id: str) -> Path:
    """
    Find story file by ID.

    Args:
        story_id: Story ID (US-001 or full US-001-auth-login-admin)

    Returns:
        Path to story file

    Raises:
        FileNotFoundError: If story not found
    """
    project_root = get_project_root()
    stories_dir = project_root / ".sdlc-workflow" / "stories"

    if not stories_dir.exists():
        raise FileNotFoundError(f"Stories directory not found: {stories_dir}")

    # Normalize story ID (extract US-XXX part)
    if story_id.startswith("US-"):
        # Extract just the number part (US-001)
        parts = story_id.split('-')
        if len(parts) >= 2:
            short_id = f"{parts[0]}-{parts[1]}"  # US-001
        else:
            short_id = story_id
    else:
        raise ValueError(f"Invalid story ID format: {story_id} (must start with US-)")

    # Search for story files matching the ID
    matching_files = list(stories_dir.rglob(f"{short_id}-*.md"))

    if not matching_files:
        # Try exact match if full ID provided
        matching_files = list(stories_dir.rglob(f"{story_id}.md"))

    if not matching_files:
        raise FileNotFoundError(f"Story {story_id} not found in {stories_dir}")

    # Return first match (should be only one)
    return matching_files[0]


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    story_id = sys.argv[1]

    try:
        story_path = find_story(story_id)
        print(str(story_path))
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Create new user story from template.

Usage:
    story_create.py <domain> <feature> <scope>

Arguments:
    domain: auth, booking, admin, etc.
    feature: login, signup, dashboard, etc.
    scope: admin, user, validation, etc.

Examples:
    story_create.py auth login admin
    → Creates US-001-auth-login-admin
"""
import sys
from pathlib import Path
from datetime import date


def get_project_root() -> Path:
    """Find project root (where .claude/ exists)."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".claude").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Not in a project with .claude/")


def get_next_story_number(stories_dir: Path) -> int:
    """
    Scan existing stories to find next story number.

    Args:
        stories_dir: Path to .sdlc-workflow/stories/

    Returns:
        Next story number (1, 2, 3, etc.)
    """
    story_files = list(stories_dir.rglob("US-*.md"))

    if not story_files:
        return 1

    numbers = []
    for file in story_files:
        try:
            # US-001-auth-login.md -> 001
            parts = file.stem.split('-')
            if len(parts) >= 2 and parts[0] == "US":
                num_str = parts[1]
                numbers.append(int(num_str))
        except (ValueError, IndexError):
            continue

    return max(numbers) + 1 if numbers else 1


def create_story(domain: str, feature: str, scope: str) -> str:
    """
    Create new user story from template.

    Args:
        domain: Story domain (auth, booking, etc.)
        feature: Feature name (login, signup, etc.)
        scope: Scope (admin, user, etc.)

    Returns:
        Story ID (US-001-auth-login-admin)
    """
    project_root = get_project_root()
    stories_dir = project_root / ".sdlc-workflow" / "stories"
    template_file = project_root / ".claude" / "templates" / "user-story.md"

    # Validate
    if not stories_dir.exists():
        raise FileNotFoundError(f"Stories directory not found: {stories_dir}")

    if not template_file.exists():
        raise FileNotFoundError(f"Template not found: {template_file}")

    # Get next story number
    next_number = get_next_story_number(stories_dir)

    # Generate story ID
    story_id = f"US-{next_number:03d}-{domain}-{feature}-{scope}"

    # Create domain directory if needed
    domain_dir = stories_dir / domain
    domain_dir.mkdir(parents=True, exist_ok=True)

    # Read template
    template_content = template_file.read_text()

    # Replace placeholders
    story_content = template_content.replace("{ID}", story_id)
    story_content = story_content.replace("{domain}", domain)
    story_content = story_content.replace("{feature}", feature)
    story_content = story_content.replace("{scope}", scope)
    story_content = story_content.replace("{created_date}", date.today().isoformat())

    # Write story file
    story_file = domain_dir / f"{story_id}.md"
    story_file.write_text(story_content)

    return story_id


def main():
    """CLI entry point."""
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    domain = sys.argv[1]
    feature = sys.argv[2]
    scope = sys.argv[3]

    try:
        story_id = create_story(domain, feature, scope)
        print(story_id)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Story Creation Script

Creates a new user story from template with automatic ID generation.

Usage:
    python story_create.py --domain auth --title "Login flow" --type feature --priority high

Arguments:
    --domain: Story domain (auth, booking, property, admin, etc.)
    --title: Short story title
    --type: Story type (feature, validation, bugfix, refactor, spike)
    --priority: Priority level (high, medium, low)

Output:
    Creates .sdlc-workflow/stories/{domain}/US-{ID}-{domain}-{title-slug}.md
"""

import argparse
import os
import re
from datetime import datetime
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    # Script is in .sdlc-workflow/scripts/, project root is two levels up
    return Path(__file__).parent.parent.parent


def get_all_story_ids() -> dict:
    """
    Scan all existing story IDs (including suffixed variants like US-001B).

    Returns:
        Dict mapping base ID -> list of variants
        Example: {"001": ["US-001", "US-001B"], "016": ["US-016"]}
    """
    stories_dir = get_project_root() / ".sdlc-workflow" / "stories"
    story_ids = {}

    if not stories_dir.exists():
        return story_ids

    # Pattern matches: US-001, US-001B, US-042C, etc.
    pattern = re.compile(r"US-(\d{3})([A-Z]?)")

    for md_file in stories_dir.rglob("*.md"):
        # Skip template and README
        if md_file.name in ["TEMPLATE.md", "README.md"]:
            continue

        match = pattern.search(md_file.name)
        if match:
            base_id = match.group(1)  # "001"
            suffix = match.group(2)    # "B" or ""
            full_id = f"US-{base_id}{suffix}"

            if base_id not in story_ids:
                story_ids[base_id] = []
            story_ids[base_id].append(full_id)

    return story_ids


def get_next_story_id() -> str:
    """
    Generate the next US-XXX ID by scanning existing stories.

    Returns:
        Next available ID in format US-001, US-002, etc.
    """
    story_ids = get_all_story_ids()

    if not story_ids:
        return "US-001"

    # Find max base ID (as integer)
    max_id = max(int(base_id) for base_id in story_ids.keys())
    next_id = max_id + 1
    return f"US-{next_id:03d}"


def validate_story_id_unique(story_id: str) -> tuple[bool, str]:
    """
    Check if story ID already exists.

    Args:
        story_id: Full story ID like "US-001" or "US-001B"

    Returns:
        Tuple of (is_unique, error_message)
        - (True, "") if ID is unique
        - (False, "error message") if ID already exists
    """
    story_ids = get_all_story_ids()

    # Extract base ID and suffix from input
    pattern = re.compile(r"US-(\d{3})([A-Z]?)")
    match = pattern.match(story_id)
    if not match:
        return False, f"Invalid story ID format: {story_id}"

    base_id = match.group(1)
    suffix = match.group(2)

    # Check if this exact ID exists
    if base_id in story_ids:
        existing_variants = story_ids[base_id]
        if story_id in existing_variants:
            return False, f"Story ID {story_id} already exists: {existing_variants}"

    return True, ""


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.

    Example: "Login Flow" -> "login-flow"
    """
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and underscores with hyphens
    text = re.sub(r"[\s_]+", "-", text)
    # Remove non-alphanumeric characters except hyphens
    text = re.sub(r"[^a-z0-9-]", "", text)
    # Remove multiple consecutive hyphens
    text = re.sub(r"-+", "-", text)
    # Remove leading/trailing hyphens
    text = text.strip("-")
    return text


def create_story(
    domain: str,
    title: str,
    story_type: str,
    priority: str,
    story_id: str = None,
    suffix: str = None
) -> Path:
    """
    Create a new user story from template.

    Args:
        domain: Story domain (auth, booking, etc.)
        title: Short title for the story
        story_type: Type of story (feature, validation, etc.)
        priority: Priority level (high, medium, low)
        story_id: Optional specific story ID (e.g., "US-042" to fill gap)
        suffix: Optional suffix for related story (e.g., "B" for US-001B)

    Returns:
        Path to the created story file
    """
    project_root = get_project_root()
    stories_dir = project_root / ".sdlc-workflow" / "stories"
    template_path = stories_dir / "TEMPLATE.md"

    # Validate template exists
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    # Generate or validate story ID
    if story_id:
        # Manual ID provided - validate format
        if not re.match(r"US-\d{3}$", story_id):
            raise ValueError(f"Invalid story ID format: {story_id}. Expected: US-XXX (e.g., US-042)")
        final_story_id = story_id
    else:
        # Auto-generate next ID
        final_story_id = get_next_story_id()

    # Add suffix if provided
    if suffix:
        if not re.match(r"^[A-Z]$", suffix):
            raise ValueError(f"Invalid suffix: {suffix}. Must be single uppercase letter (A-Z)")
        final_story_id = f"{final_story_id}{suffix}"

    # Validate ID uniqueness
    is_unique, error_msg = validate_story_id_unique(final_story_id)
    if not is_unique:
        # Show what IDs exist and suggest alternatives
        story_ids = get_all_story_ids()
        existing_info = "\n".join([f"  - {base}: {', '.join(variants)}"
                                   for base, variants in sorted(story_ids.items())])
        raise ValueError(
            f"{error_msg}\n\n"
            f"Existing story IDs:\n{existing_info}\n\n"
            f"Suggestions:\n"
            f"  - Use next sequential ID: {get_next_story_id()}\n"
            f"  - Add suffix to related story: {final_story_id[:-1] if suffix else final_story_id}B\n"
            f"  - Fill a gap: US-002 to US-015 are available"
        )

    # Create filename
    title_slug = slugify(title)
    filename = f"{final_story_id}-{domain}-{title_slug}.md"

    # Create domain directory if needed
    domain_dir = stories_dir / domain
    domain_dir.mkdir(exist_ok=True)

    # Full path for new story
    story_path = domain_dir / filename

    # Check if file already exists
    if story_path.exists():
        raise FileExistsError(f"Story already exists: {story_path}")

    # Read template
    with open(template_path, "r") as f:
        template_content = f.read()

    # Replace placeholders
    current_date = datetime.now().strftime("%Y-%m-%d")

    story_content = template_content.replace("{story_id}", final_story_id)
    story_content = story_content.replace("{title}", title)
    story_content = story_content.replace("{domain}", domain)
    story_content = story_content.replace("{type}", story_type)
    story_content = story_content.replace("{priority}", priority)
    story_content = story_content.replace("{date}", current_date)

    # Write new story file
    with open(story_path, "w") as f:
        f.write(story_content)

    return story_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create a new user story from template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-generate next ID (e.g., US-018)
  python story_create.py --domain auth --title "Password reset" --type feature --priority high

  # Fill a gap in milestone (US-002)
  python story_create.py --domain property --title "Homepage" --type feature --priority high --story-id US-002

  # Create related/follow-up story with suffix (US-001B)
  python story_create.py --domain auth --title "RBAC and audit" --type feature --priority high --story-id US-001 --suffix B

  # Or let script auto-generate and add suffix to next ID
  python story_create.py --domain auth --title "MFA support" --type feature --priority high --suffix C
        """
    )

    parser.add_argument(
        "--domain",
        required=True,
        help="Story domain (auth, booking, property, admin, etc.)"
    )

    parser.add_argument(
        "--title",
        required=True,
        help="Short story title (will be slugified for filename)"
    )

    parser.add_argument(
        "--type",
        required=True,
        choices=["feature", "validation", "bugfix", "refactor", "spike"],
        help="Type of story"
    )

    parser.add_argument(
        "--priority",
        required=True,
        choices=["high", "medium", "low"],
        help="Priority level"
    )

    parser.add_argument(
        "--story-id",
        required=False,
        help="Optional: Specific story ID (e.g., US-042 to fill gap). If omitted, next sequential ID is used."
    )

    parser.add_argument(
        "--suffix",
        required=False,
        help="Optional: Letter suffix for related story (e.g., B for US-001B). Requires --story-id or uses next ID."
    )

    args = parser.parse_args()

    try:
        story_path = create_story(
            domain=args.domain,
            title=args.title,
            story_type=args.type,
            priority=args.priority,
            story_id=args.story_id,
            suffix=args.suffix
        )

        print(f"✅ Story created successfully!")
        print(f"📄 File: {story_path}")
        print(f"")
        print(f"Next steps:")
        print(f"1. Open the file and fill in the story details")
        print(f"2. Add acceptance criteria")
        print(f"3. Define technical requirements")
        print(f"4. Review and commit")

    except Exception as e:
        print(f"❌ Error creating story: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

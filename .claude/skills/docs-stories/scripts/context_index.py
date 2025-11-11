#!/usr/bin/env python3
"""
Context Indexer for SDLC Workflow

Scans .sdlc-workflow/ and .claude/tasks/ to build structured JSON index
with bidirectional cross-references for instant context restoration.

Usage:
    python context_index.py [--story-id US-XXX] [--output PATH] [--verbose]

Output:
    .sdlc-workflow/.index/sdlc-index.json
"""

import json
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import argparse


# Find project root (contains .claude/ folder)
def find_project_root() -> Path:
    current = Path.cwd()
    while current != current.parent:
        if (current / ".claude").is_dir():
            return current
        current = current.parent
    raise RuntimeError("Not in a project with .claude/ folder")


PROJECT_ROOT = find_project_root()
STORIES_DIR = PROJECT_ROOT / ".sdlc-workflow" / "stories"
TASKS_DIR = PROJECT_ROOT / ".claude" / "tasks"
INDEX_DIR = PROJECT_ROOT / ".sdlc-workflow" / ".index"
INDEX_FILE = INDEX_DIR / "sdlc-index.json"


def parse_story_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """Parse story markdown file and extract metadata."""
    try:
        content = file_path.read_text(encoding='utf-8')

        # Extract story ID from filename (US-XXX or US-XXXA)
        match = re.search(r'US-\d+[A-Z]?', file_path.name)
        if not match:
            return None
        story_id = match.group(0)

        # Extract title (# User Story: US-XXX - Title)
        title_match = re.search(r'# User Story: US-\d+[A-Z]? - (.+)', content)
        title = title_match.group(1) if title_match else "Unknown"

        # Extract metadata from YAML-like frontmatter
        status_match = re.search(r'\*\*Status:\*\* (.+)', content)
        status = status_match.group(1).strip() if status_match else "UNKNOWN"

        domain_match = re.search(r'\*\*Domain:\*\* (.+)', content)
        domain = domain_match.group(1).strip() if domain_match else "unknown"

        # Extract acceptance criteria section
        ac_match = re.search(
            r'## Acceptance Criteria\s+(.*?)(?=\n## |\Z)',
            content,
            re.DOTALL
        )
        acceptance_criteria = []
        if ac_match:
            ac_text = ac_match.group(1)
            # Find all AC items (- [ ] **AC-X:** Description)
            ac_items = re.findall(r'- \[ \] \*\*AC-\d+:\*\* (.+)', ac_text)
            acceptance_criteria = ac_items

        return {
            "id": story_id,
            "title": title,
            "status": status,
            "domain": domain,
            "file": str(file_path.relative_to(PROJECT_ROOT)),
            "acceptance_criteria": acceptance_criteria,
            "tasks": [],  # Will populate later
            "commits": [],  # Will populate later
            "implementation_files": []  # Will populate later
        }
    except Exception as e:
        print(f"Warning: Failed to parse {file_path}: {e}")
        return None


def scan_stories(story_id_filter: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """Scan .sdlc-workflow/stories/ for story files."""
    stories = {}

    if not STORIES_DIR.exists():
        return stories

    for story_file in STORIES_DIR.rglob("US-*.md"):
        if story_file.name == "TEMPLATE.md":
            continue

        story = parse_story_file(story_file)
        if story:
            if story_id_filter and story["id"] != story_id_filter:
                continue
            stories[story["id"]] = story

    return stories


def parse_task_folder(task_dir: Path) -> Optional[Dict[str, Any]]:
    """Parse task folder and extract metadata from STATE.json."""
    state_file = task_dir / "STATE.json"

    if not state_file.exists():
        return None

    try:
        state = json.loads(state_file.read_text(encoding='utf-8'))

        task_id = state.get("task_id", task_dir.name)

        # Extract decisions from decisions.md
        decisions = ""
        decisions_file = task_dir / "decisions.md"
        if decisions_file.exists():
            decisions = decisions_file.read_text(encoding='utf-8')

        # Collect subagent reports
        reports_dir = task_dir / "subagent-reports"
        subagent_reports = []
        if reports_dir.exists():
            for report_file in reports_dir.glob("*.md"):
                subagent_reports.append(str(report_file.relative_to(PROJECT_ROOT)))

        return {
            "id": task_id,
            "semantic_name": state.get("semantic_name", ""),
            "story": state.get("story", ""),
            "status": state.get("status", "NOT_STARTED"),
            "phase": state.get("phase", "RESEARCH"),
            "folder": str(task_dir.relative_to(PROJECT_ROOT)),
            "decisions": decisions[:500] if decisions else "",  # Truncate for size
            "files_modified": state.get("files_modified", []),
            "commits": state.get("commits", []),
            "subagent_reports": subagent_reports
        }
    except Exception as e:
        print(f"Warning: Failed to parse {task_dir}: {e}")
        return None


def scan_tasks(story_id_filter: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """Scan .claude/tasks/ for task folders."""
    tasks = {}

    if not TASKS_DIR.exists():
        return tasks

    for task_dir in TASKS_DIR.iterdir():
        if not task_dir.is_dir() or task_dir.name == "TEMPLATE":
            continue

        task = parse_task_folder(task_dir)
        if task:
            if story_id_filter and task["story"] != story_id_filter:
                continue
            tasks[task["id"]] = task

    return tasks


def scan_git_commits(story_id_filter: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """Parse git log for commits with US-XXX or TASK-YYY references."""
    commits = {}

    try:
        # Get git log with commit hash, date, message, and files changed
        git_log = subprocess.run(
            ["git", "log", "--all", "--pretty=format:%H|%ci|%s", "--name-only"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True
        )

        lines = git_log.stdout.strip().split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            if '|' in line:
                parts = line.split('|', 2)
                if len(parts) == 3:
                    commit_hash, date_str, message = parts

                    # Extract story/task references from message
                    story_refs = re.findall(r'US-\d+[A-Z]?', message)
                    task_refs = re.findall(r'TASK-\d+(?:-[\w-]+)?', message)

                    if story_id_filter and story_id_filter not in story_refs:
                        i += 1
                        continue

                    # Collect files changed (next lines until empty line or next commit)
                    files = []
                    i += 1
                    while i < len(lines) and lines[i] and '|' not in lines[i]:
                        files.append(lines[i])
                        i += 1

                    commits[commit_hash] = {
                        "hash": commit_hash,
                        "date": date_str,
                        "message": message,
                        "story_refs": story_refs,
                        "task_refs": task_refs,
                        "files": files
                    }
            i += 1
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to scan git log: {e}")

    return commits


def parse_file_header(file_path: Path) -> Optional[Dict[str, Any]]:
    """Parse file header for design pattern, architecture layer, trade-offs."""
    try:
        content = file_path.read_text(encoding='utf-8')

        # Look for header comments (first 50 lines)
        lines = content.split('\n')[:50]
        header_text = '\n'.join(lines)

        # Extract design pattern
        pattern_match = re.search(r'Design Pattern:\s*(.+)', header_text, re.IGNORECASE)
        design_pattern = pattern_match.group(1).strip() if pattern_match else ""

        # Extract architecture layer
        layer_match = re.search(r'Architecture Layer:\s*(.+)', header_text, re.IGNORECASE)
        architecture_layer = layer_match.group(1).strip() if layer_match else ""

        # Extract trade-offs
        tradeoffs_match = re.search(r'Trade-offs?:\s*(.+)', header_text, re.IGNORECASE)
        tradeoffs = tradeoffs_match.group(1).strip() if tradeoffs_match else ""

        if design_pattern or architecture_layer or tradeoffs:
            return {
                "design_pattern": design_pattern,
                "architecture_layer": architecture_layer,
                "tradeoffs": tradeoffs
            }
    except Exception:
        pass

    return None


def scan_files(commits: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Scan implementation files for headers."""
    files = {}

    # Collect unique file paths from commits
    all_files = set()
    for commit in commits.values():
        all_files.update(commit["files"])

    for file_path_str in all_files:
        file_path = PROJECT_ROOT / file_path_str
        if not file_path.exists():
            continue

        # Only parse implementation files (not docs, configs, etc.)
        if not (file_path.suffix in ['.py', '.ts', '.svelte', '.tsx', '.jsx']):
            continue

        header = parse_file_header(file_path)
        if header:
            files[file_path_str] = {
                "path": file_path_str,
                **header,
                "stories": [],  # Will populate later
                "tasks": [],  # Will populate later
                "commits": []  # Will populate later
            }

    return files


def build_cross_references(
    stories: Dict[str, Dict[str, Any]],
    tasks: Dict[str, Dict[str, Any]],
    commits: Dict[str, Dict[str, Any]],
    files: Dict[str, Dict[str, Any]]
) -> None:
    """Build bidirectional cross-references between all entities."""

    # Link tasks → stories
    for task_id, task in tasks.items():
        story_id = task["story"]
        if story_id in stories:
            if task_id not in stories[story_id]["tasks"]:
                stories[story_id]["tasks"].append(task_id)

    # Link commits → stories and tasks
    for commit_hash, commit in commits.items():
        for story_id in commit["story_refs"]:
            if story_id in stories:
                if commit_hash not in stories[story_id]["commits"]:
                    stories[story_id]["commits"].append(commit_hash)

        for task_ref in commit["task_refs"]:
            # Extract task ID (TASK-001 from TASK-001-semantic-name)
            task_id_match = re.match(r'TASK-\d+', task_ref)
            if task_id_match:
                task_id = task_id_match.group(0)
                if task_id in tasks:
                    if commit_hash not in tasks[task_id]["commits"]:
                        tasks[task_id]["commits"].append(commit_hash)

    # Link files → stories and tasks via commits
    for commit_hash, commit in commits.items():
        for file_path in commit["files"]:
            if file_path in files:
                # Add commit reference
                if commit_hash not in files[file_path]["commits"]:
                    files[file_path]["commits"].append(commit_hash)

                # Add story references
                for story_id in commit["story_refs"]:
                    if story_id not in files[file_path]["stories"]:
                        files[file_path]["stories"].append(story_id)

                    # Add file to story's implementation_files
                    if story_id in stories:
                        if file_path not in stories[story_id]["implementation_files"]:
                            stories[story_id]["implementation_files"].append(file_path)

                # Add task references
                for task_ref in commit["task_refs"]:
                    task_id_match = re.match(r'TASK-\d+', task_ref)
                    if task_id_match:
                        task_id = task_id_match.group(0)
                        if task_id not in files[file_path]["tasks"]:
                            files[file_path]["tasks"].append(task_id)


def build_index(story_id_filter: Optional[str] = None, verbose: bool = False) -> Dict[str, Any]:
    """Build complete SDLC index."""
    if verbose:
        print(f"Scanning stories from {STORIES_DIR}...")
    stories = scan_stories(story_id_filter)
    if verbose:
        print(f"Found {len(stories)} stories")

    if verbose:
        print(f"Scanning tasks from {TASKS_DIR}...")
    tasks = scan_tasks(story_id_filter)
    if verbose:
        print(f"Found {len(tasks)} tasks")

    if verbose:
        print("Scanning git commits...")
    commits = scan_git_commits(story_id_filter)
    if verbose:
        print(f"Found {len(commits)} commits")

    if verbose:
        print("Scanning implementation files...")
    files = scan_files(commits)
    if verbose:
        print(f"Found {len(files)} files with headers")

    if verbose:
        print("Building cross-references...")
    build_cross_references(stories, tasks, commits, files)

    index = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "total_stories": len(stories),
            "total_tasks": len(tasks),
            "total_commits": len(commits),
            "total_files": len(files)
        },
        "stories": stories,
        "tasks": tasks,
        "commits": commits,
        "files": files
    }

    return index


def main():
    parser = argparse.ArgumentParser(
        description="Build SDLC context index from stories, tasks, and git history"
    )
    parser.add_argument(
        "--story-id",
        help="Index specific story only (e.g., US-001)"
    )
    parser.add_argument(
        "--output",
        help=f"Output path (default: {INDEX_FILE})",
        default=str(INDEX_FILE)
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    if args.verbose:
        print(f"Project root: {PROJECT_ROOT}")
        print(f"Building index...")

    index = build_index(args.story_id, args.verbose)

    # Create output directory if needed
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write index
    output_path.write_text(json.dumps(index, indent=2), encoding='utf-8')

    print(f"✅ Index created: {output_path}")
    print(f"   Stories: {index['metadata']['total_stories']}")
    print(f"   Tasks: {index['metadata']['total_tasks']}")
    print(f"   Commits: {index['metadata']['total_commits']}")
    print(f"   Files: {index['metadata']['total_files']}")


if __name__ == "__main__":
    main()

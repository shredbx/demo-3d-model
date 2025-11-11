# docs-stories Script Updates for Multi-Product Support

**Date:** 2025-11-07
**Related Decision:** `.claude/reports/20251107-multi-product-story-workflow.md`

---

## Overview

The following scripts need updates to support multi-product workflow (bestays + realestate).

---

## story_create.py Updates

### Current Behavior
Creates story from TEMPLATE.md with placeholders.

### Required Changes

**1. Add product parameter:**
```python
def create_story(domain, feature, scope, product='bestays'):
```

**2. Replace new placeholders in template:**
```python
# After copying TEMPLATE.md, replace:
content = content.replace('{default_product}', product)
content = content.replace('{portable}', 'true')  # or prompt user
content = content.replace('{ported_to}', '[]')
```

**3. Update CLI arguments:**
```bash
python story_create.py <domain> <feature> <scope> [--product bestays|realestate]
```

---

## story_find.py Updates

### Current Behavior
Finds stories by domain and status.

### Required Changes

**1. Add product filter:**
```python
def find_stories(domain=None, status=None, product=None, portable=None):
```

**2. Parse story metadata:**
```python
# Read story file and extract:
# - default_product
# - portable
# - ported_to
```

**3. Filter by product:**
```python
# If --product bestays: return stories where default_product='bestays' or 'bestays' in ported_to
# If --product realestate: return stories where default_product='realestate' or 'realestate' in ported_to
```

**4. Update CLI arguments:**
```bash
python story_find.py [domain] [--status STATUS] [--product PRODUCT] [--portable-only]
```

---

## task_create.py Updates

### Current Behavior
Creates task from TEMPLATE folder.

### Required Changes

**1. Add task type detection:**
```python
def create_task(story_id, task_number, semantic_name, task_type='IMPLEMENTATION'):
    # task_type: 'IMPLEMENTATION' or 'PORTING'
```

**2. Use correct template:**
```python
if task_type == 'PORTING':
    template_path = '.claude/tasks/TEMPLATE-PORTING/'
else:
    template_path = '.claude/tasks/TEMPLATE/'
```

**3. For porting tasks, require additional params:**
```python
def create_porting_task(story_id, task_number, semantic_name,
                       source_product, target_product, source_task):
    # Populate PORTING-specific STATE.json fields
```

**4. Update CLI arguments:**
```bash
# Implementation task (existing)
python task_create.py <story_id> <task_number> <semantic_name>

# Porting task (new)
python task_create.py <story_id> <task_number> <semantic_name> \
    --type PORTING \
    --source-product bestays \
    --target-product realestate \
    --source-task TASK-001
```

---

## task_list.py Updates

### Current Behavior
Lists tasks for a story.

### Required Changes

**1. Display task type:**
```python
# Output:
# TASK-001 (login-bestays): IMPLEMENTATION, IN_PROGRESS, PLANNING
# TASK-050 (port-login-realestate): PORTING, NOT_STARTED, RESEARCH
```

**2. Filter by task type:**
```python
def list_tasks(story_id, task_type=None):
    # --type IMPLEMENTATION | PORTING
```

**3. Update CLI arguments:**
```bash
python task_list.py <story_id> [--type IMPLEMENTATION|PORTING]
```

---

## context_index.py Updates (Future)

### Current Behavior
Not yet implemented (US-001D).

### Required Changes

**1. Index product metadata:**
```python
# In index JSON:
{
  "stories": {
    "US-001": {
      "default_product": "bestays",
      "portable": true,
      "ported_to": ["realestate"],
      ...
    }
  }
}
```

**2. Index porting tasks separately:**
```python
{
  "tasks": {
    "TASK-001-login-bestays": {
      "type": "IMPLEMENTATION",
      "product": "bestays",
      ...
    },
    "TASK-050-port-login-realestate": {
      "type": "PORTING",
      "source_product": "bestays",
      "target_product": "realestate",
      "source_task": "TASK-001",
      ...
    }
  }
}
```

**3. Query by product:**
```python
# Find all stories for bestays:
stories = index.find_stories(product='bestays')

# Find all porting tasks for realestate:
tasks = index.find_tasks(type='PORTING', target_product='realestate')
```

---

## story_update_ported.py (New Script)

### Purpose
Update story metadata after porting is complete.

### Implementation

```python
#!/usr/bin/env python3
"""Update story ported_to field after successful porting."""

import sys
import json
from pathlib import Path

def update_ported_to(story_id, target_product):
    """
    Update story's ported_to field.

    Args:
        story_id: Story ID (e.g., US-001)
        target_product: Product name (e.g., realestate)
    """
    # Find story file
    story_file = find_story_file(story_id)

    # Read story content
    with open(story_file) as f:
        content = f.read()

    # Parse ported_to field (current value)
    # Update to include target_product
    # Write back to file

    print(f"✅ Updated {story_id}: ported_to now includes {target_product}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python story_update_ported.py <story_id> <target_product>")
        sys.exit(1)

    update_ported_to(sys.argv[1], sys.argv[2])
```

**CLI:**
```bash
python story_update_ported.py US-001 realestate
# Updates US-001.md: ported_to: [] → ported_to: [realestate]
```

---

## Implementation Priority

**Priority 1 (Required for multi-product workflow):**
1. `story_create.py` - Add product parameter
2. `task_create.py` - Support PORTING task type
3. `story_update_ported.py` - New script for updating ported_to

**Priority 2 (Nice to have):**
4. `story_find.py` - Filter by product
5. `task_list.py` - Display task type

**Priority 3 (Future, after US-001D):**
6. `context_index.py` - Index product metadata

---

## Testing

### Test Scenarios

**Scenario 1: Create story for bestays**
```bash
python story_create.py auth login flow --product bestays
# Verify: default_product: bestays in story file
```

**Scenario 2: Create implementation task**
```bash
python task_create.py US-001 1 login-bestays
# Verify: type: IMPLEMENTATION in STATE.json
```

**Scenario 3: Create porting task**
```bash
python task_create.py US-001 50 port-login-realestate \
    --type PORTING \
    --source-product bestays \
    --target-product realestate \
    --source-task TASK-001
# Verify: type: PORTING, source_product, target_product in STATE.json
```

**Scenario 4: Update ported_to**
```bash
python story_update_ported.py US-001 realestate
# Verify: ported_to: [realestate] in story file
```

**Scenario 5: Find stories by product**
```bash
python story_find.py --product bestays
# Returns: Stories where default_product=bestays or ported_to includes bestays
```

---

## Migration Plan

### Existing Stories

**No migration needed** - Existing stories without product metadata will:
- Default to `bestays` product
- Default to `portable: true`
- Default to `ported_to: []`

Scripts should handle missing fields gracefully:
```python
def get_product(story_metadata):
    return story_metadata.get('default_product', 'bestays')
```

---

## Notes

- All script changes should maintain backward compatibility
- Scripts should validate product names (bestays, realestate)
- Porting task creation should validate source_task exists
- Update docs-stories SKILL.md after implementing changes

---

**Created By:** Coordinator
**Requires Implementation By:** dev-backend-fastapi (Python scripts)
**Estimated Effort:** 2-3 hours

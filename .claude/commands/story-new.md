---
description: Create a new user story from template
---

You are helping create a new user story for the Bestays project.

## Process

1. **Ask the user for story details:**
   - Domain (auth, booking, property, payment, admin, etc.)
   - Title (short descriptive title)
   - Type (feature, validation, bugfix, refactor, spike)
   - Priority (high, medium, low)

2. **Run the story creation script:**
   ```bash
   python3 .sdlc-workflow/scripts/story_create.py \
     --domain {domain} \
     --title "{title}" \
     --type {type} \
     --priority {priority}
   ```

3. **Open the created file** and help the user fill in:
   - Story statement (As a/I want/So that)
   - Background and context
   - Acceptance criteria
   - Technical notes
   - Testing strategy
   - Documentation requirements

4. **Explain next steps:**
   - Review and refine the story
   - Break down into tasks when ready
   - Start implementation workflow

## Story Types

- **feature**: New functionality to be built
- **validation**: Validate, document, and test existing code
- **bugfix**: Fix identified bugs or issues
- **refactor**: Improve code quality without changing behavior
- **spike**: Research or investigation task

## Tips

- Keep titles concise (2-5 words)
- Focus on user value in story statement
- Make acceptance criteria specific and testable
- Link related stories and dependencies
- Start small - first stories should be simple

## Example Usage

User: "Create a story for password reset"
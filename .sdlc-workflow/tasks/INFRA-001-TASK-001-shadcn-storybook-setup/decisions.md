# Architectural Decisions: INFRA-001-TASK-001

## Decision 1: Component Library Choice

**Context**: Need a production-ready component library for Bestays frontend that integrates with Tailwind CSS and supports Svelte 5.

**Options Considered**:
1. shadcn-svelte (Tailwind-based, copy/paste approach)
2. Skeleton UI (comprehensive Svelte component library)
3. Carbon Components Svelte (IBM design system)
4. Build custom components from scratch

**Decision**: Use shadcn-svelte

**Rationale**:
- Copy/paste approach gives full control over components
- Tailwind CSS integration (already using Tailwind CSS 4)
- Active development and Svelte 5 support
- Customizable with CSS variables
- No dependency bloat (only install what you need)
- TypeScript support out of the box

**Trade-offs**:
- ✅ Full customization control
- ✅ No runtime dependency overhead
- ✅ Easy to understand and modify
- ❌ Need to manually update components (no npm update)
- ❌ Less comprehensive than full UI libraries

---

## Decision 2: Documentation Approach

**Context**: Need component documentation system for development team and design consistency.

**Options Considered**:
1. Storybook (industry standard)
2. Histoire (Vite-native, lighter weight)
3. Custom documentation site
4. No formal documentation

**Decision**: Use Storybook

**Rationale**:
- Industry standard with broad adoption
- Excellent SvelteKit support
- Addons ecosystem (a11y, controls, docs)
- Interactive component playground
- Design system documentation
- Already planned in SDLC workflow (CLAUDE.md mentions "Using Storybook")

**Trade-offs**:
- ✅ Rich feature set
- ✅ Team familiarity
- ✅ Excellent documentation
- ❌ Heavier than alternatives
- ❌ Additional build configuration

---

## Decision 3: Component Path Structure

**Context**: Need to decide where shadcn components live vs. custom components.

**Decision**:
- shadcn components: `$lib/components/ui/`
- Custom components: `$lib/components/`
- Stories: `src/stories/`

**Rationale**:
- Follows shadcn-svelte convention
- Clear separation between library and custom components
- Easy to identify which components are shadcn vs. custom
- Stories in separate directory for organization

---

## Decision 4: Coordinator vs Implementer Workflow

**Context**: Need to respect SDLC coordinator/implementer role separation during setup.

**Decision**:
- Coordinator (main Claude) runs CLI initialization commands
- dev-frontend-svelte subagent handles all file modifications

**Rationale**:
- CLI commands (npm, npx) are bash operations (coordinator allowed)
- File modifications (Edit/Write) must go through subagent
- Maintains audit trail and context preservation
- Respects sdlc_guardian.py hook enforcement
- Ensures specialized frontend expertise applied

---

## Decision 5: Storybook Port Configuration

**Context**: Docker environment needs Storybook accessible.

**Decision**: Use port 6006 (Storybook default)

**Rationale**:
- Already exposed in Docker configuration
- Standard Storybook port
- No conflicts with existing services:
  - Frontend: 5183
  - Backend: 8011
  - PostgreSQL: 5433
  - Redis: 6379

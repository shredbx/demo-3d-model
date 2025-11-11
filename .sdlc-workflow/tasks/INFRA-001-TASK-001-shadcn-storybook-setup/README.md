# INFRA-001-TASK-001: shadcn-svelte and Storybook Setup

## Task Overview

Set up shadcn-svelte component library and Storybook for component documentation in the Bestays frontend application.

## Objectives

1. Install and configure shadcn-svelte component library
2. Initialize Storybook for SvelteKit with Svelte 5 support
3. Add essential shadcn components (Button, Badge, Card, Input, Select)
4. Update UserButton component to use shadcn Badge
5. Create component stories for documentation
6. Verify hot reload and development workflow

## Tech Stack Context

- **Frontend**: SvelteKit 2, Svelte 5 (runes), Tailwind CSS 4, TypeScript
- **Environment**: Docker with port 6006 exposed for Storybook
- **Component Library**: shadcn-svelte (Tailwind-based, customizable)
- **Documentation**: Storybook 7+ with SvelteKit support

## Implementation Phases

### Phase 1: shadcn-svelte Setup (Coordinator)

Install dependencies and initialize shadcn-svelte:

```bash
cd apps/frontend
npm install -D clsx tailwind-merge class-variance-authority
npx shadcn-svelte@latest init
npx shadcn-svelte@latest add button badge card input select
```

**Configuration**:
- TypeScript: Yes
- Global CSS: src/app.css
- CSS variables: Yes (for theming)
- Tailwind config: tailwind.config.js
- Components path: $lib/components/ui
- Utils path: $lib/utils

### Phase 2: Storybook Setup (Coordinator)

Initialize Storybook for SvelteKit:

```bash
cd apps/frontend
npx storybook@latest init --type sveltekit
```

**Requirements**:
- Support Svelte 5 and runes
- Hot reload enabled
- Tailwind CSS integration
- TypeScript support

### Phase 3: Component Integration (Subagent: dev-frontend-svelte)

Update existing components and create stories:

1. **Update UserButton.svelte**:
   - Replace current role badge with shadcn Badge component
   - Import from $lib/components/ui/badge
   - Use Badge variants for different roles

2. **Create Component Stories**:
   - UserButton.stories.ts (admin, agent, user variants)
   - Button.stories.ts (shadcn component)
   - Badge.stories.ts (shadcn component)
   - Card.stories.ts (shadcn component)

3. **Verify Configuration**:
   - .storybook/main.js supports Svelte 5
   - package.json has storybook scripts
   - Hot reload works

## Files to Create/Modify

**Coordinator (Initialization)**:
- apps/frontend/package.json (dependencies)
- apps/frontend/components.json (shadcn config - auto-generated)
- apps/frontend/src/lib/utils/cn.ts (class utility - auto-generated)
- apps/frontend/src/lib/components/ui/* (shadcn components - auto-generated)
- apps/frontend/.storybook/* (Storybook config - auto-generated)

**Subagent (Customization)**:
- apps/frontend/src/lib/components/UserButton.svelte (update)
- apps/frontend/src/stories/UserButton.stories.ts (create)
- apps/frontend/src/stories/Button.stories.ts (create)
- apps/frontend/src/stories/Badge.stories.ts (create)
- apps/frontend/src/stories/Card.stories.ts (create)
- apps/frontend/.storybook/main.js (verify/update)
- apps/frontend/.storybook/preview.js (verify/update)
- apps/frontend/package.json (scripts - verify/update)

## Acceptance Criteria

- [ ] shadcn-svelte components install without errors
- [ ] UserButton uses shadcn Badge for role indicators
- [ ] Storybook starts on port 6006 (`npm run storybook`)
- [ ] At least 4 component stories are visible in Storybook
- [ ] Hot reload works for story changes
- [ ] TypeScript types are correct (no errors)
- [ ] Tailwind CSS styling works in Storybook

## Skills Required

- frontend-svelte (Svelte 5 patterns with runes)
- frontend-typescript (TypeScript typing)
- frontend-tailwind (Tailwind CSS styling)
- frontend-storyboard-artist (Storybook best practices)

## Notes

- shadcn-svelte components are customizable (copy/paste approach)
- Components use Tailwind CSS with CSS variables for theming
- Storybook should support Svelte 5 runes syntax
- Docker environment already configured for port 6006

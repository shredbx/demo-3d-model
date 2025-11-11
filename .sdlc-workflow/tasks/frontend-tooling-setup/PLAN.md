# Frontend Tooling Setup Plan

## Overview
Set up shadcn-svelte and Storybook for efficient component development and documentation in the Bestays frontend.

## Objectives
1. Install and configure shadcn-svelte for pre-built UI components
2. Set up Storybook for component isolation and documentation
3. Ensure Docker environment supports both tools with hot reload
4. Create foundation for component-driven development

## Tech Stack Confirmation
- **Existing**: SvelteKit 2, Svelte 5 (runes), Tailwind CSS 4, TypeScript
- **Adding**: shadcn-svelte (UI components), Storybook (component documentation)

## Implementation Phases

### Phase 1: Environment Preparation (DevOps Agent)
**Agent**: devops-infra
**Priority**: Critical (blocking)

#### Tasks:
1. **Docker Configuration Updates**
   - Add Storybook port exposure (6006:6006) to docker-compose.yml
   - Ensure volume mounts include Storybook config directories
   - Verify hot reload configuration for both dev servers

2. **Makefile Commands**
   ```makefile
   storybook:       ## Run Storybook in development mode
       docker exec -it bestays-frontend-dev npm run storybook

   storybook-build: ## Build Storybook for production
       docker exec -it bestays-frontend-dev npm run build-storybook
   ```

3. **Network Configuration**
   - Ensure Storybook port doesn't conflict with existing services
   - Add to service documentation

### Phase 2: shadcn-svelte Setup (Frontend Agent)
**Agent**: dev-frontend-svelte
**Priority**: High

#### Tasks:
1. **Installation**
   ```bash
   npm install -D clsx tailwind-merge class-variance-authority
   npx shadcn-svelte@latest init
   ```

2. **Configuration**
   - Path aliases in svelte.config.js
   - Component directory: `$lib/components/ui/`
   - CSS variables in app.css
   - cn() utility function setup

3. **Initial Components**
   Priority components for RBAC UI:
   - Button (primary, secondary, destructive variants)
   - Badge (for role indicators)
   - Card (for property listings)
   - Input, Select (for forms)
   - Dialog/Modal (for interactions)

4. **Integration**
   - Update UserButton.svelte to use shadcn Badge
   - Create example usage patterns

### Phase 3: Storybook Configuration (Frontend Agent)
**Agent**: dev-frontend-svelte
**Priority**: Medium

#### Tasks:
1. **Installation**
   ```bash
   npx storybook@latest init --type sveltekit
   ```

2. **Svelte 5 Configuration**
   - Configure for runes support
   - Set up Vite configuration
   - CSF 3.0 story format

3. **Initial Stories**
   - UserButton.stories.ts (with role variants)
   - shadcn component stories
   - Form component examples

4. **Addons**
   - @storybook/addon-essentials (controls, actions)
   - @storybook/addon-a11y (accessibility testing)
   - @storybook/addon-svelte-csf (if needed)

### Phase 4: Validation
**Coordinator**: Main Claude
**Priority**: Required

#### Success Criteria:
- [ ] shadcn-svelte components import and render correctly
- [ ] Storybook runs on http://localhost:6006
- [ ] Hot reload works for both dev server and Storybook
- [ ] UserButton displays with shadcn Badge for roles
- [ ] At least 5 components documented in Storybook
- [ ] No TypeScript errors
- [ ] Docker logs show both servers running

## Risk Mitigation

### Potential Issues:
1. **Svelte 5 Compatibility**
   - Solution: Use latest shadcn-svelte version
   - Fallback: Manual component adaptation

2. **Tailwind CSS 4**
   - Solution: Verify PostCSS configuration
   - Fallback: Adjust component styles if needed

3. **Docker Hot Reload**
   - Solution: Use polling if inotify doesn't work
   - Fallback: Manual restart commands

4. **Port Conflicts**
   - Solution: Check all services before assignment
   - Fallback: Use alternative port (6007)

## File Structure After Setup

```
apps/frontend/
├── src/
│   ├── lib/
│   │   ├── components/
│   │   │   ├── ui/           # shadcn components
│   │   │   │   ├── button/
│   │   │   │   ├── badge/
│   │   │   │   ├── card/
│   │   │   │   └── ...
│   │   │   └── UserButton.svelte (updated)
│   │   └── utils/
│   │       └── cn.ts         # Class name utility
│   └── app.css              # With CSS variables
├── .storybook/
│   ├── main.js              # Storybook configuration
│   └── preview.js           # Global decorators
├── stories/
│   ├── UserButton.stories.ts
│   └── ui/
│       ├── Button.stories.ts
│       └── Badge.stories.ts
└── components.json          # shadcn configuration

docker-compose.yml (updated with port 6006)
Makefile (updated with storybook commands)
```

## Timeline
- Phase 1 (DevOps): 30 minutes
- Phase 2 (shadcn): 45 minutes
- Phase 3 (Storybook): 45 minutes
- Phase 4 (Validation): 15 minutes
- **Total**: ~2.5 hours

## Next Steps After Completion
1. Continue with RBAC implementation (TASK-003 through TASK-006)
2. Use shadcn components for RBAC UI elements
3. Document all RBAC components in Storybook
4. Create component development guidelines

## Commands Cheat Sheet
```bash
# Development
make dev              # Start all services
make storybook        # Run Storybook

# Component Management
npx shadcn-svelte@latest add [component]  # Add new component
npm run storybook                          # Start Storybook
npm run build-storybook                    # Build static Storybook

# Container Access
make shell-frontend   # Access frontend container
```

## Documentation References
- [shadcn-svelte](https://www.shadcn-svelte.com/)
- [Storybook for SvelteKit](https://storybook.js.org/docs/get-started/frameworks/sveltekit)
- [Svelte 5 Runes](https://svelte.dev/docs/svelte/runes)

---

**Status**: Ready for Implementation
**Created**: 2025-11-07
**Updated**: 2025-11-07
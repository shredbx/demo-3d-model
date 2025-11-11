# Subagent Specification: Component Integration

**Subagent**: dev-frontend-svelte
**Task**: INFRA-001-TASK-001
**Phase**: Component Integration & Story Creation

---

## Objective

Update UserButton component to use shadcn Badge and create comprehensive Storybook stories for UserButton and shadcn UI components.

---

## Current State

### shadcn-svelte Setup (COMPLETED)
- ✅ Dependencies installed (clsx, tailwind-merge, class-variance-authority)
- ✅ shadcn-svelte initialized with config:
  - Base color: neutral
  - CSS: src/app.css
  - Components: $lib/components/ui
  - Utils: $lib/utils
- ✅ Components installed:
  - button
  - badge
  - card
  - input
  - select
  - separator (bonus)

### Storybook Setup (COMPLETED)
- ✅ Storybook 10.0.5 initialized for SvelteKit
- ✅ Configuration created (.storybook/main.ts, .storybook/preview.ts)
- ✅ Example stories created (Button, Header, Page)
- ✅ Scripts added to package.json:
  - `npm run storybook` (dev on port 6006)
  - `npm run build-storybook` (build)
- ✅ Addons installed:
  - addon-svelte-csf
  - addon-docs
  - addon-a11y
  - addon-vitest

---

## Tasks for Subagent

### Task 1: Update UserButton.svelte to Use shadcn Badge

**File**: `/Users/solo/Projects/_repos/bestays/apps/frontend/src/lib/components/UserButton.svelte`

**Current Implementation** (lines 72-84):
```svelte
<p class="text-xs flex items-center gap-2">
  {#if authStore.user.role === 'admin'}
    <span class="px-2 py-0.5 text-xs font-medium rounded-full bg-red-500 text-white">
      Admin
    </span>
  {:else if authStore.user.role === 'agent'}
    <span class="px-2 py-0.5 text-xs font-medium rounded-full bg-blue-500 text-white">
      Agent
    </span>
  {:else}
    <span class="text-gray-600 capitalize">{authStore.user.role}</span>
  {/if}
</p>
```

**Required Changes**:

1. **Import shadcn Badge**:
   ```svelte
   import { Badge } from '$lib/components/ui/badge';
   ```

2. **Replace role indicators** with Badge component:
   ```svelte
   <p class="text-xs flex items-center gap-2">
     {#if authStore.user.role === 'admin'}
       <Badge variant="destructive">Admin</Badge>
     {:else if authStore.user.role === 'agent'}
       <Badge variant="default">Agent</Badge>
     {:else}
       <Badge variant="secondary" class="capitalize">{authStore.user.role}</Badge>
     {/if}
   </p>
   ```

3. **Check Badge variants**: Review `/Users/solo/Projects/_repos/bestays/apps/frontend/src/lib/components/ui/badge/index.ts` and choose appropriate variants:
   - `destructive` (red) for admin
   - `default` (primary) for agent
   - `secondary` (neutral) for regular users

4. **Preserve existing functionality**:
   - Keep all file header comments
   - Maintain Clerk integration
   - Keep loading states
   - Keep responsive visibility (hidden md:block)

---

### Task 2: Create UserButton Stories

**File**: `/Users/solo/Projects/_repos/bestays/apps/frontend/src/stories/UserButton.stories.svelte` (CREATE NEW)

**Requirements**:

1. **Story Structure** (Svelte CSF format):
   ```svelte
   <script context="module">
     import { defineMeta } from '@storybook/addon-svelte-csf';
     import UserButton from '$lib/components/UserButton.svelte';

     const { Story } = defineMeta({
       title: 'Components/UserButton',
       component: UserButton,
       tags: ['autodocs'],
     });
   </script>

   <Story name="Admin User">
     <!-- Story implementation -->
   </Story>

   <Story name="Agent User">
     <!-- Story implementation -->
   </Story>

   <Story name="Regular User">
     <!-- Story implementation -->
   </Story>
   ```

2. **Story Variants**:
   - **Admin User**: Show UserButton with role="admin", destructive badge
   - **Agent User**: Show UserButton with role="agent", default badge
   - **Regular User**: Show UserButton with role="user", secondary badge
   - **Loading State**: Show UserButton before Clerk mounts (loading placeholder)

3. **Mock Data**:
   Since UserButton depends on `authStore` and `clerk`, you'll need to mock these:
   - Create a wrapper component or use Storybook decorators
   - Mock `authStore.user` with appropriate data
   - Mock `clerk.user` and `clerk.mountUserButton`

4. **Example Mock** (simplified approach):
   ```svelte
   <!-- Option A: Create a simplified demo version for Storybook -->
   <!-- Option B: Use actual component with mocked dependencies -->
   ```

**Guidance**: If mocking Clerk SDK is complex, create a simplified UserButton demo component specifically for Storybook that shows the visual states without Clerk integration. Focus on demonstrating the Badge variants and layout.

---

### Task 3: Create shadcn Component Stories

Create story files for the installed shadcn components to document their usage.

#### 3a. Badge Stories

**File**: `/Users/solo/Projects/_repos/bestays/apps/frontend/src/stories/Badge.stories.svelte` (CREATE NEW)

**Variants to Show**:
- Default
- Secondary
- Destructive
- Outline

**Example Structure**:
```svelte
<script context="module">
  import { defineMeta } from '@storybook/addon-svelte-csf';
  import { Badge } from '$lib/components/ui/badge';

  const { Story } = defineMeta({
    title: 'UI/Badge',
    component: Badge,
    tags: ['autodocs'],
  });
</script>

<Story name="Default">
  <Badge>Default Badge</Badge>
</Story>

<Story name="Secondary">
  <Badge variant="secondary">Secondary Badge</Badge>
</Story>

<Story name="Destructive">
  <Badge variant="destructive">Destructive Badge</Badge>
</Story>

<Story name="Outline">
  <Badge variant="outline">Outline Badge</Badge>
</Story>

<Story name="All Variants">
  <div class="flex gap-2 flex-wrap">
    <Badge>Default</Badge>
    <Badge variant="secondary">Secondary</Badge>
    <Badge variant="destructive">Destructive</Badge>
    <Badge variant="outline">Outline</Badge>
  </div>
</Story>
```

---

#### 3b. Button Stories

**File**: `/Users/solo/Projects/_repos/bestays/apps/frontend/src/stories/ShadcnButton.stories.svelte` (CREATE NEW)

Note: Storybook already created a Button.stories.svelte example. Create a new one for the shadcn Button component specifically.

**Variants to Show**:
- Default
- Secondary
- Destructive
- Outline
- Ghost
- Link
- Sizes (default, sm, lg, icon)

---

#### 3c. Card Stories

**File**: `/Users/solo/Projects/_repos/bestays/apps/frontend/src/stories/Card.stories.svelte` (CREATE NEW)

**Variants to Show**:
- Basic Card with Header, Content, Footer
- Card with Title and Description
- Nested Cards
- Card with custom styling

---

### Task 4: Verify Storybook Configuration

**File**: `/Users/solo/Projects/_repos/bestays/apps/frontend/.storybook/main.ts`

**Current Config**:
```typescript
{
  "stories": [
    "../src/**/*.mdx",
    "../src/**/*.stories.@(js|ts|svelte)"
  ],
  "framework": {
    "name": "@storybook/sveltekit",
    "options": {}
  }
}
```

**Verification**:
1. ✅ Config supports `.svelte` story files
2. ✅ Framework is `@storybook/sveltekit` (Svelte 5 compatible)
3. Check if any Svelte 5 specific config needed (usually automatic with SvelteKit adapter)

**If Needed**: Add Svelte 5 runes support (usually automatic, but verify)

---

### Task 5: Update .storybook/preview.ts for Tailwind

**File**: `/Users/solo/Projects/_repos/bestays/apps/frontend/.storybook/preview.ts`

**Ensure Tailwind CSS is imported**:
```typescript
import '../src/app.css'; // Global CSS with Tailwind
```

**Add theme configuration** (optional but recommended):
```typescript
export const parameters = {
  backgrounds: {
    default: 'light',
    values: [
      { name: 'light', value: '#ffffff' },
      { name: 'dark', value: '#1a1a1a' },
    ],
  },
  controls: {
    matchers: {
      color: /(background|color)$/i,
      date: /Date$/,
    },
  },
};
```

---

## Technical Requirements

### Svelte 5 Compatibility
- Use `$state`, `$derived`, `$effect` runes where appropriate
- All stories must work with Svelte 5 syntax
- No deprecated Svelte 4 patterns

### TypeScript
- All files should be TypeScript compatible
- Import types correctly from shadcn components
- Use proper Svelte component types

### Tailwind CSS
- All styling uses Tailwind classes
- shadcn components already use Tailwind internally
- Ensure app.css is loaded in Storybook preview

### Storybook Best Practices
- Use Svelte CSF format (not MDX for Svelte)
- Include `tags: ['autodocs']` for automatic documentation
- Group stories logically:
  - `Components/UserButton` (project components)
  - `UI/Badge`, `UI/Button`, `UI/Card` (shadcn components)

---

## Acceptance Criteria

- [ ] UserButton.svelte uses shadcn Badge component
- [ ] Badge variants correctly applied (destructive for admin, default for agent, secondary for user)
- [ ] UserButton stories created with all role variants
- [ ] Badge stories created showing all variants
- [ ] Button stories created for shadcn Button
- [ ] Card stories created for shadcn Card
- [ ] .storybook/preview.ts imports Tailwind CSS
- [ ] All stories visible in Storybook
- [ ] No TypeScript errors
- [ ] No Svelte compilation errors
- [ ] Hot reload works for story changes

---

## Files to Modify/Create

**Modify**:
1. `/Users/solo/Projects/_repos/bestays/apps/frontend/src/lib/components/UserButton.svelte`
2. `/Users/solo/Projects/_repos/bestays/apps/frontend/.storybook/preview.ts`

**Create**:
1. `/Users/solo/Projects/_repos/bestays/apps/frontend/src/stories/UserButton.stories.svelte`
2. `/Users/solo/Projects/_repos/bestays/apps/frontend/src/stories/Badge.stories.svelte`
3. `/Users/solo/Projects/_repos/bestays/apps/frontend/src/stories/ShadcnButton.stories.svelte`
4. `/Users/solo/Projects/_repos/bestays/apps/frontend/src/stories/Card.stories.svelte`

---

## Skills to Use

- `frontend-svelte` - Svelte 5 patterns with runes
- `frontend-typescript` - TypeScript typing
- `frontend-tailwind` - Tailwind CSS styling
- `frontend-storyboard-artist` - Storybook best practices

---

## Notes for Subagent

1. **shadcn Badge component** is located at `$lib/components/ui/badge` - check the actual structure before importing
2. **Clerk mocking** for UserButton stories - if too complex, create a simplified demo component
3. **Story format** - Use Svelte CSF (defineMeta) not MDX, as recommended for Svelte components
4. **File headers** - Preserve all architecture documentation comments in UserButton.svelte
5. **Testing** - After creating stories, verify they render without errors (Storybook will be run separately)

---

## Reference Files

**Check these for implementation details**:
- `/Users/solo/Projects/_repos/bestays/apps/frontend/src/lib/components/ui/badge/index.ts` - Badge component API
- `/Users/solo/Projects/_repos/bestays/apps/frontend/src/lib/components/ui/button/index.ts` - Button component API
- `/Users/solo/Projects/_repos/bestays/apps/frontend/src/lib/components/ui/card/index.ts` - Card component API
- `/Users/solo/Projects/_repos/bestays/apps/frontend/src/stories/Button.stories.svelte` - Example story format
- `/Users/solo/Projects/_repos/bestays/apps/frontend/.storybook/main.ts` - Storybook config

---

## Deliverable

Complete implementation report documenting:
1. Changes made to UserButton.svelte
2. Story files created
3. Any issues encountered
4. Verification that stories work

Report should be saved to:
`/Users/solo/Projects/_repos/bestays/.sdlc-workflow/tasks/INFRA-001-TASK-001-shadcn-storybook-setup/subagent-reports/frontend-report.md`

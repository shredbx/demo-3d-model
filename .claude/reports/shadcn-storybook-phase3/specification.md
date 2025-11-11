# Phase 3: shadcn-svelte and Storybook Integration

**Date:** 2025-11-07
**Subagent:** dev-frontend-svelte
**Type:** Infrastructure enhancement (Storybook integration)

---

## Context

Phase 1 & 2 of shadcn-svelte installation are complete. Components are available in `$lib/components/ui/`. This phase completes the integration by:
1. Updating existing components to use shadcn
2. Fixing Storybook configuration
3. Creating comprehensive component stories

---

## Task 1: Update UserButton.svelte

**File:** `apps/frontend/src/lib/components/UserButton.svelte`

**Current implementation (lines 72-84):**
```svelte
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
```

**Required changes:**

1. Add Badge import at top of script section:
```svelte
import { Badge } from '$lib/components/ui/badge';
```

2. Replace role indicator section with Badge components:
```svelte
{#if authStore.user.role === 'admin'}
  <Badge variant="destructive">Admin</Badge>
{:else if authStore.user.role === 'agent'}
  <Badge variant="default">Agent</Badge>
{:else}
  <Badge variant="secondary">{authStore.user.role}</Badge>
{/if}
```

**Badge variants mapping:**
- Admin → `variant="destructive"` (red)
- Agent → `variant="default"` (primary blue)
- User → `variant="secondary"` (neutral gray)

**Important:** Keep all existing functionality intact (Clerk integration, loading states, onMount/onDestroy logic).

---

## Task 2: Fix Storybook Preview

**File:** `apps/frontend/.storybook/preview.ts`

**Required change:**
Add Tailwind CSS import at the very top of the file (line 1):
```typescript
import '../src/app.css';
```

**Current file:**
```typescript
import type { Preview } from '@storybook/sveltekit'

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
       color: /(background|color)$/i,
       date: /Date$/i,
      },
    },
  },
};

export default preview;
```

**After:**
```typescript
import '../src/app.css';
import type { Preview } from '@storybook/sveltekit'

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
       color: /(background|color)$/i,
       date: /Date$/i,
      },
    },
  },
};

export default preview;
```

**Purpose:** Ensures Tailwind styles are available in Storybook stories.

---

## Task 3: Create Component Stories

Create the following story files in `apps/frontend/src/stories/`:

### 3.1 UserButton.stories.ts

**File:** `apps/frontend/src/stories/UserButton.stories.ts`

**Requirements:**
- Title: `'Components/UserButton'`
- Stories: Admin, Agent, User, Loading
- Mock authStore properly for each variant
- Show Clerk integration (note: may need mocking strategy)

**Example structure:**
```typescript
import type { Meta, StoryObj } from '@storybook/svelte';
import UserButton from '$lib/components/UserButton.svelte';

const meta = {
  title: 'Components/UserButton',
  component: UserButton,
  tags: ['autodocs'],
} satisfies Meta<UserButton>;

export default meta;
type Story = StoryObj<typeof meta>;

// Note: Will need to mock authStore and clerk
export const Admin: Story = {
  // Implementation with mocked admin user
};

export const Agent: Story = {
  // Implementation with mocked agent user
};

export const User: Story = {
  // Implementation with mocked regular user
};

export const Loading: Story = {
  // Implementation showing loading state
};
```

### 3.2 Badge.stories.ts

**File:** `apps/frontend/src/stories/Badge.stories.ts`

**Requirements:**
- Title: `'UI/Badge'`
- Show all variants: default, secondary, destructive, outline
- Use proper argTypes for variant selection
- Include examples with different content

**Example:**
```typescript
import type { Meta, StoryObj } from '@storybook/svelte';
import Badge from '$lib/components/ui/badge/badge.svelte';

const meta = {
  title: 'UI/Badge',
  component: Badge,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['default', 'secondary', 'destructive', 'outline']
    }
  }
} satisfies Meta<Badge>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    variant: 'default',
  },
  render: (args) => ({
    Component: Badge,
    props: args,
    // Need to pass children
  })
};

export const Secondary: Story = {
  args: {
    variant: 'secondary',
  }
};

export const Destructive: Story = {
  args: {
    variant: 'destructive',
  }
};

export const Outline: Story = {
  args: {
    variant: 'outline',
  }
};
```

**Note:** Badge uses snippet children pattern (`{@render children?.()}`), so stories need proper children rendering.

### 3.3 ShadcnButton.stories.ts

**File:** `apps/frontend/src/stories/ShadcnButton.stories.ts`

**Requirements:**
- Title: `'UI/Button'`
- Show all variants: default, destructive, outline, secondary, ghost, link
- Show all sizes: default, sm, lg, icon, icon-sm, icon-lg
- Include disabled state example
- Demonstrate both button and link (href) modes

**Button component info:**
- Path: `$lib/components/ui/button/button.svelte`
- Variants: default, destructive, outline, secondary, ghost, link
- Sizes: default, sm, lg, icon, icon-sm, icon-lg
- Props: variant, size, href (optional), disabled, type

### 3.4 Card.stories.ts

**File:** `apps/frontend/src/stories/Card.stories.ts`

**Requirements:**
- Title: `'UI/Card'`
- Show basic card example
- Show card with header and footer
- Show card with all parts (header, title, description, content, footer, action)

**Card components:**
- `Card` (main container)
- `CardHeader`
- `CardTitle`
- `CardDescription`
- `CardContent`
- `CardFooter`
- `CardAction`

**Example composition:**
```svelte
<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card description</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Card content goes here</p>
  </CardContent>
  <CardFooter>
    <p>Footer content</p>
  </CardFooter>
</Card>
```

---

## Task 4: Validation

After completing all changes, run the following:

1. **TypeScript check:**
```bash
cd apps/frontend && npm run check
```

2. **Storybook dev server (manual test):**
```bash
cd apps/frontend && npm run storybook
```
- Verify stories load without errors
- Verify Tailwind styles are applied
- Check all component variants render correctly

3. **Visual verification:**
- UserButton displays Badge components correctly
- Badge variants match expected colors
- Button variants and sizes work
- Card composition displays properly

---

## Expected Files Modified/Created

**Modified:**
1. `apps/frontend/src/lib/components/UserButton.svelte` (Badge integration)
2. `apps/frontend/.storybook/preview.ts` (Tailwind import)

**Created:**
1. `apps/frontend/src/stories/UserButton.stories.ts`
2. `apps/frontend/src/stories/Badge.stories.ts`
3. `apps/frontend/src/stories/ShadcnButton.stories.ts`
4. `apps/frontend/src/stories/Card.stories.ts`

---

## Technical Notes

### Svelte 5 Patterns

- Use `$props()` for component props
- Badge and Button use snippet children pattern: `{@render children?.()}`
- Stories need to handle snippet rendering properly

### shadcn-svelte Components

All components use `tailwind-variants` for styling:
- Badge: `badgeVariants`
- Button: `buttonVariants`
- Variants are type-safe exports from components

### Storybook Svelte 5 Compatibility

Story structure for Svelte 5 components:
```typescript
export const StoryName: Story = {
  args: {
    // Component props
  },
  render: (args) => ({
    Component: MyComponent,
    props: args,
    // May need slots/snippets handling
  })
};
```

---

## Success Criteria

- ✅ UserButton uses Badge component (no custom spans)
- ✅ Storybook shows Tailwind styles correctly
- ✅ All 4 story files created and functional
- ✅ `npm run check` passes with no errors
- ✅ Stories demonstrate all component variants
- ✅ Components are properly documented in Storybook

---

## References

- shadcn-svelte components: `apps/frontend/src/lib/components/ui/`
- Badge component: `apps/frontend/src/lib/components/ui/badge/badge.svelte`
- Button component: `apps/frontend/src/lib/components/ui/button/button.svelte`
- Card components: `apps/frontend/src/lib/components/ui/card/`
- Existing UserButton: `apps/frontend/src/lib/components/UserButton.svelte`
- Storybook config: `apps/frontend/.storybook/`

# TASK-003: Add Role Indicator Badges to UserButton

**Story:** US-001 - Login Flow Validation
**Status:** IN_PROGRESS
**Created:** 2025-11-06
**Assigned Subagent:** dev-frontend-svelte

## Objective

Add visual role indicator badges to the UserButton component for RBAC testing purposes. Replace the current colored dot indicators with prominent badge pills for admin and agent roles.

## Context

We're implementing RBAC (Role-Based Access Control) and need a visual indicator to show which role is currently logged in during testing. The user avatar with dropdown is located at the top of the screen.

Current implementation shows roles with colored dots (admin: blue, agent: green, user: gray). We need to make this more prominent for testing.

## Files to Modify

- `apps/frontend/src/lib/components/UserButton.svelte` (lines 72-81)

## Implementation Specification

### Current Code (lines 72-81)
```svelte
<p class="text-xs text-gray-600 capitalize">
  {authStore.user.role}
  {#if authStore.user.role === 'admin'}
    <span class="text-blue-600">•</span>
  {:else if authStore.user.role === 'agent'}
    <span class="text-green-600">•</span>
  {:else}
    <span class="text-gray-600">•</span>
  {/if}
</p>
```

### Replacement Code
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

### Visual Design
- **Admin:** Red badge pill with white text (`bg-red-500 text-white`)
- **Agent:** Blue badge pill with white text (`bg-blue-500 text-white`)
- **Regular users:** Plain text (no badge, clean UI)

## Testing Requirements

Test with these Clerk test accounts:
- Admin: `admin.claudecode@bestays.app` → Should see red "Admin" badge
- Agent: `agent.claudecode@bestays.app` → Should see blue "Agent" badge
- User: `user.claudecode@bestays.app` → Should see plain text (no badge)

## Acceptance Criteria

- [ ] UserButton component updated with badge pills
- [ ] Admin role shows red "Admin" badge
- [ ] Agent role shows blue "Agent" badge
- [ ] Regular user role shows plain text (no badge)
- [ ] TypeScript types are correct
- [ ] Clerk dropdown still functions properly
- [ ] Visual appearance is clean and professional
- [ ] Tested with all three test accounts

## Skills Required

- `frontend-svelte` - Svelte 5 patterns
- `frontend-tailwind` - Tailwind CSS styling
- Follow existing component patterns in UserButton.svelte

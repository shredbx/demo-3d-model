# Implementation Guide: Role Indicator Badges

**Task:** RBAC-BADGE-001
**File:** `/Users/solo/Projects/_repos/bestays/apps/frontend/src/lib/components/UserButton.svelte`

## Change Summary

Replace the current role indicator (colored dots) with prominent badge pills for admin and agent roles.

## Exact Code Changes

### Location
File: `apps/frontend/src/lib/components/UserButton.svelte`
Lines: 72-81

### Current Code (TO REPLACE)
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

### New Code (REPLACEMENT)
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

## Changes Explained

1. **Container:** Changed to `flex items-center gap-2` for proper badge alignment
2. **Admin Badge:** Red pill background (`bg-red-500`), white text, "Admin" label
3. **Agent Badge:** Blue pill background (`bg-blue-500`), white text, "Agent" label
4. **User Role:** Plain gray text (no badge), maintains capitalize
5. **Styling:** Uses existing Tailwind utilities, no new CSS needed

## Testing Checklist

### Test Accounts
```
Admin: admin.claudecode@bestays.app / rHe/997?lo&l
Agent: agent.claudecode@bestays.app / y>1T;)5s!X1X
User:  user.claudecode@bestays.app / 9kB*k926O8):
```

### Visual Testing
- [ ] Login as admin → See red "Admin" badge
- [ ] Login as agent → See blue "Agent" badge
- [ ] Login as user → See gray "user" text (no badge)
- [ ] Desktop view (≥768px) → Badge visible
- [ ] Mobile view (<768px) → User info hidden (existing behavior)
- [ ] Clerk dropdown menu still opens
- [ ] Logout still works

### TypeScript Check
```bash
cd apps/frontend
npm run check
```

### Browser Testing
- [ ] Chrome: Badges display correctly
- [ ] Firefox: Badges display correctly
- [ ] Safari: Badges display correctly

## Expected Visual Result

**Admin User:**
```
john@example.com
[Admin] ← Red pill badge with white text
```

**Agent User:**
```
jane@example.com
[Agent] ← Blue pill badge with white text
```

**Regular User:**
```
user@example.com
user ← Plain gray text
```

## Rollback Instructions

If issues occur, revert to original code:
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

## No Dependencies Changed

- No new packages required
- No TypeScript types modified
- No props changed
- No component API changes
- Uses existing Tailwind classes

## Estimated Time

- Implementation: 2 minutes
- Testing: 5 minutes
- Total: ~7 minutes

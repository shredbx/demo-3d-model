# Task: Add Role Indicator Badges to UserButton

**Task ID:** RBAC-BADGE-001
**Created:** 2025-11-06
**Status:** IN_PROGRESS
**Story:** N/A (Standalone RBAC testing enhancement)

## Objective

Add visual role indicator badges to the UserButton component for easier RBAC testing.

## Context

Currently, the UserButton shows role information with small colored dots. For RBAC testing purposes, we need more prominent visual indicators that clearly show which role is logged in (admin, agent, or user).

## Files to Modify

- `/Users/solo/Projects/_repos/bestays/apps/frontend/src/lib/components/UserButton.svelte`

## Implementation Specification

### Current Implementation (lines 72-81)

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

### New Implementation

Replace with colored badge pills:

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

## Visual Design

- **Admin Badge:** Red background (`bg-red-500`), white text, rounded pill
- **Agent Badge:** Blue background (`bg-blue-500`), white text, rounded pill
- **User Role:** Plain gray text, no badge (keeps UI clean)
- **Size:** Small (`text-xs`, `px-2 py-0.5`)
- **Responsive:** Maintains existing `hidden md:block` on parent div

## Acceptance Criteria

1. ✅ Admin users see red "Admin" badge
2. ✅ Agent users see blue "Agent" badge
3. ✅ Regular users see plain "user" text (no badge)
4. ✅ Badge is visible on desktop (hidden on mobile per existing design)
5. ✅ Clerk UserButton continues to function correctly
6. ✅ No TypeScript errors
7. ✅ No visual regressions

## Testing Instructions

**Test Accounts:**

- Admin: `admin.claudecode@bestays.app` / `rHe/997?lo&l`
- Agent: `agent.claudecode@bestays.app` / `y>1T;)5s!X1X`
- User: `user.claudecode@bestays.app` / `9kB*k926O8):`

**Test Steps:**

1. Login as admin → Verify red "Admin" badge appears
2. Login as agent → Verify blue "Agent" badge appears
3. Login as user → Verify plain "user" text (no badge)
4. Test on desktop (should show badge/text)
5. Test on mobile (<768px, should be hidden per existing design)
6. Verify Clerk dropdown still works
7. Verify logout still works

## Subagent

**Assigned to:** frontend-svelte
**Reason:** Svelte component modification with Tailwind styling

## Technical Notes

- Uses existing Tailwind utility classes (no new CSS needed)
- Maintains existing responsive design (parent has `hidden md:block`)
- No changes to component logic, only visual presentation
- No props changed, no API modifications

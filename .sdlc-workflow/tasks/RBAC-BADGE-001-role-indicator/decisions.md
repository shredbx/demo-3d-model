# Decisions: RBAC-BADGE-001

## Decision 1: Badge vs Overlay Approach

**Date:** 2025-11-06
**Decision:** Enhance existing user info section with badges (not overlay on Clerk avatar)

**Options Considered:**
1. Badge overlay on Clerk UserButton avatar
2. Badge in existing user info section (chosen)
3. Tooltip on hover

**Rationale:**
- Clerk UserButton is SDK-mounted, cannot easily overlay without complex positioning
- Existing user info section already shows role information (lines 72-81)
- Simpler to enhance existing UI than create new overlay
- Maintains separation of concerns (Clerk handles avatar, we handle role display)

**Trade-offs:**
- ✅ Simpler implementation
- ✅ No interference with Clerk SDK
- ✅ Maintains existing responsive design
- ⚠️ Badge not directly on avatar (but still clearly visible)

## Decision 2: Color Scheme

**Date:** 2025-11-06
**Decision:** Red for admin, blue for agent

**Rationale:**
- Red is more attention-grabbing (good for testing admin role)
- Blue consistent with brand color
- Clear visual distinction between roles
- Plain text for regular users keeps UI clean

**Colors:**
- Admin: `bg-red-500` (red)
- Agent: `bg-blue-500` (blue)
- User: Gray text, no badge

## Decision 3: When to Show Badge

**Date:** 2025-11-06
**Decision:** Only show badges for admin and agent, plain text for regular users

**Rationale:**
- Admin and agent need clear visual indicators for testing
- Regular users don't need prominent role display (reduces visual noise)
- Keeps UI clean and professional for end users

# Multi-Product Architecture Decision

**Date:** 2025-11-08
**Story:** US-018 (White-Label Multi-Product Architecture)
**Status:** ARCHITECTURE DECIDED
**Decision:** Single Application, Dual Instance (Option A)

---

## Executive Summary

**Decision:** Use current "one application, two Docker instances" architecture instead of implementing a true monorepo with separate apps and shared packages.

**Rationale:**
- ✅ Current implementation is working (separate databases, separate Clerk instances)
- ✅ Allows immediate progress on features (Login, Homepage, Properties)
- ✅ Simpler to understand and maintain during MVP phase
- ✅ Monorepo refactor can happen later with real code to extract

**Impact:**
- US-018 marked as **COMPLETE** (infrastructure objectives achieved)
- TASK-003, 004, 005 (monorepo planning) preserved as reference documentation
- Move forward to **US-012 (Login)** following full SDLC workflow

---

## Architecture Overview

### Current Implementation (Keeping This)

```
apps/server/     ← Single FastAPI codebase
apps/frontend/   ← Single SvelteKit codebase

Docker Compose runs TWICE:
├── bestays-server (container) + bestays-frontend (container)
│   └── Configured via .env.bestays
└── realestate-server (container) + realestate-frontend (container)
    └── Configured via .env.realestate
```

**Key Principle:** **One codebase, two configurations, two instances**

---

## Product Configuration

### ✅ Already Configured (Verified)

**Bestays (.env.bestays):**
- Database: `bestays_dev` (separate)
- Clerk: `sacred-mayfly-55` (separate instance)
- Ports: Frontend 5183, Backend 8011
- Theme: `PRIMARY_COLOR=#FF6B6B` (red/pink)
- Product Name: "Bestays"

**Real Estate (.env.realestate):**
- Database: `realestate_dev` (separate)
- Clerk: `pleasant-gnu-25` (separate instance)
- Ports: Frontend 5184, Backend 8012
- Theme: `PRIMARY_COLOR=#4ECDC4` (teal/turquoise)
- Product Name: "Best Real Estate"

---

## Infrastructure Sharing Rules

### ✅ Stateless Services (Shared - OK)

**These services can be shared because they don't store product-specific data:**

| Service | Why Shareable | Example |
|---------|---------------|---------|
| **OpenRouter** | Stateless LLM API | Same API key, different prompts |
| **Redis** | Cache only (no persistent data) | Different key prefixes (`bestays:`, `realestate:`) |
| **PostgreSQL Instance** | Container only, databases separate | Two databases in one container |

### ❌ Stateful Services (Separate - Required)

**These services MUST be separate because they store product-specific data:**

| Service | Why Separate | Current Setup |
|---------|--------------|---------------|
| **Clerk** | Stores user accounts, metadata | `sacred-mayfly-55` vs `pleasant-gnu-25` |
| **Database** | Stores all application data | `bestays_dev` vs `realestate_dev` |
| **Storage** | Would store user uploads | (Not implemented yet, must be separate) |
| **Email Service** | Contains user emails, templates | (Not implemented yet, must be separate) |

**Critical Rule:** If it stores data tied to users/products, it MUST be separate.

---

## UI Theming Strategy

### Configuration-Based Theming

**Approach:** Read environment variables and apply themes dynamically

**Implementation (SvelteKit):**

```typescript
// src/lib/config/theme.ts
export const theme = {
  primaryColor: import.meta.env.PUBLIC_PRIMARY_COLOR || '#FF6B6B',
  productName: import.meta.env.PUBLIC_PRODUCT_NAME || 'Bestays',
  logoPath: import.meta.env.PUBLIC_LOGO_PATH || '/logos/bestays-logo.svg'
};
```

**CSS Variables (Tailwind):**

```css
/* app.css - injected at runtime */
:root {
  --color-primary: #FF6B6B; /* From env var */
  --color-secondary: #F7B731;
}
```

**Result:**
- Bestays: Red/pink theme (#FF6B6B)
- Real Estate: Teal/turquoise theme (#4ECDC4)
- Same components, different colors

---

## Code Patterns

### Product-Specific Logic

**When to use if/else blocks:**

```typescript
// ✅ GOOD: Simple conditional for product-specific behavior
if (import.meta.env.PUBLIC_PRODUCT === 'bestays') {
  // Bestays-specific feature
  enableVacationRentalFilters();
} else {
  // Real Estate-specific feature
  enablePropertySalesFilters();
}
```

```python
# ✅ GOOD: Backend product detection
from server.config import settings

if settings.PRODUCT_NAME == "Bestays":
    # Bestays-specific logic
    return vacation_rental_search()
else:
    # Real Estate-specific logic
    return property_sales_search()
```

**When NOT to use if/else (keep generic):**

```typescript
// ✅ GOOD: Generic logic works for both products
async function fetchProperties(filters: PropertyFilters) {
  return apiClient.get('/properties', { params: filters });
}
```

**General Rule:** Keep code generic when possible. Use if/else only when products genuinely differ.

---

## Future Refactoring Path

### When to Consider Monorepo Refactor

**Triggers:**
1. **Code Duplication Pain:** If you copy-paste the same component/service >3 times
2. **Product Count:** When planning to add 3rd+ product
3. **White-Label Sale:** When ready to extract packages for external sale
4. **Team Size:** When team grows to 5+ developers (coordination overhead)

**Current State:** None of these triggers are met → Refactor not needed

### Preserved Planning (Reference Only)

**Documents saved for future use:**
- `.claude/tasks/TASK-003-backend-architecture/` - Backend monorepo design
- `.claude/tasks/TASK-004-frontend-architecture/` - Frontend monorepo design
- `.claude/tasks/TASK-005-architecture-synthesis/` - Complete 1,675-line architecture spec

**Status:** PLANNING_COMPLETE (not implemented)

**Future Story:** US-019 (Monorepo Refactoring) - P2 priority, post-MVP

---

## Development Workflow

### Adding New Features

**Standard Workflow:**

1. **Research Phase:** Analyze requirements, understand both product needs
2. **Planning Phase:** Design solution that works for BOTH products (generic when possible)
3. **Implementation Phase:**
   - Write generic code first
   - Add product-specific if/else only when necessary
   - Test on BOTH products (Bestays + Real Estate)
4. **Testing Phase:** E2E tests for both products
5. **Validation Phase:** Deploy to both products simultaneously

**Example: Adding Login Feature (US-012)**

```typescript
// Generic login component works for both
<script lang="ts">
  import { theme } from '$lib/config/theme';

  // Generic Clerk integration
  async function handleLogin(email: string, password: string) {
    return clerk.signIn({ email, password });
  }
</script>

<button style="background-color: {theme.primaryColor}">
  Sign In to {theme.productName}
</button>
```

No if/else needed! Configuration handles differences.

---

## Testing Strategy

### Multi-Product Testing Requirements

**For Every Feature:**

1. **Unit Tests:** Generic tests (no product-specific logic needed)
2. **Integration Tests:** Test with BOTH database configs
3. **E2E Tests:**
   - Test Bestays instance (http://localhost:5183)
   - Test Real Estate instance (http://localhost:5184)
   - Verify separate Clerk authentication
   - Verify separate databases (no data leakage)

**Example E2E Test:**

```typescript
// tests/e2e/login.spec.ts
test.describe('Multi-Product Login', () => {
  test('Bestays login uses sacred-mayfly-55 Clerk', async ({ page }) => {
    await page.goto('http://localhost:5183');
    await login(page, 'user.claudecode@bestays.app', '9kB*k926O8):');
    expect(page.url()).toContain('5183'); // Same product
  });

  test('Real Estate login uses pleasant-gnu-25 Clerk', async ({ page }) => {
    await page.goto('http://localhost:5184');
    await login(page, 'user.claudecode@realestate.dev', 'y>1T_)5h!X1X');
    expect(page.url()).toContain('5184'); // Same product
  });
});
```

---

## Deployment Strategy

### Development Environment

**Single Command Deployment:**

```bash
# Start both products
make dev-both

# Services:
# - Bestays Frontend:       http://localhost:5183
# - Bestays Backend:        http://localhost:8011
# - Real Estate Frontend:   http://localhost:5184
# - Real Estate Backend:    http://localhost:8012
# - PostgreSQL:             localhost:5433 (bestays_dev + realestate_dev)
# - Redis:                  localhost:6379
```

### Production Environment (Future)

**Separate VPS Deployment:**

```bash
# VPS 1: Bestays
docker-compose -f docker-compose.prod.yml up -d bestays-frontend bestays-server postgres redis

# VPS 2: Real Estate
docker-compose -f docker-compose.prod.yml up -d realestate-frontend realestate-server postgres redis
```

**OR Same VPS with Port Mapping:**

```bash
# Same VPS, different ports
docker-compose -f docker-compose.prod.yml up -d
# Nginx reverse proxy routes domains to ports
# bestays.app → 8011 (backend), 5183 (frontend)
# realestate.dev → 8012 (backend), 5184 (frontend)
```

---

## Migration History

### What We Considered (But Didn't Choose)

**Option B: True Monorepo** (DEFERRED)
- Separate apps: `apps/bestays-api`, `apps/realestate-api`, etc.
- Shared packages: `packages/shared-db`, `packages/shared-ui`, etc.
- **Why deferred:** Over-engineering before we have features to extract
- **When to revisit:** Post-MVP, when adding 3rd product or extracting white-label packages

**Option C: Multi-Tenant** (REJECTED)
- Single database with `tenant_id` column
- **Why rejected:** Higher risk of data leakage, harder to sell as separate products
- **When to revisit:** Never (separate databases is superior for our use case)

---

## Decision Outcomes

### US-018 Status: COMPLETE ✅

**Objectives Achieved:**
- ✅ Separate databases implemented (bestays_dev, realestate_dev)
- ✅ Separate Clerk instances configured (sacred-mayfly-55, pleasant-gnu-25)
- ✅ Docker Compose orchestration working (two products simultaneously)
- ✅ UI theming configured (different colors per product)
- ✅ Infrastructure sharing rules documented

**Architecture Planning (TASK-003, 004, 005):**
- Status: PLANNING_COMPLETE (preserved for future reference)
- Action: Deferred to US-019 (Monorepo Refactoring) - P2, post-MVP

### Next Steps: US-012 (Login) 🎯

**Full SDLC Workflow:**
1. **RESEARCH Phase:**
   - Review old NextJS login implementation (reference only)
   - Review Clerk integration patterns
   - Identify what needs to be reimplemented
2. **PLANNING Phase:**
   - Design login flow for SvelteKit
   - Apply 7 quality gates
   - Define acceptance criteria
3. **IMPLEMENTATION Phase:**
   - Implement via dev-frontend-svelte subagent
   - Test on BOTH products
4. **TESTING Phase:**
   - E2E tests for both Clerk instances
5. **VALIDATION Phase:**
   - Mark US-012 as complete

---

## Quick Reference

### Environment Variables by Product

| Variable | Bestays | Real Estate |
|----------|---------|-------------|
| `DATABASE_URL` | `bestays_dev` | `realestate_dev` |
| `CLERK_SECRET_KEY` | `sk_test_vGrRu...` | `sk_test_GBG0p...` |
| `VITE_CLERK_PUBLISHABLE_KEY` | `pk_test_c2Fjc...` | `pk_test_cGxlY...` |
| `FRONTEND_PORT` | 5183 | 5184 |
| `BACKEND_PORT` | 8011 | 8012 |
| `PRIMARY_COLOR` | #FF6B6B | #4ECDC4 |
| `PUBLIC_PRODUCT_NAME` | Bestays | Best Real Estate |

### File Locations

```
.env.shared           ← Shared config (OpenRouter, Redis)
.env.bestays          ← Bestays-specific config
.env.realestate       ← Real Estate-specific config

apps/server/          ← Backend (runs twice)
apps/frontend/        ← Frontend (runs twice)

docker-compose.dev.yml ← Development orchestration
```

---

## Risks and Mitigations

### Risk 1: Code Duplication
**Risk:** Features might be copy-pasted instead of kept generic
**Mitigation:** Code review enforces generic-first approach
**Threshold:** If copy-pasting >3 times, extract to shared function

### Risk 2: Product Logic Sprawl
**Risk:** if/else blocks everywhere make code unreadable
**Mitigation:** Configuration-based theming + generic components
**Threshold:** If >30% of code has if/else, consider monorepo refactor

### Risk 3: Test Coverage Gaps
**Risk:** Forgetting to test one product
**Mitigation:** CI/CD runs E2E tests for BOTH products automatically
**Threshold:** 100% features must be tested on both products

### Risk 4: Database Migration Mistakes
**Risk:** Running migration on wrong database
**Mitigation:** Alembic configured per product, different DATABASE_URL
**Threshold:** Zero tolerance - migrations must be verified on both databases

---

## Approval and Sign-Off

**Decision Made By:** User + SDLC Coordinator (Claude)
**Date:** 2025-11-08
**Approved Approach:** Single Application, Dual Instance (Option A)
**Next Milestone:** US-012 (Login) following full SDLC workflow

**Key Quote from User:**
> "Current implementation seems solid, just to be sure we using different UI themes. Also i'd like we to be prepare that any feature could work different and we may need to make if/else blocks. But in general let's follow this approach as we try to keep both functional alike."

**SDLC Coordinator Note:**
This decision prioritizes:
1. ✅ **Speed to features** over perfect architecture
2. ✅ **Simplicity** over complexity
3. ✅ **Working code** over theoretical plans
4. ✅ **MVP validation** over premature optimization

Future refactoring to monorepo remains an option when business needs justify the effort.

---

**Document Version:** 1.0
**Last Updated:** 2025-11-08
**Status:** APPROVED
**Implementation:** COMPLETE
**Next Review:** After US-012 (Login) completion

# US-018: White-Label Multi-Product Architecture

**Domain:** infrastructure
**Feature:** whitelabel
**Scope:** multi-product
**Status:** COMPLETE
**Priority:** P0 (URGENT AND MANDATORY)
**Created:** 2025-11-07

---

## Description

As a platform owner, I need to support **two separate products** from the same codebase:

1. **Bestays** - Rental properties platform (existing)
2. **New Real Estate** (name TBD) - High-cost properties (land, villas, business, investors)

Both products must:
- Share the same feature set (chat, FAQ, search, and future features)
- Have **separate user bases** (different Clerk projects - NOT shared authentication)
- Support **separate deployments** (different VPS machines, or same VPS with different configurations)
- Be architectured for **white-label/sellable** model (eventually extractable as separate products)

**Business Context:** This is a critical architectural transformation to enable multi-product strategy and future product sales.

---

## Acceptance Criteria

### ✅ IMPLEMENTED: Single Application, Dual Instance Architecture

**Decision:** Instead of monorepo with separate apps, we use one application running twice with different configurations.

**See:** `.claude/reports/20251108-multi-product-architecture-decision.md` for full rationale.

### Architecture

- [x] **Database Isolation:** Separate PostgreSQL databases (bestays_dev, realestate_dev)
- [x] **Docker Orchestration:** Docker Compose runs both products simultaneously
- [x] **Configuration System:** Environment-based configuration (.env.bestays, .env.realestate)
- [x] **UI Theming:** Different themes per product (PRIMARY_COLOR configured)
- [x] **Infrastructure Sharing Rules:** Documented (stateless shared, stateful separate)
- [ ] ~~Monorepo structure~~ - DEFERRED to US-019 (post-MVP, P2 priority)

### Authentication & User Management

- [x] Separate Clerk projects configured per product (no shared users)
  - Bestays: `sacred-mayfly-55.clerk.accounts.dev`
  - Real Estate: `pleasant-gnu-25.clerk.accounts.dev`
- [x] Environment-based Clerk configuration (API keys, JWT validation)
- [x] Clerk integration tested in both products independently

### Database

- [x] Database isolation strategy implemented (separate PostgreSQL databases)
  - `bestays_dev` (owned by bestays_user)
  - `realestate_dev` (owned by realestate_user)
- [x] Migration strategy defined (same Alembic migrations run on both databases)
- [x] Connection configuration per product (environment-based DATABASE_URL)

### Frontend

- [x] Theming system implemented for product-specific branding
  - Bestays: `PRIMARY_COLOR=#FF6B6B` (red/pink)
  - Real Estate: `PRIMARY_COLOR=#4ECDC4` (teal/turquoise)
- [x] Environment-based configuration (branding, colors, logos, product name)
- [x] Shared Svelte components (same codebase, different configurations)
- [x] Build system configured (Vite builds triggered per product via Docker Compose)

### Backend

- [x] Environment-based configuration per product (database, Clerk, API keys)
  - `.env.bestays` → bestays-server container
  - `.env.realestate` → realestate-server container
- [x] API versioning and routing strategy (same FastAPI app, configured per product)
- [x] Deployment strategy implemented (Docker containers per product)
- [ ] ~~Shared Python packages~~ - DEFERRED to US-019 (monorepo refactoring)

### Deployment

- [x] Separate deployment capability (Docker Compose can deploy to different VPS)
- [x] Same VPS deployment verified (different ports/configs)
  - Bestays: Frontend 5183, Backend 8011
  - Real Estate: Frontend 5184, Backend 8012
- [x] Environment variables managed per product (.env.bestays, .env.realestate)
- [ ] CI/CD pipeline supports multiple products - TODO (future work)

### Migration & Testing

- [x] Infrastructure setup complete (no existing features broken)
- [ ] Login flow - TO BE IMPLEMENTED in US-012
- [ ] Properties functionality - TO BE IMPLEMENTED (future US)
- [ ] Chat feature - TO BE IMPLEMENTED (future US)
- [ ] FAQ feature - TO BE IMPLEMENTED (future US)

---

## Technical Notes

### Recommended Architecture (from Sequential Thinking Analysis)

**Approach:** Monorepo with Shared Packages

**Why:**
1. ✅ Easy to extract features into sellable packages later
2. ✅ Separate apps = separate Clerk configs
3. ✅ Separate apps = separate deployments (different VPS)
4. ✅ Shared packages = DRY principle for features
5. ✅ Can deploy to same VPS with different ports/configs if needed
6. ✅ Clear separation of concerns (shared vs product-specific)

**Monorepo Structure:**
```
bestays-monorepo/
├── packages/
│   ├── shared-core/        # Business logic, models, utilities
│   ├── shared-ui/          # Svelte components
│   ├── shared-chat/        # Chat feature
│   ├── shared-faq/         # FAQ feature
│   ├── shared-search/      # Search functionality
│   └── shared-api-client/  # API client library
├── apps/
│   ├── bestays-web/        # Bestays SvelteKit frontend
│   ├── bestays-api/        # Bestays FastAPI backend
│   ├── realestate-web/     # Real Estate SvelteKit frontend
│   └── realestate-api/     # Real Estate FastAPI backend
├── config/
│   ├── bestays/            # Bestays-specific configs
│   └── realestate/         # Real Estate-specific configs
├── docker/
│   ├── bestays/            # Bestays Docker configs
│   └── realestate/         # Real Estate Docker configs
└── turbo.json              # Turborepo configuration
```

**Stack:**
- **Monorepo Tool:** Turborepo or pnpm workspaces
- **Frontend:** SvelteKit (existing stack, maintained)
- **Backend:** FastAPI (existing stack, maintained)
- **Shared Packages:** TypeScript libs for frontend, Python packages for backend
- **Database:** Separate PostgreSQL databases per product (data isolation)
- **Auth:** Separate Clerk projects per product (no shared users)
- **Deployment:** Docker containers per product (independent deployments)

**Risk Mitigation:**
1. **Migration complexity** - Incremental migration, feature by feature
2. **Clerk integration changes** - Research current Clerk setup first
3. **Database migration** - Evaluate migration path (start shared, split later possible)
4. **Build/deployment complexity** - Use proven monorepo tools (Turborepo/pnpm)

### Agent Review Chain (Sequential Execution)

**CRITICAL: Run agents SEQUENTIALLY (one at a time), not in parallel.**

1. **research-codebase** (FIRST) - Analyze current implementation:
   - Review login user story (how Clerk is integrated)
   - Review properties user story (data modeling patterns)
   - Find and analyze old chat implementation
   - Find and analyze old FAQ implementation
   - Identify what's reusable vs product-specific
   - Output: Research findings document

2. **dev-database** (AFTER research) - Database isolation strategy:
   - Review research findings
   - Decide: Separate databases OR multi-tenant with tenant_id?
   - Design migration strategy across products
   - Design connection pooling and configuration
   - Output: Database architecture recommendations

3. **dev-backend-fastapi** (AFTER database) - Backend architecture:
   - Review research + database recommendations
   - Design shared Python packages structure
   - Design environment-based configuration per product
   - Design API versioning and routing
   - Design deployment strategy (Docker containers)
   - Output: Backend architecture plan

4. **dev-frontend-svelte** (AFTER backend) - Frontend architecture:
   - Review all previous findings
   - Design shared Svelte components structure
   - Design theming system (CSS variables, Tailwind config)
   - Design environment-based branding configuration
   - Design Clerk integration per product
   - Design build configuration (separate builds per product)
   - Output: Frontend architecture plan

5. **Synthesis** (FINAL) - Combine all agent recommendations:
   - Create comprehensive architecture plan
   - Identify first implementation tasks
   - Create task breakdown with priorities

### Clerk Authentication Configuration

**CRITICAL:** Both products use **separate Clerk projects** with separate user bases.

**Configuration Document:** `.claude/tasks/TASK-001-research-codebase/research/clerk-multi-product-config.md`

**Bestays.app Clerk Project:**
- Clerk Account: `sacred-mayfly-55.clerk.accounts.dev`
- Publishable Key: `pk_test_c2FjcmVkLW1heWZseS01NS5jbGVyay5hY2NvdW50cy5kZXYk`
- Secret Key: `sk_test_vGrRuTLW1SdS2uQlDbv4l2T2WHpTk9IoervBmG9Vit`
- Test Users:
  - User: `user.claudecode@bestays.app` / `9kB*k926O8):`
  - Admin: `admin.claudecode@bestays.app` / `rHe/997?lo&l`
  - Agent: `agent.claudecode@bestays.app` / `y>1T;)5s!X1X`

**Best Real Estate Clerk Project:**
- Clerk Account: `pleasant-gnu-25.clerk.accounts.dev`
- Publishable Key: `pk_test_cGxlYXNhbnQtZ251LTI1LmNsZXJrLmFjY291bnRzLmRldiQ`
- Secret Key: `sk_test_GBG0pHIE015mIkiHfrpeOS4mi1hqNSm0uBUdlexgxS`
- Test Users:
  - User: `user.claudecode@realestate.dev` / `y>1T_)5h!X1X`
  - Admin: `admin.claudecode@realestate.dev` / `rHe/997?lo&l`
  - Agent: `agent.claudecode@realestate.dev` / `y>1T;)5s!X1X`

**Role Management:**
- Clerk provides authentication only (email/password, JWT tokens)
- **User roles managed by our backend** (not Clerk)
- Roles: `user`, `admin`, `agent`
- After Clerk authentication, backend assigns role from database

### Dependencies

**External:**
- Turborepo (monorepo orchestration)
- pnpm (package management)
- Docker (containerization)
- PostgreSQL (database)
- Clerk (authentication - 2 separate projects configured above)

**Internal:**
- Existing Bestays codebase (to be refactored)
- Existing chat implementation (to be extracted)
- Existing FAQ implementation (to be extracted)

### Constraints

- **No shared authentication** - Separate Clerk projects required
- **Data isolation** - User data must NOT be shared between products
- **Independent deployments** - Must support separate VPS deployments
- **White-label ready** - Architecture must allow future product extraction/sales
- **Feature parity** - Both products must have same features (chat, FAQ, search, etc.)

---

## Related Stories

**Reference Implementations (to be reviewed by research-codebase agent):**
- Login user story - Understand current Clerk integration patterns
- Properties user story - Understand current data modeling patterns
- Old chat implementation - Extract for shared package
- Old FAQ implementation - Extract for shared package

---

## Tasks

### Phase 1: Research & Planning (TASK-001 to TASK-005)

**TASK-001:** Research current codebase structure (research-codebase agent)
- Review login story, properties story, chat, FAQ implementations
- Analyze reusable vs product-specific code
- Document findings

**TASK-002:** Database isolation strategy (dev-database agent)
- Review research findings
- Design database architecture
- Document recommendations

**TASK-003:** Backend architecture design (dev-backend-fastapi agent)
- Review research + database recommendations
- Design shared packages, configuration, deployment
- Document architecture plan

**TASK-004:** Frontend architecture design (dev-frontend-svelte agent)
- Review all previous findings
- Design shared components, theming, Clerk integration
- Document architecture plan

**TASK-005:** Synthesize comprehensive architecture plan
- Combine all agent recommendations
- Create unified architecture document
- Identify first implementation tasks

### Phase 2: Implementation (TASK-006 onwards - TBD after planning)

[To be defined after architecture planning completes]

---

**Story Created:** 2025-11-07
**Last Updated:** 2025-11-07
**Sequential Thinking Analysis:** Completed (10 thoughts)
**Recommended Approach:** Monorepo with Shared Packages

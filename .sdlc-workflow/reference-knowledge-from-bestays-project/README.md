# Reference Knowledge from Bestays Project

**Purpose:** This directory preserves implementation patterns, architectural decisions, and code examples from the Bestays real estate rental platform project that was used as the foundation for ShredBX Model Generator.

**Use Case:** Reference these files when implementing similar features in ShredBX (authentication, database, API design, etc.) without following the old user stories directly.

---

## What's Preserved Here

This knowledge base contains:

1. **Implementation Patterns**
   - How to build FastAPI backend with PostgreSQL
   - How to implement Clerk authentication
   - How to structure SvelteKit frontend
   - How to set up Docker development environment
   - How to implement RBAC (Role-Based Access Control)

2. **Architectural Decisions**
   - Why we chose certain technologies
   - Trade-offs and alternatives considered
   - Database schema design patterns
   - API endpoint structure

3. **Code Examples**
   - Authentication flows
   - Database models and migrations
   - API endpoints
   - Svelte components
   - E2E tests

4. **DevOps Knowledge**
   - Docker Compose setup
   - Environment configuration
   - Multi-product deployment strategies
   - Database migration workflows

---

## Directory Structure

```
reference-knowledge-from-bestays-project/
├── README.md (this file)
├── implementation-patterns/
│   ├── authentication-clerk.md
│   ├── database-postgresql-sqlalchemy.md
│   ├── fastapi-backend-structure.md
│   ├── sveltekit-frontend-structure.md
│   └── rbac-implementation.md
├── code-examples/
│   ├── backend/
│   │   ├── clerk-integration.py
│   │   ├── database-models.py
│   │   ├── api-endpoints.py
│   │   └── rbac-middleware.py
│   ├── frontend/
│   │   ├── auth-flow.svelte
│   │   ├── api-client.ts
│   │   └── protected-routes.svelte
│   └── tests/
│       ├── e2e-login-flow.spec.ts
│       └── backend-unit-tests.py
├── architecture/
│   ├── tech-stack-decisions.md
│   ├── database-schema.md
│   ├── api-design-principles.md
│   └── multi-product-strategy.md
├── devops/
│   ├── docker-compose-setup.md
│   ├── environment-configuration.md
│   ├── database-migrations.md
│   └── deployment-workflow.md
└── old-user-stories/ (archived, for reference only)
    ├── auth/
    ├── properties/
    ├── homepage/
    └── booking/
```

---

## How to Use This Knowledge

### ✅ DO:

1. **Reference implementation patterns** when building similar features in ShredBX
   - Example: "How do I implement Clerk auth?" → Check `implementation-patterns/authentication-clerk.md`

2. **Copy code snippets** and adapt them for ShredBX context
   - Example: FastAPI structure, database models, Svelte components

3. **Learn from architectural decisions** to avoid repeating mistakes
   - Example: Why we chose Clerk over custom auth

4. **Use as SDLC examples** for quality standards
   - Example: File headers, testing coverage, documentation

### ❌ DON'T:

1. **Don't follow old user stories** (US-001, US-019, etc.) - they're for a different product
2. **Don't copy code blindly** - adapt to ShredBX context (3D models vs properties)
3. **Don't feel obligated to replicate** every Bestays feature
4. **Don't reference old task numbers** in new ShredBX work

---

## Quick Reference Index

### When Building...

| ShredBX Feature | Reference Knowledge |
|-----------------|---------------------|
| **Image upload API** | `code-examples/backend/file-upload.py` |
| **User authentication** | `implementation-patterns/authentication-clerk.md` |
| **Database models** | `code-examples/backend/database-models.py` |
| **FastAPI endpoints** | `code-examples/backend/api-endpoints.py` |
| **Svelte components** | `code-examples/frontend/*.svelte` |
| **E2E tests** | `code-examples/tests/e2e-*.spec.ts` |
| **Docker setup** | `devops/docker-compose-setup.md` |
| **Environment config** | `devops/environment-configuration.md` |
| **RBAC (if needed)** | `implementation-patterns/rbac-implementation.md` |

---

## Migration Summary

### What Was Moved Here

**Old User Stories** (for reference only):
- US-001 series: Login flow validation
- US-001B series: RBAC implementation
- US-019: Auth login flow
- US-020: Homepage editable content
- US-021: Locale switching
- US-026: Homepage property categories

**Old Tasks** (archived):
- TASK-001 to TASK-019 (Bestays implementation work)
- All `.claude/tasks/TASK-*` folders

### What Stays Active

**ShredBX User Stories** (new):
- US-001: Image to 3D Model Viewer (NEW)
- Future stories for ShredBX features

**Active Skills**:
- All `.claude/skills/*` (dev-philosophy, dev-code-quality, etc.)
- SDLC workflow guides

**Active Infrastructure**:
- CLAUDE.md (updated for ShredBX context)
- SDLC templates and guides
- Git workflow documentation

---

## Knowledge Extraction Examples

### Example 1: FastAPI Backend Structure

**Old Bestays Code:**
```python
# apps/server/app/api/v1/endpoints/properties.py
@router.get("/properties", response_model=List[PropertySchema])
async def list_properties(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    properties = db.query(Property).all()
    return properties
```

**Adapted for ShredBX:**
```python
# apps/server/app/api/v1/endpoints/models.py
@router.get("/3d-models", response_model=List[ModelSchema])
async def list_3d_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Optional for ShredBX
):
    models = db.query(ThreeDModel).all()
    return models
```

### Example 2: Svelte Component Pattern

**Old Bestays Code:**
```svelte
<!-- PropertyCard.svelte -->
<script lang="ts">
  export let property: Property;
</script>

<div class="card">
  <img src={property.cover_image} alt={property.title} />
  <h3>{property.title}</h3>
  <p>{property.description}</p>
</div>
```

**Adapted for ShredBX:**
```svelte
<!-- ModelCard.svelte -->
<script lang="ts">
  export let model: ThreeDModel;
</script>

<div class="card">
  <img src={model.thumbnail_url} alt={model.name} />
  <h3>{model.name}</h3>
  <p>{model.created_at}</p>
</div>
```

---

## Memory MCP Entities

The following knowledge has been stored in Memory MCP for instant recall:

1. **"Bestays FastAPI Backend Pattern"**
   - FastAPI structure, dependency injection, database sessions

2. **"Clerk Authentication Implementation"**
   - Frontend and backend integration patterns

3. **"SvelteKit 5 + Runes Patterns"**
   - Component structure, state management, routing

4. **"Docker Development Environment"**
   - Multi-service orchestration, hot reload setup

5. **"RBAC Implementation Pattern"**
   - Role-based access control with Clerk + FastAPI

6. **"E2E Testing with Playwright"**
   - Test structure, login flows, assertions

You can recall these with:
```
mcp__memory__open_nodes(names: ["Bestays FastAPI Backend Pattern"])
```

---

## Frequently Needed Patterns

### 1. Clerk Authentication (Backend)

**File:** `implementation-patterns/authentication-clerk.md`

**Key Learnings:**
- Use Clerk SDK to verify JWT tokens
- Store minimal user info in database (Clerk ID + roles)
- Don't store passwords or sensitive Clerk data
- Use middleware for protected routes

### 2. PostgreSQL + SQLAlchemy

**File:** `database-postgresql-sqlalchemy.md`

**Key Learnings:**
- Use Alembic for migrations
- Use asyncio for better performance
- Separate models from schemas (Pydantic)
- Use pgvector for embeddings (if needed)

### 3. SvelteKit 5 + Runes

**File:** `sveltekit-frontend-structure.md`

**Key Learnings:**
- Use $state for reactive state
- Use $effect for side effects (carefully!)
- Prefer onMount for non-reactive initialization
- Use load functions for server-side data

### 4. Docker Development Environment

**File:** `devops/docker-compose-setup.md`

**Key Learnings:**
- Use volumes for hot reload
- Separate dev/prod compose files
- Use Makefile for common commands
- Use health checks for service dependencies

---

## Questions?

**"How do I implement X in ShredBX?"**
→ Check this knowledge base first, then adapt for 3D models context

**"Can I copy code from old tasks?"**
→ Yes, but adapt it! Don't blindly copy property-related code

**"Should I read old user stories?"**
→ Only for understanding implementation patterns, not as requirements

**"Where is the Clerk integration code?"**
→ Check `code-examples/backend/clerk-integration.py`

---

**Created:** 2025-11-11
**Purpose:** Preserve Bestays knowledge for ShredBX reference
**Status:** Active reference, not active development

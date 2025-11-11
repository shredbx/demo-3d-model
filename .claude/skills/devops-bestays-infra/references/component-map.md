# Bestays System Component Map

**Purpose**: Index of all system components and where their specifications live.

**Pattern**: This file does NOT duplicate spec content. It provides POINTERS to definitive sources.

---

## Core Principle

**Single Source of Truth**: All detailed information lives in specs or config files. This map just points to them.

**When to Read This**: When you need to find information about a specific component but don't know where to look.

---

## Infrastructure & DevOps

### Docker Compose

**Definitive Source**: `docker-compose.dev.yml` (development), `docker-compose.prod.yml` (production)

**What's There**:

- Service definitions (backend, frontend, postgres, redis)
- Port mappings
- Environment variables
- Volume mounts
- Health checks
- Dependencies

**Spec**: `.pattern-book/specifications/tech/preflight-validation.md` (validation system)

**Discussion**: `.pattern-book/discussions/20251027-2321-infrastructure-setup-deployment-testing-/`

### Makefile

**Definitive Source**: `Makefile`

**What's There**:

- All development commands (`make dev`, `make rebuild`, etc.)
- Service management (start, stop, restart)
- Logging commands
- Health checks
- Validation workflows

**Key Commands**:

- `make dev` - Smart start/restart with validation
- `make logs` - View all service logs
- `make check` - Health check all services
- `make rebuild` - Full rebuild with migrations
- `make shell-server` / `make shell-frontend` / `make shell-db` - Access service shells

### Preflight Validation

**Definitive Source**: `.sdlc-workflow/scripts/preflight.sh`

**What's There**:

- Environment validation checks
- Port availability checks
- Docker daemon status
- .env file validation
- Directory structure checks

**Spec**: `.pattern-book/specifications/tech/preflight-validation.md`

**What It Validates**:

- Docker running
- Ports available (8011, 5183, 5433, 6379)
- .env file exists
- Required env vars set
- Docker Compose file valid
- Required directories present

---

## Backend (Python/FastAPI)

### Server Application

**Definitive Source**: `apps/server/`

**Structure**:

- `src/server/` - Main application code
- `src/server/main.py` - FastAPI entry point
- `src/server/api/` - API routes
- `src/server/core/` - Core functionality
- `src/server/db/` - Database models
- `src/server/schemas/` - Pydantic schemas

**Docker**: Service name `server` in docker-compose.dev.yml

**Ports**: 8011 (host) → 8011 (container)

**Health Endpoint**: `http://localhost:8011/api/health`

**API Docs**: `http://localhost:8011/docs` (Swagger UI)

**Specs**:

- URS: `.pattern-book/specifications/urs/openrouter-chat.md`
- Tech: `.pattern-book/specifications/tech/openrouter-chat.md`
- Integration: `.pattern-book/specifications/integration/openrouter-chat.md`

### Database (PostgreSQL)

**Definitive Source**: `docker-compose.dev.yml` (service: `postgres`)

**Connection**:

- Host port: 5433 → Container port: 5432
- Database: `bestays_dev`
- User: `bestays_user`
- Password: `bestays_password`

**Access**:

- Via Makefile: `make shell-db`
- Direct: `psql -h localhost -p 5433 -U bestays_user -d bestays_dev`

**Migrations**: Alembic (run via `make migrate` or `docker-compose exec server alembic upgrade head`)

### Cache (Redis)

**Definitive Source**: `docker-compose.dev.yml` (service: `redis`)

**Connection**:

- Port: 6379
- URL: `redis://localhost:6379`

**Usage**:

- LLM response caching
- Session storage
- Rate limiting

---

## Frontend (SvelteKit)

### Frontend Application

**Definitive Source**: `apps/frontend/`

**Structure**:

- `src/` - Source code
- `src/routes/` - SvelteKit routes
- `src/lib/` - Shared libraries
- `src/lib/components/` - Svelte components
- `src/lib/types/` - TypeScript types

**Docker**: Service name `frontend` in docker-compose.dev.yml

**Ports**: 5183 (host) → 5183 (container)

**Dev Server**: Vite with hot-reload

**Specs**:

- URS: `.pattern-book/specifications/urs/openrouter-chat.md` (chat UI)
- Tech: `.pattern-book/specifications/tech/openrouter-chat.md`
- Integration: `.pattern-book/specifications/integration/openrouter-chat.md`

---

## External Services

### OpenRouter (LLM API)

**What's There**:

- Multi-model LLM access
- API integration details

**Spec**: `.pattern-book/specifications/integration/openrouter-chat.md`

**Env Vars**:

- `OPENROUTER_API_KEY`
- `OPENROUTER_BASE_URL`

### Clerk (Authentication)

**What's There**:

- User authentication
- Session management

**Env Vars**:

- `CLERK_SECRET_KEY`
- `CLERK_WEBHOOK_SECRET`
- `VITE_CLERK_PUBLISHABLE_KEY`

---

## Pattern-Book System

### Discussions

**Location**: `.pattern-book/discussions/`

**Index**: `.pattern-book/DISCUSSIONS-INDEX.md`

**Key Discussions**:

- Infrastructure: `20251027-2321-infrastructure-setup-deployment-testing-/`
- OpenRouter Chat: `20251027-2024-openrouter-chat-implementation/`

### Specifications

**Location**: `.pattern-book/specifications/`

**Index**: `.pattern-book/SPECS-INDEX.md`

**Types**:

- `urs/` - User Requirements Specifications
- `tech/` - Technical Specifications
- `integration/` - Integration Contracts

**Available Specs**:

- `preflight-validation` - Tech spec for environment validation
- `openrouter-chat` - Full URS + Tech + Integration specs

### Scripts

**Location**: `.pattern-book/scripts/`

**Categories**:

- `discussions/` - Discussion management scripts
- `specifications/` - Spec creation and validation scripts
- `common/` - Shared utilities

---

## Configuration Files

### Environment Variables

**Definitive Source**: `.env` (not in git)

**Template**: `.env.example`

**Required Variables**:

- `CLERK_SECRET_KEY` - Clerk authentication
- `OPENROUTER_API_KEY` - LLM API access
- `DATABASE_URL` - Database connection (has default)

**Where Used**: Loaded by docker-compose.dev.yml into services

### Docker Configuration

**Dockerfiles**:

- Backend: `docker/server/Dockerfile.dev`
- Frontend: `docker/frontend/Dockerfile.dev`

**Compose Files**:

- Development: `docker-compose.dev.yml`
- Production: `docker-compose.prod.yml`

---

## How to Use This Map

### Example 1: "What ports does the system use?"

**Answer**: Look in `docker-compose.dev.yml` → `services` → `ports` sections

### Example 2: "How do I debug the backend?"

**Answer**:

1. Check health: `make check`
2. View logs: `make logs-server`
3. Access shell: `make shell-server`
4. Refer to infrastructure discussion for debugging workflows

### Example 3: "Where are the chat API schemas defined?"

**Answer**:

1. Backend schemas: `apps/server/src/server/schemas/`
2. Frontend types: `apps/frontend/src/lib/types/`
3. Contract spec: `.pattern-book/specifications/integration/openrouter-chat.md`

### Example 4: "How do I add a new environment variable?"

**Answer**:

1. Add to `.env` file
2. Add to docker-compose.dev.yml → service → environment
3. Document in relevant spec
4. Update this component map if it's a new subsystem

---

## Self-Update Protocol

**When This Map Is Incomplete**:

1. Identify the missing component
2. Find its definitive source (config file, code, or spec)
3. Add entry to appropriate section
4. Follow the pointer pattern (WHERE, not WHAT)
5. Commit update to skill

**Pattern to Follow**:

```markdown
### [Component Name]

**Definitive Source**: [file path]

**What's There**: [brief list of what information is available]

**Spec** (if applicable): [path to spec]

**Key Details**: [critical facts that help locate information]
```

---

**Last Updated**: 2025-10-28
**Maintainer**: bestays-devenv skill (self-updating)

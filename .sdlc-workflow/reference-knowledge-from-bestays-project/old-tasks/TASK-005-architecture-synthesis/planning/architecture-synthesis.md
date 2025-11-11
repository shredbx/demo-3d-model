# TASK-005: Architecture Synthesis

**Date:** 2025-11-07
**Agent:** Architecture Synthesis
**User Story:** US-018 (White-Label Multi-Product Architecture)
**Status:** COMPLETE
**Priority:** P0 (URGENT AND MANDATORY)

---

## Executive Summary

**Unified Architecture:** **Mixed Monorepo (Python + JavaScript) with Shared Packages**

**Key Integration Points:**
1. **Database Layer** - PostgreSQL with separate databases (bestays_db, realestate_db)
2. **Backend Layer** - FastAPI apps sharing Python packages (shared-db, shared-chat, shared-faq)
3. **Frontend Layer** - SvelteKit apps sharing JavaScript packages (shared-ui, shared-api-client)
4. **Deployment** - Docker Compose orchestration with unified development workflow

**Alignment with User Priorities:**
- ✅ **Simplicity for deployment** - Single `docker-compose up` command starts all services
- ✅ **Simplicity for development** - Standard Python + JavaScript tooling (pip + pnpm)
- ✅ **Modular architecture** - Clear package boundaries, one-way dependencies
- ✅ **Clear documentation** - Environment-based configuration, comprehensive README

**Risk Assessment:** LOW - This synthesis uses proven patterns from all three prior tasks (TASK-002, TASK-003, TASK-004) without introducing new architectural concepts.

---

## Complete Monorepo Structure

### Directory Layout

```
bestays-monorepo/
├── .claude/                           # Claude Code workspace
│   ├── tasks/                         # Architecture tasks
│   ├── memory/                        # Patterns, decisions
│   └── user-stories/                  # US-018
│
├── packages/                          # Shared packages (backend + frontend)
│   │
│   ├── Backend (Python)
│   ├── shared-db/                     # SQLAlchemy models + database utilities
│   │   ├── src/
│   │   │   ├── models/               # User, Property, Chat, FAQ models
│   │   │   ├── database.py           # Async engine, session factory
│   │   │   └── seeds/                # Seed data utilities
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   ├── shared-config/                 # Pydantic Settings base classes
│   │   ├── src/
│   │   │   ├── base.py               # BaseSettings
│   │   │   └── database.py           # DatabaseSettings
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   ├── shared-core/                   # Core utilities
│   │   ├── src/
│   │   │   ├── exceptions.py         # APIException classes
│   │   │   ├── logging.py            # Structured logging
│   │   │   ├── auth.py               # RBAC decorators
│   │   │   └── cache.py              # Redis cache utilities
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   ├── shared-chat/                   # Chat feature (extracted)
│   │   ├── src/
│   │   │   ├── services/             # ChatService, ConversationService
│   │   │   ├── schemas/              # Pydantic schemas
│   │   │   └── router.py             # FastAPI router
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   ├── shared-faq/                    # FAQ RAG system (extracted)
│   │   ├── src/
│   │   │   ├── services/             # FAQRagPipeline, VectorSearch
│   │   │   ├── schemas/              # Pydantic schemas
│   │   │   └── router.py             # FastAPI router
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   ├── shared-search/                 # Search utilities
│   │   ├── src/
│   │   │   ├── vector_search.py
│   │   │   ├── keyword_search.py
│   │   │   └── hybrid_search.py
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   ├── Frontend (JavaScript/TypeScript)
│   ├── shared-ui/                     # Reusable Svelte components
│   │   ├── src/
│   │   │   ├── components/           # Button, Card, Input, Modal
│   │   │   ├── styles/               # Base CSS, CSS variables
│   │   │   └── utils/                # cn() utility
│   │   ├── tests/
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── shared-api-client/             # TypeScript API client
│   │   ├── src/
│   │   │   ├── types.ts              # API types (from backend Pydantic)
│   │   │   ├── client.ts             # Fetch wrapper
│   │   │   ├── endpoints/            # users.ts, chat.ts, faq.ts
│   │   │   └── errors.ts             # Error handling
│   │   ├── tests/
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── shared-chat-ui/                # Chat UI components
│   │   ├── src/
│   │   │   ├── components/           # ChatInterface, MessageList
│   │   │   ├── stores/               # chat.ts (Svelte runes)
│   │   │   └── types.ts
│   │   ├── tests/
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── shared-faq-ui/                 # FAQ UI components
│   │   ├── src/
│   │   │   ├── components/           # FAQSearch, FAQList
│   │   │   └── types.ts
│   │   ├── tests/
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   └── shared-config/                 # Configuration types
│       ├── src/
│       │   └── types.ts              # ProductConfig interface
│       ├── package.json
│       └── tsconfig.json
│
├── apps/                              # Product applications
│   │
│   ├── Backend (Python/FastAPI)
│   ├── bestays-api/                   # Bestays FastAPI app
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   ├── deps.py           # Product-specific dependencies
│   │   │   │   └── v1/
│   │   │   │       ├── endpoints/    # users.py, properties.py
│   │   │   │       └── router.py
│   │   │   ├── config/
│   │   │   │   ├── __init__.py      # BestaysSettings
│   │   │   │   ├── chat.py          # Chat-specific config
│   │   │   │   └── faq.py           # FAQ-specific config
│   │   │   └── main.py              # FastAPI app initialization
│   │   ├── alembic/
│   │   │   ├── versions/            # Bestays migrations
│   │   │   └── env.py
│   │   ├── alembic.ini
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   ├── integration/
│   │   │   └── conftest.py
│   │   ├── pyproject.toml           # Dependencies include shared-*
│   │   └── .env.development
│   │
│   ├── realestate-api/               # Real Estate FastAPI app
│   │   ├── app/
│   │   │   ├── api/
│   │   │   ├── config/
│   │   │   │   ├── __init__.py      # RealEstateSettings
│   │   │   │   ├── chat.py
│   │   │   │   └── faq.py
│   │   │   └── main.py
│   │   ├── alembic/
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── .env.development
│   │
│   ├── Frontend (SvelteKit)
│   ├── bestays-web/                   # Bestays SvelteKit app
│   │   ├── src/
│   │   │   ├── lib/
│   │   │   │   ├── config/
│   │   │   │   │   ├── index.ts       # Bestays-specific config
│   │   │   │   │   ├── chat.ts
│   │   │   │   │   └── theme.ts
│   │   │   │   ├── clerk.ts           # Clerk SDK initialization
│   │   │   │   └── api.ts             # API client instance
│   │   │   ├── routes/
│   │   │   │   ├── +layout.svelte     # Global layout
│   │   │   │   ├── +page.svelte       # Home page
│   │   │   │   └── ...
│   │   │   └── app.css                # Product-specific CSS
│   │   ├── static/                    # Bestays assets
│   │   ├── .env.development
│   │   ├── svelte.config.js
│   │   ├── vite.config.ts
│   │   ├── tailwind.config.js
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   └── realestate-web/                # Real Estate SvelteKit app
│       ├── src/
│       │   ├── lib/
│       │   │   ├── config/
│       │   │   │   ├── index.ts       # Real Estate-specific config
│       │   │   │   ├── chat.ts
│       │   │   │   └── theme.ts
│       │   │   ├── clerk.ts
│       │   │   └── api.ts
│       │   ├── routes/
│       │   └── app.css
│       ├── static/
│       ├── .env.development
│       ├── svelte.config.js
│       ├── vite.config.ts
│       ├── tailwind.config.js
│       ├── package.json
│       └── tsconfig.json
│
├── docker/                            # Docker configurations
│   ├── bestays-api/
│   │   ├── Dockerfile.dev
│   │   └── Dockerfile.prod
│   ├── realestate-api/
│   │   ├── Dockerfile.dev
│   │   └── Dockerfile.prod
│   ├── bestays-web/
│   │   ├── Dockerfile.dev
│   │   ├── Dockerfile.prod
│   │   └── nginx.conf
│   ├── realestate-web/
│   │   ├── Dockerfile.dev
│   │   ├── Dockerfile.prod
│   │   └── nginx.conf
│   └── postgres/
│       └── init-multi-db.sql        # Create both databases
│
├── scripts/                           # Automation scripts
│   ├── sync-migrations.sh           # Sync migrations Bestays → Real Estate
│   ├── install-shared-packages.sh   # Install all shared Python packages
│   └── validate-environment.sh      # Validate .env files
│
├── tests/                             # E2E tests (Playwright)
│   ├── e2e/
│   │   ├── bestays/
│   │   │   ├── auth.spec.ts
│   │   │   └── chat.spec.ts
│   │   └── realestate/
│   │       ├── auth.spec.ts
│   │       └── chat.spec.ts
│   └── playwright.config.ts
│
├── docs/                              # Documentation
│   ├── architecture/
│   │   ├── diagrams/
│   │   └── decisions/
│   └── api/
│       └── integration-guide.md
│
├── docker-compose.dev.yml            # Development environment
├── docker-compose.prod.yml           # Production environment
├── pnpm-workspace.yaml               # pnpm workspaces config
├── .env.example                      # Example environment variables
├── .gitignore
├── Makefile                          # Common commands
└── README.md                         # Setup instructions
```

---

## Package Dependency Graph

### Complete Dependency Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (SvelteKit)                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  apps/bestays-web                    apps/realestate-web           │
│       ↓                                      ↓                     │
│  shared-chat-ui ──→ shared-ui ──→ shared-config                   │
│       ↓                  ↓                                         │
│  shared-faq-ui ────→ shared-api-client                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                ↓ API CALLS
┌─────────────────────────────────────────────────────────────────────┐
│                       BACKEND (FastAPI)                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  apps/bestays-api                  apps/realestate-api             │
│       ↓                                      ↓                     │
│  shared-chat ──→ shared-db ──→ shared-config                       │
│       ↓              ↓                                             │
│  shared-faq ─────→ shared-core                                     │
│       ↓                                                            │
│  shared-search                                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                ↓ DATABASE QUERIES
┌─────────────────────────────────────────────────────────────────────┐
│                    DATABASE (PostgreSQL)                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  PostgreSQL Instance (Single Container)                             │
│       ├── bestays_db (Bestays data)                                │
│       └── realestate_db (Real Estate data)                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Cross-Layer Type Flow

```
Backend Pydantic Schemas
        ↓
    (Manual sync)
        ↓
Frontend TypeScript Types
        ↓
API Client Implementation
        ↓
Svelte Components
```

**Future Improvement:** Automated type generation (Pydantic → TypeScript)

---

## Unified Development Workflow

### Development Ports

**All Services:**

| Service | Port | URL |
|---------|------|-----|
| **PostgreSQL** | 5432 | postgresql://localhost:5432 |
| **Redis** | 6379 | redis://localhost:6379 |
| **Bestays API** | 8101 | http://localhost:8101 |
| **Real Estate API** | 8102 | http://localhost:8102 |
| **Bestays Frontend** | 5273 | http://localhost:5273 |
| **Real Estate Frontend** | 5274 | http://localhost:5274 |

**Database Names:**
- `bestays_db_dev` - Bestays development database
- `realestate_db_dev` - Real Estate development database

**Redis Databases:**
- DB 0 - Bestays cache
- DB 1 - Real Estate cache

### Single-Command Startup

**Complete Development Environment:**

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up

# Verify services
make health-check
```

**What This Starts:**
1. PostgreSQL (with both databases)
2. Redis (with both DB namespaces)
3. Bestays API (port 8101)
4. Real Estate API (port 8102)
5. Bestays Frontend (port 5273)
6. Real Estate Frontend (port 5274)

---

## Docker Compose Configuration

### Development Environment

**`docker-compose.dev.yml`:**

```yaml
version: '3.9'

services:
  # ============================================================================
  # PostgreSQL Instance (One Container, Two Databases)
  # ============================================================================
  postgres:
    image: postgres:16-alpine
    container_name: bestays-postgres-dev
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      PGDATA: /var/lib/postgresql/data/pgdata
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init-multi-db.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - bestays-network
    restart: unless-stopped

  # ============================================================================
  # Redis (Shared, Multiple Databases)
  # ============================================================================
  redis:
    image: redis:7-alpine
    container_name: bestays-redis-dev
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - bestays-network
    restart: unless-stopped

  # ============================================================================
  # Bestays Backend API
  # ============================================================================
  bestays-api:
    build:
      context: .
      dockerfile: docker/bestays-api/Dockerfile.dev
    container_name: bestays-api-dev
    environment:
      # Product Identification
      APP_NAME: Bestays
      PRODUCT_ID: bestays

      # Database (bestays_db)
      DATABASE_URL: postgresql+asyncpg://bestays_user:bestays_password@postgres:5432/bestays_db_dev
      DATABASE_POOL_SIZE: 10
      DATABASE_MAX_OVERFLOW: 20
      DATABASE_ECHO: "false"

      # Clerk (Bestays Clerk Project)
      CLERK_SECRET_KEY: ${BESTAYS_CLERK_SECRET_KEY}
      CLERK_PUBLISHABLE_KEY: ${BESTAYS_CLERK_PUBLISHABLE_KEY}
      CLERK_WEBHOOK_SECRET: ${BESTAYS_CLERK_WEBHOOK_SECRET}

      # Redis (DB 0)
      REDIS_URL: redis://redis:6379/0
      REDIS_KEY_PREFIX: bestays:

      # Frontend URL (for CORS)
      FRONTEND_URL: http://localhost:5273

      # OpenAI
      OPENAI_API_KEY: ${OPENAI_API_KEY}

      # Feature Flags
      CHAT_ENABLED: "true"
      FAQ_ENABLED: "true"
      SEARCH_ENABLED: "true"
    ports:
      - "8101:8000"
    volumes:
      - ./apps/bestays-api:/app:delegated
      - ./packages:/packages:delegated
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - bestays-network
    restart: unless-stopped
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # ============================================================================
  # Real Estate Backend API
  # ============================================================================
  realestate-api:
    build:
      context: .
      dockerfile: docker/realestate-api/Dockerfile.dev
    container_name: realestate-api-dev
    environment:
      # Product Identification
      APP_NAME: Best Real Estate
      PRODUCT_ID: realestate

      # Database (realestate_db)
      DATABASE_URL: postgresql+asyncpg://realestate_user:realestate_password@postgres:5432/realestate_db_dev
      DATABASE_POOL_SIZE: 10
      DATABASE_MAX_OVERFLOW: 20
      DATABASE_ECHO: "false"

      # Clerk (Real Estate Clerk Project)
      CLERK_SECRET_KEY: ${REALESTATE_CLERK_SECRET_KEY}
      CLERK_PUBLISHABLE_KEY: ${REALESTATE_CLERK_PUBLISHABLE_KEY}
      CLERK_WEBHOOK_SECRET: ${REALESTATE_CLERK_WEBHOOK_SECRET}

      # Redis (DB 1)
      REDIS_URL: redis://redis:6379/1
      REDIS_KEY_PREFIX: realestate:

      # Frontend URL (for CORS)
      FRONTEND_URL: http://localhost:5274

      # OpenAI
      OPENAI_API_KEY: ${OPENAI_API_KEY}

      # Feature Flags
      CHAT_ENABLED: "true"
      FAQ_ENABLED: "true"
      SEARCH_ENABLED: "true"
    ports:
      - "8102:8000"
    volumes:
      - ./apps/realestate-api:/app:delegated
      - ./packages:/packages:delegated
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - bestays-network
    restart: unless-stopped
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # ============================================================================
  # Bestays Frontend (SvelteKit)
  # ============================================================================
  bestays-web:
    build:
      context: .
      dockerfile: docker/bestays-web/Dockerfile.dev
    container_name: bestays-web-dev
    environment:
      # Product Identification
      VITE_PRODUCT_ID: bestays
      VITE_APP_NAME: Bestays
      VITE_APP_TAGLINE: Find your perfect vacation rental

      # API
      VITE_API_URL: http://localhost:8101

      # Clerk (Bestays Project)
      PUBLIC_CLERK_PUBLISHABLE_KEY: ${BESTAYS_CLERK_PUBLISHABLE_KEY}

      # Feature Flags
      VITE_CHAT_ENABLED: "true"
      VITE_FAQ_ENABLED: "true"
      VITE_SEARCH_ENABLED: "true"
      VITE_DARK_MODE_ENABLED: "true"

      # Branding
      VITE_PRIMARY_COLOR: "#3B82F6"
      VITE_SECONDARY_COLOR: "#10B981"
      VITE_ACCENT_COLOR: "#F59E0B"
    ports:
      - "5273:5173"
    volumes:
      - ./apps/bestays-web:/app/apps/bestays-web:delegated
      - ./packages:/app/packages:delegated
      - /app/node_modules
      - /app/apps/bestays-web/node_modules
    depends_on:
      - bestays-api
    networks:
      - bestays-network
    restart: unless-stopped
    command: pnpm run dev --host 0.0.0.0

  # ============================================================================
  # Real Estate Frontend (SvelteKit)
  # ============================================================================
  realestate-web:
    build:
      context: .
      dockerfile: docker/realestate-web/Dockerfile.dev
    container_name: realestate-web-dev
    environment:
      # Product Identification
      VITE_PRODUCT_ID: realestate
      VITE_APP_NAME: Best Real Estate
      VITE_APP_TAGLINE: Luxury properties and investment opportunities

      # API
      VITE_API_URL: http://localhost:8102

      # Clerk (Real Estate Project)
      PUBLIC_CLERK_PUBLISHABLE_KEY: ${REALESTATE_CLERK_PUBLISHABLE_KEY}

      # Feature Flags
      VITE_CHAT_ENABLED: "true"
      VITE_FAQ_ENABLED: "true"
      VITE_SEARCH_ENABLED: "true"
      VITE_DARK_MODE_ENABLED: "false"

      # Branding
      VITE_PRIMARY_COLOR: "#EF4444"
      VITE_SECONDARY_COLOR: "#F59E0B"
      VITE_ACCENT_COLOR: "#8B5CF6"
    ports:
      - "5274:5173"
    volumes:
      - ./apps/realestate-web:/app/apps/realestate-web:delegated
      - ./packages:/app/packages:delegated
      - /app/node_modules
      - /app/apps/realestate-web/node_modules
    depends_on:
      - realestate-api
    networks:
      - bestays-network
    restart: unless-stopped
    command: pnpm run dev --host 0.0.0.0

networks:
  bestays-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

### Production Environment

**`docker-compose.prod.yml`:**

```yaml
version: '3.9'

services:
  # PostgreSQL (Production)
  postgres:
    image: postgres:16-alpine
    container_name: bestays-postgres-prod
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_MASTER_PASSWORD}
      PGDATA: /var/lib/postgresql/data/pgdata
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init-multi-db-prod.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 5
    networks:
      - bestays-network
    restart: always

  # Redis (Production)
  redis:
    image: redis:7-alpine
    container_name: bestays-redis-prod
    command: >
      redis-server
      --maxmemory 2gb
      --maxmemory-policy allkeys-lru
      --appendonly yes
      --requirepass ${REDIS_PASSWORD}
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5
    networks:
      - bestays-network
    restart: always

  # Bestays API (Production)
  bestays-api:
    build:
      context: .
      dockerfile: docker/bestays-api/Dockerfile.prod
    container_name: bestays-api-prod
    environment:
      APP_NAME: Bestays
      PRODUCT_ID: bestays
      ENVIRONMENT: production
      DATABASE_URL: postgresql+asyncpg://bestays_user:${BESTAYS_DB_PASSWORD}@postgres:5432/bestays_db
      CLERK_SECRET_KEY: ${BESTAYS_CLERK_SECRET_KEY}
      CLERK_PUBLISHABLE_KEY: ${BESTAYS_CLERK_PUBLISHABLE_KEY}
      REDIS_URL: redis://redis:6379/0
      REDIS_KEY_PREFIX: bestays:
      FRONTEND_URL: https://bestays.app
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "8101:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - bestays-network
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G

  # Real Estate API (Production)
  realestate-api:
    build:
      context: .
      dockerfile: docker/realestate-api/Dockerfile.prod
    container_name: realestate-api-prod
    environment:
      APP_NAME: Best Real Estate
      PRODUCT_ID: realestate
      ENVIRONMENT: production
      DATABASE_URL: postgresql+asyncpg://realestate_user:${REALESTATE_DB_PASSWORD}@postgres:5432/realestate_db
      CLERK_SECRET_KEY: ${REALESTATE_CLERK_SECRET_KEY}
      CLERK_PUBLISHABLE_KEY: ${REALESTATE_CLERK_PUBLISHABLE_KEY}
      REDIS_URL: redis://redis:6379/1
      REDIS_KEY_PREFIX: realestate:
      FRONTEND_URL: https://realestate.app
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "8102:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - bestays-network
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G

  # Bestays Frontend (Production)
  bestays-web:
    build:
      context: .
      dockerfile: docker/bestays-web/Dockerfile.prod
    container_name: bestays-web-prod
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - bestays-api
    networks:
      - bestays-network
    restart: always

  # Real Estate Frontend (Production)
  realestate-web:
    build:
      context: .
      dockerfile: docker/realestate-web/Dockerfile.prod
    container_name: realestate-web-prod
    ports:
      - "81:80"
      - "444:443"
    depends_on:
      - realestate-api
    networks:
      - bestays-network
    restart: always

networks:
  bestays-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

---

## Makefile Commands

**`Makefile`:**

```makefile
.PHONY: help setup dev-up dev-down health-check test-all migrate-all seed-all clean

# ============================================================================
# Help
# ============================================================================
help:
	@echo "Bestays Monorepo - Available Commands"
	@echo ""
	@echo "Development:"
	@echo "  make setup          - Install all dependencies (Python + JavaScript)"
	@echo "  make dev-up         - Start all development services"
	@echo "  make dev-down       - Stop all development services"
	@echo "  make health-check   - Check health of all services"
	@echo ""
	@echo "Database:"
	@echo "  make migrate-all    - Run migrations for both databases"
	@echo "  make seed-all       - Seed development data for both databases"
	@echo "  make reset-db       - Reset both databases (WARNING: destroys data)"
	@echo ""
	@echo "Testing:"
	@echo "  make test-backend   - Run backend tests (unit + integration)"
	@echo "  make test-frontend  - Run frontend tests (unit + component)"
	@echo "  make test-e2e       - Run E2E tests (Playwright)"
	@echo "  make test-all       - Run all tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           - Lint all code (Python + JavaScript)"
	@echo "  make format         - Format all code (black, prettier)"
	@echo "  make type-check     - Type check all code (mypy, tsc)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Remove build artifacts and caches"

# ============================================================================
# Development Setup
# ============================================================================
setup:
	@echo "📦 Installing dependencies..."
	@bash scripts/install-shared-packages.sh
	@cd apps/bestays-api && pip install -e .
	@cd apps/realestate-api && pip install -e .
	@pnpm install
	@echo "✅ Setup complete!"

dev-up:
	@echo "🚀 Starting development environment..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "✅ Development environment started!"
	@echo ""
	@echo "Services available at:"
	@echo "  - PostgreSQL:          localhost:5432"
	@echo "  - Redis:               localhost:6379"
	@echo "  - Bestays API:         http://localhost:8101"
	@echo "  - Real Estate API:     http://localhost:8102"
	@echo "  - Bestays Frontend:    http://localhost:5273"
	@echo "  - Real Estate Frontend: http://localhost:5274"

dev-down:
	@echo "🛑 Stopping development environment..."
	docker-compose -f docker-compose.dev.yml down
	@echo "✅ Development environment stopped!"

health-check:
	@echo "🔍 Checking service health..."
	@curl -f http://localhost:8101/api/health || echo "❌ Bestays API not responding"
	@curl -f http://localhost:8102/api/health || echo "❌ Real Estate API not responding"
	@curl -f http://localhost:5273 || echo "❌ Bestays Frontend not responding"
	@curl -f http://localhost:5274 || echo "❌ Real Estate Frontend not responding"
	@echo "✅ Health check complete!"

# ============================================================================
# Database Management
# ============================================================================
migrate-all:
	@echo "📦 Running migrations for all databases..."
	@cd apps/bestays-api && alembic upgrade head
	@cd apps/realestate-api && alembic upgrade head
	@echo "✅ All migrations complete!"

seed-all:
	@echo "🌱 Seeding development data..."
	@cd apps/bestays-api && python scripts/seed_dev_data.py
	@cd apps/realestate-api && python scripts/seed_dev_data.py
	@echo "✅ All databases seeded!"

reset-db:
	@echo "⚠️  WARNING: This will delete all data in both databases!"
	@read -p "Are you sure? (yes/no): " CONFIRM && [ "$$CONFIRM" = "yes" ] || exit 1
	@cd apps/bestays-api && alembic downgrade base && alembic upgrade head
	@cd apps/realestate-api && alembic downgrade base && alembic upgrade head
	@make seed-all
	@echo "✅ Databases reset complete!"

# ============================================================================
# Testing
# ============================================================================
test-backend:
	@echo "🧪 Running backend tests..."
	@cd apps/bestays-api && pytest tests/
	@cd apps/realestate-api && pytest tests/
	@echo "✅ Backend tests complete!"

test-frontend:
	@echo "🧪 Running frontend tests..."
	@cd apps/bestays-web && pnpm run test
	@cd apps/realestate-web && pnpm run test
	@echo "✅ Frontend tests complete!"

test-e2e:
	@echo "🧪 Running E2E tests..."
	@playwright test
	@echo "✅ E2E tests complete!"

test-all: test-backend test-frontend test-e2e

# ============================================================================
# Code Quality
# ============================================================================
lint:
	@echo "🔍 Linting all code..."
	@cd apps/bestays-api && ruff check .
	@cd apps/realestate-api && ruff check .
	@pnpm run lint
	@echo "✅ Linting complete!"

format:
	@echo "✨ Formatting all code..."
	@cd apps/bestays-api && black .
	@cd apps/realestate-api && black .
	@pnpm run format
	@echo "✅ Formatting complete!"

type-check:
	@echo "🔍 Type checking all code..."
	@cd apps/bestays-api && mypy .
	@cd apps/realestate-api && mypy .
	@pnpm run type-check
	@echo "✅ Type checking complete!"

# ============================================================================
# Cleanup
# ============================================================================
clean:
	@echo "🧹 Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name "node_modules" -exec rm -rf {} +
	@find . -type d -name "build" -exec rm -rf {} +
	@echo "✅ Cleanup complete!"
```

---

## Environment Configuration

### Root `.env.example`

```bash
# ============================================================================
# PostgreSQL
# ============================================================================
POSTGRES_MASTER_PASSWORD=your_secure_master_password

# ============================================================================
# Bestays Configuration
# ============================================================================
# Clerk (Bestays Clerk Project)
BESTAYS_CLERK_SECRET_KEY=sk_test_vGrRuTLW1SdS2uQlDbv4l2T2WHpTk9IoervBmG9Vit
BESTAYS_CLERK_PUBLISHABLE_KEY=pk_test_c2FjcmVkLW1heWZseS01NS5jbGVyay5hY2NvdW50cy5kZXYk
BESTAYS_CLERK_WEBHOOK_SECRET=whsec_bestays_dev

# Database
BESTAYS_DB_PASSWORD=bestays_password

# ============================================================================
# Real Estate Configuration
# ============================================================================
# Clerk (Real Estate Clerk Project)
REALESTATE_CLERK_SECRET_KEY=sk_test_GBG0pHIE015mIkiHfrpeOS4mi1hqNSm0uBUdlexgxS
REALESTATE_CLERK_PUBLISHABLE_KEY=pk_test_cGxlYXNhbnQtZ251LTI1LmNsZXJrLmFjY291bnRzLmRldiQ
REALESTATE_CLERK_WEBHOOK_SECRET=whsec_realestate_dev

# Database
REALESTATE_DB_PASSWORD=realestate_password

# ============================================================================
# Shared Configuration
# ============================================================================
# OpenAI API Key (shared or separate per product)
OPENAI_API_KEY=sk-proj-your_openai_api_key

# Redis
REDIS_PASSWORD=your_redis_password
```

---

## Complete Setup Guide

### Prerequisites

**Required Tools:**
- Docker Desktop (for containers)
- Python 3.12+ (for backend development)
- Node.js 20+ (for frontend development)
- pnpm (for JavaScript package management)

**Installation:**

```bash
# macOS (Homebrew)
brew install docker python@3.12 node pnpm

# Ubuntu/Debian
apt-get install docker.io python3.12 nodejs npm
npm install -g pnpm

# Windows (Chocolatey)
choco install docker-desktop python nodejs
npm install -g pnpm
```

### Step-by-Step Setup

**1. Clone Repository:**

```bash
git clone <repository-url> bestays-monorepo
cd bestays-monorepo
```

**2. Create Environment File:**

```bash
cp .env.example .env
# Edit .env with your credentials (Clerk keys, OpenAI key, etc.)
```

**3. Install Dependencies:**

```bash
make setup
```

This installs:
- All Python shared packages (shared-db, shared-chat, shared-faq, etc.)
- Backend dependencies (fastapi, sqlalchemy, langchain, etc.)
- Frontend dependencies (svelte, tailwindcss, etc.)

**4. Start Development Environment:**

```bash
make dev-up
```

This starts:
- PostgreSQL (with both databases)
- Redis
- Bestays API
- Real Estate API
- Bestays Frontend
- Real Estate Frontend

**5. Run Migrations:**

```bash
make migrate-all
```

This creates all database tables in both `bestays_db_dev` and `realestate_db_dev`.

**6. Seed Development Data:**

```bash
make seed-all
```

This creates test users and sample data in both databases.

**7. Verify Setup:**

```bash
make health-check
```

**8. Access Applications:**

- Bestays Frontend: http://localhost:5273
- Real Estate Frontend: http://localhost:5274
- Bestays API Docs: http://localhost:8101/docs
- Real Estate API Docs: http://localhost:8102/docs

---

## Testing Strategy

### Test Pyramid

```
           ╱╲
          ╱  ╲
         ╱ E2E ╲           ~5% (Playwright)
        ╱────────╲
       ╱          ╲
      ╱ Integration╲        ~25% (pytest + PostgreSQL)
     ╱──────────────╲
    ╱                ╲
   ╱  Unit + Component╲      ~70% (pytest + Vitest)
  ╱────────────────────╲
```

### Backend Testing

**Unit Tests (SQLite In-Memory):**

```bash
# Run backend unit tests
cd apps/bestays-api
pytest tests/unit/

# With coverage
pytest tests/unit/ --cov=app --cov-report=html
```

**Integration Tests (PostgreSQL):**

```bash
# Run backend integration tests (requires PostgreSQL running)
cd apps/bestays-api
pytest tests/integration/
```

**Test Coverage Targets:**
- Shared packages: ≥95% (high-risk, used by both products)
- Product apps: ≥80% (medium-risk, product-specific logic)

### Frontend Testing

**Unit Tests (Vitest):**

```bash
# Run frontend unit tests
cd apps/bestays-web
pnpm run test

# With coverage
pnpm run test:coverage
```

**Component Tests:**

```bash
# Test shared UI components
cd packages/shared-ui
pnpm run test
```

### E2E Testing (Playwright)

**Run E2E Tests:**

```bash
# Run all E2E tests
make test-e2e

# Run specific product tests
playwright test --grep "Bestays"
playwright test --grep "Real Estate"
```

**E2E Test Structure:**

```typescript
// tests/e2e/bestays/auth.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Bestays Authentication', () => {
  test.beforeAll(async () => {
    // Reset test databases
    await exec('make reset-db');
  });

  test('user can sign in with Clerk', async ({ page }) => {
    await page.goto('http://localhost:5273');

    // Click sign in
    await page.click('text=Sign In');

    // Fill Clerk form
    await page.fill('input[name="email"]', 'user.claudecode@bestays.app');
    await page.fill('input[name="password"]', '9kB*k926O8):');
    await page.click('button:has-text("Sign In")');

    // Verify redirect
    await expect(page).toHaveURL('http://localhost:5273/dashboard');
  });
});
```

---

## Migration Plan from Current State

### Phased Migration Timeline (8 Weeks Total)

**Week 1: Monorepo Setup**
- ✅ Create directory structure
- ✅ Set up pnpm workspaces
- ✅ Set up Python shared packages
- ✅ Configure Docker Compose

**Week 2: Database Isolation**
- ✅ Implement separate databases (bestays_db, realestate_db)
- ✅ Create PostgreSQL init script
- ✅ Test connection isolation

**Week 3: Backend Shared Packages**
- ✅ Extract shared-db package
- ✅ Extract shared-config package
- ✅ Extract shared-core package
- ✅ Test with existing server

**Week 4: Bestays Backend App**
- ✅ Create apps/bestays-api from existing server
- ✅ Update configuration (PRODUCT_ID = "bestays")
- ✅ Run migrations, seed data
- ✅ Verify tests pass

**Week 5: Backend Feature Extraction**
- ✅ Extract shared-chat package
- ✅ Extract shared-faq package
- ✅ Update Bestays app to use shared packages
- ✅ Test chat and FAQ features

**Week 6: Real Estate Backend App**
- ✅ Copy Bestays app to apps/realestate-api
- ✅ Update configuration (PRODUCT_ID = "realestate")
- ✅ Copy and update migrations
- ✅ Seed Real Estate-specific data

**Week 7: Frontend Migration**
- ✅ Create frontend shared packages
- ✅ Create apps/bestays-web
- ✅ Create apps/realestate-web
- ✅ Extract shared-ui, shared-api-client

**Week 8: E2E Testing & Validation**
- ✅ Run E2E tests for both products
- ✅ Performance testing
- ✅ Security audit
- ✅ Documentation updates

---

## Deployment to Production

### Production Checklist

**1. Environment Variables:**
- [ ] All `.env` files created (not checked into git)
- [ ] Clerk production keys configured
- [ ] OpenAI production API key set
- [ ] Database passwords secure (strong passwords)
- [ ] Redis password set

**2. Database Setup:**
- [ ] PostgreSQL production databases created
- [ ] Migrations run on production databases
- [ ] Database backups configured (daily cron jobs)

**3. Docker Images:**
- [ ] Backend images built with production Dockerfiles
- [ ] Frontend images built with production Dockerfiles
- [ ] Images pushed to container registry (if applicable)

**4. Services:**
- [ ] All services start successfully with `docker-compose -f docker-compose.prod.yml up`
- [ ] Health checks passing for all services
- [ ] CORS configured correctly per product
- [ ] SSL certificates configured (for HTTPS)

**5. Monitoring:**
- [ ] Health check endpoints configured
- [ ] Logging configured (structured logs)
- [ ] Error tracking configured (Sentry, etc.)
- [ ] Uptime monitoring configured

**6. Backup & Recovery:**
- [ ] Database backup script tested
- [ ] Database restore script tested
- [ ] Backup retention policy defined (30 days)
- [ ] Backup uploaded to remote storage (S3, etc.)

### Production Deployment Commands

```bash
# 1. Pull latest code
git pull origin main

# 2. Build production images
docker-compose -f docker-compose.prod.yml build

# 3. Stop current production services (if running)
docker-compose -f docker-compose.prod.yml down

# 4. Start production services
docker-compose -f docker-compose.prod.yml up -d

# 5. Run migrations
cd apps/bestays-api && alembic upgrade head
cd apps/realestate-api && alembic upgrade head

# 6. Verify services
curl http://localhost:8101/api/health
curl http://localhost:8102/api/health

# 7. Monitor logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

## Monitoring and Maintenance

### Health Checks

**Backend Health Endpoint:**

```python
# apps/bestays-api/app/api/v1/endpoints/health.py

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_bestays_db

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "ok", "product": "bestays"}

@router.get("/health/db")
async def database_health_check(db: AsyncSession = Depends(get_bestays_db)):
    """Database connectivity health check."""
    try:
        await db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "product": "bestays",
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "error",
            "product": "bestays",
            "database": "disconnected",
            "error": str(e),
        }
```

### Log Aggregation

**Structured Logging:**

```python
# packages/shared-core/src/logging.py

import logging
import json
from datetime import datetime

class StructuredLogger:
    """Structured JSON logger for production."""

    def __init__(self, product_id: str):
        self.product_id = product_id
        self.logger = logging.getLogger(product_id)

    def info(self, message: str, **kwargs):
        self.logger.info(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "product": self.product_id,
            "level": "INFO",
            "message": message,
            **kwargs
        }))
```

### Backup Automation

**Automated Daily Backups:**

```bash
# /etc/cron.d/bestays-backups

# Backup Bestays database daily at 2 AM
0 2 * * * /opt/bestays/scripts/backup-bestays-db.sh

# Backup Real Estate database daily at 3 AM
0 3 * * * /opt/bestays/scripts/backup-realestate-db.sh

# Clean old backups (keep last 30 days)
0 4 * * * find /backups/bestays -name "*.gz" -mtime +30 -delete
0 4 * * * find /backups/realestate -name "*.gz" -mtime +30 -delete
```

---

## Documentation Standards

### README Requirements

**Each package and app MUST have a README.md with:**

1. **Purpose** - What does this package/app do? (1-2 sentences)
2. **Setup** - How to install dependencies and configure
3. **Usage** - How to use this package/app
4. **Testing** - How to run tests and coverage targets
5. **Configuration** - Environment variables and settings
6. **Dependencies** - What this depends on (both external and internal)
7. **Integration** - How this integrates with other packages/apps

**Example Backend README:**

```markdown
# Bestays API

## Purpose

FastAPI application for Bestays vacation rental platform, providing REST API for user authentication, property management, chat, and FAQ features.

## Setup

```bash
# Install dependencies
pip install -e .

# Install shared packages
pip install -e ../../packages/shared-db
pip install -e ../../packages/shared-config
pip install -e ../../packages/shared-core
pip install -e ../../packages/shared-chat
pip install -e ../../packages/shared-faq

# Create .env file
cp .env.example .env
# Edit .env with your credentials

# Run migrations
alembic upgrade head

# Seed development data
python scripts/seed_dev_data.py
```

## Usage

```bash
# Development
uvicorn app.main:app --reload --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Testing

```bash
# Unit tests (SQLite in-memory)
pytest tests/unit/

# Integration tests (PostgreSQL)
pytest tests/integration/

# Coverage report
pytest --cov=app --cov-report=html
```

**Target Coverage:** ≥80%

## Configuration

**Environment Variables:**

- `APP_NAME` - Application name ("Bestays")
- `PRODUCT_ID` - Product identifier ("bestays")
- `DATABASE_URL` - PostgreSQL connection string
- `CLERK_SECRET_KEY` - Clerk authentication secret
- `REDIS_URL` - Redis connection string
- `OPENAI_API_KEY` - OpenAI API key

## Dependencies

**External:**
- fastapi (web framework)
- sqlalchemy (ORM)
- alembic (migrations)
- langchain (LLM integration)
- clerk-backend-api (authentication)

**Internal:**
- shared-db (database models)
- shared-config (settings)
- shared-core (utilities)
- shared-chat (chat feature)
- shared-faq (FAQ feature)

## Integration

- **Database:** Connects to `bestays_db_dev` (PostgreSQL)
- **Frontend:** CORS configured for `http://localhost:5273`
- **Clerk:** Uses Bestays Clerk project (sacred-mayfly-55)
- **Redis:** Uses DB 0 with key prefix `bestays:`
```

---

## Trade-offs and Risks

### Pros of This Architecture

**Simplicity:**
- ✅ Single Docker Compose command starts everything
- ✅ Standard Python (pip) + JavaScript (pnpm) tooling
- ✅ No complex build systems (Turborepo, Lerna)
- ✅ Environment-based configuration (clear `.env` files)

**Modularity:**
- ✅ Clear package boundaries (shared packages vs apps)
- ✅ One-way dependencies (shared → apps, never reverse)
- ✅ Easy to extract packages for white-label sales
- ✅ Products completely isolated (separate databases, Clerk projects)

**Safety:**
- ✅ Zero risk of cross-product data leakage
- ✅ Type safety (Python type hints, TypeScript)
- ✅ High test coverage (≥95% shared, ≥80% apps)
- ✅ Complete authentication isolation (separate Clerk projects)

**Developer Experience:**
- ✅ Hot reload for both backend and frontend
- ✅ Fast feedback loop (SQLite unit tests, Vite HMR)
- ✅ Clear error messages (standardized API error format)
- ✅ Comprehensive documentation (README per package)

### Cons of This Architecture

**Package Management:**
- ❌ Manual installation of Python shared packages (`pip install -e packages/shared-*`)
  - **Mitigation:** Automation script (`scripts/install-shared-packages.sh`)
  - **Mitigation:** Makefile command (`make setup`)

**Migration Overhead:**
- ❌ Need to sync migrations between products
  - **Mitigation:** Automation script (`scripts/sync-migrations.sh`)
  - **Mitigation:** Shared SQLAlchemy models package

**Type Synchronization:**
- ❌ Manual sync of types from Pydantic to TypeScript
  - **Mitigation:** Code review checks for type consistency
  - **Future:** Automated type generation tool

**Deployment Complexity:**
- ❌ Two Docker images per product (backend + frontend)
  - **Mitigation:** Shared base images (future optimization)
  - **Mitigation:** Docker Compose simplifies orchestration

### When to Revisit This Architecture

**Scenario 1: More Than 5 Products**

If the platform grows to 10+ products:
- Consider shared authentication (single Clerk project with metadata)
- Consider multi-tenant database (tenant_id) for cost efficiency
- Consider Kubernetes for horizontal scaling

**Scenario 2: Extremely High Scale (1M+ users per product)**

If traffic exceeds single PostgreSQL instance capacity:
- Move to separate PostgreSQL instances (different VPS)
- Consider PostgreSQL clustering (Patroni, Citus)
- Consider cloud-managed databases (AWS RDS, Azure Database)

**Scenario 3: Complex CI/CD Requirements**

If deployment frequency requires sophisticated caching:
- Consider Turborepo for build caching
- Consider Nx for better monorepo tooling
- Consider separate repositories per product

---

## Next Steps

### Immediate Actions (Week 1)

1. **Review Architecture:**
   - Validate all integration points
   - Confirm package structure with team
   - Verify Clerk configuration

2. **Create Monorepo:**
   - Initialize directory structure
   - Set up pnpm workspaces
   - Configure Python packages

3. **Set Up Docker Compose:**
   - Create `docker-compose.dev.yml`
   - Create PostgreSQL init script
   - Test local development environment

### Short-Term Actions (Weeks 2-8)

1. **Database Isolation (Week 2):**
   - Implement separate databases
   - Test connection isolation
   - Document migration strategy

2. **Backend Architecture (Weeks 3-6):**
   - Extract shared packages
   - Create product apps
   - Implement feature extraction

3. **Frontend Architecture (Week 7):**
   - Create frontend shared packages
   - Implement product apps
   - Integrate with backend APIs

4. **Testing & Validation (Week 8):**
   - E2E tests for both products
   - Performance testing
   - Security audit

### Long-Term Actions (Post-MVP)

1. **Automated Type Generation:**
   - Pydantic → TypeScript type generation
   - CI/CD integration

2. **Enhanced Monitoring:**
   - Prometheus metrics
   - Grafana dashboards
   - Alert configuration

3. **Performance Optimization:**
   - Database query optimization
   - Frontend bundle size optimization
   - API response time optimization

---

## Conclusion

**Recommended Architecture: Mixed Monorepo (Python + JavaScript) with Shared Packages**

**Why This Architecture:**
1. ✅ **Simplest** - Single Docker Compose command, standard tooling
2. ✅ **Most Modular** - Clear package boundaries, one-way dependencies
3. ✅ **Safest** - Complete product isolation, zero data leakage risk
4. ✅ **Best Documented** - Comprehensive READMEs, clear configuration

**Alignment with User Priorities:**
- ✅ **Simplicity for deployment** - `docker-compose up` starts everything
- ✅ **Simplicity for development** - Hot reload, fast tests, clear errors
- ✅ **Modular architecture** - Shared packages, product apps, clear boundaries
- ✅ **Clear documentation** - README per package, comprehensive setup guide

**Confidence Level: HIGH** - This architecture synthesizes proven patterns from TASK-002, TASK-003, and TASK-004 without introducing new risks.

**Ready for Implementation:** YES - All architectural decisions documented, all integration points defined, complete development workflow specified.

---

**Document Version:** 1.0
**Date:** 2025-11-07
**Agent:** Architecture Synthesis
**Status:** COMPLETE
**Next Steps:** Begin implementation with Week 1 tasks (monorepo setup)

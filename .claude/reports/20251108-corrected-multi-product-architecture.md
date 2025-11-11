# Corrected Multi-Product Architecture (Simple Approach)

**Date:** 2025-11-08
**Purpose:** Run two separate products from same codebase without multi-tenancy complexity
**Supersedes:** 20251107-local-multi-product-development.md (incorrect multi-tenant approach)

---

## User Requirements (Clarified)

> "Two totally separate projects that share the code for auth/chat/FAQ and others. They could be run in parallel on the same machine with no problem, no shared DB and anything else per original requirements."

**Key Points:**
- ✅ Same codebase (DRY principle)
- ✅ Separate databases (bestays_dev, realestate_dev)
- ✅ Separate Clerk instances (different users)
- ✅ Run in parallel (different ports)
- ❌ NO shared database
- ❌ NO product filtering
- ❌ NO multi-tenancy infrastructure

---

## Architecture

### Strategy: Same Code, Different Instances

**Concept:** Run the **exact same application twice** with different configurations.

```
apps/
├── frontend/     # One codebase
└── server/       # One codebase

Docker runs 4 containers:
1. bestays-frontend   → uses apps/frontend + .env.bestays
2. bestays-server     → uses apps/server + .env.bestays
3. realestate-frontend → uses apps/frontend + .env.realestate
4. realestate-server   → uses apps/server + .env.realestate
```

### Key Differences Per Product

| Configuration | Bestays | Real Estate |
|---------------|---------|-------------|
| **Database** | bestays_dev | realestate_dev |
| **Frontend Port** | 5183 | 5184 |
| **Backend Port** | 8011 | 8012 |
| **Clerk Instance** | sacred-mayfly-55 | pleasant-gnu-25 |
| **Property Types** | Rental (business logic) | Land/Villa/Business (business logic) |

---

## Configuration Files

### `.env.shared` (Common Settings)

```bash
# OpenRouter (shared LLM service)
OPENROUTER_API_KEY=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
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Redis (shared cache)
REDIS_URL=redis://redis:6379/0
REDIS_CACHE_TTL=3600

# Common settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

**Note:** No DATABASE_URL in shared file (each product has its own).

---

### `.env.bestays` (Bestays Product)

```bash
# Database (separate)
DATABASE_URL=postgresql+asyncpg://bestays_user:bestays_password@postgres:5432/bestays_dev

# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_c2FjcmVkLW1heWZseS01NS5jbGVyay5hY2NvdW50cy5kZXYk
CLERK_SECRET_KEY=sk_test_vGrRuTLW1SdS2uQlDbv4l2T2WHpTk9IoervBmG9Vit

# Ports
FRONTEND_PORT=5183
BACKEND_PORT=8011

# Frontend public env vars
PUBLIC_API_URL=http://localhost:8011
PUBLIC_PRODUCT_NAME=Bestays

# Backend configuration
API_HOST=0.0.0.0
API_PORT=8011
CORS_ORIGINS=http://localhost:5183
```

---

### `.env.realestate` (Real Estate Product)

```bash
# Database (separate)
DATABASE_URL=postgresql+asyncpg://realestate_user:realestate_password@postgres:5432/realestate_dev

# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_cGxlYXNhbnQtZ251LTI1LmNsZXJrLmFjY291bnRzLmRldiQ
CLERK_SECRET_KEY=sk_test_GBG0pHIE015mIkiHfrpeOS4mi1hqNSm0uBUdlexgxS

# Ports
FRONTEND_PORT=5184
BACKEND_PORT=8012

# Frontend public env vars
PUBLIC_API_URL=http://localhost:8012
PUBLIC_PRODUCT_NAME=Best Real Estate

# Backend configuration
API_HOST=0.0.0.0
API_PORT=8012
CORS_ORIGINS=http://localhost:5184
```

---

## Docker Compose Configuration

### PostgreSQL Setup

**Create both databases on init:**

```yaml
postgres:
  image: postgres:16-alpine
  environment:
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres
    POSTGRES_MULTIPLE_DATABASES: bestays_dev,realestate_dev
  volumes:
    - ./docker/postgres/create-multiple-databases.sh:/docker-entrypoint-initdb.d/create-databases.sh
```

**Init Script** (`docker/postgres/create-multiple-databases.sh`):
```bash
#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE bestays_dev;
    CREATE DATABASE realestate_dev;

    CREATE USER bestays_user WITH PASSWORD 'bestays_password';
    CREATE USER realestate_user WITH PASSWORD 'realestate_password';

    GRANT ALL PRIVILEGES ON DATABASE bestays_dev TO bestays_user;
    GRANT ALL PRIVILEGES ON DATABASE realestate_dev TO realestate_user;
EOSQL
```

### Service Configuration

```yaml
bestays-server:
  env_file:
    - .env.shared
    - .env.bestays
  environment:
    PYTHONPATH: /app/src
  ports:
    - "8011:8011"
  # Uses DATABASE_URL from .env.bestays

realestate-server:
  env_file:
    - .env.shared
    - .env.realestate
  environment:
    PYTHONPATH: /app/src
  ports:
    - "8012:8012"
  # Uses DATABASE_URL from .env.realestate
```

---

## What Changed From Previous Approach

### Removed (Unnecessary Complexity)

- ❌ `PRODUCT` environment variable
- ❌ Product context middleware (159 lines)
- ❌ Product column in database tables
- ❌ Database migration for product field
- ❌ Product filtering in queries
- ❌ Multi-tenant architecture patterns

### Kept (Correct Infrastructure)

- ✅ Docker Compose with 4 services
- ✅ Makefile targets (dev-bestays, dev-realestate, dev-both)
- ✅ Separate Clerk credentials
- ✅ Separate ports
- ✅ Environment file structure

### Added (Simple Separation)

- ✅ Separate DATABASE_URLs
- ✅ Two PostgreSQL databases (bestays_dev, realestate_dev)
- ✅ Database init script for multiple databases

---

## How It Works

### Running Bestays Only

```bash
make dev-bestays
```

**What happens:**
1. Docker starts: bestays-frontend, bestays-server, postgres, redis
2. Loads: .env.shared + .env.bestays
3. Backend connects to: `bestays_dev` database
4. Frontend connects to: http://localhost:8011
5. Users login via: sacred-mayfly-55.clerk.accounts.dev

### Running Real Estate Only

```bash
make dev-realestate
```

**What happens:**
1. Docker starts: realestate-frontend, realestate-server, postgres, redis
2. Loads: .env.shared + .env.realestate
3. Backend connects to: `realestate_dev` database
4. Frontend connects to: http://localhost:8012
5. Users login via: pleasant-gnu-25.clerk.accounts.dev

### Running Both Products

```bash
make dev-both
```

**What happens:**
1. Docker starts: All 6 services
2. Bestays runs on 5183/8011 → bestays_dev database
3. Real Estate runs on 5184/8012 → realestate_dev database
4. **No data sharing** (impossible - different databases)
5. **No code changes needed** (just different configs)

---

## Property Type Differentiation (Business Logic)

**Question:** How do products differ if using same code?

**Answer:** Property types are just data, not infrastructure.

### Property Model (No Changes Needed)

```python
class Property(Base):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    property_type: Mapped[str]  # "rental", "land", "villa", "business"
    # ... other fields
```

### Seeding Different Data

**Bestays Database:**
```sql
-- Rental properties only
INSERT INTO properties (title, property_type) VALUES
  ('Beach House', 'rental'),
  ('Mountain Cabin', 'rental');
```

**Real Estate Database:**
```sql
-- High-value properties
INSERT INTO properties (title, property_type) VALUES
  ('Commercial Land', 'land'),
  ('Luxury Villa', 'villa'),
  ('Business Complex', 'business');
```

**No code changes needed** - just different data in different databases.

---

## Implementation Steps

### Step 1: Update docker-compose.dev.yml

**Change:**
```yaml
postgres:
  environment:
    POSTGRES_MULTIPLE_DATABASES: bestays_dev,realestate_dev
  volumes:
    - ./docker/postgres/create-multiple-databases.sh:/docker-entrypoint-initdb.d/create-databases.sh
```

### Step 2: Create Database Init Script

**File:** `docker/postgres/create-multiple-databases.sh`

### Step 3: Update .env Files

**Remove from both .env.bestays and .env.realestate:**
```bash
PRODUCT=bestays  # DELETE - not needed
```

**Ensure each has separate DATABASE_URL:**
- .env.bestays → bestays_dev
- .env.realestate → realestate_dev

### Step 4: Test

```bash
# Clean start
make down
docker volume rm bestays_postgres_data_dev

# Run Bestays only
make dev-bestays
# Test: http://localhost:5183
# Login: user.claudecode@bestays.app

# Stop, then run Real Estate only
make down
make dev-realestate
# Test: http://localhost:5184
# Login: user.claudecode@realestate.dev

# Run both together
make dev-both
# Both accessible simultaneously
```

---

## Benefits of This Approach

### Simplicity
- ✅ **No multi-tenant code** - just run app twice
- ✅ **No filtering logic** - impossible to query wrong database
- ✅ **No middleware** - standard FastAPI app
- ✅ **Easy to understand** - separate instances, separate data

### Safety
- ✅ **Zero risk of data leakage** - physically separate databases
- ✅ **No forgotten filters** - can't accidentally query wrong data
- ✅ **Clear separation** - each product is truly independent

### Maintainability
- ✅ **Same codebase** - DRY principle maintained
- ✅ **Standard patterns** - no custom multi-tenancy
- ✅ **Easy testing** - test one app, both products work
- ✅ **Future monorepo** - can extract shared packages later

---

## Future: Monorepo with Shared Packages (Optional)

**When to consider:**
- When chat/FAQ/auth need to be extracted as sellable packages
- When products start diverging significantly
- When team grows and needs separate ownership

**Monorepo structure (future):**
```
packages/
  shared-auth/     # Clerk wrapper
  shared-chat/     # Chat feature
  shared-faq/      # FAQ feature

apps/
  bestays/
    frontend/
    server/
  realestate/
    frontend/
    server/
```

**For now:** Keep current simple approach. Refactor later if needed.

---

## Test Credentials

### Bestays Product

| Email | Password | Role |
|-------|----------|------|
| user.claudecode@bestays.app | 9kB*k926O8): | user |
| admin.claudecode@bestays.app | rHe/997?lo&l | admin |
| agent.claudecode@bestays.app | y>1T;)5s!X1X | agent |

### Real Estate Product

| Email | Password | Role |
|-------|----------|------|
| user.claudecode@realestate.dev | y>1T_)5h!X1X | user |
| admin.claudecode@realestate.dev | rHe/997?lo&l | admin |
| agent.claudecode@realestate.dev | y>1T;)5s!X1X | agent |

---

## Summary

**Simple is better.**

Instead of:
- ❌ Multi-tenant architecture
- ❌ Product filtering
- ❌ Complex middleware

We use:
- ✅ Same app, different configs
- ✅ Separate databases
- ✅ Zero complexity

**Code changes needed:** ~50 lines (docker-compose + init script)
**Code complexity added:** Zero
**Risk of data leakage:** Impossible

---

**Document Version:** 1.0
**Created:** 2025-11-08
**Status:** APPROVED (correct approach)

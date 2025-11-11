# Local Multi-Product Development Environment

**Date:** 2025-11-07
**Purpose:** Enable running both Bestays and Real Estate products simultaneously in local development
**Scope:** Development environment only (not production deployment)
**Related Story:** US-018 (subset - immediate dev environment needs)

---

## Overview

Enable developers to run **both products (Bestays + Real Estate) simultaneously** from the same codebase using environment-based configuration.

**Key Requirements:**
1. Single codebase (`apps/frontend`, `apps/server`)
2. Environment-based product selection (PRODUCT env var)
3. Separate Clerk instances per product
4. Simple Makefile commands (`make dev-bestays`, `make dev-realestate`, `make dev-both`)
5. Separate terminal for each product (parallel development)

---

## Architecture Approach

**Strategy:** Environment-based multi-tenancy

### Current Architecture
```
apps/
├── frontend/        # Single SvelteKit app
└── server/          # Single FastAPI app
docker-compose.yml   # Single service config
.env                 # Single environment file
Makefile            # Single dev command
```

### Target Architecture
```
apps/
├── frontend/        # Same SvelteKit app (product-aware via env)
└── server/          # Same FastAPI app (product-aware via env)

docker-compose.yml   # 4 services (bestays-frontend, bestays-server, realestate-frontend, realestate-server)

.env.shared          # Common config (DATABASE_URL, REDIS_URL, OPENROUTER_API_KEY)
.env.bestays         # Bestays-specific (PRODUCT=bestays, Clerk keys, ports)
.env.realestate      # Realestate-specific (PRODUCT=realestate, Clerk keys, ports)

Makefile             # Multiple targets (dev-bestays, dev-realestate, dev-both)
```

---

## Configuration Files

### `.env.shared` (Common Configuration)

```bash
# Database (shared multi-tenant)
DATABASE_URL=postgresql://bestays:bestays@postgres:5432/bestays
POSTGRES_USER=bestays
POSTGRES_PASSWORD=bestays
POSTGRES_DB=bestays

# Redis (shared)
REDIS_URL=redis://redis:6379/0

# OpenRouter (shared)
OPENROUTER_API_KEY=<user-provided>

# Common settings
ENVIRONMENT=development
LOG_LEVEL=INFO
```

---

### `.env.bestays` (Bestays Product)

```bash
# Product identification
PRODUCT=bestays
PRODUCT_NAME=Bestays
PRODUCT_DOMAIN=bestays.app

# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_c2FjcmVkLW1heWZseS01NS5jbGVyay5hY2NvdW50cy5kZXYk
CLERK_SECRET_KEY=sk_test_vGrRuTLW1SdS2uQlDbv4l2T2WHpTk9IoervBmG9Vit

# Port configuration (Bestays)
FRONTEND_PORT=5183
BACKEND_PORT=8011

# Frontend public env vars
PUBLIC_PRODUCT=bestays
PUBLIC_API_URL=http://localhost:8011
PUBLIC_PRODUCT_NAME=Bestays

# Backend configuration
API_HOST=0.0.0.0
API_PORT=8011
CORS_ORIGINS=http://localhost:5183

# Branding/Theme (optional - for future)
PRIMARY_COLOR=#FF6B6B
LOGO_PATH=/logos/bestays-logo.svg
```

---

### `.env.realestate` (Real Estate Product)

```bash
# Product identification
PRODUCT=realestate
PRODUCT_NAME=Best Real Estate
PRODUCT_DOMAIN=realestate.dev

# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_cGxlYXNhbnQtZ251LTI1LmNsZXJrLmFjY291bnRzLmRldiQ
CLERK_SECRET_KEY=sk_test_GBG0pHIE015mIkiHfrpeOS4mi1hqNSm0uBUdlexgxS

# Port configuration (Real Estate)
FRONTEND_PORT=5184
BACKEND_PORT=8012

# Frontend public env vars
PUBLIC_PRODUCT=realestate
PUBLIC_API_URL=http://localhost:8012
PUBLIC_PRODUCT_NAME=Best Real Estate

# Backend configuration
API_HOST=0.0.0.0
API_PORT=8012
CORS_ORIGINS=http://localhost:5184

# Branding/Theme (optional - for future)
PRIMARY_COLOR=#4ECDC4
LOGO_PATH=/logos/realestate-logo.svg
```

---

## Docker Compose Configuration

### Service Architecture

**4 Services:**
1. `bestays-frontend` - Bestays SvelteKit (port 5183)
2. `bestays-server` - Bestays FastAPI (port 8011)
3. `realestate-frontend` - Real Estate SvelteKit (port 5184)
4. `realestate-server` - Real Estate FastAPI (port 8012)

**Shared Services:**
5. `postgres` - PostgreSQL (port 5433)
6. `redis` - Redis (port 6379)

### Environment Loading Strategy

Each service loads:
1. `.env.shared` (common config)
2. `.env.bestays` OR `.env.realestate` (product-specific)

**Example (Bestays Frontend):**
```yaml
bestays-frontend:
  env_file:
    - .env.shared
    - .env.bestays
  ports:
    - "5183:5183"
  environment:
    - VITE_PORT=5183
```

---

## Makefile Commands

### Target: `make dev-bestays`

**Purpose:** Run Bestays product only

**Services:**
- bestays-frontend (port 5183)
- bestays-server (port 8011)
- postgres (port 5433)
- redis (port 6379)

**Command:**
```bash
make dev-bestays
# Opens: http://localhost:5183
# API: http://localhost:8011/docs
```

---

### Target: `make dev-realestate`

**Purpose:** Run Real Estate product only

**Services:**
- realestate-frontend (port 5184)
- realestate-server (port 8012)
- postgres (port 5433)
- redis (port 6379)

**Command:**
```bash
make dev-realestate
# Opens: http://localhost:5184
# API: http://localhost:8012/docs
```

---

### Target: `make dev-both`

**Purpose:** Run both products simultaneously

**Services:** All 6 services

**Command:**
```bash
make dev-both
# Bestays: http://localhost:5183 | API: http://localhost:8011
# Real Estate: http://localhost:5184 | API: http://localhost:8012
```

---

### Target: `make logs-bestays`

**Purpose:** View Bestays logs only

**Command:**
```bash
make logs-bestays
# Filters logs for bestays-frontend and bestays-server
```

---

### Target: `make logs-realestate`

**Purpose:** View Real Estate logs only

**Command:**
```bash
make logs-realestate
# Filters logs for realestate-frontend and realestate-server
```

---

## Database Strategy

### Multi-Tenant with Product Context

**Approach:** Shared PostgreSQL database with `product` field

**Why:**
- Simpler for early development (single migration pipeline)
- Easy to split later if needed
- Standard multi-tenant pattern
- Shared schema evolution

**Schema Changes Required:**

1. Add `product` column to relevant tables:
```sql
ALTER TABLE users ADD COLUMN product VARCHAR(50) DEFAULT 'bestays';
ALTER TABLE properties ADD COLUMN product VARCHAR(50) DEFAULT 'bestays';
ALTER TABLE bookings ADD COLUMN product VARCHAR(50) DEFAULT 'bestays';
```

2. Add index for performance:
```sql
CREATE INDEX idx_users_product ON users(product);
CREATE INDEX idx_properties_product ON properties(product);
CREATE INDEX idx_bookings_product ON bookings(product);
```

3. Update queries to filter by product:
```python
# Before
users = session.query(User).all()

# After (with product context from env)
product = os.getenv("PRODUCT", "bestays")
users = session.query(User).filter(User.product == product).all()
```

---

## Backend Implementation

### Product Context Middleware

**File:** `apps/server/core/product_context.py`

```python
"""
Product Context Middleware

Extracts PRODUCT env var and adds to request state.
All queries automatically filter by product.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import os

class ProductContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Set product context from env
        request.state.product = os.getenv("PRODUCT", "bestays")
        response = await call_next(request)
        return response
```

**Integration:**
```python
# apps/server/main.py
from core.product_context import ProductContextMiddleware

app = FastAPI()
app.add_middleware(ProductContextMiddleware)
```

---

### Clerk Configuration per Product

**File:** `apps/server/core/clerk.py`

```python
"""
Clerk Configuration (Product-Aware)

Loads Clerk keys from environment (product-specific).
"""

import os
from clerk import Clerk

def get_clerk_client():
    """Get Clerk client with product-specific keys."""
    secret_key = os.getenv("CLERK_SECRET_KEY")
    if not secret_key:
        raise ValueError("CLERK_SECRET_KEY not set")

    return Clerk(secret_key=secret_key)
```

**Usage:**
```python
# No changes needed in endpoint code
# Clerk client automatically uses correct keys from env
clerk = get_clerk_client()
user = clerk.users.get(user_id)
```

---

## Frontend Implementation

### Product Detection

**File:** `apps/frontend/src/lib/config.ts`

```typescript
/**
 * Product Configuration
 *
 * Detects product from PUBLIC_PRODUCT env var.
 */

export const PRODUCT = import.meta.env.PUBLIC_PRODUCT || 'bestays';
export const PRODUCT_NAME = import.meta.env.PUBLIC_PRODUCT_NAME || 'Bestays';
export const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8011';

export const config = {
  product: PRODUCT,
  productName: PRODUCT_NAME,
  apiUrl: API_URL,
  clerkPublishableKey: import.meta.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY,
};
```

---

### Clerk Integration (Product-Aware)

**File:** `apps/frontend/src/routes/+layout.svelte`

```svelte
<script lang="ts">
  import { ClerkProvider } from '@clerk/clerk-svelte';
  import { config } from '$lib/config';

  // Clerk uses product-specific publishable key from env
  const clerkPublishableKey = config.clerkPublishableKey;
</script>

<ClerkProvider {clerkPublishableKey}>
  <slot />
</ClerkProvider>
```

**No changes needed** - Clerk automatically uses correct keys from environment.

---

## Test Credentials

### Bestays Product

**Clerk Instance:** sacred-mayfly-55.clerk.accounts.dev

| Email | Password | Role |
|-------|----------|------|
| user.claudecode@bestays.app | 9kB*k926O8): | user |
| admin.claudecode@bestays.app | rHe/997?lo&l | admin |
| agent.claudecode@bestays.app | y>1T;)5s!X1X | agent |

### Real Estate Product

**Clerk Instance:** pleasant-gnu-25.clerk.accounts.dev

| Email | Password | Role |
|-------|----------|------|
| user.claudecode@realestate.dev | y>1T_)5h!X1X | user |
| admin.claudecode@realestate.dev | rHe/997?lo&l | admin |
| agent.claudecode@realestate.dev | y>1T;)5s!X1X | agent |

### Role Setup (Manual)

After authentication, roles need to be set in database:

```sql
-- Bestays admin
UPDATE users SET role = 'admin' WHERE email = 'admin.claudecode@bestays.app' AND product = 'bestays';

-- Bestays agent
UPDATE users SET role = 'agent' WHERE email = 'agent.claudecode@bestays.app' AND product = 'bestays';

-- Real Estate admin
UPDATE users SET role = 'admin' WHERE email = 'admin.claudecode@realestate.dev' AND product = 'realestate';

-- Real Estate agent
UPDATE users SET role = 'agent' WHERE email = 'agent.claudecode@realestate.dev' AND product = 'realestate';
```

---

## Implementation Plan

### Phase 1: Environment Configuration (devops-infra)

**Tasks:**
1. Create `.env.shared` with common config
2. Create `.env.bestays` with Bestays Clerk keys and ports
3. Create `.env.realestate` with Real Estate Clerk keys and ports
4. Update `.env.example` with multi-product template
5. Add `.env.bestays` and `.env.realestate` to `.gitignore` (if not already)

---

### Phase 2: Docker Compose Configuration (devops-infra)

**Tasks:**
1. Update `docker-compose.yml` to define 4 services (bestays-frontend, bestays-server, realestate-frontend, realestate-server)
2. Configure env_file loading (shared + product-specific)
3. Update port mappings (5183/8011 for Bestays, 5184/8012 for Real Estate)
4. Ensure postgres and redis are shared services

---

### Phase 3: Makefile Targets (devops-infra)

**Tasks:**
1. Add `dev-bestays` target (up bestays services only)
2. Add `dev-realestate` target (up realestate services only)
3. Add `dev-both` target (up all services)
4. Add `logs-bestays` target (filter logs)
5. Add `logs-realestate` target (filter logs)
6. Update `down` target to stop all services

---

### Phase 4: Backend Product Context (dev-backend-fastapi)

**Tasks:**
1. Create `apps/server/core/product_context.py` middleware
2. Integrate middleware in `apps/server/main.py`
3. Update Clerk configuration to use env-based keys
4. Add database migration for `product` column
5. Update SQLAlchemy models with `product` field
6. Update queries to filter by product context

---

### Phase 5: Frontend Product Detection (dev-frontend-svelte)

**Tasks:**
1. Create `apps/frontend/src/lib/config.ts` for product detection
2. Update Clerk integration to use env-based publishable key
3. Update API client to use env-based API URL
4. (Optional) Add product-specific theming support

---

### Phase 6: Testing

**Tasks:**
1. Test `make dev-bestays` (login with bestays credentials)
2. Test `make dev-realestate` (login with realestate credentials)
3. Test `make dev-both` (both products running simultaneously)
4. Verify Clerk authentication working per product
5. Verify database isolation (product filtering working)
6. Document manual role setup steps

---

## Success Criteria

- [ ] `make dev-bestays` runs Bestays on ports 5183/8011
- [ ] `make dev-realestate` runs Real Estate on ports 5184/8012
- [ ] `make dev-both` runs both products simultaneously
- [ ] Login with bestays credentials works on port 5183
- [ ] Login with realestate credentials works on port 5184
- [ ] Database queries filter by product automatically
- [ ] No data leakage between products
- [ ] Documentation updated (README, CLAUDE.md)

---

## Future Enhancements (Out of Scope)

- Product-specific branding/theming
- Separate databases (data isolation)
- Production deployment strategy (US-018)
- Full monorepo transformation (US-018)
- Automated role setup via seed script
- CI/CD pipeline for multiple products

---

## Risk Mitigation

**Risk:** Environment variable conflicts
**Mitigation:** Use clear naming (PRODUCT, FRONTEND_PORT, BACKEND_PORT)

**Risk:** Port conflicts with existing services
**Mitigation:** Use non-standard ports (5183/5184, 8011/8012)

**Risk:** Database data contamination
**Mitigation:** Add `product` column and index, filter all queries

**Risk:** Clerk credential mix-up
**Mitigation:** Separate env files, clear naming, documentation

---

**Document Version:** 1.0
**Created:** 2025-11-07
**Next Steps:** Spawn devops-infra agent to implement Phase 1-3

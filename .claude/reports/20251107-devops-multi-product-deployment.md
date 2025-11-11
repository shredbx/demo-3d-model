# DevOps Multi-Product Deployment Strategy

**Date:** 2025-11-07
**Author:** devops-infra agent
**Context:** Multi-product workflow decision (bestays.app + Real Estate product)
**Status:** RECOMMENDATIONS

---

## Executive Summary

**Recommended Approach:** **Task-Based Deployment Tracking with Product Tagging**

**Key DevOps Recommendations:**
1. **Deployment Tracking** - Git commits + task references provide sufficient traceability
2. **Infrastructure** - Separate containers per product with shared PostgreSQL instance
3. **CI/CD** - Product-aware pipelines filtering by task semantic names
4. **Monitoring** - Product tags in metrics, logs, and error tracking
5. **Risk Mitigation** - Branch naming validation prevents cross-product contamination

**Confidence Level:** HIGH - Aligns with existing architecture decisions (TASK-002, TASK-003, TASK-004, TASK-005)

---

## 1. Deployment Tracking

### Current System Analysis

**What We Have:**
- Git commits reference tasks: `feat: implement login (US-001 TASK-001-login-bestays)`
- Task STATE.json contains product context (via semantic name)
- Branch names include task semantic names: `feat/TASK-001-login-bestays-US-001`

**What We Need:**
- Ability to identify which product a deployment affects
- Clear audit trail for production deployments
- Rollback capability per product

### Recommended Approach: Leverage Existing Task System

**Why Git Commits Are Sufficient:**

```
Commit Message:
feat: implement login flow (US-001 TASK-001-login-bestays)

Subagent: dev-frontend-svelte
Product: bestays
Files: apps/frontend/src/routes/login/+page.svelte

Story: US-001
Task: TASK-001-login-bestays
```

**Product Identification:**
1. **Task semantic name** contains product: `login-bestays` vs `port-login-realestate`
2. **Product field** in commit message body (optional but recommended)
3. **Task STATE.json** documents product context

**Deployment Traceability:**

```bash
# Find all commits for Bestays product
git log --all --grep="bestays" --oneline

# Find all commits for Real Estate product
git log --all --grep="realestate" --oneline

# Find commits for specific task
git log --all --grep="TASK-001-login-bestays" --oneline
```

**Verdict:** ✅ **Git commits + task references are SUFFICIENT** - No additional deployment tracking system needed.

---

## 2. Infrastructure Architecture

### Current State (Single Product)

```yaml
docker-compose.dev.yml:
services:
  postgres:       # Single database: bestays_dev
  server:         # FastAPI on port 8011
  frontend:       # SvelteKit on port 5183
  redis:          # Port 6379
```

### Recommended Architecture (Multi-Product)

**Align with TASK-002 Database Isolation Strategy:**

```yaml
docker-compose.dev.yml:
services:
  # ==========================================================================
  # Shared Infrastructure
  # ==========================================================================
  postgres:
    container_name: bestays-postgres-dev
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - ./docker/postgres/init-multi-db.sql:/docker-entrypoint-initdb.d/init.sql:ro
    ports:
      - "5433:5432"  # Keep existing port mapping
    # Creates TWO databases: bestays_dev, realestate_dev

  redis:
    container_name: bestays-redis-dev
    ports:
      - "6379:6379"
    # Both products use different Redis DB numbers (0, 1)

  # ==========================================================================
  # Bestays Product (Existing)
  # ==========================================================================
  bestays-server:
    container_name: bestays-server-dev
    environment:
      APP_NAME: BeStays
      PRODUCT_ID: bestays
      DATABASE_URL: postgresql+asyncpg://bestays_user:bestays_password@postgres:5432/bestays_dev
      REDIS_URL: redis://redis:6379/0
      REDIS_KEY_PREFIX: bestays:
      CLERK_SECRET_KEY: ${CLERK_SECRET_KEY}
      FRONTEND_URL: http://localhost:5183
    ports:
      - "8011:8011"  # Keep existing port
    volumes:
      - ./apps/server:/app:delegated

  bestays-frontend:
    container_name: bestays-frontend-dev
    environment:
      VITE_API_URL: http://localhost:8011
      VITE_PRODUCT_ID: bestays
      VITE_CLERK_PUBLISHABLE_KEY: ${VITE_CLERK_PUBLISHABLE_KEY}
    ports:
      - "5183:5183"  # Keep existing port
    volumes:
      - ./apps/frontend:/app:delegated

  # ==========================================================================
  # Real Estate Product (New)
  # ==========================================================================
  realestate-server:
    container_name: realestate-server-dev
    environment:
      APP_NAME: Best Real Estate
      PRODUCT_ID: realestate
      DATABASE_URL: postgresql+asyncpg://realestate_user:realestate_password@postgres:5432/realestate_dev
      REDIS_URL: redis://redis:6379/1
      REDIS_KEY_PREFIX: realestate:
      CLERK_SECRET_KEY: ${REALESTATE_CLERK_SECRET_KEY}
      FRONTEND_URL: http://localhost:5184
    ports:
      - "8012:8011"  # Different host port, same container port
    volumes:
      - ./apps/server:/app:delegated

  realestate-frontend:
    container_name: realestate-frontend-dev
    environment:
      VITE_API_URL: http://localhost:8012
      VITE_PRODUCT_ID: realestate
      VITE_CLERK_PUBLISHABLE_KEY: ${REALESTATE_CLERK_PUBLISHABLE_KEY}
    ports:
      - "5184:5183"  # Different host port, same container port
    volumes:
      - ./apps/frontend:/app:delegated
```

**Key Design Decisions:**

1. **Separate Containers per Product**
   - ✅ Clear product isolation
   - ✅ Independent scaling (future)
   - ✅ Independent deployment (production)
   - ✅ Different environment variables per product

2. **Shared PostgreSQL Instance** (from TASK-002)
   - ✅ Cost-effective for development
   - ✅ Two databases: `bestays_dev`, `realestate_dev`
   - ✅ Complete data isolation
   - ✅ Same approach as architecture synthesis

3. **Shared Redis, Different DB Numbers**
   - ✅ Bestays uses DB 0 (`redis://redis:6379/0`)
   - ✅ Real Estate uses DB 1 (`redis://redis:6379/1`)
   - ✅ Key prefixes prevent collisions (`bestays:`, `realestate:`)

4. **Port Mapping Strategy**
   - Bestays: 8011 (backend), 5183 (frontend)
   - Real Estate: 8012 (backend), 5184 (frontend)
   - PostgreSQL: 5433 (existing mapping to avoid host conflicts)
   - Redis: 6379 (shared)

### Environment Variables Strategy

**Current:** Single `.env` file

**Recommended:** Product-scoped environment variables

**.env (Development):**
```bash
# ==========================================================================
# Shared Configuration
# ==========================================================================
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# ==========================================================================
# Bestays Product
# ==========================================================================
CLERK_SECRET_KEY=sk_test_vGrRuTLW1SdS2uQlDbv4l2T2WHpTk9IoervBmG9Vit
VITE_CLERK_PUBLISHABLE_KEY=pk_test_c2FjcmVkLW1heWZseS01NS5jbGVyay5hY2NvdW50cy5kZXYk

# LLM Configuration (Bestays)
OPENROUTER_API_KEY=sk-or-v1-...
LLM_CHAT_MODEL=anthropic/claude-3-sonnet

# ==========================================================================
# Real Estate Product
# ==========================================================================
REALESTATE_CLERK_SECRET_KEY=sk_test_GBG0pHIE015mIkiHfrpeOS4mi1hqNSm0uBUdlexgxS
REALESTATE_CLERK_PUBLISHABLE_KEY=pk_test_cGxlYXNhbnQtZ251LTI1LmNsZXJrLmFjY291bnRzLmRldiQ

# LLM Configuration (Real Estate) - can share or separate
REALESTATE_OPENROUTER_API_KEY=sk-or-v1-...  # Optional: separate budget tracking
REALESTATE_LLM_CHAT_MODEL=anthropic/claude-3-sonnet
```

**Why Single .env File (Development):**
- ✅ Simple to manage (one file)
- ✅ Easy to share between products (shared OpenRouter key)
- ✅ Clear product prefixes (REALESTATE_*)

**Production:** Separate `.env.bestays` and `.env.realestate` for security isolation

---

## 3. CI/CD Pipeline Strategy

### Deployment Flow

**Goal:** Deploy correct product based on task semantic name

**Approach:** Extract product from commit message + task semantic name

### GitHub Actions Workflow (Example)

```yaml
# .github/workflows/deploy.yml

name: Deploy

on:
  push:
    branches:
      - main

jobs:
  detect-product:
    runs-on: ubuntu-latest
    outputs:
      products: ${{ steps.detect.outputs.products }}
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 2  # Fetch last 2 commits

      - name: Detect affected products
        id: detect
        run: |
          # Get commit message
          COMMIT_MSG=$(git log -1 --pretty=%B)

          # Extract task semantic name
          TASK=$(echo "$COMMIT_MSG" | grep -oP 'TASK-\d+-[a-z-]+')

          PRODUCTS=""

          # Check if task semantic name contains product
          if echo "$TASK" | grep -q "bestays"; then
            PRODUCTS="bestays"
          elif echo "$TASK" | grep -q "realestate"; then
            PRODUCTS="realestate"
          elif echo "$TASK" | grep -q "port-.*-realestate"; then
            # Porting task - target product is realestate
            PRODUCTS="realestate"
          else
            # Default to bestays for backward compatibility
            PRODUCTS="bestays"
          fi

          echo "products=$PRODUCTS" >> $GITHUB_OUTPUT
          echo "Detected products: $PRODUCTS"

  deploy-bestays:
    needs: detect-product
    if: contains(needs.detect-product.outputs.products, 'bestays')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy Bestays
        run: |
          echo "Deploying Bestays..."
          # SSH to VPS
          # docker-compose -f docker-compose.prod.yml up -d bestays-server bestays-frontend

      - name: Tag deployment
        run: |
          git tag "bestays-deploy-$(date +%Y%m%d-%H%M%S)"
          git push --tags

  deploy-realestate:
    needs: detect-product
    if: contains(needs.detect-product.outputs.products, 'realestate')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy Real Estate
        run: |
          echo "Deploying Real Estate..."
          # SSH to VPS
          # docker-compose -f docker-compose.prod.yml up -d realestate-server realestate-frontend

      - name: Tag deployment
        run: |
          git tag "realestate-deploy-$(date +%Y%m%d-%H%M%S)"
          git push --tags
```

### Product Detection Logic

**Rules:**
1. If task semantic name contains `bestays` → Deploy to Bestays
2. If task semantic name contains `realestate` → Deploy to Real Estate
3. If task semantic name contains `port-*-realestate` → Deploy to Real Estate (porting task)
4. Default → Deploy to Bestays (backward compatibility)

**Examples:**

| Task Semantic Name | Product Deployed | Reason |
|--------------------|------------------|--------|
| `TASK-001-login-bestays` | bestays | Contains "bestays" |
| `TASK-050-port-login-realestate` | realestate | Porting task, target is realestate |
| `TASK-002-database-schema` | bestays | No product specified, default to bestays |
| `TASK-051-property-search-realestate` | realestate | Contains "realestate" |

### Deployment Order (Porting Tasks)

**Scenario:** Porting login from Bestays to Real Estate

**Task Flow:**
1. `TASK-001-login-bestays` (initial implementation) → Deploy to Bestays
2. `TASK-050-port-login-realestate` (porting task) → Deploy to Real Estate

**CI/CD Behavior:**
- Step 1: Deploy `TASK-001-login-bestays` → Only Bestays containers restart
- Step 2: Deploy `TASK-050-port-login-realestate` → Only Real Estate containers restart

**Verdict:** ✅ **Task semantic names provide enough context for CI/CD filtering**

---

## 4. Monitoring and Logging

### Metrics Tagging

**Strategy:** Tag all metrics with product ID

**Prometheus Metrics Example:**

```python
# packages/shared-core/src/metrics.py

from prometheus_client import Counter, Histogram

# HTTP request counter with product label
http_requests = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['product', 'method', 'endpoint', 'status']
)

# API response time with product label
api_response_time = Histogram(
    'api_response_seconds',
    'API response time',
    ['product', 'endpoint']
)

# LLM token usage with product label
llm_tokens_used = Counter(
    'llm_tokens_total',
    'Total LLM tokens used',
    ['product', 'model']
)

# Usage in FastAPI middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    product_id = settings.PRODUCT_ID  # "bestays" or "realestate"

    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    # Record metrics with product tag
    http_requests.labels(
        product=product_id,
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    api_response_time.labels(
        product=product_id,
        endpoint=request.url.path
    ).observe(duration)

    return response
```

**Grafana Dashboard:**
```
Panel 1: HTTP Requests per Product
Query: sum by (product) (rate(http_requests_total[5m]))

Panel 2: API Response Time per Product
Query: histogram_quantile(0.95, rate(api_response_seconds_bucket[5m]))
Filter by: product=bestays, product=realestate

Panel 3: LLM Token Usage per Product
Query: sum by (product, model) (llm_tokens_total)
```

### Error Tracking

**Strategy:** Separate error tracking dashboards per product

**Sentry Integration:**

```python
# apps/bestays-api/app/main.py

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/project-id",
    environment=settings.ENVIRONMENT,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    integrations=[FastApiIntegration()],
    # Tag all errors with product
    before_send=lambda event, hint: {
        **event,
        "tags": {
            **event.get("tags", {}),
            "product": settings.PRODUCT_ID,  # "bestays" or "realestate"
        }
    }
)
```

**Sentry Filters:**
- Filter by `product:bestays` → Bestays errors only
- Filter by `product:realestate` → Real Estate errors only

### Deployment Logs

**Strategy:** Reference task IDs in deployment logs

**Example Deployment Log:**

```
2025-11-07 14:30:00 [INFO] Deployment started
2025-11-07 14:30:01 [INFO] Product: bestays
2025-11-07 14:30:01 [INFO] Task: TASK-001-login-bestays
2025-11-07 14:30:01 [INFO] Commit: a3f4b2c feat: implement login (US-001 TASK-001-login-bestays)
2025-11-07 14:30:05 [INFO] Building Docker image: bestays-server:latest
2025-11-07 14:30:30 [INFO] Stopping container: bestays-server-prod
2025-11-07 14:30:35 [INFO] Starting container: bestays-server-prod
2025-11-07 14:30:40 [INFO] Health check: PASSED
2025-11-07 14:30:40 [INFO] Deployment complete (40 seconds)
2025-11-07 14:30:40 [INFO] Tagged: bestays-deploy-20251107-143040
```

**Searchable by:**
- Product: `product:bestays`
- Task: `TASK-001-login-bestays`
- Git commit: `a3f4b2c`
- Deployment tag: `bestays-deploy-20251107-143040`

**Verdict:** ✅ **Task IDs in logs provide full traceability**

---

## 5. Risk Mitigation

### Risk 1: Deploying Bestays Code to Real Estate (Cross-Product Contamination)

**Scenario:** Developer commits code for Bestays but forgets to update task semantic name

**Example:**
```bash
# BAD: Generic task name, no product context
git commit -m "feat: update login flow (US-001 TASK-002-update-login)"

# CI/CD can't determine product → defaults to Bestays
# If code was meant for Real Estate → WRONG PRODUCT DEPLOYED
```

**Mitigation 1: Pre-commit Hook (Git)**

```python
# .git/hooks/pre-commit

import sys
import re

def validate_commit_message():
    """Ensure commit message includes product in task semantic name."""
    with open('.git/COMMIT_EDITMSG', 'r') as f:
        commit_msg = f.read()

    # Extract task semantic name
    match = re.search(r'TASK-\d+-([a-z-]+)', commit_msg)
    if not match:
        print("❌ ERROR: Commit message must reference a task (TASK-XXX-semantic-name)")
        sys.exit(1)

    task_semantic = match.group(1)

    # Check if product is specified
    if 'bestays' not in task_semantic and 'realestate' not in task_semantic:
        print("⚠️  WARNING: Task semantic name does not contain product.")
        print(f"    Task: TASK-XXX-{task_semantic}")
        print("    Expected: TASK-XXX-{feature}-bestays OR TASK-XXX-{feature}-realestate")
        print("    Or: TASK-XXX-port-{feature}-realestate")

        response = input("    Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)

if __name__ == '__main__':
    validate_commit_message()
```

**Mitigation 2: Branch Naming Validation (Existing)**

✅ Already implemented in `.sdlc-workflow/scripts/validate_branch.py`
✅ PreToolUse hook validates branch names before operations

**Mitigation 3: CI/CD Explicit Product Tagging**

Add explicit product tag to commit message body:

```
feat: implement login flow (US-001 TASK-001-login-bestays)

Subagent: dev-frontend-svelte
Product: bestays  # <-- EXPLICIT TAG
Files: apps/frontend/src/routes/login/+page.svelte

Story: US-001
Task: TASK-001-login-bestays
```

CI/CD checks:
1. Extract product from task semantic name
2. Validate against `Product:` field in commit body
3. If mismatch → fail CI/CD pipeline

**Verdict:** ✅ **Existing validation hooks + CI/CD checks prevent cross-product contamination**

---

### Risk 2: Shared Database Accidental Queries

**Scenario:** Backend code accidentally queries wrong database

**Example:**
```python
# BAD: Hardcoded database name
engine = create_async_engine("postgresql://user:pass@host/bestays_dev")

# If this code runs in Real Estate container → queries Bestays database!
```

**Mitigation: Environment-Based Configuration (from TASK-002)**

✅ Already implemented in architecture synthesis:

```python
# apps/bestays-api/app/config.py
class BestaysSettings(DatabaseSettings):
    PRODUCT_ID: str = "bestays"
    DATABASE_URL: PostgresDsn  # Set via environment variable

# Docker Compose ensures correct DATABASE_URL per container
bestays-server:
  environment:
    DATABASE_URL: postgresql+asyncpg://bestays_user:pass@postgres:5432/bestays_dev

realestate-server:
  environment:
    DATABASE_URL: postgresql+asyncpg://realestate_user:pass@postgres:5432/realestate_dev
```

**Why This Works:**
- ✅ Each container gets different DATABASE_URL
- ✅ Application code uses `settings.DATABASE_URL` (no hardcoding)
- ✅ Impossible to query wrong database (connection string is wrong database)

**Verdict:** ✅ **Environment-based configuration prevents wrong database access**

---

### Risk 3: Deployment Rollback Complexity

**Scenario:** Real Estate deployment fails, need to rollback

**Challenge:** Both products in same monorepo, how to rollback only one?

**Solution: Product-Specific Docker Images + Git Tags**

**Deployment Tags:**
```bash
# Bestays deployments
git tag bestays-deploy-20251107-143000
git tag bestays-deploy-20251107-150000

# Real Estate deployments
git tag realestate-deploy-20251107-144000
git tag realestate-deploy-20251107-151000
```

**Rollback Process:**

```bash
# Rollback Real Estate to previous deployment
PREV_TAG=$(git tag -l "realestate-deploy-*" | tail -2 | head -1)

# Checkout previous version
git checkout $PREV_TAG

# Rebuild and redeploy ONLY Real Estate
docker-compose -f docker-compose.prod.yml build realestate-server realestate-frontend
docker-compose -f docker-compose.prod.yml up -d realestate-server realestate-frontend

# Verify
curl http://localhost:8102/api/health
```

**Why This Works:**
- ✅ Git tags track deployments per product
- ✅ Docker Compose can rebuild/restart single product
- ✅ Bestays containers keep running (unaffected by Real Estate rollback)
- ✅ Database rollback: Use product-specific backup (`realestate_db_backup_*.sql`)

**Automated Rollback Script:**

```bash
#!/bin/bash
# scripts/rollback-product.sh

PRODUCT=$1  # "bestays" or "realestate"
PREVIOUS_TAG=$(git tag -l "${PRODUCT}-deploy-*" | tail -2 | head -1)

if [ -z "$PREVIOUS_TAG" ]; then
  echo "❌ No previous deployment found for $PRODUCT"
  exit 1
fi

echo "Rolling back $PRODUCT to $PREVIOUS_TAG"

# Checkout previous tag
git checkout $PREVIOUS_TAG

# Rebuild Docker images
docker-compose -f docker-compose.prod.yml build ${PRODUCT}-server ${PRODUCT}-frontend

# Restart containers
docker-compose -f docker-compose.prod.yml up -d ${PRODUCT}-server ${PRODUCT}-frontend

# Verify health
sleep 10
HEALTH_URL="http://localhost:$( [ "$PRODUCT" = "bestays" ] && echo 8011 || echo 8012 )/api/health"
curl -f $HEALTH_URL || {
  echo "❌ Health check failed. Manual intervention required."
  exit 1
}

echo "✅ Rollback complete: $PRODUCT → $PREVIOUS_TAG"
```

**Verdict:** ✅ **Product-specific tags + Docker Compose enable independent rollbacks**

---

## 6. Production Deployment Architecture

### VPS Deployment Strategy

**Recommended:** Single VPS with Docker Compose (aligned with simplicity priority)

**Why Single VPS:**
- ✅ Simple to manage (one server)
- ✅ Cost-effective (no multiple VPS bills)
- ✅ Shared PostgreSQL instance (as per TASK-002)
- ✅ Easy to scale later (move to separate VPS if needed)

**Production Docker Compose:**

```yaml
# docker-compose.prod.yml

services:
  postgres:
    image: postgres:16-alpine
    container_name: bestays-postgres-prod
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init-multi-db-prod.sql:/docker-entrypoint-initdb.d/init.sql:ro
    restart: always

  redis:
    image: redis:7-alpine
    container_name: bestays-redis-prod
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: always

  bestays-server:
    build:
      context: .
      dockerfile: docker/server/Dockerfile.prod
    container_name: bestays-server-prod
    environment:
      PRODUCT_ID: bestays
      DATABASE_URL: postgresql+asyncpg://bestays_user:${BESTAYS_DB_PASSWORD}@postgres:5432/bestays_prod
      CLERK_SECRET_KEY: ${BESTAYS_CLERK_SECRET_KEY}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      REDIS_KEY_PREFIX: bestays:
    ports:
      - "8011:8011"
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G

  realestate-server:
    build:
      context: .
      dockerfile: docker/server/Dockerfile.prod
    container_name: realestate-server-prod
    environment:
      PRODUCT_ID: realestate
      DATABASE_URL: postgresql+asyncpg://realestate_user:${REALESTATE_DB_PASSWORD}@postgres:5432/realestate_prod
      CLERK_SECRET_KEY: ${REALESTATE_CLERK_SECRET_KEY}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/1
      REDIS_KEY_PREFIX: realestate:
    ports:
      - "8012:8011"
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G

  bestays-frontend:
    build:
      context: .
      dockerfile: docker/frontend/Dockerfile.prod
      args:
        VITE_API_URL: https://api.bestays.app
        VITE_PRODUCT_ID: bestays
        VITE_CLERK_PUBLISHABLE_KEY: ${BESTAYS_CLERK_PUBLISHABLE_KEY}
    container_name: bestays-frontend-prod
    restart: always

  realestate-frontend:
    build:
      context: .
      dockerfile: docker/frontend/Dockerfile.prod
      args:
        VITE_API_URL: https://api.realestate.app
        VITE_PRODUCT_ID: realestate
        VITE_CLERK_PUBLISHABLE_KEY: ${REALESTATE_CLERK_PUBLISHABLE_KEY}
    container_name: realestate-frontend-prod
    restart: always

  nginx:
    image: nginx:alpine
    container_name: bestays-nginx-prod
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./docker/nginx/ssl:/etc/nginx/ssl:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - bestays-server
      - realestate-server
      - bestays-frontend
      - realestate-frontend
    restart: always

volumes:
  postgres_data:
  redis_data:
```

**Nginx Routing (Product Separation):**

```nginx
# docker/nginx/nginx.conf

# Bestays Backend API
server {
    listen 443 ssl;
    server_name api.bestays.app;

    ssl_certificate /etc/nginx/ssl/bestays.crt;
    ssl_certificate_key /etc/nginx/ssl/bestays.key;

    location / {
        proxy_pass http://bestays-server-prod:8011;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Real Estate Backend API
server {
    listen 443 ssl;
    server_name api.realestate.app;

    ssl_certificate /etc/nginx/ssl/realestate.crt;
    ssl_certificate_key /etc/nginx/ssl/realestate.key;

    location / {
        proxy_pass http://realestate-server-prod:8012;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Bestays Frontend
server {
    listen 443 ssl;
    server_name bestays.app www.bestays.app;

    ssl_certificate /etc/nginx/ssl/bestays.crt;
    ssl_certificate_key /etc/nginx/ssl/bestays.key;

    location / {
        proxy_pass http://bestays-frontend-prod:80;
        proxy_set_header Host $host;
    }
}

# Real Estate Frontend
server {
    listen 443 ssl;
    server_name realestate.app www.realestate.app;

    ssl_certificate /etc/nginx/ssl/realestate.crt;
    ssl_certificate_key /etc/nginx/ssl/realestate.key;

    location / {
        proxy_pass http://realestate-frontend-prod:80;
        proxy_set_header Host $host;
    }
}
```

---

## 7. Deployment Workflow

### Manual Deployment (MVP)

**Step 1: Build Images**
```bash
# On VPS
cd /opt/bestays
git pull origin main

# Build all images
docker-compose -f docker-compose.prod.yml build
```

**Step 2: Restart Services**
```bash
# Restart all services
docker-compose -f docker-compose.prod.yml up -d

# Or restart specific product
docker-compose -f docker-compose.prod.yml up -d bestays-server bestays-frontend
```

**Step 3: Run Migrations**
```bash
# Bestays migrations
docker exec bestays-server-prod alembic upgrade head

# Real Estate migrations
docker exec realestate-server-prod alembic upgrade head
```

**Step 4: Verify**
```bash
# Health checks
curl https://api.bestays.app/api/health
curl https://api.realestate.app/api/health

# Check logs
docker-compose -f docker-compose.prod.yml logs -f bestays-server
```

### Automated Deployment (GitHub Actions)

**Trigger:** Push to `main` branch

**Workflow:**
1. Extract product from commit message
2. SSH to VPS
3. Pull latest code
4. Rebuild Docker images for affected product
5. Restart containers for affected product
6. Run migrations for affected product
7. Verify health checks
8. Tag deployment in git

---

## 8. Backup and Recovery

### Backup Strategy (Per Product)

**Daily Automated Backups:**

```bash
# /etc/cron.d/bestays-backups

# Backup Bestays database daily at 2 AM
0 2 * * * /opt/bestays/scripts/backup-db.sh bestays

# Backup Real Estate database daily at 3 AM
0 3 * * * /opt/bestays/scripts/backup-db.sh realestate

# Clean old backups (keep 30 days)
0 4 * * * find /backups -name "*.gz" -mtime +30 -delete
```

**Backup Script:**

```bash
#!/bin/bash
# scripts/backup-db.sh

PRODUCT=$1  # "bestays" or "realestate"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/${PRODUCT}"
BACKUP_FILE="${BACKUP_DIR}/${PRODUCT}_db_${TIMESTAMP}.sql.gz"

mkdir -p $BACKUP_DIR

# Backup database
docker exec bestays-postgres-prod pg_dump \
  -U postgres \
  -d ${PRODUCT}_prod \
  --format=plain \
  | gzip > $BACKUP_FILE

echo "✅ Backup saved: $BACKUP_FILE"

# Upload to S3 (optional)
# aws s3 cp $BACKUP_FILE s3://bestays-backups/${PRODUCT}/
```

**Restore Script:**

```bash
#!/bin/bash
# scripts/restore-db.sh

PRODUCT=$1  # "bestays" or "realestate"
BACKUP_FILE=$2

echo "⚠️  WARNING: This will overwrite ${PRODUCT} database!"
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  exit 0
fi

# Stop application
docker-compose -f docker-compose.prod.yml stop ${PRODUCT}-server

# Drop and recreate database
docker exec bestays-postgres-prod psql -U postgres -c "DROP DATABASE IF EXISTS ${PRODUCT}_prod;"
docker exec bestays-postgres-prod psql -U postgres -c "CREATE DATABASE ${PRODUCT}_prod OWNER ${PRODUCT}_user;"

# Restore from backup
gunzip -c $BACKUP_FILE | docker exec -i bestays-postgres-prod psql -U postgres -d ${PRODUCT}_prod

# Restart application
docker-compose -f docker-compose.prod.yml start ${PRODUCT}-server

echo "✅ Database restored: ${PRODUCT}"
```

---

## 9. Monitoring Dashboard

### Recommended Tools

**Metrics:** Prometheus + Grafana
**Logs:** Loki (or ELK stack)
**Errors:** Sentry
**Uptime:** UptimeRobot (or similar)

### Grafana Dashboard (Multi-Product)

**Dashboard Layout:**

```
Row 1: Product Overview
├─ Panel 1: Total Requests per Product (Last 24h)
├─ Panel 2: Error Rate per Product (Last 24h)
└─ Panel 3: API Response Time (p95) per Product

Row 2: Bestays Metrics
├─ Panel 4: Bestays API Requests (by endpoint)
├─ Panel 5: Bestays LLM Token Usage
└─ Panel 6: Bestays User Sessions (active)

Row 3: Real Estate Metrics
├─ Panel 7: Real Estate API Requests (by endpoint)
├─ Panel 8: Real Estate LLM Token Usage
└─ Panel 9: Real Estate User Sessions (active)

Row 4: Infrastructure
├─ Panel 10: PostgreSQL Connections (both databases)
├─ Panel 11: Redis Memory Usage (both DBs)
└─ Panel 12: Container CPU/Memory Usage
```

---

## 10. Migration from Current State

### Current State

- Single product (Bestays)
- Docker Compose with 4 services (postgres, server, frontend, redis)
- Ports: 5433 (postgres), 8011 (server), 5183 (frontend), 6379 (redis)

### Migration Steps

**Step 1: Update PostgreSQL Init Script**

Create `docker/postgres/init-multi-db.sql`:

```sql
-- Create Bestays database (rename from bestays_dev)
CREATE DATABASE bestays_dev;
CREATE USER bestays_user WITH PASSWORD 'bestays_password';
GRANT ALL PRIVILEGES ON DATABASE bestays_dev TO bestays_user;

\c bestays_dev
GRANT ALL ON SCHEMA public TO bestays_user;
CREATE EXTENSION IF NOT EXISTS pgvector;

-- Create Real Estate database
\c postgres
CREATE DATABASE realestate_dev;
CREATE USER realestate_user WITH PASSWORD 'realestate_password';
GRANT ALL PRIVILEGES ON DATABASE realestate_dev TO realestate_user;

\c realestate_dev
GRANT ALL ON SCHEMA public TO realestate_user;
CREATE EXTENSION IF NOT EXISTS pgvector;
```

**Step 2: Rename Existing Services in docker-compose.dev.yml**

```yaml
# Change service names
server: → bestays-server:
frontend: → bestays-frontend:
```

**Step 3: Add Real Estate Services**

```yaml
# Copy bestays-server and bestays-frontend
# Rename to realestate-server and realestate-frontend
# Update environment variables (PRODUCT_ID, DATABASE_URL, ports)
```

**Step 4: Update .env**

```bash
# Add Real Estate Clerk credentials
REALESTATE_CLERK_SECRET_KEY=...
REALESTATE_CLERK_PUBLISHABLE_KEY=...
```

**Step 5: Test**

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# Verify Bestays
curl http://localhost:8011/api/health
# Expected: {"status": "ok", "product": "bestays"}

# Verify Real Estate
curl http://localhost:8012/api/health
# Expected: {"status": "ok", "product": "realestate"}
```

**Migration Time:** ~2 hours (mostly configuration)

---

## 11. Recommendations Summary

### Immediate Actions (This Week)

1. ✅ **Update docker-compose.dev.yml**
   - Rename services: `server` → `bestays-server`
   - Add `PRODUCT_ID: bestays` to environment
   - Add Real Estate services (copy + modify)

2. ✅ **Create PostgreSQL init script**
   - `docker/postgres/init-multi-db.sql`
   - Creates both databases

3. ✅ **Update .env**
   - Add Real Estate Clerk credentials
   - Add product-scoped variables

4. ✅ **Test locally**
   - Verify both products work independently
   - Verify database isolation

### Short-Term Actions (Next Month)

1. ✅ **Set up CI/CD**
   - GitHub Actions workflow
   - Product detection from task semantic names
   - Automated deployment per product

2. ✅ **Implement monitoring**
   - Prometheus metrics with product tags
   - Grafana dashboard
   - Sentry error tracking

3. ✅ **Production deployment**
   - VPS setup
   - Nginx reverse proxy
   - SSL certificates per product

### Long-Term Actions (Future)

1. ✅ **Automated backups**
   - Daily database backups per product
   - S3 upload
   - Restore testing

2. ✅ **Scaling strategy**
   - Monitor resource usage per product
   - Plan for separate VPS if needed
   - Consider Kubernetes if >5 products

---

## 12. Conclusion

**Key Findings:**

1. ✅ **Git commits + task references are sufficient for deployment tracking**
   - Task semantic names provide product context
   - No additional tracking system needed

2. ✅ **Separate containers per product with shared PostgreSQL**
   - Aligns with TASK-002 database isolation strategy
   - Simple to deploy and manage
   - Clear product boundaries

3. ✅ **Product-aware CI/CD filtering by task semantic names**
   - Automatic product detection from commit messages
   - Independent deployments per product
   - No manual product tagging required

4. ✅ **Metrics tagged by product for clear monitoring**
   - Prometheus labels: `product=bestays`, `product=realestate`
   - Separate Grafana panels per product
   - Sentry error filtering per product

5. ✅ **Existing validation hooks prevent cross-product contamination**
   - Branch naming validation (existing)
   - Commit message validation (can add)
   - Environment-based configuration prevents wrong database access

**Confidence Level:** HIGH

**Ready for Implementation:** YES

**Estimated Effort:**
- Infrastructure setup: 2-4 hours
- CI/CD pipeline: 4-6 hours
- Monitoring setup: 4-6 hours
- Total: 10-16 hours

---

**Document Version:** 1.0
**Date:** 2025-11-07
**Agent:** devops-infra
**Status:** COMPLETE
**Next Steps:** Review with user, implement docker-compose.dev.yml changes

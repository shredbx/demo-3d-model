# Service URLs Reference

**Version:** 1.0
**Last Updated:** 2025-11-09
**Status:** Active

---

## Overview

Comprehensive list of all service URLs for both **Bestays** and **Real Estate** products across development, testing, and production environments.

---

## Development Environment (Local)

### Bestays Product (Vacation Rentals)

| Service | URL | Port | Purpose |
|---------|-----|------|---------|
| **Frontend Dev** | http://localhost:5183 | 5183 | SvelteKit development server (hot-reload) |
| **Storybook** | http://localhost:6006 | 6006 | Component library & documentation |
| **Backend API** | http://localhost:8011 | 8011 | FastAPI server |
| **API Docs (Swagger)** | http://localhost:8011/docs | 8011 | Interactive API documentation |
| **API Docs (ReDoc)** | http://localhost:8011/redoc | 8011 | Alternative API documentation |
| **Health Check** | http://localhost:8011/api/health | 8011 | Server health status |
| **Playwright Tests** | http://localhost:5183 | 5183 | E2E tests run against frontend |

**Commands:**
```bash
make dev-bestays        # Start Bestays services
make storybook          # Start Storybook (port 6006)
npm run test:e2e        # Run Playwright E2E tests
```

---

### Real Estate Product

| Service | URL | Port | Purpose |
|---------|-----|------|---------|
| **Frontend Dev** | http://localhost:5184 | 5184 | SvelteKit development server (hot-reload) |
| **Storybook** | http://localhost:6007 | 6007 | Component library & documentation |
| **Backend API** | http://localhost:8012 | 8012 | FastAPI server |
| **API Docs (Swagger)** | http://localhost:8012/docs | 8012 | Interactive API documentation |
| **API Docs (ReDoc)** | http://localhost:8012/redoc | 8012 | Alternative API documentation |
| **Health Check** | http://localhost:8012/api/health | 8012 | Server health status |
| **Playwright Tests** | http://localhost:5184 | 5184 | E2E tests run against frontend |

**Commands:**
```bash
make dev-realestate     # Start Real Estate services
make storybook-realestate  # Start Storybook (port 6007)
npm run test:e2e        # Run Playwright E2E tests
```

---

### Shared Services

| Service | URL | Port | Purpose |
|---------|-----|------|---------|
| **PostgreSQL** | localhost:5433 | 5433 | Database (host port, avoids conflict with local PostgreSQL) |
| **PostgreSQL (Container)** | postgres:5432 | 5432 | Database connection from within Docker network |
| **Redis** | localhost:6379 | 6379 | Cache, sessions, rate limiting |

**Databases:**
- `bestays_dev` - Bestays product database
- `realestate_dev` - Real Estate product database

**Commands:**
```bash
make shell-db           # Connect to PostgreSQL shell
make logs-db            # View database logs
redis-cli               # Connect to Redis CLI
```

---

## Testing URLs

### Frontend Testing

| Test Type | URL | Tool | Purpose |
|-----------|-----|------|---------|
| **Unit Tests** | N/A | Vitest | Component unit tests |
| **E2E Tests (Bestays)** | http://localhost:5183 | Playwright | Full user journey tests |
| **E2E Tests (Real Estate)** | http://localhost:5184 | Playwright | Full user journey tests |
| **Storybook Tests** | http://localhost:6006 | Storybook + Vitest | Component visual & interaction tests |

**Commands:**
```bash
# Unit tests
npm run test:unit
npm run test:coverage

# E2E tests (Playwright)
cd apps/frontend
npm run test:e2e                    # Run all E2E tests
npm run test:e2e -- --headed       # Run with browser visible
npm run test:e2e -- --debug        # Debug mode

# Storybook
make storybook                      # Start Storybook dev server
npm run storybook:build             # Build static Storybook
```

---

### Backend Testing

| Test Type | URL | Tool | Purpose |
|-----------|-----|------|---------|
| **Unit Tests** | N/A | pytest | Service/model unit tests |
| **Integration Tests** | http://localhost:8011 or 8012 | pytest | API integration tests |
| **API Testing** | http://localhost:8011/docs | Swagger UI | Manual API testing |

**Commands:**
```bash
# Backend tests
make test-server        # Run all backend tests
make test-coverage      # Run with coverage report
pytest -v               # Verbose output
pytest -k "test_name"   # Run specific test
```

---

## External Validation URLs (Required for Backend)

**All backend implementations MUST test against these URLs:**

### Bestays Backend
```bash
# External validation with curl
curl http://localhost:8011/api/health
curl http://localhost:8011/api/v1/properties
curl -X POST http://localhost:8011/api/v1/properties/search/semantic
```

### Real Estate Backend
```bash
# External validation with curl
curl http://localhost:8012/api/health
curl http://localhost:8012/api/v1/properties
curl -X POST http://localhost:8012/api/v1/properties/search/semantic
```

**See:** `.sdlc-workflow/guides/backend-validation-requirements.md`

---

## Production URLs (VPS)

### Bestays Product
- **Frontend:** https://bestays.app
- **Backend API:** https://api.bestays.app
- **API Docs:** https://api.bestays.app/docs

### Real Estate Product
- **Frontend:** https://realestate.domain.com (TBD)
- **Backend API:** https://api.realestate.domain.com (TBD)
- **API Docs:** https://api.realestate.domain.com/docs (TBD)

**Production Commands:**
```bash
make deploy-bestays     # Deploy Bestays to production
make deploy-realestate  # Deploy Real Estate to production
```

---

## Port Allocation Summary

| Port | Service | Product | Environment |
|------|---------|---------|-------------|
| 5183 | Frontend Dev | Bestays | Development |
| 5184 | Frontend Dev | Real Estate | Development |
| 6006 | Storybook | Bestays | Development |
| 6007 | Storybook | Real Estate | Development |
| 8011 | Backend API | Bestays | Development |
| 8012 | Backend API | Real Estate | Development |
| 5433 | PostgreSQL | Shared | Development (host) |
| 5432 | PostgreSQL | Shared | Development (container) |
| 6379 | Redis | Shared | Development |

---

## Environment Variables

### Required for Development

**Bestays:**
```bash
# .env.bestays
VITE_API_URL=http://localhost:8011
CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

**Real Estate:**
```bash
# .env.realestate
VITE_API_URL=http://localhost:8012
CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

**Shared:**
```bash
# .env.shared
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/bestays_dev
REDIS_URL=redis://redis:6379
OPENROUTER_API_KEY=sk-or-v1-...
```

---

## CORS Configuration

**Backend allows these origins in development:**
```python
BACKEND_CORS_ORIGINS = [
    "http://localhost:5173",  # Vite default
    "http://localhost:5183",  # Bestays frontend
    "http://localhost:5184",  # Real Estate frontend
    "http://localhost:3000",  # Legacy
    "http://localhost:6006",  # Storybook Bestays
    "http://localhost:6007",  # Storybook Real Estate
    "http://127.0.0.1:5183",  # IPv4 Bestays
    "http://127.0.0.1:5184",  # IPv4 Real Estate
]
```

---

## Troubleshooting

### Port Already in Use
```bash
# Check what's using a port
lsof -i :5183
lsof -i :8011

# Kill process on port
kill -9 $(lsof -t -i:5183)
```

### Service Not Responding
```bash
# Check service status
make status

# Check logs
make logs-server        # Backend logs
make logs-frontend      # Frontend logs
make logs-all           # All service logs

# Restart specific service
make restart-server
make restart-frontend
```

### Database Connection Issues
```bash
# Check database is running
make status | grep postgres

# Connect to database
make shell-db

# Verify connection
psql postgresql://postgres:postgres@localhost:5433/bestays_dev
```

---

## Quick Reference

### Start Development
```bash
# Bestays only
make dev-bestays

# Real Estate only
make dev-realestate

# Both products
make dev-both

# With Storybook
make dev-bestays && make storybook
```

### Run Tests
```bash
# All tests
make test-all

# Fast tests only (no E2E)
make test-fast

# Backend tests with coverage
make test-coverage

# Frontend E2E tests
cd apps/frontend && npm run test:e2e
```

### Access Documentation
```bash
# API Documentation (Swagger)
open http://localhost:8011/docs      # Bestays
open http://localhost:8012/docs      # Real Estate

# Storybook (Component Library)
make storybook
open http://localhost:6006
```

---

## Related Documentation

- **Backend Validation:** `.sdlc-workflow/guides/backend-validation-requirements.md`
- **Testing Strategy:** `.sdlc-workflow/guides/testing-strategy.md`
- **Docker Setup:** `docker-compose.dev.yml`, `docker-compose.prod.yml`
- **Makefile:** `Makefile` (all available commands)
- **README:** `README.md` (getting started)

---

**Last Updated:** 2025-11-09
**Maintained By:** DevOps / Infrastructure Team

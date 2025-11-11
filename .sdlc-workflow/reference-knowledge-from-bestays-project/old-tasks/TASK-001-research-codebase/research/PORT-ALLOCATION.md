# Port Allocation Reference

**Document Purpose:** Central port allocation registry for white-label multi-product architecture

**Last Updated:** 2025-11-07

---

## Port Allocation Strategy

**Pattern:** Base + 100 to avoid conflicts with other parallel projects

**Base Ports (OLD - DO NOT USE):**
- ❌ Backend: 8001, 8002
- ❌ Frontend: 5173, 5174

**New Ports (OFFICIAL - USE THESE):**
- ✅ Backend: 8101, 8102
- ✅ Frontend: 5273, 5274

---

## Development Environment Ports

### Bestays Product

| Service | Port | URL | Notes |
|---------|------|-----|-------|
| **Backend API** | **8101** | `http://localhost:8101` | FastAPI server |
| **Frontend Web** | **5273** | `http://localhost:5273` | SvelteKit dev server |
| PostgreSQL | 5432 | `postgresql://localhost:5432/bestays_db` | Shared PostgreSQL instance |
| Redis | 6379 (DB 0) | `redis://localhost:6379/0` | Separate keyspace |

### Real Estate Product

| Service | Port | URL | Notes |
|---------|------|-----|-------|
| **Backend API** | **8102** | `http://localhost:8102` | FastAPI server |
| **Frontend Web** | **5274** | `http://localhost:5274` | SvelteKit dev server |
| PostgreSQL | 5432 | `postgresql://localhost:5432/realestate_db` | Shared PostgreSQL instance |
| Redis | 6379 (DB 1) | `redis://localhost:6379/1` | Separate keyspace |

---

## Docker Compose Port Mapping

### Development (docker-compose.dev.yml)

```yaml
services:
  bestays-api:
    ports:
      - "8101:8000"  # Host 8101 → Container 8000

  realestate-api:
    ports:
      - "8102:8000"  # Host 8102 → Container 8000

  bestays-web:
    ports:
      - "5273:5173"  # Host 5273 → Container 5173 (Vite default)

  realestate-web:
    ports:
      - "5274:5173"  # Host 5274 → Container 5173 (Vite default)

  postgres:
    ports:
      - "5432:5432"  # Shared PostgreSQL

  redis:
    ports:
      - "6379:6379"  # Shared Redis
```

---

## Environment Variables

### Bestays (.env.development)

```bash
# Backend API
API_URL=http://localhost:8101
API_PORT=8000  # Internal container port

# Frontend
VITE_API_URL=http://localhost:8101
VITE_PORT=5173  # Internal container port (mapped to 5273)

# CORS
ALLOWED_ORIGINS=["http://localhost:5273"]
```

### Real Estate (.env.development)

```bash
# Backend API
API_URL=http://localhost:8102
API_PORT=8000  # Internal container port

# Frontend
VITE_API_URL=http://localhost:8102
VITE_PORT=5173  # Internal container port (mapped to 5274)

# CORS
ALLOWED_ORIGINS=["http://localhost:5274"]
```

---

## Testing Ports

### E2E Tests (Playwright)

```typescript
// tests/e2e/config.ts
export const BESTAYS_CONFIG = {
  frontendUrl: 'http://localhost:5273',
  apiUrl: 'http://localhost:8101',
};

export const REALESTATE_CONFIG = {
  frontendUrl: 'http://localhost:5274',
  apiUrl: 'http://localhost:8102',
};
```

---

## Production Ports

### Separate VPS Deployment

**Bestays VPS:**
```
Backend:  https://api.bestays.app (reverse proxy → 8101)
Frontend: https://bestays.app (reverse proxy → 5273)
```

**Real Estate VPS:**
```
Backend:  https://api.realestate.app (reverse proxy → 8102)
Frontend: https://realestate.app (reverse proxy → 5274)
```

### Same VPS Deployment (Optional)

```nginx
# nginx.conf
server {
  server_name api.bestays.app;
  location / {
    proxy_pass http://localhost:8101;
  }
}

server {
  server_name api.realestate.app;
  location / {
    proxy_pass http://localhost:8102;
  }
}

server {
  server_name bestays.app;
  location / {
    proxy_pass http://localhost:5273;
  }
}

server {
  server_name realestate.app;
  location / {
    proxy_pass http://localhost:5274;
  }
}
```

---

## Port Conflict Prevention

### Before Starting Services

```bash
# Check if ports are in use
lsof -i :8101  # Bestays backend
lsof -i :8102  # Real Estate backend
lsof -i :5273  # Bestays frontend
lsof -i :5274  # Real Estate frontend
```

### Kill Conflicting Processes

```bash
# Kill process by port
kill -9 $(lsof -t -i:8101)
kill -9 $(lsof -t -i:8102)
kill -9 $(lsof -t -i:5273)
kill -9 $(lsof -t -i:5274)
```

---

## Migration Notes

### Old → New Port Mapping

| Service | Old Port | New Port | Status |
|---------|----------|----------|--------|
| Bestays Backend | 8001 | **8101** | ✅ Updated |
| Real Estate Backend | 8002 | **8102** | ✅ Updated |
| Bestays Frontend | 5173 | **5273** | ✅ Updated |
| Real Estate Frontend | 5174 | **5274** | ✅ Updated |

### Files Updated

1. `.claude/tasks/TASK-001-research-codebase/research/clerk-multi-product-config.md` ✅
2. `.claude/tasks/TASK-002-database-isolation/planning/database-architecture-recommendations.md` (pending)
3. `.claude/tasks/TASK-003-backend-architecture/planning/backend-architecture-recommendations.md` (pending)
4. `.claude/tasks/TASK-001-research-codebase/research/findings-summary.md` (pending)

---

## Search Commands for Port References

**Find all port references in repo:**
```bash
cd /Users/solo/Projects/_repos/bestays
grep -r "8001\|8002\|5173\|5174" \
  --include="*.md" \
  --include="*.json" \
  --include="*.yml" \
  --include="*.yaml" \
  --include="*.py" \
  --include="*.ts" \
  --include="*.js" \
  --include="*.svelte" \
  .claude/ .sdlc-workflow/ apps/ packages/
```

**Find specific old ports:**
```bash
# Backend old ports
grep -r "localhost:8001\|localhost:8002" .

# Frontend old ports
grep -r "localhost:5173\|localhost:5174" .
```

---

## Verification Checklist

After updating all port references:

- [ ] All `.md` files in `.claude/` updated
- [ ] All `.md` files in `.sdlc-workflow/` updated
- [ ] All environment config examples updated
- [ ] Docker Compose configurations updated
- [ ] Testing configurations updated (Playwright, Jest, Vitest)
- [ ] README files updated
- [ ] CORS configurations updated (backend)
- [ ] API client base URLs updated (frontend)
- [ ] No lingering references to old ports (run grep search)

---

**Reference Document Version:** 1.0
**Last Port Change:** 2025-11-07
**Next Review:** Before TASK-004 (Frontend Architecture)

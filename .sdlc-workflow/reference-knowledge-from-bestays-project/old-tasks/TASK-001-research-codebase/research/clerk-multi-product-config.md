# Clerk Multi-Product Configuration

**Document Purpose:** Define Clerk authentication configuration for both products (Bestays and Best Real Estate)

**Date Created:** 2025-11-07
**User Story:** US-018 (White-Label Multi-Product Architecture)

---

## Overview

Both products use **separate Clerk projects** with **separate user bases** (no shared authentication).

**Role Management:**
- Clerk provides **user authentication only** (email/password, JWT tokens)
- **User roles managed by our backend** (not Clerk)
- After Clerk authentication, backend assigns roles: `user`, `admin`, `agent`

---

## Product 1: Bestays.app

### Clerk Project Configuration

**Environment Variables:**
```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_c2FjcmVkLW1heWZseS01NS5jbGVyay5hY2NvdW50cy5kZXYk
CLERK_SECRET_KEY=sk_test_vGrRuTLW1SdS2uQlDbv4l2T2WHpTk9IoervBmG9Vit
```

**Clerk Account:** sacred-mayfly-55.clerk.accounts.dev

### Test Users (for Development & Testing)

| Email | Password | Intended Role | Notes |
|-------|----------|---------------|-------|
| `user.claudecode@bestays.app` | `9kB*k926O8):` | `user` | Standard user role |
| `admin.claudecode@bestays.app` | `rHe/997?lo&l` | `admin` | Administrator role |
| `agent.claudecode@bestays.app` | `y>1T;)5s!X1X` | `agent` | Agent/broker role |

**Role Assignment:**
- Users authenticate via Clerk
- Backend checks user email or database record
- Backend assigns role: `user`, `admin`, or `agent`
- Role stored in backend database (not Clerk)

---

## Product 2: Best Real Estate

### Clerk Project Configuration

**Environment Variables:**
```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_cGxlYXNhbnQtZ251LTI1LmNsZXJrLmFjY291bnRzLmRldiQ
CLERK_SECRET_KEY=sk_test_GBG0pHIE015mIkiHfrpeOS4mi1hqNSm0uBUdlexgxS
```

**Clerk Account:** pleasant-gnu-25.clerk.accounts.dev

### Test Users (for Development & Testing)

| Email | Password | Intended Role | Notes |
|-------|----------|---------------|-------|
| `user.claudecode@realestate.dev` | `y>1T_)5h!X1X` | `user` | Standard user role |
| `admin.claudecode@realestate.dev` | `rHe/997?lo&l` | `admin` | Administrator role |
| `agent.claudecode@realestate.dev` | `y>1T;)5s!X1X` | `agent` | Agent/broker role |

**Role Assignment:**
- Users authenticate via Clerk
- Backend checks user email or database record
- Backend assigns role: `user`, `admin`, or `agent`
- Role stored in backend database (not Clerk)

---

## Environment Configuration Strategy

### Development Environment (.env.development)

**Bestays App:**
```bash
# Product identification
PRODUCT_NAME=bestays
APP_NAME="Bestays"

# Clerk authentication (Bestays project)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_c2FjcmVkLW1heWZseS01NS5jbGVyay5hY2NvdW50cy5kZXYk
CLERK_SECRET_KEY=sk_test_vGrRuTLW1SdS2uQlDbv4l2T2WHpTk9IoervBmG9Vit

# Database (separate per product)
DATABASE_URL=postgresql://user:pass@localhost:5432/bestays_db

# API endpoints
API_URL=http://localhost:8101
```

**Best Real Estate App:**
```bash
# Product identification
PRODUCT_NAME=realestate
APP_NAME="Best Real Estate"

# Clerk authentication (Real Estate project)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_cGxlYXNhbnQtZ251LTI1LmNsZXJrLmFjY291bnRzLmRldiQ
CLERK_SECRET_KEY=sk_test_GBG0pHIE015mIkiHfrpeOS4mi1hqNSm0uBUdlexgxS

# Database (separate per product)
DATABASE_URL=postgresql://user:pass@localhost:5432/realestate_db

# API endpoints
API_URL=http://localhost:8102
```

---

## Production Environment (.env.production)

### Bestays App (Production)

```bash
# Product identification
PRODUCT_NAME=bestays
APP_NAME="Bestays"

# Clerk authentication (production keys - TBD)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_[PRODUCTION_KEY_TBD]
CLERK_SECRET_KEY=sk_live_[PRODUCTION_KEY_TBD]

# Database
DATABASE_URL=postgresql://[PROD_USER]:[PROD_PASS]@[PROD_HOST]:5432/bestays_production

# API endpoints
API_URL=https://api.bestays.app
```

### Best Real Estate App (Production)

```bash
# Product identification
PRODUCT_NAME=realestate
APP_NAME="Best Real Estate"

# Clerk authentication (production keys - TBD)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_[PRODUCTION_KEY_TBD]
CLERK_SECRET_KEY=sk_live_[PRODUCTION_KEY_TBD]

# Database
DATABASE_URL=postgresql://[PROD_USER]:[PROD_PASS]@[PROD_HOST]:5432/realestate_production

# API endpoints
API_URL=https://api.realestate.app
```

---

## Multi-Product Configuration Pattern

### Recommended Approach: Environment-Based Product Selection

**Monorepo Structure:**
```
bestays-monorepo/
├── apps/
│   ├── bestays-web/
│   │   ├── .env.development
│   │   ├── .env.production
│   │   └── svelte.config.js (reads PRODUCT_NAME)
│   ├── bestays-api/
│   │   ├── .env.development
│   │   ├── .env.production
│   │   └── config.py (reads PRODUCT_NAME, CLERK_SECRET_KEY)
│   ├── realestate-web/
│   │   ├── .env.development
│   │   ├── .env.production
│   │   └── svelte.config.js (reads PRODUCT_NAME)
│   └── realestate-api/
│       ├── .env.development
│       ├── .env.production
│       └── config.py (reads PRODUCT_NAME, CLERK_SECRET_KEY)
```

### Configuration Loading (Backend - FastAPI)

```python
# apps/bestays-api/app/config.py (or apps/realestate-api/app/config.py)

from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    # Product identification
    PRODUCT_NAME: Literal["bestays", "realestate"]
    APP_NAME: str  # "Bestays" or "Best Real Estate"

    # Clerk authentication (product-specific)
    CLERK_PUBLISHABLE_KEY: str
    CLERK_SECRET_KEY: str
    CLERK_ISSUER: str  # Computed from publishable key

    # Database (product-specific)
    DATABASE_URL: str

    # API configuration
    API_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Singleton instance
settings = Settings()
```

### Configuration Loading (Frontend - SvelteKit)

```typescript
// apps/bestays-web/src/lib/config.ts (or apps/realestate-web/src/lib/config.ts)

import { PUBLIC_CLERK_PUBLISHABLE_KEY } from '$env/static/public';
import { CLERK_SECRET_KEY } from '$env/static/private';

export const config = {
  productName: import.meta.env.VITE_PRODUCT_NAME || 'bestays',
  appName: import.meta.env.VITE_APP_NAME || 'Bestays',

  clerk: {
    publishableKey: PUBLIC_CLERK_PUBLISHABLE_KEY,
    // Secret key only available server-side
  },

  api: {
    url: import.meta.env.VITE_API_URL || 'http://localhost:8101',
  },
};
```

---

## Role Management Implementation

### Backend: Role Assignment Flow

**After Clerk Authentication:**

```python
# apps/{product}-api/app/services/auth.py

from clerk import Clerk
from app.database import get_user_by_email, create_or_update_user

async def authenticate_user(clerk_token: str) -> User:
    # 1. Verify Clerk JWT token
    clerk_client = Clerk(api_key=settings.CLERK_SECRET_KEY)
    clerk_user = await clerk_client.verify_token(clerk_token)

    # 2. Get or create user in our database
    user = await get_user_by_email(clerk_user.email)

    if not user:
        # 3. Create user with default role
        user = await create_or_update_user(
            email=clerk_user.email,
            clerk_id=clerk_user.id,
            role="user",  # Default role
        )

    # 4. Return user with role
    return user
```

**Role Check Dependency:**

```python
# apps/{product}-api/app/api/deps.py

from fastapi import Depends, HTTPException, status
from app.services.auth import authenticate_user

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    user = await authenticate_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

async def require_agent(user: User = Depends(get_current_user)) -> User:
    if user.role not in ["agent", "admin"]:
        raise HTTPException(status_code=403, detail="Agent access required")
    return user
```

### Database: User Role Table

```sql
-- Separate database per product, but same schema
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    clerk_id VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',  -- 'user', 'admin', 'agent'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for fast role lookups
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_clerk_id ON users(clerk_id);
```

---

## Testing Strategy

### Manual Testing with Test Users

**Bestays App:**
1. Navigate to `http://localhost:5273` (or dev URL)
2. Click "Sign In"
3. Enter credentials:
   - User role: `user.claudecode@bestays.app` / `9kB*k926O8):`
   - Admin role: `admin.claudecode@bestays.app` / `rHe/997?lo&l`
   - Agent role: `agent.claudecode@bestays.app` / `y>1T;)5s!X1X`
4. Verify backend assigns correct role after Clerk auth
5. Test role-based access control (admin pages, agent features, etc.)

**Best Real Estate App:**
1. Navigate to `http://localhost:5274` (or dev URL)
2. Click "Sign In"
3. Enter credentials:
   - User role: `user.claudecode@realestate.dev` / `y>1T_)5h!X1X`
   - Admin role: `admin.claudecode@realestate.dev` / `rHe/997?lo&l`
   - Agent role: `agent.claudecode@realestate.dev` / `y>1T;)5s!X1X`
4. Verify backend assigns correct role after Clerk auth
5. Test role-based access control

### E2E Testing with Playwright

```typescript
// tests/e2e/auth/clerk-multi-product.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Bestays - Clerk Authentication', () => {
  test('user role authentication', async ({ page }) => {
    await page.goto('http://localhost:5273');
    await page.click('text=Sign In');
    await page.fill('input[name="email"]', 'user.claudecode@bestays.app');
    await page.fill('input[name="password"]', '9kB*k926O8):');
    await page.click('button:has-text("Sign In")');

    // Verify user role
    await expect(page.locator('text=User Dashboard')).toBeVisible();
  });

  test('admin role authentication', async ({ page }) => {
    await page.goto('http://localhost:5273');
    await page.click('text=Sign In');
    await page.fill('input[name="email"]', 'admin.claudecode@bestays.app');
    await page.fill('input[name="password"]', 'rHe/997?lo&l');
    await page.click('button:has-text("Sign In")');

    // Verify admin role
    await expect(page.locator('text=Admin Dashboard')).toBeVisible();
  });
});

test.describe('Real Estate - Clerk Authentication', () => {
  test('user role authentication', async ({ page }) => {
    await page.goto('http://localhost:5274');
    await page.click('text=Sign In');
    await page.fill('input[name="email"]', 'user.claudecode@realestate.dev');
    await page.fill('input[name="password"]', 'y>1T_)5h!X1X');
    await page.click('button:has-text("Sign In")');

    // Verify user role
    await expect(page.locator('text=User Dashboard')).toBeVisible();
  });

  test('admin role authentication', async ({ page }) => {
    await page.goto('http://localhost:5274');
    await page.click('text=Sign In');
    await page.fill('input[name="email"]', 'admin.claudecode@realestate.dev');
    await page.fill('input[name="password"]', 'rHe/997?lo&l');
    await page.click('button:has-text("Sign In")');

    // Verify admin role
    await expect(page.locator('text=Admin Dashboard')).toBeVisible();
  });
});
```

---

## Security Considerations

### Credential Management

**Development/Testing:**
- ✅ Test credentials documented here (safe for development)
- ✅ Test Clerk projects (separate from production)
- ✅ Passwords should be rotated periodically

**Production:**
- ❌ **NEVER commit production Clerk keys to git**
- ✅ Use environment variables only
- ✅ Use secrets management (e.g., 1Password, Vault)
- ✅ Rotate keys regularly
- ✅ Use Clerk production projects (not test projects)

### Role-Based Access Control (RBAC)

**Backend enforcement (CRITICAL):**
- ✅ Always check roles in backend API endpoints
- ✅ Never trust frontend role checks alone
- ✅ Use FastAPI dependencies for role enforcement
- ✅ Log role changes for audit trail

**Frontend enforcement (UX only):**
- ✅ Hide UI elements based on role (better UX)
- ❌ But always enforce in backend (security)

---

## Migration Plan (Existing Bestays Users)

**If Bestays already has users in production:**

1. **Create Bestays Clerk project** (done: sacred-mayfly-55.clerk.accounts.dev)
2. **Migrate existing users to Clerk:**
   - Option A: Invite users to create Clerk accounts (email invitations)
   - Option B: Clerk Import API (bulk import with hashed passwords)
3. **Map existing database users to Clerk IDs:**
   ```sql
   ALTER TABLE users ADD COLUMN clerk_id VARCHAR(255);
   CREATE UNIQUE INDEX idx_users_clerk_id ON users(clerk_id);
   ```
4. **Update backend authentication to use Clerk JWT tokens**
5. **Preserve existing user roles** (already in database)

---

## Next Steps for Agent Review Chain

### TASK-002: Database Isolation Strategy (dev-database agent)

**Required Context from This Document:**
- Separate databases per product (`bestays_db`, `realestate_db`)
- Same schema structure (users table with roles)
- Migration strategy for schema changes across products

### TASK-003: Backend Architecture (dev-backend-fastapi agent)

**Required Context from This Document:**
- Environment-based Clerk configuration
- Role assignment flow after Clerk authentication
- FastAPI dependencies for role enforcement
- Separate API per product (ports 8001, 8002)

### TASK-004: Frontend Architecture (dev-frontend-svelte agent)

**Required Context from This Document:**
- Environment-based Clerk publishable keys
- SvelteKit configuration per product
- Role-based UI rendering (but always enforce in backend)
- Separate frontend per product (ports 5173, 5174)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-07
**Maintained By:** Bestays SDLC Team
**User Story:** US-018 (White-Label Multi-Product Architecture)

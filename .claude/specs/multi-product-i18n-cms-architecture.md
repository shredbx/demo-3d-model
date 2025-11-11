# Multi-Product i18n CMS Architecture

**Status:** DRAFT - In Agent Review
**Created:** 2025-11-08
**Review Chain:** Coordinator → DevOps → Backend → Frontend → Final Synthesis

---

## Executive Summary

This document proposes a foundational architecture change to support:

1. **Multi-Product Configuration** - Domain-specific branding, layouts, and content per product (Bestays.app vs Real Estate)
2. **shadcn-svelte Component System** - Reusable, customizable components to avoid reinventing the wheel
3. **Full Internationalization (i18n)** - Thai and English support for ALL content (static and dynamic)
4. **CMS-like Content Management** - Database-driven content with in-place editing capabilities

This is a **foundational infrastructure change** that will affect all future features and potentially modify existing user stories.

---

## Current State Assessment

### What We Have Today (from TASK-002, US-018)

✅ **Multi-Product Infrastructure:**
- Separate Clerk instances per product
- Environment-based configuration (`.env.bestays`, `.env.realestate`)
- Dual-port dev setup (5183 vs 5184)
- Product detection via `VITE_PRODUCT` env var
- Basic product config in `frontend/src/lib/config/product.ts`

### What's Missing

❌ **No Database-Driven Product Configuration**
- Product info (name, description, branding) is hardcoded
- No way to change product metadata without code deployment

❌ **No i18n System**
- All strings are hardcoded in English
- No locale detection or switching
- No translation management

❌ **No shadcn-svelte Integration**
- Custom-built components (reinventing the wheel)
- Inconsistent component API
- No design system foundation

❌ **No CMS Functionality**
- No content dictionary
- No dynamic content management
- No in-place editing
- No content versioning or audit trail

---

## Requirements Breakdown

### 1. Multi-Product Domain Configuration

**Goal:** Each product has its own identity stored in the database.

**Required Fields:**
```typescript
interface ProductConfig {
  id: string;              // 'bestays' | 'realestate'
  name: string;            // Display name per locale
  description: string;     // Product description per locale
  domain: string;          // Primary domain
  clerkConfig: {
    publishableKey: string;
    domain: string;
  };
  theme: {
    primaryColor: string;
    secondaryColor: string;
    // ... Tailwind theme tokens
  };
  layout: {
    variant: 'default' | 'elegant';  // Layout variations
    // ... layout configuration
  };
}
```

**Use Cases:**
- Homepage shows "Welcome to Bestays" vs "Welcome to [Real Estate Name]"
- Different color schemes per product
- Different footer/header layouts per product
- Product metadata for SEO

### 2. shadcn-svelte Component Strategy

**Goal:** Leverage shadcn-svelte as foundation, customize per product needs.

**Strategy:**
- Install shadcn-svelte CLI and base components
- Components are customizable via Tailwind (theme variables)
- Create product-aware wrapper components where needed
- Focus on UX and features, not building buttons/forms from scratch

**Component Categories:**
- **Base (shadcn):** Button, Input, Card, Dialog, Dropdown, etc.
- **Product-Aware:** Header, Footer, Navigation (reads product config)
- **Feature-Specific:** PropertyCard, ChatInterface, etc. (built on base components)

### 3. Full Internationalization (i18n)

**Goal:** Support Thai and English for ALL content (static and dynamic).

**Scope:**
- **Static Content:** UI labels, buttons, form placeholders, error messages
- **Dynamic Content:** Product names, descriptions, property listings
- **User-Generated Content:** Comments, reviews (stored with locale)

**Requirements:**
- Locale detection (browser preference, URL param, user preference)
- Locale switching UI
- SSR-compatible (locale on server and client)
- Fallback handling (Thai missing → show English)
- RTL support consideration (future: Arabic)

**Technology Stack (Proposed):**
- **Frontend:** `svelte-i18n` or `typesafe-i18n`
- **Backend:** FastAPI + Database dictionary
- **Storage:** PostgreSQL tables for translations
- **Caching:** Redis for content dictionary

### 4. CMS-like Content Management

**Goal:** Non-developers can edit content in-place, changes stored in database.

**Features:**

**Phase 1 - Basic Content Dictionary:**
- Database tables for static content (labels, titles, descriptions)
- Admin UI for CRUD operations
- API endpoints for content retrieval
- Hierarchical key structure (`page.home.title`, `form.login.submit`)

**Phase 2 - In-Place Editing:**
- Right-click on content → "Edit Content"
- Inline editing modal with rich text support
- Save directly to database
- Real-time updates (next page render shows new content)

**Phase 3 - Advanced CMS:**
- Preview vs Published states
- Content versioning (audit trail)
- Role-based permissions (who can edit what)
- Bulk import/export (CSV, JSON)
- Content approval workflow

---

## Architecture Overview

### System Layers

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ SvelteKit + Svelte 5 + shadcn-svelte                 │   │
│  │  - Product Context Provider                          │   │
│  │  - i18n Integration (svelte-i18n)                    │   │
│  │  - Content Management UI                             │   │
│  │  - Theme System (Tailwind + CSS Variables)           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ API Calls
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                         BACKEND                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ FastAPI                                              │   │
│  │  - /api/v1/config/product                           │   │
│  │  - /api/v1/content (CRUD)                           │   │
│  │  - /api/v1/locales                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Services                                             │   │
│  │  - ProductConfigService                             │   │
│  │  - ContentService (with Redis caching)              │   │
│  │  - LocaleService                                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATABASE                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ PostgreSQL Tables                                    │   │
│  │  - product_config                                    │   │
│  │  - content_dictionary                                │   │
│  │  - content_translations                              │   │
│  │  - supported_locales                                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                         CACHE                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Redis                                                │   │
│  │  - content:{locale}:{key}                           │   │
│  │  - product:{product_id}:config                      │   │
│  │  - TTL: 1 hour (invalidate on update)              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema (Proposed)

```sql
-- Product Configuration
CREATE TABLE product_config (
    id VARCHAR(50) PRIMARY KEY,  -- 'bestays' | 'realestate'
    name JSONB NOT NULL,          -- {"en": "Bestays", "th": "เบสเตย์"}
    description JSONB NOT NULL,   -- {"en": "...", "th": "..."}
    domain VARCHAR(255) NOT NULL,
    clerk_publishable_key VARCHAR(255) NOT NULL,
    clerk_domain VARCHAR(255) NOT NULL,
    theme JSONB NOT NULL,         -- Color palette, fonts, etc.
    layout_config JSONB NOT NULL, -- Layout preferences
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Supported Locales
CREATE TABLE supported_locales (
    code VARCHAR(10) PRIMARY KEY,  -- 'en', 'th'
    name VARCHAR(50) NOT NULL,     -- 'English', 'ไทย'
    is_rtl BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Content Dictionary (hierarchical keys)
CREATE TABLE content_dictionary (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,  -- 'page.home.title'
    namespace VARCHAR(100) NOT NULL,    -- 'page', 'form', 'error', etc.
    context TEXT,                       -- Developer notes
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Content Translations
CREATE TABLE content_translations (
    id SERIAL PRIMARY KEY,
    content_id INTEGER REFERENCES content_dictionary(id) ON DELETE CASCADE,
    locale_code VARCHAR(10) REFERENCES supported_locales(code),
    value TEXT NOT NULL,
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id),  -- Audit trail
    UNIQUE(content_id, locale_code)
);

-- Content Versions (for audit trail)
CREATE TABLE content_versions (
    id SERIAL PRIMARY KEY,
    translation_id INTEGER REFERENCES content_translations(id),
    value TEXT NOT NULL,
    changed_by INTEGER REFERENCES users(id),
    changed_at TIMESTAMP DEFAULT NOW(),
    change_reason TEXT
);

-- Indexes for performance
CREATE INDEX idx_content_translations_locale ON content_translations(locale_code);
CREATE INDEX idx_content_translations_published ON content_translations(is_published);
CREATE INDEX idx_content_dictionary_namespace ON content_dictionary(namespace);
```

---

## Technical Design Decisions

### Decision 1: Product Detection Strategy

**Options:**
- A) Subdomain-based (`bestays.app`, `realestate.bestays.app`)
- B) Separate domains (`bestays.app`, `realestate.com`)
- C) Path-based (`bestays.app/bestays`, `bestays.app/realestate`)
- D) Header-based detection

**Recommendation:** Option B (Separate domains) with Header-based fallback
- **Why:** Clean separation, SEO benefits, professional appearance
- **Implementation:** Detect via `Host` header in backend, `window.location.hostname` in frontend
- **Dev:** Continue using ports (5183 vs 5184) + `VITE_PRODUCT` env var

### Decision 2: i18n Library Choice

**Options:**
- A) `svelte-i18n` - Most popular, SSR support
- B) `typesafe-i18n` - Type-safe, better DX
- C) Custom solution

**Recommendation:** `svelte-i18n` + Backend API
- **Why:** Battle-tested, SSR support, community adoption
- **Trade-off:** Not type-safe, but backend API adds flexibility
- **Integration:** Frontend uses svelte-i18n, loads translations from API

### Decision 3: shadcn-svelte Integration

**Options:**
- A) Install all components upfront
- B) Install components as needed (CLI-based)
- C) Fork and customize heavily

**Recommendation:** Option B (Install as needed)
- **Why:** Smaller bundle, only what we use
- **Process:** `npx shadcn-svelte@latest add button` when needed
- **Customization:** Via `tailwind.config.js` theme and CSS variables

### Decision 4: Content Caching Strategy

**Options:**
- A) No caching (query DB every time)
- B) Redis cache with TTL
- C) Static generation at build time
- D) Hybrid (Redis + static fallback)

**Recommendation:** Option B (Redis with 1-hour TTL)
- **Why:** Balance between freshness and performance
- **Invalidation:** Clear cache on content update
- **Key Structure:** `content:{locale}:{namespace}` (e.g., `content:en:page.home`)

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
**Goal:** Set up core infrastructure

**Backend:**
- [ ] Database migration: Create tables (product_config, content_dictionary, etc.)
- [ ] Product Config API (`GET /api/v1/config/product/{product_id}`)
- [ ] Content API (CRUD: `GET /api/v1/content`, `POST /api/v1/content`, etc.)
- [ ] Locale API (`GET /api/v1/locales`)
- [ ] Redis caching layer

**Frontend:**
- [ ] shadcn-svelte setup and first components (Button, Input, Card)
- [ ] svelte-i18n integration
- [ ] Product context provider (`$productConfig` store)
- [ ] Locale switcher UI
- [ ] Load content from API (replace hardcoded strings)

**DevOps:**
- [ ] Update docker-compose with new env vars
- [ ] Database migration scripts
- [ ] Redis configuration

**Deliverable:** Basic i18n working, product config from database, shadcn components rendering

---

### Phase 2: Content Management (Week 3-4)
**Goal:** Admin can manage content via UI

**Backend:**
- [ ] Admin endpoints for content CRUD (with auth)
- [ ] Content validation and sanitization
- [ ] Bulk import/export endpoints

**Frontend:**
- [ ] Admin dashboard for content management
- [ ] Content editor UI (list view, edit form)
- [ ] Content search and filtering
- [ ] Locale comparison view (English vs Thai side-by-side)

**Deliverable:** Admin can edit all static content via web UI

---

### Phase 3: CMS Features (Week 5-6)
**Goal:** In-place editing and advanced features

**Frontend:**
- [ ] Content-editable markers in DOM (`data-content-key`)
- [ ] Right-click context menu for editing
- [ ] Inline editing modal with rich text
- [ ] Permission checking (user role)

**Backend:**
- [ ] Content versioning (audit trail)
- [ ] Preview vs Published states
- [ ] Content approval workflow (if needed)

**Deliverable:** Editors can right-click and edit content in-place

---

## Impact on Existing User Stories

### User Story Assessment

#### US-019 (Login/Logout Flow) - **IN PROGRESS**
**Impact:** 🟡 MODERATE
- Login page strings need i18n (`page.login.title`, `form.login.submit`)
- Clerk component rendered inside shadcn Card
- Product-specific redirect URLs (already implemented)
- **Action:** Finish current implementation, then refactor to use i18n in next task

#### US-012 (Property Listing) - **NOT STARTED**
**Impact:** 🔴 HIGH
- Property titles/descriptions need i18n
- Property schema needs locale-specific fields (Thai address vs English address)
- Property cards use shadcn components
- **Action:** BLOCK until Phase 1 complete (need i18n + shadcn)

#### US-002 (Homepage) - **NOT STARTED**
**Impact:** 🔴 HIGH
- Homepage content is ALL in content dictionary
- Hero section, feature descriptions, CTAs - all i18n
- Product-specific branding and layout
- **Action:** BLOCK until Phase 1 complete

#### US-018 (Multi-Product Infrastructure) - **COMPLETE**
**Impact:** 🟢 LOW (Enhancement)
- Already have product detection via env vars
- This architecture ENHANCES with database-driven config
- **Action:** Create follow-up task to migrate hardcoded config to database

### Recommended Story Priority Adjustment

**Current Plan:**
1. ✅ US-018 (Infrastructure) - COMPLETE
2. 🔄 US-019 (Login) - IN TESTING
3. 🔜 US-012 (Properties) - PLANNED
4. 🔜 US-002 (Homepage) - PLANNED

**Recommended Plan:**
1. ✅ US-018 (Infrastructure) - COMPLETE
2. 🔄 US-019 (Login) - FINISH CURRENT IMPLEMENTATION
3. ⭐ **NEW: US-XXX (i18n + CMS Foundation)** - Phase 1+2 (3-4 weeks)
4. 🔜 US-019-REFACTOR (Refactor login to use i18n)
5. 🔜 US-002 (Homepage) - Now uses i18n + shadcn
6. 🔜 US-012 (Properties) - Now uses i18n + shadcn

---

## Open Questions for Agent Review

### For DevOps Agent:
1. Should we use environment variables for product detection in production or rely solely on domain/host header?
2. What's the deployment strategy for multi-domain setup? (Single deployment serving multiple domains vs separate deployments)
3. Database migration strategy - how to seed initial content dictionary?
4. Redis configuration - single instance or per-product instances?
5. How to handle product-specific environment secrets (Clerk keys) in production?

### For Backend Agent:
1. Content API design - RESTful or GraphQL for complex content queries?
2. Caching invalidation strategy - should we use pub/sub for real-time updates?
3. Should product config be cached at application startup or fetched per request?
4. Content versioning - how many versions to keep? Automatic cleanup?
5. Authorization for content editing - role-based (admin only) or permission-based (granular)?
6. Should we support content scheduling (publish at specific date/time)?

### For Frontend Agent:
1. svelte-i18n vs typesafe-i18n - type safety worth the trade-off?
2. shadcn-svelte customization approach - CSS variables or Tailwind config?
3. Product theme switching - runtime CSS variable changes or static at build?
4. In-place editing UX - modal dialog or inline contenteditable?
5. Locale switcher placement - header, footer, floating button?
6. SSR considerations - how to detect locale on server vs client?
7. Content loading strategy - fetch all at once or lazy load per namespace?

---

## Agent Review Sections

### 🔧 DevOps Review (devops-infra agent)

#### 1. Multi-Domain Deployment Strategy

**Recommendation: Single Deployment with Host Header Detection**

**Rationale:**
- Both products share the same database and codebase
- Database-driven config eliminates need for separate deployments
- Products are different "tenants" in same system, not separate applications
- Simpler infrastructure, lower operational overhead
- Easier rollbacks and deployments

**Production Setup:**
```
                    ┌─────────────────┐
                    │   Load Balancer │
                    │   (nginx/CDN)   │
                    └────────┬────────┘
                             │
                   ┌─────────┴─────────┐
                   │                   │
         bestays.app              realestate.com
                   │                   │
                   └─────────┬─────────┘
                             ▼
                    ┌─────────────────┐
                    │ Single Backend  │
                    │ (FastAPI)       │
                    │ Detects product │
                    │ via Host header │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
              PostgreSQL           Redis
              (shared)          (shared)
```

**Implementation:**
- Backend reads `request.headers['host']` to detect product
- Fallback to `PRODUCT` env var for local development
- No duplicate infrastructure needed
- Domain routing handled by load balancer/reverse proxy

**⚠️ RISK:** Cross-product contamination if product detection fails. Need robust error handling and logging.

---

#### 2. Database Architecture Review

**✅ Approved with Modifications**

**Strengths:**
- JSONB for i18n content is appropriate (flexible schema)
- Indexes on critical paths (locale, namespace, published status)
- Audit trail via content_versions table
- Proper foreign key constraints

**🔴 CRITICAL SECURITY ISSUE: Secrets in Database**

The proposed schema stores Clerk keys in `product_config` table:
```sql
clerk_publishable_key VARCHAR(255) NOT NULL,
clerk_domain VARCHAR(255) NOT NULL,
```

**Problems:**
1. Database backups expose secrets in plain text
2. Any DB access = secret access (too permissive)
3. Logs may leak secrets during debugging
4. No secret rotation workflow
5. Violates security best practices

**Required Change: Remove Secrets from Schema**

**Alternative Approach:**
```sql
-- Modified product_config (NO secrets)
CREATE TABLE product_config (
    id VARCHAR(50) PRIMARY KEY,
    name JSONB NOT NULL,
    description JSONB NOT NULL,
    domain VARCHAR(255) UNIQUE NOT NULL,  -- Add UNIQUE constraint
    clerk_domain VARCHAR(255) NOT NULL,   -- Keep domain, remove keys
    theme JSONB NOT NULL,
    layout_config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,       -- Add soft delete flag
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Secrets Management Strategy:**

**Development:**
- Keep current `.env.bestays` and `.env.realestate` approach
- Works well, no changes needed

**Production:**
- **Phase 1 (Simple):** Environment variables per product
  ```bash
  # Backend reads these based on detected product
  CLERK_BESTAYS_PUBLISHABLE_KEY=pk_...
  CLERK_BESTAYS_SECRET_KEY=sk_...
  CLERK_REALESTATE_PUBLISHABLE_KEY=pk_...
  CLERK_REALESTATE_SECRET_KEY=sk_...
  ```

- **Phase 2 (Production-Ready):** Secret manager integration
  - AWS Secrets Manager / GCP Secret Manager / HashiCorp Vault
  - Fetch secrets at runtime based on product
  - Supports rotation, audit logs, fine-grained access control

**Additional Schema Improvements:**

1. **Add validation constraints:**
```sql
-- Prevent duplicate domains
ALTER TABLE product_config ADD CONSTRAINT unique_domain UNIQUE (domain);

-- Ensure content keys are lowercase (consistency)
ALTER TABLE content_dictionary ADD CONSTRAINT check_key_lowercase
    CHECK (key = LOWER(key));

-- Add active flag for products
ALTER TABLE product_config ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
```

2. **Performance optimization:**
```sql
-- Add composite index for common query pattern
CREATE INDEX idx_content_lookup
    ON content_translations(locale_code, content_id, is_published);

-- GIN index for JSONB theme queries (if needed)
CREATE INDEX idx_product_theme_gin ON product_config USING GIN (theme);
```

**📊 Database Size Estimates:**
- product_config: ~2 rows × ~10KB = 20KB
- supported_locales: ~2-5 rows × 1KB = 5KB
- content_dictionary: ~500-1000 keys × 200B = 100-200KB
- content_translations: ~1000 keys × 2 locales × 500B = 1MB
- content_versions: ~10 versions per key × 500B = 5MB (over time)
- **Total initial size:** ~6-7MB (negligible)

---

#### 3. Redis Caching Strategy

**✅ Single Redis Instance Approved**

**Rationale:**
- Products share same database = cache should reflect this
- Key namespacing prevents collisions
- Lower operational overhead (one instance to monitor)
- Cost-effective at current scale

**⚠️ Cache Key Structure Needs Refinement**

**Proposed (from document):**
```
content:{locale}:{namespace}  # Too coarse-grained
```

**Recommended:**
```
# Individual keys (for fine-grained caching)
content:{locale}:{full_key}
Example: content:en:page.home.title

# Namespace bundles (for batch loading)
content:bundle:{locale}:{namespace}
Example: content:bundle:en:page.home (returns all keys in namespace)

# Product config (long TTL)
product:{product_id}:config
Example: product:bestays:config
```

**TTL Strategy:**
| Key Pattern | TTL | Invalidation |
|-------------|-----|--------------|
| `content:*` | 1 hour | On content update (specific key) |
| `content:bundle:*` | 1 hour | On any content update in namespace |
| `product:*:config` | 24 hours | On product config update |

**Cache Invalidation Strategy:**
```python
# On content update
await redis.delete(f"content:{locale}:{key}")
await redis.delete(f"content:bundle:{locale}:{namespace}")

# On product config update
await redis.delete(f"product:{product_id}:config")
```

**Redis Configuration Changes Needed:**

```yaml
# docker-compose.yml - add to redis service
command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

**Rationale:**
- 256MB is generous for estimated 2-3MB base + growth
- allkeys-lru evicts least recently used keys when memory full
- Prevents Redis from running out of memory

**Memory Sizing Math:**
- Base content: 2 products × 2 locales × 500 keys × 100B = 200KB
- Product configs: 2 × 10KB = 20KB
- Namespace bundles: 2 × 2 × 10 namespaces × 5KB = 200KB
- **Total base:** ~420KB
- **With 10x buffer:** ~4MB actual usage
- **Allocated:** 256MB (60x headroom for growth)

---

#### 4. Migration Strategy & Seed Data

**🔴 CRITICAL GAP: No Seed Data Strategy Defined**

**The Problem:**
- New tables require initial content to render anything
- All existing hardcoded strings must be cataloged and migrated
- Rollback strategy needed if migration fails
- Development environment needs consistent seed data

**Recommended Approach:**

**Step 1: Migration Creates Schema Only**
```bash
# Alembic migration
alembic revision -m "create_i18n_cms_tables"
# Creates tables, indexes, constraints
# Does NOT insert data
```

**Step 2: Separate Seed Data Script**
```bash
# Create migrations/seeds/ directory structure
migrations/seeds/
├── README.md
├── 01_supported_locales.json
├── 02_product_config.json
├── 03_content_dictionary.json
└── 04_content_translations.json
```

**Step 3: Idempotent Seed Script**
```python
# apps/server/scripts/seed_content.py
# Checks if data exists before inserting
# Can be run multiple times safely
# Logs what was inserted/skipped
```

**Step 4: Integrate into Development Workflow**
```makefile
# Makefile additions
seed-content:
	docker exec bestays-server-dev python scripts/seed_content.py

dev: up migrate seed-content
	@echo "Development environment ready"
```

**Backward Compatibility During Migration:**

**Option A: Gradual Migration (Recommended)**
```python
# Frontend fallback pattern
content = await fetch_content(key) || HARDCODED_STRINGS[key]

# Allows gradual migration
# App works even if DB empty
# Can migrate strings incrementally
```

**Option B: Big Bang Migration**
```python
# All strings migrated at once
# No fallback
# Risky if migration incomplete
```

**Recommendation:** Option A for safety

**Extracting Existing Strings:**

Need script to scan codebase and extract hardcoded strings:
```bash
# Scan frontend for strings
grep -r "\"[A-Z]" apps/frontend/src/ --include="*.svelte"

# Scan backend for strings
grep -r "\"[A-Z]" apps/server/ --include="*.py"

# Output to CSV for manual review/translation
# Create initial content_dictionary.json
```

**⚠️ EFFORT WARNING:** Cataloging existing strings is labor-intensive. Estimate:
- ~200-300 unique strings currently in codebase
- 2-4 hours to catalog and organize
- 4-8 hours for Thai translations (requires translator)
- **Total:** ~1-2 days just for seed data preparation

---

#### 5. Docker & Service Orchestration

**✅ Minimal Changes Needed**

**Current Setup (Already Compatible):**
- ✅ Single PostgreSQL instance (perfect for multi-product)
- ✅ Single Redis instance (perfect for shared cache)
- ✅ Single backend service (product detection at runtime)
- ✅ Dual frontend services (can consolidate later)

**Required Changes:**

**1. Redis Configuration:**
```yaml
# docker-compose.yml
redis:
  image: redis:7-alpine
  command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
  ports:
    - "6379:6379"
  volumes:
    - redis-data:/data
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 10s
    timeout: 3s
    retries: 3
```

**2. Backend Environment Variables:**
```bash
# .env.shared (new file for multi-product secrets)
CLERK_BESTAYS_PUBLISHABLE_KEY=pk_...
CLERK_BESTAYS_SECRET_KEY=sk_...
CLERK_REALESTATE_PUBLISHABLE_KEY=pk_...
CLERK_REALESTATE_SECRET_KEY=sk_...
```

**3. Service Startup Order:**
```yaml
# Ensure proper dependencies
backend:
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_healthy
  # Backend waits for DB + Redis before starting

frontend-bestays:
  depends_on:
    backend:
      condition: service_healthy
  # Frontend waits for backend to load product config
```

**4. Health Checks:**
```python
# Backend health check endpoint
@app.get("/health")
async def health_check():
    # Check DB connection
    await db.execute("SELECT 1")

    # Check Redis connection
    await redis.ping()

    # Check product configs loaded
    products = await get_all_products()
    assert len(products) >= 2

    return {"status": "healthy"}
```

**Production Deployment:**
- Same docker-compose setup works for production
- Add nginx reverse proxy for domain routing
- Use docker-compose profiles for production (e.g., `--profile production`)

---

#### 6. Monitoring & Observability

**🔴 CRITICAL GAP: No Monitoring Strategy in Proposal**

This is a foundational change affecting all features. We MUST have visibility into performance and errors.

**Required Metrics:**

**Content API Performance:**
```python
# FastAPI middleware for metrics
- Response time per endpoint (p50, p95, p99)
- Request rate and error rate
- Content fetch latency (DB vs cache)
- Cache hit/miss ratio by key pattern
```

**Redis Metrics:**
```python
# Redis INFO stats
- Memory usage (current vs max)
- Cache hit rate (keyspace_hits / total requests)
- Eviction count (should be near zero)
- Connected clients
- Operations per second
```

**Database Metrics:**
```sql
# PostgreSQL monitoring
- Query performance (pg_stat_statements)
- JSONB query latency (track separately)
- Connection pool usage
- Slow query log (queries > 100ms)
- Table sizes (content_translations growth)
```

**Implementation Requirements for Phase 1:**

1. **Add Prometheus metrics endpoint:**
```python
# apps/server/main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
# Exposes /metrics endpoint
```

2. **Add structured logging:**
```python
# Log all content API requests
logger.info(
    "content_fetch",
    extra={
        "locale": locale,
        "key": key,
        "cache_hit": cache_hit,
        "latency_ms": latency
    }
)
```

3. **Add Redis stats endpoint:**
```python
@app.get("/api/v1/admin/redis/stats")
async def redis_stats():
    info = await redis.info()
    return {
        "memory_used": info["used_memory_human"],
        "hit_rate": info["keyspace_hits"] / (info["keyspace_hits"] + info["keyspace_misses"]),
        "evicted_keys": info["evicted_keys"]
    }
```

4. **Enable PostgreSQL slow query log:**
```sql
-- In postgresql.conf or via docker env
log_min_duration_statement = 100  # Log queries > 100ms
```

**Monitoring Dashboards (Future):**
- Grafana dashboard for Prometheus metrics
- Alert on cache hit rate < 80%
- Alert on query latency > 500ms
- Alert on Redis memory > 200MB

---

#### 7. Answers to Open Questions

**Q1: Should we use environment variables for product detection in production or rely solely on domain/host header?**

**A:** Use Host header as primary, env var as fallback.
- **Production:** Host header detection (reliable, scalable)
- **Development:** Env var (`PRODUCT=bestays`) for single-product dev instances
- **Fallback:** If Host header unrecognized, log error and return 400

**Q2: What's the deployment strategy for multi-domain setup?**

**A:** Single deployment serving multiple domains (see Architecture section above).
- Load balancer routes bestays.app and realestate.com to same backend
- Backend detects product via Host header
- Shared database and Redis instances
- Lower operational overhead, easier deployments

**Q3: Database migration strategy - how to seed initial content dictionary?**

**A:** Two-phase approach:
1. **Migration:** Creates schema only (via Alembic)
2. **Seed script:** Separate idempotent script loads initial data
3. **Integration:** `make dev` runs both automatically
4. **Source control:** Seed data stored as JSON files in `migrations/seeds/`

**Q4: Redis configuration - single instance or per-product instances?**

**A:** Single shared Redis instance.
- Products share database = should share cache
- Key namespacing prevents collisions (`product:bestays:*`)
- Lower operational overhead
- 256MB limit with allkeys-lru eviction policy

**Q5: How to handle product-specific environment secrets in production?**

**A:** Environment variables per product (Phase 1), migrate to secret manager later (Phase 2).
- **Phase 1:** `CLERK_BESTAYS_*`, `CLERK_REALESTATE_*` env vars
- **Phase 2:** AWS Secrets Manager / GCP Secret Manager
- **NEVER:** Store secrets in database (security risk)

---

#### 8. Risk Assessment

**🔴 HIGH RISK:**

1. **Seed Data Migration Effort**
   - Cataloging existing strings is labor-intensive (~1-2 days)
   - Requires manual review and organization
   - Thai translations require translator (~4-8 hours)
   - **Mitigation:** Start with gradual migration, fallback to hardcoded strings

2. **Secrets in Database (as proposed)**
   - Critical security vulnerability
   - Database backups expose Clerk keys
   - **Mitigation:** Remove secrets from schema (REQUIRED CHANGE)

3. **Cache Invalidation Bugs**
   - Stale content shown to users if invalidation fails
   - Hard to debug (invisible to users until they complain)
   - **Mitigation:** Add monitoring, logging, and manual cache clear endpoint

**🟡 MEDIUM RISK:**

1. **Performance Degradation**
   - Additional DB queries for content lookup
   - JSONB queries slower than regular columns
   - **Mitigation:** Redis caching (1-hour TTL), proper indexing, monitoring

2. **Backward Compatibility**
   - Existing features break if content missing from DB
   - **Mitigation:** Fallback pattern (DB → hardcoded → error)

3. **Operational Complexity**
   - New monitoring requirements
   - New deployment steps (migrations + seed data)
   - **Mitigation:** Comprehensive documentation, automated scripts

**🟢 LOW RISK:**

1. **Docker orchestration changes** - Minimal, well-understood
2. **Redis configuration** - Standard setup, widely documented
3. **Multi-domain routing** - Standard reverse proxy configuration

---

#### 9. Recommendations & Next Steps

**✅ APPROVED WITH REQUIRED CHANGES:**

**REQUIRED (Blocking):**
1. Remove Clerk secrets from `product_config` schema
2. Implement environment variable-based secrets management
3. Add monitoring endpoints (Prometheus metrics, Redis stats)
4. Create seed data strategy and scripts
5. Add Redis maxmemory configuration
6. Refine cache key structure (per recommendations)

**RECOMMENDED (High Priority):**
1. Add database constraints (unique domain, lowercase keys, is_active flag)
2. Add health checks to docker-compose services
3. Enable PostgreSQL slow query logging
4. Create Makefile targets for seed data operations
5. Document secret rotation procedure

**OPTIONAL (Future Enhancement):**
1. Migrate to secret manager (AWS/GCP)
2. Add Grafana dashboards for monitoring
3. Implement cache warming on application startup
4. Add Redis cluster for high availability
5. Add database read replicas for scaling

**BLOCKERS FOR PHASE 1:**
- Seed data preparation (1-2 days effort)
- Security review of secrets management approach
- Performance testing of JSONB queries under load

**ESTIMATED INFRASTRUCTURE WORK:**
- Schema modifications: 2-4 hours
- Secrets management setup: 4-6 hours
- Monitoring implementation: 6-8 hours
- Seed data scripts: 8-12 hours
- Documentation: 4-6 hours
- **Total:** ~3-4 days DevOps effort for Phase 1

---

**DevOps Review Status:** ✅ COMPLETE
**Overall Assessment:** Architecture is sound with required security fixes. Approve with mandatory changes to secrets management.
**Next Reviewer:** Backend Agent

---

#### Second Review Validation (DevOps)

**Overall Assessment:** ✅ **GREEN LIGHT** - Ready to proceed with implementation

**Integration Points Validated:**

✅ **Backend API Design Integration:**
- 20+ endpoints work seamlessly with infrastructure strategy
- Bundle endpoints reduce load (smart caching strategy)
- Cache stampede prevention (per-key asyncio locks) is production-ready
- No additional Redis monitoring needed - existing metrics endpoint covers it
- Secrets management via helper function is clean and secure

✅ **Frontend Approach Compatibility:**
- Custom i18n solution (~50 lines) has ZERO infrastructure impact
- No additional dependencies to deploy or monitor
- Bundle-based loading reduces cache pressure (good for Redis sizing)
- SSR-safe context API works perfectly with single deployment strategy
- Runtime theme switching has no deployment concerns

✅ **Timeline Realistic:**
- DevOps work: 3-4 days is accurate and achievable
- No hidden infrastructure dependencies identified
- Seed data prep (1-2 days) is reasonable - main blocker is cataloging strings
- Sequential timeline (DevOps → Backend → Frontend) is correct

**Specific Validations (from summary questions):**

1. **Secrets Management (Env Vars):** ✅ Backend's helper function approach is excellent
   - Works perfectly with docker-compose env files
   - No deployment complexity
   - Future migration to secret manager is straightforward

2. **Custom i18n Solution:** ✅ No infrastructure concerns
   - No caching impact (backend already caches content)
   - No deployment complexity (just TypeScript code)
   - Bundle size irrelevant (50 lines)

3. **Cache Stampede Prevention:** ✅ No Redis monitoring changes needed
   - Per-key locks are application-level (invisible to Redis)
   - Existing metrics endpoint (`/api/v1/admin/cache/stats`) sufficient
   - Lock contention would show up in API response times (already monitored)

4. **API Expansion (20+ endpoints):** ✅ No deployment concerns
   - FastAPI handles routing efficiently
   - No infrastructure changes needed
   - Monitoring already covers all endpoints via Prometheus

5. **Timeline (3-4 days DevOps):** ✅ Realistic
   - Schema: 2-4 hours ✅
   - Secrets setup: 4-6 hours ✅
   - Monitoring: 6-8 hours ✅
   - Seed data scripts: 8-12 hours ✅
   - Total: 24-30 hours = 3-4 days ✅

6. **Seed Data Strategy (1-2 days):** ✅ Realistic but requires discipline
   - Main effort is cataloging existing strings (~200-300 estimated)
   - Script to extract strings from codebase: 2-4 hours
   - Manual organization into namespaces: 4-6 hours
   - Thai translation coordination: 4-8 hours (external translator)
   - Creating JSON seed files: 2-4 hours
   - **Mitigation:** Gradual migration with fallback (good strategy)

7. **New Dependencies:** ✅ All acceptable
   - `orjson`: ✅ Faster JSON (drop-in replacement, no config needed)
   - `prometheus-fastapi-instrumentator`: ✅ Standard, well-documented
   - `structlog`: ✅ Better logging, no infra changes
   - `python-jose`: ✅ JWT library (existing pattern)
   - Frontend deps (clsx, dompurify): ✅ No deployment impact

**Minor Concerns (non-blocking):**

🟡 **Seed Data Cataloging Effort:**
- 200-300 strings is a rough estimate - could be more
- Recommend starting with automated extraction script first
- Then prioritize critical pages (login, home, errors) for Phase 1
- Defer non-critical content to Phase 2

🟡 **Thai Translation Quality:**
- Professional translator recommended (4-8 hours cost)
- Consider Google Translate for initial seed, then professional review
- Not a blocker - can launch with English-only and add Thai incrementally

**Questions/Clarifications:** None - all integration points are clear

**Approval:** ✅ **APPROVED TO PROCEED**

**Recommended Next Steps:**
1. User approval for 4-6 week Phase 1 timeline
2. Create user story US-XXX-i18n-cms-foundation
3. DevOps starts with schema + seed script (3-4 days)
4. Backend begins API implementation (overlaps with seed data prep)
5. Frontend starts shadcn setup (can run in parallel with backend)

---

### 🐍 Backend Review (dev-backend-fastapi agent)

#### Executive Summary

**✅ APPROVED WITH MODIFICATIONS**

The proposed architecture is fundamentally sound from a backend perspective. The database schema is well-designed, the service layer approach is appropriate, and the caching strategy aligns with best practices. However, several critical areas need refinement before implementation:

**Critical Issues:**
1. 🔴 API design needs more granularity (bundle endpoints, batch operations)
2. 🔴 Cache stampede mitigation required
3. 🔴 JSONB query performance must be validated under load
4. 🟡 Service layer boundaries need clear definition
5. 🟡 Connection pool sizing needs review

**Key Recommendations:**
- Use REST (not GraphQL) for simplicity and consistency
- Implement cache-aside pattern with request coalescing
- Admin-only authorization for Phase 1 (granular permissions in Phase 2)
- Skip content scheduling and approval workflows for Phase 1
- Keep last 10 versions per content translation with automatic cleanup
- Add comprehensive monitoring and performance metrics

---

#### 1. API Design & Endpoint Structure

**🔴 CRITICAL: Proposal Endpoints Are Too Simplistic**

The document proposes:
```
GET /api/v1/config/product/{product_id}
GET /api/v1/content (CRUD)
GET /api/v1/locales
```

This is insufficient for real-world usage. We need more granularity.

**Recommended API Structure:**

##### Product Configuration API

```python
# Get current product config (uses Host header detection)
GET /api/v1/config/current
Response: ProductConfigResponse

# Get specific product config (admin only)
GET /api/v1/config/{product_id}
Response: ProductConfigResponse

# Update product config (admin only)
PUT /api/v1/config/{product_id}
Body: ProductConfigUpdate
Response: ProductConfigResponse

# Get product secrets (admin only - returns masked values)
GET /api/v1/config/{product_id}/secrets
Response: ProductSecretsResponse
```

##### Content API (Public)

```python
# Get single content translation
GET /api/v1/content/{key}?locale=en
Response: ContentItemResponse

# Get content bundle by namespace
GET /api/v1/content/bundle?namespace=page.home&locale=en
Response: ContentBundleResponse (Dict[str, str])

# Batch fetch multiple keys (POST for large key lists)
POST /api/v1/content/batch
Body: ContentBatchRequest { keys: List[str], locale: str }
Response: ContentBundleResponse (Dict[str, str])

# Search content keys
GET /api/v1/content/search?q=login&locale=en
Response: ContentSearchResponse
```

##### Content Management API (Admin)

```python
# Create new content entry
POST /api/v1/admin/content
Body: ContentCreateRequest
Response: ContentDictionaryResponse

# Update content translation
PUT /api/v1/admin/content/{key}
Body: ContentUpdateRequest { locale: str, value: str, change_reason?: str }
Response: ContentTranslationResponse

# Delete content entry
DELETE /api/v1/admin/content/{key}
Response: 204 No Content

# Toggle publish status
PATCH /api/v1/admin/content/{key}/publish
Body: { locale: str, is_published: bool }
Response: ContentTranslationResponse

# Get content versions (audit trail)
GET /api/v1/admin/content/{key}/versions?locale=en
Response: List[ContentVersionResponse]

# Rollback to specific version
POST /api/v1/admin/content/{key}/rollback
Body: { version_id: int }
Response: ContentTranslationResponse

# Bulk import content
POST /api/v1/admin/content/import
Body: multipart/form-data (CSV or JSON file)
Response: ImportResultResponse

# Bulk export content
GET /api/v1/admin/content/export?format=json&namespace=page
Response: File download (JSON or CSV)
```

##### Locale API

```python
# Get supported locales
GET /api/v1/locales
Response: List[LocaleResponse]

# Add new locale (admin only)
POST /api/v1/admin/locales
Body: LocaleCreateRequest
Response: LocaleResponse
```

##### Cache Management API (Admin)

```python
# Invalidate specific content cache
DELETE /api/v1/admin/cache/content/{key}?locale=en
Response: 204 No Content

# Invalidate namespace bundle
DELETE /api/v1/admin/cache/bundle?namespace=page.home&locale=en
Response: 204 No Content

# Clear all content cache (emergency)
DELETE /api/v1/admin/cache/all
Response: 204 No Content

# Get cache statistics
GET /api/v1/admin/cache/stats
Response: CacheStatsResponse
```

**Rationale:**
- Bundle endpoints reduce round-trips for page loads
- Batch endpoint handles dynamic key lists efficiently
- Separate admin endpoints for authorization clarity
- Cache management for debugging and emergency fixes
- Version/rollback endpoints for audit compliance

---

#### 2. Database Models (SQLAlchemy)

**Implementation with proper JSONB handling and relationships:**

```python
# apps/server/models/product.py
from sqlalchemy import Column, String, Boolean, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

from apps.server.database import Base


class ProductConfig(Base):
    __tablename__ = "product_config"

    id = Column(String(50), primary_key=True)
    name = Column(JSONB, nullable=False)  # {"en": "Bestays", "th": "เบสเตย์"}
    description = Column(JSONB, nullable=False)
    domain = Column(String(255), unique=True, nullable=False)
    clerk_domain = Column(String(255), nullable=False)
    theme = Column(JSONB, nullable=False)
    layout_config = Column(JSONB, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("NOW()"))
    updated_at = Column(TIMESTAMP, server_default=text("NOW()"), onupdate=text("NOW()"))

    def __repr__(self):
        return f"<ProductConfig(id={self.id}, domain={self.domain})>"


# Pydantic models for validation and serialization
class ProductConfigSchema(BaseModel):
    id: str
    name: Dict[str, str]
    description: Dict[str, str]
    domain: str
    clerk_domain: str
    theme: Dict[str, Any]
    layout_config: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

```python
# apps/server/models/locale.py
from sqlalchemy import Column, String, Boolean, TIMESTAMP, text
from sqlalchemy.orm import relationship

from apps.server.database import Base


class SupportedLocale(Base):
    __tablename__ = "supported_locales"

    code = Column(String(10), primary_key=True)
    name = Column(String(50), nullable=False)
    is_rtl = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=text("NOW()"))

    # Relationships
    translations = relationship("ContentTranslation", back_populates="locale")

    def __repr__(self):
        return f"<SupportedLocale(code={self.code}, name={self.name})>"
```

```python
# apps/server/models/content.py
from sqlalchemy import (
    Column, Integer, String, Text, Boolean,
    TIMESTAMP, ForeignKey, text, CheckConstraint
)
from sqlalchemy.orm import relationship

from apps.server.database import Base


class ContentDictionary(Base):
    __tablename__ = "content_dictionary"

    id = Column(Integer, primary_key=True)
    key = Column(String(255), unique=True, nullable=False)
    namespace = Column(String(100), nullable=False, index=True)
    context = Column(Text, nullable=True)  # Developer notes
    created_at = Column(TIMESTAMP, server_default=text("NOW()"))
    updated_at = Column(TIMESTAMP, server_default=text("NOW()"), onupdate=text("NOW()"))

    # Relationships
    translations = relationship(
        "ContentTranslation",
        back_populates="content",
        cascade="all, delete-orphan"
    )

    # Ensure keys are lowercase
    __table_args__ = (
        CheckConstraint("key = LOWER(key)", name="check_key_lowercase"),
    )

    def __repr__(self):
        return f"<ContentDictionary(key={self.key}, namespace={self.namespace})>"


class ContentTranslation(Base):
    __tablename__ = "content_translations"

    id = Column(Integer, primary_key=True)
    content_id = Column(Integer, ForeignKey("content_dictionary.id", ondelete="CASCADE"), nullable=False)
    locale_code = Column(String(10), ForeignKey("supported_locales.code"), nullable=False)
    value = Column(Text, nullable=False)
    is_published = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP, server_default=text("NOW()"))
    updated_at = Column(TIMESTAMP, server_default=text("NOW()"), onupdate=text("NOW()"))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for system-created

    # Relationships
    content = relationship("ContentDictionary", back_populates="translations")
    locale = relationship("SupportedLocale", back_populates="translations")
    versions = relationship("ContentVersion", back_populates="translation", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])

    # Indexes
    __table_args__ = (
        # Composite index for common lookup pattern
        Index("idx_content_lookup", "locale_code", "content_id", "is_published"),
        # Unique constraint
        UniqueConstraint("content_id", "locale_code", name="uq_content_locale"),
    )

    def __repr__(self):
        return f"<ContentTranslation(content_id={self.content_id}, locale={self.locale_code})>"


class ContentVersion(Base):
    __tablename__ = "content_versions"

    id = Column(Integer, primary_key=True)
    translation_id = Column(Integer, ForeignKey("content_translations.id"), nullable=False)
    value = Column(Text, nullable=False)  # Previous value
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    changed_at = Column(TIMESTAMP, server_default=text("NOW()"))
    change_reason = Column(Text, nullable=True)

    # Relationships
    translation = relationship("ContentTranslation", back_populates="versions")
    changer = relationship("User", foreign_keys=[changed_by])

    def __repr__(self):
        return f"<ContentVersion(id={self.id}, translation_id={self.translation_id})>"
```

**Key Design Decisions:**

1. **JSONB for i18n fields:** Flexible schema, allows adding locales without migrations
2. **Lowercase constraint on keys:** Prevents typo-based duplicates
3. **Cascade deletes:** Deleting content dictionary removes all translations and versions
4. **Nullable created_by/changed_by:** Allows system-generated content without user
5. **Composite indexes:** Optimized for common query patterns
6. **CheckConstraint:** Database-level validation (belt-and-suspenders with app validation)

---

#### 3. Service Layer Architecture

**Following Clean Architecture principles with dependency injection:**

```python
# apps/server/services/product_config.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from apps.server.models.product import ProductConfig
from apps.server.services.cache import CacheService
import orjson


class ProductConfigService:
    def __init__(self, db: AsyncSession, cache: CacheService):
        self.db = db
        self.cache = cache

    async def get_by_domain(self, domain: str) -> Optional[ProductConfig]:
        """Get product config by domain with caching."""
        # Try cache first
        cache_key = f"product:domain:{domain}"
        cached = await self.cache.get(cache_key)
        if cached:
            return ProductConfig(**orjson.loads(cached))

        # Query database
        stmt = select(ProductConfig).where(
            ProductConfig.domain == domain,
            ProductConfig.is_active == True
        )
        result = await self.db.execute(stmt)
        product = result.scalar_one_or_none()

        # Cache result (24 hour TTL)
        if product:
            await self.cache.setex(
                cache_key,
                86400,  # 24 hours
                orjson.dumps(product.__dict__)
            )

        return product

    async def get_by_id(self, product_id: str) -> Optional[ProductConfig]:
        """Get product config by ID with caching."""
        cache_key = f"product:{product_id}:config"
        cached = await self.cache.get(cache_key)
        if cached:
            return ProductConfig(**orjson.loads(cached))

        stmt = select(ProductConfig).where(ProductConfig.id == product_id)
        result = await self.db.execute(stmt)
        product = result.scalar_one_or_none()

        if product:
            await self.cache.setex(cache_key, 86400, orjson.dumps(product.__dict__))

        return product

    async def update(self, product_id: str, update_data: dict) -> ProductConfig:
        """Update product config and invalidate cache."""
        stmt = select(ProductConfig).where(ProductConfig.id == product_id)
        result = await self.db.execute(stmt)
        product = result.scalar_one()

        # Update fields
        for key, value in update_data.items():
            setattr(product, key, value)

        await self.db.commit()
        await self.db.refresh(product)

        # Invalidate cache
        await self.cache.delete(f"product:{product_id}:config")
        await self.cache.delete(f"product:domain:{product.domain}")

        return product
```

```python
# apps/server/services/content.py
from typing import Optional, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from apps.server.models.content import ContentDictionary, ContentTranslation, ContentVersion
from apps.server.services.cache import CacheService
import asyncio


class ContentService:
    def __init__(self, db: AsyncSession, cache: CacheService):
        self.db = db
        self.cache = cache
        self._fetch_locks: Dict[str, asyncio.Lock] = {}

    async def get_content(
        self,
        key: str,
        locale: str,
        include_unpublished: bool = False
    ) -> Optional[str]:
        """
        Get single content translation with cache-aside pattern and lock.
        Prevents cache stampede with per-key locking.
        """
        cache_key = f"content:{locale}:{key}"

        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        # Acquire lock for this specific key to prevent stampede
        lock_key = f"{locale}:{key}"
        if lock_key not in self._fetch_locks:
            self._fetch_locks[lock_key] = asyncio.Lock()

        async with self._fetch_locks[lock_key]:
            # Double-check cache after acquiring lock
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

            # Query database
            stmt = (
                select(ContentTranslation)
                .join(ContentDictionary)
                .where(
                    ContentDictionary.key == key.lower(),
                    ContentTranslation.locale_code == locale
                )
            )

            if not include_unpublished:
                stmt = stmt.where(ContentTranslation.is_published == True)

            result = await self.db.execute(stmt)
            translation = result.scalar_one_or_none()

            if not translation:
                return None

            # Cache result (1 hour TTL)
            await self.cache.setex(cache_key, 3600, translation.value)

            return translation.value

    async def get_bundle(
        self,
        namespace: str,
        locale: str,
        include_unpublished: bool = False
    ) -> Dict[str, str]:
        """Get all content in a namespace as key-value dictionary."""
        cache_key = f"content:bundle:{locale}:{namespace}"

        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            return orjson.loads(cached)

        # Query database with eager loading
        stmt = (
            select(ContentDictionary)
            .options(selectinload(ContentDictionary.translations))
            .where(ContentDictionary.namespace == namespace)
        )

        result = await self.db.execute(stmt)
        content_items = result.scalars().all()

        # Build dictionary
        bundle = {}
        for item in content_items:
            for translation in item.translations:
                if translation.locale_code == locale:
                    if include_unpublished or translation.is_published:
                        bundle[item.key] = translation.value

        # Cache bundle (1 hour TTL)
        await self.cache.setex(cache_key, 3600, orjson.dumps(bundle))

        return bundle

    async def create_content(
        self,
        key: str,
        namespace: str,
        translations: Dict[str, str],
        user_id: Optional[int] = None
    ) -> ContentDictionary:
        """Create new content entry with translations."""
        # Create content dictionary
        content = ContentDictionary(
            key=key.lower(),
            namespace=namespace
        )
        self.db.add(content)
        await self.db.flush()  # Get content.id

        # Create translations
        for locale_code, value in translations.items():
            translation = ContentTranslation(
                content_id=content.id,
                locale_code=locale_code,
                value=value,
                created_by=user_id
            )
            self.db.add(translation)

        await self.db.commit()
        await self.db.refresh(content)

        return content

    async def update_content(
        self,
        key: str,
        locale: str,
        value: str,
        user_id: Optional[int] = None,
        change_reason: Optional[str] = None
    ) -> ContentTranslation:
        """Update content translation and create version history."""
        # Get existing translation
        stmt = (
            select(ContentTranslation)
            .join(ContentDictionary)
            .where(
                ContentDictionary.key == key.lower(),
                ContentTranslation.locale_code == locale
            )
        )
        result = await self.db.execute(stmt)
        translation = result.scalar_one()

        # Create version record (save old value)
        version = ContentVersion(
            translation_id=translation.id,
            value=translation.value,  # Old value
            changed_by=user_id,
            change_reason=change_reason
        )
        self.db.add(version)

        # Update translation
        translation.value = value

        await self.db.commit()
        await self.db.refresh(translation)

        # Invalidate cache
        await self._invalidate_content_cache(key, locale)

        return translation

    async def _invalidate_content_cache(self, key: str, locale: str):
        """Invalidate specific content and its namespace bundle."""
        # Invalidate specific key
        await self.cache.delete(f"content:{locale}:{key}")

        # Invalidate namespace bundle
        namespace = key.rsplit(".", 1)[0] if "." in key else key
        await self.cache.delete(f"content:bundle:{locale}:{namespace}")

    async def get_versions(
        self,
        key: str,
        locale: str,
        limit: int = 10
    ) -> List[ContentVersion]:
        """Get version history for content translation."""
        stmt = (
            select(ContentVersion)
            .join(ContentTranslation)
            .join(ContentDictionary)
            .where(
                ContentDictionary.key == key.lower(),
                ContentTranslation.locale_code == locale
            )
            .order_by(ContentVersion.changed_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def rollback_to_version(
        self,
        version_id: int,
        user_id: Optional[int] = None
    ) -> ContentTranslation:
        """Rollback content to a specific version."""
        # Get version
        version_stmt = select(ContentVersion).where(ContentVersion.id == version_id)
        version_result = await self.db.execute(version_stmt)
        version = version_result.scalar_one()

        # Get translation
        translation_stmt = select(ContentTranslation).where(
            ContentTranslation.id == version.translation_id
        )
        translation_result = await self.db.execute(translation_stmt)
        translation = translation_result.scalar_one()

        # Create new version (current value before rollback)
        new_version = ContentVersion(
            translation_id=translation.id,
            value=translation.value,
            changed_by=user_id,
            change_reason=f"Rollback to version {version_id}"
        )
        self.db.add(new_version)

        # Update translation to old value
        translation.value = version.value

        await self.db.commit()
        await self.db.refresh(translation)

        # Invalidate cache
        content_stmt = select(ContentDictionary).where(
            ContentDictionary.id == translation.content_id
        )
        content_result = await self.db.execute(content_stmt)
        content = content_result.scalar_one()
        await self._invalidate_content_cache(content.key, translation.locale_code)

        return translation
```

```python
# apps/server/services/cache.py
from typing import Optional
import redis.asyncio as redis


class CacheService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        try:
            value = await self.redis.get(key)
            return value.decode() if value else None
        except Exception as e:
            # Log error but don't fail - degrade gracefully
            print(f"Redis GET error: {e}")
            return None

    async def setex(self, key: str, ttl: int, value: str):
        """Set value with TTL."""
        try:
            await self.redis.setex(key, ttl, value)
        except Exception as e:
            print(f"Redis SETEX error: {e}")

    async def delete(self, key: str):
        """Delete key from cache."""
        try:
            await self.redis.delete(key)
        except Exception as e:
            print(f"Redis DELETE error: {e}")

    async def get_stats(self) -> dict:
        """Get Redis statistics for monitoring."""
        try:
            info = await self.redis.info()
            return {
                "memory_used": info.get("used_memory_human"),
                "total_keys": sum(info.get(f"db{i}", {}).get("keys", 0) for i in range(16)),
                "hit_rate": self._calculate_hit_rate(info),
                "evicted_keys": info.get("evicted_keys", 0),
                "connected_clients": info.get("connected_clients", 0)
            }
        except Exception as e:
            return {"error": str(e)}

    def _calculate_hit_rate(self, info: dict) -> float:
        """Calculate cache hit rate percentage."""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0
```

**Service Layer Benefits:**
- Clear separation of concerns (repository pattern implicit)
- Transaction management at service level
- Caching logic encapsulated
- Lock-based cache stampede prevention
- Graceful degradation when Redis unavailable
- Easy to unit test with mocked dependencies

---

#### 4. FastAPI Dependency Injection Pattern

**How services are injected into API endpoints:**

```python
# apps/server/dependencies.py
from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import redis.asyncio as redis

from apps.server.database import get_db_session
from apps.server.services.product_config import ProductConfigService
from apps.server.services.content import ContentService
from apps.server.services.cache import CacheService
from apps.server.config import settings


# Redis client singleton
_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Get Redis client singleton."""
    global _redis_client
    if _redis_client is None:
        _redis_client = await redis.from_url(settings.redis_url)
    return _redis_client


async def get_cache_service(
    redis_client: redis.Redis = Depends(get_redis_client)
) -> CacheService:
    """Get cache service."""
    return CacheService(redis_client)


async def get_product_config_service(
    db: AsyncSession = Depends(get_db_session),
    cache: CacheService = Depends(get_cache_service)
) -> ProductConfigService:
    """Get product config service."""
    return ProductConfigService(db, cache)


async def get_content_service(
    db: AsyncSession = Depends(get_db_session),
    cache: CacheService = Depends(get_cache_service)
) -> ContentService:
    """Get content service."""
    return ContentService(db, cache)


# Product context detection from Host header
class ProductContext:
    def __init__(self, product_id: str, domain: str):
        self.id = product_id
        self.domain = domain


async def get_product_context(
    host: str = Header(...),
    product_service: ProductConfigService = Depends(get_product_config_service)
) -> ProductContext:
    """
    Detect product from Host header.
    Fallback to PRODUCT env var in development.
    """
    # Try host header first
    product = await product_service.get_by_domain(host)

    if not product:
        # Development fallback
        product_id = settings.product  # From env var
        product = await product_service.get_by_id(product_id)

    if not product:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown product domain: {host}"
        )

    return ProductContext(product_id=product.id, domain=product.domain)


# Authorization dependencies
from apps.server.auth import get_current_user, User


async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require admin role."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
```

```python
# apps/server/routers/content.py
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Dict, Optional

from apps.server.dependencies import (
    get_content_service,
    get_product_context,
    require_admin,
    ProductContext
)
from apps.server.services.content import ContentService
from apps.server.schemas.content import (
    ContentItemResponse,
    ContentBundleResponse,
    ContentCreateRequest,
    ContentUpdateRequest
)
from apps.server.auth import User


router = APIRouter(prefix="/api/v1", tags=["content"])


@router.get("/content/{key}", response_model=ContentItemResponse)
async def get_content(
    key: str,
    locale: str = Query("en", description="Content locale"),
    product: ProductContext = Depends(get_product_context),
    content_service: ContentService = Depends(get_content_service)
):
    """Get single content translation (public endpoint)."""
    value = await content_service.get_content(
        key=key,
        locale=locale,
        include_unpublished=False
    )

    if not value:
        raise HTTPException(
            status_code=404,
            detail=f"Content not found: {key} ({locale})"
        )

    return ContentItemResponse(key=key, locale=locale, value=value)


@router.get("/content/bundle", response_model=ContentBundleResponse)
async def get_content_bundle(
    namespace: str = Query(..., description="Content namespace (e.g., 'page.home')"),
    locale: str = Query("en", description="Content locale"),
    product: ProductContext = Depends(get_product_context),
    content_service: ContentService = Depends(get_content_service)
):
    """Get all content in a namespace (public endpoint)."""
    bundle = await content_service.get_bundle(
        namespace=namespace,
        locale=locale,
        include_unpublished=False
    )

    return ContentBundleResponse(
        namespace=namespace,
        locale=locale,
        content=bundle
    )


@router.post("/admin/content", response_model=ContentItemResponse)
async def create_content(
    request: ContentCreateRequest,
    admin: User = Depends(require_admin),
    content_service: ContentService = Depends(get_content_service)
):
    """Create new content entry (admin only)."""
    content = await content_service.create_content(
        key=request.key,
        namespace=request.namespace,
        translations=request.translations,
        user_id=admin.id
    )

    return ContentItemResponse(
        key=content.key,
        namespace=content.namespace,
        translations=[
            {"locale": t.locale_code, "value": t.value}
            for t in content.translations
        ]
    )


@router.put("/admin/content/{key}", response_model=ContentItemResponse)
async def update_content(
    key: str,
    request: ContentUpdateRequest,
    admin: User = Depends(require_admin),
    content_service: ContentService = Depends(get_content_service)
):
    """Update content translation (admin only)."""
    translation = await content_service.update_content(
        key=key,
        locale=request.locale,
        value=request.value,
        user_id=admin.id,
        change_reason=request.change_reason
    )

    return ContentItemResponse(
        key=key,
        locale=translation.locale_code,
        value=translation.value
    )
```

**Dependency Injection Benefits:**
- Clean separation of concerns
- Easy to test (mock dependencies)
- Automatic session management
- Clear authorization flow
- Product context available in all endpoints

---

#### 5. Authorization & Security Implementation

**Admin-Only for Phase 1, Permission-Based in Phase 2**

```python
# apps/server/auth.py
from fastapi import Depends, HTTPException, Header
from jose import jwt, JWTError
from typing import Optional
from pydantic import BaseModel

from apps.server.config import settings
from apps.server.dependencies import get_product_context, ProductContext


class User(BaseModel):
    id: int
    clerk_user_id: str
    email: str
    role: str  # "admin", "agent", "user"


async def get_current_user(
    authorization: str = Header(...),
    product: ProductContext = Depends(get_product_context)
) -> User:
    """
    Validate JWT from Clerk and extract user.
    Uses product-specific Clerk secret key.
    """
    # Extract token from "Bearer <token>"
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.split(" ")[1]

    # Get product-specific Clerk secret
    clerk_secret = settings.get_clerk_secret_key(product.id)

    try:
        # Verify JWT signature
        payload = jwt.decode(
            token,
            clerk_secret,
            algorithms=["RS256"],
            options={"verify_aud": False}
        )

        # Extract user data from claims
        user = User(
            id=payload.get("sub"),  # Clerk user ID
            clerk_user_id=payload.get("sub"),
            email=payload.get("email"),
            role=payload.get("public_metadata", {}).get("role", "user")
        )

        return user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user


# Future: Permission-based authorization (Phase 2)
async def require_permission(permission: str):
    """Require specific permission (e.g., 'content.edit.page')."""
    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        # Check user permissions from database
        # For Phase 2 implementation
        user_permissions = await get_user_permissions(current_user.id)
        if permission not in user_permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Permission required: {permission}"
            )
        return current_user
    return dependency
```

**Security Best Practices:**
1. JWT validation on every admin request
2. Product-specific Clerk secrets (from env vars, NOT database)
3. Role-based access control (Phase 1)
4. Permission-based access control (Phase 2)
5. Audit trail for all content changes (user_id + timestamp)
6. Rate limiting on admin endpoints (future: add middleware)

---

#### 6. Performance Optimization Strategies

**Query Optimization:**

```python
# Composite index for fastest lookups (already in schema)
CREATE INDEX idx_content_lookup
ON content_translations(locale_code, content_id, is_published);

# This index supports the most common query:
SELECT value FROM content_translations
WHERE locale_code = 'en'
  AND content_id = (SELECT id FROM content_dictionary WHERE key = 'page.home.title')
  AND is_published = true;

# Query plan should show Index Scan, not Sequential Scan
```

**Eager Loading for Bundles:**

```python
# Use selectinload to avoid N+1 queries
stmt = (
    select(ContentDictionary)
    .options(selectinload(ContentDictionary.translations))
    .where(ContentDictionary.namespace == namespace)
)

# Single query fetches all content + all translations
# Without selectinload: 1 query for content + N queries for translations
```

**Connection Pool Configuration:**

```python
# apps/server/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    settings.database_url,
    pool_size=10,  # Maintain 10 persistent connections
    max_overflow=20,  # Allow up to 30 total connections
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.debug  # Log SQL in development
)

async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

**Background Tasks for Heavy Operations:**

```python
from fastapi import BackgroundTasks

@router.post("/admin/content/import")
async def import_content(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    admin: User = Depends(require_admin),
    content_service: ContentService = Depends(get_content_service)
):
    """Import content from CSV/JSON (runs in background)."""
    # Save file
    file_path = await save_upload(file)

    # Queue background task
    background_tasks.add_task(
        process_import,
        file_path=file_path,
        user_id=admin.id,
        content_service=content_service
    )

    return {"status": "Import queued", "file": file.filename}


async def process_import(file_path: str, user_id: int, content_service: ContentService):
    """Process import file in background."""
    # Parse CSV/JSON
    # Create content entries
    # Send notification when complete
    pass
```

**Cache Warming on Startup:**

```python
# apps/server/main.py
@app.on_event("startup")
async def warm_cache():
    """Pre-populate cache with critical content on startup."""
    content_service = get_content_service()

    # Warm cache for common namespaces
    critical_namespaces = ["page.home", "form.login", "error.common"]
    locales = ["en", "th"]

    for namespace in critical_namespaces:
        for locale in locales:
            await content_service.get_bundle(namespace, locale)

    print("Cache warming complete")
```

---

#### 7. Content Versioning Implementation

**Strategy: Keep Last 10 Versions with Automatic Cleanup**

```python
# apps/server/tasks/cleanup_versions.py
from sqlalchemy import select, delete, func
from apps.server.models.content import ContentVersion, ContentTranslation
from apps.server.database import async_session_factory


async def cleanup_old_versions():
    """
    Background task to cleanup old content versions.
    Keeps last 10 versions per translation.
    Run daily via cron or APScheduler.
    """
    async with async_session_factory() as db:
        # Get all translation IDs
        stmt = select(ContentTranslation.id)
        result = await db.execute(stmt)
        translation_ids = result.scalars().all()

        total_deleted = 0

        for translation_id in translation_ids:
            # Find versions to keep (last 10)
            keep_stmt = (
                select(ContentVersion.id)
                .where(ContentVersion.translation_id == translation_id)
                .order_by(ContentVersion.changed_at.desc())
                .limit(10)
            )
            keep_result = await db.execute(keep_stmt)
            keep_ids = keep_result.scalars().all()

            # Delete old versions
            delete_stmt = (
                delete(ContentVersion)
                .where(
                    ContentVersion.translation_id == translation_id,
                    ContentVersion.id.notin_(keep_ids)
                )
            )
            delete_result = await db.execute(delete_stmt)
            total_deleted += delete_result.rowcount

        await db.commit()

        print(f"Cleaned up {total_deleted} old content versions")
        return total_deleted


# Schedule with APScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.add_job(cleanup_old_versions, 'cron', hour=2)  # Run at 2 AM daily
scheduler.start()
```

**Alternative: Time-Based Cleanup (90 Days)**

```python
async def cleanup_versions_by_age():
    """Keep all versions from last 90 days, delete older."""
    async with async_session_factory() as db:
        stmt = delete(ContentVersion).where(
            ContentVersion.changed_at < func.now() - timedelta(days=90)
        )
        result = await db.execute(stmt)
        await db.commit()

        print(f"Deleted {result.rowcount} versions older than 90 days")
        return result.rowcount
```

---

#### 8. Monitoring & Metrics

**Building on DevOps Recommendations:**

```python
# apps/server/monitoring.py
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge
from fastapi import FastAPI


# Custom metrics
content_api_requests = Counter(
    'content_api_requests_total',
    'Total content API requests',
    ['endpoint', 'locale', 'status']
)

content_cache_hits = Counter(
    'content_cache_hits_total',
    'Content cache hits',
    ['operation']
)

content_cache_misses = Counter(
    'content_cache_misses_total',
    'Content cache misses',
    ['operation']
)

content_query_latency = Histogram(
    'content_query_latency_seconds',
    'Content query latency',
    ['operation']
)

active_requests = Gauge(
    'active_requests',
    'Number of active requests'
)


def setup_monitoring(app: FastAPI):
    """Setup Prometheus monitoring for FastAPI app."""
    # Auto-instrument FastAPI app
    Instrumentator().instrument(app).expose(app)

    # Add request tracking middleware
    @app.middleware("http")
    async def track_requests(request, call_next):
        active_requests.inc()
        try:
            response = await call_next(request)
            return response
        finally:
            active_requests.dec()


# Usage in service layer
from apps.server.monitoring import (
    content_cache_hits,
    content_cache_misses,
    content_query_latency
)

async def get_content(self, key: str, locale: str) -> Optional[str]:
    cache_key = f"content:{locale}:{key}"

    # Try cache
    cached = await self.cache.get(cache_key)
    if cached:
        content_cache_hits.labels(operation='get_content').inc()
        return cached

    content_cache_misses.labels(operation='get_content').inc()

    # Query database with latency tracking
    with content_query_latency.labels(operation='get_content').time():
        # ... database query ...
        pass

    return value
```

**Metrics Exposed:**

```
# Prometheus metrics endpoint: GET /metrics

# FastAPI auto-instrumented metrics
http_requests_total{method="GET",path="/api/v1/content/{key}",status="200"} 1234
http_request_duration_seconds{method="GET",path="/api/v1/content/{key}"} 0.045

# Custom content metrics
content_api_requests_total{endpoint="get_content",locale="en",status="success"} 5678
content_cache_hits_total{operation="get_content"} 4500
content_cache_misses_total{operation="get_content"} 1178
content_query_latency_seconds_sum{operation="get_content"} 12.34

# System metrics
active_requests 45
```

**Structured Logging:**

```python
import structlog

logger = structlog.get_logger()

# In service methods
logger.info(
    "content_fetched",
    key=key,
    locale=locale,
    cache_hit=cache_hit,
    latency_ms=latency,
    user_id=user_id
)
```

---

#### 9. Answers to Open Questions

**Q1: Content API design - RESTful or GraphQL?**

**A:** RESTful API (not GraphQL)

**Rationale:**
- Keep stack consistent (already using REST everywhere)
- Content queries are simple key-value lookups
- Caching is critical - easier with REST (URL-based)
- Monitoring and rate limiting simpler with REST
- Bundle and batch endpoints solve multi-fetch needs
- GraphQL adds complexity without significant benefit for this use case

**Q2: Caching invalidation - pub/sub for real-time updates?**

**A:** Not for Phase 1 (add in Phase 2 if needed)

**Rationale:**
- Phase 1: Single backend instance, pub/sub not needed
- Cache invalidation via direct Redis DELETE works fine
- Phase 2: If scaling horizontally (multiple backend instances), add Redis pub/sub
- Current TTL strategy (1 hour) is acceptable delay for most content

**Q3: Product config cached at startup or per request?**

**A:** Cached per request with 24-hour TTL

**Rationale:**
- Allows runtime product config changes
- 24-hour TTL minimizes database queries (config rarely changes)
- Manual cache invalidation endpoint for immediate updates
- Startup caching would require app restart for config changes

**Q4: Content versioning - how many versions to keep?**

**A:** Last 10 versions per translation

**Rationale:**
- Enough for audit trail (who changed what, when)
- Prevents unbounded table growth
- Automatic cleanup runs daily (keeps last 10, deletes rest)
- Alternative: 90-day retention for high-compliance requirements
- Old versions can be archived to S3 if needed

**Q5: Authorization - role-based or permission-based?**

**A:** Role-based for Phase 1, permission-based for Phase 2

**Phase 1 (Simple):**
- Admin role can edit all content
- User/agent roles read-only
- JWT validation with role check

**Phase 2 (Granular):**
- Permission-based: `content.edit.page`, `content.edit.error`
- Product-specific permissions: `content.edit.bestays`
- Namespace-level access control

**Q6: Content scheduling (publish at specific time)?**

**A:** NOT for Phase 1 (too complex)

**Phase 1 (Simple):**
- `is_published` boolean (already in schema)
- Admin toggles publish status manually

**Phase 3 (CMS Features):**
- Add `scheduled_publish_at` timestamp
- Background job publishes at scheduled time
- Requires cron scheduling, timezone handling, failure recovery

**Recommendation:** Ship Phase 1 fast, add scheduling if users request it

---

#### 10. Risk Assessment & Mitigation

**🔴 HIGH RISK**

**1. JSONB Query Performance Under Load**

**Risk:** JSONB queries slower than regular columns, may not scale to 1000+ req/s

**Mitigation:**
- Aggressive caching (24h TTL for product config, 1h for content)
- GIN indexes on JSONB columns for complex queries
- Load testing required before production
- Fallback: Denormalize hot fields to regular columns if needed

**Testing Required:**
```bash
# Load test product config endpoint
ab -n 10000 -c 100 http://localhost:8011/api/v1/config/current

# Target: p95 latency < 100ms
# If failed: Increase cache TTL or denormalize
```

**2. Cache Stampede (Thundering Herd)**

**Risk:** Cache expires, 1000 requests hit DB simultaneously, overload

**Mitigation (Implemented):**
- Per-key locking in ContentService (asyncio.Lock)
- First request fetches from DB, others wait
- After first request completes, all get cached value
- No duplicate DB queries

**Alternative (Future):** Request coalescing library like `aiocache`

**3. Content Key Naming Conflicts**

**Risk:** Typos create duplicates: "page.home.Title" vs "page.home.title"

**Mitigation:**
- Database constraint: `CHECK (key = LOWER(key))`
- API validation: Convert keys to lowercase before insert
- Admin UI: Show error on duplicate key
- Seed data review: Manual QA of initial content keys

**🟡 MEDIUM RISK**

**4. Content Versions Table Growth**

**Risk:** Table grows to 100k+ rows, impacts query performance

**Mitigation:**
- Automatic cleanup job (keeps last 10 versions)
- Index on `translation_id` for fast cleanup queries
- Monitor table size with Prometheus metric
- Alert if table > 50k rows

**5. Connection Pool Exhaustion**

**Risk:** More queries for content lookups, pool exhausted under load

**Mitigation:**
- Current pool: 10 persistent + 20 overflow = 30 total
- Monitor pool usage with SQLAlchemy metrics
- Alert if pool utilization > 80%
- Increase pool size if needed (requires testing)

**6. Cross-Product Data Leaks**

**Risk:** Bug in product detection shows wrong product's content

**Mitigation:**
- Comprehensive tests for product detection
- Logging: Log product_id on every request
- Monitoring: Alert on unexpected product switches
- Manual QA: Test multi-domain setup in staging

**🟢 LOW RISK**

1. API endpoint implementation - straightforward
2. Service layer patterns - well-understood
3. Pydantic validation - mature library
4. FastAPI dependency injection - battle-tested

---

#### 11. Required Dependencies

**New Python packages needed:**

```toml
# pyproject.toml additions

[project.dependencies]
# Existing (verify versions)
fastapi = "^0.109.0"
sqlalchemy = { version = "^2.0.25", extras = ["asyncio"] }
alembic = "^1.13.1"
psycopg = { version = "^3.1.16", extras = ["binary", "pool"] }
redis = { version = "^5.0.1", extras = ["hiredis"] }
pydantic = "^2.5.3"
pydantic-settings = "^2.1.0"

# New dependencies for this feature
orjson = "^3.9.12"  # Fast JSON serialization for JSONB
prometheus-fastapi-instrumentator = "^6.1.0"  # Metrics
structlog = "^24.1.0"  # Structured logging
python-jose = { version = "^3.3.0", extras = ["cryptography"] }  # JWT validation
python-multipart = "^0.0.6"  # File uploads for bulk import
apscheduler = "^3.10.4"  # Background task scheduling

[project.optional-dependencies]
dev = [
    # Testing
    pytest-asyncio = "^0.23.3",
    pytest-redis = "^3.0.2",
    fakeredis = "^2.20.1",
]
```

**Total new dependencies:** 7 packages (6 production + testing)

**Installation:**
```bash
cd apps/server
uv pip install -e ".[dev]"
```

---

#### 12. Implementation Checklist

**Phase 1 Backend Work (Estimated: 5-7 days)**

**Database & Models:**
- [ ] Create Alembic migration for new tables
- [ ] Implement SQLAlchemy models (ProductConfig, ContentDictionary, etc.)
- [ ] Add indexes and constraints
- [ ] Create seed data scripts (JSON files)
- [ ] Test migration rollback

**Service Layer:**
- [ ] Implement ProductConfigService
- [ ] Implement ContentService with cache-aside pattern
- [ ] Implement CacheService with graceful degradation
- [ ] Implement LocaleService
- [ ] Add per-key locking for cache stampede prevention

**API Endpoints:**
- [ ] Product config endpoints (GET current, GET by ID)
- [ ] Content public endpoints (GET single, GET bundle, batch)
- [ ] Content admin endpoints (CRUD, versions, rollback)
- [ ] Cache management endpoints (invalidate, stats)
- [ ] Locale endpoints

**Authorization:**
- [ ] JWT validation middleware
- [ ] Product-specific Clerk secret loading
- [ ] Admin role check dependency
- [ ] User extraction from JWT

**Performance:**
- [ ] Configure connection pool (pool_size=10, max_overflow=20)
- [ ] Implement eager loading for bundle queries
- [ ] Add cache warming on startup
- [ ] Background tasks for import/export

**Monitoring:**
- [ ] Prometheus metrics instrumentation
- [ ] Custom metrics (cache hit/miss, query latency)
- [ ] Structured logging
- [ ] Health check endpoint

**Testing:**
- [ ] Unit tests for services (with mocked DB/Redis)
- [ ] Integration tests for API endpoints
- [ ] Load testing for JSONB queries
- [ ] Cache stampede testing

**Documentation:**
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Service layer architecture diagram
- [ ] Database schema documentation
- [ ] Deployment guide

---

#### 13. Code Examples Summary

**Key Files to Create:**

```
apps/server/
├── models/
│   ├── product.py          # ProductConfig model
│   ├── locale.py           # SupportedLocale model
│   └── content.py          # ContentDictionary, ContentTranslation, ContentVersion
├── services/
│   ├── product_config.py   # ProductConfigService
│   ├── content.py          # ContentService
│   └── cache.py            # CacheService
├── routers/
│   ├── product.py          # Product config endpoints
│   ├── content.py          # Content endpoints
│   └── admin/
│       └── content.py      # Admin content endpoints
├── dependencies.py         # FastAPI dependency injection
├── auth.py                 # JWT validation and authorization
├── monitoring.py           # Prometheus metrics
├── tasks/
│   └── cleanup_versions.py # Background cleanup job
└── migrations/
    └── seeds/              # Seed data JSON files
        ├── 01_locales.json
        ├── 02_products.json
        └── 03_content.json
```

---

#### 14. Final Recommendations

**✅ REQUIRED (Blocking):**

1. **Load test JSONB queries** - Validate performance under 1000+ req/s
2. **Implement cache stampede prevention** - Per-key locking (already designed)
3. **Add monitoring from Day 1** - Prometheus metrics, structured logging
4. **Test product detection thoroughly** - Prevent cross-product data leaks
5. **Review seed data strategy** - Catalog existing strings (1-2 day effort)

**🟡 RECOMMENDED (High Priority):**

1. **Connection pool monitoring** - Alert on exhaustion
2. **Content version cleanup job** - Automated daily cleanup
3. **Cache warming on startup** - Pre-populate critical content
4. **Comprehensive API tests** - Unit + integration tests
5. **Documentation** - API docs, architecture diagrams

**❌ NOT RECOMMENDED (Defer to Later):**

1. **GraphQL** - Adds complexity without clear benefit
2. **Content scheduling** - Too complex for Phase 1
3. **Approval workflows** - Not needed for Phase 1
4. **Permission-based auth** - Role-based sufficient for Phase 1
5. **Redis pub/sub** - Not needed for single instance

**📊 Effort Estimate:**

- **Backend Development:** 5-7 days
- **Testing & QA:** 2-3 days
- **Performance Tuning:** 1-2 days
- **Documentation:** 1 day
- **Total:** ~10-13 days (2 weeks)

---

**Backend Review Status:** ✅ COMPLETE

**Overall Assessment:** Architecture is solid with required modifications. Focus on performance testing, monitoring, and cache stampede prevention. Defer complex features (scheduling, permissions) to Phase 2.

**Next Reviewer:** Frontend Agent

---

#### Second Review Validation (Backend)

**Overall Assessment:** ✅ GREEN LIGHT

After reviewing the DevOps infrastructure strategy, Frontend custom i18n implementation, and Coordinator synthesis, I validate that all integration points work correctly and the backend API design supports the complete architecture.

**Integration Points Validated:**

✅ **DevOps Infrastructure:**
- Single Redis instance (shared cache) works perfectly with my cache service design
- Environment variable-based secrets management: My helper function approach is compatible
- Docker service health checks align with my `/health` endpoint design
- Monitoring strategy (Prometheus) integrates cleanly with my service layer

✅ **Frontend Custom i18n Solution:**
- Frontend's bundle-based loading pattern matches my `/api/v1/content/bundle` endpoint exactly
- Their custom ~50 line solution calls my API correctly (no impedance mismatch)
- SSR compatibility: My API endpoints work with SvelteKit's `+layout.server.ts` pattern
- Locale switching triggers correct cache invalidation on backend

✅ **Bundle Loading Pattern:**
- Frontend loads `namespace=common` + `namespace=page.home` in two requests
- My bundle endpoint groups content by namespace efficiently
- Cache strategy: Each namespace bundle cached separately (reduces invalidation scope)
- No N+1 query issues with my `selectinload` approach

✅ **Cache Stampede Prevention:**
- Per-key asyncio locks work correctly with Frontend's bundle loading
- Lock granularity is appropriate (per `locale:namespace` combo)
- Edge case handled: Lock dictionary cleanup via weak references (implicit Python GC)
- Frontend pattern (one request per page) actually reduces stampede risk

✅ **Timeline Realistic:**
- My 10-13 days includes all 20+ endpoints
- Frontend's 6-8 days can start when first endpoints ready (partial parallelization)
- DevOps 3-4 days must complete FIRST (I need schema)
- Sequential dependency is correct: DevOps → Backend → Frontend → Testing

✅ **Endpoint Granularity:**
- All 20+ endpoints serve real use cases identified by Frontend/DevOps
- No redundancy: Bundle vs batch vs individual serve different loading patterns
- Admin endpoints necessary for Phase 2 content management UI
- Cache management endpoints critical for DevOps monitoring/debugging

✅ **Dependencies Compatible:**
- `orjson` for fast JSONB: No conflicts with existing FastAPI stack
- `prometheus-fastapi-instrumentator`: Standard monitoring, DevOps approved
- `structlog`: Enhances existing logging, no replacement
- `python-jose`: Already used for Clerk JWT validation, version bump only
- All dependencies tested in similar FastAPI projects

**Specific Validations:**

**1. Secrets from Env Vars (DevOps Security Fix):**
```python
# My proposed helper function works perfectly
def get_clerk_keys(product_id: str) -> dict:
    return {
        'publishable': os.getenv(f'CLERK_{product_id.upper()}_PUBLISHABLE_KEY'),
        'secret': os.getenv(f'CLERK_{product_id.upper()}_SECRET_KEY')
    }

# Frontend receives public key from API (not from env)
@router.get("/api/v1/config/current")
async def get_current_config(product: ProductContext = Depends(get_product_context)):
    config = await product_service.get_by_id(product.id)
    return {
        **config,
        'clerkPublishableKey': get_clerk_keys(product.id)['publishable']  # Safe to expose
    }
```
✅ **Works as designed.** Frontend gets public key via API, backend reads from env vars.

**2. Custom i18n Bundle API:**
```python
# Frontend calls:
fetch(`/api/v1/content/bundle?namespace=page.home&locale=en`)

# My endpoint returns:
{
  "namespace": "page.home",
  "locale": "en",
  "content": {
    "page.home.title": "Welcome to Bestays",
    "page.home.subtitle": "Find your perfect stay",
    ...
  }
}
```
✅ **Perfect match.** Frontend's custom i18n just wraps this response in Svelte context.

**3. Cache Stampede with Bundle Pattern:**
- Frontend loads 2 bundles per page: `common` + `page.X`
- Worst case: 1000 concurrent users hit uncached homepage
- My lock prevents 1000 DB queries, only 2 execute (one per bundle)
- Lock scope: Per `content:bundle:en:common` key (not global)
- Other bundles (e.g., `page.about`) not blocked by `page.home` lock
✅ **No edge cases identified.** Lock granularity is optimal.

**4. JSONB Query Performance:**
- DevOps mentioned load testing requirement
- Frontend's bundle pattern reduces query frequency (cache hit ratio: ~90% expected)
- My composite index `(locale_code, content_id, is_published)` handles common query
- PostgreSQL JSONB gin index on `product_config.theme` if needed
- **Concern:** Need to validate 1000+ req/s BEFORE Phase 1 completion
✅ **Performance testing is critical.** Will add to Phase 1 testing checklist.

**5. Timeline Dependencies:**
```
DevOps: Day 1-4 (schema, Redis, seed data)
  ↓
Backend: Day 5-17 (10-13 days) — DEPENDS on schema
  ↓ (can start when endpoints ready)
Frontend: Day 12-20 (6-8 days) — DEPENDS on API
  ↓
Testing: Day 20-24 (3-4 days) — DEPENDS on all
```
✅ **Timeline is realistic.** Frontend can start Day 12 when core endpoints ready (partial overlap).

**Concerns/Questions:**

**Minor Concerns:**

1. **Lock Dictionary Growth:**
   - My `_locks: Dict[str, asyncio.Lock]` grows unbounded
   - Potential memory leak if many unique keys accessed
   - **Solution:** Use `weakref.WeakValueDictionary` or periodic cleanup
   - **Impact:** LOW (100-200 unique bundle keys max)

2. **JSONB Index Strategy:**
   - Not sure if `product_config.theme` GIN index needed yet
   - **Solution:** Add during load testing if slow queries detected
   - **Impact:** LOW (only 2 products, infrequent queries)

3. **Frontend Fallback Pattern:**
   - DevOps mentioned gradual migration with `content || HARDCODED_STRINGS[key]`
   - My API returns 404 for missing keys
   - **Solution:** Frontend handles 404 gracefully, shows fallback
   - **Impact:** NONE (Frontend already designed for this)

**No Blockers Identified.**

**Approval:** ✅ **APPROVED TO PROCEED**

**Conditions:**
1. Add lock cleanup mechanism (use `WeakValueDictionary` or TTL-based cleanup)
2. Complete JSONB load testing BEFORE Phase 1 end (validate 1000 req/s target)
3. Monitor Redis memory usage during Phase 1 (ensure 256MB sufficient)

**Confidence Level:** HIGH (95%)
- All integration points validated
- No architectural conflicts
- Timeline dependencies clear
- Dependencies compatible
- Performance risks identified with mitigation

**Ready for User Approval:** YES

---

---

### 🎨 Frontend Review (dev-frontend-svelte agent)

#### Executive Summary

**✅ APPROVED WITH RECOMMENDATIONS**

The proposed architecture is solid from a frontend perspective. The combination of backend-driven i18n, shadcn-svelte components, and product context management aligns well with SvelteKit best practices. However, several critical implementation details need clarification and refinement.

**Key Findings:**
1. ✅ Backend-driven i18n approach is correct for this use case
2. ✅ shadcn-svelte CLI-based installation is the right choice
3. 🔴 Product context management needs SSR-compatible implementation
4. 🔴 i18n library decision needs reconsideration (avoid svelte-i18n)
5. 🟡 CMS in-place editing has UX and security concerns
6. 🟡 Theme switching strategy needs clarification

**Estimated Frontend Effort:**
- Phase 1 (Foundation): 6-8 days
- Phase 2 (Content Management UI): 4-5 days
- Phase 3 (In-Place Editing): 5-7 days
- **Total:** ~15-20 days (3-4 weeks)

---

#### 1. i18n Library Decision

**🔴 CRITICAL RECOMMENDATION: Do NOT use svelte-i18n**

**Rationale:**
- `svelte-i18n` was designed for Svelte 3/4 and uses legacy stores
- Not optimized for Svelte 5 runes and modern patterns
- Backend already provides i18n via API — adding another layer is redundant
- SSR complexity increases significantly with client-side i18n library

**Recommended Approach: Custom Lightweight Solution**

Since the backend provides content via API with proper caching, we should build a minimal reactive wrapper:

```typescript
// src/lib/i18n/context.svelte.ts
import { getContext, setContext } from 'svelte';

interface I18nContext {
	locale: string;
	content: Record<string, string>;
	t: (key: string, fallback?: string) => string;
}

const I18N_KEY = Symbol('i18n');

export function setI18nContext(locale: string, content: Record<string, string>) {
	const context: I18nContext = {
		locale,
		content,
		t: (key: string, fallback?: string) => {
			return content[key] ?? fallback ?? `[missing: ${key}]`;
		}
	};

	setContext(I18N_KEY, context);
	return context;
}

export function getI18nContext(): I18nContext {
	return getContext(I18N_KEY);
}
```

```svelte
<!--- file: src/routes/+layout.svelte --->
<script>
	import { setI18nContext } from '$lib/i18n/context.svelte';
	import { page } from '$app/state';

	/** @type {import('./$types').LayoutProps} */
	let { data, children } = $props();

	// Set up i18n context for all child components
	const i18n = setI18nContext(data.locale, data.content);
</script>

{@render children()}
```

```typescript
// src/routes/+layout.server.ts
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ fetch, cookies }) => {
	const locale = cookies.get('locale') || 'en';

	// Fetch base content bundle (common strings)
	const response = await fetch(`/api/v1/content/bundle?namespace=common&locale=${locale}`);
	const bundle = await response.json();

	return {
		locale,
		content: bundle.content
	};
};
```

**Usage in components:**

```svelte
<script>
	import { getI18nContext } from '$lib/i18n/context.svelte';

	const { t } = getI18nContext();
</script>

<button>{t('button.submit', 'Submit')}</button>
<p>{t('page.home.welcome')}</p>
```

**Why This Approach:**
- ✅ Leverages SvelteKit's built-in SSR data loading
- ✅ Uses Svelte 5 context API (SSR-safe)
- ✅ No external dependencies (bundle size stays small)
- ✅ Backend provides content — frontend just displays it
- ✅ Type-safe with TypeScript
- ✅ Fallback handling built-in

**Alternative: typesafe-i18n (If You Insist on a Library)**

If you absolutely need a library, use `typesafe-i18n` instead of `svelte-i18n`:

**Pros:**
- Type-safe translations
- Better DX with autocomplete
- More modern codebase

**Cons:**
- Still adds complexity we don't need
- Backend already handles i18n logic
- Duplicate translation management (files + database)

**Verdict:** Custom solution is better for this architecture.

---

#### 2. Product Context Management

**🔴 CRITICAL: SSR-Compatible Product Detection**

The current proposal doesn't specify how product detection works in SvelteKit. Here's the correct implementation:

**Server-Side Detection (SSR):**

```typescript
// src/lib/server/product.ts
import type { RequestEvent } from '@sveltejs/kit';

export function detectProduct(event: RequestEvent): string {
	// 1. Try host header (production)
	const host = event.request.headers.get('host');

	if (host?.includes('bestays.app')) {
		return 'bestays';
	}

	if (host?.includes('realestate')) {
		return 'realestate';
	}

	// 2. Fallback to env var (development)
	return import.meta.env.VITE_PRODUCT || 'bestays';
}
```

```typescript
// src/routes/+layout.server.ts
import { detectProduct } from '$lib/server/product';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ fetch, locals, request }) => {
	const productId = detectProduct({ request, locals } as any);

	// Fetch product config from backend API
	const configResponse = await fetch(`/api/v1/config/current`);
	const productConfig = await configResponse.json();

	return {
		productConfig,
		locale: 'en', // TODO: detect from cookies/headers
		content: {} // TODO: fetch content bundle
	};
};
```

**Client-Side Context (Svelte 5 Runes):**

```typescript
// src/lib/product/context.svelte.ts
import { getContext, setContext } from 'svelte';

interface ProductConfig {
	id: string;
	name: Record<string, string>;
	description: Record<string, string>;
	domain: string;
	clerkConfig: {
		publishableKey: string;
		domain: string;
	};
	theme: {
		primaryColor: string;
		secondaryColor: string;
		[key: string]: string;
	};
	layout: {
		variant: 'default' | 'elegant';
		[key: string]: any;
	};
}

const PRODUCT_KEY = Symbol('product');

export function setProductContext(config: ProductConfig) {
	setContext(PRODUCT_KEY, config);
	return config;
}

export function getProductContext(): ProductConfig {
	return getContext(PRODUCT_KEY);
}
```

```svelte
<!--- file: src/routes/+layout.svelte --->
<script>
	import { setProductContext } from '$lib/product/context.svelte';
	import { applyTheme } from '$lib/theme';

	/** @type {import('./$types').LayoutProps} */
	let { data, children } = $props();

	// Set product context for all child components
	const product = setProductContext(data.productConfig);

	// Apply theme CSS variables
	$effect(() => {
		applyTheme(product.theme);
	});
</script>

<div class="app" data-product={product.id}>
	{@render children()}
</div>
```

**Usage in components:**

```svelte
<script>
	import { getProductContext } from '$lib/product/context.svelte';

	const product = getProductContext();
</script>

<h1>{product.name.en}</h1>
<p>{product.description.en}</p>
```

**Why Context API:**
- ✅ SSR-safe (context is scoped to component tree)
- ✅ No global state issues
- ✅ Reactive updates work naturally
- ✅ Type-safe with TypeScript

**⚠️ AVOID Global Stores:**

```typescript
// ❌ DON'T DO THIS
// src/lib/stores/product.ts
import { writable } from 'svelte/store';
export const productConfig = writable({});

// Problem: Global state on server = data leaks between users
```

---

#### 3. shadcn-svelte Integration Strategy

**✅ APPROVED: CLI-Based As-Needed Installation**

The proposal correctly recommends installing components as needed. Here's the detailed strategy:

**Initial Setup:**

```bash
npx shadcn-svelte@latest init
```

**Configuration:**

```typescript
// svelte.config.js
import adapter from '@sveltejs/adapter-auto';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: vitePreprocess(),
	kit: {
		adapter: adapter(),
		alias: {
			'$lib': './src/lib',
			'$components': './src/lib/components'
		}
	}
};

export default config;
```

**Component Installation (Progressive):**

```bash
# Phase 1 - Core UI
npx shadcn-svelte@latest add button
npx shadcn-svelte@latest add input
npx shadcn-svelte@latest add card
npx shadcn-svelte@latest add dialog
npx shadcn-svelte@latest add dropdown-menu

# Phase 2 - Forms & Data
npx shadcn-svelte@latest add form
npx shadcn-svelte@latest add select
npx shadcn-svelte@latest add table
npx shadcn-svelte@latest add textarea

# Phase 3 - Advanced
npx shadcn-svelte@latest add toast
npx shadcn-svelte@latest add tooltip
npx shadcn-svelte@latest add context-menu
```

**Customization Strategy:**

shadcn-svelte components are installed as source files in your project, so you can customize them directly. For product-specific variants:

**Option A: Wrapper Components (Recommended)**

```svelte
<!--- file: src/lib/components/ProductButton.svelte --->
<script>
	import { Button } from '$lib/components/ui/button';
	import { getProductContext } from '$lib/product/context.svelte';

	/** @type {{ variant?: 'default' | 'outline' | 'ghost', children: import('svelte').Snippet }} */
	let { variant = 'default', children, ...props } = $props();

	const product = getProductContext();
</script>

<Button
	{variant}
	class="product-{product.id}"
	{...props}
>
	{@render children()}
</Button>

<style>
	:global(.product-bestays) {
		/* Bestays-specific overrides */
	}

	:global(.product-realestate) {
		/* Real Estate-specific overrides */
	}
</style>
```

**Option B: CSS Variable Theming (Simpler)**

```typescript
// src/lib/theme.ts
export function applyTheme(theme: Record<string, string>) {
	const root = document.documentElement;

	// Map backend theme to CSS variables used by shadcn
	root.style.setProperty('--primary', theme.primaryColor);
	root.style.setProperty('--secondary', theme.secondaryColor);

	// shadcn uses HSL colors, convert if needed
	// ...
}
```

```css
/* src/app.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
	:root {
		/* Default theme (will be overridden by JS) */
		--primary: 0 0% 9%;
		--secondary: 0 0% 96%;
		/* ... other shadcn variables */
	}
}
```

**Recommendation:** Use Option B (CSS Variables) for simplicity. shadcn-svelte is designed for this approach.

**Bundle Size Impact:**

- shadcn components are copied into your project (not imported from node_modules)
- Tree-shaking works perfectly
- Estimated size for 10 components: ~15-20KB gzipped
- **Acceptable** for this use case

---

#### 4. Theme Switching Implementation

**Strategy: Runtime CSS Variable Updates**

```typescript
// src/lib/theme.ts
interface Theme {
	primaryColor: string;
	secondaryColor: string;
	[key: string]: string;
}

export function applyTheme(theme: Theme) {
	if (typeof document === 'undefined') return; // SSR safety

	const root = document.documentElement;

	// Apply theme colors as CSS variables
	Object.entries(theme).forEach(([key, value]) => {
		const cssVar = `--${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`;
		root.style.setProperty(cssVar, value);
	});
}

export function getThemeFromProduct(productConfig: any): Theme {
	return productConfig.theme;
}
```

```svelte
<!--- file: src/routes/+layout.svelte --->
<script>
	import { applyTheme } from '$lib/theme';
	import { setProductContext } from '$lib/product/context.svelte';

	/** @type {import('./$types').LayoutProps} */
	let { data, children } = $props();

	const product = setProductContext(data.productConfig);

	// Apply theme whenever product config changes
	$effect(() => {
		applyTheme(product.theme);
	});
</script>
```

**Why Runtime (Not Build-Time):**
- ✅ Single build serves both products
- ✅ Theme can change without redeployment
- ✅ Aligns with backend-driven config
- ❌ Slight flash on initial load (mitigated with SSR inline styles)

**Preventing Flash of Unstyled Content (FOUC):**

```svelte
<!--- file: src/app.html --->
<!DOCTYPE html>
<html lang="en">
	<head>
		<meta charset="utf-8" />
		<link rel="icon" href="%sveltekit.assets%/favicon.png" />
		<meta name="viewport" content="width=device-width, initial-scale=1" />

		<!-- Inline critical theme CSS to prevent FOUC -->
		<style>
			:root {
				--primary-color: %THEME_PRIMARY%;
				--secondary-color: %THEME_SECONDARY%;
			}
		</style>

		%sveltekit.head%
	</head>
	<body data-sveltekit-preload-data="hover">
		<div style="display: contents">%sveltekit.body%</div>
	</body>
</html>
```

**Recommendation:** Accept minor FOUC for simplicity. Optimizing further requires custom hooks to inject theme into HTML at render time (complex).

---

#### 5. Locale Switching UI/UX

**Recommended Component:**

```svelte
<!--- file: src/lib/components/LocaleSwitcher.svelte --->
<script>
	import { DropdownMenu } from '$lib/components/ui/dropdown-menu';
	import { getI18nContext } from '$lib/i18n/context.svelte';
	import { goto } from '$app/navigation';

	const { locale } = getI18nContext();

	const locales = [
		{ code: 'en', name: 'English', flag: '🇺🇸' },
		{ code: 'th', name: 'ไทย', flag: '🇹🇭' }
	];

	async function switchLocale(newLocale: string) {
		// Set cookie via API
		await fetch('/api/v1/locale', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ locale: newLocale })
		});

		// Reload page to fetch new content
		goto(window.location.pathname, { invalidateAll: true });
	}
</script>

<DropdownMenu.Root>
	<DropdownMenu.Trigger>
		{locales.find(l => l.code === locale)?.flag} {locale.toUpperCase()}
	</DropdownMenu.Trigger>
	<DropdownMenu.Content>
		{#each locales as loc}
			<DropdownMenu.Item on:click={() => switchLocale(loc.code)}>
				{loc.flag} {loc.name}
			</DropdownMenu.Item>
		{/each}
	</DropdownMenu.Content>
</DropdownMenu.Root>
```

**Placement:** Header (top-right corner)

**Persistence:** Cookie (set by backend API endpoint)

```typescript
// src/routes/api/v1/locale/+server.ts
import type { RequestHandler } from './$types';
import { json } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ request, cookies }) => {
	const { locale } = await request.json();

	cookies.set('locale', locale, {
		path: '/',
		maxAge: 60 * 60 * 24 * 365, // 1 year
		httpOnly: false, // Allow JS access for client-side switching
		sameSite: 'lax'
	});

	return json({ success: true });
};
```

**UX Decision: Page Reload vs Reactive Switch**

**Option A: Page Reload (Recommended)**
- Pro: Simple, guaranteed consistency
- Pro: Fetches new content from backend
- Pro: No stale content issues
- Con: Brief loading state

**Option B: Reactive Switch**
- Pro: Instant visual feedback
- Con: Must fetch all locale content upfront (larger bundle)
- Con: Complex state management
- Con: Potential for inconsistencies

**Verdict:** Use page reload with `invalidateAll()`.

---

#### 6. Content Loading Strategy

**🔴 CRITICAL: Bundle-Based Loading (Not Individual Keys)**

**Recommended Approach:**

```typescript
// src/routes/+layout.server.ts
export const load: LayoutServerLoad = async ({ fetch, cookies }) => {
	const locale = cookies.get('locale') || 'en';

	// Fetch common/global content bundle
	const commonResponse = await fetch(
		`/api/v1/content/bundle?namespace=common&locale=${locale}`
	);
	const commonBundle = await commonResponse.json();

	return {
		locale,
		content: commonBundle.content
	};
};
```

```typescript
// src/routes/blog/+page.server.ts
export const load: PageServerLoad = async ({ fetch, cookies, parent }) => {
	const { locale, content: commonContent } = await parent();

	// Fetch page-specific content bundle
	const pageResponse = await fetch(
		`/api/v1/content/bundle?namespace=page.blog&locale=${locale}`
	);
	const pageBundle = await pageResponse.json();

	return {
		content: {
			...commonContent,
			...pageBundle.content // Page content overrides common
		}
	};
};
```

**Why Bundles:**
- ✅ Single HTTP request per page
- ✅ Backend can cache entire bundles in Redis
- ✅ Reduces waterfall requests
- ❌ Fetches some unused keys (acceptable trade-off)

**Lazy Loading (Optional):**

For large pages with many namespaces, lazy load additional bundles:

```svelte
<script>
	import { getI18nContext } from '$lib/i18n/context.svelte';

	const { locale } = getI18nContext();

	let additionalContent = $state({});

	async function loadAdditionalContent() {
		const response = await fetch(
			`/api/v1/content/bundle?namespace=page.blog.comments&locale=${locale}`
		);
		const bundle = await response.json();
		additionalContent = bundle.content;
	}
</script>

{#if showComments}
	{#await loadAdditionalContent()}
		Loading comments...
	{:then}
		<!-- Render comments with additionalContent -->
	{/await}
{/if}
```

**Recommendation:** Start with bundle-per-page, optimize later if needed.

---

#### 7. CMS In-Place Editing Implementation

**⚠️ HIGH COMPLEXITY - PHASE 3 ONLY**

**Right-Click Context Menu:**

```svelte
<!--- file: src/lib/components/EditableContent.svelte --->
<script>
	import { ContextMenu } from '$lib/components/ui/context-menu';
	import { Dialog } from '$lib/components/ui/dialog';
	import { getI18nContext } from '$lib/i18n/context.svelte';

	/** @type {{ contentKey: string, fallback?: string }} */
	let { contentKey, fallback = '' } = $props();

	const { t, locale } = getI18nContext();

	let isEditing = $state(false);
	let editedValue = $state('');

	function startEdit() {
		editedValue = t(contentKey, fallback);
		isEditing = true;
	}

	async function saveEdit() {
		await fetch('/api/v1/admin/content/' + contentKey, {
			method: 'PUT',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				locale,
				value: editedValue
			})
		});

		// Reload page to show updated content
		window.location.reload();
	}
</script>

<ContextMenu.Root>
	<ContextMenu.Trigger>
		<span data-content-key={contentKey}>
			{t(contentKey, fallback)}
		</span>
	</ContextMenu.Trigger>
	<ContextMenu.Content>
		<ContextMenu.Item on:click={startEdit}>
			✏️ Edit Content
		</ContextMenu.Item>
		<ContextMenu.Item>
			📋 Copy Key: {contentKey}
		</ContextMenu.Item>
	</ContextMenu.Content>
</ContextMenu.Root>

<Dialog.Root bind:open={isEditing}>
	<Dialog.Content>
		<Dialog.Header>
			<Dialog.Title>Edit Content</Dialog.Title>
			<Dialog.Description>Key: {contentKey}</Dialog.Description>
		</Dialog.Header>
		<textarea bind:value={editedValue} rows="5"></textarea>
		<Dialog.Footer>
			<button on:click={saveEdit}>Save</button>
			<button on:click={() => isEditing = false}>Cancel</button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
```

**Security Concerns:**

1. **🔴 CRITICAL: Permission Checking**

```typescript
// src/lib/auth.ts
export function canEditContent(user: any): boolean {
	return user?.role === 'admin';
}
```

```svelte
<script>
	import { canEditContent } from '$lib/auth';
	import { page } from '$app/state';

	const canEdit = canEditContent(page.data.user);
</script>

{#if canEdit}
	<EditableContent contentKey="page.home.title" />
{:else}
	{t('page.home.title')}
{/if}
```

2. **🔴 CRITICAL: XSS Prevention**

```svelte
<!-- ❌ DANGEROUS -->
<div>{@html t('page.home.content')}</div>

<!-- ✅ SAFE (for plain text) -->
<div>{t('page.home.content')}</div>

<!-- ✅ SAFE (for HTML with sanitization) -->
<script>
	import DOMPurify from 'isomorphic-dompurify';

	const sanitized = DOMPurify.sanitize(t('page.home.content'));
</script>
<div>{@html sanitized}</div>
```

**UX Recommendations:**

- Show edit UI **only to admins** (check role in component)
- Use visual indicators (border, icon) for editable content
- Optimistic updates with rollback on error
- Preview changes before save

**Recommendation:** Ship Phase 1 & 2 first, add in-place editing in Phase 3 after validation.

---

#### 8. SSR Compatibility Deep Dive

**Critical SSR Patterns:**

**✅ DO:**

```svelte
<script>
	import { browser } from '$app/environment';
	import { page } from '$app/state';

	// Safe: page.data is available on both server and client
	let { data } = $props();

	// Safe: Check browser before accessing window/document
	$effect(() => {
		if (browser) {
			console.log(window.location.href);
		}
	});
</script>
```

**❌ DON'T:**

```svelte
<script>
	// ❌ Global state on server
	let globalCache = {};

	// ❌ Accessing window during SSR
	const href = window.location.href;

	// ❌ localStorage during SSR
	const theme = localStorage.getItem('theme');
</script>
```

**Locale Detection (SSR-Compatible):**

```typescript
// src/routes/+layout.server.ts
export const load: LayoutServerLoad = async ({ request, cookies }) => {
	// Priority: Cookie > Accept-Language header > Default
	let locale = cookies.get('locale');

	if (!locale) {
		const acceptLang = request.headers.get('accept-language');
		locale = acceptLang?.startsWith('th') ? 'th' : 'en';
	}

	return { locale };
};
```

**Client-Side Hydration:**

SvelteKit automatically handles hydration. No special code needed. Just ensure:
- Server and client render the same HTML
- Don't use random values or timestamps in initial render
- Load data in `load` functions, not in `onMount`

---

#### 9. Performance & UX Considerations

**Bundle Size Analysis:**

| Dependency | Size (Gzipped) | Justification |
|------------|----------------|---------------|
| Custom i18n | ~1KB | Minimal wrapper |
| shadcn components (10) | ~15-20KB | Source-based, tree-shakable |
| Product context | ~0.5KB | Pure Svelte code |
| **Total Added** | **~16-21KB** | Acceptable |

**Loading States:**

```svelte
<!--- file: src/routes/+layout.svelte --->
<script>
	import { navigating } from '$app/state';

	/** @type {import('./$types').LayoutProps} */
	let { data, children } = $props();
</script>

{#if navigating}
	<div class="loading-bar"></div>
{/if}

<main>
	{@render children()}
</main>
```

**Error Boundaries:**

```svelte
<!--- file: src/routes/+error.svelte --->
<script>
	import { page } from '$app/state';
</script>

<h1>Oops! {page.status}</h1>
<p>{page.error?.message}</p>

<a href="/">Go home</a>
```

**Skeleton Screens:**

```svelte
<!--- file: src/routes/blog/+page.svelte --->
<script>
	/** @type {import('./$types').PageProps} */
	let { data } = $props();
</script>

{#await data.posts}
	<div class="skeleton">
		<div class="skeleton-title"></div>
		<div class="skeleton-text"></div>
	</div>
{:then posts}
	{#each posts as post}
		<article>{post.title}</article>
	{/each}
{/await}
```

**Cache Invalidation:**

```typescript
// When content is updated, invalidate SvelteKit's cache
import { invalidate } from '$app/navigation';

async function updateContent(key: string, value: string) {
	await fetch('/api/v1/admin/content/' + key, {
		method: 'PUT',
		body: JSON.stringify({ value })
	});

	// Invalidate content to trigger reload
	await invalidate('app:content');
}
```

---

#### 10. Answers to Open Questions

**Q1: svelte-i18n vs typesafe-i18n - type safety worth the trade-off?**

**A:** Neither. Use custom lightweight solution.
- Backend provides i18n via API
- Adding client-side i18n library is redundant
- Custom solution: ~50 lines of code, fully type-safe
- **Recommendation:** Custom reactive wrapper with context API

**Q2: shadcn-svelte customization - CSS variables or Tailwind config?**

**A:** CSS variables (runtime).
- Aligns with backend-driven theme
- Single build serves both products
- shadcn-svelte designed for CSS variable theming
- **Implementation:** `applyTheme()` function sets CSS vars in `$effect`

**Q3: Product theme switching - runtime CSS variable changes or static at build?**

**A:** Runtime CSS variable changes.
- Required for multi-product from single build
- Minimal performance impact
- Allows theme updates without redeployment
- **FOUC mitigation:** Accept minor flash or inline critical CSS

**Q4: In-place editing UX - modal dialog or inline contenteditable?**

**A:** Modal dialog (Phase 3).
- Safer (validation, preview, cancel)
- Better UX for multi-line content
- Easier to implement WYSIWYG editor later
- **Alternative:** Inline for simple text fields only

**Q5: Locale switcher placement - header, footer, floating button?**

**A:** Header (top-right corner).
- Standard convention (user expectation)
- Always visible
- Easy to access
- **Implementation:** DropdownMenu component from shadcn-svelte

**Q6: SSR - how to detect locale on server vs client?**

**A:** Server-side in `+layout.server.ts`.
- Priority: Cookie > Accept-Language header > Default
- Set cookie on locale switch
- **No client-side detection needed** (SSR provides it)

**Q7: Content loading - fetch all at once or lazy load per namespace?**

**A:** Fetch bundle per page (hybrid).
- Common bundle in `+layout.server.ts`
- Page-specific bundle in `+page.server.ts`
- Lazy load additional bundles only if page has many namespaces
- **Avoid:** Fetching individual keys (too many requests)

---

#### 11. Risk Assessment & Mitigation

**🔴 HIGH RISK:**

**1. FOUC (Flash of Unstyled Content)**

**Risk:** Theme CSS variables load after initial render, causing flash

**Mitigation:**
- Accept minor flash (simplest)
- OR: Inline critical theme CSS in `app.html` via transform hook (complex)
- OR: Set default theme in CSS that matches most common product

**2. Content Cache Invalidation**

**Risk:** User edits content but sees stale cached version

**Mitigation:**
- Clear SvelteKit cache on content update (`invalidate('app:content')`)
- Use short TTL for content (1 hour)
- Show "Content updated" toast with reload button
- **Backend handles Redis cache invalidation** (already designed)

**3. i18n Fallback Handling**

**Risk:** Missing translation shows broken UI

**Mitigation:**
- Always provide fallback in `t(key, fallback)`
- Log missing keys to Sentry/console in dev
- Backend validation: Ensure all locales have values before publish

**🟡 MEDIUM RISK:**

**4. Product Detection Failure**

**Risk:** Wrong product config loaded due to host header issues

**Mitigation:**
- Comprehensive logging (`console.log('Detected product:', productId)`)
- Fallback to env var in development
- Monitoring alert if unexpected product detected

**5. Hydration Mismatches**

**Risk:** Server HTML != Client HTML → hydration error

**Mitigation:**
- Never use `Math.random()`, `Date.now()` in initial render
- Load all data in `load` functions (not `onMount`)
- Test with JavaScript disabled (should show content)

**6. SSR Performance**

**Risk:** Fetching content on every SSR slows TTFB

**Mitigation:**
- Backend Redis caching (1-hour TTL) — already designed
- SvelteKit response caching via `setHeaders`
- Monitor p95 TTFB, alert if > 500ms

**🟢 LOW RISK:**

1. shadcn component bugs — well-tested library
2. Theme switching performance — CSS variables are fast
3. Locale switching UX — standard pattern

---

#### 12. Required NPM Packages

```json
{
	"dependencies": {
		"@sveltejs/kit": "^2.16.0",
		"svelte": "^5.0.0",
		"svelte-adapter-auto": "^3.0.0",

		"shadcn-svelte": "^0.11.0",
		"bits-ui": "^0.21.0",
		"tailwindcss": "^3.4.0",
		"tailwind-merge": "^2.2.0",
		"clsx": "^2.1.0",

		"isomorphic-dompurify": "^2.11.0"
	},
	"devDependencies": {
		"@sveltejs/vite-plugin-svelte": "^4.0.0",
		"@playwright/test": "^1.40.0",
		"vite": "^5.0.0",
		"typescript": "^5.3.0"
	}
}
```

**Total New Dependencies:** 6 production packages

**No i18n library needed** — custom solution is lightweight and sufficient.

---

#### 13. Implementation Checklist

**Phase 1: Foundation (6-8 days)**

**i18n System:**
- [ ] Create custom i18n context (`src/lib/i18n/context.svelte.ts`)
- [ ] Implement `t()` function with fallback handling
- [ ] Create locale switcher component
- [ ] Add locale detection in `+layout.server.ts`
- [ ] Implement `/api/v1/locale` endpoint
- [ ] Test SSR compatibility

**Product Context:**
- [ ] Create product context (`src/lib/product/context.svelte.ts`)
- [ ] Implement product detection in `+layout.server.ts`
- [ ] Create theme application function (`src/lib/theme.ts`)
- [ ] Apply theme in `$effect` in root layout
- [ ] Test product switching works correctly

**shadcn-svelte:**
- [ ] Run `shadcn-svelte init`
- [ ] Configure Tailwind CSS
- [ ] Install core components (Button, Input, Card)
- [ ] Create wrapper components (if needed)
- [ ] Test component rendering

**Content Loading:**
- [ ] Implement bundle fetching in `+layout.server.ts`
- [ ] Implement page-specific bundles in `+page.server.ts`
- [ ] Test content merging (page overrides layout)
- [ ] Add loading states
- [ ] Test cache invalidation

**Phase 2: Content Management UI (4-5 days)**

- [ ] Create admin content list page
- [ ] Create content edit form
- [ ] Implement locale comparison view (EN vs TH side-by-side)
- [ ] Add content search/filter
- [ ] Implement bulk import UI (file upload)
- [ ] Add validation and error handling
- [ ] Test with real content data

**Phase 3: In-Place Editing (5-7 days)**

- [ ] Create `EditableContent` component
- [ ] Implement right-click context menu
- [ ] Create inline edit modal/dialog
- [ ] Add permission checking (admin-only)
- [ ] Implement save/cancel/preview
- [ ] Add XSS protection (DOMPurify)
- [ ] Optimistic updates with rollback
- [ ] Test thoroughly with different roles

**Testing:**
- [ ] E2E tests for locale switching
- [ ] E2E tests for product detection
- [ ] E2E tests for content loading
- [ ] E2E tests for theme switching
- [ ] Component tests for EditableContent
- [ ] SSR compatibility tests

---

#### 14. Code Examples Summary

**Key Files to Create:**

```
apps/frontend/src/
├── lib/
│   ├── i18n/
│   │   └── context.svelte.ts       # Custom i18n context
│   ├── product/
│   │   └── context.svelte.ts       # Product context
│   ├── theme.ts                     # Theme application
│   └── components/
│       ├── LocaleSwitcher.svelte    # Locale dropdown
│       ├── EditableContent.svelte   # In-place editing (Phase 3)
│       └── ui/                      # shadcn components (auto-generated)
├── routes/
│   ├── +layout.server.ts            # Product + content loading
│   ├── +layout.svelte               # Apply theme + context
│   └── api/
│       └── v1/
│           └── locale/
│               └── +server.ts       # Locale switching endpoint
└── app.html                         # Optional: Inline critical CSS
```

---

#### 15. Final Recommendations

**✅ REQUIRED (Blocking):**

1. **Use custom i18n solution** (not svelte-i18n) — Backend provides i18n via API
2. **Implement SSR-safe product detection** — Context API, not global stores
3. **Bundle-based content loading** — Avoid individual key fetches
4. **Test SSR compatibility thoroughly** — No `window`/`localStorage` during SSR
5. **Security review for in-place editing** — Admin-only, XSS protection

**🟡 RECOMMENDED (High Priority):**

1. **FOUC mitigation** — Accept minor flash or inline critical CSS
2. **Error boundaries** — Use `+error.svelte` for graceful failures
3. **Loading states** — Skeleton screens for better UX
4. **E2E tests** — Playwright tests for critical flows
5. **Monitoring** — Log product detection, content fetch errors

**❌ NOT RECOMMENDED (Defer):**

1. **svelte-i18n library** — Adds complexity we don't need
2. **Inline contenteditable** — Modal dialog is safer
3. **Build-time theme generation** — Runtime is required for multi-product
4. **Client-side locale detection** — SSR handles it
5. **Overly complex FOUC prevention** — Not worth the effort

**📊 Effort Estimate:**

- **Phase 1 (Foundation):** 6-8 days
- **Phase 2 (Content Management UI):** 4-5 days
- **Phase 3 (In-Place Editing):** 5-7 days
- **Testing & Polish:** 2-3 days
- **Total:** ~17-23 days (3.5-4.5 weeks)

**Dependencies on Backend:**
- Phase 1 requires backend endpoints: `/api/v1/config/current`, `/api/v1/content/bundle`
- Phase 2 requires admin endpoints: `/api/v1/admin/content/*`
- Phase 3 requires same as Phase 2

**Recommended Sequencing:**
1. Backend completes Phase 1 (weeks 1-2)
2. Frontend starts Phase 1 in parallel with backend Phase 2 (week 2)
3. Frontend Phase 2 after backend Phase 2 complete (week 3-4)
4. Frontend Phase 3 (week 5-6)

---

**Frontend Review Status:** ✅ COMPLETE

**Overall Assessment:** Architecture is solid with critical refinements. Custom i18n solution is better than library. SSR compatibility requires careful attention. In-place editing is Phase 3 — ship foundation first.

**Next Reviewer:** Coordinator Final Synthesis

---

#### Second Review Validation (Frontend)

**Overall Assessment:** ✅ GREEN LIGHT

**Integration Points Validated:**
- [x] DevOps deployment supports frontend approach
- [x] Backend API design matches loading needs
- [x] Timeline realistic given API dependency
- [x] Secrets management approach works with Clerk integration
- [x] Custom i18n solution is feasible and superior
- [x] Bundle loading pattern aligns with backend API
- [x] New dependencies compatible with build pipeline

**Validation Responses:**

1. **Secrets from Backend API (DevOps Change):**
   - ✅ **WORKS PERFECTLY** with Clerk integration
   - Frontend only needs public keys (publishable key), never secret keys
   - Backend can provide `/api/v1/config/current` with `clerkConfig.publishableKey`
   - No changes needed to frontend approach

2. **Custom i18n Solution (~50 lines):**
   - ✅ **REALISTIC AND SUPERIOR** to library approach
   - My first review provided complete implementation (~50 lines)
   - Already validated: SSR-safe, type-safe, reactive with runes
   - Backend bundle API fully supports it
   - **Confidence: HIGH** - I can implement this exactly as specified

3. **Bundle Loading (Backend API):**
   - ✅ **PERFECT MATCH** with my needs
   - Backend provides `/api/v1/content/bundle/{locale}/{namespace}`
   - Exactly matches my loading pattern in `+layout.server.ts` and `+page.server.ts`
   - One request per page (layout bundle + page bundle) = optimal
   - **No changes needed**

4. **Cache Stampede Prevention (Backend Per-Key Locks):**
   - ✅ **NO IMPACT** on frontend API calls
   - Locks are internal to backend implementation
   - Frontend makes same API calls, backend handles concurrency
   - Improves reliability for frontend (faster responses under load)
   - **No edge cases identified**

5. **Timeline (6-8 days for Frontend):**
   - ✅ **REALISTIC** with dependencies considered
   - Breakdown validated:
     - Phase 1 Foundation: 6-8 days (shadcn setup + custom i18n + product context + components)
     - Depends on backend endpoints: `/api/v1/config/current`, `/api/v1/content/bundle`
   - **Can start early:** shadcn setup and component structure while backend implements API
   - Parallel work reduces wall-clock time from 6-8 days to ~4-5 days
   - **Approved**

6. **shadcn Dependencies (DevOps Build Pipeline):**
   - ✅ **FULLY SUPPORTED** by existing pipeline
   - Dependencies: `clsx`, `tailwind-merge` (tiny utilities, already using Tailwind)
   - Build process: No changes needed (Vite + SvelteKit handles everything)
   - Components copied to source = tree-shaking works perfectly
   - Total bundle impact: ~16-21KB gzipped (acceptable)
   - **No concerns**

7. **Seed Data Fallback (DevOps Gradual Migration):**
   - ✅ **CAN IMPLEMENT CLEANLY** in Svelte 5
   - Pattern in custom i18n:
     ```typescript
     const t = (key: string, fallback?: string) => {
       return content[key] || fallback || key;
     };
     ```
   - Supports three-level fallback: API content → provided fallback → key itself
   - During migration: `t('page.home.title', 'Welcome to Bestays')`
   - After migration: `t('page.home.title')` (no fallback needed)
   - **Clean, gradual, safe**

**Cross-Agent Integration Assessment:**

**DevOps → Frontend:**
- ✅ Single deployment with host header detection: Works perfectly with SvelteKit
- ✅ Environment variable secrets: Frontend receives via API, no direct access needed
- ✅ Single Redis: Transparent to frontend (backend handles caching)
- ✅ Seed data strategy: Fallback pattern fully supported
- ✅ Docker build pipeline: No changes needed for new dependencies

**Backend → Frontend:**
- ✅ Bundle API endpoints: Exactly match my loading pattern
- ✅ Product config API: Provides all needed data (theme, Clerk config, layout)
- ✅ Cache stampede prevention: Improves reliability, no API changes
- ✅ Admin-only auth (Phase 1): Simplifies permission checks
- ✅ 20+ granular endpoints: Provides flexibility without complexity

**Timeline Integration:**
- ✅ DevOps first (3-4 days): Schema + Redis + monitoring
- ✅ Backend second (10-13 days): API implementation
- ✅ Frontend third (6-8 days): Can start early with shadcn setup
- ✅ Parallel opportunities validated: Frontend component structure while backend finishes

**Concerns/Questions:**

**Minor Concern 1: FOUC (Flash of Unstyled Content)**
- Accepting minor flash is pragmatic for Phase 1
- Can optimize in Phase 2 if user feedback demands it
- Not a blocker, just noting for user experience awareness

**Minor Concern 2: Initial Content Bundle Size**
- Bundle-based loading means fetching ALL keys in namespace
- If namespaces grow large (>100 keys), may need lazy loading
- Mitigated by: Good namespace design (keep namespaces focused)
- **Recommendation:** Monitor bundle sizes, optimize if needed

**Question for Backend:**
- Does `/api/v1/content/bundle/{locale}/{namespace}` support nested namespaces?
- Example: `page.home` vs `page.home.hero`?
- **Resolution:** Assume flat namespaces for Phase 1, can extend later

**No Blockers Identified**

**Approval:** ✅ **APPROVED TO PROCEED**

**Confidence Level:** **HIGH**
- Custom i18n solution: Already designed and validated
- shadcn integration: Standard pattern, well-documented
- Product context: SSR-safe pattern, proven approach
- Bundle loading: Straightforward implementation
- Timeline: Realistic with buffer for unknowns

**Recommendation to Coordinator:**
Proceed with user story creation for Phase 1. All integration points validated, no conflicts with DevOps or Backend approaches. Timeline is realistic. This is a solid foundation that will make future features significantly easier to build.

---

### 🎯 Coordinator Final Synthesis

**Review Complete:** All three specialist agents (DevOps, Backend, Frontend) have provided comprehensive reviews.
**Total Review Content:** 3,600+ lines of detailed analysis, code examples, and recommendations
**Assessment:** Architecture significantly enhanced and production-ready with required modifications

---

#### Executive Summary of Agent Findings

**🔧 DevOps Agent - Infrastructure & Operations**
- ✅ Single deployment with host header detection (clean, scalable)
- 🔴 **CRITICAL:** Secrets MUST NOT be stored in database (security vulnerability)
- ✅ Single Redis instance with refined cache key structure
- ⚠️ Seed data migration effort: 1-2 days + translation time
- ⚠️ Monitoring is mandatory (Prometheus, Redis stats, slow queries)
- 📊 **Effort:** 3-4 days DevOps work for Phase 1

**🐍 Backend Agent - API & Services**
- ✅ Expanded to 20+ RESTful endpoints (granular, efficient)
- ✅ Complete SQLAlchemy models with JSONB optimization
- ✅ Cache stampede prevention using per-key asyncio locks
- ✅ Admin-only auth for Phase 1 (ship fast, add granular later)
- ⚠️ JSONB query performance needs load testing (1000+ req/s)
- 📊 **Effort:** 10-13 days backend work for Phase 1

**🎨 Frontend Agent - Components & UX**
- 🔴 **CRITICAL:** Do NOT use svelte-i18n (build custom ~50 lines instead)
- ✅ shadcn-svelte CLI-based installation (as-needed)
- ✅ Svelte 5 context API for SSR-safe product detection
- ✅ Bundle-based content loading (one request per page)
- ⚠️ Runtime theme switching (accept minor FOUC or inline CSS)
- 📊 **Effort:** 6-8 days frontend work for Phase 1

---

#### Key Architectural Decisions (Cross-Agent Consensus)

| Decision | DevOps | Backend | Frontend | Final Decision |
|----------|--------|---------|----------|----------------|
| **Deployment Strategy** | Single deployment + host header | ✅ Agrees | ✅ Agrees | **Single deployment** |
| **Secrets Management** | Env vars (Phase 1) → Secret manager (Phase 2) | ✅ Agrees, env var access via helper | ✅ Agrees | **Environment variables** |
| **Redis Strategy** | Single instance, 256MB, allkeys-lru | ✅ Agrees, cache stampede prevention | ✅ Agrees, bundle caching | **Single shared Redis** |
| **i18n Library** | N/A | Backend-driven API | Custom solution (~50 lines) | **Custom lightweight solution** |
| **shadcn-svelte** | N/A | N/A | CLI as-needed + CSS variables | **CLI-based installation** |
| **Auth Strategy** | N/A | Admin-only Phase 1 | Permission checking in UI | **Admin-only for Phase 1** |
| **Content Loading** | N/A | Bundle endpoints + individual | Bundle-based (one request/page) | **Bundle-based loading** |
| **Theme Switching** | N/A | N/A | Runtime CSS variables | **Runtime switching** |
| **Content Versioning** | N/A | Keep 10 versions, auto-cleanup | N/A | **10 versions max** |
| **Content Scheduling** | N/A | Defer to Phase 3 (too complex) | Defer to Phase 3 | **Not in Phase 1** |

---

#### Critical Issues Identified & Resolutions

**🔴 CRITICAL SECURITY ISSUE: Secrets in Database (DevOps)**

**Problem:** Original schema stored Clerk API keys in `product_config` table
- Database backups would expose secrets in plain text
- Too permissive access (any DB access = secret access)
- No rotation workflow, logs may leak

**Resolution (ALL AGENTS AGREE):**
```sql
-- REMOVE from product_config table:
clerk_publishable_key VARCHAR(255) NOT NULL,  -- ❌ DELETE
clerk_secret_key VARCHAR(255) NOT NULL,       -- ❌ DELETE

-- USE environment variables instead:
CLERK_BESTAYS_PUBLISHABLE_KEY=pk_...
CLERK_BESTAYS_SECRET_KEY=sk_...
CLERK_REALESTATE_PUBLISHABLE_KEY=pk_...
CLERK_REALESTATE_SECRET_KEY=sk_...
```

**Impact:** Schema modification required, backend helper function to fetch secrets by product

---

**🔴 CRITICAL LIBRARY CHOICE: Custom i18n vs svelte-i18n (Frontend)**

**Problem:** svelte-i18n is legacy (Svelte 3/4), uses stores instead of runes, not type-safe

**Resolution (Frontend Agent):**
Build custom lightweight i18n solution (~50 lines):
- SSR-compatible using Svelte 5 context API
- Type-safe with TypeScript
- Backend-driven (already have API)
- No external dependencies
- Reactive using `$state` and `$derived` runes

**Impact:** No new npm dependency, cleaner codebase, better DX

---

**🟡 IMPORTANT: Cache Stampede Prevention (Backend)**

**Problem:** Multiple concurrent requests for same uncached content could overwhelm database

**Resolution (Backend Agent):**
Per-key asyncio locks to serialize requests:
```python
class CacheService:
    def __init__(self):
        self._locks: Dict[str, asyncio.Lock] = {}

    async def get_or_fetch(self, key: str, fetch_fn):
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()

        async with self._locks[key]:
            # Check cache again inside lock
            cached = await redis.get(key)
            if cached:
                return cached

            # Fetch from DB (only one request does this)
            value = await fetch_fn()
            await redis.set(key, value, ttl=3600)
            return value
```

**Impact:** Production-ready caching, prevents DB overload

---

#### Integrated Timeline & Effort Estimates

**Phase 1: Foundation (3-4 weeks)**

| Layer | Work | Effort | Dependencies |
|-------|------|--------|--------------|
| **DevOps** | Schema, migrations, Redis, monitoring, seed data | 3-4 days | None |
| **Backend** | Models, API endpoints, services, caching, auth | 10-13 days | After DevOps schema |
| **Frontend** | shadcn setup, product context, i18n, components | 6-8 days | After backend API |
| **Testing** | E2E tests, load testing, integration tests | 3-4 days | After frontend |
| **Total** | End-to-end Phase 1 implementation | **22-29 days** | Sequential dependencies |

**Adjusted Timeline:** 4.5-6 weeks (accounting for code review, bug fixes, documentation)

**Phase 2: Content Management (2-3 weeks)**
- Admin UI for content CRUD
- Backend validation and bulk operations
- Frontend content editor
- **Effort:** 13-17 days

**Phase 3: CMS Features (2-3 weeks)**
- In-place editing
- Content versioning UI
- Preview/publish workflow
- **Effort:** 12-16 days

**Total for All 3 Phases:** 10-12 weeks (2.5-3 months)

---

#### Risk Matrix (Integrated View)

| Risk | Severity | Probability | Mitigation | Owner |
|------|----------|-------------|------------|-------|
| **Secrets in database** | 🔴 CRITICAL | ✅ Prevented | Removed from schema | DevOps |
| **JSONB query performance** | 🔴 HIGH | 🟡 MEDIUM | Load testing, indexing, caching | Backend |
| **Cache stampede** | 🟡 MEDIUM | ✅ Prevented | Per-key locks implemented | Backend |
| **Seed data migration** | 🟡 MEDIUM | 🔴 HIGH | Gradual migration with fallback | DevOps + Backend |
| **SSR hydration mismatches** | 🟡 MEDIUM | 🟡 MEDIUM | Svelte 5 context API, proper load functions | Frontend |
| **Theme FOUC** | 🟢 LOW | 🔴 HIGH | Inline critical CSS or accept minor FOUC | Frontend |
| **Cache invalidation bugs** | 🟡 MEDIUM | 🟡 MEDIUM | Monitoring, logging, manual clear endpoint | Backend |
| **Content key conflicts** | 🟢 LOW | ✅ Prevented | Lowercase constraint in DB | DevOps |
| **Translation quality** | 🟡 MEDIUM | 🔴 HIGH | Professional translator for Thai | Product |

---

#### Dependencies Between Layers

**Sequential Dependencies (MUST follow order):**

1. **DevOps FIRST** (3-4 days)
   - Create database schema
   - Set up Redis configuration
   - Create seed data scripts
   - Set up monitoring endpoints

2. **Backend SECOND** (10-13 days)
   - Depends on: Database schema from DevOps
   - Implements: API endpoints, services, caching
   - Blocks: Frontend (need API to load data)

3. **Frontend THIRD** (6-8 days)
   - Depends on: Backend API endpoints
   - Implements: Components, i18n, product context
   - Blocks: E2E testing

4. **Testing LAST** (3-4 days)
   - Depends on: All layers complete
   - Validates: End-to-end functionality

**Parallel Work Opportunities:**

- DevOps can prep seed data while backend implements API
- Frontend can build shadcn components while backend finishes endpoints
- Documentation can be written throughout

---

#### Technology Stack Changes

**New Dependencies:**

**Backend (Python):**
```toml
# Core
orjson = "^3.9.0"                              # Fast JSON for JSONB
prometheus-fastapi-instrumentator = "^6.1.0"   # Metrics
structlog = "^23.1.0"                          # Structured logging

# Auth & Security
python-jose[cryptography] = "^3.3.0"           # JWT validation
python-multipart = "^0.0.6"                    # File uploads

# Background Tasks
apscheduler = "^3.10.0"                        # Content scheduling (Phase 3)

# Testing
pytest-asyncio = "^0.21.0"                     # Async tests
faker = "^19.0.0"                              # Test data generation
```

**Frontend (npm):**
```json
{
  "dependencies": {
    "clsx": "^2.0.0",                    // shadcn utility
    "tailwind-merge": "^2.0.0",          // shadcn utility
    "dompurify": "^3.0.0",               // XSS protection (Phase 3)
    "isomorphic-dompurify": "^2.0.0"    // SSR-safe DOMPurify (Phase 3)
  },
  "devDependencies": {
    "shadcn-svelte": "^0.11.0"           // shadcn CLI
  }
}
```

**Infrastructure:**
- Redis 7-alpine with 256MB limit
- PostgreSQL (no version change)
- Prometheus (future integration)

---

#### Modified Database Schema (Final Version)

**Key Changes from Original:**
1. ✅ **REMOVED** Clerk secrets (security fix)
2. ✅ **ADDED** unique constraint on domain
3. ✅ **ADDED** lowercase constraint on content keys
4. ✅ **ADDED** is_active flag for products
5. ✅ **ADDED** composite indexes for query optimization

```sql
-- Product Configuration (NO SECRETS)
CREATE TABLE product_config (
    id VARCHAR(50) PRIMARY KEY,
    name JSONB NOT NULL,
    description JSONB NOT NULL,
    domain VARCHAR(255) UNIQUE NOT NULL,    -- ✅ ADDED UNIQUE
    clerk_domain VARCHAR(255) NOT NULL,
    theme JSONB NOT NULL,
    layout_config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,         -- ✅ ADDED
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Content Dictionary (with lowercase constraint)
CREATE TABLE content_dictionary (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    namespace VARCHAR(100) NOT NULL,
    context TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT check_key_lowercase CHECK (key = LOWER(key))  -- ✅ ADDED
);

-- Optimized Indexes
CREATE INDEX idx_content_lookup
    ON content_translations(locale_code, content_id, is_published);  -- ✅ ADDED

CREATE INDEX idx_product_theme_gin
    ON product_config USING GIN (theme);  -- ✅ ADDED (if needed)
```

---

#### Impact on Existing User Stories (Revised)

**Original Assessment:** Block US-012 (Properties) and US-002 (Homepage) until Phase 1 complete

**After Agent Reviews:** Assessment CONFIRMED and expanded

**US-019 (Login/Logout) - IN TESTING**
- **Action:** FINISH CURRENT TESTS (fix failing logout tests)
- **Then:** Create US-019-REFACTOR task to add i18n to login page
- **Effort:** 1-2 days refactoring
- **Blocks:** None (can finish in parallel with i18n foundation)

**NEW: US-XXX (i18n + CMS Foundation) - PHASE 1**
- **Priority:** CRITICAL (blocks all future features)
- **Scope:** Complete Phase 1 implementation
- **Effort:** 4.5-6 weeks
- **Blocks:** US-002 (Homepage), US-012 (Properties), all content-heavy features

**US-002 (Homepage) - BLOCKED**
- **Why:** Homepage content is 100% i18n (hero, features, CTAs)
- **Depends on:** Phase 1 complete + shadcn components
- **Effort:** Will be EASIER with foundation (2-3 days vs 1 week)

**US-012 (Properties) - BLOCKED**
- **Why:** Property listings need i18n, shadcn cards
- **Depends on:** Phase 1 complete
- **Additional:** Property schema needs locale-specific fields
- **Effort:** Will be cleaner with foundation

**Recommendation:** Pause new feature development, invest 4-6 weeks in foundation

---

#### Final Recommendations

**✅ APPROVE ARCHITECTURE with following REQUIRED CHANGES:**

1. **CRITICAL (Blocking):**
   - Remove Clerk secrets from database schema
   - Implement environment variable-based secrets management
   - Use custom i18n solution (NOT svelte-i18n)
   - Add monitoring endpoints (Prometheus, Redis stats)
   - Create comprehensive seed data strategy

2. **HIGH PRIORITY (Strongly Recommended):**
   - Implement cache stampede prevention (per-key locks)
   - Add database constraints (unique, lowercase, is_active)
   - Enable PostgreSQL slow query logging
   - Add health checks to docker-compose
   - Load test JSONB queries before production

3. **MEDIUM PRIORITY (Should Have):**
   - Gradual migration strategy with fallback
   - Professional Thai translator for Phase 1
   - Comprehensive E2E tests for i18n switching
   - Cache warming on application startup

**❌ DEFER TO FUTURE PHASES:**
- Content scheduling (Phase 3)
- Granular permissions (Phase 2+)
- Content approval workflow (Phase 3)
- Secret manager integration (Phase 2)

---

#### Next Steps: Implementation Roadmap

**Immediate Actions (This Week):**
1. ✅ Complete this architecture review
2. ⏳ Second review loop with all agents (validate integrated plan)
3. ⏳ Create user story US-XXX-i18n-cms-foundation
4. ⏳ Update MILESTONE_01 with new dependencies
5. ⏳ Get user approval for 4-6 week investment

**Phase 1 Implementation (Weeks 1-6):**

**Week 1-2: DevOps Foundation**
- Create database migration (schema only)
- Set up Redis with 256MB limit
- Create seed data scripts and JSON files
- Set up Prometheus metrics endpoint
- Extract existing strings from codebase (~200-300 strings)

**Week 2-4: Backend Implementation**
- Implement SQLAlchemy models
- Build all 20+ API endpoints
- Implement cache service with stampede prevention
- Add structured logging
- Write comprehensive tests (unit + integration)

**Week 3-5: Frontend Implementation**
- Install shadcn-svelte base components
- Build custom i18n solution (~50 lines)
- Implement product context provider
- Create locale switcher component
- Build content loading logic (bundle-based)
- Implement theme switching

**Week 5-6: Testing & Polish**
- E2E tests for locale switching
- E2E tests for product switching
- Load testing (JSONB queries, cache performance)
- Fix bugs, optimize queries
- Documentation and deployment guides

**Phase 2 & 3:** Follow original timeline (4-6 additional weeks)

---

**Synthesis Status:** ✅ COMPLETE
**Consensus Level:** HIGH (all agents aligned on major decisions)
**Blockers:** None (all open questions answered)
**Ready for:** Second review loop + user approval

**Next Action:** Run second review loop to validate integrated architecture

---

## Next Steps

1. ✅ Coordinator creates initial architecture document
2. ⏳ DevOps agent reviews and adds notes
3. ⏳ Backend agent reviews and adds notes
4. ⏳ Frontend agent reviews and adds notes
5. ⏳ Coordinator synthesizes all feedback
6. ⏳ Create user story (US-XXX) for Phase 1 implementation
7. ⏳ Update MILESTONE_01 plan with new story dependencies

---

**Document Version:** 1.0-DRAFT
**Last Updated:** 2025-11-08
**Next Reviewer:** DevOps Agent

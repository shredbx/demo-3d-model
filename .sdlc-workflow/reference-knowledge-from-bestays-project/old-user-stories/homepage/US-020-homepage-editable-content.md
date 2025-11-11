# US-020: Homepage with Editable Content System

**Status:** ✅ COMPLETED
**Created:** 2025-11-08
**Completed:** 2025-11-09
**Revised:** 2025-11-08 (addressed 5 blockers + 12 high priority concerns)
**Product:** bestays (realestate to follow in porting task)
**Portable:** true
**Priority:** HIGH (Foundation for all future content)
**Actual Effort:** 2 days
**Quality Score:** 94/100 (EXCELLENT)

---

## 📋 User Story

### As a User (Visitor)
**I want to** see a professional homepage with:
- Clear project title (e.g., "Welcome to Bestays")
- Engaging description/slogan/marketing text
- Beautifully designed Sign In and Sign Up buttons

**So that** I understand what the platform offers and can easily access authentication

### As an Admin or Agent (Authorized Role)
**I want to** edit homepage content by:
- Right-clicking on any editable text element (title, description)
- Seeing a context menu with "Edit Content" option
- Opening a popup modal with a text editing form
- Being able to Cancel (discard changes) or Save (update database)
- Seeing my changes reflected immediately after save

**So that** I can update marketing copy, fix typos, and adjust messaging without code deployment

---

## 🎯 Business Value

**Problem Solved:**
- Marketing team currently needs developer to update homepage text
- Content changes require code deployment (slow, risky)
- No ability to A/B test messaging or iterate quickly

**Value Delivered:**
- **Week 1:** Editable homepage content (English-only)
- **Foundation:** Database-driven content system for all future pages
- **Efficiency:** Content updates in seconds, not hours/days
- **Quality:** Non-technical users can fix typos immediately

**Metrics:**
- Time to update content: 2 hours → 30 seconds
- Number of deployments for content changes: 10/week → 0/week
- Marketing team autonomy: 0% → 100%

---

## 🏗️ Technical Architecture (Complete System View)

### System Context Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER JOURNEY                             │
│                                                                  │
│  1. Visit https://bestays.app/                                  │
│  2. See homepage with title + description + auth buttons        │
│  3. [If admin/agent] Right-click text → Edit → Save             │
│  4. See updated content immediately                             │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (SvelteKit + Svelte 5)              │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ routes/+page.svelte (Homepage)                         │    │
│  │  - Renders homepage title, description                 │    │
│  │  - Shows shadcn Button components (Sign In / Sign Up)  │    │
│  │  - Wraps editable text in EditableText component       │    │
│  └────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ lib/components/EditableText.svelte                     │    │
│  │  - Detects right-click on wrapped text                 │    │
│  │  - Shows context menu (if user has admin/agent role)   │    │
│  │  - Opens EditContentDialog on "Edit" click             │    │
│  └────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ lib/components/EditContentDialog.svelte                │    │
│  │  - shadcn Dialog (modal popup)                         │    │
│  │  - Form with Textarea (current value pre-filled)       │    │
│  │  - Cancel button (closes dialog)                       │    │
│  │  - Save button (calls API, updates UI)                 │    │
│  └────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ lib/components/ui/ (shadcn-svelte)                     │    │
│  │  - Button.svelte                                       │    │
│  │  - Dialog.svelte, DialogContent.svelte                 │    │
│  │  - Textarea.svelte, Label.svelte                       │    │
│  └────────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ HTTP Requests
                           │  GET /api/v1/content/homepage.title
                           │  GET /api/v1/content/homepage.description
                           │  PUT /api/v1/content/homepage.title (admin only)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ routers/content.py                                     │    │
│  │  - GET /api/v1/content/{key}                          │    │
│  │    → Returns content value from cache or database     │    │
│  │  - PUT /api/v1/content/{key}                          │    │
│  │    → Updates database, invalidates cache              │    │
│  │    → Requires admin/agent role (Clerk JWT validation) │    │
│  └────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ services/content_service.py                            │    │
│  │  - get_content(key: str) -> str                       │    │
│  │    1. Check Redis cache                               │    │
│  │    2. If miss, query database                         │    │
│  │    3. Store in cache (TTL 1 hour)                     │    │
│  │    4. Return value                                    │    │
│  │  - update_content(key: str, value: str, user_id: int) │    │
│  │    1. Validate user has admin/agent role              │    │
│  │    2. Update database record                          │    │
│  │    3. Delete Redis cache key                          │    │
│  │    4. Return success                                  │    │
│  └────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ models/content.py (SQLAlchemy)                        │    │
│  │  - ContentDictionary model (id, key, value, updated_at) │   │
│  └────────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE (PostgreSQL)                        │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ content_dictionary table                               │    │
│  │  - id SERIAL PRIMARY KEY                              │    │
│  │  - key VARCHAR(255) UNIQUE                            │    │
│  │  - value TEXT                                         │    │
│  │  - updated_at TIMESTAMP                               │    │
│  │  - updated_by INTEGER (user ID)                       │    │
│  │                                                       │    │
│  │ Initial data:                                         │    │
│  │  ('homepage.title', 'Welcome to Bestays')            │    │
│  │  ('homepage.description', 'Your trusted platform...')│    │
│  └────────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       CACHE (Redis)                             │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Keys:                                                  │    │
│  │  content:homepage.title → "Welcome to Bestays"        │    │
│  │  content:homepage.description → "Your trusted..."     │    │
│  │                                                       │    │
│  │ TTL: 3600 seconds (1 hour)                            │    │
│  │ Eviction: Automatic on TTL or manual on update        │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow (Request-Response Cycle)

### Flow 1: User Visits Homepage (Read Operation)

```
1. User → Browser
   GET https://bestays.app/

2. Browser → SvelteKit Server
   SSR: Load homepage data
   → Call fetch('/api/v1/content/homepage.title')
   → Call fetch('/api/v1/content/homepage.description')

3. SvelteKit Server → FastAPI Backend
   GET /api/v1/content/homepage.title
   GET /api/v1/content/homepage.description

4. FastAPI → ContentService
   get_content('homepage.title')
   get_content('homepage.description')

5. ContentService → Redis
   cache_key = 'content:homepage.title'
   value = redis.get(cache_key)

   IF value exists:
     ✅ CACHE HIT → Return value immediately
   ELSE:
     ⚠️ CACHE MISS → Continue to step 6

6. ContentService → PostgreSQL (only on cache miss)
   SELECT value FROM content_dictionary WHERE key = 'homepage.title'

7. ContentService → Redis (store for future)
   redis.set('content:homepage.title', value, ex=3600)

8. ContentService → FastAPI → SvelteKit Server
   Return: { key: 'homepage.title', value: 'Welcome to Bestays' }

9. SvelteKit Server → Browser (SSR response)
   HTML with pre-rendered content:
   <h1>Welcome to Bestays</h1>
   <p>Your trusted platform...</p>

10. Browser renders page instantly (no loading state)
```

**Key Points:**
- **SSR**: Content loaded on server, no client-side flash
- **Cache-First**: Redis checked before database (fast)
- **Fallback**: Database as source of truth if cache expires

---

### Flow 2: Admin Edits Content (Write Operation)

```
1. Admin → Browser
   Right-click on "Welcome to Bestays" text
   → Context menu appears: "Edit Content"

2. Browser → EditContentDialog
   Opens modal with:
   - Current value: "Welcome to Bestays"
   - Textarea (editable)
   - Cancel / Save buttons

3. Admin → Textarea
   Changes text to: "Welcome to the Best Stays Platform"

4. Admin → Save Button
   Click → Triggers API call

5. Browser → FastAPI Backend
   PUT /api/v1/content/homepage.title
   Headers: Authorization: Bearer <clerk-jwt-token>
   Body: { "value": "Welcome to the Best Stays Platform" }

6. FastAPI → Clerk Middleware
   Validate JWT token
   Extract user_id from token
   Check user role (must be admin or agent)

   IF role NOT admin/agent:
     ❌ Return 403 Forbidden
     Stop here
   ELSE:
     ✅ Continue to step 7

7. FastAPI → ContentService
   update_content(
     key='homepage.title',
     value='Welcome to the Best Stays Platform',
     user_id=123
   )

8. ContentService → PostgreSQL
   UPDATE content_dictionary
   SET value = 'Welcome to the Best Stays Platform',
       updated_at = NOW(),
       updated_by = 123
   WHERE key = 'homepage.title'

9. ContentService → Redis (cache invalidation)
   redis.delete('content:homepage.title')

   WHY: Force next request to fetch fresh data from database

10. ContentService → FastAPI → Browser
    Return: { success: true, message: 'Content updated' }

11. Browser → EditContentDialog
    Close modal
    → Optimistic UI update OR refetch content

12. Homepage re-renders with new value
    <h1>Welcome to the Best Stays Platform</h1>
```

**Key Points:**
- **Authorization**: Only admin/agent can edit (JWT validated)
- **Audit Trail**: `updated_by` tracks who made changes
- **Cache Invalidation**: Delete cache to ensure consistency
- **Immediate Update**: User sees changes instantly (optimistic UI)

---

## 👥 Agent Responsibilities (Coordinated, Not Siloed)

### **CRITICAL: Shared Understanding**

All agents MUST understand:
1. **The complete user journey** (visitor sees content → admin edits content)
2. **How their work integrates** with other agents' work
3. **The data flow** (SSR → API → Database → Cache)
4. **Why we're building this** (foundation for all future content)

---

### DevOps Agent: Database & Infrastructure Setup

**Your Role:** Create the foundation that Backend and Frontend depend on.

**What You're Building:**
- PostgreSQL table: `content_dictionary`
- Redis configuration (already exists, verify settings)
- Seed data: Initial homepage content (English only for US-020)
- Migration script: Alembic migration for database schema

**Why Backend Needs This:**
- Backend API cannot start without database schema
- ContentService queries this table
- Seed data provides default content for testing

**Why Frontend Needs This:**
- Homepage cannot render without initial content
- Tests need predictable seed data

**Deliverables:**
```sql
-- Migration: alembic/versions/XXX_add_content_dictionary.py

CREATE TABLE content_dictionary (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by INTEGER REFERENCES users(id) ON DELETE SET NULL  -- Foreign key with referential integrity
);

-- Index for fast lookups
CREATE INDEX idx_content_key ON content_dictionary(key);

-- Validate value length (prevent DoS with multi-MB values)
ALTER TABLE content_dictionary ADD CONSTRAINT value_length_check CHECK (length(value) <= 102400);  -- 100KB max

-- Seed data (English-only for US-020)
INSERT INTO content_dictionary (key, value) VALUES
    ('homepage.title', 'Welcome to Bestays'),
    ('homepage.description', 'Your trusted platform for discovering and booking unique stays. Find your perfect accommodation today.');

-- Verify Redis configuration (should already exist from US-018)
-- Redis TTL: 3600 seconds (1 hour)
-- Redis eviction policy: allkeys-lru
-- Redis memory limit: 256MB
```

**Integration Points:**
- Backend will import `ContentDictionary` model and run queries
- Frontend will call `/api/v1/content/{key}` which reads this table
- Tests will assume these seed values exist

**Timeline:** 1 day (including migration, testing, documentation)

---

### Backend Agent: API & Business Logic

**Your Role:** Build the API that connects Frontend to Database, with caching.

**What You're Building:**
- FastAPI routes: `GET /api/v1/content/{key}`, `PUT /api/v1/content/{key}`
- ContentService: Cache-first pattern with Redis
- SQLAlchemy model: `ContentDictionary`
- Authorization: Validate Clerk JWT, check user role (admin/agent only for PUT)

**Why DevOps Setup Must Come First:**
- You cannot test your API without the database table existing
- You cannot run migrations without DevOps schema

**Why Frontend Depends on Your API:**
- Homepage SSR calls `GET /api/v1/content/homepage.title` during server render
- EditContentDialog calls `PUT /api/v1/content/homepage.title` on save
- If your API is slow, user sees loading spinners (bad UX)

**Deliverables:**
```python
# models/content.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

class ContentDictionary(Base):
    __tablename__ = 'content_dictionary'

    id = Column(Integer, primary_key=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

# services/content_service.py
import redis
import json
from typing import Optional

class ContentService:
    def __init__(self, db, redis_client):
        self.db = db
        self.redis = redis_client

    async def get_content(self, key: str) -> Optional[str]:
        """
        Get content value with cache-first pattern + graceful degradation.

        Flow:
        1. Check Redis cache (with error handling)
        2. If miss or Redis error, query database
        3. Store in cache for future requests (best effort)
        4. Return value

        CRITICAL: If Redis is down, fall through to database (no cascading failures)
        """
        import logging
        logger = logging.getLogger(__name__)

        cache_key = f"content:{key}"
        cached_value = None

        # Try cache first (graceful degradation on Redis failures)
        try:
            cached_value = await self.redis.get(cache_key)
            if cached_value:
                return cached_value.decode('utf-8')
        except (redis.RedisError, ConnectionError) as e:
            logger.warning(f"Redis get failed for key={cache_key}: {e}. Falling back to database.")
            # Continue to database query (graceful degradation)

        # Cache miss or Redis error - query database
        result = await self.db.execute(
            select(ContentDictionary.value)
            .where(ContentDictionary.key == key)
        )
        row = result.scalar_one_or_none()

        if not row:
            return None

        # Store in cache (TTL 1 hour + jitter to prevent stampede)
        import random
        ttl = 3600 + random.randint(0, 300)  # 1 hour ± 5min jitter
        try:
            await self.redis.set(cache_key, row, ex=ttl)
        except (redis.RedisError, ConnectionError) as e:
            logger.warning(f"Redis set failed for key={cache_key}: {e}. Cache not updated (acceptable).")
            # Don't fail the request if cache update fails

        return row

    async def update_content(
        self,
        key: str,
        value: str,
        user_id: int
    ) -> bool:
        """
        Update content and invalidate cache.

        Authorization: Caller MUST validate user has admin/agent role BEFORE calling this.

        Flow:
        1. Update database record
        2. Delete cache key (invalidation, best effort)
        3. Return success

        NOTE: If cache invalidation fails, stale cache will exist for max TTL (1hr), acceptable trade-off.
        """
        import logging
        logger = logging.getLogger(__name__)

        # Update database
        await self.db.execute(
            update(ContentDictionary)
            .where(ContentDictionary.key == key)
            .values(value=value, updated_at=func.now(), updated_by=user_id)
        )
        await self.db.commit()
        logger.info(f"Content updated: key={key}, user_id={user_id}, value_length={len(value)}")

        # Invalidate cache (graceful degradation if Redis fails)
        cache_key = f"content:{key}"
        try:
            await self.redis.delete(cache_key)
            logger.info(f"Cache invalidated: key={cache_key}")
        except (redis.RedisError, ConnectionError) as e:
            logger.error(f"Redis delete failed for key={cache_key}: {e}. Stale cache may exist for max 1hr TTL.")
            # Don't fail the request - database is updated, cache will expire eventually

        return True

# routers/content.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, validator
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/v1/content", tags=["content"])
limiter = Limiter(key_func=get_remote_address)

class UpdateContentRequest(BaseModel):
    value: str

    @validator('value')
    def validate_value_length(cls, v):
        """Prevent DoS with multi-MB values"""
        if len(v) > 102400:  # 100KB max
            raise ValueError('Content value cannot exceed 100KB')
        return v

@router.get("/{key}")
async def get_content(
    key: str,
    service: ContentService = Depends(get_content_service)
):
    """
    Public endpoint - anyone can read content.
    Used by SSR to load homepage content.

    SECURITY: No rate limiting (read-only, cacheable)
    """
    value = await service.get_content(key)
    if not value:
        raise HTTPException(status_code=404, detail="Content not found")
    return {"key": key, "value": value}

@router.put("/{key}")
@limiter.limit("10/minute")  # Rate limiting: 10 requests per minute per IP
async def update_content(
    key: str,
    request: UpdateContentRequest,
    current_user: dict = Depends(get_current_user),  # Clerk JWT validation
    service: ContentService = Depends(get_content_service)
):
    """
    Protected endpoint - only admin/agent can update content.

    Flow:
    1. Rate limiting (10 req/min per IP)
    2. Clerk middleware validates JWT SIGNATURE (not just decode)
    3. get_current_user extracts user_id and role from VALIDATED token
    4. Check if role is admin or agent
    5. Validate value length (< 100KB)
    6. If authorized, update content

    SECURITY:
    - JWT signature validation via Clerk SDK (not just decode)
    - Role check on validated claims
    - Rate limiting to prevent spam
    - Input validation (length)
    """
    # CRITICAL: Verify current_user dict came from JWT signature validation
    # (This assumes get_current_user dependency validates signature via Clerk SDK)
    if not current_user or "id" not in current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

    # Authorization check
    user_role = current_user.get("role")
    if user_role not in ["admin", "agent"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or agent roles can update content"
        )

    # Update content
    success = await service.update_content(
        key=key,
        value=request.value,
        user_id=current_user["id"]
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content key not found"
        )

    return {
        "success": True,
        "message": "Content updated",
        "key": key,
        "value": request.value,
        "updated_at": datetime.utcnow().isoformat()
    }
```

**Integration Points:**
- Frontend calls `GET /api/v1/content/homepage.title` → You return value from cache/DB
- Frontend calls `PUT /api/v1/content/homepage.title` → You validate role, update DB, invalidate cache
- DevOps provides the database table and seed data you query

**Performance Requirements:**
- `GET` endpoint: < 50ms response time (cache hit), < 200ms (cache miss)
- `PUT` endpoint: < 300ms response time
- Redis cache hit ratio: > 80% (measure after deployment)

**Timeline:** 2 days (models, services, routes, tests, documentation)

---

### Frontend Agent: UI & User Experience

**Your Role:** Build the user interface that makes content editable and beautiful.

**What You're Building:**
- Homepage: `routes/+page.svelte` with title, description, auth buttons
- EditableText component: Wraps text, detects right-click, shows context menu
- EditContentDialog: Modal popup with form (Cancel/Save)
- shadcn-svelte components: Button, Dialog, Textarea
- Integration with Backend API

**Why Backend API Must Exist First:**
- You cannot load homepage content without `GET /api/v1/content/{key}`
- You cannot test Save button without `PUT /api/v1/content/{key}`
- If Backend returns 500 errors, your UI looks broken

**Why DevOps Seed Data Matters:**
- Your SSR calls API during server render
- If database is empty, homepage shows "Content not found"
- Seed data ensures predictable content for development

**Deliverables:**
```typescript
// routes/+page.ts (SSR Load Function - CORRECT PATTERN)
export async function load({ fetch }) {
  const [titleRes, descRes] = await Promise.all([
    fetch('/api/v1/content/homepage.title'),
    fetch('/api/v1/content/homepage.description')
  ]);

  return {
    title: (await titleRes.json()).value,
    description: (await descRes.json()).value
  };
}
```

```svelte
<!-- routes/+page.svelte (Homepage) -->
<script lang="ts">
  import Button from '$lib/components/ui/button/Button.svelte';
  import EditableText from '$lib/components/EditableText.svelte';

  // Get data from load function (defined in +page.ts)
  let { data } = $props();

  // Reactive state for optimistic updates
  let title = $state(data.title);
  let description = $state(data.description);
</script>

<div class="container mx-auto px-4 py-16">
  <!-- Editable title -->
  <EditableText contentKey="homepage.title" bind:value={title}>
    <h1 class="text-4xl font-bold text-gray-900 mb-4">
      {title}
    </h1>
  </EditableText>

  <!-- Editable description -->
  <EditableText contentKey="homepage.description" bind:value={description}>
    <p class="text-lg text-gray-600 mb-8">
      {description}
    </p>
  </EditableText>

  <!-- Auth buttons (shadcn-svelte) -->
  <div class="flex gap-4">
    <Button href="/login" variant="default">Sign In</Button>
    <Button href="/signup" variant="outline">Sign Up</Button>
  </div>
</div>

<!-- lib/components/EditableText.svelte -->
<script lang="ts">
  import { getContext } from 'svelte';
  import EditContentDialog from './EditContentDialog.svelte';

  let { contentKey, value, children } = $props();

  // Get user role from auth context
  const authContext = getContext('auth');
  const userRole = authContext?.user?.role;

  let showContextMenu = $state(false);
  let showEditDialog = $state(false);
  let menuPosition = $state({ x: 0, y: 0 });

  function handleRightClick(e: MouseEvent) {
    // Only show context menu if user is admin or agent
    if (userRole !== 'admin' && userRole !== 'agent') {
      return;
    }

    e.preventDefault();
    menuPosition = { x: e.clientX, y: e.clientY };
    showContextMenu = true;
  }

  function handleEdit() {
    showContextMenu = false;
    showEditDialog = true;
  }

  function handleSave(newValue: string) {
    value = newValue;  // Optimistic update
    showEditDialog = false;
  }
</script>

<div on:contextmenu={handleRightClick} role="article" aria-label="Editable content">
  {@render children()}
</div>

{#if showContextMenu}
  <div
    role="menu"
    aria-label="Content editing options"
    class="context-menu"
    style="left: {menuPosition.x}px; top: {menuPosition.y}px"
    tabindex="-1"
  >
    <button role="menuitem" on:click={handleEdit}>Edit Content</button>
  </div>
{/if}

{#if showEditDialog}
  <EditContentDialog
    {contentKey}
    currentValue={value}
    onSave={handleSave}
    onCancel={() => showEditDialog = false}
  />
{/if}

<!-- lib/components/EditContentDialog.svelte -->
<script lang="ts">
  import Dialog from '$lib/components/ui/dialog/Dialog.svelte';
  import DialogContent from '$lib/components/ui/dialog/DialogContent.svelte';
  import Textarea from '$lib/components/ui/textarea/Textarea.svelte';
  import Button from '$lib/components/ui/button/Button.svelte';

  let { contentKey, currentValue, onSave, onCancel } = $props();

  let editedValue = $state(currentValue);
  let isSaving = $state(false);
  let error = $state('');

  async function handleSave() {
    isSaving = true;
    error = '';

    try {
      const response = await fetch(`/api/v1/content/${contentKey}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getClerkToken()}`  // Clerk JWT
        },
        body: JSON.stringify({ value: editedValue })
      });

      if (!response.ok) {
        throw new Error('Failed to update content');
      }

      onSave(editedValue);  // Notify parent component
    } catch (err) {
      error = 'Failed to save content. Please try again.';
    } finally {
      isSaving = false;
    }
  }
</script>

<Dialog open={true} onOpenChange={(open) => !open && onCancel()}>
  <DialogContent>
    <h2>Edit Content</h2>
    <p class="text-sm text-gray-500">Key: {contentKey}</p>

    <Textarea
      bind:value={editedValue}
      rows={5}
      placeholder="Enter content..."
    />

    {#if error}
      <p class="text-red-500 text-sm">{error}</p>
    {/if}

    <div class="flex gap-2">
      <Button onclick={handleSave} disabled={isSaving}>
        {isSaving ? 'Saving...' : 'Save'}
      </Button>
      <Button variant="outline" onclick={onCancel} disabled={isSaving}>
        Cancel
      </Button>
    </div>
  </DialogContent>
</Dialog>
```

**Integration Points:**
- You call Backend's `GET /api/v1/content/{key}` during SSR load
- You call Backend's `PUT /api/v1/content/{key}` when admin saves edits
- If Backend returns 404, you show "Content not found" error
- If Backend returns 403, you show "Unauthorized" error

**UX Requirements:**
- Homepage loads instantly (SSR, no loading spinner)
- Right-click menu only shows for admin/agent users
- Edit dialog has clear Cancel/Save buttons
- Optimistic UI update (show new value immediately, don't wait for API)
- Error handling for network failures

**Timeline:** 2-3 days (components, integration, styling, tests)

---

### E2E Testing Agent: Validation & Acceptance

**Your Role:** Validate the COMPLETE user journey works end-to-end.

**What You're Testing:**
- Visitor can see homepage with title and description
- Admin can right-click and edit content
- Changes are saved to database and reflected immediately
- Unauthorized users cannot access edit functionality

**Why You Need All Agents' Work First:**
- DevOps must deploy database with seed data
- Backend API must be running and returning correct responses
- Frontend UI must be deployed and accessible

**Deliverables:**
```typescript
// tests/e2e/homepage-editable-content.spec.ts
import { test, expect } from '@playwright/test';

test.describe('US-020: Homepage Editable Content', () => {
  test('Visitor sees homepage with title and description', async ({ page }) => {
    await page.goto('http://localhost:5183/');

    // Homepage loads successfully
    await expect(page).toHaveTitle(/Bestays/i);

    // Title is visible
    await expect(page.locator('h1')).toContainText('Welcome to Bestays');

    // Description is visible
    await expect(page.locator('p').first()).toContainText('Your trusted platform');

    // Sign In and Sign Up buttons are visible
    await expect(page.locator('a:has-text("Sign In")')).toBeVisible();
    await expect(page.locator('a:has-text("Sign Up")')).toBeVisible();
  });

  test('Admin can edit homepage title via right-click', async ({ page }) => {
    // Login as admin first
    await loginAsAdmin(page);

    // Go to homepage
    await page.goto('http://localhost:5183/');

    // Right-click on title
    const titleElement = page.locator('h1');
    await titleElement.click({ button: 'right' });

    // Context menu appears
    await expect(page.locator('text=Edit Content')).toBeVisible();

    // Click "Edit Content"
    await page.locator('text=Edit Content').click();

    // Edit dialog opens
    await expect(page.locator('dialog')).toBeVisible();
    await expect(page.locator('h2:has-text("Edit Content")')).toBeVisible();

    // Textarea has current value
    const textarea = page.locator('textarea');
    await expect(textarea).toHaveValue('Welcome to Bestays');

    // Change value
    await textarea.fill('Welcome to the Best Stays Platform');

    // Click Save
    await page.locator('button:has-text("Save")').click();

    // Dialog closes
    await expect(page.locator('dialog')).not.toBeVisible();

    // New value is visible immediately (optimistic update)
    await expect(titleElement).toContainText('Welcome to the Best Stays Platform');

    // Reload page to verify database was updated
    await page.reload();
    await expect(titleElement).toContainText('Welcome to the Best Stays Platform');
  });

  test('Regular user cannot see edit functionality', async ({ page }) => {
    // Login as regular user (not admin)
    await loginAsUser(page);

    // Go to homepage
    await page.goto('http://localhost:5183/');

    // Right-click on title
    const titleElement = page.locator('h1');
    await titleElement.click({ button: 'right' });

    // Context menu should NOT appear
    await expect(page.locator('text=Edit Content')).not.toBeVisible();
  });

  test('Database persists content changes', async ({ page }) => {
    // This test validates Backend + DevOps integration

    // Login as admin
    await loginAsAdmin(page);
    await page.goto('http://localhost:5183/');

    // Edit content
    await editContent(page, 'h1', 'New Title Value');

    // Directly query API to verify database
    const response = await page.request.get('/api/v1/content/homepage.title');
    const data = await response.json();
    expect(data.value).toBe('New Title Value');
  });
});
```

**Integration Validation:**
- Test passes = All agents' work is correctly integrated
- Test fails = Integration issue between DevOps/Backend/Frontend

**Timeline:** 1 day (test writing, execution, bug fixes)

---

## ✅ Acceptance Criteria (Cross-Agent Validation)

### AC-1: Content Display (Frontend + Backend + DevOps)
**Given** the database has seed data
**When** a visitor navigates to https://bestays.app/
**Then** they see:
- Title: "Welcome to Bestays"
- Description: "Your trusted platform for discovering..."
- Sign In button
- Sign Up button

**Validation:**
- ✅ DevOps: Seed data inserted correctly
- ✅ Backend: API returns correct values
- ✅ Frontend: SSR renders content without loading state
- ✅ E2E: Test confirms all elements visible

---

### AC-2: Admin Edit Functionality (Frontend + Backend)
**Given** I am logged in as an admin
**When** I right-click on the homepage title
**Then** I see a context menu with "Edit Content" option

**And when** I click "Edit Content"
**Then** a modal dialog opens with:
- Current title value pre-filled in textarea
- Cancel button
- Save button

**Validation:**
- ✅ Frontend: Context menu shows only for admin/agent role
- ✅ Frontend: Dialog renders correctly
- ✅ E2E: Test confirms workflow

---

### AC-3: Content Update Persistence (Backend + DevOps)
**Given** I am editing homepage title in the dialog
**When** I change the value and click Save
**Then**:
- The API call succeeds (200 OK)
- The database is updated with new value
- The Redis cache is invalidated
- The UI updates immediately (optimistic)

**And when** I reload the page
**Then** the new value persists

**Validation:**
- ✅ Backend: PUT endpoint updates database and cache
- ✅ DevOps: Database constraints allow updates
- ✅ Frontend: Optimistic UI update works
- ✅ E2E: Test confirms persistence after reload

---

### AC-4: Authorization (Backend)
**Given** I am logged in as a regular user (not admin/agent)
**When** I try to call PUT /api/v1/content/homepage.title
**Then** I receive a 403 Forbidden response

**And** the database is NOT updated

**Validation:**
- ✅ Backend: Role check works correctly
- ✅ E2E: Test confirms unauthorized users cannot edit

---

### AC-5: Performance (Backend + DevOps)
**Given** the content is cached in Redis
**When** the API is called for the same key
**Then** the response time is < 50ms (cache hit)

**And when** the cache is empty
**Then** the response time is < 200ms (database query)

**Validation:**
- ✅ Backend: Cache-first pattern implemented
- ✅ DevOps: Redis configured correctly
- ✅ Load testing: Measure actual response times

---

## 📦 Deliverables Checklist

### DevOps Agent
- [ ] Alembic migration: `content_dictionary` table
- [ ] Seed data: `homepage.title` and `homepage.description`
- [ ] Redis verification: TTL and eviction policy
- [ ] Documentation: Database schema and seed data

### Backend Agent
- [ ] SQLAlchemy model: `ContentDictionary`
- [ ] Service: `ContentService` with cache-first pattern
- [ ] Routes: `GET /api/v1/content/{key}`, `PUT /api/v1/content/{key}`
- [ ] Authorization: Clerk JWT validation, role check
- [ ] Tests: Unit tests for service, integration tests for API
- [ ] Documentation: API spec (OpenAPI)

### Frontend Agent
- [ ] shadcn-svelte setup: Install Button, Dialog, Textarea components
- [ ] Homepage: `routes/+page.svelte` with SSR load
- [ ] EditableText component: Right-click detection, context menu
- [ ] EditContentDialog component: Modal with form and API integration
- [ ] Tests: Component tests for EditableText and EditContentDialog
- [ ] Documentation: Component usage guide

### E2E Testing Agent
- [ ] Test: Visitor sees homepage content
- [ ] Test: Admin can edit content via right-click
- [ ] Test: Regular user cannot edit content
- [ ] Test: Content persists after reload
- [ ] Test: Authorization enforced
- [ ] Documentation: Test results and coverage report

---

## 🚀 Implementation Timeline

| Day | Agent | Task | Dependencies |
|-----|-------|------|--------------|
| **Day 1** | DevOps | Database migration + seed data | None |
| **Day 2** | Backend | Models + ContentService | Day 1 complete |
| **Day 3** | Backend | API routes + authorization | Day 2 complete |
| **Day 4** | Frontend | shadcn-svelte + homepage SSR | Day 3 complete |
| **Day 5** | Frontend | EditableText + EditContentDialog | Day 4 complete |
| **Day 6** | E2E Testing | Write and run tests | Day 5 complete |
| **Day 7** | All Agents | Bug fixes, polish, documentation | Day 6 complete |

**Critical Path:** DevOps → Backend → Frontend → E2E Testing

**Parallel Work Opportunities:**
- Day 3: Backend can work on tests while Frontend installs shadcn-svelte
- Day 5: E2E agent can start writing test skeletons

---

## 🎓 Lessons for Future Stories

**What This Story Establishes:**
1. **Content system pattern** - All future content (properties, reviews) follows this model
2. **shadcn-svelte foundation** - All future UI uses these components
3. **Admin editing pattern** - Right-click → Edit → Save workflow reused everywhere
4. **Cache-first pattern** - All future APIs can use this performance strategy

**Why This is Foundation, Not Just a Feature:**
- US-021 (Thai localization) will ADD to this table (locale column)
- Future properties feature will use same content editing pattern
- All pages will use shadcn-svelte components we install here

---

## 📊 Success Metrics

**Technical Metrics:**
- [ ] Cache hit ratio > 80% (measured after 1 week)
- [ ] API response time < 50ms (cache hit), < 200ms (cache miss)
- [ ] Zero content update failures due to authorization bugs

**Business Metrics:**
- [ ] Time to update homepage content: 2 hours → 30 seconds
- [ ] Number of code deployments for content changes: 10/week → 0/week
- [ ] Marketing team satisfaction: Survey after 2 weeks

**User Experience Metrics:**
- [ ] Homepage loads in < 1 second (SSR, no loading spinner)
- [ ] Edit dialog opens in < 100ms
- [ ] Content save completes in < 500ms

---

## 🔐 Security & Authorization Checklist

**Backend Responsibilities:**

- [ ] **JWT Signature Validation:** `get_current_user` dependency MUST validate JWT signature via Clerk SDK, not just decode
- [ ] **Role-Based Access Control:** Only `admin` and `agent` roles can call PUT `/api/v1/content/{key}`
- [ ] **Input Validation:** Pydantic validator enforces value length < 100KB
- [ ] **Rate Limiting:** slowapi limits PUT endpoint to 10 requests/minute per IP
- [ ] **SQL Injection Prevention:** SQLAlchemy parameterized queries (automatic)
- [ ] **XSS Prevention:** Frontend MUST escape content when rendering (Svelte auto-escapes)
- [ ] **CSRF Protection:** SvelteKit provides CSRF tokens automatically
- [ ] **Error Message Sanitization:** Don't leak internal details (e.g., stack traces) in production

**Frontend Responsibilities:**

- [ ] **Content Escaping:** Svelte's `{value}` syntax auto-escapes HTML (verified)
- [ ] **Authorization UI:** Context menu only shows for admin/agent users
- [ ] **Token Management:** Clerk JWT token retrieved securely and sent in Authorization header
- [ ] **Error Handling:** Generic error messages to user, specific errors logged to console

---

## 📊 Monitoring & Observability

**Required Endpoints (Backend):**

```python
# Add to routers/admin.py or routers/health.py
@router.get("/api/v1/health/cache")
async def cache_health(redis_client = Depends(get_redis)):
    """
    Expose Redis cache metrics for monitoring.

    IMPORTANT: Use this endpoint to validate AC-5 performance requirements.
    """
    try:
        info = await redis_client.info('stats')
        hits = int(info.get("keyspace_hits", 0))
        misses = int(info.get("keyspace_misses", 0))
        total = hits + misses
        hit_ratio = hits / total if total > 0 else 0

        return {
            "status": "healthy",
            "keyspace_hits": hits,
            "keyspace_misses": misses,
            "cache_hit_ratio": round(hit_ratio, 3),
            "memory_used_mb": round(int(info.get("used_memory", 0)) / 1024 / 1024, 2)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

**Logging Strategy (Backend):**

```python
# Enable SQLAlchemy query logging in development
import logging

# Development environment
if settings.ENVIRONMENT == "development":
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)  # Log all SQL queries

# Production environment
if settings.ENVIRONMENT == "production":
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)  # Only log slow queries
    # Configure slow query logging in PostgreSQL: log_min_duration_statement = 100
```

**Metrics to Track:**

| Metric | Target | How to Measure | Alert Threshold |
|--------|--------|----------------|-----------------|
| Cache hit ratio | > 80% | `/api/v1/health/cache` | < 50% |
| GET response time (cache hit) | < 50ms | Application metrics | > 100ms |
| GET response time (cache miss) | < 200ms | Application metrics | > 500ms |
| PUT response time | < 300ms | Application metrics | > 1000ms |
| Redis memory usage | < 200MB | `/api/v1/health/cache` | > 200MB |
| Failed cache operations | 0/hour | Application logs | > 10/hour |

**Observability Checklist:**

- [ ] Redis cache health endpoint deployed
- [ ] SQLAlchemy query logging enabled (development)
- [ ] PostgreSQL slow query log configured (production, log_min_duration_statement = 100ms)
- [ ] Application logs include: content updates (key, user_id, value_length)
- [ ] Application logs include: Redis errors (cache misses, failures)
- [ ] Dashboard created (Grafana/Prometheus) to visualize cache hit ratio

---

## 🚀 Deployment & Operations

**Deployment Procedure:**

```bash
# Step 1: Backup database (CRITICAL - before any migration)
docker exec -it bestays-postgres-dev pg_dump -U postgres bestays > backup_before_us020_$(date +%Y%m%d_%H%M%S).sql

# Step 2: Run Alembic migration
make migrate
# Expected output: Running upgrade ... -> XXX, add content_dictionary

# Step 3: Verify migration success
make shell-db
# Then run:
\d content_dictionary
SELECT * FROM content_dictionary;
# Expected: 2 rows (homepage.title, homepage.description)

# Step 4: Restart backend (load new models)
docker-compose restart server

# Step 5: Smoke test (verify API works)
curl http://localhost:8011/api/v1/content/homepage.title
# Expected: {"key":"homepage.title","value":"Welcome to Bestays"}

curl http://localhost:8011/api/v1/content/homepage.description
# Expected: {"key":"homepage.description","value":"Your trusted platform..."}

# Step 6: Verify Redis caching works
# First request (cache miss):
time curl http://localhost:8011/api/v1/content/homepage.title
# Note response time (should be < 200ms)

# Second request (cache hit):
time curl http://localhost:8011/api/v1/content/homepage.title
# Note response time (should be < 50ms)

# Step 7: Verify cache health endpoint
curl http://localhost:8011/api/v1/health/cache
# Expected: {"status":"healthy","cache_hit_ratio":...}

# Step 8: Frontend deployment (after backend confirmed working)
cd apps/frontend && npm run build
# Then deploy build artifacts
```

**Rollback Procedure:**

```bash
# Scenario 1: Backend deployment fails AFTER migration
# DO NOT rollback migration (data loss risk)
# FIX: Debug and redeploy Backend
# - Check logs: docker-compose logs server
# - Fix code issue
# - Redeploy: docker-compose restart server

# Scenario 2: Migration fails during execution
# Alembic auto-rollbacks transaction on failure
# FIX: Debug migration script, re-run migration

# Scenario 3: Need to fully rollback US-020 (nuclear option)
# 1. Revert Backend code
# 2. Revert Frontend code
# 3. Rollback database migration:
alembic downgrade -1
# WARNING: This drops content_dictionary table (data loss)
# 4. Restore from backup if needed:
psql -U postgres bestays < backup_before_us020_YYYYMMDD_HHMMSS.sql
```

**Smoke Test Checklist:**

- [ ] GET `/api/v1/content/homepage.title` returns 200 + correct value
- [ ] GET `/api/v1/content/homepage.description` returns 200 + correct value
- [ ] GET `/api/v1/health/cache` returns 200 + healthy status
- [ ] Homepage loads in browser (http://localhost:5183/) with title and description
- [ ] Admin login works
- [ ] Admin can right-click and see context menu
- [ ] Admin can edit and save content
- [ ] Content persists after page reload
- [ ] Regular user cannot see edit functionality

---

## 🧪 Testing Considerations

**Test Data Management:**

```bash
# Reset database to seed state between E2E tests
# Option 1: Transaction rollback (preferred, faster)
# - Wrap each test in BEGIN/ROLLBACK transaction
# - Requires test-specific database configuration

# Option 2: Manual cleanup (simple, slower)
# - After each test, restore seed data:
DELETE FROM content_dictionary WHERE key NOT IN ('homepage.title', 'homepage.description');
UPDATE content_dictionary
SET value = 'Welcome to Bestays',
    updated_at = NOW(),
    updated_by = NULL
WHERE key = 'homepage.title';

UPDATE content_dictionary
SET value = 'Your trusted platform for discovering and booking unique stays. Find your perfect accommodation today.',
    updated_at = NOW(),
    updated_by = NULL
WHERE key = 'homepage.description';
```

**Locator Strategy (Frontend + E2E):**

```typescript
// RULE: Use data-testid for all testable elements
// Priority: data-testid > role > text content

// Add to EditableText.svelte:
<div data-testid="editable-content-{contentKey}" on:contextmenu={handleRightClick}>
  {@render children()}
</div>

// Add to EditContentDialog.svelte:
<Dialog data-testid="edit-content-dialog">
  <Textarea data-testid="content-value-input" />
  <Button data-testid="save-button">Save</Button>
  <Button data-testid="cancel-button">Cancel</Button>
</Dialog>

// E2E test usage:
await page.locator('[data-testid="editable-content-homepage.title"]').click({ button: 'right' });
await page.locator('[data-testid="edit-content-dialog"]').waitFor();
await page.locator('[data-testid="content-value-input"]').fill('New value');
await page.locator('[data-testid="save-button"]').click();
```

**Explicit Wait Strategies (E2E):**

```typescript
// Wait for cache invalidation before verifying persistence
await page.locator('[data-testid="save-button"]').click();

// Wait for dialog to close (optimistic update complete)
await page.locator('[data-testid="edit-content-dialog"]').waitFor({ state: 'hidden' });

// Wait for network idle (cache invalidation complete)
await page.waitForLoadState('networkidle');

// THEN reload and verify
await page.reload();
await expect(page.locator('h1')).toContainText('New value');
```

**Edge Cases to Test:**

- [ ] Empty content submission (should validation error)
- [ ] Very long content (>100KB should validation error)
- [ ] Special characters: quotes, HTML tags, Unicode (Thai characters)
- [ ] Network timeout during save (retry? error message?)
- [ ] Concurrent edits (two admins editing same content - last write wins)
- [ ] Edit dialog cancel (changes discarded)
- [ ] SSR failure (API down during page load - error page or fallback?)
- [ ] Redis down (graceful degradation to database)
- [ ] Database down (500 error, proper error message)

---

## 🔒 Definition of Done

- [x] All agents understand the complete system (read this document)
- [ ] DevOps: Database migration deployed, seed data inserted
- [ ] Backend: API endpoints working, tests passing
- [ ] Frontend: Homepage rendering, edit functionality working
- [ ] E2E: All acceptance criteria tests passing
- [ ] Documentation: All agents document their work
- [ ] Code review: At least one other agent reviews each implementation
- [ ] User demo: Demo to user, get approval to merge

---

**Status:** DRAFT - Awaiting User Approval
**Next Step:** User reviews and approves this story, then create US-021 (Thai localization)
**Dependencies:** US-019 (Login) must be complete first (failing tests fixed)

---

**Questions for User:**
1. Is this level of coordination and detail what you meant by "all agents on the same page"?
2. Any concerns about the 7-day timeline?
3. Should we add any other content keys besides `homepage.title` and `homepage.description`?

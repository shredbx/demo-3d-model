# CLAUDE.md

Project-specific guidance for **ShredBX Model Generator** - an AI-powered image-to-3D model conversion tool for dirt bikes.

---

## 🎯 PROJECT OVERVIEW

**ShredBX Model Generator** allows users to upload photos of dirt bikes (like the YZ 250X) and convert them into interactive 3D models that can be rotated, zoomed, and downloaded.

### Technology Stack

- **Backend:** FastAPI (Python 3.10+), PostgreSQL, SQLAlchemy, Alembic
- **Frontend:** SvelteKit 2, Svelte 5 (runes), Tailwind CSS, Three.js
- **AI Service:** Meshy.ai API (image-to-3D conversion)
- **Storage:** Cloudflare R2 (or AWS S3)
- **Dev:** Docker Compose

### Current Status

- ✅ Project structure established
- ✅ Knowledge base from Bestays project preserved
- 📋 **US-001:** Image to 3D Model Viewer (PLANNING)
- 🎯 **Goal:** MVP with homepage upload → 3D viewer

---

## 🚀 QUICK START

### For New Sessions

1. **Load Memory MCP:**
   ```
   mcp__memory__open_nodes(names: [
     "ShredBX Project Context",
     "Bestays FastAPI Backend Pattern",
     "SvelteKit 5 Runes Best Practices",
     "Clerk Authentication Integration"
   ])
   ```

2. **Check Current Story:**
   - Active: US-001 (Image to 3D Model Viewer)
   - Location: `.sdlc-workflow/stories/image-to-3d/US-001-image-to-3d-viewer.md`

3. **Reference Knowledge:**
   - Old Bestays patterns: `.sdlc-workflow/reference-knowledge-from-bestays-project/`
   - Use for implementation examples, NOT as active requirements

---

## 📚 KNOWLEDGE BASE FROM BESTAYS PROJECT

**Location:** `.sdlc-workflow/reference-knowledge-from-bestays-project/`

This project is built on patterns from the **Bestays** real estate rental platform. The old code/stories have been archived for reference.

### ✅ Use This Knowledge For:

- **FastAPI backend structure** (routers, dependencies, schemas)
- **Clerk authentication** (frontend + backend integration)
- **SvelteKit 5** component patterns (runes, routing)
- **Docker development** environment setup
- **PostgreSQL + Alembic** migrations
- **E2E testing** with Playwright

### ❌ Don't:

- Follow old user stories (US-001, US-019, etc.) - they're for a different product
- Copy property/booking/real estate code without adapting to 3D models
- Reference old task numbers in new work

### Quick Reference Index

| Need to Build... | Reference... |
|------------------|--------------|
| Image upload API | `reference-knowledge.../code-examples/backend/` |
| FastAPI endpoint | `reference-knowledge.../implementation-patterns/fastapi-backend-structure.md` |
| Svelte component | `reference-knowledge.../code-examples/frontend/` |
| Docker setup | `reference-knowledge.../devops/docker-compose-setup.md` |
| Database models | `reference-knowledge.../code-examples/backend/database-models.py` |

---

## 🎯 CRITICAL CONTEXT: SHREDBX PROJECT

**THIS IS A NEW PROJECT - NOT BESTAYS**

We're building ShredBX Model Generator, which converts dirt bike photos to 3D models. Although we use patterns from Bestays (FastAPI, SvelteKit, etc.), the features are completely different.

### Current User Story

**US-001: Image to 3D Model Viewer**

**High-Level Requirement:**
> Homepage contains a drag-drop area for images. User drops a dirt bike photo, backend processes it via Meshy.ai API, and user sees an interactive 3D model in Three.js that they can rotate and zoom.

**Location:** `.sdlc-workflow/stories/image-to-3d/US-001-image-to-3d-viewer.md`

**Status:** PLANNING

**Task Breakdown:**
- TASK-001: Backend (FastAPI + Meshy.ai integration)
- TASK-002: Frontend upload UI
- TASK-003: Three.js viewer
- TASK-004: Status polling & integration
- TASK-005: Polish & optimization
- TASK-006: Testing

---

## 🔧 DEVELOPMENT WORKFLOW

### SDLC Phases

1. **RESEARCH:** Understand requirements, explore patterns
2. **PLANNING:** Design architecture, write specs
3. **IMPLEMENTATION:** Write code via subagents
4. **TESTING:** E2E, unit, integration tests
5. **VALIDATION:** Code review, acceptance criteria check

### Your Role: Coordinator ONLY

**YOU ARE COORDINATOR. NEVER IMPLEMENTER.**

✅ **You CAN:**
- Read files (research, context)
- Plan and coordinate work
- Launch subagents for implementation
- Update workflow docs
- Git operations
- Track progress (TodoWrite)

❌ **You CANNOT:**
- Edit/Write `apps/server/**` (backend code)
- Edit/Write `apps/frontend/src/**` (frontend code)
- Edit/Write `tests/**` (test files)
- Create implementation files yourself

**Subagent Mapping:**

| Path | Subagent |
|------|----------|
| `apps/server/**/*.py` | dev-backend-fastapi |
| `apps/frontend/src/**` | dev-frontend-svelte |
| `tests/e2e/**/*.spec.ts` | playwright-e2e-tester |

---

## 📋 USING THE KNOWLEDGE BASE

### Memory MCP Entities (Instant Recall)

Load these at session start:

```typescript
[
  "ShredBX Project Context",
  "Bestays FastAPI Backend Pattern",
  "Clerk Authentication Integration",
  "SvelteKit 5 Runes Best Practices",
  "Docker Development Environment Pattern",
  "PostgreSQL SQLAlchemy Alembic Pattern",
  "RBAC Implementation Pattern",
  "E2E Testing Playwright Pattern"
]
```

### Example: Building an API Endpoint

**Need:** Create Meshy.ai integration endpoint

**Reference:**
1. Load Memory: `"Bestays FastAPI Backend Pattern"`
2. Check: `reference-knowledge.../code-examples/backend/api-endpoints.py`
3. Adapt for ShredBX: Change from properties to 3D models
4. Launch subagent: `dev-backend-fastapi`

---

## 🛠️ COMMON COMMANDS

```bash
# Start development (from project root)
make dev           # Start all services
make logs          # View logs
make down          # Stop services

# Database
make migrate       # Run Alembic migrations
make shell-db      # PostgreSQL shell

# Backend shell
make shell-server

# Frontend shell
make shell-frontend
```

---

## 🌐 SERVICES

| Service | URL | Port |
|---------|-----|------|
| Frontend | http://localhost:5183 | 5183 |
| Backend API | http://localhost:8011 | 8011 |
| PostgreSQL | localhost:5433 | 5433 |
| Swagger Docs | http://localhost:8011/docs | 8011 |

---

## 🔐 ENVIRONMENT VARIABLES

Copy `.env.example` → `.env` (NEVER commit `.env`)

**Required:**
```bash
# Meshy.ai (for 3D generation)
MESHY_API_KEY=msy_xxxxx

# Storage (Cloudflare R2 or AWS S3)
R2_ACCOUNT_ID=xxxxx
R2_ACCESS_KEY_ID=xxxxx
R2_SECRET_ACCESS_KEY=xxxxx
R2_BUCKET_NAME=shredbx-uploads

# Database
DATABASE_URL=postgresql://user:pass@postgres:5432/shredbx

# Optional: Authentication (for later)
CLERK_SECRET_KEY=sk_test_xxxxx
```

---

## 📖 DOCUMENTATION LOCATIONS

### Active (ShredBX)

- **User Stories:** `.sdlc-workflow/stories/image-to-3d/`
- **Tasks:** `.claude/tasks/` (currently empty, will populate during implementation)
- **Reports:** `.claude/reports/`
- **Technical Specs:**
  - System Design: `.claude/reports/20251111-shredbx-image-to-3d-system-design.md`
  - Architecture: `.claude/reports/20251111-shredbx-openrouter-meshy-architecture.md`

### Reference (Bestays Knowledge)

- **Implementation Patterns:** `.sdlc-workflow/reference-knowledge-from-bestays-project/implementation-patterns/`
- **Code Examples:** `.sdlc-workflow/reference-knowledge-from-bestays-project/code-examples/`
- **Architecture:** `.sdlc-workflow/reference-knowledge-from-bestays-project/architecture/`
- **Old User Stories:** `.sdlc-workflow/reference-knowledge-from-bestays-project/old-user-stories/` (reference only)
- **Old Tasks:** `.sdlc-workflow/reference-knowledge-from-bestays-project/old-tasks/` (reference only)

---

## 🎨 SHREDBX-SPECIFIC PATTERNS

### 1. Image to 3D Flow

```
User uploads image (YZ 250X photo)
    ↓
FastAPI receives file
    ↓
Upload to R2 storage
    ↓
Call Meshy.ai API (image_url)
    ↓
Return task_id to frontend
    ↓
Frontend polls /status/{task_id}
    ↓
Meshy generates 3D model (5-15 min)
    ↓
Frontend gets model_url (GLB)
    ↓
Three.js loads and displays GLB
    ↓
User can rotate, zoom, download
```

### 2. Three.js Integration Pattern

**CRITICAL:** Mount Three.js in `onMount`, NOT `$effect`

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import * as THREE from 'three';
  import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

  let canvas: HTMLCanvasElement;
  let scene: THREE.Scene;
  let renderer: THREE.WebGLRenderer;

  onMount(() => {
    // Initialize Three.js scene
    scene = new THREE.Scene();
    renderer = new THREE.WebGLRenderer({ canvas });
    // ... setup

    // Animation loop
    function animate() {
      requestAnimationFrame(animate);
      renderer.render(scene, camera);
    }
    animate();

    // Cleanup
    return () => {
      renderer.dispose();
    };
  });
</script>

<canvas bind:this={canvas}></canvas>
```

**Why onMount?** External libraries with imperative APIs should be initialized once, not reactively.

### 3. Meshy.ai API Pattern

```python
# Backend: apps/server/app/services/model_generator.py

class MeshyImageTo3DService:
    async def create_task(self, image_url: str) -> dict:
        """Create 3D generation task"""
        payload = {"image_url": image_url, "enable_pbr": True}
        response = await httpx.post(
            "https://api.meshy.ai/v2/image-to-3d",
            json=payload,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()  # {"id": "task_abc123"}

    async def get_status(self, task_id: str) -> dict:
        """Poll task status"""
        response = await httpx.get(
            f"https://api.meshy.ai/v2/image-to-3d/{task_id}",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()  # {"status": "SUCCEEDED", "model_url": "..."}
```

---

## 🧪 TESTING STRATEGY

### E2E Testing (Playwright)

**Location:** `apps/frontend/tests/e2e/`

**Pattern:** (Reference from Bestays)
```typescript
import { test, expect } from '@playwright/test';

test.describe('3D Model Generation', () => {
  test('should upload image and display 3D model', async ({ page }) => {
    await page.goto('/');

    // Upload image
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('./test-assets/yz250x.jpg');

    // Wait for generation (mock or actual)
    await expect(page.locator('.three-viewer')).toBeVisible({ timeout: 60000 });

    // Verify 3D canvas rendered
    const canvas = page.locator('canvas');
    await expect(canvas).toBeVisible();
  });
});
```

### Backend Testing

**Pattern:** (Reference from Bestays)
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_generate_3d_model(client: AsyncClient):
    """Test 3D model generation endpoint"""
    with open("test_bike.jpg", "rb") as f:
        response = await client.post(
            "/api/v1/3d-models/generate",
            files={"file": f}
        )

    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "PENDING"
```

---

## 🚨 COMMON PITFALLS

### 1. Svelte 5 Mounting Issues

❌ **Don't:**
```svelte
$effect(() => {
  // Initialize Three.js here - CAUSES RACE CONDITIONS
});
```

✅ **Do:**
```svelte
onMount(() => {
  // Initialize Three.js here - RUNS ONCE
});
```

### 2. Confusing Old Project with New

❌ **Don't:**
- "Let's implement US-019 (Bestays auth login)"
- Copy property code without adapting

✅ **Do:**
- "Reference Bestays auth pattern for ShredBX auth (if needed)"
- Adapt property upload → image upload

### 3. Forgetting Sequential Thinking

❌ **Don't:**
- Jump straight to implementation without planning

✅ **Do:**
- Use `mcp__sequential-thinking__sequentialthinking` for complex tasks
- Think → Plan → Design → Execute

---

## 🎯 MILESTONES & ROADMAP

**Full Plan:** `.claude/reports/FINAL-milestone-plan-v2.md`
**Timeline:** 7 weeks total
**Status:** Expert-approved, ready for implementation

### Milestone -1: Market Discovery (1 week)

**Goal:** Validate demand before building

- Interview 20+ dirt bike owners
- Document use cases
- Validate pricing ($9.99-$29.99/month)
- Competitor research
- GO/NO-GO decision

**Acceptance:** 50%+ interest, 3+ use cases, pricing validated

---

### Milestone 0: Technical Validation (1 week)

**Goal:** Prove technology works

- Test 3 APIs (Meshy.ai vs TripoSR vs Luma)
- Choose best API (quality + cost + latency)
- Validate Three.js performance (60fps on iPhone 12)
- Cross-browser testing (Chrome, Firefox, Safari)
- Cost validation (< $0.60/model)
- GO/NO-GO decision

**Acceptance:** 80% acceptable models, 60fps, cost < $0.60

---

### Milestone 1: Public MVP (3 weeks)

**Goal:** Launch complete product

**Tech Stack:**
- Backend: Railway (FastAPI + Redis)
- Frontend: Vercel (SvelteKit)
- Database: Supabase (PostgreSQL + Auth)
- Storage: Cloudflare R2
- Email: SendGrid

**Features:**
- Authentication (user accounts)
- Image upload (drag-drop)
- Server-Sent Events (real-time status)
- Three.js viewer (rotate, zoom, download)
- Email notifications (mandatory)
- Mobile-first responsive design
- Model gallery (save past generations)
- CI/CD pipeline
- Accessibility (WCAG 2.1 AA)

**Acceptance:** 70% conversion, email >99% delivery, mobile works, public launch

---

### Milestone 2: Production Hardening (2 weeks)

**Goal:** Optimize and secure

- E2E tests (Playwright, 100% coverage)
- Backend tests (>80% coverage)
- Load testing (100 concurrent users)
- Performance optimization (P95 < 150ms)
- Security audit (OWASP top 10)
- Monitoring (Sentry, PostHog, uptime)
- Backup/restore procedures

**Acceptance:** 99.5% uptime, P95 < 150ms, zero critical bugs

---

### Monetization Model

**Pricing Tiers:**
- **Free:** 3 models/month (watermarked)
- **Hobby ($9.99/mo):** 15 models/month (no watermark, downloads)
- **Pro ($29.99/mo):** 50 models/month (API access, commercial license)

**Unit Economics:**
- Cost: $0.53/model (Meshy) or $0.13/model (TripoSR)
- Target margin: 70%
- Required revenue: $1.77/model (Meshy) or $0.43/model (TripoSR)

**Monthly Costs:**
- MVP: $50-75/month
- Production: $150-200/month (with scaling)

---

### Current Status

**Phase:** Ready to start Milestone -1 (Market Discovery)
**Next Action:** Begin customer interviews (20+ dirt bike owners)

**Key Decisions Made:**
- ✅ Market validation FIRST (de-risk demand)
- ✅ Tech validation SECOND (de-risk quality)
- ✅ Authentication added (prevent abuse)
- ✅ SSE instead of polling (efficiency)
- ✅ Mobile-first approach
- ✅ Production stack defined (Railway + Vercel + Supabase)

**Expert Reviews:**
- 🟢 DevOps: GREEN LIGHT
- 🟢 Backend: GREEN LIGHT
- 🟢 Frontend: GREEN LIGHT
- 🟢 CTO: GREEN LIGHT

---

## 📞 GETTING HELP

### "How do I build X?"

1. **Check Memory MCP** first
2. **Check reference knowledge** (Bestays patterns)
3. **Check technical specs** (reports/)
4. **Ask user** if still unclear

### "Can I reuse Bestays code?"

✅ **Yes, if:**
- It's a general pattern (FastAPI structure, auth flow)
- You adapt it for ShredBX context (3D models, not properties)

❌ **No, if:**
- It's product-specific (booking, properties, real estate features)

---

## 🎓 LEARNING RESOURCES

### Internal

- **Bestays Patterns:** `.sdlc-workflow/reference-knowledge-from-bestays-project/README.md`
- **System Design:** `.claude/reports/20251111-shredbx-openrouter-meshy-architecture.md`

### External

- **Meshy.ai Docs:** https://docs.meshy.ai/en/api/image-to-3d
- **Three.js Docs:** https://threejs.org/docs
- **SvelteKit 5:** https://svelte.dev/docs/kit
- **FastAPI:** https://fastapi.tiangolo.com

---

**Version:** 1.0 (ShredBX)
**Last Updated:** 2025-11-11
**Project:** ShredBX Model Generator

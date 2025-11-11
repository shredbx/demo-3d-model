# RAPID PROTOTYPE v0 - Proof of Concept

**Mode:** Feature Proofing (Speed > Clean Code)
**Goal:** Working image → 3D model demo in < 4 hours
**Timeline:** NOW
**Refactoring:** Later (documented below)

---

## 🎯 Absolute Minimum Viable Demo

**User Flow:**
1. Upload dirt bike image
2. Wait 5-15 min (show progress)
3. View 3D model in Three.js
4. Done.

**What We're Skipping (For Now):**
- ❌ Authentication (wide open)
- ❌ Database (ephemeral storage only)
- ❌ Proper error handling
- ❌ Rate limiting
- ❌ Email notifications
- ❌ Download button
- ❌ Mobile optimization
- ❌ Accessibility
- ❌ Tests

**What We MUST Have:**
- ✅ Meshy.ai API integration (working)
- ✅ Image upload to R2 or local storage
- ✅ Status polling (simple, can be inefficient)
- ✅ Three.js viewer (basic scene)
- ✅ End-to-end flow (upload → view)

---

## 🏗️ Tech Stack (Minimal)

**Backend:**
- FastAPI (single file: `apps/server/app/prototype.py`)
- In-memory task storage (dict, not Redis)
- Meshy.ai API client (httpx)
- File upload to local `/tmp` (not R2 yet)

**Frontend:**
- Single Svelte page: `apps/frontend/src/routes/prototype/+page.svelte`
- Three.js via CDN (no npm install delay)
- Fetch API for polling (no SSE complexity)

**No Docker Compose (yet):**
- Run FastAPI directly: `uvicorn app.prototype:app --reload`
- Run SvelteKit directly: `npm run dev`

---

## 📋 Implementation Steps (4 Tasks)

### TASK 1: Backend Meshy Integration (30 min)
**File:** `apps/server/app/prototype.py`

**Endpoints:**
```python
POST /api/prototype/upload
  - Accept image file
  - Upload to Meshy.ai
  - Return task_id

GET /api/prototype/status/{task_id}
  - Poll Meshy.ai status
  - Return {status, progress, model_url}
```

**In-Memory Storage:**
```python
TASKS = {}  # task_id -> {status, progress, model_url, meshy_task_id}
```

**Meshy.ai Flow:**
1. Upload image → Get presigned URL from Meshy
2. Upload to presigned URL
3. Create image-to-3D task
4. Poll status every 5 seconds
5. Return GLB URL when complete

**Technical Debt:**
- No database (ephemeral)
- No error handling (will crash on errors)
- No validation (accepts any file)
- Meshy API key hardcoded in .env (OK for prototype)

---

### TASK 2: Frontend Upload UI (20 min)
**File:** `apps/frontend/src/routes/prototype/+page.svelte`

**UI:**
```svelte
<script lang="ts">
  let file: File | null = null;
  let taskId: string | null = null;
  let status = 'idle'; // idle | uploading | processing | complete

  async function handleUpload() {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch('http://localhost:8011/api/prototype/upload', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    taskId = data.task_id;
    status = 'processing';
    pollStatus();
  }
</script>

<input type="file" accept="image/*" bind:files={...} />
<button on:click={handleUpload}>Upload</button>
{#if status === 'processing'}
  <p>Processing... {progress}%</p>
{/if}
```

**Technical Debt:**
- No drag-drop (just file input)
- No file validation
- No preview
- No error handling
- Hardcoded backend URL
- No mobile responsive

---

### TASK 3: Three.js Viewer (30 min)
**File:** `apps/frontend/src/routes/prototype/+page.svelte` (same file)

**Three.js Setup:**
```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import * as THREE from 'three';
  import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
  import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

  let canvas: HTMLCanvasElement;
  let modelUrl: string | null = null;

  onMount(() => {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, 800/600, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ canvas });

    const controls = new OrbitControls(camera, renderer.domElement);
    const loader = new GLTFLoader();

    camera.position.z = 5;

    // Basic lighting
    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(1, 1, 1);
    scene.add(light);
    scene.add(new THREE.AmbientLight(0x404040));

    // Animation loop
    function animate() {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    }
    animate();

    // Load model when available
    if (modelUrl) {
      loader.load(modelUrl, (gltf) => {
        scene.add(gltf.scene);
      });
    }
  });
</script>

<canvas bind:this={canvas} width="800" height="600"></canvas>
```

**Technical Debt:**
- Fixed canvas size (not responsive)
- No loading state for model
- No error handling (model load fails)
- No camera positioning optimization
- No lighting optimization
- No touch gesture support

---

### TASK 4: Status Polling (20 min)
**File:** `apps/frontend/src/routes/prototype/+page.svelte` (same file)

**Polling Logic:**
```svelte
<script lang="ts">
  let progress = 0;

  async function pollStatus() {
    const interval = setInterval(async () => {
      const res = await fetch(`http://localhost:8011/api/prototype/status/${taskId}`);
      const data = await res.json();

      progress = data.progress || 0;

      if (data.status === 'SUCCEEDED') {
        modelUrl = data.model_url;
        status = 'complete';
        clearInterval(interval);
        loadModel(modelUrl); // Trigger Three.js load
      }

      if (data.status === 'FAILED') {
        status = 'failed';
        clearInterval(interval);
      }
    }, 5000); // Poll every 5 seconds
  }
</script>
```

**Technical Debt:**
- Polling (not SSE) = inefficient
- No exponential backoff
- No error handling (network failure)
- Interval not cleaned up on unmount
- Hardcoded 5-second interval

---

## 🔥 Quick Start Commands

### 1. Install Dependencies (if needed)
```bash
# Backend
cd apps/server
pip install fastapi uvicorn httpx python-multipart

# Frontend
cd apps/frontend
npm install three
```

### 2. Set Environment Variables
```bash
# apps/server/.env
MESHY_API_KEY=msy_your_api_key_here
```

### 3. Run Backend
```bash
cd apps/server
uvicorn app.prototype:app --reload --port 8011
```

### 4. Run Frontend
```bash
cd apps/frontend
npm run dev
```

### 5. Test
```
Open: http://localhost:5173/prototype
Upload: dirt bike image
Wait: 5-15 minutes
View: 3D model rotates
```

---

## 📝 Technical Debt Register (For Refactoring)

### Critical (Must Fix for MVP)
1. **Authentication** - Wide open API (anyone can use)
2. **Database** - Ephemeral storage (lost on restart)
3. **Error Handling** - Crashes on errors
4. **File Validation** - No size/type checks
5. **Rate Limiting** - Can be abused

### High Priority
6. **Polling → SSE** - Inefficient polling (60-180 requests)
7. **R2 Storage** - Using local /tmp (not persistent)
8. **Mobile Responsive** - Fixed canvas size
9. **Email Notifications** - No notification when complete
10. **Download Button** - Can't download GLB file

### Medium Priority
11. **Accessibility** - No keyboard nav, screen readers
12. **Loading States** - No spinners, progress unclear
13. **Touch Gestures** - No mobile 3D controls
14. **CORS Config** - Hardcoded origins
15. **Logging** - No structured logging

### Low Priority
16. **Tests** - Zero test coverage
17. **Docker Compose** - Manual service management
18. **CI/CD** - No automated deployment
19. **Monitoring** - No error tracking (Sentry)
20. **Analytics** - No usage tracking

---

## 🎯 Success Criteria (Prototype)

**Minimum bar:**
- ✅ Upload image via UI
- ✅ Meshy.ai returns 3D model
- ✅ Model loads in Three.js
- ✅ Can rotate/zoom model
- ✅ End-to-end flow works

**Failure acceptable:**
- ❌ Crashes on invalid input (we know)
- ❌ Lost data on restart (we know)
- ❌ Mobile doesn't work (we know)
- ❌ No error messages (we know)

**Timeline:**
- Backend: 30 min
- Frontend Upload: 20 min
- Three.js Viewer: 30 min
- Status Polling: 20 min
- Testing/Debugging: 2 hours
- **Total: ~4 hours**

---

## 🔄 Refactoring Path

**Phase 1: Stabilize (1 day)**
- Add error handling
- Add file validation
- Add database (PostgreSQL)
- Add R2 storage
- Add basic auth

**Phase 2: Optimize (2 days)**
- Replace polling with SSE
- Add Redis caching
- Add rate limiting
- Mobile responsive
- Email notifications

**Phase 3: Production (1 week)**
- Full authentication (Supabase)
- Comprehensive tests
- CI/CD pipeline
- Monitoring (Sentry)
- Docker Compose
- Follow FINAL-milestone-plan-v2.md

---

## 📦 File Structure (Prototype)

```
apps/
├── server/
│   ├── app/
│   │   └── prototype.py          # Single-file backend
│   └── .env                       # MESHY_API_KEY
└── frontend/
    └── src/
        └── routes/
            └── prototype/
                └── +page.svelte   # Single-page frontend
```

**No changes to existing codebase.**
**Prototype is isolated.**
**Easy to delete or refactor later.**

---

## 🚀 GO GO GO

**Next Action:**
Launch dev-backend-fastapi subagent to implement `apps/server/app/prototype.py`

**Command:**
```bash
# User will say "go" or "do it"
# Then I launch subagent with this task
```

---

**Created:** 2025-11-11
**Mode:** RAPID PROTOTYPE
**Status:** Ready to implement
**Timeline:** 4 hours to working demo

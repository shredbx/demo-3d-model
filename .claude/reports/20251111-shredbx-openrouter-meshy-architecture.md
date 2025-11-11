# ShredBX Image-to-3D with OpenRouter + Meshy.ai API

**Date:** 2025-11-11
**Architecture:** Cloud-based (No GPU Required)
**Cost:** ~$0.20-0.50 per 3D model generation

---

## Updated Architecture (API-Based)

Since you're using **OpenRouter** for AI capabilities, we'll integrate with **Meshy.ai API** for image-to-3D conversion. This eliminates the need for local GPU hosting.

### Why Meshy.ai?

✅ **Best Image-to-3D API** (2025 benchmark winner)
✅ **Fast:** 2-15 minutes per model
✅ **High Quality:** Production-ready textured meshes
✅ **Simple REST API** (similar to OpenRouter)
✅ **Affordable:** ~20-40 credits ($0.20-0.40) per generation
✅ **Free tier:** 200 credits/month to start

---

## System Architecture

```
┌──────────────────┐
│  Web Frontend    │
│  (SvelteKit)     │
└────────┬─────────┘
         │ POST /api/generate-3d-model
         │
┌────────┴─────────┐
│  FastAPI Server  │
│  (Your Backend)  │
├──────────────────┤
│ • Upload image   │
│ • Call Meshy API │
│ • Poll status    │
│ • Return GLB URL │
└────────┬─────────┘
         │
    ┌────┴────┬──────────────┐
    │         │              │
┌───┴───┐ ┌──┴──────┐ ┌─────┴──────┐
│Meshy  │ │OpenRouter│ │ PostgreSQL │
│.ai API│ │   API    │ │  (Storage) │
└───────┘ └──────────┘ └────────────┘
```

### Workflow

1. **User uploads dirt bike image** (YZ 250X photo)
2. **Backend sends to Meshy.ai API** (Image to 3D task)
3. **Meshy generates 3D model** (~5-15 minutes)
4. **Backend polls for completion** (or webhook)
5. **Model URL returned** (GLB file hosted on Meshy CDN)
6. **Frontend displays in Three.js** (interactive viewer)
7. **Optional: Store in DB** (model URL, metadata)

---

## Implementation

### 1. Backend Integration (FastAPI)

#### File: `apps/server/app/services/model_generator.py`

```python
import httpx
import asyncio
from typing import Optional
from app.core.config import settings

class MeshyImageTo3DService:
    """
    Meshy.ai Image to 3D API Integration

    Docs: https://docs.meshy.ai/en/api/image-to-3d
    """

    def __init__(self):
        self.api_key = settings.MESHY_API_KEY
        self.base_url = "https://api.meshy.ai/v2/image-to-3d"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def create_task(
        self,
        image_url: str,
        enable_pbr: bool = True,
        resolution: str = "1024"  # 512, 1024, 2048
    ) -> dict:
        """
        Create Image to 3D generation task

        Args:
            image_url: Public URL of uploaded image
            enable_pbr: Enable PBR materials (better textures)
            resolution: Texture resolution (512, 1024, 2048)

        Returns:
            {"task_id": "...", "status": "PENDING"}
        """
        payload = {
            "image_url": image_url,
            "enable_pbr": enable_pbr,
            "texture_resolution": resolution
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.base_url,
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def get_task_status(self, task_id: str) -> dict:
        """
        Poll task status

        Returns:
            {
                "id": "task_id",
                "status": "PENDING" | "PROCESSING" | "SUCCEEDED" | "FAILED",
                "progress": 0-100,
                "model_url": "https://cdn.meshy.ai/.../model.glb" (when done),
                "thumbnail_url": "https://cdn.meshy.ai/.../preview.png"
            }
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/{task_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def wait_for_completion(
        self,
        task_id: str,
        max_wait: int = 900,  # 15 minutes
        poll_interval: int = 10  # 10 seconds
    ) -> dict:
        """
        Wait for task to complete with polling

        Args:
            task_id: Task ID from create_task
            max_wait: Maximum seconds to wait
            poll_interval: Seconds between polls

        Returns:
            Final task result with model_url

        Raises:
            TimeoutError: If exceeds max_wait
            ValueError: If task fails
        """
        elapsed = 0

        while elapsed < max_wait:
            result = await self.get_task_status(task_id)
            status = result.get("status")

            if status == "SUCCEEDED":
                return result
            elif status == "FAILED":
                raise ValueError(f"Task failed: {result.get('error')}")

            # Still processing
            progress = result.get("progress", 0)
            print(f"Task {task_id}: {status} ({progress}%)")

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise TimeoutError(f"Task {task_id} exceeded {max_wait}s")

    async def generate_3d_model(self, image_url: str) -> str:
        """
        High-level: Upload image and wait for GLB URL

        Args:
            image_url: Public URL of dirt bike image

        Returns:
            GLB model URL (hosted on Meshy CDN)
        """
        # Create task
        task = await self.create_task(image_url)
        task_id = task["id"]

        print(f"Created Meshy task: {task_id}")

        # Wait for completion
        result = await self.wait_for_completion(task_id)

        # Return model URL
        model_url = result.get("model_url")
        if not model_url:
            raise ValueError("No model URL in response")

        return model_url
```

#### File: `apps/server/app/api/v1/endpoints/models.py`

```python
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from app.services.model_generator import MeshyImageTo3DService
from app.services.storage import upload_to_s3  # Or your storage
import uuid

router = APIRouter()
meshy_service = MeshyImageTo3DService()

@router.post("/generate-3d-model")
async def generate_3d_model(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Generate 3D model from uploaded dirt bike image

    Process:
    1. Upload image to storage (S3/Cloudflare R2)
    2. Send public URL to Meshy API
    3. Return task ID for polling
    4. (Optional) Process in background
    """
    try:
        # Read uploaded image
        image_bytes = await file.read()

        # Upload to your storage (S3, R2, etc.)
        image_id = str(uuid.uuid4())
        image_url = await upload_to_s3(
            image_bytes,
            f"uploads/{image_id}.jpg"
        )

        # Create Meshy task
        task = await meshy_service.create_task(image_url)

        # Return task ID for frontend polling
        return {
            "task_id": task["id"],
            "status": "PENDING",
            "message": "3D model generation started. This takes 5-15 minutes."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/generate-3d-model/{task_id}/status")
async def get_generation_status(task_id: str):
    """
    Poll generation status

    Returns:
        {
            "status": "PENDING" | "PROCESSING" | "SUCCEEDED" | "FAILED",
            "progress": 0-100,
            "model_url": "..." (when done)
        }
    """
    try:
        result = await meshy_service.get_task_status(task_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-3d-model-sync")
async def generate_3d_model_sync(file: UploadFile = File(...)):
    """
    Synchronous version (waits for completion)
    WARNING: Can take 5-15 minutes, client must have long timeout
    """
    try:
        # Upload image
        image_bytes = await file.read()
        image_id = str(uuid.uuid4())
        image_url = await upload_to_s3(image_bytes, f"uploads/{image_id}.jpg")

        # Generate and wait
        model_url = await meshy_service.generate_3d_model(image_url)

        return {
            "status": "SUCCEEDED",
            "model_url": model_url,
            "message": "3D model generated successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### File: `apps/server/app/core/config.py`

```python
class Settings(BaseSettings):
    # Existing
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # Add Meshy.ai
    MESHY_API_KEY: str

    # Storage (for image uploads)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    S3_BUCKET_NAME: Optional[str] = None

    # Or Cloudflare R2
    R2_ACCOUNT_ID: Optional[str] = None
    R2_ACCESS_KEY_ID: Optional[str] = None
    R2_SECRET_ACCESS_KEY: Optional[str] = None
    R2_BUCKET_NAME: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()
```

#### File: `.env`

```bash
# Existing
OPENROUTER_API_KEY=your_openrouter_key

# Add Meshy.ai
MESHY_API_KEY=your_meshy_api_key

# Storage (choose one)
# Option 1: AWS S3
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
S3_BUCKET_NAME=shredbx-uploads

# Option 2: Cloudflare R2 (cheaper)
R2_ACCOUNT_ID=your_r2_account
R2_ACCESS_KEY_ID=your_r2_key
R2_SECRET_ACCESS_KEY=your_r2_secret
R2_BUCKET_NAME=shredbx-uploads
```

---

### 2. Frontend (SvelteKit)

#### File: `apps/frontend/src/routes/generate/+page.svelte`

```svelte
<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import * as THREE from 'three';
  import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
  import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

  let fileInput: HTMLInputElement;
  let selectedFile: File | null = null;
  let taskId: string | null = null;
  let status: 'idle' | 'uploading' | 'generating' | 'completed' | 'error' = 'idle';
  let progress = 0;
  let modelUrl: string | null = null;
  let errorMessage = '';

  // Three.js
  let canvas: HTMLCanvasElement;
  let scene: THREE.Scene;
  let camera: THREE.PerspectiveCamera;
  let renderer: THREE.WebGLRenderer;
  let controls: OrbitControls;
  let currentModel: THREE.Object3D | null = null;

  onMount(() => {
    initThreeJS();
  });

  onDestroy(() => {
    if (renderer) {
      renderer.dispose();
    }
  });

  function initThreeJS() {
    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a2e);

    // Camera
    camera = new THREE.PerspectiveCamera(50, 800 / 600, 0.1, 1000);
    camera.position.set(0, 1, 3);

    // Renderer
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setSize(800, 600);
    renderer.setPixelRatio(window.devicePixelRatio);

    // Controls
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(5, 5, 5);
    scene.add(directionalLight);

    // Grid
    const grid = new THREE.GridHelper(10, 10);
    scene.add(grid);

    // Animate
    function animate() {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    }
    animate();
  }

  function handleFileSelect(event: Event) {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files[0]) {
      selectedFile = target.files[0];
    }
  }

  async function generateModel() {
    if (!selectedFile) return;

    status = 'uploading';
    errorMessage = '';

    try {
      // Upload image and start generation
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch('/api/v1/models/generate-3d-model', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      taskId = data.task_id;
      status = 'generating';

      // Start polling
      pollStatus();

    } catch (error) {
      status = 'error';
      errorMessage = error instanceof Error ? error.message : 'Unknown error';
    }
  }

  async function pollStatus() {
    if (!taskId) return;

    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/v1/models/generate-3d-model/${taskId}/status`);
        const data = await response.json();

        progress = data.progress || 0;

        if (data.status === 'SUCCEEDED') {
          clearInterval(pollInterval);
          modelUrl = data.model_url;
          status = 'completed';
          loadModel(modelUrl);
        } else if (data.status === 'FAILED') {
          clearInterval(pollInterval);
          status = 'error';
          errorMessage = 'Generation failed';
        }
      } catch (error) {
        clearInterval(pollInterval);
        status = 'error';
        errorMessage = 'Polling failed';
      }
    }, 5000); // Poll every 5 seconds
  }

  function loadModel(url: string) {
    const loader = new GLTFLoader();
    loader.load(
      url,
      (gltf) => {
        if (currentModel) {
          scene.remove(currentModel);
        }

        currentModel = gltf.scene;

        // Center and scale
        const box = new THREE.Box3().setFromObject(currentModel);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        const maxDim = Math.max(size.x, size.y, size.z);
        const scale = 2 / maxDim;

        currentModel.scale.multiplyScalar(scale);
        currentModel.position.sub(center.multiplyScalar(scale));

        scene.add(currentModel);
      },
      undefined,
      (error) => {
        console.error('Model loading error:', error);
      }
    );
  }

  function reset() {
    selectedFile = null;
    taskId = null;
    status = 'idle';
    progress = 0;
    modelUrl = null;
    errorMessage = '';

    if (currentModel) {
      scene.remove(currentModel);
      currentModel = null;
    }
  }
</script>

<div class="container">
  <h1>🏍️ ShredBX Model Generator</h1>
  <p>Convert your dirt bike photos into 3D models</p>

  <div class="upload-section">
    <input
      type="file"
      accept="image/*"
      bind:this={fileInput}
      on:change={handleFileSelect}
      disabled={status === 'generating'}
    />

    <button
      on:click={generateModel}
      disabled={!selectedFile || status === 'generating'}
    >
      {#if status === 'idle'}
        Generate 3D Model
      {:else if status === 'uploading'}
        Uploading...
      {:else if status === 'generating'}
        Generating... {progress}%
      {:else}
        Generate Another
      {/if}
    </button>

    {#if status === 'generating'}
      <div class="progress-bar">
        <div class="progress-fill" style="width: {progress}%"></div>
      </div>
      <p class="info">⏱️ This takes 5-15 minutes. You can close this tab and come back.</p>
    {/if}

    {#if status === 'completed'}
      <p class="success">✅ Model generated successfully!</p>
      <a href={modelUrl} download>Download GLB</a>
    {/if}

    {#if status === 'error'}
      <p class="error">❌ Error: {errorMessage}</p>
    {/if}
  </div>

  <div class="viewer">
    <canvas bind:this={canvas}></canvas>
  </div>

  <div class="actions">
    <button on:click={reset}>Reset</button>
  </div>
</div>

<style>
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }

  h1 {
    font-size: 3em;
    text-align: center;
    background: linear-gradient(45deg, #00d4ff, #0099ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .upload-section {
    background: rgba(255, 255, 255, 0.05);
    padding: 30px;
    border-radius: 15px;
    margin: 30px 0;
    text-align: center;
  }

  button {
    background: linear-gradient(45deg, #00d4ff, #0099ff);
    border: none;
    padding: 12px 30px;
    font-size: 1.1em;
    color: white;
    border-radius: 8px;
    cursor: pointer;
    margin: 10px;
  }

  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .progress-bar {
    width: 100%;
    height: 20px;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 10px;
    overflow: hidden;
    margin: 20px 0;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(45deg, #00d4ff, #0099ff);
    transition: width 0.5s ease;
  }

  .viewer {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 15px;
    overflow: hidden;
    display: flex;
    justify-content: center;
    padding: 20px;
  }

  .success {
    color: #00ff00;
    font-weight: bold;
  }

  .error {
    color: #ff0000;
    font-weight: bold;
  }

  .info {
    color: #aaa;
    font-style: italic;
  }
</style>
```

---

## Setup Instructions

### 1. Get Meshy.ai API Key

```bash
# Sign up at https://www.meshy.ai/
# Go to API section
# Get your API key
```

**Free Tier:** 200 credits/month (~5-10 models)
**Pro Tier:** $20/month = 1,000 credits (~25-50 models)

### 2. Configure Environment

```bash
# Add to .env
MESHY_API_KEY=msy_xxxxxxxxxxxxx
```

### 3. Install Dependencies

```bash
# Backend
cd apps/server
pip install httpx  # For async HTTP requests

# Frontend (already have Three.js)
cd apps/frontend
# three, GLTFLoader already installed
```

### 4. Test API

```bash
# Test Meshy API connectivity
curl -X POST https://api.meshy.ai/v2/image-to-3d \
  -H "Authorization: Bearer $MESHY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/bike.jpg",
    "enable_pbr": true
  }'
```

---

## Cost Analysis

### Meshy.ai Pricing

| Plan | Price | Credits | Cost per Model |
|------|-------|---------|----------------|
| Free | $0 | 200/month | ~$0 (5-10 models) |
| Pro | $20/month | 1,000 | ~$0.40 |
| Max | $60/month | 4,000 | ~$0.30 |
| Max Unlimited | $120/month | 4,000 + unlimited relaxed | ~$0 (unlimited) |

**Image to 3D Cost:** ~20-40 credits per generation

### Comparison: API vs Self-Hosted

| Approach | Setup Cost | Monthly Cost | Speed | Quality |
|----------|-----------|-------------|-------|---------|
| **Meshy API** | $0 | $20-60 | 5-15 min | Excellent |
| **TripoSR Local (GPU)** | $800 (RTX 3060) | $10 (electricity) | 2-5 sec | Good |
| **TripoSR Cloud GPU** | $0 | $50-100 | 2-5 sec | Good |

**Recommendation:** Start with Meshy API (no setup, proven quality), switch to self-hosted if generating >200 models/month.

---

## Alternative: Use OpenRouter + Shap-E

If you want to stay purely with OpenRouter:

```python
# OpenRouter doesn't have native 3D generation
# But you can use text-to-3D via Shap-E prompts

# 1. Generate text description with vision model
description = await openrouter_vision(image, "Describe this dirt bike in detail")

# 2. Use Shap-E model (if available on OpenRouter)
# or call Shap-E separately

# Note: Quality is lower than Meshy, but cheaper
```

**Verdict:** Meshy is significantly better for production use.

---

## Next Steps

1. **Get Meshy API key** (free tier to start)
2. **Add backend endpoint** (`model_generator.py`)
3. **Create SvelteKit page** (`/generate`)
4. **Test with YZ 250X image**
5. **Optional: Add DB storage** (save generated models)
6. **Optional: Add Three.js MCP** (AI control)

---

## Questions?

- Want me to create the full implementation as a user story?
- Should I integrate with existing Bestays infrastructure?
- Prefer standalone project or part of Bestays?

Ready to proceed! 🏍️

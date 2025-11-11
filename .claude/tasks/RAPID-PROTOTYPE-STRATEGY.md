# Rapid Prototype Strategy - OpenRouter Approach

**Date:** 2025-11-11
**Mode:** RAPID PROTOTYPING
**Goal:** Process bike-test.jpg → Generate 3D model → Display on hero page

---

## 🎯 Refined Strategy (Based on User Input)

### What We're Building
1. **Python script** to process `docs/bike-test.jpg`
2. **OpenRouter + Vision Model** to analyze the bike and extract description
3. **Text-to-3D generation** (NOT image-to-3D, as that's harder)
4. **Three.js viewer** on dark hero homepage
5. **Track usage carefully** (one test only initially)

### Why This Approach?
- OpenRouter doesn't have native image-to-3D models
- We can use vision model (GPT-4 Vision, Claude 3.5 Sonnet) to describe the bike
- Then use text-to-3D (cheaper, faster than image-to-3D)
- Alternative: Still use Meshy.ai for image-to-3D (better quality)

---

## 🔧 Technical Approach

### Option A: Vision → Text Description → Text-to-3D
```
bike-test.jpg
  → OpenRouter (GPT-4 Vision) → "Blue YZ250X dirt bike with skull graphics..."
  → Text-to-3D API (Meshy, Shap-E, or local) → bike.glb
  → Three.js viewer
```

**Pros:**
- Uses OpenRouter (as user requested)
- Text-to-3D is cheaper than image-to-3D
- Can refine description for better results

**Cons:**
- Two-step process (more latency)
- Text-to-3D quality may be lower than image-to-3D
- Loses visual details from photo

### Option B: Direct Image-to-3D (Meshy.ai)
```
bike-test.jpg
  → Meshy.ai API → bike.glb
  → Three.js viewer
```

**Pros:**
- Single step (simpler)
- Better quality (image preserves details)
- Proven to work well

**Cons:**
- Not using OpenRouter (but we can use it later for other features)
- Costs ~$0.50 per generation

### Recommendation: **Option B (Meshy.ai)** for MVP
- Better quality for prototype demo
- Use OpenRouter later for chat features, object extraction, refinements
- Track Meshy usage: 1 test = $0.50, have 1000 credits ($500 budget)

---

## 🚀 Implementation Plan

### Step 1: Backend Script (30 min)
**File:** `scripts/generate_3d_model.py`

```python
#!/usr/bin/env python3
"""
Generate 3D model from bike image using Meshy.ai API
Usage: python scripts/generate_3d_model.py docs/bike-test.jpg
"""

import httpx
import asyncio
import os
import sys
from pathlib import Path

MESHY_API_KEY = os.getenv("MESHY_API_KEY", "msy_...")

async def upload_image(image_path: str) -> str:
    """Upload image to Meshy and return public URL"""
    # Implementation
    pass

async def create_3d_task(image_url: str) -> str:
    """Create image-to-3D generation task"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.meshy.ai/v2/image-to-3d",
            json={
                "image_url": image_url,
                "enable_pbr": True,  # Physically Based Rendering textures
                "ai_model": "meshy-4"  # Latest model
            },
            headers={"Authorization": f"Bearer {MESHY_API_KEY}"}
        )
        data = response.json()
        return data["id"]  # task_id

async def poll_status(task_id: str) -> dict:
    """Poll task status until complete"""
    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(
                f"https://api.meshy.ai/v2/image-to-3d/{task_id}",
                headers={"Authorization": f"Bearer {MESHY_API_KEY}"}
            )
            data = response.json()

            print(f"Status: {data['status']}, Progress: {data.get('progress', 0)}%")

            if data["status"] == "SUCCEEDED":
                return data
            elif data["status"] == "FAILED":
                raise Exception(f"Generation failed: {data.get('error')}")

            await asyncio.sleep(10)  # Poll every 10 seconds

async def download_model(model_url: str, output_path: str):
    """Download GLB file"""
    async with httpx.AsyncClient() as client:
        response = await client.get(model_url)
        Path(output_path).write_bytes(response.content)

async def main(image_path: str):
    print(f"🚀 Processing: {image_path}")

    # Step 1: Upload image
    print("📤 Uploading image to Meshy...")
    image_url = await upload_image(image_path)
    print(f"✅ Image URL: {image_url}")

    # Step 2: Create task
    print("🎨 Creating 3D generation task...")
    task_id = await create_3d_task(image_url)
    print(f"✅ Task ID: {task_id}")

    # Step 3: Poll until complete
    print("⏳ Waiting for generation (5-15 min)...")
    result = await poll_status(task_id)

    # Step 4: Download model
    output_path = f"apps/frontend/static/models/bike-{task_id}.glb"
    print(f"⬇️  Downloading model to {output_path}...")
    await download_model(result["model_urls"]["glb"], output_path)

    print(f"✅ Done! Model saved to: {output_path}")
    print(f"💰 Cost: ~$0.50 (tracked in Meshy dashboard)")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/generate_3d_model.py <image_path>")
        sys.exit(1)

    asyncio.run(main(sys.argv[1]))
```

### Step 2: Frontend Hero Page (30 min)
**File:** `apps/frontend/src/routes/+page.svelte`

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import * as THREE from 'three';
  import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
  import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

  let canvas: HTMLCanvasElement;

  onMount(() => {
    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0a); // Dark background

    // Camera
    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    camera.position.set(3, 2, 5);

    // Renderer
    const renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);

    // Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(5, 10, 7.5);
    scene.add(directionalLight);

    const spotLight = new THREE.SpotLight(0x00ffff, 0.5);
    spotLight.position.set(-5, 5, 5);
    scene.add(spotLight);

    // Load model
    const loader = new GLTFLoader();
    loader.load(
      '/models/bike-TASK_ID.glb', // Replace with actual task ID
      (gltf) => {
        const model = gltf.scene;

        // Center model
        const box = new THREE.Box3().setFromObject(model);
        const center = box.getCenter(new THREE.Vector3());
        model.position.sub(center);

        scene.add(model);
      },
      (progress) => {
        console.log('Loading:', (progress.loaded / progress.total) * 100, '%');
      },
      (error) => {
        console.error('Error loading model:', error);
      }
    );

    // Animation loop
    function animate() {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    }
    animate();

    // Resize handler
    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });
  });
</script>

<div class="hero">
  <div class="hero-content">
    <h1>ShredBX</h1>
    <p>Transform Your Bike into 3D</p>
  </div>
  <canvas bind:this={canvas} />
</div>

<style>
  .hero {
    position: relative;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
  }

  .hero-content {
    position: absolute;
    top: 20%;
    left: 50%;
    transform: translateX(-50%);
    text-align: center;
    z-index: 10;
    color: #fff;
  }

  h1 {
    font-size: 4rem;
    font-weight: 900;
    background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
  }

  p {
    font-size: 1.5rem;
    color: #8892b0;
    margin-top: 1rem;
  }

  canvas {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
  }
</style>
```

### Step 3: Updated Ports (as requested)
**Original Ports → New Ports (+310)**

| Service | Original | New (+310) |
|---------|----------|------------|
| Frontend | 5173 | **5483** |
| Backend | 8011 | **8321** |
| PostgreSQL | 5432 | **5742** |
| Redis | 6379 | **6689** |

**Files to update:**
- `.env`
- `docker-compose.yml`
- `apps/frontend/vite.config.ts`
- `apps/server/.env`

---

## 📝 Execution Steps

### 1. Set up environment
```bash
# Install dependencies
pip install httpx python-dotenv

# Create .env
cat > .env << EOF
MESHY_API_KEY=msy_YOUR_KEY_HERE
OPENROUTER_API_KEY=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
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
EOF
```

### 2. Run generation script
```bash
python scripts/generate_3d_model.py docs/bike-test.jpg
# Wait 5-15 minutes
# Output: apps/frontend/static/models/bike-XXXXX.glb
```

### 3. Update frontend
```bash
# Update +page.svelte with correct model path
# Update ports to 5483
cd apps/frontend
npm install three
npm run dev -- --port 5483
```

### 4. View result
```
Open: http://localhost:5483
See: 3D bike model rotating on dark hero page
```

---

## 💰 Cost Tracking

**Meshy.ai Usage:**
- Account: 1000 credits ($500 budget)
- Cost per model: ~$0.50 (1 credit)
- First test: 1 credit used
- Remaining: 999 credits

**Track in dashboard:** https://app.meshy.ai/dashboard

---

## 🔄 Future: Use OpenRouter

**When we add features later:**
- **Chat interface:** Use OpenRouter (Claude, GPT-4) for chat
- **Object extraction:** Use vision models to extract bike parts
- **Description refinement:** Let users describe what they want changed
- **Multi-model comparison:** Test different 3D generation approaches

**For now:** Meshy.ai for best quality prototype

---

## ✅ Success Criteria

- ✅ Script processes bike-test.jpg successfully
- ✅ Meshy.ai returns GLB model
- ✅ Model loads on homepage
- ✅ Can rotate/zoom bike in 3D
- ✅ Dark hero design looks professional
- ✅ Cost tracked (1 credit used)

---

**Next Action:** Create backend script + update ports

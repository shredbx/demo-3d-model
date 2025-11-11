# ShredBX Image-to-3D Model Generator - System Design & Implementation Plan

**Date:** 2025-11-11
**Project:** ShredBX Model Generator
**Goal:** Convert dirt bike photos (like YZ 250X) into interactive 3D models with textures

---

## Executive Summary

This document outlines a complete system for converting single dirt bike images into 3D models that can be viewed and manipulated in a web browser using Three.js. The system uses **TripoSR** (Stability AI's open-source image-to-3D model) for generation and provides an interactive Three.js viewer with optional AI control via the Three.js MCP server.

### Key Capabilities

✅ **Single Image to 3D:** Upload a dirt bike photo, get a 3D model
✅ **Fast Generation:** ~0.5s on GPU, ~30s on CPU
✅ **Interactive Viewer:** Rotate, zoom, pan in browser
✅ **Texture Baking:** Apply colors from original image
✅ **AI Control (Optional):** Use MCP to manipulate model via natural language
✅ **Export:** Download as GLB/OBJ for use in Blender, Unity, etc.

---

## Architecture Overview

### System Components

```
┌─────────────────┐
│   Web Browser   │
│  (Three.js UI)  │
└────────┬────────┘
         │ HTTP (Upload image, download GLB)
         │
┌────────┴────────┐
│  FastAPI Server │
│  (Python 3.10+) │
├─────────────────┤
│ • Image upload  │
│ • TripoSR model │
│ • 3D generation │
│ • Texture baking│
└────────┬────────┘
         │ Load model weights
         │
┌────────┴────────┐
│  TripoSR Model  │
│  (Hugging Face) │
│  • MIT License  │
│  • ~6GB VRAM    │
└─────────────────┘

Optional: Three.js MCP Server
┌─────────────────┐
│   Claude Code   │
└────────┬────────┘
         │ stdio
┌────────┴────────┐
│ three-js-mcp    │
│ (WebSocket:8082)│
└────────┬────────┘
         │ WebSocket
┌────────┴────────┐
│ Three.js Viewer │
└─────────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI (Python 3.10+) | API server, image processing |
| **AI Model** | TripoSR (Stability AI) | Image → 3D mesh generation |
| **Frontend** | HTML/JS or SvelteKit | Upload UI, Three.js viewer |
| **3D Rendering** | Three.js | WebGL-based 3D rendering |
| **Model Format** | GLB (GLTF Binary) | Compact, texture-embedded format |
| **Optional MCP** | three-js-mcp | AI control of 3D scene |

---

## Phase 1: Core System (MVP)

### 1.1 Backend Setup (Python + TripoSR)

#### Directory Structure

```
shredbx-model-generator/
├── backend/
│   ├── app.py              # FastAPI server
│   ├── requirements.txt    # Python dependencies
│   ├── models/             # TripoSR model cache
│   └── uploads/            # Temporary image storage
├── frontend/
│   ├── index.html          # Upload UI + Three.js viewer
│   ├── app.js              # Three.js logic
│   └── style.css           # Styling
├── output/                 # Generated 3D models
└── README.md               # Project documentation
```

#### Backend: app.py (FastAPI)

```python
from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import torch
from PIL import Image
import io
import os
from pathlib import Path
import uuid

# TripoSR imports
from tsr.system import TSR
from tsr.utils import save_mesh, save_glb

app = FastAPI(title="ShredBX Model Generator")

# CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize TripoSR model (lazy loading)
model = None
device = "cuda" if torch.cuda.is_available() else "cpu"

def load_model():
    global model
    if model is None:
        print(f"Loading TripoSR model on {device}...")
        model = TSR.from_pretrained(
            "stabilityai/TripoSR",
            config_name="config.yaml",
            weight_name="model.ckpt"
        )
        model.to(device)
        print("Model loaded successfully")
    return model

@app.get("/")
async def root():
    return {
        "service": "ShredBX Model Generator",
        "status": "running",
        "device": device
    }

@app.post("/generate-model")
async def generate_model(
    file: UploadFile = File(...),
    bake_texture: bool = True,
    texture_resolution: int = 1024
):
    """
    Generate 3D model from uploaded image

    Args:
        file: Image file (PNG, JPG, etc.)
        bake_texture: Whether to bake textures from image
        texture_resolution: Texture size (512, 1024, 2048)

    Returns:
        GLB file download
    """
    try:
        # Load image
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Load model
        tsr_model = load_model()

        # Generate 3D mesh
        print("Generating 3D model...")
        with torch.no_grad():
            scene_codes = tsr_model([image], device=device)

        # Extract mesh
        meshes = tsr_model.extract_mesh(scene_codes)
        mesh = meshes[0]

        # Generate unique filename
        output_id = str(uuid.uuid4())
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        if bake_texture:
            # Bake texture from original image
            output_path = output_dir / f"{output_id}_textured.glb"
            save_glb(
                mesh,
                output_path,
                image=image,
                texture_resolution=texture_resolution
            )
        else:
            # Simple mesh without texture
            output_path = output_dir / f"{output_id}.glb"
            save_glb(mesh, output_path)

        print(f"Model saved to {output_path}")

        # Return file for download
        return FileResponse(
            output_path,
            media_type="model/gltf-binary",
            filename=f"bike_{output_id}.glb"
        )

    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/models/{model_id}")
async def get_model(model_id: str):
    """Download previously generated model"""
    output_path = Path(f"output/{model_id}.glb")

    if not output_path.exists():
        # Try textured version
        output_path = Path(f"output/{model_id}_textured.glb")

    if output_path.exists():
        return FileResponse(
            output_path,
            media_type="model/gltf-binary",
            filename=f"bike_{model_id}.glb"
        )
    else:
        return {"error": "Model not found"}, 404

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### Backend: requirements.txt

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
pillow==10.2.0
torch>=2.0.0
torchvision>=0.15.0
numpy>=1.24.0
trimesh>=4.0.0
rembg>=2.0.50
huggingface-hub>=0.20.0

# TripoSR (install from GitHub)
# git+https://github.com/VAST-AI-Research/TripoSR.git
```

#### Installation Steps

```bash
# Create virtual environment
cd /Users/solo/Projects/_repos/shredbx-model-generator
python3 -m venv venv
source venv/bin/activate

# Install PyTorch with CUDA (if you have NVIDIA GPU)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Or CPU-only version (slower)
pip install torch torchvision

# Install dependencies
pip install -r backend/requirements.txt

# Install TripoSR
pip install git+https://github.com/VAST-AI-Research/TripoSR.git

# Verify installation
python -c "import tsr; print('TripoSR installed successfully')"
```

---

### 1.2 Frontend (Three.js Viewer)

#### Frontend: index.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShredBX - Dirt Bike 3D Model Generator</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🏍️ ShredBX Model Generator</h1>
            <p>Convert your dirt bike photos into 3D models</p>
        </header>

        <div class="upload-section">
            <input type="file" id="imageInput" accept="image/*" />
            <button id="generateBtn" disabled>Generate 3D Model</button>

            <div id="status"></div>

            <div class="options">
                <label>
                    <input type="checkbox" id="bakeTexture" checked />
                    Bake textures from image
                </label>
                <label>
                    Texture Resolution:
                    <select id="textureRes">
                        <option value="512">512px</option>
                        <option value="1024" selected>1024px</option>
                        <option value="2048">2048px</option>
                    </select>
                </label>
            </div>
        </div>

        <div id="viewer">
            <canvas id="canvas3d"></canvas>
            <div id="controls-help">
                Left-click: Rotate | Right-click: Pan | Scroll: Zoom
            </div>
        </div>

        <div class="actions">
            <button id="downloadBtn" style="display: none;">Download GLB</button>
            <button id="resetBtn">Reset</button>
        </div>
    </div>

    <script type="importmap">
        {
            "imports": {
                "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
                "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
            }
        }
    </script>
    <script type="module" src="app.js"></script>
</body>
</html>
```

#### Frontend: app.js

```javascript
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

// Configuration
const API_URL = 'http://localhost:8000';

// Three.js scene setup
let scene, camera, renderer, controls;
let currentModel = null;
let currentBlob = null;

// DOM elements
const imageInput = document.getElementById('imageInput');
const generateBtn = document.getElementById('generateBtn');
const downloadBtn = document.getElementById('downloadBtn');
const resetBtn = document.getElementById('resetBtn');
const status = document.getElementById('status');
const canvas = document.getElementById('canvas3d');

// Initialize Three.js
function initThree() {
    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a1a);

    // Camera
    camera = new THREE.PerspectiveCamera(
        50,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
    );
    camera.position.set(0, 1, 3);

    // Renderer
    renderer = new THREE.WebGLRenderer({
        canvas,
        antialias: true
    });
    renderer.setSize(window.innerWidth * 0.8, window.innerHeight * 0.6);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;

    // Controls
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(5, 5, 5);
    directionalLight.castShadow = true;
    scene.add(directionalLight);

    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight2.position.set(-5, 3, -5);
    scene.add(directionalLight2);

    // Grid helper
    const gridHelper = new THREE.GridHelper(10, 10);
    scene.add(gridHelper);

    // Animation loop
    animate();
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

// Handle window resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth * 0.8, window.innerHeight * 0.6);
});

// Enable generate button when image is selected
imageInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        generateBtn.disabled = false;
        updateStatus(`Image selected: ${e.target.files[0].name}`);
    }
});

// Generate 3D model
generateBtn.addEventListener('click', async () => {
    const file = imageInput.files[0];
    if (!file) return;

    const bakeTexture = document.getElementById('bakeTexture').checked;
    const textureRes = document.getElementById('textureRes').value;

    generateBtn.disabled = true;
    updateStatus('Generating 3D model... This may take 10-30 seconds');

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(
            `${API_URL}/generate-model?bake_texture=${bakeTexture}&texture_resolution=${textureRes}`,
            {
                method: 'POST',
                body: formData
            }
        );

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const blob = await response.blob();
        currentBlob = blob;

        // Load GLB into Three.js
        const url = URL.createObjectURL(blob);
        loadModel(url);

        updateStatus('✅ Model generated successfully!');
        downloadBtn.style.display = 'inline-block';

    } catch (error) {
        updateStatus(`❌ Error: ${error.message}`);
        console.error(error);
    } finally {
        generateBtn.disabled = false;
    }
});

// Load GLB model into scene
function loadModel(url) {
    // Remove existing model
    if (currentModel) {
        scene.remove(currentModel);
    }

    const loader = new GLTFLoader();
    loader.load(
        url,
        (gltf) => {
            currentModel = gltf.scene;

            // Center and scale model
            const box = new THREE.Box3().setFromObject(currentModel);
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());

            const maxDim = Math.max(size.x, size.y, size.z);
            const scale = 2 / maxDim;
            currentModel.scale.multiplyScalar(scale);

            currentModel.position.sub(center.multiplyScalar(scale));
            currentModel.position.y = 0;

            scene.add(currentModel);

            // Auto-rotate
            currentModel.rotation.y = Math.PI / 4;

            updateStatus('Model loaded in viewer');
        },
        (progress) => {
            const percent = (progress.loaded / progress.total * 100).toFixed(0);
            updateStatus(`Loading model: ${percent}%`);
        },
        (error) => {
            updateStatus(`Error loading model: ${error.message}`);
            console.error(error);
        }
    );
}

// Download generated model
downloadBtn.addEventListener('click', () => {
    if (!currentBlob) return;

    const url = URL.createObjectURL(currentBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bike_${Date.now()}.glb`;
    a.click();
    URL.revokeObjectURL(url);

    updateStatus('Model downloaded');
});

// Reset
resetBtn.addEventListener('click', () => {
    if (currentModel) {
        scene.remove(currentModel);
        currentModel = null;
    }
    currentBlob = null;
    imageInput.value = '';
    generateBtn.disabled = true;
    downloadBtn.style.display = 'none';
    updateStatus('Ready to generate a new model');
});

// Update status message
function updateStatus(message) {
    status.textContent = message;
}

// Initialize on load
initThree();
updateStatus('Upload a dirt bike image to get started');
```

#### Frontend: style.css

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: #fff;
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
}

header {
    text-align: center;
    margin-bottom: 40px;
}

header h1 {
    font-size: 3em;
    margin-bottom: 10px;
    background: linear-gradient(45deg, #00d4ff, #0099ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

header p {
    font-size: 1.2em;
    color: #aaa;
}

.upload-section {
    background: rgba(255, 255, 255, 0.05);
    padding: 30px;
    border-radius: 15px;
    margin-bottom: 30px;
    text-align: center;
}

input[type="file"] {
    margin-bottom: 20px;
}

button {
    background: linear-gradient(45deg, #00d4ff, #0099ff);
    border: none;
    padding: 12px 30px;
    font-size: 1.1em;
    color: white;
    border-radius: 8px;
    cursor: pointer;
    transition: transform 0.2s;
    margin: 5px;
}

button:hover:not(:disabled) {
    transform: translateY(-2px);
}

button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

#status {
    margin: 20px 0;
    padding: 15px;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 8px;
    min-height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.options {
    margin-top: 20px;
    display: flex;
    gap: 20px;
    justify-content: center;
    flex-wrap: wrap;
}

.options label {
    display: flex;
    align-items: center;
    gap: 8px;
}

#viewer {
    position: relative;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 15px;
    overflow: hidden;
    margin-bottom: 30px;
}

#canvas3d {
    display: block;
    margin: 0 auto;
}

#controls-help {
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0, 0, 0, 0.7);
    padding: 10px 20px;
    border-radius: 20px;
    font-size: 0.9em;
}

.actions {
    text-align: center;
}
```

---

## Phase 2: Running the System

### Step 1: Start Backend

```bash
cd /Users/solo/Projects/_repos/shredbx-model-generator
source venv/bin/activate
python backend/app.py
```

Server will run at: `http://localhost:8000`

### Step 2: Serve Frontend

```bash
# Simple Python HTTP server
cd /Users/solo/Projects/_repos/shredbx-model-generator/frontend
python3 -m http.server 3000
```

Frontend will be at: `http://localhost:3000`

### Step 3: Test with YZ 250X Image

1. Open browser to `http://localhost:3000`
2. Click "Choose File" and select your YZ 250X image
3. Check "Bake textures from image"
4. Click "Generate 3D Model"
5. Wait 10-30 seconds (depends on CPU/GPU)
6. View and interact with generated model
7. Download GLB file for use in Blender, Unity, etc.

---

## Phase 3: Optional - Three.js MCP Integration

### Why Add MCP?

Allows AI control of the 3D model:
- "Rotate the bike to show the exhaust"
- "Zoom in on the front suspension"
- "Change the color to red"
- "Add a second bike next to it"

### Setup Steps

1. **Install three-js-mcp** (from earlier report)

```bash
cd ~/Projects/mcp-servers
git clone https://github.com/locchung/three-js-mcp.git
cd three-js-mcp
npm install
npm run build

# Configure Claude Code
claude mcp add "three-js-mcp" \
  --type stdio \
  --command node \
  --arg /Users/solo/Projects/mcp-servers/three-js-mcp/build/main.js
```

2. **Add WebSocket client to app.js**

```javascript
// Add to top of app.js
let mcpSocket = null;

// Connect to MCP server
function connectMCP() {
    mcpSocket = new WebSocket('ws://localhost:8082');

    mcpSocket.onopen = () => {
        console.log('[MCP] Connected');
        sendSceneState();
    };

    mcpSocket.onmessage = (event) => {
        const command = JSON.parse(event.data);
        handleMCPCommand(command);
    };

    mcpSocket.onclose = () => {
        console.log('[MCP] Disconnected, reconnecting...');
        setTimeout(connectMCP, 5000);
    };
}

function sendSceneState() {
    if (!mcpSocket || mcpSocket.readyState !== WebSocket.OPEN) return;

    const state = {
        objects: scene.children
            .filter(obj => obj.type === 'Group') // Only models
            .map(obj => ({
                id: obj.uuid,
                type: 'model',
                position: obj.position.toArray(),
                rotation: obj.rotation.toArray(),
                scale: obj.scale.toArray()
            }))
    };

    mcpSocket.send(JSON.stringify(state));
}

function handleMCPCommand(command) {
    switch(command.tool) {
        case 'moveObject':
            if (currentModel) {
                currentModel.position.set(...command.arguments.position);
                sendSceneState();
            }
            break;
        case 'startRotation':
            // Add rotation animation
            break;
        // ... handle other commands
    }
}

// Call after initializing Three.js
initThree();
connectMCP();
```

3. **Use Claude to control model**

```
User: "Rotate the bike 90 degrees to the right"
Claude: [Uses moveObject MCP tool]

User: "Make it spin slowly"
Claude: [Uses startRotation MCP tool with speed: 0.01]
```

---

## Performance Optimization

### GPU Acceleration

If you have an NVIDIA GPU:

```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Install CUDA-enabled PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

**Speed comparison:**
- CPU: ~20-40 seconds per image
- GPU (6GB VRAM): ~0.5-2 seconds per image

### Model Caching

The backend loads the TripoSR model once and keeps it in memory. First generation is slower (model loading), subsequent generations are fast.

### Texture Quality vs Speed

| Resolution | File Size | Quality | Generation Time |
|------------|-----------|---------|-----------------|
| 512px | ~2MB | Good | Fast |
| 1024px | ~5MB | Better | Medium |
| 2048px | ~15MB | Best | Slower |

Recommendation: Use 1024px for balanced quality/speed.

---

## Advanced Features (Future Enhancements)

### Multi-View Generation

For better 3D reconstruction:

1. Upload 3-5 photos from different angles
2. TripoSR processes each view
3. Combine meshes using photogrammetry
4. Result: More accurate 3D model

### Custom Training

Fine-tune TripoSR on dirt bike dataset:

1. Collect 100+ dirt bike images
2. Generate ground truth 3D models
3. Fine-tune TripoSR weights
4. Improved accuracy for dirt bikes specifically

### Real-Time Preview

Add a "Quick Preview" mode:

1. Lower resolution (256x256)
2. Lower poly mesh (5k triangles)
3. Generate in ~2 seconds
4. User confirms, then generate high-res

### Mobile Support

1. Progressive Web App (PWA)
2. Take photo with phone camera
3. Upload and generate on server
4. View on phone (WebGL)

---

## Troubleshooting

### Issue: "CUDA out of memory"

**Solution:**
```python
# In app.py, reduce batch size or use CPU
device = "cpu"  # Force CPU mode
```

Or upgrade GPU VRAM (need 6GB+).

### Issue: Generation takes too long

**Solutions:**
1. Use GPU instead of CPU
2. Reduce texture resolution to 512px
3. Disable texture baking (faster, no textures)

### Issue: Model quality is poor

**Reasons:**
- Image has poor lighting
- Bike is partially obscured
- Background is cluttered

**Solutions:**
1. Use clearer images with good lighting
2. Crop image to focus on bike
3. Remove background (use `rembg` library)

### Issue: Three.js viewer shows black screen

**Check:**
1. Browser console for errors
2. CORS is enabled on backend
3. GLB file downloaded successfully
4. WebGL is supported in browser

---

## Deployment (Production)

### Option 1: Docker Container

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install git+https://github.com/VAST-AI-Research/TripoSR.git

# Copy application
COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t shredbx-backend .
docker run -p 8000:8000 shredbx-backend
```

### Option 2: Cloud GPU (Recommended)

Use services with GPU support for faster generation:

- **RunPod:** GPU instances from $0.20/hour
- **Vast.ai:** GPU marketplace, cheap spot instances
- **AWS EC2 g4dn.xlarge:** ~$0.50/hour
- **Google Colab:** Free GPU (limited hours)

### Option 3: Serverless (Advanced)

Use Modal, Banana, or Replicate for serverless GPU:

```python
# Example with Modal
import modal

stub = modal.Stub("shredbx-generator")

@stub.function(gpu="T4", image=modal.Image.debian_slim().pip_install(...))
def generate_model(image_bytes):
    # TripoSR code here
    return glb_bytes
```

---

## Cost Analysis

### Self-Hosted (Local GPU)

- **Initial:** $500-1000 (NVIDIA RTX 3060/4060)
- **Electricity:** ~$10/month
- **Unlimited generations**

### Cloud GPU

- **Pay-per-use:** $0.20-0.50/hour
- **~100 models/hour**
- **Cost per model:** $0.002-0.005

### Serverless

- **Pay-per-generation:** $0.01-0.02/model
- **No maintenance**
- **Scales automatically**

---

## Next Steps

### Immediate Actions

1. **Set up development environment:**
   ```bash
   cd /Users/solo/Projects/_repos/shredbx-model-generator
   mkdir -p backend frontend output
   ```

2. **Install dependencies:**
   - Create `backend/requirements.txt`
   - Install Python packages
   - Install TripoSR

3. **Create backend server:**
   - Copy `app.py` code
   - Test with `python backend/app.py`

4. **Create frontend:**
   - Copy HTML/JS/CSS files
   - Test with local server

5. **Test with YZ 250X image:**
   - Upload image
   - Generate model
   - View in Three.js

### Week 1 Goals

- ✅ Working backend (FastAPI + TripoSR)
- ✅ Working frontend (Three.js viewer)
- ✅ Can generate basic 3D models
- ✅ Can download GLB files

### Week 2 Goals

- ✅ Texture baking from images
- ✅ Better lighting in viewer
- ✅ Model quality improvements
- ✅ Three.js MCP integration

### Future Roadmap

- Multi-view generation
- Custom training on dirt bike dataset
- Mobile app (PWA)
- Model gallery/database
- Social sharing
- AR viewer (view bike in your garage via phone)

---

## Conclusion

This system provides a complete pipeline for converting dirt bike photos into interactive 3D models. Using TripoSR (state-of-the-art, open-source, MIT licensed) ensures high quality results with fast generation times, especially on GPU.

The modular architecture allows for easy enhancement:
- Add MCP for AI control
- Deploy to cloud for scalability
- Train custom models for better accuracy
- Build mobile apps for on-the-go generation

Ready to start building! 🏍️

---

**Next:** Create user story and tasks following SDLC workflow?

**Questions for User:**
1. Do you have an NVIDIA GPU? (affects speed dramatically)
2. Prefer simple HTML or SvelteKit for frontend?
3. Want to integrate with Bestays or keep as standalone project?
4. Priority: Speed vs Quality vs Features?

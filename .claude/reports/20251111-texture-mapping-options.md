# Texture Mapping Options for 3D Models

**Date:** 2025-11-11
**Context:** How to apply custom textures from bike photos to 3D models
**Status:** Technical Guide

---

## Current Situation

You have:
- ✅ **KTM dirt bike GLB model** (14MB, with existing textures)
- ✅ **Bike photo** (`docs/bike-test.jpg` - blue/white bike)
- ❌ **No automated texture mapping** (Meshy requires paid plan)

---

## Option 1: Use Meshy.ai (Automated - Paid)

**What it does:**
- Automatically extracts colors and textures from your bike photo
- Applies them to the generated 3D model
- Handles UV mapping, lighting, materials

**Cost:** $16/month (Starter plan)
**Quality:** ⭐⭐⭐⭐⭐ (AI-powered, professional)
**Time:** 5-15 minutes per model

**How to use:**
1. Upgrade at https://www.meshy.ai/settings/subscription
2. Run: `source venv/bin/activate && python scripts/generate_3d_model.py docs/bike-test.jpg`
3. Wait 5-15 minutes
4. Get GLB with textures from your exact bike photo

**Pros:**
- Fully automated
- Professional quality
- Works with any photo
- PBR textures (realistic materials)

**Cons:**
- Costs money
- Requires subscription
- API-dependent

---

## Option 2: Manual Texture Mapping (Free - Complex)

**What it requires:**
- Blender (3D software)
- UV unwrapping knowledge
- Texture extraction skills
- 2-4 hours of work

### Steps:

#### 1. **Extract Bike Image**
Already have: `docs/bike-test.jpg`

#### 2. **Load Model in Blender**
```bash
# Install Blender
brew install --cask blender

# Open KTM model
blender docs/3d-glb/ktm_dirt_bike.glb
```

#### 3. **UV Unwrap the Model**
- Select bike mesh
- UV Editing workspace
- Unwrap → Smart UV Project
- Adjust UV islands to match bike parts

#### 4. **Create Texture from Photo**
- Image Editor → Open `bike-test.jpg`
- Paint bike colors onto UV map
- Extract decals/graphics from photo
- Apply to corresponding UV regions

#### 5. **Bake Materials**
- Set up material nodes
- Use bike photo as reference
- Bake diffuse, metallic, roughness maps
- Export as GLB

#### 6. **Export and Test**
```
File → Export → glTF 2.0 (.glb)
```

**Pros:**
- FREE
- Full control over textures
- Can mix multiple photos
- Learn 3D skills

**Cons:**
- Very time-consuming (2-4 hours)
- Requires Blender expertise
- Manual UV mapping is tedious
- Results depend on your skill level

---

## Option 3: Shader-Based Color Replacement (Moderate)

**Concept:** Use Three.js shaders to dynamically replace colors in the existing KTM model

### Implementation:

```svelte
<!-- apps/frontend/src/routes/+page.svelte -->

<script lang="ts">
  import * as THREE from 'three';

  // After loading the model:
  model.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      // Replace KTM orange with bike blue
      if (child.material.color) {
        const currentColor = child.material.color.getHex();

        // KTM orange: #FF6600
        if (currentColor === 0xFF6600) {
          child.material.color.setHex(0x0066FF); // Blue from bike photo
        }

        // Replace black with custom color
        if (currentColor === 0x000000) {
          child.material.color.setHex(0x1a1a1a); // Dark gray
        }
      }
    }
  });
</script>
```

**Pros:**
- Quick to implement (30 min)
- No external tools needed
- Can customize colors dynamically
- Free

**Cons:**
- Limited to color changes
- Can't add graphics/decals
- Doesn't handle complex textures
- May not match photo exactly

---

## Option 4: Use TripoSR (Free Alternative to Meshy)

**What it is:** Open-source image-to-3D model (runs locally)

### Setup:

```bash
# Install TripoSR
pip install triposr

# Generate 3D model
python -m triposr.run \
  --image docs/bike-test.jpg \
  --output apps/frontend/static/models/bike-triposr.glb
```

**Cost:** FREE (runs on your GPU)
**Quality:** ⭐⭐⭐ (Good, but not as polished as Meshy)
**Time:** 2-5 minutes (local processing)

**Pros:**
- Completely free
- Runs locally (no API)
- Generates from your exact photo
- Includes textures

**Cons:**
- Lower quality than Meshy
- Requires GPU (CUDA)
- Less polished results
- May need manual cleanup

**GitHub:** https://github.com/VAST-AI-Research/TripoSR

---

## Option 5: Hybrid Approach (Recommended for MVP)

**Strategy:** Use KTM model + color adjustments + Meshy later

### Phase 1: MVP (Now)
1. ✅ Use KTM dirt bike model as-is
2. ✅ Demonstrate working 3D viewer
3. ✅ Show rotation, zoom, lighting
4. ✅ Get user feedback

### Phase 2: Color Customization (1 hour)
1. Implement shader-based color replacement
2. Extract dominant colors from bike photo:
   ```python
   from PIL import Image
   from collections import Counter

   img = Image.open('docs/bike-test.jpg')
   pixels = img.getcolors(maxcolors=100000)
   # Find blue: #0066FF
   # Find white: #FFFFFF
   ```
3. Apply to KTM model

### Phase 3: Real Textures (When budget allows)
1. Upgrade Meshy.ai ($16/month)
2. Generate from bike photo
3. Replace KTM model with generated model

---

## Recommendation

**For NOW (Free MVP):**

Use **Option 5 (Hybrid)**:
1. Keep KTM model (already working)
2. Add shader-based color adjustments (30 min)
3. Document "This is a demo model, upload your bike to get a custom model"

**For PRODUCTION:**

Use **Option 1 (Meshy.ai)**:
- Best quality
- Automated
- Professional results
- Worth $16/month for real product

**Alternative:**

Try **Option 4 (TripoSR)** if you:
- Have a good GPU (NVIDIA)
- Want free solution
- Don't mind lower quality
- Can run Python locally

---

## Quick Color Adjustment Code

Add this to your `+page.svelte` after loading the model:

```svelte
<script lang="ts">
  // After model loads successfully:

  // Extract colors from bike photo (approximately)
  const BIKE_BLUE = 0x0066FF;   // Blue plastic
  const BIKE_WHITE = 0xFFFFFF;  // White graphics
  const BIKE_BLACK = 0x1a1a1a;  // Dark frame

  // Replace KTM colors
  const KTM_ORANGE = 0xFF6600;
  const KTM_BLACK = 0x000000;

  model.traverse((child) => {
    if (child instanceof THREE.Mesh && child.material) {
      const material = child.material;

      if (material.color) {
        const hex = material.color.getHex();

        // Replace orange with blue
        if (Math.abs(hex - KTM_ORANGE) < 0x111111) {
          material.color.setHex(BIKE_BLUE);
        }

        // Adjust black slightly
        if (hex === KTM_BLACK) {
          material.color.setHex(BIKE_BLACK);
        }
      }
    }
  });

  console.log('✅ Colors adjusted to match bike photo');
</script>
```

---

## Summary

| Option | Cost | Time | Quality | Automation |
|--------|------|------|---------|------------|
| **Meshy.ai** | $16/mo | 15 min | ⭐⭐⭐⭐⭐ | Full |
| **Manual (Blender)** | FREE | 2-4 hours | ⭐⭐⭐⭐ | None |
| **Shader Colors** | FREE | 30 min | ⭐⭐ | Partial |
| **TripoSR** | FREE | 5 min | ⭐⭐⭐ | Full |
| **Hybrid (KTM)** | FREE | 30 min | ⭐⭐⭐ | Partial |

**Best for MVP:** Hybrid approach (use KTM + color tweaks)
**Best for Production:** Meshy.ai (when ready to invest)

---

**Next Steps:**
1. ✅ KTM model is already implemented
2. ⏺ Visit http://localhost:5483/ to see it
3. ⏺ Add color adjustments if desired
4. ⏺ Decide on Meshy subscription for production

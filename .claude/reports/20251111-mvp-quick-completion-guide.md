# MVP Quick Completion Guide

**Date:** 2025-11-11
**Goal:** Get a working dirt bike 3D viewer ASAP
**Time:** 15 minutes

---

## Current Status

✅ **Frontend Working:**
- Beautiful hero page at http://localhost:5483/
- Three.js viewer configured
- Auto-rotation, controls, professional lighting
- Hero text moved to top (5%)

⚠️ **Meshy API Issue:**
- API returns 404 "NoMatchingRoute"
- Likely API version mismatch or endpoint changed
- Need to debug, but this blocks MVP

---

## MVP Solution: Use Pre-Made Model

Since the hard part (Three.js viewer) is DONE, let's use a free dirt bike model to complete the MVP.

### Option 1: Sketchfab (Recommended - 5 minutes)

**Steps:**

1. **Visit Sketchfab:**
   https://sketchfab.com/3d-models/dirt-bike-2f6a85f5bae2407abf3419cff3eacd07

2. **Download GLB:**
   - Click "Download 3D Model" button
   - Choose "glTF" format (includes .glb)
   - Free for personal use

3. **Move to project:**
   ```bash
   # Download will be in ~/Downloads/
   mv ~/Downloads/dirt_bike.glb apps/frontend/static/models/dirt-bike.glb
   ```

4. **Update frontend:**
   Edit `apps/frontend/src/routes/+page.svelte` line 14:
   ```typescript
   const MODEL_PATH = '/models/dirt-bike.glb';
   ```

5. **Reload browser:**
   Visit http://localhost:5483/ - you should see the dirt bike!

### Option 2: Find Better Model (10 minutes)

Browse Sketchfab for best match to your blue bike:
```
https://sketchfab.com/search?q=yamaha+dirt+bike&type=models
https://sketchfab.com/search?q=yz250&type=models
```

Look for:
- Free download
- Good quality (check polygon count)
- Similar to your bike-test.jpg image
- Available in GLB or glTF format

---

## After MVP Works

Once you have a working dirt bike model displaying:

### 1. Fix Meshy API Integration

The API issue needs debugging. Possible solutions:

**A. Check Meshy Dashboard:**
- Log in to https://app.meshy.ai/
- Check API docs for current endpoint
- Verify API key is active
- Check credits balance

**B. Try Different API Version:**
Currently using: `https://api.meshy.ai/v2/image-to-3d`

Try:
- `https://api.meshy.ai/v1/image-to-3d`
- `https://api.meshy.ai/v3/image-to-3d`
- Check docs for latest version

**C. Alternative: Luma AI**
Better docs, similar pricing ($0.50/model):
```python
# https://lumalabs.ai/api
LUMA_API_URL = "https://api.lumalabs.ai/dream-machine/v1/generations"
```

### 2. Document the Working MVP

Create screenshots:
1. Homepage with dirt bike
2. Rotating 3D model
3. Zoom functionality
4. Mobile view (if responsive)

### 3. Add Upload UI (Next Phase)

Once the viewer works with a static model, add:
```svelte
<!-- apps/frontend/src/routes/+page.svelte -->

<div class="upload-zone">
  <input type="file" accept="image/*" on:change={handleUpload} />
  <p>Upload your dirt bike photo</p>
</div>

<script>
  async function handleUpload(event) {
    const file = event.target.files[0];
    // Send to backend API
    // Poll for status
    // Update MODEL_PATH when complete
  }
</script>
```

---

## Quick Commands

```bash
# Current status
cd /Users/solo/Projects/_repos/shredbx-model-generator

# Frontend running on:
# http://localhost:5483/

# Download a model from Sketchfab
# Move to: apps/frontend/static/models/dirt-bike.glb

# Update model path in:
# apps/frontend/src/routes/+page.svelte
# Line 14: const MODEL_PATH = '/models/dirt-bike.glb';

# Refresh browser - DONE!
```

---

## Why This Approach?

### Pros:
- **Fast:** Working MVP in 5-15 minutes
- **De-risks:** Separates frontend (working) from backend (broken API)
- **Demonstrates:** The core value prop (3D bike viewer)
- **Professional:** Uses real 3D model, not placeholder

### Cons:
- Not using actual bike photo (yet)
- Manual model download (temporary)
- Meshy API still needs fixing

---

## MVP Acceptance Criteria

✅ **Must Have:**
- [x] Beautiful landing page
- [x] 3D dirt bike model visible
- [x] User can rotate model (drag)
- [x] User can zoom (scroll)
- [ ] Model looks like a dirt bike (get from Sketchfab)

⏺ **Nice to Have (Later):**
- [ ] Upload image
- [ ] Generate from photo
- [ ] Download model
- [ ] Save to gallery

---

## Next Steps After MVP

1. **Debug Meshy API:**
   - Check dashboard
   - Try different endpoints
   - Contact support if needed

2. **Build Backend:**
   - FastAPI upload endpoint
   - Meshy integration (once fixed)
   - Status polling
   - Storage (Cloudflare R2)

3. **Connect Frontend:**
   - Upload UI component
   - API client
   - Loading states
   - Error handling

4. **Production Ready:**
   - Authentication (Clerk)
   - Database (PostgreSQL)
   - Deployment (Railway + Vercel)

---

## Current File to Edit

**File:** `apps/frontend/src/routes/+page.svelte`

**Line 14 (change this):**
```typescript
const MODEL_PATH = '/models/test-model.glb';  // ← helmet model
```

**To this:**
```typescript
const MODEL_PATH = '/models/dirt-bike.glb';  // ← your downloaded bike
```

**Save and refresh:** http://localhost:5483/

---

## Summary

**Fastest MVP Path:**
1. Download dirt bike GLB from Sketchfab (5 min)
2. Move to `apps/frontend/static/models/dirt-bike.glb`
3. Update MODEL_PATH in +page.svelte
4. Refresh browser → Working MVP! 🎉

**Then:**
- Screenshot/demo the working viewer
- Debug Meshy API separately
- Build upload functionality

The hard part (Three.js + lighting + controls) is DONE.
Just need a proper dirt bike model to display!

---

**Status:** Ready to complete MVP
**Blocker:** Need to download free GLB model
**ETA:** 5-15 minutes

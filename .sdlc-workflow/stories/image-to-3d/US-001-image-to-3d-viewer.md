# User Story: US-001 - Image to 3D Model Viewer

**Status:** 📋 PLANNING
**Domain:** image-to-3d
**Type:** feature
**Priority:** high
**Created:** 2025-11-11
**Updated:** 2025-11-11
**Estimated Complexity:** High (new feature, external API integration)
**Default Product:** shredbx
**Portable:** true
**Ported To:** []

---

## Story

**As a** dirt bike enthusiast
**I want** to upload a photo of my bike (like a YZ 250X) to the homepage
**So that** I can see it as an interactive 3D model that I can rotate and zoom

---

## Acceptance Criteria

### Functional Requirements

1. **Homepage Upload Interface**
   - ✅ Drag-and-drop area prominently displayed on homepage
   - ✅ Click to upload alternative
   - ✅ Accept image formats: JPG, PNG, WEBP
   - ✅ File size limit: 10MB
   - ✅ Preview uploaded image before processing

2. **Backend Processing**
   - ✅ FastAPI endpoint receives image upload
   - ✅ Upload image to storage (Cloudflare R2 or S3)
   - ✅ Call Meshy.ai API for 3D generation
   - ✅ Poll for completion with status updates
   - ✅ Return GLB model URL when ready

3. **3D Viewer (Three.js)**
   - ✅ Display generated 3D model in interactive viewer
   - ✅ Support orbit controls (rotate with mouse/touch)
   - ✅ Support zoom (mouse wheel/pinch)
   - ✅ Support pan (right-click drag)
   - ✅ Proper lighting (ambient + directional)
   - ✅ Grid/ground plane for context
   - ✅ Smooth camera controls with damping

4. **User Experience**
   - ✅ Loading states during upload
   - ✅ Progress indicator during generation (5-15 minutes)
   - ✅ Error handling with clear messages
   - ✅ Download GLB button after generation
   - ✅ Reset/upload another image option

### Technical Requirements

1. **API Integration**
   - ✅ Meshy.ai API key configured
   - ✅ Async polling mechanism (not blocking)
   - ✅ Webhook support (optional, for faster updates)
   - ✅ Rate limiting awareness

2. **Storage**
   - ✅ Uploaded images stored in cloud (R2/S3)
   - ✅ Generated models cached (URL from Meshy CDN)
   - ✅ Database record of generations (optional)

3. **Frontend**
   - ✅ SvelteKit page with Three.js integration
   - ✅ Responsive design (desktop, tablet, mobile)
   - ✅ WebGL compatibility check
   - ✅ Fallback for non-WebGL browsers

4. **Performance**
   - ✅ Image upload < 5 seconds
   - ✅ 3D model loading < 3 seconds
   - ✅ Smooth 60fps rendering on mid-range devices
   - ✅ Texture quality: 1024px (configurable)

### Non-Functional Requirements

1. **Security**
   - ✅ File type validation (prevent malicious uploads)
   - ✅ File size enforcement
   - ✅ API key stored securely (env vars)
   - ✅ CORS properly configured

2. **Cost Management**
   - ✅ Track Meshy.ai credit usage
   - ✅ Alert when approaching credit limit
   - ✅ Free tier: 200 credits (~5-10 models)

3. **Error Handling**
   - ✅ Invalid file format error
   - ✅ File too large error
   - ✅ API failure retry logic
   - ✅ Generation timeout handling (max 20 minutes)
   - ✅ Network offline detection

---

## Architecture

### High-Level Flow

```
┌──────────────┐
│   Homepage   │
│  (SvelteKit) │
│              │
│ [Drop Image] │
└──────┬───────┘
       │ POST /api/v1/3d-models/generate
       │ (multipart/form-data)
       ↓
┌──────────────────┐
│ FastAPI Backend  │
│                  │
│ 1. Validate      │
│ 2. Upload to R2  │
│ 3. Call Meshy    │
│ 4. Return taskId │
└──────┬───────────┘
       │
       ↓
┌──────────────────┐         ┌─────────────┐
│  Meshy.ai API    │←────────│  Frontend   │
│                  │         │  (Polling)  │
│  [Generating]    │─────────→│             │
│  5-15 minutes    │  Status │GET /status/{│
└──────┬───────────┘         │    taskId}  │
       │                     └─────────────┘
       │ model_url (CDN)
       ↓
┌──────────────────┐
│  Three.js Viewer │
│                  │
│ 1. Load GLB      │
│ 2. Center model  │
│ 3. Add controls  │
│ 4. Render loop   │
└──────────────────┘
```

### Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | SvelteKit 2 + Svelte 5 | Upload UI + 3D viewer |
| **3D Rendering** | Three.js + GLTFLoader | WebGL 3D model display |
| **Backend** | FastAPI (Python 3.10+) | API server, orchestration |
| **AI Service** | Meshy.ai API | Image → 3D conversion |
| **Storage** | Cloudflare R2 (or S3) | Image upload storage |
| **Database** | PostgreSQL (optional) | Track generations |
| **HTTP Client** | httpx (Python) | Async API calls |

---

## Data Flow

### 1. Image Upload

```json
POST /api/v1/3d-models/generate
Content-Type: multipart/form-data

{
  "file": <image_binary>,
  "options": {
    "texture_resolution": 1024,
    "enable_pbr": true
  }
}

Response:
{
  "task_id": "abc123",
  "status": "PENDING",
  "message": "Generation started. This takes 5-15 minutes.",
  "image_url": "https://r2.shredbx.com/uploads/abc123.jpg"
}
```

### 2. Status Polling

```json
GET /api/v1/3d-models/generate/{task_id}/status

Response (Processing):
{
  "task_id": "abc123",
  "status": "PROCESSING",
  "progress": 45,
  "message": "Generating 3D mesh..."
}

Response (Completed):
{
  "task_id": "abc123",
  "status": "SUCCEEDED",
  "progress": 100,
  "model_url": "https://cdn.meshy.ai/models/xyz789.glb",
  "thumbnail_url": "https://cdn.meshy.ai/previews/xyz789.png"
}
```

### 3. Model Display

```javascript
// Frontend loads GLB from Meshy CDN
const loader = new GLTFLoader();
loader.load(model_url, (gltf) => {
  scene.add(gltf.scene);
  // Center, scale, render
});
```

---

## Files to Create

### Backend

1. **`apps/server/app/services/model_generator.py`**
   - MeshyImageTo3DService class
   - create_task, get_task_status, wait_for_completion methods

2. **`apps/server/app/services/storage.py`**
   - upload_to_r2 or upload_to_s3 function
   - Cloud storage integration

3. **`apps/server/app/api/v1/endpoints/models.py`**
   - POST /generate-3d-model
   - GET /generate-3d-model/{task_id}/status
   - FastAPI routes

4. **`apps/server/app/core/config.py`** (update)
   - Add MESHY_API_KEY
   - Add R2/S3 credentials

5. **`apps/server/app/schemas/model.py`**
   - Pydantic models for requests/responses

### Frontend

1. **`apps/frontend/src/routes/+page.svelte`** (homepage)
   - Drag-and-drop upload area
   - Upload button
   - Status display

2. **`apps/frontend/src/routes/viewer/+page.svelte`** (or modal)
   - Three.js canvas
   - OrbitControls
   - GLTFLoader
   - Lighting setup

3. **`apps/frontend/src/lib/components/ImageUploader.svelte`**
   - Reusable upload component
   - Drag-and-drop logic
   - File validation

4. **`apps/frontend/src/lib/components/ThreeViewer.svelte`**
   - Reusable 3D viewer component
   - Three.js scene management
   - Controls abstraction

5. **`apps/frontend/src/lib/api/models.ts`**
   - API client functions
   - generateModel, getModelStatus

### Environment

1. **`.env`** (update)
   ```bash
   MESHY_API_KEY=msy_xxxxx
   R2_ACCOUNT_ID=xxxxx
   R2_ACCESS_KEY_ID=xxxxx
   R2_SECRET_ACCESS_KEY=xxxxx
   R2_BUCKET_NAME=shredbx-uploads
   ```

---

## Task Breakdown

### Phase 1: Backend Foundation (TASK-001)
**Estimated:** 1 day

1. Add Meshy.ai service integration
2. Create storage service (R2/S3)
3. Add FastAPI endpoints
4. Add environment configuration
5. Test with curl/httpie

**Acceptance:**
- ✅ Can upload image via API
- ✅ Can call Meshy.ai and get task_id
- ✅ Can poll status and get model_url
- ✅ External validation with curl

### Phase 2: Frontend Upload (TASK-002)
**Estimated:** 1 day

1. Create ImageUploader component
2. Add drag-and-drop functionality
3. Add file validation
4. Add upload progress indicator
5. Integrate with backend API

**Acceptance:**
- ✅ Can drag-drop image
- ✅ Can click to upload
- ✅ Shows upload progress
- ✅ Validates file type/size
- ✅ Gets task_id from backend

### Phase 3: Three.js Viewer (TASK-003)
**Estimated:** 2 days

1. Create ThreeViewer component
2. Initialize Three.js scene
3. Add GLTFLoader
4. Add OrbitControls
5. Add lighting and grid
6. Add responsive canvas sizing
7. Test with sample GLB models

**Acceptance:**
- ✅ Can load and display GLB model
- ✅ Can rotate (mouse drag)
- ✅ Can zoom (scroll)
- ✅ Can pan (right-click drag)
- ✅ Smooth 60fps rendering

### Phase 4: Status Polling & Integration (TASK-004)
**Estimated:** 1 day

1. Implement polling mechanism
2. Add progress UI (percentage, spinner)
3. Handle completion → load model
4. Handle errors → show message
5. Add retry logic for failed generations

**Acceptance:**
- ✅ Polls every 5 seconds
- ✅ Shows progress percentage
- ✅ Auto-loads model when done
- ✅ Shows error messages
- ✅ Can retry failed generations

### Phase 5: Polish & Optimization (TASK-005)
**Estimated:** 1 day

1. Add download GLB button
2. Add reset/upload another button
3. Add responsive design (mobile, tablet)
4. Add WebGL fallback message
5. Add loading skeletons/placeholders
6. Performance testing

**Acceptance:**
- ✅ Can download generated model
- ✅ Can reset and upload another
- ✅ Works on mobile/tablet
- ✅ Shows fallback if no WebGL
- ✅ Smooth UX throughout

### Phase 6: Testing (TASK-006)
**Estimated:** 1 day

1. E2E tests (Playwright)
   - Upload image
   - Wait for generation
   - Verify 3D model loads
2. Unit tests (backend services)
3. Component tests (Svelte Testing Library)
4. Manual testing (various browsers)

**Acceptance:**
- ✅ E2E test passes
- ✅ Backend tests pass (>80% coverage)
- ✅ Component tests pass
- ✅ Tested on Chrome, Firefox, Safari

---

## Dependencies

### External Services

1. **Meshy.ai API**
   - Free tier: 200 credits/month (~5-10 models)
   - Pro tier: $20/month = 1,000 credits (~25-50 models)
   - API Docs: https://docs.meshy.ai/en/api/image-to-3d

2. **Cloudflare R2 (or AWS S3)**
   - For image upload storage
   - R2: $0.015/GB storage, free egress
   - S3: $0.023/GB storage, $0.09/GB egress

### Internal Dependencies

- Existing FastAPI server (apps/server)
- Existing SvelteKit frontend (apps/frontend)
- Existing environment configuration (.env)

### NPM Packages (Frontend)

```json
{
  "three": "^0.160.0",
  "@types/three": "^0.160.0"
}
```

### Python Packages (Backend)

```txt
httpx==0.25.0  # For async API calls
```

---

## Success Metrics

### User Experience
- **Upload to display:** < 20 minutes total (15 min generation + UI time)
- **3D viewer performance:** 60fps on mid-range devices
- **Error rate:** < 5% of generations fail
- **User satisfaction:** Positive feedback on UX

### Technical
- **API response time:** < 500ms (excluding Meshy generation)
- **Model quality:** Recognizable 3D representation of bike
- **Uptime:** 99.5% availability
- **Cost per model:** < $0.50 (within Meshy pricing)

---

## Risks & Mitigation

### Risk 1: Meshy.ai Generation Quality
**Risk:** Generated models may not accurately represent dirt bikes
**Mitigation:**
- Test with multiple bike images before launch
- Add "Refine" option to regenerate
- Consider custom training if quality insufficient

### Risk 2: Long Generation Time
**Risk:** 5-15 minutes is too long, users may leave
**Mitigation:**
- Clearly communicate time expectation upfront
- Allow users to leave page and return (email notification?)
- Add preview/quick mode (lower quality, faster)

### Risk 3: Cost Overrun
**Risk:** Too many generations exceed budget
**Mitigation:**
- Start with free tier (200 credits)
- Monitor usage closely
- Add rate limiting (X models per user per day)
- Implement user authentication to track usage

### Risk 4: WebGL Compatibility
**Risk:** Some users may not have WebGL support
**Mitigation:**
- Add WebGL detection
- Show fallback message with static image
- Provide download link to view in external app

---

## Future Enhancements (Out of Scope for US-001)

1. **Multi-View Upload:** Upload 3-5 photos from different angles for better 3D quality
2. **Custom Training:** Fine-tune model on dirt bike dataset
3. **AR Viewer:** View bike in your garage via phone camera
4. **Gallery:** Browse/search previously generated models
5. **Social Sharing:** Share 3D model links on social media
6. **Annotations:** Add labels to bike parts (engine, exhaust, etc.)
7. **Color Customization:** Change bike colors in 3D viewer
8. **Three.js MCP Integration:** Control viewer with AI commands

---

## References

- **Technical Design:** `.claude/reports/20251111-shredbx-openrouter-meshy-architecture.md`
- **Meshy.ai Docs:** https://docs.meshy.ai/en/api/image-to-3d
- **Three.js Docs:** https://threejs.org/docs
- **GLTFLoader:** https://threejs.org/docs/#examples/en/loaders/GLTFLoader

---

## Notes

- This is the MVP (Minimum Viable Product) for ShredBX
- Focus on dirt bikes initially, can expand to other vehicles later
- Start with free Meshy tier, upgrade based on usage
- Prioritize UX over features (simple, smooth, fast)
- Consider adding authentication later (for tracking, limiting abuse)

---

**Created by:** Coordinator (Claude Code)
**Date:** 2025-11-11
**Last Updated:** 2025-11-11

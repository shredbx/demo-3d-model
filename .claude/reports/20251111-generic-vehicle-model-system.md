# Generic Vehicle Model System Design

**Date:** 2025-11-11
**Author:** Claude Code Coordinator
**Status:** Design Complete

---

## Overview

Design for a flexible, extensible vehicle model system that supports dirt bikes initially, with the ability to expand to cars, motorcycles, ATVs, and other vehicles in the future.

---

## Core Architecture

### 1. Database Schema (PostgreSQL)

```sql
-- Vehicle Categories (extensible)
CREATE TABLE vehicle_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,  -- e.g., "dirt_bike", "car", "motorcycle", "atv"
    display_name VARCHAR(100) NOT NULL,  -- e.g., "Dirt Bike", "Car", "Motorcycle"
    description TEXT,
    icon_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Vehicle Models (the 3D models)
CREATE TABLE vehicle_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,  -- Owner of the model
    category_id UUID NOT NULL REFERENCES vehicle_categories(id),

    -- Input image
    input_image_url VARCHAR(500) NOT NULL,

    -- Generated model
    model_url VARCHAR(500),  -- GLB file URL (Cloudflare R2)
    thumbnail_url VARCHAR(500),  -- Preview image

    -- Processing status
    status VARCHAR(50) NOT NULL,  -- "pending", "processing", "completed", "failed"
    task_id VARCHAR(255),  -- Meshy.ai task ID

    -- Model metadata
    model_metadata JSONB,  -- Flexible JSON for category-specific metadata

    -- Example for dirt bikes:
    -- {
    --   "make": "Yamaha",
    --   "model": "YZ250X",
    --   "year": 2023,
    --   "color": "Blue/White",
    --   "detected_features": ["wheels", "engine", "handlebars"]
    -- }

    -- Example for cars:
    -- {
    --   "make": "Toyota",
    --   "model": "Camry",
    --   "year": 2024,
    --   "color": "Silver",
    --   "body_type": "sedan"
    -- }

    -- Quality metrics
    quality_score FLOAT,  -- 0.0 - 1.0 (from AI analysis)
    polygon_count INTEGER,
    file_size_bytes BIGINT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,

    -- Soft delete
    deleted_at TIMESTAMP
);

CREATE INDEX idx_vehicle_models_user_id ON vehicle_models(user_id);
CREATE INDEX idx_vehicle_models_category_id ON vehicle_models(category_id);
CREATE INDEX idx_vehicle_models_status ON vehicle_models(status);
CREATE INDEX idx_vehicle_models_created_at ON vehicle_models(created_at DESC);

-- User preferences for vehicle categories
CREATE TABLE user_vehicle_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    category_id UUID NOT NULL REFERENCES vehicle_categories(id),
    is_favorite BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id, category_id)
);
```

---

## 2. Backend API Structure

### Service Layer Pattern

```
apps/server/app/
├── models/
│   ├── vehicle_category.py        # SQLAlchemy model
│   ├── vehicle_model.py            # SQLAlchemy model
│   └── user_vehicle_preference.py
├── schemas/
│   ├── vehicle_category.py         # Pydantic schemas
│   └── vehicle_model.py
├── services/
│   ├── model_generator.py          # Meshy.ai integration (unchanged)
│   ├── vehicle_category_service.py # Category CRUD
│   └── vehicle_model_service.py    # Model CRUD + generation orchestration
├── routers/
│   ├── vehicle_categories.py       # /api/v1/vehicle-categories
│   └── vehicle_models.py           # /api/v1/vehicle-models
└── utils/
    ├── storage.py                  # Cloudflare R2 uploads
    └── metadata_extractor.py       # Extract metadata from images (optional AI)
```

---

## 3. API Endpoints

### Vehicle Categories

```
GET    /api/v1/vehicle-categories
       List all available vehicle categories
       Response: [{"id": "uuid", "name": "dirt_bike", "display_name": "Dirt Bike", ...}]

GET    /api/v1/vehicle-categories/{category_id}
       Get category details

POST   /api/v1/vehicle-categories
       Create new category (admin only)
```

### Vehicle Models

```
POST   /api/v1/vehicle-models
       Generate a new 3D model from image
       Body: {
         "category_id": "uuid",
         "image": "file" (multipart),
         "metadata": {
           "make": "Yamaha",
           "model": "YZ250X",
           "year": 2023  // optional, user-provided
         }
       }
       Response: {
         "id": "uuid",
         "task_id": "meshy_task_abc123",
         "status": "pending"
       }

GET    /api/v1/vehicle-models/{model_id}
       Get model details and status

GET    /api/v1/vehicle-models/{model_id}/status
       Poll for generation status
       Response: {
         "status": "completed",
         "model_url": "https://r2.../model.glb",
         "thumbnail_url": "https://r2.../thumb.jpg"
       }

GET    /api/v1/vehicle-models
       List user's models (with filters)
       Query params:
         - category_id (optional)
         - status (optional)
         - limit, offset (pagination)

DELETE /api/v1/vehicle-models/{model_id}
       Delete model (soft delete)
```

---

## 4. Frontend Structure

### Component Hierarchy

```
apps/frontend/src/
├── routes/
│   ├── +page.svelte                    # Homepage (category selection)
│   ├── categories/
│   │   └── [category]/
│   │       ├── +page.svelte            # Upload page for specific category
│   │       └── +page.server.ts         # Load category data
│   ├── models/
│   │   └── [modelId]/
│   │       ├── +page.svelte            # 3D viewer
│   │       └── +page.server.ts         # Load model data
│   └── gallery/
│       └── +page.svelte                # User's model gallery
├── lib/
│   ├── components/
│   │   ├── CategoryCard.svelte         # Display vehicle category
│   │   ├── UploadZone.svelte           # Generic upload (reusable)
│   │   ├── ThreeViewer.svelte          # 3D viewer (reusable)
│   │   ├── ModelCard.svelte            # Gallery item
│   │   └── StatusPoller.svelte         # Poll generation status
│   ├── stores/
│   │   ├── categories.svelte.ts        # $state for categories
│   │   └── models.svelte.ts            # $state for user models
│   └── api/
│       ├── categories.ts               # API client for categories
│       └── models.ts                   # API client for models
```

---

## 5. User Flow

### Homepage (Category Selection)

```
┌─────────────────────────────────────┐
│         ShredBX Model Generator      │
│   Transform Your Vehicle into 3D    │
├─────────────────────────────────────┤
│                                      │
│   ┌──────────┐  ┌──────────┐       │
│   │ Dirt Bike│  │   Car    │       │
│   │  [icon]  │  │  [icon]  │       │
│   │  Click   │  │  Click   │       │
│   └──────────┘  └──────────┘       │
│                                      │
│   ┌──────────┐  ┌──────────┐       │
│   │    ATV   │  │   Truck  │       │
│   │  [icon]  │  │  [icon]  │       │
│   │ (coming) │  │ (coming) │       │
│   └──────────┘  └──────────┘       │
└─────────────────────────────────────┘
```

### Upload Page (`/categories/dirt_bike`)

```
┌─────────────────────────────────────┐
│   Upload Your Dirt Bike Photo      │
├─────────────────────────────────────┤
│                                      │
│   ┌───────────────────────────┐    │
│   │   Drag & Drop Zone        │    │
│   │   or Click to Browse      │    │
│   └───────────────────────────┘    │
│                                      │
│   Optional Details:                 │
│   Make: [Yamaha           ]        │
│   Model: [YZ250X          ]        │
│   Year: [2023             ]        │
│                                      │
│   [Generate 3D Model]               │
└─────────────────────────────────────┘
```

### Viewer Page (`/models/{id}`)

```
┌─────────────────────────────────────┐
│   Yamaha YZ250X (2023)              │
├─────────────────────────────────────┤
│                                      │
│   [Interactive 3D Viewer]           │
│                                      │
│   🖱️ Drag to rotate                │
│   🔍 Scroll to zoom                 │
│                                      │
│   [Download GLB]  [Share]  [Delete] │
└─────────────────────────────────────┘
```

---

## 6. Implementation Strategy

### Phase 1: MVP (Current - Dirt Bikes Only)

1. Hardcode `dirt_bike` category (no database table yet)
2. Simple upload → generate → view flow
3. Store minimal metadata in `model_metadata` JSON field
4. **Goal:** Validate concept with single category

### Phase 2: Multi-Category Support (Week 3-4)

1. Add `vehicle_categories` table
2. Seed with initial categories: `dirt_bike`, `car`, `motorcycle`, `atv`
3. Update frontend to show category selection
4. Update API to accept `category_id`
5. **Goal:** Generic system ready for expansion

### Phase 3: Advanced Features (Week 5-7)

1. AI-powered metadata extraction (detect make/model from image)
2. Category-specific viewer presets (camera angles, lighting)
3. User preferences (favorite categories)
4. Social features (share models, public gallery)

---

## 7. Frontend Integration with Three.js MCP

### WebSocket Connection

The Three.js MCP server runs on `ws://localhost:8082` and expects the frontend to:

1. Connect via WebSocket
2. Send scene state updates as JSON
3. Receive commands from MCP server

### Example Integration in `ThreeViewer.svelte`

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import * as THREE from 'three';

  let ws: WebSocket;
  let scene: THREE.Scene;

  onMount(() => {
    // Initialize Three.js scene (existing code)
    scene = new THREE.Scene();
    // ... renderer, camera, controls setup

    // Connect to MCP server
    ws = new WebSocket('ws://localhost:8082');

    ws.onopen = () => {
      console.log('Connected to Three.js MCP server');
    };

    ws.onmessage = (event) => {
      const command = JSON.parse(event.data);
      handleMCPCommand(command);
    };

    // Send scene state updates
    function sendSceneState() {
      const state = {
        objects: scene.children.map(obj => ({
          type: obj.type,
          position: obj.position.toArray(),
          rotation: obj.rotation.toArray()
        }))
      };
      ws.send(JSON.stringify(state));
    }

    // Animation loop
    function animate() {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
      sendSceneState();  // Update MCP server
    }
    animate();

    return () => {
      ws.close();
      renderer.dispose();
    };
  });

  function handleMCPCommand(command: any) {
    // Handle commands from MCP (add objects, etc.)
    if (command.type === 'addObject') {
      // Add object to scene based on command
    }
  }
</script>
```

---

## 8. Category-Specific Configurations

### Extensibility via JSON Configuration

```json
{
  "dirt_bike": {
    "viewer_preset": {
      "camera_position": [4, 2, 6],
      "camera_fov": 60,
      "auto_rotate_speed": 0.5
    },
    "metadata_fields": [
      {"name": "make", "label": "Make", "required": false},
      {"name": "model", "label": "Model", "required": false},
      {"name": "year", "label": "Year", "type": "number", "required": false}
    ],
    "ai_prompt": "Detect motorcycle make, model, and color from this dirt bike photo"
  },
  "car": {
    "viewer_preset": {
      "camera_position": [6, 3, 8],
      "camera_fov": 50,
      "auto_rotate_speed": 0.3
    },
    "metadata_fields": [
      {"name": "make", "label": "Make", "required": false},
      {"name": "model", "label": "Model", "required": false},
      {"name": "year", "label": "Year", "type": "number", "required": false},
      {"name": "body_type", "label": "Body Type", "type": "select", "options": ["sedan", "suv", "truck", "coupe"]}
    ],
    "ai_prompt": "Detect car make, model, year, and body type from this photo"
  }
}
```

---

## 9. Migration Path

### From Current Setup to Generic System

**Current State:**
- Hardcoded for bikes
- No category system
- Direct Meshy.ai integration

**Migration Steps:**

1. **Database Migration (Alembic):**
   ```bash
   alembic revision --autogenerate -m "add vehicle categories and models"
   alembic upgrade head
   ```

2. **Seed Categories:**
   ```python
   # apps/server/app/seeds/vehicle_categories.py
   categories = [
       {"name": "dirt_bike", "display_name": "Dirt Bike", "description": "Off-road motorcycles"},
       {"name": "car", "display_name": "Car", "description": "Passenger vehicles"},
       {"name": "motorcycle", "display_name": "Motorcycle", "description": "Street motorcycles"},
       {"name": "atv", "display_name": "ATV", "description": "All-terrain vehicles"}
   ]
   ```

3. **Update API Routes:**
   - Add category endpoints
   - Update model generation to accept `category_id`

4. **Update Frontend:**
   - Add category selection page
   - Make upload page dynamic (category-based)
   - Update viewer to use category presets

---

## 10. Testing Strategy

### Unit Tests
- Test category CRUD operations
- Test model generation with different categories
- Test metadata validation

### Integration Tests
- Test upload → generate → view flow for each category
- Test WebSocket connection to MCP server
- Test category switching

### E2E Tests (Playwright)
```typescript
test('should generate 3D model for dirt bike', async ({ page }) => {
  await page.goto('/categories/dirt_bike');
  await page.setInputFiles('input[type="file"]', './test-assets/yz250x.jpg');
  await page.click('button:has-text("Generate 3D Model")');
  await expect(page.locator('.status')).toContainText('Processing');
  // ... wait for completion
});

test('should switch between vehicle categories', async ({ page }) => {
  await page.goto('/');
  await page.click('text=Dirt Bike');
  await expect(page).toHaveURL('/categories/dirt_bike');

  await page.goto('/');
  await page.click('text=Car');
  await expect(page).toHaveURL('/categories/car');
});
```

---

## 11. Cost Considerations

### Per-Category Costs
- **Dirt Bike:** $0.53/model (Meshy.ai)
- **Car:** $0.53/model (same API, similar complexity)
- **Other vehicles:** $0.53/model

**Optimization:**
- Use lower-quality preset for previews ($0.13/model with TripoSR)
- Offer "quick preview" (low-poly) vs "high quality" (high-poly) options

---

## Summary

This design provides:
1. **Flexibility:** Easy to add new vehicle categories
2. **Scalability:** JSON metadata handles category-specific data
3. **Maintainability:** Shared components (upload, viewer) across categories
4. **User Experience:** Clear category selection → upload → view flow
5. **Future-Proof:** WebSocket integration with MCP server for advanced features

**Next Steps:**
1. Implement Phase 1 (MVP with dirt bikes)
2. Validate with users
3. Add Phase 2 (multi-category support)
4. Expand to cars, motorcycles, ATVs based on demand

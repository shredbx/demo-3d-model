# Three.js MCP Server Setup - Complete

**Date:** 2025-11-11
**Status:** ✅ Installation Complete
**Author:** Claude Code Coordinator

---

## Summary

Successfully installed and configured the Three.js MCP server for ShredBX Model Generator. The system is now ready to support advanced 3D scene manipulation through natural language commands.

---

## What Was Done

### 1. Installation ✅

- **Cloned Repository:** `https://github.com/locchung/three-js-mcp`
- **Location:** `/Users/solo/Projects/_repos/three-js-mcp`
- **Dependencies:** Installed (127 packages)
- **Build:** TypeScript compiled successfully

### 2. Configuration ✅

- **MCP Server Added:** `/Users/solo/Library/Application Support/Claude/claude_desktop_config.json`
- **Entry Point:** `node /Users/solo/Projects/_repos/three-js-mcp/build/main.js`
- **WebSocket Port:** 8082 (default)

### 3. Architecture Design ✅

- **Generic Vehicle System:** Designed flexible system for bikes, cars, and other vehicles
- **Documentation:** `.claude/reports/20251111-generic-vehicle-model-system.md`

---

## How It Works

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude Code Session                      │
│  (You can now use natural language to control Three.js)    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ stdio (MCP protocol)
                           │
                   ┌───────▼────────┐
                   │   Three.js MCP  │
                   │     Server      │
                   │  (port: 8082)   │
                   └───────┬────────┘
                           │
                           │ WebSocket
                           │
                   ┌───────▼────────┐
                   │   SvelteKit     │
                   │   Frontend      │
                   │ (localhost:5483)│
                   └────────────────┘
                           │
                   ┌───────▼────────┐
                   │   Three.js      │
                   │   3D Scene      │
                   └────────────────┘
```

### MCP Server Capabilities

The Three.js MCP server provides these tools (available to Claude Code):

1. **addObject:** Add objects to the 3D scene
2. **removeObject:** Remove objects from the scene
3. **moveObject:** Move objects in 3D space
4. **rotateObject:** Rotate objects
5. **getSceneState:** Retrieve current scene state

---

## How to Use

### Step 1: Restart Claude Code

The MCP server configuration requires a restart:

1. **Quit Claude Code completely** (Cmd+Q)
2. **Restart Claude Code**
3. The Three.js MCP server will auto-start

### Step 2: Verify Connection (Optional)

```bash
# Check if MCP server is running (after Claude Code restart)
ps aux | grep "three-js-mcp"

# You should see:
# node /Users/solo/Projects/_repos/three-js-mcp/build/main.js
```

### Step 3: Use Natural Language Commands

After restart, you can use commands like:

```
"Add a blue cube at position [2, 1, 0] to the scene"
"Rotate the cube 45 degrees on the Y axis"
"Move the model to the center"
"Get the current scene state"
```

---

## Integration with ShredBX Frontend

### Current Setup (apps/frontend/src/routes/+page.svelte)

The frontend currently has:
- ✅ Three.js scene initialized
- ✅ GLTFLoader for bike models
- ✅ OrbitControls for rotation/zoom
- ✅ Professional lighting setup
- ✅ Auto-rotation

### Next: Add WebSocket Connection

To enable MCP control, add this to `+page.svelte`:

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import * as THREE from 'three';
  // ... existing imports

  let ws: WebSocket;
  let mcpConnected = $state(false);

  onMount(() => {
    // ... existing Three.js setup

    // Connect to MCP server (optional, for advanced features)
    try {
      ws = new WebSocket('ws://localhost:8082');

      ws.onopen = () => {
        console.log('✅ Connected to Three.js MCP server');
        mcpConnected = true;
      };

      ws.onmessage = (event) => {
        const command = JSON.parse(event.data);
        handleMCPCommand(command);
      };

      ws.onerror = () => {
        console.log('⚠️ MCP server not available (optional feature)');
        mcpConnected = false;
      };

      // Send scene state to MCP (for Claude to understand scene)
      function sendSceneState() {
        if (mcpConnected && ws.readyState === WebSocket.OPEN) {
          const state = {
            camera: {
              position: camera.position.toArray(),
              rotation: camera.rotation.toArray()
            },
            objects: scene.children
              .filter(obj => obj.type === 'Mesh' || obj.type === 'Group')
              .map(obj => ({
                uuid: obj.uuid,
                type: obj.type,
                name: obj.name,
                position: obj.position.toArray(),
                rotation: obj.rotation.toArray(),
                scale: obj.scale.toArray()
              }))
          };
          ws.send(JSON.stringify(state));
        }
      }

      // Send state updates periodically
      const stateInterval = setInterval(sendSceneState, 1000);

      // Cleanup
      return () => {
        clearInterval(stateInterval);
        if (ws) ws.close();
      };
    } catch (err) {
      console.log('MCP server connection skipped (optional)');
    }
  });

  function handleMCPCommand(command: any) {
    console.log('Received MCP command:', command);

    switch (command.action) {
      case 'addObject':
        // Add object based on command.params
        break;
      case 'removeObject':
        // Remove object by UUID
        break;
      case 'moveObject':
        // Move object to new position
        break;
      // ... etc
    }
  }
</script>
```

---

## Generic Vehicle Model System

See: `.claude/reports/20251111-generic-vehicle-model-system.md`

### Key Design Decisions

1. **Database Schema:**
   - `vehicle_categories` table (dirt_bike, car, motorcycle, atv)
   - `vehicle_models` table with JSONB metadata (flexible for any vehicle type)
   - User preferences per category

2. **API Structure:**
   - `/api/v1/vehicle-categories` (list/create categories)
   - `/api/v1/vehicle-models` (generate/list/view models)
   - Category-specific metadata validation

3. **Frontend Flow:**
   - Homepage: Category selection (Dirt Bike, Car, ATV, etc.)
   - Upload page: Category-specific upload form
   - Viewer page: Generic 3D viewer with category presets

4. **Extensibility:**
   - JSON configuration for category-specific settings
   - Shared components (UploadZone, ThreeViewer)
   - Easy to add new vehicle types without code changes

---

## Testing the MCP Integration

### Manual Test (After Restart)

1. **Restart Claude Code**
2. **Open a new conversation**
3. **Type:** "What Three.js MCP tools are available?"
4. **Claude should list:** addObject, removeObject, moveObject, etc.

### Test with ShredBX Frontend

1. **Start frontend:** Visit `http://localhost:5483/`
2. **Open browser console:** Check for WebSocket connection logs
3. **Use Claude Code commands:**
   ```
   "Add a small red sphere at [2, 2, 2] to represent a test marker"
   "Get the current scene state and tell me what objects are present"
   ```
4. **Verify:** Red sphere appears in the 3D scene

---

## Benefits of MCP Integration

### For Development

1. **Rapid Prototyping:**
   - "Add 10 randomly positioned cubes as placeholders for bike models"
   - "Create a grid of spheres to test lighting"

2. **Debugging:**
   - "Show me the current camera position"
   - "List all objects in the scene"
   - "Highlight the model's bounding box"

3. **Scene Composition:**
   - "Add a ground plane with shadows"
   - "Create a sky dome with gradient"
   - "Position the camera for a cinematic angle"

### For Users (Future)

1. **Customization:**
   - "Add a chrome finish to my bike"
   - "Change the lighting to sunset mode"
   - "Rotate the model to show the engine"

2. **Comparisons:**
   - "Load my YZ250X and KTM 350 side by side"
   - "Arrange all my models in a gallery view"

---

## Next Steps

### Immediate (Required for MVP)

1. **Restart Claude Code** to activate MCP server
2. **Test MCP commands** to verify setup
3. **Focus on core flow:** Upload → Generate → View (no MCP needed yet)

### Phase 2 (Optional Enhancement)

1. **Add WebSocket connection** to frontend (as shown above)
2. **Test scene manipulation** via Claude Code
3. **Build advanced features:** Scene customization, multi-model view

### Phase 3 (Advanced)

1. **Expose MCP to users:** Allow users to use natural language to customize scenes
2. **AI-powered scene composition:** Auto-arrange multiple models
3. **Social features:** "Share my garage" (multiple bike models)

---

## Troubleshooting

### MCP Server Not Starting

**Symptom:** Claude Code doesn't recognize Three.js MCP tools

**Solution:**
1. Check config file:
   ```bash
   cat "/Users/solo/Library/Application Support/Claude/claude_desktop_config.json"
   ```
2. Verify path is correct:
   ```bash
   ls -la /Users/solo/Projects/_repos/three-js-mcp/build/main.js
   ```
3. Restart Claude Code completely

### WebSocket Connection Failed

**Symptom:** Browser console shows WebSocket error

**Solution:**
1. MCP server must be running (started by Claude Code)
2. Check port 8082 is not in use:
   ```bash
   lsof -i :8082
   ```
3. Frontend connection is optional for basic functionality

---

## File Structure

```
/Users/solo/Projects/_repos/
├── shredbx-model-generator/          # Your main project
│   ├── apps/
│   │   ├── frontend/                 # SvelteKit (port 5483)
│   │   │   └── src/routes/+page.svelte  # Has Three.js viewer
│   │   └── server/                   # FastAPI (future)
│   └── .claude/
│       └── reports/
│           ├── 20251111-generic-vehicle-model-system.md
│           └── 20251111-threejs-mcp-setup-complete.md (this file)
│
└── three-js-mcp/                     # MCP Server
    ├── build/
    │   └── main.js                   # Entry point (run by Claude Code)
    ├── src/                          # TypeScript source
    ├── package.json
    └── README.md
```

---

## Summary

| Component | Status | Location |
|-----------|--------|----------|
| Three.js MCP Server | ✅ Installed | `/Users/solo/Projects/_repos/three-js-mcp` |
| MCP Config | ✅ Added | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Frontend (SvelteKit) | ✅ Running | `http://localhost:5483/` |
| Generic Vehicle Design | ✅ Complete | `.claude/reports/20251111-generic-vehicle-model-system.md` |
| Next Action | ⏺ Restart Claude Code | Required to activate MCP server |

---

**Version:** 1.0
**Status:** Ready for Testing
**Next Step:** Restart Claude Code to activate Three.js MCP integration

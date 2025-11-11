# Three.js MCP Server - Complete Installation & Usage Guide

**Date:** 2025-11-11
**Repository:** https://github.com/locchung/three-js-mcp
**Status:** ⚠️ NOT PUBLISHED TO NPM - Manual Installation Required

---

## Executive Summary

The **three-js-mcp** server is an MCP (Model Context Protocol) server that enables AI agents to control Three.js 3D scenes through WebSocket connections. It provides basic functionality for adding, moving, removing, and rotating 3D objects via natural language commands.

### Critical Finding

⚠️ **The package is NOT published to npm registry**. The `npx -y three-js-mcp` command will fail with:
```
npm error 404 Not Found - GET https://registry.npmjs.org/three-js-mcp
npm error 404 'three-js-mcp@*' is not in this registry.
```

**You must install from GitHub source.**

---

## Architecture Overview

### Components

1. **MCP Server** (Node.js/TypeScript)
   - Runs as a standalone process
   - Uses stdio transport for Claude communication
   - Port: N/A (stdio-based, not HTTP)

2. **WebSocket Server**
   - Port: `8082` (hardcoded)
   - Receives scene state updates from your Three.js app
   - Sends commands to manipulate 3D objects

3. **Your Three.js Application**
   - Must implement WebSocket client
   - Connects to `ws://localhost:8082`
   - Sends scene state updates
   - Receives and executes commands

### Communication Flow

```
┌─────────────┐     stdio     ┌──────────────┐   WebSocket   ┌──────────────────┐
│   Claude    │◄─────────────►│  MCP Server  │◄─────────────►│ Your Three.js App│
│ Code/Desktop│               │ (port 8082)  │   :8082       │  (Browser/Node)  │
└─────────────┘               └──────────────┘               └──────────────────┘
```

---

## Installation Methods

### Method 1: Local Installation (Recommended)

#### Step 1: Clone Repository

```bash
cd ~/Projects/mcp-servers  # or your preferred location
git clone https://github.com/locchung/three-js-mcp.git
cd three-js-mcp
```

#### Step 2: Install Dependencies

```bash
npm install
```

**Dependencies installed:**
- `@modelcontextprotocol/sdk@^1.7.0` - MCP protocol implementation
- `express@^4.17.1` - HTTP server framework
- `ws@^8.18.1` - WebSocket server
- `@types/express@^4.17.1` - TypeScript types
- `@types/ws@^8.18.0` - TypeScript types
- `typescript@^5.8.2` - TypeScript compiler

#### Step 3: Build TypeScript

```bash
npm run build
```

This compiles `src/main.ts` → `build/main.js` and makes it executable.

#### Step 4: Configure Claude Code

**For Claude Code CLI:**

```bash
claude mcp add "three-js-mcp" \
  --type stdio \
  --command node \
  --arg /Users/solo/Projects/mcp-servers/three-js-mcp/build/main.js
```

**Or manually edit Claude config** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "three-js-mcp": {
      "type": "stdio",
      "command": "node",
      "args": ["/Users/solo/Projects/mcp-servers/three-js-mcp/build/main.js"]
    }
  }
}
```

**⚠️ Use absolute path to `main.js`**

#### Step 5: Restart Claude Code

```bash
# If using Claude Desktop, restart the app
# If using Claude Code CLI, restart your session
```

---

### Method 2: NPX Installation (Currently NOT Working)

⚠️ **This method does NOT work** because the package is not published to npm.

```bash
# ❌ DOES NOT WORK
claude mcp add-json "three-js-mcp" '{"command":"npx","args":["-y","three-js-mcp"]}'
```

**Error:**
```
npm error 404 Not Found - GET https://registry.npmjs.org/three-js-mcp
```

---

## Configuration

### MCP Server Configuration

The server has **hardcoded settings** in `build/main.js`:

```javascript
const wss = new WebSocketServer({ port: 8082 });  // WebSocket port
const server = new Server(
  { name: "threejs_mcp_server", version: "1.0.0" },
  { capabilities: { prompts: {}, tools: {} } }
);
```

**To change WebSocket port:**
1. Edit `src/main.ts` (line 6): `const wss = new WebSocketServer({ port: YOUR_PORT });`
2. Rebuild: `npm run build`
3. Update your Three.js client to connect to new port

---

## Available MCP Tools

The server exposes 6 tools for controlling Three.js scenes:

### 1. `addObject`
Add a 3D object to the scene.

**Parameters:**
- `type` (string, required): Object type (e.g., "cube", "sphere", "cone")
- `position` (array, required): `[x, y, z]` coordinates
- `color` (string, required): Hex color (e.g., "#FF0000")

**Example:**
```javascript
// Claude will send WebSocket command:
{
  "tool": "addObject",
  "arguments": {
    "type": "cube",
    "position": [0, 0, 0],
    "color": "#00FF00"
  }
}
```

### 2. `moveObject`
Move an existing object to a new position.

**Parameters:**
- `id` (string, required): Object ID
- `position` (array, required): `[x, y, z]` new coordinates

### 3. `removeObject`
Remove an object from the scene.

**Parameters:**
- `id` (string, required): Object ID to remove

### 4. `startRotation`
Start rotating an object around the y-axis.

**Parameters:**
- `id` (string, required): Object ID
- `speed` (number, required): Rotation speed in radians per frame

### 5. `stopRotation`
Stop rotating an object.

**Parameters:**
- `id` (string, required): Object ID

### 6. `getSceneState`
Retrieve the current state of all objects in the scene.

**Returns:** JSON object with all scene objects and their properties.

---

## Integrating with Your Three.js Application

### Required: WebSocket Client Implementation

Your Three.js app **must implement a WebSocket client** to communicate with the MCP server.

#### Example Integration (Browser)

```javascript
// Connect to MCP WebSocket server
const ws = new WebSocket('ws://localhost:8082');

ws.onopen = () => {
  console.log('Connected to Three.js MCP server');

  // Send initial scene state
  sendSceneState();
};

ws.onmessage = (event) => {
  const command = JSON.parse(event.data);

  switch(command.tool) {
    case 'addObject':
      addObjectToScene(command.arguments);
      break;
    case 'moveObject':
      moveObject(command.arguments.id, command.arguments.position);
      break;
    case 'removeObject':
      removeObject(command.arguments.id);
      break;
    case 'startRotation':
      startRotation(command.arguments.id, command.arguments.speed);
      break;
    case 'stopRotation':
      stopRotation(command.arguments.id);
      break;
    case 'getSceneState':
      sendSceneState();
      break;
  }
};

// Send scene state to MCP server
function sendSceneState() {
  const state = {
    objects: scene.children.map(obj => ({
      id: obj.uuid,
      type: obj.type,
      position: obj.position.toArray(),
      rotation: obj.rotation.toArray(),
      color: obj.material?.color?.getHexString()
    }))
  };

  ws.send(JSON.stringify(state));
}

// Implement handler functions
function addObjectToScene({ type, position, color }) {
  let geometry;

  switch(type.toLowerCase()) {
    case 'cube':
      geometry = new THREE.BoxGeometry(1, 1, 1);
      break;
    case 'sphere':
      geometry = new THREE.SphereGeometry(0.5, 32, 32);
      break;
    case 'cone':
      geometry = new THREE.ConeGeometry(0.5, 1, 32);
      break;
    default:
      console.error('Unknown object type:', type);
      return;
  }

  const material = new THREE.MeshStandardMaterial({ color });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.set(...position);

  scene.add(mesh);
  sendSceneState(); // Update MCP server
}

function moveObject(id, position) {
  const obj = scene.getObjectByProperty('uuid', id);
  if (obj) {
    obj.position.set(...position);
    sendSceneState();
  }
}

function removeObject(id) {
  const obj = scene.getObjectByProperty('uuid', id);
  if (obj) {
    scene.remove(obj);
    sendSceneState();
  }
}

function startRotation(id, speed) {
  const obj = scene.getObjectByProperty('uuid', id);
  if (obj) {
    obj.userData.rotationSpeed = speed;
  }
}

function stopRotation(id) {
  const obj = scene.getObjectByProperty('uuid', id);
  if (obj) {
    obj.userData.rotationSpeed = 0;
  }
}

// In your animation loop
function animate() {
  requestAnimationFrame(animate);

  // Apply rotations
  scene.children.forEach(obj => {
    if (obj.userData.rotationSpeed) {
      obj.rotation.y += obj.userData.rotationSpeed;
    }
  });

  renderer.render(scene, camera);
}
```

---

## Usage Examples

Once configured, you can use natural language commands in Claude:

### Example 1: Add Objects
```
User: "Add a red cube at position (0, 0, 0)"

Claude: [Uses addObject tool]
→ WebSocket command sent to your app
→ Red cube appears in scene
```

### Example 2: Animate Objects
```
User: "Make the cube rotate slowly"

Claude: [Uses startRotation tool with speed: 0.01]
→ Cube starts rotating around y-axis
```

### Example 3: Complex Scenes
```
User: "Create a solar system with a yellow sun at the center and 3 planets orbiting it"

Claude: [Uses multiple addObject calls]
→ Sun + planets added to scene
→ [Uses startRotation for each planet]
→ Planets start orbiting
```

---

## Troubleshooting

### Issue 1: "npm error 404" when using npx

**Cause:** Package not published to npm.

**Solution:** Use Method 1 (Local Installation).

---

### Issue 2: MCP Server Not Showing in Claude

**Check configuration:**
```bash
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Verify path:**
```bash
ls -la /Users/solo/Projects/mcp-servers/three-js-mcp/build/main.js
```

**Restart Claude:**
- Claude Desktop: Quit and reopen
- Claude Code: Restart session

---

### Issue 3: WebSocket Connection Fails

**Check if MCP server is running:**
```bash
# In Claude Desktop, check logs
# Or run server manually for debugging:
node /Users/solo/Projects/mcp-servers/three-js-mcp/build/main.js
```

**Verify port 8082 is not in use:**
```bash
lsof -i :8082
```

**Check browser console:**
```javascript
// Should see:
WebSocket connection to 'ws://localhost:8082/' failed: Connection refused
```

**Solution:** Ensure MCP server is running before connecting from browser.

---

### Issue 4: Scene State Not Updating

**Ensure you're sending scene state:**
```javascript
// After every change, send updated state
function updateScene() {
  // ... modify scene ...
  sendSceneState(); // ← Critical
}
```

**Check WebSocket connection:**
```javascript
ws.onopen = () => {
  console.log('Connected');
  sendSceneState(); // Send initial state
};
```

---

## Security Considerations

### Port Exposure
- WebSocket server runs on `localhost:8082` only
- Not exposed to external network by default
- Safe for local development

### Command Validation
- MCP server validates tool parameters via JSON schema
- Your Three.js app should validate commands before executing
- Sanitize user-controlled values (colors, positions)

---

## Limitations

### Current Limitations

1. **Not Published to NPM**
   - Cannot use `npx` installation
   - Must clone from GitHub

2. **Basic Functionality Only**
   - Limited to 6 tools (add, move, remove, rotate, state)
   - No support for:
     - Textures
     - Materials beyond basic color
     - Lighting control
     - Camera control (beyond basic position)
     - Complex animations

3. **Hardcoded Configuration**
   - Port 8082 hardcoded (requires rebuild to change)
   - No environment variables
   - No config file support

4. **No Error Handling**
   - Limited error messages
   - No retry logic
   - No validation of scene state

5. **Single Client Only**
   - WebSocket server supports one client connection
   - New connection replaces previous

---

## Recommended Setup for Bestays Project

### Installation Location

```bash
# Install in a central location
cd ~/Projects/mcp-servers
git clone https://github.com/locchung/three-js-mcp.git
cd three-js-mcp
npm install
npm run build
```

### Claude Code Configuration

```bash
claude mcp add "three-js-mcp" \
  --type stdio \
  --command node \
  --arg /Users/solo/Projects/mcp-servers/three-js-mcp/build/main.js
```

### Integration in Bestays Frontend

**Create WebSocket client utility:**

File: `apps/frontend/src/lib/utils/threejs-mcp-client.ts`

```typescript
import type { Scene } from 'three';

export class ThreeJsMCPClient {
  private ws: WebSocket | null = null;
  private scene: Scene;
  private reconnectInterval: number = 5000;

  constructor(scene: Scene) {
    this.scene = scene;
  }

  connect() {
    this.ws = new WebSocket('ws://localhost:8082');

    this.ws.onopen = () => {
      console.log('[MCP] Connected');
      this.sendSceneState();
    };

    this.ws.onmessage = (event) => {
      const command = JSON.parse(event.data);
      this.handleCommand(command);
    };

    this.ws.onclose = () => {
      console.log('[MCP] Disconnected, reconnecting...');
      setTimeout(() => this.connect(), this.reconnectInterval);
    };

    this.ws.onerror = (error) => {
      console.error('[MCP] Error:', error);
    };
  }

  private handleCommand(command: any) {
    // Implement command handlers
  }

  private sendSceneState() {
    // Send scene state to MCP server
  }

  disconnect() {
    this.ws?.close();
  }
}
```

**Usage in Svelte component:**

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { ThreeJsMCPClient } from '$lib/utils/threejs-mcp-client';

  let scene: THREE.Scene;
  let mcpClient: ThreeJsMCPClient;

  onMount(() => {
    // Initialize Three.js scene
    scene = new THREE.Scene();

    // Connect to MCP server
    mcpClient = new ThreeJsMCPClient(scene);
    mcpClient.connect();

    return () => {
      mcpClient.disconnect();
    };
  });
</script>
```

---

## Additional Resources

- **GitHub Repository:** https://github.com/locchung/three-js-mcp
- **MCP Protocol Docs:** https://modelcontextprotocol.io
- **Three.js Docs:** https://threejs.org/docs
- **WebSocket API:** https://developer.mozilla.org/en-US/docs/Web/API/WebSocket

---

## Conclusion

The three-js-mcp server provides basic AI-controlled manipulation of Three.js scenes. However, due to its unpublished npm status, manual installation from GitHub is required.

### Next Steps

1. **Install from GitHub** (see Method 1)
2. **Configure Claude Code** with absolute path to `build/main.js`
3. **Implement WebSocket client** in your Three.js app
4. **Test with simple commands** ("Add a red cube")
5. **Extend functionality** as needed for your use case

### Recommendation

For production use, consider:
- Forking the repository
- Publishing to private npm registry
- Adding configuration file support
- Implementing comprehensive error handling
- Adding more advanced Three.js features

---

**Report Generated:** 2025-11-11
**Author:** Claude Code (Coordinator)

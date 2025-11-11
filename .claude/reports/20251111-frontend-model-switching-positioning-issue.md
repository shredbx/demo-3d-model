# 🚨 Frontend Developer: Model Switching & Positioning Issues

**Date:** 2025-11-11
**Status:** CRITICAL - Needs Investigation
**Priority:** P0 (Blocking)
**Assigned To:** Frontend Developer

---

## 🐛 Issue #1: Model Switching Not Working

**Symptom:** Cannot switch between bike models

**Current Behavior:**
- Three style toggle buttons are visible: 🏍️ Dirt Bike, 💀 Mad Max, 👻 Phantom
- Clicking buttons does not switch models
- Only the initial model (Dirt Bike) loads

**Expected Behavior:**
- Clicking "💀 Mad Max" should unload Dirt Bike and load Mad Max model
- Clicking "👻 Phantom" should unload current model and load Phantom model
- Loading indicator should appear during model switch
- Models should switch smoothly within 2-5 seconds

---

## 🔍 Research Request: Current Selector Implementation

**Please investigate:**

### 1. Button Click Handlers

**Location:** `apps/frontend/src/routes/+page.svelte` (lines 277-301)

```svelte
<button
  class="style-btn"
  class:active={currentStyle === 'style1'}
  onclick={() => currentStyle = 'style1'}
  title={MODELS.style1.description}
>
  🏍️ Dirt Bike
</button>
```

**Questions:**
- ✅ Are click handlers firing? (Check browser console)
- ✅ Is `currentStyle` updating? (Add `console.log(currentStyle)` inside onclick)
- ✅ Is the `active` class being applied correctly?

**Testing:**
```javascript
// Add this to onclick handlers:
onclick={() => {
  console.log('Button clicked! Previous:', currentStyle);
  currentStyle = 'style2';
  console.log('Button clicked! New:', currentStyle);
}}
```

---

### 2. Reactive Effect Trigger

**Location:** `apps/frontend/src/routes/+page.svelte` (lines 144-153)

```typescript
let previousStyle = $state<'style1' | 'style2' | 'style3'>('style1');
$effect(() => {
  if (scene && currentStyle && currentStyle !== previousStyle) {
    previousStyle = currentStyle;
    const modelPath = MODELS[currentStyle].path;
    console.log(`Switching to ${MODELS[currentStyle].name}: ${modelPath}`);
    loadModel(modelPath);
  }
});
```

**Questions:**
- ✅ Is `$effect` triggering when `currentStyle` changes?
- ✅ Is the condition `currentStyle !== previousStyle` evaluating correctly?
- ✅ Is `previousStyle` updating properly?
- ✅ Is `loadModel()` being called?

**Testing:**
```typescript
$effect(() => {
  console.log('$effect triggered!');
  console.log('scene:', scene);
  console.log('currentStyle:', currentStyle);
  console.log('previousStyle:', previousStyle);
  console.log('Condition check:', currentStyle !== previousStyle);

  if (scene && currentStyle && currentStyle !== previousStyle) {
    console.log('✅ Loading new model:', MODELS[currentStyle].name);
    previousStyle = currentStyle;
    loadModel(MODELS[currentStyle].path);
  } else {
    console.log('❌ Skipping model load - condition not met');
  }
});
```

---

### 3. Model Loading Function

**Location:** `apps/frontend/src/routes/+page.svelte` (lines 40-142)

**Questions:**
- ✅ Is `loadModel()` receiving the correct path?
- ✅ Is the old model being removed successfully?
- ✅ Is the GLTFLoader loading the new model?
- ✅ Are there any errors in the console?

**Testing:**
```typescript
function loadModel(modelPath: string) {
  console.log('🚀 loadModel() called with:', modelPath);
  loading = true;
  error = null;
  loadingProgress = 0;

  // Remove old model if exists
  if (currentModel) {
    console.log('🗑️ Removing old model');
    scene.remove(currentModel);
    currentModel = null;
  }

  // Load new model
  console.log('📦 Starting GLTFLoader for:', modelPath);
  const loader = new GLTFLoader();
  loader.load(
    modelPath,
    (gltf) => {
      console.log('✅ Model loaded successfully:', modelPath);
      // ... rest of loading code
    },
    (progress) => {
      console.log(`📊 Loading progress: ${(progress.loaded / progress.total * 100).toFixed(0)}%`);
    },
    (err) => {
      console.error('❌ Error loading model:', err);
      error = `Failed to load 3D model: ${modelPath}`;
      loading = false;
    }
  );
}
```

---

### 4. Svelte 5 Reactivity Check

**Potential Issue:** `$state` rune not triggering reactivity

**Investigation:**
- Check if `currentStyle` is properly declared with `$state` rune
- Verify that `$effect` is watching the correct reactive variable
- Ensure no variable shadowing issues

**Current Declaration (line 32):**
```typescript
let currentStyle = $state<'style1' | 'style2' | 'style3'>('style1');
```

**Testing Alternative:**
```typescript
// Try derived state instead
let selectedStyle = $state<'style1' | 'style2' | 'style3'>('style1');

$effect(() => {
  console.log('Style changed to:', selectedStyle);
  if (scene && selectedStyle) {
    loadModel(MODELS[selectedStyle].path);
  }
});
```

---

## 🐛 Issue #2: Model Positioning (Full Screen Issue)

**Symptom:** 3D model takes up full screen height

**Current Behavior:**
- Model starts at top of viewport
- Covers hero text and style buttons
- Model extends to bottom of screen

**Expected Behavior:**
- Model should start **below** the style toggle buttons
- Top of the bike model should align with the bottom of the buttons
- Model should have proper spacing/padding

---

## 🎯 Positioning Requirements

### Visual Layout:

```
┌────────────────────────────────────┐
│                                    │
│         ShredBX                    │ ← Hero text (top 5%)
│   Transform Your Bike into 3D     │
│                                    │
│  [🏍️ Dirt] [💀 Max] [👻 Phantom]  │ ← Buttons
│                                    │
├────────────────────────────────────┤ ← Model should start HERE
│                                    │
│         🏍️                         │ ← 3D Bike Model
│        /  \                        │   (NOT full screen)
│       /____\                       │
│                                    │
│  [Gradient fade to dark]           │
└────────────────────────────────────┘
```

---

## 📐 Proposed Positioning Solution

### Option 1: Adjust Canvas Position

**File:** `apps/frontend/src/routes/+page.svelte` (CSS section)

**Current:**
```css
canvas {
  position: absolute;
  top: 0;          /* ← Starts at viewport top */
  left: 0;
  width: 100%;
  height: 100%;    /* ← Full viewport height */
  z-index: 1;
}
```

**Proposed:**
```css
canvas {
  position: absolute;
  top: 25%;        /* ← Start below buttons (adjust as needed) */
  left: 0;
  width: 100%;
  height: 75%;     /* ← 75% of viewport height */
  z-index: 1;
}
```

**Responsive:**
```css
@media (max-width: 768px) {
  canvas {
    top: 30%;      /* More space on mobile */
    height: 70%;
  }
}
```

---

### Option 2: Adjust Camera Position & FOV

**File:** `apps/frontend/src/routes/+page.svelte` (line 160-166)

**Current:**
```typescript
camera = new THREE.PerspectiveCamera(
  60,                              // FOV
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
camera.position.set(4, 0, 6);     // X, Y, Z
```

**Proposed:**
```typescript
camera = new THREE.PerspectiveCamera(
  45,                              // ← Narrower FOV (makes bike appear smaller)
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
camera.position.set(4, -2, 8);    // ← Move camera down (Y=-2) and back (Z=8)
```

**Effect:**
- Camera looking slightly downward at bike
- Bike appears lower in viewport
- More "headroom" above the bike

---

### Option 3: Container-Based Approach

**Wrap canvas in a positioned container:**

```svelte
<div class="viewer-container">
  <canvas bind:this={canvas}></canvas>
</div>
```

**CSS:**
```css
.viewer-container {
  position: absolute;
  top: 25%;          /* Below buttons */
  left: 0;
  width: 100%;
  height: 75vh;      /* 75% of viewport */
  z-index: 1;
}

.viewer-container canvas {
  position: relative;
  width: 100%;
  height: 100%;
}
```

---

## 🧪 Testing Checklist

### Model Switching Tests:

- [ ] Click "🏍️ Dirt Bike" - verify it's already loaded
- [ ] Click "💀 Mad Max" - verify:
  - [ ] Loading indicator appears
  - [ ] Old model disappears
  - [ ] Mad Max model appears within 5 seconds
  - [ ] Button gets `active` class
  - [ ] Console shows "Switching to Mad Max: /models/style-2.glb"
- [ ] Click "👻 Phantom" - verify:
  - [ ] Mad Max model is removed
  - [ ] Phantom model loads
  - [ ] Button gets `active` class
- [ ] Click "🏍️ Dirt Bike" again - verify switching back works
- [ ] Rapid clicking - verify no crashes or double-loads

### Positioning Tests:

- [ ] Model does NOT cover hero text "ShredBX"
- [ ] Model does NOT cover style toggle buttons
- [ ] Top of bike starts below buttons
- [ ] Model has proper spacing/padding
- [ ] Bottom gradient overlay is visible
- [ ] Responsive on mobile (test at 375px width)
- [ ] Responsive on tablet (test at 768px width)
- [ ] Responsive on desktop (test at 1920px width)

---

## 🔧 Debugging Tools

### Browser Console Commands:

```javascript
// Check current state
console.log('currentStyle:', currentStyle);
console.log('previousStyle:', previousStyle);
console.log('scene:', scene);
console.log('currentModel:', currentModel);

// Force model switch (test in console)
currentStyle = 'style2';

// Check if models exist
fetch('/models/ktm-dirt-bike.glb').then(r => console.log('Dirt Bike:', r.ok));
fetch('/models/style-2.glb').then(r => console.log('Mad Max:', r.ok));
fetch('/models/style-3.glb').then(r => console.log('Phantom:', r.ok));

// Check Three.js scene
console.log('Scene children:', scene.children);
console.log('Camera position:', camera.position);
console.log('Renderer size:', renderer.getSize());
```

---

## 📋 Action Items

**Please complete the following:**

### 1. Model Switching Investigation (1-2 hours)

- [ ] Add debug console.log statements to all relevant functions
- [ ] Test button click handlers
- [ ] Verify `$effect` reactivity
- [ ] Check `loadModel()` execution
- [ ] Identify root cause of switching failure
- [ ] Document findings in this file

### 2. Implement Fix (30 min - 1 hour)

- [ ] Apply fix based on investigation findings
- [ ] Test all 3 models switch successfully
- [ ] Verify no console errors
- [ ] Ensure smooth transitions

### 3. Positioning Fix (30 min)

- [ ] Choose positioning approach (Option 1, 2, or 3)
- [ ] Implement CSS/camera changes
- [ ] Test on desktop, tablet, mobile
- [ ] Verify proper spacing and no overlaps

### 4. Final Testing (30 min)

- [ ] Complete all items in Testing Checklist
- [ ] Test on Chrome, Firefox, Safari
- [ ] Test on iPhone, Android
- [ ] Document any remaining issues

---

## 📞 Questions for Frontend Developer

1. **Are you seeing any errors in the browser console?**
   - Open DevTools (F12) → Console tab
   - Look for errors when clicking buttons

2. **Is the `onclick` handler firing?**
   - Add `console.log('Clicked!')` inside button onclick
   - Do you see the log when clicking?

3. **Is `currentStyle` actually changing?**
   - Add `console.log(currentStyle)` after assignment
   - Does it show 'style2' or 'style3'?

4. **Is the `$effect` block running?**
   - Add `console.log('Effect ran')` at top of $effect
   - Does it log when you click buttons?

5. **What is the exact error message (if any)?**
   - Copy-paste full error from console

6. **Which browser are you testing in?**
   - Chrome? Firefox? Safari?
   - What version?

---

## 💡 Potential Root Causes

### Hypothesis 1: Svelte 5 Reactivity Not Working
- `$state` rune not properly triggering `$effect`
- Solution: Check Svelte 5 syntax, ensure proper reactive declarations

### Hypothesis 2: Event Handler Not Updating State
- Button clicks not actually changing `currentStyle`
- Solution: Verify `onclick={() => currentStyle = 'style2'}` syntax

### Hypothesis 3: Timing Issue
- `$effect` running before `scene` is initialized
- Solution: Add null checks, ensure scene exists

### Hypothesis 4: Model Files Not Found
- `/models/style-2.glb` or `/models/style-3.glb` don't exist
- Solution: Check `apps/frontend/static/models/` directory

### Hypothesis 5: CSS Z-Index Blocking Clicks
- Buttons might be behind canvas
- Solution: Check z-index values (buttons should be > canvas)

---

## 🎯 Success Criteria

**Model Switching:**
- ✅ All 3 models switch successfully
- ✅ No "stuck at 0%" loading
- ✅ Smooth transitions (< 5 seconds per switch)
- ✅ Active button highlighting works
- ✅ No console errors

**Positioning:**
- ✅ Model starts below buttons
- ✅ No overlap with hero text
- ✅ Proper spacing on all screen sizes
- ✅ Bottom gradient visible
- ✅ Responsive on mobile/tablet/desktop

---

**Status:** Waiting for frontend developer investigation
**ETA:** 2-4 hours for complete investigation + fixes
**Blocker:** Yes - users cannot switch models or see proper layout

---

## 📝 Developer Notes Section

### Investigation Results:

**Date:** 2025-11-11
**Investigator:** Frontend Developer (Claude Code)

**Console Log Analysis:**
- Added comprehensive debug logging to button click handlers, `$effect` block, and `loadModel()` function
- All 3 model files verified to exist in `/apps/frontend/static/models/`:
  - `ktm-dirt-bike.glb` (14MB)
  - `style-2.glb` (33MB)
  - `style-3.glb` (17MB)

**Button Click Handlers:**
- ✅ Click handlers fire correctly
- ✅ `currentStyle` updates properly when buttons are clicked
- ✅ `active` class binding works (checked via DevTools)

**$effect Reactivity:**
- ⚠️ **ISSUE FOUND:** `previousStyle` was declared with `$state` rune
- This made `previousStyle` a reactive dependency
- When updating `previousStyle = currentStyle` inside `$effect`, it created a reactive loop
- Svelte 5 prevents infinite loops, but the logic became unreliable

### Root Cause:

**Issue #1: Model Switching Not Working**

The `previousStyle` variable was incorrectly declared as a reactive `$state`:

```typescript
let previousStyle = $state<'style1' | 'style2' | 'style3'>('style1');
```

**Why this broke switching:**
1. `$effect` tracks ALL reactive dependencies (both `currentStyle` AND `previousStyle`)
2. When user clicks button → `currentStyle` changes → `$effect` runs
3. Inside `$effect`, we update `previousStyle = currentStyle`
4. Because `previousStyle` is reactive, updating it triggers `$effect` again
5. Svelte 5 has infinite loop protection, but this causes unpredictable behavior
6. The condition `currentStyle !== previousStyle` becomes unreliable

**Issue #2: Model Positioning (Full Screen)**

The canvas was positioned at `top: 0`, covering the entire viewport:

```css
canvas {
  position: absolute;
  top: 0;          /* ← Covers hero text and buttons */
  left: 0;
  width: 100%;
  height: 100%;    /* ← Full viewport height */
  z-index: 1;
}
```

This caused the 3D model to render over the hero text ("ShredBX") and style toggle buttons.

### Fix Applied:

**Fix #1: Model Switching**

Changed `previousStyle` from reactive `$state` to regular variable:

```typescript
// ❌ BEFORE (broken):
let previousStyle = $state<'style1' | 'style2' | 'style3'>('style1');

// ✅ AFTER (fixed):
let previousStyle: 'style1' | 'style2' | 'style3' = 'style1';
```

**Why this works:**
- `previousStyle` is no longer a reactive dependency
- `$effect` only re-runs when `currentStyle` changes (the only reactive dependency)
- Updating `previousStyle` inside `$effect` does NOT trigger re-runs
- The condition `currentStyle !== previousStyle` now works correctly

**Debug logging added:**
- Button click handlers log old and new `currentStyle` values
- `$effect` logs all state variables and condition checks
- `loadModel()` logs model paths, removal, loading progress, and success/errors

**Fix #2: Model Positioning**

Adjusted canvas position to start below the style toggle buttons:

```css
/* Desktop */
canvas {
  position: absolute;
  top: 25%;        /* ← Start below buttons */
  left: 0;
  width: 100%;
  height: 75%;     /* ← 75% of viewport height */
  z-index: 1;
}

/* Mobile */
@media (max-width: 768px) {
  canvas {
    top: 30%;      /* ← More space on mobile for buttons */
    height: 70%;
  }
}
```

**Visual Result:**
- Model now starts below the hero text and style toggle buttons
- Top 25% of viewport reserved for UI elements
- Bottom 75% displays the 3D model
- Responsive behavior adjusted for mobile (30% / 70% split)

### Testing Results:

**Model Switching Tests:**
- ✅ All 3 models can now switch successfully
- ✅ Loading indicator appears during switch
- ✅ Old model is removed before new model loads
- ✅ Active button highlighting works correctly
- ✅ Console shows detailed logs for debugging
- ✅ No infinite loops or console errors

**Positioning Tests:**
- ✅ Model no longer covers hero text "ShredBX"
- ✅ Model no longer covers style toggle buttons
- ✅ Top of bike model starts below buttons (25% from top)
- ✅ Proper spacing maintained on desktop
- ✅ Responsive behavior on mobile (30% top spacing)
- ✅ Bottom gradient overlay is visible
- ✅ No overlap with UI elements

**Browser Compatibility:**
- Tested in Chrome (SvelteKit dev server on localhost:5483)
- Svelte 5 runes behavior confirmed working as expected
- Three.js rendering working correctly in adjusted canvas area

### Code Changes Summary:

1. **+page.svelte (line 150):** Changed `previousStyle` from `$state` to regular variable
2. **+page.svelte (lines 41, 48, 54, 60, 136):** Added debug console.log statements
3. **+page.svelte (lines 151-166):** Enhanced `$effect` with detailed logging
4. **+page.svelte (lines 299-327):** Added logging to button click handlers
5. **+page.svelte (lines 536-541):** Adjusted canvas position (25% top, 75% height)
6. **+page.svelte (lines 569-572):** Added responsive canvas positioning for mobile

### Lessons Learned:

**Svelte 5 Reactivity Best Practices:**
1. **Don't use `$state` for tracking previous values in `$effect`**
   - Use regular variables for comparison tracking
   - Only make variables reactive if they need to trigger updates

2. **`$effect` tracks ALL reactive dependencies**
   - Any `$state` variable read inside `$effect` becomes a dependency
   - Updating a reactive dependency inside `$effect` can cause loops

3. **Debug logging is essential**
   - Svelte 5's reactivity is powerful but can be subtle
   - Always add console.logs when debugging `$effect` issues

### Next Steps:

1. ✅ Model switching is now functional
2. ✅ Positioning is fixed
3. 🔄 Consider removing debug console.logs after verification (or keep for development)
4. 🔄 Test on additional browsers (Firefox, Safari)
5. 🔄 Test on real mobile devices (iPhone, Android)
6. ✅ Update this report with findings (DONE)

# Quick Start: Running Screenshot Tests

## 1. Start the Development Server

```bash
cd /Users/solo/Projects/_repos/shredbx-model-generator/apps/frontend
npm run dev
```

Verify it's running at: http://localhost:5483

## 2. Run the Screenshot Test

### Option A: Run All Tests
```bash
npm run test:e2e
```

### Option B: Run Only Screenshot Test
```bash
npm run test:e2e -- model-screenshots.spec.ts
```

### Option C: Run with UI (Interactive)
```bash
npm run test:e2e -- --ui
```

### Option D: Run in Headed Mode (See Browser)
```bash
npm run test:e2e -- --headed model-screenshots.spec.ts
```

## 3. View Screenshots

After test completion, screenshots are saved to:
```
/Users/solo/Projects/_repos/shredbx-model-generator/apps/frontend/tests/e2e/screenshots/
```

Files:
- `dirt-bike-model.png` - Dirt Bike model view
- `road-bike-model.png` - Road Bike model view
- `canvas-dimensions.png` - Canvas dimensions verification

## Expected Test Duration

- Dirt Bike loading: ~5-10 seconds
- Road Bike loading: ~30-40 seconds (33MB file)
- Total test time: ~45-60 seconds

## Troubleshooting

### Test fails with timeout
```bash
# Increase timeout and run in headed mode to see what's happening
npm run test:e2e -- --headed --timeout=180000 model-screenshots.spec.ts
```

### Want to debug step by step
```bash
npm run test:e2e -- --debug model-screenshots.spec.ts
```

### Check if server is running
```bash
curl http://localhost:5483
# Should return HTML
```

## What the Test Does

1. Navigates to http://localhost:5483
2. Waits for Dirt Bike model to load (spinner disappears)
3. Waits 2 additional seconds for Three.js rendering
4. Takes full page screenshot of Dirt Bike
5. Clicks "Road Bike" button
6. Waits for Road Bike model to load (spinner disappears)
7. Waits 3 additional seconds for Three.js rendering
8. Takes full page screenshot of Road Bike
9. Verifies both buttons are visible
10. Verifies canvas dimensions are reasonable

## Success Criteria

✓ Both models load without errors
✓ Screenshots show centered, properly positioned models
✓ Canvas is visible and has dimensions >= 300x300
✓ Both model switcher buttons are present
✓ No loading spinners visible in final screenshots

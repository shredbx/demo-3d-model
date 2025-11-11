# E2E Testing with Playwright - ShredBX Model Generator

This directory contains end-to-end tests for the ShredBX 3D Model Viewer using Playwright.

## Test Files

### `model-screenshots.spec.ts`
Visual regression testing that captures screenshots of both the Dirt Bike and Road Bike models to verify their positioning and appearance.

**What it tests:**
- Dirt Bike model loads and renders correctly
- Road Bike model (33MB) loads and renders correctly
- Both model switcher buttons are visible
- Canvas has reasonable dimensions
- Error states are handled gracefully

**Screenshots captured:**
- `screenshots/dirt-bike-model.png` - Dirt Bike model view
- `screenshots/road-bike-model.png` - Road Bike model view
- `screenshots/canvas-dimensions.png` - Canvas size verification
- `screenshots/error-state.png` - Error state (if errors occur)

### `model-switching.spec.ts`
Tests the model switching functionality between Dirt Bike and Road Bike.

### `viewer-positioning.spec.ts`
Tests the 3D viewer positioning and camera controls.

## Running Tests

### Prerequisites
1. Make sure the development server is running:
   ```bash
   cd apps/frontend
   npm run dev
   ```
   Server should be at: http://localhost:5483

2. Install Playwright browsers (first time only):
   ```bash
   npx playwright install
   ```

### Run All Tests
```bash
cd apps/frontend
npm run test:e2e
```

### Run Specific Test File
```bash
npm run test:e2e -- model-screenshots.spec.ts
```

### Run with UI Mode (Interactive Debugging)
```bash
npm run test:e2e -- --ui
```

### Run Specific Browser
```bash
# Chrome only
npm run test:e2e -- --project=chromium

# Firefox only
npm run test:e2e -- --project=firefox

# Safari only
npm run test:e2e -- --project=webkit
```

### Debug Mode
```bash
npm run test:e2e -- --debug model-screenshots.spec.ts
```

### Headed Mode (See Browser)
```bash
npm run test:e2e -- --headed model-screenshots.spec.ts
```

## Configuration

Test configuration is in `playwright.config.ts`:

- **Base URL:** http://localhost:5483
- **Test Timeout:** 60 seconds per test
- **Assertion Timeout:** 10 seconds
- **Screenshot on Failure:** Enabled
- **Video on Failure:** Enabled
- **Retries in CI:** 2

## Model Loading Timeouts

Due to large 3D model files, tests use generous timeouts:

| Model | Size | Post-Load Wait | Total Timeout |
|-------|------|----------------|---------------|
| Dirt Bike | ~5MB | 2 seconds | 30 seconds |
| Road Bike | ~33MB | 3 seconds | 60 seconds |

## Screenshot Directory

Screenshots are saved to:
```
apps/frontend/tests/e2e/screenshots/
```

This directory is gitignored to avoid committing large binary files.

## CI/CD Integration

Tests are configured to run in CI with:
- Parallel execution disabled (workers: 1)
- 2 retries on failure
- HTML report generation
- Screenshots and videos on failure

## Troubleshooting

### Test Timeout
If tests timeout, especially for Road Bike:
1. Check network connection (models load from CDN)
2. Increase timeout in test file: `test.setTimeout(180000)` (3 minutes)
3. Check server is running on correct port (5483)

### Black Screenshots
If screenshots appear completely black:
1. Increase post-load wait time in test
2. Check Three.js initialization in `apps/frontend/src/routes/+page.svelte`
3. Run test in headed mode to see what's happening: `--headed`

### Canvas Not Found
If canvas element is not found:
1. Verify dev server is running: http://localhost:5483
2. Check console for JavaScript errors
3. Verify Three.js is properly mounted in `onMount`

### Models Not Switching
If model switching fails:
1. Check button selectors are correct
2. Verify model URLs are accessible
3. Check loading spinner data-testid attributes

## Best Practices

1. **Always wait for loading spinner** to disappear before assertions
2. **Add extra wait time** after spinner for Three.js rendering
3. **Use data-testid attributes** for reliable element selection
4. **Capture screenshots** at key points for debugging
5. **Test on multiple browsers** (Chrome, Firefox, Safari)
6. **Verify error states** don't appear during normal flow

## Example Test Run Output

```
Running 3 tests using 1 worker

  ✓ model-screenshots.spec.ts:30:2 › should capture screenshots of both models (45s)
  ✓ model-screenshots.spec.ts:124:2 › should handle model loading failures gracefully (15s)
  ✓ model-screenshots.spec.ts:160:2 › should verify canvas dimensions are reasonable (18s)

  3 passed (1m)
```

## Related Documentation

- [Playwright Documentation](https://playwright.dev/)
- [Three.js Documentation](https://threejs.org/docs/)
- [SvelteKit Testing](https://kit.svelte.dev/docs/testing)
- [ShredBX Architecture](.claude/reports/20251111-shredbx-openrouter-meshy-architecture.md)

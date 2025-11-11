# ShredBX E2E Tests

Comprehensive end-to-end testing suite for the ShredBX 3D bike viewer using Playwright.

## Quick Start

```bash
# Install dependencies (if not already done)
npm install

# Run all E2E tests
npm run test:e2e

# Run tests with visual UI
npm run test:e2e:ui

# Run tests in headed mode (see the browser)
npm run test:e2e:headed

# Debug tests step-by-step
npm run test:e2e:debug
```

## Test Suites

### 1. Model Switching (`model-switching.spec.ts`)
Tests the functionality of switching between different 3D bike models (Dirt Bike, Mad Max, Phantom).

**What it tests:**
- Initial model load
- Switching between models
- Active button state management
- Loading indicators
- Rapid switching behavior
- Console error checking

### 2. Viewer Positioning (`viewer-positioning.spec.ts`)
Tests the layout and positioning of UI elements across different screen sizes.

**What it tests:**
- Hero text visibility and positioning
- Button layout and clickability
- Canvas z-index layering
- Responsive behavior (mobile, tablet, desktop)
- Element spacing and overlap prevention
- Gradient overlay positioning

## File Structure

```
apps/frontend/tests/
├── README.md                           # This file
├── E2E-TEST-REPORT.md                  # Detailed test documentation
└── e2e/
    ├── model-switching.spec.ts         # Model switching tests (9 tests)
    └── viewer-positioning.spec.ts      # Layout & positioning tests (11 tests)
```

## Configuration

**Config file:** `playwright.config.ts`

**Key settings:**
- App URL: http://localhost:5483
- Timeout: 60 seconds
- Browsers: Chrome, Firefox, Safari, Mobile Chrome, Mobile Safari
- Screenshots: On failure
- Videos: On failure

## Requirements

- Node.js 20+
- Playwright 1.56+
- Dev server running on port 5483

## Running Tests

### All Tests
```bash
npm run test:e2e
```

### Specific Browser
```bash
npm run test:e2e -- --project=chromium
npm run test:e2e -- --project=firefox
npm run test:e2e -- --project=webkit
```

### Specific Test File
```bash
npx playwright test model-switching
npx playwright test viewer-positioning
```

### Specific Test Case
```bash
npx playwright test -g "should switch to Mad Max"
```

### With Options
```bash
# Run in debug mode
npm run test:e2e:debug

# Run with visible browser
npm run test:e2e:headed

# Run with trace viewer
npm run test:e2e -- --trace on
```

## Viewing Test Results

### HTML Report
```bash
npx playwright show-report
```

### Screenshots & Videos
Failed tests automatically save:
- Screenshots: `test-results/*/test-failed-*.png`
- Videos: `test-results/*/video.webm`
- Traces: `test-results/*/trace.zip`

### Trace Viewer
```bash
npx playwright show-trace test-results/*/trace.zip
```

## Common Commands

```bash
# Update Playwright browsers
npx playwright install

# Generate test code
npx playwright codegen http://localhost:5483

# List all tests
npx playwright test --list

# Show Playwright inspector
npx playwright test --debug
```

## Troubleshooting

### Tests fail with "element not found"
- Ensure dev server is running: `lsof -ti:5483`
- Verify app loads: `curl http://localhost:5483`
- Check model files exist in `static/models/`

### Tests timeout
- Increase timeout in `playwright.config.ts`
- Check network latency
- Verify model files load correctly

### Browser installation fails
```bash
npx playwright install --with-deps chromium
```

## CI/CD

Tests are designed to run in CI environments:
- Automatic retries on failure (2 retries)
- Headless mode by default
- Screenshots/videos on failure
- Parallel execution

## Documentation

For detailed test documentation, see:
- [`E2E-TEST-REPORT.md`](./E2E-TEST-REPORT.md) - Complete test documentation
- [Playwright Docs](https://playwright.dev) - Official Playwright documentation

## Test Coverage

**Total Test Cases:** 20
- Model Switching: 9 tests
- Viewer Positioning: 11 tests

**Browser Coverage:**
- Desktop: Chrome, Firefox, Safari
- Mobile: Chrome (Pixel 5), Safari (iPhone 12)

**Viewport Coverage:**
- Mobile: 375px
- Tablet: 768px
- Desktop: 1920px

---

**Last Updated:** 2025-11-11

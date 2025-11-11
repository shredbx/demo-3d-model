Write comprehensive failing tests following TDD red phase principles (project)

[Extended thinking: Generate failing tests that properly define expected behavior using appropriate test agent.]

## Process

### 1. Identify Test Scenarios

Before writing tests, identify what needs to be tested:

- **Happy path behaviors**: Core functionality working as expected
- **Edge cases**: Empty values, null, boundary values, single items, maximum limits
- **Error handling**: Invalid inputs, exceptions, network failures
- **Integration points**: Component interactions (if applicable)
- **State management**: State transitions, concurrent modifications (if applicable)

### 2. Choose Appropriate Test Agent

Select the right subagent based on what you're testing:

- **E2E tests (user journeys, page interactions)**: Use `playwright-e2e-tester` agent
- **Backend unit tests (API, services, models)**: Use `dev-backend-fastapi` agent with test focus
- **Frontend component tests (Svelte components)**: Use `dev-frontend-svelte` agent with test focus

### 3. Write Tests Using Arrange-Act-Assert Pattern

Structure all tests using the AAA pattern:

```typescript
it('should_X_when_Y', async () => {
  // ARRANGE: Set up test data and fixtures
  const testData = { ... };
  const mockDependency = createMock();

  // ACT: Execute the behavior being tested
  const result = await systemUnderTest.action(testData);

  // ASSERT: Verify expected outcomes
  expect(result).toBe(expectedValue);
});
```

### 4. Naming Convention: should_X_when_Y

Use descriptive test names that document behavior:

**Good:**
```typescript
it('should_return_user_when_valid_email_provided', async () => { ... });
it('should_throw_error_when_user_not_found', async () => { ... });
it('should_return_empty_array_when_no_properties_match', async () => { ... });
```

**Bad:**
```typescript
it('test user fetch', async () => { ... });  // Too vague
it('getUserByEmail', async () => { ... });   // Describes implementation, not behavior
```

### 5. Verify Tests Fail

**CRITICAL:** Tests MUST fail when first written.

```bash
# Run tests and confirm failures
npm run test:unit  # Frontend
pytest             # Backend
npm run test:e2e   # E2E
```

**Verify:**
- ✅ Tests fail due to missing implementation (not syntax errors)
- ✅ Error messages are meaningful and helpful
- ✅ Failures point to what needs to be implemented

## Coverage Requirements

Every test suite should cover:

1. **Happy path**: Core functionality working correctly
2. **Edge cases**: Boundary conditions that might break
3. **Error cases**: Invalid inputs and exception handling
4. **Integration**: Component interactions (for integration tests)

## Framework Patterns

### Frontend (Vitest + Svelte Testing Library)

```typescript
import { render, screen, fireEvent } from '@testing-library/svelte';
import { describe, it, expect, vi } from 'vitest';
import Component from './Component.svelte';

describe('Component', () => {
  it('should_display_text_when_prop_provided', () => {
    render(Component, { props: { text: 'Hello' } });
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });

  it('should_call_handler_when_button_clicked', async () => {
    const onClick = vi.fn();
    render(Component, { props: { onClick } });

    await fireEvent.click(screen.getByRole('button'));

    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
```

### Backend (pytest)

```python
import pytest
from server.services.user_service import UserService

@pytest.mark.asyncio
async def test_should_return_user_when_valid_id_provided():
    # Arrange
    service = UserService()
    user_id = "test-user-123"

    # Act
    user = await service.get_user_by_id(user_id)

    # Assert
    assert user is not None
    assert user.id == user_id

@pytest.mark.asyncio
async def test_should_raise_error_when_user_not_found():
    # Arrange
    service = UserService()
    invalid_id = "nonexistent-user"

    # Act & Assert
    with pytest.raises(UserNotFoundError):
        await service.get_user_by_id(invalid_id)
```

### E2E (Playwright)

```typescript
import { test, expect } from '@playwright/test';

test.describe('Property Detail Page', () => {
  test('should_display_property_details_when_valid_id_provided', async ({ page }) => {
    // Arrange
    await page.goto('/properties/123');

    // Act
    await page.waitForLoadState('networkidle');

    // Assert
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    await expect(page.getByText('$1,200,000')).toBeVisible();
  });

  test('should_show_error_when_property_not_found', async ({ page }) => {
    // Arrange & Act
    await page.goto('/properties/nonexistent');

    // Assert
    await expect(page.getByText(/not found/i)).toBeVisible();
  });
});
```

## Output

After running this command, you should have:

- ✅ Test files with comprehensive test coverage
- ✅ Documentation of test scenarios in test names
- ✅ Commands to run tests documented
- ✅ Confirmation that tests fail (with meaningful errors)

## Anti-Patterns to Avoid

❌ **Don't write tests that already pass** - Tests must fail first
❌ **Don't test implementation details** - Test behavior, not internals
❌ **Don't create complex test setup** - Keep tests simple and readable
❌ **Don't test multiple behaviors in one test** - One behavior per test
❌ **Don't use vague test names** - Use descriptive should_X_when_Y pattern

## Example: Complete RED Phase

**Scenario:** User wants to add property image gallery with navigation

**Test Suite (apps/frontend/tests/unit/PropertyGallery.spec.ts):**

```typescript
import { render, screen, fireEvent } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import PropertyGallery from '$lib/components/PropertyGallery.svelte';

describe('PropertyGallery', () => {
  const mockImages = [
    { url: '/img1.jpg', alt: 'Image 1' },
    { url: '/img2.jpg', alt: 'Image 2' },
    { url: '/img3.jpg', alt: 'Image 3' }
  ];

  it('should_display_first_image_when_gallery_loaded', () => {
    render(PropertyGallery, { props: { images: mockImages } });

    const img = screen.getByRole('img');
    expect(img).toHaveAttribute('src', '/img1.jpg');
  });

  it('should_show_next_image_when_next_button_clicked', async () => {
    render(PropertyGallery, { props: { images: mockImages } });

    const nextButton = screen.getByRole('button', { name: /next/i });
    await fireEvent.click(nextButton);

    const img = screen.getByRole('img');
    expect(img).toHaveAttribute('src', '/img2.jpg');
  });

  it('should_wrap_to_first_image_when_next_clicked_on_last', async () => {
    render(PropertyGallery, { props: { images: mockImages } });

    // Navigate to last image
    const nextButton = screen.getByRole('button', { name: /next/i });
    await fireEvent.click(nextButton);
    await fireEvent.click(nextButton);

    // Click next again (should wrap to first)
    await fireEvent.click(nextButton);

    const img = screen.getByRole('img');
    expect(img).toHaveAttribute('src', '/img1.jpg');
  });

  it('should_show_empty_state_when_no_images_provided', () => {
    render(PropertyGallery, { props: { images: [] } });

    expect(screen.getByText(/no images available/i)).toBeInTheDocument();
  });
});
```

**Run tests:**
```bash
cd apps/frontend
npm run test:unit -- PropertyGallery.spec.ts
```

**Expected output:**
```
❌ should_display_first_image_when_gallery_loaded
   Error: Unable to find element with role "img"

❌ should_show_next_image_when_next_button_clicked
   Error: Unable to find element with role "button"

❌ should_wrap_to_first_image_when_next_clicked_on_last
   Error: Unable to find element with role "button"

❌ should_show_empty_state_when_no_images_provided
   Error: Unable to find text matching /no images available/i

Tests: 0 passed, 4 failed
```

**Status: RED ✅** - All tests fail as expected. Ready for GREEN phase.

## Next Steps

After tests are written and failing correctly, use `/tdd-green` to implement minimal code to make them pass.

## Integration with SDLC

This command is used during:
- **IMPLEMENTATION Phase**: First step in `/tdd-cycle` workflow
- **PLANNING Phase**: Writing test specifications (not actual tests yet)
- **Task execution**: Any feature development requiring tests

## Coverage Thresholds

Tests written during RED phase should aim for:
- **80% line coverage** minimum
- **75% branch coverage** minimum
- **100% critical path coverage** (authentication, payments, data loss prevention)

See: `.claude/reports/20251109-tdd-workflows-plugin-review.md` for TDD integration details.

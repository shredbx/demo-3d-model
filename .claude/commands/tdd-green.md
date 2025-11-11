Implement minimal code to make failing tests pass in TDD green phase (project)

[Extended thinking: Guide implementation of minimal code necessary to make tests pass, avoiding over-engineering.]

## Process

### 1. Review Failing Tests

Before implementing, understand what tests expect:

```bash
# Run tests to see failures
npm run test:unit  # Frontend
pytest             # Backend
npm run test:e2e   # E2E
```

**Analyze:**
- What behavior do tests expect?
- What's the simplest path to green?
- Are there patterns in test failures?

### 2. Choose Appropriate Implementation Agent

Select the right subagent based on what you're implementing:

- **Backend code (API, services, models)**: Use `dev-backend-fastapi` agent
- **Frontend code (Svelte components, routes)**: Use `dev-frontend-svelte` agent
- **Infrastructure (Docker, deploy)**: Use `devops-infra` agent

### 3. Implementation Strategy

Choose the simplest strategy to make tests pass:

#### Strategy 1: Fake It (Recommended for first test)

Return hard-coded values when appropriate:

```typescript
// Tests expect: getUser('123') => { id: '123', name: 'John' }

class UserService {
  getUser(id: string) {
    return { id: '123', name: 'John' };  // Fake it!
  }
}
```

**When to use:**
- First test for a new feature
- Complex external dependencies
- Implementation approach uncertain

#### Strategy 2: Obvious Implementation

When solution is trivial and clear:

```typescript
// Tests expect: add(2, 3) => 5

function add(a: number, b: number): number {
  return a + b;  // Obvious!
}
```

**When to use:**
- Implementation is straightforward
- Solution is immediately clear
- Faking would be more complex

#### Strategy 3: Triangulation

Generalize only when multiple tests require it:

```typescript
// First test: getUser('123') => { id: '123', name: 'John' }
getUser(id) { return { id: '123', name: 'John' }; }  // Fake it

// Second test: getUser('456') => { id: '456', name: 'Jane' }
getUser(id) {
  const users = {
    '123': { id: '123', name: 'John' },
    '456': { id: '456', name: 'Jane' }
  };
  return users[id];  // Now generalize
}
```

**When to use:**
- Second or third test reveals pattern
- Need to avoid premature generalization

### 4. Implementation Constraints

**✅ DO:**
- Write ONLY code needed to make tests pass
- Keep implementations simple and readable
- Run tests frequently to verify progress
- Commit after each test passes

**❌ DON'T:**
- Add extra features beyond test requirements
- Optimize prematurely
- Add design patterns unless tests require them
- Modify tests to make them pass

### 5. Verify Tests Pass

After implementation, verify all tests are green:

```bash
# Run tests
npm run test:unit  # Frontend
pytest             # Backend
npm run test:e2e   # E2E

# Check coverage
npm run test:coverage  # Frontend
pytest --cov       # Backend
```

**Success Criteria:**
- ✅ All tests pass (100% green)
- ✅ Coverage meets thresholds (80% line, 75% branch)
- ✅ No extra functionality added
- ✅ Code is readable

## Framework-Specific Patterns

### Svelte Component Implementation

```svelte
<!-- PropertyGallery.svelte -->
<script lang="ts">
  // Minimal implementation to make tests pass
  let { images = [] }: { images: Array<{ url: string; alt: string }> } = $props();
  let currentIndex = $state(0);

  function nextImage() {
    currentIndex = (currentIndex + 1) % images.length;
  }

  function previousImage() {
    currentIndex = (currentIndex - 1 + images.length) % images.length;
  }
</script>

{#if images.length === 0}
  <p>No images available</p>
{:else}
  <img src={images[currentIndex].url} alt={images[currentIndex].alt} />
  <button onclick={previousImage}>Previous</button>
  <button onclick={nextImage}>Next</button>
{/if}
```

**Note:** No styling, no animations, no extras - just what tests require.

### FastAPI Endpoint Implementation

```python
from fastapi import APIRouter, HTTPException
from server.schemas.user import UserResponse

router = APIRouter()

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    # Minimal implementation - in-memory for now
    users = {
        "123": {"id": "123", "name": "John"},
        "456": {"id": "456", "name": "Jane"}
    }

    user = users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
```

**Note:** No database, no caching, no validation - just passing tests.

### SvelteKit Load Function

```typescript
// +page.server.ts
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
  // Minimal implementation - hard-coded data
  const properties = {
    '123': { id: '123', title: 'Beautiful Home', price: 1200000 },
    '456': { id: '456', title: 'Cozy Apartment', price: 450000 }
  };

  const property = properties[params.id];

  if (!property) {
    throw error(404, 'Property not found');
  }

  return { property };
};
```

**Note:** No API calls, no database - just what tests need.

## Progressive Implementation Example

**Scenario:** Implementing user authentication

### Stage 1: Fake It (First Test Passes)

```typescript
// Test: should_return_token_when_valid_credentials
class AuthService {
  async authenticate(email: string, password: string) {
    return { success: true, token: 'fake-token-123' };
  }
}
```

**Status:** ✅ 1 test passes. Tests are green!

### Stage 2: Handle Error Case (Second Test Passes)

```typescript
// Test: should_fail_when_invalid_credentials
class AuthService {
  async authenticate(email: string, password: string) {
    if (email === 'test@example.com' && password === 'password') {
      return { success: true, token: 'fake-token-123' };
    }
    return { success: false, error: 'INVALID_CREDENTIALS' };
  }
}
```

**Status:** ✅ 2 tests pass. Still minimal!

### Stage 3: Triangulate (Third Test Requires Generalization)

```typescript
// Test: should_check_database_for_user
class AuthService {
  private users = new Map([
    ['test@example.com', { email: 'test@example.com', passwordHash: 'hashed-password' }],
    ['user@example.com', { email: 'user@example.com', passwordHash: 'hashed-pass-2' }]
  ]);

  async authenticate(email: string, password: string) {
    const user = this.users.get(email);
    if (!user) {
      return { success: false, error: 'INVALID_CREDENTIALS' };
    }

    // Still simplified password check
    const passwordMatches = password === 'password';
    if (!passwordMatches) {
      return { success: false, error: 'INVALID_CREDENTIALS' };
    }

    return { success: true, token: `token-${user.email}` };
  }
}
```

**Status:** ✅ 3 tests pass. Now generalized!

**Note:** No bcrypt, no database, no JWT - refactoring phase will add those.

## Quality Checks

Before proceeding to refactor phase:

- ✅ All tests pass (100% green)
- ✅ Coverage thresholds met (80% line, 75% branch)
- ✅ No extra functionality added
- ✅ Code is readable even if not optimal
- ✅ Implementation time was minimized

## Anti-Patterns to Avoid

❌ **Gold Plating**: Adding features not required by tests
```typescript
// Bad: Tests don't require caching
class UserService {
  private cache = new Map(); // Extra!
  private rateLimiter = new RateLimiter(); // Extra!
  private logger = new Logger(); // Extra!
}
```

❌ **Premature Optimization**: Optimizing before tests require it
```typescript
// Bad: Tests don't measure performance
function processData(data) {
  // Complex optimization when simple loop would pass tests
  return data.reduce((acc, item) => {
    const memoized = this.cache.get(item.id);
    // ... 50 lines of optimization ...
  }, []);
}
```

❌ **Design Patterns Without Justification**: Adding patterns tests don't need
```typescript
// Bad: Tests don't require Factory pattern
class UserFactory {
  createUser(type: string) {
    switch(type) {
      case 'admin': return new AdminUser();
      case 'user': return new RegularUser();
    }
  }
}

// Good: Simple object creation passes tests
function createUser(data: UserData) {
  return { ...data, createdAt: new Date() };
}
```

❌ **Modifying Tests**: Changing tests to make implementation easier
```typescript
// Bad: Changed test expectation
it('should_return_user_when_valid_id', () => {
  expect(service.getUser('123')).toBe(undefined); // Changed from expecting user!
});

// Good: Keep test expectation, fix implementation
it('should_return_user_when_valid_id', () => {
  expect(service.getUser('123')).toEqual({ id: '123', name: 'John' });
});
```

## Next Steps

After all tests are green and coverage thresholds are met, use `/tdd-refactor` to improve code quality while keeping tests green.

## Integration with SDLC

This command is used during:
- **IMPLEMENTATION Phase**: Second step in `/tdd-cycle` workflow (after /tdd-red)
- **Task execution**: Making failing tests pass
- **Bug fixes**: Minimal fix to make broken tests pass again

## Coverage Thresholds

Implementation must achieve:
- **80% line coverage** minimum
- **75% branch coverage** minimum
- **100% critical path coverage** (authentication, payments, data loss prevention)

```bash
# Verify coverage after implementation
npm run test:coverage  # Frontend
pytest --cov          # Backend
```

## Example: Complete GREEN Phase

**Scenario:** PropertyGallery tests from RED phase are now failing

**Command:**
```bash
# Current state: 4 failing tests
cd apps/frontend
npm run test:unit -- PropertyGallery.spec.ts
```

**Implementation (minimal):**

```svelte
<!-- apps/frontend/src/lib/components/PropertyGallery.svelte -->
<script lang="ts">
  interface Image {
    url: string;
    alt: string;
  }

  let { images = [] }: { images: Image[] } = $props();
  let currentIndex = $state(0);

  function nextImage() {
    currentIndex = (currentIndex + 1) % images.length;
  }
</script>

{#if images.length === 0}
  <p>No images available</p>
{:else}
  <img src={images[currentIndex].url} alt={images[currentIndex].alt} />
  <button onclick={nextImage}>Next</button>
{/if}
```

**Run tests:**
```bash
npm run test:unit -- PropertyGallery.spec.ts
```

**Expected output:**
```
✅ should_display_first_image_when_gallery_loaded
✅ should_show_next_image_when_next_button_clicked
✅ should_wrap_to_first_image_when_next_clicked_on_last
✅ should_show_empty_state_when_no_images_provided

Tests: 4 passed, 0 failed
Coverage: 100% (all lines covered)
```

**Status: GREEN ✅** - All tests pass. Ready for REFACTOR phase.

**Note:** No styling, no transitions, no previous button - just enough to make tests pass. Refactoring phase will improve this.

## Recovery Process

If tests still fail after implementation:

1. **Review test requirements carefully**
   - Read test expectations again
   - Understand what behavior is expected

2. **Check for misunderstood assertions**
   - Are you returning the right type?
   - Are you handling edge cases?

3. **Add minimal code to address specific failures**
   - Fix one failing test at a time
   - Don't rewrite from scratch

4. **Run tests after each change**
   - Verify progress incrementally
   - Catch regressions immediately

5. **Consider if tests need adjustment**
   - Are tests testing the right thing?
   - Is the test specification correct?

See: `.claude/reports/20251109-tdd-workflows-plugin-review.md` for TDD integration details.

Refactor code with confidence using comprehensive test safety net (project)

[Extended thinking: Guide safe refactoring using tests as safety net, applying design patterns and SOLID principles.]

## Process

### 1. Pre-Refactoring Checks

Before refactoring, establish a green baseline:

```bash
# Verify all tests pass
npm run test:unit  # Frontend
pytest             # Backend
npm run test:e2e   # E2E

# Document current state
git status
git diff
```

**Requirements:**
- ✅ All tests must be green
- ✅ Coverage meets thresholds (80/75)
- ✅ No uncommitted changes (commit GREEN phase first)

### 2. Use Code Review Agent

For complex refactorings, use `qa-code-auditor` agent to:
- Identify code smells
- Detect SOLID violations
- Measure cyclomatic complexity
- Suggest design patterns

### 3. Refactoring Triggers (When to Refactor)

Refactor when code exhibits these issues:

| Trigger | Threshold | Action |
|---------|-----------|--------|
| **Cyclomatic Complexity** | > 10 | Break into smaller functions |
| **Method Length** | > 20 lines | Extract methods |
| **Class Length** | > 200 lines | Split responsibilities |
| **Code Duplication** | > 3 lines | Extract common code |
| **Magic Numbers** | Any | Replace with named constants |
| **Long Parameter Lists** | > 3 params | Use parameter objects |

### 4. Refactoring Techniques

#### Extract Method
```typescript
// Before
function processOrder(order) {
  let total = 0;
  for (const item of order.items) {
    total += item.price * item.quantity;
  }
  const tax = total * 0.08;
  const shipping = total > 100 ? 0 : 15;
  return total + tax + shipping;
}

// After
function processOrder(order) {
  const subtotal = calculateSubtotal(order.items);
  const tax = calculateTax(subtotal);
  const shipping = calculateShipping(subtotal);
  return subtotal + tax + shipping;
}

function calculateSubtotal(items) {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

function calculateTax(amount) {
  return amount * 0.08;
}

function calculateShipping(amount) {
  return amount > 100 ? 0 : 15;
}
```

#### Rename for Clarity
```typescript
// Before
function f(u) {
  const d = u.getData();
  return d.filter(x => x.a);
}

// After
function getActiveUsers(userService) {
  const users = userService.getData();
  return users.filter(user => user.isActive);
}
```

#### Replace Magic Numbers
```typescript
// Before
if (order.total > 100) {
  discount = 0.1;
}

// After
const FREE_SHIPPING_THRESHOLD = 100;
const BULK_DISCOUNT_RATE = 0.1;

if (order.total > FREE_SHIPPING_THRESHOLD) {
  discount = BULK_DISCOUNT_RATE;
}
```

#### Extract Component (Svelte)
```svelte
<!-- Before: One large component -->
<script lang="ts">
  let property = $props();
  let currentImage = $state(0);
  let showModal = $state(false);
</script>

<div>
  <!-- 100 lines of gallery code -->
  <!-- 50 lines of details code -->
  <!-- 30 lines of modal code -->
</div>

<!-- After: Extracted components -->
<script lang="ts">
  import PropertyGallery from './PropertyGallery.svelte';
  import PropertyDetails from './PropertyDetails.svelte';
  import PropertyModal from './PropertyModal.svelte';

  let property = $props();
</script>

<PropertyGallery images={property.images} />
<PropertyDetails property={property} />
<PropertyModal property={property} />
```

### 5. Apply SOLID Principles

#### Single Responsibility
```typescript
// Before: Class does too much
class UserService {
  async getUser(id) { ... }
  async sendEmail(user, template) { ... }
  async logActivity(user, action) { ... }
}

// After: Split responsibilities
class UserService {
  async getUser(id) { ... }
}

class EmailService {
  async sendEmail(user, template) { ... }
}

class ActivityLogger {
  async logActivity(user, action) { ... }
}
```

#### Open/Closed
```typescript
// Before: Modifying function for new payment types
function processPayment(type, amount) {
  if (type === 'credit') {
    return processCreditCard(amount);
  } else if (type === 'paypal') {
    return processPayPal(amount);
  }
  // Need to modify for each new type!
}

// After: Open for extension, closed for modification
interface PaymentProcessor {
  process(amount: number): Promise<PaymentResult>;
}

class CreditCardProcessor implements PaymentProcessor {
  async process(amount: number) { ... }
}

class PayPalProcessor implements PaymentProcessor {
  async process(amount: number) { ... }
}

function processPayment(processor: PaymentProcessor, amount: number) {
  return processor.process(amount);
}
```

#### Dependency Inversion
```typescript
// Before: Depends on concrete implementation
class OrderService {
  private database = new PostgreSQLDatabase();

  async getOrder(id: string) {
    return this.database.query('SELECT * FROM orders WHERE id = ?', [id]);
  }
}

// After: Depends on abstraction
interface Database {
  query(sql: string, params: any[]): Promise<any>;
}

class OrderService {
  constructor(private database: Database) {}

  async getOrder(id: string) {
    return this.database.query('SELECT * FROM orders WHERE id = ?', [id]);
  }
}
```

### 6. Safety Verification

**After EACH refactoring:**

```bash
# 1. Run tests immediately
npm run test:unit

# 2. Verify all tests still pass
# Tests: X passed, 0 failed

# 3. Check coverage maintained
npm run test:coverage

# 4. Commit if successful
git add .
git commit -m "refactor: extract calculateSubtotal method"
```

**⚠️ IF TESTS FAIL:**
- Stop immediately
- Revert last change: `git checkout .`
- Analyze what broke
- Make smaller incremental changes

### 7. Refactoring Workflow

```
1. Green baseline ✅
   ↓
2. Identify code smell
   ↓
3. Make ONE small refactoring
   ↓
4. Run tests ✅
   ↓
5. Tests pass? → Commit → Repeat from step 2
   ↓
   Tests fail? → Revert → Smaller change
```

## Design Patterns to Consider

### Creational Patterns

**Factory Pattern** (when creating complex objects):
```typescript
class PropertyFactory {
  static create(type: 'rental' | 'sale', data: any) {
    switch(type) {
      case 'rental':
        return new RentalProperty(data);
      case 'sale':
        return new SaleProperty(data);
    }
  }
}
```

**Builder Pattern** (when object has many optional parameters):
```typescript
class PropertyQueryBuilder {
  private filters: Filter[] = [];

  withLocation(location: string) {
    this.filters.push({ type: 'location', value: location });
    return this;
  }

  withPriceRange(min: number, max: number) {
    this.filters.push({ type: 'price', value: { min, max } });
    return this;
  }

  build() {
    return new PropertyQuery(this.filters);
  }
}

// Usage
const query = new PropertyQueryBuilder()
  .withLocation('Miami')
  .withPriceRange(100000, 500000)
  .build();
```

### Structural Patterns

**Repository Pattern** (data access abstraction):
```typescript
interface PropertyRepository {
  findById(id: string): Promise<Property | null>;
  findAll(filters: PropertyFilters): Promise<Property[]>;
  save(property: Property): Promise<void>;
}

class ApiPropertyRepository implements PropertyRepository {
  async findById(id: string) {
    const response = await fetch(`/api/properties/${id}`);
    return response.json();
  }
}
```

### Behavioral Patterns

**Strategy Pattern** (interchangeable algorithms):
```typescript
interface PricingStrategy {
  calculate(base: number): number;
}

class StandardPricing implements PricingStrategy {
  calculate(base: number) {
    return base;
  }
}

class DiscountPricing implements PricingStrategy {
  constructor(private discount: number) {}

  calculate(base: number) {
    return base * (1 - this.discount);
  }
}

class PropertyService {
  constructor(private pricingStrategy: PricingStrategy) {}

  getPrice(property: Property) {
    return this.pricingStrategy.calculate(property.basePrice);
  }
}
```

## Performance Optimization

Only optimize if:
1. Tests require specific performance
2. Profiling shows bottleneck
3. User experience is affected

**Example: Optimize after profiling**
```typescript
// Before: N+1 queries
async function getPropertiesWithOwners() {
  const properties = await db.query('SELECT * FROM properties');
  for (const property of properties) {
    property.owner = await db.query('SELECT * FROM users WHERE id = ?', [property.ownerId]);
  }
  return properties;
}

// After: Single query with JOIN
async function getPropertiesWithOwners() {
  return db.query(`
    SELECT p.*, u.* FROM properties p
    JOIN users u ON p.owner_id = u.id
  `);
}
```

## Quality Checks

Before completing refactor phase:

- ✅ All tests still pass (100% green)
- ✅ Code complexity reduced (cyclomatic ≤ 10)
- ✅ Duplication eliminated (< 3 lines)
- ✅ Performance maintained or improved
- ✅ Test readability improved
- ✅ Coverage maintained or increased (≥ 80/75)

## Anti-Patterns to Avoid

❌ **Changing behavior during refactoring**
```typescript
// Bad: Added new feature during refactor
function calculateTotal(items) {
  const total = items.reduce(...);
  sendAnalytics(total); // New behavior!
  return total;
}
```

❌ **Skipping test runs**
```typescript
// Bad: Multiple refactorings without testing
- Extract method
- Rename variables
- Move code to new file
// Finally run tests (too late!)
```

❌ **Large refactorings without commits**
```
Bad:
- Refactor 10 files
- Rename 50 variables
- Restructure entire module
- Run tests (fail, can't isolate issue)

Good:
- Refactor 1 file → Test → Commit
- Rename in 1 file → Test → Commit
- Move 1 component → Test → Commit
```

## Integration with SDLC

This command is used during:
- **IMPLEMENTATION Phase**: Third step in `/tdd-cycle` workflow (after /tdd-green)
- **Task execution**: Improving code quality after tests pass
- **Maintenance**: Continuous code improvement

## Success Criteria

- ✅ All tests pass (100% green)
- ✅ Cyclomatic complexity ≤ 10
- ✅ Methods ≤ 20 lines
- ✅ Classes ≤ 200 lines
- ✅ No code duplication > 3 lines
- ✅ SOLID principles applied
- ✅ Code is more readable than before

## Example: Complete REFACTOR Phase

**Scenario:** PropertyGallery from GREEN phase needs refactoring

**Current State (from GREEN phase):**
```svelte
<!-- Minimal but messy -->
<script lang="ts">
  let { images = [] } = $props();
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

**Refactored (SOLID, semantic HTML, accessibility):**
```svelte
<script lang="ts">
  interface GalleryImage {
    url: string;
    alt: string;
  }

  interface Props {
    images?: GalleryImage[];
  }

  let { images = [] }: Props = $props();
  let currentIndex = $state(0);

  // Computed properties for clarity
  const hasImages = $derived(images.length > 0);
  const currentImage = $derived(images[currentIndex]);
  const totalImages = $derived(images.length);

  // Semantic action methods
  function navigateNext() {
    currentIndex = (currentIndex + 1) % totalImages;
  }

  function navigatePrevious() {
    currentIndex = (currentIndex - 1 + totalImages) % totalImages;
  }
</script>

{#if !hasImages}
  <div class="gallery-empty" role="status" aria-live="polite">
    <p>No images available</p>
  </div>
{:else}
  <div class="gallery" role="region" aria-label="Property image gallery">
    <img
      src={currentImage.url}
      alt={currentImage.alt}
      class="gallery-image"
    />

    <nav class="gallery-controls" aria-label="Gallery navigation">
      <button
        onclick={navigatePrevious}
        aria-label="Previous image"
        class="gallery-button"
      >
        Previous
      </button>

      <span class="gallery-counter" aria-live="polite">
        {currentIndex + 1} / {totalImages}
      </span>

      <button
        onclick={navigateNext}
        aria-label="Next image"
        class="gallery-button"
      >
        Next
      </button>
    </nav>
  </div>
{/if}

<style>
  .gallery {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .gallery-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
</style>
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
Coverage: 100%
```

**Improvements Made:**
- ✅ Added TypeScript interfaces for type safety
- ✅ Extracted computed properties ($derived)
- ✅ Semantic method names (navigateNext vs nextImage)
- ✅ Added accessibility (ARIA labels, roles)
- ✅ Added semantic HTML (nav, region)
- ✅ Added image counter
- ✅ Added previous button
- ✅ Added styling structure
- ✅ Tests still pass!

**Status: REFACTOR ✅** - Code improved, tests still green!

See: `.claude/reports/20251109-tdd-workflows-plugin-review.md` for TDD integration details.

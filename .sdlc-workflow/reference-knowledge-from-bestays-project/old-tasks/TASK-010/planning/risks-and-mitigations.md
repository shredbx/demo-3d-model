# Risks and Mitigations: US-021 Thai Localization

**Task:** TASK-010
**Story:** US-021
**Date:** 2025-11-08

Comprehensive risk analysis with mitigations and contingency plans.

---

## Risk Matrix

| Risk | Severity | Likelihood | Priority | Mitigation | Contingency |
|------|----------|------------|----------|------------|-------------|
| #1: Cache Invalidation Complexity | HIGH | MEDIUM | CRITICAL | Comprehensive unit tests, clear cache key pattern | FLUSHALL cache if collision |
| #2: Thai Character Encoding | MEDIUM | LOW | MEDIUM | Verify database UTF-8, test Thai in seed data | Re-create database with UTF-8 |
| #3: SSR/CSR Hydration Mismatch | MEDIUM | LOW | MEDIUM | Test SSR rendering, validate context setup | Disable SSR for locale routes |
| #4: URL Redirect Loops | HIGH | LOW | MEDIUM | Test redirect logic, validate locale params | Remove redirect, manual selection |
| #5: Missing Thai Translations | LOW | HIGH | LOW | Implement fallback logic, log missing keys | Admin dashboard for gaps |
| #6: Multi-Product Cache Collision | CRITICAL | MEDIUM | CRITICAL | Include product in cache keys, cross-product tests | Namespace Redis by product |

---

## Risk #1: Cache Invalidation Complexity

### Description
Multi-locale, multi-product cache keys create complexity in invalidation logic. Risk of stale content or cache collisions.

### Impact
- **Severity:** HIGH
- **Likelihood:** MEDIUM
- Users may see stale content after edits
- Cache collisions could show wrong product's content
- Performance degradation if cache always missed

### Root Causes
- Cache key format change: `content:{key}` → `content:{product}:{locale}:{key}`
- Multiple invalidation points (edit Thai vs English)
- Redis shared between products

### Mitigation Strategy

**1. Clear Cache Key Pattern:**
```python
def _get_cache_key(key: str, locale: str) -> str:
    """Generate cache key with product and locale"""
    PRODUCT_NAME = os.getenv("PRODUCT_NAME", "bestays")
    return f"content:{PRODUCT_NAME}:{locale}:{key}"
```

**2. Comprehensive Unit Tests:**
- Test cache invalidation for Thai content only
- Test cache invalidation for English content only
- Test multi-product isolation (different keys)
- Test cache key format matches expected pattern

**3. Monitoring:**
- Log all cache operations (hit, miss, invalidate)
- Alert if cache hit rate drops below 80%
- Track cache keys by pattern

**4. Documentation:**
- Document cache key format in architecture spec
- Comment cache key generation functions
- Include examples in code

### Contingency Plan

**If cache collision detected:**
1. Immediately FLUSHALL Redis cache
2. Cache repopulates from database (performance hit but safe)
3. Fix cache key format in backend
4. Redeploy backend
5. Validate no more collisions

**Command:**
```bash
docker exec -it bestays-redis-dev redis-cli FLUSHALL
```

**Rollback:**
- Revert to old cache key format temporarily
- Clear all cache keys
- Allow cache to repopulate with old format

---

## Risk #2: Thai Character Encoding

### Description
Thai characters (UTF-8) may not display correctly if database/frontend not configured for UTF-8.

### Impact
- **Severity:** MEDIUM
- **Likelihood:** LOW
- Garbled Thai text (squares, question marks)
- Poor user experience for Thai users
- Data integrity issues

### Root Causes
- PostgreSQL database charset not UTF-8
- Frontend not declaring UTF-8
- Database client not using UTF-8 connection

### Mitigation Strategy

**1. Verify Database Encoding:**
```sql
-- Check database encoding
SELECT datname, pg_encoding_to_char(encoding) FROM pg_database;
-- Expected: UTF8
```

**2. Test Thai Characters in Seed Data:**
```python
THAI_TRANSLATIONS = {
    "hero.title": "ยินดีต้อนรับสู่ Bestays",  # Must display correctly
}
```

**3. Frontend UTF-8 Declaration:**
```html
<!-- Already in SvelteKit default template -->
<meta charset="utf-8" />
```

**4. Manual Visual Inspection:**
- Load `/th/` page
- Verify Thai characters display correctly: ยินดีต้อนรับสู่ Bestays
- No squares, no question marks

### Contingency Plan

**If Thai characters garbled:**

**Option 1: Database Re-creation (NUCLEAR OPTION)**
```bash
# Backup existing data
docker exec -it bestays-postgres-dev pg_dump -U bestays_user bestays_dev > backup.sql

# Drop and re-create database with UTF-8
docker exec -it bestays-postgres-dev psql -U bestays_user -c "DROP DATABASE bestays_dev;"
docker exec -it bestays-postgres-dev psql -U bestays_user -c "CREATE DATABASE bestays_dev WITH ENCODING 'UTF8';"

# Restore data
docker exec -i bestays-postgres-dev psql -U bestays_user bestays_dev < backup.sql
```

**Option 2: Client-Side Fix (LIKELY)**
- Ensure SQLAlchemy connection uses UTF-8:
```python
engine = create_engine(DATABASE_URL, connect_args={"client_encoding": "utf8"})
```

**Option 3: Frontend Fix**
- Ensure API responses declare UTF-8:
```python
return JSONResponse(content=data, media_type="application/json; charset=utf-8")
```

---

## Risk #3: SSR/CSR Hydration Mismatch

### Description
Locale context set differently on server vs client could cause hydration mismatch.

### Impact
- **Severity:** MEDIUM
- **Likelihood:** LOW
- Console errors in browser
- Flash of wrong content
- Poor user experience

### Root Causes
- Locale determined client-side only
- Browser-specific locale detection
- Conditional rendering based on `browser` variable

### Mitigation Strategy

**1. Server-Side Locale Determination:**
```typescript
// routes/[lang]/+layout.ts
export const load: LayoutLoad = async ({ params }) => {
  const locale = params.lang; // From URL, available on server
  
  if (!SUPPORTED_LOCALES.includes(locale as any)) {
    redirect(302, '/en');
  }
  
  return { locale }; // Same value on server and client
};
```

**2. No Conditional Rendering:**
- Avoid `{#if browser}` blocks in locale context
- Use URL parameter (available on both server and client)
- No client-only locale detection

**3. Testing:**
- Test SSR rendering (view source)
- Verify locale in HTML matches URL
- No hydration warnings in console

### Contingency Plan

**If hydration mismatch occurs:**

**Option 1: Disable SSR for Locale Routes (LAST RESORT)**
```typescript
// routes/[lang]/+page.ts
export const ssr = false; // Disable SSR
```

**Option 2: Use $page Store Instead of Context**
```svelte
<script>
  import { page } from '$app/stores';
  const locale = $page.params.lang;
</script>
```

**Option 3: Client-Only Mount**
```svelte
{#if mounted}
  <LocaleSwitcher />
{/if}
```

---

## Risk #4: URL Redirect Loops

### Description
Redirect logic could cause infinite loops (e.g., `/` → `/en` → `/` → ...).

### Impact
- **Severity:** HIGH (site unusable)
- **Likelihood:** LOW
- Browser shows "too many redirects" error
- Users cannot access site
- Critical bug

### Root Causes
- Incorrect redirect logic in root `+page.svelte`
- Layout redirecting to root
- Invalid locale parameter handling

### Mitigation Strategy

**1. Test Redirect Logic:**
```typescript
// routes/+page.svelte
onMount(() => {
  goto('/en', { replaceState: true }); // One-time redirect
});
```

**2. Validate Locale Parameter:**
```typescript
// routes/[lang]/+layout.ts
if (!SUPPORTED_LOCALES.includes(locale as any)) {
  redirect(302, '/en'); // Fallback to valid locale
}
```

**3. E2E Test:**
- Test root redirect (/ → /en)
- Test invalid locale (/invalid → /en)
- Test valid locale (/th → stays on /th)

### Contingency Plan

**If redirect loop occurs:**

**Immediate Fix:**
```svelte
<!-- routes/+page.svelte - TEMPORARY FIX -->
<script>
  // Remove redirect, show manual selection
</script>

<div class="locale-selection">
  <a href="/en">English</a>
  <a href="/th">ภาษาไทย</a>
</div>
```

**Permanent Fix:**
- Debug redirect logic
- Ensure no circular redirects
- Test thoroughly before redeploying

---

## Risk #5: Missing Thai Translations

### Description
Some content keys may not have Thai translations initially.

### Impact
- **Severity:** LOW
- **Likelihood:** HIGH
- Thai users see English fallback
- Incomplete user experience
- Not a critical bug (graceful degradation)

### Root Causes
- Thai translations added incrementally
- New content keys added without Thai version
- Content updates in English only

### Mitigation Strategy

**1. Implement Fallback Logic:**
```python
async def get_content(db: Session, key: str, locale: str = 'en'):
    # Try (key, locale)
    content = db.query(ContentDictionary).filter_by(key=key, locale=locale).first()
    
    # Fallback to English if not found
    if not content and locale != 'en':
        content = db.query(ContentDictionary).filter_by(key=key, locale='en').first()
    
    return content
```

**2. Log Missing Translations:**
```python
if not content and locale != 'en':
    logger.warning(f"Missing translation: {key} ({locale})")
    # Still return English fallback
```

**3. Admin Dashboard (Future):**
- Show list of missing translations
- Allow admin to add Thai translations
- Track translation completion percentage

### Contingency Plan

**If many missing translations:**

**Short-term:**
- Accept English fallback (AC-4 allows this)
- Create Notion/spreadsheet for tracking missing keys
- Prioritize high-visibility content for translation

**Long-term:**
- Build admin dashboard to identify gaps
- Integrate with translation service (Google Translate API for suggestions)
- Set up process for content creators to add Thai translations

---

## Risk #6: Multi-Product Cache Collision (CRITICAL)

### Description
**LESSON FROM US-020:** Cache keys without product identifier caused wrong content to display.

### Impact
- **Severity:** CRITICAL
- **Likelihood:** MEDIUM
- Bestays users see Real Estate content (or vice versa)
- Data integrity breach
- User confusion
- Brand damage

### Root Causes
- Shared Redis instance
- Cache keys without product identifier
- Incorrect PRODUCT_NAME environment variable

### Mitigation Strategy

**1. Include Product in Cache Keys:**
```python
PRODUCT_NAME = os.getenv("PRODUCT_NAME", "bestays")

def _get_cache_key(key: str, locale: str) -> str:
    return f"content:{PRODUCT_NAME}:{locale}:{key}"
    # Example: content:bestays:th:hero.title
    # Example: content:realestate:th:hero.title
```

**2. Comprehensive Cross-Product Tests:**
```typescript
// tests/e2e/multi-product-locale.spec.ts
test('editing bestays content does not affect realestate', async () => {
  // Edit bestays content
  await editContent('bestays', 'hero.title', 'New Title');
  
  // Verify realestate unchanged
  const realEstateContent = await getContent('realestate', 'hero.title');
  expect(realEstateContent).not.toBe('New Title');
});
```

**3. Environment Variable Validation:**
```python
# In config.py
PRODUCT_NAME = os.getenv("PRODUCT_NAME")
if not PRODUCT_NAME or PRODUCT_NAME not in ['bestays', 'realestate']:
    raise ValueError("Invalid PRODUCT_NAME. Must be 'bestays' or 'realestate'")
```

**4. Monitoring:**
- Log cache key patterns
- Alert if unexpected cache keys appear
- Track cache keys by product

### Contingency Plan

**If cache collision detected (URGENT):**

**Immediate Response (< 5 minutes):**
```bash
# FLUSHALL Redis cache (nuclear option but safe)
docker exec -it bestays-redis-dev redis-cli FLUSHALL
```

**Root Cause Fix (< 1 hour):**
1. Verify `PRODUCT_NAME` environment variable correct
2. Fix cache key generation to include product
3. Deploy backend fix
4. Verify cache keys now include product

**Verification:**
```bash
# Check cache keys
docker exec -it bestays-redis-dev redis-cli KEYS "content:*"

# Expected: Keys grouped by product
# content:bestays:en:hero.title
# content:bestays:th:hero.title
# content:realestate:en:hero.title
# content:realestate:th:hero.title
```

**Permanent Fix:**
- Namespace Redis databases by product (future enhancement):
```yaml
# docker-compose.yml
services:
  bestays-redis:
    image: redis:7-alpine
  
  realestate-redis:
    image: redis:7-alpine
```

---

## Risk Summary

| Risk | Status | Owner | Due Date |
|------|--------|-------|----------|
| #1: Cache Invalidation | ✅ Mitigated | dev-backend-fastapi | Phase 2 |
| #2: Thai Encoding | ✅ Mitigated | devops-infra | Phase 1 |
| #3: Hydration Mismatch | ✅ Mitigated | dev-frontend-svelte | Phase 3 |
| #4: Redirect Loops | ✅ Mitigated | dev-frontend-svelte | Phase 3 |
| #5: Missing Translations | ✅ Accepted | N/A | Ongoing |
| #6: Multi-Product Collision | ✅ Mitigated | dev-backend-fastapi | Phase 2 |

**Overall Risk Level:** MEDIUM

All CRITICAL and HIGH risks have mitigations in place. Contingency plans documented for all risks.

---

## Monitoring and Alerts

### Metrics to Track

1. **Cache Hit Rate**
   - Target: >90%
   - Alert: <80%
   - Action: Investigate cache invalidation logic

2. **API Response Time**
   - Target: <100ms (cached)
   - Alert: >200ms
   - Action: Check Redis latency, database query performance

3. **Error Rate**
   - Target: <0.1%
   - Alert: >1%
   - Action: Check logs for errors, investigate root cause

4. **Fallback Usage**
   - Target: <10% (low missing translations)
   - Alert: >20%
   - Action: Prioritize Thai translation efforts

5. **Locale Distribution**
   - Track: % EN vs % TH traffic
   - Insight: Understand Thai user adoption

### Log Queries

**Missing Translations:**
```bash
docker logs bestays-server-dev | grep "Missing translation"
```

**Cache Operations:**
```bash
docker logs bestays-server-dev | grep "cache"
```

**API Errors:**
```bash
docker logs bestays-server-dev | grep "ERROR"
```

---

## Post-Deployment Review

**After 1 Week:**
- [ ] Review cache hit rate
- [ ] Review error logs
- [ ] Review user feedback
- [ ] Identify any regressions
- [ ] Document lessons learned

**After 1 Month:**
- [ ] Analyze locale distribution (EN vs TH)
- [ ] Identify popular Thai content
- [ ] Plan additional Thai translations
- [ ] Optimize cache TTL if needed
- [ ] Consider additional locales (future)

# Deferred Optimizations - i18n CMS System

**Purpose:** Document architectural optimizations that are DELIBERATELY DEFERRED until metrics justify implementation.

**Philosophy:** "Measure First, Optimize Second" - Don't add complexity without data proving it's needed.

**Status:** Active decision tracking
**Created:** 2025-11-08
**Review Frequency:** After each major phase, or when triggers activate

---

## How to Use This Document

**For Future Sessions (LLM):**
1. When user asks about caching performance → Check "Cache Stampede Prevention" triggers
2. When load testing Phase 1 → Evaluate if any triggers activated
3. When user reports slow queries → Check "Query Optimization" triggers
4. **NEVER suggest these optimizations unless triggers activated**

**For User:**
- This document prevents premature optimization
- Each optimization has clear WHEN/WHY conditions
- Implement only when metrics prove need
- Re-evaluate triggers after each phase

---

## Optimization 1: Cache Stampede Prevention

### Current Status: DEFERRED (Not in Phase 1)

### What Is It?

**Problem:** When cache key expires, multiple concurrent requests simultaneously query database for same data.

**Solution (Deferred):** Per-key asyncio locks serialize DB queries for same cache key.

```python
# DEFERRED - Do NOT implement in Phase 1
class CacheService:
    def __init__(self):
        self._locks: Dict[str, asyncio.Lock] = {}

    async def get_or_fetch(self, key: str, fetch_fn):
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()

        async with self._locks[key]:
            cached = await redis.get(key)
            if cached:
                return cached

            value = await fetch_fn()
            await redis.set(key, value, ttl=3600)
            return value
```

### Phase 1: Simple Pattern (APPROVED)

```python
# APPROVED for Phase 1 - Simple cache-aside
async def get_content(locale: str, key: str) -> dict:
    cache_key = f"content:{locale}:{key}"

    # Try cache
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # Cache miss - fetch DB
    value = await db.execute(...)
    await redis.set(cache_key, json.dumps(value), ex=3600)

    return value
```

### When to Implement (TRIGGERS)

Implement cache stampede prevention ONLY IF **ANY** of these conditions met:

#### Trigger 1: High Concurrent Traffic
```yaml
Condition: > 1000 concurrent requests per second to same cache key
How to Measure:
  - Load testing tools (Locust, k6, Apache Bench)
  - Prometheus metric: rate(content_api_requests_total[1m]) > 1000
  - Redis MONITOR command showing stampede pattern
Action: Run load test after Phase 1, measure concurrent requests per key
```

#### Trigger 2: Cache Hit Ratio < 50%
```yaml
Condition: Cache hit ratio below 50% (too many misses)
How to Measure:
  - Redis INFO stats: keyspace_hits / (keyspace_hits + keyspace_misses)
  - Application logs: cache_hit vs cache_miss counts
  - Prometheus: cache_hit_ratio gauge < 0.5
Action: Monitor for 1 week in production, calculate daily average
```

#### Trigger 3: Database Query Latency > 500ms
```yaml
Condition: Content queries taking > 500ms (expensive operations)
How to Measure:
  - PostgreSQL slow query log (log_min_duration_statement = 100)
  - Application metrics: p95 query latency
  - Prometheus: histogram_quantile(0.95, content_query_duration) > 0.5
Action: Enable slow query logging in Phase 1, review weekly
```

#### Trigger 4: Database Connection Pool Exhaustion
```yaml
Condition: Database runs out of connections during traffic spikes
How to Measure:
  - PostgreSQL logs: "remaining connection slots reserved"
  - SQLAlchemy pool metrics: pool_overflow > 0
  - Application errors: TimeoutError acquiring connection
Action: Monitor connection pool usage during peak hours
```

### How to Measure (Checklist)

**Week 1 After Phase 1 Launch:**
- [ ] Enable PostgreSQL slow query logging
- [ ] Add Prometheus metrics for cache hit ratio
- [ ] Configure Redis INFO monitoring
- [ ] Set up connection pool metrics

**Monthly Review:**
- [ ] Check cache hit ratio (target: > 80%)
- [ ] Review slow query logs (target: < 5 queries/day > 100ms)
- [ ] Measure peak concurrent requests (current baseline: ?)
- [ ] Check connection pool usage (current max: ?)

**Decision Point:**
- If **ANY** trigger activated → Create task to implement stampede prevention
- If **ALL** metrics healthy → Continue monitoring, re-evaluate quarterly

### Estimated Effort (When Triggered)

- **Implementation:** 4-6 hours (add lock service, update cache calls)
- **Testing:** 2-3 hours (unit tests for locks, integration tests)
- **Monitoring:** 2 hours (add lock contention metrics)
- **Total:** 1-2 days

### References

- **Architecture Doc:** `.claude/specs/multi-product-i18n-cms-architecture.md` (Backend section 2923-2956)
- **Backend Agent Review:** Lines 2779-2858 (has complete implementation)
- **Decision Rationale:** User requested deferral on 2025-11-08 (simplify Phase 1, add only when needed)

---

## Optimization 2: Redis Clustering

### Current Status: DEFERRED (Single instance sufficient)

### What Is It?

**Problem:** Single Redis instance becomes bottleneck or single point of failure.

**Solution (Deferred):** Redis Cluster (3+ nodes) or Redis Sentinel (failover).

### Phase 1: Single Instance (APPROVED)

```yaml
redis:
  image: redis:7-alpine
  command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
  # Single instance, no clustering
```

### When to Implement (TRIGGERS)

#### Trigger 1: Memory Usage > 200MB
```yaml
Condition: Redis memory consistently above 200MB (80% of 256MB limit)
How to Measure:
  - Redis INFO memory: used_memory_human
  - Prometheus: redis_memory_used_bytes > 200000000
Action: Monitor weekly via /api/v1/admin/redis/stats
```

#### Trigger 2: High Eviction Rate
```yaml
Condition: Redis evicting keys due to memory pressure
How to Measure:
  - Redis INFO stats: evicted_keys > 100/hour
  - Prometheus: rate(redis_evicted_keys_total[1h]) > 100
Action: Check evicted_keys counter weekly
```

#### Trigger 3: Downtime Impact
```yaml
Condition: Redis downtime causes user-facing errors (not graceful degradation)
How to Measure:
  - Application errors when Redis unavailable
  - User complaints about slow/broken features
  - Uptime monitoring shows Redis as critical path
Action: Test graceful degradation in Phase 1 (app works without Redis)
```

### How to Measure (Checklist)

**Weekly:**
- [ ] Check Redis memory usage (current: ?, target: < 150MB)
- [ ] Check eviction count (current: ?, target: < 10/hour)
- [ ] Verify graceful degradation works (monthly test)

**Decision Point:**
- If memory > 200MB → Increase limit to 512MB first, cluster if still growing
- If evictions > 100/hour → Review TTL strategy, then consider clustering
- If downtime causes errors → Implement Sentinel for failover

### Estimated Effort (When Triggered)

- **Redis Cluster:** 2-3 days (setup, testing, application changes)
- **Redis Sentinel:** 1-2 days (failover only, simpler)

---

## Optimization 3: JSONB Query Performance

### Current Status: MONITOR (Indexes exist, load test needed)

### What Is It?

**Problem:** JSONB queries on `product_config.theme` or `content_translations.value` are slow.

**Solution (Deferred):** GIN indexes on JSONB columns.

### Phase 1: Basic Indexes (APPROVED)

```sql
-- Already in schema
CREATE INDEX idx_content_lookup
    ON content_translations(locale_code, content_id, is_published);

-- Optional (add if needed)
CREATE INDEX idx_product_theme_gin
    ON product_config USING GIN (theme);
```

### When to Implement (TRIGGERS)

#### Trigger 1: Query Latency > 100ms
```yaml
Condition: Content queries taking > 100ms at p95
How to Measure:
  - PostgreSQL slow query log
  - Application metrics: histogram_quantile(0.95, query_duration)
Action: Load test with 1000 concurrent users, measure query times
```

#### Trigger 2: EXPLAIN Shows Sequential Scan
```yaml
Condition: EXPLAIN ANALYZE shows Seq Scan on content_translations
How to Measure:
  - Run EXPLAIN ANALYZE on production queries
  - Look for "Seq Scan" instead of "Index Scan"
Action: Test queries after Phase 1 deployment
```

### How to Measure (Checklist)

**After Phase 1:**
- [ ] Run load test (1000 concurrent users)
- [ ] Capture p50, p95, p99 query latencies
- [ ] Run EXPLAIN ANALYZE on top 10 queries
- [ ] Check if GIN index on theme is being used

**Decision Point:**
- If p95 > 100ms → Add GIN indexes
- If seq scans detected → Add missing indexes
- If p95 < 50ms → No action needed

---

## Optimization 4: Database Read Replicas

### Current Status: DEFERRED (Single PostgreSQL sufficient)

### When to Implement (TRIGGERS)

#### Trigger 1: Database CPU > 70%
```yaml
Condition: PostgreSQL CPU consistently above 70%
How to Measure:
  - Server monitoring: top, htop
  - PostgreSQL stats: pg_stat_database
Action: Monitor after Phase 1 launch
```

#### Trigger 2: Query Queue Latency
```yaml
Condition: Queries waiting > 50ms for connection from pool
How to Measure:
  - SQLAlchemy pool metrics: pool_wait_time
  - PostgreSQL logs: connection wait time
Action: Monitor connection pool metrics
```

### Estimated Effort: 3-5 days

---

## Optimization 5: Content Scheduling (Publish at Specific Time)

### Current Status: DEFERRED TO PHASE 3

### What Is It?

**Problem:** Admins want to schedule content to publish at future date/time.

**Solution (Deferred):** Background job scheduler (APScheduler) + `publish_at` timestamp.

### Phase 1: Immediate Publish Only (APPROVED)

```python
# Content is published immediately when created/updated
async def create_content(key: str, locale: str, value: str):
    translation = ContentTranslation(
        content_id=content_id,
        locale_code=locale,
        value=value,
        is_published=True,  # Always true in Phase 1
        created_at=datetime.utcnow()
    )
    await db.add(translation)
```

### When to Implement (TRIGGERS)

#### Trigger 1: User Requests Scheduling
```yaml
Condition: 3+ requests from users for scheduled publishing
How to Measure:
  - User feedback
  - Feature requests
  - Support tickets
Action: Track feature requests in Phase 2
```

### Estimated Effort: 1-2 weeks (Phase 3 feature)

---

## How to Use This Document in Future Sessions

### For LLM (Claude Code):

**When user asks about performance:**
1. Read this document: `.claude/specs/DEFERRED-OPTIMIZATIONS-i18n-cms.md`
2. Check if they're reporting symptoms matching triggers
3. If YES → Suggest implementing the optimization
4. If NO → Remind them we deliberately deferred until metrics justify

**When planning Phase 1:**
1. Read this document to know what NOT to implement
2. Use simple patterns documented here
3. Add monitoring for triggers
4. Set up metrics collection for decision points

**When reviewing after Phase 1:**
1. Evaluate each optimization's triggers
2. Report which (if any) were activated
3. Recommend prioritization if multiple triggered

### Example Future Conversation:

```
User: "The app is slow when loading content"

LLM: Let me check the deferred optimizations document...

*Reads DEFERRED-OPTIMIZATIONS-i18n-cms.md*

LLM: I need to check if we hit any triggers:
1. What's the cache hit ratio? (Check Redis INFO)
2. What's p95 query latency? (Check Prometheus)
3. How many concurrent requests? (Check load testing)

If cache hit ratio < 50% → Implement stampede prevention
If p95 latency > 100ms → Add GIN indexes
If concurrent requests > 1000 → Implement stampede prevention

Can you share these metrics so I can recommend the right optimization?
```

---

## Decision Log

### 2025-11-08: Cache Stampede Prevention Deferred

**Decision:** Use simple cache-aside pattern in Phase 1, defer stampede prevention.

**Rationale:**
- Expected traffic: < 100 req/s (low-medium)
- Query cost: < 50ms (fast with indexes)
- Cache size: 256MB with 60x headroom (no pressure)
- Stampede prevention adds complexity (50+ lines, lock management)
- Simple pattern is proven, testable, maintainable

**Triggers Set:**
- Concurrent requests > 1000/s
- Cache hit ratio < 50%
- Query latency > 500ms
- Connection pool exhaustion

**Review Date:** After Phase 1 load testing

**Approved By:** User (explicit request to simplify and defer)

**References:**
- Architecture review conversation: 2025-11-08
- User quote: "we taking account redis caching in our setup to stay simple but utilize core backend data flow best practices"

---

## Monitoring Dashboard (Setup in Phase 1)

```yaml
Metrics to Track:
  Redis:
    - memory_used_bytes (gauge)
    - cache_hit_ratio (gauge)
    - evicted_keys_total (counter)
    - operations_per_second (gauge)

  Database:
    - query_duration_seconds (histogram)
    - slow_queries_total (counter)
    - connection_pool_size (gauge)
    - connection_pool_overflow (gauge)

  Application:
    - content_api_requests_total (counter)
    - content_api_duration_seconds (histogram)
    - cache_stampede_detected_total (counter) # Will always be 0 until implemented

  Alerts:
    - Cache hit ratio < 50% (warning)
    - Query p95 > 100ms (warning)
    - Redis memory > 200MB (warning)
    - Connection pool exhausted (critical)
```

---

**Document Status:** ACTIVE
**Next Review:** After Phase 1 load testing
**Owner:** Coordinator (track triggers, recommend implementation)
**Searchable Keywords:** deferred optimization, cache stampede, premature optimization, when to optimize, performance triggers


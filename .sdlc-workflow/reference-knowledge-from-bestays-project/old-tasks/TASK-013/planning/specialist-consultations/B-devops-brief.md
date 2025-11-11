# DevOps/Infrastructure Specialist Consultation Brief

## Context
TASK-013: Property V2 Schema Migration - PostgreSQL schema design and indexing strategy

We need to migrate from a basic property model to a comprehensive Property V2 schema with:
- 5 JSONB fields (physical_specs, location_details, amenities, policies, contact_info)
- property_translations table for multi-language support
- pgvector columns for future semantic search
- Complex indexing strategy (B-tree, GIN, future HNSW)

## Proposed Indexing Strategy

### B-tree Indexes (Exact Matches & Ranges)
```sql
CREATE INDEX idx_properties_is_published ON properties(is_published) WHERE is_published = true;
CREATE INDEX idx_properties_transaction_type ON properties(transaction_type);
CREATE INDEX idx_properties_property_type ON properties(property_type);
CREATE INDEX idx_properties_rent_price ON properties(rent_price) WHERE rent_price IS NOT NULL;
CREATE INDEX idx_properties_listing_priority ON properties(listing_priority DESC, created_at DESC);
```

### GIN Indexes (JSONB Queries)
```sql
CREATE INDEX idx_properties_amenities ON properties USING GIN (amenities);
CREATE INDEX idx_properties_physical_specs ON properties USING GIN (physical_specs);
CREATE INDEX idx_properties_location_details ON properties USING GIN (location_details);
CREATE INDEX idx_properties_tags ON properties USING GIN (tags);
```

### Future: pgvector Indexes
```sql
-- Deferred until embeddings are populated
-- CREATE INDEX idx_properties_embedding_en ON properties USING hnsw (description_embedding_en vector_cosine_ops);
-- CREATE INDEX idx_properties_embedding_th ON properties USING hnsw (description_embedding_th vector_cosine_ops);
```

## Questions for DevOps

1. **GIN vs GiST for JSONB:**
   - Is GIN the right choice for our JSONB query patterns (containment, path queries)?
   - When would GiST be better than GIN?
   - Should we use `jsonb_path_ops` for GIN indexes or default operator class?

2. **Index Creation Strategy:**
   - Should we use CREATE INDEX CONCURRENTLY for production migration?
   - What's the expected index creation time for 1k, 10k, 100k properties?
   - Can we create indexes in parallel or should it be sequential?
   - Any risk of locking issues during migration?

3. **Query Performance Benchmarking:**
   - How to benchmark JSONB query performance before launch?
   - What tools should we use (EXPLAIN ANALYZE, pg_stat_statements)?
   - What are acceptable query response times for property listing (with 24 results)?
   - Expected cache hit ratios for property queries?

4. **pgvector Integration:**
   - HNSW vs IVFFlat index type - which for our use case?
   - Should we add empty vector columns now or defer to later migration?
   - Separate embeddings per locale (en, th) or single multilingual embedding?
   - Expected query performance for semantic search (top 20 similar properties)?

5. **Migration Risk Assessment:**
   - What are the risks of this migration in production?
   - Rollback strategy if migration fails?
   - How to test migration safely (dry-run approach)?
   - Should we use transactions for the entire migration?

6. **Infrastructure Scaling:**
   - Will current PostgreSQL configuration handle this schema at scale?
   - Any PostgreSQL tuning parameters we should adjust?
   - Storage size estimates for 10k properties with full JSONB data?

## Deliverable
Infrastructure recommendations, indexing strategy, migration risk assessment, and performance benchmarks.

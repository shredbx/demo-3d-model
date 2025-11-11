# US-024: Advanced Semantic Search for Properties

**Domain:** properties
**Feature:** semantic-search
**Scope:** advanced
**Status:** READY (Future Enhancement)
**Created:** 2025-11-09
**Priority:** P2
**Default Product:** bestays
**Portable:** true
**Ported To:** []

---

## Description

Implement AI-powered semantic search that allows users to search for properties using natural language queries instead of traditional filters. Users can describe what they're looking for in plain English or Thai, and the system returns relevant properties using vector embeddings and semantic similarity.

**User Story:**
As a user, I want to search for properties using natural language (e.g., "cozy beachfront villa with pool near Phuket, good for families"), so that I can find properties that match my intent even if I don't know the exact filter terms.

**Examples:**
- "Modern apartment with good view near BTS"
- "Quiet villa for retirement, not too far from hospital"
- "Budget-friendly condo with gym and security"
- "ทาวน์เฮ้าส์ใกล้โรงเรียนนานาชาติ" (Townhouse near international school)

---

## Acceptance Criteria

### Phase 1: Basic Semantic Search
- [ ] AC-1: Search bar accepts natural language queries (EN/TH)
- [ ] AC-2: Backend generates embeddings for property descriptions using OpenRouter/OpenAI
- [ ] AC-3: Search queries converted to embeddings using same model
- [ ] AC-4: PostgreSQL pgvector extension performs similarity search
- [ ] AC-5: Results ranked by semantic similarity score (cosine similarity)
- [ ] AC-6: Minimum similarity threshold (e.g., 0.7) to filter irrelevant results

### Phase 2: Hybrid Search (Semantic + Filters)
- [ ] AC-7: Users can combine natural language with traditional filters (price, location)
- [ ] AC-8: Search results merge semantic matches + filter matches with boosted ranking
- [ ] AC-9: "Show me what you found" UI displays search interpretation

### Phase 3: Search Enhancement
- [ ] AC-10: Search suggestions based on popular queries
- [ ] AC-11: "Did you mean..." for typos and misspellings
- [ ] AC-12: Search analytics (track queries, clicks, conversions)
- [ ] AC-13: Periodic re-embedding for updated property descriptions

---

## Technical Notes

**Architecture:**
```
User Query → Embedding API → pgvector Search → Results Ranking → UI
```

**Tech Stack:**
- **Embedding Model:** text-embedding-3-small (OpenAI) or voyage-2 (via OpenRouter)
- **Vector Database:** PostgreSQL 16 + pgvector extension (already installed)
- **Similarity Metric:** Cosine similarity
- **Backend:** FastAPI endpoint `/api/v1/properties/search/semantic`

**Database Schema:**
```sql
-- Already exists in Property V2 schema
ALTER TABLE properties ADD COLUMN IF NOT EXISTS description_embedding vector(1536);

-- Index for fast similarity search
CREATE INDEX IF NOT EXISTS idx_properties_embedding
ON properties USING ivfflat (description_embedding vector_cosine_ops);
```

**Embedding Generation:**
- On property create/update: Generate embedding from title + description + amenities
- Store in `description_embedding` column
- Re-generate periodically for stale properties (> 30 days)

**API Endpoint:**
```typescript
POST /api/v1/properties/search/semantic
Body: {
  query: "cozy beachfront villa with pool",
  locale: "en",
  limit: 20,
  min_similarity: 0.7,
  filters?: { price_max: 50000, location: "Phuket" }
}

Response: {
  results: [
    { property: {...}, similarity_score: 0.92 },
    ...
  ],
  interpretation: "Looking for: beachfront properties with pool amenities"
}
```

**Cost Estimation:**
- Embedding generation: ~$0.0001 per property (one-time + updates)
- Search query embedding: ~$0.0001 per query
- For 10,000 properties: ~$1 initial + $0.10/1000 searches

**Dependencies:**
- US-023: Property V2 schema with pgvector (COMPLETED)
- US-018: Multi-product infrastructure (COMPLETED)
- OpenRouter/OpenAI API key

---

## Related Stories

- US-023: Property Display (provides data foundation)
- US-002: Homepage with Search (integrates semantic search UI)
- Future: US-XXX - Search Analytics & Recommendations

---

## Tasks

[Automatically populated by system - do not edit manually]

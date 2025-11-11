# pgvector + RAG Architecture

**Status:** Architectural Vision (TBD Implementation)
**Created:** 2025-11-09
**Scope:** System-Wide (Search, FAQ, Knowledge Base, AI Chat)
**Impact:** Database, LLM Integration, User Experience

---

## Overview

**pgvector** enables vector embeddings in PostgreSQL for semantic similarity search and RAG (Retrieval-Augmented Generation). This is a **foundational architecture** that powers multiple systems:

1. **Semantic Property Search** - Natural language queries with intent understanding
2. **FAQ System** - Contextual answers to user questions
3. **AI Chat (RAG)** - Knowledge-grounded responses from property data
4. **Knowledge Base** - Document retrieval and contextual information

---

## Why pgvector?

### Traditional Search Limitations
❌ **Keyword-only:** "beach villa" won't match "sea view house"
❌ **No synonyms:** "pet-friendly" won't match "animals allowed"
❌ **Language barrier:** English search won't match Thai descriptions
❌ **No context:** Can't understand "family-friendly" implies multiple bedrooms

### pgvector Advantages
✅ **Semantic understanding:** Finds similar meaning, not just keywords
✅ **Multi-language:** Embeddings work across English/Thai
✅ **Contextual:** Understands relationships and intent
✅ **Scalable:** Efficient indexing for millions of records
✅ **Native PostgreSQL:** No external vector database needed

---

## Architecture Components

### 1. Vector Embeddings

**What are embeddings?**
- Numerical representations of text (vectors)
- Similar meanings → similar vectors
- Dimension: 1536 (OpenAI ada-002) or 768 (sentence-transformers)

**Example:**
```python
# Text to embedding
text = "Beach view villa with private pool"
embedding = openai.embeddings.create(
    model="text-embedding-ada-002",
    input=text
).data[0].embedding

# Result: [0.023, -0.015, 0.032, ..., 0.008]  # 1536 dimensions
```

### 2. Database Schema

**Properties Table with Embeddings**
```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding column
ALTER TABLE bestays_properties_v2
ADD COLUMN embedding vector(1536),
ADD COLUMN embedding_model VARCHAR(50) DEFAULT 'text-embedding-ada-002',
ADD COLUMN embedding_updated_at TIMESTAMP;

-- Create indexes (choose one strategy below)

-- OPTION A: IVFFLAT (Inverted File with Flat compression)
-- Pros: Fast, memory-efficient, good for 10k-1M records
-- Cons: Slightly lower recall than HNSW
CREATE INDEX idx_properties_v2_embedding ON bestays_properties_v2
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- OPTION B: HNSW (Hierarchical Navigable Small World)
-- Pros: Better recall, faster queries
-- Cons: More memory, slower indexing
-- CREATE INDEX idx_properties_v2_embedding ON bestays_properties_v2
-- USING hnsw (embedding vector_cosine_ops)
-- WITH (m = 16, ef_construction = 64);

-- Composite index for hybrid search (vector + filters)
CREATE INDEX idx_properties_v2_hybrid ON bestays_properties_v2 (rent_price, property_type)
WHERE is_published = true;
```

**FAQ Table with Embeddings**
```sql
CREATE TABLE faq (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  category VARCHAR(50), -- 'booking', 'property', 'payment', 'policies'
  locale VARCHAR(5) NOT NULL, -- 'en', 'th'
  embedding vector(1536),
  embedding_model VARCHAR(50) DEFAULT 'text-embedding-ada-002',
  is_published BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_faq_embedding ON faq
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 50);

CREATE INDEX idx_faq_category ON faq (category, locale) WHERE is_published = true;
```

**Knowledge Base Table (for RAG)**
```sql
CREATE TABLE knowledge_base (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content TEXT NOT NULL,
  content_type VARCHAR(50), -- 'property_description', 'policy_doc', 'agent_guide'
  source_id UUID, -- Reference to property/document/guide
  chunk_index INTEGER, -- For chunked documents
  metadata JSONB, -- Additional context
  embedding vector(1536),
  embedding_model VARCHAR(50) DEFAULT 'text-embedding-ada-002',
  locale VARCHAR(5) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_knowledge_base_embedding ON knowledge_base
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX idx_knowledge_base_source ON knowledge_base (source_id, chunk_index);
```

### 3. Embedding Generation Service

**Backend Service (FastAPI)**
```python
# apps/server/src/services/embeddings/generator.py

from openai import AsyncOpenAI
from typing import List
import numpy as np

class EmbeddingGenerator:
    """Generate and cache embeddings for text content."""

    def __init__(self):
        self.client = AsyncOpenAI()
        self.model = "text-embedding-ada-002"
        self.cache = {}  # Redis cache in production

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for single text."""
        # Check cache first
        cache_key = f"emb:{hash(text)}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Generate embedding
        response = await self.client.embeddings.create(
            model=self.model,
            input=text
        )
        embedding = response.data[0].embedding

        # Cache for future use
        self.cache[cache_key] = embedding
        return embedding

    async def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (more efficient)."""
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]

    def generate_property_embedding(self, property: Property) -> str:
        """
        Generate comprehensive text representation for property embedding.

        Combines:
        - Title and description
        - Property type and location
        - Key amenities
        - Price and policies
        """
        text_parts = [
            property.title,
            property.description,
            f"Property type: {property.property_type}",
            f"Location: {property.location_details.get('district')}",
            f"Price: {property.rent_price} THB/month",
        ]

        # Add amenities
        amenities = []
        for category in ['interior', 'exterior', 'building']:
            if items := property.amenities.get(category):
                amenities.extend([item['name'] for item in items])
        if amenities:
            text_parts.append(f"Amenities: {', '.join(amenities)}")

        # Add policies
        if property.policies:
            if property.policies.get('pets_allowed'):
                text_parts.append("Pets allowed")
            if property.policies.get('smoking_allowed'):
                text_parts.append("Smoking allowed")

        return " | ".join(text_parts)
```

**Async Background Job (Celery)**
```python
# apps/server/src/tasks/embeddings.py

@celery.task
async def generate_property_embeddings(property_ids: List[UUID]):
    """Background task to generate embeddings for properties."""
    generator = EmbeddingGenerator()

    for prop_id in property_ids:
        property = await get_property(prop_id)

        # Generate text representation
        text = generator.generate_property_embedding(property)

        # Generate embedding
        embedding = await generator.generate_embedding(text)

        # Update database
        await db.execute(
            """
            UPDATE bestays_properties_v2
            SET embedding = $1,
                embedding_updated_at = NOW()
            WHERE id = $2
            """,
            embedding,
            prop_id
        )
```

### 4. Vector Similarity Search

**Query Properties by Semantic Similarity**
```python
# apps/server/src/services/search/vector_search.py

class VectorSearch:
    """Perform semantic similarity search using pgvector."""

    async def search_properties(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict] = None,
        min_similarity: float = 0.7
    ) -> List[Property]:
        """
        Search properties by semantic similarity.

        Args:
            query: Natural language search query
            limit: Max results to return
            filters: Additional SQL filters (price, bedrooms, etc.)
            min_similarity: Minimum cosine similarity threshold (0-1)

        Returns:
            List of properties ranked by similarity
        """
        # Generate query embedding
        generator = EmbeddingGenerator()
        query_embedding = await generator.generate_embedding(query)

        # Build SQL query
        sql = """
        SELECT
            id,
            title,
            description,
            rent_price,
            1 - (embedding <=> $1::vector) AS similarity
        FROM bestays_properties_v2
        WHERE is_published = true
            AND 1 - (embedding <=> $1::vector) >= $2
        """

        # Add filters
        params = [query_embedding, min_similarity]
        if filters:
            if price_max := filters.get('price_max'):
                sql += f" AND rent_price <= ${len(params) + 1}"
                params.append(price_max)
            if bedrooms := filters.get('bedrooms'):
                sql += f" AND (physical_specs->>'rooms'->>'bedrooms')::int >= ${len(params) + 1}"
                params.append(bedrooms)

        sql += f" ORDER BY similarity DESC LIMIT ${len(params) + 1}"
        params.append(limit)

        # Execute query
        results = await db.fetch(sql, *params)
        return [Property(**row) for row in results]

    async def hybrid_search(
        self,
        query: str,
        limit: int = 10,
        vector_weight: float = 0.7,
        fulltext_weight: float = 0.3
    ) -> List[Property]:
        """
        Combine vector similarity with full-text search.

        Hybrid approach:
        - Vector search captures semantic meaning
        - Full-text search captures exact keywords
        - Weighted combination for best results
        """
        # Vector similarity score
        query_embedding = await EmbeddingGenerator().generate_embedding(query)

        sql = """
        SELECT
            id,
            title,
            description,
            rent_price,
            (
                ($2 * (1 - (embedding <=> $1::vector))) +
                ($3 * ts_rank(to_tsvector('english', title || ' ' || description), plainto_tsquery($4)))
            ) AS combined_score
        FROM bestays_properties_v2
        WHERE is_published = true
        ORDER BY combined_score DESC
        LIMIT $5
        """

        results = await db.fetch(
            sql,
            query_embedding,
            vector_weight,
            fulltext_weight,
            query,
            limit
        )
        return [Property(**row) for row in results]
```

### 5. RAG (Retrieval-Augmented Generation)

**Chat with Knowledge Base Context**
```python
# apps/server/src/services/chat/rag.py

class RAGService:
    """RAG service for knowledge-grounded chat responses."""

    async def chat_with_context(
        self,
        user_query: str,
        conversation_history: List[Message],
        max_context_chunks: int = 3
    ) -> ChatResponse:
        """
        Generate chat response grounded in relevant knowledge.

        Process:
        1. Generate embedding for user query
        2. Retrieve most relevant knowledge chunks (vector search)
        3. Build context prompt with retrieved knowledge
        4. Send to LLM (OpenRouter) for response
        5. Return response with citations
        """
        # 1. Generate query embedding
        generator = EmbeddingGenerator()
        query_embedding = await generator.generate_embedding(user_query)

        # 2. Retrieve relevant knowledge chunks
        knowledge_chunks = await db.fetch(
            """
            SELECT
                content,
                content_type,
                source_id,
                metadata,
                1 - (embedding <=> $1::vector) AS similarity
            FROM knowledge_base
            WHERE locale = $2
            ORDER BY similarity DESC
            LIMIT $3
            """,
            query_embedding,
            "en",  # or detect from user query
            max_context_chunks
        )

        # 3. Build context prompt
        context = "\n\n".join([
            f"[Source: {chunk['content_type']}]\n{chunk['content']}"
            for chunk in knowledge_chunks
        ])

        prompt = f"""
        You are a helpful assistant for Bestays property rentals.
        Use the following context to answer the user's question.
        If the context doesn't contain relevant information, say so.

        Context:
        {context}

        Conversation history:
        {format_conversation(conversation_history)}

        User question: {user_query}

        Answer:
        """

        # 4. Send to LLM
        response = await openrouter.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        # 5. Return with citations
        return ChatResponse(
            message=response.choices[0].message.content,
            sources=[
                Source(
                    content_type=chunk['content_type'],
                    source_id=chunk['source_id'],
                    similarity=chunk['similarity']
                )
                for chunk in knowledge_chunks
            ]
        )
```

### 6. FAQ System

**Semantic FAQ Lookup**
```python
# apps/server/src/api/v1/faq.py

@router.get("/api/v1/faq/search")
async def search_faq(
    query: str,
    locale: str = "en",
    limit: int = 5
) -> List[FAQItem]:
    """
    Search FAQ using semantic similarity.

    Example:
        query: "Can I bring my dog?"
        → Matches: "Are pets allowed in the properties?"
    """
    # Generate query embedding
    generator = EmbeddingGenerator()
    query_embedding = await generator.generate_embedding(query)

    # Search FAQ
    results = await db.fetch(
        """
        SELECT
            id,
            question,
            answer,
            category,
            1 - (embedding <=> $1::vector) AS similarity
        FROM faq
        WHERE locale = $2
            AND is_published = true
            AND 1 - (embedding <=> $1::vector) >= 0.6
        ORDER BY similarity DESC
        LIMIT $3
        """,
        query_embedding,
        locale,
        limit
    )

    return [FAQItem(**row) for row in results]
```

---

## Index Optimization Strategies

### IVFFLAT vs HNSW

**IVFFLAT (Inverted File with Flat compression)**
- **Best for:** 10k - 1M records, memory-constrained systems
- **Pros:** Fast, memory-efficient, good enough for most use cases
- **Cons:** Slightly lower recall (~95%)
- **Config:** `lists` = √(total_records), e.g., 100 for 10k records

**HNSW (Hierarchical Navigable Small World)**
- **Best for:** 100k+ records, high-recall requirements
- **Pros:** Better recall (>99%), faster queries
- **Cons:** 2-3x more memory, slower indexing
- **Config:** `m` (links per node, default 16), `ef_construction` (build quality, default 64)

### Tuning Parameters

**IVFFLAT:**
```sql
-- For 10,000 records
CREATE INDEX ... WITH (lists = 100);

-- For 100,000 records
CREATE INDEX ... WITH (lists = 316);

-- For 1,000,000 records
CREATE INDEX ... WITH (lists = 1000);

-- Query-time tuning (trade speed for recall)
SET ivfflat.probes = 10;  -- Default: 1, higher = better recall
```

**HNSW:**
```sql
-- Default (balanced)
CREATE INDEX ... WITH (m = 16, ef_construction = 64);

-- High recall (more memory, slower build)
CREATE INDEX ... WITH (m = 32, ef_construction = 128);

-- Fast build (less memory, slightly lower recall)
CREATE INDEX ... WITH (m = 8, ef_construction = 32);

-- Query-time tuning
SET hnsw.ef_search = 40;  -- Default: ef_construction, higher = better recall
```

### Hybrid Indexing Strategy

**Combine pgvector with traditional indexes:**
```sql
-- Vector index for semantic search
CREATE INDEX idx_properties_embedding ON bestays_properties_v2
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Full-text index for keyword search
CREATE INDEX idx_properties_fulltext ON bestays_properties_v2
USING GIN (to_tsvector('english', title || ' ' || description));

-- JSONB index for structured filters
CREATE INDEX idx_properties_amenities ON bestays_properties_v2
USING GIN (amenities jsonb_path_ops);

-- B-tree indexes for range queries
CREATE INDEX idx_properties_price ON bestays_properties_v2 (rent_price)
WHERE is_published = true;
```

### Partial Indexes

**Only index published properties:**
```sql
CREATE INDEX idx_properties_embedding_published ON bestays_properties_v2
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)
WHERE is_published = true AND embedding IS NOT NULL;
```

---

## Best Practices

### 1. Embedding Generation

**✅ DO:**
- Generate embeddings asynchronously (background jobs)
- Batch embeddings (OpenAI allows up to 2048 inputs per request)
- Cache embeddings (Redis)
- Update embeddings when content changes (trigger or cron)
- Include rich context (title + description + amenities)

**❌ DON'T:**
- Generate embeddings synchronously on user requests
- Embed individual words (embed full sentences/paragraphs)
- Forget to normalize text (lowercase, remove special chars)
- Exceed token limits (8191 tokens for ada-002)

### 2. Search Quality

**✅ DO:**
- Use hybrid search (vector + full-text) for best results
- Set minimum similarity threshold (0.6-0.7 for general search, 0.8+ for strict matching)
- Limit results (10-20 max to avoid overloading user)
- Show similarity scores to users (optional)
- A/B test search relevance

**❌ DON'T:**
- Rely on vector search alone (miss exact keyword matches)
- Return low-similarity results (<0.5 is usually irrelevant)
- Show too many results (information overload)

### 3. RAG Implementation

**✅ DO:**
- Chunk documents into 200-500 tokens (optimal for context)
- Include metadata (source, timestamp, category)
- Retrieve 3-5 chunks (balance context vs token usage)
- Cite sources in responses
- Handle "no relevant context" gracefully

**❌ DON'T:**
- Chunk too small (<100 tokens, loses context)
- Chunk too large (>1000 tokens, dilutes relevance)
- Retrieve too many chunks (exceeds LLM context window)
- Return hallucinated answers (always ground in retrieved context)

### 4. Performance

**✅ DO:**
- Use connection pooling (asyncpg)
- Cache frequent queries (Redis)
- Monitor query latency (<100ms target for vector search)
- Pre-compute embeddings (don't generate on-the-fly)
- Use EXPLAIN ANALYZE to optimize queries

**❌ DON'T:**
- Generate embeddings in request path (use background jobs)
- Query without filters (always add WHERE clauses)
- Forget to vacuum/analyze (pgvector indexes need maintenance)

---

## Implementation Phases

### Phase 1: Foundation (US-022, US-023)
- [ ] Add pgvector extension to database
- [ ] Add embedding columns to properties table
- [ ] Create embedding generation service
- [ ] Background job for bulk embedding generation
- [ ] Basic vector similarity search API

### Phase 2: Semantic Search (US-027)
- [ ] Hybrid search (vector + full-text)
- [ ] Search results ranking
- [ ] A/B testing framework
- [ ] Performance monitoring

### Phase 3: FAQ System (US-028)
- [ ] Create FAQ table with embeddings
- [ ] FAQ search API
- [ ] Admin interface for FAQ management
- [ ] Auto-suggest FAQ in chat

### Phase 4: RAG for Chat (US-029)
- [ ] Create knowledge base table
- [ ] Document chunking service
- [ ] RAG chat endpoint
- [ ] Citation/source attribution
- [ ] Conversational context management

### Phase 5: Optimization (US-030)
- [ ] Index tuning (IVFFLAT → HNSW if needed)
- [ ] Embedding model evaluation (ada-002 vs alternatives)
- [ ] Multi-language embeddings (EN/TH)
- [ ] Cost optimization (caching, batch processing)

---

## Cost Analysis

### Embedding Generation Costs

**OpenAI text-embedding-ada-002:**
- $0.0001 per 1,000 tokens
- Average property: ~500 tokens
- Cost per property: $0.00005 (0.005 cents)
- 10,000 properties: $0.50
- 100,000 properties: $5.00

**Update frequency:**
- Initial generation: One-time cost
- Updates: Only when property changes (~10% per month)
- Monthly cost for 10k properties: $0.05

### Search Costs

**pgvector (self-hosted):**
- Free (open-source)
- Only database resources (CPU, memory, storage)

**Alternative (external vector DB like Pinecone):**
- ~$70-$200/month for 100k vectors
- Additional latency (network roundtrip)

**Winner:** pgvector (native PostgreSQL, no extra costs)

---

## Related Documentation

- `.sdlc-workflow/guides/semantic-search-architecture.md` - Semantic property search
- `.sdlc-workflow/guides/chat-driven-ui-architecture.md` - Chat-driven field suggestions
- `.sdlc-workflow/guides/ai-agent-workflow-pattern.md` - AI safety model

---

## Questions for Planning

1. **Embedding model:** OpenAI ada-002 (1536 dims) or sentence-transformers (768 dims)?
   - Ada-002: Better quality, external API
   - Sentence-transformers: Free, self-hosted, faster

2. **Index strategy:** Start with IVFFLAT or go straight to HNSW?
   - IVFFLAT: Simpler, good enough for MVP
   - HNSW: Better long-term, higher memory

3. **Update strategy:** Real-time or batch?
   - Real-time: Embedding on every property create/update (slower)
   - Batch: Background job every N minutes (more efficient)

4. **Multi-language:** Separate embeddings for EN/TH or multilingual model?
   - Separate: Better quality per language
   - Multilingual: Single embedding for both (ada-002 supports this)

---

**Version:** 1.0
**Status:** Architectural Vision (Not Yet Implemented)
**Next Review:** During RESEARCH phase of US-022 (TASK-012)

# RAG Architecture Analysis for Property Extraction

**Date:** 2025-11-06
**Purpose:** Design RAG system for LLM-powered property attribute detection
**Scope:** 165+ amenities, 81 location advantages, property types & conditions

---

## 1. Knowledge Base Design

Embed **catalogue_options** table (amenities, location advantages, property types, conditions) with descriptions as foundational knowledge. Single unified `catalogue_embeddings` table stores vectorized metadata: option ID, name, description, category (interior/exterior/building/utilities/location), property_type filters (villa/house/apartment). Embeddings refresh monthly via scheduled task. This enables semantic matching when LLM detects property attributes from images, text, or user input—e.g., matching "infinity pool" → `am_ext_private_pool`, or "peaceful neighborhood" → `loc_quiet_area`. Store raw text descriptions alongside vectors for context injection into LLM prompts.

---

## 2. Embedding Strategy

Use **OpenAI ada-002** model (1536-dimensional embeddings, matches existing pgvector schema). Embed compound documents: **"[Category] - [Option Name]: [Description]"** format for each catalogue_option. Example: "Building Amenities - 24h Security: Round-the-clock security staffed premises". This structured format improves semantic search for both exact matches and synonyms. Batch embed 400+ options monthly at ~$0.02/1k tokens. Store embedding cost (usage tracking) in `embedding_logs` table for cost monitoring.

---

## 3. Retrieval

**Cosine similarity search** via pgvector `<=>` operator. Top-K retrieval (K=10) returns nearest neighbours ranked by similarity score (threshold: 0.7). Add **metadata filters** in WHERE clause: filter by `category` (if user specifies amenity category) and `property_type` (if property type known). Example query: retrieve interior amenities relevant to "villa" properties with "ac" in semantic space. Hybrid approach: combine semantic + keyword matching for robustness (e.g., exact "air conditioning" match takes precedence). Results feed LLM context for confirmation/selection.

---

## 4. SQL Schema

```sql
CREATE TABLE catalogue_embeddings (
    id VARCHAR(50) PRIMARY KEY,
    catalogue_id VARCHAR(50) NOT NULL REFERENCES catalogues(id) ON DELETE CASCADE,
    option_id VARCHAR(50) NOT NULL REFERENCES catalogue_options(id) ON DELETE CASCADE,

    -- Content
    option_name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50),

    -- Vector
    embedding VECTOR(1536) NOT NULL,
    embedding_model VARCHAR(50) DEFAULT 'ada-002',

    -- Metadata filters
    property_type VARCHAR(50),
    region VARCHAR(100),
    is_active BOOLEAN DEFAULT true,

    -- Tracking
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_embedded_at TIMESTAMPTZ,

    UNIQUE(option_id)
);

CREATE INDEX idx_catalogue_embeddings_vector ON catalogue_embeddings USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_catalogue_embeddings_category ON catalogue_embeddings(category);
CREATE INDEX idx_catalogue_embeddings_property_type ON catalogue_embeddings(property_type);
CREATE INDEX idx_catalogue_embeddings_is_active ON catalogue_embeddings(is_active);

CREATE TABLE embedding_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    catalogue_id VARCHAR(50),
    batch_size INTEGER,
    tokens_used INTEGER,
    cost_usd DECIMAL(10, 4),
    status VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 5. Code Example

```python
from typing import List, Dict
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from pgvector.sqlalchemy import Vector
from server.core.database import async_session
from server.models import CatalogueEmbeddings
from server.core.llm import OpenRouterClient

async def retrieve_similar_amenities(query: str, top_k: int = 10, category: str = None, property_type: str = None) -> List[Dict]:
    """Retrieve semantically similar amenities using RAG."""

    # 1. Generate embedding for user query
    llm = OpenRouterClient()
    query_embedding = await llm.embed_text(query)

    async with async_session() as session:
        # 2. Build search query with filters
        stmt = select(CatalogueEmbeddings).where(
            and_(
                CatalogueEmbeddings.is_active == True,
                CatalogueEmbeddings.embedding.cosine_distance(query_embedding) < 0.3  # similarity > 0.7
            )
        )

        # 3. Apply optional filters
        if category:
            stmt = stmt.where(CatalogueEmbeddings.category == category)
        if property_type:
            stmt = stmt.where(CatalogueEmbeddings.property_type == property_type)

        # 4. Order by similarity and limit
        stmt = stmt.order_by(
            CatalogueEmbeddings.embedding.cosine_distance(query_embedding)
        ).limit(top_k)

        results = await session.execute(stmt)
        embeddings = results.scalars().all()

        # 5. Format response with context
        return [
            {
                "id": e.option_id,
                "name": e.option_name,
                "description": e.description,
                "category": e.category,
                "similarity_score": 1 - (e.embedding.cosine_distance(query_embedding)),
                "catalogue_id": e.catalogue_id
            }
            for e in embeddings
        ]

async def extract_property_amenities(property_text: str, property_type: str = None) -> Dict[str, List[str]]:
    """Extract amenities from property description using LLM + RAG."""

    # Retrieve relevant amenities from knowledge base
    interior = await retrieve_similar_amenities(
        property_text,
        category="interior",
        property_type=property_type,
        top_k=15
    )
    exterior = await retrieve_similar_amenities(
        property_text,
        category="exterior",
        property_type=property_type,
        top_k=15
    )
    building = await retrieve_similar_amenities(
        property_text,
        category="building",
        property_type=property_type,
        top_k=15
    )

    # Inject into LLM prompt for confirmation
    llm = OpenRouterClient()
    prompt = f"""
    Property description: {property_text}

    Detected amenities (candidate list):
    Interior: {', '.join([a['name'] for a in interior])}
    Exterior: {', '.join([a['name'] for a in exterior])}
    Building: {', '.join([a['name'] for a in building])}

    Select which amenities are ACTUALLY present in this property.
    Return as JSON: {{"interior": [...], "exterior": [...], "building": [...]}}
    """

    response = await llm.generate(prompt)
    return response.json()
```

---

## 6. MVP Scope

- **Phase 1 (MVP):** Embed **amenities only** (165 options: interior 47 + exterior 44 + building 44 + utilities 27)
  - Skip location advantages until Phase 2
  - Use simple cosine similarity (K=10)
  - Manual validation workflow
  - Cost: ~$0.30 initial embedding

- **Phase 2:** Location advantages (81 options), fine-tuning LLM with feedback
- **Phase 3:** Real-time streaming extraction, multi-modal (images), feedback loop optimization

---

## 7. Cost Analysis

| Item | Cost | Notes |
|------|------|-------|
| Embed 400 catalogue options (ada-002) | $0.30 | One-time; 50k tokens @ $0.10/1M |
| Monthly re-embedding (incremental) | $0.02 | ~5k new/modified options |
| Storage: 400 embeddings (1536-dim) | Included | ~2.4 MB (pgvector native) |
| Query cost (semantic search) | $0 | Pure DB; no API calls |
| **Total monthly (after MVP)** | **$0.02** | Negligible if batched |

---

## Integration Points

**Backend:** FastAPI endpoint `POST /api/v2/properties/extract-amenities` accepts property text + type, returns ranked amenities list via RAG retrieval + LLM confirmation.

**Frontend:** Chat interface calls endpoint, displays suggested amenities with confidence scores, user confirms selection.

**Database:** `catalogue_embeddings` auto-populated via migration; quarterly refresh via scheduled task.

---

**Status:** Ready for implementation
**Next Step:** Create Alembic migration for `catalogue_embeddings` table

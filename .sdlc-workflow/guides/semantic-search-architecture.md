# Semantic Search Architecture

**Status:** Architectural Vision (TBD Implementation)
**Created:** 2025-11-09
**Scope:** Homepage + Property Search
**Impact:** Search Experience, LLM Integration, Property Schema

---

## Vision

Natural language property search where users describe what they need in plain English/Thai, and the system understands intent, constraints, and preferences to return relevant results with intelligent suggestions.

**Example Queries:**
- "beach view villa on the island and i have 2 dogs and i smoke"
- "3 bedroom house near school with garden, budget 30k/month"
- "modern condo with pool and gym, walking distance to BTS"
- "ที่พักใกล้ทะเล สามารถเลี้ยงสัตว์ได้" (Thai: accommodation near beach, pets allowed)

**System Response:**
- Parse natural language → extract structured filters
- Apply semantic understanding (synonyms, intent, context)
- Return matching properties
- Provide intelligent suggestions ("Did you mean...", "You might also like...")

---

## Core Principles

### 1. Natural Language Understanding
- Users don't need to know property terminology
- System understands casual language, typos, abbreviations
- Multi-language support (EN/TH)
- Contextual understanding (e.g., "island" in Koh Phangan context = specific locations)

### 2. Intelligent Parsing
- Extract structured filters from unstructured text
- Identify explicit constraints (bedrooms, budget, location)
- Identify implicit preferences (lifestyle, priorities)
- Handle complex queries with multiple requirements

### 3. Semantic Matching
- Beyond keyword matching → understand intent
- Synonyms: "beach view" = "sea view" = "ocean view"
- Related concepts: "family-friendly" implies pet-friendly, safe neighborhood, near school
- Negative filters: "i smoke" → filter out non-smoking properties

---

## Architecture Components

### Frontend (SvelteKit)

**1. Semantic Search Input (Homepage)**
```svelte
<!-- apps/frontend/src/routes/[locale]/+page.svelte -->
<SemanticSearchBar
  placeholder="Try: 'beach view villa with pool, pets allowed'"
  onSearch={handleSemanticSearch}
  showSuggestions={true}
  suggestions={recentSearches}
/>
```

**Features:**
- Large, prominent search bar on homepage hero
- Auto-suggestions as user types (recent searches, popular queries)
- Voice input support (future)
- Multi-language placeholder text

**2. Search Results Page**
```svelte
<!-- apps/frontend/src/routes/[locale]/search/+page.svelte -->
<SearchResults
  query={semanticQuery}
  parsedFilters={extractedFilters}
  properties={results}
  suggestions={intelligentSuggestions}
/>
```

**Shows:**
- Parsed query breakdown ("Showing results for: Beach view + Villa + Pets allowed + Smoking allowed")
- Result count
- Filter adjustments ("Try removing 'smoking allowed' to see 15 more results")
- Related searches

### Backend (FastAPI)

**1. Semantic Search API**
```python
# apps/server/src/api/v1/search/semantic.py

@router.post("/api/v1/search/semantic")
async def semantic_property_search(
    query: str,
    locale: str = "en",
    user: Optional[User] = Depends(get_optional_user)
) -> SemanticSearchResponse:
    """
    Natural language property search.

    Process:
    1. Parse natural language query via LLM (OpenRouter)
    2. Extract structured filters (bedrooms, price, amenities, policies)
    3. Apply semantic matching (synonyms, related concepts)
    4. Query property database with filters
    5. Rank results by relevance
    6. Generate intelligent suggestions

    Example:
        Input: "beach view villa on the island and i have 2 dogs and i smoke"

        Parsed Filters:
        - location: ["near_beach", "island"]
        - property_type: ["villa"]
        - amenities: ["sea_view", "beach_view"]
        - policies.pets_allowed: true
        - policies.smoking_allowed: true

        Results: 3 matching properties
        Suggestions:
        - "Remove 'smoking allowed' to see 12 more results"
        - "Also try: beachfront apartments with pet-friendly policies"
    """
    pass
```

**2. LLM Query Parser**
```python
# apps/server/src/services/llm/query_parser.py

class SemanticQueryParser:
    """Parse natural language search queries into structured filters."""

    async def parse_query(self, query: str, locale: str) -> ParsedQuery:
        """
        Use LLM (OpenRouter) to extract structured data from natural language.

        Prompt example:
        '''
        Parse this property search query into structured JSON filters.
        Use the property dictionary schema for amenities and policies.

        Query: "beach view villa on the island and i have 2 dogs and i smoke"

        Return JSON:
        {
          "location": ["near_beach", "island"],
          "property_type": ["villa"],
          "amenities": ["sea_view", "beach_view"],
          "policies": {
            "pets_allowed": true,
            "smoking_allowed": true
          },
          "confidence": 0.95,
          "ambiguities": []
        }
        '''
        """
        pass

    def expand_synonyms(self, filters: ParsedQuery) -> ParsedQuery:
        """
        Expand filters with synonyms and related concepts.

        Example:
        - "beach view" → ["sea_view", "ocean_view", "beach_view", "water_view"]
        - "family-friendly" → ["pets_allowed", "safe_neighborhood", "near_school"]
        """
        pass

    def handle_ambiguities(self, filters: ParsedQuery) -> List[Suggestion]:
        """
        Generate suggestions for ambiguous queries.

        Example:
        - Query: "2 bedroom" (didn't specify budget)
          → Suggestion: "What's your budget? (฿10k-20k, ฿20k-30k, ฿30k+)"
        """
        pass
```

**3. Semantic Matching Engine**
```python
# apps/server/src/services/search/semantic_matcher.py

class SemanticMatcher:
    """Match properties using semantic understanding."""

    def build_query(self, parsed: ParsedQuery) -> PropertyQuery:
        """
        Build database query with semantic filters.

        Uses:
        - PostgreSQL full-text search (tsvector)
        - JSONB queries for amenities/policies
        - PostGIS for location-based search (future)
        - Similarity scoring (trigram, fuzzy matching)
        """
        pass

    def rank_results(self, results: List[Property], query: ParsedQuery) -> List[Property]:
        """
        Rank results by relevance score.

        Scoring factors:
        - Exact matches (higher weight)
        - Semantic matches (medium weight)
        - Partial matches (lower weight)
        - Recency (newer listings ranked higher)
        - User preferences (if authenticated)
        """
        pass
```

**4. Suggestion Generator**
```python
# apps/server/src/services/search/suggestion_generator.py

class SuggestionGenerator:
    """Generate intelligent suggestions for search refinement."""

    def generate_suggestions(
        self,
        query: ParsedQuery,
        result_count: int,
        all_properties_count: int
    ) -> List[Suggestion]:
        """
        Generate suggestions based on search results.

        Types:
        1. Relaxation suggestions (if few results)
           - "Try removing 'smoking allowed' to see 15 more results"
           - "Expand budget range to ฿35k to see 8 more properties"

        2. Refinement suggestions (if too many results)
           - "Narrow down by adding 'with pool' or 'modern style'"

        3. Alternative suggestions
           - "You might also like: beachfront apartments"
           - "Similar properties in nearby areas: Thong Sala, Haad Rin"

        4. Related searches
           - "Other users also searched for: pet-friendly villas with garden"
        """
        pass
```

### Database Schema Extensions

**Property V2 Schema Updates (Required for Semantic Search)**

```sql
-- === FULL-TEXT SEARCH (Traditional) ===
-- For keyword-based search
CREATE INDEX idx_properties_v2_fulltext ON bestays_properties_v2
USING GIN (to_tsvector('english', title || ' ' || description));

CREATE INDEX idx_properties_v2_fulltext_thai ON bestays_properties_v2
USING GIN (to_tsvector('thai', title || ' ' || description));

-- === TRIGRAM (Fuzzy Matching) ===
-- For typo tolerance and partial matches
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_properties_v2_title_trgm ON bestays_properties_v2
USING GIN (title gin_trgm_ops);

-- === JSONB (Structured Queries) ===
-- For filtering by amenities, policies, location
CREATE INDEX idx_properties_v2_amenities_semantic ON bestays_properties_v2
USING GIN (amenities jsonb_path_ops);

CREATE INDEX idx_properties_v2_policies_semantic ON bestays_properties_v2
USING GIN (policies jsonb_path_ops);

CREATE INDEX idx_properties_v2_location_semantic ON bestays_properties_v2
USING GIN (location_details jsonb_path_ops);

-- === PGVECTOR (Semantic Embeddings) ===
-- For RAG, semantic similarity, and best-in-class search
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding column to properties
ALTER TABLE bestays_properties_v2
ADD COLUMN embedding vector(1536); -- OpenAI ada-002 or similar

-- Create IVFFLAT index for fast similarity search
-- (Use HNSW for better recall, but IVFFLAT is simpler to start)
CREATE INDEX idx_properties_v2_embedding ON bestays_properties_v2
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Alternative: HNSW index (better recall, more memory)
-- CREATE INDEX idx_properties_v2_embedding ON bestays_properties_v2
-- USING hnsw (embedding vector_cosine_ops)
-- WITH (m = 16, ef_construction = 64);
```

**Why pgvector?**
- Semantic similarity search (understand intent, not just keywords)
- RAG (Retrieval-Augmented Generation) for AI chat
- FAQ system with contextual answers
- Multi-language support (embeddings work across languages)
- Best-in-class search experience

**Search History Tracking (Optional)**

```sql
CREATE TABLE search_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  raw_query TEXT NOT NULL,
  parsed_filters JSONB NOT NULL,
  result_count INTEGER NOT NULL,
  clicked_property_id UUID REFERENCES bestays_properties_v2(id),
  locale VARCHAR(5) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_search_history_user ON search_history(user_id);
CREATE INDEX idx_search_history_query ON search_history USING GIN (to_tsvector('english', raw_query));
```

### Chat Integration

**Chat can also perform semantic search:**

```typescript
// User in chat: "Find me a villa with beach view and pet-friendly"
// Chat calls same semantic search API
// Returns inline results in chat interface
// User can refine search via follow-up questions

Chat: "I found 5 villas matching your criteria. Would you like to see them?"
User: "Yes, but only with private pool"
Chat: [Calls semantic search with added filter] "Here are 3 villas with private pool"
```

### MCP Integration (External LLM Access)

**Allow external LLMs to search properties via MCP:**

```typescript
// .claude/mcp/property-search-mcp/tools.ts

{
  name: "semantic-property-search",
  description: "Search properties using natural language",
  inputSchema: {
    type: "object",
    properties: {
      query: { type: "string", description: "Natural language search query" },
      locale: { type: "string", enum: ["en", "th"], default: "en" }
    },
    required: ["query"]
  }
}

// External LLM (e.g., ChatGPT) can call this tool:
// User: "I'm looking for a place in Koh Phangan with beach view"
// ChatGPT: [Calls semantic-property-search MCP tool]
// Returns: Results from Bestays database
```

### llm.txt File (Context for External LLMs)

**Provide context for external LLMs accessing our search:**

```
# apps/frontend/static/llm.txt

# Bestays Property Search

## Overview
Bestays offers vacation rentals in Koh Phangan, Thailand.

## Property Types
- Villa: Standalone house with private garden/pool
- House: Residential property with multiple rooms
- Apartment: Unit in multi-family building
- Condo: Modern condominium with facilities
- Bungalow: Small standalone unit, often near beach

## Common Amenities
- Sea view, mountain view, garden view
- Private pool, shared pool
- Air conditioning, WiFi, washing machine
- Fully equipped kitchen, kitchenware
- Parking, security, 24h guard

## Policies
- Pets allowed/not allowed
- Smoking allowed/not allowed
- Minimum lease: 1 month, 3 months, 6 months
- Security deposit: 1-2 months

## Locations (Koh Phangan)
- Thong Sala (main town, ferry pier)
- Haad Rin (party beach, Full Moon)
- Baan Tai (quiet, family-friendly)
- Chaloklum (north, peaceful fishing village)
- Haad Yao (west coast, sunset beach)

## Price Ranges (THB/month)
- Budget: ฿10,000 - ฿20,000
- Mid-range: ฿20,000 - ฿35,000
- Premium: ฿35,000 - ฿60,000
- Luxury: ฿60,000+

## Search API
Use MCP tool "semantic-property-search" to find properties.
Example: semantic-property-search(query="beach view villa with pets allowed")
```

---

## Implementation Phases

### Phase 1: Foundation (US-022, US-023)
- ✅ Property V2 schema with policies (pets, smoking, lease terms)
- ✅ Property dictionary with amenities
- ⏳ Full-text search indexes on title/description
- ⏳ Basic keyword search (non-semantic)

### Phase 2: Semantic Search Backend (TBD - US-027?)
- [ ] LLM query parser (OpenRouter integration)
- [ ] Semantic matching engine
- [ ] Synonym expansion
- [ ] Suggestion generator
- [ ] Search history tracking

### Phase 3: Semantic Search Frontend (TBD - US-028?)
- [ ] Semantic search bar on homepage
- [ ] Search results page with parsed filters
- [ ] Intelligent suggestions UI
- [ ] Voice input support (future)

### Phase 4: Chat Integration (TBD - US-029?)
- [ ] Chat can call semantic search API
- [ ] Inline results in chat interface
- [ ] Follow-up question refinement
- [ ] Search history in chat context

### Phase 5: MCP + External LLM Access (TBD - US-030?)
- [ ] MCP tool for property search
- [ ] llm.txt file with context
- [ ] Rate limiting for external access
- [ ] Analytics for external LLM usage

---

## Property Schema Requirements

### Critical Policies (Must Have)

**Already in Property V2 Schema:**
```json
{
  "policies": {
    "pets_allowed": true,
    "pet_details": "2 dogs max, no cats",
    "smoking_allowed": false,
    "house_rules": ["No parties", "Quiet hours 10pm-8am"],
    "restrictions": ["No smoking indoors"],
    "lease_terms": {
      "minimum_lease_months": 3,
      "security_deposit_months": 2
    }
  }
}
```

**Need to Verify/Add:**
- [ ] Pet policies (types, size, quantity)
- [ ] Smoking policies (indoor, outdoor, not allowed)
- [ ] Noise policies (party-friendly, quiet)
- [ ] Guest policies (additional guests allowed)
- [ ] Lease flexibility (short-term, long-term)

### Location Metadata (Must Have)

**Already in Property V2 Schema:**
```json
{
  "location_details": {
    "region": "Koh Phangan",
    "district": "Baan Tai",
    "proximity": {
      "near_beach": { "distance": 500, "unit": "meters" },
      "near_school": { "distance": 2, "unit": "km" }
    }
  }
}
```

**Need to Verify/Add:**
- [ ] Proximity to key locations (beach, school, hospital, pier, market)
- [ ] Transportation access (main road, dirt road, 4WD required)
- [ ] Neighborhood type (quiet, lively, tourist area)

---

## Example Semantic Search Flows

### Flow 1: Simple Query
```
User Input: "beach view villa"

LLM Parsing:
{
  "property_type": ["villa"],
  "amenities": ["sea_view", "beach_view", "ocean_view"],
  "location": ["near_beach"]
}

Database Query:
- property_type = 'villa'
- amenities.exterior CONTAINS ANY ["sea_view", "beach_view", "ocean_view"]
- location_details.proximity.near_beach IS NOT NULL

Results: 12 properties

Suggestions:
- "Refine by price range: ฿20k-30k (5 results), ฿30k-40k (4 results)"
- "You might also like: beachfront houses (8 more results)"
```

### Flow 2: Complex Query with Constraints
```
User Input: "3 bedroom house near school with garden, budget 30k/month, i have 2 dogs"

LLM Parsing:
{
  "property_type": ["house"],
  "physical_specs": {
    "rooms": { "bedrooms": 3 }
  },
  "location": {
    "proximity": { "near_school": true }
  },
  "amenities": ["garden", "private_garden"],
  "price_range": {
    "max": 30000,
    "currency": "THB"
  },
  "policies": {
    "pets_allowed": true,
    "pet_details": "2 dogs"
  }
}

Database Query:
- property_type = 'house'
- physical_specs.rooms.bedrooms >= 3
- location_details.proximity.near_school IS NOT NULL
- amenities.exterior CONTAINS ANY ["garden", "private_garden"]
- rent_price <= 30000
- policies.pets_allowed = true

Results: 2 properties

Suggestions:
- "Expand budget to ฿35k to see 3 more properties"
- "Try removing 'near school' to see 5 more pet-friendly houses"
```

### Flow 3: Ambiguous Query
```
User Input: "nice place for family"

LLM Parsing:
{
  "ambiguous": true,
  "inferred": {
    "property_type": ["house", "villa"],
    "amenities": ["safe_neighborhood", "near_school"],
    "policies": {
      "pets_allowed": "maybe",
      "family_friendly": true
    }
  },
  "confidence": 0.6
}

System Response:
- "I found properties that might suit families. To refine search:"
  - "How many bedrooms do you need? (2, 3, 4+)"
  - "What's your budget? (฿20k-30k, ฿30k-40k, ฿40k+)"
  - "Do you have children? (will show properties near schools)"
  - "Do you have pets? (will filter by pet-friendly policies)"

User: "3 bedrooms, budget 30k, yes we have kids"

[System refines search with new filters]
```

---

## Technical Considerations

### Performance
- Cache popular queries (24h TTL)
- Pre-compute common filter combinations
- Async LLM calls (don't block user)
- Fallback to keyword search if LLM fails

### Accuracy
- Confidence scores for LLM parsing
- User feedback on search relevance
- A/B testing semantic vs keyword search
- Track click-through rates

### Cost Optimization
- Batch LLM queries where possible
- Use smaller models for simple queries (GPT-3.5)
- Use larger models for complex queries (GPT-4)
- Cache LLM responses for identical queries

### Privacy
- Anonymous users: no search history stored
- Authenticated users: opt-in search history
- Never expose PII in llm.txt or MCP responses

---

## Related Documentation

- `.sdlc-workflow/guides/chat-driven-ui-architecture.md` - Chat-driven field suggestions
- `.sdlc-workflow/guides/ai-agent-workflow-pattern.md` - AI safety model
- `.sdlc-workflow/.specs/PROPERTY_SCHEMA_QUICK_REFERENCE.md` - Property V2 schema

---

## Questions for Future Planning

1. Should semantic search be available to anonymous users or require login?
2. Should we show "popular searches" on homepage to guide users?
3. Should search history be shared across devices (if authenticated)?
4. Should voice input be a priority (mobile users)?
5. Should we support conversational refinement (chat-like search)?

---

**Version:** 1.0
**Status:** Architectural Vision (Not Yet Implemented)
**Next Review:** During PLANNING phase of Homepage US (US-002 update or new US-027)

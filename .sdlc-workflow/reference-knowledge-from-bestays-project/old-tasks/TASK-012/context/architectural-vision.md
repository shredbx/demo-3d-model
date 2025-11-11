# Architectural Vision for US-022

**Created:** 2025-11-09
**Task:** TASK-012 (US-022 RESEARCH)
**Impact:** System-Wide Architecture

---

## Critical Context

During TASK-012 planning, user provided major architectural insight that affects how we design property management and ALL future features.

---

## 1. Inline Editing Philosophy (Immediate - US-022)

### Key Decision: NO Separate Admin Forms

**Approach:**
- ❌ **DO NOT** create separate admin forms for property editing
- ✅ **DO** implement inline editing on public-facing property detail page
- ✅ **DO** use right-click context menu + editable fields (like US-020)
- ✅ **DO** let agents see exactly what users see (WYSIWYG)

### Rationale
- Agent understands user experience → better quality control
- Faster workflow (no form navigation between admin/public views)
- Consistent with US-020 homepage editable content pattern
- Modern UX standard (Notion, Coda, Contentful, modern CMS)

### Dashboard vs Detail Page
- **Dashboard listings:** Navigation, bulk actions, metadata (status, created date, views)
- **Detail page:** Primary editing interface (inline, context-aware)

### Impact on US-022
- AC-16 updated: Property detail page includes inline editing for agents
- Property detail page design must support dual mode: view (visitors) + edit (agents)
- RBAC checks on page load to determine editable fields
- Context menu component reusable from US-020

---

## 2. Chat-Driven UI Intelligence (Future Vision - TBD)

### Universal Pattern for ALL Pages

**Vision:** AI chat assistant can interact with ANY field on ANY page, providing intelligent suggestions based on context.

**Key Components:**
1. **Chat Always Available:** Folded or expanded on EVERY page
2. **Page Context Awareness:** Chat knows current route, fields, user role, page state
3. **Field-Level Suggestions:** Chat can suggest values for ANY input field
4. **Inline Popups:** Suggestions appear directly in input fields (NOT separate modal)
5. **Carousel Navigation:** Multiple suggestions → left/right navigation
6. **API-Like Interface:** Every page exports `getChatContext()` for chat interaction

### Example Flow
```
Agent on property detail page
→ Opens chat
→ "Suggest amenities based on these 3 images"
→ Chat analyzes images + page context
→ Inline popup appears in amenities field
→ Carousel shows: "Private Pool" (1/5), "Mountain View" (2/5), "Modern Kitchen" (3/5)
→ Agent clicks or navigates carousel
→ Value inserted into field
```

### Implementation Status
- ⏳ **Phase 1 (US-020, US-022):** Foundation - inline editing, chat UI, property dictionary
- ⏳ **Phase 2 (Future US):** Chat-page interface (`getChatContext()` on all pages)
- ⏳ **Phase 3 (Future US):** Field suggestion UI (inline popups, carousel)
- ⏳ **Phase 4 (Future US):** Backend suggestion API (`/api/v1/chat/suggest`)
- ⏳ **Phase 5 (Future US):** Advanced features (batch suggestions, learning)

### Architectural Impact

**For TASK-012 RESEARCH:**
- Property detail page design must account for future field-level suggestions
- Field components should have consistent IDs and metadata
- Consider `getChatContext()` interface when designing page structure

**For Backend (All Features):**
- Design APIs with suggestion-compatible responses
- Include confidence scores and sources in responses
- Plan for field metadata (type, validation, current value)

**For Frontend (All Features):**
- Use reusable field components (easy to add suggestion support later)
- Maintain consistent field IDs across pages
- Design forms with inline popup space in mind

**For DevOps:**
- Monitor suggestion API performance (when implemented)
- Cache strategy for frequent suggestions
- LLM usage tracking and cost optimization

---

## 3. Documentation References

**Full Architectural Visions:**
- `.sdlc-workflow/guides/chat-driven-ui-architecture.md` (chat-driven field suggestions, 300+ lines)
- `.sdlc-workflow/guides/semantic-search-architecture.md` (natural language property search, 400+ lines)
- `.sdlc-workflow/guides/pgvector-rag-architecture.md` (vector embeddings, RAG, FAQ system, 600+ lines)

**Related Patterns:**
- `.sdlc-workflow/guides/ai-agent-workflow-pattern.md` (AI safety model)
- `.sdlc-workflow/stories/content/US-020-homepage-editable-content.md` (inline editing pattern)

---

## 3. Semantic Search + pgvector + RAG (Future Vision - TBD)

### Natural Language Property Search

**Vision:** Homepage has semantic search bar where users describe what they need in natural language.

**Example Queries:**
- "beach view villa on the island and i have 2 dogs and i smoke"
- "3 bedroom house near school with garden, budget 30k/month"
- "modern condo with pool and gym, walking distance to BTS"

**System Response:**
- Parse natural language → extract structured filters
- Apply semantic understanding (synonyms, intent, context)
- Return matching properties with intelligent suggestions
- "Did you mean...", "Try removing X to see Y more results"

### pgvector Integration

**Why pgvector?**
- Already in tech stack (PostgreSQL extension)
- Semantic similarity search (understand intent, not just keywords)
- Multi-language support (embeddings work across EN/TH)
- RAG for AI chat (knowledge-grounded responses)
- FAQ system with contextual answers

**Key Features:**
- Vector embeddings for all properties (1536 dimensions)
- IVFFLAT or HNSW indexes for fast similarity search
- Hybrid search (vector + full-text + JSONB filters)
- Embedding generation service (OpenAI ada-002 or sentence-transformers)
- Background jobs for bulk embedding updates

### RAG (Retrieval-Augmented Generation)

**Chat with Knowledge Base:**
- User asks: "Can I bring my dog?"
- System retrieves relevant policy chunks (vector search)
- LLM generates answer grounded in retrieved context
- Response includes citations/sources

**FAQ System:**
- Semantic FAQ lookup (understand user intent)
- "Can I bring my dog?" matches "Are pets allowed?" (even if different wording)
- Auto-suggest FAQ answers in chat
- Admin interface for FAQ management

### MCP + llm.txt for External LLMs

**Allow external LLMs to search properties:**
- MCP tool: `semantic-property-search`
- External LLM (e.g., ChatGPT) can query Bestays properties
- llm.txt file provides context (property types, locations, price ranges)
- Rate limiting and analytics for external access

### Implementation Status

- ⏳ **Phase 1 (US-022):** Property V2 schema with full policies (pets, smoking)
- ⏳ **Phase 2 (US-027):** Semantic search backend (LLM parser, vector search)
- ⏳ **Phase 3 (US-028):** FAQ system with pgvector
- ⏳ **Phase 4 (US-029):** RAG for AI chat
- ⏳ **Phase 5 (US-030):** MCP + external LLM access

### Architectural Impact

**For TASK-012 RESEARCH:**
- Property schema MUST support comprehensive policies (pets, smoking, noise, guests)
- Property schema MUST support rich location metadata (proximity to key locations)
- Consider embedding column in Property V2 schema (add now or later?)
- Design property dictionary with semantic search in mind

**For Backend (All Features):**
- Embedding generation service (async, background jobs)
- Vector similarity search API
- Hybrid search strategy (vector + full-text + filters)
- RAG service for chat
- FAQ management API

**For Database:**
- pgvector extension (already available)
- Embedding columns (vector(1536))
- IVFFLAT/HNSW indexes
- Full-text search indexes (GIN)
- JSONB indexes for structured filters

**For Frontend:**
- Semantic search bar on homepage
- Search results with parsed filters
- Intelligent suggestions UI
- FAQ interface
- Chat with RAG responses

---

## 4. Questions for User

**Q1: Separate User Story?**
Should chat-driven UI intelligence be a separate US story (e.g., US-026), or keep as architectural guidance only?

**Recommendation:**
- Keep as architectural guidance NOW
- Create separate US story when ready for implementation (post-MVP)
- US-022 focuses on property management with inline editing
- Future US story focuses on universal chat-field suggestions

**Q2: Priority for Chat Suggestions?**
Which pages should get field suggestions first?
- Option A: Property detail page (high value, agent productivity)
- Option B: Profile/settings pages (simpler, good learning project)
- Option C: Homepage content editing (US-020 extension)

**Q3: Implementation Timeline?**
- Milestone 2 (Post-website replication)?
- Milestone 3 (After core features stable)?
- Defer until agent feedback requests it?

---

## 5. Action Items for TASK-012

### During RESEARCH Phase
- [ ] Design property detail page with inline editing in mind
- [ ] Consider future `getChatContext()` interface when planning page structure
- [ ] Ensure field components have consistent IDs and types
- [ ] Document field metadata (type, validation, max length, etc.)

### During PLANNING Phase
- [ ] Plan RBAC for inline editing (agent vs visitor views)
- [ ] Design context menu component (reusable from US-020)
- [ ] Plan field component structure (future suggestion support)
- [ ] Consider mobile UX for inline editing

### Documentation
- [ ] Reference chat-driven architecture in implementation spec
- [ ] Note architectural considerations in planning docs
- [ ] Ensure backend API design is suggestion-compatible

---

**Status:** Documented for RESEARCH phase
**Next Review:** During PLANNING phase of US-022 (TASK-013)

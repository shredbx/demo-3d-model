# US-022: AI-Powered Property Management System

**Domain:** properties
**Feature:** ai-creation
**Scope:** management
**Status:** DEFERRED
**Created:** 2025-11-09
**Default Product:** bestays
**Portable:** true
**Ported To:** []
**Deferred To:** Phase 2 (after US-023 completion)

---

## DEFERRAL NOTE

**Reason:** Agile delivery prioritizes user value first. Users need to browse properties (US-023) before agents need AI creation tools (US-022).

**Phase 1 (HIGH PRIORITY):** US-023 - Property Import & Display
- Import existing properties from old bestays.app
- Display homepage grid with property listings
- Enable users to browse rentals

**Phase 2 (DEFERRED):** US-022 - AI-Powered Property Creation
- Implement AFTER users can browse properties
- Adds agent tooling on top of working product
- Research findings from TASK-012 remain valid

**Dependencies:** US-023 must be COMPLETED before starting US-022.

---

## Description

Implement AI-powered property management system for agents to create rental property listings through natural chat interface. Agents upload property images and provide text description, then LLM (OpenRouter) analyzes content to extract structured property data, tag images, and generate highlights. System uses property dictionary (MCP) for amenity categorization and validation.

**User Story:**
As a real estate agent, I want to create property listings by uploading images and describing the property naturally in chat, so that I can quickly add properties without filling complex forms.

**Key Features:**
- Chat-based property creation (upload images + text → structured property)
- AI image analysis (detect: mountain view, sea view, pool, modern style, etc.)
- AI text extraction (bedrooms, bathrooms, price, amenities, location)
- Property dictionary (150+ amenities, categorized by type)
- MCP integration for dictionary access
- Cloudflare R2 image storage
- Real-time LLM streaming with confirmation modal
- Multi-product support (Bestays rentals → port to Real Estate sales)

**Context:**
- Building on US-016 (Property V2 schema with 5 JSONB fields already implemented)
- Porting "Properties for Rent" from old NextJS site (bestays.app/listings/properties-for-rent)
- Research findings: `.claude/reports/20251109-property-rent-scraping-findings.md`
- **LLM Parsing Validation:** `.claude/reports/20251109-llm-parsing-validation.md` (✅ PASSED - 85% extraction success)
- **AI Workflow Pattern:** `.sdlc-workflow/guides/ai-agent-workflow-pattern.md` (safety guidelines)

**AI Safety Model:**
This feature follows the approved **AI Agent Workflow Pattern**:
- ✅ **Phase 1:** AI analyzes input, generates structured JSON (safe - no database writes)
- ✅ **Phase 2:** Agent reviews preview modal, edits fields, clicks "Create Property" CTA
- ✅ **Phase 3:** API request with JWT → RBAC validation → database write

**Key Principle:** AI prepares data, user executes actions. No autonomous database mutations.

### UI/UX Approach: Inline Editing (Like US-020)

**Property Editing Philosophy:**
- ❌ **NO separate admin forms** for property editing
- ✅ **Inline editing on public-facing property detail page**
- ✅ **Agent sees exactly what users see** (WYSIWYG)
- ✅ **Right-click context menu + editable fields** (like US-020 homepage content)
- ✅ **Dashboard listings for navigation**, main editing = inline

**Rationale:**
- Agent knows how users see properties → better quality control
- Faster workflow (no form navigation)
- Consistent with US-020 inline editing pattern
- Matches industry UX (Notion, Coda, modern CMS)

**Future Vision:**
See `.sdlc-workflow/guides/chat-driven-ui-architecture.md` for long-term vision of chat-driven field suggestions across ALL pages (TBD implementation in future milestones).

---

## Acceptance Criteria

### Phase 1: Property Dictionary & MCP
- [ ] AC-1: Property dictionary MCP server created with 150+ amenities categorized (comfort, security, outdoor, kitchen, bathroom, entertainment, etc.)
- [ ] AC-2: Highlight categories defined (views, proximity, unique features) with multi-language labels (EN/TH)
- [ ] AC-3: JSON schemas for validation (physical_specs, location_details, amenities, policies, contact_info)
- [ ] AC-4: MCP tool `property-dictionary-lookup` returns amenity/highlight by ID or category

### Phase 2: AI-Powered Backend
- [ ] AC-5: OpenRouter text analysis endpoint extracts structured JSON from agent's property description (bedrooms, bathrooms, price, location, amenities)
- [ ] AC-6: OpenRouter image analysis endpoint tags images using property dictionary (mountain view, sea view, pool, modern style, outdoor spaces)
- [ ] AC-7: Cloudflare R2 integration for image upload with signed URLs
- [ ] AC-8: Property creation API endpoint (`POST /api/v1/properties`) accepts agent input + LLM analysis results, validates with Zod, stores in Property V2 schema
- [ ] AC-9: Error handling for LLM failures with fallback to manual entry

### Phase 3: Agent Chat Interface
- [ ] AC-10: Chat UI component with file upload (images + text input) for agent property creation
- [ ] AC-11: Real-time LLM streaming shows analysis progress (extracting fields, tagging images, generating highlights)
- [ ] AC-12: Property preview modal displays extracted data with editable fields before final confirmation
- [ ] AC-13: Agent can review and edit LLM-generated fields before creating property
- [ ] AC-14: Success confirmation with redirect to property detail page

### Phase 4: Property Listings Frontend
- [ ] AC-15: Property list page displays rental properties in grid layout (3 columns on desktop)
- [ ] AC-16: Property detail page shows full property information with image gallery, amenities, policies, contact info; **agents can edit inline** (right-click context menu like US-020)
- [ ] AC-17: Multi-product routing (`/listings/properties-for-rent` for Bestays, `/listings/properties-for-sale` for Real Estate)

### Phase 5: Testing & Validation
- [ ] AC-18: E2E tests for chat-based property creation flow (upload → LLM analysis → review → confirm)
- [ ] AC-19: E2E tests for property listings (list view, detail view, filters)
- [ ] AC-20: Unit tests for Zod validation of JSONB fields

---

## Technical Notes

### Architecture Decisions

**1. Storage Strategy: JSONB + Zod (Already Implemented in US-016)**
- Property V2 schema with 5 JSONB columns (physical_specs, location_details, amenities, policies, contact_info)
- Zod validation for type safety
- GIN indexes for fast JSONB queries
- Rationale: 1 row per property vs 150+ rows with normalized tables

**2. Multi-Product Architecture: Shared API + Domain-Specific Routes**
- Shared: Property V2 schema, AI creation workflow, property dictionary (MCP), image analysis
- Domain-Specific: Frontend routes (`/listings/properties-for-rent` vs `/listings/properties-for-sale`), filters, branding
- Rationale: Maximize code reuse while allowing product customization

**3. Image Storage: Cloudflare R2**
- Current: Supabase Storage (`/bestays-images/properties/`)
- Future: Cloudflare R2 (cost-effective, CDN, S3-compatible)
- Migration: Existing images can stay on Supabase, new images use R2

**4. LLM Provider: OpenRouter**
- Models: GPT-4V or Claude 3.5 Sonnet for image analysis, GPT-4 Turbo for text extraction
- Rationale: Unified API, cost-effective, fallback support

**5. Property Dictionary: MCP Server**
- Structure: 150+ amenities (comfort, security, outdoor, kitchen, bathroom, entertainment), highlight categories (views, proximity, features)
- Storage: JSON files or database (TBD in RESEARCH)
- Multi-language: EN/TH labels
- Versioning: Semantic versioning for dictionary updates

### Dependencies

**External:**
- OpenRouter API (text + image analysis)
- Cloudflare R2 (image storage)
- MCP protocol (property dictionary access)

**Internal:**
- US-016 (Property V2 schema) - COMPLETED
- Clerk authentication (agent login)
- TanStack Query (API calls)
- Svelte 5 (frontend components)

### Constraints

- LLM analysis may fail or return incorrect data → Require agent review/confirmation
- Image analysis accuracy varies by model → Need confidence thresholds
- 150+ amenities = large dictionary → MCP must be fast (<500ms lookup)
- Multi-product routing must be SEO-friendly

### Technical Risks

**High Risk:**
- LLM hallucinations (extracting non-existent amenities) → Mitigate with property dictionary validation
- Image analysis errors (tagging wrong features) → Mitigate with agent confirmation modal

**Medium Risk:**
- Cloudflare R2 migration complexity → Mitigate with dual storage (Supabase + R2) during transition
- MCP server performance (150+ amenities) → Mitigate with caching

**Low Risk:**
- JSONB query performance → GIN indexes already implemented in US-016
- Multi-product routing → SvelteKit route groups handle this well

### Research Questions (TASK-012 RESEARCH Phase)

1. **MCP Architecture**
   - New MCP server or extend existing?
   - Dictionary storage: database vs JSON files?
   - How to version property dictionary?

2. **Image Storage Migration**
   - Keep Supabase or full migration to R2?
   - Migration strategy for existing images?
   - Thumbnail generation approach?

3. **LLM Model Selection**
   - GPT-4V vs Claude 3.5 Sonnet for image analysis?
   - Cost vs accuracy trade-off?
   - Fallback strategy if LLM fails?

4. **Agent Experience**
   - Chat-first or form-first?
   - Allow manual field editing after LLM analysis?
   - Confirmation flow design?

5. **Multi-Product Routing**
   - SvelteKit route groups?
   - Shared layouts vs product-specific?
   - SEO considerations?

---

## Related Stories

- **US-016:** Property Migration Design (Property V2 schema with 5 JSONB fields) - COMPLETED
- **US-023:** Property Listings Frontend (grid view, detail view, filters) - TO BE CREATED
- **US-024:** Porting to Real Estate (properties for sale) - TO BE CREATED
- **US-025:** Advanced Property Search/Filters (price, bedrooms, amenities) - TO BE CREATED

---

## Implementation Phases (Recommended Task Breakdown)

### TASK-012: RESEARCH (Property Dictionary + AI Analysis Design)
- Review US-016 Property V2 schema
- Design property dictionary structure (150+ amenities, categories, JSON schemas)
- Research MCP server patterns (new vs extend existing)
- Design AI-powered creation flow (text + image analysis)
- Evaluate image storage options (Supabase vs R2)
- Create implementation plan

### TASK-013: PLANNING (Architecture + API Design)
- Define MCP tool interfaces (property-dictionary-lookup, etc.)
- Design OpenRouter integration (text extraction, image tagging)
- Design Cloudflare R2 integration (upload, signed URLs, thumbnails)
- Design property creation API endpoint (validation, Zod schemas)
- Design agent chat interface (upload, streaming, confirmation)
- Create quality gate checklist

### TASK-014: IMPLEMENTATION - Property Dictionary MCP (Backend)
- Create MCP server for property dictionary
- Implement 150+ amenities with categories
- Implement highlight categories
- Add JSON schemas for validation
- Add multi-language labels (EN/TH)
- Write unit tests

### TASK-015: IMPLEMENTATION - AI Analysis Backend (Backend)
- Implement OpenRouter text analysis (field extraction)
- Implement OpenRouter image analysis (tagging)
- Implement Cloudflare R2 image upload
- Implement property creation API endpoint
- Add Zod validation for JSONB fields
- Write unit tests

### TASK-016: IMPLEMENTATION - Agent Chat Interface (Frontend)
- Create chat UI component (file upload + text input)
- Implement real-time LLM streaming
- Create property preview modal
- Add edit capability for LLM-generated fields
- Add confirmation flow
- Write Storybook stories

### TASK-017: IMPLEMENTATION - Property Listings UI (Frontend)
- Create property list page (grid layout)
- Create property detail page (image gallery, amenities, policies)
- Implement multi-product routing (bestays vs realestate)
- Add filters (price, bedrooms, property type)
- Write Storybook stories

### TASK-018: TESTING (E2E + Integration Tests)
- E2E test: Chat-based property creation flow
- E2E test: Property listings (list view, detail view)
- E2E test: Multi-product routing
- Integration test: LLM analysis with mock responses
- Unit test: Zod validation

### TASK-019: VALIDATION (User Testing + Deployment)
- Agent user testing (create 5 properties via chat)
- Verify LLM accuracy (check extracted fields vs actual)
- Performance testing (LLM response time, image upload)
- Deploy to staging
- Deploy to production (feature flag)

---

## Tasks

[Automatically populated by system - do not edit manually]

---

## Tasks

[Automatically populated by system - do not edit manually]

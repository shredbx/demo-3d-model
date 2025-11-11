# Editable Content + MCP Integration Architecture Specification

**Date**: 2025-11-11
**Status**: Draft
**Affects**: Multiple user stories (US-020, US-024, property management)

---

## Executive Summary

This specification defines a unified architecture for:
1. **Editable Content Pattern** - Role-aware, reusable component for in-place editing
2. **Property Management Flow** - Admin/agent property CRUD with MCP integration
3. **Chat-Driven Property Creation** - LLM-powered property creation via MCP tools
4. **Single Source of Truth** - Shared validation schema between frontend/backend

**Core Principle**: "One Source of Truth" - Validation rules, schemas, and business logic defined once and imported everywhere.

---

## 1. Problem Statement

### 1.1 Current Issues

**Homepage Editable Fields (BROKEN)**
- Previously implemented editable fields for multilingual content
- Component pattern exists but integration is failing
- Root cause unknown - needs investigation
- Expected: Drop-in component that auto-detects role and provides edit context
- Reality: Integration errors preventing functionality

**Property Management Gap**
- No UI for admin/agent to edit properties
- Manual database edits required for property updates
- No MCP integration for property CRUD
- No chat integration for property creation

### 1.2 Expected System Behavior

Based on git history, documentation, and file comments:
- ✅ Editable component should be implemented
- ✅ Role detection (admin/agent) should work
- ✅ Database dictionary integration should exist
- ❌ Current state: Not functioning

**Investigation Required:**
- Trace component lifecycle: render → role-check → db fetch → display → edit activation → save
- Identify integration breakpoint
- Restore functionality before extending pattern

---

## 2. Architecture Requirements

### 2.1 Core Principles

1. **Single Source of Truth (CRITICAL)**
   - Validation schemas defined once in `/apps/server/src/server/lib/schemas/`
   - Frontend imports and uses same schemas
   - Backend validates using same schemas
   - No duplication of validation logic

2. **Self-Validating System**
   - Frontend validates before API call
   - Backend validates on receive (defense in depth)
   - Validation errors use consistent key names
   - Schema evolution tracked in version control

3. **Role-Aware Components**
   - Role detection from secure server session (not localStorage)
   - Components receive `roleContext` prop
   - RBAC enforcement at API layer
   - UI adapts to role capabilities

4. **MCP-First Integration**
   - Every FastAPI endpoint has MCP equivalent
   - MCP provides role-based tool discovery
   - Authentication via Clerk (admin/agent credentials)
   - MCP cannot publish (security constraint)

---

## 2.2 Component Architecture

### Editable Component Pattern

**Location**: `apps/frontend/src/lib/components/EditableContent.svelte`

**Props Interface**:
```typescript
interface EditableContentProps {
  dictionaryKey: string;        // e.g., "homepage.hero.title"
  lang: "en" | "th";             // Current language
  roleContext: RoleContext;      // { userId, role, permissions }
  schema?: ValidationSchema;     // Optional override, defaults to shared schema
  onSave?: (payload: unknown) => Promise<void>;
}

interface RoleContext {
  userId: string;
  role: "admin" | "agent" | "user";
  permissions: string[];         // From Clerk metadata
}
```

**Behavior**:
1. **Mount**: Load value via `dictionaryKey` + `lang` from backend
2. **Role Detection**: Use `roleContext` from server-side props (SSR) or session
3. **Edit Activation**: Show edit UI only if role is admin/agent
4. **Validation**: Import shared schema, validate locally before save
5. **Save Flow**: POST to `/api/content/update` with validated payload
6. **Error Handling**: Display inline errors with same keys as backend

**Design Pattern**: Composition over Configuration
- Small, focused component
- Clear prop contract
- No hidden dependencies
- Easy to test in isolation

---

## 2.3 Property Management Architecture

### Edit Mode Flow

**Trigger**: Edit button (top-right header on property details page)

**Visibility**:
- ✅ Admin: All properties
- ✅ Agent: Own properties only
- ❌ User: Hidden

**Edit Mode Behavior**:

| Field Type | View Mode | Edit Mode |
|------------|-----------|-----------|
| Boolean (e.g., wifi) | Show tag only if true | Checkbox (checked if true) |
| Integer (e.g., rooms) | Display value | Number input with min/max validation |
| Text (e.g., description) | Display text | Textarea with maxlength |
| List (e.g., amenities) | Show selected tags | Multi-checkbox with all options |
| Invisible fields | Hidden | Show in "Advanced" collapsible section |

**Validation Rules**:
- Import from `/apps/server/src/server/lib/schemas/property_schema.py`
- Frontend generates TypeScript types from Python schema (tooling TBD)
- Real-time validation with inline error messages
- Submit blocked until all validation passes

**Save Flow**:
```
1. User clicks Save
2. Frontend validates against schema
3. If valid: PUT /api/properties/{id}
4. Backend validates (defense in depth)
5. If success: Show toast, refresh UI
6. If error: Display inline errors (keyed by field name)
```

**Publish Flow** (Admin Only):
- Separate action from Save
- Admin navigates to "All Properties" page (new)
- Grid view: thumbnail + title + search + Publish button
- Publish button: POST /api/properties/{id}/publish
- Agent cannot publish (UI hidden, API returns 403)

---

## 2.4 MCP Integration Architecture

### MCP Server Structure

**Location**: `/apps/server/src/server/mcp/`

```
mcp/
├── __init__.py
├── server.py              # MCP server initialization
├── auth.py                # Clerk authentication middleware
├── tools/
│   ├── __init__.py
│   ├── property_tools.py  # Property CRUD tools
│   ├── content_tools.py   # Editable content tools
│   └── chat_tools.py      # Chat integration tools
└── schemas/
    ├── __init__.py
    └── tool_schemas.py    # MCP tool input/output schemas
```

### MCP Tool Registry

**Role-Based Discovery**:
```
GET /mcp/tools
Headers: Authorization: Bearer <clerk_token>

Response:
{
  "tools": [
    {
      "name": "create_property",
      "description": "Create new property (agent/admin only)",
      "roles": ["admin", "agent"],
      "parameters": { ... }
    },
    {
      "name": "update_property",
      "description": "Update existing property",
      "roles": ["admin", "agent"],
      "parameters": { ... }
    },
    {
      "name": "list_properties",
      "description": "List properties with filters",
      "roles": ["admin", "agent", "user"],
      "parameters": { ... }
    }
  ]
}
```

**Security Model**:
- Claude Code CLI registers MCP server: `claude mcp add bestays http://localhost:8011/mcp`
- Authentication: Clerk JWT token in Authorization header
- Role extracted from token claims
- Tools filtered by role before returning list
- API calls validate role again (defense in depth)

### MCP Tool: Create Property

**Input** (free text or structured):
```json
{
  "raw_text": "Beachfront villa in Phuket, 4 bedrooms, pool, WiFi, $200/night",
  "auth_token": "clerk_jwt_token"
}
```

**Processing**:
1. Authenticate token → extract role
2. Parse raw text using LLM (OpenRouter)
3. Map to property schema
4. Validate against shared schema
5. Create property (status: draft, not published)
6. Return property ID + preview URL

**Output**:
```json
{
  "id": "prop_123",
  "status": "draft",
  "preview_url": "https://bestays.app/en/properties/prop_123?preview=true",
  "title": "Beachfront villa in Phuket",
  "thumbnail_url": null,
  "needs_review": ["images", "exact_location", "availability"]
}
```

**Constraints**:
- ❌ Cannot set `published: true` via MCP
- ✅ Creates draft property
- ✅ Agent must navigate to UI to publish

---

## 2.5 Chat Integration Architecture

### Chat → Property Creation Flow

**User Action**: Paste property description in chat

**Chat Response**:
```
I've created a draft property for you:

┌─────────────────────────────────────┐
│ 🏠 Beachfront villa in Phuket       │
│                                     │
│ [Thumbnail placeholder]             │
│                                     │
│ 📍 Phuket, Thailand                 │
│ 🛏️  4 bedrooms                      │
│ 💰 $200/night                       │
│                                     │
│ Status: DRAFT (Not published)       │
│                                     │
│ Actions:                            │
│ [View & Edit] [Publish]             │
└─────────────────────────────────────┘

⚠️ Property needs review:
  - Add images
  - Verify exact location
  - Set availability calendar
```

**Action Buttons**:
1. **View & Edit**: Opens property details page in edit mode
2. **Publish**: Opens modal with publish confirmation (admin only)

### Chat Tools Configuration

**Location**: `/apps/server/src/server/lib/llm/chat/tools/`

```python
# Property creation tool
@tool(roles=["admin", "agent"])
async def create_property_from_text(
    raw_text: str,
    user_context: UserContext
) -> PropertyCreationResult:
    """
    Parse free text and create property draft.

    Uses:
    - LLM for text parsing (OpenRouter)
    - MCP endpoint for creation
    - Shared property schema for validation
    """
    # Implementation connects to MCP
    pass
```

**Tool Registration**:
- Tools auto-discovered from `/tools/` directory
- Each tool decorated with `@tool(roles=[...])`
- LangChain integration for tool calling
- Same tools exposed via MCP and Chat

---

## 2.6 Shared Schema Architecture

### Schema Definition Location

**Python (Backend)**:
```python
# /apps/server/src/server/lib/schemas/property_schema.py

from pydantic import BaseModel, Field
from typing import List, Optional

class PropertySchema(BaseModel):
    title: str = Field(..., max_length=200, description="Property title")
    description: Optional[str] = Field(None, max_length=5000)
    wifi: bool = Field(False, description="Has WiFi")
    rooms: int = Field(1, ge=1, le=50, description="Number of rooms")
    amenities: List[str] = Field(default_factory=list)

    class Config:
        schema_extra = {
            "roles": {
                "admin": {"can_publish": True, "can_edit_all": True},
                "agent": {"can_publish": False, "can_edit_own": True}
            }
        }
```

**TypeScript (Frontend)**:
```typescript
// /apps/frontend/src/lib/schemas/property.schema.ts
// Generated from Python schema (tool TBD)

export interface PropertySchema {
  title: string;              // max: 200 chars
  description?: string;       // max: 5000 chars
  wifi: boolean;
  rooms: number;              // min: 1, max: 50
  amenities: string[];
}

export const PropertyValidationRules = {
  title: { required: true, maxLength: 200 },
  description: { required: false, maxLength: 5000 },
  wifi: { type: "boolean" },
  rooms: { type: "integer", min: 1, max: 50 },
  amenities: { type: "array", items: { type: "string" } }
};
```

### Schema Synchronization Strategy

**Option 1**: Code Generation
- Python schema is source of truth
- CI/CD runs script: `python scripts/generate_ts_schemas.py`
- Generates TypeScript types + validation rules
- Committed to version control
- Build fails if schemas diverge

**Option 2**: JSON Schema Bridge
- Python schema exports JSON Schema
- Frontend imports JSON Schema at build time
- Runtime validation library (e.g., Zod) reads JSON Schema
- Single file defines both

**Recommendation**: Start with Option 2 (simpler), migrate to Option 1 if needed.

---

## 3. Integration Points

### 3.1 Homepage Editable Content (REPAIR)

**Current Story**: Likely US-020 (editable homepage content)

**Investigation Tasks**:
1. Locate editable component implementation
2. Trace git history for breaking change
3. Identify integration failure point
4. Restore functionality
5. Add integration tests to prevent regression

**Files to Investigate**:
- `apps/frontend/src/lib/components/Editable*.svelte`
- `apps/frontend/src/routes/[lang]/+page.svelte`
- `apps/server/src/server/api/content.py`
- Recent commits touching these files

### 3.2 Property Management (NEW)

**Required Stories**:
1. **US-XXX**: Property Edit UI (Admin/Agent)
   - Edit button on property details
   - Edit mode for all fields
   - Save flow with validation
   - Integration tests

2. **US-YYY**: Admin Property Management Dashboard
   - Grid view of all properties
   - Search + filter
   - Publish action
   - Batch operations

3. **US-ZZZ**: MCP Property Tools
   - MCP server implementation
   - Property CRUD tools
   - Clerk authentication
   - Claude Code CLI integration guide

4. **US-AAA**: Chat Property Creation
   - LLM text parsing
   - MCP tool integration
   - Chat response formatting
   - Action buttons (View/Edit/Publish)

### 3.3 Cloudflare R2 Integration (FUTURE)

**Scope**: Image and video storage

**Integration Point**: Property image uploads

**Reference**: https://developers.cloudflare.com/agents/model-context-protocol/mcp-servers-for-cloudflare/

**Tasks**:
1. Setup Cloudflare R2 bucket
2. Generate access credentials
3. Install Cloudflare MCP server (if available)
4. Integrate with property management flow
5. Image upload UI component

**Priority**: Medium (can use local/database storage initially)

---

## 4. Implementation Phases

### Phase 1: Investigation & Repair (CRITICAL)

**Goal**: Fix broken homepage editable content

**Tasks**:
1. Investigate component implementation
2. Identify breaking change
3. Restore functionality
4. Add regression tests

**Deliverables**:
- Bug fix PR
- Integration tests
- Postmortem: what broke and why

**Timeline**: 2-3 days

### Phase 2: Shared Schema Infrastructure

**Goal**: Establish single source of truth for validation

**Tasks**:
1. Create `/apps/server/src/server/lib/schemas/`
2. Implement property schema (Pydantic)
3. Generate TypeScript types
4. Update existing validation to use shared schema

**Deliverables**:
- Python property schema
- TypeScript types
- Schema synchronization tooling
- Migration guide

**Timeline**: 3-4 days

### Phase 3: Property Edit UI

**Goal**: Admin/agent can edit properties via UI

**Tasks**:
1. Edit button component
2. Edit mode implementation
3. Field validation with shared schema
4. Save flow integration
5. E2E tests

**Deliverables**:
- Property edit UI
- Integration with FastAPI endpoint
- E2E test suite

**Timeline**: 5-7 days

### Phase 4: MCP Integration

**Goal**: Property CRUD via MCP tools

**Tasks**:
1. MCP server implementation
2. Property CRUD tools
3. Clerk authentication middleware
4. Claude Code CLI registration guide
5. Integration tests

**Deliverables**:
- MCP server (`/mcp/` module)
- Property tools
- CLI integration guide
- MCP test suite

**Timeline**: 5-7 days

### Phase 5: Chat Integration

**Goal**: Create properties via chat

**Tasks**:
1. LLM text parsing tool
2. MCP tool integration
3. Chat response formatting
4. Action buttons (View/Edit/Publish)
5. Integration tests

**Deliverables**:
- Chat property creation flow
- Formatted property cards
- Integration with MCP
- E2E tests

**Timeline**: 4-6 days

### Phase 6: Admin Dashboard

**Goal**: Manage all properties from single view

**Tasks**:
1. Property grid component
2. Search + filter
3. Publish action
4. Batch operations
5. E2E tests

**Deliverables**:
- Admin property management page
- Search/filter functionality
- Publish workflow
- E2E tests

**Timeline**: 5-7 days

### Phase 7: Cloudflare R2 Integration (FUTURE)

**Goal**: Store images/videos in R2

**Tasks**:
1. R2 bucket setup
2. Cloudflare MCP integration
3. Image upload UI
4. Migration script for existing images

**Deliverables**:
- R2 storage integration
- Image upload flow
- Migration tooling

**Timeline**: 4-6 days

---

## 5. Testing Strategy

### 5.1 Investigation Phase Tests

**Goal**: Verify editable component works

**Tests**:
1. Component renders with correct role
2. Edit mode activates for admin/agent
3. Save flow updates database
4. Validation prevents invalid data
5. Error messages display correctly

### 5.2 Integration Tests

**Goal**: End-to-end flows work

**Tests**:
1. Homepage editable content: view → edit → save → verify
2. Property edit: view → edit → save → verify
3. MCP property creation: authenticate → create → verify
4. Chat property creation: send text → receive card → click action → verify

### 5.3 Schema Validation Tests

**Goal**: Frontend/backend schemas match

**Tests**:
1. Python schema exports valid JSON Schema
2. TypeScript types match Python schema
3. Validation rules identical on both sides
4. Schema changes break tests (catch divergence)

### 5.4 Security Tests

**Goal**: RBAC enforced correctly

**Tests**:
1. User cannot access edit UI
2. Agent cannot publish
3. Admin can publish
4. MCP authentication required
5. Role-based tool discovery works

---

## 6. Success Criteria

### 6.1 Functional Requirements

- ✅ Homepage editable content works in both languages
- ✅ Editable component is drop-in (< 5 props)
- ✅ Property edit UI works for admin/agent
- ✅ Validation uses single source of truth
- ✅ MCP tools authenticate with Clerk
- ✅ Chat creates properties via MCP
- ✅ Admin can publish from dashboard
- ✅ Agent cannot publish via MCP or chat

### 6.2 Quality Requirements

- ✅ Integration tests cover all flows
- ✅ E2E tests for critical paths
- ✅ No validation logic duplication
- ✅ Schema changes tracked in version control
- ✅ Error messages use consistent keys

### 6.3 Documentation Requirements

- ✅ Editable component usage guide
- ✅ Shared schema documentation
- ✅ MCP integration guide for Claude Code CLI
- ✅ Chat tool development guide
- ✅ Postmortem: what broke and how to prevent

---

## 7. Risk Assessment

### 7.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Homepage editable content cannot be repaired | Low | High | Reimplement from scratch with tests |
| Schema synchronization breaks | Medium | Medium | CI/CD validation, automated tests |
| MCP authentication complex | Medium | Medium | Start with simple Bearer token, iterate |
| Chat property creation poor quality | High | Low | Provide examples, iterate on prompts |
| Cloudflare R2 integration delays | Low | Low | Use local storage initially |

### 7.2 Process Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scope creep | High | High | Strict phase boundaries, incremental delivery |
| Timeline underestimation | Medium | Medium | Buffer time, prioritize ruthlessly |
| Test coverage gaps | Medium | High | TDD approach, E2E tests required |

---

## 8. Open Questions

1. **Schema Synchronization**: Code generation or JSON Schema bridge?
   - **Recommendation**: Start with JSON Schema, migrate if needed

2. **MCP Authentication**: JWT in header or custom mechanism?
   - **Recommendation**: Start with Bearer token (Clerk JWT)

3. **Chat Property Cards**: Markdown or custom component?
   - **Recommendation**: Custom component with actions

4. **Cloudflare R2**: Now or later?
   - **Recommendation**: Later (Phase 7), use local storage initially

5. **Property Images**: Where to scrape from?
   - **Answer**: https://www.bestays.app/listings/properties-for-rent

6. **Publish Workflow**: Modal or redirect?
   - **Recommendation**: Modal for inline, redirect for batch

---

## 9. Dependencies

### External Services
- ✅ Clerk (authentication) - already integrated
- ✅ OpenRouter (LLM) - already integrated
- ⏳ Cloudflare R2 (storage) - Phase 7
- ⏳ Cloudflare MCP (if available) - Research needed

### Internal Components
- ✅ FastAPI backend - exists
- ✅ SvelteKit frontend - exists
- ✅ Property model - exists
- ⏳ MCP server - needs implementation
- ⏳ Chat LangChain integration - exists but needs tools
- ⏳ Shared schema - needs creation

---

## 10. Next Steps

1. **Immediate (Today)**:
   - Save this specification to `.sdlc-workflow/.specs/`
   - Map to existing user stories
   - Identify new stories needed
   - Launch specialist agents for architecture review

2. **Phase 1 (Days 1-3)**:
   - Investigate broken homepage editable content
   - Create bug fix task
   - Implement fix with tests
   - Document postmortem

3. **Phase 2 (Days 4-7)**:
   - Design shared schema architecture
   - Implement property schema
   - Generate TypeScript types
   - Add schema validation tests

4. **Phase 3+ (Weeks 2-6)**:
   - Implement property edit UI
   - Build MCP server
   - Integrate chat property creation
   - Build admin dashboard

---

## Appendix A: Terminology

- **Editable Component**: Role-aware UI component for in-place content editing
- **MCP**: Model Context Protocol - API for LLM tool integration
- **Single Source of Truth**: Validation rules defined once and imported everywhere
- **Role Context**: User role + permissions passed to components
- **Draft Property**: Property created but not published (visible only to creator + admins)
- **MCP Tool**: Function exposed via MCP that LLMs can call
- **Tool Discovery**: API endpoint that lists available tools for a role

---

## Appendix B: References

- Cloudflare MCP Documentation: https://developers.cloudflare.com/agents/model-context-protocol/mcp-servers-for-cloudflare/
- Bestays Property Listings: https://www.bestays.app/listings/properties-for-rent
- User Stories Location: `.sdlc-workflow/stories/`
- Task Folders Location: `.claude/tasks/`

---

**Document Status**: Draft for Architecture Review
**Next Review**: After specialist agent analysis
**Owner**: Architecture Team (CTO + DevOps + Backend + Frontend specialists)

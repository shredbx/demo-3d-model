# Story Mapping: Editable Content + MCP Architecture

**Date**: 2025-11-11
**Spec Reference**: `EDITABLE-CONTENT-MCP-ARCHITECTURE.md`
**Status**: Mapping Complete → Ready for Specialist Review

---

## Executive Summary

User request encompasses:
1. **REPAIR**: Broken homepage editable content (US-020 COMPLETED but failing)
2. **EXTEND**: Apply editable pattern to property management
3. **NEW**: MCP integration for property CRUD
4. **NEW**: Chat-driven property creation
5. **NEW**: Shared schema infrastructure (single source of truth)
6. **NEW**: Cloudflare R2 integration

---

## Story Mapping

### 🔴 EXISTING STORY - NEEDS REPAIR

#### US-020: Homepage Editable Content
**Status**: ✅ COMPLETED (but BROKEN - investigation required)

**What User Reported**:
- Previously implemented editable fields for multilingual content
- Component pattern exists but integration is failing
- Expected: Drop-in component that auto-detects role
- Reality: Integration errors

**Action Required**:
1. **NEW TASK**: TASK-020-hotfix-editable-content
   - **Type**: BUGFIX
   - **Priority**: CRITICAL (blocking other work)
   - **Scope**: Investigate and repair
   - **Timeline**: 2-3 days

**Tasks**:
- Investigate: Trace component lifecycle (render → role-check → db fetch → display → edit → save)
- Identify: Find integration breakpoint
- Fix: Restore functionality
- Test: Add regression tests
- Document: Postmortem report

**Mapping to Spec**:
- ✅ Spec Section 1: Problem Statement (Homepage Editable Fields BROKEN)
- ✅ Spec Phase 1: Investigation & Repair

---

### 🟡 EXISTING STORY - NEEDS UPDATE

#### US-022: AI-Powered Property Management
**Status**: DEFERRED (Phase 2)

**Current Scope**:
- Chat-based property creation
- LLM analysis (text + images)
- Property dictionary (MCP)

**User Request Additions**:
- MCP for property CRUD (create/update/list)
- Property edit UI (inline editing, not forms)
- Admin dashboard (grid view, search, publish)
- Chat integration with MCP tools

**Action Required**:
1. **UPDATE STORY**: Expand US-022 to include:
   - Property edit UX (inline, role-aware)
   - MCP CRUD tools
   - Chat property creation
   - Admin dashboard

2. **NEW TASKS**:
   - TASK-022-mcp-property-tools
   - TASK-022-property-edit-ui
   - TASK-022-chat-integration
   - TASK-022-admin-dashboard

**Mapping to Spec**:
- ✅ Spec Section 2.3: Property Management Architecture
- ✅ Spec Section 2.4: MCP Integration Architecture
- ✅ Spec Section 2.5: Chat Integration Architecture
- ✅ Spec Phases 3-6: Property Edit, MCP, Chat, Dashboard

---

### 🟢 NEW STORY - CREATE

#### US-030: Shared Schema Infrastructure (Single Source of Truth)
**Status**: NEW (to be created)

**Scope**:
- Create `/apps/server/src/server/lib/schemas/` module
- Implement property schema (Pydantic)
- Generate TypeScript types from Python schemas
- Update all validation to use shared schemas
- Schema synchronization CI/CD

**Rationale**:
- Foundation for all future features
- Prevents frontend/backend validation drift
- Required by property management (US-022)
- Required by editable content repair (US-020)

**Acceptance Criteria**:
- Python property schema (Pydantic) with all field types
- TypeScript types auto-generated or synchronized
- Validation rules identical on frontend/backend
- Schema changes break CI if frontend/backend diverge
- Documentation: Schema versioning strategy

**Mapping to Spec**:
- ✅ Spec Section 2.6: Shared Schema Architecture
- ✅ Spec Phase 2: Shared Schema Infrastructure
- ✅ Spec Core Principle #1: Single Source of Truth

**Tasks**:
- TASK-030-001-schema-architecture
- TASK-030-002-property-schema
- TASK-030-003-typescript-generation
- TASK-030-004-validation-migration

---

### 🟢 NEW STORY - CREATE

#### US-031: MCP Server for Property Management
**Status**: NEW (to be created)

**Scope**:
- MCP server implementation (`/apps/server/src/server/mcp/`)
- Property CRUD tools (create, update, list, get, publish)
- Clerk authentication middleware
- Role-based tool discovery
- Claude Code CLI integration guide

**Acceptance Criteria**:
- MCP server registers with Claude Code CLI
- Authenticates via Clerk JWT tokens
- Tools filtered by user role (admin/agent/user)
- Property creation via MCP creates draft (not published)
- Admin can publish via MCP, agent cannot
- Documentation: CLI registration and usage guide

**Mapping to Spec**:
- ✅ Spec Section 2.4: MCP Integration Architecture
- ✅ Spec Phase 4: MCP Integration
- ✅ Spec Appendix B: Claude Code CLI commands

**Dependencies**:
- US-030 (shared schemas) must exist
- US-022 (property model) must exist

**Tasks**:
- TASK-031-001-mcp-server-setup
- TASK-031-002-property-tools
- TASK-031-003-auth-middleware
- TASK-031-004-role-discovery
- TASK-031-005-cli-integration

---

### 🟢 NEW STORY - CREATE

#### US-032: Cloudflare R2 Integration
**Status**: NEW (to be created - Phase 7, LOW PRIORITY)

**Scope**:
- R2 bucket setup
- Image upload workflow
- Cloudflare MCP integration (if available)
- Migration script for existing images

**Acceptance Criteria**:
- R2 bucket configured with access credentials
- Image upload API endpoint with signed URLs
- Property images stored in R2
- Migration script moves existing images from local/database

**Mapping to Spec**:
- ✅ Spec Phase 7: Cloudflare R2 Integration (FUTURE)
- ✅ Spec Section 3.3: Cloudflare R2 Integration

**Note**: This is FUTURE work, not blocking current development.

---

### 🟢 NEW STORY - CREATE

#### US-033: LLM Library Refactoring (Extraction-Ready Architecture)
**Status**: NEW (to be created)

**Scope**:
- Refactor chat/FAQ from `apps/server/src/server/services/` → `apps/server/src/server/lib/llm/`
- Config-driven architecture (portable to other projects)
- Integration tests prove nothing breaks
- Prepare for future extraction to separate package

**Acceptance Criteria**:
- Chat logic in `lib/llm/chat/`
- FAQ logic in `lib/llm/faq/`
- Config files define project-specific behavior
- All existing functionality works (integration tests pass)
- Documentation: Migration guide, architecture decisions

**Mapping to Spec**:
- ✅ User request: "Move chat and FAQ to separate generic package"
- ✅ Approach: Refactor within monorepo first, extract later

**Dependencies**:
- None (can start immediately)

**Tasks**:
- TASK-033-001-llm-module-design
- TASK-033-002-chat-refactoring
- TASK-033-003-faq-refactoring
- TASK-033-004-config-system
- TASK-033-005-integration-tests

---

## Implementation Priority

### 🔥 CRITICAL PATH (Start Immediately)

**Phase 1: Investigation & Repair (2-3 days)**
1. **TASK-020-hotfix-editable-content** (US-020 repair)
   - Investigate broken homepage editable content
   - Fix integration issues
   - Add regression tests
   - **BLOCKS**: All other editable content work

### 🎯 HIGH PRIORITY (After Phase 1)

**Phase 2: Shared Schema Foundation (3-4 days)**
2. **US-030 tasks** (Shared Schema Infrastructure)
   - Create schema module
   - Implement property schema
   - Generate TypeScript types
   - **ENABLES**: Property edit UI, MCP tools, validation consistency

**Phase 3: LLM Refactoring (4-5 days - CAN RUN IN PARALLEL)**
3. **US-033 tasks** (LLM Library Refactoring)
   - Refactor chat/FAQ to `lib/llm/`
   - Config-driven architecture
   - Integration tests
   - **ENABLES**: Future extraction, multi-product reuse

### 📋 MEDIUM PRIORITY (After Phase 2)

**Phase 4: MCP Integration (5-7 days)**
4. **US-031 tasks** (MCP Server)
   - MCP server implementation
   - Property CRUD tools
   - Clerk authentication
   - Claude Code CLI integration

**Phase 5: Property Management UX (7-10 days)**
5. **US-022 updated tasks** (Property Edit + Chat)
   - Property edit UI (inline editing)
   - Chat property creation
   - Admin dashboard
   - Integration with MCP

### 🔮 LOW PRIORITY (Future)

**Phase 6: Cloudflare R2 (4-6 days - FUTURE)**
6. **US-032 tasks** (R2 Integration)
   - R2 bucket setup
   - Image upload workflow
   - Migration script

**Phase 7: Library Extraction (Future - After realestate MVP)**
7. **Extract `lib/llm/` to separate package** (when patterns proven)

---

## Dependency Graph

```
PHASE 1: Investigation & Repair
  TASK-020-hotfix-editable-content (US-020 repair)
    ↓ BLOCKS
PHASE 2: Foundation (Parallel tracks)
  ┌─────────────────────────────────┬────────────────────────────────┐
  │                                 │                                │
  US-030: Shared Schema         US-033: LLM Refactoring    (US-020 fixed)
  (property schema,             (chat → lib/llm/chat/,      (editable pattern working)
   TypeScript types)             FAQ → lib/llm/faq/)
    ↓ ENABLES                       ↓ ENABLES                    ↓ ENABLES
PHASE 3: Integration
  ┌─────────────────────────────────┬────────────────────────────────┐
  │                                 │                                │
  US-031: MCP Server            US-022: Property Edit UI     (all depend on Phase 2)
  (property CRUD tools,         (inline editing,
   auth, CLI integration)        admin dashboard)
    ↓ ENABLES                       ↓
PHASE 4: Advanced Features
  ┌─────────────────────────────────┴────────────────────────────────┐
  │                                                                   │
  US-022: Chat Integration                                  US-032: R2 Integration
  (LLM property creation via MCP)                          (image storage - FUTURE)
```

---

## Specialist Agent Assignments

### Investigation & Repair (Phase 1)
- **Frontend Specialist**: Investigate editable component
- **Backend Specialist**: Verify API endpoints
- **DevOps Specialist**: Check database/Redis state

### Foundation (Phase 2-3)
- **Backend Specialist**: Shared schema + LLM refactoring
- **Frontend Specialist**: TypeScript type generation
- **DevOps Specialist**: CI/CD for schema synchronization

### Integration (Phase 4-5)
- **Backend Specialist**: MCP server + property CRUD
- **Frontend Specialist**: Property edit UI + chat integration
- **DevOps Specialist**: MCP deployment + monitoring

### Advanced (Phase 6-7)
- **DevOps Specialist**: Cloudflare R2 + image migration
- **Backend Specialist**: R2 API integration
- **CTO Specialist**: Library extraction strategy (future)

---

## Story Creation Checklist

### Immediate Actions
- [x] Create architecture spec: `EDITABLE-CONTENT-MCP-ARCHITECTURE.md`
- [x] Create story mapping: `STORY-MAPPING-EDITABLE-MCP.md`
- [ ] Create US-030: Shared Schema Infrastructure
- [ ] Create US-031: MCP Server for Property Management
- [ ] Create US-032: Cloudflare R2 Integration (low priority)
- [ ] Create US-033: LLM Library Refactoring
- [ ] Update US-022: Add property edit UX + chat integration scope
- [ ] Create TASK-020-hotfix-editable-content (bugfix for US-020)

### Story Files to Create
```bash
# Using docs-stories skill
Skill(docs-stories) → story_create.py
- US-030: shared schema infrastructure
- US-031: mcp property management
- US-032: cloudflare r2 integration
- US-033: llm refactoring extraction-ready

# Update existing
Skill(docs-stories) → story_update.py
- US-022: Add MCP + property edit + chat integration scope
```

---

## Questions for User (Before Creating Stories)

1. **Phase 1 Priority**: Confirm you want to start with US-020 repair (homepage editable content investigation)?
   - ✅ YES → Proceed with TASK-020-hotfix-editable-content
   - ❌ NO → Prioritize differently

2. **LLM Refactoring Timing**: Should US-033 (LLM library refactoring) run in parallel with schema work, or wait until after?
   - Option A: Parallel (faster, more complex coordination)
   - Option B: Sequential (slower, simpler dependencies)

3. **MCP Authentication**: Confirm Clerk JWT tokens are acceptable for MCP authentication?
   - ✅ YES → Use Bearer token in Authorization header
   - ❌ NO → Design alternative auth mechanism

4. **Cloudflare R2**: Confirm this is Phase 7 (future work), not blocking current milestone?
   - ✅ YES → Defer to after property management works
   - ❌ NO → Prioritize higher

5. **Property Import Source**: Confirm scraping from https://www.bestays.app/listings/properties-for-rent?
   - ✅ YES → Use web scraping (need to plan this task)
   - ❌ NO → Alternative data source?

---

## Success Metrics

### Phase 1 Success
- ✅ US-020 repair complete (editable content works)
- ✅ Regression tests prevent future breaks
- ✅ Postmortem documents what went wrong

### Phase 2 Success
- ✅ Shared property schema in use by frontend + backend
- ✅ LLM chat/FAQ refactored to `lib/llm/`
- ✅ All integration tests pass (nothing broken)

### Phase 3 Success
- ✅ MCP server works with Claude Code CLI
- ✅ Property CRUD via MCP (create, update, list)
- ✅ Clerk authentication validated

### Phase 4 Success
- ✅ Property edit UI works (inline editing, role-aware)
- ✅ Chat creates properties via MCP
- ✅ Admin can publish from dashboard

---

## Next Steps

1. **[NOW]** Launch specialist agents for architecture review:
   - CTO: Strategic validation
   - DevOps: Infrastructure planning
   - Backend: Technical feasibility
   - Frontend: UX validation

2. **[AFTER REVIEW]** Create new user stories:
   - US-030, US-031, US-032, US-033
   - Update US-022

3. **[AFTER STORIES]** Create Phase 1 task:
   - TASK-020-hotfix-editable-content

4. **[THEN]** Begin implementation:
   - Phase 1 → Phase 2 → Phase 3 → Phase 4

---

**Document Status**: Ready for Specialist Review
**Blocking**: Need user confirmation on questions above
**Next Action**: Launch specialist agents with full context

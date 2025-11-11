# Task: TASK-006 - Endpoint Restructuring + RBAC Integration

**Story:** US-001B - Role-Based Access Control Implementation
**Type:** refactor
**Status:** NOT_STARTED
**Created:** 2025-11-07
**Branch:** TBD (breaking change - needs dedicated branch)

## Description

Restructure API endpoints into clear domain-based organization and apply permission-based RBAC to all endpoints. This addresses:
- Confusing endpoint paths (e.g., `/admin/categories/` for FAQ categories)
- Mixed domains (FAQ, Chat, Admin scattered across paths)
- Missing RBAC enforcement (using basic `require_admin` instead of permissions)
- No audit logging on mutations

**See:** `.claude/reports/20251107-endpoint-structure-analysis.md` for full analysis

## Objectives

1. Restructure endpoints into domain-based paths
2. Add new FAQ and CHAT permissions
3. Apply `@require_permission` decorators to all endpoints
4. Add audit logging to all mutation endpoints
5. Update frontend to use new paths
6. Provide deprecation notices for old paths

## Proposed Domain Structure

### Domain 1: User Management (`/api/v1/users/`)
- GET /me → Authenticated (no permission)
- GET / → USER_VIEW
- GET /{user_id} → USER_VIEW
- PATCH /{user_id}/role → USER_UPDATE
- DELETE /{user_id} → USER_DELETE

### Domain 2: FAQ System (`/api/v1/faq/`)
```
/api/v1/faq/
├── categories/
│   ├── GET, POST, PUT, DELETE
│   └── Permissions: FAQ_VIEW, FAQ_CREATE, FAQ_UPDATE, FAQ_DELETE
│
├── documents/
│   ├── GET, POST, PUT, DELETE, POST /reindex
│   └── Permissions: FAQ_VIEW, FAQ_CREATE, FAQ_UPDATE, FAQ_DELETE
│
└── analytics/
    └── Permissions: FAQ_VIEW or AUDIT_VIEW
```

### Domain 3: Chat System (`/api/v1/chat/`)
```
/api/v1/chat/
├── / (POST) → PUBLIC (guest chat)
├── /health → PUBLIC
│
├── admin/prompts/
│   └── Permissions: CHAT_CONFIG
│
└── admin/tools/
    └── Permissions: CHAT_CONFIG
```

### Domain 4: Infrastructure (`/api/v1/`)
- /health, /health/ready, /health/live → PUBLIC
- /webhooks/clerk → Svix signature auth

## Technical Requirements

### Phase 1: Add New Permissions

**File:** `apps/server/src/server/api/auth/permissions.py`

Add to `Permission` enum:
```python
# FAQ permissions
FAQ_VIEW = "faq:view"
FAQ_CREATE = "faq:create"
FAQ_UPDATE = "faq:update"
FAQ_DELETE = "faq:delete"

# Chat configuration permissions
CHAT_CONFIG = "chat:config"
```

Update `ROLE_PERMISSIONS`:
```python
"admin": [
    # All existing...
    Permission.FAQ_VIEW,
    Permission.FAQ_CREATE,
    Permission.FAQ_UPDATE,
    Permission.FAQ_DELETE,
    Permission.CHAT_CONFIG,
],
"agent": [
    # All existing...
    Permission.FAQ_VIEW,
    Permission.FAQ_CREATE,
    Permission.FAQ_UPDATE,
    # Note: Agents CANNOT delete FAQs or configure chat
],
"user": [
    # All existing...
    Permission.FAQ_VIEW,
],
```

### Phase 2: Create New Endpoint Structure

**New Files to Create:**
```
apps/server/src/server/api/v1/endpoints/
├── faq/
│   ├── __init__.py
│   ├── categories.py (move from admin/categories.py)
│   └── documents.py (move from admin/faqs.py)
│
└── chat/
    ├── __init__.py
    ├── guest.py (move from llm/chat.py)
    └── admin.py (move from admin/chat_config.py)
```

**Each endpoint file must:**
1. Use `@require_permission` decorator
2. Call `AuditService.log_action()` for mutations
3. Follow file header pattern (ARCHITECTURE, PATTERNS, etc.)
4. Include proper docstrings
5. Return consistent error formats

### Phase 3: Update Router

**File:** `apps/server/src/server/api/v1/router.py`

```python
from server.api.v1.endpoints import users, webhooks
from server.api.v1.endpoints.faq import router as faq_router
from server.api.v1.endpoints.chat import router as chat_router

api_router = APIRouter()

# User management
api_router.include_router(users.router)

# FAQ system (new structure)
api_router.include_router(faq_router, prefix="/faq", tags=["faq"])

# Chat system (new structure)
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])

# Infrastructure
api_router.include_router(webhooks.router)
```

### Phase 4: Deprecate Old Endpoints

Keep old endpoints temporarily with deprecation warnings:
```python
@router.get("/admin/categories/")
@deprecated("Use /api/v1/faq/categories/ instead. This endpoint will be removed in v2.0")
async def old_list_categories():
    raise HTTPException(
        status_code=410,
        detail={
            "error": {
                "code": "ENDPOINT_DEPRECATED",
                "message": "This endpoint has moved to /api/v1/faq/categories/",
                "new_url": "/api/v1/faq/categories/",
                "removal_date": "2025-12-01"
            }
        }
    )
```

### Phase 5: Update Frontend

**Files to modify:**
- Update all API calls to use new paths
- Update TypeScript API client
- Test all user flows

### Phase 6: Add Audit Logging

For each mutation endpoint (POST, PUT, PATCH, DELETE):
```python
@router.post("/categories/", response_model=CategoryResponse)
@require_permission(Permission.FAQ_CREATE)
async def create_category(
    category_data: CategoryCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_clerk_user),
):
    # Create category...

    # Log audit trail
    await AuditService.log_action(
        db=db,
        entity_type="faq_category",
        entity_id=category.id,
        action="create",
        changes={"new": category_data.model_dump()}
    )

    return category
```

## Acceptance Criteria

### Backend
- [ ] New permissions added to `permissions.py`
- [ ] New endpoint structure created (`/faq/`, `/chat/`)
- [ ] All endpoints use `@require_permission` decorators
- [ ] All mutations log to audit trail
- [ ] Old endpoints return 410 Gone with migration info
- [ ] Router updated to use new structure
- [ ] All tests updated for new paths
- [ ] All tests passing

### Frontend
- [ ] API client updated for new paths
- [ ] All user flows tested
- [ ] No broken functionality

### Documentation
- [ ] API docs updated (Swagger/OpenAPI)
- [ ] Migration guide created
- [ ] Changelog updated
- [ ] Deprecation dates documented

## Files to Create/Modify

### Create
- `apps/server/src/server/api/v1/endpoints/faq/__init__.py`
- `apps/server/src/server/api/v1/endpoints/faq/categories.py`
- `apps/server/src/server/api/v1/endpoints/faq/documents.py`
- `apps/server/src/server/api/v1/endpoints/chat/__init__.py`
- `apps/server/src/server/api/v1/endpoints/chat/guest.py`
- `apps/server/src/server/api/v1/endpoints/chat/admin.py`
- `.claude/docs/api-migration-guide.md`

### Modify
- `apps/server/src/server/api/auth/permissions.py` (add FAQ/CHAT permissions)
- `apps/server/src/server/api/v1/router.py` (new router composition)
- `apps/server/src/server/api/v1/endpoints/users.py` (add RBAC + audit)
- `apps/server/tests/test_rbac.py` (add new permission tests)
- All frontend API calls

### Deprecate (keep temporarily)
- `apps/server/src/server/api/v1/endpoints/admin/categories.py`
- `apps/server/src/server/api/v1/endpoints/admin/faqs.py`
- `apps/server/src/server/api/v1/endpoints/admin/chat_config.py`
- `apps/server/src/server/api/v1/endpoints/llm/chat.py`

### Delete (after deprecation period)
- All deprecated files above

## Dependencies

### Completed
- TASK-002: Database migrations ✅
- TASK-003: RBAC components ✅
- TASK-004: Audit logging system ✅

### Requires
- TASK-005: E2E audit tests (recommended before this)
- User approval for breaking changes
- Coordination with frontend team

## Migration Path

### Step 1: Backend Changes (Non-Breaking)
1. Add new permissions
2. Create new endpoint structure alongside old
3. Test new endpoints
4. All tests passing

### Step 2: Frontend Migration
1. Update API client to use new paths
2. Test all user flows
3. Deploy frontend

### Step 3: Deprecation
1. Update old endpoints to return 410 Gone
2. Announce deprecation timeline
3. Monitor usage of old endpoints

### Step 4: Cleanup
1. Remove old endpoint files
2. Remove deprecation code
3. Update documentation

## Testing Strategy

### Backend Tests
- [ ] Permission tests for new permissions
- [ ] Endpoint tests with new paths
- [ ] RBAC enforcement tests
- [ ] Audit logging tests
- [ ] Deprecation endpoint tests (410 responses)

### Integration Tests
- [ ] Full flow tests with new paths
- [ ] Cross-domain tests (e.g., FAQ + Chat)

### E2E Tests
- [ ] All user flows with new paths
- [ ] Role-based access tests
- [ ] Audit trail verification

## Breaking Changes

⚠️ **This is a breaking change for frontend clients**

**What breaks:**
- All API calls to `/admin/categories/`
- All API calls to `/admin/faqs/`
- All API calls to `/admin/chat_config/`
- All API calls to `/llm/chat`

**Migration required:**
- Frontend must update all API paths
- External integrations must update
- Mobile apps must update

**Mitigation:**
- Old endpoints return 410 with new path
- Grace period before removal (30 days)
- Migration guide provided

## Success Criteria Checklist

- [ ] All new permissions added and tested
- [ ] New endpoint structure created
- [ ] All endpoints use `@require_permission`
- [ ] All mutations log audit trail
- [ ] Router updated
- [ ] Frontend updated
- [ ] All tests passing (backend + frontend + E2E)
- [ ] API documentation updated
- [ ] Migration guide created
- [ ] Deprecation notices in place

## Notes

### Why This Matters

**Current problems:**
- `/admin/categories/` → Confusing (property or FAQ categories?)
- Permissions scattered → Hard to audit who can do what
- No audit trail → Can't track changes
- Mixed domains → Hard to maintain and scale

**After restructuring:**
- Clear domain boundaries → Easy to understand
- Permission-based RBAC → Centralized authorization
- Audit trail → Full compliance and traceability
- Scalable → Easy to add new domains

### Risk Assessment

**Medium Risk:**
- Breaking changes for frontend
- Requires coordination across teams
- Potential for missed API calls during migration

**Mitigation:**
- Comprehensive testing before deployment
- Gradual migration path with deprecation period
- Clear communication and migration guide
- Monitoring of old endpoint usage

### Timeline Estimate

- Phase 1 (Permissions): 2 hours
- Phase 2 (New Endpoints): 8 hours
- Phase 3 (Router Update): 1 hour
- Phase 4 (Deprecation): 2 hours
- Phase 5 (Frontend Update): 4 hours
- Phase 6 (Audit Logging): 4 hours
- Testing: 4 hours
- Documentation: 2 hours

**Total:** ~27 hours (3-4 days)

### Future Enhancements

After this task:
- Add OpenAPI/Swagger documentation
- Add API versioning (v2) for future breaking changes
- Add rate limiting per domain
- Add domain-specific middleware

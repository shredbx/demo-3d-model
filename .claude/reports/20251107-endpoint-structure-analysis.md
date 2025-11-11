# Current Endpoint Structure Analysis

## Current Endpoints (Grouped by Current Location)

### `/api/v1/users/` - User Management
- GET /me - Get current user profile
- GET / - List users (admin-only)
- GET /{clerk_user_id} - Get specific user
- PATCH /{clerk_user_id}/role - Update user role
- DELETE /{clerk_user_id} - Delete user

### `/api/v1/admin/categories/` - FAQ Categories (CONFUSING NAME)
- GET / - List FAQ categories
- POST / - Create FAQ category
- PUT /{category_id} - Update FAQ category
- DELETE /{category_id} - Delete FAQ category

### `/api/v1/admin/faqs/` - FAQ Management
- GET / - List FAQs
- GET /{faq_id} - Get FAQ detail
- POST / - Create FAQ
- PUT /{faq_id} - Update FAQ
- DELETE /{faq_id} - Delete FAQ
- POST /reindex - Reindex FAQs for search

### `/api/v1/admin/chat_config/` - Chat Configuration
**Prompts:**
- GET /prompts - List chat prompts
- GET /prompts/active - Get active prompt
- GET /prompts/{prompt_id} - Get specific prompt
- POST /prompts - Create prompt
- PUT /prompts/{prompt_id} - Update prompt
- PUT /prompts/{prompt_id}/activate - Activate prompt
- DELETE /prompts/{prompt_id} - Delete prompt
- GET /prompts/{prompt_id}/history - Get prompt history

**Tools:**
- GET /tools - List chat tools
- GET /tools/{tool_name} - Get specific tool
- PUT /tools/{tool_name} - Update tool config
- PUT /tools/{tool_name}/toggle - Enable/disable tool

### `/api/v1/llm/` - Chat & AI
- GET /health - LLM health check
- POST /chat - Guest chat endpoint

### `/api/v1/webhooks/` - Webhooks
- POST /clerk - Clerk webhook events

### `/api/v1/` - Infrastructure
- GET /health - Basic health check
- GET /health/ready - Readiness probe
- GET /health/live - Liveness probe

---

## PROBLEMS Identified

1. **Confusing Naming**: `/admin/categories/` looks like property categories, but it's FAQ categories
2. **Domain Mixing**: FAQ, Chat Config, and Categories are related but split across paths
3. **No RBAC Applied**: Using basic `require_admin` instead of permission-based RBAC
4. **Inconsistent Nesting**: Some admin endpoints under `/admin/`, others not
5. **No Audit Logging**: None of the mutation endpoints trigger audit logs yet

---

## PROPOSED Domain-Based Structure

### Domain 1: **User Management** (`/api/v1/users/`)
**Purpose:** User profiles, roles, and account management
**Permissions Required:**
- GET /me → Authenticated (no specific permission)
- GET / → USER_VIEW
- GET /{user_id} → USER_VIEW
- PATCH /{user_id}/role → USER_UPDATE
- DELETE /{user_id} → USER_DELETE

**Audit Logging:** Yes (user updates/deletes)

---

### Domain 2: **FAQ System** (`/api/v1/faq/`)
**Purpose:** FAQ content, categories, and related FAQs
**Permissions Required:** FAQ_VIEW, FAQ_CREATE, FAQ_UPDATE, FAQ_DELETE

#### Proposed Structure:
```
/api/v1/faq/
├── categories/
│   ├── GET    /           → List categories (FAQ_VIEW)
│   ├── POST   /           → Create category (FAQ_CREATE)
│   ├── GET    /{id}       → Get category (FAQ_VIEW)
│   ├── PUT    /{id}       → Update category (FAQ_UPDATE)
│   └── DELETE /{id}       → Delete category (FAQ_DELETE)
│
├── documents/
│   ├── GET    /           → List FAQs (FAQ_VIEW)
│   ├── POST   /           → Create FAQ (FAQ_CREATE)
│   ├── GET    /{id}       → Get FAQ (FAQ_VIEW)
│   ├── PUT    /{id}       → Update FAQ (FAQ_UPDATE)
│   ├── DELETE /{id}       → Delete FAQ (FAQ_DELETE)
│   └── POST   /reindex    → Reindex search (FAQ_UPDATE)
│
└── analytics/
    ├── GET    /           → View FAQ analytics (AUDIT_VIEW or FAQ_VIEW)
    └── GET    /{id}       → Get specific FAQ analytics (FAQ_VIEW)
```

**Audit Logging:** Yes (FAQ content changes tracked)

---

### Domain 3: **Chat System** (`/api/v1/chat/`)
**Purpose:** AI chat, prompts, tools, and guest conversations
**Permissions Required:** CHAT_CONFIG (for admin), Public (for guest chat)

#### Proposed Structure:
```
/api/v1/chat/
├── /                      → POST Guest chat (PUBLIC)
├── /health               → GET Chat health (PUBLIC)
│
├── admin/prompts/
│   ├── GET    /           → List prompts (CHAT_CONFIG)
│   ├── GET    /active     → Get active prompt (CHAT_CONFIG)
│   ├── POST   /           → Create prompt (CHAT_CONFIG)
│   ├── GET    /{id}       → Get prompt (CHAT_CONFIG)
│   ├── PUT    /{id}       → Update prompt (CHAT_CONFIG)
│   ├── PUT    /{id}/activate → Activate prompt (CHAT_CONFIG)
│   ├── DELETE /{id}       → Delete prompt (CHAT_CONFIG)
│   └── GET    /{id}/history → Prompt history (CHAT_CONFIG)
│
└── admin/tools/
    ├── GET    /           → List tools (CHAT_CONFIG)
    ├── GET    /{name}     → Get tool (CHAT_CONFIG)
    ├── PUT    /{name}     → Update tool (CHAT_CONFIG)
    └── PUT    /{name}/toggle → Toggle tool (CHAT_CONFIG)
```

**Audit Logging:** Yes (prompt/tool config changes tracked)

---

### Domain 4: **Infrastructure** (`/api/v1/`)
**Purpose:** Health checks, webhooks, system endpoints
**Permissions Required:** Public

```
/api/v1/
├── /health              → GET Basic health (PUBLIC)
├── /health/ready        → GET Readiness probe (PUBLIC)
├── /health/live         → GET Liveness probe (PUBLIC)
└── /webhooks/
    └── clerk            → POST Clerk webhook (Svix auth)
```

**Audit Logging:** No (infrastructure only)

---

## NEW Permissions to Add

Based on the domains, we need to add these to `Permission` enum:

```python
# FAQ permissions
FAQ_VIEW = "faq:view"
FAQ_CREATE = "faq:create"
FAQ_UPDATE = "faq:update"
FAQ_DELETE = "faq:delete"

# Chat configuration permissions
CHAT_CONFIG = "chat:config"
```

---

## Role Mapping Updates

```python
ROLE_PERMISSIONS = {
    "admin": [
        # All existing permissions...
        Permission.FAQ_VIEW,
        Permission.FAQ_CREATE,
        Permission.FAQ_UPDATE,
        Permission.FAQ_DELETE,
        Permission.CHAT_CONFIG,
    ],
    "agent": [
        # All existing permissions...
        Permission.FAQ_VIEW,
        Permission.FAQ_CREATE,
        Permission.FAQ_UPDATE,
        # Note: Agents CANNOT delete FAQs or configure chat
    ],
    "user": [
        # All existing permissions...
        Permission.FAQ_VIEW,  # Users can view FAQs
        # Note: Users CANNOT create/update/delete FAQs
    ],
}
```

---

## Migration Path

### Phase 1: Add New Permissions
1. Update `permissions.py` with FAQ and CHAT permissions
2. Update `ROLE_PERMISSIONS` mapping
3. Run tests to ensure no regressions

### Phase 2: Restructure Endpoints (Breaking Change)
1. Create new router structure
2. Move endpoints to domain-based paths
3. Apply `@require_permission` decorators
4. Add audit logging to mutations
5. Update frontend to use new paths
6. Deprecate old paths (return 410 Gone with migration info)

### Phase 3: Remove Old Endpoints
1. Remove deprecated paths after grace period
2. Update all documentation

---

## Files to Create/Modify

### New Files:
- `apps/server/src/server/api/v1/endpoints/faq/categories.py`
- `apps/server/src/server/api/v1/endpoints/faq/documents.py`
- `apps/server/src/server/api/v1/endpoints/faq/__init__.py`
- `apps/server/src/server/api/v1/endpoints/chat/guest.py`
- `apps/server/src/server/api/v1/endpoints/chat/admin.py`
- `apps/server/src/server/api/v1/endpoints/chat/__init__.py`

### Modify:
- `apps/server/src/server/api/auth/permissions.py` (add FAQ/CHAT permissions)
- `apps/server/src/server/api/v1/router.py` (update router composition)
- All endpoint files (add RBAC decorators + audit logging)

### Delete (after deprecation):
- `apps/server/src/server/api/v1/endpoints/admin/categories.py`
- `apps/server/src/server/api/v1/endpoints/admin/faqs.py`
- `apps/server/src/server/api/v1/endpoints/admin/chat_config.py`
- `apps/server/src/server/api/v1/endpoints/llm/` (move to chat/)

---

## Testing Requirements

1. **Unit Tests**: Permission checks for each endpoint
2. **Integration Tests**: RBAC enforcement end-to-end
3. **E2E Tests**: Frontend flows with new paths
4. **Migration Tests**: Old paths return proper deprecation responses
5. **Audit Tests**: Mutations create audit logs

---

## Summary

**Current State:** Confusing structure, no RBAC, no audit logging, domains mixed
**Proposed State:** Clear domains, permission-based RBAC, automatic audit logging
**Impact:** Breaking changes for frontend (new API paths)
**Benefit:** Maintainable, secure, compliant, scalable


# Research Findings: Bestays Codebase Analysis for Multi-Product Architecture

**Task:** TASK-001 - Research Codebase Structure
**Date:** 2025-11-07
**Status:** Complete
**Duration:** ~2 hours
**Researcher:** research-codebase agent (Claude Code)

---

## Executive Summary

The Bestays codebase is a **modern full-stack real estate platform** built with **SvelteKit (frontend)** and **FastAPI (backend)** using **PostgreSQL**. The current architecture is **already well-structured** for multi-product transformation with:

✅ **Clean separation** - Frontend and backend are independent applications
✅ **Modern async patterns** - FastAPI async + SQLAlchemy 2.0 + asyncpg
✅ **Comprehensive authentication** - Clerk integration (JWT + RBAC + JIT provisioning)
✅ **Production-ready features** - Chat (4500+ LOC), FAQ with RAG (vector search + keyword search), User management
✅ **Docker orchestration** - Docker Compose for development, production-ready setup exists
✅ **Database migrations** - Alembic with comprehensive schema

**Key Challenges:**
❌ No monorepo tooling (Turborepo/pnpm workspaces)
❌ Clerk configuration is environment-based (requires separate projects per product)
❌ Chat and FAQ features are tightly coupled to the existing application
❌ No shared packages structure yet

**Recommendation:** The codebase is **ready for transformation** with a **phased migration approach**:
1. Extract shared features (Chat, FAQ) into packages
2. Set up monorepo tooling (Turborepo + pnpm)
3. Duplicate and configure separate apps (Bestays, Real Estate)
4. Implement product-specific branding and configuration

---

## 1. Authentication Patterns (Clerk Integration)

### Current Implementation

**Location:** User Story `US-001-login-flow-validation.md`

**Architecture:**
- **Frontend SDK:** `@clerk/clerk-js` v5.102.1
- **Backend SDK:** `clerk-backend-api` v3.3.1
- **Pattern:** JWT token validation + JIT provisioning + RBAC

### Frontend Clerk Integration

**File:** `/apps/frontend/src/lib/clerk.ts` (110 lines)

**Key Functions:**
```typescript
- clerk.load(): Initialize Clerk SDK
- clerk.mountSignIn(div, options): Mount sign-in UI
- getClerkToken(): Get current session token
- isSignedIn(): Check authentication status
- getCurrentClerkUser(): Get Clerk user object
```

**Initialization Pattern:**
- Singleton instance created in `clerk.ts`
- Initialized globally in `+layout.svelte` (onMount)
- Environment variable: `VITE_CLERK_PUBLISHABLE_KEY`

**File:** `/apps/frontend/src/lib/stores/auth.svelte.ts` (120 lines)

**State Management:**
```typescript
class AuthStore {
  user: User | null
  isLoading: boolean
  error: string | null
  
  // Computed (reactive)
  isSignedIn: boolean
  isAdmin: boolean
  isAgent: boolean
  isUser: boolean
  
  // Methods
  fetchUser(): Promise<void>  // GET /api/v1/users/me
  clearUser(): void
  initialize(): Promise<void>
}
```

**Flow:**
```
User logs in (Clerk UI)
  ↓
Clerk handles authentication
  ↓
authStore.fetchUser() → GET /api/v1/users/me (with Clerk token)
  ↓
redirectAfterAuth(role) → redirect based on role
  - user → /
  - agent → /dashboard
  - admin → /dashboard
```

### Backend Clerk Integration

**File:** `/apps/server/src/server/core/clerk.py` (44 lines)

**Pattern:** Singleton Clerk client

```python
from clerk_backend_api import Clerk
from server.config import settings

clerk_client = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)
```

**File:** `/apps/server/src/server/api/clerk_deps.py` (256 lines)

**Key Dependencies:**
```python
async def get_clerk_user(request, db) -> User:
    """
    1. Validate Clerk token (JWT)
    2. Fetch user from local DB by clerk_user_id
    3. JIT provision if missing (webhook failure fallback)
    4. First admin bootstrap (promote first user to admin if no admins exist)
    5. Return User object
    """

async def require_admin(current_user) -> User:
    """RBAC: Admin-only access"""

async def require_agent_or_admin(current_user) -> User:
    """RBAC: Agent or Admin access"""
```

**Flow:**
```
Request with Authorization: Bearer <clerk-token>
  ↓
clerk_client.authenticate_request(request, options)
  ↓
Validate token signature, expiry, authorized parties
  ↓
Extract clerk_user_id from JWT payload
  ↓
Query local DB: SELECT * FROM users WHERE clerk_id = ?
  ↓
If not found → JIT provision from Clerk API
  ↓
First admin bootstrap check (if user.role == 'user' AND admin count == 0 → promote to admin)
  ↓
Return User object
```

### Environment Configuration

**Backend (`/apps/server/src/server/config.py`):**
```python
CLERK_SECRET_KEY: str = "test_clerk_secret_key"  # sk_test_* or sk_live_*
CLERK_PUBLISHABLE_KEY: str = "test_clerk_publishable_key"  # pk_test_*
CLERK_WEBHOOK_SECRET: str = "test_clerk_webhook_secret"  # whsec_*
FRONTEND_URL: str = "http://localhost:5183"
```

**Frontend (`VITE_*` in .env):**
```bash
VITE_CLERK_PUBLISHABLE_KEY=pk_test_*
VITE_API_URL=http://localhost:8101
```

### Reusability Analysis

#### ✅ Reusable for Multi-Product (Shared Logic)
- **Clerk SDK initialization pattern** - Can be abstracted into shared function
- **Auth store pattern** (Svelte 5 runes) - Can be copied to each product
- **JWT validation logic** (backend) - Can be shared in common package
- **RBAC patterns** (require_admin, require_agent) - Can be shared
- **JIT provisioning logic** - Can be shared

#### ❌ Product-Specific (Needs Duplication or Configuration)
- **Clerk API keys** - Each product needs separate Clerk project
  - `CLERK_SECRET_KEY` (backend)
  - `CLERK_PUBLISHABLE_KEY` (frontend)
  - `CLERK_WEBHOOK_SECRET` (backend)
- **User database** - Separate `users` table per product (or tenant_id)
- **Authorized parties** - `FRONTEND_URL` differs per product
- **Redirect logic** - Role-based redirects might differ per product

### Recommendations for White-Label Architecture

**Option 1: Separate Clerk Projects (Recommended)**
```
bestays-rentals/
  .env.production
    CLERK_SECRET_KEY=sk_live_bestays_rentals_*
    CLERK_PUBLISHABLE_KEY=pk_live_bestays_rentals_*
    FRONTEND_URL=https://bestays.com

realestate-sales/
  .env.production
    CLERK_SECRET_KEY=sk_live_realestate_*
    CLERK_PUBLISHABLE_KEY=pk_live_realestate_*
    FRONTEND_URL=https://realestate.com
```

**Benefits:**
- Complete user isolation (no shared authentication)
- Separate Clerk dashboards (different user management)
- Different branding/UX per product
- Independent security policies

**Challenges:**
- Duplicate Clerk subscriptions (cost)
- No cross-product user accounts (feature, not bug)

**Option 2: Shared Clerk with Metadata (NOT RECOMMENDED)**
```javascript
// Store product ID in user metadata
clerk.user.publicMetadata.product = "bestays" | "realestate"
```

**Benefits:**
- Single Clerk subscription
- Users can have accounts in both products

**Challenges:**
- Users are shared across products (violates US-018 requirement)
- Complex RBAC (product-based permissions)
- Risk of data leakage between products

**Verdict:** **Use Option 1** (separate Clerk projects) to meet US-018 requirement: "separate user bases (different Clerk projects - NOT shared authentication)."

---

## 2. Data Modeling Patterns

### Current Implementation

**Location:** `/apps/server/src/server/models/`

**ORM:** SQLAlchemy 2.0 (async) with asyncpg driver

**Patterns Used:**
- Declarative Base with type hints (`Mapped[...]`)
- Server-side timestamps (`server_default=func.now()`)
- UUID primary keys (`gen_random_uuid()`)
- JSONB columns for flexible data
- Foreign key relationships
- Soft deletes (`deleted_at` timestamp)
- Audit tracking (`created_by`, `updated_by`)

### Key Models

#### User Model

**File:** `/apps/server/src/server/models/user.py`

```python
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    clerk_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(20), default="user")  # user | agent | admin
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
```

#### Property Model

**File:** `/apps/server/src/server/models/property.py`

**User Story:** `US-016-property-migration-design.md`

```python
class Property(Base):
    __tablename__ = "properties"
    
    # Primary key
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, server_default=func.gen_random_uuid())
    
    # Basic
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Publishing
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    # Audit tracking
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    published_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by])
    updater: Mapped[Optional["User"]] = relationship("User", foreign_keys=[updated_by])
    publisher: Mapped[Optional["User"]] = relationship("User", foreign_keys=[published_by])
```

**Note:** There is a comprehensive V2 schema planned (60+ columns, JSONB fields, translations) in the migration user story.

#### Chat Models

**File:** `/apps/server/src/server/models/chat.py`

```python
class Conversation(Base):
    __tablename__ = "conversations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)  # UUID for guests
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)  # NULL for guests
    title: Mapped[Optional[str]]
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    
    messages: Mapped[list["Message"]] = relationship("Message", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"))
    role: Mapped[str] = mapped_column(String(20))  # user | assistant | system
    content: Mapped[str] = mapped_column(Text)
    model: Mapped[Optional[str]]  # OpenRouter model used
    prompt_tokens: Mapped[Optional[int]]
    completion_tokens: Mapped[Optional[int]]
    cost_usd: Mapped[Optional[float]]
    created_at: Mapped[datetime]
```

**Pattern:** Guest support (nullable user_id, session_id for tracking)

#### FAQ Models

**File:** `/apps/server/src/server/models/faq.py`

**Comprehensive RAG system:**

```python
class FAQCategory(Base):
    __tablename__ = "faq_categories"
    
    id: Mapped[UUID]
    name: Mapped[str]
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    parent_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("faq_categories.id"))
    level: Mapped[int] = mapped_column(Integer, default=0)  # 0=main, 1=sub
    is_active: Mapped[bool]
    
    children: Mapped[list["FAQCategory"]] = relationship(...)
    documents: Mapped[list["FAQDocument"]] = relationship(...)

class FAQDocument(Base):
    __tablename__ = "faq_documents"
    
    id: Mapped[UUID]
    question: Mapped[str] = mapped_column(String(200))
    answer: Mapped[str] = mapped_column(Text)
    category_id: Mapped[Optional[UUID]]
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft | published | archived
    tags: Mapped[Optional[list[str]]] = mapped_column(ArrayType)
    
    # Analytics
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    helpful_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # JSONB
    faq_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    
    embeddings: Mapped[list["FAQEmbedding"]] = relationship(...)

class FAQEmbedding(Base):
    __tablename__ = "faq_embeddings"
    
    id: Mapped[UUID]
    document_id: Mapped[UUID] = mapped_column(ForeignKey("faq_documents.id", ondelete="CASCADE"))
    chunk_text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[Optional[list[float]]] = mapped_column(JSON)  # 1536-dim vectors (OpenAI ada-002)
    chunk_index: Mapped[Optional[int]]
```

### Database Configuration

**File:** `/apps/server/src/server/core/database.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DATABASE_ECHO,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

**Pattern:** FastAPI dependency injection with async context manager

**Environment Variable:**
```python
DATABASE_URL: PostgresDsn  # postgresql+asyncpg://user:pass@host:port/db
```

### Migrations

**Tool:** Alembic

**Location:** `/apps/server/alembic/versions/`

**Migrations Found:**
- `20251021_2053-289f7ac3c0ae_create_users_table_for_authentication.py`
- `20251024_0418-clerk_integration.py`
- `20251024_0514-a438dcb04080_add_webhook_events_table_for_idempotency.py`
- `20251024_0719-rename_customer_role_to_user.py`
- `20251024_1709-e199f68360bf_add_chat_conversations_and_messages.py`
- `20251025_2304_add_chat_config_tables.py`
- `20251025_add_faq_tables.py`
- `20251025_enable_pgvector_extension.py`
- `20251107_0230-add_rbac_audit_tables.py`

**Pattern:** Timestamped migrations with descriptive names

### Reusability Analysis

#### ✅ Reusable for Multi-Product (Shared Schema)
- **Base class pattern** - All models extend `Base` (can be shared)
- **Common fields pattern** - `created_at`, `updated_at`, UUID primary keys
- **Audit pattern** - `created_by`, `updated_by` (can be shared)
- **Migration tooling** - Alembic configuration
- **SQLAlchemy 2.0 patterns** - Async sessions, type hints

#### ❌ Product-Specific (Needs Isolation)
- **Database instances** - Separate PostgreSQL databases per product
  - Option A: `bestays_db` and `realestate_db` (complete isolation)
  - Option B: Single DB with `tenant_id` column (multi-tenant)
- **User tables** - Separate users per product (different Clerk projects)
- **Property schema** - Might differ between products
  - Bestays: Rental properties (apartments, villas)
  - Real Estate: High-value properties (land, commercial, investment)
- **FAQ content** - Product-specific FAQ data
- **Chat conversations** - Separate conversation history per product

### Recommendations for White-Label Architecture

**Option 1: Separate Databases (Recommended for US-018)**
```
PostgreSQL Instance
├── bestays_db
│   ├── users (Clerk project A)
│   ├── properties (rental-focused)
│   ├── conversations
│   └── faq_documents
└── realestate_db
    ├── users (Clerk project B)
    ├── properties (high-value focused)
    ├── conversations
    └── faq_documents
```

**Benefits:**
- Complete data isolation (meets US-018 requirement)
- Independent backups and scaling
- No risk of data leakage
- Clear separation of concerns

**Challenges:**
- Duplicate schemas (migrations run twice)
- No shared data (feature, not bug)

**Option 2: Multi-Tenant with tenant_id (NOT RECOMMENDED)**
```sql
ALTER TABLE users ADD COLUMN tenant_id VARCHAR(50);  -- 'bestays' | 'realestate'
ALTER TABLE properties ADD COLUMN tenant_id VARCHAR(50);
-- All queries: WHERE tenant_id = ?
```

**Benefits:**
- Single database (simpler ops)
- Shared infrastructure

**Challenges:**
- Risk of data leakage (WHERE clause errors)
- Violates US-018 requirement (not separate databases)
- Complex RLS policies

**Verdict:** **Use Option 1** (separate databases) to meet US-018 isolation requirement.

**Migration Strategy:**
1. Create shared SQLAlchemy models package (`@bestays/db-models`)
2. Each app imports and uses same schema
3. Alembic migrations run per database:
   - `alembic -c bestays.ini upgrade head`
   - `alembic -c realestate.ini upgrade head`

---

## 3. Chat Feature Implementation

### Overview

**Location:** `/apps/frontend/src/lib/components/chat/`

**Total LOC:** ~4500 lines (backend + frontend)

**Status:** MVP complete, metadata-driven UI pending

**Technologies:**
- **Frontend:** SvelteKit, Svelte 5 (runes), TypeScript
- **Backend:** FastAPI, LangChain, OpenRouter API
- **State Management:** Svelte writable stores
- **API:** HTTP POST `/api/v1/llm/chat`

### Frontend Implementation

**Components:**

| File | Purpose | LOC | Status |
|------|---------|-----|--------|
| `ChatInterface.svelte` | Main container | 343 | Complete |
| `MessageList.svelte` | Scrollable message display | 136 | Complete |
| `Message.svelte` | Individual message | 145 | Complete |
| `MessageInput.svelte` | Text input with validation | 243 | Complete |
| `ChatToggle.svelte` | FAB button | 120 | Complete |
| `MessageRenderer.svelte` | Markdown rendering | ~100 | Complete |
| `AttachmentRenderer.svelte` | Metadata attachments | ~80 | Partial |

**State Management:**

**File:** `/apps/frontend/src/lib/stores/chat.ts` (163 lines)

```typescript
// Svelte writable stores
export const messages = writable<Message[]>([]);
export const isExpanded = writable<boolean>(false);
export const isLoading = writable<boolean>(false);
export const error = writable<string | null>(null);
export const sessionId = writable<string | null>(null);
export const conversationId = writable<number | null>(null);

// Actions
export async function sendMessage(content: string) {
  // 1. Add user message optimistically
  messages.update(m => [...m, { role: 'user', content }]);
  
  // 2. Call API
  isLoading.set(true);
  const response = await chatApi.sendMessage(content);
  
  // 3. Add assistant message
  messages.update(m => [...m, response.message]);
  
  // 4. Update IDs
  sessionId.set(response.session_id);
  conversationId.set(response.conversation_id);
}
```

**API Client:**

**File:** `/apps/frontend/src/lib/services/chatApi.ts` (129 lines)

```typescript
export const chatApi = {
  async sendMessage(content: string): Promise<ChatResponse> {
    const response = await fetch(`${API_URL}/llm/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${await getClerkToken()}`
      },
      body: JSON.stringify({ content, session_id: sessionId })
    });
    
    return response.json();
  }
};
```

**Type Definitions:**

**File:** `/apps/frontend/src/lib/types/chat.ts` (95 lines)

```typescript
export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export interface ChatResponse {
  message: Message;
  model: string;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  finish_reason: string;
  conversation_id: number;
  session_id: string;
  // TODO: metadata field not yet used
}
```

### Backend Implementation

**Services:**

| File | Purpose | LOC | Complexity |
|------|---------|-----|------------|
| `chat_service.py` | Main chat orchestration | ~300 | High |
| `conversation_service.py` | Conversation management | ~200 | Medium |
| `chat_config_service.py` | Configuration | ~150 | Low |
| `chat_tools/faq_tool.py` | FAQ RAG integration | ~200 | High |

**Endpoint:**

**File:** `/apps/server/src/server/api/v1/endpoints/llm/chat.py`

```python
@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = None  # Guest support
):
    """
    Chat endpoint with AI assistant.
    
    Flow:
    1. Get or create conversation (by session_id)
    2. Add user message to DB
    3. Call LLM via chat_service (LangChain + OpenRouter)
    4. Add assistant message to DB
    5. Return response with metadata
    """
```

**LLM Integration:**

**Technology:** LangChain + OpenRouter API

**Models Used:**
- Chat: `anthropic/claude-3-sonnet` (default)
- Search: `anthropic/claude-3-haiku`
- Fallback: `openai/gpt-4o-mini`

**Tools Available:**
- FAQ RAG search (vector + keyword hybrid)
- Future: Property search, booking, etc.

**Configuration:**

**File:** `/apps/server/src/server/models/chat_config.py`

```python
class ChatPrompt(Base):
    """System prompt configuration (admin-editable)"""
    system_prompt: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool]
    environment: Mapped[str] = mapped_column(String(20), default="production")

class ChatTool(Base):
    """Chat tools configuration"""
    name: Mapped[str] = mapped_column(String(100), unique=True)  # e.g., 'faq_rag'
    is_enabled: Mapped[bool]
    config: Mapped[dict] = mapped_column(JSONB)  # Tool-specific config
```

**Pattern:** Database-driven configuration (no code changes to update prompts/tools)

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     CHAT ARCHITECTURE                    │
└─────────────────────────────────────────────────────────┘

Frontend (SvelteKit)
┌──────────────────────────────────────────────────────────┐
│ ChatInterface.svelte (Container)                         │
│   ├─ MessageList.svelte                                  │
│   │   └─ Message.svelte × N                              │
│   │       └─ MessageRenderer.svelte (Markdown)           │
│   │           └─ AttachmentRenderer.svelte (Metadata)    │
│   └─ MessageInput.svelte (Text input + validation)       │
│                                                           │
│ Svelte Stores (chat.ts)                                  │
│   ├─ messages: Message[]                                 │
│   ├─ isLoading: boolean                                  │
│   └─ sendMessage(content) → chatApi.sendMessage()        │
└──────────────────────────────────────────────────────────┘
                        ↓ HTTP POST
┌──────────────────────────────────────────────────────────┐
│ Backend (FastAPI)                                        │
│                                                           │
│ POST /api/v1/llm/chat                                    │
│   ├─ Get/create conversation (session_id)               │
│   ├─ Save user message                                   │
│   ├─ Call ChatService                                    │
│   │   ├─ Load system prompt (ChatPrompt)                │
│   │   ├─ Load enabled tools (ChatTool)                  │
│   │   ├─ Build LangChain chain                          │
│   │   ├─ Call OpenRouter API (Claude/GPT)               │
│   │   └─ Tools: FAQ RAG search (optional)               │
│   ├─ Save assistant message                              │
│   └─ Return ChatResponse                                 │
│                                                           │
│ Database (PostgreSQL)                                    │
│   ├─ conversations (session_id, user_id)                │
│   ├─ messages (role, content, tokens, cost)             │
│   ├─ chat_prompts (system_prompt, is_active)            │
│   └─ chat_tools (name, is_enabled, config)              │
└──────────────────────────────────────────────────────────┘
```

### External Dependencies

**Frontend:**
- None (vanilla Svelte, no chat libraries)

**Backend:**
- `langchain>=0.3.0` - LLM orchestration
- `langchain-openai>=0.2.0` - OpenAI/OpenRouter integration
- `langchain-anthropic>=0.2.0` - Anthropic/Claude integration
- `tiktoken>=0.8.0` - Token counting
- `sse-starlette>=2.2.0` - Streaming (not yet used)

**API Keys Required:**
- `OPENROUTER_API_KEY` - For LLM calls

### Reusability for Multi-Product

#### ✅ Highly Reusable (Extract to @bestays/chat)

**Frontend Components:**
- All Svelte components are product-agnostic
- Minimal branding (colors, logo via CSS variables)
- No hardcoded business logic

**Backend Services:**
- `ChatService` - LLM orchestration
- `ConversationService` - Conversation management
- `ChatConfigService` - Configuration management

**Database Schema:**
- `conversations` table - Generic, works for any product
- `messages` table - Generic
- `chat_prompts` table - Product-specific content, shared structure
- `chat_tools` table - Product-specific config, shared structure

#### ❌ Product-Specific Configuration

**System Prompts:**
```sql
-- Bestays (rentals)
INSERT INTO chat_prompts (system_prompt, is_active) VALUES 
('You are a helpful assistant for Bestays, a vacation rental platform...', true);

-- Real Estate (high-value properties)
INSERT INTO chat_prompts (system_prompt, is_active) VALUES 
('You are a real estate advisor specializing in luxury properties...', true);
```

**Tools Enabled:**
```sql
-- Bestays: FAQ + Booking
UPDATE chat_tools SET is_enabled = true WHERE name IN ('faq_rag', 'booking_calendar');

-- Real Estate: FAQ + Investment Analysis
UPDATE chat_tools SET is_enabled = true WHERE name IN ('faq_rag', 'investment_calculator');
```

**Branding:**
```css
/* bestays.css */
--chat-primary-color: #3B82F6;
--chat-assistant-bg: #F3F4F6;

/* realestate.css */
--chat-primary-color: #10B981;
--chat-assistant-bg: #ECFDF5;
```

### Migration Strategy to @bestays/chat Package

**Phase 1: Extract Components**
```
packages/chat/
├── frontend/
│   ├── components/
│   │   ├── ChatInterface.svelte
│   │   ├── MessageList.svelte
│   │   ├── Message.svelte
│   │   └── MessageInput.svelte
│   ├── stores/
│   │   └── chat.ts
│   └── types/
│       └── chat.ts
└── backend/
    ├── services/
    │   ├── chat_service.py
    │   └── conversation_service.py
    ├── models/
    │   ├── conversation.py
    │   └── chat_config.py
    └── api/
        └── chat_router.py
```

**Phase 2: Configuration Layer**
```typescript
// apps/bestays-web/src/config/chat.ts
export const chatConfig = {
  branding: {
    primaryColor: '#3B82F6',
    assistantBg: '#F3F4F6',
  },
  features: {
    guestMessagesLimit: 5,
    enableVoiceInput: false,
    enableFileUpload: true,
  }
};
```

```python
# apps/bestays-api/config/chat.py
CHAT_CONFIG = {
    "system_prompt_default": "You are a helpful assistant for Bestays...",
    "tools_enabled": ["faq_rag", "booking_calendar"],
    "models": {
        "chat": "anthropic/claude-3-sonnet",
        "search": "anthropic/claude-3-haiku"
    }
}
```

**Phase 3: Import in Apps**
```typescript
// apps/bestays-web/src/routes/+layout.svelte
import { ChatInterface } from '@bestays/chat/frontend';
import { chatConfig } from '$config/chat';

<ChatInterface config={chatConfig} />
```

```python
# apps/bestays-api/main.py
from bestays_chat import ChatRouter

app.include_router(ChatRouter(config=CHAT_CONFIG))
```

### Complexity Estimate

**Extraction Effort:** Medium (2-3 days)
- Components are well-isolated
- Minimal dependencies
- Clear API boundaries

**Challenges:**
- CSS scoping (ensure Svelte component styles work in package)
- Environment variables (API_URL needs to be configurable)
- Store initialization (shared vs. product-specific)

**Recommendation:** Extract chat early (Phase 2 of migration) to validate package pattern.

---

## 4. FAQ Feature Implementation

### Overview

**Location:** `/apps/server/src/server/services/faq*.py`

**Total LOC:** ~2000 lines (backend RAG system + frontend admin UI)

**Status:** Production-ready RAG system with hybrid search

**Technologies:**
- **Vector Search:** pgvector extension + OpenAI embeddings (1536-dim)
- **Keyword Search:** PostgreSQL full-text search
- **Caching:** Redis (15-min query cache)
- **LLM:** OpenAI GPT-4 (response generation)

### Backend Implementation

**Services:**

| File | Purpose | LOC | Complexity |
|------|---------|-----|------------|
| `faq_rag_pipeline.py` | End-to-end RAG orchestration | ~300 | High |
| `faq_vector_search.py` | Cosine similarity search | ~250 | High |
| `faq_keyword_search.py` | PostgreSQL FTS | ~200 | Medium |
| `faq_search.py` | Hybrid search (vector + keyword) | ~280 | High |
| `faq_context_assembler.py` | Context building for LLM | ~180 | Medium |
| `faq_response_generator.py` | LLM response generation | ~220 | Medium |
| `faq_embeddings.py` | OpenAI embedding generation | ~150 | Low |
| `faq_chunking.py` | Text chunking (800 tokens) | ~120 | Low |
| `faq_cache.py` | Redis caching layer | ~130 | Low |
| `faq_reindex_service.py` | Bulk reindexing | ~170 | Medium |

**Total Backend LOC:** ~2000 lines

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FAQ RAG ARCHITECTURE                      │
└─────────────────────────────────────────────────────────────┘

User Query: "What is the cancellation policy?"
    ↓
┌──────────────────────────────────────────────────────────────┐
│ 1. Query Processing (faq_rag_pipeline.py)                   │
│    ├─ Validate query                                         │
│    ├─ Check Redis cache (15-min TTL)                        │
│    └─ If miss → proceed to search                           │
└──────────────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────────────┐
│ 2. Hybrid Search (faq_search.py)                            │
│                                                               │
│    ┌──────────────────┐        ┌──────────────────┐         │
│    │ Vector Search    │        │ Keyword Search   │         │
│    │                  │        │                  │         │
│    │ OpenAI Embedding │        │ PostgreSQL FTS   │         │
│    │ Cosine Similarity│        │ ts_rank()        │         │
│    │ Threshold: 0.7   │        │ tsvector         │         │
│    └──────────────────┘        └──────────────────┘         │
│            ↓                            ↓                     │
│    ┌───────────────────────────────────────────┐            │
│    │ Hybrid Ranking (weighted)                 │            │
│    │   vector_score * 0.7 + keyword_score * 0.3│            │
│    │   Top 3 results                            │            │
│    └───────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────────────┐
│ 3. Context Assembly (faq_context_assembler.py)              │
│    ├─ Build context from top 3 FAQs                         │
│    ├─ Include question + answer + category                  │
│    └─ Format for LLM prompt                                 │
└──────────────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────────────┐
│ 4. Response Generation (faq_response_generator.py)          │
│    ├─ Call OpenAI GPT-4                                     │
│    ├─ System prompt: "Answer based on provided FAQs..."    │
│    ├─ User prompt: Original query + context                │
│    └─ Generate natural language response                    │
└──────────────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────────────┐
│ 5. Caching & Response (faq_cache.py)                        │
│    ├─ Cache result in Redis (15-min)                        │
│    ├─ Log analytics (query, similarity, helpful?)          │
│    └─ Return response to user                               │
└──────────────────────────────────────────────────────────────┘
```

### Database Schema

**Models:**

```python
# faq_categories - Hierarchical categories
class FAQCategory(Base):
    id: UUID
    name: str
    slug: str (unique)
    parent_id: UUID (nullable, self-referencing)
    level: int  # 0=main, 1=sub
    is_active: bool

# faq_documents - FAQ content
class FAQDocument(Base):
    id: UUID
    question: str (max 200 chars)
    answer: text (unlimited)
    category_id: UUID
    sub_category_id: UUID (nullable)
    status: str  # draft | published | archived
    tags: list[str]  # PostgreSQL array
    
    # Analytics
    view_count: int
    helpful_count: int
    not_helpful_count: int
    
    # JSONB metadata
    faq_metadata: dict

# faq_embeddings - Vector embeddings
class FAQEmbedding(Base):
    id: UUID
    document_id: UUID
    chunk_text: text
    embedding: list[float]  # 1536-dim vector (JSON or pgvector)
    chunk_index: int
    chunk_metadata: dict

# faq_analytics - Query tracking
class FAQAnalytic(Base):
    id: UUID
    document_id: UUID
    query_text: text
    similarity_score: float
    user_session_id: str
    response_helpful: bool (nullable)
```

**Indexes:**
```sql
-- Vector search (pgvector)
CREATE INDEX idx_faq_embeddings_vector ON faq_embeddings USING ivfflat (embedding);

-- Keyword search (PostgreSQL FTS)
CREATE INDEX idx_faq_documents_fts ON faq_documents USING GIN (to_tsvector('english', question || ' ' || answer));

-- Tags (GIN for array containment)
CREATE INDEX idx_faq_documents_tags ON faq_documents USING GIN (tags);
```

### Configuration

**Environment Variables:**
```python
OPENAI_API_KEY: str = "sk-..."
OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"
OPENAI_EMBEDDING_DIMENSIONS: int = 1536

FAQ_CHUNK_SIZE: int = 800  # tokens
FAQ_CHUNK_OVERLAP: int = 200  # tokens

REDIS_URL: str = "redis://localhost:6379"
REDIS_FAQ_QUERY_TTL: int = 900  # 15 minutes
```

### Frontend Implementation

**Admin UI for FAQ Management:**

**Location:** `/apps/frontend/src/lib/components/admin/`

**Components:**
- `FAQForm.svelte` - Create/edit FAQ
- `FAQToolConfigModal.svelte` - Configure FAQ RAG tool

**User-facing:** FAQ search integrated into chat (via `faq_tool.py`)

### External Dependencies

**Backend:**
- `openai>=1.54.0` - Embeddings + response generation
- `pgvector>=0.3.6` - Vector similarity search (PostgreSQL extension)
- `redis[hiredis]>=5.2.0` - Query caching
- `tiktoken>=0.8.0` - Token counting for chunking

**PostgreSQL Extensions:**
```sql
CREATE EXTENSION IF NOT EXISTS pgvector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For fuzzy text search
```

### Reusability for Multi-Product

#### ✅ Highly Reusable (Extract to @bestays/faq)

**Backend Services:**
- All RAG pipeline services are product-agnostic
- Configuration-driven (system prompts, chunk size, weights)
- No hardcoded business logic

**Database Schema:**
- Generic schema works for any FAQ content
- Product-specific via `faq_metadata` JSONB column

**Search Algorithm:**
- Hybrid search (vector + keyword) is domain-independent
- Weights configurable per product

#### ❌ Product-Specific Content

**FAQ Data:**
```sql
-- Bestays FAQs
INSERT INTO faq_documents (question, answer, category_id) VALUES 
('What is the cancellation policy?', 'Full refund if cancelled 30+ days...', cat_policies);

-- Real Estate FAQs
INSERT INTO faq_documents (question, answer, category_id) VALUES 
('What are the property taxes?', 'Property taxes in Thailand...', cat_legal);
```

**System Prompts:**
```python
# Bestays
FAQ_SYSTEM_PROMPT = "You are a helpful assistant for vacation rental FAQs..."

# Real Estate
FAQ_SYSTEM_PROMPT = "You are a real estate expert answering property investment questions..."
```

**Categories:**
```
Bestays: Policies, Booking, Payment, Check-in/out, Amenities
Real Estate: Legal, Financing, Taxes, Investment, Market Trends
```

### Migration Strategy to @bestays/faq Package

**Phase 1: Extract Services**
```
packages/faq/
├── backend/
│   ├── services/
│   │   ├── faq_rag_pipeline.py
│   │   ├── faq_vector_search.py
│   │   ├── faq_keyword_search.py
│   │   ├── faq_search.py
│   │   ├── faq_context_assembler.py
│   │   ├── faq_response_generator.py
│   │   ├── faq_embeddings.py
│   │   ├── faq_chunking.py
│   │   └── faq_cache.py
│   ├── models/
│   │   └── faq.py (all FAQ models)
│   └── api/
│       └── faq_router.py
└── frontend/
    └── components/
        ├── FAQSearch.svelte (user-facing)
        └── admin/
            └── FAQForm.svelte
```

**Phase 2: Configuration Layer**
```python
# apps/bestays-api/config/faq.py
FAQ_CONFIG = {
    "system_prompt": "You are a helpful assistant for Bestays vacation rental FAQs...",
    "search_weights": {
        "vector": 0.7,
        "keyword": 0.3
    },
    "chunk_size": 800,
    "chunk_overlap": 200,
    "top_k_results": 3,
    "cache_ttl": 900  # 15 min
}

# apps/realestate-api/config/faq.py
FAQ_CONFIG = {
    "system_prompt": "You are a real estate expert answering property investment questions...",
    "search_weights": {
        "vector": 0.6,  # Less weight on vector for technical queries
        "keyword": 0.4
    },
    # ... same structure, different values
}
```

**Phase 3: Import in Apps**
```python
# apps/bestays-api/main.py
from bestays_faq import FAQRouter, FAQRagPipeline

faq_pipeline = FAQRagPipeline(config=FAQ_CONFIG)
app.include_router(FAQRouter(pipeline=faq_pipeline))
```

### Complexity Estimate

**Extraction Effort:** High (4-5 days)
- Many interconnected services
- Redis caching layer
- PostgreSQL extension dependency (pgvector)
- OpenAI API integration

**Challenges:**
- pgvector extension must be installed in both product databases
- Redis configuration (separate instances or shared with key prefixes?)
- Migration of existing FAQ data (product-specific content)

**Recommendation:** Extract FAQ after chat (Phase 3 of migration) since it's more complex.

---

## 5. Search Functionality Analysis

### Current Implementation

**Location:** `/apps/server/src/server/services/faq_*_search.py`

**Search Technology:** Hybrid approach

**Components:**

1. **Vector Similarity Search** (`faq_vector_search.py`)
   - **Technology:** pgvector extension (PostgreSQL)
   - **Embeddings:** OpenAI `text-embedding-ada-002` (1536 dimensions)
   - **Algorithm:** Cosine similarity
   - **Threshold:** 0.7 (high confidence)
   - **Performance:** <200ms for typical queries

2. **Keyword Search** (`faq_keyword_search.py`)
   - **Technology:** PostgreSQL full-text search (tsvector + ts_rank)
   - **Language:** English
   - **Index:** GIN index on `to_tsvector('english', question || ' ' || answer)`

3. **Hybrid Search** (`faq_search.py`)
   - **Combines:** Vector search (70%) + Keyword search (30%)
   - **Algorithm:** Weighted ranking
   - **Normalization:** All scores normalized to 0-1 range
   - **Top K:** Configurable (default 3)

### Search Types

**FAQ Search:**
- Hybrid vector + keyword search
- Used in chat tool integration
- Cached in Redis (15-min TTL)

**Property Search:**
- **Not yet implemented** (mentioned in Property V2 schema)
- Future: Filters (price, location, amenities), sorting, pagination

### External Services

**None used currently:**
- ❌ Algolia
- ❌ Elasticsearch
- ❌ Meilisearch
- ❌ Typesense

**Rationale:** PostgreSQL with pgvector is sufficient for current scale

### Reusability for Multi-Product

#### ✅ Highly Reusable (Extract to @bestays/search)

**FAQ Search Services:**
- All search algorithms are product-agnostic
- Configuration-driven weights and thresholds
- Generic schema

**Future Property Search:**
- Search infrastructure can be shared
- Filters/facets are configurable

#### ❌ Product-Specific Data

**Search Indexes:**
```sql
-- Separate indexes per product database
-- bestays_db
CREATE INDEX idx_faq_fts_bestays ON faq_documents USING GIN (...);

-- realestate_db
CREATE INDEX idx_faq_fts_realestate ON faq_documents USING GIN (...);
```

**Search Configuration:**
```python
# Bestays: FAQ-heavy
SEARCH_CONFIG = {
    "faq_weight": 0.7,
    "property_weight": 0.3
}

# Real Estate: Property-heavy
SEARCH_CONFIG = {
    "faq_weight": 0.3,
    "property_weight": 0.7
}
```

### Migration Strategy to @bestays/search Package

**Phase 1: Extract Search Services**
```
packages/search/
└── backend/
    ├── services/
    │   ├── vector_search.py (generic)
    │   ├── keyword_search.py (generic)
    │   └── hybrid_search.py (generic)
    └── schemas/
        └── search.py (SearchResult, SearchQuery, SearchResponse)
```

**Phase 2: Product-Specific Configuration**
```python
# apps/bestays-api/config/search.py
SEARCH_CONFIG = {
    "vector_weight": 0.7,
    "keyword_weight": 0.3,
    "top_k": 3,
    "threshold": 0.7
}
```

**Phase 3: Import in Apps**
```python
# apps/bestays-api/routers/search.py
from bestays_search import HybridSearchService

search_service = HybridSearchService(config=SEARCH_CONFIG, db=db)
results = await search_service.search(query="cancellation policy")
```

### Complexity Estimate

**Extraction Effort:** Low (1-2 days)
- Services are well-isolated
- Minimal dependencies (just PostgreSQL + OpenAI)
- Clear API boundaries

**Recommendation:** Extract search as part of FAQ extraction (since they're tightly coupled).

---

## 6. Current Project Structure

### Root Structure

```
/Users/solo/Projects/_repos/bestays/
├── .claude/                    # Claude Code workflow files
│   ├── commands/              # Custom slash commands
│   ├── skills/                # Specialized agent skills
│   ├── reports/               # Review reports
│   └── tasks/                 # Task tracking
├── .sdlc-workflow/            # SDLC workflow (stories, specs, plans)
│   ├── stories/               # User stories (auth, properties, infrastructure)
│   ├── .specs/                # Architecture specs
│   └── .index/                # SDLC index
├── apps/                      # Application code
│   ├── frontend/              # SvelteKit frontend
│   └── server/                # FastAPI backend
├── docker/                    # Docker configs
│   ├── server/                # Backend Dockerfile
│   ├── frontend/              # Frontend Dockerfile
│   └── postgres/              # PostgreSQL init scripts
├── scripts/                   # Utility scripts
├── tests/                     # End-to-end tests
├── docker-compose.dev.yml     # Development environment
├── docker-compose.prod.yml    # Production environment
├── Makefile                   # Development commands
└── .env.example               # Environment template
```

### Frontend Structure

```
apps/frontend/
├── src/
│   ├── lib/
│   │   ├── api/               # API clients (users, chat, FAQs, categories)
│   │   ├── assets/            # Static assets
│   │   ├── clerk.ts           # Clerk SDK singleton
│   │   ├── components/        # Svelte components
│   │   │   ├── admin/         # Admin UI (FAQ, Chat config)
│   │   │   ├── chat/          # Chat components (9 files, ~1200 LOC)
│   │   │   ├── dashboard/     # Dashboard layout
│   │   │   ├── ui/            # Reusable UI (button, card, input, etc.)
│   │   │   ├── AuthNav.svelte
│   │   │   ├── ErrorBoundary.svelte
│   │   │   └── UserButton.svelte
│   │   ├── config/            # Navigation config
│   │   ├── guards/            # Auth guards
│   │   ├── services/          # API services (chatApi, actionHandler)
│   │   ├── stores/            # Svelte stores (auth, chat)
│   │   ├── types/             # TypeScript types
│   │   └── utils/             # Utilities (redirect logic)
│   ├── routes/                # SvelteKit routes
│   │   ├── +layout.svelte     # Global layout (Clerk init)
│   │   ├── +page.svelte       # Home page
│   │   ├── login/             # Login page
│   │   ├── signup/            # Signup page
│   │   ├── dashboard/         # Dashboard pages
│   │   │   ├── ai-agent/      # AI agent config
│   │   │   └── faqs/          # FAQ management
│   │   ├── me/                # User profile
│   │   └── unauthorized/      # Unauthorized page
│   └── stories/               # Storybook stories
├── tests/                     # Vitest + Playwright tests
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   ├── e2e/                   # E2E tests (Playwright)
│   └── contracts/             # Contract tests
├── package.json               # Dependencies (Svelte 5, SvelteKit, Clerk, TailwindCSS)
├── vite.config.ts             # Vite configuration
└── playwright.config.ts       # Playwright E2E config
```

**Dependencies (Frontend):**
```json
{
  "dependencies": {
    "@clerk/clerk-js": "^5.102.1",
    "@tanstack/svelte-query": "^5.90.2",
    "@ai-sdk/openai": "^0.0.68",
    "ai": "^3.4.33",
    "svelte": "^5.39.5",
    "bits-ui": "^2.14.2",
    "lucide-svelte": "^0.548.0"
  },
  "devDependencies": {
    "@sveltejs/kit": "^2.43.2",
    "@playwright/test": "^1.56.1",
    "vitest": "^4.0.3",
    "tailwindcss": "^4.1.16",
    "typescript": "^5.9.2",
    "storybook": "^10.0.5"
  }
}
```

### Backend Structure

```
apps/server/
├── src/server/
│   ├── api/
│   │   ├── auth/              # Auth decorators, permissions
│   │   ├── context/           # Request context (audit)
│   │   ├── middleware/        # Audit middleware
│   │   ├── services/          # Audit service, role service
│   │   ├── clerk_deps.py      # Clerk authentication dependencies
│   │   ├── deps.py            # Generic dependencies (get_db)
│   │   └── v1/                # API v1 routes
│   │       ├── endpoints/
│   │       │   ├── admin/     # Admin endpoints (chat config, FAQs)
│   │       │   ├── llm/       # LLM endpoints (chat)
│   │       │   ├── health.py  # Health check
│   │       │   ├── users.py   # User endpoints
│   │       │   └── webhooks.py # Clerk webhooks
│   │       └── router.py      # Main API router
│   ├── core/
│   │   ├── clerk.py           # Clerk client singleton
│   │   ├── database.py        # SQLAlchemy async setup
│   │   └── security.py        # Security utilities
│   ├── llm_config/            # LLM configuration
│   ├── models/                # SQLAlchemy models
│   │   ├── audit.py           # Audit log
│   │   ├── base.py            # Base model
│   │   ├── chat_config.py     # Chat configuration
│   │   ├── chat.py            # Conversations, messages
│   │   ├── faq.py             # FAQ documents, embeddings, categories
│   │   ├── property.py        # Property model (basic)
│   │   ├── user.py            # User model
│   │   └── webhook_event.py   # Webhook tracking
│   ├── schemas/               # Pydantic schemas
│   │   ├── auth.py            # Auth schemas
│   │   ├── chat_config.py     # Chat config schemas
│   │   ├── faq_admin.py       # FAQ admin schemas
│   │   ├── llm.py             # LLM schemas
│   │   ├── search.py          # Search schemas
│   │   ├── setup.py           # Setup schemas
│   │   └── user.py            # User schemas
│   ├── services/              # Business logic
│   │   ├── chat_config_service.py
│   │   ├── chat_service.py
│   │   ├── chat_tools/        # Chat tool implementations
│   │   │   └── faq_tool.py
│   │   ├── conversation_service.py
│   │   ├── faq_cache.py
│   │   ├── faq_chunking.py
│   │   ├── faq_context_assembler.py
│   │   ├── faq_embeddings.py
│   │   ├── faq_keyword_search.py
│   │   ├── faq_rag_pipeline.py
│   │   ├── faq_reindex_service.py
│   │   ├── faq_response_generator.py
│   │   ├── faq_search.py
│   │   ├── faq_vector_search.py
│   │   ├── openai_client.py
│   │   └── user_service.py
│   ├── config.py              # Application configuration (Pydantic Settings)
│   ├── exceptions.py          # Custom exceptions
│   └── main.py                # FastAPI application
├── alembic/                   # Database migrations
│   ├── versions/              # Migration files (9 migrations)
│   ├── env.py                 # Alembic environment
│   └── script.py.mako         # Migration template
├── scripts/                   # Utility scripts
│   ├── backfill_embeddings.py # Generate embeddings for existing FAQs
│   ├── seed_chat_config.py    # Seed chat configuration
│   └── seed_faq_data.py       # Seed FAQ data
├── tests/                     # Pytest tests
│   ├── api/                   # API endpoint tests
│   ├── core/                  # Core functionality tests
│   ├── integration/           # Integration tests
│   ├── models/                # Model tests
│   ├── schemas/               # Schema validation tests
│   ├── services/              # Service tests
│   └── test_*.py              # Specific feature tests (FAQ RAG, RBAC, etc.)
├── pyproject.toml             # Python dependencies + tool config
├── pytest.ini                 # Pytest configuration
└── alembic.ini                # Alembic configuration
```

**Dependencies (Backend):**
```toml
[project.dependencies]
fastapi = ">=0.110.0"
uvicorn = ">=0.27.0"
pydantic = ">=2.6.0"
sqlalchemy = ">=2.0.0"
asyncpg = ">=0.29.0"
alembic = ">=1.13.0"
clerk-backend-api = ">=3.3.1"
langchain = ">=0.3.0"
langchain-openai = ">=0.2.0"
langchain-anthropic = ">=0.2.0"
openai = ">=1.54.0"
anthropic = ">=0.39.0"
redis = ">=5.2.0"
pgvector = ">=0.3.6"
sse-starlette = ">=2.2.0"

[project.optional-dependencies.dev]
pytest = ">=8.0.0"
pytest-asyncio = ">=0.23.0"
pytest-cov = ">=4.1.0"
httpx = ">=0.26.0"
fakeredis = ">=2.21.0"
```

### Monorepo Setup

**Current Status:** ❌ **No monorepo tooling**

**What's Missing:**
- No `turbo.json` (Turborepo configuration)
- No `pnpm-workspace.yaml` (pnpm workspaces)
- No `packages/` directory
- No root `package.json`

**Current Structure:** Two independent applications
- Frontend: `/apps/frontend/` with its own `package.json`
- Backend: `/apps/server/` with its own `pyproject.toml`

**Docker Orchestration:** Docker Compose (development + production)
- `docker-compose.dev.yml` - Development environment
- `docker-compose.prod.yml` - Production environment

**Makefiles:** Root `Makefile` with development commands
- `make dev` - Start development environment
- `make up` - Start all services
- `make logs` - View logs
- `make test-server` - Run backend tests

### Recommendations for Multi-Product Architecture

**Option 1: Turborepo + pnpm Workspaces (Recommended)**

```
bestays-monorepo/
├── packages/
│   ├── chat/                  # Shared chat package
│   │   ├── frontend/          # Svelte components
│   │   └── backend/           # Python services
│   ├── faq/                   # Shared FAQ package
│   ├── search/                # Shared search package
│   ├── ui/                    # Shared Svelte UI components
│   └── db-models/             # Shared database models (SQLAlchemy)
├── apps/
│   ├── bestays-web/           # Bestays SvelteKit frontend
│   ├── bestays-api/           # Bestays FastAPI backend
│   ├── realestate-web/        # Real Estate SvelteKit frontend
│   └── realestate-api/        # Real Estate FastAPI backend
├── config/
│   ├── bestays/               # Bestays-specific configs
│   └── realestate/            # Real Estate-specific configs
├── docker/                    # Docker configs per product
├── turbo.json                 # Turborepo configuration
├── pnpm-workspace.yaml        # pnpm workspaces
└── package.json               # Root package.json
```

**Benefits:**
- Shared packages (DRY principle)
- Turborepo caching (faster builds)
- Clear separation of concerns
- Easy to extract packages later for sale

**Challenges:**
- Setup complexity (new tooling)
- Python packages in monorepo (need structure)
- Migration effort from current structure

**Option 2: Duplicate Applications (Simpler, Not Recommended)**

```
bestays/
├── frontend/
├── server/
└── ...

realestate/
├── frontend/  (copy of bestays/frontend)
├── server/    (copy of bestays/server)
└── ...
```

**Benefits:**
- Simple to set up (just copy)
- No monorepo tooling needed

**Challenges:**
- Code duplication (violates DRY)
- Hard to maintain (fix bugs twice)
- Not white-label ready

**Verdict:** **Use Option 1** (Turborepo + pnpm) for maintainability and white-label readiness.

---

## 7. Environment Configuration

### Current Approach

**Backend Configuration:**

**File:** `/apps/server/src/server/config.py`

**Pattern:** Pydantic Settings (type-safe environment variables)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    APP_NAME: str = "Simka"  # Hardcoded (should be configurable)
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5273", ...]
    
    # Database
    DATABASE_URL: PostgresDsn
    
    # Clerk
    CLERK_SECRET_KEY: str
    CLERK_PUBLISHABLE_KEY: str
    CLERK_WEBHOOK_SECRET: str
    FRONTEND_URL: str
    
    # OpenAI
    OPENAI_API_KEY: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"

settings = get_settings()  # Singleton
```

**Frontend Configuration:**

**Pattern:** Vite environment variables (`VITE_*`)

**Files:**
- `.env` (local, gitignored)
- `.env.example` (template)
- Runtime: `import.meta.env.VITE_*`

```typescript
// Access in code
const apiUrl = import.meta.env.VITE_API_URL;
const clerkKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;
```

### Multi-Product Requirements

**Per-Product Configuration:**

**Backend:**
```python
# apps/bestays-api/.env
APP_NAME=Bestays
CLERK_SECRET_KEY=sk_live_bestays_*
DATABASE_URL=postgresql+asyncpg://bestays_user:pass@localhost:5432/bestays_db
FRONTEND_URL=https://bestays.com
OPENAI_API_KEY=sk-*  # Shared or separate?
REDIS_URL=redis://localhost:6379/0  # DB 0

# apps/realestate-api/.env
APP_NAME=Real Estate Pro
CLERK_SECRET_KEY=sk_live_realestate_*
DATABASE_URL=postgresql+asyncpg://realestate_user:pass@localhost:5432/realestate_db
FRONTEND_URL=https://realestate-pro.com
OPENAI_API_KEY=sk-*  # Shared or separate?
REDIS_URL=redis://localhost:6379/1  # DB 1
```

**Frontend:**
```bash
# apps/bestays-web/.env
VITE_APP_NAME=Bestays
VITE_CLERK_PUBLISHABLE_KEY=pk_live_bestays_*
VITE_API_URL=https://api.bestays.com
VITE_THEME_PRIMARY_COLOR=#3B82F6

# apps/realestate-web/.env
VITE_APP_NAME=Real Estate Pro
VITE_CLERK_PUBLISHABLE_KEY=pk_live_realestate_*
VITE_API_URL=https://api.realestate-pro.com
VITE_THEME_PRIMARY_COLOR=#10B981
```

### Configuration Layer Pattern

**Shared Configuration Package:**

```typescript
// packages/config/src/types.ts
export interface ProductConfig {
  app: {
    name: string;
    logo: string;
    tagline: string;
  };
  branding: {
    primaryColor: string;
    secondaryColor: string;
    font: string;
  };
  features: {
    chatEnabled: boolean;
    faqEnabled: boolean;
    searchEnabled: boolean;
  };
  api: {
    baseUrl: string;
    timeout: number;
  };
  clerk: {
    publishableKey: string;
  };
}
```

```typescript
// apps/bestays-web/src/config/index.ts
import type { ProductConfig } from '@bestays/config';

export const config: ProductConfig = {
  app: {
    name: import.meta.env.VITE_APP_NAME || 'Bestays',
    logo: '/logo-bestays.svg',
    tagline: 'Find your perfect vacation rental'
  },
  branding: {
    primaryColor: import.meta.env.VITE_THEME_PRIMARY_COLOR || '#3B82F6',
    secondaryColor: '#1E40AF',
    font: 'Inter'
  },
  features: {
    chatEnabled: true,
    faqEnabled: true,
    searchEnabled: true
  },
  api: {
    baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:8101',
    timeout: 30000
  },
  clerk: {
    publishableKey: import.meta.env.VITE_CLERK_PUBLISHABLE_KEY
  }
};
```

### Recommendations

**1. Centralized Configuration Package**
```
packages/config/
├── src/
│   ├── types.ts          # TypeScript types
│   ├── schemas.py        # Pydantic schemas (Python)
│   └── validation.ts     # Runtime validation (Zod)
└── package.json
```

**2. Per-Product Config Files**
```
apps/bestays-web/src/config/
├── index.ts              # Main config (imports from @bestays/config)
├── branding.ts           # Branding overrides
└── features.ts           # Feature flags

apps/bestays-api/config/
├── settings.py           # Pydantic Settings (imports from config package)
├── chat.py               # Chat-specific config
└── faq.py                # FAQ-specific config
```

**3. Environment Variable Validation**
```typescript
// Validate at build time (Vite plugin)
import { z } from 'zod';

const envSchema = z.object({
  VITE_APP_NAME: z.string().min(1),
  VITE_CLERK_PUBLISHABLE_KEY: z.string().startsWith('pk_'),
  VITE_API_URL: z.string().url(),
});

envSchema.parse(import.meta.env);  // Throws if invalid
```

```python
# Validate at startup (Pydantic)
class Settings(BaseSettings):
    APP_NAME: str = Field(..., min_length=1)
    CLERK_SECRET_KEY: str = Field(..., pattern=r'^sk_(test|live)_')
    DATABASE_URL: PostgresDsn
    
    @field_validator('DATABASE_URL')
    def validate_database_url(cls, v):
        if not v.startswith('postgresql+asyncpg://'):
            raise ValueError('Must use asyncpg driver')
        return v
```

---

## 8. Deployment & Infrastructure

### Current Deployment

**Development Environment:**

**Tool:** Docker Compose

**File:** `/docker-compose.dev.yml`

**Services:**
```yaml
services:
  postgres:
    image: postgres:16-alpine
    ports:
      - "5433:5432"  # Avoid conflict with host PostgreSQL
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: bestays_user
      POSTGRES_PASSWORD: bestays_password
      POSTGRES_DB: bestays_dev
  
  server:
    build:
      dockerfile: docker/server/Dockerfile.dev
    ports:
      - "8101:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://bestays_user:bestays_password@postgres:5432/bestays_dev
      CLERK_SECRET_KEY: ${CLERK_SECRET_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis
  
  frontend:
    build:
      dockerfile: docker/frontend/Dockerfile.dev
    ports:
      - "5183:5173"
    environment:
      VITE_API_URL: http://localhost:8101
      VITE_CLERK_PUBLISHABLE_KEY: ${VITE_CLERK_PUBLISHABLE_KEY}
    depends_on:
      - server
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

**Commands:**
```bash
# Start development environment
make dev

# Stop
make down

# Logs
make logs

# Restart
make restart
```

**Production Deployment:**

**File:** `/docker-compose.prod.yml` (exists, production-ready)

**VPS Hosting:** Not specified in codebase (likely DigitalOcean/Hetzner/AWS)

**SSL/TLS:** Not configured yet (would need Nginx + Let's Encrypt)

### Multi-Product Deployment Strategy

**Option 1: Separate VPS Instances (Complete Isolation)**

```
VPS 1 (Bestays)
├── PostgreSQL (bestays_db)
├── Redis (DB 0)
├── Backend (Docker: bestays-api)
├── Frontend (Docker: bestays-web)
└── Nginx (SSL + reverse proxy)

VPS 2 (Real Estate)
├── PostgreSQL (realestate_db)
├── Redis (DB 1)
├── Backend (Docker: realestate-api)
├── Frontend (Docker: realestate-web)
└── Nginx (SSL + reverse proxy)
```

**Benefits:**
- Complete isolation (no shared resources)
- Independent scaling
- Independent backups
- Separate billing/monitoring

**Challenges:**
- Higher cost (2 VPS instances)
- Duplicate infrastructure management

**Option 2: Same VPS with Different Ports/Configs**

```
Single VPS
├── PostgreSQL
│   ├── bestays_db (port 5432)
│   └── realestate_db (port 5432)
├── Redis (multiple databases)
│   ├── DB 0 (Bestays)
│   └── DB 1 (Real Estate)
├── Docker Containers
│   ├── bestays-api (port 8101)
│   ├── bestays-web (port 5183)
│   ├── realestate-api (port 8102)
│   └── realestate-web (port 5184)
└── Nginx (reverse proxy)
    ├── bestays.com → bestays-web:5183
    ├── api.bestays.com → bestays-api:8101
    ├── realestate.com → realestate-web:5184
    └── api.realestate.com → realestate-api:8102
```

**Benefits:**
- Lower cost (single VPS)
- Shared infrastructure (Redis, PostgreSQL)
- Easier monitoring

**Challenges:**
- Resource contention (CPU, memory)
- More complex configuration
- Harder to scale independently

**Option 3: Kubernetes (Over-Engineering for MVP)**

Not recommended at current scale.

**Verdict:** **Use Option 2** (same VPS with different configs) for MVP, migrate to Option 1 (separate VPS) when scaling.

### Docker Configuration for Multi-Product

**Separate Docker Compose Files:**

```
docker/
├── bestays/
│   ├── docker-compose.yml
│   ├── Dockerfile.api
│   └── Dockerfile.web
└── realestate/
    ├── docker-compose.yml
    ├── Dockerfile.api
    └── Dockerfile.web
```

**Nginx Configuration:**

```nginx
# /etc/nginx/sites-available/bestays.conf
server {
    listen 80;
    server_name bestays.com www.bestays.com;
    
    location / {
        proxy_pass http://localhost:5183;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 80;
    server_name api.bestays.com;
    
    location / {
        proxy_pass http://localhost:8101;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Similar for realestate.com and api.realestate.com
```

**SSL with Let's Encrypt:**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificates
sudo certbot --nginx -d bestays.com -d www.bestays.com -d api.bestays.com
sudo certbot --nginx -d realestate.com -d www.realestate.com -d api.realestate.com
```

### CI/CD Pipeline

**Current Status:** ❌ Not configured

**Recommended:** GitHub Actions

```yaml
# .github/workflows/deploy-bestays.yml
name: Deploy Bestays

on:
  push:
    branches: [main]
    paths:
      - 'apps/bestays-web/**'
      - 'apps/bestays-api/**'
      - 'packages/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker images
        run: |
          docker build -t bestays-api:latest -f docker/bestays/Dockerfile.api .
          docker build -t bestays-web:latest -f docker/bestays/Dockerfile.web .
      
      - name: Deploy to VPS
        uses: appleboy/ssh-action@v0.1.10
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/bestays
            docker-compose pull
            docker-compose up -d --no-deps --build
```

---

## 9. Overall Architecture Assessment

### Strengths (What's Already Good for Multi-Product)

#### ✅ 1. Clean Separation of Concerns
- **Frontend and backend are independent** - Can duplicate easily
- **Docker orchestration** - Each service is containerized
- **API versioning** - `/api/v1/` prefix allows future versions

#### ✅ 2. Modern Async Patterns
- **FastAPI async** - Async/await throughout
- **SQLAlchemy 2.0** - Async sessions with asyncpg
- **Svelte 5** - Modern reactivity with runes
- **Type safety** - TypeScript (frontend) + Pydantic (backend)

#### ✅ 3. Production-Ready Features
- **Comprehensive authentication** - Clerk integration with JWT + RBAC + JIT provisioning
- **Chat system** - 4500+ LOC, LLM integration, metadata-driven UI ready
- **FAQ RAG** - 2000+ LOC, hybrid search, vector embeddings, Redis caching
- **Database migrations** - Alembic with comprehensive schema
- **Testing** - Pytest + Vitest + Playwright

#### ✅ 4. Configuration-Driven Design
- **Pydantic Settings** - Type-safe environment variables
- **Database-driven config** - Chat prompts, tools configurable without code changes
- **Environment-based** - Development vs. production configs

#### ✅ 5. Developer Experience
- **Makefile** - Simple development commands
- **Docker Compose** - One-command environment setup
- **Hot reload** - Frontend and backend both support hot reload
- **Comprehensive documentation** - README files, user stories, specs

### Challenges (What Needs Significant Refactoring)

#### ❌ 1. No Monorepo Tooling
- **Missing:** Turborepo, pnpm workspaces, package structure
- **Impact:** Can't share code easily between products
- **Effort:** High (setup monorepo from scratch)

#### ❌ 2. Tightly Coupled Features
- **Chat integration** - Hardcoded in main app, not a package
- **FAQ system** - Tightly coupled to database schema
- **User management** - Clerk integration spread across multiple files

#### ❌ 3. Product-Specific Hardcoding
- **APP_NAME** - Hardcoded as "Simka" in `config.py`
- **Branding** - CSS colors hardcoded in Tailwind config
- **System prompts** - Some defaults hardcoded (should be DB-driven)

#### ❌ 4. Single Database Assumption
- **Database URL** - Single `DATABASE_URL` environment variable
- **Migrations** - Alembic assumes single database
- **Foreign keys** - No concept of multi-tenancy or product isolation

#### ❌ 5. Environment Variables Not Product-Scoped
- **Clerk keys** - Single set of keys (CLERK_SECRET_KEY, CLERK_PUBLISHABLE_KEY)
- **Redis** - Single REDIS_URL (no database prefix)
- **FRONTEND_URL** - Single URL for authorized parties

### Quick Wins (Easy Extractions)

#### 🚀 1. Search Services (1-2 days)
- **Why:** Well-isolated, minimal dependencies
- **Extract:** `faq_vector_search.py`, `faq_keyword_search.py`, `faq_search.py`
- **Package:** `@bestays/search`

#### 🚀 2. UI Components (2-3 days)
- **Why:** Svelte components are already modular
- **Extract:** `components/ui/` (button, card, input, etc.)
- **Package:** `@bestays/ui`

#### 🚀 3. Database Models (1 day)
- **Why:** SQLAlchemy models are independent
- **Extract:** All models to shared package
- **Package:** `@bestays/db-models`

#### 🚀 4. Configuration Types (1 day)
- **Why:** Type definitions are product-agnostic
- **Extract:** TypeScript interfaces, Pydantic schemas
- **Package:** `@bestays/config`

### Complex Migrations (Require Careful Planning)

#### 🛑 1. Chat Feature Extraction (4-5 days)
- **Why:** Many interconnected services, LLM integration, Redis caching
- **Challenges:**
  - State management (Svelte stores)
  - API client configuration
  - LLM prompt templating
  - Cost tracking per product

#### 🛑 2. FAQ RAG System (4-5 days)
- **Why:** Complex RAG pipeline, pgvector dependency, OpenAI integration
- **Challenges:**
  - pgvector extension in multiple databases
  - Redis key prefixing
  - Embedding generation cost allocation
  - Search algorithm configuration per product

#### 🛑 3. Clerk Integration Duplication (3-4 days)
- **Why:** Spread across multiple layers (frontend, backend, dependencies)
- **Challenges:**
  - Separate Clerk projects setup
  - JWT validation per product
  - Webhook endpoints per product
  - User database isolation

#### 🛑 4. Database Isolation (2-3 days)
- **Why:** Need separate databases per product
- **Challenges:**
  - Alembic migrations per database
  - Connection pooling configuration
  - Foreign key constraints across products (none needed, but validate)

---

## 10. Recommendations for Next Steps

Based on the research findings, here's a **prioritized action plan** for the next agents:

### TASK-002: Database Isolation Strategy (dev-database agent)

**Inputs:**
- Current models: `user.py`, `property.py`, `chat.py`, `faq.py`, `chat_config.py`
- Alembic migrations: 9 existing migrations
- Environment: PostgreSQL + asyncpg

**Questions to Answer:**
1. **Database Architecture:**
   - ✅ Separate databases (`bestays_db`, `realestate_db`) OR
   - ❌ Multi-tenant with `tenant_id` column?
   - **Recommendation:** Separate databases for US-018 compliance

2. **Connection Management:**
   - How to configure multiple database connections in FastAPI?
   - Connection pooling strategy (separate pools or shared?)

3. **Migration Strategy:**
   - Run Alembic migrations twice (once per database)?
   - Share migration files or duplicate?
   - How to handle schema drift between products?

4. **Shared Data:**
   - Any data shared between products? (None expected per US-018)
   - How to prevent accidental cross-product queries?

**Deliverables:**
1. Database architecture document
2. SQLAlchemy configuration pattern for multi-database
3. Alembic migration strategy
4. Connection pooling recommendations

---

### TASK-003: Backend Architecture Design (dev-backend-fastapi agent)

**Inputs:**
- Database recommendations from TASK-002
- Current backend structure (FastAPI, LangChain, SQLAlchemy)
- Existing services: Chat (~1500 LOC), FAQ RAG (~2000 LOC), User management

**Questions to Answer:**
1. **Shared Python Packages:**
   - Which services to extract first? (Chat, FAQ, Search, Auth?)
   - Package structure for Python in monorepo?
   - Import paths (`from @bestays/chat import ...` vs. `from bestays_chat import ...`)?

2. **Configuration Strategy:**
   - Environment-based config per product (Pydantic Settings)
   - Database-driven config (chat prompts, tools)
   - How to override shared package config in apps?

3. **API Routing:**
   - Same API structure for both products?
   - Product-specific endpoints (e.g., `/api/v1/bestays/*` vs. `/api/v1/realestate/*`)?
   - Versioning strategy?

4. **Deployment:**
   - Docker containers per product?
   - Shared base images or separate?
   - Environment variable management?

**Deliverables:**
1. Backend architecture plan
2. Shared packages structure
3. Configuration pattern examples
4. API routing strategy
5. Deployment architecture diagram

---

### TASK-004: Frontend Architecture Design (dev-frontend-svelte agent)

**Inputs:**
- Backend architecture from TASK-003
- Current frontend structure (SvelteKit, Svelte 5, TailwindCSS)
- Existing components: Chat (9 files), UI components (button, card, etc.)

**Questions to Answer:**
1. **Shared Svelte Components:**
   - Which components to extract first? (Chat, UI, FAQ search?)
   - Package structure for Svelte in monorepo?
   - CSS scoping strategy (Tailwind config per product)?

2. **Theming System:**
   - CSS variables for branding (primary color, font, logo)?
   - Tailwind config overrides per product?
   - Dark mode support per product?

3. **Clerk Integration:**
   - Separate Clerk projects setup
   - Environment variable configuration (`VITE_CLERK_PUBLISHABLE_KEY` per product)
   - Auth store reusability (shared logic, product-specific config)

4. **Build Configuration:**
   - Separate builds per product (different entry points)?
   - Shared Vite config or duplicated?
   - Static asset management (logos, images per product)?

**Deliverables:**
1. Frontend architecture plan
2. Shared components structure
3. Theming system design
4. Clerk integration strategy
5. Build configuration examples

---

### TASK-005: Comprehensive Architecture Plan (Synthesis)

**Inputs:**
- Database architecture (TASK-002)
- Backend architecture (TASK-003)
- Frontend architecture (TASK-004)

**Deliverables:**
1. **Unified Architecture Document:**
   - Monorepo structure (Turborepo + pnpm)
   - Shared packages list with priorities
   - Per-product app structure
   - Configuration management strategy
   - Deployment architecture

2. **Migration Roadmap:**
   - Phase 1: Monorepo setup (1 week)
   - Phase 2: Extract Chat package (1 week)
   - Phase 3: Extract FAQ package (1 week)
   - Phase 4: Duplicate apps (Bestays, Real Estate) (1 week)
   - Phase 5: Clerk integration per product (1 week)
   - Phase 6: Testing & validation (1 week)

3. **First Implementation Tasks:**
   - TASK-006: Setup Turborepo + pnpm workspaces
   - TASK-007: Extract UI components package
   - TASK-008: Extract database models package
   - TASK-009: Extract Chat package
   - TASK-010: Extract FAQ package
   - TASK-011: Create Bestays app (configuration)
   - TASK-012: Create Real Estate app (configuration)
   - TASK-013: Setup separate Clerk projects
   - TASK-014: Setup separate databases
   - TASK-015: End-to-end testing

4. **Risk Mitigation Plan:**
   - Data isolation validation
   - Clerk project separation testing
   - Performance benchmarking
   - Rollback procedures

---

## Appendix: Key File Locations

### Authentication Files
- **Frontend Clerk SDK:** `/apps/frontend/src/lib/clerk.ts`
- **Frontend Auth Store:** `/apps/frontend/src/lib/stores/auth.svelte.ts`
- **Backend Clerk Client:** `/apps/server/src/server/core/clerk.py`
- **Backend Auth Dependencies:** `/apps/server/src/server/api/clerk_deps.py`
- **User Model:** `/apps/server/src/server/models/user.py`

### Chat Files
- **Frontend Components:** `/apps/frontend/src/lib/components/chat/` (9 files)
- **Frontend Store:** `/apps/frontend/src/lib/stores/chat.ts`
- **Backend Services:** `/apps/server/src/server/services/chat_*.py` (4 files)
- **Backend Models:** `/apps/server/src/server/models/chat.py`

### FAQ Files
- **Backend RAG Services:** `/apps/server/src/server/services/faq_*.py` (12 files)
- **Backend Models:** `/apps/server/src/server/models/faq.py`
- **Frontend Admin UI:** `/apps/frontend/src/lib/components/admin/FAQForm.svelte`

### Configuration Files
- **Backend Config:** `/apps/server/src/server/config.py`
- **Environment Template:** `/.env.example`
- **Docker Compose:** `/docker-compose.dev.yml`, `/docker-compose.prod.yml`

### Database Files
- **Database Setup:** `/apps/server/src/server/core/database.py`
- **Migrations:** `/apps/server/alembic/versions/` (9 migrations)
- **Models:** `/apps/server/src/server/models/` (8 model files)

---

**End of Research Findings**

**Next Steps:** Pass findings to TASK-002 (dev-database), TASK-003 (dev-backend-fastapi), TASK-004 (dev-frontend-svelte) agents for architecture design.

**Estimated Time to MVP:** 6-8 weeks with sequential implementation of tasks.

**Confidence Level:** High - The existing codebase is well-structured and ready for transformation with the monorepo approach.

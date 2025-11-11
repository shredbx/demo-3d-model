# TASK-003: Backend Architecture Design

**Date:** 2025-11-07
**Agent:** dev-backend
**User Story:** US-018 (White-Label Multi-Product Architecture)
**Status:** COMPLETE
**Priority:** P0 (URGENT AND MANDATORY)

---

## Executive Summary

**Recommended Approach:** **Python Namespace Packages with Shared Services**

**Key Rationale:**
1. **Simplicity First** - Python's native namespace packages (`packages/shared-*`) with `pip install -e`
2. **No Complex Tooling** - Avoid Turborepo/Lerna for Python (use Python ecosystem norms)
3. **Modular Architecture** - Clear package boundaries with explicit dependencies
4. **Clear Documentation** - Environment-based configuration, standard Python patterns

**Alignment with User Priorities:**
- ✅ **Simplicity for deployment** - Docker Compose orchestration (existing pattern)
- ✅ **Simplicity for development** - `pip install -e packages/shared-*` (standard Python workflow)
- ✅ **Modular architecture** - Shared packages + product apps with clean boundaries
- ✅ **Clear documentation** - Environment variables, Pydantic settings, explicit imports

**Risk Assessment:** LOW - This approach uses standard Python packaging, proven FastAPI patterns, and existing Docker Compose orchestration.

---

## Monorepo Package Structure

### Directory Layout

```
bestays-monorepo/
├── packages/                          # Shared Python packages
│   ├── shared-db/                     # SQLAlchemy models + database utilities
│   │   ├── src/
│   │   │   ├── models/               # User, Property, Chat, FAQ models
│   │   │   ├── database.py           # Async engine, session factory
│   │   │   └── seeds/                # Seed data utilities
│   │   ├── tests/                    # Unit tests (SQLite in-memory)
│   │   └── pyproject.toml
│   │
│   ├── shared-config/                 # Pydantic Settings base classes
│   │   ├── src/
│   │   │   ├── base.py               # BaseSettings
│   │   │   └── database.py           # DatabaseSettings
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   ├── shared-core/                   # Core utilities
│   │   ├── src/
│   │   │   ├── exceptions.py         # APIException classes
│   │   │   ├── logging.py            # Structured logging setup
│   │   │   ├── auth.py               # RBAC decorators
│   │   │   └── cache.py              # Redis cache utilities
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   ├── shared-chat/                   # Chat feature (extracted)
│   │   ├── src/
│   │   │   ├── services/
│   │   │   │   ├── chat_service.py
│   │   │   │   ├── conversation_service.py
│   │   │   │   └── chat_config_service.py
│   │   │   ├── schemas/
│   │   │   │   └── chat.py           # Pydantic schemas
│   │   │   └── router.py             # FastAPI router
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   ├── shared-faq/                    # FAQ RAG system (extracted)
│   │   ├── src/
│   │   │   ├── services/
│   │   │   │   ├── faq_rag_pipeline.py
│   │   │   │   ├── faq_vector_search.py
│   │   │   │   ├── faq_keyword_search.py
│   │   │   │   └── faq_search.py
│   │   │   ├── schemas/
│   │   │   │   └── faq.py
│   │   │   └── router.py
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   └── shared-search/                 # Search utilities
│       ├── src/
│       │   ├── vector_search.py
│       │   ├── keyword_search.py
│       │   └── hybrid_search.py
│       ├── tests/
│       └── pyproject.toml
│
├── apps/                              # Product applications
│   ├── bestays-api/                   # Bestays FastAPI app
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   ├── deps.py           # Product-specific dependencies
│   │   │   │   └── v1/
│   │   │   │       ├── endpoints/
│   │   │   │       │   ├── users.py
│   │   │   │       │   ├── properties.py
│   │   │   │       │   └── health.py
│   │   │   │       └── router.py
│   │   │   ├── config/
│   │   │   │   ├── __init__.py      # BestaysSettings
│   │   │   │   ├── chat.py          # Chat-specific config
│   │   │   │   └── faq.py           # FAQ-specific config
│   │   │   └── main.py              # FastAPI app initialization
│   │   ├── alembic/
│   │   │   ├── versions/            # Bestays migrations
│   │   │   └── env.py
│   │   ├── alembic.ini
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   ├── integration/
│   │   │   └── conftest.py
│   │   ├── pyproject.toml           # Dependencies include shared-*
│   │   └── .env.development
│   │
│   └── realestate-api/               # Real Estate FastAPI app
│       ├── app/
│       │   ├── api/
│       │   │   ├── deps.py
│       │   │   └── v1/
│       │   ├── config/
│       │   │   ├── __init__.py      # RealEstateSettings
│       │   │   ├── chat.py
│       │   │   └── faq.py
│       │   └── main.py
│       ├── alembic/
│       ├── alembic.ini
│       ├── tests/
│       ├── pyproject.toml
│       └── .env.development
│
├── docker/
│   ├── bestays-api/
│   │   ├── Dockerfile.dev
│   │   └── Dockerfile.prod
│   ├── realestate-api/
│   │   ├── Dockerfile.dev
│   │   └── Dockerfile.prod
│   └── postgres/
│       └── init-multi-db.sql        # Create both databases
│
├── scripts/
│   └── sync-migrations.sh           # Sync migrations from Bestays to Real Estate
│
├── docker-compose.dev.yml           # Development environment
├── docker-compose.prod.yml          # Production environment
└── README.md
```

### Package Dependency Graph

```
apps/bestays-api
    ↓
shared-chat ──→ shared-db ──→ shared-config
    ↓               ↓
shared-faq ─────→ shared-core
    ↓
shared-search
```

**Dependency Rules:**
1. **Shared packages can depend on other shared packages**
2. **Product apps can depend on any shared package**
3. **Shared packages CANNOT depend on product apps** (one-way dependency)
4. **No circular dependencies** (enforced by Python import system)

### Import Patterns

```python
# In product apps (apps/bestays-api/app/api/v1/endpoints/users.py)
from shared_db.models import User
from shared_db.database import get_db
from shared_core.exceptions import APIException
from shared_chat.services import ChatService
from shared_faq.services import FAQRagPipeline

# In shared packages (packages/shared-chat/src/services/chat_service.py)
from shared_db.models import Conversation, Message
from shared_core.logging import logger
from shared_core.cache import RedisCache
```

**Import Style:**
- ✅ `from shared_db.models import User` (clear, explicit)
- ❌ `from bestays.db.models import User` (package aliasing not needed)
- ✅ Standard Python namespace packages

### Versioning Strategy

**Development Phase:**
```toml
# packages/shared-db/pyproject.toml
[project]
name = "shared-db"
version = "0.1.0"  # Pre-release versioning
```

**After MVP (If Selling Packages):**
```toml
[project]
name = "shared-chat"
version = "1.0.0"  # Semantic versioning
```

**Benefits:**
- During development: Keep all packages at 0.x.y (no API stability guarantees)
- After MVP: Use semantic versioning for released packages
- Products can pin to specific versions if needed

---

## Configuration Management

### Base Settings Classes

**Shared Configuration Package** (`packages/shared-config/`):

```python
# packages/shared-config/src/base.py
"""Base configuration for all products."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class BaseProductSettings(BaseSettings):
    """Base settings shared across all products."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str
    PRODUCT_ID: str
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Frontend (for CORS)
    FRONTEND_URL: str
```

```python
# packages/shared-config/src/database.py
"""Database configuration shared across products."""

from pydantic import PostgresDsn, field_validator
from shared_config.base import BaseProductSettings


class DatabaseSettings(BaseProductSettings):
    """Database configuration pattern."""

    # Database Connection
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_PRE_PING: bool = True
    DATABASE_ECHO: bool = False

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: str | PostgresDsn) -> str:
        """Ensure DATABASE_URL uses asyncpg driver."""
        if isinstance(v, str):
            if v.startswith("postgresql://"):
                v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif not v.startswith("postgresql+asyncpg://"):
                msg = "DATABASE_URL must use postgresql+asyncpg:// scheme"
                raise ValueError(msg)
        return str(v)
```

### Product-Specific Configuration

**Bestays Configuration** (`apps/bestays-api/app/config/__init__.py`):

```python
"""Bestays API configuration."""

from shared_config.database import DatabaseSettings


class BestaysSettings(DatabaseSettings):
    """Bestays-specific settings."""

    # Product Identification
    APP_NAME: str = "Bestays"
    PRODUCT_ID: str = "bestays"

    # Clerk Authentication (Bestays Clerk Project)
    CLERK_SECRET_KEY: str
    CLERK_PUBLISHABLE_KEY: str
    CLERK_WEBHOOK_SECRET: str

    # Redis (with product prefix)
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_KEY_PREFIX: str = "bestays:"

    # OpenAI (shared or product-specific)
    OPENAI_API_KEY: str

    # Feature Flags
    CHAT_ENABLED: bool = True
    FAQ_ENABLED: bool = True
    SEARCH_ENABLED: bool = True


# Singleton instance
settings = BestaysSettings()
```

**Real Estate Configuration** (`apps/realestate-api/app/config/__init__.py`):

```python
"""Real Estate API configuration."""

from shared_config.database import DatabaseSettings


class RealEstateSettings(DatabaseSettings):
    """Real Estate-specific settings."""

    # Product Identification
    APP_NAME: str = "Best Real Estate"
    PRODUCT_ID: str = "realestate"

    # Clerk Authentication (Real Estate Clerk Project)
    CLERK_SECRET_KEY: str
    CLERK_PUBLISHABLE_KEY: str
    CLERK_WEBHOOK_SECRET: str

    # Redis (with product prefix)
    REDIS_URL: str = "redis://localhost:6379/1"
    REDIS_KEY_PREFIX: str = "realestate:"

    # OpenAI (shared or product-specific)
    OPENAI_API_KEY: str

    # Feature Flags
    CHAT_ENABLED: bool = True
    FAQ_ENABLED: bool = True
    SEARCH_ENABLED: bool = True


# Singleton instance
settings = RealEstateSettings()
```

### Feature-Specific Configuration

**Chat Configuration** (`apps/bestays-api/app/config/chat.py`):

```python
"""Chat feature configuration for Bestays."""

CHAT_CONFIG = {
    "system_prompt": "You are a helpful assistant for Bestays, a vacation rental platform. "
                     "Help users find properties, answer questions about bookings, and "
                     "provide information about amenities and locations.",

    "models": {
        "chat": "anthropic/claude-3-sonnet",      # Main chat model
        "search": "anthropic/claude-3-haiku",     # Search/tool calling
        "fallback": "openai/gpt-4o-mini",         # Fallback if primary fails
    },

    "tools_enabled": [
        "faq_rag",              # FAQ search tool
        "property_search",      # Property search tool (future)
        "booking_calendar",     # Check availability (future)
    ],

    "max_tokens": 2000,
    "temperature": 0.7,
    "timeout_seconds": 30,
}
```

**Real Estate Chat Configuration** (`apps/realestate-api/app/config/chat.py`):

```python
"""Chat feature configuration for Real Estate."""

CHAT_CONFIG = {
    "system_prompt": "You are a real estate advisor specializing in luxury properties, "
                     "land investments, and commercial real estate. Help users evaluate "
                     "properties, understand market trends, and make informed investment decisions.",

    "models": {
        "chat": "anthropic/claude-3-sonnet",
        "search": "anthropic/claude-3-haiku",
        "fallback": "openai/gpt-4o-mini",
    },

    "tools_enabled": [
        "faq_rag",              # FAQ search tool
        "property_search",      # High-value property search
        "investment_calculator", # ROI calculator (future)
    ],

    "max_tokens": 2000,
    "temperature": 0.7,
    "timeout_seconds": 30,
}
```

### Environment Variable Validation

**Startup Validation** (in `app/main.py`):

```python
"""FastAPI application initialization."""

from fastapi import FastAPI
from app.config import settings


def validate_environment():
    """Validate environment configuration on startup."""

    # Required settings
    required = [
        "DATABASE_URL",
        "CLERK_SECRET_KEY",
        "CLERK_PUBLISHABLE_KEY",
        "OPENAI_API_KEY",
    ]

    missing = [key for key in required if not getattr(settings, key, None)]

    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    # Validate database connection
    if not settings.DATABASE_URL.startswith("postgresql+asyncpg://"):
        raise ValueError("DATABASE_URL must use asyncpg driver")

    # Validate Clerk keys
    if not settings.CLERK_SECRET_KEY.startswith("sk_"):
        raise ValueError("CLERK_SECRET_KEY must start with sk_")

    print(f"✅ Configuration validated for {settings.PRODUCT_ID}")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
)

# Validate on startup
@app.on_event("startup")
async def startup_event():
    validate_environment()
```

---

## API Routing Strategy

### Route Structure Decision

**Recommended: Same Routes for Both Products**

```
Bestays API (http://localhost:8101):
    GET  /api/v1/users
    GET  /api/v1/properties
    POST /api/v1/llm/chat
    GET  /api/v1/faq/search

Real Estate API (http://localhost:8102):
    GET  /api/v1/users
    GET  /api/v1/properties
    POST /api/v1/llm/chat
    GET  /api/v1/faq/search
```

**Why Same Routes:**
1. ✅ **Frontend Simplicity** - Same API client library works for both products (just change base URL)
2. ✅ **Shared Documentation** - Single OpenAPI spec (per product) describes all endpoints
3. ✅ **Clear Separation** - Product differentiation at deployment level (ports/domains), not routes
4. ✅ **Testing Simplicity** - Same integration tests work for both products

**Product Differentiation:**
- **Development:** Different ports (8001 vs 8002)
- **Production:** Different domains (api.bestays.app vs api.realestate.app)
- **No route prefixes needed** (`/api/v1/bestays/*` NOT used)

### API Versioning Approach

**Pattern: `/api/v{version}/{resource}`**

```python
# apps/bestays-api/app/main.py
from fastapi import FastAPI
from app.api.v1.router import api_router

app = FastAPI(title="Bestays API")

app.include_router(api_router, prefix="/api/v1")
```

**Future Versioning:**
```python
# When API v2 is needed
from app.api.v1.router import api_router as api_v1_router
from app.api.v2.router import api_router as api_v2_router

app.include_router(api_v1_router, prefix="/api/v1")
app.include_router(api_v2_router, prefix="/api/v2")
```

**Benefits:**
- Clear versioning in URL
- Can run multiple API versions simultaneously
- Easy deprecation path (remove `/api/v1` after migration period)

### CORS Configuration Per Product

**Bestays CORS** (`apps/bestays-api/app/main.py`):

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],  # http://localhost:5273 (dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Real Estate CORS** (`apps/realestate-api/app/main.py`):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],  # http://localhost:5274 (dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Why Product-Specific:**
- Each product only accepts requests from its own frontend
- Prevents cross-product requests (security)
- Simple environment-based configuration

### Swagger Documentation Strategy

**Per-Product OpenAPI Docs:**

```
Bestays API:
    http://localhost:8101/docs  (Swagger UI)
    http://localhost:8101/redoc (ReDoc)

Real Estate API:
    http://localhost:8102/docs  (Swagger UI)
    http://localhost:8102/redoc (ReDoc)
```

**Customization:**

```python
# apps/bestays-api/app/main.py
app = FastAPI(
    title="Bestays API",
    description="API for Bestays vacation rental platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
```

### Error Response Format (Standardized)

**Shared Error Format** (`packages/shared-core/src/exceptions.py`):

```python
"""Standardized error responses."""

from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime


class APIException(Exception):
    """Base API exception."""

    def __init__(self, status_code: int, detail: str, error_code: str = None):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code


async def api_exception_handler(request: Request, exc: APIException):
    """Global exception handler for API exceptions."""
    from app.config import settings  # Import inside function to avoid circular import

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code or f"{exc.status_code}_ERROR",
                "message": exc.detail,
                "product": settings.PRODUCT_ID,
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path),
            }
        }
    )
```

**Example Error Responses:**

```json
// 401 Unauthorized
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token",
    "product": "bestays",
    "timestamp": "2025-11-07T12:34:56.789Z",
    "path": "/api/v1/users/me"
  }
}

// 403 Forbidden
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Admin access required",
    "product": "realestate",
    "timestamp": "2025-11-07T12:35:00.123Z",
    "path": "/api/v1/admin/chat/prompts"
  }
}

// 404 Not Found
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Property not found",
    "product": "bestays",
    "timestamp": "2025-11-07T12:35:15.456Z",
    "path": "/api/v1/properties/abc123"
  }
}
```

---

## Feature Extraction Plan

### Chat Feature Extraction

**Current Location:** `apps/server/src/server/services/chat*.py` (~4500 LOC)

**Target Location:** `packages/shared-chat/`

**Extraction Strategy:**

```python
# packages/shared-chat/src/services/chat_service.py
"""Shared chat service implementation."""

from dataclasses import dataclass
from typing import Optional
from shared_db.models import Conversation, Message, User
from shared_core.logging import logger


@dataclass
class ChatConfig:
    """Chat configuration."""
    system_prompt: str
    models: dict[str, str]
    tools_enabled: list[str]
    max_tokens: int
    temperature: float


class ChatService:
    """Chat service with LLM integration.

    This service is product-agnostic - all product-specific logic is
    passed via ChatConfig.
    """

    def __init__(self, config: ChatConfig, openai_api_key: str, redis_client):
        self.config = config
        self.openai_api_key = openai_api_key
        self.redis_client = redis_client
        self.llm_client = self._create_llm_client()

    def _create_llm_client(self):
        """Create LangChain LLM client."""
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=self.config.models["chat"],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            openai_api_key=self.openai_api_key,
        )

    async def send_message(
        self,
        conversation: Conversation,
        content: str,
        user: Optional[User] = None
    ) -> Message:
        """Send message and get LLM response.

        Args:
            conversation: Conversation object
            content: User message content
            user: Optional user (None for guests)

        Returns:
            Message: LLM response message
        """
        logger.info(
            "chat_message_sent",
            conversation_id=conversation.id,
            user_id=user.id if user else None,
            message_length=len(content),
        )

        # Call LLM (implementation omitted for brevity)
        response = await self._call_llm(conversation, content)

        return response
```

**Product-Specific Usage:**

```python
# apps/bestays-api/app/api/v1/endpoints/chat.py
from shared_chat.services import ChatService, ChatConfig
from app.config.chat import CHAT_CONFIG

@router.post("/llm/chat")
async def chat_endpoint(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    # Create product-specific chat service
    chat_service = ChatService(
        config=ChatConfig(**CHAT_CONFIG),
        openai_api_key=settings.OPENAI_API_KEY,
        redis_client=redis_client,
    )

    # Use shared service with product-specific config
    response = await chat_service.send_message(conversation, request.content, current_user)
    return response
```

**Parameterization Strategy:**

| Element | Shared | Product-Specific | How |
|---------|--------|------------------|-----|
| **LLM client** | ✅ Yes | ❌ No | Shared LangChain integration |
| **System prompt** | ❌ No | ✅ Yes | Passed via ChatConfig |
| **Enabled tools** | ❌ No | ✅ Yes | Passed via ChatConfig |
| **Database models** | ✅ Yes | ❌ No | Shared (Conversation, Message) |
| **Token tracking** | ✅ Yes | ❌ No | Shared cost calculation logic |
| **Conversation management** | ✅ Yes | ❌ No | Shared conversation CRUD |

### FAQ Feature Extraction

**Current Location:** `apps/server/src/server/services/faq*.py` (~2000 LOC)

**Target Location:** `packages/shared-faq/`

**Extraction Strategy:**

```python
# packages/shared-faq/src/services/faq_rag_pipeline.py
"""Shared FAQ RAG pipeline."""

from dataclasses import dataclass
from shared_db.models import FAQDocument
from shared_core.logging import logger


@dataclass
class FAQConfig:
    """FAQ RAG configuration."""
    system_prompt: str
    vector_weight: float
    keyword_weight: float
    top_k_results: int
    cache_ttl: int  # seconds


class FAQRagPipeline:
    """FAQ RAG pipeline with hybrid search.

    This service is product-agnostic - FAQ content is stored in
    product-specific databases.
    """

    def __init__(self, config: FAQConfig, db, redis_client, openai_api_key: str):
        self.config = config
        self.db = db
        self.redis_client = redis_client
        self.openai_api_key = openai_api_key

    async def search(self, query: str) -> list[FAQDocument]:
        """Search FAQ documents using hybrid search.

        Args:
            query: Search query

        Returns:
            List of relevant FAQ documents
        """
        logger.info("faq_search", query=query, query_length=len(query))

        # 1. Check cache
        cached = await self._check_cache(query)
        if cached:
            return cached

        # 2. Vector search (using OpenAI embeddings)
        vector_results = await self._vector_search(query)

        # 3. Keyword search (using PostgreSQL FTS)
        keyword_results = await self._keyword_search(query)

        # 4. Hybrid ranking
        results = self._hybrid_rank(vector_results, keyword_results)

        # 5. Cache results
        await self._cache_results(query, results)

        return results[:self.config.top_k_results]
```

**Product-Specific Usage:**

```python
# apps/bestays-api/app/api/v1/endpoints/faq.py
from shared_faq.services import FAQRagPipeline, FAQConfig
from app.config.faq import FAQ_CONFIG

@router.get("/faq/search")
async def search_faq(
    query: str,
    db: AsyncSession = Depends(get_db),
):
    # Create product-specific FAQ service
    faq_pipeline = FAQRagPipeline(
        config=FAQConfig(**FAQ_CONFIG),
        db=db,
        redis_client=redis_client,
        openai_api_key=settings.OPENAI_API_KEY,
    )

    # Search product-specific FAQ database
    results = await faq_pipeline.search(query)
    return results
```

**FAQ Content Separation:**

```sql
-- Bestays FAQs (bestays_db)
INSERT INTO faq_documents (question, answer, category_id) VALUES
('What is the cancellation policy?', 'Full refund if cancelled 30+ days...', cat_policies),
('How do I book a property?', 'Click the "Book Now" button...', cat_booking);

-- Real Estate FAQs (realestate_db)
INSERT INTO faq_documents (question, answer, category_id) VALUES
('What are property taxes in Thailand?', 'Property taxes vary by location...', cat_legal),
('How do I evaluate ROI?', 'Calculate ROI by dividing net profit...', cat_investment);
```

**Parameterization Strategy:**

| Element | Shared | Product-Specific | How |
|---------|--------|------------------|-----|
| **Vector search algorithm** | ✅ Yes | ❌ No | Shared cosine similarity logic |
| **Keyword search algorithm** | ✅ Yes | ❌ No | Shared PostgreSQL FTS logic |
| **Hybrid ranking** | ✅ Yes | ❌ No | Shared weighted ranking |
| **FAQ content** | ❌ No | ✅ Yes | Stored in separate databases |
| **System prompt** | ❌ No | ✅ Yes | Passed via FAQConfig |
| **Search weights** | ❌ No | ✅ Yes | Passed via FAQConfig (vector vs keyword) |
| **Cache key prefix** | ❌ No | ✅ Yes | Via RedisCache(key_prefix="bestays:") |

### Search Feature Extraction

**Current Location:** `apps/server/src/server/services/search/` (~600 LOC)

**Target Location:** `packages/shared-search/`

**Extraction Strategy:**

```python
# packages/shared-search/src/hybrid_search.py
"""Shared hybrid search utilities."""

from typing import TypeVar, Generic
from dataclasses import dataclass

T = TypeVar('T')


@dataclass
class SearchResult(Generic[T]):
    """Generic search result."""
    item: T
    score: float
    source: str  # "vector" or "keyword"


class HybridSearchService(Generic[T]):
    """Generic hybrid search service.

    This service can be used for any type of hybrid search
    (properties, FAQs, documents, etc.)
    """

    def __init__(self, vector_weight: float = 0.7, keyword_weight: float = 0.3):
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight

    def rank(
        self,
        vector_results: list[SearchResult[T]],
        keyword_results: list[SearchResult[T]],
    ) -> list[SearchResult[T]]:
        """Combine and rank results from vector and keyword searches.

        Args:
            vector_results: Results from vector search
            keyword_results: Results from keyword search

        Returns:
            Combined and ranked results
        """
        # Normalize scores to 0-1 range
        vector_results = self._normalize_scores(vector_results)
        keyword_results = self._normalize_scores(keyword_results)

        # Combine results with weighted scoring
        combined = {}

        for result in vector_results:
            combined[result.item.id] = result.score * self.vector_weight

        for result in keyword_results:
            if result.item.id in combined:
                combined[result.item.id] += result.score * self.keyword_weight
            else:
                combined[result.item.id] = result.score * self.keyword_weight

        # Sort by combined score
        sorted_items = sorted(combined.items(), key=lambda x: x[1], reverse=True)

        return [
            SearchResult(item=item_id, score=score, source="hybrid")
            for item_id, score in sorted_items
        ]
```

**Complexity Estimate:**
- **Extraction Effort:** LOW (1-2 days)
- **Benefits:** Reusable for FAQ search, property search, document search
- **Challenges:** Minimal (search algorithms are domain-independent)

---

## Dependency Injection Patterns

### Shared Dependencies

**Database Session** (`packages/shared-db/src/database.py`):

```python
"""Shared database connection utilities."""

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


def create_database_engine(settings):
    """Create async engine with product-specific settings."""
    return create_async_engine(
        str(settings.DATABASE_URL),
        echo=settings.DATABASE_ECHO,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
        future=True,
    )


def create_session_factory(engine):
    """Create async session factory."""
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def get_db(session_factory) -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

**Product-Specific Database Dependency:**

```python
# apps/bestays-api/app/api/deps.py
"""Bestays API dependencies."""

from functools import partial
from shared_db.database import create_database_engine, create_session_factory, get_db
from app.config import settings

# Create product-specific engine and session factory
engine = create_database_engine(settings)
session_factory = create_session_factory(engine)

# Create product-specific dependency
get_bestays_db = partial(get_db, session_factory)
```

**Usage in Endpoints:**

```python
# apps/bestays-api/app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_bestays_db

router = APIRouter()

@router.get("/users")
async def list_users(db: AsyncSession = Depends(get_bestays_db)):
    # This db session ONLY connects to bestays_db
    result = await db.execute(select(User))
    return result.scalars().all()
```

### Authentication Dependencies

**Shared RBAC Decorators** (`packages/shared-core/src/auth.py`):

```python
"""Shared authentication and authorization utilities."""

from functools import wraps
from fastapi import HTTPException
from shared_db.models import User


def require_role(*allowed_roles: str):
    """Decorator to require specific user roles.

    Usage:
        @require_role("admin")
        async def admin_endpoint(current_user: User):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(current_user: User, *args, **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Required role: {', '.join(allowed_roles)}"
                )
            return await func(current_user=current_user, *args, **kwargs)
        return wrapper
    return decorator
```

**Product-Specific Clerk Integration:**

```python
# apps/bestays-api/app/api/deps.py
from clerk_backend_api import Clerk
from shared_db.models import User
from app.config import settings

# Create product-specific Clerk client
clerk_client = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_bestays_db),
) -> User:
    """Get current authenticated user (Bestays Clerk project).

    This validates JWT tokens against Bestays Clerk project and
    retrieves/creates users in bestays_db.
    """
    # Verify Clerk JWT token (product-specific)
    clerk_user = await clerk_client.verify_token(token)

    # Get or create user in product database
    user = await db.get(User, clerk_user.id)

    if not user:
        # JIT provisioning
        user = User(
            clerk_user_id=clerk_user.id,
            email=clerk_user.email,
            role="user",  # Default role
        )
        db.add(user)
        await db.commit()

    return user


async def get_current_user_optional(
    token: str = Depends(oauth2_scheme_optional),
    db: AsyncSession = Depends(get_bestays_db),
) -> User | None:
    """Get current user if authenticated, otherwise None (for guest support)."""
    if not token:
        return None
    return await get_current_user(token, db)
```

**Usage with RBAC:**

```python
# apps/bestays-api/app/api/v1/endpoints/admin.py
from shared_core.auth import require_role
from app.api.deps import get_current_user

@router.post("/admin/chat/prompts")
@require_role("admin")
async def update_chat_prompt(
    prompt: ChatPromptUpdate,
    current_user: User = Depends(get_current_user),
):
    # Only admins can reach this endpoint
    ...
```

### Service Dependencies

**Chat Service Dependency:**

```python
# apps/bestays-api/app/api/deps.py
from shared_chat.services import ChatService, ChatConfig
from shared_core.cache import RedisCache
from app.config.chat import CHAT_CONFIG

def get_chat_service(
    db: AsyncSession = Depends(get_bestays_db),
) -> ChatService:
    """Get product-specific chat service."""
    redis_client = RedisCache(
        redis_url=settings.REDIS_URL,
        key_prefix=settings.REDIS_KEY_PREFIX,
    )

    return ChatService(
        config=ChatConfig(**CHAT_CONFIG),
        db=db,
        redis_client=redis_client,
        openai_api_key=settings.OPENAI_API_KEY,
    )
```

**FAQ Service Dependency:**

```python
def get_faq_service(
    db: AsyncSession = Depends(get_bestays_db),
) -> FAQRagPipeline:
    """Get product-specific FAQ service."""
    redis_client = RedisCache(
        redis_url=settings.REDIS_URL,
        key_prefix=settings.REDIS_KEY_PREFIX,
    )

    return FAQRagPipeline(
        config=FAQConfig(**FAQ_CONFIG),
        db=db,
        redis_client=redis_client,
        openai_api_key=settings.OPENAI_API_KEY,
    )
```

### Testing with Dependency Injection

**Override Dependencies in Tests:**

```python
# apps/bestays-api/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.api.deps import get_bestays_db


@pytest.fixture
def test_db_engine():
    """Create SQLite in-memory database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_db_session(test_db_engine):
    """Create test database session."""
    Session = sessionmaker(bind=test_db_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def client(test_db_session):
    """Create test client with overridden dependencies."""
    def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_bestays_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
```

---

## Testing Strategy

### Unit Tests (SQLite In-Memory)

**Pattern: Shared Packages with SQLite**

```python
# packages/shared-chat/tests/test_chat_service.py
"""Unit tests for chat service."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared_db.database import Base
from shared_db.models import Conversation, Message, User
from shared_chat.services import ChatService, ChatConfig


@pytest.fixture
def db_engine():
    """Create in-memory SQLite database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(db_engine):
    """Create database session."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()


def test_chat_service_initialization(db_session):
    """Test ChatService can be initialized."""
    config = ChatConfig(
        system_prompt="Test prompt",
        models={"chat": "gpt-4o-mini"},
        tools_enabled=[],
        max_tokens=100,
        temperature=0.7,
    )

    chat_service = ChatService(
        config=config,
        openai_api_key="test_key",
        redis_client=None,
    )

    assert chat_service.config.system_prompt == "Test prompt"


async def test_send_message(db_session):
    """Test sending a chat message."""
    # Create test conversation
    conversation = Conversation(session_id="test_123", user_id=1)
    db_session.add(conversation)
    db_session.commit()

    # Create test user
    user = User(clerk_user_id="test_user", email="test@example.com", role="user")
    db_session.add(user)
    db_session.commit()

    # Create chat service (with mocked LLM)
    config = ChatConfig(
        system_prompt="Test",
        models={"chat": "gpt-4o-mini"},
        tools_enabled=[],
        max_tokens=100,
        temperature=0.7,
    )

    chat_service = ChatService(config=config, openai_api_key="test", redis_client=None)

    # Send message (mock LLM response)
    with pytest.mock.patch.object(chat_service, '_call_llm') as mock_llm:
        mock_llm.return_value = Message(
            conversation_id=conversation.id,
            role="assistant",
            content="Test response"
        )

        response = await chat_service.send_message(conversation, "Hello", user)
        assert response.content == "Test response"
```

**Coverage Targets:**
- Shared packages: **≥95%** (high-risk, used by both products)
- Product apps: **≥80%** (medium-risk, product-specific logic)

### Integration Tests (PostgreSQL)

**Pattern: Test Databases per Product**

```python
# apps/bestays-api/tests/integration/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from shared_db.database import Base


@pytest.fixture
async def test_postgres_engine():
    """Create test PostgreSQL database."""
    test_db_url = "postgresql+asyncpg://postgres:postgres@localhost:5432/bestays_db_test"

    engine = create_async_engine(test_db_url)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_db_session(test_postgres_engine):
    """Create test database session."""
    async_session = sessionmaker(
        test_postgres_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
```

```python
# apps/bestays-api/tests/integration/test_chat_endpoint.py
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_chat_endpoint(test_db_session):
    """Test chat endpoint with real database."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/llm/chat",
            json={"content": "Hello"},
            headers={"Authorization": "Bearer test_token"}
        )

        assert response.status_code == 200
        assert "message" in response.json()
```

### E2E Tests (Playwright)

**Pattern: Test Against Running Services**

```typescript
// apps/bestays-api/tests/e2e/chat.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Bestays Chat', () => {
  test.beforeAll(async () => {
    // Reset test database
    await exec('bash scripts/reset-bestays-test-db.sh');
  });

  test('user can send chat message', async ({ page }) => {
    // Navigate to Bestays frontend
    await page.goto('http://localhost:5273');

    // Login
    await page.click('text=Sign In');
    await page.fill('input[name="email"]', 'user.claudecode@bestays.app');
    await page.fill('input[name="password"]', '9kB*k926O8):');
    await page.click('button:has-text("Sign In")');

    // Open chat
    await page.click('[data-testid="chat-toggle"]');

    // Send message
    await page.fill('[data-testid="chat-input"]', 'What is the cancellation policy?');
    await page.click('[data-testid="chat-send"]');

    // Verify response
    await expect(page.locator('[data-testid="chat-message"]').last()).toContainText('Full refund');
  });
});
```

### Test Data Management

**Shared Test Fixtures** (`packages/shared-db/tests/fixtures.py`):

```python
"""Shared test data fixtures."""

from shared_db.models import User, Property, Conversation


def create_test_user(
    clerk_user_id: str = "test_user",
    email: str = "test@example.com",
    role: str = "user",
) -> User:
    """Create test user."""
    return User(
        clerk_user_id=clerk_user_id,
        email=email,
        role=role,
    )


def create_test_property(
    title: str = "Test Property",
    created_by: int = 1,
) -> Property:
    """Create test property."""
    return Property(
        title=title,
        description="Test property description",
        created_by=created_by,
    )


def create_test_conversation(
    session_id: str = "test_session",
    user_id: int | None = None,
) -> Conversation:
    """Create test conversation."""
    return Conversation(
        session_id=session_id,
        user_id=user_id,
    )
```

---

## Docker Deployment

### Dockerfile Per Product

**Bestays API Dockerfile** (`docker/bestays-api/Dockerfile.prod`):

```dockerfile
# Stage 1: Build dependencies
FROM python:3.12-slim AS builder

WORKDIR /build

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy shared packages
COPY packages/shared-db /build/packages/shared-db
COPY packages/shared-config /build/packages/shared-config
COPY packages/shared-core /build/packages/shared-core
COPY packages/shared-chat /build/packages/shared-chat
COPY packages/shared-faq /build/packages/shared-faq
COPY packages/shared-search /build/packages/shared-search

# Install shared packages
RUN pip install --no-cache-dir \
    /build/packages/shared-db \
    /build/packages/shared-config \
    /build/packages/shared-core \
    /build/packages/shared-chat \
    /build/packages/shared-faq \
    /build/packages/shared-search

# Copy app dependencies
COPY apps/bestays-api/pyproject.toml /build/

# Install app dependencies
RUN pip install --no-cache-dir -r /build/pyproject.toml

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12

# Copy application code
COPY apps/bestays-api /app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Real Estate API Dockerfile** (`docker/realestate-api/Dockerfile.prod`):

```dockerfile
# Same structure as Bestays, just change:
# - COPY apps/realestate-api /app
# - (Everything else is identical)
```

### Docker Compose Orchestration

**Development** (`docker-compose.dev.yml`):

```yaml
services:
  # PostgreSQL (One Container, Two Databases)
  postgres:
    image: postgres:16-alpine
    container_name: bestays-postgres-dev
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init-multi-db.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - bestays-network

  # Redis (Shared, Multiple Databases)
  redis:
    image: redis:7-alpine
    container_name: bestays-redis-dev
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - bestays-network

  # Bestays API
  bestays-api:
    build:
      context: .
      dockerfile: docker/bestays-api/Dockerfile.dev
    container_name: bestays-api-dev
    environment:
      APP_NAME: Bestays
      PRODUCT_ID: bestays
      DATABASE_URL: postgresql+asyncpg://bestays_user:bestays_password@postgres:5432/bestays_db_dev
      CLERK_SECRET_KEY: ${BESTAYS_CLERK_SECRET_KEY}
      CLERK_PUBLISHABLE_KEY: ${BESTAYS_CLERK_PUBLISHABLE_KEY}
      REDIS_URL: redis://redis:6379/0
      REDIS_KEY_PREFIX: bestays:
      FRONTEND_URL: http://localhost:5273
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "8101:8000"
    volumes:
      - ./apps/bestays-api:/app:delegated
      - ./packages:/packages:delegated
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - bestays-network

  # Real Estate API
  realestate-api:
    build:
      context: .
      dockerfile: docker/realestate-api/Dockerfile.dev
    container_name: realestate-api-dev
    environment:
      APP_NAME: Best Real Estate
      PRODUCT_ID: realestate
      DATABASE_URL: postgresql+asyncpg://realestate_user:realestate_password@postgres:5432/realestate_db_dev
      CLERK_SECRET_KEY: ${REALESTATE_CLERK_SECRET_KEY}
      CLERK_PUBLISHABLE_KEY: ${REALESTATE_CLERK_PUBLISHABLE_KEY}
      REDIS_URL: redis://redis:6379/1
      REDIS_KEY_PREFIX: realestate:
      FRONTEND_URL: http://localhost:5274
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "8102:8000"
    volumes:
      - ./apps/realestate-api:/app:delegated
      - ./packages:/packages:delegated
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - bestays-network

networks:
  bestays-network:
    driver: bridge

volumes:
  postgres_data:
```

### Image Optimization

**Multi-Stage Build Benefits:**
1. ✅ **Smaller images** - Runtime image doesn't include build tools
2. ✅ **Faster builds** - Builder stage cached independently
3. ✅ **Security** - Fewer packages in production image

**Shared Package Handling:**
- Shared packages copied into builder stage
- Installed with `pip install /build/packages/shared-*`
- No need for external package registry during development

---

## Migration from Current State

### 7-Week Phased Migration Plan

**Phase 1: Setup Monorepo Structure (Week 1)**

**Tasks:**
1. Create `packages/` directory structure
2. Set up `pyproject.toml` for each shared package
3. Create base `packages/shared-db/` with empty models
4. Create base `packages/shared-config/` with empty settings

**Validation:**
- Directory structure created
- All `pyproject.toml` files valid
- `pip install -e packages/shared-*` works

**Risk:** LOW - Just creating structure, no code changes

---

**Phase 2: Extract Shared Database Models (Week 2)**

**Tasks:**
1. Copy models from `apps/server/src/server/models/` to `packages/shared-db/src/models/`
2. Update imports in `packages/shared-db/src/models/` (remove server references)
3. Create `packages/shared-db/src/database.py` with connection utilities
4. Install `shared-db` in existing server: `pip install -e packages/shared-db`
5. Update imports in `apps/server/` to use `from shared_db.models import User`
6. Run existing tests to ensure nothing broke

**Validation:**
- All models imported from `shared-db`
- All existing tests pass
- No circular import errors

**Risk:** LOW - Just moving files, maintaining same structure

---

**Phase 3: Extract Configuration Package (Week 2)**

**Tasks:**
1. Create `packages/shared-config/src/base.py` (BaseProductSettings)
2. Create `packages/shared-config/src/database.py` (DatabaseSettings)
3. Update `apps/server/src/server/config.py` to inherit from `DatabaseSettings`
4. Test with existing server

**Validation:**
- Configuration loading works
- Environment variables validated correctly
- Existing server starts successfully

**Risk:** LOW - Just creating base classes

---

**Phase 4: Create Bestays App (Week 3)**

**Tasks:**
1. Copy `apps/server/` to `apps/bestays-api/`
2. Update `apps/bestays-api/app/config.py`:
   - Add `PRODUCT_ID = "bestays"`
   - Update `DATABASE_URL` to point to `bestays_db_dev`
   - Add `CLERK_SECRET_KEY` for Bestays Clerk project
3. Update `apps/bestays-api/alembic.ini` (database URL)
4. Run migrations: `alembic upgrade head`
5. Seed development data
6. Test Bestays API: `http://localhost:8101/docs`

**Validation:**
- Bestays API starts successfully
- Swagger UI accessible
- Can create users, properties
- Existing tests pass

**Risk:** MEDIUM - First time creating separate product app

**Rollback:** Revert to `apps/server/` if issues found

---

**Phase 5: Extract Chat Feature (Week 4)**

**Tasks:**
1. Create `packages/shared-chat/src/services/`
2. Move chat services from `apps/bestays-api/app/services/` to `packages/shared-chat/`
3. Parameterize product-specific logic:
   - Extract system prompts to `apps/bestays-api/app/config/chat.py`
   - Pass config via `ChatConfig` dataclass
4. Update `apps/bestays-api/` to use `from shared_chat.services import ChatService`
5. Write unit tests for `shared-chat` package
6. Test chat endpoint with Bestays

**Validation:**
- Chat feature works in Bestays
- All tests pass (unit + integration)
- Coverage ≥95% for `shared-chat` package

**Risk:** HIGH - Complex LangChain dependencies

**Rollback:** Revert `shared-chat` extraction, keep services in app

---

**Phase 6: Extract FAQ Feature (Week 5)**

**Tasks:**
1. Create `packages/shared-faq/src/services/`
2. Move FAQ RAG services from `apps/bestays-api/app/services/` to `packages/shared-faq/`
3. Parameterize search weights via `FAQConfig`
4. Update Bestays to use `from shared_faq.services import FAQRagPipeline`
5. Write unit tests for `shared-faq` package
6. Test FAQ search with Bestays

**Validation:**
- FAQ search works in Bestays
- Vector search accurate (cosine similarity)
- Keyword search accurate (PostgreSQL FTS)
- Coverage ≥95% for `shared-faq` package

**Risk:** HIGH - pgvector, OpenAI, Redis dependencies

**Rollback:** Revert `shared-faq` extraction

---

**Phase 7: Create Real Estate App (Week 6)**

**Tasks:**
1. Copy `apps/bestays-api/` to `apps/realestate-api/`
2. Update configuration:
   - `PRODUCT_ID = "realestate"`
   - `APP_NAME = "Best Real Estate"`
   - `DATABASE_URL` → `realestate_db_dev`
   - `CLERK_SECRET_KEY` → Real Estate Clerk project
   - `REDIS_KEY_PREFIX = "realestate:"`
3. Update Alembic config
4. Copy migrations from Bestays
5. Update migration revision IDs (script: `scripts/update_migration_revisions.py`)
6. Run migrations: `alembic upgrade head`
7. Seed Real Estate-specific data:
   - FAQ content (legal, investment, market trends)
   - Test properties (high-value, commercial)
8. Test Real Estate API: `http://localhost:8102/docs`

**Validation:**
- Real Estate API starts successfully
- Separate database verified (no cross-product data)
- Chat works with Real Estate system prompts
- FAQ returns Real Estate content (not Bestays)

**Risk:** MEDIUM - First time duplicating product

**Rollback:** Delete `apps/realestate-api/`, keep only Bestays

---

**Phase 8: Validation & Documentation (Week 7)**

**Tasks:**
1. Run E2E tests for both products (Playwright)
2. Performance testing:
   - Chat response times (<2s)
   - FAQ search response times (<500ms)
   - API endpoint response times (<200ms)
3. Security audit:
   - CORS configuration correct
   - JWT validation working
   - No cross-product data leakage
4. Update documentation:
   - README for each shared package
   - README for each product app
   - Architecture diagrams
   - API integration guide for frontend
5. Final validation checklist:
   - [ ] Both APIs start successfully
   - [ ] Both databases isolated
   - [ ] Both Clerk projects configured
   - [ ] All tests pass (unit, integration, E2E)
   - [ ] Coverage targets met (≥95% shared, ≥80% apps)
   - [ ] Docker Compose works
   - [ ] Documentation complete

**Risk:** LOW - Validation and documentation only

---

### How to Preserve Existing Bestays Data

**Scenario:** Production Bestays already has user data in `bestays_dev` database

**Migration Strategy:**

```bash
#!/bin/bash
# migrate-existing-bestays.sh

set -e

echo "📦 Migrating existing Bestays data..."

# Step 1: Backup current database
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U postgres bestays_dev > /tmp/bestays_backup_${TIMESTAMP}.sql

echo "✅ Backup created: /tmp/bestays_backup_${TIMESTAMP}.sql"

# Step 2: Create new database
psql -h localhost -U postgres -c "CREATE DATABASE bestays_db;"
psql -h localhost -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE bestays_db TO bestays_user;"

# Step 3: Restore data to new database
psql -h localhost -U postgres bestays_db < /tmp/bestays_backup_${TIMESTAMP}.sql

echo "✅ Data restored to bestays_db"

# Step 4: Run any new migrations
cd apps/bestays-api
export DATABASE_URL=postgresql+asyncpg://bestays_user:password@localhost:5432/bestays_db
alembic upgrade head

echo "✅ Migrations applied"

# Step 5: Validate data
python scripts/validate_migration.py

echo "✅ Migration complete!"
echo "⚠️  Keep backup at /tmp/bestays_backup_${TIMESTAMP}.sql for 7 days"
```

**Data Validation Script:**

```python
# apps/bestays-api/scripts/validate_migration.py
"""Validate data migration."""

import asyncio
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from shared_db.models import User, Property


async def validate_migration():
    """Verify all data migrated correctly."""

    # Connect to old database
    old_engine = create_async_engine("postgresql+asyncpg://...@localhost/bestays_dev")
    old_session = sessionmaker(old_engine, class_=AsyncSession)

    # Connect to new database
    new_engine = create_async_engine("postgresql+asyncpg://...@localhost/bestays_db")
    new_session = sessionmaker(new_engine, class_=AsyncSession)

    # Count users
    async with old_session() as old_db, new_session() as new_db:
        old_user_count = await old_db.scalar(select(func.count(User.id)))
        new_user_count = await new_db.scalar(select(func.count(User.id)))

        print(f"Old database: {old_user_count} users")
        print(f"New database: {new_user_count} users")

        if old_user_count == new_user_count:
            print("✅ User count matches!")
        else:
            print("❌ User count mismatch!")
            return False

        # Count properties
        old_property_count = await old_db.scalar(select(func.count(Property.id)))
        new_property_count = await new_db.scalar(select(func.count(Property.id)))

        print(f"Old database: {old_property_count} properties")
        print(f"New database: {new_property_count} properties")

        if old_property_count == new_property_count:
            print("✅ Property count matches!")
        else:
            print("❌ Property count mismatch!")
            return False

    await old_engine.dispose()
    await new_engine.dispose()

    return True


if __name__ == "__main__":
    result = asyncio.run(validate_migration())
    exit(0 if result else 1)
```

---

## Code Examples

### Configuration Example

**Bestays .env.development:**

```bash
# Product Identification
APP_NAME=Bestays
PRODUCT_ID=bestays

# Database
DATABASE_URL=postgresql+asyncpg://bestays_user:bestays_password@localhost:5432/bestays_db_dev

# Clerk (Bestays Project)
CLERK_SECRET_KEY=sk_test_vGrRuTLW1SdS2uQlDbv4l2T2WHpTk9IoervBmG9Vit
CLERK_PUBLISHABLE_KEY=pk_test_c2FjcmVkLW1heWZseS01NS5jbGVyay5hY2NvdW50cy5kZXYk
CLERK_WEBHOOK_SECRET=whsec_bestays_dev

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_KEY_PREFIX=bestays:

# Frontend
FRONTEND_URL=http://localhost:5273

# OpenAI
OPENAI_API_KEY=sk-proj-...

# Feature Flags
CHAT_ENABLED=true
FAQ_ENABLED=true
SEARCH_ENABLED=true
```

### FastAPI App Initialization

**apps/bestays-api/app/main.py:**

```python
"""Bestays API application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared_db.database import create_database_engine, create_session_factory
from shared_core.exceptions import api_exception_handler, APIException

from app.config import settings
from app.api.v1.router import api_router


# Create product-specific database engine
engine = create_database_engine(settings)
session_factory = create_session_factory(engine)


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="API for Bestays vacation rental platform",
    version="1.0.0",
)


# CORS middleware (product-specific)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
app.add_exception_handler(APIException, api_exception_handler)


# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Startup validation."""
    print(f"✅ {settings.APP_NAME} API starting...")
    print(f"   Product ID: {settings.PRODUCT_ID}")
    print(f"   Database: {settings.DATABASE_URL}")
    print(f"   Frontend: {settings.FRONTEND_URL}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    await engine.dispose()
    print(f"✅ {settings.APP_NAME} API shutdown complete")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": settings.APP_NAME,
        "product_id": settings.PRODUCT_ID,
        "version": "1.0.0",
    }
```

### Dependency Injection Example

**apps/bestays-api/app/api/deps.py:**

```python
"""Bestays API dependencies."""

from functools import partial
from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from clerk_backend_api import Clerk

from shared_db.database import create_database_engine, create_session_factory, get_db
from shared_db.models import User
from shared_chat.services import ChatService, ChatConfig
from shared_faq.services import FAQRagPipeline, FAQConfig
from shared_core.cache import RedisCache

from app.config import settings
from app.config.chat import CHAT_CONFIG
from app.config.faq import FAQ_CONFIG


# Create product-specific database dependencies
engine = create_database_engine(settings)
session_factory = create_session_factory(engine)
get_bestays_db = partial(get_db, session_factory)


# Clerk authentication
clerk_client = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)
oauth2_scheme = HTTPBearer()


async def get_current_user(
    credentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_bestays_db),
) -> User:
    """Get current authenticated user (Bestays)."""
    token = credentials.credentials

    try:
        # Verify Clerk JWT token
        clerk_user = await clerk_client.verify_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Get user from database
    user = await db.get(User, clerk_user.id)

    if not user:
        # JIT provisioning
        user = User(
            clerk_user_id=clerk_user.id,
            email=clerk_user.email,
            role="user",
        )
        db.add(user)
        await db.commit()

    return user


async def get_current_user_optional(
    credentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_bestays_db),
) -> Optional[User]:
    """Get current user if authenticated, otherwise None."""
    if not credentials:
        return None
    return await get_current_user(credentials, db)


# Chat service dependency
def get_chat_service(
    db: AsyncSession = Depends(get_bestays_db),
) -> ChatService:
    """Get product-specific chat service."""
    redis_client = RedisCache(
        redis_url=settings.REDIS_URL,
        key_prefix=settings.REDIS_KEY_PREFIX,
    )

    return ChatService(
        config=ChatConfig(**CHAT_CONFIG),
        db=db,
        redis_client=redis_client,
        openai_api_key=settings.OPENAI_API_KEY,
    )


# FAQ service dependency
def get_faq_service(
    db: AsyncSession = Depends(get_bestays_db),
) -> FAQRagPipeline:
    """Get product-specific FAQ service."""
    redis_client = RedisCache(
        redis_url=settings.REDIS_URL,
        key_prefix=settings.REDIS_KEY_PREFIX,
    )

    return FAQRagPipeline(
        config=FAQConfig(**FAQ_CONFIG),
        db=db,
        redis_client=redis_client,
        openai_api_key=settings.OPENAI_API_KEY,
    )
```

### API Endpoint Example

**apps/bestays-api/app/api/v1/endpoints/chat.py:**

```python
"""Chat endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared_db.models import User
from shared_chat.services import ChatService
from shared_chat.schemas import ChatRequest, ChatResponse

from app.api.deps import get_bestays_db, get_current_user_optional, get_chat_service


router = APIRouter(prefix="/llm", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    db: AsyncSession = Depends(get_bestays_db),
    current_user: User | None = Depends(get_current_user_optional),
    chat_service: ChatService = Depends(get_chat_service),
):
    """Send chat message and get AI response.

    Args:
        request: Chat request with message content
        db: Database session
        current_user: Current user (optional, supports guests)
        chat_service: Chat service (product-specific)

    Returns:
        ChatResponse: AI response with message and metadata
    """
    # Get or create conversation
    conversation = await chat_service.get_or_create_conversation(
        db=db,
        session_id=request.session_id,
        user=current_user,
    )

    # Send message and get response
    response = await chat_service.send_message(
        conversation=conversation,
        content=request.content,
        user=current_user,
    )

    return response
```

---

## Trade-offs and Risks

### Pros of Recommended Approach

**Simplicity:**
- ✅ **Python namespace packages** - Standard Python packaging, no complex tooling
- ✅ **Environment-based configuration** - Clear `.env` files per product
- ✅ **Docker Compose** - Existing orchestration pattern, one command deployment
- ✅ **Same API routes** - Frontend uses same client library, just different base URL

**Modularity:**
- ✅ **Clear package boundaries** - Shared packages vs product apps
- ✅ **Explicit dependencies** - Each package declares dependencies in `pyproject.toml`
- ✅ **One-way dependencies** - No circular imports (shared → apps, never reverse)
- ✅ **Easy extraction** - Shared packages can be sold independently

**Safety:**
- ✅ **Product-specific database connections** - Zero risk of cross-product queries
- ✅ **Product-specific Clerk projects** - Complete user isolation
- ✅ **Product-specific Redis namespaces** - No cache collision

**Testability:**
- ✅ **Unit tests with SQLite** - Fast, no PostgreSQL needed
- ✅ **Integration tests with PostgreSQL** - Real database validation
- ✅ **E2E tests with Playwright** - Full stack testing
- ✅ **Coverage enforcement** - ≥95% shared, ≥80% apps

### Cons of Recommended Approach

**Package Management:**
- ❌ **Manual package installation** - Need `pip install -e packages/shared-*` for each package
  - **Mitigation:** Script to install all shared packages (`scripts/install-shared-packages.sh`)
- ❌ **No automatic package registry** - Shared packages not published to PyPI
  - **Mitigation:** Use file paths in `pyproject.toml` for development

**Migration Overhead:**
- ❌ **Need to sync migrations** - Copy from Bestays to Real Estate, update revision IDs
  - **Mitigation:** Automation script (`scripts/sync-migrations.sh`)
- ❌ **Run migrations twice** - Once per database
  - **Mitigation:** Makefile targets (`make migrate-all`)

**Deployment Complexity:**
- ❌ **Two Dockerfiles** - One per product (duplicated structure)
  - **Mitigation:** Shared base image (future optimization if needed)
- ❌ **Two API containers** - Separate ports/domains
  - **Mitigation:** Docker Compose manages both, nginx reverse proxy in production

### Comparison with Alternatives

**Alternative 1: Turborepo + pnpm Workspaces**

| Factor | Recommended (Python Namespace) | Turborepo + pnpm |
|--------|-------------------------------|------------------|
| **Complexity** | ✅ Low (standard Python) | ❌ High (new tooling) |
| **Build Speed** | ✅ Fast (no build step) | ✅ Fast (Turborepo caching) |
| **Python Ecosystem** | ✅ Native | ⚠️ Requires shims |
| **Learning Curve** | ✅ Familiar | ❌ New concepts |

**Verdict:** Stick with Python namespace packages for simplicity

**Alternative 2: Monolithic App with tenant_id**

| Factor | Recommended (Separate Products) | Monolithic Multi-Tenant |
|--------|--------------------------------|-------------------------|
| **Data Isolation** | ✅ Complete (separate DBs) | ⚠️ Requires WHERE tenant_id |
| **Risk of Data Leakage** | ✅ Zero | ❌ High (missing WHERE clause) |
| **Deployment** | ✅ Independent per product | ✅ Single deployment |
| **White-Label Readiness** | ✅ Easy to extract | ❌ Hard to untangle |

**Verdict:** Separate products for white-label architecture

### When to Revisit This Decision

**Scenario 1: More Than 5 Products**

If the platform grows to 10+ products:
- Consider shared authentication (single Clerk project with metadata)
- Consider multi-tenant database (tenant_id) for cost efficiency
- Consider Kubernetes for horizontal scaling

**Scenario 2: Shared User Accounts Required**

If business requirements change to allow cross-product users:
- Switch to single Clerk project
- Add product_id to users table (multi-tenant)
- Implement RBAC per product

**Scenario 3: Selling Shared Packages**

If selling Chat or FAQ packages as SaaS:
- Publish to PyPI (versioning, dependency management)
- Create separate repositories per package
- Add package licensing and documentation

---

## Next Steps for Frontend Agent (TASK-004)

**What Frontend Needs from This Backend Design:**

### 1. API Integration Patterns

**API Base URLs:**
```typescript
// apps/bestays-web/src/config/api.ts
export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8101',
  timeout: 30000,
};

// apps/realestate-web/src/config/api.ts
export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8102',
  timeout: 30000,
};
```

**Key Insight:** Same API client library, just different base URL

### 2. API Routes Structure

**All products use identical routes:**
```
GET  /api/v1/users
GET  /api/v1/users/me
GET  /api/v1/properties
POST /api/v1/llm/chat
GET  /api/v1/faq/search
```

**Frontend should:**
- Create ONE API client library (e.g., `packages/shared-api-client/`)
- Reuse for both products
- Only difference: base URL configuration

### 3. Error Response Format

**Standard error format:**
```typescript
interface APIError {
  error: {
    code: string;
    message: string;
    product: string;  // "bestays" or "realestate"
    timestamp: string;
    path: string;
  }
}
```

**Frontend should:**
- Create error handling utilities in shared package
- Display user-friendly error messages
- Log errors with product context

### 4. Authentication Flow

**Clerk Configuration:**
```typescript
// apps/bestays-web/src/lib/clerk.ts
import { CLERK_PUBLISHABLE_KEY } from '$env/static/public';

export const clerk = new Clerk(CLERK_PUBLISHABLE_KEY);
```

**Key Insight:** Separate Clerk projects per product (different publishable keys)

### 5. Environment Variables

**Bestays Frontend (.env.development):**
```bash
VITE_APP_NAME=Bestays
VITE_API_URL=http://localhost:8101
VITE_CLERK_PUBLISHABLE_KEY=pk_test_c2FjcmVkLW1heWZseS01NS5jbGVyay5hY2NvdW50cy5kZXYk
```

**Real Estate Frontend (.env.development):**
```bash
VITE_APP_NAME=Best Real Estate
VITE_API_URL=http://localhost:8102
VITE_CLERK_PUBLISHABLE_KEY=pk_test_cGxlYXNhbnQtZ251LTI1LmNsZXJrLmFjY291bnRzLmRldiQ
```

### 6. TypeScript Types from Backend

**Frontend should:**
1. Read backend Pydantic schemas to understand API contracts
2. Create matching TypeScript interfaces:
   ```typescript
   // From shared_chat.schemas.ChatResponse
   export interface ChatResponse {
     message: Message;
     model: string;
     usage: {
       prompt_tokens: number;
       completion_tokens: number;
       total_tokens: number;
     };
     conversation_id: number;
     session_id: string;
   }
   ```
3. Use Zod for runtime validation (matches Pydantic validation)

### 7. Shared Components Strategy

**Frontend should create:**
```
packages/
├── shared-ui/          # Reusable Svelte components
├── shared-api-client/  # API client library
└── shared-types/       # TypeScript types
```

**Products import shared components:**
```typescript
// apps/bestays-web/src/routes/+page.svelte
import { ChatInterface } from '@bestays/shared-ui';
import { config } from '$config';

<ChatInterface config={config} />
```

---

## Conclusion

**Recommended Approach: Python Namespace Packages with Shared Services**

**Why This Approach:**
1. ✅ **Simplest** - Standard Python packaging, no complex tooling
2. ✅ **Most Modular** - Clear package boundaries, explicit dependencies
3. ✅ **Best Documented** - Environment variables, Pydantic settings, standard patterns
4. ✅ **Safest** - Product-specific database connections prevent cross-product queries

**Alignment with User Priorities:**
- ✅ **Simplicity for deployment** - Docker Compose orchestration
- ✅ **Simplicity for development** - `pip install -e packages/shared-*`
- ✅ **Modular architecture** - Shared packages + product apps
- ✅ **Clear documentation** - Environment-based configuration

**Confidence Level: HIGH** - This approach uses proven Python patterns, existing Docker orchestration, and maintains simplicity throughout.

**Next Agent (TASK-004):** Frontend agent should design SvelteKit architecture with shared components, use API patterns documented here, and implement product-specific branding via configuration.

---

**Document Version:** 1.0
**Date:** 2025-11-07
**Agent:** dev-backend
**Status:** COMPLETE
**Next Task:** TASK-004 (Frontend Architecture Design by dev-frontend-svelte agent)

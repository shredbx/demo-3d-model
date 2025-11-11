# TASK-002: Database Isolation Strategy

**Date:** 2025-11-07
**Agent:** dev-database
**User Story:** US-018 (White-Label Multi-Product Architecture)
**Status:** COMPLETE
**Priority:** P0 (URGENT AND MANDATORY)

---

## Executive Summary

**Recommended Approach:** **Separate Databases (Option A)**

**Key Rationale:**
1. **Simplicity First** - Two PostgreSQL databases (`bestays_db`, `realestate_db`) on the same PostgreSQL instance
2. **Complete Data Isolation** - Zero risk of cross-product data leakage
3. **Modular Architecture** - Each product is independently deployable and scalable
4. **Clear Documentation** - Connection configuration per product via environment variables

**Alignment with User Priorities:**
- ✅ **Simplicity for deployment** - Same PostgreSQL instance, different databases (one command: `docker-compose up`)
- ✅ **Simplicity for development** - No complex tenant_id filtering, straightforward testing
- ✅ **Modular architecture** - Each product has its own database namespace
- ✅ **Clear documentation** - Environment-based configuration, easy to understand

**Risk Assessment:** LOW - This approach is proven, simple, and eliminates the risk of data leakage that multi-tenancy introduces.

---

## Database Isolation Design

### Architecture Diagram

```
PostgreSQL Instance (Single Docker Container)
├── bestays_db (Database 1)
│   ├── users (Clerk: sacred-mayfly-55)
│   ├── properties (rental properties)
│   ├── conversations (chat history)
│   ├── faq_documents (rental FAQs)
│   ├── faq_embeddings (vector search)
│   └── ... (all shared schema tables)
│
└── realestate_db (Database 2)
    ├── users (Clerk: pleasant-gnu-25)
    ├── properties (high-value properties)
    ├── conversations (chat history)
    ├── faq_documents (real estate FAQs)
    ├── faq_embeddings (vector search)
    └── ... (all shared schema tables)
```

**Key Design Decisions:**

1. **Same PostgreSQL Instance** - Cost-effective, simple to deploy
2. **Separate Databases** - Complete isolation, no risk of cross-product queries
3. **Identical Schema** - Both databases use the same SQLAlchemy models (shared package)
4. **No Shared Tables** - Each product is completely independent (no shared data)

### Database Naming Conventions

**Development:**
```
bestays_db_dev       # Bestays development database
realestate_db_dev    # Real Estate development database
```

**Production:**
```
bestays_db           # Bestays production database
realestate_db        # Real Estate production database
```

**Pattern:** `{product}_db[_environment]`

### Data Isolation Guarantees

**Physical Isolation:**
- Separate PostgreSQL databases (namespace isolation)
- No foreign keys across databases (impossible to reference)
- No shared tables or views

**Application Isolation:**
- Each FastAPI app connects to ONE database only
- Connection string configured per product via environment variables
- No application code can accidentally query the wrong database

**User Isolation:**
- Each product has its own `users` table
- Separate Clerk projects (different authentication realms)
- User IDs are product-scoped (no cross-product user references)

**Risk Mitigation:**
- ❌ **Cannot happen:** Cross-product queries (databases are separate)
- ❌ **Cannot happen:** Shared user accounts (Clerk projects are separate)
- ❌ **Cannot happen:** Data leakage via JOIN (no foreign keys across databases)

### Product-Specific vs Shared Tables

**All Tables are Product-Specific (No Shared Tables):**

Both products have identical schema structure, but completely separate data:

| Table | Bestays Content | Real Estate Content | Shared? |
|-------|-----------------|---------------------|---------|
| `users` | Bestays users (Clerk: sacred-mayfly-55) | Real Estate users (Clerk: pleasant-gnu-25) | ❌ No |
| `properties` | Rental properties | High-value properties | ❌ No |
| `conversations` | Bestays chat history | Real Estate chat history | ❌ No |
| `messages` | Bestays chat messages | Real Estate chat messages | ❌ No |
| `faq_documents` | Rental FAQs | Real Estate FAQs | ❌ No |
| `faq_embeddings` | Rental FAQ vectors | Real Estate FAQ vectors | ❌ No |
| `chat_prompts` | Bestays system prompts | Real Estate system prompts | ❌ No |
| `chat_tools` | Bestays tool config | Real Estate tool config | ❌ No |

**Why No Shared Tables?**
- US-018 requirement: "separate user bases" → no shared authentication
- Complete data isolation required for white-label model
- Simpler to sell products independently if all data is isolated

---

## Connection Configuration

### Python Code Examples (Pydantic Settings)

**Shared Settings Base Class** (`packages/shared-config/src/database.py`):

```python
"""Shared database configuration patterns for all products."""

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Shared database configuration pattern.

    Each product app imports this and configures via environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

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
            # Convert postgresql:// to postgresql+asyncpg://
            if v.startswith("postgresql://"):
                v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif not v.startswith("postgresql+asyncpg://"):
                msg = "DATABASE_URL must use postgresql+asyncpg:// scheme"
                raise ValueError(msg)
        return str(v)
```

**Product-Specific Configuration** (`apps/bestays-api/app/config.py`):

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

    # Frontend URL (for CORS)
    FRONTEND_URL: str = "http://localhost:5273"

    # Redis (with product prefix)
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_KEY_PREFIX: str = "bestays:"


# Singleton instance
settings = BestaysSettings()
```

**Product-Specific Configuration** (`apps/realestate-api/app/config.py`):

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

    # Frontend URL (for CORS)
    FRONTEND_URL: str = "http://localhost:5274"

    # Redis (with product prefix)
    REDIS_URL: str = "redis://localhost:6379/1"
    REDIS_KEY_PREFIX: str = "realestate:"


# Singleton instance
settings = RealEstateSettings()
```

### Environment Variable Patterns

**Bestays Development** (`.env.development`):

```bash
# Product Identification
APP_NAME=Bestays
PRODUCT_ID=bestays

# Database (separate database on same PostgreSQL instance)
DATABASE_URL=postgresql+asyncpg://bestays_user:bestays_password@localhost:5432/bestays_db_dev

# Clerk Authentication (Bestays Clerk Project)
CLERK_SECRET_KEY=sk_test_vGrRuTLW1SdS2uQlDbv4l2T2WHpTk9IoervBmG9Vit
CLERK_PUBLISHABLE_KEY=pk_test_c2FjcmVkLW1heWZseS01NS5jbGVyay5hY2NvdW50cy5kZXYk
CLERK_WEBHOOK_SECRET=whsec_bestays_dev

# Frontend
FRONTEND_URL=http://localhost:5273

# Redis (DB 0 for Bestays)
REDIS_URL=redis://localhost:6379/0
REDIS_KEY_PREFIX=bestays:

# OpenAI (shared or separate API key)
OPENAI_API_KEY=sk-proj-...
```

**Real Estate Development** (`.env.development`):

```bash
# Product Identification
APP_NAME=Best Real Estate
PRODUCT_ID=realestate

# Database (separate database on same PostgreSQL instance)
DATABASE_URL=postgresql+asyncpg://realestate_user:realestate_password@localhost:5432/realestate_db_dev

# Clerk Authentication (Real Estate Clerk Project)
CLERK_SECRET_KEY=sk_test_GBG0pHIE015mIkiHfrpeOS4mi1hqNSm0uBUdlexgxS
CLERK_PUBLISHABLE_KEY=pk_test_cGxlYXNhbnQtZ251LTI1LmNsZXJrLmFjY291bnRzLmRldiQ
CLERK_WEBHOOK_SECRET=whsec_realestate_dev

# Frontend
FRONTEND_URL=http://localhost:5274

# Redis (DB 1 for Real Estate)
REDIS_URL=redis://localhost:6379/1
REDIS_KEY_PREFIX=realestate:

# OpenAI (shared or separate API key)
OPENAI_API_KEY=sk-proj-...
```

### Connection Pooling Strategy

**Shared Database Connection Module** (`packages/shared-db/src/database.py`):

```python
"""Shared database connection setup for all products."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    def dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def create_database_engine(settings):
    """Create async engine with product-specific connection pooling.

    Args:
        settings: Product-specific settings (BestaysSettings or RealEstateSettings)

    Returns:
        AsyncEngine: Configured SQLAlchemy async engine
    """
    return create_async_engine(
        str(settings.DATABASE_URL),
        echo=settings.DATABASE_ECHO,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
        future=True,
    )


def create_session_factory(engine):
    """Create async session factory.

    Args:
        engine: SQLAlchemy async engine

    Returns:
        async_sessionmaker: Session factory for dependency injection
    """
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def get_db(session_factory) -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions.

    Usage:
        @app.get("/items")
        async def read_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
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

**Product App Initialization** (`apps/bestays-api/app/main.py`):

```python
"""Bestays API application."""

from fastapi import FastAPI
from shared_db.database import create_database_engine, create_session_factory

from app.config import settings

# Create product-specific engine and session factory
engine = create_database_engine(settings)
session_factory = create_session_factory(engine)

app = FastAPI(title=settings.APP_NAME)

# Dependency injection for routes
from functools import partial
from shared_db.database import get_db

get_bestays_db = partial(get_db, session_factory)

# Use in routes:
# @app.get("/users")
# async def list_users(db: AsyncSession = Depends(get_bestays_db)):
#     ...
```

### SQLAlchemy Async Engine Setup

**Connection Pool Configuration:**

```python
# Development (light load)
DATABASE_POOL_SIZE = 10
DATABASE_MAX_OVERFLOW = 20
DATABASE_POOL_PRE_PING = True  # Check connection health before use

# Production (high load)
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 40
DATABASE_POOL_PRE_PING = True
```

**Why These Values:**
- `pool_size=10` - Number of persistent connections kept open
- `max_overflow=20` - Additional connections created on demand
- `pool_pre_ping=True` - Prevents "connection closed" errors (health check before use)

**Pool Isolation:**
- Each product app has its own connection pool
- No shared connections between products
- Each pool connects to a different database

---

## Migration Strategy

### Alembic Monorepo Structure

**Recommended Structure:**

```
apps/
├── bestays-api/
│   ├── alembic/
│   │   ├── versions/          # Bestays migrations
│   │   ├── env.py             # Bestays Alembic environment
│   │   └── script.py.mako
│   ├── alembic.ini             # Bestays Alembic config
│   └── app/
│       └── ...
│
├── realestate-api/
│   ├── alembic/
│   │   ├── versions/          # Real Estate migrations
│   │   ├── env.py             # Real Estate Alembic environment
│   │   └── script.py.mako
│   ├── alembic.ini             # Real Estate Alembic config
│   └── app/
│       └── ...
│
└── shared-db/                  # Shared SQLAlchemy models
    └── src/
        └── models/
            ├── __init__.py
            ├── user.py
            ├── property.py
            ├── chat.py
            ├── faq.py
            └── ...
```

**Key Insight:** Each product has its own Alembic configuration, but imports shared models from `shared-db` package.

### Shared vs Product-Specific Migrations

**Approach: Duplicate Migration Files (Recommended for Simplicity)**

**Why Duplicate:**
1. **Simplicity** - Each product is independently deployable
2. **Safety** - No risk of applying wrong migrations to wrong database
3. **Flexibility** - Products can diverge in schema if needed later
4. **Clear ownership** - Each migration file belongs to one product

**Migration Creation Workflow:**

```bash
# Step 1: Create migration for Bestays
cd apps/bestays-api
alembic revision --autogenerate -m "add_property_listing_table"

# Step 2: Review generated migration
# File: apps/bestays-api/alembic/versions/20251107_add_property_listing_table.py

# Step 3: Copy migration to Real Estate
cp alembic/versions/20251107_add_property_listing_table.py \
   ../realestate-api/alembic/versions/20251107_add_property_listing_table.py

# Step 4: Update Real Estate migration revision ID
# Edit ../realestate-api/alembic/versions/20251107_add_property_listing_table.py
# Change: revision = "abc123" → revision = "def456" (new unique ID)

# Step 5: Apply migrations to both databases
cd apps/bestays-api && alembic upgrade head
cd apps/realestate-api && alembic upgrade head
```

**Automation Script** (`.scripts/sync-migrations.sh`):

```bash
#!/bin/bash
# Sync migrations from Bestays to Real Estate

set -e

BESTAYS_MIGRATIONS="apps/bestays-api/alembic/versions"
REALESTATE_MIGRATIONS="apps/realestate-api/alembic/versions"

# Find latest Bestays migration
LATEST=$(ls -t $BESTAYS_MIGRATIONS/*.py | head -1)
FILENAME=$(basename $LATEST)

echo "Syncing migration: $FILENAME"

# Copy to Real Estate
cp $LATEST $REALESTATE_MIGRATIONS/$FILENAME

# Generate new revision ID
NEW_REV=$(uuidgen | tr '[:upper:]' '[:lower:]' | cut -d- -f1)

# Update revision ID in Real Estate migration
sed -i '' "s/revision = '[^']*'/revision = '$NEW_REV'/" $REALESTATE_MIGRATIONS/$FILENAME

echo "✅ Migration synced. New Real Estate revision: $NEW_REV"
echo "⚠️  Review the migration before applying!"
```

### Migration Versioning Approach

**Pattern: Date-based Prefixes + Descriptive Names**

```
20251107_1423-add_property_listing_table.py
20251107_1445-add_property_amenities_jsonb.py
20251108_0900-create_chat_conversations_table.py
```

**Alembic Configuration** (`alembic.ini`):

```ini
[alembic]
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s
```

**Benefits:**
- Chronological ordering (easy to see history)
- Descriptive names (understand purpose without opening file)
- Revision IDs still present (Alembic dependency tracking)

### Testing Strategy for Migrations

**1. Unit Tests (SQLite In-Memory):**

```python
"""Test migrations with pytest-alembic."""

import pytest
from pytest_alembic import MigrationContext
from sqlalchemy import text


def test_migration_up_down(alembic_runner):
    """Test migration can be applied and rolled back."""
    alembic_runner.migrate_up_to("head")
    alembic_runner.migrate_down_to("base")


def test_migration_creates_property_table(alembic_engine, alembic_runner):
    """Test migration creates property table with correct schema."""
    alembic_runner.migrate_up_to("20251107_add_property_listing_table")

    with alembic_engine.connect() as conn:
        result = conn.execute(text(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_name = 'properties'"
        ))
        columns = {row[0]: row[1] for row in result}

        assert "id" in columns
        assert "title" in columns
        assert columns["id"] == "uuid"
        assert columns["title"] == "character varying"
```

**2. Integration Tests (Against Real PostgreSQL):**

```python
"""Integration tests for migrations."""

import pytest
from sqlalchemy import create_engine, text


@pytest.fixture
def test_postgres_db():
    """Create temporary PostgreSQL database for testing."""
    # Use test-specific database: bestays_db_test
    engine = create_engine("postgresql://user:pass@localhost:5432/bestays_db_test")
    yield engine
    engine.dispose()


def test_migration_against_postgres(test_postgres_db):
    """Test migration against actual PostgreSQL database."""
    # Run Alembic migrations
    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", str(test_postgres_db.url))

    command.upgrade(alembic_cfg, "head")

    # Verify schema
    with test_postgres_db.connect() as conn:
        result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
        tables = [row[0] for row in result]

        assert "users" in tables
        assert "properties" in tables
        assert "conversations" in tables
```

**3. Pre-Production Validation:**

```bash
#!/bin/bash
# Validate migrations before production deployment

set -e

echo "🔍 Validating migrations..."

# Step 1: Run migrations on staging database
cd apps/bestays-api
alembic upgrade head --sql > /tmp/bestays_migration.sql

# Step 2: Review SQL output (manual step)
echo "📄 Review SQL in /tmp/bestays_migration.sql"
echo "Press Enter to continue..."
read

# Step 3: Apply migrations to staging
alembic upgrade head

# Step 4: Run smoke tests
pytest tests/integration/test_migrations.py

echo "✅ Migrations validated successfully"
```

### Rollback Strategy

**1. Alembic Downgrade:**

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade abc123

# Rollback all migrations
alembic downgrade base
```

**2. Database Backup Before Migration:**

```bash
#!/bin/bash
# Backup database before migration

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="bestays_db_backup_${TIMESTAMP}.sql"

# Backup database
pg_dump -h localhost -U bestays_user bestays_db > $BACKUP_FILE

echo "✅ Database backed up to $BACKUP_FILE"

# Apply migrations
alembic upgrade head

# If migration fails, restore from backup:
# psql -h localhost -U bestays_user bestays_db < $BACKUP_FILE
```

**3. Blue-Green Deployment for Zero-Downtime:**

```bash
# Scenario: Production migration with zero downtime

# Step 1: Create new database (green)
createdb -h localhost -U postgres bestays_db_green

# Step 2: Copy current production data (blue → green)
pg_dump bestays_db | psql bestays_db_green

# Step 3: Apply migrations to green database
alembic upgrade head

# Step 4: Test green database
pytest tests/integration/ --database=bestays_db_green

# Step 5: Switch application to green database (update DATABASE_URL)
# Step 6: Monitor for errors
# Step 7: Drop blue database after 24h if all good
```

---

## Development Workflow

### Local Setup (Docker Compose)

**Updated `docker-compose.dev.yml`:**

```yaml
services:
  # PostgreSQL Instance (Single Container, Multiple Databases)
  postgres:
    image: postgres:16-alpine
    container_name: bestays-postgres-dev
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres_master_password
      PGDATA: /var/lib/postgresql/data/pgdata
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
    restart: unless-stopped

  # Bestays API
  bestays-api:
    build:
      context: .
      dockerfile: docker/bestays-api/Dockerfile.dev
    container_name: bestays-api-dev
    environment:
      # Product identification
      APP_NAME: Bestays
      PRODUCT_ID: bestays

      # Database (bestays_db)
      DATABASE_URL: postgresql+asyncpg://bestays_user:bestays_password@postgres:5432/bestays_db_dev

      # Clerk (Bestays project)
      CLERK_SECRET_KEY: sk_test_vGrRuTLW1SdS2uQlDbv4l2T2WHpTk9IoervBmG9Vit
      CLERK_PUBLISHABLE_KEY: pk_test_c2FjcmVkLW1heWZseS01NS5jbGVyay5hY2NvdW50cy5kZXYk

      # Redis (DB 0)
      REDIS_URL: redis://redis:6379/0
      REDIS_KEY_PREFIX: bestays:

      # Frontend URL
      FRONTEND_URL: http://localhost:5273
    ports:
      - "8101:8000"
    volumes:
      - ./apps/bestays-api:/app:delegated
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - bestays-network
    restart: unless-stopped

  # Real Estate API
  realestate-api:
    build:
      context: .
      dockerfile: docker/realestate-api/Dockerfile.dev
    container_name: realestate-api-dev
    environment:
      # Product identification
      APP_NAME: Best Real Estate
      PRODUCT_ID: realestate

      # Database (realestate_db)
      DATABASE_URL: postgresql+asyncpg://realestate_user:realestate_password@postgres:5432/realestate_db_dev

      # Clerk (Real Estate project)
      CLERK_SECRET_KEY: sk_test_GBG0pHIE015mIkiHfrpeOS4mi1hqNSm0uBUdlexgxS
      CLERK_PUBLISHABLE_KEY: pk_test_cGxlYXNhbnQtZ251LTI1LmNsZXJrLmFjY291bnRzLmRldiQ

      # Redis (DB 1)
      REDIS_URL: redis://redis:6379/1
      REDIS_KEY_PREFIX: realestate:

      # Frontend URL
      FRONTEND_URL: http://localhost:5274
    ports:
      - "8102:8000"
    volumes:
      - ./apps/realestate-api:/app:delegated
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - bestays-network
    restart: unless-stopped

  # Redis (Shared, Multiple Databases)
  redis:
    image: redis:7-alpine
    container_name: bestays-redis-dev
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - bestays-network
    restart: unless-stopped

networks:
  bestays-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

**PostgreSQL Initialization Script** (`docker/postgres/init-multi-db.sql`):

```sql
-- Create databases and users for both products

-- ============================================================================
-- Bestays Database
-- ============================================================================
CREATE DATABASE bestays_db_dev;
CREATE USER bestays_user WITH PASSWORD 'bestays_password';
GRANT ALL PRIVILEGES ON DATABASE bestays_db_dev TO bestays_user;

-- Connect to bestays_db_dev and grant schema permissions
\c bestays_db_dev
GRANT ALL ON SCHEMA public TO bestays_user;

-- Enable pgvector extension (for FAQ RAG)
CREATE EXTENSION IF NOT EXISTS pgvector;

-- ============================================================================
-- Real Estate Database
-- ============================================================================
\c postgres
CREATE DATABASE realestate_db_dev;
CREATE USER realestate_user WITH PASSWORD 'realestate_password';
GRANT ALL PRIVILEGES ON DATABASE realestate_db_dev TO realestate_user;

-- Connect to realestate_db_dev and grant schema permissions
\c realestate_db_dev
GRANT ALL ON SCHEMA public TO realestate_user;

-- Enable pgvector extension (for FAQ RAG)
CREATE EXTENSION IF NOT EXISTS pgvector;
```

### Database Seeding Approach

**Shared Seed Data Structure** (`packages/shared-db/seeds/`):

```python
"""Shared seed data utilities."""

from typing import Protocol
from sqlalchemy.ext.asyncio import AsyncSession


class SeederProtocol(Protocol):
    """Protocol for seed data functions."""

    async def seed(self, db: AsyncSession, product_id: str) -> None:
        """Seed data for a specific product."""
        ...


async def seed_users(db: AsyncSession, product_id: str) -> None:
    """Seed test users for development."""
    from shared_db.models import User

    # Product-specific test users
    test_users = {
        "bestays": [
            User(
                clerk_user_id="user_bestays_admin",
                email="admin.claudecode@bestays.app",
                role="admin",
            ),
            User(
                clerk_user_id="user_bestays_agent",
                email="agent.claudecode@bestays.app",
                role="agent",
            ),
            User(
                clerk_user_id="user_bestays_user",
                email="user.claudecode@bestays.app",
                role="user",
            ),
        ],
        "realestate": [
            User(
                clerk_user_id="user_realestate_admin",
                email="admin.claudecode@realestate.dev",
                role="admin",
            ),
            User(
                clerk_user_id="user_realestate_agent",
                email="agent.claudecode@realestate.dev",
                role="agent",
            ),
            User(
                clerk_user_id="user_realestate_user",
                email="user.claudecode@realestate.dev",
                role="user",
            ),
        ],
    }

    for user in test_users.get(product_id, []):
        db.add(user)

    await db.commit()
```

**Product-Specific Seed Script** (`apps/bestays-api/scripts/seed_dev_data.py`):

```python
"""Seed development data for Bestays."""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from shared_db.seeds import seed_users


async def main():
    """Seed all development data."""
    engine = create_async_engine(str(settings.DATABASE_URL))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        print(f"🌱 Seeding data for {settings.PRODUCT_ID}...")

        await seed_users(db, settings.PRODUCT_ID)
        # await seed_properties(db, settings.PRODUCT_ID)
        # await seed_faq(db, settings.PRODUCT_ID)

        print("✅ Seed data complete!")


if __name__ == "__main__":
    asyncio.run(main())
```

### Reset Scripts for Development

**Reset Bestays Database:**

```bash
#!/bin/bash
# reset-bestays-db.sh

set -e

echo "⚠️  WARNING: This will delete all Bestays data!"
read -p "Are you sure? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

cd apps/bestays-api

# Downgrade all migrations
alembic downgrade base

# Upgrade to latest
alembic upgrade head

# Seed development data
python scripts/seed_dev_data.py

echo "✅ Bestays database reset complete!"
```

**Reset Real Estate Database:**

```bash
#!/bin/bash
# reset-realestate-db.sh

set -e

echo "⚠️  WARNING: This will delete all Real Estate data!"
read -p "Are you sure? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

cd apps/realestate-api

# Downgrade all migrations
alembic downgrade base

# Upgrade to latest
alembic upgrade head

# Seed development data
python scripts/seed_dev_data.py

echo "✅ Real Estate database reset complete!"
```

---

## Testing Strategy

### Unit Tests: SQLite In-Memory (Current Approach)

**Pattern: Maintain Current Approach (No PostgreSQL Needed)**

```python
"""Test database setup for unit tests."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from shared_db.database import Base


@pytest.fixture
def db_engine():
    """Create in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(db_engine):
    """Create database session for testing."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()


def test_create_user(db_session):
    """Test user creation."""
    from shared_db.models import User

    user = User(
        clerk_user_id="user_test_123",
        email="test@example.com",
        role="user",
    )
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.email == "test@example.com"
```

**Why SQLite In-Memory:**
- ✅ **Fast** - No network overhead, no PostgreSQL startup time
- ✅ **Isolated** - Each test gets fresh database
- ✅ **Simple** - No PostgreSQL dependency for CI/CD
- ✅ **Current pattern** - Already used in existing codebase

### Integration Tests: Against Real PostgreSQL

**Pattern: Test-Specific Databases**

```python
"""Integration tests against PostgreSQL."""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from shared_db.database import Base


@pytest.fixture
async def test_postgres_engine(request):
    """Create test-specific PostgreSQL database."""
    product_id = request.param  # "bestays" or "realestate"

    # Use test-specific database
    test_db_url = f"postgresql+asyncpg://postgres:postgres@localhost:5432/{product_id}_db_test"

    engine = create_async_engine(test_db_url)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.mark.asyncio
@pytest.mark.parametrize("test_postgres_engine", ["bestays"], indirect=True)
async def test_create_user_postgres(test_postgres_engine):
    """Test user creation against PostgreSQL."""
    from shared_db.models import User

    async_session = sessionmaker(
        test_postgres_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        user = User(
            clerk_user_id="user_test_postgres",
            email="test@example.com",
            role="user",
        )
        session.add(user)
        await session.commit()

        assert user.id is not None
```

### E2E Tests: Playwright + Test Databases

**Pattern: Dedicated Test Environment**

```typescript
// tests/e2e/bestays/auth.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Bestays Authentication', () => {
  test.beforeAll(async () => {
    // Reset test database
    await exec('bash scripts/reset-bestays-test-db.sh');
  });

  test('user can sign up and log in', async ({ page }) => {
    await page.goto('http://localhost:5273');

    // Click sign up
    await page.click('text=Sign Up');

    // Fill form (Clerk test mode)
    await page.fill('input[name="email"]', 'newuser@bestays.test');
    await page.fill('input[name="password"]', 'TestPassword123!');
    await page.click('button:has-text("Sign Up")');

    // Verify redirect to dashboard
    await expect(page).toHaveURL('http://localhost:5273/dashboard');
  });
});
```

**Test Database Setup:**

```bash
#!/bin/bash
# scripts/reset-bestays-test-db.sh

set -e

# Drop and recreate test database
psql -U postgres -c "DROP DATABASE IF EXISTS bestays_db_test;"
psql -U postgres -c "CREATE DATABASE bestays_db_test OWNER bestays_user;"

# Run migrations
cd apps/bestays-api
export DATABASE_URL=postgresql+asyncpg://bestays_user:bestays_password@localhost:5432/bestays_db_test
alembic upgrade head

# Seed test data
python scripts/seed_test_data.py

echo "✅ Test database ready"
```

### Test Data Management

**Shared Test Data Fixtures** (`packages/shared-db/tests/fixtures.py`):

```python
"""Shared test data fixtures."""

from shared_db.models import User, Property


def create_test_user(
    clerk_user_id: str = "user_test",
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
```

### Test Database Cleanup

**Pattern: Automatic Cleanup After Each Test**

```python
"""Test cleanup utilities."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def clean_db(db_session: AsyncSession):
    """Clean database after each test."""
    yield db_session

    # Rollback any uncommitted changes
    await db_session.rollback()

    # Clean all tables (order matters for foreign keys)
    from shared_db.models import Base
    for table in reversed(Base.metadata.sorted_tables):
        await db_session.execute(table.delete())

    await db_session.commit()
```

---

## Production Deployment (Simplicity First)

### Docker Compose Orchestration (Existing Pattern)

**Production `docker-compose.prod.yml`:**

```yaml
services:
  # PostgreSQL Instance (One Container, Two Databases)
  postgres:
    image: postgres:16-alpine
    container_name: bestays-postgres-prod
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_MASTER_PASSWORD}
      PGDATA: /var/lib/postgresql/data/pgdata
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init-multi-db-prod.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 5
    networks:
      - bestays-network
    restart: always

  # Bestays API (Production)
  bestays-api:
    build:
      context: .
      dockerfile: docker/bestays-api/Dockerfile.prod
    container_name: bestays-api-prod
    environment:
      APP_NAME: Bestays
      PRODUCT_ID: bestays
      ENVIRONMENT: production
      DATABASE_URL: postgresql+asyncpg://bestays_user:${BESTAYS_DB_PASSWORD}@postgres:5432/bestays_db
      CLERK_SECRET_KEY: ${BESTAYS_CLERK_SECRET_KEY}
      CLERK_PUBLISHABLE_KEY: ${BESTAYS_CLERK_PUBLISHABLE_KEY}
      REDIS_URL: redis://redis:6379/0
      REDIS_KEY_PREFIX: bestays:
      FRONTEND_URL: https://bestays.app
    ports:
      - "8101:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - bestays-network
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G

  # Real Estate API (Production)
  realestate-api:
    build:
      context: .
      dockerfile: docker/realestate-api/Dockerfile.prod
    container_name: realestate-api-prod
    environment:
      APP_NAME: Best Real Estate
      PRODUCT_ID: realestate
      ENVIRONMENT: production
      DATABASE_URL: postgresql+asyncpg://realestate_user:${REALESTATE_DB_PASSWORD}@postgres:5432/realestate_db
      CLERK_SECRET_KEY: ${REALESTATE_CLERK_SECRET_KEY}
      CLERK_PUBLISHABLE_KEY: ${REALESTATE_CLERK_PUBLISHABLE_KEY}
      REDIS_URL: redis://redis:6379/1
      REDIS_KEY_PREFIX: realestate:
      FRONTEND_URL: https://realestate.app
    ports:
      - "8102:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - bestays-network
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G

  # Redis (Shared, Multiple Databases)
  redis:
    image: redis:7-alpine
    container_name: bestays-redis-prod
    command: >
      redis-server
      --maxmemory 2gb
      --maxmemory-policy allkeys-lru
      --appendonly yes
      --requirepass ${REDIS_PASSWORD}
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5
    networks:
      - bestays-network
    restart: always

networks:
  bestays-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

### PostgreSQL Container Strategy

**Recommendation: One Container, Two Databases (Simple and Cost-Effective)**

**Why One Container:**
1. ✅ **Simplicity** - Single PostgreSQL instance to manage
2. ✅ **Cost-effective** - No need for multiple VPS instances
3. ✅ **Resource efficiency** - Shared memory, shared CPU
4. ✅ **Easy backups** - Backup entire PostgreSQL instance

**Why Two Databases (Not Two Containers):**
1. ✅ **Data isolation** - Complete separation at database level
2. ✅ **Simple connection** - Just change database name in URL
3. ✅ **Same PostgreSQL version** - No version mismatch issues
4. ✅ **Easy migration** - Can move to separate containers later if needed

**When to Move to Two Containers:**
- High traffic (10,000+ concurrent users per product)
- Different PostgreSQL configurations needed per product
- Independent scaling required
- Separate VPS instances for each product

### Environment Variable Management

**Production `.env.production` (Git-ignored):**

```bash
# PostgreSQL Master Password
POSTGRES_MASTER_PASSWORD=<strong-master-password>

# Bestays Database
BESTAYS_DB_PASSWORD=<strong-bestays-password>
BESTAYS_CLERK_SECRET_KEY=sk_live_<bestays-production-key>
BESTAYS_CLERK_PUBLISHABLE_KEY=pk_live_<bestays-production-key>

# Real Estate Database
REALESTATE_DB_PASSWORD=<strong-realestate-password>
REALESTATE_CLERK_SECRET_KEY=sk_live_<realestate-production-key>
REALESTATE_CLERK_PUBLISHABLE_KEY=pk_live_<realestate-production-key>

# Redis
REDIS_PASSWORD=<strong-redis-password>

# OpenAI (shared or separate)
OPENAI_API_KEY=sk-proj-<production-key>
```

**Secrets Management (Recommended):**

```bash
# Use Docker secrets for sensitive values
docker secret create postgres_master_password <password-file>
docker secret create bestays_db_password <password-file>
docker secret create realestate_db_password <password-file>

# Update docker-compose.prod.yml to use secrets:
services:
  postgres:
    secrets:
      - postgres_master_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_master_password
```

### Backup and Restore Per Product

**Backup Bestays Database:**

```bash
#!/bin/bash
# backup-bestays-db.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/bestays"
BACKUP_FILE="${BACKUP_DIR}/bestays_db_${TIMESTAMP}.sql"

mkdir -p $BACKUP_DIR

# Backup database (with compression)
docker exec bestays-postgres-prod pg_dump \
  -U postgres \
  -d bestays_db \
  --format=custom \
  --file=/tmp/backup.dump

# Copy backup out of container
docker cp bestays-postgres-prod:/tmp/backup.dump $BACKUP_FILE

# Compress
gzip $BACKUP_FILE

echo "✅ Backup saved to ${BACKUP_FILE}.gz"

# Upload to S3 (optional)
# aws s3 cp ${BACKUP_FILE}.gz s3://bestays-backups/
```

**Restore Bestays Database:**

```bash
#!/bin/bash
# restore-bestays-db.sh

if [ -z "$1" ]; then
  echo "Usage: ./restore-bestays-db.sh <backup-file>"
  exit 1
fi

BACKUP_FILE=$1

echo "⚠️  WARNING: This will overwrite the Bestays database!"
read -p "Are you sure? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  echo "Aborted."
  exit 0
fi

# Uncompress
gunzip -k $BACKUP_FILE

# Copy backup into container
docker cp ${BACKUP_FILE%.gz} bestays-postgres-prod:/tmp/restore.dump

# Drop existing database
docker exec bestays-postgres-prod psql \
  -U postgres \
  -c "DROP DATABASE IF EXISTS bestays_db;"

# Create new database
docker exec bestays-postgres-prod psql \
  -U postgres \
  -c "CREATE DATABASE bestays_db OWNER bestays_user;"

# Restore from backup
docker exec bestays-postgres-prod pg_restore \
  -U postgres \
  -d bestays_db \
  --format=custom \
  /tmp/restore.dump

echo "✅ Database restored successfully"
```

**Automated Daily Backups (Cron Job):**

```bash
# /etc/cron.d/bestays-backups

# Backup Bestays database daily at 2 AM
0 2 * * * /opt/bestays/scripts/backup-bestays-db.sh

# Backup Real Estate database daily at 3 AM
0 3 * * * /opt/bestays/scripts/backup-realestate-db.sh

# Clean old backups (keep last 30 days)
0 4 * * * find /backups/bestays -name "*.gz" -mtime +30 -delete
0 4 * * * find /backups/realestate -name "*.gz" -mtime +30 -delete
```

### Monitoring and Health Checks

**Database Health Check Endpoint** (`apps/bestays-api/app/api/health.py`):

```python
"""Health check endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "ok"}


@router.get("/health/db")
async def database_health_check(db: AsyncSession = Depends(get_db)):
    """Database connectivity health check."""
    try:
        # Simple query to check database connection
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "error": str(e)}
```

**Docker Health Check:**

```yaml
# In docker-compose.prod.yml

services:
  bestays-api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health/db"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

**Monitoring Script (Optional - Prometheus Metrics):**

```python
"""Prometheus metrics for database monitoring."""

from prometheus_client import Counter, Histogram, Gauge
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Metrics
db_connections_active = Gauge('db_connections_active', 'Active database connections')
db_connections_total = Counter('db_connections_total', 'Total database connections')
db_query_duration = Histogram('db_query_duration_seconds', 'Database query duration')


@event.listens_for(Engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Track database connections."""
    db_connections_total.inc()
    db_connections_active.inc()


@event.listens_for(Engine, "close")
def receive_close(dbapi_conn, connection_record):
    """Track connection closures."""
    db_connections_active.dec()
```

---

## Migration from Current State

### Step-by-Step Migration Plan

**Phase 1: Prepare Shared Database Package (Week 1)**

```bash
# Step 1: Create shared-db package structure
mkdir -p packages/shared-db/src/models
mkdir -p packages/shared-db/src/seeds
mkdir -p packages/shared-db/tests

# Step 2: Move existing models to shared package
cp apps/server/src/server/models/*.py packages/shared-db/src/models/

# Step 3: Update imports in shared models
# Change: from server.core.database import Base
# To: from shared_db.database import Base

# Step 4: Create pyproject.toml for shared-db package
cat > packages/shared-db/pyproject.toml << EOF
[project]
name = "shared-db"
version = "0.1.0"
dependencies = [
    "sqlalchemy>=2.0.0",
    "asyncpg>=0.29.0",
    "pydantic>=2.6.0",
]
EOF

# Step 5: Install shared-db in existing server
cd apps/server
pip install -e ../../packages/shared-db
```

**Phase 2: Duplicate Bestays App (Week 1-2)**

```bash
# Step 1: Copy entire server directory
cp -r apps/server apps/bestays-api

# Step 2: Update imports in bestays-api
# Change: from server.* import *
# To: from shared_db.* import *

# Step 3: Update configuration
# Edit apps/bestays-api/app/config.py
# Add: PRODUCT_ID = "bestays"

# Step 4: Test Bestays API still works
cd apps/bestays-api
pytest tests/

# Step 5: Update docker-compose.dev.yml to use bestays-api
# Update service name: server → bestays-api
# Update build context: dockerfile: docker/bestays-api/Dockerfile.dev
```

**Phase 3: Create Real Estate App (Week 2)**

```bash
# Step 1: Copy Bestays app
cp -r apps/bestays-api apps/realestate-api

# Step 2: Update configuration
# Edit apps/realestate-api/app/config.py
# Change: PRODUCT_ID = "realestate"
# Change: DATABASE_URL = postgresql+asyncpg://...realestate_db
# Change: CLERK_SECRET_KEY = sk_test_GBG0pHIE015mIkiHfrpeOS4mi1hqNSm0uBUdlexgxS

# Step 3: Update Alembic config
# Edit apps/realestate-api/alembic.ini
# Update script_location if needed

# Step 4: Copy migrations from Bestays
cp -r apps/bestays-api/alembic/versions/* apps/realestate-api/alembic/versions/

# Step 5: Update migration revision IDs
# Run: python scripts/update_migration_revisions.py apps/realestate-api/alembic/versions/
```

**Phase 4: Set Up Two Databases (Week 2)**

```bash
# Step 1: Create PostgreSQL init script
cat > docker/postgres/init-multi-db.sql << 'EOF'
-- Create Bestays database
CREATE DATABASE bestays_db_dev;
CREATE USER bestays_user WITH PASSWORD 'bestays_password';
GRANT ALL PRIVILEGES ON DATABASE bestays_db_dev TO bestays_user;

\c bestays_db_dev
GRANT ALL ON SCHEMA public TO bestays_user;
CREATE EXTENSION IF NOT EXISTS pgvector;

-- Create Real Estate database
\c postgres
CREATE DATABASE realestate_db_dev;
CREATE USER realestate_user WITH PASSWORD 'realestate_password';
GRANT ALL PRIVILEGES ON DATABASE realestate_db_dev TO realestate_user;

\c realestate_db_dev
GRANT ALL ON SCHEMA public TO realestate_user;
CREATE EXTENSION IF NOT EXISTS pgvector;
EOF

# Step 2: Update docker-compose.dev.yml
# Add: realestate-api service
# Update: postgres service to use init-multi-db.sql

# Step 3: Restart Docker Compose
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d

# Step 4: Run migrations for both databases
cd apps/bestays-api && alembic upgrade head
cd apps/realestate-api && alembic upgrade head
```

**Phase 5: Test and Validate (Week 3)**

```bash
# Step 1: Seed both databases
cd apps/bestays-api && python scripts/seed_dev_data.py
cd apps/realestate-api && python scripts/seed_dev_data.py

# Step 2: Test Bestays API
curl http://localhost:8101/api/health/db
# Expected: {"status": "ok", "database": "connected"}

# Step 3: Test Real Estate API
curl http://localhost:8102/api/health/db
# Expected: {"status": "ok", "database": "connected"}

# Step 4: Test authentication with separate Clerk projects
# Login to Bestays: user.claudecode@bestays.app
# Login to Real Estate: user.claudecode@realestate.dev

# Step 5: Verify data isolation
# Query Bestays database: should only see Bestays data
# Query Real Estate database: should only see Real Estate data
```

### How to Preserve Existing Bestays Data

**Scenario: Production Bestays already has user data**

**Migration Strategy:**

```bash
#!/bin/bash
# migrate-existing-bestays-to-new-structure.sh

set -e

echo "📦 Migrating existing Bestays data to new structure..."

# Step 1: Backup current production database
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pg_dump -h production-host -U bestays_user bestays_dev > /tmp/bestays_backup_${TIMESTAMP}.sql

# Step 2: Create new database structure
psql -h production-host -U postgres -c "CREATE DATABASE bestays_db;"
psql -h production-host -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE bestays_db TO bestays_user;"

# Step 3: Restore data to new database
psql -h production-host -U bestays_user bestays_db < /tmp/bestays_backup_${TIMESTAMP}.sql

# Step 4: Run any new migrations (if schema changed)
cd apps/bestays-api
export DATABASE_URL=postgresql+asyncpg://bestays_user:password@production-host:5432/bestays_db
alembic upgrade head

# Step 5: Update application configuration
# Update DATABASE_URL in production .env file to point to bestays_db

# Step 6: Restart application
docker-compose -f docker-compose.prod.yml restart bestays-api

echo "✅ Migration complete!"
echo "⚠️  Keep backup at /tmp/bestays_backup_${TIMESTAMP}.sql for 7 days"
```

**Data Validation:**

```python
"""Validate data migration."""

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


async def validate_migration():
    """Verify all data migrated correctly."""

    # Connect to old database
    old_engine = create_async_engine("postgresql+asyncpg://user:pass@host/bestays_dev")
    old_session = sessionmaker(old_engine, class_=AsyncSession)

    # Connect to new database
    new_engine = create_async_engine("postgresql+asyncpg://user:pass@host/bestays_db")
    new_session = sessionmaker(new_engine, class_=AsyncSession)

    # Count users in both databases
    async with old_session() as old_db, new_session() as new_db:
        old_count = await old_db.scalar(select(func.count(User.id)))
        new_count = await new_db.scalar(select(func.count(User.id)))

        print(f"Old database: {old_count} users")
        print(f"New database: {new_count} users")

        if old_count == new_count:
            print("✅ User count matches!")
        else:
            print("❌ User count mismatch! Manual review required.")

    await old_engine.dispose()
    await new_engine.dispose()


asyncio.run(validate_migration())
```

### Risk Mitigation

**Risk 1: Data Loss During Migration**

**Mitigation:**
- ✅ Always backup before migration
- ✅ Validate backups (test restore)
- ✅ Run migration on staging first
- ✅ Keep backups for 30 days after migration

**Risk 2: Downtime During Migration**

**Mitigation:**
- ✅ Use blue-green deployment
- ✅ Run migration during low-traffic hours
- ✅ Keep old database available for rollback
- ✅ Test rollback procedure before production

**Risk 3: Schema Drift Between Products**

**Mitigation:**
- ✅ Use shared SQLAlchemy models package
- ✅ Sync migrations from Bestays to Real Estate
- ✅ Automated migration sync script (`.scripts/sync-migrations.sh`)
- ✅ CI/CD checks for schema consistency

**Risk 4: Connection Errors (Wrong Database)**

**Mitigation:**
- ✅ Environment-based configuration (separate .env files)
- ✅ Product ID in settings (PRODUCT_ID = "bestays")
- ✅ Health check endpoint validates correct database connection
- ✅ Integration tests per product

### Rollback Strategy

**Rollback Plan (If Migration Fails):**

```bash
#!/bin/bash
# rollback-migration.sh

set -e

echo "⚠️  Rolling back to previous state..."

# Step 1: Stop new services
docker-compose -f docker-compose.prod.yml down

# Step 2: Restore old docker-compose configuration
git checkout HEAD^ docker-compose.prod.yml

# Step 3: Restore old database (if needed)
psql -h production-host -U bestays_user bestays_dev < /tmp/bestays_backup_${TIMESTAMP}.sql

# Step 4: Start old services
docker-compose -f docker-compose.prod.yml up -d

echo "✅ Rollback complete!"
echo "System restored to previous state."
```

**Rollback Trigger Criteria:**
- ❌ Migration script errors
- ❌ Data validation fails
- ❌ Application health checks fail
- ❌ User reports of missing data
- ❌ Clerk authentication fails

---

## Trade-offs and Risks

### Pros of Separate Databases Approach

**Data Isolation:**
- ✅ **Complete isolation** - Zero risk of cross-product data leakage
- ✅ **No WHERE tenant_id = ?** - No risk of missing tenant filter in queries
- ✅ **Foreign key enforcement** - Impossible to reference wrong product's data

**Simplicity:**
- ✅ **Easy to understand** - Each product has its own database namespace
- ✅ **Easy to deploy** - Same PostgreSQL instance, different databases
- ✅ **Easy to test** - No complex tenant filtering logic

**Scalability:**
- ✅ **Independent scaling** - Can move products to separate PostgreSQL instances later
- ✅ **Independent backups** - Backup/restore per product
- ✅ **Independent optimization** - Different indexes, vacuum schedules per product

**White-Label Ready:**
- ✅ **Easy to sell** - Each product is completely independent
- ✅ **Easy to extract** - No shared data dependencies
- ✅ **Clear boundaries** - No risk of mixing product data

### Cons of Separate Databases Approach

**Duplicate Data Storage:**
- ❌ **No shared tables** - Same schema stored twice (but US-018 requires this)
- ❌ **Duplicate indexes** - Same indexes on both databases (expected for isolation)

**Migration Overhead:**
- ❌ **Run migrations twice** - One for each database (mitigated by automation script)
- ❌ **Schema sync required** - Manual or scripted sync (mitigated by shared models package)

**Connection Overhead:**
- ❌ **Two connection pools** - One per product (expected, not a real issue)

### Comparison with Multi-Tenant Approach (tenant_id)

**Why We DIDN'T Choose Multi-Tenant:**

| Factor | Separate Databases (Chosen) | Multi-Tenant (Rejected) |
|--------|-----------------------------|-----------------------|
| **Data Isolation** | ✅ Complete (impossible to leak) | ⚠️ Requires WHERE tenant_id filter (risk of missing) |
| **Query Complexity** | ✅ Simple (no filtering needed) | ❌ Every query needs WHERE tenant_id = ? |
| **Risk of Data Leakage** | ✅ Zero risk | ❌ High risk (one missing WHERE clause → leak) |
| **White-Label Readiness** | ✅ Easy to extract and sell | ⚠️ Requires untangling shared tables |
| **Deployment Simplicity** | ✅ Same as multi-tenant | ✅ Same as separate databases |
| **Scalability** | ✅ Can move to separate instances later | ⚠️ Harder to split later |
| **US-018 Requirement** | ✅ Meets "separate user bases" | ❌ Violates isolation requirement |

**User Priority: Simplicity → Separate Databases is SIMPLER**
- No complex tenant filtering logic
- No risk of missing tenant_id in queries
- No Row-Level Security (RLS) policies to manage
- Straightforward connection configuration

### When to Revisit This Decision

**Scenario 1: More Than 5 Products**

If the platform grows to 10+ products, consider:
- Shared authentication (single Clerk project with product metadata)
- Multi-tenant with tenant_id (for cost efficiency)
- Kubernetes with horizontal scaling

**Scenario 2: Shared User Accounts Required**

If business requirements change to allow cross-product user accounts:
- Switch to single Clerk project
- Add product_id to users table
- Implement RBAC per product

**Scenario 3: Extremely High Scale (1M+ users per product)**

If traffic exceeds single PostgreSQL instance capacity:
- Move to separate PostgreSQL instances (different VPS)
- Consider PostgreSQL clustering (Patroni, Citus)
- Consider cloud-managed databases (AWS RDS, Azure Database)

---

## Next Steps for Backend Agent (TASK-003)

**What Backend Needs from This Design:**

### 1. Connection Configuration Pattern

**Use this pattern in backend implementation:**

```python
# apps/{product}-api/app/config.py
from shared_config.database import DatabaseSettings

class BestaysSettings(DatabaseSettings):
    PRODUCT_ID: str = "bestays"
    DATABASE_URL: PostgresDsn  # Set via environment variable
    CLERK_SECRET_KEY: str      # Product-specific Clerk project
```

**Key Insight:** Each product imports `DatabaseSettings` from shared package, but configures via its own `.env` file.

### 2. SQLAlchemy Models Package

**Backend should:**
1. Create `packages/shared-db/src/models/` directory
2. Move all models from `apps/server/src/server/models/` to shared package
3. Update imports in all apps to use `from shared_db.models import User`

**Shared Models:**
- `user.py` (User model with Clerk integration)
- `property.py` (Property listings)
- `chat.py` (Conversations, Messages)
- `faq.py` (FAQ documents, embeddings, categories)
- `chat_config.py` (Chat prompts, tools)
- `audit.py` (Audit logs)

### 3. Alembic Migration Setup

**Backend should:**
1. Keep separate Alembic configurations per product
2. Create migration sync script (`.scripts/sync-migrations.sh`)
3. Document migration workflow in README

**Pattern:**
```bash
# Create migration in Bestays
cd apps/bestays-api
alembic revision --autogenerate -m "add_feature"

# Sync to Real Estate
bash .scripts/sync-migrations.sh
```

### 4. Testing Patterns

**Backend should:**
1. Keep SQLite in-memory for unit tests (current pattern)
2. Add PostgreSQL integration tests (pytest fixtures)
3. Document test database setup

**Example:**
```python
@pytest.fixture
def test_db_engine(product_id):
    """Create test database per product."""
    test_url = f"postgresql+asyncpg://user:pass@localhost/{product_id}_db_test"
    return create_async_engine(test_url)
```

### 5. API Structure

**Backend should consider:**
- Same API routes for both products (`/api/v1/users`, `/api/v1/properties`)
- Product identification via environment variables (not URL path)
- Separate FastAPI apps per product (apps/bestays-api, apps/realestate-api)

**Why Same Routes:**
- Frontend can use same API client library
- Shared API integration tests
- Simpler documentation

### 6. Configuration Examples

**Backend should provide:**
1. `.env.development.example` for Bestays
2. `.env.development.example` for Real Estate
3. Docker Compose with both products
4. Database initialization script

---

## Conclusion

**Recommended Approach: Separate Databases (Option A)**

**Why This Approach:**
1. ✅ **Simplest** - No complex tenant filtering, straightforward connection config
2. ✅ **Safest** - Zero risk of cross-product data leakage
3. ✅ **Most Modular** - Each product is independently deployable
4. ✅ **Best Documented** - Clear environment-based configuration

**Alignment with User Priorities:**
- ✅ Simplicity for deployment and development
- ✅ Modular architecture (each product isolated)
- ✅ Clear documentation (environment variables)

**Confidence Level: HIGH** - This approach is proven, simple, and meets all US-018 requirements.

**Next Agent (TASK-003):** Backend agent should use connection patterns documented here, focus on shared Python packages structure, and design API routing strategy.

---

**Document Version:** 1.0
**Date:** 2025-11-07
**Agent:** dev-database
**Status:** COMPLETE
**Next Task:** TASK-003 (Backend Architecture Design by dev-backend-fastapi agent)

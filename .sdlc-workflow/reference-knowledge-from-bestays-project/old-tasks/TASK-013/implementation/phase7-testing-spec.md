# Phase 7: Testing & Validation - Comprehensive Specification

**TASK:** TASK-013
**Phase:** IMPLEMENTATION - Phase 7
**Date:** 2025-11-09
**Coordinator:** Claude Code
**Target Subagent:** dev-backend-fastapi
**Status:** SPECIFICATION READY

---

## Overview

This specification defines comprehensive test coverage for Property V2 API implementation (Phases 4-6). The backend subagent will implement all test files to achieve >80% coverage with performance validation.

**Components to Test:**
- SQLAlchemy models (PropertyV2, Amenity, Policy + translations)
- Pydantic schemas (validation rules)
- Service layer (PropertyService, AmenityService, PolicyService)
- API endpoints (9 endpoints total)

**Success Criteria:**
- ✅ All tests pass (pytest)
- ✅ Coverage >80% for new code
- ✅ No SQL N+1 queries
- ✅ Property listing query <200ms (100 properties)
- ✅ All error cases covered (404, 403, 422, 400)

---

## Test Infrastructure

### File Structure

```
tests/
├── conftest.py                    # Fixtures and test configuration (CREATE)
├── models/
│   └── test_property_v2.py        # Model tests (CREATE)
├── schemas/
│   └── test_property_v2.py        # Schema validation tests (CREATE)
├── services/
│   └── test_property_service.py   # Service layer tests (CREATE)
└── api/
    └── v1/
        ├── test_properties.py     # Property endpoint tests (CREATE)
        ├── test_amenities.py      # Amenity endpoint tests (CREATE)
        └── test_policies.py       # Policy endpoint tests (CREATE)
```

**Create 7 new files + update conftest.py**

---

## 1. Test Configuration (tests/conftest.py)

### Database Strategy

**Approach:** Use test database with transaction rollback per test

```python
"""
Test configuration and fixtures for Property V2 API tests.

ARCHITECTURE:
  Layer: Testing Infrastructure
  Pattern: Fixture-based testing with pytest
  Task: TASK-013 (US-023)

PATTERNS USED:
  - Fixture factory pattern for test data
  - Transaction rollback for test isolation
  - Dependency override for authentication

DEPENDENCIES:
  External: pytest, pytest-asyncio, httpx, sqlalchemy
  Internal: server.models, server.schemas, server.database
"""

import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from server.config import get_settings
from server.database import Base, get_db
from server.main import app
from server.models.amenity import Amenity, AmenityTranslation
from server.models.policy import Policy, PolicyTranslation
from server.models.property_v2 import PropertyV2, PropertyTranslation
from server.models.user import User

# Test database URL (use in-memory SQLite for speed, or separate test PostgreSQL)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"  # Fast in-memory
# Alternative: "postgresql+asyncpg://user:pass@localhost:5433/bestays_test"

settings = get_settings()


# =====================
# Database Fixtures
# =====================

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,  # Set True to debug SQL queries
        poolclass=StaticPool,  # Required for in-memory SQLite
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create test database session with transaction rollback.

    Each test gets a clean database state via nested transaction.
    """
    async_session = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        async with session.begin():
            yield session
            # Transaction rolls back automatically after test


# =====================
# Authentication Fixtures
# =====================

@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create test user (regular role)."""
    user = User(
        id=1,
        clerk_user_id="user_test123",
        email="test@example.com",
        role="user",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create admin user."""
    user = User(
        id=2,
        clerk_user_id="user_admin456",
        email="admin@example.com",
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# =====================
# HTTP Client Fixtures
# =====================

async def override_get_db(db_session: AsyncSession):
    """Override database dependency."""
    yield db_session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Test client for public endpoints (no auth)."""
    app.dependency_overrides[get_db] = lambda: override_get_db(db_session)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user_client(
    db_session: AsyncSession, test_user: User
) -> AsyncGenerator[AsyncClient, None]:
    """Test client authenticated as regular user."""
    # Override auth dependency to return test_user
    from server.dependencies import get_current_user

    async def override_get_current_user():
        return test_user

    app.dependency_overrides[get_db] = lambda: override_get_db(db_session)
    app.dependency_overrides[get_current_user] = override_get_current_user

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_client(
    db_session: AsyncSession, admin_user: User
) -> AsyncGenerator[AsyncClient, None]:
    """Test client authenticated as admin."""
    from server.dependencies import get_current_user, require_admin

    async def override_get_current_user():
        return admin_user

    async def override_require_admin():
        return admin_user

    app.dependency_overrides[get_db] = lambda: override_get_db(db_session)
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[require_admin] = override_require_admin

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# =====================
# Test Data Fixtures
# =====================

@pytest_asyncio.fixture
async def test_amenities(db_session: AsyncSession) -> list[Amenity]:
    """Create test amenities with translations."""
    amenities = [
        Amenity(id="wifi", category="interior", icon="mdi:wifi", sort_order=1),
        Amenity(id="pool", category="exterior", icon="mdi:pool", sort_order=2),
        Amenity(id="gym", category="building", icon="mdi:gym", sort_order=3),
    ]

    translations = [
        AmenityTranslation(amenity_id="wifi", locale="en", field="name", value="WiFi"),
        AmenityTranslation(amenity_id="wifi", locale="th", field="name", value="ไวไฟ"),
        AmenityTranslation(amenity_id="pool", locale="en", field="name", value="Pool"),
        AmenityTranslation(amenity_id="pool", locale="th", field="name", value="สระว่ายน้ำ"),
        AmenityTranslation(amenity_id="gym", locale="en", field="name", value="Gym"),
        AmenityTranslation(amenity_id="gym", locale="th", field="name", value="ฟิตเนส"),
    ]

    for amenity in amenities:
        db_session.add(amenity)
    for trans in translations:
        db_session.add(trans)

    await db_session.commit()
    return amenities


@pytest_asyncio.fixture
async def test_policies(db_session: AsyncSession) -> list[Policy]:
    """Create test policies with translations."""
    policies = [
        Policy(
            id="pets_allowed",
            category="house_rules",
            data_type="boolean",
            sort_order=1,
        ),
        Policy(
            id="smoking_allowed",
            category="house_rules",
            data_type="boolean",
            sort_order=2,
        ),
    ]

    translations = [
        PolicyTranslation(
            policy_id="pets_allowed",
            locale="en",
            name="Pets Allowed",
            description="Whether pets are allowed",
        ),
        PolicyTranslation(
            policy_id="pets_allowed",
            locale="th",
            name="อนุญาตให้เลี้ยงสัตว์",
            description="อนุญาตให้เลี้ยงสัตว์หรือไม่",
        ),
        PolicyTranslation(
            policy_id="smoking_allowed",
            locale="en",
            name="Smoking Allowed",
            description="Whether smoking is allowed",
        ),
        PolicyTranslation(
            policy_id="smoking_allowed",
            locale="th",
            name="อนุญาตให้สูบบุหรี่",
            description="อนุญาตให้สูบบุหรี่หรือไม่",
        ),
    ]

    for policy in policies:
        db_session.add(policy)
    for trans in translations:
        db_session.add(trans)

    await db_session.commit()
    return policies


@pytest_asyncio.fixture
async def test_property(
    db_session: AsyncSession, test_user: User
) -> PropertyV2:
    """Create test property with translations."""
    prop = PropertyV2(
        title="Beautiful Villa",
        description="A beautiful villa with 3 bedrooms and a pool.",
        transaction_type="rent",
        property_type="villa",
        rent_price=3000000,  # 30,000 THB (stored as satang)
        currency="THB",
        physical_specs={
            "rooms": {"bedrooms": 3, "bathrooms": 2},
            "sizes": {"usable_area_sqm": 250, "land_area_sqm": 500},
        },
        location_details={
            "administrative": {
                "province_id": "10",  # Bangkok
                "district_id": "1001",
            }
        },
        amenities={"interior": ["wifi"], "exterior": ["pool"]},
        policies={"house_rules": {"pets_allowed": True}},
        contact_info={"phone": "0812345678"},
        cover_image={"url": "https://example.com/villa.jpg", "alt": "Villa"},
        images=[],
        tags=["luxury", "pool"],
        is_published=True,
        is_featured=False,
        listing_priority=50,
        created_by=test_user.id,
        updated_by=test_user.id,
    )

    db_session.add(prop)
    await db_session.commit()
    await db_session.refresh(prop)

    # Add translations
    translations = [
        PropertyTranslation(
            property_id=prop.id,
            locale="th",
            field="title",
            value="วิลล่าสวยงาม",
        ),
        PropertyTranslation(
            property_id=prop.id,
            locale="th",
            field="description",
            value="วิลล่าสวยงามพร้อม 3 ห้องนอนและสระว่ายน้ำ",
        ),
    ]

    for trans in translations:
        db_session.add(trans)

    await db_session.commit()
    await db_session.refresh(prop)

    return prop


# =====================
# Factory Fixtures
# =====================

@pytest.fixture
def property_factory(db_session: AsyncSession, test_user: User):
    """Factory fixture to create properties on-demand."""

    async def _create_property(**kwargs):
        defaults = {
            "title": f"Test Property {uuid4().hex[:8]}",
            "description": "Test description for property listing.",
            "transaction_type": "rent",
            "property_type": "condo",
            "rent_price": 1500000,  # 15,000 THB
            "currency": "THB",
            "physical_specs": {"rooms": {"bedrooms": 2, "bathrooms": 1}},
            "location_details": {},
            "amenities": {},
            "policies": {},
            "contact_info": {},
            "cover_image": None,
            "images": [],
            "tags": [],
            "is_published": True,
            "is_featured": False,
            "listing_priority": 50,
            "created_by": test_user.id,
            "updated_by": test_user.id,
        }
        defaults.update(kwargs)

        prop = PropertyV2(**defaults)
        db_session.add(prop)
        await db_session.commit()
        await db_session.refresh(prop)
        return prop

    return _create_property
```

### Notes on Fixtures

**Database Isolation:**
- Each test gets a fresh database via transaction rollback
- Amenities/policies created per test (not session-scoped)
- Properties created on-demand via factory

**Authentication:**
- Mock Clerk by overriding `get_current_user` dependency
- Three clients: public, user, admin
- Real User objects in database

**Factory Pattern:**
- `property_factory` allows creating properties with custom attributes
- Reduces test boilerplate
- Enables parameterized tests

---

## 2. Model Tests (tests/models/test_property_v2.py)

### Test Cases

```python
"""
Property V2 Model Tests - Relationships, Constraints, Soft Delete

ARCHITECTURE:
  Layer: Model (Database)
  Pattern: ORM testing with SQLAlchemy
  Task: TASK-013 (US-023)
"""

import pytest
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from server.models.property_v2 import PropertyV2, PropertyTranslation
from server.models.amenity import Amenity, AmenityTranslation
from server.models.policy import Policy, PolicyTranslation


# =====================
# Property Model Tests
# =====================

@pytest.mark.asyncio
async def test_property_creation(db_session, test_user):
    """Test basic property creation with required fields."""
    prop = PropertyV2(
        title="Test Villa",
        description="Test description for villa listing.",
        transaction_type="rent",
        property_type="villa",
        rent_price=5000000,
        currency="THB",
        physical_specs={},
        location_details={},
        amenities={},
        policies={},
        contact_info={},
        images=[],
        tags=[],
        created_by=test_user.id,
        updated_by=test_user.id,
    )

    db_session.add(prop)
    await db_session.commit()
    await db_session.refresh(prop)

    # Assertions
    assert prop.id is not None
    assert prop.title == "Test Villa"
    assert prop.transaction_type == "rent"
    assert prop.rent_price == 5000000
    assert prop.created_at is not None
    assert prop.updated_at is not None
    assert prop.deleted_at is None


@pytest.mark.asyncio
async def test_property_soft_delete(db_session, test_property):
    """Test soft delete sets deleted_at timestamp."""
    # Soft delete
    test_property.deleted_at = datetime.utcnow()
    await db_session.commit()

    # Verify deleted_at is set
    assert test_property.deleted_at is not None

    # Property still exists in database (soft delete)
    from sqlalchemy import select
    stmt = select(PropertyV2).where(PropertyV2.id == test_property.id)
    result = await db_session.execute(stmt)
    prop = result.scalar_one()
    assert prop.deleted_at is not None


@pytest.mark.asyncio
async def test_property_translations_relationship(db_session, test_property):
    """Test translation relationship and cascade."""
    # Create translation
    trans = PropertyTranslation(
        property_id=test_property.id,
        locale="ja",
        field="title",
        value="美しいヴィラ",
    )
    db_session.add(trans)
    await db_session.commit()

    # Refresh property to load relationship
    await db_session.refresh(test_property, ["translations"])

    # Verify relationship
    assert len(test_property.translations) > 0
    ja_trans = [t for t in test_property.translations if t.locale == "ja"]
    assert len(ja_trans) == 1
    assert ja_trans[0].value == "美しいヴィラ"


@pytest.mark.asyncio
async def test_property_cascade_delete_translations(db_session, test_property):
    """Test cascade delete removes translations when property deleted."""
    property_id = test_property.id

    # Add translation
    trans = PropertyTranslation(
        property_id=property_id,
        locale="en",
        field="title",
        value="Test",
    )
    db_session.add(trans)
    await db_session.commit()

    # Delete property (hard delete for this test)
    await db_session.delete(test_property)
    await db_session.commit()

    # Verify translations also deleted
    from sqlalchemy import select
    stmt = select(PropertyTranslation).where(
        PropertyTranslation.property_id == property_id
    )
    result = await db_session.execute(stmt)
    translations = result.scalars().all()
    assert len(translations) == 0


# =====================
# Amenity Model Tests
# =====================

@pytest.mark.asyncio
async def test_amenity_translation_relationship(db_session, test_amenities):
    """Test amenity translation relationship."""
    amenity = test_amenities[0]  # wifi

    # Load translations
    await db_session.refresh(amenity, ["translations"])

    # Verify translations
    assert len(amenity.translations) > 0
    locales = {t.locale for t in amenity.translations}
    assert "en" in locales
    assert "th" in locales


# =====================
# Policy Model Tests
# =====================

@pytest.mark.asyncio
async def test_policy_translation_relationship(db_session, test_policies):
    """Test policy translation relationship."""
    policy = test_policies[0]  # pets_allowed

    # Load translations
    await db_session.refresh(policy, ["translations"])

    # Verify translations
    assert len(policy.translations) > 0
    en_trans = [t for t in policy.translations if t.locale == "en"]
    assert len(en_trans) == 1
    assert en_trans[0].name == "Pets Allowed"
```

**Coverage:** 6 tests covering relationships, soft delete, cascades

---

## 3. Schema Tests (tests/schemas/test_property_v2.py)

### Test Cases

```python
"""
Property V2 Schema Tests - Pydantic Validation

ARCHITECTURE:
  Layer: Schema (Validation)
  Pattern: Pydantic model validation
  Task: TASK-013 (US-023)
"""

import pytest
from pydantic import ValidationError

from server.schemas.property_v2 import (
    PropertyCreate,
    PropertyUpdate,
    PhysicalSpecs,
    LocationDetails,
)


# =====================
# PropertyCreate Validation
# =====================

def test_property_create_valid():
    """Test valid PropertyCreate data."""
    data = PropertyCreate(
        title="Beautiful Villa",
        description="This is a beautiful villa with 3 bedrooms and a swimming pool.",
        transaction_type="rent",
        property_type="villa",
        rent_price=30000,
        currency="THB",
        physical_specs=PhysicalSpecs(rooms={"bedrooms": 3}),
        location_details=LocationDetails(),
        amenities={},
        policies={},
        contact_info={},
        images=[],
    )

    assert data.title == "Beautiful Villa"
    assert data.rent_price == 30000


def test_property_create_title_too_short():
    """Test title validation (min 10 chars)."""
    with pytest.raises(ValidationError) as exc_info:
        PropertyCreate(
            title="Short",  # Only 5 chars
            description="This is a valid description with more than 50 characters.",
            transaction_type="rent",
            property_type="villa",
            rent_price=30000,
            currency="THB",
            physical_specs=PhysicalSpecs(),
            location_details=LocationDetails(),
            amenities={},
            policies={},
            contact_info={},
            images=[],
        )

    errors = exc_info.value.errors()
    assert any("title" in str(e) for e in errors)


def test_property_create_description_too_short():
    """Test description validation (min 50 chars)."""
    with pytest.raises(ValidationError) as exc_info:
        PropertyCreate(
            title="Beautiful Villa",
            description="Short desc",  # Only 10 chars
            transaction_type="rent",
            property_type="villa",
            rent_price=30000,
            currency="THB",
            physical_specs=PhysicalSpecs(),
            location_details=LocationDetails(),
            amenities={},
            policies={},
            contact_info={},
            images=[],
        )

    errors = exc_info.value.errors()
    assert any("description" in str(e) for e in errors)


def test_property_create_negative_price():
    """Test price validation (must be positive)."""
    with pytest.raises(ValidationError) as exc_info:
        PropertyCreate(
            title="Beautiful Villa",
            description="This is a beautiful villa with 3 bedrooms and a swimming pool.",
            transaction_type="rent",
            property_type="villa",
            rent_price=-1000,  # Negative price
            currency="THB",
            physical_specs=PhysicalSpecs(),
            location_details=LocationDetails(),
            amenities={},
            policies={},
            contact_info={},
            images=[],
        )

    errors = exc_info.value.errors()
    assert any("rent_price" in str(e) for e in errors)


def test_property_create_invalid_transaction_type():
    """Test enum validation for transaction_type."""
    with pytest.raises(ValidationError) as exc_info:
        PropertyCreate(
            title="Beautiful Villa",
            description="This is a beautiful villa with 3 bedrooms and a swimming pool.",
            transaction_type="invalid_type",  # Invalid enum
            property_type="villa",
            rent_price=30000,
            currency="THB",
            physical_specs=PhysicalSpecs(),
            location_details=LocationDetails(),
            amenities={},
            policies={},
            contact_info={},
            images=[],
        )

    errors = exc_info.value.errors()
    assert any("transaction_type" in str(e) for e in errors)


# =====================
# PropertyUpdate Validation
# =====================

def test_property_update_partial():
    """Test PropertyUpdate accepts partial data."""
    data = PropertyUpdate(rent_price=35000)  # Only update rent_price

    assert data.rent_price == 35000
    assert data.title is None  # Optional field


def test_property_update_validates_provided_fields():
    """Test PropertyUpdate still validates provided fields."""
    with pytest.raises(ValidationError):
        PropertyUpdate(title="Short")  # Too short


# =====================
# Nested Model Validation
# =====================

def test_physical_specs_valid():
    """Test PhysicalSpecs nested model."""
    specs = PhysicalSpecs(
        rooms={"bedrooms": 3, "bathrooms": 2},
        sizes={"usable_area_sqm": 250},
    )

    assert specs.rooms["bedrooms"] == 3


def test_location_details_valid():
    """Test LocationDetails nested model."""
    location = LocationDetails(
        administrative={"province_id": "10", "district_id": "1001"}
    )

    assert location.administrative["province_id"] == "10"
```

**Coverage:** 10 tests covering validation rules, enums, nested models

---

## 4. Service Layer Tests (tests/services/test_property_service.py)

### Test Cases

```python
"""
Property Service Tests - Business Logic and Translations

ARCHITECTURE:
  Layer: Service (Business Logic)
  Pattern: Service layer testing
  Task: TASK-013 (US-023)
"""

import pytest
from uuid import uuid4

from server.services.property_service import property_service
from server.schemas.property_v2 import PropertyCreate, PropertyUpdate, PropertyListQuery


# =====================
# List Properties Tests
# =====================

@pytest.mark.asyncio
async def test_list_properties_no_filters(db_session, property_factory, test_user):
    """Test list_properties returns all properties with no filters."""
    # Create 3 test properties
    await property_factory(title="Property 1")
    await property_factory(title="Property 2")
    await property_factory(title="Property 3")

    # List all properties
    query = PropertyListQuery()
    properties, total = await property_service.list_properties(db_session, query)

    # Assertions
    assert total == 3
    assert len(properties) == 3


@pytest.mark.asyncio
async def test_list_properties_filter_transaction_type(
    db_session, property_factory, test_user
):
    """Test filtering by transaction_type."""
    # Create rent and sale properties
    await property_factory(transaction_type="rent", rent_price=2000000)
    await property_factory(transaction_type="sale", sale_price=5000000)
    await property_factory(transaction_type="rent", rent_price=3000000)

    # Filter by rent
    query = PropertyListQuery(transaction_type="rent")
    properties, total = await property_service.list_properties(db_session, query)

    # Assertions
    assert total == 2
    assert all(p.transaction_type == "rent" for p in properties)


@pytest.mark.asyncio
async def test_list_properties_filter_price_range(
    db_session, property_factory, test_user
):
    """Test filtering by price range."""
    # Create properties with different prices
    await property_factory(rent_price=1000000)  # 10k THB
    await property_factory(rent_price=3000000)  # 30k THB
    await property_factory(rent_price=5000000)  # 50k THB

    # Filter: 20k - 40k THB (2000000 - 4000000 satang)
    query = PropertyListQuery(min_price=20000, max_price=40000)
    properties, total = await property_service.list_properties(db_session, query)

    # Assertions
    assert total == 1
    # Note: Service returns prices in THB (divided by 100)
    assert properties[0].rent_price == 30000


@pytest.mark.asyncio
async def test_list_properties_pagination(db_session, property_factory, test_user):
    """Test pagination works correctly."""
    # Create 30 properties
    for i in range(30):
        await property_factory(title=f"Property {i+1}")

    # Request page 1, per_page 10
    query = PropertyListQuery(page=1, per_page=10)
    properties, total = await property_service.list_properties(db_session, query)

    # Assertions
    assert total == 30
    assert len(properties) == 10

    # Request page 2
    query = PropertyListQuery(page=2, per_page=10)
    properties, total = await property_service.list_properties(db_session, query)
    assert len(properties) == 10


@pytest.mark.asyncio
async def test_list_properties_with_locale(db_session, test_property):
    """Test properties return correct locale translations."""
    # test_property has Thai translations

    # Request with locale=th
    query = PropertyListQuery()
    properties, total = await property_service.list_properties(
        db_session, query, locale="th"
    )

    # Assertions
    assert total == 1
    assert properties[0].title == "วิลล่าสวยงาม"  # Thai title


@pytest.mark.asyncio
async def test_translation_fallback_chain(db_session, property_factory, test_user):
    """Test translation fallback: requested locale → EN → property field."""
    # Create property with only EN translation
    prop = await property_factory(title="English Title")

    # Add EN translation
    from server.models.property_v2 import PropertyTranslation
    trans = PropertyTranslation(
        property_id=prop.id,
        locale="en",
        field="title",
        value="English Translation",
    )
    db_session.add(trans)
    await db_session.commit()

    # Request with locale=th (no Thai translation exists)
    query = PropertyListQuery()
    properties, total = await property_service.list_properties(
        db_session, query, locale="th"
    )

    # Should fallback to EN translation
    assert properties[0].title == "English Translation"


# =====================
# Get Property Tests
# =====================

@pytest.mark.asyncio
async def test_get_property_by_id(db_session, test_property):
    """Test get_property_by_id returns correct property."""
    prop = await property_service.get_property_by_id(
        db_session, test_property.id, locale="en"
    )

    assert prop is not None
    assert prop.id == test_property.id
    assert prop.title == test_property.title


@pytest.mark.asyncio
async def test_get_property_by_id_not_found(db_session):
    """Test get_property_by_id returns None for invalid ID."""
    prop = await property_service.get_property_by_id(
        db_session, uuid4(), locale="en"
    )

    assert prop is None


@pytest.mark.asyncio
async def test_get_property_excludes_deleted(db_session, test_property):
    """Test soft-deleted properties are excluded by default."""
    from datetime import datetime

    # Soft delete
    test_property.deleted_at = datetime.utcnow()
    await db_session.commit()

    # Try to get property
    prop = await property_service.get_property_by_id(
        db_session, test_property.id, locale="en"
    )

    # Should return None
    assert prop is None


# =====================
# Create Property Tests
# =====================

@pytest.mark.asyncio
async def test_create_property(db_session, test_user, test_amenities):
    """Test creating property with valid data."""
    data = PropertyCreate(
        title="New Test Villa",
        description="This is a new test villa with all required fields.",
        transaction_type="rent",
        property_type="villa",
        rent_price=40000,
        currency="THB",
        physical_specs={"rooms": {"bedrooms": 4}},
        location_details={},
        amenities={"interior": ["wifi"]},
        policies={},
        contact_info={},
        images=[],
    )

    prop = await property_service.create_property(db_session, data, test_user.id)

    # Assertions
    assert prop.id is not None
    assert prop.title == "New Test Villa"
    assert prop.rent_price == 40000  # Returned in THB


@pytest.mark.asyncio
async def test_create_property_invalid_amenity_id(db_session, test_user):
    """Test creating property with invalid amenity ID fails."""
    from fastapi import HTTPException

    data = PropertyCreate(
        title="Test Villa",
        description="This is a test villa with invalid amenity.",
        transaction_type="rent",
        property_type="villa",
        rent_price=30000,
        currency="THB",
        physical_specs={},
        location_details={},
        amenities={"interior": ["invalid_amenity_id"]},
        policies={},
        contact_info={},
        images=[],
    )

    with pytest.raises(HTTPException) as exc_info:
        await property_service.create_property(db_session, data, test_user.id)

    assert exc_info.value.status_code == 400
    assert "Invalid amenity IDs" in exc_info.value.detail


# =====================
# Update Property Tests
# =====================

@pytest.mark.asyncio
async def test_update_property(db_session, test_property, test_user):
    """Test updating property with partial data."""
    data = PropertyUpdate(rent_price=35000)

    updated = await property_service.update_property(
        db_session, test_property.id, data, test_user.id, test_user
    )

    # Assertions
    assert updated.rent_price == 35000
    assert updated.title == test_property.title  # Unchanged


@pytest.mark.asyncio
async def test_update_property_ownership_check(
    db_session, test_property, admin_user
):
    """Test non-owner cannot update property (unless admin)."""
    # Create another user
    from server.models.user import User

    other_user = User(
        id=3,
        clerk_user_id="user_other",
        email="other@example.com",
        role="user",
    )
    db_session.add(other_user)
    await db_session.commit()

    data = PropertyUpdate(rent_price=35000)

    # Non-owner, non-admin should fail
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        await property_service.update_property(
            db_session, test_property.id, data, other_user.id, other_user
        )

    assert exc_info.value.status_code == 403


# =====================
# Delete Property Tests
# =====================

@pytest.mark.asyncio
async def test_delete_property(db_session, test_property, test_user):
    """Test soft deleting property."""
    result = await property_service.delete_property(
        db_session, test_property.id, test_user
    )

    assert result is True

    # Verify deleted_at is set
    await db_session.refresh(test_property)
    assert test_property.deleted_at is not None


# =====================
# Translation Management Tests
# =====================

@pytest.mark.asyncio
async def test_get_all_translations(db_session, test_property):
    """Test get_all_translations returns all locales."""
    translations = await property_service.get_all_translations(
        db_session, test_property.id
    )

    # Assertions
    assert "th" in translations
    assert translations["th"]["title"] == "วิลล่าสวยงาม"


@pytest.mark.asyncio
async def test_update_translations(db_session, test_property):
    """Test updating translations for a locale."""
    new_translations = {
        "title": "Updated Thai Title",
        "description": "Updated Thai Description",
    }

    updated_fields = await property_service.update_translations(
        db_session, test_property.id, "th", new_translations
    )

    # Assertions
    assert "title" in updated_fields
    assert "description" in updated_fields

    # Verify translations updated
    translations = await property_service.get_all_translations(
        db_session, test_property.id
    )
    assert translations["th"]["title"] == "Updated Thai Title"
```

**Coverage:** 20 tests covering all service methods, filters, pagination, translations

---

## 5. Property API Endpoint Tests (tests/api/v1/test_properties.py)

### Test Cases

```python
"""
Property API Endpoint Tests - HTTP Integration

ARCHITECTURE:
  Layer: API (HTTP)
  Pattern: Endpoint integration testing
  Task: TASK-013 (US-023)
"""

import pytest
from uuid import uuid4


# =====================
# List Properties Endpoint
# =====================

@pytest.mark.asyncio
async def test_list_properties_endpoint(client, property_factory, test_user):
    """Test GET /api/v1/properties."""
    # Create test properties
    await property_factory(title="Property 1")
    await property_factory(title="Property 2")

    # Request
    response = await client.get("/api/v1/properties?locale=en")

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "properties" in data
    assert "pagination" in data
    assert data["pagination"]["total"] == 2


@pytest.mark.asyncio
async def test_list_properties_with_filters(client, property_factory, test_user):
    """Test filtering properties."""
    # Create properties
    await property_factory(transaction_type="rent", rent_price=2000000)
    await property_factory(transaction_type="sale", sale_price=5000000)

    # Filter by rent
    response = await client.get("/api/v1/properties?transaction_type=rent")

    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["total"] == 1
    assert data["properties"][0]["transaction_type"] == "rent"


# =====================
# Get Property Endpoint
# =====================

@pytest.mark.asyncio
async def test_get_property_endpoint(client, test_property):
    """Test GET /api/v1/properties/{id}."""
    response = await client.get(f"/api/v1/properties/{test_property.id}?locale=en")

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["property"]["id"] == str(test_property.id)
    assert data["property"]["title"] == test_property.title


@pytest.mark.asyncio
async def test_get_property_not_found(client):
    """Test GET /api/v1/properties/{id} with invalid ID."""
    response = await client.get(f"/api/v1/properties/{uuid4()}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_property_thai_locale(client, test_property):
    """Test GET /api/v1/properties/{id} with Thai locale."""
    response = await client.get(f"/api/v1/properties/{test_property.id}?locale=th")

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["property"]["title"] == "วิลล่าสวยงาม"  # Thai title


# =====================
# Create Property Endpoint
# =====================

@pytest.mark.asyncio
async def test_create_property_endpoint_admin(admin_client, test_amenities):
    """Test POST /api/v1/properties as admin."""
    payload = {
        "title": "New Property via API",
        "description": "This is a new property created via API endpoint.",
        "transaction_type": "rent",
        "property_type": "condo",
        "rent_price": 25000,
        "currency": "THB",
        "physical_specs": {"rooms": {"bedrooms": 2}},
        "location_details": {},
        "amenities": {},
        "policies": {},
        "contact_info": {},
        "images": [],
    }

    response = await admin_client.post("/api/v1/properties", json=payload)

    # Assertions
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Property via API"


@pytest.mark.asyncio
async def test_create_property_endpoint_forbidden(user_client):
    """Test POST /api/v1/properties as regular user (should fail)."""
    payload = {
        "title": "New Property",
        "description": "This should fail because user is not admin.",
        "transaction_type": "rent",
        "property_type": "condo",
        "rent_price": 20000,
        "currency": "THB",
        "physical_specs": {},
        "location_details": {},
        "amenities": {},
        "policies": {},
        "contact_info": {},
        "images": [],
    }

    response = await user_client.post("/api/v1/properties", json=payload)

    # Assertions
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_property_validation_error(admin_client):
    """Test POST /api/v1/properties with invalid data."""
    payload = {
        "title": "Short",  # Too short
        "description": "Also short",  # Too short
        "transaction_type": "rent",
        "property_type": "condo",
        "rent_price": 20000,
        "currency": "THB",
        "physical_specs": {},
        "location_details": {},
        "amenities": {},
        "policies": {},
        "contact_info": {},
        "images": [],
    }

    response = await admin_client.post("/api/v1/properties", json=payload)

    # Assertions
    assert response.status_code == 422  # Validation error


# =====================
# Update Property Endpoint
# =====================

@pytest.mark.asyncio
async def test_update_property_endpoint_owner(user_client, test_property):
    """Test PUT /api/v1/properties/{id} as owner."""
    payload = {"rent_price": 32000}

    response = await user_client.put(
        f"/api/v1/properties/{test_property.id}", json=payload
    )

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["rent_price"] == 32000


@pytest.mark.asyncio
async def test_update_property_endpoint_admin(admin_client, test_property):
    """Test PUT /api/v1/properties/{id} as admin."""
    payload = {"is_featured": True}

    response = await admin_client.put(
        f"/api/v1/properties/{test_property.id}", json=payload
    )

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["is_featured"] is True


# =====================
# Delete Property Endpoint
# =====================

@pytest.mark.asyncio
async def test_delete_property_endpoint_owner(user_client, test_property):
    """Test DELETE /api/v1/properties/{id} as owner."""
    response = await user_client.delete(f"/api/v1/properties/{test_property.id}")

    # Assertions
    assert response.status_code == 200

    # Verify soft deleted
    get_response = await user_client.get(f"/api/v1/properties/{test_property.id}")
    assert get_response.status_code == 404  # Excluded from queries


# =====================
# Translation Endpoints
# =====================

@pytest.mark.asyncio
async def test_get_property_translations_endpoint(client, test_property):
    """Test GET /api/v1/properties/{id}/translations."""
    response = await client.get(f"/api/v1/properties/{test_property.id}/translations")

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "th" in data
    assert data["th"]["title"] == "วิลล่าสวยงาม"


@pytest.mark.asyncio
async def test_update_property_translations_endpoint(admin_client, test_property):
    """Test PUT /api/v1/properties/{id}/translations/{locale}."""
    payload = {
        "title": "Updated Thai Title via API",
        "description": "Updated Thai Description via API",
    }

    response = await admin_client.put(
        f"/api/v1/properties/{test_property.id}/translations/th", json=payload
    )

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "title" in data["updated_fields"]
```

**Coverage:** 15 tests for 7 endpoints (list, get, create, update, delete, get translations, update translations)

---

## 6. Amenity Endpoint Tests (tests/api/v1/test_amenities.py)

### Test Cases

```python
"""
Amenity API Endpoint Tests

ARCHITECTURE:
  Layer: API (HTTP)
  Pattern: Endpoint integration testing
  Task: TASK-013 (US-023)
"""

import pytest


@pytest.mark.asyncio
async def test_list_amenities_endpoint_en(client, test_amenities):
    """Test GET /api/v1/amenities with English locale."""
    response = await client.get("/api/v1/amenities?locale=en")

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "amenities" in data
    assert len(data["amenities"]) == 3

    # Verify English names
    wifi = next(a for a in data["amenities"] if a["id"] == "wifi")
    assert wifi["name"] == "WiFi"


@pytest.mark.asyncio
async def test_list_amenities_endpoint_th(client, test_amenities):
    """Test GET /api/v1/amenities with Thai locale."""
    response = await client.get("/api/v1/amenities?locale=th")

    # Assertions
    assert response.status_code == 200
    data = response.json()

    # Verify Thai names
    wifi = next(a for a in data["amenities"] if a["id"] == "wifi")
    assert wifi["name"] == "ไวไฟ"


@pytest.mark.asyncio
async def test_list_amenities_filter_category(client, test_amenities):
    """Test filtering amenities by category."""
    response = await client.get("/api/v1/amenities?category=interior")

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert len(data["amenities"]) == 1
    assert data["amenities"][0]["category"] == "interior"
```

**Coverage:** 3 tests for amenity endpoint

---

## 7. Policy Endpoint Tests (tests/api/v1/test_policies.py)

### Test Cases

```python
"""
Policy API Endpoint Tests

ARCHITECTURE:
  Layer: API (HTTP)
  Pattern: Endpoint integration testing
  Task: TASK-013 (US-023)
"""

import pytest


@pytest.mark.asyncio
async def test_list_policies_endpoint_en(client, test_policies):
    """Test GET /api/v1/policies with English locale."""
    response = await client.get("/api/v1/policies?locale=en")

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "policies" in data
    assert len(data["policies"]) == 2

    # Verify English names
    pets = next(p for p in data["policies"] if p["id"] == "pets_allowed")
    assert pets["name"] == "Pets Allowed"


@pytest.mark.asyncio
async def test_list_policies_endpoint_th(client, test_policies):
    """Test GET /api/v1/policies with Thai locale."""
    response = await client.get("/api/v1/policies?locale=th")

    # Assertions
    assert response.status_code == 200
    data = response.json()

    # Verify Thai names
    pets = next(p for p in data["policies"] if p["id"] == "pets_allowed")
    assert pets["name"] == "อนุญาตให้เลี้ยงสัตว์"


@pytest.mark.asyncio
async def test_list_policies_filter_category(client, test_policies):
    """Test filtering policies by category."""
    response = await client.get("/api/v1/policies?category=house_rules")

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert len(data["policies"]) == 2
    assert all(p["category"] == "house_rules" for p in data["policies"])
```

**Coverage:** 3 tests for policy endpoint

---

## Performance & Coverage Requirements

### Test Execution

```bash
# Run all tests
cd apps/server
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=server.models.property_v2 \
                  --cov=server.schemas.property_v2 \
                  --cov=server.services.property_service \
                  --cov=server.services.amenity_service \
                  --cov=server.services.policy_service \
                  --cov=server.api.v1.endpoints.properties \
                  --cov=server.api.v1.endpoints.amenities \
                  --cov=server.api.v1.endpoints.policies \
                  --cov-report=term-missing \
                  --cov-report=html

# Performance test
pytest tests/ -v --durations=10  # Show 10 slowest tests
```

### Coverage Target

**Minimum:** 80% for all new code

**Critical paths require 100% coverage:**
- Translation fallback logic
- Authorization checks
- Price conversion (satang/cents ↔ THB/USD)
- Soft delete behavior

### Performance Validation

**Query Performance Test:**

```python
@pytest.mark.asyncio
async def test_list_properties_performance(db_session, property_factory, test_user):
    """Test property listing performance with 100 properties."""
    import time

    # Create 100 properties
    for i in range(100):
        await property_factory(title=f"Property {i}")

    # Measure query time
    start = time.time()
    query = PropertyListQuery(per_page=24)
    properties, total = await property_service.list_properties(db_session, query)
    elapsed = time.time() - start

    # Assertions
    assert total == 100
    assert elapsed < 0.2  # Must complete in <200ms
```

**SQL N+1 Query Detection:**

```python
@pytest.mark.asyncio
async def test_no_n_plus_1_queries(db_session, property_factory, test_user):
    """Test no N+1 queries when loading translations."""
    # Enable SQL logging
    import logging
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    # Create 10 properties with translations
    for i in range(10):
        prop = await property_factory(title=f"Property {i}")
        # Add translation
        trans = PropertyTranslation(
            property_id=prop.id,
            locale="th",
            field="title",
            value=f"ทรัพย์สิน {i}",
        )
        db_session.add(trans)

    await db_session.commit()

    # Count queries
    from sqlalchemy import event
    queries = []

    def receive_after_execute(conn, cursor, statement, params, context, executemany):
        queries.append(statement)

    event.listen(db_session.bind, "after_cursor_execute", receive_after_execute)

    # List properties
    query = PropertyListQuery()
    properties, total = await property_service.list_properties(db_session, query)

    # Should be 2-3 queries max (properties + translations), not 10+
    assert len(queries) <= 3
```

---

## Test Summary

**Total Test Files:** 7
**Total Test Cases:** ~60

| File | Tests | Focus |
|------|-------|-------|
| conftest.py | N/A | Fixtures |
| test_property_v2.py (models) | 6 | Relationships, constraints, soft delete |
| test_property_v2.py (schemas) | 10 | Pydantic validation |
| test_property_service.py | 20 | Service methods, filters, translations |
| test_properties.py | 15 | Property endpoints, auth |
| test_amenities.py | 3 | Amenity endpoint |
| test_policies.py | 3 | Policy endpoint |
| **Total** | **57+** | **Comprehensive coverage** |

---

## Deliverables

After implementation, subagent must provide:

1. **All 7 test files created** (conftest.py + 6 test files)
2. **Test execution report:**
   - All tests passing
   - Coverage percentage (>80%)
   - Performance metrics (query times)
3. **SQL query analysis:**
   - Verify no N+1 queries
   - Confirm index usage
4. **Error coverage report:**
   - All error cases tested (404, 403, 422, 400)
5. **Phase 7 completion report:**
   - Summary of tests implemented
   - Coverage achieved
   - Any issues found and resolved

---

## Success Criteria Validation

Before marking Phase 7 complete, verify:

- ✅ `pytest tests/ -v` → All tests pass
- ✅ Coverage >80% for new code
- ✅ No SQL N+1 queries (verified via logging)
- ✅ Property listing <200ms (performance test)
- ✅ All error cases covered (404, 403, 422, 400)
- ✅ Translation fallback tested (locale → EN → field)
- ✅ Soft delete tested (deleted_at behavior)
- ✅ Authorization tested (admin/owner checks)
- ✅ All 9 endpoints tested
- ✅ Pagination tested
- ✅ Filters tested (transaction_type, price, bedrooms, etc.)

---

## Next Steps After Phase 7

1. **Commit tests:** `git add tests/ && git commit -m "test: comprehensive Property V2 API tests (US-023 TASK-013)"`
2. **Create phase completion report**
3. **Move to TESTING phase in task lifecycle**
4. **Run full regression suite**
5. **Deploy to staging environment**
6. **Begin Phase 8: Documentation & Monitoring** (if needed)

---

**Status:** READY FOR IMPLEMENTATION
**Assigned To:** dev-backend-fastapi subagent
**Expected Duration:** 3-4 hours
**Priority:** HIGH (blocking US-023 completion)

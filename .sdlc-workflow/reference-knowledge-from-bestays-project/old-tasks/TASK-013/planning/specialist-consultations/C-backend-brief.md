# Backend/FastAPI Specialist Consultation Brief

## Context
TASK-013: Property V2 Schema Migration - SQLAlchemy models and FastAPI API design

We need to implement:
- SQLAlchemy Property model with JSONB fields
- SQLAlchemy PropertyTranslation model
- FastAPI CRUD endpoints with localization support
- Service layer to merge property data + translations
- Pydantic schemas for validation

## Proposed SQLAlchemy Model Structure

```python
class Property(Base):
    __tablename__ = "properties"
    
    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    title = Column(String(255))  # Fallback
    description = Column(Text)    # Fallback
    
    # Classification
    transaction_type = Column(String(20), nullable=False)
    property_type = Column(String(50), nullable=False)
    
    # Pricing
    rent_price = Column(BigInteger)
    currency = Column(String(3), default="THB")
    
    # JSONB fields
    physical_specs = Column(JSONB)
    location_details = Column(JSONB)
    amenities = Column(JSONB)
    policies = Column(JSONB)
    contact_info = Column(JSONB)
    
    # pgvector (future)
    description_embedding_en = Column(Vector(1536))
    description_embedding_th = Column(Vector(1536))
    
    # Relationships
    translations = relationship("PropertyTranslation", back_populates="property")

class PropertyTranslation(Base):
    __tablename__ = "property_translations"
    
    id = Column(Integer, primary_key=True)
    property_id = Column(UUID, ForeignKey("properties.id", ondelete="CASCADE"))
    locale = Column(String(5), nullable=False)
    field = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)
    
    property = relationship("Property", back_populates="translations")
```

## Proposed API Structure

```python
# GET /api/v1/properties
async def list_properties(
    locale: str = "en",
    page: int = 1,
    per_page: int = 24,
    transaction_type: Optional[str] = None,
    property_type: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    bedrooms: Optional[int] = None,
    amenities: Optional[List[str]] = Query(None)
):
    # Merge property + translations
    # Return paginated results
```

## Questions for Backend Specialist

1. **SQLAlchemy Relationships:**
   - Should Property→PropertyTranslation use eager loading (joinedload) or lazy loading?
   - How to efficiently merge property + translations in a single query?
   - Should we use `relationship()` or manual JOINs for better performance?

2. **Query Optimization:**
   - How to query JSONB fields efficiently with SQLAlchemy ORM?
   - Example: Filter by bedrooms: `physical_specs->'rooms'->>'bedrooms' = '3'`
   - Should we use SQLAlchemy query builder or raw SQL for complex filters?
   - How to handle JSONB containment queries for amenities filtering?

3. **API Response Schema:**
   - Should translations be nested in response or flat structure?
   - Example nested: `{"title_translations": {"en": "...", "th": "..."}}`
   - Example flat: `{"title": "..."}` (merged based on locale parameter)
   - Which is more performant and maintainable?

4. **Pydantic Validation:**
   - How strict should JSONB field validation be?
   - Should we define Pydantic schemas for each JSONB field structure?
   - Example: `PhysicalSpecsSchema(BaseModel)` with nested models?
   - Or allow flexible JSONB and validate at application layer?

5. **Service Layer Design:**
   - How to structure PropertyService for translation merging?
   - Should we have separate `get_property_with_locale(id, locale)` method?
   - How to handle fallback if translation missing (e.g., TH missing, fallback to EN)?
   - Caching strategy for merged property + translations?

6. **Query Builder Pattern:**
   - For complex filtering (price range, bedrooms, amenities), should we use:
     - SQLAlchemy query builder (filter, where)?
     - Query object pattern (build filter dict)?
     - Raw SQL with SQLAlchemy execution?
   - What's most maintainable and performant?

7. **ORM Performance Considerations:**
   - N+1 query problem with translations - how to avoid?
   - Should we use `selectinload()` for translations?
   - Batch loading strategies for list endpoints?
   - When to use `.scalars()` vs `.all()` for query results?

## Deliverable
Backend architecture recommendations, SQLAlchemy patterns, API design, and query optimization strategies.

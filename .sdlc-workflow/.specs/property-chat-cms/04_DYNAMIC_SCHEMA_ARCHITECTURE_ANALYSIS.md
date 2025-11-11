# Dynamic Property Type Extensibility Analysis

**Status:** 📝 DRAFT - Architecture Decision
**Created:** 2025-11-06
**Purpose:** Analyze options for allowing LLM agents to create new property types dynamically without code changes

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Options Comparison](#options-comparison)
3. [Recommended Approach](#recommended-approach)
4. [Schema Design](#schema-design)
5. [Validation Strategy](#validation-strategy)
6. [LLM Integration](#llm-integration)
7. [Performance Considerations](#performance-considerations)
8. [Code Example](#code-example)
9. [MVP Recommendation](#mvp-recommendation)
10. [Risk Assessment](#risk-assessment)

---

## Executive Summary

### The Problem

Current architecture uses static subdomain tables (`rental_details`, `sale_details`, etc.) which require code changes to add new property types like "Eco-Resort" or "Co-living Space". User wants LLM agents to create property types on-the-fly.

### Key Constraints

- Must support 165+ existing amenities across 24 catalogues
- Must maintain query performance for filtering/search
- Must preserve data integrity and validation
- Must work with existing PostgreSQL + pgvector setup
- Must allow LLM to discover schema dynamically

### Recommendation Preview

**Hybrid approach (Option C)** - Core static schema + JSONB dynamic fields with JSON Schema validation. Start with static schema for MVP, add dynamic capability in Phase 2.

---

## Options Comparison

| Option | Pros | Cons | Performance | Complexity | Recommendation |
|--------|------|------|-------------|------------|----------------|
| **A. EAV (Entity-Attribute-Value)** | ✅ Maximum flexibility<br>✅ No schema changes needed<br>✅ Well-understood pattern | ❌ Poor query performance<br>❌ Complex JOINs<br>❌ Type safety issues<br>❌ Hard to validate | ⭐ (Very Poor)<br>10-100x slower queries | ⭐⭐⭐⭐ (High)<br>Complex filtering | ❌ **NOT RECOMMENDED**<br>Kills search performance |
| **B. JSONB with Validation** | ✅ PostgreSQL native<br>✅ GIN indexes work well<br>✅ Flexible schema<br>✅ JSON Schema validation | ❌ Less structure<br>❌ Complex validation logic<br>❌ Harder to enforce relationships | ⭐⭐⭐⭐ (Good)<br>GIN indexes help | ⭐⭐⭐ (Medium)<br>Validation logic needed | ✅ **VIABLE**<br>Good for MVP |
| **C. Hybrid (Core + Dynamic)** | ✅ Best of both worlds<br>✅ Static fields optimized<br>✅ JSONB for flexibility<br>✅ Gradual migration path | ⚠️ More planning needed<br>⚠️ Dual query patterns | ⭐⭐⭐⭐⭐ (Excellent)<br>Best balance | ⭐⭐⭐ (Medium)<br>Clear separation | ✅ **RECOMMENDED**<br>Ship static first |
| **D. PostgreSQL Inheritance** | ✅ Native PostgreSQL feature<br>✅ True OOP inheritance<br>✅ Type safety | ❌ Limited adoption<br>❌ Poor tooling support<br>❌ Complex migrations<br>❌ Partitioning issues | ⭐⭐⭐ (Fair)<br>Constraint checking overhead | ⭐⭐⭐⭐ (High)<br>Steep learning curve | ⚠️ **AVOID**<br>Not worth complexity |
| **E. Dynamic Tables** | ✅ Full relational power<br>✅ Optimal queries per type | ❌ DDL operations in production<br>❌ Schema bloat<br>❌ Migration hell<br>❌ Dangerous for LLM | ⭐⭐⭐⭐⭐ (Excellent)<br>Native queries | ⭐⭐⭐⭐⭐ (Very High)<br>Operations risk | ❌ **NOT RECOMMENDED**<br>Too risky for agents |

### Performance Details

**EAV Performance Impact:**
```sql
-- Traditional query (10ms)
SELECT * FROM properties WHERE bedrooms = 3;

-- EAV equivalent (150ms+)
SELECT p.* FROM properties p
JOIN eav_attributes ea1 ON p.id = ea1.entity_id AND ea1.attribute = 'bedrooms' AND ea1.value = '3'
JOIN eav_attributes ea2 ON p.id = ea2.entity_id AND ea2.attribute = 'bathrooms' AND ea2.value = '2';
```

**JSONB Performance:**
```sql
-- JSONB with GIN index (15ms)
SELECT * FROM properties
WHERE physical_specs @> '{"rooms": {"bedrooms": 3}}';
```

---

## Recommended Approach

### Decision: Hybrid (Option C) with Phased Rollout

**Phase 1 (MVP):** Static schema as designed in `04_PROPERTY_MODERNIZATION_PLAN.md`
- Ship with existing 5 subdomains (rental, sale, lease, business, investment)
- Use JSONB for `physical_specs`, `location_details`, `amenities`, `policies`
- Validate business value before adding complexity

**Phase 2 (Post-MVP):** Add dynamic property types capability
- Introduce `property_type_definitions` table for LLM-created types
- Store type-specific fields in validated JSONB
- LLM introspects schema via API

### Why This Approach?

1. **Ship Fast:** MVP doesn't need dynamic types - 99% of properties fit existing types
2. **Validate First:** Prove the chat-based property creation works before adding meta-schema
3. **Safety:** Don't give LLM DDL powers in production on day 1
4. **Performance:** Keep query optimization simple for launch
5. **Reversible:** Can still add dynamic types later without rewrite

### Trade-offs Accepted

✅ **Accepting:**
- Manual code deployment for new property types in MVP
- Limited to 5 transaction types initially
- Some properties might not fit perfectly (use `property_type: pt_other`)

❌ **NOT Accepting:**
- Poor query performance (no EAV)
- Production DDL by LLM (no dynamic tables)
- Data integrity risks (validation required)

### Migration Path from Static Schema

When ready for Phase 2:

1. **Add meta-schema tables** (property_type_definitions, field_definitions)
2. **Migrate existing types** to definitions table
3. **Preserve static columns** for core fields (title, location, price)
4. **Add `custom_fields` JSONB** column to properties table
5. **Update validation layer** to use type definitions
6. **Expose introspection API** for LLM

**Key principle:** Existing properties don't break, new dynamic types extend the system.

---

## Schema Design

### Property Type Definitions Table

```sql
-- Meta-schema: Define custom property types
CREATE TABLE property_type_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Type Identity
    type_code VARCHAR(50) UNIQUE NOT NULL,        -- e.g., 'pt_eco_resort', 'pt_coliving'
    type_name VARCHAR(100) NOT NULL,              -- e.g., 'Eco-Resort', 'Co-living Space'
    type_category VARCHAR(50) NOT NULL,           -- 'hospitality', 'residential', 'commercial'

    -- Schema Definition
    field_schema JSONB NOT NULL,                  -- JSON Schema for custom fields
    /*
    Example:
    {
      "type": "object",
      "properties": {
        "sustainability_rating": {
          "type": "string",
          "enum": ["gold", "silver", "bronze"],
          "description": "Eco-certification level"
        },
        "renewable_energy_percentage": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "% of energy from renewable sources"
        },
        "water_conservation_features": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Water-saving systems"
        }
      },
      "required": ["sustainability_rating"]
    }
    */

    -- UI Configuration
    ui_config JSONB DEFAULT '{}',                 -- Form layout, icons, colors
    /*
    {
      "icon": "eco",
      "color": "#4CAF50",
      "form_sections": [
        {
          "section": "Sustainability",
          "fields": ["sustainability_rating", "renewable_energy_percentage"]
        }
      ],
      "search_filters": ["sustainability_rating"]
    }
    */

    -- Validation Rules
    validation_rules JSONB DEFAULT '{}',          -- Business rules beyond JSON Schema
    /*
    {
      "min_price": 50000,
      "required_amenities": ["am_ext_solar_panels"],
      "allowed_regions": ["phuket", "krabi"]
    }
    */

    -- Parent Type (Inheritance)
    extends_type VARCHAR(50),                     -- Optional: inherit from base type

    -- Metadata
    description TEXT,
    created_by UUID REFERENCES users(id),
    is_active BOOLEAN DEFAULT true,
    is_system_type BOOLEAN DEFAULT false,         -- Core types vs user-created
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CHECK (type_code ~ '^pt_[a-z_]+$'),          -- Enforce naming convention
    CHECK (jsonb_typeof(field_schema) = 'object')
);

-- Indexes
CREATE INDEX idx_property_type_definitions_category ON property_type_definitions(type_category);
CREATE INDEX idx_property_type_definitions_active ON property_type_definitions(is_active);
CREATE INDEX idx_property_type_definitions_system ON property_type_definitions(is_system_type);
CREATE INDEX idx_property_type_definitions_schema ON property_type_definitions USING GIN(field_schema);
```

### Field Definitions Table (Optional - More Granular)

```sql
-- Reusable field definitions across property types
CREATE TABLE field_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Field Identity
    field_code VARCHAR(50) UNIQUE NOT NULL,       -- e.g., 'sustainability_rating'
    field_name VARCHAR(100) NOT NULL,             -- e.g., 'Sustainability Rating'
    field_category VARCHAR(50),                   -- 'environmental', 'financial', 'social'

    -- Schema
    field_type VARCHAR(20) NOT NULL,              -- 'string', 'number', 'boolean', 'array', 'object'
    field_schema JSONB NOT NULL,                  -- Detailed JSON Schema

    -- UI
    ui_component VARCHAR(50),                     -- 'select', 'slider', 'checkbox', 'text'
    ui_config JSONB DEFAULT '{}',

    -- Metadata
    description TEXT,
    is_searchable BOOLEAN DEFAULT true,
    is_required BOOLEAN DEFAULT false,
    sort_order INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Link fields to property types
CREATE TABLE property_type_fields (
    property_type_id UUID REFERENCES property_type_definitions(id) ON DELETE CASCADE,
    field_id UUID REFERENCES field_definitions(id) ON DELETE CASCADE,
    is_required BOOLEAN DEFAULT false,
    default_value JSONB,
    sort_order INTEGER DEFAULT 0,

    PRIMARY KEY (property_type_id, field_id)
);
```

### Updated Properties Table

```sql
-- Extend existing properties table
ALTER TABLE properties
ADD COLUMN custom_fields JSONB DEFAULT '{}',
ADD COLUMN property_type_definition_id UUID REFERENCES property_type_definitions(id);

-- Index for custom field queries
CREATE INDEX idx_properties_custom_fields ON properties USING GIN(custom_fields);

-- Example: Eco-Resort property
INSERT INTO properties (
    title,
    property_type,
    property_type_definition_id,
    custom_fields
) VALUES (
    'Green Paradise Eco-Resort',
    'pt_eco_resort',
    'uuid-of-eco-resort-type',
    '{
        "sustainability_rating": "gold",
        "renewable_energy_percentage": 85,
        "water_conservation_features": ["rainwater_harvesting", "greywater_recycling"],
        "organic_garden": true,
        "carbon_offset_program": true
    }'
);
```

### Example: Creating "Eco-Resort" Type

```sql
-- Step 1: Create the property type definition
INSERT INTO property_type_definitions (
    type_code,
    type_name,
    type_category,
    field_schema,
    ui_config,
    validation_rules,
    description,
    created_by,
    is_system_type
) VALUES (
    'pt_eco_resort',
    'Eco-Resort',
    'hospitality',
    '{
        "type": "object",
        "properties": {
            "sustainability_rating": {
                "type": "string",
                "enum": ["gold", "silver", "bronze", "certified"],
                "description": "Environmental certification level"
            },
            "renewable_energy_percentage": {
                "type": "number",
                "minimum": 0,
                "maximum": 100,
                "description": "Percentage of energy from renewable sources"
            },
            "water_conservation_features": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [
                        "rainwater_harvesting",
                        "greywater_recycling",
                        "low_flow_fixtures",
                        "native_landscaping"
                    ]
                },
                "description": "Water-saving systems installed"
            },
            "organic_garden": {
                "type": "boolean",
                "description": "Has organic vegetable/herb garden"
            },
            "carbon_offset_program": {
                "type": "boolean",
                "description": "Participates in carbon offset program"
            },
            "waste_management_score": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100,
                "description": "Waste reduction score (0-100)"
            },
            "eco_activities": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Eco-tourism activities offered"
            }
        },
        "required": ["sustainability_rating", "renewable_energy_percentage"]
    }',
    '{
        "icon": "eco",
        "color": "#4CAF50",
        "form_sections": [
            {
                "section": "Sustainability Certifications",
                "fields": ["sustainability_rating", "renewable_energy_percentage"]
            },
            {
                "section": "Conservation Features",
                "fields": ["water_conservation_features", "organic_garden", "carbon_offset_program"]
            },
            {
                "section": "Environmental Impact",
                "fields": ["waste_management_score", "eco_activities"]
            }
        ],
        "search_filters": [
            "sustainability_rating",
            "renewable_energy_percentage",
            "organic_garden"
        ]
    }',
    '{
        "min_renewable_energy": 30,
        "required_amenities": ["am_ext_solar_panels", "am_ext_garden"],
        "allowed_transaction_types": ["sale", "lease"]
    }',
    'Environmentally sustainable resort properties with eco-certifications',
    'user-uuid-here',
    false  -- User-created, not system type
) RETURNING id;

-- Step 2: Add to catalogue_options for UI selection
INSERT INTO catalogue_options (
    id,
    catalogue_id,
    name,
    description,
    icon,
    sort_order,
    metadata
) VALUES (
    'pt_eco_resort',
    'property_types',
    'Eco-Resort',
    'Sustainable resort with environmental certifications',
    'eco',
    160,
    '{"category": "hospitality", "dynamic": true}'
);

-- Step 3: Create a property with this type
INSERT INTO properties (
    title,
    property_type,
    property_type_definition_id,
    physical_specs,
    custom_fields,
    amenities_exterior
) VALUES (
    'Bamboo Beach Eco-Resort',
    'pt_eco_resort',
    (SELECT id FROM property_type_definitions WHERE type_code = 'pt_eco_resort'),
    '{
        "rooms": {"bedrooms": 12, "bathrooms": 12},
        "dimensions": {"total_area": {"value": 3000, "unit": "sqm"}}
    }',
    '{
        "sustainability_rating": "gold",
        "renewable_energy_percentage": 85,
        "water_conservation_features": ["rainwater_harvesting", "greywater_recycling"],
        "organic_garden": true,
        "carbon_offset_program": true,
        "waste_management_score": 92,
        "eco_activities": ["reef_restoration", "mangrove_planting", "wildlife_tours"]
    }',
    ARRAY['am_ext_solar_panels', 'am_ext_garden', 'am_ext_private_pool']
);
```

---

## Validation Strategy

### Three-Layer Validation

1. **PostgreSQL JSON Schema** (Database-level)
2. **Pydantic Models** (Application-level)
3. **Business Rules** (Service-level)

### 1. PostgreSQL JSON Schema Validation

```sql
-- Install extension
CREATE EXTENSION IF NOT EXISTS "pg_jsonschema";

-- Add check constraint using JSON Schema
ALTER TABLE properties
ADD CONSTRAINT validate_custom_fields
CHECK (
    CASE
        WHEN property_type_definition_id IS NULL THEN true
        ELSE validate_json_schema(
            (SELECT field_schema FROM property_type_definitions
             WHERE id = property_type_definition_id),
            custom_fields
        )
    END
);

-- Function to validate against type definition
CREATE OR REPLACE FUNCTION validate_property_custom_fields()
RETURNS TRIGGER AS $$
DECLARE
    type_schema JSONB;
BEGIN
    -- Get schema for this property type
    SELECT field_schema INTO type_schema
    FROM property_type_definitions
    WHERE id = NEW.property_type_definition_id;

    -- Validate custom_fields against schema
    IF NOT validate_json_schema(type_schema, NEW.custom_fields) THEN
        RAISE EXCEPTION 'custom_fields does not match type schema for %', NEW.property_type;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger
CREATE TRIGGER validate_custom_fields_trigger
BEFORE INSERT OR UPDATE ON properties
FOR EACH ROW
WHEN (NEW.property_type_definition_id IS NOT NULL)
EXECUTE FUNCTION validate_property_custom_fields();
```

### 2. Pydantic Application-Level Validation

```python
# server/schemas/property_type.py
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional
from uuid import UUID
import jsonschema

class PropertyTypeDefinition(BaseModel):
    """Meta-schema for custom property types"""
    id: UUID
    type_code: str = Field(..., regex=r'^pt_[a-z_]+$')
    type_name: str
    type_category: str
    field_schema: Dict[str, Any]
    ui_config: Dict[str, Any] = {}
    validation_rules: Dict[str, Any] = {}
    description: Optional[str]
    is_active: bool = True
    is_system_type: bool = False

    @validator('field_schema')
    def validate_json_schema(cls, v):
        """Ensure field_schema is valid JSON Schema"""
        try:
            # Check if it's a valid JSON Schema
            from jsonschema import Draft7Validator
            Draft7Validator.check_schema(v)
        except jsonschema.exceptions.SchemaError as e:
            raise ValueError(f"Invalid JSON Schema: {e}")
        return v

class PropertyWithCustomFields(BaseModel):
    """Property with dynamic custom fields"""
    # Core fields
    title: str
    property_type: str
    property_type_definition_id: Optional[UUID]

    # Dynamic fields
    custom_fields: Dict[str, Any] = {}

    # Physical specs (existing JSONB)
    physical_specs: Dict[str, Any] = {}
    location_details: Dict[str, Any] = {}

    @validator('custom_fields')
    def validate_custom_fields_against_type(cls, v, values):
        """Validate custom_fields against property type schema"""
        if 'property_type_definition_id' not in values:
            return v

        # Fetch type definition from DB (in real code, inject via dependency)
        # type_def = get_property_type_definition(values['property_type_definition_id'])
        # jsonschema.validate(instance=v, schema=type_def.field_schema)

        return v

# server/services/property_service.py
class PropertyService:
    async def validate_property_data(
        self,
        property_data: PropertyCreate,
        type_definition: PropertyTypeDefinition
    ) -> Dict[str, Any]:
        """Validate property against type definition"""

        # 1. JSON Schema validation
        try:
            jsonschema.validate(
                instance=property_data.custom_fields,
                schema=type_definition.field_schema
            )
        except jsonschema.ValidationError as e:
            raise ValueError(f"Custom fields validation failed: {e.message}")

        # 2. Business rules validation
        rules = type_definition.validation_rules

        # Check minimum price
        if 'min_price' in rules:
            if property_data.sale_price and property_data.sale_price < rules['min_price']:
                raise ValueError(f"Price must be at least {rules['min_price']}")

        # Check required amenities
        if 'required_amenities' in rules:
            missing = set(rules['required_amenities']) - set(property_data.amenities_exterior or [])
            if missing:
                raise ValueError(f"Missing required amenities: {missing}")

        # Check allowed regions
        if 'allowed_regions' in rules:
            region = property_data.location_details.get('region')
            if region and region not in rules['allowed_regions']:
                raise ValueError(f"Property type not allowed in region: {region}")

        return property_data.dict()
```

### 3. Business Rules Enforcement

```python
# server/services/property_type_service.py
class PropertyTypeService:
    """Service for managing dynamic property types"""

    async def create_property_type(
        self,
        type_data: PropertyTypeDefinitionCreate,
        created_by: UUID
    ) -> PropertyTypeDefinition:
        """Create new property type (LLM or admin)"""

        # Validate JSON Schema is valid
        try:
            from jsonschema import Draft7Validator
            Draft7Validator.check_schema(type_data.field_schema)
        except Exception as e:
            raise ValueError(f"Invalid JSON Schema: {e}")

        # Check type_code uniqueness
        existing = await self.repo.get_by_type_code(type_data.type_code)
        if existing:
            raise ValueError(f"Property type {type_data.type_code} already exists")

        # Validate UI config structure
        self._validate_ui_config(type_data.ui_config)

        # Create type definition
        type_def = await self.repo.create({
            **type_data.dict(),
            'created_by': created_by,
            'is_system_type': False
        })

        # Add to catalogue_options
        await self.catalogue_service.add_property_type_option(type_def)

        return type_def

    def _validate_ui_config(self, ui_config: Dict[str, Any]):
        """Validate UI configuration structure"""
        required_keys = ['icon', 'form_sections', 'search_filters']
        missing = set(required_keys) - set(ui_config.keys())
        if missing:
            raise ValueError(f"UI config missing keys: {missing}")
```

---

## LLM Integration

### How LLM Discovers Available Types

The LLM agent needs to introspect the schema to understand:
1. What property types exist
2. What fields are required for each type
3. What validation rules apply

### Schema Introspection API

```python
# server/api/v2/property_types.py
from fastapi import APIRouter, Depends
from typing import List

router = APIRouter(prefix="/api/v2/property-types", tags=["property-types"])

@router.get("/", response_model=List[PropertyTypeDefinitionPublic])
async def list_property_types(
    category: Optional[str] = None,
    is_active: bool = True,
    include_system: bool = True,
    service: PropertyTypeService = Depends()
):
    """
    List all available property types for LLM discovery.

    LLM uses this endpoint to understand schema before creating properties.
    """
    types = await service.list_types(
        category=category,
        is_active=is_active,
        include_system=include_system
    )
    return types

@router.get("/{type_code}/schema", response_model=PropertyTypeSchema)
async def get_property_type_schema(
    type_code: str,
    service: PropertyTypeService = Depends()
):
    """
    Get complete schema for a property type.

    Returns:
    - field_schema: JSON Schema definition
    - ui_config: UI rendering hints
    - validation_rules: Business rules
    - example: Sample valid data
    """
    type_def = await service.get_by_code(type_code)
    if not type_def:
        raise HTTPException(404, f"Property type {type_code} not found")

    # Generate example data
    example = generate_example_from_schema(type_def.field_schema)

    return {
        "type_code": type_def.type_code,
        "type_name": type_def.type_name,
        "field_schema": type_def.field_schema,
        "ui_config": type_def.ui_config,
        "validation_rules": type_def.validation_rules,
        "example": example
    }

@router.post("/", response_model=PropertyTypeDefinition)
async def create_property_type(
    type_data: PropertyTypeDefinitionCreate,
    current_user: User = Depends(get_current_user),
    service: PropertyTypeService = Depends()
):
    """
    Create new property type (admin or LLM agent).

    LLM can call this to create "Eco-Resort", "Co-living", etc.
    """
    # Check permissions (admin or LLM agent with property_type_creation permission)
    if not current_user.has_permission('create_property_types'):
        raise HTTPException(403, "Not authorized to create property types")

    return await service.create_property_type(type_data, current_user.id)

# Helper function
def generate_example_from_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Generate example data from JSON Schema"""
    example = {}

    for field, definition in schema.get('properties', {}).items():
        field_type = definition.get('type')

        if field_type == 'string':
            if 'enum' in definition:
                example[field] = definition['enum'][0]
            else:
                example[field] = f"example_{field}"
        elif field_type == 'number' or field_type == 'integer':
            example[field] = definition.get('minimum', 0)
        elif field_type == 'boolean':
            example[field] = True
        elif field_type == 'array':
            example[field] = []
        elif field_type == 'object':
            example[field] = {}

    return example
```

### LLM Prompt Integration

```python
# server/services/llm/property_agent.py
class PropertyChatAgent:
    """LLM agent for property creation via chat"""

    async def get_schema_context(self) -> str:
        """Generate schema context for LLM prompt"""

        # Fetch all property types
        types = await self.property_type_service.list_types(is_active=True)

        context = "# Available Property Types\n\n"

        for type_def in types:
            context += f"## {type_def.type_name} ({type_def.type_code})\n"
            context += f"{type_def.description}\n\n"
            context += f"**Category:** {type_def.type_category}\n\n"
            context += "**Required Fields:**\n"

            required = type_def.field_schema.get('required', [])
            properties = type_def.field_schema.get('properties', {})

            for field in required:
                field_def = properties.get(field, {})
                context += f"- `{field}`: {field_def.get('description', '')}\n"

            context += "\n**Optional Fields:**\n"
            optional = set(properties.keys()) - set(required)
            for field in optional:
                field_def = properties.get(field, {})
                context += f"- `{field}`: {field_def.get('description', '')}\n"

            context += "\n---\n\n"

        return context

    async def create_property_from_chat(
        self,
        user_message: str,
        chat_history: List[Dict],
        user_id: UUID
    ) -> Dict[str, Any]:
        """Create property from natural language description"""

        # Get schema context
        schema_context = await self.get_schema_context()

        # Build prompt
        prompt = f"""
{schema_context}

# User Request
{user_message}

# Your Task
Extract property information and create a structured property listing.

1. Determine the best property type from available types
2. Extract all required fields
3. Extract optional fields where information is available
4. If property doesn't fit any type, suggest creating a new type

Output JSON in this format:
{{
    "property_type": "pt_xxx",
    "core_fields": {{
        "title": "...",
        "description": "...",
        ...
    }},
    "custom_fields": {{
        ...
    }}
}}
"""

        # Call LLM
        response = await self.llm.complete(prompt, chat_history)

        # Parse and validate
        property_data = json.loads(response)

        # Validate against schema
        type_def = await self.property_type_service.get_by_code(
            property_data['property_type']
        )

        validated = await self.property_service.validate_property_data(
            property_data,
            type_def
        )

        # Create property
        property = await self.property_service.create(validated, user_id)

        return property
```

### Sync Mechanism

**Real-time sync:** LLM fetches schema on each property creation
**Caching:** Cache schema for 5 minutes, invalidate on type creation/update
**Webhook:** Notify LLM when new types are added (future)

```python
# Cache schema with TTL
@lru_cache(ttl=300)  # 5 minutes
async def get_cached_schema_context() -> str:
    return await property_type_service.get_schema_context()

# Invalidate cache on type creation
@router.post("/property-types/")
async def create_type(...):
    result = await service.create(...)
    get_cached_schema_context.cache_clear()  # Invalidate
    return result
```

---

## Performance Considerations

### Query Patterns

**Common queries for dynamic types:**

1. **List properties by custom field value**
```sql
-- Find all eco-resorts with gold rating
SELECT * FROM properties
WHERE property_type = 'pt_eco_resort'
  AND custom_fields->>'sustainability_rating' = 'gold';

-- With GIN index (good performance)
SELECT * FROM properties
WHERE property_type = 'pt_eco_resort'
  AND custom_fields @> '{"sustainability_rating": "gold"}';
```

2. **Filter by multiple custom fields**
```sql
-- Eco-resorts with gold rating AND >80% renewable energy
SELECT * FROM properties
WHERE property_type = 'pt_eco_resort'
  AND custom_fields @> '{
    "sustainability_rating": "gold",
    "renewable_energy_percentage": 80
  }';
```

3. **Search across all property types**
```sql
-- All properties with organic garden (regardless of type)
SELECT * FROM properties
WHERE custom_fields @> '{"organic_garden": true}';
```

### Index Strategy

```sql
-- 1. GIN index on custom_fields (already created)
CREATE INDEX idx_properties_custom_fields ON properties USING GIN(custom_fields);

-- 2. Composite index for common filters
CREATE INDEX idx_properties_type_custom ON properties(property_type)
INCLUDE (custom_fields)
WHERE property_type_definition_id IS NOT NULL;

-- 3. Expression indexes for specific fields
CREATE INDEX idx_properties_eco_rating ON properties(
    (custom_fields->>'sustainability_rating')
)
WHERE property_type = 'pt_eco_resort';

-- 4. Partial index for active dynamic types
CREATE INDEX idx_properties_dynamic_active ON properties
USING GIN(custom_fields)
WHERE property_type_definition_id IS NOT NULL
  AND status = 'active';
```

### Materialized Views (If Needed)

For frequently accessed custom field queries:

```sql
-- Materialized view for eco-resort search
CREATE MATERIALIZED VIEW eco_resort_search AS
SELECT
    p.id,
    p.title,
    p.property_type,
    p.custom_fields->>'sustainability_rating' AS rating,
    (p.custom_fields->>'renewable_energy_percentage')::numeric AS renewable_pct,
    p.custom_fields->'water_conservation_features' AS water_features,
    p.location_lat,
    p.location_lng,
    p.created_at
FROM properties p
WHERE p.property_type = 'pt_eco_resort'
  AND p.status = 'active';

-- Index on materialized view
CREATE INDEX idx_eco_resort_rating ON eco_resort_search(rating);
CREATE INDEX idx_eco_resort_renewable ON eco_resort_search(renewable_pct);

-- Refresh strategy
REFRESH MATERIALIZED VIEW CONCURRENTLY eco_resort_search;
```

### Performance Benchmarks

**Target performance with 10,000 properties (1,000 dynamic types):**

- **List by type:** < 50ms
- **Filter by 1 custom field:** < 100ms
- **Filter by 3 custom fields:** < 200ms
- **Full-text search + custom filters:** < 500ms
- **Create property (with validation):** < 300ms
- **Fetch type schema:** < 10ms (cached)

### Optimization Checklist

- ✅ Use GIN indexes on JSONB columns
- ✅ Create partial indexes for common property types
- ✅ Cache type schemas at application level
- ✅ Use prepared statements for common queries
- ✅ Consider materialized views for analytics
- ⚠️ Monitor JSONB query performance
- ⚠️ Add expression indexes if specific fields are hot
- ⚠️ Use `EXPLAIN ANALYZE` to validate query plans

---

## Code Example

### Create New Property Type Function

```python
# server/services/property_type_service.py
from typing import Dict, Any, List
from uuid import UUID
import jsonschema
from jsonschema import Draft7Validator

class PropertyTypeService:
    """Service for creating and managing dynamic property types"""

    async def create_property_type_from_description(
        self,
        type_name: str,
        description: str,
        category: str,
        custom_fields: List[Dict[str, Any]],
        validation_rules: Dict[str, Any],
        created_by: UUID
    ) -> PropertyTypeDefinition:
        """
        Create a new property type dynamically.

        This is the function LLM agents call to create types like "Eco-Resort".

        Args:
            type_name: Human-readable name (e.g., "Eco-Resort")
            description: What this property type represents
            category: 'hospitality', 'residential', 'commercial', etc.
            custom_fields: List of field definitions
                [
                    {
                        "name": "sustainability_rating",
                        "type": "string",
                        "description": "Eco certification level",
                        "enum": ["gold", "silver", "bronze"],
                        "required": true
                    },
                    ...
                ]
            validation_rules: Business rules
                {
                    "min_price": 50000,
                    "required_amenities": ["am_ext_solar_panels"]
                }
            created_by: User/agent creating this type

        Returns:
            PropertyTypeDefinition: Created type with generated schema
        """

        # 1. Generate type_code from name
        type_code = self._generate_type_code(type_name)

        # 2. Build JSON Schema from field definitions
        field_schema = self._build_json_schema(custom_fields)

        # 3. Validate the generated schema
        try:
            Draft7Validator.check_schema(field_schema)
        except jsonschema.exceptions.SchemaError as e:
            raise ValueError(f"Generated invalid JSON Schema: {e}")

        # 4. Build UI configuration
        ui_config = self._build_ui_config(type_name, custom_fields)

        # 5. Check for conflicts
        existing = await self.repo.get_by_type_code(type_code)
        if existing:
            raise ValueError(
                f"Property type '{type_code}' already exists. "
                f"Use a more specific name or modify existing type."
            )

        # 6. Create type definition
        type_def_data = {
            'type_code': type_code,
            'type_name': type_name,
            'type_category': category,
            'field_schema': field_schema,
            'ui_config': ui_config,
            'validation_rules': validation_rules,
            'description': description,
            'created_by': created_by,
            'is_system_type': False,
            'is_active': True
        }

        type_def = await self.repo.create(type_def_data)

        # 7. Add to catalogue_options for UI
        await self._add_to_catalogue(type_def)

        # 8. Clear schema cache
        self._invalidate_schema_cache()

        return type_def

    def _generate_type_code(self, type_name: str) -> str:
        """Generate type_code from name: 'Eco-Resort' -> 'pt_eco_resort'"""
        import re
        # Remove special chars, lowercase, replace spaces with underscores
        code = re.sub(r'[^a-zA-Z0-9\s]', '', type_name)
        code = code.lower().replace(' ', '_')
        return f"pt_{code}"

    def _build_json_schema(self, fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert field definitions to JSON Schema"""
        properties = {}
        required = []

        for field in fields:
            field_name = field['name']
            field_type = field['type']

            # Build property definition
            prop_def = {
                'type': field_type,
                'description': field.get('description', '')
            }

            # Add constraints
            if 'enum' in field:
                prop_def['enum'] = field['enum']

            if field_type in ['number', 'integer']:
                if 'minimum' in field:
                    prop_def['minimum'] = field['minimum']
                if 'maximum' in field:
                    prop_def['maximum'] = field['maximum']

            if field_type == 'string':
                if 'min_length' in field:
                    prop_def['minLength'] = field['min_length']
                if 'max_length' in field:
                    prop_def['maxLength'] = field['max_length']
                if 'pattern' in field:
                    prop_def['pattern'] = field['pattern']

            if field_type == 'array':
                prop_def['items'] = field.get('items', {'type': 'string'})

            properties[field_name] = prop_def

            # Track required fields
            if field.get('required', False):
                required.append(field_name)

        return {
            'type': 'object',
            'properties': properties,
            'required': required
        }

    def _build_ui_config(
        self,
        type_name: str,
        fields: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate UI configuration"""

        # Group fields into sections
        sections = []
        current_section = {
            'section': 'General',
            'fields': []
        }

        for field in fields:
            current_section['fields'].append(field['name'])

            # Start new section every 5 fields
            if len(current_section['fields']) >= 5:
                sections.append(current_section)
                current_section = {
                    'section': f'Additional Details {len(sections) + 1}',
                    'fields': []
                }

        if current_section['fields']:
            sections.append(current_section)

        # Determine icon and color based on category
        icon_map = {
            'hospitality': 'hotel',
            'residential': 'home',
            'commercial': 'business',
            'eco': 'eco',
            'luxury': 'star'
        }

        color_map = {
            'hospitality': '#2196F3',
            'residential': '#4CAF50',
            'commercial': '#FF9800',
            'eco': '#4CAF50',
            'luxury': '#9C27B0'
        }

        # Detect category from name/description
        icon = 'category'
        color = '#607D8B'
        for key, val in icon_map.items():
            if key in type_name.lower():
                icon = val
                color = color_map[key]
                break

        # Search filters: all enum fields + required fields
        search_filters = [
            f['name'] for f in fields
            if 'enum' in f or f.get('required', False)
        ][:5]  # Max 5 filters

        return {
            'icon': icon,
            'color': color,
            'form_sections': sections,
            'search_filters': search_filters
        }

    async def _add_to_catalogue(self, type_def: PropertyTypeDefinition):
        """Add new type to catalogue_options"""
        await self.catalogue_repo.create_option({
            'id': type_def.type_code,
            'catalogue_id': 'property_types',
            'name': type_def.type_name,
            'description': type_def.description,
            'icon': type_def.ui_config.get('icon', 'category'),
            'sort_order': 1000,  # Put dynamic types at end
            'metadata': {
                'category': type_def.type_category,
                'dynamic': True,
                'color': type_def.ui_config.get('color')
            }
        })

    def _invalidate_schema_cache(self):
        """Clear cached schemas after type creation"""
        # Implementation depends on caching strategy
        # Redis: await redis.delete('property_types:schema:*')
        # In-memory: cache.clear()
        pass


# Example usage
async def example_create_eco_resort_type():
    """Example: LLM agent creates 'Eco-Resort' property type"""

    service = PropertyTypeService(...)

    type_def = await service.create_property_type_from_description(
        type_name="Eco-Resort",
        description="Environmentally sustainable resort with eco-certifications",
        category="hospitality",
        custom_fields=[
            {
                "name": "sustainability_rating",
                "type": "string",
                "description": "Environmental certification level",
                "enum": ["gold", "silver", "bronze", "certified"],
                "required": True
            },
            {
                "name": "renewable_energy_percentage",
                "type": "number",
                "description": "% of energy from renewable sources",
                "minimum": 0,
                "maximum": 100,
                "required": True
            },
            {
                "name": "water_conservation_features",
                "type": "array",
                "description": "Water-saving systems",
                "items": {
                    "type": "string",
                    "enum": [
                        "rainwater_harvesting",
                        "greywater_recycling",
                        "low_flow_fixtures",
                        "native_landscaping"
                    ]
                },
                "required": False
            },
            {
                "name": "organic_garden",
                "type": "boolean",
                "description": "Has organic vegetable garden",
                "required": False
            },
            {
                "name": "carbon_offset_program",
                "type": "boolean",
                "description": "Participates in carbon offset",
                "required": False
            }
        ],
        validation_rules={
            "min_renewable_energy": 30,
            "required_amenities": ["am_ext_solar_panels"],
            "allowed_transaction_types": ["sale", "lease"]
        },
        created_by=UUID("user-uuid-here")
    )

    print(f"Created property type: {type_def.type_code}")
    print(f"Schema: {type_def.field_schema}")
```

---

## MVP Recommendation

### Should Dynamic Types Be in MVP?

**Recommendation: NO - Defer to Phase 2**

### Reasoning

1. **Ship Fast**
   - Current 5 static subdomains cover 95%+ of real estate properties
   - Focus on proving chat-based property creation works
   - Avoid over-engineering before validation

2. **Technical Complexity**
   - Dynamic types add significant validation complexity
   - Need robust testing before production
   - Schema introspection API needs design time

3. **Business Validation Needed**
   - Unclear if users actually need custom types
   - May be solving a non-problem
   - Better to hear user requests first

4. **Risk Mitigation**
   - Don't give LLM schema mutation power on day 1
   - Need monitoring and safety rails
   - Learn from static schema usage first

### When to Add Dynamic Types?

**Trigger conditions:**

✅ Add dynamic types when:
- Users request 3+ property types not in static schema
- Manual code deploys become bottleneck (>1 per week for new types)
- Business model pivots to multi-vertical (beyond real estate)
- LLM chat proves reliable and safe with static schema

❌ Don't add if:
- Static schema handles all requests
- User adoption is low
- Team velocity can handle occasional type additions

### Can We Defer and Start Static?

**YES - This is the recommended path**

**MVP (Phase 1): Static Schema**
```
Timeline: Weeks 1-8
Deliverables:
- 5 static subdomains (rental, sale, lease, business, investment)
- 15 static property types (house, villa, condo, etc.)
- JSONB for physical_specs, location_details, amenities
- Chat-based property creation (LLM fills static fields)
- Catalogue system for 165+ amenities
```

**Phase 2: Add Dynamic Types**
```
Timeline: Weeks 9-12 (if needed)
Triggers:
- User requests for new types accumulate
- Product-market fit validated
- Team has bandwidth for meta-schema

Deliverables:
- property_type_definitions table
- JSON Schema validation layer
- Schema introspection API
- LLM type creation capability
- Migration of static types to definitions
```

### Migration Path

When moving from static to dynamic:

1. **Create meta-schema tables** (property_type_definitions)
2. **Migrate existing types** to definitions (preserve data)
3. **Add custom_fields column** to properties
4. **Update validation** to check type definitions
5. **Expose API** for LLM introspection
6. **Enable LLM creation** with admin approval workflow

**Key principle:** Existing code keeps working, dynamic types are additive.

---

## Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **LLM creates invalid schemas** | High - Breaks validation | Medium | ✅ Multi-layer validation<br>✅ JSON Schema validation<br>✅ Admin approval workflow<br>✅ Sandbox environment for testing |
| **Query performance degrades** | High - Slow search | Medium | ✅ GIN indexes on JSONB<br>✅ Materialized views for hot queries<br>✅ Performance monitoring<br>✅ Query plan analysis |
| **Schema proliferation** | Medium - Too many types | High | ✅ Admin review before activation<br>✅ Merge similar types<br>✅ Archive unused types<br>✅ Type usage analytics |
| **Data inconsistency** | High - Invalid data stored | Low | ✅ PostgreSQL constraints<br>✅ Trigger-based validation<br>✅ Pydantic models<br>✅ Regular data audits |
| **UI rendering breaks** | Medium - Bad UX | Medium | ✅ UI config validation<br>✅ Fallback to generic form<br>✅ Frontend error boundaries<br>✅ Type preview before publish |
| **Migration complexity** | Medium - Downtime risk | Low | ✅ Dual-write period<br>✅ Rollback procedures<br>✅ Staging validation<br>✅ Gradual rollout |
| **LLM hallucinations** | High - Wrong field types | Medium | ✅ Schema validation at creation<br>✅ Example-based prompts<br>✅ Human-in-loop approval<br>✅ Type versioning |
| **Security: Type injection** | High - Malicious schemas | Low | ✅ Sanitize type_code/names<br>✅ Regex validation<br>✅ Permission checks<br>✅ Audit logging |
| **Catalog sync issues** | Low - Type not in dropdown | Low | ✅ Transactional creation<br>✅ Sync verification<br>✅ Cache invalidation |
| **Type deletion cascade** | High - Data loss | Low | ✅ Soft delete only<br>✅ Archive instead of delete<br>✅ Orphan detection<br>✅ Backup before operations |

### Critical Path Risks

**Highest Priority (Address in Phase 2 Design):**

1. **LLM Schema Quality**
   - Risk: LLM generates unusable/confusing schemas
   - Mitigation: Provide schema templates, validate against examples

2. **Performance at Scale**
   - Risk: JSONB queries slow down with 100+ dynamic types
   - Mitigation: Benchmark early, optimize indexes, consider partitioning

3. **Type Governance**
   - Risk: 50+ similar types created (confusion)
   - Mitigation: Admin approval, type merging tools, analytics

### Rollback Strategy

If dynamic types cause issues:

1. **Disable LLM type creation** (feature flag)
2. **Archive problematic types** (soft delete)
3. **Migrate dynamic properties** to closest static type
4. **Revert custom_fields** to metadata column
5. **Remove meta-schema tables** (after data migration)

---

## Appendix: Alternative Patterns Considered

### Pattern: PostgreSQL Composite Types

```sql
CREATE TYPE eco_resort_fields AS (
    sustainability_rating VARCHAR(20),
    renewable_energy_pct NUMERIC(5,2),
    water_features TEXT[]
);

ALTER TABLE properties ADD COLUMN eco_resort_data eco_resort_fields;
```

**Rejected because:**
- Requires DDL for each new type (same problem as tables)
- Poor tooling support in ORMs
- Hard to make dynamic

### Pattern: Graph Database (Neo4j)

Store property types as nodes with dynamic edges.

**Rejected because:**
- Major architecture change
- Team expertise in PostgreSQL
- Overkill for this problem
- Added operational complexity

### Pattern: Multi-Tenancy with Type Isolation

Separate schema per property type category.

**Rejected because:**
- Cross-type queries become impossible
- Increases operational burden
- Doesn't solve dynamic creation problem

---

## Conclusion

**For MVP:** Ship static schema (Option C - Hybrid, static mode)
- Fastest path to market
- Handles 95%+ of cases
- Low risk, high confidence

**For Future (Phase 2):** Add dynamic types when validated
- Use property_type_definitions table
- JSONB + JSON Schema validation
- LLM introspection API
- Admin approval workflow

**Key Success Metrics:**
- User requests for new types > 3 per month
- Static schema deployment cadence > 1 per week
- Product-market fit validated
- Team bandwidth available

**Don't over-engineer.** Start simple, add complexity when business need is proven.

---

**Document Version:** 1.0
**Last Updated:** 2025-11-06
**Author:** Claude (System Architect)
**Status:** Ready for Review
**Next Steps:** Review with stakeholders → Decide on Phase 2 timeline → Update implementation roadmap

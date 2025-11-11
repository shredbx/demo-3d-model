# US-016: Property Migration Strategy Design

**Status:** Design Phase
**Created:** 2025-11-06
**Category:** Properties
**Priority:** High
**Estimated Effort:** 4 weeks

---

## Executive Summary

This document provides a comprehensive migration strategy for transferring property data from the old NextJS/Supabase application to our new FastAPI/PostgreSQL stack. The migration adopts the battle-tested **Property2 (V2) schema** from the old system with adaptations for our **company-owned business model** (removing agent-centric fields, adding employee accountability tracking).

**Key Decision:** We will **adopt and adapt** the V2 schema rather than mapping to our existing polymorphic schema, because V2 is production-ready with 150+ amenities, 6-language translation support, and proven global real estate marketplace design.

**Migration Approach:** Dual-phase strategy
- **Phase 1:** Export/Import (development and testing)
- **Phase 2:** Direct database connection (production migration)

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Schema Adaptations](#schema-adaptations)
3. [Migration Scripts](#migration-scripts)
4. [Data Flow & Processing](#data-flow--processing)
5. [Error Handling & Rollback](#error-handling--rollback)
6. [Testing Strategy](#testing-strategy)
7. [Implementation Timeline](#implementation-timeline)
8. [Risk Assessment](#risk-assessment)
9. [Production Migration Checklist](#production-migration-checklist)
10. [Code Templates](#code-templates)

---

## Architecture Overview

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MIGRATION ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────────┘

Phase 1: Export/Import (Development)
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Supabase   │────▶│   Export     │────▶│  Transform   │────▶│  PostgreSQL  │
│  (Property2) │     │   Script     │     │   Script     │     │   (Bestays)  │
│              │     │              │     │              │     │              │
│ - REST API   │     │ - Paginated  │     │ - Field Map  │     │ - Batch      │
│ - Rate Limit │     │ - JSON Files │     │ - Validate   │     │   Insert     │
│              │     │ - Progress   │     │ - Company    │     │ - Foreign    │
│              │     │   Tracking   │     │   Model      │     │   Keys       │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                             │                    │                    │
                             ▼                    ▼                    ▼
                     properties.json      transformed.json      database rows


Phase 2: Direct Connection (Production)
┌──────────────┐                                              ┌──────────────┐
│   Supabase   │─────────────────────────────────────────────▶│  PostgreSQL  │
│  PostgreSQL  │        Direct Database Connection             │   (Bestays)  │
│              │                                               │              │
│ - Port 5432  │     ┌────────────────────────────┐           │ - Port 5433  │
│ - SSL Req    │────▶│  supabase_direct.py        │──────────▶│              │
│ - Cursor     │     │                            │           │              │
│   Streaming  │     │ - Stream rows (500/batch)  │           │              │
│              │     │ - Transform inline         │           │              │
│              │     │ - Resume capability        │           │              │
│              │     │ - Progress tracking        │           │              │
└──────────────┘     └────────────────────────────┘           └──────────────┘
                                  │
                                  ▼
                     ┌─────────────────────────┐
                     │  migration_state table  │
                     │  - last_processed_id    │
                     │  - progress metrics     │
                     │  - error log            │
                     └─────────────────────────┘
```

### Data Flow

1. **Source:** Supabase PostgreSQL database (`bestays_properties_v2` table + `bestays_property_translations`)
2. **Transformation Layer:** Python scripts with field mapping and validation
3. **Target:** Local PostgreSQL database (adapted V2 schema with company model)

### Key Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Export** | Fetch properties from Supabase | `supabase-py` client |
| **Transform** | Map fields, validate data | Python + Pydantic |
| **Import** | Batch insert to PostgreSQL | `asyncpg` + SQLAlchemy |
| **Direct** | Stream migration for production | `psycopg2` with cursors |
| **State** | Track progress, resume capability | PostgreSQL table |

---

## Schema Adaptations

### Overview

The V2 schema is **comprehensive and production-ready** with:
- **60+ columns** (core fields + system fields)
- **5 JSONB fields** (physical_specs, location_details, amenities, policies, contact_info)
- **Translation table** (6 languages × 13 fields)
- **15 property types**, 4 transaction types, 150+ amenities
- **12 strategic indexes** for performance

We will **adopt this schema** with modifications for the **company-owned model**.

---

### Company Model Adaptations

#### Fields to REMOVE (Agent-Centric Model)

| Field | Reason |
|-------|--------|
| `agent_id` | Replaced by `created_by` (agents are employees) |
| `owner_id` | Not needed (company owns all properties) |
| `agency_name` | Not needed (single company) |

#### Fields to ADD (Company Accountability)

| Field | Type | Purpose | Default |
|-------|------|---------|---------|
| `created_by` | UUID | Which employee created this property | Required (FK → users) |
| `updated_by` | UUID | Last employee to edit | Updated on each change |
| `published_by` | UUID | Who made it live | Set when is_published=true |
| `department` | VARCHAR(50) | sales, rentals, commercial | Inferred from transaction_type |
| `internal_notes` | TEXT | Private company notes (not public) | Empty |
| `commission_rate` | DECIMAL(5,2) | Agent compensation % (e.g., 2.50) | From config (default 2.5) |

#### Department Inference Rules

```python
def infer_department(property_type: str, transaction_type: str) -> str:
    """
    Infer department from property characteristics.

    Rules:
    - rent → rentals
    - sale/sale-lease → sales
    - office/warehouse/business → commercial
    - default → sales
    """
    if transaction_type == "rent":
        return "rentals"
    elif transaction_type in ("sale", "sale-lease"):
        return "sales"
    elif property_type in ("office", "warehouse", "business"):
        return "commercial"
    else:
        return "sales"  # Default fallback
```

---

### Modified Schema DDL

```sql
-- Create department enum
CREATE TYPE property_department AS ENUM ('sales', 'rentals', 'commercial');

-- Modified properties table (based on V2)
CREATE TABLE bestays_properties_v2 (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Basic Information (same as V2)
    title VARCHAR(200) NOT NULL,
    description TEXT CHECK (char_length(description) <= 5000),
    title_deed VARCHAR(100),

    -- Pricing (same as V2)
    sale_price BIGINT,
    rent_price BIGINT,
    lease_price BIGINT,
    currency VARCHAR(3) DEFAULT 'THB' CHECK (currency IN ('THB', 'USD', 'EUR')),
    price_per_unit DECIMAL(10,2),

    -- Classification (same as V2)
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('sale', 'rent', 'lease', 'sale-lease')),
    property_type VARCHAR(50) NOT NULL CHECK (property_type IN (
        'land', 'house', 'villa', 'pool-villa', 'apartment', 'condo',
        'townhouse', 'penthouse', 'office', 'shop', 'warehouse',
        'business', 'resort', 'hotel', 'other'
    )),

    -- JSONB Fields (same as V2)
    physical_specs JSONB DEFAULT '{}',
    location_details JSONB DEFAULT '{}',
    amenities JSONB DEFAULT '{}',
    policies JSONB DEFAULT '{}',
    contact_info JSONB DEFAULT '{}',  -- Will transform: remove agent-specific

    -- Media (same as V2)
    cover_image JSONB,
    images JSONB[],
    virtual_tour_url TEXT,
    video_url TEXT,

    -- Visibility (same as V2)
    is_published BOOLEAN DEFAULT false,
    is_featured BOOLEAN DEFAULT false,
    listing_priority INTEGER DEFAULT 0,

    -- Legal (same as V2)
    ownership_type VARCHAR(20) CHECK (ownership_type IN ('freehold', 'leasehold', 'company')),
    foreign_quota BOOLEAN DEFAULT false,

    -- Investment (same as V2)
    rental_yield DECIMAL(5,2),
    price_trend VARCHAR(10) CHECK (price_trend IN ('rising', 'stable', 'falling')),

    -- SEO (same as V2)
    seo_title VARCHAR(60),
    seo_description VARCHAR(160),
    tags TEXT[],

    -- ============================================
    -- COMPANY MODEL ADAPTATIONS (NEW FIELDS)
    -- ============================================
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    updated_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    published_by UUID REFERENCES users(id) ON DELETE SET NULL,
    department property_department NOT NULL DEFAULT 'sales',
    internal_notes TEXT,
    commission_rate DECIMAL(5,2) DEFAULT 2.50 CHECK (commission_rate >= 0 AND commission_rate <= 100),

    -- System Fields (same as V2)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,  -- Soft delete

    -- Legacy (same as V2)
    legacy_land_size DECIMAL(10,2),
    legacy_land_size_unit VARCHAR(10),
    legacy_metadata JSONB
);

-- Indexes (same as V2 + new ones for company fields)
CREATE INDEX idx_properties_published ON bestays_properties_v2(is_published) WHERE deleted_at IS NULL;
CREATE INDEX idx_properties_transaction ON bestays_properties_v2(transaction_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_properties_type ON bestays_properties_v2(property_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_properties_created_by ON bestays_properties_v2(created_by);
CREATE INDEX idx_properties_department ON bestays_properties_v2(department);
CREATE INDEX idx_properties_deleted ON bestays_properties_v2(deleted_at);
CREATE INDEX idx_properties_featured ON bestays_properties_v2(is_featured) WHERE is_featured = true;
CREATE INDEX idx_properties_priority ON bestays_properties_v2(listing_priority DESC);
CREATE INDEX idx_properties_location ON bestays_properties_v2 USING GIN(location_details);
CREATE INDEX idx_properties_physical ON bestays_properties_v2 USING GIN(physical_specs);
CREATE INDEX idx_properties_amenities ON bestays_properties_v2 USING GIN(amenities);
CREATE INDEX idx_properties_tags ON bestays_properties_v2 USING GIN(tags);

-- Translation table (same as V2)
CREATE TABLE bestays_property_translations (
    id SERIAL PRIMARY KEY,
    property_id UUID NOT NULL REFERENCES bestays_properties_v2(id) ON DELETE CASCADE,
    lang_code CHAR(2) NOT NULL CHECK (lang_code IN ('en', 'th', 'ru', 'zh', 'de', 'fr')),
    field VARCHAR(100) NOT NULL,
    value TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(property_id, lang_code, field)
);

CREATE INDEX idx_translations_property ON bestays_property_translations(property_id);
CREATE INDEX idx_translations_lang ON bestays_property_translations(lang_code);

-- Migration state tracking table
CREATE TABLE migration_state (
    id SERIAL PRIMARY KEY,
    migration_name VARCHAR(100) UNIQUE NOT NULL,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status VARCHAR(20) CHECK (status IN ('running', 'completed', 'failed', 'paused')) DEFAULT 'running',
    last_processed_id UUID,
    total_count INTEGER,
    processed_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    error_log JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}'
);
```

---

### Field Mapping Table

| Old Field (V2) | New Field | Transformation | Notes |
|----------------|-----------|----------------|-------|
| `id` | `id` | Direct copy | UUID preserved |
| `title` | `title` | Direct copy | - |
| `description` | `description` | Direct copy | - |
| `agent_id` | `created_by` | **Map to users table OR default admin** | Lookup user by Clerk ID |
| `owner_id` | ❌ Removed | - | Not needed (company owns all) |
| `agency_name` | ❌ Removed | - | Not needed (single company) |
| - | `created_by` | **NEW** | Map from agent_id or default |
| - | `updated_by` | **NEW** | Same as created_by initially |
| - | `published_by` | **NEW** | Set if is_published=true |
| - | `department` | **NEW** | Infer from transaction_type/property_type |
| - | `internal_notes` | **NEW** | Empty string |
| - | `commission_rate` | **NEW** | From config (default 2.5) |
| `physical_specs` | `physical_specs` | Direct copy (JSONB) | Validate structure |
| `location_details` | `location_details` | Direct copy (JSONB) | Validate structure |
| `amenities` | `amenities` | Direct copy (JSONB) | Validate structure |
| `policies` | `policies` | Direct copy (JSONB) | Validate structure |
| `contact_info` | `contact_info` | **Transform** | Remove agent-specific, add company contact |
| All other fields | Same | Direct copy | Validate enums and constraints |

---

### JSONB Transformation: contact_info

**Old Structure (Agent-Centric):**
```json
{
  "agent_name": "John Doe",
  "agent_phone": "+66812345678",
  "agent_email": "john@example.com",
  "agent_line_id": "johnagent",
  "agent_whatsapp_id": "+66812345678",
  "agency_name": "Some Agency",
  "languages_spoken": ["English", "Thai"],
  "preferred_contact": "whatsapp",
  "availability_hours": "24h"
}
```

**New Structure (Company-Centric):**
```json
{
  "company_name": "Bestays Realty",
  "company_phone": "+66812345678",
  "company_email": "info@bestays.app",
  "company_line_id": "bestays_official",
  "company_whatsapp": "+66812345678",
  "languages_spoken": ["English", "Thai", "Russian", "Chinese"],
  "preferred_contact": "whatsapp",
  "availability_hours": "Mon-Fri 9am-6pm",
  "department": "sales"  // or "rentals" or "commercial"
}
```

**Transformation Logic:**
```python
def transform_contact_info(old_contact: dict, department: str) -> dict:
    """Transform agent-centric contact to company-centric."""
    return {
        "company_name": "Bestays Realty",
        "company_phone": "+66812345678",  # From config
        "company_email": "info@bestays.app",  # From config
        "company_line_id": "bestays_official",
        "company_whatsapp": "+66812345678",
        "languages_spoken": old_contact.get("languages_spoken", ["English", "Thai"]),
        "preferred_contact": old_contact.get("preferred_contact", "email"),
        "availability_hours": "Mon-Fri 9am-6pm",
        "department": department
    }
```

---

## Migration Scripts

### Overview

Four specialized scripts for different migration phases:

| Script | Phase | Purpose | Use Case |
|--------|-------|---------|----------|
| **supabase_export.py** | 1 | Export via REST API | Development, testing |
| **transform_properties.py** | 1 | Transform and validate | Development, testing |
| **import_properties.py** | 1 | Batch import to PostgreSQL | Development, testing |
| **supabase_direct.py** | 2 | Direct DB migration | Production, one-time |

---

### Script 1: supabase_export.py

**Purpose:** Export properties from Supabase using REST API (paginated)

**Features:**
- Paginated queries (avoid memory issues)
- Export to JSON files (chunked)
- Progress tracking
- Include translations
- Error handling

**Usage:**
```bash
python scripts/migration/supabase_export.py \
  --output-dir data/exports/ \
  --batch-size 500 \
  --include-translations
```

**Output:**
```
data/exports/
├── properties_batch_001.json  (properties 1-500)
├── properties_batch_002.json  (properties 501-1000)
├── ...
├── translations.json          (all translations)
└── export_metadata.json       (counts, timestamp)
```

**Code Template:**
```python
"""
Export properties from Supabase to JSON files.

Usage:
    python supabase_export.py --output-dir data/exports/ --batch-size 500
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from supabase import create_client, Client
import click

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SupabaseExporter:
    """Export properties from Supabase."""

    def __init__(self, supabase_url: str, supabase_key: str):
        self.client: Client = create_client(supabase_url, supabase_key)
        self.table = "bestays_properties_v2"

    def count_properties(self) -> int:
        """Count total properties (excluding soft-deleted)."""
        response = self.client.table(self.table) \
            .select("id", count="exact") \
            .is_("deleted_at", "null") \
            .execute()
        return response.count

    def export_batch(self, offset: int, limit: int) -> List[Dict[str, Any]]:
        """Export a batch of properties."""
        response = self.client.table(self.table) \
            .select("*") \
            .is_("deleted_at", "null") \
            .range(offset, offset + limit - 1) \
            .execute()

        return response.data

    def export_translations(self, property_ids: List[str]) -> List[Dict[str, Any]]:
        """Export translations for given property IDs."""
        response = self.client.table("bestays_property_translations") \
            .select("*") \
            .in_("property_id", property_ids) \
            .execute()

        return response.data

    def export_all(
        self,
        output_dir: Path,
        batch_size: int = 500,
        include_translations: bool = True
    ):
        """Export all properties in batches."""
        output_dir.mkdir(parents=True, exist_ok=True)

        total = self.count_properties()
        logger.info(f"Total properties to export: {total}")

        batch_num = 1
        offset = 0
        all_property_ids = []

        while offset < total:
            logger.info(f"Exporting batch {batch_num} (offset {offset})...")

            try:
                batch = self.export_batch(offset, batch_size)

                if not batch:
                    break

                # Save batch to file
                batch_file = output_dir / f"properties_batch_{batch_num:03d}.json"
                with open(batch_file, 'w', encoding='utf-8') as f:
                    json.dump(batch, f, indent=2, default=str)

                all_property_ids.extend([p['id'] for p in batch])

                logger.info(f"✓ Batch {batch_num} saved: {len(batch)} properties")

                offset += batch_size
                batch_num += 1

            except Exception as e:
                logger.error(f"✗ Error exporting batch {batch_num}: {e}")
                raise

        # Export translations
        if include_translations and all_property_ids:
            logger.info(f"Exporting translations for {len(all_property_ids)} properties...")
            translations = self.export_translations(all_property_ids)

            translations_file = output_dir / "translations.json"
            with open(translations_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, indent=2, default=str)

            logger.info(f"✓ Translations saved: {len(translations)} records")

        # Save metadata
        metadata = {
            "export_date": datetime.now().isoformat(),
            "total_properties": len(all_property_ids),
            "total_batches": batch_num - 1,
            "batch_size": batch_size,
            "includes_translations": include_translations
        }

        metadata_file = output_dir / "export_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"✓ Export complete: {len(all_property_ids)} properties")


@click.command()
@click.option('--output-dir', type=click.Path(), required=True, help='Output directory for exports')
@click.option('--batch-size', type=int, default=500, help='Batch size for pagination')
@click.option('--include-translations/--no-translations', default=True, help='Include translations')
def main(output_dir: str, batch_size: int, include_translations: bool):
    """Export properties from Supabase to JSON files."""

    # Load config
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")

    # Run export
    exporter = SupabaseExporter(supabase_url, supabase_key)
    exporter.export_all(
        output_dir=Path(output_dir),
        batch_size=batch_size,
        include_translations=include_translations
    )


if __name__ == "__main__":
    main()
```

---

### Script 2: transform_properties.py

**Purpose:** Transform exported properties to new schema format

**Features:**
- Field mapping (old → new)
- Company model transformations
- Department inference
- JSONB structure validation
- Pydantic validation
- Error collection and reporting

**Usage:**
```bash
python scripts/migration/transform_properties.py \
  --input-dir data/exports/ \
  --output-file data/transformed.json \
  --default-admin-id "uuid-here"
```

**Code Template:**
```python
"""
Transform exported properties to new company-owned schema.

Usage:
    python transform_properties.py --input-dir data/exports/ --output-file data/transformed.json
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ValidationError
import click

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PropertyTransformer:
    """Transform properties to company-owned model."""

    def __init__(self, default_admin_id: str, config: Dict[str, Any]):
        self.default_admin_id = default_admin_id
        self.config = config
        self.errors = []

    def infer_department(self, property_type: str, transaction_type: str) -> str:
        """Infer department from property characteristics."""
        if transaction_type == "rent":
            return "rentals"
        elif transaction_type in ("sale", "sale-lease"):
            return "sales"
        elif property_type in ("office", "warehouse", "business"):
            return "commercial"
        else:
            return "sales"  # Default

    def transform_contact_info(self, old_contact: Dict, department: str) -> Dict:
        """Transform agent-centric contact to company-centric."""
        return {
            "company_name": self.config["company"]["name"],
            "company_phone": self.config["company"]["phone"],
            "company_email": self.config["company"]["email"],
            "company_line_id": self.config["company"]["line_id"],
            "company_whatsapp": self.config["company"]["whatsapp"],
            "languages_spoken": old_contact.get("languages_spoken", ["English", "Thai"]),
            "preferred_contact": old_contact.get("preferred_contact", "email"),
            "availability_hours": self.config["company"]["hours"],
            "department": department
        }

    def transform_property(self, old_prop: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Transform a single property."""
        try:
            # Infer department
            department = self.infer_department(
                old_prop.get("property_type", ""),
                old_prop.get("transaction_type", "")
            )

            # Build new property
            new_prop = {
                # Core fields (direct copy)
                "id": old_prop["id"],
                "title": old_prop["title"],
                "description": old_prop.get("description"),
                "title_deed": old_prop.get("title_deed"),

                # Pricing (direct copy)
                "sale_price": old_prop.get("sale_price"),
                "rent_price": old_prop.get("rent_price"),
                "lease_price": old_prop.get("lease_price"),
                "currency": old_prop.get("currency", "THB"),
                "price_per_unit": old_prop.get("price_per_unit"),

                # Classification (direct copy)
                "transaction_type": old_prop["transaction_type"],
                "property_type": old_prop["property_type"],

                # JSONB fields (direct copy, except contact_info)
                "physical_specs": old_prop.get("physical_specs", {}),
                "location_details": old_prop.get("location_details", {}),
                "amenities": old_prop.get("amenities", {}),
                "policies": old_prop.get("policies", {}),
                "contact_info": self.transform_contact_info(
                    old_prop.get("contact_info", {}),
                    department
                ),

                # Media (direct copy)
                "cover_image": old_prop.get("cover_image"),
                "images": old_prop.get("images"),
                "virtual_tour_url": old_prop.get("virtual_tour_url"),
                "video_url": old_prop.get("video_url"),

                # Visibility (direct copy)
                "is_published": old_prop.get("is_published", False),
                "is_featured": old_prop.get("is_featured", False),
                "listing_priority": old_prop.get("listing_priority", 0),

                # Legal (direct copy)
                "ownership_type": old_prop.get("ownership_type"),
                "foreign_quota": old_prop.get("foreign_quota", False),

                # Investment (direct copy)
                "rental_yield": old_prop.get("rental_yield"),
                "price_trend": old_prop.get("price_trend"),

                # SEO (direct copy)
                "seo_title": old_prop.get("seo_title"),
                "seo_description": old_prop.get("seo_description"),
                "tags": old_prop.get("tags", []),

                # COMPANY MODEL FIELDS (NEW)
                "created_by": self.default_admin_id,  # Map from agent_id in production
                "updated_by": self.default_admin_id,
                "published_by": self.default_admin_id if old_prop.get("is_published") else None,
                "department": department,
                "internal_notes": "",
                "commission_rate": self.config["defaults"]["commission_rate"],

                # System fields (direct copy)
                "created_at": old_prop.get("created_at"),
                "updated_at": old_prop.get("updated_at"),
                "deleted_at": old_prop.get("deleted_at"),

                # Legacy (direct copy)
                "legacy_land_size": old_prop.get("legacy_land_size"),
                "legacy_land_size_unit": old_prop.get("legacy_land_size_unit"),
                "legacy_metadata": old_prop.get("legacy_metadata")
            }

            return new_prop

        except Exception as e:
            self.errors.append({
                "property_id": old_prop.get("id"),
                "error": str(e)
            })
            logger.error(f"Error transforming property {old_prop.get('id')}: {e}")
            return None

    def transform_batch(self, properties: List[Dict]) -> List[Dict]:
        """Transform a batch of properties."""
        transformed = []
        for prop in properties:
            result = self.transform_property(prop)
            if result:
                transformed.append(result)
        return transformed


@click.command()
@click.option('--input-dir', type=click.Path(exists=True), required=True, help='Directory with exported JSON files')
@click.option('--output-file', type=click.Path(), required=True, help='Output file for transformed properties')
@click.option('--default-admin-id', type=str, required=True, help='Default admin user UUID')
@click.option('--config-file', type=click.Path(), default='config/migration.yaml', help='Migration config file')
def main(input_dir: str, output_file: str, default_admin_id: str, config_file: str):
    """Transform exported properties to new schema."""

    # Load config
    import yaml
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    transformer = PropertyTransformer(default_admin_id, config)

    # Read all batch files
    input_path = Path(input_dir)
    batch_files = sorted(input_path.glob("properties_batch_*.json"))

    logger.info(f"Found {len(batch_files)} batch files to transform")

    all_transformed = []

    for batch_file in batch_files:
        logger.info(f"Transforming {batch_file.name}...")

        with open(batch_file, 'r') as f:
            properties = json.load(f)

        transformed = transformer.transform_batch(properties)
        all_transformed.extend(transformed)

        logger.info(f"✓ Transformed {len(transformed)}/{len(properties)} properties")

    # Save transformed properties
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_transformed, f, indent=2, default=str)

    logger.info(f"✓ Transformation complete: {len(all_transformed)} properties saved")

    # Save errors if any
    if transformer.errors:
        error_file = output_path.parent / "transform_errors.json"
        with open(error_file, 'w') as f:
            json.dump(transformer.errors, f, indent=2)
        logger.warning(f"⚠ {len(transformer.errors)} errors saved to {error_file}")


if __name__ == "__main__":
    main()
```

---

### Script 3: import_properties.py

**Purpose:** Import transformed properties to PostgreSQL

**Features:**
- Async batch insert (asyncpg)
- Foreign key validation
- Transaction management
- Progress tracking
- Error handling with rollback

**Usage:**
```bash
python scripts/migration/import_properties.py \
  --input-file data/transformed.json \
  --batch-size 500
```

**Code Template:**
```python
"""
Import transformed properties to PostgreSQL.

Usage:
    python import_properties.py --input-file data/transformed.json --batch-size 500
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import asyncpg
import click

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PropertyImporter:
    """Import properties to PostgreSQL."""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None

    async def connect(self):
        """Create connection pool."""
        self.pool = await asyncpg.create_pool(self.database_url, min_size=5, max_size=20)
        logger.info("✓ Connected to database")

    async def close(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()

    async def validate_user_exists(self, user_id: str) -> bool:
        """Check if user exists (for FK validation)."""
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM users WHERE id = $1)",
                user_id
            )
            return result

    async def insert_property(self, conn, prop: Dict[str, Any]):
        """Insert a single property."""

        # Build INSERT query dynamically (all fields)
        query = """
            INSERT INTO bestays_properties_v2 (
                id, title, description, title_deed,
                sale_price, rent_price, lease_price, currency, price_per_unit,
                transaction_type, property_type,
                physical_specs, location_details, amenities, policies, contact_info,
                cover_image, images, virtual_tour_url, video_url,
                is_published, is_featured, listing_priority,
                ownership_type, foreign_quota,
                rental_yield, price_trend,
                seo_title, seo_description, tags,
                created_by, updated_by, published_by, department, internal_notes, commission_rate,
                created_at, updated_at, deleted_at,
                legacy_land_size, legacy_land_size_unit, legacy_metadata
            ) VALUES (
                $1, $2, $3, $4,
                $5, $6, $7, $8, $9,
                $10, $11,
                $12, $13, $14, $15, $16,
                $17, $18, $19, $20,
                $21, $22, $23,
                $24, $25,
                $26, $27,
                $28, $29, $30,
                $31, $32, $33, $34, $35, $36,
                $37, $38, $39,
                $40, $41, $42
            )
        """

        await conn.execute(
            query,
            prop["id"], prop["title"], prop.get("description"), prop.get("title_deed"),
            prop.get("sale_price"), prop.get("rent_price"), prop.get("lease_price"),
            prop.get("currency", "THB"), prop.get("price_per_unit"),
            prop["transaction_type"], prop["property_type"],
            json.dumps(prop.get("physical_specs", {})),
            json.dumps(prop.get("location_details", {})),
            json.dumps(prop.get("amenities", {})),
            json.dumps(prop.get("policies", {})),
            json.dumps(prop.get("contact_info", {})),
            json.dumps(prop.get("cover_image")) if prop.get("cover_image") else None,
            [json.dumps(img) for img in prop.get("images", [])],
            prop.get("virtual_tour_url"),
            prop.get("video_url"),
            prop.get("is_published", False),
            prop.get("is_featured", False),
            prop.get("listing_priority", 0),
            prop.get("ownership_type"),
            prop.get("foreign_quota", False),
            prop.get("rental_yield"),
            prop.get("price_trend"),
            prop.get("seo_title"),
            prop.get("seo_description"),
            prop.get("tags", []),
            prop["created_by"],
            prop["updated_by"],
            prop.get("published_by"),
            prop["department"],
            prop.get("internal_notes", ""),
            prop.get("commission_rate", 2.5),
            prop.get("created_at"),
            prop.get("updated_at"),
            prop.get("deleted_at"),
            prop.get("legacy_land_size"),
            prop.get("legacy_land_size_unit"),
            json.dumps(prop.get("legacy_metadata")) if prop.get("legacy_metadata") else None
        )

    async def import_batch(self, properties: List[Dict], batch_num: int):
        """Import a batch of properties (transactional)."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                for i, prop in enumerate(properties):
                    try:
                        await self.insert_property(conn, prop)
                    except Exception as e:
                        logger.error(f"Error inserting property {prop['id']}: {e}")
                        raise  # Rollback transaction

        logger.info(f"✓ Batch {batch_num} imported: {len(properties)} properties")

    async def import_all(self, properties: List[Dict], batch_size: int = 500):
        """Import all properties in batches."""
        total = len(properties)
        batch_num = 1

        for i in range(0, total, batch_size):
            batch = properties[i:i + batch_size]
            logger.info(f"Importing batch {batch_num} ({i}/{total})...")

            try:
                await self.import_batch(batch, batch_num)
            except Exception as e:
                logger.error(f"✗ Batch {batch_num} failed: {e}")
                logger.error("Rolling back and stopping import.")
                raise

            batch_num += 1

        logger.info(f"✓ Import complete: {total} properties")


@click.command()
@click.option('--input-file', type=click.Path(exists=True), required=True, help='Transformed properties JSON file')
@click.option('--batch-size', type=int, default=500, help='Batch size for import')
def main(input_file: str, batch_size: int):
    """Import transformed properties to PostgreSQL."""

    # Load properties
    with open(input_file, 'r') as f:
        properties = json.load(f)

    logger.info(f"Loaded {len(properties)} properties to import")

    # Database connection
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("Missing DATABASE_URL")

    # Run import
    async def run():
        importer = PropertyImporter(database_url)
        await importer.connect()
        try:
            await importer.import_all(properties, batch_size)
        finally:
            await importer.close()

    asyncio.run(run())


if __name__ == "__main__":
    main()
```

---

### Script 4: supabase_direct.py (Production)

**Purpose:** Direct database connection for production migration

**Features:**
- Server-side cursors (memory efficient)
- Streaming data processing
- Resume capability (migration_state table)
- Inline transformation
- Comprehensive error handling
- Progress metrics

**Usage:**
```bash
python scripts/migration/supabase_direct.py \
  --migration-name "production_v1" \
  --batch-size 500 \
  --resume
```

**Code Template:**
```python
"""
Direct database migration from Supabase to PostgreSQL (production).

Usage:
    python supabase_direct.py --migration-name production_v1 --batch-size 500
"""

import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import psycopg2
import psycopg2.extras
import asyncpg
import asyncio
import click

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DirectMigrator:
    """Direct migration from Supabase to PostgreSQL."""

    def __init__(
        self,
        source_conn_str: str,
        target_conn_str: str,
        migration_name: str,
        config: Dict[str, Any]
    ):
        self.source_conn_str = source_conn_str
        self.target_conn_str = target_conn_str
        self.migration_name = migration_name
        self.config = config

        self.source_conn = None
        self.target_pool = None

    def connect_source(self):
        """Connect to Supabase database."""
        self.source_conn = psycopg2.connect(
            self.source_conn_str,
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        logger.info("✓ Connected to Supabase (source)")

    async def connect_target(self):
        """Connect to target PostgreSQL."""
        self.target_pool = await asyncpg.create_pool(
            self.target_conn_str,
            min_size=5,
            max_size=20
        )
        logger.info("✓ Connected to PostgreSQL (target)")

    async def get_migration_state(self) -> Optional[Dict]:
        """Get existing migration state."""
        async with self.target_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM migration_state WHERE migration_name = $1",
                self.migration_name
            )
            return dict(row) if row else None

    async def init_migration_state(self, total_count: int):
        """Initialize migration state."""
        async with self.target_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO migration_state (
                    migration_name, status, total_count, processed_count
                ) VALUES ($1, $2, $3, $4)
                ON CONFLICT (migration_name) DO UPDATE SET
                    started_at = NOW(),
                    status = $2,
                    total_count = $3,
                    processed_count = $4
                """,
                self.migration_name, "running", total_count, 0
            )

    async def update_migration_state(
        self,
        processed_count: int,
        last_processed_id: str,
        failed_count: int = 0
    ):
        """Update migration progress."""
        async with self.target_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE migration_state SET
                    processed_count = $2,
                    last_processed_id = $3,
                    failed_count = $4
                WHERE migration_name = $1
                """,
                self.migration_name, processed_count, last_processed_id, failed_count
            )

    async def complete_migration(self):
        """Mark migration as completed."""
        async with self.target_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE migration_state SET
                    status = 'completed',
                    completed_at = NOW()
                WHERE migration_name = $1
                """,
                self.migration_name
            )

    def count_source_properties(self) -> int:
        """Count properties in source database."""
        cursor = self.source_conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM bestays_properties_v2 WHERE deleted_at IS NULL"
        )
        count = cursor.fetchone()[0]
        cursor.close()
        return count

    def stream_properties(self, start_after_id: Optional[str] = None):
        """Stream properties from source (server-side cursor)."""
        cursor = self.source_conn.cursor(name='migration_cursor')

        if start_after_id:
            # Resume from last checkpoint
            query = """
                SELECT * FROM bestays_properties_v2
                WHERE deleted_at IS NULL AND id > %s
                ORDER BY id
            """
            cursor.execute(query, (start_after_id,))
        else:
            # Fresh start
            query = """
                SELECT * FROM bestays_properties_v2
                WHERE deleted_at IS NULL
                ORDER BY id
            """
            cursor.execute(query)

        return cursor

    async def migrate(self, batch_size: int = 500, resume: bool = False):
        """Run the migration."""

        # Check if resuming
        start_after_id = None
        processed_count = 0

        if resume:
            state = await self.get_migration_state()
            if state and state["status"] == "paused":
                start_after_id = state["last_processed_id"]
                processed_count = state["processed_count"]
                logger.info(f"Resuming from property ID: {start_after_id}")

        # Count total
        total = self.count_source_properties()
        logger.info(f"Total properties to migrate: {total}")

        # Initialize state
        await self.init_migration_state(total)

        # Stream and transform
        cursor = self.stream_properties(start_after_id)

        batch = []
        batch_num = 1

        try:
            while True:
                rows = cursor.fetchmany(batch_size)
                if not rows:
                    break

                logger.info(f"Processing batch {batch_num} ({processed_count}/{total})...")

                # Transform and insert batch
                # (Use transformation logic from transform_properties.py)
                # (Use insert logic from import_properties.py)

                for row in rows:
                    # Transform property (inline)
                    transformed = self.transform_property(dict(row))
                    batch.append(transformed)

                # Insert batch
                await self.insert_batch(batch)

                processed_count += len(batch)
                last_id = batch[-1]["id"]

                # Update state every 10 batches
                if batch_num % 10 == 0:
                    await self.update_migration_state(processed_count, last_id)

                logger.info(f"✓ Batch {batch_num} migrated: {len(batch)} properties")

                batch = []
                batch_num += 1

            # Mark complete
            await self.complete_migration()
            logger.info(f"✓ Migration complete: {processed_count} properties")

        except Exception as e:
            logger.error(f"✗ Migration failed: {e}")
            # Update state to paused for resume
            async with self.target_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE migration_state SET status = 'paused' WHERE migration_name = $1",
                    self.migration_name
                )
            raise

        finally:
            cursor.close()

    def transform_property(self, prop: Dict) -> Dict:
        """Transform property (same as transform_properties.py)."""
        # TODO: Implement transformation logic
        pass

    async def insert_batch(self, batch: list):
        """Insert batch (same as import_properties.py)."""
        # TODO: Implement batch insert
        pass

    def close(self):
        """Close connections."""
        if self.source_conn:
            self.source_conn.close()


@click.command()
@click.option('--migration-name', type=str, required=True, help='Unique migration name')
@click.option('--batch-size', type=int, default=500, help='Batch size')
@click.option('--resume', is_flag=True, help='Resume from last checkpoint')
def main(migration_name: str, batch_size: int, resume: bool):
    """Run direct migration from Supabase to PostgreSQL."""

    # Load connection strings
    source_conn_str = os.getenv("SUPABASE_DATABASE_URL")
    target_conn_str = os.getenv("DATABASE_URL")

    if not source_conn_str or not target_conn_str:
        raise ValueError("Missing connection strings")

    # Load config
    import yaml
    with open('config/migration.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Run migration
    async def run():
        migrator = DirectMigrator(source_conn_str, target_conn_str, migration_name, config)
        migrator.connect_source()
        await migrator.connect_target()
        try:
            await migrator.migrate(batch_size, resume)
        finally:
            migrator.close()
            if migrator.target_pool:
                await migrator.target_pool.close()

    asyncio.run(run())


if __name__ == "__main__":
    main()
```

---

## Data Flow & Processing

### Phase 1: Export/Import Flow

```
1. EXPORT (supabase_export.py)
   ├─ Connect to Supabase via REST API
   ├─ Query properties (paginated, 500/batch)
   ├─ Export to JSON files (properties_batch_001.json, etc.)
   ├─ Export translations (translations.json)
   └─ Save metadata (export_metadata.json)

2. TRANSFORM (transform_properties.py)
   ├─ Load all batch files
   ├─ For each property:
   │  ├─ Map fields (old → new)
   │  ├─ Infer department
   │  ├─ Transform contact_info (agent → company)
   │  ├─ Validate with Pydantic
   │  └─ Collect errors
   ├─ Save transformed.json
   └─ Save transform_errors.json (if any)

3. IMPORT (import_properties.py)
   ├─ Load transformed.json
   ├─ Connect to PostgreSQL (asyncpg pool)
   ├─ Validate foreign keys (created_by → users)
   ├─ Insert in batches (500/batch, transactional)
   ├─ Track progress
   └─ Rollback on error
```

### Phase 2: Direct Migration Flow

```
1. DIRECT MIGRATION (supabase_direct.py)
   ├─ Connect to Supabase database (psycopg2)
   ├─ Connect to PostgreSQL (asyncpg pool)
   ├─ Check migration_state (resume if paused)
   ├─ Stream properties (server-side cursor)
   ├─ For each batch (500 rows):
   │  ├─ Transform inline
   │  ├─ Insert to PostgreSQL (transactional)
   │  ├─ Update migration_state every 10 batches
   │  └─ Log progress
   └─ Mark migration complete
```

---

## Error Handling & Rollback

### Error Categories

| Category | Severity | Action | Recovery |
|----------|----------|--------|----------|
| **Export Error** | Low | Log + skip + continue | Manual review |
| **Transform Error** | Medium | Collect all + report | Fix data + retry |
| **Import Error** | High | Rollback transaction | Fix + re-import batch |
| **FK Violation** | High | Fail fast | Create missing users |
| **Constraint Violation** | High | Fail fast | Fix data + retry |

### Rollback Procedures

#### Development Rollback (Full Reset)
```sql
-- Drop and recreate tables
DROP TABLE IF EXISTS bestays_property_translations CASCADE;
DROP TABLE IF EXISTS bestays_properties_v2 CASCADE;
DROP TABLE IF EXISTS migration_state CASCADE;

-- Re-run Alembic migration
-- alembic upgrade head
```

#### Production Rollback (Selective)
```sql
-- 1. Backup current state (just in case)
CREATE TABLE bestays_properties_v2_backup AS SELECT * FROM bestays_properties_v2;

-- 2. Delete migration data (keep original if any)
DELETE FROM bestays_properties_v2 WHERE created_at >= '2025-11-06 00:00:00';
DELETE FROM bestays_property_translations WHERE property_id IN (
    SELECT id FROM bestays_properties_v2 WHERE created_at >= '2025-11-06 00:00:00'
);

-- 3. Reset migration state
UPDATE migration_state SET status = 'paused', last_processed_id = NULL WHERE migration_name = 'production_v1';
```

#### Resume After Error
```bash
# Check migration state
psql -d bestays_dev -c "SELECT * FROM migration_state WHERE migration_name = 'production_v1';"

# Resume from last checkpoint
python supabase_direct.py --migration-name production_v1 --resume
```

---

## Testing Strategy

### Unit Tests

**Transform Logic Tests:**
```python
# tests/migration/test_transform.py

import pytest
from scripts.migration.transform_properties import PropertyTransformer

def test_infer_department_rentals():
    transformer = PropertyTransformer("admin-id", {})
    assert transformer.infer_department("condo", "rent") == "rentals"

def test_infer_department_sales():
    transformer = PropertyTransformer("admin-id", {})
    assert transformer.infer_department("villa", "sale") == "sales"

def test_infer_department_commercial():
    transformer = PropertyTransformer("admin-id", {})
    assert transformer.infer_department("warehouse", "lease") == "commercial"

def test_transform_contact_info():
    transformer = PropertyTransformer("admin-id", {
        "company": {
            "name": "Bestays",
            "phone": "+66812345678",
            "email": "info@bestays.app",
            "line_id": "bestays",
            "whatsapp": "+66812345678",
            "hours": "24h"
        }
    })

    old_contact = {
        "agent_name": "John",
        "languages_spoken": ["English", "Thai"]
    }

    result = transformer.transform_contact_info(old_contact, "sales")

    assert result["company_name"] == "Bestays"
    assert result["department"] == "sales"
    assert result["languages_spoken"] == ["English", "Thai"]
```

### Integration Tests

**Full Pipeline Test:**
```python
# tests/migration/test_integration.py

import pytest
import asyncio
from scripts.migration import supabase_export, transform_properties, import_properties

@pytest.mark.asyncio
async def test_full_migration_pipeline():
    """Test export → transform → import pipeline."""

    # 1. Export sample data (10 properties)
    # TODO: Setup test Supabase instance

    # 2. Transform
    # TODO: Run transformation

    # 3. Import to test database
    # TODO: Run import

    # 4. Validate
    # TODO: Query and compare
```

### Validation Tests

**Post-Migration Validation:**
```sql
-- Count check
SELECT
    (SELECT COUNT(*) FROM bestays_properties_v2 WHERE deleted_at IS NULL) as new_count,
    -- Compare with source count from export_metadata.json

-- FK integrity
SELECT COUNT(*) FROM bestays_properties_v2
WHERE created_by NOT IN (SELECT id FROM users);
-- Should be 0

-- Translation links
SELECT COUNT(*) FROM bestays_property_translations
WHERE property_id NOT IN (SELECT id FROM bestays_properties_v2);
-- Should be 0

-- JSONB structure (sample)
SELECT id, physical_specs->'rooms'->>'bedrooms' as bedrooms
FROM bestays_properties_v2
WHERE physical_specs->'rooms' IS NOT NULL
LIMIT 10;

-- Department distribution
SELECT department, COUNT(*)
FROM bestays_properties_v2
GROUP BY department;
```

---

## Implementation Timeline

### Week 1: Schema & Infrastructure (5 days)

**Day 1-2: Schema Design**
- [ ] Create modified V2 schema (SQL + Alembic migration)
- [ ] Add company model fields (created_by, department, etc.)
- [ ] Remove agent-centric fields
- [ ] Create migration_state table

**Day 2-3: Database Setup**
- [ ] Run Alembic migration on development database
- [ ] Create default admin user (for created_by FK)
- [ ] Test enum values
- [ ] Verify indexes created

**Day 3-4: Pydantic Models**
- [ ] Create validation models for all JSONB structures
- [ ] Add enum validators
- [ ] Test with sample data

**Day 4-5: Supabase Setup**
- [ ] Get Supabase connection credentials
- [ ] Test REST API access
- [ ] Test direct database connection
- [ ] Export sample dataset (10 properties)

---

### Week 2: Export/Import Scripts (5 days)

**Day 1-2: supabase_export.py**
- [ ] Implement paginated export
- [ ] Add progress tracking
- [ ] Export translations
- [ ] Test with 100 properties
- [ ] Handle API rate limits

**Day 2-3: transform_properties.py**
- [ ] Implement field mapping
- [ ] Add department inference
- [ ] Transform contact_info
- [ ] Pydantic validation
- [ ] Error collection
- [ ] Test with exported data

**Day 3-4: import_properties.py**
- [ ] Implement batch insert (asyncpg)
- [ ] Add transaction management
- [ ] FK validation
- [ ] Progress tracking
- [ ] Rollback on error
- [ ] Test with transformed data

**Day 4-5: Integration Testing**
- [ ] Full pipeline test (export → transform → import)
- [ ] Validate data integrity
- [ ] Test rollback procedures
- [ ] Performance testing (batch size optimization)

---

### Week 3: Direct Migration Script (5 days)

**Day 1-2: supabase_direct.py**
- [ ] Implement server-side cursor streaming
- [ ] Inline transformation
- [ ] migration_state tracking
- [ ] Resume capability
- [ ] Progress metrics

**Day 2-3: Error Recovery**
- [ ] Comprehensive error handling
- [ ] Rollback procedures
- [ ] Resume from checkpoint
- [ ] Error logging

**Day 3-4: Performance Optimization**
- [ ] Batch size tuning (100, 500, 1000)
- [ ] Connection pooling
- [ ] Memory profiling
- [ ] Query optimization

**Day 4-5: Full Migration Test**
- [ ] Clone production database (Supabase)
- [ ] Run full migration (all properties)
- [ ] Validate data integrity
- [ ] Performance benchmarks
- [ ] Document findings

---

### Week 4: Production Migration (5 days)

**Day 1: Pre-Migration**
- [ ] Full backup (Supabase + PostgreSQL)
- [ ] Freeze property edits in old system
- [ ] Verify all prerequisites
- [ ] Communication to stakeholders
- [ ] Setup monitoring

**Day 2: Migration Rehearsal**
- [ ] Test migration on production clone
- [ ] Verify all validation checks
- [ ] Test rollback procedures
- [ ] Time the migration
- [ ] Final checklist review

**Day 3: Production Migration**
- [ ] Execute migration (off-peak hours)
- [ ] Monitor progress dashboard
- [ ] Run validation queries after each batch
- [ ] Check error logs
- [ ] Pause if issues detected

**Day 4: Post-Migration Validation**
- [ ] Run all validation queries
- [ ] Sample 50 properties manually
- [ ] Test critical user flows
- [ ] Performance benchmarks
- [ ] Fix data quality issues

**Day 5: Documentation & Handoff**
- [ ] Document migration results
- [ ] Update system documentation
- [ ] Archive old system (don't delete)
- [ ] Monitor production for 1 week
- [ ] Post-mortem report

---

## Risk Assessment

### Risk Matrix

| Risk | Likelihood | Impact | Mitigation | Owner |
|------|-----------|--------|------------|-------|
| **Data loss during migration** | Medium | Critical | Full backups, transactional inserts, validation | DevOps |
| **Downtime during migration** | High | High | Read-only mode, parallel run, gradual cutover | DevOps |
| **JSONB structure incompatibility** | Low | Medium | Schema validation, test with production samples | Backend |
| **FK violations (created_by)** | Medium | Medium | Create default admin, map agent_id to users | Backend |
| **Enum value mismatches** | Low | Low | Pre-migration validation, map unknown → "other" | Backend |
| **Translation data orphaned** | Low | Medium | FK constraints, bulk insert after properties | Backend |
| **Image URLs break** | Medium | High | Keep Supabase storage OR migrate to our CDN | DevOps |
| **Performance degradation** | Low | Medium | Batch size optimization, indexes, query tuning | Backend |

### Mitigation Details

**Risk 1: Data Loss**
- **Before:** Full database backup (pg_dump)
- **During:** Transactional batches (rollback on error)
- **After:** Validation queries (count, FK integrity)
- **Rollback:** TRUNCATE + re-import from backup

**Risk 2: Downtime**
- **Approach:** Read-only mode on old system during migration
- **Alternative:** Parallel run (migrate, then switch traffic)
- **Timeline:** Off-peak hours (3am-6am)

**Risk 7: Image URLs**
- **Issue:** Supabase storage URLs may break after migration
- **Option A:** Keep Supabase storage active (pay subscription)
- **Option B:** Migrate images to Cloudflare R2 first
- **Recommendation:** Option A (simpler), migrate images later

---

## Production Migration Checklist

### Pre-Migration (1 Week Before)

- [ ] **Database Backups**
  - [ ] Supabase full backup (pg_dump)
  - [ ] PostgreSQL full backup
  - [ ] Store backups in S3/R2
  - [ ] Test restore procedure

- [ ] **Test Migration**
  - [ ] Clone production database
  - [ ] Run full migration test
  - [ ] Validate all data
  - [ ] Time the migration (estimate duration)
  - [ ] Test rollback procedures

- [ ] **User Management**
  - [ ] Verify all users exist in target system
  - [ ] Create default admin user (for created_by)
  - [ ] Map agent_id → user_id

- [ ] **Schema Validation**
  - [ ] All enums created
  - [ ] All indexes created
  - [ ] FK constraints active
  - [ ] migration_state table ready

- [ ] **Communication**
  - [ ] Notify stakeholders (maintenance window)
  - [ ] Prepare status update templates
  - [ ] Setup monitoring dashboards

---

### Day Before Migration

- [ ] **Final Checks**
  - [ ] Final backup
  - [ ] Freeze property edits in old system
  - [ ] Verify Supabase credentials
  - [ ] Verify PostgreSQL connection
  - [ ] Test scripts one last time

- [ ] **Preparation**
  - [ ] Setup migration logging
  - [ ] Prepare rollback scripts
  - [ ] Setup monitoring alerts
  - [ ] Schedule off-peak window

---

### Migration Day

- [ ] **Start Migration**
  - [ ] Start at agreed time (e.g., 3am)
  - [ ] Run supabase_direct.py
  - [ ] Monitor progress dashboard
  - [ ] Check logs every 10 minutes

- [ ] **During Migration**
  - [ ] Validate sample properties after each batch
  - [ ] Check error logs continuously
  - [ ] Pause if error rate > 5%
  - [ ] Update stakeholders hourly

- [ ] **Completion**
  - [ ] Wait for "Migration complete" message
  - [ ] Run validation queries immediately
  - [ ] Check migration_state table

---

### Post-Migration (Same Day)

- [ ] **Validation**
  - [ ] Run all validation queries (count, FK, JSONB)
  - [ ] Sample 50 properties manually
  - [ ] Test search queries
  - [ ] Test critical user flows
  - [ ] Verify translations loaded

- [ ] **Performance**
  - [ ] Run query performance tests
  - [ ] Check index usage
  - [ ] Monitor database metrics
  - [ ] Optimize slow queries

- [ ] **Communication**
  - [ ] Notify stakeholders (migration complete)
  - [ ] Share validation results
  - [ ] Document any issues found

---

### Post-Migration (Week After)

- [ ] **Monitoring**
  - [ ] Monitor production usage daily
  - [ ] Track error rates
  - [ ] Check data quality issues
  - [ ] Gather user feedback

- [ ] **Optimization**
  - [ ] Address slow queries
  - [ ] Fix data quality issues
  - [ ] Update documentation
  - [ ] Tune indexes if needed

- [ ] **Archive**
  - [ ] Archive old system (READ-ONLY, don't delete)
  - [ ] Document lessons learned
  - [ ] Update runbooks
  - [ ] Post-mortem report

---

## Code Templates

### Configuration File

**config/migration.yaml:**
```yaml
# Supabase connection (source)
supabase:
  url: "https://xxx.supabase.co"
  anon_key: "${SUPABASE_ANON_KEY}"
  service_role_key: "${SUPABASE_SERVICE_ROLE_KEY}"

  # Direct database connection (for production)
  db_host: "db.xxx.supabase.co"
  db_port: 5432
  db_name: "postgres"
  db_user: "postgres"
  db_password: "${SUPABASE_DB_PASSWORD}"

# Target database
target:
  host: "localhost"
  port: 5433
  database: "bestays_dev"
  user: "bestays_user"
  password: "${POSTGRES_PASSWORD}"

# Migration settings
migration:
  batch_size: 500
  checkpoint_interval: 10  # Save state every N batches
  max_retries: 3
  retry_delay_seconds: 5

  # Default values
  defaults:
    admin_user_id: "00000000-0000-0000-0000-000000000001"
    commission_rate: 2.5
    department: "sales"

  # Department mapping rules
  department_rules:
    rent: "rentals"
    sale: "sales"
    sale-lease: "sales"
    lease: "commercial"

# Company information (for contact_info transformation)
company:
  name: "Bestays Realty"
  phone: "+66812345678"
  email: "info@bestays.app"
  line_id: "bestays_official"
  whatsapp: "+66812345678"
  hours: "Mon-Fri 9am-6pm"

# Logging
logging:
  level: "INFO"
  file: "logs/migration_{timestamp}.log"
  console: true

# Validation rules
validation:
  max_error_rate: 0.05  # Pause if > 5% errors
  sample_size: 50  # Number of properties to manually validate
```

---

### Environment Variables

**.env.migration:**
```bash
# Supabase (Source)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
SUPABASE_DB_PASSWORD=your-db-password

# Direct connection string (for supabase_direct.py)
SUPABASE_DATABASE_URL=postgresql://postgres:your-db-password@db.xxx.supabase.co:5432/postgres

# PostgreSQL (Target)
DATABASE_URL=postgresql://bestays_user:bestays_password@localhost:5433/bestays_dev
```

---

### Pydantic Validation Models

**models/property_validation.py:**
```python
"""Pydantic models for property validation."""

from typing import Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class DepartmentEnum(str, Enum):
    SALES = "sales"
    RENTALS = "rentals"
    COMMERCIAL = "commercial"


class TransactionTypeEnum(str, Enum):
    SALE = "sale"
    RENT = "rent"
    LEASE = "lease"
    SALE_LEASE = "sale-lease"


class PropertyTypeEnum(str, Enum):
    LAND = "land"
    HOUSE = "house"
    VILLA = "villa"
    POOL_VILLA = "pool-villa"
    APARTMENT = "apartment"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    PENTHOUSE = "penthouse"
    OFFICE = "office"
    SHOP = "shop"
    WAREHOUSE = "warehouse"
    BUSINESS = "business"
    RESORT = "resort"
    HOTEL = "hotel"
    OTHER = "other"


class ContactInfo(BaseModel):
    """Company contact information."""
    company_name: str
    company_phone: str
    company_email: str
    company_line_id: Optional[str]
    company_whatsapp: Optional[str]
    languages_spoken: List[str] = []
    preferred_contact: str = "email"
    availability_hours: str = "Mon-Fri 9am-6pm"
    department: DepartmentEnum


class PropertyV2(BaseModel):
    """Property V2 schema validation."""

    id: str
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=5000)

    transaction_type: TransactionTypeEnum
    property_type: PropertyTypeEnum

    # Company model fields
    created_by: str  # UUID
    updated_by: str  # UUID
    published_by: Optional[str]  # UUID
    department: DepartmentEnum
    commission_rate: float = Field(default=2.5, ge=0, le=100)

    # JSONB fields
    contact_info: Optional[ContactInfo]

    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    @validator('commission_rate')
    def commission_valid(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Commission rate must be between 0 and 100')
        return v
```

---

### Alembic Migration

**alembic/versions/xxx_add_properties_v2.py:**
```python
"""Add properties V2 schema with company model

Revision ID: xxx
Revises: yyy
Create Date: 2025-11-06
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'xxx'
down_revision = 'yyy'
branch_labels = None
depends_on = None


def upgrade():
    # Create enums
    op.execute("CREATE TYPE property_department AS ENUM ('sales', 'rentals', 'commercial')")

    # Create properties table (full DDL from schema section)
    op.create_table(
        'bestays_properties_v2',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        # ... (all other columns from schema)
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('department', sa.Enum('sales', 'rentals', 'commercial', name='property_department'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
    )

    # Create indexes
    op.create_index('idx_properties_published', 'bestays_properties_v2', ['is_published'])
    # ... (all other indexes)

    # Create translation table
    op.create_table(
        'bestays_property_translations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('property_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('lang_code', sa.CHAR(2), nullable=False),
        sa.Column('field', sa.String(100), nullable=False),
        sa.Column('value', sa.Text()),
        sa.ForeignKeyConstraint(['property_id'], ['bestays_properties_v2.id'], ondelete='CASCADE'),
    )

    # Create migration state table
    op.create_table(
        'migration_state',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('migration_name', sa.String(100), unique=True, nullable=False),
        sa.Column('status', sa.String(20)),
        # ... (all other columns)
    )


def downgrade():
    op.drop_table('migration_state')
    op.drop_table('bestays_property_translations')
    op.drop_table('bestays_properties_v2')
    op.execute('DROP TYPE property_department')
```

---

## Appendix

### Useful SQL Queries

**Count Properties by Department:**
```sql
SELECT department, COUNT(*) as count
FROM bestays_properties_v2
WHERE deleted_at IS NULL
GROUP BY department
ORDER BY count DESC;
```

**Find Properties Missing Translations:**
```sql
SELECT p.id, p.title
FROM bestays_properties_v2 p
LEFT JOIN bestays_property_translations t ON t.property_id = p.id AND t.lang_code = 'th'
WHERE t.id IS NULL AND p.deleted_at IS NULL
LIMIT 10;
```

**Properties Created by Each Employee:**
```sql
SELECT
    u.email,
    COUNT(p.id) as properties_created
FROM bestays_properties_v2 p
JOIN users u ON u.id = p.created_by
WHERE p.deleted_at IS NULL
GROUP BY u.email
ORDER BY properties_created DESC;
```

**JSONB Query - Properties with Pools:**
```sql
SELECT id, title, amenities->'exterior' as exterior_amenities
FROM bestays_properties_v2
WHERE amenities->'exterior' @> '[{"id": "private_pool"}]'::jsonb
LIMIT 10;
```

---

### References

- **Original Schema Research:** `.sdlc-workflow/.specs/PROPERTY_SCHEMA_*.md`
- **Migration Scripts:** `scripts/migration/`
- **Config:** `config/migration.yaml`
- **Alembic Migrations:** `alembic/versions/`
- **Supabase Docs:** https://supabase.com/docs
- **Asyncpg Docs:** https://magicstack.github.io/asyncpg/

---

**Document Version:** 1.0
**Last Updated:** 2025-11-06
**Author:** Claude Code (Coordinator)
**Status:** Ready for Review


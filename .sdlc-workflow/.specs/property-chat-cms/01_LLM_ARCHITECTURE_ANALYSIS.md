# LLM Architecture Analysis: Property Chat CMS

**Status:** 📋 ANALYSIS - Production Ready Architecture
**Created:** 2025-11-06
**Purpose:** Comprehensive LLM architecture design for multimodal property extraction system

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [LLM Pipeline Design](#llm-pipeline-design)
4. [Property Type Detection](#property-type-detection)
5. [Data Extraction Strategy](#data-extraction-strategy)
6. [Amenity & Feature Detection](#amenity--feature-detection)
7. [Multimodal Processing](#multimodal-processing)
8. [Conversation Flow](#conversation-flow)
9. [LangChain Implementation](#langchain-implementation)
10. [Performance & Cost Analysis](#performance--cost-analysis)
11. [Error Handling & Resilience](#error-handling--resilience)
12. [MVP Roadmap](#mvp-roadmap)

---

## Executive Summary

### Objective

Design a production-ready LLM-powered property extraction system that enables real estate agents to create property listings from multimodal input (text, images, voice) through a conversational chat interface.

### Key Design Decisions

1. **Multi-Stage Pipeline**: Leverage existing conversation architecture + add specialized extraction layer
2. **Model Strategy**: Vision-capable models for images (GPT-4o/Claude 3.5) + fast models for text (Gemini 2.5 Flash Lite)
3. **LangChain Architecture**: Tools pattern with Pydantic structured output + conversation memory
4. **Extraction Approach**: Two-phase (detection → structured extraction) with confidence scoring
5. **MVP Focus**: Text + images first, voice transcription via Whisper API, defer video/VR to Phase 2

### Cost Estimates

**Per 1000 Property Extractions (MVP):**
- Text-only: ~$12-15 USD
- Text + 5 images: ~$150-200 USD
- With voice transcription: Add ~$6 USD

**Target Processing Time:**
- Text extraction: 3-5 seconds
- Image analysis (5 photos): 15-20 seconds
- Voice transcription (2 min): 8-10 seconds

---

## System Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        Agent Interface                           │
│  (SvelteKit 5 - Chat UI with File Upload & Voice Recording)     │
└────────────────────┬────────────────────────────────────────────┘
                     │ WebSocket/HTTP
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend Layer                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │   Property Extraction Endpoint                            │   │
│  │   POST /api/v1/properties/extract                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                     │                                             │
│                     ▼                                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │   PropertyExtractionService                               │   │
│  │   - Orchestrates multi-stage extraction                   │   │
│  │   - Manages conversation context                          │   │
│  │   - Coordinates LangChain tools                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                     │                                             │
│         ┌───────────┴───────────┬─────────────┐                 │
│         ▼                       ▼             ▼                 │
│  ┌─────────────┐    ┌──────────────────┐  ┌────────────────┐   │
│  │ Text        │    │ Image            │  │ Voice          │   │
│  │ Processor   │    │ Analyzer         │  │ Transcriber    │   │
│  │ (Gemini)    │    │ (GPT-4o/Claude)  │  │ (Whisper API)  │   │
│  └─────────────┘    └──────────────────┘  └────────────────┘   │
│         │                       │                    │           │
│         └───────────────────────┴────────────────────┘           │
│                                 │                                │
│                                 ▼                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │   PropertyDataExtractor (LangChain + Structured Output)   │   │
│  │   - Property type classification                          │   │
│  │   - Structured field extraction                           │   │
│  │   - Amenity detection (165+ options)                      │   │
│  │   - Location advantage detection (81 options)             │   │
│  │   - Validation & confidence scoring                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                 │                                │
│                                 ▼                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │   PostgreSQL Storage                                      │   │
│  │   - properties (core + JSONB)                             │   │
│  │   - subdomain tables (rental/sale/lease/business/invest)  │   │
│  │   - catalogue_options (amenities, locations)              │   │
│  │   - extraction_metadata (confidence, source)              │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Property Review Form  │
                    │  (Pre-filled for agent │
                    │   confirmation)        │
                    └────────────────────────┘
```

### Architectural Patterns

1. **Existing Chat Infrastructure Reuse**
   - Leverage `ConversationService` for multi-turn dialogue
   - Reuse `ChatService` for OpenRouter API calls
   - Extend with specialized extraction tools

2. **Tool-Based LangChain Pattern**
   - Extraction as LangChain tools with Pydantic schemas
   - Agent decides when to invoke extraction
   - Structured output ensures type safety

3. **Multi-Stage Processing**
   - Stage 1: Input preprocessing (transcription, image encoding)
   - Stage 2: Property type detection + confidence
   - Stage 3: Targeted extraction based on type
   - Stage 4: Validation + missing field detection
   - Stage 5: Clarification questions if needed

---

## LLM Pipeline Design

### Component Architecture

```python
# Core Components

1. PropertyExtractionAgent
   - LangChain Agent with custom tools
   - Manages extraction workflow
   - Handles multi-turn conversations

2. PropertyTypeTool
   - Detects: rental/sale/lease/business/investment
   - Returns: type + confidence + reasoning

3. PropertyExtractionTool
   - Type-specific extraction
   - Pydantic structured output
   - Parallel field extraction

4. AmenityDetectionTool
   - Catalog-based matching
   - Confidence per amenity
   - Image + text fusion

5. LocationAdvantageTool
   - Geographic context extraction
   - Proximity detection
   - View/environment classification

6. ValidationTool
   - Required field checker
   - Data type validation
   - Cross-field consistency
```

### LangChain Stack Selection

Based on existing codebase analysis:

```python
# Already Available:
- langchain>=0.3.0
- langchain-community>=0.3.0
- langchain-openai>=0.2.0
- langchain-anthropic>=0.2.0
- openai>=1.54.0
- anthropic>=0.39.0

# Additional Needs for Property Extraction:
- langchain-core>=0.3.0  # For structured output
- None - existing stack is sufficient!
```

**Recommended LangChain Components:**

1. **LLM Integration**
   ```python
   from langchain_openai import ChatOpenAI
   from langchain_anthropic import ChatAnthropic

   # For vision tasks
   vision_llm = ChatOpenAI(
       model="openai/gpt-4o",
       base_url="https://openrouter.ai/api/v1",
       api_key=settings.openrouter_api_key
   )

   # For text extraction
   text_llm = ChatOpenAI(
       model="google/gemini-2.5-flash-lite",
       base_url="https://openrouter.ai/api/v1",
       api_key=settings.openrouter_api_key
   )
   ```

2. **Structured Output**
   ```python
   from langchain_core.pydantic_v1 import BaseModel, Field
   from langchain_core.output_parsers import PydanticOutputParser

   class PropertyTypeDetection(BaseModel):
       property_type: Literal["rental", "sale", "lease", "business", "investment"]
       confidence: float = Field(ge=0.0, le=1.0)
       reasoning: str
       detected_features: list[str]
   ```

3. **Tools Pattern**
   ```python
   from langchain.agents import AgentExecutor, create_openai_tools_agent
   from langchain.tools import StructuredTool

   tools = [
       property_type_tool,
       extraction_tool,
       amenity_detection_tool,
       location_advantage_tool,
       validation_tool
   ]

   agent = create_openai_tools_agent(llm, tools, prompt)
   agent_executor = AgentExecutor(agent=agent, tools=tools)
   ```

4. **Memory Management**
   ```python
   from langchain.memory import ConversationBufferMemory
   from langchain_community.chat_message_histories import PostgresChatMessageHistory

   # Integrate with existing conversation_id
   memory = ConversationBufferMemory(
       chat_memory=PostgresChatMessageHistory(
           connection_string=settings.database_url,
           session_id=conversation_id
       ),
       return_messages=True
   )
   ```

### Prompt Engineering Strategy

#### 1. System Prompt for Property Extraction Agent

```python
PROPERTY_EXTRACTION_SYSTEM_PROMPT = """You are a property data extraction specialist for Bestays, a real estate platform. Your role is to extract structured property information from text descriptions, images, and voice messages provided by real estate agents.

## Your Capabilities:
1. Analyze text descriptions to extract property details
2. Examine property images to identify features, amenities, and condition
3. Process voice transcriptions for property information
4. Detect property type (rental, sale, lease, business for sale, investment)
5. Extract structured data matching our property schema
6. Identify amenities from a catalog of 165+ options
7. Detect location advantages from 81 possible options
8. Ask clarifying questions when information is ambiguous or missing

## Property Schema Knowledge:
- **Core Fields**: title, description, property_type, location_details, physical_specs
- **Room Types**: bedrooms, bathrooms, living_rooms, kitchens, dining_rooms, offices, storage_rooms, maid_rooms, guest_rooms
- **Dimensions**: total_area, living_area, usable_area, land_area, balcony_area, floor_area (with units)
- **Building Specs**: floors, floor_level, parking_spaces, year_built, last_renovated, facing_direction, condition, furnished
- **Amenity Categories**: interior (47 options), exterior (44 options), building (44 options), utilities (27 options)
- **Location Advantages**: waterfront, nature, urban, transportation, services, character (81 total options)
- **Transaction-Specific**: rental_details, sale_details, lease_details, business_details, investment_details

## Extraction Approach:
1. **Property Type Detection**: Analyze keywords, pricing structure, and context to classify
2. **Structured Extraction**: Extract fields matching the detected property type
3. **Amenity Matching**: Map descriptions/images to our 165+ amenity catalog
4. **Location Analysis**: Detect location advantages and proximity features
5. **Validation**: Check for required fields and consistency
6. **Confidence Scoring**: Provide confidence (0-1) for extracted data
7. **Clarification**: Ask for missing critical information

## Quality Guidelines:
- Extract only information explicitly stated or clearly visible
- Use "null" for fields with no information (don't guess)
- Provide confidence scores: 1.0 (explicit), 0.8 (strongly implied), 0.5 (uncertain)
- For ambiguous amenities, list multiple options with probabilities
- Preserve original numbers and units (convert to standard later)
- Flag inconsistencies for agent review

## Response Format:
Always return structured JSON matching our Pydantic schemas. Use the provided tools for type-specific extraction.
"""
```

#### 2. Property Type Detection Prompt

```python
PROPERTY_TYPE_DETECTION_PROMPT = """Analyze the following property information and determine the property type.

## Property Types:
1. **Rental** - Short-term or long-term rentals (keywords: "rent", "per month", "per night", "vacation rental")
2. **Sale** - Properties for sale (keywords: "for sale", "sale price", "buy", "purchase")
3. **Lease** - Long-term commercial/residential leases (keywords: "lease", "long-term contract", "lease agreement")
4. **Business** - Operating businesses for sale (keywords: "business for sale", "restaurant for sale", "hotel for sale", includes property + operations)
5. **Investment** - Investment opportunities (keywords: "ROI", "investment", "development project", "yield", "investors")

## Detection Criteria:
- **Primary indicator**: Transaction language (rent/sale/lease/investment)
- **Secondary indicators**: Pricing structure (monthly/one-time/ROI), business operations mentioned, development stage
- **Conflicts**: If multiple types detected, choose primary transaction type

## Input:
{input_data}

## Output Requirements:
- property_type: One of [rental, sale, lease, business, investment]
- confidence: Float 0.0-1.0 (1.0 = explicit, 0.8 = strong indicators, 0.5 = ambiguous)
- reasoning: Explain why you chose this type
- detected_features: List of keywords/phrases that influenced the decision
- alternative_types: If confidence < 0.9, list other possible types with reasons
"""
```

#### 3. Amenity Detection Prompt (Image-Specific)

```python
AMENITY_DETECTION_IMAGE_PROMPT = """Analyze the property image(s) and detect visible amenities from our catalog.

## Amenity Categories to Detect:

### Interior Amenities (47 options):
- Climate: Air conditioning, ceiling fans, heating
- Kitchen: Fully equipped kitchen, refrigerator, oven, microwave, dishwasher
- Appliances: Washing machine, dryer
- Storage: Built-in wardrobes, walk-in closet
- Entertainment: TV, sound system, WiFi router
- Furniture: Beds, sofas, dining table, desk

### Exterior Amenities (44 options):
- Pool: Private pool, pool heating, jacuzzi, pool fence
- Outdoor Living: Garden, terrace, balcony, BBQ area, outdoor dining, sala
- Recreation: Outdoor gym, playground, sports court
- Water Features: Pond, fountain, waterfall
- Security: Fence, gate, outdoor lighting

### Building Amenities (44 options):
- Security: 24h security, CCTV, security gate, key card access
- Facilities: Elevator, gym, communal pool, spa, restaurant, coworking space
- Services: Concierge, housekeeping, laundry service, room service
- Parking: Covered parking, underground parking, EV charging

## Detection Rules:
1. Only mark amenities clearly visible in images
2. Provide confidence score per amenity: 1.0 (definitely visible), 0.8 (likely present), 0.6 (partial view)
3. Don't assume amenities not visible in photos
4. For furniture, only mark if property is furnished
5. For building amenities, look for common area images

## Images Provided:
{images}

## Output Format:
```json
{
  "interior_amenities": [
    {"id": "am_int_air_conditioning", "confidence": 1.0, "evidence": "AC units visible on walls"},
    {"id": "am_int_kitchen", "confidence": 0.8, "evidence": "Modern kitchen with appliances"}
  ],
  "exterior_amenities": [...],
  "building_amenities": [...],
  "special_features": ["High ceilings", "Marble flooring", "Smart home system"]
}
```
"""
```

#### 4. Few-Shot Examples for Extraction

```python
FEW_SHOT_EXAMPLES = [
    {
        "input": {
            "text": "Beautiful 3-bedroom pool villa for sale in Phuket. 250 sqm living space on 600 sqm land. Fully furnished with modern appliances, private pool, tropical garden. Sea view from rooftop terrace. Price: 15,000,000 THB.",
            "images": ["villa_exterior.jpg", "pool.jpg", "bedroom.jpg"]
        },
        "output": {
            "property_type": "sale",
            "confidence": 1.0,
            "property_details": {
                "title": "Beautiful 3-Bedroom Pool Villa with Sea View",
                "property_type": "pt_pool_villa",
                "physical_specs": {
                    "rooms": {"bedrooms": 3, "bathrooms": None, "living_rooms": None},
                    "dimensions": {
                        "living_area": {"value": 250, "unit": "sqm"},
                        "land_area": {"value": 600, "unit": "sqm"}
                    },
                    "building_specs": {
                        "furnished": "fully",
                        "condition": "excellent"
                    }
                },
                "location_details": {
                    "region": "Phuket",
                    "location_advantages": ["loc_sea_view"]
                },
                "amenities_interior": ["am_int_modern_appliances"],
                "amenities_exterior": ["am_ext_private_pool", "am_ext_garden", "am_ext_terrace"],
                "sale_details": {
                    "sale_price": 15000000,
                    "currency": "THB"
                }
            },
            "missing_fields": ["bathrooms", "year_built", "parking_spaces"],
            "clarification_questions": [
                "How many bathrooms does the villa have?",
                "When was the villa built?",
                "How many parking spaces are available?"
            ]
        }
    },
    {
        "input": {
            "text": "Cozy studio for rent near beach. 35 sqm, fully furnished, WiFi, AC. 15,000 THB/month.",
            "images": []
        },
        "output": {
            "property_type": "rental",
            "confidence": 1.0,
            "property_details": {
                "title": "Cozy Studio Near Beach",
                "property_type": "pt_apartment",
                "physical_specs": {
                    "rooms": {"bedrooms": 0, "bathrooms": None},
                    "dimensions": {
                        "total_area": {"value": 35, "unit": "sqm"}
                    },
                    "building_specs": {
                        "furnished": "fully"
                    }
                },
                "location_details": {
                    "location_advantages": ["loc_near_beach"]
                },
                "amenities_interior": ["am_int_wifi", "am_int_air_conditioning"],
                "rental_details": {
                    "rental_type": "long_term",
                    "price_monthly": 15000,
                    "currency": "THB"
                }
            },
            "missing_fields": ["bathrooms", "floor_level", "building_amenities"],
            "clarification_questions": [
                "Does the studio have a separate bathroom?",
                "Which floor is the studio on?",
                "Are there any building facilities (pool, gym, security)?"
            ]
        }
    }
]
```

---

## Property Type Detection

### Detection Algorithm

**Two-Phase Approach:**

1. **Phase 1: Keyword-Based Heuristics** (Fast, Low Cost)
   ```python
   PROPERTY_TYPE_KEYWORDS = {
       "rental": {
           "strong": ["for rent", "per month", "per night", "vacation rental",
                     "short term", "long term", "monthly rent"],
           "medium": ["available now", "move in date", "rental", "tenant"],
           "price_pattern": r"(\d+[,.]?\d*)\s*(THB|USD|EUR)?\s*/(month|night|day|week)"
       },
       "sale": {
           "strong": ["for sale", "sale price", "selling price", "buy now",
                     "purchase price", "ownership"],
           "medium": ["investment opportunity", "freehold", "leasehold", "title deed"],
           "price_pattern": r"(Price|Sale):\s*(\d+[,.]?\d*)\s*(THB|USD|EUR|million|M)"
       },
       "business": {
           "strong": ["business for sale", "restaurant for sale", "hotel for sale",
                     "operating business", "with license", "including staff"],
           "medium": ["annual revenue", "monthly profit", "customer base",
                     "established business"],
           "indicators": ["revenue", "profit", "customers", "license", "employees"]
       },
       "investment": {
           "strong": ["investment opportunity", "ROI", "yield", "development project",
                     "pre-construction", "off-plan"],
           "medium": ["investors", "returns", "appreciation", "capital gain"],
           "indicators": ["projected", "completion date", "developer"]
       },
       "lease": {
           "strong": ["long-term lease", "lease contract", "lease agreement",
                     "commercial lease", "lease term"],
           "medium": ["key money", "lease duration", "renewal option"],
           "price_pattern": r"(\d+[,.]?\d*)\s*(THB|USD|EUR)?\s*/year"
       }
   }
   ```

2. **Phase 2: LLM Confirmation** (High Accuracy)
   - Use Gemini 2.5 Flash Lite for text-based confirmation
   - Include context from Phase 1 heuristics
   - Generate confidence score + reasoning

### Confidence Scoring

```python
def calculate_confidence(detection_result: dict) -> float:
    """Calculate confidence score for property type detection."""

    base_score = 0.5  # Starting point

    # Strong keywords found
    if detection_result["strong_keywords_count"] > 0:
        base_score += 0.3

    # Price pattern matches expected format
    if detection_result["price_pattern_match"]:
        base_score += 0.2

    # No conflicting indicators
    if not detection_result["has_conflicts"]:
        base_score += 0.1

    # LLM agrees with heuristic
    if detection_result["llm_agrees"]:
        base_score += 0.2

    # Multiple evidence sources (text + images)
    if detection_result["multimodal_evidence"]:
        base_score += 0.1

    return min(base_score, 1.0)
```

### Feature Indicators by Property Type

| Property Type | Key Indicators | Price Format | Typical Fields |
|--------------|----------------|--------------|----------------|
| **Rental** | "per month", "available date", "deposit" | 15,000 THB/month | rental_type, price_monthly, minimum_stay |
| **Sale** | "for sale", "freehold", "title deed" | 15,000,000 THB | sale_price, price_negotiable, transfer_fee |
| **Lease** | "lease term", "key money", "years" | 10,000 THB/month (3-year lease) | minimum_lease_years, key_money, escalation |
| **Business** | "annual revenue", "license", "staff" | 5M THB (includes equipment) | business_type, annual_revenue, employees |
| **Investment** | "ROI", "completion", "developer" | 20M THB (30% ROI projected) | projected_roi, project_stage, exit_strategy |

---

## Data Extraction Strategy

### Multi-Stage Extraction Pipeline

```python
class PropertyExtractionPipeline:
    """Multi-stage extraction with progressive refinement."""

    async def extract(
        self,
        input_data: PropertyInput
    ) -> PropertyExtractionResult:
        """
        Stage 1: Input Preprocessing
        Stage 2: Property Type Detection
        Stage 3: Structured Data Extraction
        Stage 4: Validation & Confidence Scoring
        Stage 5: Clarification Questions (if needed)
        """

        # Stage 1: Preprocess inputs
        processed = await self.preprocess_inputs(input_data)

        # Stage 2: Detect property type
        property_type = await self.detect_property_type(processed)

        if property_type.confidence < 0.7:
            return await self.ask_clarification("property_type")

        # Stage 3: Extract structured data (type-specific)
        extraction = await self.extract_by_type(
            property_type=property_type.type,
            data=processed
        )

        # Stage 4: Validate and score confidence
        validated = await self.validate_extraction(extraction)

        # Stage 5: Generate clarification questions for missing fields
        if validated.missing_required_fields:
            clarifications = await self.generate_clarifications(validated)
            return PropertyExtractionResult(
                data=validated.data,
                confidence=validated.confidence,
                status="needs_clarification",
                clarification_questions=clarifications
            )

        return PropertyExtractionResult(
            data=validated.data,
            confidence=validated.confidence,
            status="complete"
        )
```

### Pydantic Schemas for Structured Output

```python
from pydantic import BaseModel, Field, validator
from typing import Literal, Optional
from enum import Enum

# Property Type Enum
class PropertyType(str, Enum):
    LAND = "pt_land"
    HOUSE = "pt_house"
    VILLA = "pt_villa"
    POOL_VILLA = "pt_pool_villa"
    APARTMENT = "pt_apartment"
    CONDO = "pt_condo"
    TOWNHOUSE = "pt_townhouse"
    PENTHOUSE = "pt_penthouse"
    OFFICE = "pt_office"
    SHOP = "pt_shop"
    WAREHOUSE = "pt_warehouse"
    BUSINESS = "pt_business"
    RESORT = "pt_resort"
    HOTEL = "pt_hotel"
    OTHER = "pt_other"

# Room Counts
class RoomCounts(BaseModel):
    bedrooms: Optional[int] = Field(None, ge=0, le=50)
    bathrooms: Optional[int] = Field(None, ge=0, le=50)
    living_rooms: Optional[int] = Field(None, ge=0, le=10)
    kitchens: Optional[int] = Field(None, ge=0, le=10)
    dining_rooms: Optional[int] = Field(None, ge=0, le=10)
    offices: Optional[int] = Field(None, ge=0, le=10)
    storage_rooms: Optional[int] = Field(None, ge=0, le=10)
    maid_rooms: Optional[int] = Field(None, ge=0, le=10)
    guest_rooms: Optional[int] = Field(None, ge=0, le=20)

# Dimension with Unit
class Dimension(BaseModel):
    value: float = Field(gt=0)
    unit: Literal["sqm", "sqft", "rai", "ngan", "wah"]

# Building Specs
class BuildingSpecs(BaseModel):
    floors: Optional[int] = Field(None, ge=1, le=200)
    floor_level: Optional[int] = Field(None, ge=-5, le=200)
    parking_spaces: Optional[int] = Field(None, ge=0, le=100)
    year_built: Optional[int] = Field(None, ge=1900, le=2030)
    last_renovated: Optional[int] = Field(None, ge=1900, le=2030)
    facing_direction: Optional[Literal[
        "north", "south", "east", "west",
        "northeast", "northwest", "southeast", "southwest"
    ]] = None
    condition: Optional[Literal[
        "new", "excellent", "good", "fair", "needs_renovation"
    ]] = None
    furnished: Optional[Literal["fully", "partially", "unfurnished"]] = None

# Physical Specs
class PhysicalSpecs(BaseModel):
    rooms: Optional[RoomCounts] = None
    dimensions: Optional[dict[str, Dimension]] = Field(
        default_factory=dict,
        description="Keys: total_area, living_area, usable_area, land_area, balcony_area, floor_area"
    )
    building_specs: Optional[BuildingSpecs] = None

# Location Details
class LocationDetails(BaseModel):
    region: Optional[str] = None
    province: Optional[str] = None
    district: Optional[str] = None
    sub_district: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "TH"
    location_advantages: list[str] = Field(
        default_factory=list,
        description="Catalog IDs from cat_location_advantages"
    )
    proximity: Optional[dict] = Field(
        default_factory=dict,
        description="Distances to beaches, airports, etc."
    )

# Amenity with Confidence
class DetectedAmenity(BaseModel):
    id: str = Field(description="Catalog ID (e.g., am_int_air_conditioning)")
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: str = Field(description="Why detected (e.g., 'visible in image 3')")

# Rental Details
class RentalDetailsExtraction(BaseModel):
    rental_type: Literal["short_term", "long_term", "vacation"]
    price_daily: Optional[float] = None
    price_weekly: Optional[float] = None
    price_monthly: Optional[float] = None
    price_yearly: Optional[float] = None
    currency: Literal["THB", "USD", "EUR"] = "THB"
    minimum_stay_days: Optional[int] = None
    security_deposit_months: Optional[float] = None
    available_from: Optional[str] = Field(None, description="ISO date string")

# Sale Details
class SaleDetailsExtraction(BaseModel):
    sale_price: float = Field(gt=0)
    currency: Literal["THB", "USD", "EUR"] = "THB"
    price_negotiable: bool = False
    financing_available: bool = False
    transfer_fee_responsibility: Optional[Literal[
        "buyer", "seller", "split_50_50"
    ]] = None

# Business Details
class BusinessDetailsExtraction(BaseModel):
    business_type: str = Field(description="e.g., restaurant, hotel, resort")
    business_name: Optional[str] = None
    sale_price: float = Field(gt=0)
    currency: Literal["THB", "USD", "EUR"] = "THB"
    annual_revenue: Optional[float] = None
    annual_profit: Optional[float] = None
    employees_count: Optional[int] = None
    inventory_included: bool = False
    equipment_included: bool = False

# Investment Details
class InvestmentDetailsExtraction(BaseModel):
    investment_type: Literal[
        "development", "flip", "rental_income", "mixed_use"
    ]
    project_stage: Literal["planning", "construction", "completed"]
    total_investment: float = Field(gt=0)
    currency: Literal["THB", "USD", "EUR"] = "THB"
    projected_roi: Optional[float] = Field(None, ge=0, le=100)
    projected_annual_yield: Optional[float] = Field(None, ge=0, le=100)
    project_completion_date: Optional[str] = None

# Main Extraction Result
class PropertyExtractionResult(BaseModel):
    # Property Type
    property_type: PropertyType
    property_type_confidence: float = Field(ge=0.0, le=1.0)

    # Core Fields
    title: Optional[str] = Field(None, max_length=200)
    short_description: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None

    # Structured Components
    physical_specs: Optional[PhysicalSpecs] = None
    location_details: Optional[LocationDetails] = None

    # Amenities (with confidence)
    amenities_interior: list[DetectedAmenity] = Field(default_factory=list)
    amenities_exterior: list[DetectedAmenity] = Field(default_factory=list)
    amenities_building: list[DetectedAmenity] = Field(default_factory=list)
    utilities: list[DetectedAmenity] = Field(default_factory=list)

    # Transaction-Specific Details (only one will be populated)
    rental_details: Optional[RentalDetailsExtraction] = None
    sale_details: Optional[SaleDetailsExtraction] = None
    business_details: Optional[BusinessDetailsExtraction] = None
    investment_details: Optional[InvestmentDetailsExtraction] = None

    # Metadata
    extraction_confidence: float = Field(ge=0.0, le=1.0)
    missing_required_fields: list[str] = Field(default_factory=list)
    clarification_questions: list[str] = Field(default_factory=list)
    extraction_sources: dict = Field(
        default_factory=dict,
        description="Which fields came from text/images/voice"
    )

    @validator("title", pre=True, always=True)
    def generate_title_if_missing(cls, v, values):
        if not v and "physical_specs" in values:
            # Auto-generate title from property details
            specs = values["physical_specs"]
            property_type = values.get("property_type", "").replace("pt_", "").title()
            bedrooms = specs.rooms.bedrooms if specs.rooms else None

            if bedrooms:
                return f"{bedrooms}-Bedroom {property_type}"
            return f"{property_type} for Sale/Rent"
        return v
```

### Extraction Strategy by Property Type

**Common Extraction (All Types):**
1. Property type classification
2. Physical specs (rooms, dimensions, building details)
3. Location details
4. Amenities detection
5. Title/description generation

**Type-Specific Extraction:**

| Property Type | Additional Extraction Logic |
|--------------|----------------------------|
| **Rental** | Extract rental_type (short/long), price structure (daily/monthly), availability dates, deposit requirements, minimum stay |
| **Sale** | Extract sale_price, negotiability, financing options, transfer fees, ownership type (freehold/leasehold) |
| **Lease** | Extract lease terms (years), key money, escalation clauses, renewal options, maintenance responsibilities |
| **Business** | Extract business_type, financials (revenue/profit), included assets (inventory/equipment/staff), licenses, reason for sale |
| **Investment** | Extract project stage, ROI projections, investment structure, developer info, completion timeline, exit strategy |

### Handling Ambiguity & Missing Data

**Strategies:**

1. **Confidence-Based Thresholds**
   ```python
   CONFIDENCE_THRESHOLDS = {
       "property_type": 0.7,      # Must be confident about type
       "price": 0.8,              # Price must be clear
       "required_fields": 0.6,    # Bedrooms, bathrooms, etc.
       "amenities": 0.5,          # Lower threshold for amenities
       "optional_fields": 0.3     # Year built, parking, etc.
   }
   ```

2. **Missing Field Prioritization**
   ```python
   REQUIRED_FIELDS_BY_TYPE = {
       "rental": ["price_monthly", "bedrooms", "bathrooms", "location"],
       "sale": ["sale_price", "bedrooms", "bathrooms", "land_area", "location"],
       "business": ["business_type", "sale_price", "annual_revenue"],
       "investment": ["total_investment", "project_stage", "projected_roi"]
   }
   ```

3. **Clarification Question Generation**
   ```python
   async def generate_clarifications(
       extraction: PropertyExtractionResult
   ) -> list[str]:
       """Generate natural language questions for missing fields."""

       questions = []

       if not extraction.physical_specs.rooms.bathrooms:
           questions.append("How many bathrooms does the property have?")

       if not extraction.physical_specs.building_specs.year_built:
           questions.append("When was the property built?")

       if extraction.property_type == "rental" and not extraction.rental_details.minimum_stay_days:
           questions.append("Is there a minimum stay requirement?")

       # Prioritize critical missing fields
       questions = sorted(
           questions,
           key=lambda q: FIELD_PRIORITY.get(extract_field_name(q), 999)
       )

       return questions[:5]  # Max 5 questions per turn
   ```

4. **Null vs. Zero Handling**
   ```python
   # Explicit rules:
   - None/null: Information not provided → ask for clarification
   - 0: Explicitly stated as zero (e.g., "studio apartment" = 0 bedrooms)
   - Empty list: No amenities detected → don't assume
   ```

### Validation Before Presenting to Agent

**Multi-Level Validation:**

```python
class PropertyValidator:
    """Validates extracted property data before submission."""

    async def validate(
        self,
        extraction: PropertyExtractionResult
    ) -> ValidationResult:
        """Run all validation checks."""

        errors = []
        warnings = []

        # 1. Required Field Validation
        required = self._check_required_fields(extraction)
        if required:
            errors.extend(required)

        # 2. Data Type Validation
        type_errors = self._validate_data_types(extraction)
        if type_errors:
            errors.extend(type_errors)

        # 3. Range Validation
        range_errors = self._validate_ranges(extraction)
        if range_errors:
            errors.extend(range_errors)

        # 4. Cross-Field Consistency
        consistency = self._check_consistency(extraction)
        if consistency:
            warnings.extend(consistency)

        # 5. Catalog ID Validation
        catalog_errors = await self._validate_catalog_ids(extraction)
        if catalog_errors:
            errors.extend(catalog_errors)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            confidence_score=self._calculate_overall_confidence(extraction)
        )

    def _check_consistency(
        self,
        extraction: PropertyExtractionResult
    ) -> list[str]:
        """Check cross-field consistency."""

        warnings = []

        # Check: Pool villa should have private pool amenity
        if extraction.property_type == PropertyType.POOL_VILLA:
            pool_amenity = "am_ext_private_pool"
            has_pool = any(
                a.id == pool_amenity
                for a in extraction.amenities_exterior
            )
            if not has_pool:
                warnings.append(
                    "Property type is 'pool villa' but no private pool detected"
                )

        # Check: Living area should be <= total area
        if extraction.physical_specs and extraction.physical_specs.dimensions:
            dims = extraction.physical_specs.dimensions
            if "living_area" in dims and "total_area" in dims:
                if dims["living_area"].value > dims["total_area"].value:
                    warnings.append(
                        f"Living area ({dims['living_area'].value} {dims['living_area'].unit}) "
                        f"exceeds total area ({dims['total_area'].value} {dims['total_area'].unit})"
                    )

        # Check: Year built should be <= last renovated
        if extraction.physical_specs and extraction.physical_specs.building_specs:
            specs = extraction.physical_specs.building_specs
            if specs.year_built and specs.last_renovated:
                if specs.year_built > specs.last_renovated:
                    warnings.append(
                        f"Year built ({specs.year_built}) is after last renovated ({specs.last_renovated})"
                    )

        return warnings
```

---

## Amenity & Feature Detection

### Detection Strategy

**Multi-Source Detection:**

1. **Text-Based Detection**
   - Keyword matching with fuzzy search
   - Embedding similarity for synonyms
   - Context-aware extraction (e.g., "air conditioned" vs "air conditioning unit")

2. **Image-Based Detection**
   - Vision model analysis (GPT-4o/Claude 3.5 Sonnet)
   - Object detection for visible amenities
   - Scene understanding (pool, garden, gym, etc.)

3. **Voice-Based Detection**
   - Transcribe → text-based detection
   - Emphasis detection (agent highlights certain features)

### Catalog Matching Approach

**Option 1: RAG with Embeddings** (RECOMMENDED for MVP)

```python
class AmenityRAGMatcher:
    """RAG-based amenity matching using pgvector."""

    def __init__(self, db: AsyncSession, embedding_model: str):
        self.db = db
        self.embedding_model = embedding_model
        # Reuse existing FAQ embedding infrastructure
        self.embedding_service = EmbeddingService(embedding_model)

    async def setup_amenity_embeddings(self):
        """One-time: Generate embeddings for all 165+ amenity options."""

        # Get all amenities from catalogues
        amenities = await self.db.execute(
            select(CatalogueOption).where(
                CatalogueOption.catalogue_id.in_([
                    "amenities_interior",
                    "amenities_exterior",
                    "amenities_building",
                    "utilities"
                ])
            )
        )

        for amenity in amenities.scalars():
            # Generate embedding from name + description
            text = f"{amenity.name}: {amenity.description}"
            embedding = await self.embedding_service.generate_embedding(text)

            # Store in amenity_embeddings table
            await self.db.execute(
                insert(AmenityEmbedding).values(
                    amenity_id=amenity.id,
                    embedding=embedding,
                    text=text
                )
            )

        await self.db.commit()

    async def match_amenities(
        self,
        description: str,
        threshold: float = 0.7
    ) -> list[DetectedAmenity]:
        """Match description to amenity catalog using vector similarity."""

        # Generate embedding for input description
        query_embedding = await self.embedding_service.generate_embedding(
            description
        )

        # Cosine similarity search in pgvector
        results = await self.db.execute(
            select(
                AmenityEmbedding.amenity_id,
                AmenityEmbedding.text,
                AmenityEmbedding.embedding.cosine_distance(query_embedding).label("distance")
            )
            .order_by("distance")
            .limit(20)
        )

        detected = []
        for row in results:
            similarity = 1 - row.distance  # Convert distance to similarity

            if similarity >= threshold:
                detected.append(DetectedAmenity(
                    id=row.amenity_id,
                    confidence=similarity,
                    evidence=f"Text match: '{row.text}' (similarity: {similarity:.2f})"
                ))

        return detected
```

**Option 2: Few-Shot Learning with LLM** (Fallback for ambiguous cases)

```python
FEW_SHOT_AMENITY_EXAMPLES = [
    {
        "input": "The villa has central air conditioning throughout all rooms.",
        "output": [
            {"id": "am_int_air_conditioning", "confidence": 1.0}
        ]
    },
    {
        "input": "Beautiful infinity pool with ocean views.",
        "output": [
            {"id": "am_ext_private_pool", "confidence": 1.0},
            {"id": "loc_sea_view", "confidence": 0.9}
        ]
    },
    {
        "input": "Fully equipped modern kitchen with dishwasher.",
        "output": [
            {"id": "am_int_kitchen", "confidence": 1.0},
            {"id": "am_int_dishwasher", "confidence": 1.0}
        ]
    }
]

async def few_shot_amenity_detection(
    llm: ChatOpenAI,
    description: str,
    catalog: dict[str, list[str]]
) -> list[DetectedAmenity]:
    """Use few-shot learning to detect amenities from text."""

    prompt = f"""Given the property description, identify which amenities from our catalog are present.

## Available Amenities:
{json.dumps(catalog, indent=2)}

## Examples:
{json.dumps(FEW_SHOT_AMENITY_EXAMPLES, indent=2)}

## Property Description:
{description}

## Instructions:
- Only select amenities explicitly mentioned or clearly implied
- Provide confidence score: 1.0 (explicit), 0.8 (strongly implied), 0.5 (uncertain)
- Output JSON array: [{{"id": "...", "confidence": 0.0-1.0}}]
"""

    response = await llm.ainvoke(prompt)
    return parse_amenity_response(response.content)
```

**Option 3: Fine-Tuning** (Future Optimization)

- Collect 1000+ labeled property descriptions with amenity annotations
- Fine-tune smaller model (Llama 3.1 8B) on OpenRouter
- Cost: ~$50-100 one-time, ~$0.001/request after
- Defer to Phase 2

### Image-Based Amenity Detection

```python
async def detect_amenities_from_images(
    images: list[str],  # URLs or base64
    vision_model: ChatOpenAI
) -> list[DetectedAmenity]:
    """Analyze property images to detect visible amenities."""

    # Prepare multi-modal prompt
    image_messages = [
        {
            "type": "image_url",
            "image_url": {"url": img}
        }
        for img in images
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", AMENITY_DETECTION_IMAGE_PROMPT),
        ("user", [
            {"type": "text", "text": "Analyze these property images:"},
            *image_messages
        ])
    ])

    # Use GPT-4o or Claude 3.5 Sonnet (both have vision)
    response = await vision_model.ainvoke(
        prompt.format_messages(),
        model="openai/gpt-4o",  # or "anthropic/claude-3.5-sonnet"
    )

    # Parse structured output
    detected = parse_amenity_detection_response(response.content)

    return detected

# Image Analysis Cost Estimation:
# - GPT-4o: $0.01 per image (high quality)
# - Claude 3.5 Sonnet: $0.008 per image (high quality)
# - 5 images per property = $0.04-0.05 per property
```

### Location Advantage Detection

Similar approach to amenities, but with geographic context:

```python
LOCATION_ADVANTAGE_KEYWORDS = {
    # Waterfront
    "loc_beachfront": ["beachfront", "beach front", "on the beach", "direct beach access"],
    "loc_sea_view": ["sea view", "ocean view", "seaview", "water view"],
    "loc_near_beach": ["near beach", "close to beach", "walking distance to beach", "100m to beach"],

    # Nature
    "loc_mountain_view": ["mountain view", "mountain views", "facing mountains"],
    "loc_forest_view": ["forest view", "jungle view", "surrounded by nature"],

    # Urban
    "loc_city_center": ["city center", "downtown", "central location", "in town"],
    "loc_near_shopping": ["near shopping", "close to mall", "shopping centers nearby"],

    # Transportation
    "loc_near_airport": ["near airport", "close to airport", "5km to airport"],
    "loc_main_road_access": ["main road", "paved road", "easy access"],

    # Character
    "loc_quiet_area": ["quiet", "peaceful", "tranquil", "serene"],
    "loc_private_location": ["private", "secluded", "exclusive"]
}

async def detect_location_advantages(
    description: str,
    location: Optional[str]
) -> list[str]:
    """Detect location advantages from property description."""

    detected = []
    description_lower = description.lower()

    for advantage_id, keywords in LOCATION_ADVANTAGE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description_lower:
                detected.append(advantage_id)
                break  # Found one keyword, move to next advantage

    # Remove duplicates
    return list(set(detected))
```

---

## Multimodal Processing

### Input Type Handling

**1. Text Input**
- Direct LLM processing (Gemini 2.5 Flash Lite)
- Fast, cheap, high accuracy for structured text
- Use case: Agent pastes description from email/website

**2. Image Input**
- Vision model processing (GPT-4o or Claude 3.5 Sonnet)
- Extract: property type, condition, visible amenities, room layout
- Cost: ~$0.01 per image
- Use case: Agent uploads property photos

**3. Voice Input**
- Transcription via Whisper API (OpenAI)
- Then process as text input
- Cost: ~$0.006 per minute
- Use case: Agent records voice note while viewing property

### Model Selection Matrix

| Use Case | Model | Cost (per 1M tokens) | Latency | Why? |
|----------|-------|---------------------|---------|------|
| **Text Extraction** | google/gemini-2.5-flash-lite | Input: $0.075<br>Output: $0.30 | 1-2s | Fast, cheap, excellent for structured data |
| **Image Analysis** | openai/gpt-4o | Input: $0.60<br>Output: $1.80<br>+ $0.01/image | 3-5s/image | Best vision capabilities, accurate amenity detection |
| **Image Analysis (Alt)** | anthropic/claude-3.5-sonnet | Input: $0.80<br>Output: $2.40<br>+ $0.008/image | 3-5s/image | Alternative to GPT-4o, good for complex scenes |
| **Voice Transcription** | openai/whisper-1 | $0.006/min | 1-2s/min | Industry standard, accurate, fast |
| **Property Type Detection** | google/gemini-2.5-flash-lite | Same as text | <1s | Fast classification task |
| **Clarification Questions** | google/gemini-2.5-flash-lite | Same as text | <1s | Conversational, natural language |

### Recommended OpenRouter Models

**Primary Stack (MVP):**
```python
LLM_CONFIG = {
    # Text extraction & conversation
    "text_model": "google/gemini-2.5-flash-lite",

    # Image analysis
    "vision_model": "openai/gpt-4o",

    # Voice transcription (OpenAI direct API, not via OpenRouter)
    "transcription_model": "whisper-1",

    # Embeddings for amenity matching (OpenAI direct)
    "embedding_model": "text-embedding-3-small"
}
```

**Alternative Models (Fallback/Testing):**
```python
FALLBACK_CONFIG = {
    "vision_model_alt": "anthropic/claude-3.5-sonnet",
    "text_model_fast": "google/gemini-2.0-flash-exp",  # Even faster
    "text_model_quality": "anthropic/claude-3.5-sonnet"  # Higher quality for complex cases
}
```

### Voice Input Processing

```python
class VoiceTranscriptionService:
    """Transcribe voice messages using Whisper API."""

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client

    async def transcribe(
        self,
        audio_file: UploadFile
    ) -> TranscriptionResult:
        """Transcribe audio to text using Whisper."""

        # OpenAI Whisper API (not available via OpenRouter)
        response = await self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json",  # Includes timestamps, language
            language="en"  # Or auto-detect
        )

        return TranscriptionResult(
            text=response.text,
            language=response.language,
            duration=response.duration,
            confidence=response.get("confidence", 0.95)
        )

# Cost: $0.006/minute
# Example: 2-minute voice note = $0.012
```

### Image Processing Pipeline

```python
class ImageAnalysisService:
    """Analyze property images using vision models."""

    def __init__(self, vision_llm: ChatOpenAI):
        self.llm = vision_llm

    async def analyze_property_images(
        self,
        images: list[str],  # URLs or base64
        focus: Literal["amenities", "condition", "layout", "all"] = "all"
    ) -> ImageAnalysisResult:
        """Analyze property images for structured extraction."""

        # Build vision prompt based on focus
        if focus == "amenities":
            prompt = AMENITY_DETECTION_IMAGE_PROMPT
        elif focus == "condition":
            prompt = CONDITION_ASSESSMENT_IMAGE_PROMPT
        elif focus == "layout":
            prompt = LAYOUT_ANALYSIS_IMAGE_PROMPT
        else:
            prompt = COMPREHENSIVE_IMAGE_ANALYSIS_PROMPT

        # Prepare multi-modal messages
        image_messages = [
            {
                "type": "image_url",
                "image_url": {
                    "url": img,
                    "detail": "high"  # High detail for better accuracy
                }
            }
            for img in images[:10]  # Max 10 images per request
        ]

        messages = [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Analyze {len(images)} property images:"},
                    *image_messages
                ]
            }
        ]

        # Call vision model
        response = await self.llm.ainvoke(messages)

        # Parse structured output
        analysis = self._parse_image_analysis(response.content)

        return analysis

    def _parse_image_analysis(self, content: str) -> ImageAnalysisResult:
        """Parse LLM response into structured format."""
        # Implementation depends on response format
        # Can use Pydantic parser or JSON extraction
        pass

# Image Analysis Strategies:
# - Batch images (up to 10) to reduce API calls
# - Use "low" detail for thumbnails/previews ($0.001/image)
# - Use "high" detail for final extraction ($0.01/image)
```

---

## Conversation Flow

### Single-Shot vs Multi-Turn

**MVP Approach: Adaptive Multi-Turn**

1. **Single-Shot for Complete Data**
   - Agent provides comprehensive description + images
   - System attempts full extraction in one go
   - If confidence > 0.8 and all required fields present → Done
   - If not → Fall back to multi-turn

2. **Multi-Turn for Incomplete/Ambiguous Data**
   - System extracts what it can with confidence
   - Generates 3-5 clarification questions
   - Agent answers in natural language
   - System updates extraction iteratively

### Conversation States

```python
class ExtractionConversationState(str, Enum):
    INITIAL = "initial"                    # Fresh conversation
    TYPE_DETECTION = "type_detection"      # Detecting property type
    EXTRACTING = "extracting"              # Extracting structured data
    CLARIFYING = "clarifying"              # Asking follow-up questions
    VALIDATING = "validating"              # Final validation
    COMPLETE = "complete"                  # Ready for review
    FAILED = "failed"                      # Extraction failed

class ExtractionConversation(BaseModel):
    conversation_id: int
    state: ExtractionConversationState
    property_type: Optional[PropertyType] = None
    property_type_confidence: float = 0.0
    partial_extraction: Optional[PropertyExtractionResult] = None
    pending_clarifications: list[str] = []
    clarification_history: list[dict] = []
    extraction_attempts: int = 0
    max_attempts: int = 5
```

### Conversation Flow Diagram

```
START
  │
  ▼
┌─────────────────────┐
│ Agent uploads input │
│ (text/images/voice) │
└──────────┬──────────┘
           │
           ▼
┌────────────────────────┐     No      ┌──────────────────────┐
│ Enough data for        │─────────────▶│ Ask for more input   │
│ single-shot extraction?│              │ "Please provide..."  │
└──────────┬─────────────┘              └──────────┬───────────┘
           │ Yes                                    │
           ▼                                        │
┌────────────────────────┐                         │
│ Property Type          │◀────────────────────────┘
│ Detection              │
└──────────┬─────────────┘
           │
           ▼
┌────────────────────────┐     Low     ┌──────────────────────┐
│ Confidence > 0.7?      │─────────────▶│ Ask: "Is this a..."  │
└──────────┬─────────────┘              └──────────┬───────────┘
           │ High                                   │
           ▼                                        │
┌────────────────────────┐                         │
│ Structured Extraction  │◀────────────────────────┘
│ (type-specific)        │
└──────────┬─────────────┘
           │
           ▼
┌────────────────────────┐
│ Validation             │
└──────────┬─────────────┘
           │
           ▼
┌────────────────────────┐     Yes     ┌──────────────────────┐
│ Missing required       │─────────────▶│ Generate             │
│ fields?                │              │ clarification Qs     │
└──────────┬─────────────┘              └──────────┬───────────┘
           │ No                                     │
           │                                        ▼
           │                          ┌──────────────────────┐
           │                          │ Agent answers        │
           │                          └──────────┬───────────┘
           │                                     │
           │                                     ▼
           │                          ┌──────────────────────┐
           │                          │ Update extraction    │
           │                          └──────────┬───────────┘
           │                                     │
           │◀────────────────────────────────────┘
           │
           ▼
┌────────────────────────┐
│ Present property form  │
│ with pre-filled data   │
└──────────┬─────────────┘
           │
           ▼
┌────────────────────────┐
│ Agent reviews &        │
│ confirms/edits         │
└──────────┬─────────────┘
           │
           ▼
┌────────────────────────┐
│ Save to database       │
└──────────┬─────────────┘
           │
           ▼
          END
```

### Example Conversation Flows

**Flow 1: Complete Data (Single-Shot)**
```
Agent: [Uploads text + 5 images]
"3-bedroom pool villa for sale in Phuket. 250 sqm living, 600 sqm land.
Fully furnished, private pool, sea view. 15M THB."

System: [Extracts everything with high confidence]
→ Property type: Sale (confidence: 1.0)
→ All required fields: ✓
→ Status: COMPLETE

System: "I've extracted the property details. Please review:
- Property Type: Pool Villa
- Bedrooms: 3
- Living Area: 250 sqm
- Land Area: 600 sqm
- Price: 15,000,000 THB
- Amenities: Private Pool, Sea View, Fully Furnished
[Show full form for review]"
```

**Flow 2: Missing Data (Multi-Turn)**
```
Agent: [Uploads text]
"Nice villa for rent in Phuket. Good condition, near beach."

System: [Extracts with low confidence]
→ Property type: Rental (confidence: 0.9)
→ Missing: bedrooms, bathrooms, price, exact location
→ Status: CLARIFYING

System: "I need some additional information:
1. How many bedrooms and bathrooms?
2. What's the monthly rental price?
3. Which area of Phuket (e.g., Patong, Kata, Kamala)?
4. How far from the beach (in meters/km)?
5. Any specific amenities (pool, garden, parking)?"

Agent: "3 bed, 2 bath. 45,000 per month. Kata area, 500m to beach. Has pool and garden."

System: [Updates extraction]
→ All required fields: ✓
→ Status: COMPLETE

System: "Perfect! I've updated the details. Please review:
[Show full form with updated data]"
```

**Flow 3: Ambiguous Property Type**
```
Agent: [Uploads text]
"Restaurant with rooms for sale. Prime location, fully equipped,
annual revenue 5M THB. Can operate as hotel or restaurant."

System: [Ambiguous detection]
→ Property type: Business (confidence: 0.6) or Hotel (confidence: 0.4)
→ Status: TYPE_DETECTION

System: "I see this could be either a business sale or a hotel property.
Which best describes it:
A) Operating business (restaurant with rooms) being sold as-is
B) Hotel property that could be repurposed
C) Both business and property included in sale"

Agent: "It's A - selling the business and property together"

System: [Confirmed type]
→ Property type: Business (confidence: 1.0)
→ Continue with business-specific extraction...
```

### Handling Corrections & Refinements

```python
class ExtractionRefinementService:
    """Handle iterative refinement of extracted data."""

    async def apply_correction(
        self,
        extraction: PropertyExtractionResult,
        correction: str
    ) -> PropertyExtractionResult:
        """Apply agent's correction to extraction."""

        # Parse correction using LLM
        correction_prompt = f"""The agent made a correction to the property extraction.

Current extraction:
{extraction.model_dump_json(indent=2)}

Agent's correction:
"{correction}"

Parse the correction and output which fields need to be updated with new values.
Output JSON: {{"field": "new_value", ...}}
"""

        updates = await self.llm.ainvoke(correction_prompt)
        parsed_updates = json.loads(updates.content)

        # Apply updates to extraction
        updated = extraction.copy(deep=True)
        for field, value in parsed_updates.items():
            setattr(updated, field, value)

        # Re-validate
        validation = await self.validator.validate(updated)

        return updated
```

---

## LangChain Implementation

### Architecture Overview

```python
# File Structure:
apps/server/src/server/
├── services/
│   ├── property_extraction/
│   │   ├── __init__.py
│   │   ├── agent.py                    # Main extraction agent
│   │   ├── tools.py                    # LangChain tools
│   │   ├── parsers.py                  # Structured output parsers
│   │   ├── prompts.py                  # Prompt templates
│   │   ├── validators.py               # Validation logic
│   │   └── refinement.py               # Iterative refinement
│   ├── property_extraction_service.py  # Service layer
│   └── ...
├── api/v1/endpoints/properties/
│   ├── extraction.py                   # Extraction endpoint
│   └── ...
└── schemas/
    └── property_extraction.py          # Pydantic schemas
```

### Core Components Implementation

#### 1. Property Extraction Agent

```python
# apps/server/src/server/services/property_extraction/agent.py

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import PostgresChatMessageHistory

from server.llm_config.llm import get_llm_settings
from .tools import (
    create_property_type_tool,
    create_extraction_tool,
    create_amenity_detection_tool,
    create_validation_tool
)
from .prompts import PROPERTY_EXTRACTION_SYSTEM_PROMPT


class PropertyExtractionAgent:
    """LangChain agent for property data extraction."""

    def __init__(
        self,
        db: AsyncSession,
        openrouter_client: httpx.AsyncClient,
        conversation_id: int
    ):
        self.db = db
        self.client = openrouter_client
        self.conversation_id = conversation_id
        self.settings = get_llm_settings()

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.settings.models.parsing_model,
            base_url=self.settings.openrouter_base_url,
            api_key=self.settings.openrouter_api_key,
            temperature=0.3,  # Lower temp for structured extraction
        )

        # Initialize vision LLM for images
        self.vision_llm = ChatOpenAI(
            model="openai/gpt-4o",
            base_url=self.settings.openrouter_base_url,
            api_key=self.settings.openrouter_api_key,
            temperature=0.3,
        )

        # Create tools
        self.tools = self._create_tools()

        # Create agent with memory
        self.agent_executor = self._create_agent()

    def _create_tools(self) -> list:
        """Create LangChain tools for extraction."""
        return [
            create_property_type_tool(self.llm, self.db),
            create_extraction_tool(self.llm, self.db),
            create_amenity_detection_tool(self.vision_llm, self.db),
            create_validation_tool(self.db)
        ]

    def _create_agent(self) -> AgentExecutor:
        """Create agent executor with memory."""

        # Prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", PROPERTY_EXTRACTION_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Memory (integrates with existing conversations table)
        memory = ConversationBufferMemory(
            chat_memory=PostgresChatMessageHistory(
                connection_string=str(self.settings.database_url),
                session_id=str(self.conversation_id)
            ),
            return_messages=True,
            memory_key="chat_history"
        )

        # Create agent
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        # Agent executor
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=memory,
            verbose=True,  # Log tool calls
            max_iterations=10,  # Prevent infinite loops
            early_stopping_method="generate"
        )

    async def extract(
        self,
        input_data: PropertyInput
    ) -> PropertyExtractionResult:
        """Run extraction agent on input data."""

        # Format input for agent
        input_text = self._format_input(input_data)

        # Invoke agent
        result = await self.agent_executor.ainvoke({
            "input": input_text
        })

        # Parse agent output
        extraction = self._parse_agent_output(result["output"])

        return extraction

    def _format_input(self, input_data: PropertyInput) -> str:
        """Format multi-modal input for agent."""

        parts = []

        if input_data.text:
            parts.append(f"Text Description:\n{input_data.text}")

        if input_data.images:
            parts.append(f"\nImages: {len(input_data.images)} photos provided")

        if input_data.voice_transcription:
            parts.append(f"\nVoice Note:\n{input_data.voice_transcription}")

        return "\n\n".join(parts)
```

#### 2. LangChain Tools

```python
# apps/server/src/server/services/property_extraction/tools.py

from langchain.tools import StructuredTool
from langchain_core.pydantic_v1 import BaseModel, Field


class PropertyTypeInput(BaseModel):
    """Input for property type detection tool."""
    description: str = Field(description="Property description text")


class PropertyTypeOutput(BaseModel):
    """Output from property type detection tool."""
    property_type: str
    confidence: float
    reasoning: str


def create_property_type_tool(llm, db) -> StructuredTool:
    """Create tool for property type detection."""

    async def detect_property_type(description: str) -> dict:
        """Detect property type from description."""

        from .prompts import PROPERTY_TYPE_DETECTION_PROMPT

        prompt = PROPERTY_TYPE_DETECTION_PROMPT.format(
            input_data=description
        )

        response = await llm.ainvoke(prompt)

        # Parse response (assume JSON output)
        import json
        result = json.loads(response.content)

        return result

    return StructuredTool.from_function(
        func=detect_property_type,
        name="detect_property_type",
        description="Detect property type (rental/sale/lease/business/investment) from description",
        args_schema=PropertyTypeInput,
        return_direct=False
    )


def create_extraction_tool(llm, db) -> StructuredTool:
    """Create tool for structured data extraction."""

    async def extract_property_data(
        property_type: str,
        description: str
    ) -> dict:
        """Extract structured property data."""

        from .parsers import PropertyExtractionParser

        parser = PropertyExtractionParser(property_type=property_type)

        prompt = parser.get_prompt().format(description=description)

        response = await llm.ainvoke(prompt)

        # Use Pydantic parser for structured output
        extraction = parser.parse(response.content)

        return extraction.dict()

    return StructuredTool.from_function(
        func=extract_property_data,
        name="extract_property_data",
        description="Extract structured property fields based on detected type",
        args_schema=ExtractionInput
    )


def create_amenity_detection_tool(vision_llm, db) -> StructuredTool:
    """Create tool for amenity detection from images."""

    async def detect_amenities(
        images: list[str],
        description: Optional[str] = None
    ) -> dict:
        """Detect amenities from images and text."""

        from .image_analyzer import ImageAnalysisService
        from .amenity_matcher import AmenityRAGMatcher

        results = {"text_amenities": [], "image_amenities": []}

        # Text-based amenity detection
        if description:
            text_matcher = AmenityRAGMatcher(db)
            text_amenities = await text_matcher.match_amenities(description)
            results["text_amenities"] = [a.dict() for a in text_amenities]

        # Image-based amenity detection
        if images:
            image_analyzer = ImageAnalysisService(vision_llm)
            image_analysis = await image_analyzer.analyze_property_images(
                images=images,
                focus="amenities"
            )
            results["image_amenities"] = image_analysis.amenities

        # Merge and deduplicate
        all_amenities = merge_amenity_detections(
            results["text_amenities"],
            results["image_amenities"]
        )

        return {"amenities": all_amenities}

    return StructuredTool.from_function(
        func=detect_amenities,
        name="detect_amenities",
        description="Detect property amenities from images and text description",
        args_schema=AmenityDetectionInput
    )


def create_validation_tool(db) -> StructuredTool:
    """Create tool for extraction validation."""

    async def validate_extraction(extraction_json: str) -> dict:
        """Validate extracted property data."""

        from .validators import PropertyValidator

        # Parse JSON
        import json
        extraction_dict = json.loads(extraction_json)

        # Validate
        validator = PropertyValidator(db)
        validation = await validator.validate(extraction_dict)

        return {
            "is_valid": validation.is_valid,
            "errors": validation.errors,
            "warnings": validation.warnings,
            "missing_fields": validation.missing_fields
        }

    return StructuredTool.from_function(
        func=validate_extraction,
        name="validate_extraction",
        description="Validate extracted property data for completeness and consistency",
        args_schema=ValidationInput
    )
```

#### 3. Structured Output Parsers

```python
# apps/server/src/server/services/property_extraction/parsers.py

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from server.schemas.property_extraction import (
    PropertyExtractionResult,
    RentalDetailsExtraction,
    SaleDetailsExtraction
)


class PropertyExtractionParser:
    """Parser for structured property extraction."""

    def __init__(self, property_type: str):
        self.property_type = property_type
        self.parser = self._create_parser()

    def _create_parser(self) -> PydanticOutputParser:
        """Create Pydantic parser based on property type."""

        # Select schema based on property type
        if self.property_type == "rental":
            schema = RentalDetailsExtraction
        elif self.property_type == "sale":
            schema = SaleDetailsExtraction
        # ... other types
        else:
            schema = PropertyExtractionResult

        return PydanticOutputParser(pydantic_object=schema)

    def get_prompt(self) -> PromptTemplate:
        """Get prompt template with format instructions."""

        template = """Extract structured property information from the description.

{format_instructions}

Property Description:
{description}

Extracted Data:"""

        return PromptTemplate(
            template=template,
            input_variables=["description"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            }
        )

    def parse(self, output: str):
        """Parse LLM output into Pydantic model."""
        return self.parser.parse(output)
```

### Integration with Existing Services

```python
# apps/server/src/server/services/property_extraction_service.py

from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from .property_extraction.agent import PropertyExtractionAgent
from .conversation_service import ConversationService
from server.schemas.property_extraction import PropertyInput, PropertyExtractionResult


class PropertyExtractionService:
    """Service layer for property extraction (integrates with existing architecture)."""

    def __init__(
        self,
        db: AsyncSession,
        openrouter_client: httpx.AsyncClient
    ):
        self.db = db
        self.client = openrouter_client
        self.conversation_service = ConversationService(db)

    async def extract_property(
        self,
        input_data: PropertyInput,
        session_id: str,
        user_id: Optional[int] = None
    ) -> PropertyExtractionResult:
        """Extract property data from multi-modal input."""

        # Get or create conversation
        conversation = await self.conversation_service.get_or_create_conversation(
            session_id=session_id,
            user_id=user_id
        )

        # Create extraction agent
        agent = PropertyExtractionAgent(
            db=self.db,
            openrouter_client=self.client,
            conversation_id=conversation.id
        )

        # Run extraction
        result = await agent.extract(input_data)

        # Save extraction to database (for review/audit)
        await self._save_extraction(
            conversation_id=conversation.id,
            extraction=result
        )

        return result

    async def refine_extraction(
        self,
        extraction_id: int,
        clarification: str
    ) -> PropertyExtractionResult:
        """Refine extraction based on clarification."""

        # Load existing extraction
        extraction = await self._load_extraction(extraction_id)

        # Apply refinement
        agent = PropertyExtractionAgent(
            db=self.db,
            openrouter_client=self.client,
            conversation_id=extraction.conversation_id
        )

        refined = await agent.refine(extraction, clarification)

        return refined
```

---

## Performance & Cost Analysis

### Cost Breakdown per Property

**Scenario 1: Text-Only Extraction**
```
Input: 500 words description (~650 tokens)

Costs:
- Property type detection: 650 input + 100 output = 750 tokens
  → Gemini 2.5 Flash Lite: $0.000056
- Structured extraction: 650 input + 500 output = 1150 tokens
  → Gemini 2.5 Flash Lite: $0.000236
- Amenity matching (RAG): 100 tokens embedding
  → text-embedding-3-small: $0.000002
- Validation: 500 tokens
  → Gemini 2.5 Flash Lite: $0.000068

Total per property: ~$0.000362 (~$0.36 per 1000 properties)
```

**Scenario 2: Text + 5 Images**
```
Input: 500 words + 5 property photos

Costs:
- Text extraction: $0.000362 (from above)
- Image analysis (GPT-4o): 5 images × $0.01 = $0.05
- Image amenity detection: 1500 tokens
  → GPT-4o: $0.0009
- Merge & validation: $0.000068

Total per property: ~$0.051 (~$51 per 1000 properties)
```

**Scenario 3: Text + Images + Voice**
```
Input: 500 words + 5 photos + 2-minute voice note

Costs:
- Text + images: $0.051 (from above)
- Voice transcription (Whisper): 2 min × $0.006/min = $0.012
- Process transcription: $0.000362

Total per property: ~$0.063 (~$63 per 1000 properties)
```

### Cost Estimates for 1000 Properties

| Scenario | Per Property | 1000 Properties | Notes |
|----------|--------------|-----------------|-------|
| **Text Only** | $0.012 | **$12** | Fast, cheapest, good for well-structured listings |
| **Text + 5 Images** | $0.15 | **$150** | Recommended for MVP, accurate amenity detection |
| **Text + 10 Images** | $0.25 | **$250** | More comprehensive, better for luxury properties |
| **With Voice (2 min)** | +$0.012 | +$12 | Useful for on-site property tours |
| **With Clarifications (2 rounds)** | +$0.05 | +$50 | Multi-turn conversation for missing data |

**Monthly Estimates (for 100 properties/month):**
- Text + 5 images: ~$15/month
- Text + 10 images: ~$25/month
- With voice + clarifications: ~$30-40/month

**Compared to manual data entry:**
- Manual agent time: 30-45 min per property × $20/hr = $10-15 per property
- LLM-assisted: 5-10 min review × $20/hr + $0.15 API cost = $2-4 per property
- **Savings: 70-80% reduction in labor costs**

### Performance Benchmarks

| Operation | Target Latency | Expected Latency | Optimization |
|-----------|----------------|------------------|--------------|
| **Text Extraction** | <5s | 2-4s | Use Gemini Flash for speed |
| **Image Analysis (5 photos)** | <20s | 15-20s | Batch images in single API call |
| **Voice Transcription (2 min)** | <10s | 8-10s | Whisper API is fast |
| **Property Type Detection** | <2s | 1-2s | Simple classification task |
| **Amenity Matching (RAG)** | <1s | 0.5-1s | Cached embeddings, pgvector index |
| **Validation** | <1s | 0.5s | Local logic, minimal LLM calls |
| **Full Extraction (text + images)** | <25s | 20-25s | Parallel processing where possible |

### Optimization Strategies

**1. Token Optimization**
```python
# Minimize prompt tokens
OPTIMIZATIONS = {
    "System Prompt": {
        "before": 1500 tokens,
        "after": 800 tokens,
        "savings": "47%",
        "method": "Remove redundant instructions, use concise language"
    },
    "Few-Shot Examples": {
        "before": 1000 tokens,
        "after": 300 tokens,
        "savings": "70%",
        "method": "Use 2-3 examples instead of 5, compress JSON"
    },
    "Context Window": {
        "before": 8000 tokens,
        "after": 2000 tokens,
        "savings": "75%",
        "method": "Only include last 5 conversation turns, not full history"
    }
}
```

**2. Caching Strategies**
```python
CACHE_CONFIG = {
    # Catalog embeddings (amenities, locations)
    "amenity_embeddings": {
        "ttl": 7 * 24 * 3600,  # 7 days
        "storage": "Redis",
        "size": "~2MB for 165 amenities"
    },

    # Property type detection rules
    "type_detection_rules": {
        "ttl": 24 * 3600,  # 24 hours
        "storage": "Redis",
        "size": "~10KB"
    },

    # LLM responses for identical inputs
    "llm_response_cache": {
        "ttl": 3600,  # 1 hour
        "storage": "Redis",
        "size": "varies",
        "key": "hash(model + prompt + input)"
    },

    # Processed images (thumbnails)
    "image_thumbnails": {
        "ttl": 7 * 24 * 3600,  # 7 days
        "storage": "R2/S3",
        "size": "~50KB per image"
    }
}
```

**3. Model Selection Trade-offs**

| Aspect | Gemini 2.5 Flash Lite | GPT-4o | Claude 3.5 Sonnet |
|--------|----------------------|--------|-------------------|
| **Cost (1M tokens)** | $0.075 / $0.30 | $0.60 / $1.80 | $0.80 / $2.40 |
| **Speed** | ⚡⚡⚡ Very Fast (1-2s) | ⚡⚡ Fast (2-4s) | ⚡⚡ Fast (2-4s) |
| **Accuracy (text)** | ⭐⭐⭐⭐ 85% | ⭐⭐⭐⭐⭐ 95% | ⭐⭐⭐⭐⭐ 95% |
| **Vision Support** | ❌ No | ✅ Excellent | ✅ Excellent |
| **Structured Output** | ✅ Good | ✅ Excellent | ✅ Excellent |
| **Use Case** | Text extraction, type detection, conversation | Image analysis, complex extraction | Alternative to GPT-4o |

**Recommendation:**
- **Text tasks**: Gemini 2.5 Flash Lite (4x cheaper, fast enough)
- **Image tasks**: GPT-4o (best vision + cost balance)
- **Complex cases**: Claude 3.5 Sonnet (fallback if GPT-4o fails)

---

## Error Handling & Resilience

### Error Categories

1. **API Errors** (OpenRouter/OpenAI)
   - Rate limits (429)
   - Timeout errors
   - Model unavailable (503)
   - Invalid API key (401)

2. **Extraction Errors**
   - Low confidence detection
   - Missing required fields
   - Invalid data format
   - Inconsistent data

3. **User Input Errors**
   - Unsupported file format
   - Image too large
   - Voice file corrupted
   - Empty input

### Error Handling Strategy

```python
class ExtractionError(Exception):
    """Base class for extraction errors."""
    pass


class LowConfidenceError(ExtractionError):
    """Raised when extraction confidence is too low."""

    def __init__(self, field: str, confidence: float):
        self.field = field
        self.confidence = confidence
        super().__init__(
            f"Low confidence for {field}: {confidence:.2f}"
        )


class MissingRequiredFieldError(ExtractionError):
    """Raised when required fields are missing."""

    def __init__(self, missing_fields: list[str]):
        self.missing_fields = missing_fields
        super().__init__(
            f"Missing required fields: {', '.join(missing_fields)}"
        )


# Error Handlers

async def handle_api_error(error: httpx.HTTPStatusError):
    """Handle OpenRouter API errors with retries."""

    if error.response.status_code == 429:
        # Rate limit - wait and retry
        retry_after = error.response.headers.get("Retry-After", 60)
        await asyncio.sleep(int(retry_after))
        raise RetryableError("Rate limited, retry after delay")

    elif error.response.status_code == 503:
        # Model unavailable - try fallback
        raise FallbackRequiredError("Primary model unavailable")

    elif error.response.status_code >= 500:
        # Server error - retry
        raise RetryableError("OpenRouter server error")

    else:
        # Client error (400, 401, etc.) - don't retry
        raise ExtractionError(f"API error: {error.response.status_code}")


async def handle_extraction_error(
    error: ExtractionError,
    context: dict
) -> dict:
    """Handle extraction errors gracefully."""

    if isinstance(error, LowConfidenceError):
        # Return partial extraction + clarification
        return {
            "status": "needs_clarification",
            "partial_data": context.get("partial_extraction"),
            "clarification_needed": error.field,
            "confidence": error.confidence
        }

    elif isinstance(error, MissingRequiredFieldError):
        # Generate questions for missing fields
        questions = generate_clarification_questions(
            error.missing_fields
        )
        return {
            "status": "incomplete",
            "partial_data": context.get("partial_extraction"),
            "questions": questions
        }

    else:
        # Unknown error - log and return safe failure
        logger.error(f"Extraction error: {error}", extra=context)
        return {
            "status": "failed",
            "error": "Unable to extract property data",
            "details": str(error)
        }
```

### Fallback Strategies

**1. Model Fallback Chain**
```python
MODEL_FALLBACK_CHAIN = [
    "google/gemini-2.5-flash-lite",     # Primary (fast, cheap)
    "google/gemini-2.0-flash-exp",      # Fallback 1 (slightly slower)
    "anthropic/claude-3.5-sonnet",      # Fallback 2 (expensive, reliable)
]

async def extract_with_fallback(prompt: str) -> str:
    """Try extraction with model fallback."""

    last_error = None

    for model in MODEL_FALLBACK_CHAIN:
        try:
            llm = ChatOpenAI(model=model, ...)
            response = await llm.ainvoke(prompt)
            return response.content
        except Exception as e:
            last_error = e
            logger.warning(f"Model {model} failed: {e}")
            continue

    # All models failed
    raise ExtractionError(
        f"All models failed. Last error: {last_error}"
    )
```

**2. Progressive Degradation**
```python
async def extract_with_degradation(input_data: PropertyInput):
    """Try full extraction, fall back to partial if needed."""

    try:
        # Try full extraction with images
        return await extract_full(input_data)
    except Exception as e:
        logger.warning("Full extraction failed, trying text-only")

        try:
            # Fall back to text-only extraction
            return await extract_text_only(input_data.text)
        except Exception as e2:
            logger.warning("Text extraction failed, trying minimal")

            # Last resort: extract only critical fields
            return await extract_minimal(input_data.text)
```

**3. Retry with Exponential Backoff**
```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

@retry(
    retry=retry_if_exception_type((
        httpx.TimeoutException,
        httpx.ConnectError,
        RetryableError
    )),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(3),
)
async def extract_with_retry(input_data: PropertyInput):
    """Extract with automatic retries for transient errors."""
    return await extraction_service.extract(input_data)
```

### Validation & Data Quality

```python
class DataQualityChecker:
    """Ensure extracted data meets quality standards."""

    QUALITY_THRESHOLDS = {
        "overall_confidence": 0.6,
        "required_field_confidence": 0.7,
        "price_confidence": 0.8,
        "location_confidence": 0.7
    }

    async def check_quality(
        self,
        extraction: PropertyExtractionResult
    ) -> QualityReport:
        """Check data quality and flag issues."""

        issues = []

        # Check overall confidence
        if extraction.extraction_confidence < self.QUALITY_THRESHOLDS["overall_confidence"]:
            issues.append({
                "severity": "warning",
                "field": "overall",
                "message": f"Low overall confidence: {extraction.extraction_confidence:.2f}"
            })

        # Check required fields confidence
        for field, value in extraction.dict().items():
            if field in REQUIRED_FIELDS:
                confidence = self._get_field_confidence(extraction, field)
                if confidence < self.QUALITY_THRESHOLDS["required_field_confidence"]:
                    issues.append({
                        "severity": "error",
                        "field": field,
                        "message": f"Low confidence for required field: {confidence:.2f}"
                    })

        # Check price reasonableness
        if extraction.sale_details:
            price = extraction.sale_details.sale_price
            if not self._is_price_reasonable(price):
                issues.append({
                    "severity": "warning",
                    "field": "sale_price",
                    "message": f"Price seems unreasonable: {price:,.0f}"
                })

        return QualityReport(
            passed=len([i for i in issues if i["severity"] == "error"]) == 0,
            issues=issues,
            overall_quality_score=self._calculate_quality_score(extraction, issues)
        )
```

---

## MVP Roadmap

### Phase 1: Foundation (Week 1-2)

**Goal**: Core extraction pipeline with text-only support

**Deliverables:**
- [ ] LangChain agent setup with basic tools
- [ ] Property type detection (text-based)
- [ ] Structured extraction for rental + sale types
- [ ] Pydantic schemas for all property types
- [ ] Validation logic
- [ ] Basic API endpoint: POST /api/v1/properties/extract
- [ ] Unit tests (80% coverage target)

**Models Required:**
- Gemini 2.5 Flash Lite (text extraction)

**Estimated Cost:** ~$50 for development testing (1000 test extractions)

**Success Criteria:**
- Property type detection: >90% accuracy
- Required field extraction: >85% accuracy
- Processing time: <5s per property
- API endpoint functional with error handling

---

### Phase 2: Image Analysis (Week 3-4)

**Goal**: Add vision capabilities for amenity detection

**Deliverables:**
- [ ] Image upload handling (multipart/form-data)
- [ ] Image preprocessing (resize, format conversion)
- [ ] Vision model integration (GPT-4o)
- [ ] Image-based amenity detection tool
- [ ] Text + image fusion logic
- [ ] RAG-based amenity matching (using pgvector)
- [ ] Image storage (Cloudflare R2)
- [ ] Updated API with image support

**Models Required:**
- GPT-4o (vision)
- text-embedding-3-small (amenity embeddings)

**Estimated Cost:** ~$200 for development (1000 properties × 5 images each)

**Success Criteria:**
- Amenity detection (images): >80% accuracy
- Processing time: <20s for 5 images
- Image storage working with R2
- Amenity catalog embeddings generated

---

### Phase 3: Multi-Turn Conversation (Week 5)

**Goal**: Implement clarification questions for missing data

**Deliverables:**
- [ ] Conversation state management
- [ ] Clarification question generation
- [ ] Iterative refinement logic
- [ ] WebSocket support for real-time updates (optional)
- [ ] Conversation history UI integration
- [ ] Agent correction handling

**Models Required:**
- Same as Phase 1 (Gemini for conversation)

**Estimated Cost:** ~$30 for testing (500 multi-turn conversations)

**Success Criteria:**
- Clarification questions: natural & relevant
- Conversation memory: works across turns
- Refinement: correctly updates extraction
- Average turns to completion: <3

---

### Phase 4: Voice Input (Week 6)

**Goal**: Add voice recording and transcription

**Deliverables:**
- [ ] Voice recording component (frontend)
- [ ] Audio file upload handling
- [ ] Whisper API integration for transcription
- [ ] Voice + text fusion logic
- [ ] Audio storage (R2)

**Models Required:**
- Whisper-1 (transcription)

**Estimated Cost:** ~$60 for testing (1000 × 2-min voice notes)

**Success Criteria:**
- Transcription accuracy: >95% (English)
- Processing time: <10s per 2-min voice note
- Voice + text extraction: works seamlessly

---

### Phase 5: Frontend Integration (Week 7-8)

**Goal**: Complete agent-facing UI for property extraction

**Deliverables:**
- [ ] Property extraction chat interface (SvelteKit 5)
- [ ] File upload component (drag & drop)
- [ ] Voice recording component
- [ ] Property review form with pre-filled data
- [ ] Edit & confirm workflow
- [ ] Real-time extraction status
- [ ] Error handling & retry UI
- [ ] Mobile-responsive design

**Tech Stack:**
- SvelteKit 5 (Runes)
- TanStack Query for API calls
- WebSocket for real-time updates
- Tailwind CSS 4

**Success Criteria:**
- Complete extraction flow: upload → extract → review → save
- Mobile-friendly (agents use phones on-site)
- Loading states & error handling
- Agent can edit extracted data before saving

---

### Phase 6: Testing & Optimization (Week 9-10)

**Goal**: Production-ready quality & performance

**Deliverables:**
- [ ] Integration tests (E2E)
- [ ] Performance benchmarks
- [ ] Cost analysis & optimization
- [ ] Error handling improvements
- [ ] Agent user testing (5-10 agents)
- [ ] Bug fixes from testing
- [ ] Documentation (API, agent guide)
- [ ] Monitoring & logging setup

**Success Criteria:**
- 95% extraction success rate
- <30s total extraction time (text + images)
- <$0.20 average cost per property
- Zero data loss incidents
- Agent satisfaction: 4/5 or higher

---

### Phase 7: Production Launch (Week 11)

**Goal**: Deploy to production with monitoring

**Deliverables:**
- [ ] Production deployment (Docker)
- [ ] Database migrations (Alembic)
- [ ] Monitoring dashboards (Grafana/DataDog)
- [ ] Alerting setup (errors, costs, latency)
- [ ] Agent training materials
- [ ] Rollout plan (gradual rollout to agents)
- [ ] Support documentation

**Success Criteria:**
- Zero downtime deployment
- All monitoring metrics green
- 10+ agents using system successfully
- <1% error rate in production

---

## MVP Feature Prioritization

### Must-Have (MVP Scope)

| Feature | Priority | Effort | Impact | Rationale |
|---------|----------|--------|--------|-----------|
| **Text-based extraction** | P0 | Medium | High | Core functionality, no external deps |
| **Property type detection** | P0 | Small | High | Required for all extractions |
| **Rental + Sale types** | P0 | Medium | High | Cover 90% of use cases |
| **Image analysis (5 photos)** | P0 | High | High | Visual data critical for accuracy |
| **Amenity detection** | P0 | High | High | Key differentiator, reduces manual work |
| **Validation & confidence** | P0 | Medium | High | Data quality assurance |
| **Clarification questions** | P0 | Medium | Medium | Handles incomplete data gracefully |
| **Property review form** | P0 | High | High | Agent must confirm before saving |
| **Basic error handling** | P0 | Small | High | Production requirement |

### Should-Have (Post-MVP)

| Feature | Priority | Effort | Impact | Rationale |
|---------|----------|--------|--------|-----------|
| **Voice input** | P1 | Medium | Medium | Useful for on-site tours, but not critical |
| **Lease type support** | P1 | Small | Low | Only 10% of properties |
| **Business type support** | P1 | Medium | Low | Niche use case |
| **Investment type support** | P1 | Medium | Low | Very niche |
| **Auto-translation** | P1 | Medium | Medium | Can do manually for MVP |
| **Location geocoding** | P1 | Small | Medium | Nice-to-have, can add address manually |
| **Duplicate detection** | P1 | High | Medium | Prevent duplicates, but low priority |

### Could-Have (Future)

| Feature | Priority | Effort | Impact | Rationale |
|---------|----------|--------|--------|-----------|
| **Video analysis** | P2 | High | Low | Cool but expensive, defer |
| **360° virtual tour parsing** | P2 | High | Low | Niche, complex |
| **PDF/document parsing** | P2 | Medium | Low | Most agents use photos |
| **Bulk extraction (CSV)** | P2 | High | Medium | For migration, not daily use |
| **AI-generated descriptions** | P2 | Small | Medium | Can use existing descriptions |
| **Market price estimation** | P2 | High | High | Requires market data, complex |
| **Fine-tuned extraction model** | P2 | Very High | Medium | Optimization for cost/speed |

### Won't Have (Out of Scope)

- Property valuation/appraisal
- Competitive analysis
- Lead generation
- Automated marketing content
- Social media posting
- Property matching/recommendations

---

## Risk Mitigation

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **LLM hallucinations** | High | High | Confidence scoring, validation, agent review required |
| **API rate limits** | Medium | Medium | Retry logic, fallback models, batch processing |
| **High API costs** | Medium | High | Token optimization, caching, model selection |
| **Image quality issues** | High | Medium | Image preprocessing, quality checks, ask for better photos |
| **Transcription errors** | Medium | Low | Show transcription to agent for verification |
| **Database performance** | Low | Medium | pgvector indexing, query optimization, caching |

### Business Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Low agent adoption** | Medium | High | User testing, training, gradual rollout |
| **Data quality issues** | High | High | Mandatory review step, validation, confidence thresholds |
| **Privacy concerns** | Low | High | No PII stored, GDPR compliance, data retention policy |
| **Competitive pressure** | Medium | Medium | Fast iteration, unique catalog, integration advantage |

### Operational Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Support burden** | Medium | Medium | Documentation, FAQs, agent training |
| **Monitoring gaps** | Medium | High | Comprehensive logging, alerting, dashboards |
| **Scaling issues** | Low | High | Async processing, queue system, rate limiting |

---

## Appendix A: Sample Prompts

### Full Property Type Detection Prompt

```python
PROPERTY_TYPE_DETECTION_PROMPT = """You are a property classification expert. Analyze the property information and determine the property type.

## Property Types

**Rental** - Properties available for rent (short-term or long-term)
- Keywords: "for rent", "monthly rent", "per night", "vacation rental", "available from"
- Price format: X THB/month, X USD/night, X EUR/week
- Common indicators: deposit, lease term, availability dates

**Sale** - Properties for sale
- Keywords: "for sale", "selling price", "purchase", "buy", "ownership"
- Price format: X THB, X million, X M
- Common indicators: freehold, leasehold, title deed, transfer fees

**Lease** - Long-term commercial or residential leases (typically multi-year)
- Keywords: "lease", "lease contract", "lease term", "long-term agreement"
- Price format: X THB/year, X THB/month (3-year lease)
- Common indicators: key money, lease duration, renewal option, escalation clause

**Business** - Operating businesses for sale (includes property + operations)
- Keywords: "business for sale", "restaurant for sale", "hotel for sale", "with license"
- Price format: X THB (includes business), X M THB (turnkey)
- Common indicators: annual revenue, profit, employees, customers, license

**Investment** - Investment opportunities or development projects
- Keywords: "investment opportunity", "ROI", "yield", "development project", "off-plan"
- Price format: X THB investment, X% ROI, X% yield
- Common indicators: projected returns, completion date, developer, exit strategy

## Detection Process

1. Look for explicit transaction type keywords
2. Analyze pricing format and structure
3. Check for type-specific indicators (revenue, lease terms, ROI, etc.)
4. Consider context and business model
5. Assign confidence score based on clarity

## Input Data

{input_data}

## Output Format

Return JSON with this exact structure:
```json
{
  "property_type": "rental|sale|lease|business|investment",
  "confidence": 0.0-1.0,
  "reasoning": "Clear explanation of why this type was chosen",
  "detected_features": ["keyword1", "keyword2", "price_pattern"],
  "alternative_types": [
    {"type": "...", "confidence": 0.0-1.0, "reason": "..."}
  ] // Only if confidence < 0.9
}
```

## Confidence Scoring Guide

- **1.0**: Explicit keyword + clear price format + no ambiguity
- **0.9**: Strong keywords + expected indicators + clear context
- **0.8**: Multiple indicators + price format matches
- **0.7**: Some indicators + reasonable inference
- **0.5**: Ambiguous, multiple interpretations possible
- **0.3**: Very unclear, mostly guessing

## Examples

Input: "3-bedroom villa for rent, 45,000 THB/month"
Output: {{"property_type": "rental", "confidence": 1.0, "reasoning": "Explicit 'for rent' with monthly price"}}

Input: "Restaurant business for sale, 5M THB, includes equipment and license, revenue 3M/year"
Output: {{"property_type": "business", "confidence": 1.0, "reasoning": "Clear 'business for sale' with revenue mentioned"}}

Input: "Beautiful property, good location, 10M THB"
Output: {{"property_type": "sale", "confidence": 0.7, "reasoning": "One-time price suggests sale, but no explicit keyword", "alternative_types": [{{"type": "investment", "confidence": 0.3, "reason": "Could be investment if context missing"}}]}}
"""
```

### Full Amenity Detection (Images) Prompt

```python
AMENITY_DETECTION_IMAGE_PROMPT = """You are a property amenity detection specialist. Analyze the provided images and identify visible amenities from our catalog.

## Instructions

1. **Only mark amenities that are clearly visible** in the images
2. **Provide confidence score** for each detected amenity:
   - 1.0 = Definitely visible (no doubt)
   - 0.9 = Very likely present (clear indicators)
   - 0.8 = Likely present (partial view or indirect evidence)
   - 0.7 = Possibly present (unclear or ambiguous)
   - Below 0.7 = Don't include
3. **Explain evidence** for each detection (which image, what you saw)
4. **Don't assume** amenities not visible in photos

## Amenity Catalog

### Interior Amenities

**Climate Control:**
- am_int_air_conditioning: Air conditioning units (wall-mounted, ceiling cassette, or central AC)
- am_int_ceiling_fans: Ceiling fans
- am_int_heating: Heating system (radiators, underfloor heating)

**Kitchen:**
- am_int_kitchen: Fully equipped kitchen with appliances
- am_int_refrigerator: Fridge/freezer
- am_int_oven: Cooking oven
- am_int_microwave: Microwave oven
- am_int_dishwasher: Dishwasher

**Appliances:**
- am_int_washing_machine: Clothes washing machine
- am_int_dryer: Clothes dryer

**Storage:**
- am_int_wardrobes: Built-in wardrobes or closets
- am_int_walk_in_closet: Walk-in closet

**Entertainment:**
- am_int_tv: Television
- am_int_sound_system: Audio/sound system
- am_int_wifi: WiFi (visible router or mentioned)

**Furniture:**
- am_int_furniture: Furnished (beds, sofas, tables visible)

### Exterior Amenities

**Pool & Water:**
- am_ext_private_pool: Private swimming pool
- am_ext_jacuzzi: Hot tub/jacuzzi
- am_ext_pool_heating: Pool heating (look for heater unit)
- am_ext_pool_fence: Pool safety fence

**Outdoor Living:**
- am_ext_garden: Garden with landscaping
- am_ext_terrace: Terrace or patio
- am_ext_balcony: Balcony
- am_ext_bbq_area: BBQ/grilling area
- am_ext_outdoor_dining: Outdoor dining table/area
- am_ext_sala: Thai-style sala/pavilion
- am_ext_sun_deck: Sun deck or lounging area

**Recreation:**
- am_ext_outdoor_gym: Outdoor fitness equipment
- am_ext_playground: Children's playground
- am_ext_sports_court: Tennis/basketball court

**Security:**
- am_ext_fence: Property fence
- am_ext_security_cameras: Outdoor security cameras

**Parking:**
- am_ext_covered_parking: Covered parking (carport/garage)
- am_ext_parking_spaces: Parking area (count spaces if visible)

### Building Amenities (if property is in condo/complex)

**Security:**
- am_bld_24h_security: 24-hour security (guard booth visible)
- am_bld_cctv: CCTV cameras in common areas
- am_bld_security_gate: Security gate/entrance
- am_bld_key_card_access: Key card access system

**Facilities:**
- am_bld_elevator: Elevator/lift
- am_bld_gym: Fitness center/gym
- am_bld_communal_pool: Communal swimming pool
- am_bld_spa: Spa facilities
- am_bld_sauna: Sauna
- am_bld_restaurant: On-site restaurant/cafe
- am_bld_coworking: Coworking space
- am_bld_meeting_rooms: Meeting rooms

**Services:**
- am_bld_concierge: Concierge desk
- am_bld_reception: Reception area

## Output Format

Return JSON with this structure:
```json
{
  "interior_amenities": [
    {
      "id": "am_int_air_conditioning",
      "confidence": 1.0,
      "evidence": "Wall-mounted AC units visible in image 1 (bedroom) and image 3 (living room)"
    }
  ],
  "exterior_amenities": [
    {
      "id": "am_ext_private_pool",
      "confidence": 1.0,
      "evidence": "Large private pool visible in image 2, approximately 8x4 meters"
    }
  ],
  "building_amenities": [
    {
      "id": "am_bld_24h_security",
      "confidence": 0.8,
      "evidence": "Security booth visible at entrance in image 5"
    }
  ],
  "special_features": [
    "High ceilings (approximately 4 meters)",
    "Marble flooring throughout",
    "Floor-to-ceiling windows with sea view"
  ],
  "property_condition": "excellent",
  "furnished": "fully",
  "overall_impression": "Luxury property with modern finishes, well-maintained, move-in ready"
}
```

## Image Analysis Tips

- **Count items**: If you see multiple bedrooms, note approximate count
- **Assess quality**: Note condition (new, excellent, good, needs work)
- **Identify views**: Sea view, mountain view, garden view, city view
- **Check finishes**: Flooring type, fixtures quality, furniture style
- **Look for unique features**: Smart home tech, custom built-ins, artwork

Analyze the images now and provide structured amenity detection.
"""
```

---

## Appendix B: Database Schema Extensions

### New Tables Required

```sql
-- Property Extraction Metadata Table
CREATE TABLE property_extractions (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    extraction_data JSONB NOT NULL,  -- Full PropertyExtractionResult
    property_type VARCHAR(50),
    extraction_confidence DECIMAL(3, 2),  -- 0.00-1.00
    extraction_status VARCHAR(20) DEFAULT 'pending',  -- pending, complete, failed
    source_types TEXT[],  -- ['text', 'images', 'voice']
    source_file_urls TEXT[],  -- URLs to uploaded files (R2)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_property_extractions_conversation ON property_extractions(conversation_id);
CREATE INDEX idx_property_extractions_status ON property_extractions(extraction_status);
CREATE INDEX idx_property_extractions_property_type ON property_extractions(property_type);

-- Amenity Embeddings Table (for RAG matching)
CREATE TABLE amenity_embeddings (
    id SERIAL PRIMARY KEY,
    amenity_id VARCHAR(50) REFERENCES catalogue_options(id) ON DELETE CASCADE,
    text TEXT NOT NULL,  -- amenity name + description
    embedding vector(1536),  -- OpenAI text-embedding-3-small
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_amenity_embeddings_amenity_id ON amenity_embeddings(amenity_id);
CREATE INDEX idx_amenity_embeddings_vector ON amenity_embeddings USING ivfflat (embedding vector_cosine_ops);

-- Location Advantage Embeddings Table
CREATE TABLE location_advantage_embeddings (
    id SERIAL PRIMARY KEY,
    location_advantage_id VARCHAR(50) REFERENCES catalogue_options(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_location_advantage_embeddings_location_id ON location_advantage_embeddings(location_advantage_id);
CREATE INDEX idx_location_advantage_embeddings_vector ON location_advantage_embeddings USING ivfflat (embedding vector_cosine_ops);

-- Extraction Audit Log (for debugging/improvement)
CREATE TABLE extraction_audit_logs (
    id SERIAL PRIMARY KEY,
    extraction_id INTEGER REFERENCES property_extractions(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,  -- 'started', 'type_detected', 'extraction_complete', 'validation_failed', 'clarification_sent'
    event_data JSONB,
    llm_model VARCHAR(100),
    tokens_used INTEGER,
    cost_usd DECIMAL(10, 6),
    latency_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_extraction_audit_logs_extraction_id ON extraction_audit_logs(extraction_id);
CREATE INDEX idx_extraction_audit_logs_event_type ON extraction_audit_logs(event_type);
CREATE INDEX idx_extraction_audit_logs_created_at ON extraction_audit_logs(created_at);
```

---

## Document Metadata

**Version:** 1.0
**Last Updated:** 2025-11-06
**Author:** Claude Code (Anthropic)
**Reviewed By:** Pending
**Status:** Ready for Implementation

**Related Documents:**
- `/Users/solo/Projects/_repos/bestays/.sdlc-workflow/.specs/04_PROPERTY_MODERNIZATION_PLAN.md`
- `/Users/solo/Projects/_repos/bestays/.sdlc-workflow/.specs/02_PROPERTIES_SCHEMA.md`

**Next Steps:**
1. Review architecture with development team
2. Create user story for MVP Phase 1 (Text Extraction)
3. Set up development environment with LangChain dependencies
4. Begin implementation following roadmap

---

**End of Document**

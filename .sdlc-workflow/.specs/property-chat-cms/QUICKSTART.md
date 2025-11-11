# Property Chat CMS - Developer Quick Start

**Get started with the LLM-powered property extraction system in 30 minutes.**

---

## Prerequisites

- Existing Bestays development environment running
- OpenRouter API key configured
- OpenAI API key (for Whisper transcription)
- Python 3.12+ with existing dependencies

---

## Phase 1: Text-Only Extraction (MVP Starting Point)

### Step 1: Install Additional Dependencies (if needed)

All required LangChain dependencies are already in `pyproject.toml`:

```bash
cd apps/server

# Verify dependencies
uv pip list | grep langchain
# Should show:
# langchain>=0.3.0
# langchain-community>=0.3.0
# langchain-openai>=0.2.0
# langchain-anthropic>=0.2.0
```

### Step 2: Create Directory Structure

```bash
cd apps/server/src/server/services

# Create property extraction module
mkdir -p property_extraction
touch property_extraction/__init__.py
touch property_extraction/agent.py
touch property_extraction/tools.py
touch property_extraction/prompts.py
touch property_extraction/parsers.py
touch property_extraction/validators.py

# Create service file
touch property_extraction_service.py

# Create schemas
cd ../../schemas
touch property_extraction.py
```

### Step 3: Define Pydantic Schemas

**File: `apps/server/src/server/schemas/property_extraction.py`**

```python
"""
Pydantic schemas for property extraction.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


class PropertyType(str, Enum):
    """Property type enum."""
    LAND = "pt_land"
    HOUSE = "pt_house"
    VILLA = "pt_villa"
    POOL_VILLA = "pt_pool_villa"
    APARTMENT = "pt_apartment"
    CONDO = "pt_condo"
    # Add others...


class PropertyInput(BaseModel):
    """Input for property extraction."""
    text: Optional[str] = None
    images: list[str] = Field(default_factory=list)  # URLs or base64
    voice_transcription: Optional[str] = None


class DetectedAmenity(BaseModel):
    """Detected amenity with confidence."""
    id: str = Field(description="Catalog ID")
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: str = Field(description="Why detected")


class RoomCounts(BaseModel):
    """Room counts."""
    bedrooms: Optional[int] = Field(None, ge=0, le=50)
    bathrooms: Optional[int] = Field(None, ge=0, le=50)
    # Add others...


class PropertyExtractionResult(BaseModel):
    """Result of property extraction."""
    property_type: PropertyType
    property_type_confidence: float = Field(ge=0.0, le=1.0)
    title: Optional[str] = None
    description: Optional[str] = None
    rooms: Optional[RoomCounts] = None
    amenities_interior: list[DetectedAmenity] = Field(default_factory=list)
    amenities_exterior: list[DetectedAmenity] = Field(default_factory=list)
    extraction_confidence: float = Field(ge=0.0, le=1.0)
    missing_required_fields: list[str] = Field(default_factory=list)
    clarification_questions: list[str] = Field(default_factory=list)
```

### Step 4: Create Property Type Detection Tool

**File: `apps/server/src/server/services/property_extraction/tools.py`**

```python
"""
LangChain tools for property extraction.
"""

from langchain.tools import StructuredTool
from langchain_core.pydantic_v1 import BaseModel, Field
import json


class PropertyTypeInput(BaseModel):
    """Input for property type detection."""
    description: str = Field(description="Property description text")


async def detect_property_type(llm, description: str) -> dict:
    """Detect property type from description."""

    prompt = f"""Analyze this property description and determine the type.

Types: rental, sale, lease, business, investment

Description: {description}

Return JSON:
{{
  "property_type": "rental|sale|lease|business|investment",
  "confidence": 0.0-1.0,
  "reasoning": "explanation"
}}
"""

    response = await llm.ainvoke(prompt)
    return json.loads(response.content)


def create_property_type_tool(llm) -> StructuredTool:
    """Create property type detection tool."""

    async def _detect(description: str) -> dict:
        return await detect_property_type(llm, description)

    return StructuredTool.from_function(
        func=_detect,
        name="detect_property_type",
        description="Detect property type from description",
        args_schema=PropertyTypeInput
    )
```

### Step 5: Create Simple Agent

**File: `apps/server/src/server/services/property_extraction/agent.py`**

```python
"""
Property extraction agent.
"""

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from server.llm_config.llm import get_llm_settings
from .tools import create_property_type_tool


class PropertyExtractionAgent:
    """LangChain agent for property extraction."""

    def __init__(self, openrouter_client):
        self.settings = get_llm_settings()

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.settings.models.parsing_model,
            base_url=self.settings.openrouter_base_url,
            api_key=self.settings.openrouter_api_key,
            temperature=0.3
        )

        # Create tools
        self.tools = [
            create_property_type_tool(self.llm)
        ]

        # Create agent
        self.agent_executor = self._create_agent()

    def _create_agent(self) -> AgentExecutor:
        """Create agent executor."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a property data extraction specialist."),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5
        )

    async def extract(self, input_text: str) -> dict:
        """Run extraction."""

        result = await self.agent_executor.ainvoke({
            "input": f"Extract property information from: {input_text}"
        })

        return result
```

### Step 6: Create Service Layer

**File: `apps/server/src/server/services/property_extraction_service.py`**

```python
"""
Property extraction service.
"""

from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from .property_extraction.agent import PropertyExtractionAgent
from server.schemas.property_extraction import PropertyInput, PropertyExtractionResult


class PropertyExtractionService:
    """Service for property extraction."""

    def __init__(self, db: AsyncSession, openrouter_client: httpx.AsyncClient):
        self.db = db
        self.client = openrouter_client

    async def extract_property(
        self,
        input_data: PropertyInput
    ) -> PropertyExtractionResult:
        """Extract property from input."""

        # Create agent
        agent = PropertyExtractionAgent(self.client)

        # Run extraction (text only for now)
        if not input_data.text:
            raise ValueError("Text description required")

        result = await agent.extract(input_data.text)

        # Parse result (simplified for now)
        # TODO: Properly parse LLM output into PropertyExtractionResult
        return PropertyExtractionResult(
            property_type="pt_villa",  # Placeholder
            property_type_confidence=0.9,
            title="Extracted Property",
            extraction_confidence=0.8
        )
```

### Step 7: Create API Endpoint

**File: `apps/server/src/server/api/v1/endpoints/properties/extraction.py`**

```python
"""
Property extraction endpoint.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from typing import Annotated

from server.api.deps import get_db, get_openrouter_client
from server.schemas.property_extraction import PropertyInput, PropertyExtractionResult
from server.services.property_extraction_service import PropertyExtractionService


router = APIRouter()


@router.post("/extract", response_model=PropertyExtractionResult)
async def extract_property(
    input_data: PropertyInput,
    db: Annotated[AsyncSession, Depends(get_db)],
    openrouter_client: Annotated[httpx.AsyncClient, Depends(get_openrouter_client)]
) -> PropertyExtractionResult:
    """
    Extract property data from multimodal input.

    **Supports:**
    - Text descriptions
    - Images (Phase 2)
    - Voice recordings (Phase 4)

    **Returns:**
    - Structured property data
    - Confidence scores
    - Missing fields
    - Clarification questions if needed
    """

    try:
        service = PropertyExtractionService(db, openrouter_client)
        result = await service.extract_property(input_data)
        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}"
        )
```

### Step 8: Register Endpoint

**File: `apps/server/src/server/api/v1/endpoints/properties/__init__.py`**

```python
from fastapi import APIRouter
from .extraction import router as extraction_router

router = APIRouter()
router.include_router(extraction_router, prefix="/properties", tags=["properties"])
```

### Step 9: Test the Endpoint

```bash
# Start the server
make dev

# Test extraction
curl -X POST http://localhost:8011/api/v1/properties/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Beautiful 3-bedroom villa for sale in Phuket. 250 sqm living space, private pool, sea view. 15M THB."
  }'
```

**Expected Response:**

```json
{
  "property_type": "pt_villa",
  "property_type_confidence": 0.9,
  "title": "3-Bedroom Villa with Sea View",
  "description": "Beautiful villa in Phuket...",
  "rooms": {
    "bedrooms": 3,
    "bathrooms": null
  },
  "amenities_interior": [],
  "amenities_exterior": [
    {
      "id": "am_ext_private_pool",
      "confidence": 0.95,
      "evidence": "Explicit mention: 'private pool'"
    }
  ],
  "extraction_confidence": 0.85,
  "missing_required_fields": ["bathrooms", "exact_location"],
  "clarification_questions": [
    "How many bathrooms does the villa have?",
    "Which area of Phuket is it located in?"
  ]
}
```

---

## Testing Checklist

### Unit Tests

**File: `apps/server/tests/services/test_property_extraction_service.py`**

```python
import pytest
from server.services.property_extraction_service import PropertyExtractionService
from server.schemas.property_extraction import PropertyInput


@pytest.mark.asyncio
async def test_text_extraction(db_session, openrouter_client):
    """Test text-only extraction."""

    service = PropertyExtractionService(db_session, openrouter_client)

    input_data = PropertyInput(
        text="3-bedroom villa for sale, 15M THB"
    )

    result = await service.extract_property(input_data)

    assert result.property_type in ["pt_villa", "pt_house"]
    assert result.property_type_confidence > 0.7
    assert result.rooms.bedrooms == 3


@pytest.mark.asyncio
async def test_missing_text_error(db_session, openrouter_client):
    """Test error when text is missing."""

    service = PropertyExtractionService(db_session, openrouter_client)

    input_data = PropertyInput()

    with pytest.raises(ValueError, match="Text description required"):
        await service.extract_property(input_data)
```

Run tests:

```bash
cd apps/server
pytest tests/services/test_property_extraction_service.py -v
```

---

## Next Steps

### Phase 2: Add Image Analysis

1. Implement `ImageAnalysisService` with GPT-4o
2. Add `AmenityDetectionTool` for image-based amenity detection
3. Create RAG embeddings for amenity catalog
4. Update API to accept image uploads

### Phase 3: Add Multi-Turn Conversation

1. Add conversation state management
2. Implement clarification question generator
3. Add refinement endpoint: `POST /extract/{id}/refine`
4. Integrate with existing `ConversationService`

### Phase 4: Add Voice Input

1. Integrate Whisper API for transcription
2. Add voice upload handling
3. Fuse voice + text + images

---

## Common Issues & Solutions

### Issue: "No module named 'langchain_openai'"

**Solution:**

```bash
cd apps/server
uv pip install langchain-openai>=0.2.0
```

### Issue: LLM returns invalid JSON

**Solution:** Use structured output parser:

```python
from langchain_core.output_parsers import PydanticOutputParser

parser = PydanticOutputParser(pydantic_object=PropertyExtractionResult)
prompt = prompt + "\n\n" + parser.get_format_instructions()
```

### Issue: Rate limit errors from OpenRouter

**Solution:** Add retry logic (already in `ChatService`):

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
async def call_llm(prompt):
    return await llm.ainvoke(prompt)
```

---

## Resources

- **LangChain Docs**: https://python.langchain.com/docs/
- **OpenRouter Models**: https://openrouter.ai/models
- **Pydantic Docs**: https://docs.pydantic.dev/
- **Architecture Doc**: `01_LLM_ARCHITECTURE_ANALYSIS.md`

---

## Getting Help

1. Check architecture doc for design decisions
2. Review existing `ChatService` for OpenRouter patterns
3. Look at `FAQTool` for RAG implementation example
4. Ask in #development Slack channel

---

**Ready to Start?**

```bash
# 1. Create directory structure
cd apps/server/src/server/services
mkdir property_extraction

# 2. Copy starter code from this guide

# 3. Run tests
pytest tests/services/test_property_extraction_service.py

# 4. Test endpoint
curl -X POST http://localhost:8011/api/v1/properties/extract -H "Content-Type: application/json" -d '{"text": "3-bed villa for sale"}'
```

Good luck! 🚀

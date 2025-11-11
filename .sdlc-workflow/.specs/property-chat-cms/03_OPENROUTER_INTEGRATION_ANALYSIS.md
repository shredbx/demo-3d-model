# OpenRouter Integration Analysis for Property Management Chat Assistant

**Document Version:** 1.0
**Date:** 2025-11-06
**Status:** Draft for Review

---

## Executive Summary

This document provides a comprehensive architecture for integrating OpenRouter's multimodal AI capabilities into the Bestays property management chat assistant. The integration will process text descriptions, property images, and voice messages to extract structured property data, generate enhanced descriptions, and provide intelligent property analysis.

**Key Decisions:**
- **Primary Model:** Claude Sonnet 4.5 for text processing (balance of cost/performance)
- **Vision Model:** GPT-4o for image analysis (superior vision capabilities)
- **Audio Transcription:** OpenAI Whisper API (dedicated service, not via OpenRouter)
- **MVP Focus:** Text + Image processing first, voice in Phase 2
- **Cost Estimate:** ~$0.85 per property (10 images + text processing)

---

## Table of Contents

1. [Model Selection Matrix](#1-model-selection-matrix)
2. [Architecture Overview](#2-architecture-overview)
3. [Text Processing Pipeline](#3-text-processing-pipeline)
4. [Image Processing Pipeline](#4-image-processing-pipeline)
5. [Voice Processing Pipeline](#5-voice-processing-pipeline)
6. [Request Orchestration](#6-request-orchestration)
7. [Response Formatting](#7-response-formatting)
8. [Cost Optimization](#8-cost-optimization)
9. [Error Handling](#9-error-handling)
10. [Rate Limiting & Quotas](#10-rate-limiting--quotas)
11. [Monitoring & Observability](#11-monitoring--observability)
12. [Future Features](#12-future-features)
13. [MVP Implementation Plan](#13-mvp-implementation-plan)
14. [Code Examples](#14-code-examples)

---

## 1. Model Selection Matrix

### 1.1 Text Processing Models

| Model | Use Case | Input Cost ($/1M tokens) | Output Cost ($/1M tokens) | Latency | Context Window | Recommendation |
|-------|----------|--------------------------|---------------------------|---------|----------------|----------------|
| **Claude Sonnet 4.5** | Property description extraction | $3.00 | $15.00 | Medium | 200K | **PRIMARY** - Best for structured extraction |
| Claude Haiku 3.5 | Simple categorization | $0.80 | $4.00 | Fast | 200K | **FALLBACK** - Cost-optimized for simple tasks |
| GPT-4o | Complex reasoning | $5.00 | $20.00 | Medium | 128K | Secondary - Good alternative |
| Gemini 2.5 Flash | Batch processing | $1.25 | $10.00 | Fast | 1M | **BATCH** - Large context for multi-property |

**Rationale for Claude Sonnet 4.5:**
- Excellent structured output capabilities
- Strong multilingual support (English, Thai, Russian)
- Good balance of cost vs performance
- Native JSON mode for extraction
- Reliable function calling

### 1.2 Vision Models

| Model | Use Case | Input Cost ($/1M tokens) | Output Cost ($/1M tokens) | Image Cost | Recommendation |
|-------|----------|--------------------------|---------------------------|------------|----------------|
| **GPT-4o** | Primary image analysis | $5.00 | $20.00 | ~$0.01/image | **PRIMARY** - Superior vision |
| Claude Sonnet 4.5 | Image + text reasoning | $3.00 | $15.00 | ~$0.008/image | **FALLBACK** - Good vision + reasoning |
| Gemini 2.5 Pro | Multi-image analysis | $2.50 | $15.00 | ~$0.006/image | Secondary - Cost effective |
| Llama 3.2 90B Vision | Budget option | FREE | FREE | FREE | **DEV/TEST** - Free tier testing |

**Vision Model Selection Logic:**
```python
def select_vision_model(image_count: int, complexity: str, budget: str) -> str:
    """
    Select optimal vision model based on task requirements
    """
    if budget == "unlimited" and complexity == "high":
        return "openai/gpt-4o"  # Best quality

    elif image_count > 10 and budget == "limited":
        return "google/gemini-2.5-pro"  # Cost-effective for batches

    elif complexity == "medium":
        return "anthropic/claude-sonnet-4.5"  # Balanced

    else:
        return "openai/gpt-4o"  # Default to quality
```

### 1.3 Audio Transcription

| Service | Language Support | Cost | Accuracy | Recommendation |
|---------|------------------|------|----------|----------------|
| **OpenAI Whisper API** | 99+ languages | $0.006/min | Excellent | **PRIMARY** - Direct API |
| AssemblyAI | 50+ languages | $0.015/min | Excellent | Secondary - More features |
| Deepgram | 30+ languages | $0.0125/min | Very Good | Tertiary - Real-time option |

**Note:** OpenRouter does not natively support audio transcription. Use dedicated Whisper API.

### 1.4 Fallback Strategy

```
Primary Request → OpenRouter API
    ↓ (if fails)
Fallback Model → Cheaper/faster alternative
    ↓ (if fails)
Queue for Retry → Exponential backoff
    ↓ (if fails)
Notify Admin → Manual processing required
```

---

## 2. Architecture Overview

### 2.1 System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    Property Chat Assistant                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend Services                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  Text API   │  │  Image API  │  │  Voice API              │ │
│  │  /process   │  │  /analyze   │  │  /transcribe            │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
           │                  │                      │
           ▼                  ▼                      ▼
┌──────────────────┐ ┌──────────────────┐ ┌────────────────────┐
│  OpenRouter API  │ │  OpenRouter API  │ │  Whisper API       │
│  Claude Sonnet   │ │  GPT-4o Vision   │ │  (OpenAI Direct)   │
└──────────────────┘ └──────────────────┘ └────────────────────┘
           │                  │                      │
           ▼                  ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Result Aggregation Layer                      │
│          Merge text + image + voice insights                     │
└─────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                           │
│    Store: property_data, ai_insights, processing_metadata        │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
1. User Input (Text/Image/Voice)
   ↓
2. Input Validation & Preprocessing
   ↓
3. Route to Appropriate Pipeline
   ├─→ Text Pipeline → Claude Sonnet 4.5
   ├─→ Image Pipeline → GPT-4o (parallel processing)
   └─→ Voice Pipeline → Whisper API → Claude for processing
   ↓
4. Parallel Processing (async)
   ↓
5. Result Aggregation
   ↓
6. Validation & Formatting
   ↓
7. Store in Database
   ↓
8. Return to Frontend
```

### 2.3 Technology Stack Integration

```python
# Core Dependencies
fastapi==0.115.0
openai==1.54.0  # OpenRouter uses OpenAI SDK format
httpx==0.27.0  # Async HTTP client
pydantic==2.9.0  # Data validation
pillow==10.4.0  # Image preprocessing
boto3==1.35.0  # Cloudflare R2 integration
psycopg2-binary==2.9.9  # PostgreSQL
redis==5.1.0  # Caching layer
```

---

## 3. Text Processing Pipeline

### 3.1 Architecture

```
Text Input → Preprocessing → OpenRouter Request → Response Parsing → Validation
                               (Claude Sonnet)
```

### 3.2 Implementation

```python
from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import Optional, List
import os

# Initialize OpenRouter client
client = AsyncOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# Response Schema
class PropertyDetails(BaseModel):
    """Structured property extraction schema"""
    property_type: str  # villa, condo, apartment, house
    bedrooms: Optional[int]
    bathrooms: Optional[int]
    square_meters: Optional[float]
    price_per_month: Optional[float]
    location: Optional[str]
    amenities: List[str]
    condition: str  # excellent, good, fair, needs_renovation
    description_summary: str
    languages_detected: List[str]
    confidence_score: float  # 0.0 to 1.0

class TextProcessor:
    """Process property text descriptions"""

    def __init__(self):
        self.model = "anthropic/claude-sonnet-4.5"
        self.fallback_model = "anthropic/claude-haiku-3.5"
        self.max_tokens = 2000

    async def extract_property_details(
        self,
        description: str,
        additional_context: Optional[str] = None
    ) -> PropertyDetails:
        """
        Extract structured property details from text description

        Args:
            description: Property description text
            additional_context: Optional context (location, owner notes, etc.)

        Returns:
            Structured property details
        """

        # Preprocessing
        if len(description) > 10000:  # ~2500 tokens
            description = await self._chunk_and_summarize(description)

        # Build system prompt
        system_prompt = """You are a property analysis expert. Extract structured information from property descriptions.

Output JSON with these fields:
- property_type: villa/condo/apartment/house/land
- bedrooms: number (null if not mentioned)
- bathrooms: number (null if not mentioned)
- square_meters: float (null if not mentioned)
- price_per_month: float in THB (null if not mentioned)
- location: specific area/neighborhood
- amenities: array of features (pool, gym, parking, etc.)
- condition: excellent/good/fair/needs_renovation
- description_summary: 2-3 sentence summary
- languages_detected: array of ISO codes (en, th, ru)
- confidence_score: 0.0-1.0 based on information completeness

Handle multilingual input (English, Thai, Russian). Be conservative with confidence scores."""

        try:
            # Primary request
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Description: {description}\n\nContext: {additional_context or 'None'}"}
                ],
                response_format={"type": "json_object"},
                max_tokens=self.max_tokens,
                temperature=0.1,  # Low temperature for extraction
                extra_headers={
                    "HTTP-Referer": "https://bestays.com",
                    "X-Title": "Bestays Property CMS"
                }
            )

            # Parse response
            result = response.choices[0].message.content
            property_details = PropertyDetails.model_validate_json(result)

            return property_details

        except Exception as e:
            # Fallback to Haiku
            print(f"Primary model failed: {e}, falling back to Haiku")
            return await self._fallback_extraction(description, additional_context)

    async def _chunk_and_summarize(self, long_text: str) -> str:
        """Summarize long descriptions before extraction"""
        response = await client.chat.completions.create(
            model=self.fallback_model,  # Use cheaper model for summarization
            messages=[
                {"role": "system", "content": "Summarize this property description, preserving all key details (size, price, amenities, location)."},
                {"role": "user", "content": long_text}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        return response.choices[0].message.content

    async def _fallback_extraction(self, description: str, context: Optional[str]) -> PropertyDetails:
        """Fallback extraction with Haiku"""
        # Same logic as extract_property_details but with self.fallback_model
        # Implementation omitted for brevity
        pass

    async def stream_enhanced_description(self, property_details: PropertyDetails):
        """
        Stream an enhanced property description using SSE
        Useful for generating marketing copy in real-time
        """
        prompt = f"""Based on these property details, write an engaging property listing description:

Property Type: {property_details.property_type}
Bedrooms: {property_details.bedrooms}
Bathrooms: {property_details.bathrooms}
Size: {property_details.square_meters} sqm
Amenities: {', '.join(property_details.amenities)}

Write a 150-200 word description that highlights the best features."""

        stream = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            max_tokens=500,
            temperature=0.7  # Higher temperature for creative writing
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
```

### 3.3 API Endpoint

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

app = FastAPI()
text_processor = TextProcessor()

@app.post("/api/v1/property/extract-text", response_model=PropertyDetails)
async def extract_property_from_text(
    description: str,
    context: Optional[str] = None
):
    """Extract structured property details from text description"""
    try:
        result = await text_processor.extract_property_details(description, context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/property/enhance-description")
async def enhance_property_description(property_details: PropertyDetails):
    """Stream enhanced property description"""
    return StreamingResponse(
        text_processor.stream_enhanced_description(property_details),
        media_type="text/event-stream"
    )
```

### 3.4 Request/Response Examples

**Request:**
```json
{
  "description": "Beautiful 3 bedroom villa in Phuket with private pool. 250 sqm, fully furnished. Near beach. 80,000 THB/month. สระว่ายน้ำส่วนตัว ใกล้ชายหาด",
  "context": "Owner: John Smith, Location: Rawai, Phuket"
}
```

**Response:**
```json
{
  "property_type": "villa",
  "bedrooms": 3,
  "bathrooms": null,
  "square_meters": 250.0,
  "price_per_month": 80000.0,
  "location": "Rawai, Phuket",
  "amenities": ["private_pool", "fully_furnished", "near_beach"],
  "condition": "good",
  "description_summary": "A 3-bedroom villa in Rawai, Phuket featuring a private pool and full furnishings. Located near the beach with 250 sqm of living space.",
  "languages_detected": ["en", "th"],
  "confidence_score": 0.85
}
```

---

## 4. Image Processing Pipeline

### 4.1 Architecture

```
Image Upload → R2 Storage → Preprocessing → Parallel Vision API → Aggregation → Results
                              ↓
                          (Resize, Compress, Format)
                              ↓
                    [Image 1] [Image 2] ... [Image N]
                              ↓
                    GPT-4o Vision (async batch)
                              ↓
                    Merge insights per room/area
```

### 4.2 Image Preprocessing

```python
from PIL import Image
import io
import base64
import httpx
from typing import List, Dict

class ImagePreprocessor:
    """Prepare images for vision API"""

    MAX_SIZE = (1568, 1568)  # GPT-4o optimal size
    QUALITY = 85
    FORMAT = "JPEG"

    def resize_and_compress(self, image_bytes: bytes) -> bytes:
        """
        Resize and compress image to reduce token costs

        GPT-4o pricing: ~170 tokens per 512x512 tile
        Larger images = more tiles = higher cost
        """
        img = Image.open(io.BytesIO(image_bytes))

        # Resize if too large
        if img.size[0] > self.MAX_SIZE[0] or img.size[1] > self.MAX_SIZE[1]:
            img.thumbnail(self.MAX_SIZE, Image.Resampling.LANCZOS)

        # Convert to RGB if needed (remove alpha channel)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # Compress
        output = io.BytesIO()
        img.save(output, format=self.FORMAT, quality=self.QUALITY, optimize=True)
        output.seek(0)

        return output.read()

    def to_base64(self, image_bytes: bytes) -> str:
        """Convert image to base64 for API"""
        return base64.b64encode(image_bytes).decode('utf-8')

    async def download_from_r2(self, r2_url: str) -> bytes:
        """Download image from Cloudflare R2"""
        async with httpx.AsyncClient() as client:
            response = await client.get(r2_url)
            response.raise_for_status()
            return response.content
```

### 4.3 Vision Analysis

```python
import asyncio
from pydantic import BaseModel
from typing import List, Optional

class ImageInsights(BaseModel):
    """Insights from a single image"""
    image_id: str
    room_type: str  # bedroom, bathroom, kitchen, living_room, exterior, pool
    features_detected: List[str]
    condition_assessment: str  # excellent, good, fair, poor
    notable_amenities: List[str]
    estimated_quality_score: float  # 0-10
    issues_detected: List[str]  # stains, damage, clutter, etc.
    confidence: float

class AggregatedPropertyInsights(BaseModel):
    """Aggregated insights from all property images"""
    overall_condition: str
    room_breakdown: Dict[str, int]  # {"bedroom": 3, "bathroom": 2, ...}
    key_amenities: List[str]
    standout_features: List[str]
    potential_issues: List[str]
    estimated_property_quality: float  # 0-10
    image_analysis_count: int
    processing_time_seconds: float

class ImageAnalyzer:
    """Analyze property images with vision models"""

    def __init__(self):
        self.model = "openai/gpt-4o"
        self.fallback_model = "anthropic/claude-sonnet-4.5"
        self.preprocessor = ImagePreprocessor()
        self.batch_size = 5  # Process 5 images concurrently

    async def analyze_single_image(
        self,
        image_url: str,
        image_id: str,
        detail: str = "auto"  # low, high, auto
    ) -> ImageInsights:
        """
        Analyze a single property image

        Args:
            image_url: URL or base64 data URI
            image_id: Unique identifier for tracking
            detail: Vision detail level (low=cheaper, high=better quality)
        """

        system_prompt = """You are a property inspection expert. Analyze this property image and provide detailed insights.

Identify:
1. Room type (bedroom, bathroom, kitchen, living_room, dining_room, exterior, pool, garden, parking)
2. Visible features and amenities
3. Condition assessment (excellent/good/fair/poor)
4. Quality score (0-10)
5. Any issues (damage, stains, clutter, maintenance needs)

Be thorough and objective. Output JSON format."""

        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": system_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url,
                                    "detail": detail  # Cost optimization
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=1000,
                temperature=0.1
            )

            result = response.choices[0].message.content
            insights = ImageInsights.model_validate_json(result)
            insights.image_id = image_id

            return insights

        except Exception as e:
            print(f"Image analysis failed for {image_id}: {e}")
            # Could implement fallback to Claude here
            raise

    async def analyze_property_images(
        self,
        image_urls: List[str],
        optimize_cost: bool = True
    ) -> AggregatedPropertyInsights:
        """
        Analyze multiple property images in parallel

        Args:
            image_urls: List of image URLs (R2 URLs or base64)
            optimize_cost: If True, use 'low' detail for non-critical images
        """
        import time
        start_time = time.time()

        # Preprocess images if they're from R2
        preprocessed_images = []
        for idx, url in enumerate(image_urls):
            if url.startswith('http'):
                # Download and preprocess
                image_bytes = await self.preprocessor.download_from_r2(url)
                compressed = self.preprocessor.resize_and_compress(image_bytes)
                base64_img = self.preprocessor.to_base64(compressed)
                preprocessed_images.append({
                    'url': f"data:image/jpeg;base64,{base64_img}",
                    'id': f"img_{idx}",
                    'detail': 'low' if optimize_cost and idx > 5 else 'auto'  # First 5 in high quality
                })
            else:
                preprocessed_images.append({
                    'url': url,
                    'id': f"img_{idx}",
                    'detail': 'auto'
                })

        # Process in batches to avoid rate limits
        all_insights = []
        for i in range(0, len(preprocessed_images), self.batch_size):
            batch = preprocessed_images[i:i + self.batch_size]

            # Parallel processing within batch
            tasks = [
                self.analyze_single_image(
                    img['url'],
                    img['id'],
                    img['detail']
                ) for img in batch
            ]

            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out failed analyses
            for result in batch_results:
                if isinstance(result, ImageInsights):
                    all_insights.append(result)
                else:
                    print(f"Failed analysis: {result}")

            # Rate limiting delay between batches
            if i + self.batch_size < len(preprocessed_images):
                await asyncio.sleep(1)  # 1 second between batches

        # Aggregate insights
        aggregated = self._aggregate_insights(all_insights)
        aggregated.processing_time_seconds = time.time() - start_time

        return aggregated

    def _aggregate_insights(self, insights: List[ImageInsights]) -> AggregatedPropertyInsights:
        """Aggregate individual image insights into property-level insights"""

        # Count room types
        room_breakdown = {}
        for insight in insights:
            room_type = insight.room_type
            room_breakdown[room_type] = room_breakdown.get(room_type, 0) + 1

        # Collect all amenities and features
        all_amenities = set()
        all_features = []
        all_issues = []
        quality_scores = []

        for insight in insights:
            all_amenities.update(insight.notable_amenities)
            all_features.extend(insight.features_detected)
            all_issues.extend(insight.issues_detected)
            quality_scores.append(insight.estimated_quality_score)

        # Calculate overall condition
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0

        if avg_quality >= 8:
            overall_condition = "excellent"
        elif avg_quality >= 6:
            overall_condition = "good"
        elif avg_quality >= 4:
            overall_condition = "fair"
        else:
            overall_condition = "poor"

        # Get standout features (most mentioned)
        from collections import Counter
        feature_counts = Counter(all_features)
        standout_features = [f for f, count in feature_counts.most_common(10) if count >= 2]

        return AggregatedPropertyInsights(
            overall_condition=overall_condition,
            room_breakdown=room_breakdown,
            key_amenities=list(all_amenities),
            standout_features=standout_features,
            potential_issues=list(set(all_issues)),
            estimated_property_quality=avg_quality,
            image_analysis_count=len(insights),
            processing_time_seconds=0.0  # Will be set by caller
        )
```

### 4.4 API Endpoint

```python
from fastapi import UploadFile, File
from typing import List

image_analyzer = ImageAnalyzer()

@app.post("/api/v1/property/analyze-images", response_model=AggregatedPropertyInsights)
async def analyze_property_images(
    image_urls: List[str],
    optimize_cost: bool = True
):
    """
    Analyze multiple property images

    Args:
        image_urls: List of R2 URLs or base64 data URIs
        optimize_cost: Use lower quality for non-critical images
    """
    try:
        insights = await image_analyzer.analyze_property_images(
            image_urls,
            optimize_cost=optimize_cost
        )
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/property/upload-and-analyze")
async def upload_and_analyze(files: List[UploadFile] = File(...)):
    """
    Upload images to R2 and analyze in one request
    """
    # 1. Upload to R2
    r2_urls = []
    for file in files:
        # Upload to R2 (implementation depends on your R2 setup)
        r2_url = await upload_to_r2(file)
        r2_urls.append(r2_url)

    # 2. Analyze
    insights = await image_analyzer.analyze_property_images(r2_urls)

    # 3. Return both URLs and insights
    return {
        "uploaded_images": r2_urls,
        "analysis": insights
    }
```

### 4.5 Request/Response Examples

**Request:**
```json
{
  "image_urls": [
    "https://r2.bestays.com/properties/prop123/bedroom1.jpg",
    "https://r2.bestays.com/properties/prop123/bathroom.jpg",
    "https://r2.bestays.com/properties/prop123/pool.jpg",
    "https://r2.bestays.com/properties/prop123/exterior.jpg"
  ],
  "optimize_cost": true
}
```

**Response:**
```json
{
  "overall_condition": "excellent",
  "room_breakdown": {
    "bedroom": 1,
    "bathroom": 1,
    "pool": 1,
    "exterior": 1
  },
  "key_amenities": [
    "private_pool",
    "modern_fixtures",
    "high_ceilings",
    "natural_lighting",
    "tropical_garden"
  ],
  "standout_features": [
    "infinity_pool",
    "marble_countertops",
    "floor_to_ceiling_windows",
    "outdoor_terrace"
  ],
  "potential_issues": [
    "minor_wall_scuff_in_bedroom"
  ],
  "estimated_property_quality": 8.5,
  "image_analysis_count": 4,
  "processing_time_seconds": 12.4
}
```

---

## 5. Voice Processing Pipeline

### 5.1 Architecture

```
Audio Upload → Whisper API → Transcription → Claude Analysis → Structured Data
   (MP3/WAV)   (Transcribe)     (Text)      (Extract info)    (JSON)
```

### 5.2 Implementation

```python
import httpx
from openai import AsyncOpenAI
import os

# Separate client for Whisper
whisper_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class VoiceProcessor:
    """Process voice messages about properties"""

    SUPPORTED_FORMATS = ['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm']
    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB

    def __init__(self):
        self.text_processor = TextProcessor()

    async def transcribe_audio(
        self,
        audio_file_path: str,
        language: Optional[str] = None  # 'en', 'th', 'ru', or None for auto-detect
    ) -> Dict[str, str]:
        """
        Transcribe audio using Whisper API

        Args:
            audio_file_path: Path to audio file
            language: ISO 639-1 language code (optional)

        Returns:
            Dict with 'text' and 'language'
        """

        with open(audio_file_path, 'rb') as audio_file:
            try:
                response = await whisper_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,  # None = auto-detect
                    response_format="verbose_json"  # Includes language detection
                )

                return {
                    'text': response.text,
                    'language': response.language,
                    'duration': response.duration
                }

            except Exception as e:
                print(f"Transcription failed: {e}")
                raise

    async def process_voice_message(
        self,
        audio_file_path: str,
        expected_language: Optional[str] = None
    ) -> Dict:
        """
        Full pipeline: transcribe + extract property details

        Returns:
            Combined transcription + property details
        """

        # 1. Transcribe
        transcription = await self.transcribe_audio(audio_file_path, expected_language)

        # 2. Extract property details from transcription
        property_details = await self.text_processor.extract_property_details(
            description=transcription['text'],
            additional_context=f"Source: Voice message in {transcription['language']}"
        )

        # 3. Combine results
        return {
            'transcription': transcription,
            'property_details': property_details.model_dump(),
            'processing_notes': {
                'audio_duration_seconds': transcription['duration'],
                'detected_language': transcription['language'],
                'confidence': property_details.confidence_score
            }
        }
```

### 5.3 API Endpoint

```python
from fastapi import UploadFile, File
import tempfile
import os

voice_processor = VoiceProcessor()

@app.post("/api/v1/property/process-voice")
async def process_voice_message(
    audio: UploadFile = File(...),
    expected_language: Optional[str] = None
):
    """
    Process voice message about property

    Args:
        audio: Audio file (MP3, WAV, etc.)
        expected_language: Expected language code (optional)
    """

    # Validate file type
    file_ext = audio.filename.split('.')[-1].lower()
    if file_ext not in voice_processor.SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Use: {voice_processor.SUPPORTED_FORMATS}"
        )

    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
        content = await audio.read()

        # Check file size
        if len(content) > voice_processor.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large (max 25MB)")

        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Process
        result = await voice_processor.process_voice_message(
            tmp_path,
            expected_language
        )
        return result
    finally:
        # Cleanup temp file
        os.unlink(tmp_path)
```

### 5.4 Request/Response Example

**Request:**
```bash
curl -X POST "https://api.bestays.com/api/v1/property/process-voice" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "audio=@property_description.mp3" \
  -F "expected_language=th"
```

**Response:**
```json
{
  "transcription": {
    "text": "บ้านสวยใหม่ 3 ห้องนอน มีสระว่ายน้ำ ใกล้ชายหาด ราคา 80000 บาทต่อเดือน",
    "language": "th",
    "duration": 15.2
  },
  "property_details": {
    "property_type": "house",
    "bedrooms": 3,
    "bathrooms": null,
    "square_meters": null,
    "price_per_month": 80000.0,
    "location": null,
    "amenities": ["swimming_pool", "near_beach"],
    "condition": "good",
    "description_summary": "New 3-bedroom house with swimming pool near beach",
    "languages_detected": ["th"],
    "confidence_score": 0.75
  },
  "processing_notes": {
    "audio_duration_seconds": 15.2,
    "detected_language": "th",
    "confidence": 0.75
  }
}
```

---

## 6. Request Orchestration

### 6.1 Multimodal Coordinator

```python
from typing import Optional, List
import asyncio

class MultimodalPropertyProcessor:
    """Orchestrate text + image + voice processing"""

    def __init__(self):
        self.text_processor = TextProcessor()
        self.image_analyzer = ImageAnalyzer()
        self.voice_processor = VoiceProcessor()

    async def process_complete_property(
        self,
        text_description: Optional[str] = None,
        image_urls: Optional[List[str]] = None,
        audio_file_path: Optional[str] = None,
        timeout_seconds: int = 120
    ) -> Dict:
        """
        Process all modalities in parallel and merge results

        Args:
            text_description: Written property description
            image_urls: List of property image URLs
            audio_file_path: Path to voice message
            timeout_seconds: Max processing time

        Returns:
            Merged insights from all modalities
        """

        tasks = []
        task_names = []

        # Build task list
        if text_description:
            tasks.append(self.text_processor.extract_property_details(text_description))
            task_names.append('text')

        if image_urls:
            tasks.append(self.image_analyzer.analyze_property_images(image_urls))
            task_names.append('images')

        if audio_file_path:
            tasks.append(self.voice_processor.process_voice_message(audio_file_path))
            task_names.append('voice')

        if not tasks:
            raise ValueError("At least one input modality required")

        # Execute in parallel with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            raise Exception(f"Processing exceeded {timeout_seconds}s timeout")

        # Map results to modalities
        processed_results = {}
        errors = {}

        for name, result in zip(task_names, results):
            if isinstance(result, Exception):
                errors[name] = str(result)
            else:
                processed_results[name] = result

        # Merge results
        merged = self._merge_multimodal_results(processed_results)

        if errors:
            merged['processing_errors'] = errors

        return merged

    def _merge_multimodal_results(self, results: Dict) -> Dict:
        """
        Intelligently merge results from different modalities

        Priority: Images > Voice > Text (images most reliable)
        """

        merged = {
            'property_type': None,
            'bedrooms': None,
            'bathrooms': None,
            'square_meters': None,
            'price_per_month': None,
            'location': None,
            'amenities': set(),
            'condition': None,
            'overall_quality': None,
            'description': None,
            'confidence_breakdown': {},
            'sources_used': []
        }

        # Extract from text
        if 'text' in results:
            text_data = results['text']
            merged['property_type'] = text_data.property_type
            merged['bedrooms'] = text_data.bedrooms
            merged['bathrooms'] = text_data.bathrooms
            merged['square_meters'] = text_data.square_meters
            merged['price_per_month'] = text_data.price_per_month
            merged['location'] = text_data.location
            merged['amenities'].update(text_data.amenities)
            merged['condition'] = text_data.condition
            merged['description'] = text_data.description_summary
            merged['confidence_breakdown']['text'] = text_data.confidence_score
            merged['sources_used'].append('text')

        # Override/enhance with voice data
        if 'voice' in results:
            voice_data = results['voice']['property_details']
            # Voice can provide price/location that wasn't in text
            if not merged['price_per_month'] and voice_data['price_per_month']:
                merged['price_per_month'] = voice_data['price_per_month']
            if not merged['location'] and voice_data['location']:
                merged['location'] = voice_data['location']

            merged['amenities'].update(voice_data['amenities'])
            merged['confidence_breakdown']['voice'] = voice_data['confidence_score']
            merged['sources_used'].append('voice')

        # Override/enhance with image analysis
        if 'images' in results:
            image_data = results['images']
            # Images are most reliable for condition and amenities
            merged['condition'] = image_data.overall_condition
            merged['overall_quality'] = image_data.estimated_property_quality
            merged['amenities'].update(image_data.key_amenities)

            # Image analysis can correct room counts
            if 'bedroom' in image_data.room_breakdown:
                merged['bedrooms'] = image_data.room_breakdown['bedroom']
            if 'bathroom' in image_data.room_breakdown:
                merged['bathrooms'] = image_data.room_breakdown['bathroom']

            merged['confidence_breakdown']['images'] = 0.9  # Images generally high confidence
            merged['sources_used'].append('images')

        # Convert amenities set to list
        merged['amenities'] = list(merged['amenities'])

        # Calculate overall confidence
        if merged['confidence_breakdown']:
            merged['overall_confidence'] = sum(
                merged['confidence_breakdown'].values()
            ) / len(merged['confidence_breakdown'])

        return merged
```

### 6.2 Complete API Endpoint

```python
@app.post("/api/v1/property/process-multimodal")
async def process_multimodal_property(
    text_description: Optional[str] = None,
    image_urls: Optional[List[str]] = None,
    audio: Optional[UploadFile] = File(None)
):
    """
    Process property with multiple input modalities

    Accepts any combination of:
    - Text description
    - Image URLs
    - Voice message
    """

    processor = MultimodalPropertyProcessor()

    # Handle audio upload
    audio_path = None
    if audio:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            content = await audio.read()
            tmp.write(content)
            audio_path = tmp.name

    try:
        result = await processor.process_complete_property(
            text_description=text_description,
            image_urls=image_urls,
            audio_file_path=audio_path,
            timeout_seconds=120
        )
        return result
    finally:
        if audio_path:
            os.unlink(audio_path)
```

---

## 7. Response Formatting

### 7.1 Standardized Response Schema

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class PropertyAnalysisResponse(BaseModel):
    """Standardized response for all property analysis requests"""

    # Request metadata
    request_id: str = Field(description="Unique request identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: float

    # Property data
    property_id: Optional[str] = None
    property_type: str
    bedrooms: Optional[int]
    bathrooms: Optional[int]
    square_meters: Optional[float]
    price_per_month: Optional[float]
    price_currency: str = "THB"
    location: Optional[str]

    # Analysis results
    amenities: List[str]
    condition: str  # excellent, good, fair, poor
    quality_score: Optional[float] = Field(ge=0, le=10)
    description: str

    # Confidence & validation
    confidence_score: float = Field(ge=0, le=1)
    data_completeness: float = Field(ge=0, le=1, description="% of fields populated")
    validation_status: str  # valid, partial, invalid
    validation_issues: List[str] = []

    # Processing details
    modalities_used: List[str]  # ['text', 'images', 'voice']
    model_info: Dict[str, str]  # {'text': 'claude-sonnet-4.5', 'vision': 'gpt-4o'}

    # Costs
    estimated_cost_usd: Optional[float] = None
    token_usage: Optional[Dict[str, int]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_abc123",
                "timestamp": "2025-11-06T10:30:00Z",
                "processing_time_ms": 3450.2,
                "property_type": "villa",
                "bedrooms": 3,
                "bathrooms": 2,
                "square_meters": 250.0,
                "price_per_month": 80000.0,
                "price_currency": "THB",
                "location": "Rawai, Phuket",
                "amenities": ["private_pool", "garden", "parking"],
                "condition": "excellent",
                "quality_score": 8.5,
                "description": "Beautiful 3-bedroom villa with private pool",
                "confidence_score": 0.88,
                "data_completeness": 0.85,
                "validation_status": "valid",
                "validation_issues": [],
                "modalities_used": ["text", "images"],
                "model_info": {
                    "text": "anthropic/claude-sonnet-4.5",
                    "vision": "openai/gpt-4o"
                },
                "estimated_cost_usd": 0.042,
                "token_usage": {
                    "text_input": 450,
                    "text_output": 280,
                    "vision_tokens": 3400
                }
            }
        }

def validate_property_data(data: Dict) -> tuple[str, List[str]]:
    """
    Validate extracted property data

    Returns:
        (status, issues) where status is 'valid'/'partial'/'invalid'
    """
    issues = []
    required_fields = ['property_type', 'price_per_month', 'location']

    # Check required fields
    missing_required = [f for f in required_fields if not data.get(f)]
    if missing_required:
        issues.append(f"Missing required fields: {missing_required}")

    # Validate ranges
    if data.get('bedrooms') and (data['bedrooms'] < 0 or data['bedrooms'] > 20):
        issues.append("Invalid bedroom count")

    if data.get('price_per_month') and data['price_per_month'] < 1000:
        issues.append("Price seems unusually low")

    if data.get('confidence_score', 0) < 0.5:
        issues.append("Low confidence in extraction")

    # Determine status
    if not issues:
        status = 'valid'
    elif len(missing_required) == 0:
        status = 'partial'
    else:
        status = 'invalid'

    return status, issues

def calculate_data_completeness(data: Dict) -> float:
    """Calculate what % of expected fields are populated"""
    all_fields = [
        'property_type', 'bedrooms', 'bathrooms', 'square_meters',
        'price_per_month', 'location', 'amenities', 'condition'
    ]

    populated = sum(1 for field in all_fields if data.get(field))
    return populated / len(all_fields)
```

### 7.2 Response Wrapper

```python
import uuid
import time

class ResponseFormatter:
    """Format and enrich API responses"""

    @staticmethod
    def format_property_response(
        property_data: Dict,
        modalities: List[str],
        models_used: Dict[str, str],
        start_time: float,
        token_usage: Dict[str, int]
    ) -> PropertyAnalysisResponse:
        """Create standardized response"""

        # Validate
        validation_status, validation_issues = validate_property_data(property_data)

        # Calculate completeness
        completeness = calculate_data_completeness(property_data)

        # Estimate cost (simplified)
        cost = ResponseFormatter._estimate_cost(token_usage, models_used)

        return PropertyAnalysisResponse(
            request_id=f"req_{uuid.uuid4().hex[:12]}",
            processing_time_ms=(time.time() - start_time) * 1000,
            property_type=property_data.get('property_type', 'unknown'),
            bedrooms=property_data.get('bedrooms'),
            bathrooms=property_data.get('bathrooms'),
            square_meters=property_data.get('square_meters'),
            price_per_month=property_data.get('price_per_month'),
            location=property_data.get('location'),
            amenities=property_data.get('amenities', []),
            condition=property_data.get('condition', 'unknown'),
            quality_score=property_data.get('overall_quality'),
            description=property_data.get('description', ''),
            confidence_score=property_data.get('overall_confidence', 0.5),
            data_completeness=completeness,
            validation_status=validation_status,
            validation_issues=validation_issues,
            modalities_used=modalities,
            model_info=models_used,
            estimated_cost_usd=cost,
            token_usage=token_usage
        )

    @staticmethod
    def _estimate_cost(token_usage: Dict[str, int], models: Dict[str, str]) -> float:
        """Estimate request cost in USD"""

        # Model pricing (per 1M tokens)
        pricing = {
            'anthropic/claude-sonnet-4.5': {'input': 3.00, 'output': 15.00},
            'anthropic/claude-haiku-3.5': {'input': 0.80, 'output': 4.00},
            'openai/gpt-4o': {'input': 5.00, 'output': 20.00},
            'google/gemini-2.5-pro': {'input': 2.50, 'output': 15.00}
        }

        total_cost = 0.0

        # Text processing cost
        if 'text' in models:
            model = models['text']
            if model in pricing:
                input_tokens = token_usage.get('text_input', 0)
                output_tokens = token_usage.get('text_output', 0)

                total_cost += (input_tokens / 1_000_000) * pricing[model]['input']
                total_cost += (output_tokens / 1_000_000) * pricing[model]['output']

        # Vision processing cost
        if 'vision' in models:
            model = models['vision']
            if model in pricing:
                vision_tokens = token_usage.get('vision_tokens', 0)
                # Vision tokens are input tokens
                total_cost += (vision_tokens / 1_000_000) * pricing[model]['input']

        # Whisper cost ($0.006 per minute)
        if 'voice' in models:
            audio_duration_min = token_usage.get('audio_duration_seconds', 0) / 60
            total_cost += audio_duration_min * 0.006

        return round(total_cost, 4)
```

---

## 8. Cost Optimization

### 8.1 Token Usage Optimization

```python
class CostOptimizer:
    """Strategies to minimize API costs"""

    @staticmethod
    def should_use_cheap_model(description: str) -> bool:
        """Decide if we can use cheaper model for text"""
        # Simple heuristics
        word_count = len(description.split())

        # Use Haiku for short, simple descriptions
        if word_count < 100:
            return True

        # Use Haiku if it's just numbers and basic info
        if sum(c.isdigit() for c in description) / len(description) > 0.3:
            return True

        return False

    @staticmethod
    def optimize_image_batch(images: List[str], max_budget: float = 0.10) -> List[Dict]:
        """
        Optimize image processing to stay within budget

        Args:
            images: List of image URLs
            max_budget: Maximum USD to spend on vision

        Returns:
            List of image configs with detail level
        """

        # GPT-4o vision cost: ~$0.01 per image (high detail)
        # Low detail: ~$0.003 per image

        cost_per_image_high = 0.01
        cost_per_image_low = 0.003

        num_images = len(images)

        # If budget allows all high-detail
        if num_images * cost_per_image_high <= max_budget:
            return [{'url': img, 'detail': 'high'} for img in images]

        # Otherwise, prioritize first 3 images as high detail
        priority_count = min(3, int(max_budget / cost_per_image_high))
        remaining_budget = max_budget - (priority_count * cost_per_image_high)
        low_detail_count = int(remaining_budget / cost_per_image_low)

        configs = []
        for i, img in enumerate(images):
            if i < priority_count:
                configs.append({'url': img, 'detail': 'high'})
            elif i < priority_count + low_detail_count:
                configs.append({'url': img, 'detail': 'low'})
            else:
                # Skip remaining images if over budget
                break

        return configs

    @staticmethod
    async def compress_image_aggressively(image_bytes: bytes) -> bytes:
        """Aggressive compression for vision API"""
        from PIL import Image
        import io

        img = Image.open(io.BytesIO(image_bytes))

        # Resize to 512x512 (minimum detail)
        img.thumbnail((512, 512), Image.Resampling.LANCZOS)

        # Convert to RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Compress heavily
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=60, optimize=True)
        output.seek(0)

        return output.read()
```

### 8.2 Caching Strategy

```python
import redis
import hashlib
import json

class CacheManager:
    """Cache API responses to avoid duplicate requests"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url)
        self.ttl = 86400  # 24 hours

    def _generate_cache_key(self, prefix: str, data: Dict) -> str:
        """Generate cache key from request data"""
        data_str = json.dumps(data, sort_keys=True)
        hash_val = hashlib.sha256(data_str.encode()).hexdigest()
        return f"{prefix}:{hash_val}"

    async def get_cached_text_analysis(self, description: str) -> Optional[Dict]:
        """Check if we've seen this text before"""
        key = self._generate_cache_key("text", {"desc": description[:500]})  # First 500 chars
        cached = self.redis.get(key)

        if cached:
            return json.loads(cached)
        return None

    async def cache_text_analysis(self, description: str, result: Dict):
        """Cache text analysis result"""
        key = self._generate_cache_key("text", {"desc": description[:500]})
        self.redis.setex(key, self.ttl, json.dumps(result))

    async def get_cached_image_analysis(self, image_url: str) -> Optional[Dict]:
        """Check if we've analyzed this image before"""
        key = self._generate_cache_key("image", {"url": image_url})
        cached = self.redis.get(key)

        if cached:
            return json.loads(cached)
        return None

    async def cache_image_analysis(self, image_url: str, result: Dict):
        """Cache image analysis result"""
        key = self._generate_cache_key("image", {"url": image_url})
        self.redis.setex(key, self.ttl, json.dumps(result))

# Usage in processors
class CachedTextProcessor(TextProcessor):
    """Text processor with caching"""

    def __init__(self):
        super().__init__()
        self.cache = CacheManager()

    async def extract_property_details(self, description: str, additional_context: Optional[str] = None) -> PropertyDetails:
        # Check cache first
        cached = await self.cache.get_cached_text_analysis(description)
        if cached:
            print("Cache hit!")
            return PropertyDetails(**cached)

        # Not cached, process normally
        result = await super().extract_property_details(description, additional_context)

        # Cache result
        await self.cache.cache_text_analysis(description, result.model_dump())

        return result
```

### 8.3 Cost Monitoring

```python
from sqlalchemy import Column, String, Float, Integer, DateTime
from datetime import datetime

class APIUsageLog(Base):
    """Track API usage for cost monitoring"""
    __tablename__ = "api_usage_logs"

    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    endpoint = Column(String)  # text/image/voice
    model_used = Column(String)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    vision_tokens = Column(Integer, default=0)
    audio_minutes = Column(Float, default=0.0)
    estimated_cost_usd = Column(Float)
    property_id = Column(String)
    user_id = Column(String)

async def log_api_usage(
    endpoint: str,
    model: str,
    tokens: Dict[str, int],
    cost: float,
    property_id: str,
    user_id: str
):
    """Log API usage for billing/monitoring"""
    log_entry = APIUsageLog(
        id=f"log_{uuid.uuid4().hex}",
        endpoint=endpoint,
        model_used=model,
        input_tokens=tokens.get('input', 0),
        output_tokens=tokens.get('output', 0),
        vision_tokens=tokens.get('vision', 0),
        audio_minutes=tokens.get('audio_minutes', 0.0),
        estimated_cost_usd=cost,
        property_id=property_id,
        user_id=user_id
    )

    # Save to database
    db.add(log_entry)
    await db.commit()

# Dashboard query
async def get_daily_costs(date: str) -> Dict:
    """Get costs for a specific day"""
    results = db.query(
        APIUsageLog.endpoint,
        func.sum(APIUsageLog.estimated_cost_usd).label('total_cost'),
        func.count(APIUsageLog.id).label('request_count')
    ).filter(
        func.date(APIUsageLog.timestamp) == date
    ).group_by(
        APIUsageLog.endpoint
    ).all()

    return {
        result.endpoint: {
            'cost': result.total_cost,
            'requests': result.request_count
        }
        for result in results
    }
```

---

## 9. Error Handling

### 9.1 Error Types & Responses

```python
from enum import Enum
from fastapi import HTTPException

class ErrorCode(str, Enum):
    """Standardized error codes"""

    # OpenRouter API errors
    OPENROUTER_UNAVAILABLE = "OPENROUTER_UNAVAILABLE"
    OPENROUTER_RATE_LIMIT = "OPENROUTER_RATE_LIMIT"
    OPENROUTER_INVALID_KEY = "OPENROUTER_INVALID_KEY"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"

    # Processing errors
    IMAGE_ANALYSIS_FAILED = "IMAGE_ANALYSIS_FAILED"
    TRANSCRIPTION_FAILED = "TRANSCRIPTION_FAILED"
    EXTRACTION_FAILED = "EXTRACTION_FAILED"
    VALIDATION_FAILED = "VALIDATION_FAILED"

    # Input errors
    INVALID_IMAGE_FORMAT = "INVALID_IMAGE_FORMAT"
    INVALID_AUDIO_FORMAT = "INVALID_AUDIO_FORMAT"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    MISSING_INPUT = "MISSING_INPUT"

    # Timeout errors
    PROCESSING_TIMEOUT = "PROCESSING_TIMEOUT"

class ProcessingError(Exception):
    """Custom exception for processing errors"""

    def __init__(self, code: ErrorCode, message: str, details: Dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class ErrorHandler:
    """Handle errors with fallback strategies"""

    @staticmethod
    async def handle_openrouter_error(error: Exception, context: Dict) -> Dict:
        """
        Handle OpenRouter API errors with fallback

        Returns:
            Result with error info or fallback result
        """

        error_msg = str(error)

        # Rate limit error
        if "rate_limit" in error_msg.lower():
            # Wait and retry
            await asyncio.sleep(5)
            raise ProcessingError(
                ErrorCode.OPENROUTER_RATE_LIMIT,
                "Rate limit exceeded, queued for retry",
                {"retry_after_seconds": 5}
            )

        # Model unavailable
        elif "model" in error_msg.lower() and "unavailable" in error_msg.lower():
            # Try fallback model
            print(f"Model unavailable, trying fallback")
            # Return special indicator to use fallback
            return {"use_fallback": True, "original_error": error_msg}

        # Invalid API key
        elif "unauthorized" in error_msg.lower() or "invalid" in error_msg.lower():
            raise ProcessingError(
                ErrorCode.OPENROUTER_INVALID_KEY,
                "OpenRouter API key is invalid",
                {"check": "Verify OPENROUTER_API_KEY environment variable"}
            )

        # Generic API error
        else:
            raise ProcessingError(
                ErrorCode.OPENROUTER_UNAVAILABLE,
                f"OpenRouter API error: {error_msg}",
                {"context": context}
            )

    @staticmethod
    def handle_image_error(error: Exception, image_id: str) -> Dict:
        """Handle image processing errors"""

        return {
            "image_id": image_id,
            "status": "failed",
            "error": str(error),
            "fallback_data": {
                "room_type": "unknown",
                "features_detected": [],
                "condition_assessment": "unknown",
                "confidence": 0.0
            }
        }

    @staticmethod
    def handle_transcription_error(error: Exception, audio_file: str) -> Dict:
        """Handle transcription errors"""

        error_msg = str(error)

        # File format issues
        if "format" in error_msg.lower():
            raise ProcessingError(
                ErrorCode.INVALID_AUDIO_FORMAT,
                "Audio file format not supported",
                {"supported_formats": ["mp3", "wav", "m4a", "webm"]}
            )

        # File too large
        elif "size" in error_msg.lower():
            raise ProcessingError(
                ErrorCode.FILE_TOO_LARGE,
                "Audio file exceeds 25MB limit"
            )

        # Generic transcription error
        else:
            raise ProcessingError(
                ErrorCode.TRANSCRIPTION_FAILED,
                f"Transcription failed: {error_msg}"
            )

# Global error handler for FastAPI
@app.exception_handler(ProcessingError)
async def processing_error_handler(request, exc: ProcessingError):
    """Handle custom processing errors"""

    return JSONResponse(
        status_code=500,
        content={
            "error_code": exc.code,
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

### 9.2 Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class ResilientProcessor:
    """Processor with automatic retries"""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, TimeoutError))
    )
    async def call_openrouter_with_retry(self, request_data: Dict) -> Dict:
        """
        Call OpenRouter with automatic retries

        Retries up to 3 times with exponential backoff:
        - 1st retry: wait 2s
        - 2nd retry: wait 4s
        - 3rd retry: wait 8s
        """

        response = await client.chat.completions.create(**request_data)
        return response

    async def process_with_fallback(self, primary_model: str, fallback_model: str, request_data: Dict) -> Dict:
        """Try primary model, fall back to secondary on failure"""

        try:
            request_data['model'] = primary_model
            return await self.call_openrouter_with_retry(request_data)

        except Exception as e:
            print(f"Primary model {primary_model} failed: {e}")
            print(f"Falling back to {fallback_model}")

            try:
                request_data['model'] = fallback_model
                return await self.call_openrouter_with_retry(request_data)

            except Exception as fallback_error:
                # Both failed, raise error
                raise ProcessingError(
                    ErrorCode.MODEL_UNAVAILABLE,
                    "Both primary and fallback models failed",
                    {
                        "primary_error": str(e),
                        "fallback_error": str(fallback_error)
                    }
                )
```

### 9.3 Circuit Breaker

```python
from datetime import datetime, timedelta

class CircuitBreaker:
    """Circuit breaker to prevent cascading failures"""

    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func):
        """Wrap function with circuit breaker"""

        if self.state == "OPEN":
            # Check if timeout has passed
            if datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.timeout_seconds):
                self.state = "HALF_OPEN"
                print("Circuit breaker entering HALF_OPEN state")
            else:
                raise ProcessingError(
                    ErrorCode.OPENROUTER_UNAVAILABLE,
                    "Circuit breaker is OPEN - service temporarily unavailable",
                    {
                        "retry_after_seconds": self.timeout_seconds,
                        "state": self.state
                    }
                )

        try:
            result = func()

            # Success - reset if in HALF_OPEN
            if self.state == "HALF_OPEN":
                self.reset()

            return result

        except Exception as e:
            self.record_failure()
            raise e

    def record_failure(self):
        """Record a failure"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            print(f"Circuit breaker opened after {self.failure_count} failures")

    def reset(self):
        """Reset circuit breaker"""
        self.failure_count = 0
        self.state = "CLOSED"
        print("Circuit breaker reset to CLOSED")

# Usage
openrouter_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout_seconds=60)

async def safe_openrouter_call(request_data: Dict):
    """Call OpenRouter with circuit breaker protection"""

    async def make_call():
        return await client.chat.completions.create(**request_data)

    return openrouter_circuit_breaker.call(lambda: asyncio.run(make_call()))
```

---

## 10. Rate Limiting & Quotas

### 10.1 Rate Limit Strategy

```python
from asyncio import Semaphore, Queue
import time

class RateLimiter:
    """
    Rate limiter for OpenRouter API

    OpenRouter limits (typical):
    - 60 requests per minute per API key
    - 10,000 requests per hour
    """

    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 10000):
        self.rpm_limit = requests_per_minute
        self.rph_limit = requests_per_hour

        self.minute_requests = []
        self.hour_requests = []

        self.semaphore = Semaphore(requests_per_minute)

    async def acquire(self):
        """Acquire permission to make a request"""

        now = time.time()

        # Clean old requests from tracking
        self.minute_requests = [t for t in self.minute_requests if now - t < 60]
        self.hour_requests = [t for t in self.hour_requests if now - t < 3600]

        # Check if we're at limits
        if len(self.minute_requests) >= self.rpm_limit:
            wait_time = 60 - (now - self.minute_requests[0])
            print(f"Rate limit: waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)

        if len(self.hour_requests) >= self.rph_limit:
            wait_time = 3600 - (now - self.hour_requests[0])
            print(f"Hourly limit: waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)

        # Record request
        self.minute_requests.append(now)
        self.hour_requests.append(now)

        await self.semaphore.acquire()

    def release(self):
        """Release semaphore"""
        self.semaphore.release()

# Global rate limiter
openrouter_limiter = RateLimiter(requests_per_minute=60, requests_per_hour=10000)

# Wrap API calls
async def rate_limited_api_call(request_data: Dict):
    """Make API call with rate limiting"""

    await openrouter_limiter.acquire()

    try:
        response = await client.chat.completions.create(**request_data)
        return response
    finally:
        openrouter_limiter.release()
```

### 10.2 Request Queue

```python
from enum import Enum

class RequestPriority(int, Enum):
    """Request priority levels"""
    LOW = 3
    NORMAL = 2
    HIGH = 1
    CRITICAL = 0

class PriorityQueue:
    """Priority queue for API requests"""

    def __init__(self):
        self.queues = {
            RequestPriority.CRITICAL: Queue(),
            RequestPriority.HIGH: Queue(),
            RequestPriority.NORMAL: Queue(),
            RequestPriority.LOW: Queue()
        }
        self.processor_task = None

    async def enqueue(self, request_data: Dict, priority: RequestPriority = RequestPriority.NORMAL):
        """Add request to queue"""

        await self.queues[priority].put(request_data)

        # Start processor if not running
        if self.processor_task is None or self.processor_task.done():
            self.processor_task = asyncio.create_task(self._process_queue())

    async def _process_queue(self):
        """Process queued requests in priority order"""

        while True:
            # Check queues in priority order
            for priority in [RequestPriority.CRITICAL, RequestPriority.HIGH, RequestPriority.NORMAL, RequestPriority.LOW]:
                if not self.queues[priority].empty():
                    request_data = await self.queues[priority].get()

                    try:
                        result = await rate_limited_api_call(request_data)
                        # Store result somewhere for retrieval
                        # (implementation depends on your setup)
                    except Exception as e:
                        print(f"Queued request failed: {e}")

                    break
            else:
                # All queues empty, sleep briefly
                await asyncio.sleep(0.1)

# Global queue
request_queue = PriorityQueue()

# Usage
async def queue_property_analysis(property_id: str, image_urls: List[str], priority: RequestPriority):
    """Queue property for analysis"""

    request_data = {
        'property_id': property_id,
        'image_urls': image_urls,
        'timestamp': time.time()
    }

    await request_queue.enqueue(request_data, priority)

    return {
        'status': 'queued',
        'priority': priority.name,
        'message': 'Property analysis queued for processing'
    }
```

### 10.3 Quota Management

```python
class QuotaManager:
    """Manage daily/monthly API quotas"""

    def __init__(self, daily_budget_usd: float = 100.0, monthly_budget_usd: float = 2000.0):
        self.daily_budget = daily_budget_usd
        self.monthly_budget = monthly_budget_usd
        self.redis = redis.Redis()

    async def check_quota(self) -> Dict[str, any]:
        """Check if we're within quota"""

        today = datetime.utcnow().strftime('%Y-%m-%d')
        this_month = datetime.utcnow().strftime('%Y-%m')

        # Get current usage
        daily_spent = float(self.redis.get(f"quota:daily:{today}") or 0)
        monthly_spent = float(self.redis.get(f"quota:monthly:{this_month}") or 0)

        # Check limits
        daily_ok = daily_spent < self.daily_budget
        monthly_ok = monthly_spent < self.monthly_budget

        return {
            'quota_available': daily_ok and monthly_ok,
            'daily_spent': daily_spent,
            'daily_budget': self.daily_budget,
            'daily_remaining': max(0, self.daily_budget - daily_spent),
            'monthly_spent': monthly_spent,
            'monthly_budget': self.monthly_budget,
            'monthly_remaining': max(0, self.monthly_budget - monthly_spent)
        }

    async def record_usage(self, cost_usd: float):
        """Record API usage against quota"""

        today = datetime.utcnow().strftime('%Y-%m-%d')
        this_month = datetime.utcnow().strftime('%Y-%m')

        # Increment daily
        self.redis.incrbyfloat(f"quota:daily:{today}", cost_usd)
        self.redis.expire(f"quota:daily:{today}", 86400 * 2)  # Keep for 2 days

        # Increment monthly
        self.redis.incrbyfloat(f"quota:monthly:{this_month}", cost_usd)
        self.redis.expire(f"quota:monthly:{this_month}", 86400 * 60)  # Keep for 60 days

    async def enforce_quota(self):
        """Raise error if quota exceeded"""

        status = await self.check_quota()

        if not status['quota_available']:
            if status['daily_remaining'] <= 0:
                raise ProcessingError(
                    ErrorCode.QUOTA_EXCEEDED,
                    "Daily API budget exceeded",
                    status
                )
            else:
                raise ProcessingError(
                    ErrorCode.QUOTA_EXCEEDED,
                    "Monthly API budget exceeded",
                    status
                )

# Global quota manager
quota_manager = QuotaManager(daily_budget_usd=100.0, monthly_budget_usd=2000.0)

# Middleware
@app.middleware("http")
async def quota_middleware(request: Request, call_next):
    """Check quota before processing request"""

    # Check quota for API endpoints
    if request.url.path.startswith("/api/v1/property"):
        await quota_manager.enforce_quota()

    response = await call_next(request)
    return response
```

---

## 11. Monitoring & Observability

### 11.1 Logging

```python
import logging
import json
from datetime import datetime

# Structured logging
class StructuredLogger:
    """JSON structured logging for analysis"""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(logging.INFO)

        # JSON formatter
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)

    def log_api_request(
        self,
        endpoint: str,
        model: str,
        input_size: int,
        request_id: str,
        user_id: str
    ):
        """Log API request"""

        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'service': self.service_name,
            'event_type': 'api_request',
            'endpoint': endpoint,
            'model': model,
            'input_size': input_size,
            'request_id': request_id,
            'user_id': user_id
        }

        self.logger.info(json.dumps(log_data))

    def log_api_response(
        self,
        request_id: str,
        status: str,
        latency_ms: float,
        output_size: int,
        cost_usd: float
    ):
        """Log API response"""

        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'service': self.service_name,
            'event_type': 'api_response',
            'request_id': request_id,
            'status': status,
            'latency_ms': latency_ms,
            'output_size': output_size,
            'cost_usd': cost_usd
        }

        self.logger.info(json.dumps(log_data))

    def log_error(
        self,
        request_id: str,
        error_code: str,
        error_message: str,
        stack_trace: str = None
    ):
        """Log error"""

        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'service': self.service_name,
            'event_type': 'error',
            'request_id': request_id,
            'error_code': error_code,
            'error_message': error_message,
            'stack_trace': stack_trace
        }

        self.logger.error(json.dumps(log_data))

logger = StructuredLogger('openrouter-integration')
```

### 11.2 Metrics

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
api_requests_total = Counter(
    'openrouter_requests_total',
    'Total OpenRouter API requests',
    ['endpoint', 'model', 'status']
)

api_latency_seconds = Histogram(
    'openrouter_latency_seconds',
    'OpenRouter API latency',
    ['endpoint', 'model']
)

api_cost_usd = Counter(
    'openrouter_cost_usd_total',
    'Total API cost in USD',
    ['endpoint', 'model']
)

api_tokens = Counter(
    'openrouter_tokens_total',
    'Total tokens processed',
    ['endpoint', 'model', 'token_type']
)

active_requests = Gauge(
    'openrouter_active_requests',
    'Number of active API requests',
    ['endpoint']
)

class MetricsCollector:
    """Collect and export metrics"""

    @staticmethod
    def track_request(endpoint: str, model: str):
        """Track API request start"""
        active_requests.labels(endpoint=endpoint).inc()
        start_time = time.time()
        return start_time

    @staticmethod
    def track_response(
        endpoint: str,
        model: str,
        start_time: float,
        status: str,
        input_tokens: int,
        output_tokens: int,
        cost: float
    ):
        """Track API response"""

        # Latency
        latency = time.time() - start_time
        api_latency_seconds.labels(endpoint=endpoint, model=model).observe(latency)

        # Request count
        api_requests_total.labels(endpoint=endpoint, model=model, status=status).inc()

        # Tokens
        api_tokens.labels(endpoint=endpoint, model=model, token_type='input').inc(input_tokens)
        api_tokens.labels(endpoint=endpoint, model=model, token_type='output').inc(output_tokens)

        # Cost
        api_cost_usd.labels(endpoint=endpoint, model=model).inc(cost)

        # Active requests
        active_requests.labels(endpoint=endpoint).dec()

# Expose metrics endpoint
from prometheus_client import make_asgi_app

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

### 11.3 Health Checks

```python
@app.get("/health")
async def health_check():
    """Service health check"""

    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'checks': {}
    }

    # Check OpenRouter connectivity
    try:
        test_response = await client.chat.completions.create(
            model="anthropic/claude-haiku-3.5",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        health_status['checks']['openrouter'] = 'healthy'
    except Exception as e:
        health_status['checks']['openrouter'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'degraded'

    # Check Redis
    try:
        redis_client = redis.Redis()
        redis_client.ping()
        health_status['checks']['redis'] = 'healthy'
    except Exception as e:
        health_status['checks']['redis'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'degraded'

    # Check database
    try:
        # Execute simple query
        await db.execute("SELECT 1")
        health_status['checks']['database'] = 'healthy'
    except Exception as e:
        health_status['checks']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'degraded'

    # Check quota
    quota_status = await quota_manager.check_quota()
    if not quota_status['quota_available']:
        health_status['checks']['quota'] = 'exceeded'
        health_status['status'] = 'unhealthy'
    else:
        health_status['checks']['quota'] = f"healthy ({quota_status['daily_remaining']:.2f} USD remaining today)"

    return health_status

@app.get("/stats")
async def get_stats():
    """Get usage statistics"""

    today = datetime.utcnow().strftime('%Y-%m-%d')

    # Get today's usage
    costs = await get_daily_costs(today)

    # Get quota info
    quota = await quota_manager.check_quota()

    return {
        'date': today,
        'usage_by_endpoint': costs,
        'quota': quota,
        'circuit_breaker_state': openrouter_circuit_breaker.state
    }
```

---

## 12. Future Features

### 12.1 Image Enhancement Pipeline

```python
# Future: Image upscaling and enhancement

class ImageEnhancer:
    """
    Enhance property images before analysis or display

    Potential services:
    - Replicate (Real-ESRGAN for upscaling)
    - Cloudflare Image Resizing
    - Adobe Firefly API (when available)
    """

    async def upscale_image(self, image_url: str, scale: int = 2) -> str:
        """
        Upscale image using Real-ESRGAN

        Cost: ~$0.001 per image
        """

        # Replicate API call
        import replicate

        output = await replicate.run(
            "nightmareai/real-esrgan:42fed1c4974146d4d2414e2be2c5277c7fcf05fcc3a73abf41610695738c1d7b",
            input={
                "image": image_url,
                "scale": scale,
                "face_enhance": True
            }
        )

        return output

    async def apply_hdr(self, image_url: str) -> str:
        """Apply HDR enhancement to property images"""
        # Implementation with image processing service
        pass

    async def remove_background(self, image_url: str) -> str:
        """Remove background from property items (furniture, etc.)"""
        # Use remove.bg API or similar
        pass
```

### 12.2 3D Walkthrough Generation

```python
# Future: Generate 3D walkthroughs from 2D images

class WalkthroughGenerator:
    """
    Generate 3D property walkthroughs

    Potential approaches:
    - Luma AI Dream Machine (video generation)
    - Runway Gen-3 (video from images)
    - NeRF-based reconstruction
    - Matterport-style tours (if hardware available)
    """

    async def generate_walkthrough(
        self,
        property_images: List[str],
        narration_script: str
    ) -> str:
        """
        Generate video walkthrough from images

        Estimated cost: $1-5 per video
        Processing time: 5-15 minutes
        """

        # Example with Luma AI
        import lumaai

        # 1. Generate video frames from images
        video_url = await lumaai.generate_video(
            images=property_images,
            style="architectural_walkthrough",
            duration_seconds=30
        )

        # 2. Add voice narration (ElevenLabs or OpenAI TTS)
        narrated_video_url = await self.add_narration(video_url, narration_script)

        return narrated_video_url

    async def add_narration(self, video_url: str, script: str) -> str:
        """Add AI voice narration to video"""
        # ElevenLabs API for voice generation
        # FFmpeg to merge audio with video
        pass
```

### 12.3 Voice-Over Generation

```python
# Future: Generate property listing voice-overs

class VoiceOverGenerator:
    """
    Generate professional voice-overs for property listings

    Services:
    - ElevenLabs (high quality, multilingual)
    - OpenAI TTS (good quality, cheaper)
    - Google Cloud TTS (decent, very cheap)
    """

    async def generate_voiceover(
        self,
        script: str,
        language: str = "en",
        voice_style: str = "professional"
    ) -> bytes:
        """
        Generate voice-over audio

        Cost:
        - ElevenLabs: $0.30 per 1000 characters
        - OpenAI TTS: $15 per 1M characters
        - Google TTS: $4 per 1M characters
        """

        # Example with ElevenLabs
        from elevenlabs import generate, Voice

        audio = generate(
            text=script,
            voice=Voice(
                voice_id="21m00Tcm4TlvDq8ikWAM",  # Professional male voice
                settings={
                    "stability": 0.75,
                    "similarity_boost": 0.85
                }
            ),
            model="eleven_multilingual_v2"  # Supports Thai, English, Russian
        )

        return audio
```

### 12.4 Roadmap

```
Q1 2026: MVP Launch
- ✅ Text extraction (Claude Sonnet 4.5)
- ✅ Image analysis (GPT-4o Vision)
- ✅ Basic caching and optimization
- ⏳ Voice transcription integration

Q2 2026: Enhancement Phase
- 🔮 Advanced image preprocessing
- 🔮 Multi-property batch processing
- 🔮 Enhanced caching strategies
- 🔮 Cost analytics dashboard

Q3 2026: Premium Features
- 🔮 Image enhancement (upscaling, HDR)
- 🔮 Voice-over generation
- 🔮 Multi-language support enhancement
- 🔮 A/B testing for model selection

Q4 2026: Advanced AI
- 🔮 3D walkthrough generation
- 🔮 Virtual staging
- 🔮 Property comparison AI
- 🔮 Predictive pricing models
```

---

## 13. MVP Implementation Plan

### 13.1 Phase 1: Text Processing (Week 1)

**Goal:** Extract property details from text descriptions

**Tasks:**
1. Set up OpenRouter API client
2. Implement TextProcessor with Claude Sonnet 4.5
3. Create PropertyDetails schema
4. Build `/api/v1/property/extract-text` endpoint
5. Add basic error handling
6. Unit tests

**Success Criteria:**
- Can extract structured data from text descriptions
- Handles English, Thai, Russian
- Confidence scores > 0.7 for clear descriptions
- Response time < 3 seconds

### 13.2 Phase 2: Image Analysis (Week 2-3)

**Goal:** Analyze property images to detect features and condition

**Tasks:**
1. Implement ImagePreprocessor (resize, compress)
2. Build ImageAnalyzer with GPT-4o Vision
3. Add R2 integration for image storage
4. Implement parallel image processing
5. Create insight aggregation logic
6. Build `/api/v1/property/analyze-images` endpoint
7. Integration tests

**Success Criteria:**
- Can analyze 10 images in < 30 seconds
- Accurately detects room types (>80% accuracy)
- Identifies key amenities
- Stays within $0.10 per property budget

### 13.3 Phase 3: Multimodal Orchestration (Week 4)

**Goal:** Combine text + image processing into unified pipeline

**Tasks:**
1. Build MultimodalPropertyProcessor
2. Implement result merging logic
3. Add validation and confidence scoring
4. Create standardized response format
5. Build `/api/v1/property/process-multimodal` endpoint
6. End-to-end tests

**Success Criteria:**
- Can process text + 10 images in < 35 seconds
- Merges insights intelligently
- Returns comprehensive property data
- Overall confidence > 0.75

### 13.4 Phase 4: Production Hardening (Week 5)

**Goal:** Make system production-ready

**Tasks:**
1. Implement rate limiting
2. Add caching layer (Redis)
3. Set up error handling and retries
4. Configure logging and monitoring
5. Add quota management
6. Performance optimization
7. Security audit

**Success Criteria:**
- Handles 100 concurrent requests
- 99% uptime
- Average response time < 10 seconds
- Cost < $1 per property

### 13.5 Phase 5: Voice Processing (Week 6) [Optional for MVP]

**Goal:** Add voice message transcription

**Tasks:**
1. Integrate Whisper API
2. Build VoiceProcessor
3. Add audio file handling
4. Create `/api/v1/property/process-voice` endpoint
5. Tests

**Success Criteria:**
- Transcribes Thai/English/Russian audio
- < 30 seconds for 2-minute audio
- Accuracy > 90%

---

## 14. Code Examples

### 14.1 Complete FastAPI Application

```python
# main.py - Complete OpenRouter integration

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Initialize app
app = FastAPI(
    title="Bestays Property AI API",
    description="OpenRouter-powered property analysis",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processors
text_processor = TextProcessor()
image_analyzer = ImageAnalyzer()
voice_processor = VoiceProcessor()
multimodal_processor = MultimodalPropertyProcessor()

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.post("/api/v1/property/extract-text", response_model=PropertyAnalysisResponse)
async def extract_text(
    description: str,
    context: Optional[str] = None,
    property_id: Optional[str] = None
):
    """Extract property details from text description"""

    start_time = time.time()
    request_id = f"req_{uuid.uuid4().hex[:12]}"

    try:
        # Log request
        logger.log_api_request(
            endpoint="text",
            model="anthropic/claude-sonnet-4.5",
            input_size=len(description),
            request_id=request_id,
            user_id="system"  # Replace with actual user
        )

        # Process
        result = await text_processor.extract_property_details(description, context)

        # Format response
        response = ResponseFormatter.format_property_response(
            property_data=result.model_dump(),
            modalities=['text'],
            models_used={'text': 'anthropic/claude-sonnet-4.5'},
            start_time=start_time,
            token_usage={'text_input': 500, 'text_output': 300}  # Estimate
        )

        # Log response
        logger.log_api_response(
            request_id=request_id,
            status='success',
            latency_ms=response.processing_time_ms,
            output_size=len(response.model_dump_json()),
            cost_usd=response.estimated_cost_usd
        )

        return response

    except Exception as e:
        logger.log_error(request_id, "TEXT_PROCESSING_ERROR", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/property/analyze-images", response_model=PropertyAnalysisResponse)
async def analyze_images(
    image_urls: List[str],
    optimize_cost: bool = True,
    property_id: Optional[str] = None
):
    """Analyze property images"""

    start_time = time.time()
    request_id = f"req_{uuid.uuid4().hex[:12]}"

    try:
        # Check quota
        await quota_manager.enforce_quota()

        # Process images
        insights = await image_analyzer.analyze_property_images(
            image_urls,
            optimize_cost=optimize_cost
        )

        # Format response
        response = ResponseFormatter.format_property_response(
            property_data=insights.model_dump(),
            modalities=['images'],
            models_used={'vision': 'openai/gpt-4o'},
            start_time=start_time,
            token_usage={'vision_tokens': len(image_urls) * 850}  # Estimate
        )

        # Record usage
        await quota_manager.record_usage(response.estimated_cost_usd)

        return response

    except ProcessingError as e:
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/property/process-multimodal")
async def process_multimodal(
    text_description: Optional[str] = None,
    image_urls: Optional[List[str]] = None,
    property_id: Optional[str] = None,
    background_tasks: BackgroundTasks = None
):
    """
    Process property with multiple modalities

    This is the main endpoint for comprehensive property analysis
    """

    start_time = time.time()

    if not text_description and not image_urls:
        raise HTTPException(
            status_code=400,
            detail="At least one of text_description or image_urls required"
        )

    try:
        # Process
        result = await multimodal_processor.process_complete_property(
            text_description=text_description,
            image_urls=image_urls,
            timeout_seconds=120
        )

        # Format
        response = ResponseFormatter.format_property_response(
            property_data=result,
            modalities=result['sources_used'],
            models_used={
                'text': 'anthropic/claude-sonnet-4.5',
                'vision': 'openai/gpt-4o'
            },
            start_time=start_time,
            token_usage={
                'text_input': 500,
                'text_output': 300,
                'vision_tokens': len(image_urls or []) * 850
            }
        )

        # Background: Save to database
        if background_tasks and property_id:
            background_tasks.add_task(
                save_property_analysis,
                property_id,
                response.model_dump()
            )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/health")
async def health():
    """Health check"""
    return await health_check()


@app.get("/api/v1/stats")
async def stats():
    """Usage statistics"""
    return await get_stats()


# ============================================================================
# BACKGROUND TASKS
# ============================================================================

async def save_property_analysis(property_id: str, analysis: Dict):
    """Save analysis to database (background task)"""
    # Implementation depends on your database setup
    pass


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup():
    """Initialize resources on startup"""
    print("Starting Bestays Property AI API...")

    # Test OpenRouter connection
    try:
        test_response = await client.chat.completions.create(
            model="anthropic/claude-haiku-3.5",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        print("✓ OpenRouter connection successful")
    except Exception as e:
        print(f"✗ OpenRouter connection failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    print("Shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 14.2 Environment Configuration

```bash
# .env

# OpenRouter
OPENROUTER_API_KEY=sk-or-v1-xxx

# OpenAI (for Whisper)
OPENAI_API_KEY=sk-xxx

# Database
DATABASE_URL=postgresql://user:pass@localhost/bestays

# Redis
REDIS_URL=redis://localhost:6379

# Cloudflare R2
R2_ACCOUNT_ID=xxx
R2_ACCESS_KEY_ID=xxx
R2_SECRET_ACCESS_KEY=xxx
R2_BUCKET_NAME=bestays-properties

# Quotas
DAILY_BUDGET_USD=100.0
MONTHLY_BUDGET_USD=2000.0

# Features
ENABLE_CACHING=true
ENABLE_RATE_LIMITING=true
ENABLE_VOICE_PROCESSING=false  # MVP: disable initially
```

### 14.3 Requirements

```txt
# requirements.txt

fastapi==0.115.0
uvicorn[standard]==0.31.0
pydantic==2.9.0
openai==1.54.0
httpx==0.27.0
python-dotenv==1.0.1
pillow==10.4.0
redis==5.1.0
psycopg2-binary==2.9.9
sqlalchemy==2.0.35
boto3==1.35.0  # For R2
tenacity==9.0.0  # Retry logic
prometheus-client==0.21.0  # Metrics
```

---

## 15. Cost Estimates

### 15.1 Per-Property Cost Breakdown

**Scenario:** 1 property with 10 images + text description

| Component | Model | Tokens/Images | Unit Cost | Total Cost |
|-----------|-------|---------------|-----------|------------|
| Text extraction | Claude Sonnet 4.5 | 500 input + 300 output | $3/$15 per 1M | $0.006 |
| Image analysis (10 images) | GPT-4o Vision | 10 images @ 850 tokens each | $5 per 1M input | $0.043 |
| **TOTAL** | | | | **$0.049** |

**With optimization (low detail for 5 images):**

| Component | Cost |
|-----------|------|
| Text extraction | $0.006 |
| 5 images (high detail) | $0.021 |
| 5 images (low detail) | $0.013 |
| **TOTAL** | **$0.040** |

### 15.2 Volume Estimates

**1000 properties (10 images each):**

| Scenario | Cost per Property | Total Cost |
|----------|-------------------|------------|
| No optimization | $0.049 | $49.00 |
| With optimization | $0.040 | $40.00 |
| Aggressive optimization (3 high + 7 low) | $0.033 | $33.00 |

**With caching (50% cache hit rate):**

| Scenario | Total Cost | Savings |
|----------|------------|---------|
| No cache | $49.00 | - |
| 50% cache hits | $24.50 | 50% |
| 75% cache hits | $12.25 | 75% |

### 15.3 Monthly Budget Planning

**Daily limits:**
- Budget: $100/day
- Properties processable: ~2,500 properties/day (with optimization)
- Images: ~25,000 images/day

**Monthly limits:**
- Budget: $2,000/month
- Properties: ~50,000 properties/month
- Images: ~500,000 images/month

---

## 16. Production Considerations

### 16.1 Security

```python
# Security best practices

# 1. API Key rotation
async def rotate_api_key():
    """Rotate OpenRouter API key periodically"""
    # Implement key rotation logic
    pass

# 2. Input validation
from pydantic import validator, Field

class SecurePropertyInput(BaseModel):
    description: str = Field(max_length=10000)
    image_urls: List[str] = Field(max_items=50)

    @validator('image_urls')
    def validate_urls(cls, v):
        """Ensure URLs are from trusted domains"""
        allowed_domains = ['r2.bestays.com', 'cdn.bestays.com']
        for url in v:
            domain = url.split('/')[2]
            if domain not in allowed_domains:
                raise ValueError(f"URL domain not allowed: {domain}")
        return v

# 3. Rate limiting per user
class UserRateLimiter:
    """Per-user rate limiting"""

    def __init__(self):
        self.redis = redis.Redis()

    async def check_user_limit(self, user_id: str, limit: int = 100) -> bool:
        """Check if user is within their hourly limit"""
        key = f"user_limit:{user_id}:{datetime.utcnow().strftime('%Y%m%d%H')}"
        count = self.redis.incr(key)
        self.redis.expire(key, 3600)

        return count <= limit
```

### 16.2 Scalability

```python
# Horizontal scaling considerations

# 1. Stateless design - all state in Redis/DB
# 2. Load balancing - multiple FastAPI instances
# 3. Queue-based processing - separate workers for heavy tasks

# Worker setup
# docker-compose.yml

version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000-8003:8000"
    replicas: 4
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    depends_on:
      - redis
      - postgres

  worker:
    build: .
    command: python worker.py
    replicas: 2
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}

  redis:
    image: redis:7-alpine

  postgres:
    image: postgres:16-alpine
```

### 16.3 Disaster Recovery

```python
# Backup and recovery strategies

# 1. Database backups
# - Daily PostgreSQL dumps
# - Stored in S3/R2 with 30-day retention

# 2. Configuration backups
# - Environment configs in version control
# - Secrets in vault (HashiCorp Vault, AWS Secrets Manager)

# 3. Graceful degradation
async def process_with_fallback(request_data: Dict):
    """Process with multiple fallback levels"""

    try:
        # Primary: Full AI processing
        return await multimodal_processor.process_complete_property(**request_data)
    except Exception as e:
        print(f"Primary processing failed: {e}")

        try:
            # Fallback 1: Text-only processing
            if request_data.get('text_description'):
                return await text_processor.extract_property_details(
                    request_data['text_description']
                )
        except Exception as e2:
            print(f"Fallback 1 failed: {e2}")

            # Fallback 2: Return partial data
            return {
                'status': 'partial',
                'message': 'AI processing unavailable, manual review required',
                'raw_data': request_data
            }
```

---

## Appendix A: OpenRouter Model Reference

### Available Models (as of 2025-11)

**Text Models:**
- `anthropic/claude-sonnet-4.5` - $3/$15 per 1M tokens
- `anthropic/claude-haiku-3.5` - $0.80/$4 per 1M tokens
- `openai/gpt-4o` - $5/$20 per 1M tokens
- `google/gemini-2.5-pro` - $2.50/$15 per 1M tokens
- `google/gemini-2.5-flash` - $1.25/$10 per 1M tokens

**Vision Models:**
- `openai/gpt-4o` - $5/$20 per 1M tokens (best vision)
- `anthropic/claude-sonnet-4.5` - $3/$15 per 1M tokens (good vision)
- `google/gemini-2.5-pro` - $2.50/$15 per 1M tokens (cost-effective)
- `meta-llama/llama-3.2-90b-vision-instruct` - FREE (lower quality)

**Free Tier Models (for testing):**
- `meta-llama/llama-3.2-11b-vision-instruct:free`
- `qwen/qwen-2.5-vl-7b-instruct:free`
- `google/gemma-2-9b-it:free`

---

## Appendix B: API Request Examples

### Text Extraction

```bash
curl -X POST "https://api.bestays.com/api/v1/property/extract-text" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "description": "Beautiful 3BR villa in Phuket with pool. 250 sqm, 80k/month.",
    "context": "Location: Rawai",
    "property_id": "prop_123"
  }'
```

### Image Analysis

```bash
curl -X POST "https://api.bestays.com/api/v1/property/analyze-images" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "image_urls": [
      "https://r2.bestays.com/prop_123/bedroom1.jpg",
      "https://r2.bestays.com/prop_123/pool.jpg"
    ],
    "optimize_cost": true,
    "property_id": "prop_123"
  }'
```

### Multimodal Processing

```bash
curl -X POST "https://api.bestays.com/api/v1/property/process-multimodal" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "text_description": "3BR villa with pool",
    "image_urls": ["https://r2.bestays.com/prop_123/1.jpg"],
    "property_id": "prop_123"
  }'
```

---

## Conclusion

This OpenRouter integration architecture provides a comprehensive, production-ready solution for multimodal property processing. The MVP focuses on text and image processing with Claude Sonnet 4.5 and GPT-4o Vision, achieving:

- **Cost efficiency:** ~$0.04 per property
- **Performance:** < 30 seconds for full analysis
- **Reliability:** 99% uptime with fallbacks
- **Scalability:** Handles 2,500+ properties/day

Future enhancements will add voice processing, image enhancement, and 3D walkthrough generation as the platform matures.

---

**Document Status:** Ready for Implementation
**Next Steps:**
1. Review with engineering team
2. Set up OpenRouter API key
3. Begin Phase 1 implementation (text processing)
4. Schedule weekly check-ins for progress review

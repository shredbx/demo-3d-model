# Property Chat CMS - LLM Architecture Documentation

This directory contains the architecture analysis and implementation plan for the **Property Chat CMS** - an LLM-powered system that enables real estate agents to create property listings through multimodal chat input.

---

## Documentation Index

### 01_LLM_ARCHITECTURE_ANALYSIS.md

**Comprehensive architecture design covering:**

1. **System Architecture** - High-level flow, component design, architectural patterns
2. **LLM Pipeline Design** - LangChain stack, component architecture, prompt engineering
3. **Property Type Detection** - Detection algorithm, confidence scoring, feature indicators
4. **Data Extraction Strategy** - Multi-stage pipeline, Pydantic schemas, validation
5. **Amenity & Feature Detection** - RAG-based matching, image analysis, catalog integration
6. **Multimodal Processing** - Text/image/voice handling, model selection matrix
7. **Conversation Flow** - Single-shot vs multi-turn, state management, example flows
8. **LangChain Implementation** - Code examples, tools, parsers, integration
9. **Performance & Cost Analysis** - Detailed cost breakdowns, optimization strategies
10. **Error Handling & Resilience** - Error categories, fallback strategies, validation
11. **MVP Roadmap** - 7-phase implementation plan (11 weeks)
12. **Appendices** - Sample prompts, database schemas, risk mitigation

---

## Quick Reference

### Key Features

- **Multimodal Input**: Text descriptions, property images, voice recordings
- **Property Type Detection**: Automatic classification (rental/sale/lease/business/investment)
- **Structured Data Extraction**: 165+ amenities, 81 location advantages, full property schema
- **Conversational UI**: Multi-turn dialogue with clarification questions
- **Agent Review**: Pre-filled form for confirmation before publishing

### Tech Stack

- **LLM Framework**: LangChain 0.3+ with structured output
- **Models**:
  - Text: Google Gemini 2.5 Flash Lite (fast, cheap)
  - Vision: OpenAI GPT-4o (accurate image analysis)
  - Voice: Whisper API (transcription)
- **Backend**: FastAPI, PostgreSQL + pgvector, Redis
- **Frontend**: SvelteKit 5 (Runes)

### Cost Estimates (per 1000 properties)

| Scenario | Cost | Use Case |
|----------|------|----------|
| Text only | $12 | Simple listings |
| Text + 5 images | **$150** | **MVP target** |
| Text + images + voice | $200 | On-site tours |

### MVP Timeline

- **Phase 1-2** (Weeks 1-4): Text + Image extraction
- **Phase 3-4** (Weeks 5-6): Multi-turn + Voice
- **Phase 5-6** (Weeks 7-10): Frontend + Testing
- **Phase 7** (Week 11): Production launch

**Total: 11 weeks from start to production**

---

## Implementation Checklist

### Phase 1: Foundation (Weeks 1-2)
- [ ] LangChain agent setup
- [ ] Property type detection
- [ ] Structured extraction (rental + sale)
- [ ] Validation logic
- [ ] API endpoint
- [ ] Unit tests

### Phase 2: Image Analysis (Weeks 3-4)
- [ ] Vision model integration (GPT-4o)
- [ ] Image upload handling
- [ ] Amenity detection from images
- [ ] RAG-based amenity matching
- [ ] Image storage (R2)

### Phase 3: Multi-Turn (Week 5)
- [ ] Conversation state management
- [ ] Clarification questions
- [ ] Iterative refinement
- [ ] Agent correction handling

### Phase 4: Voice (Week 6)
- [ ] Voice recording (frontend)
- [ ] Whisper API integration
- [ ] Voice + text fusion

### Phase 5: Frontend (Weeks 7-8)
- [ ] Chat interface (SvelteKit)
- [ ] File upload component
- [ ] Property review form
- [ ] Mobile-responsive design

### Phase 6: Testing (Weeks 9-10)
- [ ] Integration tests
- [ ] Performance benchmarks
- [ ] Agent user testing
- [ ] Bug fixes

### Phase 7: Launch (Week 11)
- [ ] Production deployment
- [ ] Monitoring setup
- [ ] Agent training
- [ ] Gradual rollout

---

## Key Design Decisions

### 1. Multi-Stage Pipeline
✅ **Chosen**: Detection → Extraction → Validation → Clarification
- Better error handling
- Higher confidence scoring
- Iterative refinement capability

❌ **Rejected**: Single-shot extraction
- Lower accuracy for incomplete data
- No opportunity for clarification

### 2. Model Strategy
✅ **Chosen**: Vision models for images + fast models for text
- GPT-4o for images ($0.01/image) - best accuracy
- Gemini 2.5 Flash Lite for text ($0.075/1M tokens) - 4x cheaper
- Whisper for voice ($0.006/min) - industry standard

❌ **Rejected**: Single model for everything
- No multimodal support in Gemini yet
- More expensive if using GPT-4o for text

### 3. Amenity Detection
✅ **Chosen**: RAG with pgvector embeddings
- Reuses existing FAQ infrastructure
- Handles synonyms and variations
- Fast (<1s with indexed vectors)

❌ **Rejected**: Few-shot learning only
- Requires more tokens per request
- Less consistent results
- Can't leverage catalog structure

### 4. Conversation Flow
✅ **Chosen**: Adaptive multi-turn
- Single-shot if data complete (fast)
- Multi-turn if clarification needed (accurate)
- Agent controls pace

❌ **Rejected**: Always multi-turn
- Slower for simple cases
- More API calls = higher cost

---

## Architecture Highlights

### LangChain Components

```python
# Agent with Tools Pattern
PropertyExtractionAgent
  ├── PropertyTypeTool (detect type)
  ├── PropertyExtractionTool (extract fields)
  ├── AmenityDetectionTool (match catalog)
  └── ValidationTool (check completeness)

# Memory Integration
ConversationBufferMemory
  └── PostgresChatMessageHistory (reuse existing conversations)

# Structured Output
PydanticOutputParser
  └── PropertyExtractionResult (type-safe schemas)
```

### Database Extensions

```sql
-- New tables required:
- property_extractions (extraction metadata + results)
- amenity_embeddings (RAG matching)
- location_advantage_embeddings (RAG matching)
- extraction_audit_logs (debugging + improvement)
```

### API Endpoints

```
POST /api/v1/properties/extract
  - Multipart: text, images[], voice_file
  - Response: PropertyExtractionResult

POST /api/v1/properties/extract/{id}/refine
  - Body: clarification answer
  - Response: Updated PropertyExtractionResult

GET /api/v1/properties/extract/{id}
  - Response: Extraction status + data
```

---

## Success Metrics

### Technical Metrics
- Property type detection accuracy: >90%
- Required field extraction accuracy: >85%
- Amenity detection accuracy: >80%
- Processing time: <25s (text + 5 images)
- API uptime: >99.9%

### Business Metrics
- Agent adoption rate: >80% of active agents
- Time savings: 70-80% reduction vs manual entry
- Data quality: <5% correction rate after agent review
- Cost per property: <$0.20 average

### User Experience Metrics
- Agent satisfaction: >4/5 rating
- Average conversation turns: <3
- Completion rate: >95%
- Mobile usage: >60% of interactions

---

## Risk Mitigation

### Top 5 Risks & Mitigations

1. **LLM Hallucinations** → Confidence scoring + mandatory agent review
2. **High API Costs** → Token optimization + caching + model selection
3. **Low Agent Adoption** → User testing + training + gradual rollout
4. **Data Quality Issues** → Validation + confidence thresholds + review workflow
5. **API Rate Limits** → Retry logic + fallback models + batch processing

---

## Next Steps

1. ✅ Architecture analysis complete
2. ⏭️ Review with development team
3. ⏭️ Create user story for Phase 1 (US-XXX: Property Extraction - Text Only)
4. ⏭️ Set up LangChain dependencies
5. ⏭️ Begin Phase 1 implementation

---

## Related Documentation

- [Property Modernization Plan](../04_PROPERTY_MODERNIZATION_PLAN.md) - Database schema
- [Properties Schema](../02_PROPERTIES_SCHEMA.md) - Property data model
- [Architecture Overview](../01_ARCHITECTURE.md) - System architecture

---

**Status**: 📋 Analysis Complete - Ready for Implementation
**Last Updated**: 2025-11-06
**Contact**: Development Team

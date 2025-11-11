# Chat-Driven UI Architecture

**Status:** Architectural Vision (TBD Implementation)
**Created:** 2025-11-09
**Scope:** System-Wide Pattern
**Impact:** ALL Features (Current + Future)

---

## Vision

A universal pattern where the AI chat assistant can interact with ANY field on ANY page, providing intelligent suggestions based on context. The chat is always available (folded or expanded) and has full awareness of the current page state and all input fields.

---

## Core Principles

### 1. Universal Chat Availability
- Chat component is present on EVERY page (public, agent, admin)
- Always accessible in folded or expanded state
- Persists across page navigation (floating component)
- Context-aware of current route, user role, page state

### 2. Field-Level Intelligence
- Chat has API-like interface to ALL input fields on current page
- Can suggest values for ANY field based on:
  - Page context (property details, user profile, listing page)
  - User role (agent, admin, visitor)
  - Related data (images, previous inputs, database records)
  - LLM analysis (image recognition, text extraction, semantic understanding)

### 3. Inline Suggestion UI
- Suggestions appear as **inline popups** in actual input fields
- NOT separate modal or sidebar
- User sees suggestion directly where they would type
- Multiple suggestions → carousel navigation (left/right arrows)
- One-click insertion into field
- Non-intrusive (dismissible, doesn't block workflow)

---

## Architecture Components

### Frontend (SvelteKit)

**1. Universal Suggestion Component**
```typescript
// apps/frontend/src/lib/components/chat/FieldSuggestion.svelte
interface FieldSuggestion {
  fieldId: string;           // DOM element ID or selector
  suggestions: string[];     // Array of suggested values
  currentIndex: number;      // Carousel position
  confidence: number;        // AI confidence (0-100%)
  source: 'llm' | 'historical' | 'dictionary';
}
```

**2. Page Context Provider**
```typescript
// apps/frontend/src/lib/stores/pageContext.svelte.ts
class PageContext {
  currentRoute: string;
  availableFields: FieldMetadata[];
  userRole: 'visitor' | 'agent' | 'admin';
  pageData: Record<string, any>;

  registerField(field: FieldMetadata): void;
  getSuggestions(fieldId: string): Promise<FieldSuggestion>;
}
```

**3. Chat-Page Interface**
- Every page exports `getChatContext()` function
- Returns: Available fields, current values, field types, validation rules
- Chat queries this interface for suggestions

**Example:**
```typescript
// apps/frontend/src/routes/[locale]/listings/properties/[id]/+page.svelte
export function getChatContext() {
  return {
    pageType: 'property_detail',
    editableFields: [
      { id: 'title', type: 'text', maxLength: 200, currentValue: '...' },
      { id: 'price', type: 'number', min: 0, currentValue: 35000 },
      { id: 'amenities', type: 'multi-select', dictionary: 'property_amenities' }
    ],
    relatedData: {
      images: [...],
      location: { lat, lng },
      propertyType: 'villa'
    }
  };
}
```

### Backend (FastAPI)

**1. Field Suggestion API**
```python
# apps/server/src/api/v1/chat/field_suggestions.py
@router.post("/api/v1/chat/suggest")
async def suggest_field_value(
    field_context: FieldContext,
    user: User = Depends(get_current_user)
) -> FieldSuggestion:
    """
    Generate suggestions for a specific field based on:
    - Field type and validation rules
    - Page context (images, text, related data)
    - User history (previous inputs)
    - Property dictionary (for amenities, categories)
    - LLM analysis (if images or text provided)
    """
    pass
```

**2. Context-Aware LLM Prompts**
```python
# Include field metadata in LLM prompts
prompt = f"""
Analyze this property image and suggest values for:
- Field: {field_id}
- Type: {field_type}
- Validation: {validation_rules}
- Current page: {page_type}
- User role: {user_role}

Return suggestions as JSON array with confidence scores.
"""
```

### Database Schema

**1. Suggestion History (Optional)**
```sql
CREATE TABLE suggestion_history (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  field_id TEXT NOT NULL,
  suggested_value TEXT NOT NULL,
  accepted BOOLEAN NOT NULL,
  confidence DECIMAL(5,2),
  source TEXT, -- 'llm', 'historical', 'dictionary'
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_suggestion_acceptance ON suggestion_history(field_id, accepted);
```

**2. Field Configuration (Optional)**
```sql
CREATE TABLE field_configs (
  id UUID PRIMARY KEY,
  page_type TEXT NOT NULL,
  field_id TEXT NOT NULL,
  field_type TEXT NOT NULL,
  validation_rules JSONB,
  suggestion_enabled BOOLEAN DEFAULT TRUE,
  suggestion_sources TEXT[], -- ['llm', 'historical', 'dictionary']
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(page_type, field_id)
);
```

---

## User Experience Flow

### Example 1: Property Creation (Chat-Driven)
1. Agent opens chat on property detail page
2. Agent: "I have 3 images of a villa. Can you help fill in the details?"
3. Agent uploads images to chat
4. Chat analyzes images → identifies pool, mountain view, modern kitchen
5. Chat: "I found these features. Would you like me to suggest values for the fields?"
6. Agent: "Yes"
7. **Inline popups appear** in these fields:
   - `amenities` field → Suggests: "Private Pool", "Mountain View", "Modern Kitchen" (carousel: 1/3)
   - `property_type` field → Suggests: "Villa"
   - `bedrooms` field → Suggests: "3" (if visible in images)
8. Agent navigates carousel (left/right arrows) or clicks to insert
9. Agent edits if needed, saves property

### Example 2: Property Editing (Inline + Chat)
1. Agent viewing property detail page (public-facing view)
2. Right-click on `title` field → "Edit Title" (like US-020)
3. OR: Opens chat → "Suggest a better title based on the property features"
4. Chat analyzes: location, amenities, property type
5. **Inline popup appears** in `title` field → "Luxury 3BR Villa with Pool & Mountain View"
6. Agent clicks to insert, edits if needed, saves

### Example 3: Multi-Field Batch Suggestions
1. Agent on property detail page with partial data
2. Chat: "I notice some fields are empty. Would you like suggestions?"
3. Agent: "Yes, fill in what you can"
4. **Multiple inline popups appear** simultaneously:
   - `description` field → Suggested paragraph
   - `amenities` field → Carousel of 10 suggested amenities
   - `location.proximity` field → "500m to beach"
5. Agent reviews each suggestion, accepts/edits/rejects

---

## Implementation Phases

### Phase 1: Foundation (Current - US-020, US-022)
- ✅ Inline editing pattern (US-020 homepage content)
- ✅ Property detail page with editable fields (US-022)
- ✅ Chat UI component (basic)
- ✅ Property dictionary (MCP)

### Phase 2: Chat-Page Interface (TBD - Future US)
- [ ] `getChatContext()` interface for all pages
- [ ] PageContext store (Svelte)
- [ ] Field registration system
- [ ] Chat can query current page state

### Phase 3: Field Suggestion UI (TBD - Future US)
- [ ] Universal FieldSuggestion component
- [ ] Inline popup rendering
- [ ] Carousel navigation (multiple suggestions)
- [ ] Keyboard shortcuts (Tab to accept, Esc to dismiss)

### Phase 4: Backend Suggestion API (TBD - Future US)
- [ ] `/api/v1/chat/suggest` endpoint
- [ ] Context-aware LLM prompts
- [ ] Historical suggestion tracking
- [ ] Confidence scoring

### Phase 5: Advanced Features (TBD - Future US)
- [ ] Multi-field batch suggestions
- [ ] Real-time suggestions as user types
- [ ] Learning from user acceptance/rejection
- [ ] Per-field configuration (enable/disable suggestions)

---

## Design Principles

### 1. Non-Intrusive
- Suggestions are **optional** and **dismissible**
- User can ignore and type manually
- No blocking modals or forced workflows

### 2. Context-Aware
- Suggestions must match field type and validation rules
- Consider page context (property type, location, user role)
- Use related data (images, existing fields) for better accuracy

### 3. Transparent
- Show confidence scores for LLM suggestions
- Indicate source: LLM analysis, historical data, dictionary lookup
- User always in control (can edit or reject)

### 4. Performance
- Suggestions load asynchronously (don't block page render)
- Cache frequent suggestions (property types, common amenities)
- Debounce API calls (wait for user to pause typing)

---

## Technical Considerations

### Security
- RBAC: Only agents/admins can see suggestions (visitors cannot)
- Rate limiting: Prevent abuse of suggestion API
- Input validation: Sanitize all suggested values before insertion

### Accessibility
- Keyboard navigation for carousel (left/right arrows, Enter to accept)
- Screen reader announcements for suggestions
- Focus management (return focus to field after insertion)

### Mobile UX
- Touch-friendly carousel (swipe gestures)
- Larger tap targets for suggestion buttons
- Responsive popup positioning

---

## Current Implementation Status

**US-020 (Homepage Editable Content):**
- ✅ Inline editing with right-click context menu
- ✅ Edit dialog with field preview
- ✅ RBAC enforcement (admin-only)
- ❌ NO chat-driven suggestions yet

**US-022 (AI Property Management):**
- ⏳ Property detail page with inline editing (planned)
- ⏳ Chat interface for property creation (planned)
- ❌ NO field-level suggestions yet (future vision)

---

## Architectural Impact

### For System Architects
- Design ALL pages with `getChatContext()` interface in mind
- Plan API endpoints with chat suggestion capability
- Consider field-level metadata in UI components

### For Backend Developers
- Design APIs to return suggestion-compatible responses
- Include confidence scores and sources in API responses
- Plan for suggestion history tracking

### For Frontend Developers
- Use reusable field components (easy to add suggestion support later)
- Maintain consistent field IDs across pages
- Design forms with inline popup space in mind

### For DevOps
- Monitor suggestion API performance (latency, rate limits)
- Cache strategy for frequent suggestions
- LLM usage tracking (cost optimization)

---

## Related Documentation

- `.sdlc-workflow/guides/ai-agent-workflow-pattern.md` - AI safety model (prepare → confirm → execute)
- `.sdlc-workflow/stories/content/US-020-homepage-editable-content.md` - Inline editing pattern
- `.sdlc-workflow/stories/properties/US-022-properties-ai-creation-management.md` - AI property creation

---

## Questions for Future Planning

1. Should every page have suggestion capability, or start with high-value pages (property detail, profile)?
2. Should we track suggestion acceptance rates to improve LLM prompts?
3. Should suggestions be personalized per agent (learn from their preferences)?
4. Should we support voice input for chat → suggestions?
5. Should suggestions appear automatically or only when requested?

---

**Version:** 1.0
**Status:** Architectural Vision (Not Yet Implemented)
**Next Review:** During PLANNING phase of Chat Suggestion US (TBD)

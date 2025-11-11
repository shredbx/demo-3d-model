# AI Agent Workflow Pattern

**Status:** APPROVED
**Date:** 2025-11-09
**Applies To:** All AI-powered features (US-022 AI Property Creation, future chat-based CMS)

---

## Core Principle

**AI agents PREPARE data. Users EXECUTE actions.**

The AI agent is an **assistant**, not an **autonomous actor**. All database mutations require explicit user confirmation via CTA click + RBAC validation.

---

## Workflow Pattern

### Phase 1: AI Data Collection (Safe)

**AI Agent Role:**
- Analyze user input (text, images, files)
- Extract structured data using LLM
- Generate JSON payloads
- Prepare preview/confirmation UI
- **NO database writes**
- **NO API mutations**

**Example (Property Creation):**
```
Agent uploads: 10 images + property description
↓
LLM analyzes: Text extraction + image tagging
↓
AI generates: Property V2 JSON (physical_specs, amenities, etc.)
↓
Show preview modal: Agent reviews extracted fields
```

**Safety:** AI can't break anything. Only preparing data.

---

### Phase 2: User Confirmation (Required)

**User (Agent) Actions:**
1. Review AI-generated data in preview modal
2. Edit any incorrect/incomplete fields
3. Verify confidence scores (green/yellow/red indicators)
4. Click CTA button: **"Create Property"**, **"Update Property"**, **"Delete Property"**

**UI Pattern:**
```svelte
<!-- Property Creation Confirmation Modal -->
<div class="preview-modal">
  <h2>Review Property Details</h2>

  <!-- AI-generated fields with confidence indicators -->
  {#each extractedFields as field}
    <FieldPreview
      {field}
      confidence={field.confidence}
      editable={true}
    />
  {/each}

  <!-- CTA buttons -->
  <button on:click={handleCancel}>Cancel</button>
  <button on:click={handleCreateProperty} class="primary">
    Create Property
  </button>
</div>
```

**User Clicks "Create Property"** → Triggers Phase 3

---

### Phase 3: API Request + RBAC (Secure)

**Frontend Action:**
```typescript
const handleCreateProperty = async () => {
  // Send API request with user JWT token
  const response = await fetch('/api/v1/properties', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${userToken}`, // Clerk JWT
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(aiGeneratedProperty)
  });

  if (response.ok) {
    navigate('/properties/' + response.data.id);
  }
};
```

**Backend Validation:**
```python
@router.post("/api/v1/properties")
async def create_property(
    property_data: PropertyCreate,
    current_user: User = Depends(get_current_user)  # Clerk authentication
):
    # RBAC validation
    if current_user.role not in ["agent", "admin"]:
        raise HTTPException(403, "Insufficient permissions")

    # Validate data
    validated_data = PropertyV2Schema.parse(property_data)

    # Create in database
    property = await db.properties.create(validated_data)

    return property
```

**Security Layers:**
1. ✅ User authentication (Clerk JWT)
2. ✅ RBAC validation (agent/admin role required)
3. ✅ Data validation (Zod/Pydantic schemas)
4. ✅ Database constraints (PostgreSQL checks)

**Result:** Property created in database with `created_by = current_user.id`

---

## Safety Guarantees

### What AI Agent CAN Do (Safe)
- ✅ Analyze text/images
- ✅ Generate structured JSON
- ✅ Show preview modals
- ✅ Suggest values
- ✅ Highlight confidence scores
- ✅ Prepare data payloads

### What AI Agent CANNOT Do (Protected by RBAC)
- ❌ Write to database directly
- ❌ Call mutation APIs autonomously
- ❌ Create/Update/Delete records
- ❌ Bypass RBAC checks
- ❌ Execute actions without user confirmation

**Key Rule:** Database mutations ALWAYS require:
1. User CTA click
2. Frontend API request with JWT
3. Backend RBAC validation
4. Schema validation

---

## Application to US-022 (AI Property Creation)

### Workflow Sequence

**Step 1: Agent Opens Chat Interface**
```
Agent role logged in (Clerk authentication)
↓
Opens property creation chat UI
↓
Uploads: 10 images + text description
```

**Step 2: AI Analysis (Safe Phase)**
```
LLM processes:
- Text extraction: bedrooms, bathrooms, price, amenities
- Image analysis: pool, garden, mountain view, modern style
↓
Generates Property V2 JSON:
{
  "physical_specs": { "rooms": { "bedrooms": 4, "bathrooms": 3 } },
  "amenities": { "exterior": ["private_pool"], ... },
  "location_details": { "location_advantages": ["mountain_view"] }
}
↓
Shows preview modal with confidence scores
```

**Step 3: Agent Review (User Control)**
```
Agent sees preview modal:
✅ Bedrooms: 4 (confidence: 95% - green)
⚠️ Bathrooms: 3 (confidence: 75% - yellow) → Agent edits to 2
✅ Pool: Yes (confidence: 100% - green)
✅ Price: ฿150,000/month (confidence: 98% - green)

Agent clicks: "Create Property"
```

**Step 4: API Request + RBAC (Secure Phase)**
```
Frontend: POST /api/v1/properties with Clerk JWT
↓
Backend: Validates agent role + Zod schema
↓
Database: Inserts property with created_by = agent.id
↓
Success: Redirect to /properties/{id}
```

### Key Takeaway for US-022

**AI prepares, user executes.**
- Agent confirmation modal is MANDATORY (not optional)
- Every field editable before creation
- No autonomous property creation
- RBAC ensures only agents/admins can create properties

---

## Future Applications

### Chat-Based CMS (General Pattern)

**Use Case:** Agent asks AI to update property description

**Workflow:**
```
Agent: "Update property 123 description to: Beautiful seaside villa..."
↓
AI generates: { "description": "Beautiful seaside villa..." }
↓
Shows preview: "You're about to update property 123. Review changes?"
↓
Agent clicks: "Confirm Update"
↓
API: PATCH /api/v1/properties/123 (with RBAC validation)
↓
Database: Updates property (updated_by = agent.id)
```

**Safety:** AI prepares update payload, but database write only happens after:
1. Agent reviews changes
2. Agent clicks "Confirm Update"
3. Backend validates RBAC
4. Schema validation passes

### Bulk Operations (Advanced Pattern)

**Use Case:** Agent asks AI to update 50 properties

**Workflow:**
```
Agent: "Add 'pet_friendly' amenity to all properties in Phuket"
↓
AI generates: List of 50 property IDs + amendment JSON
↓
Shows preview table: "You're about to update 50 properties. Review?"
↓
Agent clicks: "Confirm Bulk Update"
↓
API: POST /api/v1/properties/bulk-update (with RBAC validation)
↓
Backend: Validates agent role + iterates updates
↓
Database: Updates 50 properties (audit trail with updated_by = agent.id)
```

**Safety:** Even bulk operations require explicit user confirmation.

---

## Implementation Checklist

### For Every AI-Powered Feature

**Phase 1: AI Preparation (Safe)**
- [ ] AI agent analyzes user input
- [ ] LLM generates structured data
- [ ] Show preview modal with confidence scores
- [ ] All fields editable by user

**Phase 2: User Confirmation (Required)**
- [ ] Clear CTA button (Create/Update/Delete)
- [ ] Review UI shows all changes
- [ ] User can cancel at any time
- [ ] User explicitly clicks to proceed

**Phase 3: API + RBAC (Secure)**
- [ ] Frontend sends API request with JWT
- [ ] Backend validates user authentication (Clerk)
- [ ] Backend validates RBAC (role-based permissions)
- [ ] Backend validates data schema (Zod/Pydantic)
- [ ] Database operation with audit trail (created_by/updated_by)

**Phase 4: Success Feedback**
- [ ] Show success message
- [ ] Redirect to resource page
- [ ] Update UI state
- [ ] Log action for audit

---

## RBAC Matrix for Property Operations

| Role | Create Property | Update Own Property | Update Any Property | Delete Property | Bulk Operations |
|------|----------------|---------------------|---------------------|-----------------|-----------------|
| **User** | ❌ No | ❌ No | ❌ No | ❌ No | ❌ No |
| **Agent** | ✅ Yes | ✅ Yes | ⚠️ Limited (own + assigned) | ⚠️ Limited (own) | ⚠️ Limited |
| **Admin** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |

**Backend Enforcement:**
```python
# Example RBAC check
def check_property_write_permission(current_user: User, property_id: str = None):
    if current_user.role == "admin":
        return True  # Admins can do anything

    if current_user.role == "agent":
        if property_id is None:
            return True  # Agents can create

        # Agents can only update their own properties
        property = db.properties.get(property_id)
        return property.created_by == current_user.id

    return False  # Users cannot write properties
```

---

## Error Handling

### AI Generation Failures

**Scenario:** LLM times out or returns invalid JSON

**Handling:**
```
AI generation fails
↓
Show fallback UI: "AI couldn't analyze. Please fill form manually."
↓
Agent fills form with known data
↓
Agent clicks "Create Property"
↓
API request proceeds normally
```

**Key:** Degraded experience, but property creation still possible without AI.

### RBAC Failures

**Scenario:** User tries to create property without agent role

**Handling:**
```
User clicks "Create Property"
↓
Frontend: POST /api/v1/properties
↓
Backend: Validates role → User is not agent/admin
↓
Returns 403 Forbidden
↓
Frontend shows: "You don't have permission to create properties."
```

**Security:** Backend ALWAYS validates, never trusts frontend.

---

## Audit Trail

**Every mutation includes:**
```json
{
  "created_by": "user-uuid",
  "updated_by": "user-uuid",
  "created_at": "2025-11-09T10:30:00Z",
  "updated_at": "2025-11-09T14:20:00Z"
}
```

**AI metadata (optional):**
```json
{
  "ai_metadata": {
    "generated_by": "gpt-4-turbo",
    "generation_timestamp": "2025-11-09T10:29:45Z",
    "confidence_scores": {
      "bedrooms": 95,
      "bathrooms": 75,
      "price": 98
    },
    "agent_edited_fields": ["bathrooms", "description"]
  }
}
```

**Purpose:** Track what AI suggested vs what agent confirmed.

---

## Benefits of This Pattern

### 1. Safety
- ✅ AI can't break anything (no database access)
- ✅ User always in control
- ✅ RBAC enforced on all mutations

### 2. User Experience
- ✅ AI speeds up data entry (85% auto-fill)
- ✅ User reviews and edits (quality assurance)
- ✅ Clear feedback (confidence scores)

### 3. Compliance
- ✅ Audit trail (who created, who updated)
- ✅ RBAC enforcement (role-based permissions)
- ✅ Data validation (schema checks)

### 4. Flexibility
- ✅ Works even if AI fails (fallback to manual)
- ✅ User can override any AI suggestion
- ✅ Gradual rollout (feature flags)

---

## Related Documentation

- **US-022:** AI-Powered Property Management System (uses this pattern)
- **CLAUDE.md:** Multi-product workflow and RBAC guidelines
- **Property V2 Schema:** Database structure and validation rules
- **Clerk Authentication:** User authentication and role management

---

**Version:** 1.0
**Last Updated:** 2025-11-09
**Status:** APPROVED for all AI-powered features

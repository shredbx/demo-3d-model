# Chat-as-CMS UX Design Analysis

**Status:** DRAFT - For Review
**Created:** 2025-11-06
**Purpose:** Design conversational interface for property creation and management
**Target Users:** Real estate agents (tech-savvy, multilingual)
**Goal:** Reduce property creation time from 15-30 minutes to 3-5 minutes

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Design Principles](#design-principles)
3. [Conversation Flow Design](#conversation-flow-design)
4. [Multimodal Input Handling](#multimodal-input-handling)
5. [Property Type Detection UX](#property-type-detection-ux)
6. [Data Extraction Presentation](#data-extraction-presentation)
7. [Correction & Refinement](#correction--refinement)
8. [Amenity Selection UX](#amenity-selection-ux)
9. [Progress & State Management](#progress--state-management)
10. [Multi-Property Management](#multi-property-management)
11. [Error Handling & Fallbacks](#error-handling--fallbacks)
12. [Mobile Experience](#mobile-experience)
13. [Localization](#localization)
14. [Example Conversation Flows](#example-conversation-flows)
15. [Message Schemas](#message-schemas)
16. [State Machine](#state-machine)
17. [MVP Scope](#mvp-scope)
18. [Integration Strategy](#integration-strategy)

---

## Executive Summary

### The Challenge

Real estate agents currently spend 15-30 minutes per property filling out 20+ form fields, managing 165+ amenity options, 81 location advantages, and 9 room types. This is tedious and slows down their workflow, especially when they're on-site with photos and voice notes ready.

### The Solution

A **conversational AI interface** that:
- Accepts multimodal input (photos + voice/text)
- Extracts structured data using LLM
- Presents extracted data for quick review/correction
- Reduces creation time to 3-5 minutes
- Works seamlessly on mobile

### Key Innovations

1. **Single-Message Creation**: Agent can upload 10-20 photos + voice/text description in one message
2. **Smart Extraction**: LLM extracts 80%+ of required fields automatically
3. **Confidence-Based UI**: Shows high-confidence fields as "ready", low-confidence as "needs review"
4. **Conversational Correction**: Natural language edits ("Actually it's 4 bedrooms, not 3")
5. **Progressive Disclosure**: Only show complex options (amenities) when needed
6. **Hybrid Approach**: Chat for quick creation, form for detailed editing

---

## Design Principles

### 1. Speed Over Precision (First Pass)
- Prioritize getting properties listed quickly
- Accept 80% accuracy, allow refinement later
- Draft state by default, publish when ready

### 2. Conversational, Not Form-Like
- No "Please enter the number of bedrooms"
- Instead: Show extracted data, ask for corrections only if uncertain

### 3. Progressive Disclosure
- Don't overwhelm with 165 amenities upfront
- Show LLM-detected amenities first
- Offer "Add more" if agent wants to browse catalogue

### 4. Mobile-First Interaction
- Large touch targets
- Voice input priority
- Camera integration
- Minimal typing

### 5. Trust But Verify
- Show confidence scores for uncertain fields
- Make corrections effortless
- Never force agent to re-explain obvious things

### 6. Multilingual by Default
- Detect agent's language from input
- Allow mixed languages (Thai input → English description)
- Show UI in agent's preferred language

---

## Conversation Flow Design

### Primary Flow: Single-Message Creation

```
[AGENT] Uploads 15 photos + voice note describing villa
        ↓
[AI]    "I'm analyzing your photos and description..."
        (Processing: 5-10 seconds)
        ↓
[AI]    Shows extracted property card with confidence indicators
        "I've created a draft for a 3-bedroom pool villa in Patong.
         Here's what I found - let me know if anything needs changing."

        [Property Preview Card]
        ✓ Type: Pool Villa (95% confident)
        ✓ Location: Patong, Phuket (90% confident)
        ✓ Bedrooms: 3 (85% confident)
        ⚠ Bathrooms: 2 (60% confident) - Please verify
        ✓ Pool: Private pool detected
        ✓ Price: Not detected - Please add

        [Buttons: "Looks good" | "Make changes" | "Add pricing"]
        ↓
[AGENT] "Actually 4 bathrooms, and price is 15M baht"
        ↓
[AI]    Updates property
        "Got it! Updated to 4 bathrooms and 15,000,000 THB.
         Want to add this to the sale listings now?"

        [Buttons: "Yes, publish" | "Save as draft" | "Add more details"]
```

### Alternative Flow: Multi-Turn Creation

```
[AGENT] "I want to add a new villa"
        ↓
[AI]    "Great! I can help you create a listing quickly.
         You can upload photos and tell me about it,
         or we can go step-by-step. What works better?"

        [Buttons: "Upload photos" | "Step-by-step" | "Voice description"]
        ↓
[AGENT] Uploads 10 photos
        ↓
[AI]    "Nice property! I can see it's a villa with a pool.
         Can you tell me more about it? (Or record a voice note)"

        [Voice button] [Text input]
        ↓
[AGENT] Records voice: "It's a 3 bedroom villa in Patong..."
        ↓
[AI]    Shows extracted property card (same as above)
```

### Key Design Decisions

**✓ Single message with attachments (PREFERRED)**
- Faster for agents
- Mimics natural behavior (take photos → describe)
- Fewer round trips

**✗ Multi-turn conversation**
- More hand-holding
- Useful for uncertain agents
- Fallback if single-message fails

**Handling Missing Information:**

```
[AI]    "I couldn't detect the price from your description.
         What's the listing price?"

        [Quick inputs: Currency selector | Price input]
        [Or: "I'll add it later" button]
```

**Smart Follow-ups:**
- Only ask for critical missing fields (price, location if not detected)
- Everything else can be added later
- Never block listing creation on optional fields

---

## Multimodal Input Handling

### Multiple Images at Once

**Upload Experience:**

```
[Agent taps camera icon]
  ↓
[System shows options]
  • Take photos now (opens camera)
  • Choose from gallery (allows multi-select)
  • From recent (shows last 20 photos)
```

**During Upload:**

```
[Chat shows upload progress]
📷 Uploading 15 photos...
[Progress bar] 8/15

[As images upload, show thumbnails]
[✓] bedroom1.jpg
[✓] pool.jpg
[...] kitchen.jpg (uploading)
```

**After Upload:**

```
[AI message]
"I've received 15 photos. I can see:
 • Exterior and pool (6 photos)
 • Bedrooms (4 photos)
 • Kitchen and living area (3 photos)
 • Bathrooms (2 photos)

Ready to analyze when you give me a description.
Or should I start analyzing now?"

[Buttons: "Analyze now" | "Let me add description first"]
```

### Voice + Images + Text in One Message

**Input Combination:**

```
[Agent's message composition area]
┌────────────────────────────────┐
│ [Voice recording active] 0:45  │
│ "This is a beautiful 3-bed..." │
│                                │
│ [📷 15 photos attached]        │
│                                │
│ [Optional text field]          │
│ "Beachfront location"          │
│                                │
│ [Send button - blue, prominent]│
└────────────────────────────────┘
```

**Processing Priority:**
1. Images → Extract visual features (property type, rooms, amenities)
2. Voice → Transcribe → Extract structured data
3. Text → Parse additional context
4. Combine all sources → Resolve conflicts (voice overrides image if contradictory)

### Contextual Uploads

**Should agents label uploads?**

**Option A: Let AI figure it out (PREFERRED)**
- Simpler for agent
- AI can categorize images (bedroom, pool, kitchen)
- Shows categorization in preview

**Option B: Optional context**
- Agent can add: "Here are the bedrooms" before uploading
- AI uses context as hint, not requirement
- Useful for ambiguous photos

**Implementation:**

```
[Agent uploads 5 photos]
"Here are the bedroom photos"
  ↓
[AI response]
"Thanks! I've categorized these as bedrooms:
 [Thumbnail grid with labels]
 • Master bedroom (king bed, ensuite)
 • Guest bedroom 1 (twin beds)
 • Guest bedroom 2 (queen bed)

 I detected 3 bedrooms total. Correct?"

[Buttons: "Correct" | "Actually 4 bedrooms" | "Show all photos"]
```

### Incremental Uploads

**Use Case:** Agent realizes they forgot exterior photos

```
[Agent in draft property view]
"Can I add more photos?"
  ↓
[AI]
"Of course! Just upload them and I'll add them to your listing.
 What photos are you adding?"

[Upload button]
  ↓
[Agent uploads 3 more photos]
"Exterior views"
  ↓
[AI]
"Added 3 exterior photos to your villa listing.
 I noticed a nice garden area - should I add 'garden' to amenities?"

[Buttons: "Yes, add it" | "No thanks"]
```

**State Handling:**
- Property remains in draft during additions
- AI can re-analyze and suggest new amenities/features
- Version history tracks what was added when

---

## Property Type Detection UX

### High Confidence Detection

```
[After analyzing photos + description]

[AI message with property card]
"I've identified this as a **Pool Villa** (95% confident)

Based on:
 ✓ Private swimming pool visible
 ✓ Detached structure
 ✓ Multiple bedrooms (3)
 ✓ Luxury finishes

[Property Type Badge: Pool Villa ✓]

Is this correct?"

[Buttons: "Correct" | "Change type"]
```

### Uncertain Detection (50/50)

```
[AI message]
"I'm not sure if this is a **Villa** or a **House**.

What I see:
 • Detached structure ✓
 • Private pool (leans toward villa)
 • But simpler finishes (leans toward house)

Which is more accurate?"

[Radio buttons with images]
○ Villa (typically luxury, pool, high-end finishes)
○ House (standard residential, may have pool)
○ Other: [Dropdown]

[Helper text: "Not sure? Villa = luxury, House = standard"]
```

### Override Type

**From Property Preview:**

```
[Property Card]
Type: House

[Pencil icon to edit]
  ↓
[Modal or inline editor]
"Change property type:"

[Searchable dropdown with icons]
🏠 House
🏡 Villa
🏊 Pool Villa
🏢 Condo
🏘️ Townhouse
...

[Each option shows example image]
```

**Conversational Override:**

```
[Agent] "This is a pool villa, not a house"
        ↓
[AI]    "Updated! Changed type from House to Pool Villa.
         Should I also update the listing title to include 'Pool Villa'?"

[Buttons: "Yes, update title" | "No, keep current title"]
```

---

## Data Extraction Presentation

### Property Preview Card (Primary UI)

```
┌─────────────────────────────────────────┐
│ PROPERTY DRAFT                    [Edit]│
├─────────────────────────────────────────┤
│ [Cover image thumbnail]                 │
│                                         │
│ BEACHFRONT POOL VILLA IN PATONG    95% │
│ ─────────────────────────────────────── │
│                                         │
│ Type & Location                         │
│ ✓ Pool Villa                       95% │
│ ✓ Patong, Phuket                   90% │
│                                         │
│ Physical Details                        │
│ ✓ 3 Bedrooms                       85% │
│ ⚠ 2 Bathrooms                      60% │ ← Low confidence
│ ✓ 250 sqm living area              80% │
│ ✓ 600 sqm land area                75% │
│                                         │
│ Pricing                                 │
│ ⚠ Not detected - Please add             │ ← Missing
│                                         │
│ Amenities Detected (8)                  │
│ ✓ Private pool, Garden, Terrace         │
│ ✓ Air conditioning, WiFi                │
│ [View all] [Add more]                   │
│                                         │
│ Confidence Score: 82% - Good            │
├─────────────────────────────────────────┤
│ [Save as draft] [Add pricing] [Publish] │
└─────────────────────────────────────────┘
```

### Confidence Indicators

**Visual System:**

| Confidence | Icon | Color | Action Required |
|-----------|------|-------|----------------|
| 90-100% | ✓ | Green | None |
| 70-89% | ✓ | Blue | Optional review |
| 50-69% | ⚠ | Orange | Please verify |
| 0-49% | ✗ | Red | Required |
| Missing | 📝 | Gray | Please add |

### Highlighting Uncertain Fields

**Inline Highlighting:**

```
[Property Card with expandable sections]

Physical Details                    [Expand ▼]
─────────────────────────────────────────
✓ 3 Bedrooms                         85%
⚠ 2 Bathrooms                        60%  ← Orange highlight
  [Quick fix: "Is this correct?"]
  [Buttons: ✓ Correct | Change to: 1 2 3 4+]
```

**Alternative: Tooltip on Hover (Desktop)**

```
[Agent hovers over "2 Bathrooms"]
  ↓
[Tooltip appears]
"60% confident - Detected from photos,
 but some bathrooms may not be visible.
 Please verify."

[Quick action: Correct | Change]
```

### Show Confidence Scores?

**Decision: YES, but contextually**

**When to show:**
- ✓ In admin/agent view (they need to verify)
- ✗ In public listing (users don't care)
- ✓ During draft review (helps prioritize corrections)
- ✗ After agent confirms (remove uncertainty markers)

**How to show:**

```
Option A: Percentage (RECOMMENDED)
  "3 Bedrooms (85% confident)"

Option B: Confidence level
  "3 Bedrooms - High confidence"

Option C: Icon only
  "3 Bedrooms ✓✓"  (very confident)
  "2 Bathrooms ⚠"  (uncertain)

→ Use Option C (icon only) for clean UI,
  Show percentage on hover/tap
```

### Inline Editing vs "Edit in Form" Button

**Hybrid Approach (RECOMMENDED):**

```
[Property Card]

Quick Edits (Inline):
  • Property type [Dropdown]
  • Bedrooms/bathrooms [Number input]
  • Price [Currency + amount]
  • Location [Map picker]

Complex Edits (Form):
  • Amenities (165+ options)
  • Policies and rules
  • Contact information
  • SEO metadata

[Button: "Edit in full form" - for power users]
```

**Inline Edit Example:**

```
⚠ 2 Bathrooms (60% confident)
   [Pencil icon]
     ↓
   [Inline editor appears]
   Bathrooms: [1] [2] [3] [4] [5] [6+]

   [Save] [Cancel]
```

**When to Force Form:**
- If agent wants to add complex policies
- If agent wants to browse all amenities
- If agent says "I want to add more details"

---

## Correction & Refinement

### Natural Language Corrections

**Simple Corrections:**

```
[Agent] "Actually it's 4 bedrooms, not 3"
        ↓
[AI]    "Updated! Changed bedrooms from 3 → 4.
         [Property Card shows updated value]

         Anything else to fix?"
```

**Multiple Corrections:**

```
[Agent] "It's 4 bedrooms, 3 bathrooms, and the price is 15 million baht"
        ↓
[AI]    "Got it! Updated:
         • Bedrooms: 3 → 4
         • Bathrooms: 2 → 3
         • Price: ✓ 15,000,000 THB (Sale)

         [Updated property card]

         Ready to publish?"
```

**Complex Corrections:**

```
[Agent] "The pool is actually 12x6 meters, and it has a jacuzzi"
        ↓
[AI]    "Thanks for the details! I've:
         • Updated pool dimensions (12m x 6m)
         • Added 'Jacuzzi' to amenities

         Should I also mention this in the description?"

[Buttons: "Yes, add to description" | "No, just amenities"]
```

### Correction Strategies

**Strategy 1: Parse-and-Update (PREFERRED)**
- AI parses natural language correction
- Updates specific fields
- Shows what changed
- Fast and conversational

**Strategy 2: Guided Correction**
- AI asks clarifying questions
- Agent provides structured answers
- More accurate but slower

**When to use which:**

| Scenario | Strategy | Example |
|----------|----------|---------|
| Clear correction | Parse-and-Update | "4 bedrooms not 3" |
| Ambiguous | Guided | "Different price" → "For rent or sale?" |
| Multiple fields | Parse-and-Update | "4 bed, 3 bath, 15M baht" |
| Complex policies | Guided | "Security deposit?" → Ask specific questions |

### Re-run Extraction vs Manual Edit

**Agent says:** "I want to add more details"

**Option A: Re-run Extraction**
```
[AI] "Want to tell me more or upload additional photos?
      I'll re-analyze and update the listing."

[Buttons: "Record voice note" | "Upload photos" | "Type details"]
```

**Option B: Manual Edit**
```
[AI] "I can open the full form where you can:
      • Add more amenities
      • Set policies and rules
      • Add pricing details

      Or tell me what you want to add and I'll do it."

[Buttons: "Open form" | "Tell you"]
```

**Decision: Offer both, but recommend conversational**

```
[AI] "What would you like to add?

      You can:
      • Tell me in chat (faster) 💬
      • Open the full form (more options) 📋"

[Buttons with icons]
```

### Handling Complex Corrections

**Example: Change Multiple Amenities**

```
[Agent] "Actually it doesn't have a garden, but it has a gym"
        ↓
[AI]    "Got it! Amenities updated:
         • Removed: Garden
         • Added: Gym

         Want to add any other amenities?"

[Buttons: "No, that's it" | "Browse amenities" | "Tell me more"]
```

**Example: Change Property Subdomain**

```
[Agent] "This is for lease, not sale"
        ↓
[AI]    "Important change! Switching from Sale → Lease.

         For lease properties, I need a few more details:
         • Minimum lease term?
         • Security deposit (months)?
         • Monthly rent?

         Can you tell me these? (Or skip for now)"

[Buttons: "Tell you now" | "I'll add later"]
```

---

## Amenity Selection UX

### The Challenge

165+ amenity options across 4 categories:
- Interior (47): AC, kitchen, WiFi, wardrobes...
- Exterior (44): Pool, garden, terrace, parking...
- Building (44): Security, gym, elevator, pool...
- Utilities (27): Electricity, water, internet...

### LLM-Detected Amenities (Primary)

```
[Property Card]

Amenities Detected (12)                [Expand ▼]
─────────────────────────────────────────────
Interior (5)
  ✓ Air conditioning (95%)
  ✓ WiFi (90%)
  ✓ Fully equipped kitchen (85%)
  ⚠ Washing machine (65%) - Please verify
  ✓ Built-in wardrobes (80%)

Exterior (4)
  ✓ Private pool (98%)
  ✓ Garden (90%)
  ✓ Terrace (85%)
  ✓ Parking (2 spaces) (80%)

Building (2)
  ✓ 24h Security (75%)
  ✓ CCTV (70%)

Utilities (1)
  ✓ Electricity, Water, Internet

[Buttons below]
✓ Looks good | ✗ Remove incorrect | + Add more
```

### Adding Missing Amenities

**Option A: Search-First (RECOMMENDED)**

```
[Agent taps "Add more"]
  ↓
[Modal appears]
┌──────────────────────────────────┐
│ Add Amenities                    │
├──────────────────────────────────┤
│ [Search box: "What amenities?"]  │
│                                  │
│ Suggestions based on property:   │
│ □ Jacuzzi                        │
│ □ BBQ Area                       │
│ □ Outdoor Dining                 │
│ □ Sea View                       │
│                                  │
│ Or browse categories:            │
│ [Interior] [Exterior] [Building] │
├──────────────────────────────────┤
│          [Done]                  │
└──────────────────────────────────┘
```

**Option B: Category Browse**

```
[Agent taps "Add more" → "Browse categories"]
  ↓
[Expandable categories]

▼ Interior (47)
  □ Air conditioning ✓ (already added)
  □ Ceiling fans
  □ Heating
  □ Fully equipped kitchen ✓
  □ Refrigerator
  ...
  [Show 10, Load more]

▼ Exterior (44)
  □ Private pool ✓
  □ Jacuzzi
  □ Pool heating
  □ Garden ✓
  ...
```

**Option C: Conversational**

```
[Agent] "It also has a jacuzzi and BBQ area"
        ↓
[AI]    "Great! Added to amenities:
         • Jacuzzi
         • BBQ Area

         Anything else?"
```

### Smart Suggestions

**Context-Aware:**

```
[If property type = "Pool Villa"]
  → Suggest: Jacuzzi, Pool heating, Outdoor shower

[If location = "Beachfront"]
  → Suggest: Sea view, Beach access, Outdoor dining

[If detected from photos but uncertain]
  → "I might see a gym in one photo - is there a gym?"
```

### Bulk Selection

**For agents who want full control:**

```
[Agent] "Open full amenity list"
        ↓
[AI]    [Opens modal with all 165 options]

┌─────────────────────────────────────┐
│ All Amenities (165)          [✓ 12] │
├─────────────────────────────────────┤
│ [Search: "pool"]                    │
│                                     │
│ ☑ Private pool                      │ ← Already selected
│ □ Pool heating                      │
│ □ Communal pool                     │
│ ☑ Jacuzzi                           │
│                                     │
│ [Filter by category: All ▼]        │
│                                     │
│ [Select common combinations:]       │
│ • Luxury villa essentials (15)     │
│ • Beachfront extras (8)            │
│ • Family-friendly (12)             │
├─────────────────────────────────────┤
│ [Cancel] [Save 14 amenities]       │
└─────────────────────────────────────┘
```

### Handling Agent Uncertainty

**Agent doesn't know all amenities:**

```
[AI after showing detected amenities]
"I've found 12 amenities. If you're not sure about others,
 we can always add them later.

 Want to:
 • Publish with these 12 ✓
 • Browse to add more 🔍
 • I'll add them later ⏭"

[Buttons]
```

---

## Progress & State Management

### Property Creation States

```
States:
┌─────────────────────────────────────┐
│ 1. Creating    (AI analyzing)       │
│ 2. Draft       (Agent reviewing)    │
│ 3. Incomplete  (Missing critical)   │
│ 4. Ready       (Can publish)        │
│ 5. Published   (Live on site)       │
│ 6. Archived    (Delisted)           │
└─────────────────────────────────────┘

Critical fields required to publish:
  • Property type
  • Location (region + district)
  • Price (at least one price type)
  • At least 1 photo
```

### Save as Draft

**Auto-save:**

```
[During conversation]
Every message: Auto-save to draft
              ↓
[Chat shows indicator]
"Draft auto-saved • Last edit: 2 mins ago"
```

**Manual save:**

```
[Agent taps "Save as draft"]
  ↓
[AI]
"Saved! You can come back to finish this anytime.

 I'll remind you about:
 • Villa in Patong (missing price)

 Want to continue now or later?"

[Buttons: "Continue" | "Done for now"]
```

### Return to Incomplete Properties

**Dashboard View:**

```
MY PROPERTIES
─────────────────────────────────────

📝 Drafts (3)
  • Villa in Patong
    Started: Today, 2:30 PM
    Missing: Price, amenities
    [Continue in chat →]

  • Condo in Bangkok
    Started: Yesterday
    Missing: Photos, description
    [Continue in chat →]

  • Business for sale
    Started: Nov 3
    Mostly complete
    [Continue in chat →]

✓ Published (12)
  [View all →]
```

**Returning to Draft in Chat:**

```
[Agent taps "Continue in chat" on Villa draft]
  ↓
[Chat loads previous context]

[AI]
"Welcome back! You were adding a villa in Patong.

 [Shows previous property card]

 What we still need:
 ⚠ Listing price
 ⚠ More photos (only 3 so far)

 Want to add these now?"

[Buttons: "Add price" | "Upload photos" | "Edit other details"]
```

### Progress Indicator

**During Multi-Step Creation:**

```
[Top of chat shows progress]

Creating Villa Listing
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 75%

✓ Photos uploaded (15)
✓ Property analyzed
✓ Details extracted
○ Price needed
○ Review & publish

[Can tap to jump to specific step]
```

**Property Completion Score:**

```
[In property card]

Listing Completion: 82%
─────────────────────────────────────
✓ Essential info complete
✓ Photos (15) - Good
⚠ Amenities (8) - Add more?
○ Policies - Not set
○ SEO - Not optimized

[Button: "Improve listing"]
```

---

## Multi-Property Management

### Creating Multiple Properties

**Sequential Creation:**

```
[Agent just published a property]
  ↓
[AI]
"Published! Your villa is now live.

 Want to add another property?"

[Buttons: "Yes, new property" | "No, I'm done"]
```

**Batch Creation (Future):**

```
[Agent] "I have 5 properties to add"
        ↓
[AI]    "Great! I can help you add them one by one.

         For fastest results:
         1. Upload all photos for property 1
         2. Give me a quick description
         3. Repeat for each property

         Ready with property 1?"
```

### Switching Between Properties

**Context Management:**

```
[Agent is editing Villa A]
[Agent] "Let me check my condo listing"
        ↓
[AI]    "Sure! Which condo?

         Your condos:
         1. Condo in Sukhumvit (Published)
         2. Condo in Silom (Draft)

         Or search: [Search box]"
        ↓
[Agent] "Sukhumvit"
        ↓
[AI]    [Loads condo property card]
        "Here's your Sukhumvit condo.
         What do you want to do?"

[Buttons: "View live listing" | "Edit" | "Archive"]

[Context indicator at top]
"Now viewing: Condo in Sukhumvit"
[← Back to Villa A]
```

### Editing Existing Properties

**Via Search:**

```
[Agent] "Edit my Patong villa"
        ↓
[AI]    [Shows search results]
        "Found 2 villas in Patong:

         1. Beachfront Pool Villa - ฿15M
            Status: Published

         2. Hillside Villa - ฿8M
            Status: Draft

         Which one?"
```

**Via List:**

```
[Agent] "Show my properties"
        ↓
[AI]    [Shows interactive list]

        YOUR PROPERTIES (15 total)
        ─────────────────────────

        Filters: [All ▼] [Published ▼] [Price ▼]
        Sort: [Recent ▼]

        📍 Patong (5)
        📍 Kata (3)
        📍 Bangkok (7)

        [Each with quick actions: Edit | Archive | Share]
```

**Natural Language Edits:**

```
[Agent] "Change price of my Patong villa to 14 million"
        ↓
[AI]    "Found: Beachfront Pool Villa in Patong
         Current price: 15,000,000 THB

         Update to 14,000,000 THB?"

[Buttons: "Yes, update" | "No, different property"]
```

### Archiving/Deleting Properties

**Soft Delete (Archive):**

```
[Agent] "Archive my Kata condo"
        ↓
[AI]    "Are you sure you want to archive:

         Modern Condo in Kata Beach
         • Status: Published
         • Views: 234
         • Inquiries: 12

         This will remove it from the site but keep the data."

[Buttons: "Yes, archive" | "Cancel"]
        ↓
[Agent confirms]
        ↓
[AI]    "Archived! It's now hidden from the site.
         You can restore it anytime from the archive."
```

**Bulk Operations:**

```
[Agent] "Archive all my sold properties"
        ↓
[AI]    "Found 4 properties with status 'Sold':

         □ Villa in Patong - Sold Oct 15
         □ Condo in Bangkok - Sold Oct 20
         □ Land in Phuket - Sold Nov 1
         □ House in Chiang Mai - Sold Nov 2

         Archive all 4?"

[Buttons: "Yes, archive all" | "Let me choose"]
```

### Search/Filter Properties in Chat

**Natural Language Search:**

```
[Agent] "Show me my villas under 10 million"
        ↓
[AI]    "Found 3 villas under ฿10M:

         1. Hillside Villa, Patong - ฿8M
            3 bed, 2 bath, 400 sqm
            [View] [Edit]

         2. Pool Villa, Kata - ฿9.5M
            2 bed, 2 bath, 350 sqm
            [View] [Edit]

         3. Modern Villa, Rawai - ฿7M
            2 bed, 1 bath, 300 sqm (Draft)
            [View] [Edit]"
```

**Filter Commands:**

```
Supported filters:
• "Show drafts"
• "Show published properties"
• "Show properties in [location]"
• "Show [property type]"
• "Show properties over/under [price]"
• "Show recent properties"
• "Show properties with most views"
```

---

## Error Handling & Fallbacks

### LLM Extraction Fails Completely

**Scenario: AI can't extract anything useful**

```
[Agent uploads photos + description]
  ↓
[AI processes... but fails]
  ↓
[AI]
"I'm having trouble analyzing your property from these photos.

 This might help:
 • Add a description with key details (bedrooms, location, price)
 • Or we can fill it out step-by-step together
 • Or switch to the standard form

 What would you prefer?"

[Buttons: "Add description" | "Step-by-step" | "Use form"]
```

**Fallback Hierarchy:**

```
1st attempt: Full AI extraction
     ↓ (fails)
2nd attempt: AI with guided questions
     ↓ (fails)
3rd attempt: Open standard form with AI assistance
     ↓ (fails)
4th attempt: Basic form (no AI)
```

### Partial Extraction Success

**Scenario: AI gets some fields but not others**

```
[AI]
"I was able to detect:
 ✓ Property type: Villa (90% confident)
 ✓ Location: Phuket (but not specific area)
 ✓ Bedrooms: 3
 ✗ Price: Not detected
 ✗ Land size: Not detected

 Can you help me fill in the missing parts?

 Where in Phuket is it?"

[Quick location buttons]
[Patong] [Kata] [Karon] [Rawai] [Other]
```

### Image Upload Failures

**Individual file failures:**

```
[During upload]
📷 Uploading 15 photos...
✓ bedroom1.jpg
✓ pool.jpg
✗ kitchen.jpg - Upload failed
✓ bathroom.jpg
...

[After upload]
[AI]
"14 of 15 photos uploaded successfully.
 kitchen.jpg failed - would you like to retry?"

[Buttons: "Retry kitchen.jpg" | "Skip it" | "Choose another photo"]
```

**Complete upload failure:**

```
[All uploads fail]
  ↓
[AI]
"I'm having trouble uploading photos right now.

 You can:
 • Try again in a moment
 • Continue without photos (add them later)
 • Save as draft and return later

 What would you like to do?"
```

### Voice Transcription Errors

**Scenario: Voice note is unclear or in mixed languages**

```
[AI processes voice note]
  ↓
[AI]
"I transcribed your voice note, but I'm not sure about some parts:

 '3 bedroom villa in [unclear] with private pool...'

 Could you clarify:
 1. What location did you say? (I heard: 'Pa-dong' or 'Patong'?)

 Or just type the location:"

[Text input box]
[Buttons: "Patong" | "Pang-tao" | "Type it"]
```

### Ambiguous Corrections

**Scenario: Agent says "change the price" but multiple prices exist**

```
[Agent] "Change the price to 200,000 baht"
        ↓
[AI]    "This property has multiple prices:
         • Sale price: 15,000,000 THB
         • Monthly rent: 80,000 THB

         Which one should I change to 200,000 THB?

         Or did you mean 20,000,000 (20 million)?"

[Buttons: "Sale price" | "Rent price" | "I meant 20 million"]
```

### Network/Service Errors

**Transient failures:**

```
[During AI processing]
  ↓
[Error occurs]
  ↓
[AI]
"Oops! Something went wrong while analyzing.
 Your photos and description are saved.

 Retrying... (attempt 2/3)"

[Auto-retry after 2 seconds]
```

**Persistent failures:**

```
[After 3 failed attempts]
  ↓
[AI]
"I'm having trouble connecting to the AI service.

 Your draft is saved. You can:
 • Try again later (I'll keep everything)
 • Continue with the standard form (no AI assistance)
 • Contact support if this keeps happening

 What would you like to do?"

[Buttons: "Try again" | "Use form" | "Save and exit"]
```

### Data Validation Errors

**Scenario: Agent provides invalid data**

```
[Agent] "Price is 500 baht"
        ↓
[AI]    "That seems unusually low for a villa (฿500).

         Did you mean:
         • ฿500,000 (500 thousand)
         • ฿5,000,000 (5 million)
         • ฿500 per night (short-term rental)

         Or is it really ฿500?"

[Buttons for each option + "It's correct"]
```

### Graceful Degradation

**When AI features are unavailable:**

```
[System detects AI service is down]
  ↓
[Chat shows notice]
"⚠ AI assistance is temporarily unavailable.

 You can still create properties using:
 • The standard form (full features)
 • Quick create (basic info only)

 AI features will return shortly."

[Buttons: "Use form" | "Quick create"]
```

---

## Mobile Experience

### Mobile-First Principles

**Key Differences from Desktop:**
- ✓ Larger touch targets (48x48dp minimum)
- ✓ Voice input prominently displayed
- ✓ Camera integration for instant photo capture
- ✓ Simplified UI (fewer options visible at once)
- ✓ Bottom-sheet modals (easier thumb reach)
- ✓ Swipe gestures for common actions

### Camera Integration

**Instant Photo Capture:**

```
[Mobile chat interface]
┌────────────────────────────────┐
│ Create Property                │
├────────────────────────────────┤
│                                │
│ [Chat messages]                │
│                                │
├────────────────────────────────┤
│ Message Input                  │
│ ┌──────────────────────────┐  │
│ │ [Type message]           │  │
│ └──────────────────────────┘  │
│                                │
│ [📷 Camera] [🖼️ Gallery]      │
│ [🎤 Voice]   [📎 Files]       │
└────────────────────────────────┘

[Tapping Camera icon]
  ↓
[Opens camera with custom overlay]
┌────────────────────────────────┐
│ 📷 Take Property Photos        │
├────────────────────────────────┤
│                                │
│     [Camera viewfinder]        │
│                                │
│ [Grid lines helper]            │
│                                │
├────────────────────────────────┤
│ Tips: Capture bedrooms, pool,  │
│ kitchen, bathrooms, exterior   │
├────────────────────────────────┤
│ Taken: 8 photos                │
│ [●] Capture  [✓] Done          │
└────────────────────────────────┘
```

**Photo Counter:**
- Shows how many photos taken
- Minimum 3, recommended 10-15
- Can review/delete before sending

### Voice Input Priority

**Large, Prominent Voice Button:**

```
[Message input area on mobile]
┌────────────────────────────────┐
│ ┌──────────────────────────┐  │
│ │ Tap to type or...        │  │
│ └──────────────────────────┘  │
│                                │
│     🎤  Hold to record         │ ← Large button
│     [___________________]      │ ← Waveform when recording
│                                │
│  Or: [📷 Photos] [✍️ Type]     │
└────────────────────────────────┘
```

**Voice Recording Flow:**

```
1. Agent taps & holds voice button
   → Shows recording interface
   → Waveform animation
   → Timer (00:45)

2. Agent releases to send
   → Auto-transcribes
   → Shows transcription while processing
   → Agent can edit transcription if wrong

3. AI processes with photos
```

**Voice Error Handling:**

```
[If transcription is uncertain]
  ↓
[AI shows]
"I heard: '3 bedroom villa in [Pa-tong?]'

Is this correct?"

[Buttons: "Correct" | "Edit" | "Re-record"]
```

### Simplified Mobile UI

**Property Card on Mobile:**

```
[Mobile view - scrollable]
┌──────────────────────────┐
│ 🏠 PROPERTY DRAFT        │
├──────────────────────────┤
│ [Cover image - large]    │
│                          │
│ Pool Villa in Patong     │
│                          │
│ ✓ 3 Bed • 2 Bath        │
│ ✓ 250 sqm               │
│ ✓ Private Pool          │
│                          │
│ [Swipe for more details] │
│ ──────────────────────── │
│                          │
│ ⚠ Price not set          │
│ [Tap to add →]           │
│                          │
│ [Save Draft]             │
│ [Publish]                │
└──────────────────────────┘

[Swipe up reveals full details]
```

**Bottom Sheet for Actions:**

```
[Agent taps property card]
  ↓
[Bottom sheet slides up]
┌──────────────────────────┐
│ ═════════ [drag handle]  │
├──────────────────────────┤
│ Edit Property            │
│                          │
│ 📝 Edit basic info       │
│ 💰 Add/change price      │
│ 📷 Manage photos         │
│ 🏷️ Edit amenities        │
│ 📍 Change location       │
│                          │
│ 🗑️ Delete draft          │
│                          │
│ [Cancel]                 │
└──────────────────────────┘
```

### Offline Capability

**Offline Draft Creation (MVP Scope - Maybe not):**

```
[Agent loses connection while creating property]
  ↓
[UI shows offline banner]
"📵 Offline - Changes saved locally"

[Agent can continue:]
• Taking photos (stored locally)
• Recording voice (stored locally)
• Typing description
• Making edits

[When connection returns]
"✓ Back online - Syncing..."
[Auto-uploads to server]
```

**Sync Conflict Handling:**

```
[If property was edited elsewhere while offline]
  ↓
[AI shows conflict]
"⚠ This property was updated on another device.

Your changes (offline):
  • Changed bedrooms: 3 → 4

Other device changes:
  • Added price: ฿15M
  • Added 5 photos

Keep both changes?"

[Buttons: "Keep both" | "Keep mine" | "Keep other"]
```

### Mobile Gestures

**Swipe Actions:**

```
[Property list]
┌─────────────────────────────┐
│ Villa in Patong             │ ← Swipe left reveals actions
│ Draft • 2 hours ago         │
│ ═══════════════════════     │
└─────────────────────────────┘

[After swipe left]
┌─────────────────────────────┐
│ Villa in Patong      [✏️][🗑️]│
│ Draft • 2 hours ago   Edit Delete
└─────────────────────────────┘
```

**Pull-to-Refresh:**

```
[In property list]
[Agent pulls down]
  ↓
[Refresh animation]
"Checking for updates..."
  ↓
[Updates list]
"✓ All properties up to date"
```

### Mobile-Specific Optimizations

**Photo Compression:**
- Auto-compress before upload (reduce from 5MB to 500KB)
- Show upload progress per photo
- Allow background upload

**Voice Optimization:**
- Use device's native speech recognition when available (faster)
- Fallback to server transcription if needed
- Cache transcriptions locally

**Data Saving Mode:**
- Option to disable image previews in chat (save bandwidth)
- Load thumbnails instead of full images
- Progressive image loading

---

## Localization

### Multi-Language Support

**Supported Languages:**
- 🇹🇭 Thai (ไทย)
- 🇬🇧 English
- 🇷🇺 Russian (Русский)
- 🇨🇳 Chinese (中文)

### Language Detection

**Auto-Detect from Input:**

```
[Agent sends first message]
"สวัสดี ฉันต้องการเพิ่มวิลล่า"
  ↓
[AI detects Thai, responds in Thai]
"สวัสดีค่ะ! ดีใจที่จะช่วยคุณสร้างรายการวิลล่า
 คุณอัพโหลดรูปถ่ายได้เลยค่ะ"
```

**Language Switcher:**

```
[In chat settings]
┌────────────────────────────┐
│ Language / ภาษา            │
├────────────────────────────┤
│ ○ English                  │
│ ● ไทย (Thai)               │
│ ○ Русский (Russian)        │
│ ○ 中文 (Chinese)            │
│                            │
│ [Save]                     │
└────────────────────────────┘
```

### Mixed Language Scenarios

**Scenario 1: Agent speaks Thai, wants English description**

```
[Agent in Thai]
"ฉันพูดภาษาไทย แต่ต้องการคำอธิบายภาษาอังกฤษ"
  ↓
[AI in Thai]
"เข้าใจค่ะ! คุณสามารถพูดภาษาไทย
 แต่ฉันจะสร้างคำอธิบายเป็นภาษาอังกฤษให้

 เริ่มได้เลยค่ะ - บอกเกี่ยวกับบ้านของคุณ"

[Agent describes in Thai]
  ↓
[AI generates English description]
"I've created an English description:

'Luxury 3-bedroom pool villa in Patong Beach.
Modern design with private pool and garden...'

[Property card shows English fields]
```

**Scenario 2: Agent uploads photos with Thai text in images**

```
[AI detects Thai text in photos (signage, documents)]
  ↓
[AI]
"I noticed some Thai text in the photos.
 Should I:
 • Include Thai details in the listing
 • Translate to English only
 • Show both languages

 What's your preference?"
```

### Translation Handling

**Property Fields in Multiple Languages:**

```
[Property creation]
  ↓
[AI]
"I've created the property in English.

 Want me to also create Thai/Russian/Chinese versions?
 I can auto-translate, but you can edit them."

[Buttons: "Yes, translate" | "No, just English" | "I'll translate manually"]
```

**Translation Review:**

```
[If agent chooses auto-translate]
  ↓
[AI generates translations]
  ↓
[Shows preview]
"Here's the Thai version:

 Title: วิลล่าพร้อมสระว่ายน้ำในปาตอง
 Description: วิลล่าหรู 3 ห้องนอนพร้อมสระว่ายน้ำส่วนตัว...

 [Edit translation] [Looks good]"
```

### UI Language vs Content Language

**System Design:**

```
UI Language: Agent's preference (Thai)
  → All system messages, buttons, labels in Thai

Content Language: Property description language (English)
  → Property titles, descriptions, amenities in English

Example:
┌────────────────────────────────┐
│ [Thai UI elements]             │
│ "สร้างรายการ" (Create listing) │
│                                │
│ [English content]              │
│ "Luxury Pool Villa in Patong"  │
│ "3 bedrooms, 2 bathrooms..."   │
└────────────────────────────────┘
```

### Handling Catalogue Translations

**Amenities in Multiple Languages:**

```
[Catalogue structure]
{
  "id": "am_int_air_conditioning",
  "translations": {
    "en": "Air Conditioning",
    "th": "เครื่องปรับอากาศ",
    "ru": "Кондиционер",
    "zh": "空调"
  }
}

[UI shows in agent's language]
[But property stores IDs, can display in any language]
```

### Right-to-Left (RTL) Considerations

**For future Arabic support:**
- Chat bubbles flip to right side
- Text input aligns right
- Property cards mirror layout

---

## Example Conversation Flows

### Flow 1: Agent Creates Villa Rental (Happy Path)

```
[AGENT opens chat, taps camera icon]
[AGENT takes 15 photos of villa]
[AGENT taps voice button and holds]
  ↓
[AGENT speaks] (0:45 voice note)
"This is a beautiful 3-bedroom pool villa in Patong.
It's about 250 square meters with a private pool,
nice garden, modern kitchen, all bedrooms have AC and
en-suite bathrooms. It's for long-term rent,
80,000 baht per month."
  ↓
[AGENT releases voice button]
  ↓
[UI shows] "📤 Uploading 15 photos..."
[UI shows] "🎤 Transcribing voice..."
  ↓
[AI MESSAGE] (5 seconds later)
"Thanks! I'm analyzing your villa..."
  ↓
[AI MESSAGE] (8 seconds later)
"I've created your listing! Here's what I found:

┌─────────────────────────────────────┐
│ 🏠 POOL VILLA IN PATONG       [95%] │
├─────────────────────────────────────┤
│ [Cover: Pool photo]                 │
│                                     │
│ TYPE & LOCATION                     │
│ ✓ Pool Villa                   95%  │
│ ✓ Patong, Phuket               92%  │
│                                     │
│ PHYSICAL DETAILS                    │
│ ✓ 3 Bedrooms                   90%  │
│ ✓ 3 Bathrooms (en-suite)       88%  │
│ ✓ 250 sqm living area          85%  │
│ ⚠ Land area not detected            │
│                                     │
│ PRICING                             │
│ ✓ Long-term rental             98%  │
│ ✓ 80,000 THB/month             98%  │
│                                     │
│ AMENITIES (9 detected)              │
│ ✓ Private pool, Garden              │
│ ✓ Modern kitchen                    │
│ ✓ Air conditioning (all rooms)      │
│ [View all] [Add more]               │
│                                     │
│ COMPLETION: 85% - Looking good!     │
├─────────────────────────────────────┤
│ [Save draft] [Add details] [Publish]│
└─────────────────────────────────────┘

Everything look correct?"

[AGENT MESSAGE]
"Looks great! But the land is 600 square meters"
  ↓
[AI MESSAGE]
"Perfect! Updated land area to 600 sqm.

✓ Land area: 600 sqm

Anything else to add or correct?"

[AGENT MESSAGE]
"Nope, publish it"
  ↓
[AI MESSAGE]
"🎉 Published!

Your villa is now live at:
bestays.com/properties/pool-villa-patong-xyz123

📊 Quick stats:
• 15 photos uploaded
• 9 amenities
• Listing score: 87% (Excellent)

Want me to:
• Share listing link 🔗
• Add another property ➕
• Done for now ✓"

[AGENT taps "Done for now"]
  ↓
[AI MESSAGE]
"Great work! I'll notify you when you get inquiries."

[Conversation ends]
```

---

### Flow 2: Agent Creates Business-for-Sale (Complex)

```
[AGENT MESSAGE]
"I need to list a restaurant for sale"
  ↓
[AI MESSAGE]
"I can help you list your restaurant business!

For business listings, I'll need:
• Photos of the restaurant
• Basic info (location, size, price)
• Business details (revenue, why selling, etc.)

Want to upload photos first?"

[AGENT taps "Upload photos"]
[AGENT uploads 12 photos: interior, kitchen, exterior, licenses]
  ↓
[AI MESSAGE] (analyzing...)
"I can see this is a restaurant in good condition.

What can you tell me about the business?
(Revenue, number of seats, licenses, etc.)

You can record a voice note or type:"

[AGENT taps voice button]
[AGENT speaks] (1:30 voice note)
"It's an Italian restaurant in Patong, been running
for 5 years. 80 seats, fully licensed. Annual revenue
around 6 million baht, profit about 2 million.
Owner wants to retire. Asking 8 million baht for the
business including all equipment, furniture, and the
remaining 7 years on the lease. Monthly rent is 80,000."
  ↓
[AI MESSAGE]
"Thanks for the details! Here's what I've prepared:

┌─────────────────────────────────────┐
│ 🍝 ITALIAN RESTAURANT - PATONG      │
├─────────────────────────────────────┤
│ [Cover: Restaurant interior]        │
│                                     │
│ BUSINESS TYPE                       │
│ ✓ Restaurant (Italian)         95%  │
│ ✓ Patong, Phuket               98%  │
│                                     │
│ SALE DETAILS                        │
│ ✓ Asking price: 8,000,000 THB  98%  │
│ ✓ Established: 5 years         95%  │
│ ✓ Fully licensed               90%  │
│                                     │
│ BUSINESS METRICS                    │
│ ✓ Annual revenue: 6,000,000 THB     │
│ ✓ Annual profit: 2,000,000 THB      │
│ ✓ Capacity: 80 seats                │
│                                     │
│ WHAT'S INCLUDED                     │
│ ✓ All equipment & furniture         │
│ ✓ Remaining lease (7 years)         │
│ ✓ Monthly rent: 80,000 THB          │
│                                     │
│ REASON FOR SALE                     │
│ ✓ Owner retirement                  │
│                                     │
│ ⚠ MISSING INFO                      │
│ • Number of employees?              │
│ • Training period included?         │
│ • Seasonal business?                │
│                                     │
│ COMPLETION: 75%                     │
├─────────────────────────────────────┤
│ [Save draft] [Add details] [Publish]│
└─────────────────────────────────────┘

Want to add the missing details or publish as-is?"

[AGENT MESSAGE]
"5 employees, they'll stay. 2 weeks training included.
Not seasonal, busy all year."
  ↓
[AI MESSAGE]
"Excellent! Updated:

✓ 5 employees (staying with business)
✓ Training: 2 weeks included
✓ Not seasonal (year-round business)

Completion: 92% - Excellent!

Should I add these details to the description too?"

[AGENT MESSAGE]
"Yes, and publish"
  ↓
[AI MESSAGE]
"🎉 Published!

Your restaurant listing is live:
bestays.com/businesses/italian-restaurant-patong-xyz456

📊 Listing quality: 92% (Excellent)
💰 ROI: 25% (I calculated this from profit/price)

Pro tip: Business listings get more inquiries when
you add:
• Monthly expenses breakdown
• Recent tax documents (private, only to verified buyers)
• Photos of licenses

Want to add these now or later?"

[AGENT MESSAGE]
"Later"
  ↓
[AI MESSAGE]
"No problem! I'll remind you.

Good luck with the sale! 🍝"
```

---

### Flow 3: Agent Corrects Extracted Data (Error Handling)

```
[AGENT uploads 8 photos + types]
"4 bedroom villa, Kata beach, 12M baht"
  ↓
[AI MESSAGE] (analyzing...)
"I've analyzed your property:

┌─────────────────────────────────────┐
│ 🏡 VILLA IN KATA BEACH              │
├─────────────────────────────────────┤
│ TYPE & LOCATION                     │
│ ✓ Villa (not pool villa)       88%  │
│ ✓ Kata, Phuket                 95%  │
│                                     │
│ DETAILS                             │
│ ✓ 4 Bedrooms                   95%  │
│ ⚠ 2 Bathrooms                  55%  │ ← Low confidence
│ ⚠ 180 sqm                      60%  │ ← Estimated
│ ✗ No pool detected                  │
│                                     │
│ PRICING                             │
│ ✓ Sale: 12,000,000 THB         98%  │
└─────────────────────────────────────┘

I'm uncertain about bathrooms and size. Can you confirm?"

[AGENT MESSAGE]
"It's actually 3 bathrooms, 220 sqm, and it DOES have a pool"
  ↓
[AI MESSAGE]
"Thanks for correcting! Updated:

• Bathrooms: 2 → 3 ✓
• Living area: 180 sqm → 220 sqm ✓
• Added: Private pool ✓

Since it has a pool, should I change the type to
'Pool Villa'?"

[AGENT MESSAGE]
"Yes"
  ↓
[AI MESSAGE]
"Done! Updated to Pool Villa.

[Shows updated property card]

┌─────────────────────────────────────┐
│ 🏊 POOL VILLA IN KATA BEACH         │
├─────────────────────────────────────┤
│ ✓ Pool Villa                   98%  │ ← Updated
│ ✓ 4 Bedrooms                        │
│ ✓ 3 Bathrooms                       │ ← Corrected
│ ✓ 220 sqm                           │ ← Corrected
│ ✓ Private pool                      │ ← Added
│ ✓ Sale: 12,000,000 THB              │
│                                     │
│ COMPLETION: 78%                     │
└─────────────────────────────────────┘

Looking better! Anything else to fix?"

[AGENT MESSAGE]
"The pool is 10x4 meters"
  ↓
[AI MESSAGE]
"Great detail! Added pool dimensions (10m x 4m).

Should I mention this in the description?
'Features a spacious 10m x 4m private pool'"

[AGENT MESSAGE]
"Yes, sounds good"
  ↓
[AI MESSAGE]
"✓ Updated description

Ready to publish?"

[AGENT taps "Publish"]
  ↓
[AI MESSAGE]
"🎉 Published! Despite some initial confusion,
we got there!

Your listing: bestays.com/properties/pool-villa-kata-xyz789"
```

---

### Flow 4: Agent Adds More Photos Later (Incremental Update)

```
[AGENT opens existing draft property]
  ↓
[AI MESSAGE]
"Welcome back! You were working on:

┌─────────────────────────────────────┐
│ Modern Condo in Sukhumvit           │
│ Status: Draft                       │
│ Last edited: 2 days ago             │
│                                     │
│ ⚠ Only 3 photos uploaded            │
│ ⚠ Missing amenities                 │
│                                     │
│ [Continue editing →]                │
└─────────────────────────────────────┘

What would you like to do?"

[AGENT MESSAGE]
"I have more photos"
  ↓
[AI MESSAGE]
"Great! Upload away - I'll add them to your condo listing."

[AGENT uploads 8 more photos: gym, pool, lobby, parking]
  ↓
[AI MESSAGE] (analyzing new photos...)
"Added 8 photos! (Total: 11)

I noticed some building amenities in the new photos:
• Gym / fitness center
• Swimming pool (communal)
• Modern lobby
• Covered parking

Should I add these to amenities?"

[AGENT MESSAGE]
"Yes add them"
  ↓
[AI MESSAGE]
"✓ Added 4 building amenities

I also re-analyzed all 11 photos and noticed:
• Sky lounge/rooftop area
• Security desk/24h security

Add these too?"

[AGENT MESSAGE]
"Yes, and also has a sauna"
  ↓
[AI MESSAGE]
"Perfect! Added:
✓ Sky lounge
✓ 24h security
✓ Sauna

[Shows updated property card]
Amenities: 12 (was 5)
Photos: 11 (was 3)
Completion: 88% ↑ (was 65%)

Anything else to add?"

[AGENT MESSAGE]
"Publish it"
  ↓
[AI MESSAGE]
"🎉 Published!

The new photos and amenities really improved your listing!

📊 Quality score: 88%
📷 11 photos (recommended minimum: 5) ✓
🏷️ 12 amenities"
```

---

## Message Schemas

### Message Types

```typescript
// Base message structure
interface ChatMessage {
  id: string;
  conversation_id: string;
  sender: 'agent' | 'ai';
  timestamp: string;
  type: 'text' | 'property_card' | 'system' | 'action_required';
  content: MessageContent;
  metadata?: MessageMetadata;
}

// Text message
interface TextMessage extends ChatMessage {
  type: 'text';
  content: {
    text: string;
    attachments?: Attachment[];
  };
}

// Property card message (shows extracted property)
interface PropertyCardMessage extends ChatMessage {
  type: 'property_card';
  content: {
    property_id: string;
    property_draft: PropertyDraft;
    confidence_score: number;
    fields: FieldConfidence[];
    actions: Action[];
  };
}

// System message (status updates)
interface SystemMessage extends ChatMessage {
  type: 'system';
  content: {
    message: string;
    status: 'processing' | 'success' | 'error' | 'warning';
    progress?: number; // 0-100
  };
}

// Action required message
interface ActionRequiredMessage extends ChatMessage {
  type: 'action_required';
  content: {
    message: string;
    fields_needed: RequiredField[];
    quick_actions: QuickAction[];
  };
}
```

### Property Draft Structure

```typescript
interface PropertyDraft {
  id: string;
  status: 'creating' | 'draft' | 'ready' | 'published';

  // Core fields
  title?: string;
  short_description?: string;
  description?: string;
  property_type?: string; // catalogue ID

  // Location
  location_lat?: number;
  location_lng?: number;
  location_details?: {
    region?: string;
    district?: string;
    sub_district?: string;
    location_advantages?: string[]; // catalogue IDs
  };

  // Physical specs
  physical_specs?: {
    rooms?: {
      bedrooms?: number;
      bathrooms?: number;
      living_rooms?: number;
      kitchens?: number;
      // ... other room types
    };
    dimensions?: {
      total_area?: { value: number; unit: string };
      living_area?: { value: number; unit: string };
      land_area?: { value: number; unit: string };
    };
    building_specs?: {
      floors?: number;
      year_built?: number;
      condition?: string; // catalogue ID
      furnished?: string; // catalogue ID
    };
  };

  // Amenities (catalogue IDs)
  amenities_interior?: string[];
  amenities_exterior?: string[];
  amenities_building?: string[];
  utilities?: string[];

  // Pricing (depends on transaction type)
  transaction_types?: ('sale' | 'rent' | 'lease' | 'business' | 'investment')[];
  pricing?: {
    sale_price?: number;
    rent_price_monthly?: number;
    lease_price_monthly?: number;
    business_sale_price?: number;
    currency?: string;
  };

  // Media
  images?: PropertyImage[];
  cover_image_id?: string;

  // Metadata
  confidence_scores?: Record<string, number>; // field -> confidence
  completion_percentage?: number;
  created_at: string;
  updated_at: string;
  agent_id: string;
}
```

### Field Confidence

```typescript
interface FieldConfidence {
  field: string; // e.g., "physical_specs.rooms.bedrooms"
  value: any;
  confidence: number; // 0-100
  source: 'image' | 'voice' | 'text' | 'manual' | 'inferred';
  needs_verification: boolean;
}

// Example
{
  field: "physical_specs.rooms.bathrooms",
  value: 2,
  confidence: 60,
  source: "image",
  needs_verification: true
}
```

### Attachment Structure

```typescript
interface Attachment {
  id: string;
  type: 'image' | 'voice' | 'document';
  url: string;
  thumbnail_url?: string;
  metadata: {
    filename: string;
    size: number; // bytes
    mime_type: string;
    duration?: number; // for voice, in seconds
    dimensions?: { width: number; height: number }; // for images
  };
  upload_status: 'pending' | 'uploading' | 'completed' | 'failed';
  upload_progress?: number; // 0-100

  // AI analysis results (for images)
  analysis?: {
    detected_room_type?: string; // bedroom, bathroom, kitchen, pool, exterior
    detected_amenities?: string[];
    detected_features?: string[];
    confidence?: number;
  };
}
```

### Quick Action Buttons

```typescript
interface QuickAction {
  id: string;
  label: string;
  action_type: 'navigate' | 'update_field' | 'open_modal' | 'send_message';
  icon?: string;
  style?: 'primary' | 'secondary' | 'danger';

  // For 'update_field' actions
  field?: string;
  value?: any;

  // For 'send_message' actions
  message?: string;

  // For 'open_modal' actions
  modal_component?: string;
  modal_props?: Record<string, any>;
}

// Example quick actions
[
  {
    id: "publish",
    label: "Publish",
    action_type: "navigate",
    icon: "check",
    style: "primary"
  },
  {
    id: "add_price",
    label: "Add pricing",
    action_type: "open_modal",
    icon: "currency",
    style: "secondary",
    modal_component: "PricingModal",
    modal_props: { property_id: "123" }
  },
  {
    id: "correct_bedrooms",
    label: "Actually 4 bedrooms",
    action_type: "update_field",
    field: "physical_specs.rooms.bedrooms",
    value: 4
  }
]
```

### Required Field Prompt

```typescript
interface RequiredField {
  field: string;
  label: string;
  description?: string;
  required: boolean;
  current_value?: any;
  confidence?: number;
  input_type: 'text' | 'number' | 'select' | 'multiselect' | 'location' | 'price';
  options?: Array<{ value: string; label: string }>; // for select
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
  };
}

// Example
{
  field: "pricing.sale_price",
  label: "Sale Price",
  description: "Asking price for the property",
  required: true,
  current_value: null,
  input_type: "price",
  validation: {
    min: 0
  }
}
```

### Voice Transcription

```typescript
interface VoiceTranscription {
  id: string;
  audio_url: string;
  transcript: string;
  language: string; // ISO code
  confidence: number;
  duration: number; // seconds

  // Extracted structured data
  extracted_data?: {
    property_type?: string;
    location?: string;
    bedrooms?: number;
    bathrooms?: number;
    price?: { amount: number; currency: string; type: string };
    amenities?: string[];
    description_fragments?: string[];
  };

  // Allow editing
  edited?: boolean;
  original_transcript?: string;
}
```

### AI Processing Status

```typescript
interface ProcessingStatus {
  status: 'queued' | 'processing' | 'completed' | 'failed';
  steps: ProcessingStep[];
  current_step?: string;
  progress: number; // 0-100
  estimated_time_remaining?: number; // seconds
  error?: {
    code: string;
    message: string;
    retryable: boolean;
  };
}

interface ProcessingStep {
  id: string;
  name: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  result?: any;
}

// Example
{
  status: 'processing',
  steps: [
    { id: 'upload', name: 'Uploading images', status: 'completed', progress: 100 },
    { id: 'analyze', name: 'Analyzing photos', status: 'processing', progress: 45 },
    { id: 'extract', name: 'Extracting data', status: 'pending', progress: 0 },
    { id: 'generate', name: 'Generating description', status: 'pending', progress: 0 }
  ],
  current_step: 'analyze',
  progress: 35,
  estimated_time_remaining: 8
}
```

---

## State Machine

### Property Creation States

```
┌─────────────────────────────────────────────────────────┐
│                  PROPERTY CREATION                      │
│                    STATE MACHINE                        │
└─────────────────────────────────────────────────────────┘

States:
  • INITIAL
  • UPLOADING
  • ANALYZING
  • DRAFT
  • INCOMPLETE
  • READY
  • PUBLISHING
  • PUBLISHED
  • FAILED
  • ARCHIVED

Transitions:

┌─────────┐
│ INITIAL │ (Agent starts conversation)
└────┬────┘
     │ upload_files OR record_voice OR type_description
     ↓
┌────────────┐
│ UPLOADING  │ (Files uploading to server)
└─────┬──────┘
      │ upload_complete
      ↓
┌────────────┐
│ ANALYZING  │ (AI extracting data)
└─────┬──────┘
      │ extraction_complete
      ↓
┌─────────┐
│  DRAFT  │ (Property card shown for review)
└────┬────┘
     │
     ├─→ agent_confirms → [Is complete?]
     │                      │
     │                      ├─→ YES → READY
     │                      └─→ NO → INCOMPLETE
     │
     ├─→ agent_makes_correction → DRAFT (loop)
     │
     ├─→ agent_adds_more_photos → ANALYZING
     │
     └─→ agent_saves_draft → DRAFT (persisted)

┌────────────┐
│ INCOMPLETE │ (Missing required fields)
└─────┬──────┘
      │ agent_adds_required_fields
      ↓
┌─────────┐
│  READY  │ (All required fields present)
└────┬────┘
     │ agent_publishes
     ↓
┌────────────┐
│ PUBLISHING │ (Creating database records)
└─────┬──────┘
      │ publish_complete
      ↓
┌───────────┐
│ PUBLISHED │ (Live on site)
└─────┬─────┘
      │
      ├─→ agent_edits → DRAFT
      ├─→ agent_archives → ARCHIVED
      └─→ auto_sold/rented → ARCHIVED

┌──────────┐
│  FAILED  │ (Error occurred)
└────┬─────┘
     │ agent_retries
     ├─→ ANALYZING (retry extraction)
     └─→ INITIAL (start over)

┌──────────┐
│ ARCHIVED │ (No longer active)
└──────────┘
```

### State Details

```typescript
enum PropertyState {
  INITIAL = 'initial',
  UPLOADING = 'uploading',
  ANALYZING = 'analyzing',
  DRAFT = 'draft',
  INCOMPLETE = 'incomplete',
  READY = 'ready',
  PUBLISHING = 'publishing',
  PUBLISHED = 'published',
  FAILED = 'failed',
  ARCHIVED = 'archived'
}

interface PropertyStateMachine {
  current_state: PropertyState;
  previous_state?: PropertyState;
  state_history: StateHistoryEntry[];

  // State metadata
  metadata: {
    upload_progress?: number;
    analysis_progress?: number;
    error?: Error;
    completion_percentage?: number;
    missing_fields?: string[];
  };
}

interface StateHistoryEntry {
  state: PropertyState;
  timestamp: string;
  triggered_by: 'agent' | 'system' | 'ai';
  action?: string;
}
```

### State Transitions & Validations

```typescript
// Required fields by state
const STATE_REQUIREMENTS = {
  [PropertyState.READY]: {
    required_fields: [
      'property_type',
      'location_details.region',
      'location_details.district',
      'pricing', // At least one price
      'images' // At least one image
    ],
    min_completion: 70
  },

  [PropertyState.PUBLISHED]: {
    required_fields: [
      'title',
      'description',
      'property_type',
      'location_details.region',
      'location_details.district',
      'pricing',
      'images',
      'contact_info'
    ],
    min_completion: 70
  }
};

// State transition guards
function canTransitionTo(
  from: PropertyState,
  to: PropertyState,
  property: PropertyDraft
): boolean {
  // Check if transition is allowed
  const allowed_transitions = {
    [PropertyState.INITIAL]: [PropertyState.UPLOADING],
    [PropertyState.UPLOADING]: [PropertyState.ANALYZING, PropertyState.FAILED],
    [PropertyState.ANALYZING]: [PropertyState.DRAFT, PropertyState.FAILED],
    [PropertyState.DRAFT]: [
      PropertyState.INCOMPLETE,
      PropertyState.READY,
      PropertyState.ANALYZING, // Re-analyze
      PropertyState.DRAFT // Stay in draft
    ],
    [PropertyState.INCOMPLETE]: [PropertyState.DRAFT, PropertyState.READY],
    [PropertyState.READY]: [PropertyState.PUBLISHING, PropertyState.DRAFT],
    [PropertyState.PUBLISHING]: [PropertyState.PUBLISHED, PropertyState.FAILED],
    [PropertyState.PUBLISHED]: [PropertyState.DRAFT, PropertyState.ARCHIVED],
    [PropertyState.FAILED]: [PropertyState.INITIAL, PropertyState.ANALYZING],
    [PropertyState.ARCHIVED]: [] // Terminal state
  };

  if (!allowed_transitions[from]?.includes(to)) {
    return false;
  }

  // Check state-specific requirements
  if (to === PropertyState.READY || to === PropertyState.PUBLISHED) {
    return validateRequirements(property, STATE_REQUIREMENTS[to]);
  }

  return true;
}

function validateRequirements(
  property: PropertyDraft,
  requirements: typeof STATE_REQUIREMENTS[PropertyState]
): boolean {
  // Check required fields
  for (const field of requirements.required_fields) {
    if (!getNestedValue(property, field)) {
      return false;
    }
  }

  // Check minimum completion
  if (property.completion_percentage < requirements.min_completion) {
    return false;
  }

  return true;
}
```

### Conversation State

```typescript
interface ConversationState {
  conversation_id: string;
  agent_id: string;

  // Current focus
  active_property_id?: string;
  property_state?: PropertyStateMachine;

  // Conversation context
  intent: ConversationIntent;
  context: {
    last_mentioned_property?: string;
    awaiting_response_for?: string;
    unresolved_corrections?: string[];
    suggested_amenities?: string[];
  };

  // Session info
  created_at: string;
  last_activity: string;
  message_count: number;
}

enum ConversationIntent {
  CREATE_PROPERTY = 'create_property',
  EDIT_PROPERTY = 'edit_property',
  VIEW_PROPERTY = 'view_property',
  SEARCH_PROPERTIES = 'search_properties',
  GENERAL_QUESTION = 'general_question'
}
```

---

## MVP Scope

### Phase 1: MVP (Weeks 1-4)

**Core Features:**

✅ **Must Have (MVP)**
- Single-message property creation (photos + voice/text)
- AI extraction of basic fields:
  - Property type (15 types)
  - Location (region + district)
  - Bedrooms, bathrooms
  - Basic dimensions (living area, land area)
  - Price (one type: sale OR rent)
- Property card preview with confidence indicators
- Natural language corrections (simple)
- Auto-detected amenities (top 20 most common)
- Draft saving and resuming
- Mobile camera integration
- Voice input (native device transcription)
- Publish to listings
- English only
- Single transaction type per property (sale OR rent, not both)

⚠️ **Should Have (Post-MVP, Week 5-6)**
- Multi-language support (Thai, Russian, Chinese)
- Advanced amenity selection (all 165 options)
- Complex corrections (policies, detailed specs)
- Multi-transaction support (sale + lease)
- Business and investment property types
- Bulk photo upload improvements
- Offline capability
- Property analytics (views, inquiries)
- Listing optimization suggestions

🔮 **Could Have (Future)**
- AI-generated descriptions (beyond extraction)
- Automatic photo categorization and sorting
- Virtual tour integration
- Market price suggestions
- Duplicate property detection
- Batch property creation
- Import from other platforms
- Video upload and analysis

❌ **Won't Have (Out of Scope)**
- Full CMS replacement (form still exists for power users)
- Automatic translation of content
- Blockchain/NFT property tokens
- VR/AR property tours
- IoT smart home integration

### MVP User Stories

**US-CHAT-001: Create Property via Photos + Voice**
```
As a real estate agent
I want to upload photos and record a voice description
So that I can create property listings in under 5 minutes

Acceptance Criteria:
- Agent can upload 10-20 photos at once
- Agent can record voice note (up to 2 minutes)
- AI extracts: property type, location, beds, baths, price
- Property card shows extracted data with confidence scores
- Agent can publish in 3 taps
```

**US-CHAT-002: Review and Correct Extracted Data**
```
As a real estate agent
I want to quickly fix incorrect extracted data
So that I don't have to re-explain obvious things

Acceptance Criteria:
- Property card highlights uncertain fields (< 70% confidence)
- Agent can correct via natural language ("Actually 4 bedrooms")
- AI updates specific fields without re-extracting everything
- Agent sees what changed
```

**US-CHAT-003: Save Draft and Return Later**
```
As a real estate agent
I want to save incomplete listings as drafts
So that I can finish them when I have more information

Acceptance Criteria:
- Auto-save every message
- Agent can explicitly save draft
- Draft shows what's missing
- Agent can resume from draft in chat
- Shows "Last edited X ago"
```

**US-CHAT-004: Mobile Camera Integration**
```
As a real estate agent on-site
I want to take photos directly in the chat
So that I don't have to switch between apps

Acceptance Criteria:
- Camera opens from chat interface
- Can take multiple photos in sequence
- Shows photo count (e.g., "8 photos taken")
- Can review and delete before sending
- Works on iOS and Android
```

**US-CHAT-005: Voice Input on Mobile**
```
As a real estate agent
I want to describe properties using voice
So that I can create listings while walking around

Acceptance Criteria:
- Large, accessible voice button
- Shows recording duration
- Shows waveform animation
- Auto-transcribes when released
- Agent can edit transcription if wrong
```

### MVP Data Model (Simplified)

```typescript
// MVP Property Draft (subset of full schema)
interface PropertyDraftMVP {
  id: string;
  status: 'draft' | 'published';

  // Basic info
  title?: string;
  description?: string;
  property_type: string; // Only: villa, house, condo, apartment, land

  // Location (required)
  location_details: {
    region: string; // e.g., "Phuket"
    district: string; // e.g., "Patong"
  };

  // Physical (optional)
  physical_specs?: {
    rooms?: {
      bedrooms?: number;
      bathrooms?: number;
    };
    dimensions?: {
      living_area?: { value: number; unit: 'sqm' };
      land_area?: { value: number; unit: 'sqm' };
    };
  };

  // Pricing (one type only in MVP)
  transaction_type: 'sale' | 'rent'; // Single type
  price: {
    amount: number;
    currency: 'THB';
    period?: 'monthly' | 'yearly'; // For rent only
  };

  // Amenities (limited to 20 most common)
  amenities: string[]; // IDs from catalogue

  // Media (required at least 1)
  images: PropertyImage[];
  cover_image_id?: string;

  // Confidence scores
  confidence_scores: Record<string, number>;
  completion_percentage: number;

  // Metadata
  agent_id: string;
  created_at: string;
  updated_at: string;
}
```

### MVP Technical Stack

**Backend:**
- FastAPI endpoints:
  - `POST /api/v2/chat/properties` - Create property from chat
  - `PATCH /api/v2/chat/properties/{id}` - Update from corrections
  - `GET /api/v2/chat/properties/{id}` - Get draft
  - `POST /api/v2/chat/properties/{id}/publish` - Publish
- LangChain integration for:
  - Image analysis (GPT-4 Vision or Claude Vision)
  - Voice transcription (Whisper or OpenRouter)
  - Data extraction (structured output)
- PostgreSQL for storage
- R2 for images

**Frontend:**
- Svelte 5 chat component
- TanStack Query for state management
- Native device APIs:
  - Camera (getUserMedia)
  - Microphone (MediaRecorder)
  - File picker
- Mobile-optimized UI

**AI/LLM:**
- OpenRouter with:
  - Vision model for images (GPT-4 Vision or Claude Sonnet)
  - Text model for extraction (Claude or GPT-4)
- Prompt templates for:
  - Property type detection
  - Field extraction
  - Natural language correction parsing

### MVP Development Timeline

**Week 1: Foundation**
- [ ] Design database schema (simplified)
- [ ] Create API endpoints (CRUD)
- [ ] Set up LangChain integration
- [ ] Create basic chat UI

**Week 2: AI Integration**
- [ ] Implement image upload and analysis
- [ ] Implement voice transcription
- [ ] Implement data extraction
- [ ] Test extraction accuracy

**Week 3: Chat UX**
- [ ] Implement property card component
- [ ] Implement confidence indicators
- [ ] Implement natural language corrections
- [ ] Mobile camera integration

**Week 4: Polish & Testing**
- [ ] Draft saving/loading
- [ ] Error handling
- [ ] End-to-end testing
- [ ] Performance optimization

---

## Integration Strategy

### Chat vs Form Relationship

**Hybrid Approach:**

```
┌─────────────────────────────────────────┐
│         PROPERTY CREATION               │
├─────────────────────────────────────────┤
│                                         │
│  QUICK CREATE (Chat)                    │
│  • Photos + voice/text                  │
│  • AI extraction                        │
│  • 3-5 minutes                          │
│  • 70-80% complete                      │
│  ↓                                      │
│  [Publish] OR [Refine in form]         │
│  ↓                                      │
│  DETAILED EDIT (Form)                   │
│  • All 165 amenities                    │
│  • Complex policies                     │
│  • SEO optimization                     │
│  • 100% complete                        │
│                                         │
└─────────────────────────────────────────┘
```

**When to Use What:**

| Scenario | Tool | Reason |
|----------|------|--------|
| Agent on-site with photos | **Chat** | Fastest, mobile-friendly |
| Agent wants quick listing | **Chat** | Get to 70% in 3-5 min |
| Agent has complex property (business) | **Chat → Form** | Start chat, finish in form |
| Agent is power user | **Form** | Direct access to all fields |
| Agent wants to browse all amenities | **Form** | Better for 165+ options |
| Agent wants to edit SEO | **Form** | Chat doesn't expose SEO |

### Transition Between Chat and Form

**Chat → Form:**

```
[In chat after property creation]

[AI MESSAGE]
"Your villa is 85% complete! Want to:

• Publish now (looks good) ✓
• Add more details in form 📋
• Keep editing in chat 💬"

[Agent taps "Add more details in form"]
  ↓
[Opens form with pre-filled data]
[Form shows banner]
"Loaded from chat: Villa in Patong
 [✓] Basic info complete
 [✓] Photos uploaded (15)
 [ ] Add more amenities (8/165)
 [ ] Set policies
 [ ] Optimize SEO"
```

**Form → Chat:**

```
[In form]
[Agent clicks "Quick edit in chat" button]
  ↓
[Opens chat]

[AI MESSAGE]
"Hey! I can help you edit:

Beachfront Pool Villa in Patong

What would you like to change?"

[Agent can make conversational edits]
```

### Data Synchronization

**Real-time Sync:**

```typescript
// When agent edits in form, chat reflects changes
PropertyEditForm.on('save', async (property) => {
  await chatService.syncProperty(property.id);
  // Chat conversation updates with new data
});

// When agent edits in chat, form reflects changes
ChatService.on('property_updated', async (propertyId) => {
  if (formIsOpen(propertyId)) {
    await propertyForm.reload(propertyId);
    showNotification("Property updated in chat");
  }
});
```

**Conflict Resolution:**

```
[If agent edits same property in both chat and form simultaneously]

[System detects conflict]
  ↓
[Shows modal in both interfaces]

"⚠ Conflict Detected

This property was edited in:
• Chat: Changed bedrooms to 4 (2 mins ago)
• Form: Changed price to 14M (1 min ago)

Which changes should we keep?"

[Options:]
• Keep chat changes (discard form)
• Keep form changes (discard chat)
• Keep both (merge - recommended)
• Review manually

[Recommended: Merge]
  ↓
[System merges non-conflicting changes]
[Shows diff for conflicts]
```

### Entry Points

**Multiple Ways to Start:**

```
1. Dashboard → "Create Property" button
   → Opens chat interface

2. Mobile → FAB (Floating Action Button)
   → Opens chat with camera prompt

3. Dashboard → "Quick Create (Chat)" vs "Full Form"
   → Agent chooses upfront

4. Property List → "Edit" button
   → Opens modal: "Edit in chat or form?"

5. Navigation → "Chat Assistant"
   → General chat, can initiate property creation
```

**Recommended Default:**
- **Mobile:** Always open chat (mobile-optimized)
- **Desktop:** Show choice (chat vs form)
- **Returning to draft:** Open in original mode (if started in chat, return to chat)

### Feature Availability Matrix

| Feature | Chat | Form | Notes |
|---------|------|------|-------|
| Basic info (type, location, beds, price) | ✅ | ✅ | Chat is faster |
| Photo upload | ✅ | ✅ | Chat supports camera |
| Voice description | ✅ | ❌ | Chat only |
| AI extraction | ✅ | ❌ | Chat only |
| All 165 amenities | ⚠️ | ✅ | Chat shows detected + search |
| Complex policies | ⚠️ | ✅ | Chat can set basic policies |
| SEO metadata | ❌ | ✅ | Form only |
| Translations | ⚠️ | ✅ | Chat can request, form can edit |
| Multi-transaction (sale+lease) | ⚠️ | ✅ | MVP: Chat single only |
| Batch operations | ❌ | ✅ | Form only |

Legend:
- ✅ Fully supported
- ⚠️ Partially supported (limited or simplified)
- ❌ Not supported

---

## Conclusion

This chat-as-CMS design prioritizes:

1. **Speed**: 15-30 minutes → 3-5 minutes
2. **Ease**: Natural conversation over forms
3. **Mobile**: Camera + voice first
4. **Intelligence**: AI does 80% of work
5. **Flexibility**: Chat for speed, form for depth
6. **Trust**: Show confidence, allow corrections

**Key Success Metrics:**

- ⏱️ Average time to publish: < 5 minutes
- 🎯 AI extraction accuracy: > 80%
- 📱 Mobile usage: > 70%
- ✅ Agent satisfaction: > 4.5/5
- 📈 Properties created per agent: +50%

**Next Steps:**

1. Review this design with stakeholders
2. Create user story for MVP (US-CHAT-001 to US-CHAT-005)
3. Build technical proof-of-concept (image analysis + extraction)
4. Design Figma mockups based on wireframes
5. Begin MVP implementation (Week 1-4)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-06
**Status:** Draft - Ready for Review
**Next Review:** After stakeholder feedback

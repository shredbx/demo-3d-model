# Property Chat CMS - Critical Questions & Decisions Required

**Project:** Bestays RealEstate Platform
**Feature:** LLM-Powered Chat-as-CMS for Property Creation
**Date:** 2025-11-06
**Status:** Awaiting Stakeholder Input

---

## Purpose

This document contains **critical questions that require stakeholder decisions** before proceeding with implementation. These decisions will significantly impact:
- MVP scope and timeline
- API costs and budget allocation
- Technical complexity
- User experience
- Integration requirements

**Please review and provide answers to enable the team to proceed with User Story creation and implementation planning.**

---

## 1. Budget & Cost Management

### Q1.1: What is the monthly API budget for OpenRouter?

**Context:**
- Estimated cost per property: $0.04-0.08 (text + images optimized)
- Higher for full multimodal (text + images + voice): $0.08-0.10
- Average agent might create 10-20 properties per month
- Initial pilot with 10 agents = ~$8-16/month
- Scale to 50 agents = ~$40-80/month

**Options:**

| **Budget Level** | **Monthly Cost** | **Capacity**                    | **Recommended Scope**          |
| ---------------- | ---------------- | ------------------------------- | ------------------------------ |
| **A) Conservative** | $50/month     | ~500 properties (text+images)   | Text-only MVP, add images in Phase 2 |
| **B) Standard**     | $200/month    | ~2,500 properties (text+images) | Full multimodal MVP            |
| **C) Aggressive**   | $500/month    | ~6,000 properties (text+images) | Full multimodal + experimentation |

**Your Answer:**
```
[ ] Option A - $50/month (conservative, text-only MVP)
[ ] Option B - $200/month (standard, full multimodal)
[ ] Option C - $500/month (aggressive, with buffer)
[ ] Other: $_____/month
```

---

### Q1.2: Should we implement per-agent cost caps?

**Context:**
- Prevent individual agents from accidentally incurring high costs
- Useful for beta testing phase
- Could limit legitimate usage

**Options:**
- **A) Yes, hard cap:** $5/agent/day (reject requests after limit)
- **B) Yes, soft cap:** $10/agent/day (warning but allow)
- **C) No caps:** Trust agents, monitor globally

**Your Answer:**
```
[ ] Option A - Hard cap at $____ per agent per day
[ ] Option B - Soft cap at $____ per agent per day with warning
[ ] Option C - No per-agent caps
```

---

## 2. MVP Scope & Features

### Q2.1: Should MVP include image processing, or start with text-only?

**Context:**

**Text-Only MVP (Faster, Cheaper):**
- ✅ Ship in 6 weeks (vs 11 weeks)
- ✅ $0.025 per property (vs $0.04-0.08)
- ✅ Simpler to debug and optimize
- ❌ Lower accuracy (no visual verification)
- ❌ Agents still need to manually enter room counts

**Text + Images MVP (Better UX):**
- ✅ 85%+ accuracy (images confirm text)
- ✅ Room counting from photos (major time saver)
- ✅ Condition assessment (excellent/good/fair)
- ❌ 11 weeks to ship (5 weeks longer)
- ❌ 2-3x higher cost per property
- ❌ More complex error handling

**Recommended:** Text + Images (better validates product value, justifies cost)

**Your Answer:**
```
[ ] Option A - Text-only MVP (faster, cheaper, validate concept)
[ ] Option B - Text + Images MVP (better UX, higher accuracy)
[ ] Option C - Hybrid: Text MVP first, add images in Week 6
```

---

### Q2.2: Should MVP include voice transcription?

**Context:**

**Without Voice (Standard):**
- Agents type or paste descriptions
- 95% of use cases covered
- Desktop + mobile work fine

**With Voice (Mobile-Optimized):**
- ✅ Faster on mobile (primary device for agents)
- ✅ Especially useful for Thai language
- ✅ More natural for field agents
- ❌ +1-2 weeks development time
- ❌ +$0.01-0.02 per property cost
- ❌ iOS Safari audio recording quirks

**Recommended:** Add voice in Week 6 (after validating text+images)

**Your Answer:**
```
[ ] Option A - No voice in MVP (text + images only)
[ ] Option B - Include voice from Day 1
[ ] Option C - Add voice in Phase 2 (post-MVP)
```

---

### Q2.3: Multi-turn conversations: MVP or Phase 2?

**Context:**

**Multi-Turn** = Agent can refine property via follow-up messages:
```
Agent: "It has 2.5 bathrooms and 250 sqm living area"
AI: ✓ Updated! Confidence now 95%
```

**Without Multi-Turn (Single-Shot):**
- Agent uploads → AI extracts → Agent clicks "Edit in Form" to fix
- Simpler backend (no conversation state management)
- -2 weeks development time

**With Multi-Turn (Conversational):**
- More natural UX (especially on mobile)
- Better for iterative refinement
- Requires conversation memory (Redis sessions)

**Recommended:** Include multi-turn (it's core to "chat-as-CMS" value prop)

**Your Answer:**
```
[ ] Option A - Single-shot MVP (AI extracts once, then form editor)
[ ] Option B - Multi-turn MVP (conversational refinement)
```

---

## 3. Language & Localization

### Q3.1: Which languages must be supported in MVP?

**Context:**
- Most agents in Thailand speak Thai + English
- Property descriptions often mix languages
- Claude Sonnet 4.5 handles Thai well
- Whisper supports Thai transcription

**Options:**

| **Option** | **Languages**      | **Complexity** | **Accuracy Impact** |
| ---------- | ------------------ | -------------- | ------------------- |
| **A**      | English only       | Low            | High (simpler)      |
| **B**      | Thai + English     | Medium         | Medium (LLM handles both) |
| **C**      | Thai + English + Chinese | High     | Lower (more edge cases) |

**Your Answer:**
```
[ ] Option A - English only (simplify MVP, add Thai in Phase 2)
[ ] Option B - Thai + English (required for most agents)
[ ] Option C - Thai + English + Chinese
[ ] Other: ________________
```

---

### Q3.2: Should AI auto-translate property descriptions?

**Context:**
- Many properties need bilingual listings (Thai for locals, English for expats)
- LLM can generate translations during extraction
- Adds ~500 output tokens = ~$0.01 per property

**Your Answer:**
```
[ ] Yes, auto-translate to [Thai/English/both] during extraction
[ ] No, agents will translate manually if needed
[ ] Add in Phase 2
```

---

## 4. Integration & Dependencies

### Q4.1: Status of existing chat module - suitable for property integration?

**Context:**
- Feature requires integrating property creation into chat
- Existing chat may need refactoring to support:
  - File uploads (images, audio)
  - Structured responses (property preview cards)
  - Multi-turn context management

**Please assess:**
```
Current chat module status:
[ ] Ready to use - minimal changes needed
[ ] Needs refactoring - 2-3 weeks work
[ ] Needs complete rebuild - 4-6 weeks
[ ] Not sure - requires investigation

Action Required:
[ ] Proceed with current chat (accept refactoring risk)
[ ] Investigate chat module first (create US-00X for assessment)
[ ] Build property chat as standalone, integrate later
```

---

### Q4.2: Image storage - Cloudflare R2 ready?

**Context:**
- Feature requires storing uploaded property images
- Proposed: Cloudflare R2 (S3-compatible, cheaper egress)
- Alternative: AWS S3, local storage (not recommended for production)

**Your Answer:**
```
[ ] Cloudflare R2 account already set up (provide credentials)
[ ] Need to create Cloudflare R2 account (team will handle)
[ ] Use alternative: ________________
```

---

### Q4.3: PostgreSQL pgvector extension - installed on production VPS?

**Context:**
- RAG amenity matching requires pgvector extension
- Not installed by default on most PostgreSQL instances
- Docker container can include it, but VPS needs it too

**Your Answer:**
```
[ ] Yes, pgvector already installed on production VPS
[ ] No, need to install (team can handle)
[ ] Not sure - requires investigation
[ ] We use Docker for production (pgvector in container)
```

---

## 5. Performance & Scale

### Q5.1: How many agents will use this feature?

**Context:**
- Helps estimate load, cost, infrastructure needs
- Pilot typically starts with 5-10 agents, then scales

**Your Answer:**
```
Beta (first 3 months): _____ agents
Year 1: _____ agents
Year 2: _____ agents (if successful)
```

---

### Q5.2: Acceptable processing time for property extraction?

**Context:**

| **Processing Time** | **User Perception**   | **Technical Feasibility** |
| ------------------- | --------------------- | ------------------------- |
| 1-2 seconds         | Instant               | Impossible (API latency)  |
| 3-5 seconds         | Fast                  | Achievable (text-only)    |
| 5-10 seconds        | Acceptable            | Achievable (text+images)  |
| 10-20 seconds       | Slow but tolerable    | Multimodal with many images |
| 20+ seconds         | Too slow              | Needs optimization        |

**Your Answer:**
```
[ ] Option A - Must be under 5 seconds (text-only MVP)
[ ] Option B - 5-10 seconds acceptable (text + images)
[ ] Option C - Up to 15 seconds ok (full multimodal)
[ ] Option D - No hard requirement (just show progress indicator)
```

---

### Q5.3: Peak concurrent property creations?

**Context:**
- Helps size infrastructure (API rate limits, Redis, DB connections)
- Example: 50 agents, 20% active at once = 10 concurrent

**Your Answer:**
```
Expected peak: _____ concurrent property creations
(e.g., "10 concurrent", "50 concurrent", "not sure")
```

---

## 6. User Experience & Design

### Q6.1: Should agents be able to edit AI-extracted data before saving?

**Context:**

**Option A - Always Preview First (Recommended):**
- AI extracts → Show preview card → Agent reviews → Agent clicks "Publish"
- Safer (no accidental incorrect data)
- Builds trust in AI

**Option B - Auto-Save as Draft:**
- AI extracts → Auto-save as draft → Agent can edit later
- Faster (fewer clicks)
- Risk: Agents forget to review

**Your Answer:**
```
[ ] Option A - Always show preview, require manual publish
[ ] Option B - Auto-save as draft, agent can review later
[ ] Option C - Let agent choose (setting/preference)
```

---

### Q6.2: Mobile vs Desktop priority?

**Context:**
- Agents often take property photos on-site (mobile)
- Desktop better for detailed editing

**Your Answer:**
```
Primary device for property creation:
[ ] Mobile (70%+ of usage) - optimize chat interface for touch
[ ] Desktop (70%+ of usage) - optimize form/keyboard shortcuts
[ ] 50/50 split - design for both equally
[ ] Not sure - track analytics first
```

---

## 7. Data & Privacy

### Q7.1: Should property extraction history be kept?

**Context:**
- `property_extractions` table stores:
  - Original images, voice recordings
  - Full LLM responses
  - Confidence scores, processing metadata

**Purposes:**
- Debugging (why did AI extract wrong data?)
- Analytics (improve prompts over time)
- Audit trail (who created what, when)

**Privacy concerns:**
- Voice recordings may contain personal info
- Original images stored twice (R2 + extraction history)

**Your Answer:**
```
[ ] Yes, keep full extraction history (recommended)
[ ] Yes, but delete voice recordings after 30 days
[ ] Yes, but anonymize/hash sensitive data
[ ] No, delete extraction history after property published
```

---

### Q7.2: GDPR/Privacy compliance for agent-uploaded data?

**Context:**
- Agents may accidentally upload personal data (client faces, IDs, etc.)
- LLM providers (OpenAI, Anthropic) process images

**Your Answer:**
```
[ ] Agents trained not to upload personal data (policy enforcement)
[ ] Implement client-side image scanning (detect faces, blur)
[ ] Use OpenRouter zero-retention models only
[ ] No special requirements (internal tool only)
[ ] Requires legal review before proceeding
```

---

## 8. Error Handling & Reliability

### Q8.1: What happens if OpenRouter API is down?

**Context:**
- OpenRouter typically 99.9% uptime, but outages happen
- Options for fallback

**Your Answer:**
```
[ ] Option A - Fail gracefully, show "Try again later" message
[ ] Option B - Fallback to direct OpenAI API (requires separate key)
[ ] Option C - Queue requests, process when API returns
[ ] Option D - Allow manual form entry as backup
```

---

### Q8.2: How to handle low-confidence extractions?

**Context:**
- Some properties will have < 70% confidence (unclear photos, vague descriptions)

**Options:**

| **Approach**          | **Trade-off**                                 |
| --------------------- | --------------------------------------------- |
| **A) Allow publish**  | Fast, but risk of incorrect data              |
| **B) Require review** | Safer, but slows down agents                  |
| **C) Prompt for more info** | Best accuracy, but adds extra chat turns |

**Your Answer:**
```
[ ] Option A - Allow publish with warning ("Low confidence: please review")
[ ] Option B - Block publish if confidence < 70%, force manual review
[ ] Option C - AI automatically asks clarifying questions
```

---

## 9. Testing & Validation

### Q9.1: How should we validate extraction accuracy?

**Context:**
- Need to measure if AI correctly extracts property data
- Manual QA is gold standard but time-consuming

**Options:**
- **A) Manual QA:** Team reviews 50 random properties per week
- **B) Agent feedback:** Agents rate AI accuracy after each creation
- **C) Automated:** Compare AI extraction to final published data (reveals edits)
- **D) Hybrid:** A + C

**Your Answer:**
```
[ ] Option A - Manual QA by team
[ ] Option B - Agent feedback ratings
[ ] Option C - Automated edit distance tracking
[ ] Option D - Hybrid (manual QA + automated tracking)
```

---

### Q9.2: Beta testing scope

**Context:**
- Pilot with small group before full rollout
- Gather feedback, iterate quickly

**Your Answer:**
```
Beta duration: _____ weeks
Beta cohort size: _____ agents
Beta selection criteria:
[ ] Tech-savvy agents (early adopters)
[ ] High-volume agents (stress test)
[ ] Mix of mobile/desktop users
[ ] Agents in specific location: ________________
```

---

## 10. Deployment & Rollout

### Q10.1: Deployment strategy

**Context:**

**Option A - Feature Flag:**
- Deploy to production, enable for beta agents only
- Can quickly disable if issues arise
- Requires feature flag system

**Option B - Separate Staging:**
- Beta agents use staging environment
- Zero risk to production
- More complex (maintain 2 environments)

**Option C - Gradual Rollout:**
- Week 1: 5 agents
- Week 2: 10 agents
- Week 3: 25 agents
- Week 4: All agents

**Your Answer:**
```
[ ] Option A - Feature flag in production
[ ] Option B - Separate staging environment
[ ] Option C - Gradual rollout (specify schedule: ________________)
```

---

### Q10.2: Rollback plan if MVP fails?

**Context:**
- What if agents hate it, or costs spiral?

**Your Answer:**
```
[ ] Keep old property creation form as backup (don't delete)
[ ] If beta NPS < 3.0, pause rollout and reassess
[ ] If cost > $____ per day, pause and optimize
[ ] Other: ________________
```

---

## 11. Dynamic Property Types (Post-MVP)

### Q11.1: When should dynamic property types be implemented?

**Context:**
- **Static schema MVP:** 5 fixed property types (rental, sale, lease, business, investment)
- **Dynamic types:** Admins can create new types via UI (e.g., "agricultural land", "commercial warehouse")

**Recommendation:** Ship static schema in MVP, defer dynamic types to Phase 2 (see `04_DYNAMIC_SCHEMA_ARCHITECTURE_ANALYSIS.md`)

**Your Answer:**
```
[ ] Option A - MVP only (static 5 types, add dynamic in Phase 2)
[ ] Option B - Build dynamic types from Day 1 (adds 3-4 weeks)
[ ] Option C - Depends on beta feedback
```

---

### Q11.2: If dynamic types needed, what's the priority?

**Context:**
- Dynamic types enable:
  1. Admin creates new property type (e.g., "Boat Marina")
  2. Defines custom fields (e.g., "number_of_boat_slips")
  3. LLM extracts custom fields automatically

**Your Answer:**
```
Priority for dynamic types:
[ ] High - We have 10+ property types we need to support
[ ] Medium - Nice to have in Year 1
[ ] Low - Current 5 types cover 95%+ of properties
[ ] Not needed - Static schema is sufficient
```

---

## 12. Documentation & Training

### Q12.1: Agent training requirements

**Context:**
- Agents need to learn new chat-based workflow
- Options for training

**Your Answer:**
```
[ ] Option A - Video tutorial (5 min) + written guide
[ ] Option B - Live training session (30 min Zoom call)
[ ] Option C - In-app onboarding (interactive tutorial)
[ ] Option D - Agents are tech-savvy, just provide docs
```

---

### Q12.2: Support during beta

**Context:**
- Agents will have questions and issues

**Your Answer:**
```
Support channel during beta:
[ ] Dedicated Slack channel
[ ] Email: support@bestays.com
[ ] In-app chat support
[ ] Schedule: 9am-6pm Bangkok time, Mon-Fri
[ ] Other: ________________
```

---

## 13. Success Definition

### Q13.1: What defines a successful MVP?

**Context:**
- Need clear success criteria to evaluate if feature should be scaled or killed

**Please rank priorities (1 = highest, 5 = lowest):**
```
___ Time savings (15-30 min → 3-5 min)
___ Agent adoption rate (60%+ of agents use it)
___ Agent satisfaction (NPS > 4.5/5)
___ Cost efficiency (< $0.10 per property)
___ Extraction accuracy (> 80% correct)
```

**Minimum acceptable values:**
```
Time savings: Reduce to under _____ minutes
Adoption rate: At least _____% of agents use it
Satisfaction: NPS must be at least _____/5
Cost: Must be under $_____ per property
Accuracy: At least _____% of fields extracted correctly
```

---

### Q13.2: When should we decide to scale or kill the feature?

**Context:**
- After beta, evaluate if worth scaling to all agents

**Your Answer:**
```
Decision point: After _____ weeks of beta

Scale to all agents if:
[ ] 70%+ of beta agents use it regularly
[ ] NPS > 4.0/5
[ ] Cost within budget
[ ] Fewer than 5 critical bugs

Kill feature if:
[ ] < 30% adoption
[ ] NPS < 3.0/5
[ ] Cost 2x over budget
[ ] Agents prefer old form

Pivot/Iterate if: (middle ground)
________________
```

---

## 14. Dependencies on Other Work

### Q14.1: Does this feature depend on other in-progress work?

**Context:**
- Check if any parallel work could conflict or enable this feature

**Your Answer:**
```
Blocking dependencies (must finish before we start):
[ ] None - can start immediately
[ ] US-001 (Login flow) - must complete first
[ ] Property schema migration - must complete first
[ ] Chat refactoring - must complete first
[ ] Other: ________________

Parallel work (should coordinate):
[ ] Frontend redesign - align on UI components
[ ] API gateway refactor - align on auth
[ ] Database migration - coordinate schema changes
[ ] Other: ________________
```

---

### Q14.2: Should this work block or inform US-001 (Login)?

**Context:**
- CLAUDE.md says: "Don't block US-001 (Login) - inform architecture, not block it"
- Property chat CMS is a separate feature

**Your Answer:**
```
[ ] US-001 and Property Chat CMS are independent (proceed in parallel)
[ ] Property Chat CMS should wait until US-001 complete
[ ] US-001 should incorporate auth requirements from Property Chat CMS
[ ] Coordinate on shared components (e.g., chat UI, file uploads)
```

---

## 15. Open Questions & Unknowns

### Q15.1: Are there any requirements or constraints we haven't captured?

**Your Input:**
```
Business requirements:
-

Technical constraints:
-

Regulatory/Legal requirements:
-

Other considerations:
-
```

---

### Q15.2: Stakeholder availability for iterative feedback

**Context:**
- Agile approach requires frequent check-ins (weekly or bi-weekly)
- Need stakeholder availability to review progress, approve scope changes

**Your Answer:**
```
Primary stakeholder: ________________
Availability for weekly check-ins: [Yes/No]
Preferred communication channel: [Slack/Email/Zoom/Other]
Decision-making authority: [Can approve scope changes: Yes/No]
```

---

## 16. Final Sign-Off

**Please review all questions above and provide answers.**

Once answered, the team will:
1. Create User Story US-002 (or appropriate number) for Property Chat CMS
2. Update architecture documents based on decisions
3. Generate task breakdown and sprint plan
4. Proceed with Week 1 implementation (API + basic chat UI)

**Completed By:**
```
Name: ________________
Role: ________________
Date: ________________
Signature: ________________
```

**Next Steps After Sign-Off:**
- [ ] Team reviews answers and clarifies any ambiguities
- [ ] Update `00_FINAL_SOLUTION.md` with decisions
- [ ] Create User Story US-002 in `.sdlc-workflow/user-stories/`
- [ ] Begin Sprint 1 planning (Weeks 1-2 deliverables)
- [ ] Set up OpenRouter API account and test integration
- [ ] Provision Cloudflare R2 bucket (if not already done)

---

**Document Status:** 📝 Awaiting Stakeholder Input
**Last Updated:** 2025-11-06
**Related Documents:**
- `00_FINAL_SOLUTION.md` - Architecture and roadmap
- `01_LLM_ARCHITECTURE_ANALYSIS.md` - Detailed LLM design
- `02_RAG_ARCHITECTURE_ANALYSIS.md` - Amenity matching design
- `03_OPENROUTER_INTEGRATION_ANALYSIS.md` - API integration design
- `04_DYNAMIC_SCHEMA_ARCHITECTURE_ANALYSIS.md` - Dynamic types (Phase 2)
- `05_CHAT_UX_DESIGN_ANALYSIS.md` - Conversational UX design

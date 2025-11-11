# Properties User Stories

This directory contains user stories related to property management features.

---

## Stories

### US-016: Property Migration Strategy Design

**Status:** Design Phase
**Priority:** High
**File:** `US-016-property-migration-design.md`

**Summary:**
Comprehensive migration strategy for transferring property data from the old NextJS/Supabase application to our new FastAPI/PostgreSQL stack. Adopts the battle-tested Property2 (V2) schema with adaptations for our company-owned business model.

**Key Decisions:**
- Adopt V2 schema (150+ amenities, 6 languages, production-ready)
- Adapt for company model (remove agent-centric, add employee accountability)
- Dual-phase approach (export/import for dev, direct connection for production)
- 4-week implementation timeline

**Deliverables:**
1. Migration architecture document with system diagrams
2. Updated schema design for company model
3. Python script templates (4 scripts)
4. Implementation plan with testing strategy
5. Production migration checklist

**Next Steps:**
- Review design document
- Approve schema adaptations
- Schedule implementation (4 weeks)
- Setup Supabase test environment

---

## Related Documentation

- **Property Schema Research:** `../../.specs/PROPERTY_SCHEMA_*.md`
- **Milestone 01:** `../../.specs/MILESTONE_01_WEBSITE_REPLICATION.md`
- **Story Template:** `../TEMPLATE.md`
- **SDLC Workflow:** `../../GIT_WORKFLOW.md`

---

**Last Updated:** 2025-11-06

# CTO Specialist Consultation Brief

## Context
TASK-013: Property V2 Schema Migration for US-023 (Property Import & Display with Localization)

We are designing the foundational database schema for a rental property platform with multi-language support (EN/TH, with future expansion). This is a "measure twice, cut once" decision that will impact:
- Query performance for 10k+ properties
- Localization strategy (EN/TH now, more languages later)
- Future features (semantic search with pgvector, AI suggestions)
- Maintenance complexity

## Current Situation
- Basic property model exists (title, description, is_published)
- Old system has comprehensive Property V2 schema with 5 JSONB fields
- US-021 (i18n infrastructure) is COMPLETE
- Need to migrate to rich property schema with localization

## Proposed Architecture: Hybrid Localization

**Layer 1: Properties Table (Queryable Data)**
- Dedicated columns: rent_price, transaction_type, property_type
- JSONB fields: physical_specs, location_details, amenities, policies, contact_info
- B-tree indexes for exact matches, GIN indexes for JSONB queries

**Layer 2: property_translations Table (Localized Text)**
- Normalized structure: (property_id, locale, field, value)
- Translatable fields: title, description, location names, policies text

**Layer 3: Frontend Dictionaries (Static Labels)**
- Amenity IDs → Labels (translated in frontend)
- Field labels (translated in frontend)

## Questions for CTO

1. **Industry Alignment:**
   - Is this hybrid approach aligned with real estate industry standards?
   - How do Airbnb, Booking.com, Zillow, MLS platforms handle multi-language property data at scale?
   - Any patterns from these platforms we should adopt or avoid?

2. **Strategic Data Model:**
   - JSONB vs relational vs hybrid - is our approach optimal for property data?
   - What are the irreversible decisions here that will be hard to change later?
   - Should we store property amenities as IDs (requires frontend translation) or full objects with translations?

3. **Scalability & Future-Proofing:**
   - Will this architecture scale to 10k-100k properties efficiently?
   - pgvector for semantic search: Should we store separate embeddings per locale or single multilingual embedding?
   - Should we add empty pgvector columns now or defer to later migration?

4. **Trade-offs Analysis:**
   - What are the main risks with this approach?
   - When should we revisit this architecture (what metrics/thresholds)?
   - Any alternative approaches we should consider?

5. **Real Estate Specific:**
   - Are there property-specific query patterns we're missing?
   - Should we plan for map-based search (geospatial queries) in the schema design?
   - How important is full-text search vs semantic search for property descriptions?

## Deliverable
Strategic analysis and recommendations for the property schema architecture decision.

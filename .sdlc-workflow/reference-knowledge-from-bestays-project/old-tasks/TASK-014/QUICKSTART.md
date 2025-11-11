# TASK-014 Quick Start Guide

## Import Sample Properties in 3 Steps

### Step 1: Start Development Environment

```bash
make dev
```

Wait for all services to start (server, frontend, postgres, redis).

### Step 2: Seed Amenities (Required)

```bash
make shell-server
python app/scripts/seed_amenities_policies.py
exit
```

This populates the amenities and policies tables required for properties.

### Step 3: Import Sample Properties

```bash
make shell-server
python app/scripts/import_sample_properties.py
exit
```

This will import 5 sample properties.

## Verify Import

### Check via API

```bash
# List all properties
curl http://localhost:8011/api/v1/properties | jq

# Count properties
curl http://localhost:8011/api/v1/properties | jq '.pagination.total'

# Get first property ID and view details
curl http://localhost:8011/api/v1/properties | jq '.properties[0].id'
curl http://localhost:8011/api/v1/properties/{property-id} | jq
```

### Check via Browser

1. Open API Docs: http://localhost:8011/docs
2. Navigate to `/properties` GET endpoint
3. Click "Try it out" → "Execute"
4. View the 5 imported properties

### Check via Database

```bash
make shell-db
SELECT COUNT(*) FROM properties;
SELECT title, rent_price/100 as price_thb, property_type FROM properties LIMIT 5;
\q
```

## Expected Result

You should see **5 properties**:

1. Quiet 1-Bedroom Home Near Secret Beach (฿35,000)
2. Modern 2-Bedroom Villa with Sea View (฿45,000)
3. Luxury 3-Bedroom Beachfront Villa (฿75,000)
4. Cozy 1-Bedroom Apartment in Baan Tai (฿28,000)
5. Spacious 2-Bedroom House with Garden (฿38,000)

## Troubleshooting

### "service not running"
```bash
make down
make dev
```

### "connection refused"
```bash
# Check server logs
make logs

# Verify server is running on port 8011
curl http://localhost:8011/health
```

### "amenity not found"
```bash
# Seed amenities first
make shell-server
python app/scripts/seed_amenities_policies.py
```

### Want to import more properties?

```bash
make shell-server
python app/scripts/import_sample_properties.py --limit 10
```

## Next Steps

With properties imported, you can now:
- Build frontend property list component (TASK-015)
- Test property detail views
- Develop property search/filtering
- Create property card components

## Files Location

- **Sample Data Script:** `apps/server/app/scripts/import_sample_properties.py`
- **Web Scraping Script:** `apps/server/app/scripts/import_live_properties.py`
- **Documentation:** `apps/server/app/scripts/README_PROPERTY_IMPORT.md`
- **Report:** `.claude/tasks/TASK-014/implementation/property-import-script-report.md`

# Property Schema - Example Data

Real-world examples of properties using the Property2 (V2) schema.

---

## Example 1: Luxury Beach Villa (Phuket)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Beachfront Luxury Villa with Infinity Pool",
  "description": "Stunning 4-bedroom oceanfront villa on Bang Tao Beach with private infinity pool, modern architecture, and 24/7 security. Perfect for families or luxury vacation rentals.",
  "title_deed": "JJ-2023-B001234",
  
  "transaction_type": "rent",
  "property_type": "pool-villa",
  "sale_price": null,
  "rent_price": 3500000,
  "lease_price": null,
  "currency": "THB",
  "price_per_unit": 35000,
  
  "physical_specs": {
    "rooms": {
      "bedrooms": 4,
      "bathrooms": 3,
      "living_rooms": 2,
      "kitchens": 1,
      "dining_rooms": 1,
      "offices": 1,
      "storage_rooms": 1,
      "maid_rooms": 1,
      "guest_rooms": 0
    },
    "dimensions": {
      "total_area": { "value": 450, "unit": "sqm" },
      "living_area": { "value": 350, "unit": "sqm" },
      "usable_area": { "value": 380, "unit": "sqm" },
      "land_area": { "value": 1200, "unit": "sqm" },
      "balcony_area": { "value": 80, "unit": "sqm" },
      "floor_area": { "value": 450, "unit": "sqm" }
    },
    "building_specs": {
      "floors": 2,
      "floor_level": 0,
      "parking_spaces": 3,
      "year_built": 2018,
      "last_renovated": 2023,
      "facing_direction": "southwest",
      "condition": "excellent",
      "furnished": "fully"
    }
  },
  
  "location_details": {
    "region": "Phuket",
    "district": "Thalang",
    "sub_district": "Bang Tao",
    "location_advantages": [
      "beachfront",
      "private_beach_access",
      "sea_view",
      "gated_community",
      "near_airport",
      "near_marina",
      "near_beach_club"
    ],
    "location_advantages_additional": [
      "5-star resort nearby",
      "International school within 5km"
    ],
    "proximity": {
      "beach_distance": { "value": 0, "unit": "m" },
      "road_access": "private_road_access",
      "nearest_town": { "name": "Bang Tao Town", "distance": 3, "unit": "km" }
    },
    "transportation": {
      "nearest_airport": { "name": "Phuket International Airport", "distance": 35, "unit": "km" },
      "public_transport": ["Taxi", "Private car service"],
      "parking_available": true
    }
  },
  
  "amenities": {
    "interior": [
      { "id": "air_conditioning", "name": "Air Conditioning", "icon": "Snowflake" },
      { "id": "european_kitchen", "name": "European Kitchen", "icon": "UtensilsCrossed" },
      { "id": "dishwasher", "name": "Dishwasher", "icon": "Utensils" },
      { "id": "smart_tv", "name": "Smart TV", "icon": "Tv" },
      { "id": "sound_system", "name": "Sound System", "icon": "Volume2" },
      { "id": "cinema_room", "name": "Cinema Room", "icon": "Film" },
      { "id": "walk_in_closet", "name": "Walk-in Closet", "icon": "Shirt" },
      { "id": "high_ceilings", "name": "High Ceilings", "icon": "ArrowUp" }
    ],
    "exterior": [
      { "id": "private_pool", "name": "Private Swimming Pool", "icon": "Waves" },
      { "id": "infinity_pool", "name": "Infinity Pool", "icon": "Waves" },
      { "id": "pool_heating", "name": "Pool Heating", "icon": "Thermometer" },
      { "id": "jacuzzi_outdoor", "name": "Outdoor Jacuzzi", "icon": "Bath" },
      { "id": "terrace", "name": "Terrace", "icon": "Mountain" },
      { "id": "rooftop_terrace", "name": "Rooftop Terrace", "icon": "ArrowUp" },
      { "id": "outdoor_dining", "name": "Outdoor Dining Area", "icon": "UtensilsCrossed" },
      { "id": "bbq_area", "name": "BBQ Area", "icon": "Flame" },
      { "id": "tropical_garden", "name": "Tropical Garden", "icon": "Palmtree" },
      { "id": "garage", "name": "Garage", "icon": "Warehouse" }
    ],
    "building": [
      { "id": "24h_security", "name": "24h Security", "icon": "Shield" },
      { "id": "security_cameras", "name": "Security Cameras", "icon": "Camera" },
      { "id": "gated_community", "name": "Gated Community", "icon": "Lock" },
      { "id": "concierge", "name": "Concierge Service", "icon": "User" }
    ],
    "neighborhood": [],
    "special_features": [
      { "id": "beachfront_location", "name": "Beachfront Location", "icon": "Waves" },
      { "id": "ocean_view", "name": "Ocean View", "icon": "Binoculars" }
    ],
    "utilities": [
      { "id": "fiber_internet", "name": "Fiber Internet", "icon": "Wifi" },
      { "id": "water_supply", "name": "Water Supply", "icon": "Droplets" },
      { "id": "electricity", "name": "Electricity", "icon": "Zap" },
      { "id": "backup_generator", "name": "Backup Generator", "icon": "Battery" },
      { "id": "hot_water", "name": "Hot Water", "icon": "Thermometer" }
    ]
  },
  
  "policies": {
    "inclusions": [
      "WiFi Internet",
      "Cable TV",
      "Air Conditioning",
      "Weekly Housekeeping",
      "Pool Maintenance",
      "24/7 Security",
      "Parking"
    ],
    "restrictions": [
      "No smoking inside",
      "No large parties without notice",
      "No permanent pets"
    ],
    "house_rules": [
      "Quiet hours: 10 PM - 8 AM",
      "Guest registration required",
      "Pool rules must be followed",
      "Check-out 11 AM, Check-in 2 PM"
    ],
    "additional_fees": [
      {
        "type": "Service charge",
        "amount": 350000,
        "currency": "THB",
        "frequency": "monthly",
        "description": "Utilities, maintenance, housekeeping"
      },
      {
        "type": "Cleaning fee",
        "amount": 50000,
        "currency": "THB",
        "frequency": "one_time",
        "description": "Final cleaning at checkout"
      }
    ],
    "lease_terms": {
      "minimum_lease_months": 1,
      "maximum_lease_months": 12,
      "notice_period_days": 14,
      "security_deposit_months": 1,
      "advance_payment_months": 1
    }
  },
  
  "contact_info": {
    "agent_name": "Somchai Kongsoon",
    "agent_phone": "+66-82-123-4567",
    "agent_email": "somchai@bestays.app",
    "agent_line_id": "somchai.property",
    "agent_whatsapp_id": "+66821234567",
    "agency_name": "Phuket Luxury Villas",
    "languages_spoken": ["English", "Thai", "Russian", "Chinese"],
    "preferred_contact": "whatsapp",
    "availability_hours": "24h"
  },
  
  "cover_image": {
    "url": "https://cdn.bestays.app/properties/550e8400/cover.jpg",
    "color": "#87CEEB",
    "path": "properties/550e8400/cover.jpg",
    "alt": "Beachfront villa with infinity pool at sunset"
  },
  
  "images": [
    { "url": "https://cdn.bestays.app/properties/550e8400/img1.jpg", "color": "#...", "path": "...", "alt": "Master bedroom" },
    { "url": "https://cdn.bestays.app/properties/550e8400/img2.jpg", "color": "#...", "path": "...", "alt": "Living room" },
    { "url": "https://cdn.bestays.app/properties/550e8400/img3.jpg", "color": "#...", "path": "...", "alt": "Pool area" }
  ],
  
  "virtual_tour_url": "https://virtualtour.bestays.app/phuket-villa-001",
  "video_url": "https://youtube.com/watch?v=abc123",
  
  "ownership_type": "freehold",
  "foreign_quota": true,
  
  "is_published": true,
  "is_featured": true,
  "listing_priority": 100,
  
  "rental_yield": 8.5,
  "price_trend": "rising",
  
  "seo_title": "Luxury Beachfront Villa Phuket - 4BR Pool House Bang Tao",
  "seo_description": "Stunning oceanfront villa in Phuket with private infinity pool, 4 bedrooms, modern design. Perfect for families and vacation rentals.",
  "tags": ["phuket", "villa", "beachfront", "luxury", "rental", "pool", "family"],
  
  "created_by": "user-123",
  "updated_by": "user-123",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-11-05T14:20:00Z",
  "deleted_at": null
}
```

---

## Example 2: Bangkok Condo Apartment (Sale)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "title": "Luxury High-Rise Condo Central Bangkok",
  "description": "Modern 2-bedroom condominium in prime Silom area. Close to BTS, shopping malls, and restaurants. Excellent investment property with strong rental history.",
  "title_deed": "BKK-2020-C005678",
  
  "transaction_type": "sale",
  "property_type": "condo",
  "sale_price": 6500000,
  "rent_price": null,
  "lease_price": null,
  "currency": "THB",
  "price_per_unit": 130000,
  
  "physical_specs": {
    "rooms": {
      "bedrooms": 2,
      "bathrooms": 2,
      "living_rooms": 1,
      "kitchens": 1,
      "dining_rooms": 0,
      "offices": 0,
      "storage_rooms": 1,
      "maid_rooms": 0,
      "guest_rooms": 0
    },
    "dimensions": {
      "total_area": { "value": 125, "unit": "sqm" },
      "living_area": { "value": 100, "unit": "sqm" },
      "usable_area": { "value": 110, "unit": "sqm" },
      "land_area": null,
      "balcony_area": { "value": 15, "unit": "sqm" },
      "floor_area": { "value": 125, "unit": "sqm" }
    },
    "building_specs": {
      "floors": 35,
      "floor_level": 25,
      "parking_spaces": 1,
      "year_built": 2015,
      "last_renovated": 2022,
      "facing_direction": "east",
      "condition": "excellent",
      "furnished": "partially"
    }
  },
  
  "location_details": {
    "region": "Bangkok",
    "district": "Silom",
    "sub_district": "Silom",
    "location_advantages": [
      "on_main_road",
      "near_bts",
      "near_shopping_mall",
      "near_cafes_restaurants",
      "near_hospital_clinic"
    ],
    "location_advantages_additional": [
      "Walking distance to nightlife",
      "Central business district"
    ],
    "proximity": {
      "beach_distance": null,
      "road_access": "on_main_road",
      "nearest_town": { "name": "Silom", "distance": 0.5, "unit": "km" }
    },
    "transportation": {
      "nearest_airport": { "name": "Suvarnabhumi Airport", "distance": 30, "unit": "km" },
      "public_transport": ["BTS Silom", "MRT Lumphini", "Buses"],
      "parking_available": true
    }
  },
  
  "amenities": {
    "interior": [
      { "id": "air_conditioning", "name": "Air Conditioning", "icon": "Snowflake" },
      { "id": "dishwasher", "name": "Dishwasher", "icon": "Utensils" },
      { "id": "smart_tv", "name": "Smart TV", "icon": "Tv" },
      { "id": "walk_in_closet", "name": "Walk-in Closet", "icon": "Shirt" }
    ],
    "exterior": [
      { "id": "balcony", "name": "Balcony", "icon": "Building" }
    ],
    "building": [
      { "id": "24h_security", "name": "24h Security", "icon": "Shield" },
      { "id": "elevator", "name": "Elevator", "icon": "ArrowUp" },
      { "id": "swimming_pool_shared", "name": "Swimming Pool", "icon": "Waves" },
      { "id": "fitness_center", "name": "Fitness Center", "icon": "Dumbbell" },
      { "id": "concierge", "name": "Concierge Service", "icon": "User" },
      { "id": "valet_parking", "name": "Valet Parking", "icon": "Car" }
    ],
    "neighborhood": [],
    "special_features": [],
    "utilities": [
      { "id": "fiber_internet", "name": "Fiber Internet", "icon": "Wifi" },
      { "id": "cable_tv", "name": "Cable TV", "icon": "Tv" },
      { "id": "water_supply", "name": "Water Supply", "icon": "Droplets" },
      { "id": "electricity", "name": "Electricity", "icon": "Zap" }
    ]
  },
  
  "policies": {
    "inclusions": [],
    "restrictions": [
      "No permanent pets",
      "Owner occupancy preferred"
    ],
    "house_rules": [],
    "additional_fees": [],
    "lease_terms": null
  },
  
  "contact_info": {
    "agent_name": "Niran Taksinee",
    "agent_phone": "+66-87-654-3210",
    "agent_email": "niran@bestays.app",
    "agent_line_id": "niran.realtor",
    "agent_whatsapp_id": "+66876543210",
    "agency_name": "Bangkok Properties Co.",
    "languages_spoken": ["English", "Thai", "German"],
    "preferred_contact": "phone",
    "availability_hours": "9am-5pm"
  },
  
  "cover_image": {
    "url": "https://cdn.bestays.app/properties/550e8400-2/cover.jpg",
    "color": "#F0E68C",
    "path": "properties/550e8400-2/cover.jpg",
    "alt": "Modern condo living room with city views"
  },
  
  "images": [
    { "url": "https://cdn.bestays.app/properties/550e8400-2/bedroom.jpg", "color": "#...", "path": "...", "alt": "Master bedroom" },
    { "url": "https://cdn.bestays.app/properties/550e8400-2/kitchen.jpg", "color": "#...", "path": "...", "alt": "Modern kitchen" },
    { "url": "https://cdn.bestays.app/properties/550e8400-2/balcony.jpg", "color": "#...", "path": "...", "alt": "Balcony city view" }
  ],
  
  "virtual_tour_url": null,
  "video_url": null,
  
  "ownership_type": "leasehold",
  "foreign_quota": true,
  
  "is_published": true,
  "is_featured": false,
  "listing_priority": 5,
  
  "rental_yield": 6.2,
  "price_trend": "stable",
  
  "seo_title": "2BR Condo Silom Bangkok - Luxury Apartment Investment",
  "seo_description": "Modern 2-bedroom condo in central Bangkok Silom. Near BTS, fully furnished, great investment opportunity.",
  "tags": ["bangkok", "condo", "silom", "sale", "investment", "bts"],
  
  "created_by": "user-456",
  "updated_by": "user-456",
  "created_at": "2025-02-20T09:15:00Z",
  "updated_at": "2025-10-30T16:45:00Z",
  "deleted_at": null
}
```

---

## Example 3: Chiang Mai Land (Development)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "title": "Development Land Chiang Mai - Mountain View",
  "description": "5-rai prime development land in Chiang Mai hills. Stunning mountain views, clean title, approved for residential development. Perfect for villa community or eco-resort project.",
  "title_deed": "CMU-2018-L009999",
  
  "transaction_type": "sale",
  "property_type": "land",
  "sale_price": 20000000,
  "rent_price": null,
  "lease_price": null,
  "currency": "THB",
  "price_per_unit": 250000,
  
  "physical_specs": {
    "rooms": null,
    "dimensions": {
      "total_area": { "value": 5, "unit": "rai" },
      "living_area": null,
      "usable_area": { "value": 5, "unit": "rai" },
      "land_area": { "value": 5, "unit": "rai" },
      "balcony_area": null,
      "floor_area": null
    },
    "building_specs": {
      "floors": null,
      "floor_level": null,
      "parking_spaces": null,
      "year_built": null,
      "last_renovated": null,
      "facing_direction": "south",
      "condition": null,
      "furnished": null
    }
  },
  
  "location_details": {
    "region": "Chiang Mai",
    "district": "Hang Dong",
    "sub_district": "Tha Sala",
    "location_advantages": [
      "mountain_view",
      "jungle_view",
      "near_hiking_trails",
      "near_national_park_waterfall",
      "quiet_cul_de_sac",
      "paved_road_access"
    ],
    "location_advantages_additional": [
      "Clear 3-month title",
      "Water source available",
      "Electricity access"
    ],
    "proximity": {
      "beach_distance": null,
      "road_access": "paved_road_access",
      "nearest_town": { "name": "Hang Dong", "distance": 8, "unit": "km" }
    },
    "transportation": {
      "nearest_airport": { "name": "Chiang Mai International Airport", "distance": 45, "unit": "km" },
      "public_transport": ["Songthaew"],
      "parking_available": true
    }
  },
  
  "amenities": {
    "interior": [],
    "exterior": [],
    "building": [],
    "neighborhood": [],
    "special_features": [
      { "id": "clean_title", "name": "Clean Title Deed", "icon": "CheckCircle" },
      { "id": "mountain_view", "name": "Mountain View", "icon": "Mountain" },
      { "id": "natural_landscape", "name": "Natural Landscape", "icon": "Trees" }
    ],
    "utilities": [
      { "id": "water_supply", "name": "Water Supply", "icon": "Droplets" },
      { "id": "electricity", "name": "Electricity", "icon": "Zap" }
    ]
  },
  
  "policies": {
    "inclusions": ["Clear 3-month title deed", "Marked boundaries"],
    "restrictions": [
      "Residential/eco-tourism development only",
      "Building height restricted to 3 stories"
    ],
    "house_rules": [],
    "additional_fees": [],
    "lease_terms": null
  },
  
  "contact_info": {
    "agent_name": "Pranee Lertpanya",
    "agent_phone": "+66-81-555-6666",
    "agent_email": "pranee@bestays.app",
    "agent_line_id": "pranee.development",
    "agent_whatsapp_id": "+66815556666",
    "agency_name": "Northern Thailand Development",
    "languages_spoken": ["English", "Thai"],
    "preferred_contact": "email",
    "availability_hours": "9am-5pm"
  },
  
  "cover_image": {
    "url": "https://cdn.bestays.app/properties/550e8400-3/cover.jpg",
    "color": "#228B22",
    "path": "properties/550e8400-3/cover.jpg",
    "alt": "5-rai development land with mountain views"
  },
  
  "images": [
    { "url": "https://cdn.bestays.app/properties/550e8400-3/landscape1.jpg", "color": "#...", "path": "...", "alt": "Land overview" },
    { "url": "https://cdn.bestays.app/properties/550e8400-3/mountain-view.jpg", "color": "#...", "path": "...", "alt": "Mountain vista" }
  ],
  
  "virtual_tour_url": null,
  "video_url": "https://youtube.com/watch?v=dev123",
  
  "ownership_type": "freehold",
  "foreign_quota": false,
  
  "is_published": true,
  "is_featured": false,
  "listing_priority": 2,
  
  "rental_yield": null,
  "price_trend": "rising",
  
  "seo_title": "5-Rai Land Chiang Mai - Development, Mountain View",
  "seo_description": "Prime 5-rai development land in Chiang Mai hills with mountain views. Clean title, approved for residential/resort development.",
  "tags": ["chiang-mai", "land", "development", "mountain-view", "investment"],
  
  "created_by": "user-789",
  "updated_by": "user-789",
  "created_at": "2025-03-10T11:20:00Z",
  "updated_at": "2025-11-04T10:10:00Z",
  "deleted_at": null
}
```

---

## Example 4: Commercial Office Space (Lease)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "title": "Office Space in Business Park - Ready to Move In",
  "description": "Professional office space in modern business park. 500 sqm with flexible layout, excellent natural lighting, meeting rooms, and full facilities. Ideal for tech startups and corporate offices.",
  "title_deed": null,
  
  "transaction_type": "lease",
  "property_type": "office",
  "sale_price": null,
  "rent_price": 500000,
  "lease_price": null,
  "currency": "THB",
  "price_per_unit": 1000,
  
  "physical_specs": {
    "rooms": {
      "bedrooms": 0,
      "bathrooms": 4,
      "living_rooms": 0,
      "kitchens": 1,
      "dining_rooms": 0,
      "offices": 1,
      "storage_rooms": 2,
      "maid_rooms": 0,
      "guest_rooms": 0
    },
    "dimensions": {
      "total_area": { "value": 500, "unit": "sqm" },
      "living_area": { "value": 500, "unit": "sqm" },
      "usable_area": { "value": 500, "unit": "sqm" },
      "land_area": null,
      "balcony_area": null,
      "floor_area": { "value": 500, "unit": "sqm" }
    },
    "building_specs": {
      "floors": 12,
      "floor_level": 8,
      "parking_spaces": 5,
      "year_built": 2019,
      "last_renovated": 2024,
      "facing_direction": "north",
      "condition": "excellent",
      "furnished": "partially"
    }
  },
  
  "location_details": {
    "region": "Bangkok",
    "district": "Rama 9",
    "sub_district": "Rama 9",
    "location_advantages": [
      "near_bts",
      "on_main_road",
      "near_shopping_mall",
      "gated_community",
      "near_hospital_clinic"
    ],
    "location_advantages_additional": [
      "Modern business park",
      "High-speed internet",
      "24/7 security"
    ],
    "proximity": {
      "beach_distance": null,
      "road_access": "on_main_road",
      "nearest_town": { "name": "Rama 9", "distance": 0.5, "unit": "km" }
    },
    "transportation": {
      "nearest_airport": { "name": "Suvarnabhumi Airport", "distance": 25, "unit": "km" },
      "public_transport": ["BTS Rama 9", "MRT Rama 9"],
      "parking_available": true
    }
  },
  
  "amenities": {
    "interior": [
      { "id": "air_conditioning", "name": "Air Conditioning", "icon": "Snowflake" },
      { "id": "high_ceilings", "name": "High Ceilings", "icon": "ArrowUp" }
    ],
    "exterior": [],
    "building": [
      { "id": "24h_security", "name": "24h Security", "icon": "Shield" },
      { "id": "elevator", "name": "Elevator", "icon": "ArrowUp" },
      { "id": "business_center", "name": "Business Center", "icon": "Building2" },
      { "id": "meeting_rooms", "name": "Meeting Rooms", "icon": "Users" },
      { "id": "cafe", "name": "On-site Cafe", "icon": "Coffee" },
      { "id": "valet_parking", "name": "Valet Parking", "icon": "Car" }
    ],
    "neighborhood": [],
    "special_features": [
      { "id": "flexible_layout", "name": "Flexible Floor Plan", "icon": "Layers" }
    ],
    "utilities": [
      { "id": "fiber_internet", "name": "Fiber Internet", "icon": "Wifi" },
      { "id": "water_supply", "name": "Water Supply", "icon": "Droplets" },
      { "id": "electricity", "name": "Electricity", "icon": "Zap" },
      { "id": "backup_generator", "name": "Backup Generator", "icon": "Battery" }
    ]
  },
  
  "policies": {
    "inclusions": [
      "Utilities",
      "Internet",
      "Security",
      "Building maintenance",
      "Access to common areas"
    ],
    "restrictions": [
      "Business use only",
      "No manufacturing"
    ],
    "house_rules": [
      "Operating hours 6 AM - 10 PM",
      "Parking reserved spaces assigned",
      "No alterations without landlord approval"
    ],
    "additional_fees": [
      {
        "type": "Service charge",
        "amount": 100000,
        "currency": "THB",
        "frequency": "monthly",
        "description": "Common area maintenance"
      }
    ],
    "lease_terms": {
      "minimum_lease_months": 12,
      "maximum_lease_months": 36,
      "notice_period_days": 60,
      "security_deposit_months": 2,
      "advance_payment_months": 1
    }
  },
  
  "contact_info": {
    "agent_name": "Aroon Siripradit",
    "agent_phone": "+66-85-777-8888",
    "agent_email": "aroon@bestays.app",
    "agent_line_id": "aroon.commercial",
    "agent_whatsapp_id": "+66857778888",
    "agency_name": "Bangkok Commercial Properties",
    "languages_spoken": ["English", "Thai", "Chinese"],
    "preferred_contact": "email",
    "availability_hours": "9am-5pm"
  },
  
  "cover_image": {
    "url": "https://cdn.bestays.app/properties/550e8400-4/cover.jpg",
    "color": "#C0C0C0",
    "path": "properties/550e8400-4/cover.jpg",
    "alt": "Modern office space with natural lighting"
  },
  
  "images": [
    { "url": "https://cdn.bestays.app/properties/550e8400-4/office.jpg", "color": "#...", "path": "...", "alt": "Open office layout" },
    { "url": "https://cdn.bestays.app/properties/550e8400-4/meeting.jpg", "color": "#...", "path": "...", "alt": "Meeting room" }
  ],
  
  "virtual_tour_url": "https://virtualtour.bestays.app/office-rama9",
  "video_url": null,
  
  "ownership_type": null,
  "foreign_quota": null,
  
  "is_published": true,
  "is_featured": false,
  "listing_priority": 3,
  
  "rental_yield": null,
  "price_trend": "stable",
  
  "seo_title": "500 SQM Office Space Bangkok - Modern Business Park",
  "seo_description": "Professional office space in business park. 500 sqm, flexible layout, meeting rooms, high-speed internet. Available for immediate lease.",
  "tags": ["bangkok", "office", "commercial", "lease", "business-park"],
  
  "created_by": "user-corp",
  "updated_by": "user-corp",
  "created_at": "2025-05-12T08:30:00Z",
  "updated_at": "2025-11-02T13:00:00Z",
  "deleted_at": null
}
```

---

## Field Mapping Notes for Developers

### What to Include / Exclude Based on Property Type

**Land Properties:**
- Exclude: bedrooms, bathrooms, living_rooms, kitchens, furnishing, condition (building state)
- Include: land_area, year_built (year purchased), facing_direction
- Optional: physical specs should be minimal/null

**Residential (House/Villa/Condo):**
- Include: All room counts, building specs, furnished level, condition
- Include: Interior amenities, some exterior amenities
- Optional: Maid room, guest room (depending on type)

**Commercial (Office/Shop):**
- Include: Office rooms, bathrooms, floor level, parking
- Exclude: Bedrooms, living rooms (unless live-work), dining room
- Include: Building amenities (meeting rooms, business center)

**Hospitality (Resort/Hotel):**
- Flexible: Custom room configurations
- Include: All service amenities
- Include: Restaurant, facilities, recreation

---

## Translation Example

Same property translated to Thai:

```json
{
  "property_id": "550e8400-e29b-41d4-a716-446655440001",
  "lang_code": "th",
  "translations": [
    {
      "field": "title",
      "value": "วิลลาหรูหรือริมชายหาด พูเก็ต"
    },
    {
      "field": "description",
      "value": "วิลลาชายหาดสวยงามพร้อมสระว่ายน้ำแบบอินฟินิตี้ สถาปัตยกรรมสมัยใหม่ และเนื้ที่ 4 ห้องนอน"
    },
    {
      "field": "location_region",
      "value": "ภูเก็ต"
    },
    {
      "field": "location_district",
      "value": "บางเทา"
    },
    {
      "field": "policies_inclusions",
      "value": "อินเทอร์เน็ต WiFi, โทรทัศน์สายเคเบิล, แอร์เย็น, บริการทำความสะอาด, บำรุงรักษาสระ"
    },
    {
      "field": "seo_title",
      "value": "วิลลาหรูหรือพูเก็ต - บ้านสระว่ายน้ำส่วนตัว 4 ห้องนอน"
    }
  ]
}
```

---

## Data Validation Examples

### Valid Property
```javascript
const property = {
  title: "Villa with Pool",  // ✅ 200 chars max
  description: "Beautiful...",  // ✅ 5000 chars max
  rent_price: 3500000,  // ✅ >= 0
  property_type: "pool-villa",  // ✅ Valid enum
  transaction_type: "rent",  // ✅ Valid enum
  bedrooms: 4,  // ✅ >= 0
  // ... other fields
}
```

### Invalid Property
```javascript
const property = {
  title: "Very long title that exceeds...",  // ❌ > 200 chars
  rent_price: -100,  // ❌ < 0
  property_type: "mansion",  // ❌ Not in enum
  bedrooms: -1,  // ❌ < 0
  currency: "GBP",  // ❌ Only THB, USD, EUR
}
```

---

**Version:** 1.0  
**Last Updated:** 2025-11-06


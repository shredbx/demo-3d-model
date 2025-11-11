# US-025: Property Booking System with Date Range & Agent Approval

**Domain:** booking
**Feature:** date-range
**Scope:** request-system
**Status:** READY (Future Enhancement)
**Created:** 2025-11-09
**Priority:** P1 (Core Feature)
**Default Product:** bestays
**Portable:** true
**Ported To:** []

---

## Description

Implement a booking request system where users can select date ranges for properties, send booking requests (registered users only), and agents can approve/reject requests. Non-registered users see interest indicators, and approved bookings block the calendar for other users.

**User Story:**
As a registered user, I want to select start/end dates and send a booking request for a property, so that I can reserve it for my vacation. As a non-registered user, I want to see when others are interested in the same dates, so I'm encouraged to register. As an agent, I want to review and approve/reject booking requests, so I can manage my property availability.

---

## Acceptance Criteria

### Phase 1: Database & Schema
- [ ] AC-1: Create `bookings` table with fields: id, property_id, user_id, start_date, end_date, status, created_at, approved_at, agent_notes
- [ ] AC-2: Status enum: PENDING, APPROVED, REJECTED, CANCELLED
- [ ] AC-3: Create indexes on property_id + date range for fast availability queries
- [ ] AC-4: Add booking_rules JSONB to properties (min_stay, max_stay, advance_notice, etc.)

### Phase 2: User Booking Flow (Registered Users)
- [ ] AC-5: Property detail page shows calendar with availability
- [ ] AC-6: Users select check-in and check-out dates
- [ ] AC-7: "Request to Book" button for registered users (redirects to /login if not authenticated)
- [ ] AC-8: Booking request form: name, phone, email (pre-filled), message to agent
- [ ] AC-9: Backend creates booking with status=PENDING
- [ ] AC-10: User receives confirmation email: "Request sent to agent"
- [ ] AC-11: User sees booking status in "My Bookings" dashboard

### Phase 3: Interest Indicators (Non-Registered Users)
- [ ] AC-12: Non-registered users see "X people interested in these dates" on calendar
- [ ] AC-13: Interest tracked via anonymous session (Redis cache with TTL)
- [ ] AC-14: Hovering date range shows: "2 people interested" tooltip
- [ ] AC-15: CTA: "Sign up to book" button prominent on property page

### Phase 4: Agent Dashboard & Approval Workflow
- [ ] AC-16: Agent dashboard shows pending booking requests with priority sorting
- [ ] AC-17: Agent can view user profile, booking history, property details
- [ ] AC-18: Agent actions: APPROVE (with notes), REJECT (with reason), REQUEST MORE INFO
- [ ] AC-19: On approval: Booking status → APPROVED, send confirmation email to user + agent
- [ ] AC-20: On rejection: Booking status → REJECTED, send rejection email with reason
- [ ] AC-21: Calendar automatically updates: approved dates marked as "Not Available"

### Phase 5: Calendar Display & Blocking
- [ ] AC-22: Calendar UI shows 3 states: AVAILABLE (green), PENDING (yellow), BOOKED (red/grey)
- [ ] AC-23: Users cannot select dates that overlap with APPROVED bookings
- [ ] AC-24: Users can select dates with PENDING bookings (shown as warning: "Another user requested these dates")
- [ ] AC-25: Agent can override: manually block dates (maintenance, personal use)

### Phase 6: Notifications & Reminders
- [ ] AC-26: User receives email when agent approves/rejects
- [ ] AC-27: Agent receives email when new booking request arrives
- [ ] AC-28: User receives reminder 7 days before check-in
- [ ] AC-29: User receives reminder 1 day after check-out (leave review)

### Phase 7: Booking Management
- [ ] AC-30: Users can cancel bookings (up to X days before check-in, per property rules)
- [ ] AC-31: Agents can cancel bookings (with refund policy enforcement)
- [ ] AC-32: Calendar automatically releases cancelled dates
- [ ] AC-33: Booking history preserved for analytics (soft delete)

---

## Technical Notes

**Database Schema:**

```sql
CREATE TABLE bookings (
  id SERIAL PRIMARY KEY,
  property_id INTEGER NOT NULL REFERENCES properties(id),
  user_id INTEGER NOT NULL REFERENCES users(id),

  -- Date range
  check_in_date DATE NOT NULL,
  check_out_date DATE NOT NULL,
  num_nights INTEGER GENERATED ALWAYS AS (check_out_date - check_in_date) STORED,

  -- Booking details
  num_guests INTEGER NOT NULL,
  guest_message TEXT,

  -- Status
  status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    -- PENDING, APPROVED, REJECTED, CANCELLED

  -- Agent workflow
  agent_id INTEGER REFERENCES users(id),
  agent_notes TEXT,
  approved_at TIMESTAMPTZ,
  rejected_at TIMESTAMPTZ,
  rejection_reason TEXT,

  -- Pricing snapshot (at time of booking)
  nightly_rate DECIMAL(12,2),
  total_price DECIMAL(12,2),
  currency VARCHAR(3) DEFAULT 'THB',

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  -- Constraints
  CONSTRAINT check_dates CHECK (check_out_date > check_in_date),
  CONSTRAINT check_guests CHECK (num_guests > 0)
);

CREATE INDEX idx_bookings_property_dates
ON bookings(property_id, check_in_date, check_out_date)
WHERE status IN ('PENDING', 'APPROVED');

-- Interest tracking (non-registered users)
CREATE TABLE booking_interests (
  id SERIAL PRIMARY KEY,
  property_id INTEGER NOT NULL REFERENCES properties(id),
  session_id VARCHAR(255) NOT NULL,
  check_in_date DATE NOT NULL,
  check_out_date DATE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '7 days'
);

CREATE INDEX idx_interests_property_dates
ON booking_interests(property_id, check_in_date, check_out_date)
WHERE expires_at > NOW();
```

**API Endpoints:**

```typescript
// Check availability
GET /api/v1/properties/{id}/availability?month=2025-12&locale=en
Response: {
  available_dates: ["2025-12-01", "2025-12-02", ...],
  pending_dates: ["2025-12-15", "2025-12-16"], // Yellow
  booked_dates: ["2025-12-25", "2025-12-26"],  // Red
  interest_counts: { "2025-12-10": 3, "2025-12-11": 3 }
}

// Create booking request
POST /api/v1/bookings/request
Body: {
  property_id: 123,
  check_in_date: "2025-12-10",
  check_out_date: "2025-12-15",
  num_guests: 2,
  guest_message: "Looking forward to staying!"
}
Response: { booking_id: 456, status: "PENDING" }

// Track interest (non-registered)
POST /api/v1/bookings/interest
Body: {
  property_id: 123,
  check_in_date: "2025-12-10",
  check_out_date: "2025-12-15",
  session_id: "anon-xyz123"
}

// Agent approval
PUT /api/v1/bookings/{id}/approve
Body: { agent_notes: "Approved!" }

// Agent rejection
PUT /api/v1/bookings/{id}/reject
Body: { rejection_reason: "Dates not available" }
```

**Calendar Component (Frontend):**

```svelte
<script lang="ts">
  import { Calendar } from '$lib/components/Calendar.svelte';

  let selectedDates = { checkIn: null, checkOut: null };
  let availability = { available: [...], pending: [...], booked: [...] };
</script>

<Calendar
  bind:selectedDates
  {availability}
  onSelect={(dates) => checkRules(dates)}
/>
```

**Business Rules:**
- Minimum stay: 1 night (configurable per property via booking_rules JSONB)
- Maximum advance booking: 365 days
- Agent response SLA: 24 hours (send reminder if no action)
- Cancellation policy: Free up to 7 days before, 50% refund 3-7 days, no refund < 3 days

**Email Templates:**
- `booking_request_user.html` - "Your request has been sent"
- `booking_request_agent.html` - "New booking request for Property #123"
- `booking_approved.html` - "Your booking is confirmed!"
- `booking_rejected.html` - "Unfortunately, your booking was not approved"
- `booking_reminder_checkin.html` - "Your stay is coming up"
- `booking_reminder_review.html` - "How was your stay?"

**Dependencies:**
- US-019: Clerk Authentication (user/agent roles) - COMPLETED
- US-023: Property Display - COMPLETED
- Email service: SendGrid or AWS SES
- Calendar UI library: @schedule-x/calendar or react-day-picker (Svelte port)

**Estimated Effort:** 2-3 weeks (8-12 days)

---

## Related Stories

- US-019: Authentication (provides user/agent roles)
- US-023: Property Display (booking integrated into detail page)
- US-002: Homepage (shows "Top Booked Properties")
- Future: US-XXX - Payment Integration (Stripe/Omise)
- Future: US-XXX - Review System (post-booking reviews)

---

## Tasks

[Automatically populated by system - do not edit manually]

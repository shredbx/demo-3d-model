# ShredBX Model Generator - Milestone Plan v2 (FINAL)

**Project:** ShredBX Model Generator
**Goal:** Convert dirt bike photos to interactive 3D models
**Status:** FINAL - Expert Approved
**Date:** 2025-11-11
**Revisions:** Incorporates feedback from DevOps, Backend, Frontend, CTO specialists

---

## Executive Summary

ShredBX Model Generator enables users to upload photos of dirt bikes and convert them into interactive 3D models viewable in the browser.

### Key Changes from v1
- ✅ Added Milestone -1 (Market Discovery) - validate demand first
- ✅ Added authentication/authorization (API keys + user accounts)
- ✅ Replaced polling with Server-Sent Events (SSE)
- ✅ Mobile-first approach with detailed specifications
- ✅ Defined production stack (Railway + Supabase + Cloudflare)
- ✅ Added monetization model and unit economics
- ✅ Redis for status caching
- ✅ CI/CD moved to Milestone 1
- ✅ Email notifications (mandatory)

### Timeline: 7 weeks total
- **Week -1:** Market Discovery (validate demand)
- **Week 0:** Technical Validation (validate technology)
- **Weeks 1-3:** Public MVP (build and launch)
- **Weeks 4-5:** Production Hardening (optimize and test)

### Revised Cost: $50-75/month (MVP), $100-150/month (production)

---

## MILESTONE -1: Market Discovery (NEW)

**Duration:** 1 week
**Goal:** Validate that dirt bike owners want this product before building it

**Why First?**
- Don't waste 6 weeks building something nobody wants
- Understand use cases before designing features
- Validate pricing before setting monetization strategy
- Identify competitors early

### Scope

**Customer Interviews:**
- ✅ Interview 20+ dirt bike owners (forums, Reddit, Instagram)
- ✅ Questions:
  - "Would you use a tool to convert bike photos to 3D models?"
  - "What would you DO with a 3D model of your bike?"
  - "Would you pay for this? How much?"
  - "What features would make this valuable?"

**Competitor Research:**
- ✅ Identify existing 3D model services for vehicles
- ✅ Analyze pricing models
- ✅ Identify gaps in market

**Use Case Validation:**
- ✅ Document top 5 use cases from interviews
- ✅ Prioritize by frequency and willingness to pay
- ✅ Map use cases to features

**Pricing Research:**
- ✅ Validate willingness to pay
- ✅ Test pricing tiers (free, $9.99, $29.99)
- ✅ Calculate target market size

### Acceptance Criteria

1. **Demand Validation**
   - ✅ 50%+ of interviewees express interest
   - ✅ 3+ clear use cases identified
   - ✅ Competitor landscape documented

2. **Pricing Validation**
   - ✅ 30%+ willing to pay $5+ per model OR $10+ per month
   - ✅ Unit economics calculated (cost vs revenue)
   - ✅ Pricing tiers defined

3. **GO/NO-GO Decision**
   - ✅ If YES: Proceed to Milestone 0 (Technical Validation)
   - ✅ If NO: Pivot or kill project

### Deliverables
- Market research report (20+ interview notes)
- Competitor analysis document
- Use case prioritization matrix
- Pricing strategy document
- GO/NO-GO decision with justification

### Risks
- ❌ No demand found → **Mitigation:** Small sample (20 interviews), may need more
- ❌ Pricing too low → **Mitigation:** Test higher tiers ($49.99/month)

---

## MILESTONE 0: Technical Validation

**Duration:** 1 week
**Goal:** Prove the technology stack can deliver acceptable results

**Changes from v1:**
- Added API comparison (Meshy.ai vs TripoSR vs Luma)
- Added cross-browser testing
- Added mobile device testing
- Added Redis architecture

### Scope

**API Comparison (NEW):**
- ✅ Test Meshy.ai (cloud API)
- ✅ Test TripoSR local (self-hosted)
- ✅ Test Luma AI (cloud API)
- ✅ Compare: quality, cost, latency, control
- ✅ Decision: Choose best API for MVP

**Backend:**
- ✅ Meshy.ai integration (if chosen)
- ✅ Cloudflare R2 storage setup
- ✅ Redis for status caching (NEW)
- ✅ Basic FastAPI endpoints (no UI)
- ✅ Test with 10+ real dirt bike photos

**Frontend:**
- ✅ Three.js basic scene with GLTFLoader
- ✅ Test on real devices (iPhone 12, Android mid-range, iPad)
- ✅ Cross-browser testing (Chrome, Firefox, Safari, Mobile Safari) (NEW)
- ✅ Measure FPS on all devices

**Manual Testing:**
- ✅ Upload image via curl
- ✅ Verify 3D model quality
- ✅ Load model in Three.js test page
- ✅ Measure total time (upload → 3D model)

### High-Level Acceptance Criteria

1. **Quality Validation**
   - ✅ Chosen API produces recognizable 3D models (80% success rate)
   - ✅ Models have textures (not gray mesh)
   - ✅ Bike parts identifiable (exhaust, wheels, suspension)

2. **Performance Validation**
   - ✅ Three.js renders at 60fps on iPhone 12
   - ✅ GLB models load in < 3 seconds
   - ✅ Total generation time < 20 minutes (acceptable)

3. **Cost Validation**
   - ✅ Cost per model < $0.60 (budget target)
   - ✅ R2 storage projection < $10/month for 100 models
   - ✅ Total infrastructure < $75/month

4. **Technical Validation**
   - ✅ Upload to R2 works reliably
   - ✅ API integration robust (error handling, retries)
   - ✅ Redis caching works (status updates)
   - ✅ Three.js works on all tested browsers/devices

5. **API Decision (NEW)**
   - ✅ Document chosen API with justification
   - ✅ Design API abstraction layer (no vendor lock-in)
   - ✅ Document exit strategy if API fails

### Success Metrics
- **Quality:** 80% of test images → acceptable models
- **Performance:** 60fps on mid-range devices
- **Cost:** < $0.60 per generation
- **Browser Support:** Works on Chrome, Firefox, Safari (desktop + mobile)

### Deliverables
- Technical validation report (quality, performance, cost)
- API comparison matrix (Meshy vs TripoSR vs Luma)
- API choice decision document
- Risk assessment and mitigation plan
- GO/NO-GO decision for Milestone 1

### Risks
- ❌ No API produces acceptable quality → **Mitigation:** Test 3 APIs, choose best
- ❌ Mobile performance too slow → **Mitigation:** Reduce poly count/texture resolution
- ❌ Costs exceed budget → **Mitigation:** Choose TripoSR local (lower cost)

---

## MILESTONE 1: Public MVP

**Duration:** 3 weeks
**Goal:** Launch a public-facing product with complete user journey

**Major Changes from v1:**
- Added authentication (API keys + user accounts)
- Replaced polling with Server-Sent Events (SSE)
- Added Redis for caching
- Added CI/CD pipeline
- Email notifications (mandatory, not optional)
- Mobile-first design approach
- Defined production stack

### Production Stack (NEW)

**Hosting:**
- **Backend:** Railway ($20/month) - FastAPI + Redis + Workers
- **Frontend:** Vercel (Free tier) - SvelteKit SSR + CDN
- **Database:** Supabase (Free tier → $25/month) - PostgreSQL + Auth
- **Storage:** Cloudflare R2 ($5-10/month) - Images + GLB files
- **Email:** SendGrid (Free tier) - Transactional emails

**Architecture:**
```
User → Vercel (SvelteKit)
       ↓
Railway (FastAPI) → Supabase (PostgreSQL)
                  → Redis (status cache)
                  → Cloudflare R2 (storage)
                  → Meshy.ai/TripoSR (3D generation)
                  → SendGrid (email notifications)
```

### Scope

**Infrastructure (DevOps):**
- ✅ Docker Compose development environment
- ✅ Production deployment (Railway + Vercel + Supabase)
- ✅ CI/CD pipeline (GitHub Actions) (MOVED FROM M2)
- ✅ Staging environment (test before prod)
- ✅ Environment configuration (.env management)

**Backend (FastAPI):**
- ✅ Authentication (API keys or JWT) (NEW)
- ✅ User accounts (email/password via Supabase Auth) (NEW)
- ✅ Image upload endpoint (multipart/form-data)
- ✅ 3D generation service (Meshy.ai or TripoSR)
- ✅ Server-Sent Events (SSE) for status updates (NEW - replaces polling)
- ✅ Model download endpoint (pre-signed R2 URLs)
- ✅ Redis integration (status caching) (NEW)
- ✅ Error handling (400, 404, 500, Meshy-specific errors)
- ✅ Rate limiting (per user, not just IP) (NEW)
- ✅ API documentation (OpenAPI/Swagger)

**Frontend (SvelteKit + Three.js):**
- ✅ Homepage with drag-drop upload
- ✅ Mobile-first responsive design (NEW)
- ✅ Touch gesture support (OrbitControls) (NEW)
- ✅ File validation (client-side + server-side)
- ✅ Upload progress indicator
- ✅ SSE client (real-time status updates) (NEW)
- ✅ Three.js viewer with:
  - OrbitControls (rotate, zoom, pan)
  - Proper lighting (ambient + directional)
  - Auto-centering and scaling
  - Grid/ground plane
  - Reset camera button (NEW)
- ✅ Download GLB button
- ✅ User authentication UI (login, signup)
- ✅ Model gallery (user's past generations) (NEW)
- ✅ Accessibility (keyboard nav, WCAG 2.1 AA) (NEW)

**Email Notifications (NEW - MANDATORY):**
- ✅ Email sent when model generation complete
- ✅ Email contains link to view model
- ✅ "Close this tab, we'll email you" prominent message

**State Management (NEW):**
- ✅ Svelte 5 $state runes for reactive state
- ✅ Svelte stores for global state (user, session)
- ✅ Three.js lifecycle managed in onMount (not $effect)

**User Journey:**
1. User visits homepage
2. Signs up / logs in (NEW)
3. Drags/drops dirt bike photo
4. Client validates file (size, type)
5. Image uploads to R2
6. Backend calls 3D generation API
7. Frontend connects to SSE stream (NEW)
8. Real-time status updates (5-15 min)
9. Email notification sent (NEW)
10. User views 3D model in Three.js
11. User downloads GLB or saves to gallery

### High-Level Acceptance Criteria

1. **Authentication & Authorization (NEW)**
   - ✅ Users can sign up with email/password
   - ✅ Users can log in and access past models
   - ✅ API endpoints protected (require auth token)
   - ✅ Rate limiting per user (10 uploads/day free tier)

2. **Functional Completeness**
   - ✅ Complete user journey works end-to-end
   - ✅ Upload → process → view → download
   - ✅ Email notification arrives within 1 minute
   - ✅ Model gallery shows past generations

3. **Real-Time Updates (NEW)**
   - ✅ SSE provides status updates every 2-5 seconds
   - ✅ No polling overhead (efficient)
   - ✅ Connection resilience (auto-reconnect on drop)

4. **Mobile Experience (NEW)**
   - ✅ Works on iPhone (Safari) and Android (Chrome)
   - ✅ Touch gestures smooth (pinch, pan, rotate)
   - ✅ Responsive breakpoints (320px, 768px, 1024px)
   - ✅ Mobile file picker works (no drag-drop required)

5. **Performance**
   - ✅ Upload + API call < 10 seconds
   - ✅ Three.js 60fps on iPhone 12
   - ✅ Frontend bundle < 800KB (adjusted from 500KB)
   - ✅ API response time < 200ms (excluding 3D generation)

6. **Reliability**
   - ✅ Upload success rate > 95%
   - ✅ Generation completion rate > 90%
   - ✅ Viewer load success > 95%
   - ✅ Email delivery success > 99%

7. **Accessibility (NEW)**
   - ✅ Keyboard navigation works
   - ✅ Screen reader support
   - ✅ WCAG 2.1 AA compliant
   - ✅ Color contrast meets standards

8. **CI/CD (MOVED FROM M2)**
   - ✅ Automated tests run on PR
   - ✅ Auto-deploy to staging on merge to main
   - ✅ Manual approval for production deploy
   - ✅ Rollback script documented

### Success Metrics
- **Conversion:** 70% of uploads → viewable models
- **Retention:** Email open rate > 40%
- **Performance:** P95 response time < 300ms
- **Mobile:** 40%+ traffic from mobile devices

### Deliverables
- Deployed MVP (publicly accessible)
- User documentation (how to use)
- API documentation (OpenAPI spec)
- Operations runbook (how to operate)
- Monetization dashboard (track usage/costs)

### Risks
- ❌ Auth complexity delays launch → **Mitigation:** Use Supabase Auth (pre-built)
- ❌ SSE not supported on old browsers → **Mitigation:** Fallback to long-polling
- ❌ Email deliverability issues → **Mitigation:** Use SendGrid (high deliverability)
- ❌ Mobile performance issues → **Mitigation:** Extensive mobile testing in M0

---

## MILESTONE 2: Production Hardening

**Duration:** 2 weeks
**Goal:** Make MVP reliable, scalable, and production-ready

**Changes from v1:**
- CI/CD moved to M1 (already deployed)
- Focus on testing, optimization, monitoring
- Load testing added

### Scope

**Testing:**
- ✅ E2E tests (Playwright) - complete user flows
- ✅ Backend unit tests (>80% coverage)
- ✅ Frontend component tests (Svelte Testing Library)
- ✅ Visual regression tests (Three.js scenes) (NEW)
- ✅ Load testing (100 concurrent users) (NEW)
- ✅ Cross-browser E2E tests (Chrome, Firefox, Safari)

**Performance Optimization:**
- ✅ Three.js rendering optimization (LOD, frustum culling)
- ✅ Image compression before upload (client-side)
- ✅ GLB caching strategy (Cloudflare CDN)
- ✅ API response time optimization (< 150ms target)
- ✅ Frontend bundle optimization (code splitting, lazy loading)
- ✅ Database query optimization (indexes, connection pooling)

**Reliability:**
- ✅ Comprehensive error handling (all edge cases)
- ✅ Retry logic for API failures (exponential backoff)
- ✅ Circuit breaker pattern for 3D generation API
- ✅ Graceful degradation (WebGL fallback, offline mode)
- ✅ Data retention policy (7-day TTL free, permanent paid) (NEW)
- ✅ Automated cleanup jobs (delete expired models)

**Monitoring & Observability (EXPANDED):**
- ✅ Application logs (structured JSON, Cloudflare Logs)
- ✅ Error tracking (Sentry)
- ✅ Uptime monitoring (UptimeRobot)
- ✅ Performance monitoring (Railway metrics)
- ✅ Cost monitoring (R2 usage alerts, Meshy credit tracking)
- ✅ Analytics (PostHog - track uploads, completions, downloads) (NEW)

**Security:**
- ✅ File upload validation (10MB max, JPEG/PNG only, dimension limits)
- ✅ API key security (rotation procedure documented)
- ✅ Rate limiting enforcement (tested under load)
- ✅ HTTPS enforced (all endpoints)
- ✅ CORS properly configured (whitelist, not wildcard)
- ✅ Security audit (OWASP top 10 checklist)

**Backup & Disaster Recovery (NEW):**
- ✅ Daily database backups (pg_dump to R2)
- ✅ 7-day backup retention
- ✅ Restore procedure documented and tested
- ✅ RTO: 4 hours, RPO: 24 hours

### High-Level Acceptance Criteria

1. **Quality Assurance**
   - ✅ E2E test suite passes (100%)
   - ✅ Backend coverage > 80%
   - ✅ Frontend coverage > 70%
   - ✅ Zero critical production bugs

2. **Performance**
   - ✅ API P95 response time < 150ms
   - ✅ Frontend bundle < 600KB (optimized)
   - ✅ Three.js 60fps on iPhone 12
   - ✅ Page load time < 2 seconds

3. **Load Testing (NEW)**
   - ✅ 100 concurrent users uploading
   - ✅ No 500 errors under load
   - ✅ Database handles 1000 concurrent reads
   - ✅ SSE scales to 500 concurrent connections

4. **Reliability**
   - ✅ Uptime > 99.5% (measured over 1 week)
   - ✅ Error rate < 1%
   - ✅ All errors logged and alerted
   - ✅ Backup restore tested successfully

5. **Security**
   - ✅ Security audit complete (no critical findings)
   - ✅ Penetration testing complete
   - ✅ All OWASP top 10 mitigated

6. **Monitoring**
   - ✅ All critical metrics dashboarded
   - ✅ Alerts configured (downtime, errors, costs)
   - ✅ On-call runbook documented

### Success Metrics
- **Uptime:** 99.5%+ in first month
- **Performance:** P95 < 150ms
- **Quality:** Zero critical bugs
- **Testing:** 100% E2E coverage

### Deliverables
- Complete test suite (E2E, unit, integration, load)
- Performance optimization report
- Security audit report
- Monitoring dashboards
- Incident response plan
- Operations runbook

### Risks
- ❌ Performance issues under load → **Mitigation:** Load testing identifies bottlenecks
- ❌ Security vulnerabilities → **Mitigation:** Security audit + penetration testing
- ❌ Backup restore fails → **Mitigation:** Test restore before launch

---

## Monetization Model (NEW)

**Unit Economics:**
```
Cost per model:
- API (Meshy.ai): $0.50 or TripoSR: $0.10
- R2 storage: $0.01
- Infrastructure (prorated): $0.02
Total cost: $0.53/model (Meshy) or $0.13/model (TripoSR)

Target margin: 70%
Required revenue: $1.77/model (Meshy) or $0.43/model (TripoSR)
```

**Pricing Tiers:**

### Free Tier
- 3 models/month
- Watermarked previews
- Public gallery only
- Standard queue (5-20 min)

### Hobby ($9.99/month)
- 15 models/month ($0.67 ea)
- No watermark
- Private gallery
- Download GLB
- Priority queue (5-10 min)

### Pro ($29.99/month)
- 60 models/month ($0.50 ea)
- All Hobby features
- API access
- Commercial license
- Fastest queue (2-5 min)

**Margins:**
- Hobby: $9.99 - (15 × $0.53) = $9.99 - $7.95 = **$2.04 profit (20% margin)**
- Pro: $29.99 - (60 × $0.53) = $29.99 - $31.80 = **-$1.81 LOSS**

**Adjustment Needed:**
- Pro tier: 50 models/month max (not 60) = $3.49 profit (12% margin)
- OR use TripoSR ($0.13/model) = much better margins
- OR increase Pro to $49.99/month

**Target Market:**
- Primary: Individual dirt bike owners (enthusiasts, sellers)
- Secondary: Dealerships (bulk usage, custom pricing)
- Tertiary: Manufacturers (3D asset creation)

---

## Dependencies & Risks

### External Dependencies

1. **3D Generation API**
   - Primary: Meshy.ai or TripoSR (decided in M0)
   - Backup: Alternative API ready to swap
   - Risk: API downtime, quality degradation, price increase
   - Mitigation: API abstraction layer, exit strategy documented

2. **Hosting (Railway + Vercel)**
   - Risk: Platform downtime, price increase
   - Mitigation: Monitor SLAs, budget alerts

3. **Email (SendGrid)**
   - Risk: Deliverability issues, suspended account
   - Mitigation: Use transactional tier, monitor delivery rates

### Technical Risks

1. **3D Model Quality**
   - Risk: API doesn't work well for dirt bikes
   - Mitigation: M0 validation with 10+ photos, 3 API comparison

2. **Mobile Performance**
   - Risk: Three.js too slow on mid-range phones
   - Mitigation: M0 device testing, optimization in M2

3. **Cost Overruns**
   - Risk: Viral usage exhausts budget
   - Mitigation: Rate limiting, usage alerts, paid tiers

4. **Email Deliverability**
   - Risk: Notifications marked as spam
   - Mitigation: SPF/DKIM/DMARC, SendGrid reputation

### Business Risks

1. **No Market Demand**
   - Risk: Nobody uses the product
   - Mitigation: M-1 validation (20+ interviews)

2. **Low Conversion to Paid**
   - Risk: Free tier sufficient, no paid users
   - Mitigation: Limit free tier (3 models/month), add value to paid

3. **Competitor Launch**
   - Risk: Similar product launches first
   - Mitigation: Speed to market (7 weeks), niche focus (dirt bikes)

---

## Timeline & Resources

### Timeline: 7 weeks

| Milestone | Duration | Calendar |
|-----------|----------|----------|
| M-1: Market Discovery | 1 week | Week -1 |
| M0: Technical Validation | 1 week | Week 0 |
| M1: Public MVP | 3 weeks | Weeks 1-3 |
| M2: Production Hardening | 2 weeks | Weeks 4-5 |

### Resource Requirements

**Development:**
- Coordinator (Claude Code) - Full time
- Subagents (dev-backend-fastapi, dev-frontend-svelte, playwright-e2e-tester, devops-infra)

**Infrastructure (Monthly Costs):**
```
MVP Phase:
- Railway (backend + Redis): $20
- Vercel (frontend): Free
- Supabase (database): Free → $25
- Cloudflare R2 (storage): $5-10
- Meshy.ai (3D generation): $20
- SendGrid (email): Free
- Sentry (monitoring): Free
- Domain: $1/month
Total: $50-75/month

Production Phase (with scaling):
- Railway: $50 (higher tier)
- Supabase: $25 (paid tier)
- R2: $20 (more storage)
- Meshy.ai: $60 (Max tier)
- SendGrid: $15 (100k emails)
- Sentry: $26 (paid tier)
- PostHog (analytics): $20
Total: $150-200/month at scale
```

---

## Success Criteria Summary

### Milestone -1: Market Discovery
✅ 50%+ interest rate from interviews
✅ 3+ validated use cases
✅ Pricing model validated ($9.99-29.99 acceptable)
✅ GO decision with confidence

### Milestone 0: Technical Validation
✅ Chosen API produces 80%+ acceptable models
✅ Three.js 60fps on mid-range devices
✅ Cost per model < $0.60
✅ Cross-browser compatibility verified
✅ GO decision for M1

### Milestone 1: Public MVP
✅ Complete user journey (signup → upload → view → download)
✅ 70%+ conversion (uploads → viewable models)
✅ Email notifications working (>99% delivery)
✅ Mobile responsive (works on phones)
✅ CI/CD deployed
✅ Public launch

### Milestone 2: Production Hardening
✅ E2E test coverage 100%
✅ Uptime > 99.5%
✅ P95 response time < 150ms
✅ Load tested (100 concurrent users)
✅ Zero critical bugs
✅ Security audit passed

---

## Next Steps

1. ✅ **Review this plan with user**
2. ✅ **Add to CLAUDE.md** (if approved)
3. ✅ **Begin Milestone -1** (Market Discovery)

---

**Status:** FINAL - Expert Approved (4/4 specialists reviewed)
**Version:** v2
**Date:** 2025-11-11
**Ready for Implementation:** YES

---

## Changes from v1

### Added:
1. Milestone -1 (Market Discovery) - 1 week
2. Authentication/authorization (API keys + user accounts)
3. Server-Sent Events (replaced polling)
4. Redis for status caching
5. Defined production stack (Railway + Supabase + Vercel + R2)
6. Monetization model (pricing tiers + unit economics)
7. Email notifications (mandatory)
8. Mobile-first approach
9. Accessibility requirements (WCAG 2.1 AA)
10. State management architecture
11. CI/CD moved to M1 (from M2)
12. Load testing
13. Analytics (PostHog)
14. API comparison in M0 (test 3 alternatives)
15. Cross-browser testing in M0 (from M2)
16. Data retention policy
17. Backup/restore procedures

### Removed:
- Vague "cloud deployment" (replaced with specific stack)
- Polling mechanism (replaced with SSE)
- Optional email notifications (now mandatory)

### Modified:
- Timeline: 6 weeks → 7 weeks (added M-1)
- Cost: $25-30/month → $50-75/month (realistic)
- Testing moved earlier (cross-browser in M0, not M2)

**Approval Status:**
- DevOps: 🟢 GREEN LIGHT (blockers addressed)
- Backend: 🟢 GREEN LIGHT (auth + SSE + API design added)
- Frontend: 🟢 GREEN LIGHT (mobile + a11y + state mgmt added)
- CTO: 🟢 GREEN LIGHT (market validation + monetization + API comparison added)

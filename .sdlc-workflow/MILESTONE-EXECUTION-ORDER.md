# Milestone Execution Order - STRICT ENFORCEMENT

**Purpose:** Define EXACTLY what order work must happen in, with NO EXCEPTIONS.

**Philosophy:** "Follow the plan, no matter how clear the context seems."

**Status:** ACTIVE - All agents MUST follow this order
**Created:** 2025-11-08
**Last Updated:** 2025-11-08

---

## 🚨 CRITICAL RULES

### Rule 1: NEVER Skip Steps
**Even if:**
- The context is clear
- An agent thinks they can work ahead
- It seems like an obvious optimization
- Previous work gives you all the context you need

**Reason:** Parallel work creates integration bugs. Sequential work ensures clean integration.

---

### Rule 2: NEVER Start Next Milestone Until Current is COMPLETE
**Complete Means:**
- ✅ All deliverables done
- ✅ All tests passing (100%)
- ✅ Code reviewed and merged
- ✅ User approval received

**NOT Complete:**
- ❌ "Almost done, just fixing one test"
- ❌ "95% passing, close enough"
- ❌ "Code works, tests are just flaky"
- ❌ "I think the user will approve"

---

### Rule 3: NEVER Work on Multiple Milestones Simultaneously
**One milestone at a time. Period.**

**Reason:** Context switching causes mistakes. Focus produces quality.

---

## 📋 EXECUTION ORDER (NO DEVIATIONS)

### MILESTONE 1: Fix US-019 Logout Tests ⏳ CURRENT

**Status:** IN PROGRESS (Tests failing)

**What's Failing:**
- Logout flow tests (6 failures - Bestays + Real Estate)
- Protected route tests (strict mode violations)
- Chat journey tests (4 failures)
- Old login.spec.ts tests (legacy issues)

**Success Criteria:**
```
✅ 66/66 tests passing (100%)
✅ No timeouts
✅ No strict mode violations
✅ Code reviewed
✅ User approves merge
```

**Blocking:** ALL future work

**Timeline:** TBD (depends on fixes)

**Agents Involved:**
- Coordinator (diagnose issues, create fix plan)
- dev-frontend-svelte (implement fixes)
- playwright-e2e-tester (verify fixes)

**Deliverables:**
- [ ] All logout tests passing
- [ ] All protected route tests passing
- [ ] All chat tests passing (or explicitly marked as out-of-scope)
- [ ] Test report showing 100% pass rate

**🔒 GATE:** Cannot proceed to Milestone 2 until this is 100% complete.

---

### MILESTONE 2: US-020 Homepage Editable Content 🔜 NEXT

**Status:** WAITING (Blocked by Milestone 1)

**Dependencies:**
- US-019 tests 100% passing ✅
- US-019 merged to main ✅
- User approval to start US-020 ✅

**Success Criteria:**
```
✅ Database: content_dictionary table created
✅ Backend: GET/PUT /api/v1/content/{key} working
✅ Frontend: Homepage with editable title/description
✅ E2E: All US-020 acceptance criteria tests passing
✅ Code reviewed
✅ User approves merge
```

**Timeline:** 5-7 days (per US-020 plan)

**Agents Involved:**
1. **Day 1:** DevOps (database schema + seed data)
2. **Day 2-3:** Backend (API + service layer)
3. **Day 4-5:** Frontend (components + integration)
4. **Day 6:** E2E Testing (validation)
5. **Day 7:** Bug fixes + polish

**Deliverables:**
- [ ] DevOps: Alembic migration + seed data
- [ ] Backend: ContentService + API routes
- [ ] Frontend: shadcn-svelte + EditableText + EditContentDialog
- [ ] E2E: All AC tests passing
- [ ] Documentation: Complete

**🔒 GATE:** Cannot proceed to Milestone 3 until this is 100% complete.

---

### MILESTONE 3: US-021 Thai Localization 🔮 FUTURE

**Status:** WAITING (Blocked by Milestone 2)

**Dependencies:**
- US-020 100% complete ✅
- US-020 merged to main ✅
- User approval to start US-021 ✅

**Success Criteria:**
```
✅ Database: locale column added, Thai translations inserted
✅ Backend: API accepts ?locale=en|th parameter
✅ Frontend: Routes restructured to /[lang]/, locale switcher works
✅ E2E: All US-021 acceptance criteria tests passing
✅ Thai content reviewed by professional translator
✅ Code reviewed
✅ User approves merge
```

**Timeline:** 4-6 days (per US-021 plan)

**Agents Involved:**
1. **Day 1:** DevOps (schema migration + Thai seed data)
2. **Day 2:** Backend (locale-aware API)
3. **Day 3-4:** Frontend (route restructure + i18n context + locale switcher)
4. **Day 5:** E2E Testing (multi-locale validation)
5. **Day 6:** Bug fixes + professional translation review

**Deliverables:**
- [ ] DevOps: Migration + Thai translations
- [ ] Backend: Locale parameter support + fallback logic
- [ ] Frontend: [lang] routes + LocaleSwitcher + updated components
- [ ] E2E: Locale switching tests passing
- [ ] Professional Thai review complete

**🔒 GATE:** Cannot proceed to Milestone 4 (TBD) until this is 100% complete.

---

## 🛡️ ENFORCEMENT MECHANISMS

### For Coordinator (Me)
**If I'm tempted to skip ahead:**
1. Read this document
2. Check current milestone status
3. If not 100% complete, STOP
4. Focus only on current milestone

**Example:**
```
❌ BAD: "US-019 is 95% passing, let's start planning US-020 DevOps work"
✅ GOOD: "US-019 is 95% passing, let's fix the remaining 5% first"
```

---

### For User
**If you want to jump ahead:**
- I will remind you of this document
- I will show current milestone status
- I will ask: "Should we finish [current milestone] first?"
- If you insist on skipping, I'll note it and proceed (you're the boss)

**Example:**
```
User: "Let's start US-020 while we wait for tests to finish"
Coordinator: "I see US-019 tests are at 95% (45/66 passing).
             Should we fix the remaining 5% first?
             The MILESTONE-EXECUTION-ORDER.md document says we must complete
             Milestone 1 (100% tests passing) before starting Milestone 2 (US-020).

             What would you like to do?"
```

---

### For Agents (Subagents)
**Each agent receives the complete user story document** (US-020 or US-021) which includes:
- Complete system architecture
- Data flow diagrams
- What other agents are building
- Why their work matters to the complete system
- Integration points clearly defined

**If an agent completes their work early:**
- They document their work
- They review other agents' code (if available)
- They do NOT start work on next milestone

---

## 📊 Progress Tracking

### Current Status (2025-11-08)

| Milestone | Status | Progress | Blocking? |
|-----------|--------|----------|-----------|
| **M1: Fix US-019 Tests** | 🔄 IN PROGRESS | 45/66 tests (68%) | ✅ BLOCKS ALL |
| **M2: US-020 Homepage** | ⏸️ WAITING | 0% | Blocked by M1 |
| **M3: US-021 Localization** | ⏸️ WAITING | 0% | Blocked by M2 |

**Next Action:** Fix remaining 21 failing tests in US-019

---

## 🎯 Gate Checklist (Before Moving to Next Milestone)

### Before Starting Milestone 2 (US-020):
- [ ] US-019 E2E tests: 66/66 passing (100%)
- [ ] No test timeouts
- [ ] No strict mode violations
- [ ] Code reviewed and approved
- [ ] Changes merged to main branch
- [ ] User explicitly approves starting US-020

### Before Starting Milestone 3 (US-021):
- [ ] US-020 fully deployed and working
- [ ] All US-020 E2E tests passing
- [ ] Homepage editable content works in production
- [ ] Code reviewed and approved
- [ ] Changes merged to main branch
- [ ] User explicitly approves starting US-021

---

## 📝 Deviation Log

**Purpose:** Track any deviations from this order (with user approval).

| Date | Deviation | Reason | Approved By | Outcome |
|------|-----------|--------|-------------|---------|
| - | - | - | - | - |

---

## 🔄 How This Document is Used

### Start of Each Session:
1. Coordinator reads this document
2. Checks current milestone status
3. Continues work on current milestone ONLY
4. Does NOT plan ahead unless current milestone 100% complete

### When User Asks to Plan Ahead:
1. Show this document
2. Show current milestone status
3. Remind user of sequential execution rule
4. Get explicit approval if proceeding anyway

### When Current Milestone Complete:
1. Update progress table (mark current as COMPLETE)
2. Move next milestone to IN PROGRESS
3. Begin work on next milestone
4. Update this document with actual timeline/issues

---

## ✅ Benefits of This Approach

**Why Sequential > Parallel:**
1. **Clean Integration:** Each milestone fully tested before next starts
2. **Focus:** Agents work on one thing at a time (better quality)
3. **Debuggability:** If something breaks, we know exactly which milestone caused it
4. **User Visibility:** Clear progress, clear status, clear blockers
5. **Predictability:** Know exactly what comes next

**Why NOT Parallel:**
1. **Integration Hell:** Features collide, merge conflicts, unclear blame
2. **Context Switching:** Agents jump between tasks (more mistakes)
3. **Wasted Work:** If Milestone 1 changes design, Milestone 2 work may be invalidated
4. **Testing Chaos:** Can't isolate which feature caused which bug

---

## 🚀 Summary

**Current Focus:** Fix US-019 logout tests (Milestone 1)

**After That:** US-020 Homepage (Milestone 2)

**After That:** US-021 Localization (Milestone 3)

**Rule:** One at a time. No exceptions. No matter how clear the context.

---

**Document Owner:** Coordinator
**Enforcement:** STRICT (all agents + user)
**Review Frequency:** After each milestone complete
**Last Updated:** 2025-11-08
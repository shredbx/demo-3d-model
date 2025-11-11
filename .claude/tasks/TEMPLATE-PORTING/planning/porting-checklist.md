# Porting Checklist: {feature} ({source_product} → {target_product})

**Task:** {task_id}
**Story:** {story_id}
**Source Task:** {source_task_id}

---

## Pre-Porting Review

### 1. Review Source Implementation

- [ ] Read source task README: `.claude/tasks/{source_task_id}/README.md`
- [ ] Review source decisions: `.claude/tasks/{source_task_id}/planning/decisions.md`
- [ ] Review source subagent reports: `.claude/tasks/{source_task_id}/subagent-reports/`
- [ ] Understand source architecture and patterns

### 2. Identify Porting Scope

- [ ] List all files to port
- [ ] Identify portable vs product-specific elements
- [ ] Document required adaptations
- [ ] Estimate porting effort

---

## Files to Port

### Backend Files

- [ ] `{file_path}` → Adaptation: {describe changes needed}
- [ ] `{file_path}` → Adaptation: {describe changes needed}
- [ ] `{file_path}` → Portable (no changes)

### Frontend Files

- [ ] `{file_path}` → Adaptation: {describe changes needed}
- [ ] `{file_path}` → Adaptation: {describe changes needed}
- [ ] `{file_path}` → Portable (no changes)

### Test Files

- [ ] `{file_path}` → Adaptation: {describe changes needed}
- [ ] `{file_path}` → Portable (no changes)

---

## Configuration Changes

### Environment Variables

- [ ] Create/update `.env.{target_product}`
- [ ] Update Clerk instance/keys for {target_product}
- [ ] Update API endpoints (if different)
- [ ] Update database connection (if separate)
- [ ] Update Redis keys/prefixes

### Application Config

- [ ] Update `apps/{target_product}/config.ts`
- [ ] Update feature flags
- [ ] Update product-specific constants
- [ ] Update third-party service configs

---

## Product-Specific Adaptations

### Business Logic

- [ ] **Role Mappings:**
  - {source_product}: {list roles}
  - {target_product}: {list roles}
  - Mapping: {describe how roles map}

- [ ] **Workflow Differences:**
  - {describe workflow adaptations needed}

- [ ] **Data Model Differences:**
  - {describe schema differences}

### UI/UX Adaptations

- [ ] **Branding:**
  - Update colors (Tailwind config)
  - Update logo/favicon
  - Update fonts (if different)

- [ ] **Navigation:**
  - Source redirect: {url}
  - Target redirect: {url}

- [ ] **Copy/Messaging:**
  - Update product-specific terminology
  - Update help text
  - Update error messages

### Data Adaptations

- [ ] **Database Schema:**
  - Create migration for {target_product} tables (if needed)
  - Add product-specific columns
  - Update constraints

- [ ] **Test Data:**
  - Create {target_product} test accounts
  - Set up {target_product} test fixtures
  - Update seed data

---

## Testing

### Unit Tests

- [ ] Port unit tests from source
- [ ] Adapt tests for {target_product} context
- [ ] Add {target_product}-specific test cases
- [ ] All unit tests passing

### Integration Tests

- [ ] Port integration tests from source
- [ ] Update API endpoints for {target_product}
- [ ] Update test database connection
- [ ] All integration tests passing

### E2E Tests (Playwright)

- [ ] Port E2E tests from source
- [ ] Update test URLs ({target_product} domain)
- [ ] Update test credentials ({target_product} accounts)
- [ ] Update selectors (if UI differs)
- [ ] All E2E tests passing

### Manual QA

- [ ] Test on {target_product} staging environment
- [ ] Test all user flows
- [ ] Test error scenarios
- [ ] Test edge cases
- [ ] Cross-browser testing (Chrome, Firefox, Safari)
- [ ] Mobile testing (if applicable)

---

## Deployment

### Pre-Deployment

- [ ] Code review completed
- [ ] All tests passing
- [ ] No merge conflicts
- [ ] Environment variables configured in production
- [ ] Database migrations ready (if needed)

### Deployment Steps

- [ ] Deploy to {target_product} staging
- [ ] Smoke test on staging
- [ ] Run full QA on staging
- [ ] Deploy to {target_product} production
- [ ] Verify production deployment
- [ ] Monitor logs for errors

### Post-Deployment

- [ ] Monitor {target_product} metrics
- [ ] Check error tracking dashboard
- [ ] Validate with stakeholders
- [ ] Document any production issues
- [ ] Update story metadata: `ported_to: [{target_product}]`

---

## Verification

### Functional Verification

- [ ] All acceptance criteria met for {target_product}
- [ ] Core functionality works identically to {source_product}
- [ ] Product-specific adaptations work as expected
- [ ] No regressions in {source_product}

### Non-Functional Verification

- [ ] Performance acceptable (same or better than {source_product})
- [ ] Security reviewed (no new vulnerabilities)
- [ ] Accessibility maintained (WCAG compliance)
- [ ] SEO maintained (if applicable)

---

## Challenges & Decisions

### Unexpected Challenges

Document any unexpected issues encountered during porting:

- **Challenge:** {describe}
- **Solution:** {describe}
- **Trade-offs:** {describe}

### Porting Decisions

Document any decisions made during porting:

- **Decision:** {what was decided}
- **Rationale:** {why this was chosen}
- **Alternatives:** {what else was considered}

---

## Completion

### Final Checklist

- [ ] All files ported and adapted
- [ ] All tests passing
- [ ] Deployed to production
- [ ] QA approved
- [ ] Story metadata updated
- [ ] Documentation complete
- [ ] Subagent report saved

### Sign-Off

**Ported By:** {subagent_name}
**Reviewed By:** Coordinator
**Completed:** {completion_date}

---

**Template Version:** 1.0
**Last Updated:** 2025-11-07

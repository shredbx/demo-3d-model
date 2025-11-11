# Product-Specific Requirements: {target_product}

**Task:** {task_id}
**Source Product:** {source_product}
**Target Product:** {target_product}

---

## {target_product} Product Overview

### Domain

{Describe the target product domain}

### Target Users

- {List primary user personas}
- {List secondary user personas}

### Key Differences from {source_product}

**Business Model:**
- {source_product}: {describe business model}
- {target_product}: {describe business model}

**Use Cases:**
- {source_product}: {describe primary use cases}
- {target_product}: {describe primary use cases}

---

## Product-Specific Requirements

### Functional Requirements

**Required Adaptations:**

1. **{Requirement Category}**
   - Source behavior: {describe}
   - Target behavior: {describe}
   - Reason for difference: {explain}

2. **{Another Category}**
   - Source behavior: {describe}
   - Target behavior: {describe}
   - Reason for difference: {explain}

### Non-Functional Requirements

**Performance:**
- Expected load: {describe}
- Response time targets: {specify}
- Concurrent users: {estimate}

**Security:**
- Authentication: {same as source or different?}
- Authorization: {same roles or different?}
- Data privacy: {any specific requirements}

**Compliance:**
- Regulations: {list applicable regulations}
- Data retention: {policies}
- Audit requirements: {specify}

---

## Integration Points

### Third-Party Services

**{source_product} integrations:**
- Service A: {describe integration}
- Service B: {describe integration}

**{target_product} integrations:**
- Service A: {same, different, or N/A}
- Service B: {same, different, or N/A}
- Service C: {new integration for target product}

### Internal Services

**Shared Services:**
- Auth service: {shared or separate instance}
- Database: {shared or separate}
- Cache: {shared or separate}

**Product-Specific Services:**
- {List services unique to target product}

---

## Data Considerations

### Database Schema

**Shared Tables:**
- {List tables used by both products}
- Isolation strategy: {tenant column, separate schema, etc.}

**Product-Specific Tables:**
- {List tables unique to target product}

### Data Migration

**Required Migrations:**
- [ ] {Describe migration}
- [ ] {Describe migration}

**Data Seeding:**
- [ ] {Describe seed data needed}
- [ ] {Describe seed data needed}

---

## UI/UX Requirements

### Branding Guidelines

**Colors:**
- Primary: {hex code}
- Secondary: {hex code}
- Accent: {hex code}

**Typography:**
- Font family: {font name}
- Heading sizes: {specify}
- Body text: {specify}

**Logo:**
- Location: {file path}
- Sizes needed: {list sizes}
- Usage guidelines: {link to brand guide}

### Navigation Structure

**{source_product} navigation:**
```
- Home
- Feature A
- Feature B
```

**{target_product} navigation:**
```
- Dashboard
- Feature X
- Feature Y
```

### Content Differences

**Terminology:**
- {source_product} term → {target_product} term
- {source_product} term → {target_product} term

**Help Text:**
- {Describe differences in help/tooltip content}

**Error Messages:**
- {Describe product-specific error messages}

---

## Testing Considerations

### Test Accounts

**{target_product} test users:**
- User role: {email} / {password}
- Admin role: {email} / {password}
- Agent role: {email} / {password}

### Test Scenarios

**{target_product}-specific scenarios:**
1. {Describe scenario}
2. {Describe scenario}
3. {Describe scenario}

### Browser/Device Support

**Same as {source_product}?** Yes / No

If different, specify:
- Browsers: {list}
- Devices: {list}
- Viewports: {list}

---

## Deployment Strategy

### Environment Configuration

**{target_product} environments:**
- Development: {URL}
- Staging: {URL}
- Production: {URL}

**Infrastructure:**
- Same containers as {source_product}? Yes / No
- Separate database? Yes / No
- Separate Redis instance? Yes / No

### Rollout Plan

**Phase 1:**
- {Describe initial rollout}
- Audience: {specify}
- Success criteria: {specify}

**Phase 2:**
- {Describe full rollout}
- Audience: {specify}
- Success criteria: {specify}

---

## Success Metrics

### Functional Metrics

- [ ] Feature works as expected for {target_product} users
- [ ] All acceptance criteria met
- [ ] No critical bugs

### Business Metrics

- [ ] User adoption: {target}
- [ ] Engagement: {target}
- [ ] Performance: {target}

---

## Risks & Mitigation

### Identified Risks

**Risk 1: {describe risk}**
- Likelihood: High / Medium / Low
- Impact: High / Medium / Low
- Mitigation: {describe mitigation}

**Risk 2: {describe risk}**
- Likelihood: High / Medium / Low
- Impact: High / Medium / Low
- Mitigation: {describe mitigation}

---

## References

- **Product Spec:** {link}
- **Brand Guidelines:** {link}
- **API Documentation:** {link}
- **Infrastructure Docs:** {link}

---

**Template Version:** 1.0
**Last Updated:** 2025-11-07

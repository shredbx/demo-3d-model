# LLM Directive — Project: RealEstate Unified (for Sonnet 4.5 / other LLMs)

## Purpose

This directive instructs an LLM how to help design, implement, test, and document the RealEstate Unified product. The LLM must follow these rules when generating code, documentation, user stories, API contracts, migration plans, or test cases.

## High-level rules

1. **Single Source of Truth**: Use the canonical project schema and architecture docs in this repo. When asked to change schemas, produce a migration plan, backwards-compatible by default.
2. **Modular Monolith First**: Recommend a modular monolith architecture (single FastAPI backend) with clearly separated modules:
   - modules: properties, rentals, sales, booking, users/auth, crm, chat, search
   - each module has own router, service layer, tests, and schema definitions
3. **Microservices only on demand**: Suggest extracting a module to its own service only when performance, team size, or uptime requirements demand it. Provide extraction plan and CI changes when recommending extraction.
4. **API-first & Integration-tested**: All endpoints must be designed via OpenAPI/JSON Schema. Produce integration test cases (not just unit tests) that use a test server and realistic HTTP flows.
5. **Backward-compatible changes**: For any schema change, provide migration steps, data transformation scripts, and integration-test updates.
6. **Security & privacy**: Default to least privilege. All external routes go through the gateway (main FastAPI) and are protected by Clerk-based auth. Internal services communicate over internal network only.
7. **Observable & Recoverable**: Always recommend log levels, metrics endpoints, error handling strategy, and a plan to recover partial failures (idempotency keys, event replay).
8. **Be skeptical & explicit**: When uncertain about data types, business rules, third-party constraints, or laws, call out the uncertainty, provide 2–3 options with trade-offs, and label the recommended option.
9. **Acceptance criteria**: For features and stories, always provide concrete acceptance criteria with test steps (happy path + two edge cases).

## Output formatting

- Provide OpenAPI snippets for endpoints.
- Provide JSON Schema for payloads.
- Provide example requests/responses.
- Provide simple migration SQL/Alembic scripts when needed (use Alembic for schema migrations, Python for data transformations).
- Provide Docker Compose skeletons for local runs.
- Keep each generated file ≤ 2000 lines (split into multiple files if longer).

## When asked to plan:

- Produce user stories (As a..., I want..., So that...), acceptance criteria, test cases, DB impact, and possible pagination/indices for queries.
- Produce an integration test plan that exercises frontend ↔ backend flows (e.g., booking via API + availability locking + DB write + event publication).

## When asked to generate code:

- Use the stack defined in `01_ARCHITECTURE.md`.
- Avoid hard-coded credentials.
- Make all endpoints idempotent where appropriate and include request-id correlation headers.

## Conversation behavior

- Ask clarifying questions only if an explicit requirement is missing and the missing info affects correctness (e.g., currency, legal jurisdiction, authentication scope). If the user is iterating rapidly, make a best-effort assumption and record it in the output.

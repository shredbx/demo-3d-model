# Architecture Brief — RealEstate Unified

## Goal

A single-company real estate platform covering short-term rentals, long-term leases, sales (land, villa, business-for-sale), and investment projects. Fast iteration, low VPS footprint (4GB target), modular development with easy future extraction to microservices.

## Chosen Stack (justification)

- **Frontend:** SvelteKit 5
  - Reason: fast SSR, small bundle sizes, great DX for progressive hydration.
- **Auth:** Clerk
  - Reason: Managed auth, session management, and role support (agent, admin, user).
- **Backend:** FastAPI (Python) as a modular monolith
  - Reason: Async, lightweight, easy to split into services later, rich ecosystem for testing and OpenAPI generation.
- **DB (primary):** PostgreSQL 16 + pgvector extension
  - Reason: ACID transactions for bookings, referential integrity, JSONB for flexible property attributes, unified vector search via pgvector (1536-dim embeddings). Single database reduces operational complexity and fits 4GB VPS target.
- **Cache/locks/queue:** Redis
  - Reason: Fast availability checks, distributed locks, pub/sub for events, LLM response caching.
- **Object Storage + CDN:** Cloudflare R2 + CDN
  - Reason: Low-cost object store with global delivery.
- **Deployment:** Docker Compose (dev → prod), gateway via Nginx or Caddy, Cloudflare in front.
  - Reason: Simple, reproducible, manageable on 4GB VPS.

## Networking & Access

- Single public gateway (fastapi-main) exposed to the internet.
- All other services (postgres, redis) run in the internal Docker network.
- Use environment variable secrets and Vault/Secrets Manager for prod.

## Dev → Prod Path

- Local development: Docker Compose with PostgreSQL + Redis.
- Staging: small VPS with Compose + managed PostgreSQL (Render/Railway/Supabase optional).
- Production: VPS cluster or managed instance with PostgreSQL (pgvector-enabled), optimized Compose or Kubernetes if scaling needed.
- Migrations: Alembic for schema versioning and zero-downtime deployments.

## CI / Testing

- Use GitHub Actions or Cloud Code CI to:
  - Run unit tests (pytest).
  - Run integration tests against docker-compose test environment (spin up ephemeral services).
  - Publish OpenAPI spec and run contract tests.

## Observability

- Expose metrics endpoint (`/metrics`) for Prometheus scraping.
- Centralized logs (file + optional remote logging aggregation).
- Healthcheck endpoints for each module.

## Notes on costs & scaling

- Start: all self-hosted on one 4GB VPS (~1.6GB footprint: Postgres 800MB, Redis 200MB, FastAPI 300MB, SvelteKit 300MB).
- Grow: move DB to managed PostgreSQL with pgvector support (Render/Supabase/AWS RDS); add read replicas for search-heavy workloads; split services into containers with autoscaling where needed.
- Vector scaling: pgvector IVFFlat indexes support up to 1M vectors; for larger scale, consider HNSW indexes or dedicated vector DB (Qdrant/Pinecone) as a future migration.

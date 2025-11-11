# Bestays Troubleshooting Index

**Purpose**: Quick index of common issues and where to find solutions.

**Pattern**: This file provides POINTERS to troubleshooting information, not the solutions themselves.

---

## How to Use This Index

1. Find your issue category below
2. Follow the pointer to the definitive source
3. If issue not found, add it following the self-update protocol

---

## Environment & Startup Issues

### "make dev fails"

**Symptoms**: `make dev` command fails to start services

**Troubleshooting Path**:

1. Run preflight validation: `bash .sdlc-workflow/scripts/preflight.sh`
2. Check preflight output for specific failure
3. Follow error message instructions
4. See: `.pattern-book/specifications/tech/preflight-validation.md` → Error Handling section

**Common Causes**:

- Docker not running → Start Docker Desktop
- Ports occupied → Stop conflicting processes
- .env missing → Copy from .env.example
- Env vars not set → Check CLERK_SECRET_KEY, OPENROUTER_API_KEY

### "Port already in use"

**Symptoms**: Error about port 8011, 5183, 5433, or 6379 being occupied

**Troubleshooting Path**:

1. Identify process using port: `lsof -Pi :[PORT]`
2. If it's a bestays container: `make down` then `make dev`
3. If it's another process: Kill it or change port in docker-compose.dev.yml

**Definitive Source**: Preflight script handles this → `.sdlc-workflow/scripts/preflight.sh` → check_port_available()

### "Docker daemon not running"

**Symptoms**: Cannot connect to Docker daemon

**Solution**: Start Docker Desktop (macOS) or `sudo systemctl start docker` (Linux)

**See**: Preflight validation → `.pattern-book/specifications/tech/preflight-validation.md` → Check 1

### "Environment variable not set"

**Symptoms**: Missing CLERK_SECRET_KEY, OPENROUTER_API_KEY, etc.

**Troubleshooting Path**:

1. Check .env file exists: `ls -la .env`
2. Check variables are set: `grep CLERK_SECRET_KEY .env`
3. Ensure no placeholder values (no "change_me")
4. Restart services: `make dev`

**Definitive Source**: docker-compose.dev.yml → environment sections for each service

---

## Service-Specific Issues

### Backend (Server) Not Starting

**Symptoms**:

- Health check fails at `http://localhost:8011/api/health`
- Container restarts repeatedly
- Cannot access API docs

**Troubleshooting Path**:

1. Check logs: `make logs-server`
2. Check container status: `docker ps -a | grep bestays-server`
3. Access shell: `make shell-server`
4. Check Python errors in logs
5. Verify database connection

**Common Causes**:

- Database not ready → Wait for postgres health check
- Migration failed → Run `make migrate`
- Missing env vars → Check docker-compose.dev.yml environment
- Python dependencies → Rebuild container `make rebuild`

**Definitive Sources**:

- Logs: `docker-compose logs server`
- Health check: docker-compose.dev.yml → healthcheck section
- Discussion: `.pattern-book/discussions/20251027-2321-infrastructure-setup-deployment-testing-/` → Debugging Workflows

### Frontend Not Loading

**Symptoms**:

- Cannot access `http://localhost:5183`
- White screen
- Build errors in logs

**Troubleshooting Path**:

1. Check logs: `make logs-frontend`
2. Check if Vite dev server started
3. Check for JavaScript errors in logs
4. Verify backend is accessible

**Common Causes**:

- Backend not running → Start with `make dev`
- CORS issues → Check ALLOWED_ORIGINS in docker-compose.dev.yml
- Node modules → Rebuild `make rebuild`
- Vite config → Check apps/frontend/vite.config.ts

**Definitive Sources**:

- Config: apps/frontend/vite.config.ts
- Docker setup: docker-compose.dev.yml → frontend service

### Database Connection Failed

**Symptoms**:

- "Cannot connect to database"
- "Connection refused" errors
- Backend fails to start

**Troubleshooting Path**:

1. Check postgres running: `docker ps | grep bestays-db`
2. Check postgres health: `make shell-db`
3. Verify connection string: `grep DATABASE_URL docker-compose.dev.yml`
4. Check logs: `make logs-db`

**Common Causes**:

- Container not started → `make dev`
- Wrong port → Should be 5433 (host) or 5432 (container-to-container)
- Wrong credentials → Check docker-compose.dev.yml
- Database not initialized → Check init.sql ran

**Definitive Sources**:

- Connection details: docker-compose.dev.yml → postgres service
- Init script: docker/postgres/init.sql

### Redis Connection Issues

**Symptoms**:

- "Cannot connect to Redis"
- Caching not working
- Rate limiting failures

**Troubleshooting Path**:

1. Check redis running: `docker ps | grep bestays-redis`
2. Test connection: `docker-compose exec redis redis-cli ping`
3. Check logs: `make logs-db` (includes redis)

**Common Causes**:

- Container not started → `make dev`
- Wrong URL → Should be redis://redis:6379 (container) or redis://localhost:6379 (host)

**Definitive Source**: docker-compose.dev.yml → redis service

---

## Application-Level Issues

### Chat Not Working

**Symptoms**:

- Chat interface loads but no responses
- "API key not set" errors
- Timeout errors

**Troubleshooting Path**:

1. Check OPENROUTER_API_KEY set: `grep OPENROUTER_API_KEY .env`
2. Check backend logs for API errors: `make logs-server`
3. Test backend health: `curl http://localhost:8011/api/health`
4. Check OpenRouter API status

**Definitive Sources**:

- Spec: `.pattern-book/specifications/integration/openrouter-chat.md`
- Backend implementation: apps/server/src/server/api/

### Authentication Errors

**Symptoms**:

- Cannot login
- "Invalid token" errors
- Clerk errors

**Troubleshooting Path**:

1. Check CLERK_SECRET_KEY: `grep CLERK_SECRET_KEY .env`
2. Check backend logs: `make logs-server`
3. Verify Clerk dashboard configuration
4. Check frontend has VITE_CLERK_PUBLISHABLE_KEY

**Definitive Sources**:

- Env vars: docker-compose.dev.yml → server and frontend services
- Clerk docs: https://clerk.com/docs

---

## Docker & Container Issues

### "Container keeps restarting"

**Symptoms**: Container status shows "Restarting" or exits immediately

**Troubleshooting Path**:

1. Check logs for crash reason: `docker logs [container-name]`
2. Check health check: docker-compose.dev.yml → healthcheck
3. Check dependencies: Ensure db/redis started first
4. Check resource limits

**Common Causes**:

- Application crash → Check logs
- Failed health check → Fix health endpoint
- Missing dependencies → Check depends_on in docker-compose
- Out of memory → Check Docker Desktop resources

### "Volume mount issues"

**Symptoms**:

- Changes not reflected in container
- Permission errors
- Files missing in container

**Troubleshooting Path**:

1. Check volume mounts: docker-compose.dev.yml → volumes
2. Verify files exist on host
3. Check Docker Desktop file sharing settings (macOS)
4. Rebuild if needed: `make rebuild`

**Definitive Source**: docker-compose.dev.yml → volumes sections

### "Image build fails"

**Symptoms**: `docker-compose build` fails

**Troubleshooting Path**:

1. Check Dockerfile syntax
2. Check base image availability
3. Check network connectivity
4. Clear cache and rebuild: `docker-compose build --no-cache`

**Definitive Sources**:

- Backend Dockerfile: docker/server/Dockerfile.dev
- Frontend Dockerfile: docker/frontend/Dockerfile.dev

---

## Performance Issues

### "Slow startup time"

**Symptoms**: Services take >60 seconds to start

**Troubleshooting Path**:

1. Check disk space: `df -h`
2. Check Docker Desktop resources (CPU, RAM)
3. Check for image pulls (first time)
4. Review container logs for slow operations

**See**: `.pattern-book/specifications/tech/preflight-validation.md` → Performance Considerations

### "High memory usage"

**Symptoms**: System becomes slow, Docker uses excessive RAM

**Troubleshooting Path**:

1. Check container stats: `docker stats`
2. Identify memory-heavy container
3. Check for memory leaks in logs
4. Consider increasing Docker Desktop memory limit

---

## Development Workflow Issues

### "Hot reload not working"

**Symptoms**: Code changes don't appear without restart

**Troubleshooting Path**:

1. Verify volume mounts in docker-compose.dev.yml
2. Check dev server logs
3. For backend: Uvicorn should show --reload flag
4. For frontend: Vite should detect changes

**Definitive Sources**:

- Backend command: docker-compose.dev.yml → server → command
- Frontend command: docker-compose.dev.yml → frontend → command

### "make command not found"

**Symptoms**: Cannot run Makefile commands

**Solution**: Ensure you're in project root directory with Makefile

**See**: `Makefile` → All available commands

---

## Integration & API Issues

### "CORS errors"

**Symptoms**: "Access-Control-Allow-Origin" errors in browser console

**Troubleshooting Path**:

1. Check ALLOWED_ORIGINS in docker-compose.dev.yml
2. Verify frontend URL matches allowed origin
3. Check CORS middleware in backend

**Definitive Source**: docker-compose.dev.yml → server → environment → ALLOWED_ORIGINS

### "API endpoint not found"

**Symptoms**: 404 errors for API calls

**Troubleshooting Path**:

1. Check API docs: http://localhost:8011/docs
2. Verify endpoint path and prefix
3. Check API_V1_PREFIX in env vars

**Definitive Sources**:

- API routes: apps/server/src/server/api/
- Integration spec: `.pattern-book/specifications/integration/openrouter-chat.md`

---

## Pattern-Book System Issues

### "Cannot find spec"

**Symptoms**: Looking for specification but can't locate it

**Solution**:

1. Check SPECS-INDEX: `.pattern-book/SPECS-INDEX.md`
2. Search by tag/module: `.pattern-book/scripts/specifications/find-spec.sh [query]`

### "Discussion not indexed"

**Symptoms**: Discussion exists but not in index

**Solution**:

1. Check DISCUSSIONS-INDEX: `.pattern-book/DISCUSSIONS-INDEX.md`
2. Manually add if missing

---

## Self-Update Protocol

**When You Encounter a New Issue**:

1. Troubleshoot and document solution
2. Add entry to this index following the pattern:

   ```markdown
   ### "[Issue Title]"

   **Symptoms**: [What user sees/experiences]

   **Troubleshooting Path**: [Step-by-step diagnosis]

   **Common Causes**: [Typical root causes]

   **Definitive Source**: [Where solution is documented]
   ```

3. Update relevant spec if needed
4. Commit to skill

**Pattern Rules**:

- Provide POINTERS, not complete solutions
- Link to authoritative sources
- Keep troubleshooting paths actionable
- Update component map if new component discovered

---

**Last Updated**: 2025-10-28
**Maintainer**: bestays-devenv skill (self-updating)

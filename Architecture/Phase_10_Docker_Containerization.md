# AMW Django ERP - Phase Execution Plan: Phase 10

## 1. Document Purpose

This file is the working execution plan for Phase 10: Docker & Containerization.

It must be used together with:
- `Constitution_AMW_DJ_ERP.md`
- The current repository state
- Ahmad's latest instructions for the phase

---

## 2. Phase Identity

- **Phase Number:** `Phase 10`
- **Phase Name:** `Docker & Containerization`
- **Branch Name:** `Phase-10-Docker`
- **Status:** ✅ **IN PROGRESS**
- **Primary Goal:** `Dockerize the application, set up Docker Hub registry, and prepare for Render deployment.`
- **Depends On:** `Phase 9` (DRF must be complete first)
- **Manager Approval Required:** `Yes`
- **Completion Date:** `TBD`
- **Merge Date:** `TBD`

---

## 3. Phase Scope

### In Scope

- Optimize Dockerfile for production
- Create GitHub Actions workflow to build and push Docker images to Docker Hub
- Add `.dockerignore` to reduce image size
- Create separate `docker-compose.prod.yml` for production
- Document Docker Hub repository setup

### Out of Scope

- Render deployment configuration (Phase 11)
- Supabase integration (Phase 11)
- Kubernetes or advanced orchestration
- Multi-region deployment

### Required Outcomes

- Docker image builds successfully
- Image is pushed to Docker Hub on tag/release
- Production docker-compose works standalone
- Documentation for running Docker locally

---

## 4. Constitutional Alignment

### Mandatory Checks

- **Stack & Tools:** Follow existing Docker patterns (Section 11.2)
- **Utility Scripts:** Use `infra_manage.sh` for Docker operations
- **Security:** No secrets in Docker images, use environment variables

---

## 5. Architecture Targets

### Files Affected

- `Dockerfile` — Optimize for production
- `docker-compose.yml` — Already exists
- `docker-compose.prod.yml` — NEW production config
- `.dockerignore` — NEW to reduce image size
- `.github/workflows/docker.yml` — NEW GitHub Actions workflow
- `README.md` — Update Docker instructions

### Operational Impact

- Automated Docker image builds on push to master
- Images available on Docker Hub for Pull deployment
- Render can pull from Docker Hub

---

## 6. Implementation Strategy

### Phase Strategy Summary

1. **Optimize:** Improve Dockerfile for smaller, faster builds
2. **Ignore:** Add .dockerignore to exclude unnecessary files
3. **Workflow:** Create GitHub Actions for Docker Hub push
4. **Production:** Create standalone production docker-compose
5. **Document:** Update README with Docker instructions

### Sequencing Rule

1. Add .dockerignore
2. Optimize Dockerfile
3. Create GitHub Actions workflow
4. Create production docker-compose
5. Update README
6. Test locally and verify workflow

---

## 7. Parts Breakdown

### Part 1: Docker Optimization

- **Goal:** `Optimize Dockerfile for production efficiency`
- **Owner:** `Agent`
- **Status:** ⏳ **PENDING**

#### Tasks

1. **Task 10.1.1:** `Create .dockerignore`
   - Output: `.dockerignore excludes __pycache__, .git, node_modules, etc.`
   - Verification: `Docker build excludes unnecessary files`

2. **Task 10.1.2:** `Optimize Dockerfile with multi-stage build improvements`
   - Output: `Final production-optimized Dockerfile`
   - Verification: `Image builds and runs successfully`

---

### Part 2: GitHub Actions Workflow

- **Goal:** `Create automated Docker Hub push workflow`
- **Owner:** `Agent`
- **Status:** ⏳ **PENDING**

#### Tasks

1. **Task 10.2.1:** `Create .github/workflows/docker.yml`
   - Output: `Workflow to build and push to Docker Hub on tag`
   - Verification: `Workflow runs on git tag push`

2. **Task 10.2.2:** `Add Docker Hub secrets to GitHub`
   - Output: `DOCKER_USERNAME and DOCKER_PASSWORD secrets configured`
   - Verification: `GitHub Actions can push to Docker Hub`

---

### Part 3: Production Docker Compose

- **Goal:** `Create production-ready docker-compose`
- **Owner:** `Agent`
- **Status:** ⏳ **PENDING**

#### Tasks

1. **Task 10.3.1:** `Create docker-compose.prod.yml`
   - Output: `Production config with gunicorn, no volume mounts`
   - Verification: `docker-compose -f docker-compose.prod.yml up works`

2. **Task 10.3.2:** `Update .env.example with Docker variables`
   - Output: `Environment variables documented for Docker`
   - Verification: `Variables are clear for production deployment`

---

### Part 4: Documentation

- **Goal:** `Update README with Docker instructions`
- **Owner:** `Agent`
- **Status:** ⏳ **PENDING**

#### Tasks

1. **Task 10.4.1:** `Update README.md Docker section`
   - Output: `README documents: build, run, push workflows`
   - Verification: `README is clear for new developers`

2. **Task 10.4.2:** `Create DOCKER.md with detailed guide`
   - Output: `Detailed Docker guide in docs/ or DOCKER.md`
   - Verification: `Guide covers all common operations`

---

### Part 5: Verification

- **Goal:** `Verify Docker setup works correctly`
- **Owner:** `Agent`
- **Status:** ⏳ **PENDING**

#### Tasks

1. **Task 10.5.1:** `Build Docker image locally`
   - Output: `docker build completes successfully`
   - Verification: `Image size is reasonable (<500MB)`

2. **Task 10.5.2:** `Test docker-compose services`
   - Output: `All services start correctly`
   - Verification: `curl localhost:8010/health returns 200`

3. **Task 10.5.3:** `Verify GitHub Actions workflow syntax`
   - Output: `Workflow is syntactically correct`
   - Verification: `No YAML errors in workflow file`

---

## 8. Notes

### Docker Hub Naming Convention

Images will be pushed as:
```
docker.io/{DOCKER_USERNAME}/amw-django-erp:{tag}
```

Example:
```
docker.io/amwuser/amw-django-erp:v0.9.0
```

### GitHub Actions Triggers

| Trigger | Action |
|---------|--------|
| `v*.*.*` tag push | Build and push to Docker Hub |
| `master` branch push | Build and push `latest` |
| Pull request | Build for testing (no push) |

---

## 9. Docker Commands Reference

```bash
# Build locally
docker build -t amw-django-erp:latest .

# Run locally
docker-compose up -d

# Tag for Docker Hub
docker tag amw-django-erp:latest amwuser/amw-django-erp:v0.10.0

# Push to Docker Hub
docker push amwuser/amw-django-erp:v0.10.0

# Run from Docker Hub
docker pull amwuser/amw-django-erp:latest
docker run -p 8010:8010 amwuser/amw-django-erp:latest
```

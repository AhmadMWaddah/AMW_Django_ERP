# AMW Django ERP - Phase Execution Plan: Phase 11

## 1. Document Purpose

This file is the working execution plan for Phase 11: Render Deployment.

It must be used together with:
- `Constitution_AMW_DJ_ERP.md`
- The current repository state
- Ahmad's latest instructions for the phase

---

## 2. Phase Identity

- **Phase Number:** `Phase 11`
- **Phase Name:** `Render Deployment`
- **Branch Name:** `phase-11`
- **Status:** ✅ **COMPLETE**
- **Primary Goal:** `Deploy the Django application to Render, pulling from Docker Hub, with environment configuration.`
- **Depends On:** `Phase 10` (Docker must be complete first)
- **Manager Approval Required:** `Yes`
- **Completion Date:** `2026-04-27`
- **Merge Date:** `2026-04-27`

---

## 3. Phase Scope

### In Scope

- Create Render account
- Connect GitHub repository to Render
- Configure Render to pull from Docker Hub
- Set environment variables on Render
- Deploy web service
- Configure health checks
- Set up logging

### Out of Scope

- Production SSL certificates (Render provides)
- Custom domain setup (optional future)
- Database migration to Supabase (Phase 12)

### Required Outcomes

- Application deployed and accessible on Render
- Health endpoint responding
- Logs viewable in Render dashboard
- Environment variables properly configured

---

## 4. Constitutional Alignment

### Mandatory Checks

- **Stack & Tools:** Keep PostgreSQL as database (Section 11.1)
- **Environment:** Use environment variables for all secrets
- **Security:** Never commit secrets to git

---

## 5. Architecture Targets

### Services Used

- `Render.com` — Web hosting platform
- `Docker Hub` — Container registry (from Phase 10)

### Files to Configure

- Render dashboard settings
- Environment variables on Render
- Health check endpoint

### Operational Impact

- Application publicly accessible at `*.onrender.com`
- Can demonstrate live deployment
- CI/CD can be configured for auto-deploy

---

## 6. Implementation Strategy

### Phase Strategy Summary

1. **Account:** Create Render account and connect GitHub
2. **Configure:** Set up web service with Docker Hub image
3. **Environment:** Add environment variables
4. **Deploy:** Deploy and verify
5. **Verify:** Check health and logs

### Sequencing Rule

1. Create account / Sign in to Render
2. Create new Web Service
3. Configure to pull from Docker Hub
4. Add environment variables
5. Deploy and wait for build
6. Verify application works

---

## 7. Parts Breakdown

### Part 1: Render Account Setup

- **Goal:** `Create Render account and connect repository`
- **Owner:** `Agent`
- **Status:** ✅ **COMPLETE**

#### Tasks

1. **Task 11.1.1:** `Create or sign in to Render account`
   - Output: `Account at render.com`
   - Verification: `Can access Render dashboard`

2. **Task 11.1.2:** `Connect GitHub repository`
   - Output: `Repository connected in Render`
   - Verification: `Repositories list shows amw-django-erp`

---

### Part 2: Web Service Configuration

- **Goal:** `Configure web service to pull from Docker Hub`
- **Owner:** `Agent`
- **Status:** ✅ **COMPLETE**

#### Tasks

1. **Task 11.2.1:** `Create new Web Service on Render`
   - Output: `Web service configured`
   - Verification: `Service shows in Render dashboard`

2. **Task 11.2.2:** `Configure Docker Hub image`
   - Output: `Image path: docker.io/{USERNAME}/amw-django-erp:latest`
   - Verification: `Render can pull image`

3. **Task 11.2.3:** `Set environment variables`
   - Output: `DB_HOST, DB_PORT, SECRET_KEY, ALLOWED_HOSTS configured`
   - Verification: `Environment variables set`

4. **Task 11.2.4:** `Configure health check`
   - Output: `Health check at /health/ or /health`
   - Verification: `Health check passes`

---

### Part 3: Deployment & Verification

- **Goal:** `Deploy and verify application works`
- **Owner:** `Agent`
- **Status:** ✅ **COMPLETE**

#### Tasks

1. **Task 11.3.1:** `Deploy web service`
   - Output: `Deployment triggered`
   - Verification: `Service status is "Live"`

2. **Task 11.3.2:** `Verify application loads`
   - Output: `Can access homepage`
   - Verification: `curl {app}.onrender.com returns 200`

3. **Task 11.3.3:** `Check logs in dashboard`
   - Output: `Logs viewable`
   - Verification: `No error logs in first minute`

---

### Part 4: Documentation

- **Goal:** `Document Render deployment process`
- **Owner:** `Agent`
- **Status:** ✅ **COMPLETE**

#### Tasks

1. **Task 11.4.1:** `Create RENDER.md deployment guide`
   - Output: `Complete guide in docs/`
   - Verification: `Guide covers all steps`

2. **Task 11.4.2:** `Update README with deployment info`
   - Output: `README mentions deployment`
   - Verification: `URL and steps documented`
   - Verification: `Guide covers all steps`

2. **Task 11.4.2:** `Update README with deployment info`
   - Output: `README mentions deployment`
   - Verification: `URL and steps documented`

---

## 8. Notes

### Render Free Tier Limitations

| Resource | Free Limit |
|----------|------------|
| Web Service | 750 hours/month |
| Sleep | Sleeps after 15 min inactivity |
| Build | 5 GB bandwidth |
| Static Files | 1 GB |

**Note:** Free tier services sleep after 15 minutes of inactivity.

### Environment Variables Required

```bash
# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=amw_django_erp
DB_USER=amw_erp_user
DB_PASSWORD=[RENDER_SECRET]
DB_HOST=[.internal-address]
DB_PORT=5432

# Redis
REDIS_URL=redis://:[internal-address]/0

# Django
DJANGO_SECRET_KEY=[RENDER_SECRET]
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=[app].onrender.com
```

### Internal Networking

Render provides internal networking for PostgreSQL. Use the internal address (not external) for database connection.

---

## 9. Commands Reference

```bash
# SSH into Render service (if needed)
render ssh [service-name]

# View logs (dashboard or CLI)
render logs [service-name]

# Trigger deployment
# Push to GitHub or Docker Hub, then trigger in dashboard

# Check service status
render services list
```

---

## 10. Render vs Local Development

| Aspect | Local Docker | Render |
|---------|-------------|--------|
| **Access** | localhost:8010 | *.onrender.com |
| **Database** | Local PostgreSQL | Render PostgreSQL or Supabase |
| **SSL** | HTTP | HTTPS (auto) |
| **Sleep** | No | Yes (free tier) |
| **Cost** | Free | Free tier available |
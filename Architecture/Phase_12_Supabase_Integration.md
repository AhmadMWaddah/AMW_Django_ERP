# AMW Django ERP - Phase Execution Plan: Phase 12

## 1. Document Purpose

This file is the working execution plan for Phase 12: Supabase Integration.

It must be used together with:
- `Constitution_AMW_DJ_ERP.md`
- The current repository state
- Ahmad's latest instructions for the phase

---

## 2. Phase Identity

- **Phase Number:** `Phase 12`
- **Phase Name:** `Supabase Integration`
- **Branch Name:** `phase-12`
- **Status:** ⏳ **PLANNED**
- **Primary Goal:** `Integrate Supabase as a managed PostgreSQL backup/external database while keeping local Docker PostgreSQL for development.`
- **Depends On:** `Phase 11` (Render deployment must be complete first)
- **Manager Approval Required:** `Yes`
- **Completion Date:** `TBD`
- **Merge Date:** `TBD`

---

## 3. Phase Scope

### In Scope

- Create Supabase account and project
- Configure Django to connect to Supabase PostgreSQL
- Add Supabase connection string to environment variables
- Document Supabase setup process
- Test Django with Supabase database
- Keep local Docker PostgreSQL for development

### Out of Scope

- Replacing local development database (optional future task)
- Supabase Authentication integration
- Supabase Realtime features
- Migrating all data to Supabase permanently

### Required Outcomes

- Django can connect to Supabase PostgreSQL
- Environment variables configured for both local and Supabase
- Documentation for Supabase setup
- Ability to switch between local and Supabase DB

---

## 4. Constitutional Alignment

### Mandatory Checks

- **Stack & Tools:** Keep PostgreSQL as primary (Section 11.1)
- **Environment Rule:** Use environment variables for Supabase connection
- **Security:** Never commit Supabase credentials to git

---

## 5. Architecture Targets

### Files Affected

- `.env` — Add Supabase connection string
- `.env.example` — Document Supabase variables
- `config/settings/` — Add Supabase database configuration
- `README.md` — Update with Supabase instructions
- `docs/SUPABASE.md` — NEW setup guide

### Operational Impact

- Can deploy to production using Supabase managed database
- External connections to database possible
- Backup option if Docker fails
- Learning opportunity for Supabase

---

## 6. Implementation Strategy

### Phase Strategy Summary

1. **Create:** Set up Supabase account and project
2. **Configure:** Add Supabase connection to Django settings
3. **Document:** Write Supabase setup guide
4. **Test:** Verify Django connects to Supabase
5. **Backup:** Use Supabase as secondary/backup database

### Sequencing Rule

1. Create Supabase account
2. Create new Supabase project
3. Get connection string
4. Configure Django settings
5. Test connection
6. Document process

---

## 7. Parts Breakdown

### Part 1: Supabase Setup

- **Goal:** `Create Supabase account and project`
- **Owner:** `Agent`
- **Status:** ⏳ **PENDING**

#### Tasks

1. **Task 11.1.1:** `Create Supabase account`
   - Output: `Account created at supabase.com`
   - Verification: `Can log in to Supabase dashboard`

2. **Task 11.1.2:** `Create new Supabase project`
   - Output: `New project with PostgreSQL database`
   - Verification: `Project shows "Healthy" status`

3. **Task 11.1.3:** `Get Supabase connection string`
   - Output: `PostgreSQL connection string from settings`
   - Verification: `Can connect using psql or admin tool`

---

### Part 2: Django Configuration

- **Goal:** `Configure Django to connect to Supabase`
- **Owner:** `Agent`
- **Status:** ⏳ **PENDING**

#### Tasks

1. **Task 11.2.1:** `Add Supabase environment variables to .env`
   - Output: `DB_SUPABASE_URL and DB_SUPABASE_KEY variables`
   - Verification: `.env is updated (not committed)`

2. **Task 11.2.2:** `Update settings to support Supabase`
   - Output: `Settings can switch between local and Supabase DB`
   - Verification: `Django check passes with Supabase config`

3. **Task 11.2.3:** `Run migrations on Supabase`
   - Output: `All migrations apply to Supabase database`
   - Verification: `python manage.py migrate succeeds`

---

### Part 3: Documentation

- **Goal:** `Document Supabase setup and usage`
- **Owner:** `Agent`
- **Status:** ⏳ **PENDING**

#### Tasks

1. **Task 11.3.1:** `Create docs/SUPABASE.md`
   - Output: `Complete guide to Supabase setup`
   - Verification: `Guide covers account creation to first connection`

2. **Task 11.3.2:** `Update .env.example`
   - Output: `Documented variables for Supabase connection`
   - Verification: `Variables are clearly explained`

3. **Task 11.3.3:** `Update README.md`
   - Output: `README mentions Supabase option`
   - Verification: `Instructions are clear`

---

### Part 4: Verification

- **Goal:** `Verify Supabase integration works`
- **Owner:** `Agent`
- **Status:** ⏳ **PENDING**

#### Tasks

1. **Task 11.4.1:** `Test Django with Supabase database`
   - Output: `Django connects and serves pages from Supabase`
   - Verification: `Can access /admin/ on Supabase-connected instance`

2. **Task 11.4.2:** `Test local dev still works`
   - Output: `Local Docker PostgreSQL still works`
   - Verification: `Can run both configurations`

3. **Task 11.4.3:** `Verify secrets are not in git`
   - Output: `No Supabase credentials in repository`
   - Verification: `.env is in .gitignore`

---

## 8. Notes

### Supabase Connection String Format

```
postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT].supabase.co:5432/postgres
```

### Environment Variables

```bash
# Supabase (Production/Staging)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=[YOUR-PASSWORD]
DB_HOST=db.[YOUR-PROJECT].supabase.co
DB_PORT=5432
```

### Switching Between Local and Supabase

For development, keep using local Docker PostgreSQL. For deployment, switch to Supabase by changing environment variables.

### Free Tier Limits

| Resource | Free Limit |
|----------|-------------|
| Database | 500MB |
| Bandwidth | 2GB/month |
| Projects | 2 |
| API Requests | Unlimited |

---

## 9. Supabase vs Local PostgreSQL

| Aspect | Local Docker | Supabase |
|--------|-------------|----------|
| **Setup** | Manual (Phase 2) | Auto-provisioned |
| **Maintenance** | You manage | Managed by Supabase |
| **Backups** | Manual | Automatic |
| **External Access** | Requires config | Built-in |
| **Cost** | Free | Free tier available |
| **Best For** | Development | Staging/Production |

---

## 10. Commands Reference

```bash
# Connect to Supabase from local machine
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres"

# Test Django with Supabase
DB_HOST=db.[PROJECT].supabase.co DB_PASSWORD=[PASSWORD] python manage.py check

# Run migrations on Supabase
DB_HOST=db.[PROJECT].supabase.co DB_PASSWORD=[PASSWORD] python manage.py migrate
```

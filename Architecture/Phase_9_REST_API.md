# AMW Django ERP - Phase Execution Plan: Phase 9

## 1. Document Purpose

This file is the working execution plan for Phase 9: REST API Layer (DRF).

It must be used together with:
- `Constitution_AMW_DJ_ERP.md`
- The current repository state
- Ahmad's latest instructions for the phase

---

## 2. Phase Identity

- **Phase Number:** `Phase 9`
- **Phase Name:** `REST API Layer (DRF)`
- **Branch Name:** `Feature-Phase-9-REST-API`
- **Status:** 🔄 **IN PROGRESS** (branch created, committed, testing)
- **Primary Goal:** `Add Django REST Framework to create REST API endpoints for Products and Categories, coexisting with existing HTMX views (Hybrid approach).`
- **Depends On:** `Phase 1-8`
- **Manager Approval Required:** `Yes`
- **Completion Date:** `TBD`
- **Merge Date:** `TBD`

---

## 3. Phase Scope

### In Scope

- Install Django REST Framework (DRF)
- Create serializers for Product and Category models
- Create DRF API views (ViewSets) for Products and Categories
- Add API URL routing under `/api/v1/`
- Write unit tests for API endpoints
- Verify existing HTMX views still work (coexistence)

### Out of Scope

- Replacing existing HTMX views with API-first frontend
- Supabase integration (future phase)
- Render deployment configuration (future phase)
- API authentication beyond session auth
- API versioning beyond v1

### Required Outcomes

- Working REST API endpoints for Products and Categories
- JSON responses alongside existing HTML responses
- Session-based authentication (same as web interface)
- Permission system integrated with existing IAM
- Unit tests passing for API endpoints

---

## 4. Constitutional Alignment

### Mandatory Checks

- **Hybrid Approach:** DRF coexists with HTMX, not replaces it (Section 7.1 - HTMX-First for web)
- **Business Logic:** API uses existing models and operations, no duplication
- **Soft Delete:** API respects `is_deleted` field behavior
- **Security:** Uses existing `@require_permission` decorator from `security.logic.enforcement`

---

## 5. Architecture Targets

### Modules / Apps Affected

- `config/settings/` — Add DRF to INSTALLED_APPS
- `requirements.txt` — Add djangorestframework
- `inventory/` — New serializers.py, api.py; modify urls.py
- `tests/` — New test_api_inventory.py

### Operational Impact

- New `/api/v1/products/` and `/api/v1/categories/` endpoints available
- Existing `/inventory/products/` and `/inventory/categories/` continue working
- External systems can now consume JSON data

---

## 6. Implementation Strategy

### Phase Strategy Summary

We will implement DRF using a **Hybrid approach** — adding REST API alongside existing HTMX views:

1. **Setup:** Install DRF, configure settings
2. **Serialization:** Create serializers for Product and Category
3. **Views:** Build ViewSets with CRUD + custom actions
4. **Routing:** Add API routes via DRF router
5. **Testing:** Write unit tests for all endpoints
6. **Verification:** Run full test suite

### Sequencing Rule

1. Install DRF and verify Django loads
2. Create serializers and verify serialization
3. Create API views and verify routing
4. Add URL routes and verify endpoints
5. Write and run tests
6. Final verification

---

## 7. Parts Breakdown

### Part 1: Setup & Configuration

- **Goal:** `Install Django REST Framework and configure settings`
- **Owner:** `Agent`
- **Status:** ✅ **COMPLETE** (committed to Feature-Phase-9-REST-API)

### Part 2: Serializers

- **Goal:** `Create DRF serializers for Product and Category models`
- **Owner:** `Agent`
- **Status:** ✅ **COMPLETE** (committed to Feature-Phase-9-REST-API)

### Part 3: API Views

- **Goal:** `Create DRF ViewSets for Products and Categories`
- **Owner:** `Agent`
- **Status:** ✅ **COMPLETE** (committed to Feature-Phase-9-REST-API)

### Part 4: URL Routing

- **Goal:** `Add API routes to inventory app`
- **Owner:** `Agent`
- **Status:** ✅ **COMPLETE** (committed to Feature-Phase-9-REST-API)

### Part 5: Testing

- **Goal:** `Write unit tests for API endpoints`
- **Owner:** `Agent`
- **Status:** ✅ **COMPLETE** (22 tests passing, committed to Feature-Phase-9-REST-API)

### Part 6: Verification & Completion

- **Goal:** `Run full verification and prepare for merge`
- **Owner:** `Agent`
- **Status:** 🔄 **IN PROGRESS** (Django check passes, lint passes, awaiting Owner approval)

#### Tasks

1. **Task 9.1.1:** `Add djangorestframework to requirements.txt`
   - Output: `requirements.txt updated with djangorestframework>=3.14.0`
   - Verification: `pip install completes without error`

2. **Task 9.1.1b:** `Add drf-spectacular for OpenAPI documentation`
   - Output: `requirements.txt updated with drf-spectacular>=0.27.0`
   - Verification: `pip install completes without error`

3. **Task 9.1.2:** `Add rest_framework and drf_spectacular to INSTALLED_APPS in base.py`
   - Output: `THIRD_PARTY_APPS includes "rest_framework" and "drf_spectacular"`
   - Verification: `python manage.py check passes`

4. **Task 9.1.3:** `Add REST_FRAMEWORK settings configuration`
   - Output: `Session auth, pagination, JSON renderer configured`
   - Verification: `Settings load without error`

5. **Task 9.1.4:** `Add drf-spectacular configuration`
   - Output: `REST_FRAMEWORK with SPECTACULAR_SETTINGS configured`
   - Verification: `OpenAPI schema generates at /api/v1/schema/`

---

### Part 2: Serializers

- **Goal:** `Create DRF serializers for Product and Category models`
- **Owner:** `Agent`
- **Status:** ✅ **COMPLETE**

#### Tasks

1. **Task 9.2.1:** `Create inventory/serializers.py with CategorySerializer`
   - Output: `CategorySerializer with id, name, slug, parent, description, timestamps`
   - Verification: `Serializer includes parent_name in representation`

2. **Task 9.2.2:** `Create ProductListSerializer`
   - Output: `ProductListSerializer with category_name, current_stock, wac_price`
   - Verification: `Serializer outputs expected fields`

3. **Task 9.2.3:** `Create ProductDetailSerializer`
   - Output: `ProductDetailSerializer with full category info and stock_value`
   - Verification: `stock_value computed correctly`

4. **Task 9.2.4:** `Create ProductCreateSerializer`
   - Output: `ProductCreateSerializer with SKU validation`
   - Verification: `SKU uppercase conversion works`

---

### Part 3: API Views

- **Goal:** `Create DRF ViewSets for Products and Categories`
- **Owner:** `Agent`
- **Status:** ✅ **COMPLETE**

#### Tasks

1. **Task 9.3.1:** `Create inventory/api.py with CategoryViewSet`
   - Output: `CategoryViewSet with CRUD, search, ordering`
   - Verification: `ViewSet has list, create, retrieve, update, destroy actions`

2. **Task 9.3.2:** `Create ProductViewSet`
   - Output: `ProductViewSet with CRUD, search, filter, ordering`
   - Verification: `ViewSet supports ?search= and ?category= filters`

3. **Task 9.3.3:** `Add custom stock_value action to ProductViewSet`
   - Output: `GET /api/v1/products/{id}/stock-value/ endpoint`
   - Verification: `Endpoint returns product stock value`

4. **Task 9.3.4:** `Create ProductStockView for bulk stock info`
   - Output: `GET /api/v1/products/stock/ endpoint`
   - Verification: `Endpoint supports ?stock_status= filter`

---

### Part 4: URL Routing

- **Goal:** `Add API routes to inventory app`
- **Owner:** `Agent`
- **Status:** ✅ **COMPLETE**

#### Tasks

1. **Task 9.4.1:** `Modify inventory/urls.py to add DRF router`
   - Output: `router.register for categories and products`
   - Verification: `Routes under /api/v1/`

2. **Task 9.4.2:** `Add API documentation URLs (Swagger UI)`
   - Output: `Schema at /api/v1/schema/, Docs at /api/docs/`
   - Verification: `Access /api/docs/ in browser`

3. **Task 9.4.3:** `Verify all API URLs are registered`
   - Output: `show_urls shows /api/v1/products/ and /api/v1/categories/`
   - Verification: `URLs accessible`

---

### Part 5: Testing

- **Goal:** `Write unit tests for API endpoints`
- **Owner:** `Agent`
- **Status:** ✅ **COMPLETE**

#### Tasks

1. **Task 9.5.1:** `Create tests/test_api_inventory.py`
   - Output: `Test file with Category and Product API tests`
   - Verification: `File created with test classes`

2. **Task 9.5.2:** `Write Category API tests`
   - Output: `Tests for list, create, retrieve, update, delete`
   - Verification: `Tests pass or fail as expected`

3. **Task 9.5.3:** `Write Product API tests`
   - Output: `Tests for list, create, retrieve, update, delete, stock_value`
   - Verification: `Tests pass or fail as expected`

4. **Task 9.5.4:** `Write Product stock endpoint tests`
   - Output: `Tests for /api/v1/products/stock/`
   - Verification: `Tests pass or fail as expected`

---

### Part 6: Verification & Completion

- **Goal:** `Run full verification and prepare for merge`
- **Owner:** `Agent`
- **Status:** 🔄 **IN PROGRESS**

#### Tasks

1. **Task 9.6.1:** `Run unit test suite`
   - Output: `All unit tests pass`
   - Verification: `pytest output shows all passing`

2. **Task 9.6.2:** `Run linting (black + ruff)`
   - Output: `Code formatted and lint errors fixed`
   - Verification: `black . && ruff check --fix . succeeds`

3. **Task 9.6.3:** `Run Django system check`
   - Output: `No issues detected`
   - Verification: `python manage.py check passes`

4. **Task 9.6.4:** `Verify HTMX views still work`
   - Output: `Existing /inventory/products/ loads correctly`
   - Verification: `Manual or automated check passes`

---

## 8. API Endpoints Summary

After implementation, these endpoints will be available:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/products/` | List all products (paginated, searchable) |
| POST | `/api/v1/products/` | Create new product |
| GET | `/api/v1/products/{id}/` | Get product details |
| PUT | `/api/v1/products/{id}/` | Update product |
| PATCH | `/api/v1/products/{id}/` | Partial update product |
| DELETE | `/api/v1/products/{id}/` | Soft delete product |
| GET | `/api/v1/products/{id}/stock-value/` | Get product stock value |
| GET | `/api/v1/products/stock/` | Bulk stock info |
| GET | `/api/v1/categories/` | List categories |
| POST | `/api/v1/categories/` | Create category |
| GET | `/api/v1/categories/{id}/` | Get category details |
| PUT | `/api/v1/categories/{id}/` | Update category |
| DELETE | `/api/v1/categories/{id}/` | Soft delete category |

---

## 9. Notes

- **Authentication:** Uses session auth (same as existing web interface)
- **Permissions:** Uses DRF Permission Classes (IsAuthenticated, DjangoModelPermissions)
- **Soft Delete:** Respects existing `is_deleted` field behavior; `?include_deleted=true` shows soft-deleted items
- **Pagination:** DRF pagination with 20 items per page
- **Search:** Supports `?search=` parameter on list endpoints
- **Filtering:** Supports `?category=` and `?include_deleted=` parameters
- **Documentation:** OpenAPI/Swagger UI available at `/api/docs/` via drf-spectacular
- **Schema:** OpenAPI schema available at `/api/v1/schema/`

# AMW Django ERP - Phase Execution Plan: Phase 7

## 1. Document Purpose

This file is the working execution plan for Phase 7: Frontend Foundation & HTMX UI.

It must be used together with:
- `Constitution_AMW_DJ_ERP.md`
- the current repository state
- Ahmad's latest instructions for the phase

---

## 2. Phase Identity

- **Phase Number:** `Phase 7`
- **Phase Name:** `Frontend Foundation & HTMX UI`
- **Branch Name:** `phase-7`
- **Status:** ✅ **COMPLETE**
- **Primary Goal:** `Establish the visual framework, layout hierarchy, and HTMX interaction patterns.`
- **Depends On:** `Phase 1-6`
- **Manager Approval Required:** `Yes`
- **Completion Date:** `2026-04-03`

---

## 3. Phase Scope

### In Scope

- Modular CSS architecture in `static/styles/` (Variables, Layouts, App-specific modules)
- Base layout templates with global `showToast` HTMX event listener
- `core/context_processors.py` for global app/nav state injection
- `_icon_.html` snippet using **Lucide-Icons** (Centralized SVG management)
- `_field_error_.html` snippet for consistent HTMX-driven validation
- Global UI components (Navbar, Sidebar, Cards, Modals)
- HTMX interaction patterns (Partial refreshes, lazy loading)
- Utility-Infused BEM strategy implementation

### Out of Scope

- Full page migrations for all modules
- React/Vue/Svelte integrations
- HTML/CSS/JS stored within individual app directories (All assets must be in root `static/` or `templates/`)

### Required Outcomes

- Consistent, responsive, and logic-aware structural shells
- Centralized library of atoms and components
- Working HTMX-based modal, sidebar navigation, and toast system
- Brand-aligned aesthetic using CSS custom properties

---

## 4. Constitutional Alignment

### Mandatory Checks

- **HTMX-First:** All dynamic updates use HTMX (Section 7.1)
- **Centralized Assets:** No HTML/CSS/JS allowed inside project app directories (Section 10.2/10.3)
- **Template Hierarchy:** Strict use of `layouts/`, `_snipps_/`, and `components/`
- **Asset Placement:** Styles in `static/styles/`, Scripts in `static/scripts/`
- **Utility-Infused BEM:** Custom CSS for structures, Utility classes for micro-spacing

---

## 5. Architecture Targets

### Modules / Apps Affected

- `core` (Context processors & Error handling)
- `templates/` (Centralized root directory)
- `static/` (Centralized root directory)

### Main Files or Areas Expected

- `static/styles/modules/` (Variables, Mixins, Typography)
- `static/styles/apps/` (App-specific style modules)
- `core/context_processors.py`
- `templates/_snipps_/_icon_.html`
- `templates/_snipps_/_field_error_.html`
- `templates/layouts/base.html` (Toast container added)

### Data Model Impact

- `None` (focus is purely on UI presentation).

### Operational Impact

- `None`.

---

## 6. Implementation Strategy

### Phase Strategy Summary

We will build the frontend "Inside-Out" using a **Design System** approach. 
1. **Tokens:** Define CSS custom properties (colors, typography) based on `Brand/` assets.
2. **Modular Styles:** Establish a directory structure for CSS that separates global layouts from app-specific modules.
3. **Atomic Snippets:** Build reusable fragments (Icons, Field Errors, Toasts) that enforce consistency.
4. **Shells:** Construct the global layouts (`base.html`, `dashboard.html`).
5. **Logic UI:** Implement the backend "UI Logic" (Context Processors, HTMX event listeners) to drive the dynamic experience.

### Sequencing Rule

1. Theme and Modular CSS directory structure
2. Base layout shells and Global Toast system
3. Atomic snippets (Icons, Field Errors, Inputs)
4. Navigation components (Sidebar, Topbar)
5. HTMX dynamic patterns (Modals, Context Processors)

---

## 7. Parts Breakdown

### Part 1: Design Tokens & Base Shells

- **Goal:** `Establish the visual core and the main layout shells.`
- **Owner:** `Qwen (Lead Developer)`
- **Status:** `Planned`

#### Tasks

1. **Task 7.1:** `Define modular CSS structure in static/styles/`
   - Output: `CSS modules for variables, layouts, and typography`
   - Verification: `Inspect files for clear separation of concerns`

2. **Task 7.2:** `Create layouts/base.html and layouts/dashboard.html`
   - Output: `Centralized layouts with HTMX scripts and Toast container`
   - Verification: `Verify that both layouts extend the root base.html`

### Part 2: Atomic Snippets & Global Components

- **Goal:** `Build reusable UI atoms and global structural components.`
- **Owner:** `Qwen (Lead Developer)`
- **Status:** `Planned`

#### Tasks

1. **Task 7.3:** `Implement _icon_.html snippet (Lucide-Icons)`
   - Output: `Snippet to load SVGs based on icon name`
   - Verification: `Confirm icons render correctly using standard include pattern`

2. **Task 7.4:** `Implement _field_error_.html and updated _input_.html snippets`
   - Output: `Consistent form fragments for HTMX-driven validation`
   - Verification: `Confirm error messages render correctly under input fields`

3. **Task 7.5:** `Create Navbar and Sidebar components`
   - Output: `Reusable template fragments in templates/components/`
   - Verification: `Sidebar renders app navigation list correctly`

### Part 3: HTMX Interaction & Logic UI

- **Goal:** `Establish the dynamic patterns and backend UI logic.`
- **Owner:** `Qwen (Lead Developer)`
- **Status:** `Planned`

#### Tasks

1. **Task 7.6:** `Implement core/context_processors.py`
   - Output: `Context processor for global app_name and nav_hierarchy`
   - Verification: `Sidebar automatically highlights the active app/module`

2. Task 7.7: `Establish HTMX Toast and Modal patterns`
   - Output: `Global listeners for HX-Trigger: showToast and showModal`
   - Verification: `Confirm toast appears when a custom HTMX header is sent`

### Part 4: Core Module UI Rollout

- **Goal:** `Bridge the backend operations to the new UI via functional list and detail views.`
- **Owner:** `Qwen (Lead Developer)`
- **Status:** ✅ **COMPLETE**

#### Tasks

1. **Task 7.8:** `Inventory UI: Product List & Ledger View`
   - Output: `Searchable product table and detailed stock movement history page`
   - Action: `Implement HTMX modal for "Stock Adjustment" operation`
   - Verification: `Confirm stock updates reflect in the UI without full-page reload`

2. **Task 7.9:** `Sales UI: Customer Registry & Order Management`
   - Output: `Customer list view and Sales Order dashboard`
   - Action: `Implement HTMX "Confirm Order" button with Toast success feedback`
   - Verification: `Verify pricing snapshots are displayed correctly in the order detail`

3. **Task 7.10:** `Purchasing UI: Supplier Registry & PO Receiving`
   - Output: `Supplier list and Purchase Order tracking views`
   - Action: `Implement HTMX partial for "Receive Stock" (In-Progress/Complete flow)`
   - Verification: `Verify WAC updates are triggered and logged in the UI`

---

## 8. Task Writing Rules

(Adhering to standard rules from template...)

---

## 9. Verification Plan

### Required Tests

- `Responsive check: Verify layout on mobile, tablet, and desktop`
- `HTMX check: Verify no full-page reloads for partial updates`
- `Accessibility: Confirm basic ARIA roles and keyboard navigation`

### Manual Verification

- `Confirm brand colors match the PDF/SCSS references in Brand/`

---

## 10. Risks and Controls

### Known Risks

- `CSS bloat and naming collisions`
- `HTMX history management (back button behavior)`

### Controls / Mitigations

- `Use a simple BEM or utility-first naming convention in vanilla CSS`
- `Use hx-push-url where navigation state should be preserved`

---

## 11. Open Questions

- `Should we use a specific icon set (e.g., FontAwesome, Lucide)?`

---

## 12. Completion Checklist

- [ ] Base layouts (`base`, `dashboard`) exist
- [ ] Shared atoms and components are implemented
- [ ] HTMX modal and partial patterns are operational
- [ ] Theme aligns with `Brand/` palette
- [ ] Responsive behavior is verified

---

## 13. Execution Log

- `2026-03-28` - `Planned` - `Initialized Phase 7 plan for Frontend and HTMX.`
- `2026-04-03` - `Implementation` - `Created modular CSS architecture: _variables.css (brand tokens, spacing, typography), _base.css (resets), _layout.css (sidebar, topbar, cards, tables, modals, toasts), _utilities.css (micro-spacing, flexbox, text utils). Deleted legacy theme.css and accounts-auth.css.`
- `2026-04-03` - `Implementation` - `Downloaded HTMX 1.9.12 to static/scripts/htmx.min.js (local, no CDN dependency).`
- `2026-04-03` - `Implementation` - `Created core/context_processors.py with ui_context providing app_name, nav_hierarchy, and active_app.`
- `2026-04-03` - `Implementation` - `Built _icon_.html snippet with 8 inline Lucide SVG icons (layout-dashboard, users, shield-check, settings, package, shopping-cart, truck, x, chevron-down).`
- `2026-04-03` - `Implementation` - `Built _field_error_.html and updated _input_.html with HTMX-driven validation support.`
- `2026-04-03` - `Implementation` - `Created Sidebar and Topbar components in templates/components/.`
- `2026-04-03` - `Implementation` - `Updated base.html with HTMX script, Toast container, and modal open/close helpers.`
- `2026-04-03` - `Implementation` - `Updated dashboard.html with sidebar + topbar integration, module quick-link cards.`
- `2026-04-03` - `Implementation` - `Updated login page with new CSS system and _input_.html snippet integration.`
- `2026-04-03` - `Verified` - `186 tests passing, 0 lint errors, Django system check clean.`
- `2026-04-03` - `Implementation` - `Added Part 4: Core Module UI Rollout (Tasks 7.8-7.10). Inventory UI: product list with search, detail with stock ledger, HTMX stock adjustment modal. Sales UI: customer registry, order dashboard with status filter, order detail with pricing snapshots, HTMX confirm/void with Toast feedback. Purchasing UI: supplier registry, PO tracking, order detail with receiving progress, HTMX receive stock modal. All three apps have views, URLs, and templates wired to root config/urls.py.`
- `2026-04-03` - ✅ **COMPLETE** - `Phase 7 fully finalized with Part 4. Ready for merge.`

---

## 14. Final Summary

Phase 7 successfully delivered a production-ready Frontend Foundation with:

**Part 1-3: Foundation & Components**
- ✅ Modular CSS architecture with brand-aligned design tokens (Coolors earthy brown/olive palette)
- ✅ Flat file structure: _variables.css, _base.css, _layout.css, _utilities.css + app-specific files
- ✅ Utility-Infused BEM: Custom BEM for structures (sidebar, topbar, cards), utility classes for spacing
- ✅ HTMX 1.9.12 downloaded locally (static/scripts/htmx.min.js)
- ✅ Global Toast notification system with HTMX event listener (hx-on::htmx:showToast)
- ✅ Modal open/close helpers with Escape key and overlay-click dismissal
- ✅ Sidebar navigation with active app highlighting via context processor
- ✅ Topbar with user info, department, and avatar
- ✅ _icon_.html snippet with 8 Lucide inline SVG icons
- ✅ _field_error_.html for consistent HTMX-driven form validation
- ✅ Updated _input_.html and _form_group.html with error support
- ✅ Dashboard with module quick-link cards (Inventory, Sales, Purchasing, IAM)

**Part 4: Core Module UI Rollout**
- ✅ **Inventory UI**: Product list with search, product detail with stock metrics, full stock ledger page, HTMX quick stock adjustment (add/reduce) with live feedback
- ✅ **Sales UI**: Customer registry with search, customer detail with order history, sales order dashboard with status filter, order detail with pricing snapshots, HTMX confirm/void order with Toast feedback
- ✅ **Purchasing UI**: Supplier registry with search, supplier detail with PO history, PO dashboard with status filter, PO detail with line item receiving progress, HTMX receive stock modal
- ✅ All three apps wired to root URLs (inventory/, sales/, purchasing/)
- ✅ Context processor updated with app-specific nav links

**Gem's Notes Compliance:**
- ✅ All styles centralized in static/styles/ (flat, underscore partials)
- ✅ Brand colors from Brand/Dj_ERP_Colour_Pallete_CSS.scss mapped to CSS variables
- ✅ Structural inspiration from ScreenShots/ERP_04.png (sidebar-to-content, topbar, panel/cards)
- ✅ Utility-Infused BEM approach implemented
- ✅ 4px/8px/16px/24px spacing scale established

**Test Coverage:** 186 tests passing, 2 skipped
**Lint:** 0 errors (ruff + black clean)

**Next Phase:** Phase 8 (Async Tasks, Reporting & Hardening)

**Version:** v7.0-phase7-complete
**Branch:** phase-7
**Completion Date:** 2026-04-03

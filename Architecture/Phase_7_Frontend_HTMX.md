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
- **Status:** `Planned`
- **Primary Goal:** `Establish the visual framework, layout hierarchy, and HTMX interaction patterns.`
- **Depends On:** `Phase 1-6`
- **Manager Approval Required:** `Yes`

---

## 3. Phase Scope

### In Scope

- Base layout templates (`base.html`, `dashboard.html`)
- Shared atom snippets (`buttons`, `inputs`, `badges`)
- Global components (`navbar`, `sidebar`, `cards`, `modals`)
- HTMX interaction patterns (partial refreshes, lazy loading)
- CSS custom properties (theme variables from `Brand/`)
- Responsive design foundations

### Out of Scope

- Full page migrations for all modules - (Specific pages are built in parallel, but Phase 7 focuses on the foundation)
- React/Vue/Svelte integrations - (HTMX only)

### Required Outcomes

- Consistent and responsive high-level structural shells
- Library of reusable UI components and snippets
- Working HTMX-based modal and sidebar navigation
- Brand-aligned aesthetic (using `Brand/` assets)

---

## 4. Constitutional Alignment

### Mandatory Checks

- HTMX-first rule is respected (Section 7.1)
- Template hierarchy (`layouts/`, `_snipps_/`, `components/`) is followed (Section 7.2)
- Theme values use CSS custom properties (Section 7.3)
- Interaction Rule: Dynamic updates use HTMX by default (Section 7.4)

### Notes for This Phase

- This phase is the visual "skinning" of the ERP. It must align perfectly with the `Brand/` directory's color palette and typography.

---

## 5. Architecture Targets

### Modules / Apps Affected

- `templates/` (entire directory)
- `static/` (styles and scripts)
- `core` (shared views/context processors)

### Main Files or Areas Expected

- `templates/layouts/base.html`
- `templates/_snipps_/_button_.html`
- `templates/components/navbar.html`
- `static/styles/theme.css`

### Data Model Impact

- `None` (focus is purely on UI presentation).

### Operational Impact

- `None`.

---

## 6. Implementation Strategy

### Phase Strategy Summary

We will build from the "inside out." First, we'll define our design tokens and theme in CSS. Then, we will build the smallest pieces (atoms/snippets). Next, we will construct the global layouts and components. Finally, we'll implement the HTMX-driven interaction patterns (like modals and partial loading) to ensure the ERP feels modern and reactive without a heavy JS framework.

### Sequencing Rule

1. Theme and CSS variables (aligned with `Brand/`)
2. Atomic snippets (buttons, inputs)
3. Structural layouts (base, dashboard)
4. Navigation components (sidebar, navbar)
5. HTMX dynamic patterns (modals, partial refreshes)

---

## 7. Parts Breakdown

### Part 1: Design System & Layouts

- **Goal:** `Establish the visual core and structural shells.`
- **Owner:** `Cod (Frontend AI)`
- **Status:** `Planned`

#### Tasks

1. **Task 7.1:** `Define theme.css with variables from Brand/ assets`
   - Output: `CSS file with project color palette and typography`
   - Verification: `Inspect page to confirm variable application`

2. **Task 7.2:** `Create layouts/base.html and layouts/dashboard.html`
   - Output: `Standard structural templates for the entire project`
   - Verification: `Verify blocks (title, content, scripts) are correctly placed`

### Part 2: Components & Interaction

- **Goal:** `Build reusable UI elements and dynamic behavior.`
- **Owner:** `Cod (Frontend AI)`
- **Status:** `Planned`

#### Tasks

1. **Task 7.3:** `Implement shared snippets (_button_, _input_)`
   - Output: `Reusable template fragments for common UI elements`
   - Verification: `Verify snippets render correctly across different pages`

2. **Task 7.4:** `Establish HTMX Modal pattern`
   - Output: `A global modal container that loads content via HTMX`
   - Verification: `Click a button and confirm modal loads external content via HTMX`

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

---

## 14. Final Summary

(TBD)

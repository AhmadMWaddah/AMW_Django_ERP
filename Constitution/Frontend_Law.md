# Frontend & Template Law - AMW Django ERP

**Extracted from Constitution Section 10**

## 10.1 Rendering Strategy

- The project frontend is server-rendered using Django templates.
- HTMX is the primary engine for dynamic UI interactions.
- JavaScript helpers may support HTMX behavior, but must not replace the HTMX-first approach without approval.

## 10.2 Template Hierarchy

- `templates/layouts/` - structural shells (`base.html`, `dashboard.html`)
- `templates/_snipps_/` - global atoms (`_button_.html`, `_input_.html`)
- `templates/components/` - shared sections (navbar, sidebar, cards)
- `templates/<module>/components/` - module-specific fragments
- `templates/<module>/pages/` - full page views

## Naming Convention

- Page templates: `{page_name}.html`
- Component templates: `{component_name}.html`
- Snippet templates: `_{snippet_name}_.html`

## 10.3 Asset Placement

- CSS belongs in `static/styles/`
- JavaScript belongs in `static/scripts/`
- Avoid inline styles
- Theme values should use CSS custom properties
- Brand colors should align with the `Brand/` directory assets and references

## 10.4 Interaction Rule

- Dynamic updates, row injection, modal content loading, and partial refreshes should use HTMX by default.
- jQuery may be used as a support tool, not as the main frontend architecture.

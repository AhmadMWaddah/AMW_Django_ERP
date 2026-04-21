# Style Law - AMW Django ERP

**Extracted from Constitution Sections 11.5 and 12**

## 1. Python String Quotes (Section 11.5)

**MANDATORY:** Use double quotes (`"`) for all Python strings.

```python
# CORRECT
name = "Employee"
error = "Invalid email or password"

# INCORRECT
name = 'Employee'
error = 'Invalid email or password'
```

## 2. Import Management (Section 12)

- Import statements managed automatically by Ruff/isort.
- No manual section headers (`# -- Section --`) in import blocks.
- CI enforces consistent ordering across the codebase.
- Let automation handle import organization; do not manually sort.

## 3. Documentation & Commenting Law (Section 12)

- **Docstrings** required for: classes, operation methods, non-trivial utilities.
- Comments must explain **why**, not repeat what the code already says.
- Do not write comments that merely restate the obvious.

**Good — explains why:**

```python
# Use select_for_update to prevent race condition during stock deduction
items = StockItem.objects.select_for_update().filter(product=product)
```

**Bad — restates what:**

```python
# Query StockItem objects filtered by product
items = StockItem.objects.filter(product=product)
```

## 4. Code Formatting

- Black for auto-formatting (line length, spacing).
- Ruff for linting (with `I001` ignored for import sorting conflicts).
- Run before commit: `black . && ruff check --fix .`

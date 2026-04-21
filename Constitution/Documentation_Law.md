# Documentation Law - AMW Django ERP

**Extracted from Constitution Section 12**

## Docstrings

- Use docstrings for classes, operation methods, and non-trivial utilities.
- Docstrings should explain the purpose and contract, not restate the implementation.

## Comments

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

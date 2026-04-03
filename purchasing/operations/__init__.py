"""
-- AMW Django ERP - Purchasing Operations --

Constitution Alignment:
- Section 8.1: Operations-First Business Logic
- Section 8.5: Stock Valuation Rule (WAC recalculation on receipt)
- Section 8.6: Atomic Safety (transaction.atomic + select_for_update)
- Section 8.7: Audit Rule (all state changes logged)
- Section 9.5: Financial Precision (Decimal 19,4, ROUND_HALF_UP)
"""

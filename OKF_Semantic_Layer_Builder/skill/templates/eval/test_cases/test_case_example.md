---
type: TestCase
domain: sales
---
# Question
What was total gross revenue in Q1 2026 (January–March), in USD?

# Expected Answer
1238900

# Expected Query
```sql
-- Aggregated SoT table is enough for a period total — no need to scan order lines.
SELECT ROUND(SUM(gross_revenue_usd), 2) AS gross_revenue_usd
FROM   sales.agg_sales_daily
WHERE  sales_date BETWEEN DATE'2026-01-01' AND DATE'2026-03-31';
```

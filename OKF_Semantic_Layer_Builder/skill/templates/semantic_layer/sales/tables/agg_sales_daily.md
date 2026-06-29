---
type: Table
title: agg_sales_daily
description: Daily sales aggregate by customer segment — the fast Source of Truth for revenue reporting.
resource: https://catalog.example.com/datasets/orders_db/agg_sales_daily
tags: [sales, revenue, aggregated, reporting]
timestamp: 2026-06-28T14:30:00Z
sot_for: [gross_revenue]
---

# Grain

One row per **`sales_date` × `customer_segment`**. Pre-aggregated for reporting, so a quarter total is a few
hundred rows, not millions of order lines.

# Schema

| Column | Type | Description |
|---|---|---|
| `sales_date` | DATE | Reporting-timezone date. Partition column. |
| `customer_segment` | STRING | Segment. See [customer_segment](/sales/dimensions/customer_segment.md). |
| `orders_count` | INT | Distinct recognized orders that day/segment. |
| `gross_revenue_usd` | DECIMAL(18,2) | Recognized gross revenue, USD (pre-refund). |
| `refunds_usd` | DECIMAL(18,2) | Refunds booked that day/segment, USD. |
| `net_revenue_usd` | DECIMAL(18,2) | `gross_revenue_usd - refunds_usd`. |

# Joins

- Slice by [customer_segment](/sales/dimensions/customer_segment.md) (already a column — no join needed).
- For anything finer than day × segment, drop to [fct_orders](/sales/tables/fct_orders.md).

# Lineage

- **Upstream:** built nightly from [fct_orders](/sales/tables/fct_orders.md) **with revenue-recognition
  rules already applied** — recognized statuses only, test orders excluded. See
  [revenue_recognition](/sales/reference/revenue_recognition.md).
- **Downstream:** powers the exec revenue dashboard.

> **Important:** because the rules are baked in, **do not re-filter on `status` or `is_test`** here — those
> columns don't exist on this table, and the rows are already clean.

# Metrics (SoT)

- [gross_revenue](/sales/metrics/gross_revenue.md) — aggregated SoT (use for period totals, trends, segment
  splits).

# Sample Queries

```sql
-- Total gross revenue for a period (the cheapest correct way to get a period total).
SELECT ROUND(SUM(gross_revenue_usd), 2) AS gross_revenue_usd
FROM   sales.agg_sales_daily
WHERE  sales_date BETWEEN DATE'2026-01-01' AND DATE'2026-03-31';
```

```sql
-- Monthly gross-revenue trend by segment.
SELECT DATE_TRUNC('month', sales_date) AS month,
       customer_segment,
       ROUND(SUM(gross_revenue_usd), 2) AS gross_revenue_usd
FROM   sales.agg_sales_daily
WHERE  sales_date >= DATE'2026-01-01'
GROUP  BY 1, 2
ORDER  BY 1, 2;
```

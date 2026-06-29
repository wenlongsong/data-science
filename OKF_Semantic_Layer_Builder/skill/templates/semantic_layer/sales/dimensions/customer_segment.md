---
type: Dimension
title: Customer Segment
description: The go-to-market segment a customer belongs to at the time of the order.
tags: [sales, customer, segmentation]
timestamp: 2026-06-28T14:30:00Z
aliases: [segment, customer tier, gtm segment]
---

# Definition

The go-to-market segment assigned to the customer **as of the order** (`customer_segment` is snapshotted
onto each order line, so historical reporting is stable even if a customer later moves segments).

# Expected Values

| Value | Meaning |
|---|---|
| `Enterprise` | Largest accounts; field-sales led. |
| `Mid-Market` | Mid-sized accounts. |
| `SMB` | Small business; self-serve + inside sales. |
| `Consumer` | Individual consumers. |

Values are stable and case-sensitive. An unexpected value (e.g. `NULL`, `Unknown`) signals an upstream gap —
surface it rather than silently bucketing it.

# Source Tables & Sample Queries

Available directly as a column on both sales tables — no join required.

### From [agg_sales_daily](/sales/tables/agg_sales_daily.md)  *(for segment splits of reported measures)*

```sql
-- Revenue mix by segment, Q1 2026.
SELECT customer_segment,
       ROUND(SUM(gross_revenue_usd), 2) AS gross_revenue_usd
FROM   sales.agg_sales_daily
WHERE  sales_date BETWEEN DATE'2026-01-01' AND DATE'2026-03-31'
GROUP  BY customer_segment
ORDER  BY gross_revenue_usd DESC;
```

### From [fct_orders](/sales/tables/fct_orders.md)  *(when combined with order-line detail)*

```sql
-- Distinct values present in a period (handy to validate the dimension).
SELECT DISTINCT customer_segment
FROM   sales.fct_orders
WHERE  sales_date >= DATE'2026-01-01';
```

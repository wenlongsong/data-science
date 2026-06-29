---
type: Metric
title: Gross Revenue
description: Recognized gross revenue (pre-refund), in USD.
tags: [sales, revenue]
timestamp: 2026-06-28T14:30:00Z
aliases: [revenue, sales, bookings, top line, gross sales]
---

# Definition

The total recognized value of orders, **before refunds**, in USD.

- **Numerator:** `SUM(gross_amount_usd)` over qualifying order lines.
- **Denominator:** — (additive measure, not a ratio).
- **Must-apply rules:**
  1. **Recognized status only:** `status IN ('completed', 'shipped', 'delivered')`. Excludes `cancelled`
     and `pending`. See [revenue_recognition](/sales/reference/revenue_recognition.md).
  2. **Exclude test orders:** `is_test = false`.
  3. **Pre-refund:** uses `gross_amount_usd`. For revenue *net* of refunds, use `net_revenue` (not yet in
     this layer — add via maintenance if needed). Do not silently subtract refunds here.
  4. Amounts are already USD (`*_usd`); no currency conversion needed.

> When computing from [agg_sales_daily](/sales/tables/agg_sales_daily.md), rules 1–2 are **already applied**
> in the table build — do not re-filter `status`/`is_test` there.

# Grain

Additive at order-line grain; reportable at any coarser grain (day, month, quarter, segment, product). Sum
freely across rows.

# SoT Tables & Sample Queries

Include both levels — reporting needs speed, analysis needs detail.

### Aggregated — [agg_sales_daily](/sales/tables/agg_sales_daily.md)  *(use first for totals, trends, segment splits)*

```sql
-- Period total (Q1 2026). Rules already baked into the aggregate.
SELECT ROUND(SUM(gross_revenue_usd), 2) AS gross_revenue_usd
FROM   sales.agg_sales_daily
WHERE  sales_date BETWEEN DATE'2026-01-01' AND DATE'2026-03-31';
```

### Granular — [fct_orders](/sales/tables/fct_orders.md)  *(use for product-level / ad-hoc cuts the aggregate lacks)*

```sql
-- Same metric, computed from order lines, with the must-apply rules explicit.
SELECT ROUND(SUM(gross_amount_usd), 2) AS gross_revenue_usd
FROM   sales.fct_orders
WHERE  sales_date BETWEEN DATE'2026-01-01' AND DATE'2026-03-31'
  AND  status IN ('completed', 'shipped', 'delivered')
  AND  is_test = false;
```

Both queries return the same number for the same period — the aggregate is just cheaper. Slice by
[customer_segment](/sales/dimensions/customer_segment.md) on either table.

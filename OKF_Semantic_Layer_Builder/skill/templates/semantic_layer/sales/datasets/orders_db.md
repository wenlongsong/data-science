---
type: Dataset
title: orders_db
description: Operational order store (schema `sales`) — order-line facts and a daily aggregate.
resource: https://catalog.example.com/datasets/orders_db
tags: [sales, orders, revenue]
timestamp: 2026-06-28T14:30:00Z
---

# Overview

`orders_db` is the system of record for placed orders. In the warehouse it is exposed as the **`sales`**
schema. All monetary columns are pre-converted to USD (`*_usd`); the original currency is kept on
`fct_orders.currency_code` for audit.

# Schema (tables in this dataset)

| Table | Grain | Use for |
|---|---|---|
| [fct_orders](/sales/tables/fct_orders.md) | one row per order line | deep dives, ad-hoc cuts, product-level detail |
| [agg_sales_daily](/sales/tables/agg_sales_daily.md) | one row per `sales_date` × `customer_segment` | fast period totals, trends, segment splits |

# Connection notes

- Fully-qualified names: `sales.fct_orders`, `sales.agg_sales_daily`.
- `agg_sales_daily` is rebuilt nightly from `fct_orders` **with the revenue-recognition rules already
  applied** (see [revenue_recognition](/sales/reference/revenue_recognition.md)) — so queries against the
  aggregate must not re-filter on `status`.
- Timezone: `order_ts` is UTC; `sales_date` is the order's date in the company reporting timezone
  (America/Los_Angeles).

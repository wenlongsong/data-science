---
type: Table
title: fct_orders
description: One row per order line — the granular Source of Truth for sales revenue.
resource: https://catalog.example.com/datasets/orders_db/fct_orders
tags: [sales, orders, revenue, granular]
timestamp: 2026-06-28T14:30:00Z
sot_for: [gross_revenue]
---

# Grain

One row per **order line** (`order_id` × `order_line_id`). An order with three products is three rows. This
is the finest grain in the sales domain — anything coarser can be derived from it.

# Schema

| Column | Type | Description |
|---|---|---|
| `order_id` | STRING | Order identifier. FK to the order header. |
| `order_line_id` | STRING | Line identifier, unique within an order. |
| `customer_id` | STRING | Placing customer. Join key to customer dims. |
| `order_ts` | TIMESTAMP | Order creation time, UTC. |
| `sales_date` | DATE | Order date in reporting tz (America/Los_Angeles). Partition column. |
| `product_id` | STRING | Product ordered. |
| `quantity` | INT | Units on the line. |
| `unit_price_usd` | DECIMAL(18,2) | Per-unit price, USD. |
| `gross_amount_usd` | DECIMAL(18,2) | `quantity * unit_price_usd`, USD. Pre-refund. |
| `refund_amount_usd` | DECIMAL(18,2) | Refunded amount on the line, USD (≥ 0). |
| `net_amount_usd` | DECIMAL(18,2) | `gross_amount_usd - refund_amount_usd`. |
| `status` | STRING | `completed` · `shipped` · `delivered` · `cancelled` · `pending`. |
| `currency_code` | STRING | Original transaction currency (ISO-4217). |
| `customer_segment` | STRING | Segment at time of order. See [customer_segment](/sales/dimensions/customer_segment.md). |
| `is_test` | BOOLEAN | Internal/test order — exclude from reporting. |

# Joins

- To customer dimensions on `customer_id`.
- To product reference on `product_id`.
- Rolls up to [agg_sales_daily](/sales/tables/agg_sales_daily.md) on `sales_date` + `customer_segment`.

# Lineage

- **Upstream:** ingested nightly from `orders_db` (operational Postgres) via CDC.
- **Downstream:** [agg_sales_daily](/sales/tables/agg_sales_daily.md) is built from this table with
  revenue-recognition rules applied.

# Metrics (SoT)

- [gross_revenue](/sales/metrics/gross_revenue.md) — granular SoT (use for deep dives / unusual cuts).

# Sample Queries

```sql
-- Gross revenue by product for Q1 2026 (deep dive the daily aggregate can't give — it has no product_id).
-- Apply the recognized-status rule and exclude test orders (see revenue_recognition reference).
SELECT product_id,
       ROUND(SUM(gross_amount_usd), 2) AS gross_revenue_usd
FROM   sales.fct_orders
WHERE  sales_date BETWEEN DATE'2026-01-01' AND DATE'2026-03-31'
  AND  status IN ('completed', 'shipped', 'delivered')
  AND  is_test = false
GROUP  BY product_id
ORDER  BY gross_revenue_usd DESC;
```

```sql
-- Single-order audit: every line, gross vs refund vs net.
SELECT order_line_id, product_id, quantity, gross_amount_usd, refund_amount_usd, net_amount_usd, status
FROM   sales.fct_orders
WHERE  order_id = :order_id
ORDER  BY order_line_id;
```

---
type: Reference
title: Revenue Recognition Rules
description: Policy for which orders count as revenue, when, and how refunds are handled.
tags: [sales, revenue, policy, finance]
timestamp: 2026-06-28T14:30:00Z
---

# Recognized statuses

An order line is **recognized** (counts toward revenue) when `status` is one of `completed`, `shipped`, or
`delivered`. `cancelled` and `pending` are **not** recognized. This rule is the backbone of
[gross_revenue](/sales/metrics/gross_revenue.md) and is pre-applied in
[agg_sales_daily](/sales/tables/agg_sales_daily.md).

# Test orders

Internal/test orders (`is_test = true`) are excluded from all reporting. They exist for QA and must never
appear in a customer-facing or exec number.

# Gross vs net (refunds)

- **Gross revenue** uses `gross_amount_usd` — the value at order time, **before** refunds.
- **Net revenue** subtracts refunds: `net_amount_usd = gross_amount_usd - refund_amount_usd`.
- Refunds are recorded on the **original** order line/date (not the refund date), so a refund reduces the
  revenue of the period the order belongs to. If a question needs refund-date treatment, flag it — that's a
  different metric and isn't modeled here yet.

# Timezone & period boundaries

`sales_date` is the order date in the company reporting timezone (America/Los_Angeles). Use `sales_date` —
not the UTC `order_ts` — for period boundaries, or totals near midnight/quarter-end will disagree with
Finance.

# Currency

All `*_usd` columns are pre-converted to USD at the order-date rate. Do not re-convert. `currency_code` on
[fct_orders](/sales/tables/fct_orders.md) is retained for audit only.

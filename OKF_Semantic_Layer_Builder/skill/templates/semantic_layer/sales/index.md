# Sales domain

Orders, revenue, refunds, and the customer segments that slice them. Source data is the `orders_db`
dataset (schema `sales`).

## Discovery sequence

Resolve questions in this order — it goes from *what is being measured* to *where it lives*:

1. **metrics/** — start here. Most sales questions name a measure (revenue, AOV, order count). The metric
   file gives the canonical definition and points to the Source-of-Truth tables.
2. **dimensions/** — the grain or breakdown (by segment, by day). Confirms allowed values and the column to
   group by.
3. **tables/** — schema, join keys, and lineage when you need to assemble or adapt the query.
4. **datasets/** — the physical dataset/connection, when you need the fully-qualified name or to see what
   else is available.
5. **reference/** — business rules and edge cases (e.g. what counts as recognized revenue).

## What's here

* [metrics/](/sales/metrics/index.md) - Canonical sales measures and their SoT tables.
* [dimensions/](/sales/dimensions/index.md) - Ways to slice sales (e.g. customer segment).
* [tables/](/sales/tables/index.md) - Order-line and daily-aggregate tables.
* [datasets/](/sales/datasets/index.md) - The `orders_db` dataset.
* [reference/](/sales/reference/index.md) - Revenue-recognition and other business rules.

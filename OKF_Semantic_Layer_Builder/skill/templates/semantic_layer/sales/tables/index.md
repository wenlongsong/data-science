# Sales — tables

Two tables, same revenue truth at two grains. Pick by the question:

* [fct_orders](/sales/tables/fct_orders.md) - **Granular**, one row per order line. Use for deep dives,
  product-level detail, or any filter the daily aggregate doesn't carry.
* [agg_sales_daily](/sales/tables/agg_sales_daily.md) - **Aggregated**, one row per day × segment. Use for
  period totals, trends, and segment splits — it's far cheaper to scan.

**Rule of thumb:** reach for `agg_sales_daily` first for reporting; drop to `fct_orders` only when you need a
cut the aggregate can't give you.

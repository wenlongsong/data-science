---
okf_version: "0.1"
---
# Semantic Layer — domain router

Start here. Match the question to a **domain**, open that domain's `index.md`, and follow its discovery
sequence. Read only what you descend into — that is the point of the indexes.

## Domains

* [Sales](/sales/index.md) - Orders, revenue, refunds, and customer segments. Use for any question about
  bookings, revenue, order volume, average order value, or sales by segment/region/product.

<!-- One bullet per domain. In a real bundle you'd also see e.g. product/, billing/, marketing/. -->

## When to use which domain

| The question is about… | Go to |
|---|---|
| Revenue, orders, refunds, AOV, sales by segment | `sales/` |

## Fallback mechanics

Use this **only in real use** — the eval's answerer keeps fallback **off** so accuracy reflects pure
coverage. If discovery finds nothing relevant:

1. **Suggest the nearest covered concept.** Name the closest metric/table by tag or name and ask whether
   that's what they meant.
2. **Probe, if a tool is connected.** With a data-catalog tool or SQL engine available, search the catalog
   or run `SELECT * FROM <table> LIMIT 1` to explore — then answer, and **flag the answer "outside the
   semantic layer"** so the user knows it wasn't grounded in a curated concept.
3. **Otherwise, recommend extending the layer.** Tell the user the concept isn't covered and offer to add it
   via the maintenance workflow (Workflow 3).

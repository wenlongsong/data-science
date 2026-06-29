# OKF v0.1 — conventions every generated file must follow

Open Knowledge Format (OKF) is a vendor-neutral standard: knowledge is **a directory of markdown files
with YAML frontmatter**, one file per concept. It is intentionally minimal — agree on a tiny
interoperability surface, leave everything else to the producer. Source: Google Cloud,
<https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing>
· spec <https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf>.

This file is the format authority for the builder. For the *output skill's* anatomy and per-file content
rules, see `output-skill-blueprint.md`.

## 1. Frontmatter

Only **`type`** is required. Everything else is optional but recommended. Producers may add arbitrary
keys; consumers must preserve unknown keys.

```yaml
---
type: <Concept type>          # REQUIRED. Short identifier; NOT registered centrally.
title: <display name>         # recommended
description: <one sentence>    # recommended — surfaces in index.md listings
resource: <URI to the asset>   # e.g. catalog/console URL
tags: [<tag>, <tag>]           # categorization for filtering
timestamp: <ISO-8601>          # last change, e.g. 2026-06-28T14:30:00Z
# ...producer-defined keys allowed below...
---
```

**Frontmatter we use (this builder's producer convention):**

| `type` | File | Producer keys (beyond standard) |
|---|---|---|
| `Dataset` | `datasets/db_*.md` | — |
| `Table` | `tables/tb_*.md` (or descriptive name) | `sot_for: [<metric>, …]` |
| `Metric` | `metrics/metric_*.md` | `aliases: [<synonym>, …]` |
| `Dimension` | `dimensions/dimension_*.md` | `aliases: [<synonym>, …]` |
| `Reference` | `reference/reference_*.md` | — |

`grain` is **not** frontmatter — it is a body section (`# Grain`) in tables and metrics, because it is
content the agent reasons over, not an index key.

## 2. Reserved files — `index.md` and `log.md`

These two filenames are **reserved** and are **never concept documents**:

- **`index.md`** — directory listing for progressive disclosure. **No frontmatter**, with one exception:
  the **bundle-root** `semantic_layer/index.md` may carry frontmatter, and only to declare the version:
  `okf_version: "0.1"`. Index bodies use OKF's nav format — a bullet list where each entry links a child
  and gives its one-line description (pulled from that child's `description`):

  ```markdown
  * [Gross Revenue](/sales/metrics/gross_revenue.md) - Recognized revenue, net of refunds.
  * [Orders (granular)](/sales/tables/fct_orders.md) - One row per order line.
  ```

  On top of the nav bullets, our index files also carry **instructional prose** — when to use which
  child, the discovery sequence, and (at the root) the fallback mechanics. That prose is still just
  markdown body; OKF permits it.

- **`log.md`** — chronological change history, newest first, ISO `YYYY-MM-DD` headings. The bold prefix
  (`Creation` / `Update` / `Deprecation`) is optional but useful:

  ```markdown
  ## 2026-06-28
  * **Creation**: Added `gross_revenue` metric and `fct_orders` table.
  ```

## 3. Concept identity & cross-links

- **Concept ID = file path with `.md` stripped.** `sales/tables/fct_orders.md` → `sales/tables/fct_orders`.
  Paths are the keys; there are no separate IDs.
- **Cross-link with markdown links, preferring absolute bundle-relative paths** (begin with `/`, resolved
  from the bundle root): `[fct_orders](/sales/tables/fct_orders.md)`. Relative links (`./other.md`) are
  allowed but less robust when files move.
- Links assert an **undirected** relationship; the *kind* of relationship is conveyed by the surrounding
  prose ("joined on", "lineage upstream", "SoT for"). Broken links are tolerated by consumers, but avoid
  them.

## 4. Why this shape

The frontmatter holds the few fields worth querying/filtering; the body holds everything an agent reads
to actually do the work (schemas, formulas, sample queries, rules). `index.md` files let an agent descend
the tree loading only what's relevant — this progressive disclosure is what keeps context lean and answers
grounded. Build many small, richly-linked files; never one monolith.

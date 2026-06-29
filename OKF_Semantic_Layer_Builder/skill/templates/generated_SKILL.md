---
name: <name>_semantic_layer
description: >-
  Answer data questions and write correct, grounded SQL for <BUSINESS/DOMAINS> by resolving the right
  tables, metrics, dimensions, and business rules from an Open Knowledge Format (OKF) semantic layer
  before any query is written. Use this whenever the user asks for a number, metric, trend, breakdown, or
  report from <BUSINESS/DOMAINS> data; whenever they ask "how do I calculate / where do I find / which
  table has …"; whenever they want SQL for <list the domains, e.g. sales, product, billing>; or whenever a
  query needs the canonical definition of a metric or dimension. Prefer this skill over writing SQL from
  memory — it prevents wrong tables, wrong grain, and wrong metric math.
---

# <name> Semantic Layer

A semantic layer in Open Knowledge Format: a navigable library of the tables, metrics, dimensions, and
business rules for **<BUSINESS/DOMAINS>**. Its job is to resolve *what data to use* — the right Source-of-
Truth table, the canonical metric formula, the correct grain and filters — **before** any SQL is written,
so answers are grounded instead of guessed.

This skill exposes three workflows. Pick by what the user is doing.

## Workflow 1 — Answer a data question / build SQL (discovery)

Navigate by **progressive disclosure** — read small `index.md` files and descend only into what's relevant.
Do not read the whole bundle.

1. Read `semantic_layer/index.md` → match the question to one or more **domains**.
2. Read that domain's `index.md` → follow its **discovery sequence** (default `metrics → dimensions →
   tables → datasets → reference`).
3. Open the relevant **metric** file → get its definition (numerator, denominator, must-apply rules), its
   grain, and its Source-of-Truth tables with sample queries.
4. Resolve the rest:
   - **grain / filters / breakdowns** → `dimensions/*`
   - **schema / join keys / lineage** → `tables/*`
   - **business rules / edge cases** → `reference/*`
5. **Compose the SQL** from the metric's sample query, choosing the SoT table that fits: an
   **aggregated** table for a fast period/total, a **granular** table for a deep dive or unusual cut. Adapt
   the grain and filters to the question. Run it if a SQL engine is connected; otherwise return the query.
6. **Nothing matches?** Use the fallback mechanics defined at the bottom of `semantic_layer/index.md`.

Always cite which metric/table files you used — it lets the user verify the grounding.

## Workflow 2 — Evaluate accuracy (eval)

Run this when the user wants to know how trustworthy the layer is, or after editing it. The full protocol —
a two-subagent answer-then-grade design that emits an HTML report — lives in
`eval/tools/eval-harness.md`. Follow it there. In short: count `eval/test_cases/`, dispatch one answerer
subagent per case (Workflow 1, **fallback off**), grade answers at **±2%**, then
`python eval/tools/generate_report.py --results results.json` and review the report with the user.

## Workflow 3 — Add or update a data asset (maintenance)

This layer is a **living wiki** — extend it in place instead of rebuilding. Run this when the user wants to
add or change a domain, dataset, table, metric, dimension, or reference.

1. **Gather source** — if not already given, ask for the SQL/DDL, catalog link or doc, metric-definition
   doc, or other reference for the asset.
2. **Match** — search `semantic_layer/` by name / tag / path to decide: new asset, or update an existing one?
3. **Write / update** —
   - *New:* create the asset file following `semantic_layer/`'s existing conventions exactly (frontmatter +
     the required body sections for that concept type — mirror a sibling file).
   - *Update:* edit the existing asset file in place.
   - For tables and metrics, validate before trusting: run `SELECT * FROM <table> LIMIT 1` to confirm the
     schema, and run each sample query to confirm it executes (when a SQL engine is connected).
4. **Re-index** — update every affected `index.md` (the concept folder, the domain, and the root if a domain
   changed), and append a dated entry to `semantic_layer/log.md`.
5. **Seed a test** — ask the user for a question that exercises the new/changed asset, or generate one.
6. **Verify** — answer it via Workflow 1 and show the user the result + SQL.
7. **Close** — if the user is satisfied, you're done; otherwise refine and repeat from step 3.

## How this layer is organized

```
semantic_layer/
├── index.md            # domain router + fallback mechanics (start here)
├── log.md              # change history
└── <domain>/
    ├── index.md        # discovery sequence for the domain
    ├── datasets/       # physical datasets/databases and their tables
    ├── tables/         # table schemas, joins, lineage, sample queries
    ├── metrics/        # canonical metric definitions + SoT tables
    ├── dimensions/     # dimension definitions + allowed values
    └── reference/      # business rules, product, competitor context
```

Every folder has an `index.md` that tells you which file to open and when. Trust the indexes; they exist so
you never have to read everything.

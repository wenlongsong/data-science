# Output-skill blueprint — what the generated semantic-layer skill must contain

This is the anatomy of the skill the builder stamps out. Pair it with `okf-spec.md` (format rules) and the
`templates/` exemplars (worked examples to copy the shape from).

## File tree

```
<name>_semantic_layer/
├── SKILL.md                     # 3 workflows: discovery · accuracy eval · ingest/update (maintenance)
├── semantic_layer/              # OKF bundle, filled with the user's real content
│   ├── index.md                 # ROOT: okf_version frontmatter + domain router + FALLBACK mechanics
│   ├── log.md                   # OKF change history (optional; appended by maintenance workflow)
│   └── <domain>/                # one folder per business domain (sales, product, billing, …)
│       ├── index.md             # subfolder list + DISCOVERY SEQUENCE + domain scope
│       ├── datasets/   (index.md + db_*.md)
│       ├── tables/     (index.md + tb_*.md)        # ≥1 aggregated + ≥1 granular where metrics need both
│       ├── metrics/    (index.md + metric_*.md)
│       ├── dimensions/ (index.md + dimension_*.md)
│       └── reference/  (index.md + reference_*.md)
└── eval/
    ├── test_cases/*.md          # user questions + expected answer + expected query
    ├── eval_reports/*.html      # eval output
    └── tools/
        ├── eval-harness.md      # two-subagent eval protocol (copied from builder, verbatim)
        └── generate_report.py   # deterministic HTML report renderer (copied from builder, verbatim)
```

A domain only needs the subfolders it uses — omit `datasets/` if there's nothing to say about datasets,
etc. But every present folder gets an `index.md`.

## The generated `SKILL.md` — three workflows

Copy `templates/generated_SKILL.md` and customize the name + domain list. It encodes:

**Workflow 1 — Data-context discovery (metric-centric progressive disclosure)**
1. Read `semantic_layer/index.md` → pick the domain(s) matching the question.
2. Read `<domain>/index.md` → follow its discovery sequence (default `metrics → dimensions → tables →
   datasets → reference`).
3. Open the metric file → definition + SoT tables + sample queries.
4. Pull grain/filters from `dimensions/*`, schema/joins from `tables/*`, rules from `reference/*`.
5. Compose the answer / SQL from the SoT sample query, adapted to the asked grain & filters.
6. Nothing matches → fallback mechanics (below).

**Workflow 2 — Accuracy eval** → delegates to `eval/tools/eval-harness.md`.

**Workflow 3 — Ingest / update data assets (maintenance)** → the living-wiki loop: gather source → match
existing vs new → write/update the asset file on the same OKF spec → re-index every affected `index.md`
(and append `log.md`) → seed a test question → verify via Workflow 1 → close on user approval.

## Required body sections per concept type ("at least contains")

These minimums make a concept usable without guessing. Match the exemplars in `templates/semantic_layer/sales/`.

| Concept file | Required body sections |
|---|---|
| `tables/tb_*.md` | `# Grain` · `# Schema` (columns: name, type, description) · `# Joins` (keys + links to other tables) · `# Lineage` (upstream/downstream) · `# Metrics (SoT)` (metrics this table is SoT for) · `# Sample Queries` |
| `metrics/metric_*.md` | `# Definition` (numerator · denominator · must-apply rules) · `# Grain` · `# SoT Tables & Sample Queries` — list each SoT table, *when to use it*, and a runnable query; include **≥1 aggregated** (fast reporting) and **≥1 granular** (deep dive) |
| `dimensions/dimension_*.md` | `# Definition` · `# Expected Values` · `# Source Tables & Sample Queries` (where to pull it, when, with a query) |
| `datasets/db_*.md` | `# Schema` (tables in the dataset, linked) · grain/connection notes |
| `reference/reference_*.md` | Free-form business rules / product / competitor context, cross-linked to the concepts it governs |

## index.md content rules

- **Root `semantic_layer/index.md`**: frontmatter `okf_version: "0.1"`; body lists every domain with a
  one-line "use this domain when…"; ends with a **Fallback mechanics** section.
- **`<domain>/index.md`**: lists the present subfolders; states the **discovery sequence**; one-line domain
  scope.
- **Folder `index.md`** (`metrics/index.md`, etc.): bullets each concept with its description and a
  "when to use which" hint.

## Fallback mechanics (live the root index.md; **disabled during eval**)

A tiered escalation for when discovery finds nothing relevant:
1. Suggest the nearest covered concept(s) by name/tag.
2. If a catalog/SQL tool is connected, probe it (`SELECT * … LIMIT 1` / catalog search), answer, and **flag
   the answer "outside semantic layer."**
3. Otherwise tell the user it isn't covered and recommend adding it via the maintenance workflow (Workflow 3).

The eval's answerer subagent **switches fallback off** so accuracy reflects only what the layer actually
covers — see `eval/tools/eval-harness.md`.

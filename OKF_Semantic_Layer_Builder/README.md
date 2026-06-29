# OKF Semantic-Layer Builder

A Claude Code **skill that builds skills**. Point it at your warehouse repo, dbt project, data
catalog, or docs, and it scaffolds a lightweight **semantic layer** in Google's
[Open Knowledge Format (OKF)](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)
— a structured, navigable library of your domains, datasets, tables, metrics, dimensions, and business
rules that lets an AI agent find the right data context and write **correct, grounded SQL** instead of
guessing.

It is the fastest way for anyone to jump-start an effective semantic layer for natural-language-to-SQL
and analytics agents.

> ## ⚠️ Level-set: the skill gives you a head start, not a finish line
>
> This builder gets you to a working OKF semantic layer in minutes. But a semantic layer is only as good
> as the **context inside it** — the accuracy of each definition, the coverage of your metrics, the
> correctness of every sample query. The generator gives you a strong, consistent scaffold; **the final
> performance depends on the quality of the content you curate on top of it.**
>
> **After the initial generation, it is highly recommended to:**
>
> 1. **Review every markdown file** in `semantic_layer/` to ensure the information is accurate and
>    complete — schemas, metric formulas, must-apply rules, join keys, and sample queries.
> 2. **Add as many real-world questions as possible** to `eval/test_cases/` — the questions your team
>    actually asks, with their known-correct answers and reference SQL.
> 3. **Repeat the Eval** (Workflow 2) until the accuracy is acceptable for your use case, fixing the
>    layer between runs based on the report's misses and recommended actions.

---

## What it generates

Invoking the builder produces a self-contained semantic-layer skill with three workflows:

| Workflow | What it does |
|---|---|
| **1 · Data-context discovery** | Navigates the OKF bundle by progressive disclosure (`index → domain → metric → table`) to ground an answer and compose SQL. |
| **2 · Accuracy eval** | Two-subagent harness (answer → grade) that scores test cases on a three-tier scale and renders an HTML report. |
| **3 · Ingest / update (maintenance)** | A living-wiki loop to add or update a domain, table, metric, dimension, or reference in place. |

The generated bundle follows OKF exactly — a directory of markdown files with YAML frontmatter, one
file per concept, cross-linked into a navigable graph:

```
<name>_semantic_layer/
├── SKILL.md                 # the 3 workflows above
├── semantic_layer/          # the OKF bundle (your real content)
│   ├── index.md             # domain router + fallback
│   └── <domain>/            # datasets/ tables/ metrics/ dimensions/ reference/ (each with index.md)
└── eval/
    ├── test_cases/          # your questions + expected answer + expected query
    ├── eval_reports/        # generated HTML reports
    └── tools/               # eval harness + report renderer (self-contained)
```

## How the builder works

1. **Gather inputs** — skill name, codebase/repos, data-catalog access (or consent to probe with
   `SELECT * … LIMIT 1`), reference docs, and test cases.
2. **Ingest** — read the sources; extract tables, metrics, dimensions, and rules (read-only).
3. **Write the spec** — propose domains, table/metric placement, and Source-of-Truth designations.
4. **Approve** — you review and approve the spec before anything is scaffolded.
5. **Scaffold + fill** — write the OKF bundle and the generated skill.
6. **Validate against source** — confirm each table's schema and run every sample query.
7. **Seed eval + run** — convert your test cases and produce the accuracy report.

## The eval report

The eval grades each question on the answer (queries are recorded but not scored) into three tiers:

- **Correct** — within ±2% of the expected answer.
- **Partially correct** — within ±5% but beyond ±2%.
- **Incorrect** — beyond ±5%, not found in the layer, or unverifiable.

The HTML report shows top-line metrics (total questions, overall accuracy, partially-correct rate,
average tokens), a verdict bar, a case-by-case breakdown with an **explanation of each miss**, and
**recommended actions** for improving the layer — the inputs to your review loop above.

## Install

This folder ships the skill under [`skill/`](./skill). To use it in Claude Code, copy it into your
skills directory under the skill's name:

```bash
# from a clone of this repo
cp -r OKF_Semantic_Layer_Builder/skill ~/.claude/skills/okf_semantic_layer_builder
```

Then start a Claude Code session and invoke it:

```
/okf_semantic_layer_builder
```

…or simply ask Claude to "build a semantic layer for <your data>."

## Layout of this folder

```
OKF_Semantic_Layer_Builder/
├── README.md     # you are here
└── skill/        # the okf_semantic_layer_builder skill (SKILL.md + references/ + templates/)
```

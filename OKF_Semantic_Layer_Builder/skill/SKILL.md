---
name: okf_semantic_layer_builder
description: >-
  Build an Open Knowledge Format (OKF) semantic-layer skill from a codebase, data catalog, or docs —
  a structured library of domains, datasets, tables, metrics, dimensions, and references that lets an
  agent find the right data context and write correct SQL, plus a built-in accuracy-eval harness and a
  self-maintenance workflow. Use this whenever the user wants to create, scaffold, generate, or
  bootstrap a semantic layer, data foundation, metrics layer, data dictionary, knowledge layer, or
  "data context" skill for natural-language-to-SQL or analytics agents; whenever they point you at a
  warehouse repo / dbt project / data catalog and ask to make its tables and metrics discoverable to
  Claude; or whenever they mention OKF, semantic models, or text-to-SQL grounding. Prefer this skill
  even if the user does not say the words "semantic layer."
---

# OKF Semantic-Layer Builder

## What this skill is

This is a **factory**. It does not answer data questions itself — it **builds a new skill** that does.
The skill it produces is an Open Knowledge Format (OKF) bundle: a directory of markdown files, one per
concept (a metric, a table, a dimension, …), that an agent navigates by progressive disclosure to find
the right data context and compose correct SQL.

Two artifacts are involved. Keep them straight:

| Artifact | What it is | Lives in |
|---|---|---|
| **This builder** | The factory workflow + OKF spec + exemplar templates + eval tooling | this skill |
| **The generated skill** | The semantic layer you stamp out for the user's data | a new `<name>` skill dir |

The point of OKF is *interoperability and progressive disclosure*: an agent reads a small `index.md`,
follows links down to exactly the concept it needs, and ignores the rest. That is why the output is many
small linked files rather than one giant document — it keeps the agent's context lean and its answers
grounded.

## When to use

Trigger when a user wants to make a data estate queryable by an agent: "build a semantic layer for our
warehouse," "turn this dbt repo into a data-context skill," "I want Claude to know our metrics and write
correct SQL," "scaffold a metrics layer / data dictionary," or any mention of OKF. If they have a pile
of tables and want grounded text-to-SQL, this is the skill.

## Before you start — read these

- `references/okf-spec.md` — the OKF v0.1 conventions every generated file must follow (frontmatter,
  reserved files, cross-links). **Read this before writing any bundle file.**
- `references/output-skill-blueprint.md` — the exact structure and the 3-workflow `SKILL.md` the
  generated skill must contain. **Read this before scaffolding.**
- `templates/` — fully-worked exemplars (a `sales` domain, the generated `SKILL.md`, the eval tree).
  These are your few-shot examples: **copy their shape and adapt the content**, don't invent a new shape.

## The build workflow

Follow these seven steps in order. Steps 4 is a hard approval gate — do not cross it without the user.

### 1. Gather inputs

Ask the user for the following, but **skip anything the prompt already answers** — don't re-ask what you
were just told. Ask only for what's missing, ideally in one message:

1. **Skill name** for the semantic layer (e.g., `acme_sales_semantic_layer`).
2. **Codebase / repos** — GitHub links or local paths (warehouse repo, dbt project, SQL, notebooks).
3. **Data-catalog access** — a catalog search tool/MCP, or catalog docs. If neither exists, warn the
   user plainly: *"No catalog provided — to read a table's real schema I'll run `SELECT * FROM <table>
   LIMIT 1` against it. OK?"* and get consent before any probe.
4. **Reference docs** — metric definitions, business rules, KPI glossaries, product/competitor context.
5. **Test cases** — questions with expected answers + expected SQL. Deferrable to step 7; say so.

### 2. Ingest

Read the repos and docs. Extract the raw material for the bundle: tables and their columns, metric
definitions and formulas, dimensions and their allowed values, join keys, grain, and business rules.
Prefer the catalog tool for schema; fall back to the consented `LIMIT 1` probe only when needed. This is
strictly read-only — never write to the user's systems.

If the estate is large, dispatch subagents to explore different repos/domains in parallel and report
back concise concept inventories, so your own context stays clean.

### 3. Write the spec

Draft a short semantic-layer spec for the user: the **domains** you found (e.g., `sales`, `product`,
`billing`), which tables/metrics/dimensions/references land in each, which table is the **Source of
Truth (SoT)** for each metric, and naming. Group by business domain, not by source system — the agent
navigates by *question topic*, so the domains should mirror how the business asks questions.

### 4. Approve (gate)

Present the spec and **wait for explicit approval**. The user owns domain boundaries and SoT calls; a
wrong call here propagates into every file. Do not scaffold until they approve.

### 5. Scaffold + fill

Create the generated-skill tree from `references/output-skill-blueprint.md`. Then:

- Write the `semantic_layer/` OKF bundle — every file conforming to `references/okf-spec.md` and shaped
  like the matching `templates/semantic_layer/sales/` exemplar. Fill real schemas, real formulas, real
  sample queries. Cross-link concepts with absolute bundle-relative links (`/sales/tables/fct_orders.md`).
- Copy the entire `templates/eval/` tree into the generated skill's `eval/` (verbatim — it's the
  self-contained harness).
- Write the generated `SKILL.md` from `templates/generated_SKILL.md`, customized to the skill's name and
  domains.

Honor the "at least contains" rules per file type (see the blueprint). For every metric, include **at
least one aggregated-level** SoT table (fast reporting) **and at least one granular-level** table (deep
dives) — analysts need both, and the exemplar shows the pattern.

### 6. Validate against source

Before anyone trusts the layer, prove it matches reality. With a SQL tool connected:

- For each generated table file, run `SELECT * FROM <table> LIMIT 1` and confirm the written `# Schema`
  matches the live columns/types. Fix any drift.
- Run **every** embedded sample query (in tables, metrics, dimensions). Each must execute without error.
  Fix anything that breaks.

If no SQL tool is connected, you cannot validate — write the bundle but **flag it "unvalidated"** in your
summary so the user knows the schemas and queries are unverified.

### 7. Seed eval + run

If the user hasn't supplied test cases, ask for a few now (or offer to draft some from the bundle). Convert
each into `eval/test_cases/*.md` using the exemplar format. Then run the generated skill's **eval
workflow** (Workflow 2) and produce the HTML report for review. See `templates/eval/tools/eval-harness.md`
for the protocol the generated skill follows.

## Where the files go

- **Source of truth (versioned):** build into `Projects/<date>_<name>/build/v1/<skill>/` so each version is
  reproducible; future iterations go to `build/v2/`.
- **Installed (invocable):** copy the finished skill into the runtime skills directory (e.g.
  `~/.claude/skills/<skill>/`) so the user can invoke it.

## Verifying the generated skill (no data needed)

Even without live data you can prove the machinery works:

1. **Structure lint** — the tree matches the blueprint; every file has required frontmatter + body sections.
2. **Discovery dry-run** — give a subagent a sample question and the bundle; confirm it navigates
   `index → domain → metric → table` and *constructs* (need not execute) correct SQL.
3. **Report renderer check** — run `eval/tools/generate_report.py` on a small synthetic `results.json`;
   confirm it emits a valid HTML report with all sections.

## Principles

- **Many small linked files beat one big file.** That is the whole OKF bet — it's what keeps agent context
  lean. Resist the urge to consolidate.
- **Ground everything.** Every metric points to SoT tables and runnable sample queries. An agent should
  never have to guess a column name.
- **The bundle is a graph.** Use links liberally (metric→table, table→table joins, table→lineage). The
  links are how the agent — and the OKF visualizer — traverse knowledge.

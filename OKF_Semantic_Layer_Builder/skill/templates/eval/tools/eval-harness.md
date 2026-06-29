# Eval harness — accuracy protocol for this semantic-layer skill

This is Workflow 2 of the skill. It measures how well the `semantic_layer/` bundle lets an agent answer
real data questions, using a two-subagent design: one agent **answers** under the skill's own rules, a
second **grades** against expected answers. The split matters — the answerer must not grade itself, or it
will rationalize partial credit.

## 0. Preflight

Count the files in `eval/test_cases/`.
- **None?** Tell the user: *"No test cases yet. Give me a few questions with their expected answers (and
  ideally the reference SQL) and I'll evaluate coverage."* Stop until provided.
- **Some?** Tell the user how many were found, then proceed.

Each test case is a markdown file: a `# Question`, an `# Expected Answer` (the value compared at ±2%), and
an `# Expected Query` (reference SQL, recorded but not graded). `type: TestCase` frontmatter carries the
`domain` for by-domain reporting.

## 1. Subagent A — Answerer (one fresh subagent per case)

Run a **separate** subagent for each test case so token counts stay clean and cases can't leak context into
each other. Give each subagent only: this skill's `SKILL.md` Workflow 1, the `semantic_layer/` bundle, and
the single question.

Rules — state them in the dispatch prompt verbatim:

- Follow Workflow 1 (discovery) **strictly**. Navigate `index → domain → metric → table` and compose SQL
  from the bundle's sample queries.
- **Fallback is DISABLED.** Do not probe the catalog, do not run `SELECT *`, do not use outside knowledge.
  If the bundle does not contain what's needed, record `status: "failure"` and stop. We are measuring the
  *layer's* coverage, not the agent's resourcefulness.
- If a SQL engine is connected, run the composed query and record the numeric `answer`. If no engine is
  connected, record the composed SQL with `status: "not_executed"` and leave `answer` empty.

Record per case: `{id, domain, question, answer, sql, tokens, status}`.

**Token recording:** capture the subagent's reported usage (`total_tokens`) from its completion metadata
when the runtime exposes it, and set `token_method: "task_meta"`. If unavailable, estimate from the
characters of context the subagent loaded (files read + prompt) ÷ 4 and set `token_method: "estimate"`.
Stamp the method so the numbers are interpretable.

## 2. Assemble `results.json`

Collect all answerer outputs into one file for the grader and the report script:

```json
{
  "skill": "<name>",
  "run_ts": "<ISO-8601>",
  "token_method": "task_meta",
  "recommendations": [],
  "cases": [
    {"id": "tc_revenue_q1", "domain": "sales", "question": "...",
     "agent_answer": "1240500", "expected_answer": "1238900",
     "agent_sql": "SELECT ...", "expected_sql": "SELECT ...",
     "tokens": 14201, "status": "answered", "result": null, "explanation": ""}
  ]
}
```

`status` (set by the answerer) is `answered` (got a value), `failure` (not found in the layer), or
`not_executed` (no SQL engine). `result` and `explanation` are filled by the grader in step 3. `domain` is
optional — the report no longer breaks down by domain, so include it only if useful for your own analysis.

## 3. Subagent B — Grader (single pass)

One subagent reads `results.json` and each test case's expected answer:

- Set each case's **`result`** by comparing the **answer only** (ignore SQL differences — a
  different-but-correct query is fine):
  - `correct` — within **±2%** of expected.
  - `partial` — within **±5%** but beyond ±2%.
  - `incorrect` — beyond ±5%, a `failure` (not found in the layer), or `not_executed`.
- For every `partial` and `incorrect` case, write a one-line **`explanation`** of the miss — what actually
  went wrong (wrong table/grain/filter, a must-apply rule skipped, the metric isn't in the layer, etc.).
  This is what makes the report actionable.
- Write the **`recommendations`** array: concrete, file-pointing fixes inferred from the misses — e.g.
  *"add metric `net_revenue` to `sales/metrics/`"*, *"`fct_orders` schema missing `refund_amount`"*,
  *"domain `billing` scored 40% — coverage is thin"*, *"churn rule ambiguous in
  `reference/revenue_recognition.md`"*. These are the payoff of the eval; make them specific.
- Save the updated `results.json`.

## 4. Render the report

```bash
python eval/tools/generate_report.py --results results.json
```

This writes `eval/eval_reports/<timestamp>.html` with the four top-line metrics (total questions, overall
accuracy at ±2%, partially-correct rate at ±2–5%, average tokens), a case-by-case breakdown (question ·
result · agent vs expected answer · agent vs expected SQL · explanation of the miss), and the recommended
actions. Open it for the user and walk them through the misses and the recommended fixes.

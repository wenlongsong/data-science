#!/usr/bin/env python3
"""
generate_report.py — deterministic HTML renderer for the OKF semantic-layer eval.

Reads a ``results.json`` produced by the eval harness (Subagent A answers, Subagent B grades) and renders
a self-contained HTML report into ``eval_reports/``. Presentation lives in ``report_template.html`` (a
sibling of this script); this module computes statistics and fills ``{{PLACEHOLDER}}`` tokens, so the look
can be restyled without touching logic.

Result model (three tiers, compared on the ANSWER only)
-------------------------------------------------------
* ``correct``   — agent answer within +/-2% of expected.
* ``partial``   — within +/-5% but beyond +/-2%.
* ``incorrect`` — beyond +/-5%, OR not found in the layer (``failure``), OR not gradable
  (no number / no SQL engine).

The grader (Subagent B) should set each case's ``result`` and a one-line ``explanation`` for the misses.
This script trusts ``result`` when present and otherwise derives it from the numbers, so the report is
honest about *why* each case landed where it did. All rates are out of the TOTAL number of questions.

Usage
-----
    python generate_report.py --results results.json
    python generate_report.py --results results.json --out eval_reports/2026-06-28T1430.html
"""

from __future__ import annotations

import argparse
import html
import json
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

CORRECT_TOL = 0.02   # +/-2%  -> correct
PARTIAL_TOL = 0.05   # +/-5%  -> partial (when beyond 2%)

_NUMERIC_RE = re.compile(r"-?\d[\d,]*\.?\d*")


# --------------------------------------------------------------------------------------------------
# Grading
# --------------------------------------------------------------------------------------------------

def _parse_number(value: Any) -> Optional[float]:
    """Best-effort single-number extraction from an answer (handles ``$1,234.50``, ``42%``, ``1.2M``)."""
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().lower()
    multiplier = 1.0
    if text and text[-1] in "kmb":
        multiplier = {"k": 1e3, "m": 1e6, "b": 1e9}[text[-1]]
        text = text[:-1]
    match = _NUMERIC_RE.search(text)
    if not match:
        return None
    try:
        return float(match.group(0).replace(",", "")) * multiplier
    except ValueError:
        return None


def resolve_result(case: Dict[str, Any]) -> str:
    """Return ``correct`` / ``partial`` / ``incorrect``.

    Priority: explicit grader ``result`` -> numeric tolerance bands -> ``incorrect`` (ungradable misses
    count as incorrect, never silently dropped).
    """
    declared = str(case.get("result", "")).strip().lower()
    if declared in {"correct", "partial", "incorrect"}:
        return declared
    if case.get("status") in {"failure", "not_executed"}:
        return "incorrect"
    agent, expected = _parse_number(case.get("agent_answer")), _parse_number(case.get("expected_answer"))
    if agent is None or expected is None:
        return "incorrect"
    err = abs(agent) if expected == 0 else abs(agent - expected) / abs(expected)
    if err <= CORRECT_TOL:
        return "correct"
    if err <= PARTIAL_TOL:
        return "partial"
    return "incorrect"


def compute_stats(results: Dict[str, Any]) -> Dict[str, Any]:
    cases: List[Dict[str, Any]] = results.get("cases", [])
    total = len(cases)
    counts = {"correct": 0, "partial": 0, "incorrect": 0}
    tokens: List[int] = []

    for case in cases:
        case["_result"] = resolve_result(case)
        counts[case["_result"]] += 1
        if isinstance(case.get("tokens"), (int, float)):
            tokens.append(int(case["tokens"]))

    def pct_num(n: int) -> float:
        return round(100.0 * n / total, 1) if total else 0.0

    return {
        "total": total,
        "counts": counts,
        "overall_pct": f"{pct_num(counts['correct']):.0f}%" if total else "n/a",
        "partial_pct": f"{pct_num(counts['partial']):.0f}%" if total else "n/a",
        "correct_pct_num": pct_num(counts["correct"]),
        "partial_pct_num": pct_num(counts["partial"]),
        "incorrect_pct_num": pct_num(counts["incorrect"]),
        "avg_tokens": round(statistics.mean(tokens)) if tokens else None,
        "cases": cases,
    }


# --------------------------------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------------------------------

def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


_LABELS = {"correct": "Correct", "partial": "Partially correct", "incorrect": "Incorrect"}


def _value_cell(label: str, value: Any) -> str:
    shown = _esc(value) if value not in (None, "") else "<span class='muted'>—</span>"
    return (f"<div class='cmp__col'><div class='cmp__label'>{label}</div>"
            f"<div class='cmp__val'>{shown}</div></div>")


def _sql_cell(label: str, value: Any) -> str:
    shown = f"<pre class='sql'>{_esc(value)}</pre>" if value else "<span class='muted'>—</span>"
    return f"<div class='cmp__col'><div class='cmp__label'>{label}</div>{shown}</div>"


def _miss_block(case: Dict[str, Any]) -> str:
    """Explanation of the miss — shown only for partial/incorrect cases."""
    if case["_result"] == "correct":
        return ""
    explanation = case.get("explanation") or "No explanation recorded."
    return (
        "<div class='miss'><span class='miss__mark'>&#8627;</span><div class='miss__body'>"
        "<div class='miss__label'>Explanation of the miss</div>"
        f"<p>{_esc(explanation)}</p></div></div>"
    )


def render_case_blocks(cases: List[Dict[str, Any]]) -> str:
    if not cases:
        return "<p class='muted'>No test cases were evaluated.</p>"
    blocks = []
    for case in cases:
        r = case["_result"]
        blocks.append(
            f"<article class='case case--{r}'>"
            f"<div class='case__head'><span class='case__id'>{_esc(case.get('id', '—'))}</span>"
            f"<span class='badge badge--{r}'>{_LABELS[r]}</span></div>"
            f"<p class='case__q'>{_esc(case.get('question'))}</p>"
            "<div class='cmp'>"
            f"{_value_cell('Agent answer', case.get('agent_answer'))}"
            f"{_value_cell('Expected answer', case.get('expected_answer'))}</div>"
            "<div class='cmp'>"
            f"{_sql_cell('Agent SQL', case.get('agent_sql'))}"
            f"{_sql_cell('Expected SQL', case.get('expected_sql'))}</div>"
            f"{_miss_block(case)}"
            "</article>"
        )
    return "\n".join(blocks)


def render_recommendations(results: Dict[str, Any]) -> str:
    recs = results.get("recommendations") or []
    if not recs:
        return "<li class='muted'>No recommendations recorded.</li>"
    return "\n".join(f"<li>{_esc(r)}</li>" for r in recs)


def fill_template(template: str, results: Dict[str, Any], stats: Dict[str, Any]) -> str:
    c = stats["counts"]
    total = stats["total"]
    avg = stats["avg_tokens"]
    replacements = {
        "{{SKILL}}": _esc(results.get("skill", "semantic layer")),
        "{{RUN_TS}}": _esc(results.get("run_ts", datetime.now(timezone.utc).isoformat(timespec="seconds"))),
        "{{TOKEN_METHOD}}": _esc(results.get("token_method", "unknown")),
        "{{TOTAL_QUESTIONS}}": str(total),
        "{{OVERALL_PCT}}": stats["overall_pct"],
        "{{OVERALL_FRACTION}}": f"{c['correct']} / {total} within ±2%",
        "{{PARTIAL_PCT}}": stats["partial_pct"],
        "{{PARTIAL_FRACTION}}": f"{c['partial']} / {total} within ±2–5%",
        "{{AVG_TOKENS}}": "n/a" if avg is None else f"{avg:,}",
        "{{CORRECT_N}}": str(c["correct"]),
        "{{PARTIAL_N}}": str(c["partial"]),
        "{{INCORRECT_N}}": str(c["incorrect"]),
        "{{CORRECT_PCT_NUM}}": f"{stats['correct_pct_num']}",
        "{{PARTIAL_PCT_NUM}}": f"{stats['partial_pct_num']}",
        "{{INCORRECT_PCT_NUM}}": f"{stats['incorrect_pct_num']}",
        "{{CASE_BLOCKS}}": render_case_blocks(stats["cases"]),
        "{{RECOMMENDATIONS}}": render_recommendations(results),
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    return template


# --------------------------------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------------------------------

def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Render the OKF eval HTML report.")
    parser.add_argument("--results", default="results.json", help="Path to results.json")
    parser.add_argument("--template", default=str(here / "report_template.html"), help="HTML template path")
    parser.add_argument("--out", default=None, help="Output HTML path (default: eval_reports/<ts>.html)")
    args = parser.parse_args()

    results = json.loads(Path(args.results).read_text(encoding="utf-8"))
    template = Path(args.template).read_text(encoding="utf-8")
    stats = compute_stats(results)

    out_path = args.out
    if out_path is None:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
        out_dir = here.parent / "eval_reports"  # eval/eval_reports/
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{ts}.html"

    Path(out_path).write_text(fill_template(template, results, stats), encoding="utf-8")
    c = stats["counts"]
    print(f"Report written: {out_path}")
    print(f"Total {stats['total']} | correct {c['correct']} ({stats['overall_pct']}) | "
          f"partial {c['partial']} ({stats['partial_pct']}) | incorrect {c['incorrect']} | "
          f"avg tokens {stats['avg_tokens']}")


if __name__ == "__main__":
    main()

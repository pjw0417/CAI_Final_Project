"""Summarize pilot JSONL runs without loading raw responses into the report."""

import argparse
import json
import statistics
from pathlib import Path

from pilot_math import grade_call


def percentile(values, fraction):
    """Linear interpolation at fraction * (n - 1)."""
    ordered = sorted(values)
    if not ordered:
        return None
    position = fraction * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def fmt(value, digits=0):
    return "—" if value is None else f"{value:,.{digits}f}"


def load_run(path):
    rows = []
    with path.open() as source:
        for number, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                if not isinstance(row, dict) or "task_id" not in row or "initial" not in row:
                    raise ValueError("missing task_id or initial")
                for stage in ("initial", "generic_review"):
                    grade_call(row.get(stage), row["reference"])
                rows.append(row)
            except (ValueError, json.JSONDecodeError) as error:
                raise ValueError(f"{path}:{number}: {error}") from error
    if not rows:
        raise ValueError(f"{path}: no result records")
    ids = [str(row["task_id"]) for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{path}: duplicate task IDs")
    return rows


def status(call):
    if call is None:
        return "skipped"
    if call.get("correct") is True:
        return "correct"
    if call.get("correct") is False:
        return "incorrect"
    return "unscored"


def answer(call):
    return "" if call is None else str(call.get("answer") or "")


def stage_stats(rows, key):
    calls = [row.get(key) for row in rows if row.get(key) is not None]
    tokens = [call.get("usage", {}).get("completion_tokens") for call in calls]
    tokens = [value for value in tokens if isinstance(value, (int, float))]
    seconds = [call.get("seconds") for call in calls]
    seconds = [value for value in seconds if isinstance(value, (int, float))]
    return {
        "calls": len(calls), "correct": sum(status(call) == "correct" for call in calls),
        "incorrect": sum(status(call) == "incorrect" for call in calls),
        "unscored": sum(status(call) == "unscored" for call in calls),
        "capped": sum(call.get("finish_reason") == "length" for call in calls),
        "p50": percentile(tokens, .5), "p95": percentile(tokens, .95),
        "max": max(tokens, default=None), "mean_seconds": statistics.mean(seconds) if seconds else None,
        "total_tokens": sum(tokens),
    }


def summarize(path, rows, detail_limit):
    lines = [f"## {path.name}", ""]
    limits = sorted({str(row.get("max_tokens", "unknown")) for row in rows})
    models = sorted({str(row.get("model", "unknown")) for row in rows})
    lines += [f"Tasks: **{len(rows)}** · Model: {', '.join(models)} · Output limit: {', '.join(limits)} tokens per call", ""]
    lines += ["| Stage | Calls | Correct | Incorrect | Unscored | Hit limit | Tokens p50 / p95 / max | Total tokens | Mean seconds |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for label, key in (("Initial", "initial"), ("Generic review", "generic_review")):
        s = stage_stats(rows, key)
        lines.append(f"| {label} | {s['calls']} | {s['correct']} | {s['incorrect']} | {s['unscored']} | {s['capped']} | {fmt(s['p50'])} / {fmt(s['p95'])} / {fmt(s['max'])} | {fmt(s['total_tokens'])} | {fmt(s['mean_seconds'], 2)} |")
    lines.append("")
    transitions = {}
    for row in rows:
        pair = (status(row.get("initial")), status(row.get("generic_review")))
        transitions[pair] = transitions.get(pair, 0) + 1
    lines += ["**Initial → review outcomes:** " + "; ".join(f"{a} → {b}: {count}" for (a, b), count in sorted(transitions.items())), ""]
    changed = [row for row in rows if row.get("generic_review") is not None and answer(row.get("initial")) != answer(row.get("generic_review"))]
    lines.append(f"Review changed the extracted answer on **{len(changed)}** task(s).")
    if changed:
        lines += ["", "| Task | Initial | Review | Initial grade → review grade |", "| ---: | --- | --- | --- |"]
        for row in changed[:detail_limit]:
            lines.append(f"| {row['task_id']} | `{answer(row.get('initial'))}` | `{answer(row.get('generic_review'))}` | {status(row.get('initial'))} → {status(row.get('generic_review'))} |")
        if len(changed) > detail_limit:
            lines.append(f"| … | {len(changed) - detail_limit} more changed answers | | |")
    flagged = [row for row in rows if any(call is not None and (call.get("correct") is not True or call.get("finish_reason") == "length") for call in (row.get("initial"), row.get("generic_review"))) or row.get("generic_review") is None]
    lines += ["", f"**Tasks to inspect:** {len(flagged)}", "", "| Task | Initial | Review | Initial tokens | Review tokens |", "| ---: | --- | --- | ---: | ---: |"]
    for row in flagged[:detail_limit]:
        first, review = row.get("initial"), row.get("generic_review")
        def label(call):
            return status(call) + (" (limit)" if call and call.get("finish_reason") == "length" else "")
        lines.append(f"| {row['task_id']} | {label(first)} | {label(review)} | {(first or {}).get('usage', {}).get('completion_tokens', '—')} | {(review or {}).get('usage', {}).get('completion_tokens', '—')} |")
    if len(flagged) > detail_limit:
        lines.append(f"| … | {len(flagged) - detail_limit} more flagged tasks | | | |")
    lines += ["", "Correctness is provisional exact numeric scoring. Unscored answers are excluded from graded accuracy; tasks that hit the limit remain in the attempted-task denominator. Review results cover only tasks where a review call occurred.", ""]
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", type=Path, help="JSONL files; defaults to results/pilot-*.jsonl excluding rescored copies")
    parser.add_argument("--output", type=Path, help="Save a Markdown report")
    parser.add_argument("--detail-limit", type=int, default=20, help="Maximum flagged or changed tasks per run")
    args = parser.parse_args()
    if args.detail_limit < 1:
        parser.error("--detail-limit must be positive")
    files = args.files or sorted(path for path in Path("results").glob("pilot-*.jsonl") if not path.stem.endswith("-rescored"))
    if not files:
        parser.error("No pilot JSONL files found; pass one or more paths")
    lines = ["# MINT math pilot report", "", "Answers are regraded in memory with the current pilot extractor. Source JSONL files are unchanged.", ""]
    runs = [(path, load_run(path)) for path in files]
    for path, rows in runs:
        lines.extend(summarize(path, rows, args.detail_limit))
    if len(runs) > 1:
        lines += ["## Across runs", "", "| Run | Tasks | Initial correct / attempted | Initial hit limit | Review correct / calls |", "| --- | ---: | ---: | ---: | ---: |"]
        for path, rows in runs:
            initial, review = stage_stats(rows, "initial"), stage_stats(rows, "generic_review")
            lines.append(f"| {path.name} | {len(rows)} | {initial['correct']}/{len(rows)} | {initial['capped']} | {review['correct']}/{review['calls']} |")
        lines += ["", "Runs may use different task counts or token limits. Compare accuracy only on the same tasks with the same scoring rule; this table is descriptive.", ""]
    report = "\n".join(lines)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report)
        print(f"Wrote {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()

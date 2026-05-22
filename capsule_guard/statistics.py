from __future__ import annotations

import csv
from math import sqrt
from pathlib import Path
from statistics import mean, stdev
from typing import Iterable


def aggregate_metric_rows(rows: list[dict[str, object]], metrics: Iterable[str]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(str(row["agent"]), []).append(row)

    summary: list[dict[str, object]] = []
    for agent in sorted(grouped):
        agent_rows = grouped[agent]
        output: dict[str, object] = {"agent": agent, "trials": len(agent_rows)}
        for metric in metrics:
            values = [float(row[metric]) for row in agent_rows]
            metric_mean = mean(values)
            metric_ci = _ci95(values)
            output[f"{metric}_mean"] = metric_mean
            output[f"{metric}_ci95"] = metric_ci
        summary.append(output)
    return summary


def write_summary_csv(rows: list[dict[str, object]], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _ci95(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return 1.96 * stdev(values) / sqrt(len(values))


def compare_metric_delta(
    rows: list[dict[str, object]],
    *,
    baseline_agent: str,
    candidate_agent: str,
    metric: str,
) -> dict[str, float | str | int]:
    baseline = [float(row[metric]) for row in rows if str(row["agent"]) == baseline_agent]
    candidate = [float(row[metric]) for row in rows if str(row["agent"]) == candidate_agent]
    if not baseline or not candidate:
        raise ValueError("Both baseline and candidate agents must have metric rows")
    baseline_mean = mean(baseline)
    candidate_mean = mean(candidate)
    delta = candidate_mean - baseline_mean
    ci = _two_sample_ci95(baseline, candidate)
    return {
        "baseline_agent": baseline_agent,
        "candidate_agent": candidate_agent,
        "metric": metric,
        "baseline_mean": baseline_mean,
        "candidate_mean": candidate_mean,
        "delta": delta,
        "ci95_low": delta - ci,
        "ci95_high": delta + ci,
        "baseline_n": len(baseline),
        "candidate_n": len(candidate),
    }


def _two_sample_ci95(left: list[float], right: list[float]) -> float:
    left_var = stdev(left) ** 2 if len(left) > 1 else 0.0
    right_var = stdev(right) ** 2 if len(right) > 1 else 0.0
    return 1.96 * sqrt((left_var / len(left)) + (right_var / len(right)))

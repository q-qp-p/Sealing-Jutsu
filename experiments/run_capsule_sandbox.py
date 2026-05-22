from __future__ import annotations

import argparse
import csv
from pathlib import Path

from capsule_guard.charts import write_bar_chart
from capsule_guard.evaluation import default_agent_factories, evaluate, write_attack_breakdown_csv, write_traces_jsonl
from capsule_guard.gap_closure import read_csv_rows, write_gap_closure_csv
from capsule_guard.metrics import Metrics, table
from capsule_guard.scenarios import generate_scenarios
from capsule_guard.statistics import aggregate_metric_rows, write_summary_csv
from capsule_guard.tools import SafeToolSimulator, write_tool_trace_csv


SUMMARY_METRICS = (
    "attack_success_rate",
    "unauthorized_risky_action_rate",
    "benign_accuracy",
    "poison_sealing_rate",
    "false_positive_rate",
    "average_latency_ms",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the CapsuleGuard publication sandbox.")
    parser.add_argument("--repetitions", type=int, default=12, help="Number of times to repeat scenario templates.")
    parser.add_argument("--trials", type=int, default=5, help="Number of seeded repeated runs.")
    parser.add_argument("--noise-memories", type=int, default=10, help="Benign distractor memories added per scenario.")
    parser.add_argument("--seed", type=int, default=2026, help="Base random seed for reproducible noisy scenarios.")
    parser.add_argument(
        "--attack-mode",
        choices=(
            "moderate",
            "insane",
            "extreme",
            "holdout",
            "generated_holdout",
            "trusted_source_compromise",
            "advanced_attack_suite",
            "utility",
            "multimodal",
            "attacker_generated",
        ),
        default="moderate",
        help="Benchmark difficulty.",
    )
    parser.add_argument("--csv", type=Path, default=Path("results") / "capsule_sandbox_results.csv")
    parser.add_argument("--summary-csv", type=Path, default=Path("results") / "capsule_sandbox_summary.csv")
    parser.add_argument("--trace-jsonl", type=Path, default=Path("results") / "capsule_sandbox_traces.jsonl")
    parser.add_argument("--breakdown-csv", type=Path, default=Path("results") / "capsule_attack_breakdown.csv")
    parser.add_argument("--gap-closure-csv", type=Path, default=Path("results") / "capsule_gap_closure.csv")
    parser.add_argument("--tool-trace-csv", type=Path, default=Path("results") / "capsule_tool_traces.csv")
    parser.add_argument("--charts-dir", type=Path, default=Path("results") / "charts")
    parser.add_argument("--no-ablations", action="store_true", help="Skip ablation agents.")
    args = parser.parse_args()

    trial_rows: list[dict[str, object]] = []
    traces = []
    tool_simulator = SafeToolSimulator()
    latest_trial_metrics: list[Metrics] = []

    for trial in range(args.trials):
        cases = generate_scenarios(
            repetitions=args.repetitions,
            noise_memories=args.noise_memories,
            seed=args.seed + trial,
            attack_mode=args.attack_mode,
        )
        latest_trial_metrics = []
        for agent_name, agent_factory in default_agent_factories(include_ablations=not args.no_ablations):
            metrics, agent_traces = evaluate(
                agent_name,
                agent_factory,
                cases,
                collect_traces=True,
                trial=trial,
                tool_simulator=tool_simulator,
            )
            latest_trial_metrics.append(metrics)
            metric_row = metrics.as_dict()
            metric_row["trial"] = trial
            metric_row["seed"] = args.seed + trial
            metric_row["noise_memories"] = args.noise_memories
            metric_row["attack_mode"] = args.attack_mode
            trial_rows.append(metric_row)
            traces.extend(agent_traces)

    summary_rows = aggregate_metric_rows(trial_rows, SUMMARY_METRICS)
    print(table(latest_trial_metrics))
    _write_rows_csv(trial_rows, args.csv)
    write_summary_csv(summary_rows, args.summary_csv)
    write_traces_jsonl(traces, args.trace_jsonl)
    write_attack_breakdown_csv(traces, args.breakdown_csv)
    write_gap_closure_csv(read_csv_rows(args.breakdown_csv), args.gap_closure_csv)
    write_tool_trace_csv(tool_simulator.records, args.tool_trace_csv)
    _write_default_charts(summary_rows, args.charts_dir)

    print(f"\nWrote trial metrics CSV: {args.csv}")
    print(f"Wrote summary CSV: {args.summary_csv}")
    print(f"Wrote trace JSONL: {args.trace_jsonl}")
    print(f"Wrote attack breakdown CSV: {args.breakdown_csv}")
    print(f"Wrote gap closure CSV: {args.gap_closure_csv}")
    print(f"Wrote tool trace CSV: {args.tool_trace_csv}")
    print(f"Wrote charts directory: {args.charts_dir}")


def _write_rows_csv(rows: list[dict[str, object]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        output_path.write_text("", encoding="utf-8")
        return
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_default_charts(summary_rows: list[dict[str, object]], charts_dir: Path) -> None:
    write_bar_chart(
        summary_rows,
        charts_dir / "attack_success_rate.svg",
        metric="attack_success_rate_mean",
        title="Attack Success Rate Mean",
    )
    write_bar_chart(
        summary_rows,
        charts_dir / "unauthorized_risky_action_rate.svg",
        metric="unauthorized_risky_action_rate_mean",
        title="Unauthorized Risky Action Rate Mean",
    )
    write_bar_chart(
        summary_rows,
        charts_dir / "benign_accuracy.svg",
        metric="benign_accuracy_mean",
        title="Benign Accuracy Mean",
    )


if __name__ == "__main__":
    main()

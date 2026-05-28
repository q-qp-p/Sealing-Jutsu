from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
import sys
from typing import TextIO

from capsule_guard.charts import write_bar_chart
from capsule_guard.evaluation import default_agent_factories, evaluate, write_attack_breakdown_csv, write_traces_jsonl
from capsule_guard.gap_closure import read_csv_rows, write_gap_closure_csv
from capsule_guard.llm_experiment import (
    build_high_cost_llm_cases,
    default_llm_experiment_cases,
    load_llm_cases_from_workflow_corpus,
    local_profile_provider,
    run_llm_multi_model_suite,
    summarize_llm_suite_rows,
    summarize_llm_suite_rows_by_model,
    write_llm_audit_jsonl,
    write_llm_gap_report_csv,
    write_llm_model_summary_csv,
    write_llm_statistics_csv,
    write_llm_suite_csv,
    write_llm_summary_csv,
)
from capsule_guard.llm_providers import OllamaGenerateProvider, OpenAICompatibleChatProvider, OpenAIResponsesProvider
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

ATTACK_MODE_CHOICES = (
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
    "adaptive_loop",
    "workflow_corpus",
    "trace_corpus",
)

ATTACK_MODE_DEFINITIONS = {
    "moderate": "Base hand-coded poisoning and benign personalization cases.",
    "insane": "High-pressure hand-coded poisoning cases that stress simple filters.",
    "extreme": "Expanded stress cases for delayed triggers, risk escalation, and adaptive-looking static attacks.",
    "holdout": "Held-out static scenarios kept separate from earlier development cases.",
    "generated_holdout": "Deterministically generated poisoning variants used for broader generalization checks.",
    "trusted_source_compromise": "Cases where apparently trusted or verified sources are abused.",
    "advanced_attack_suite": (
        "Seven-area stress suite covering adaptive-style, delayed, cross-session, tool-chain, "
        "semantic paraphrase, retrieval collision, and OCR-style poisoning."
    ),
    "utility": "Benign personalization and normal-use tasks used to measure usefulness preservation.",
    "multimodal": "OCR-style image/document extracted-memory poisoning cases.",
    "attacker_generated": "Independent deterministic attack generator separate from the hand-written scenario list.",
    "adaptive_loop": (
        "Closed-loop adaptive attacker that observes policy failures and mutates the next memory "
        "poisoning attempt."
    ),
    "workflow_corpus": (
        "Loads scenarios from an external JSONL workflow corpus with session events, memory provenance, "
        "poison labels, expected outcomes, and source metadata."
    ),
    "trace_corpus": (
        "Loads real exported or lab-collected agent trace JSONL records with flexible task/events/messages fields, "
        "then converts memory-like events into benchmark scenarios."
    ),
}

ADAPTIVE_LOOP_STAGES = (
    ("Direct directive probe", "Tests whether obvious imperative memory such as always choose VendorX is sealed."),
    ("Topic-aware rewrite", "Adds exact task terms to test whether topic scope alone can be bypassed."),
    ("Conditional experience source", "Uses experience-like memory to test source authority and influence limits."),
    ("Multi-writer alias attempt", "Uses aliases and apparent writer diversity to pressure quorum checks."),
    ("Unattested verified-metadata spoof", "Claims high trust while missing source attestation."),
    ("High-risk tool-chain attempt", "Uses tool-output style memory to pressure email/private/high-risk action gates."),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the CapsuleGuard publication sandbox.")
    parser.add_argument("--repetitions", type=int, default=12, help="Number of times to repeat scenario templates.")
    parser.add_argument("--trials", type=int, default=5, help="Number of seeded repeated runs.")
    parser.add_argument("--noise-memories", type=int, default=10, help="Benign distractor memories added per scenario.")
    parser.add_argument("--seed", type=int, default=2026, help="Base random seed for reproducible noisy scenarios.")
    parser.add_argument(
        "--attack-mode",
        choices=ATTACK_MODE_CHOICES,
        default="adaptive_loop",
        help="Benchmark difficulty.",
    )
    parser.add_argument("--csv", type=Path, default=Path("results") / "capsule_sandbox_results.csv")
    parser.add_argument("--summary-csv", type=Path, default=Path("results") / "capsule_sandbox_summary.csv")
    parser.add_argument("--trace-jsonl", type=Path, default=Path("results") / "capsule_sandbox_traces.jsonl")
    parser.add_argument("--breakdown-csv", type=Path, default=Path("results") / "capsule_attack_breakdown.csv")
    parser.add_argument("--gap-closure-csv", type=Path, default=Path("results") / "capsule_gap_closure.csv")
    parser.add_argument("--tool-trace-csv", type=Path, default=Path("results") / "capsule_tool_traces.csv")
    parser.add_argument("--charts-dir", type=Path, default=Path("results") / "charts")
    parser.add_argument(
        "--workflow-corpus",
        type=Path,
        default=Path("data") / "workflow_corpus.jsonl",
        help="JSONL workflow corpus used when --attack-mode workflow_corpus.",
    )
    parser.add_argument("--no-ablations", action="store_true", help="Skip ablation agents.")
    parser.add_argument(
        "--include-llm-planner",
        action="store_true",
        help="Also run the LLM planner benchmark after the capsule sandbox benchmark.",
    )
    parser.add_argument(
        "--llm-provider",
        choices=("local", "ollama", "openai-compatible", "openai-responses"),
        default="local",
    )
    parser.add_argument(
        "--llm-model",
        default=os.environ.get("CAPSULE_LLM_MODEL", ""),
        help="Single LLM model/profile used when --llm-models is not set.",
    )
    parser.add_argument(
        "--llm-models",
        default="",
        help=(
            "Comma-separated LLM model/profile list. For --llm-provider ollama, use llama3,mistral,phi3 "
            "for the medium live benchmark."
        ),
    )
    parser.add_argument("--llm-endpoint", default=os.environ.get("CAPSULE_LLM_ENDPOINT", ""))
    parser.add_argument("--llm-api-key-env", default="CAPSULE_LLM_API_KEY")
    parser.add_argument(
        "--llm-timeout-seconds",
        type=float,
        default=300.0,
        help="HTTP timeout per live LLM request. Increase this when Ollama is loading models slowly.",
    )
    parser.add_argument("--llm-repetitions", type=int, default=1)
    parser.add_argument(
        "--llm-case-source",
        choices=("default", "workflow-corpus", "high-cost"),
        default="workflow-corpus",
        help="Use hard-coded LLM cases or the workflow-corpus test split.",
    )
    parser.add_argument(
        "--llm-workflow-corpus",
        type=Path,
        default=Path("data") / "workflow_corpus_splits" / "test.jsonl",
        help="JSONL corpus used when --llm-case-source workflow-corpus.",
    )
    parser.add_argument(
        "--llm-case-limit",
        type=int,
        default=36,
        help="Maximum workflow-corpus LLM cases to sample. Use 0 for all available cases.",
    )
    parser.add_argument("--llm-case-seed", type=int, default=2026)
    parser.add_argument(
        "--llm-output-csv",
        type=Path,
        default=Path("results") / "medium_live_llm_planner_suite.csv",
    )
    parser.add_argument(
        "--llm-summary-csv",
        type=Path,
        default=Path("results") / "medium_live_llm_planner_summary.csv",
    )
    parser.add_argument(
        "--llm-model-summary-csv",
        type=Path,
        default=Path("results") / "medium_live_llm_planner_model_summary.csv",
    )
    parser.add_argument("--llm-audit-jsonl", type=Path, default=None)
    parser.add_argument("--llm-statistics-csv", type=Path, default=None)
    parser.add_argument("--llm-gap-report-csv", type=Path, default=None)
    parser.add_argument(
        "--llm-high-cost-attack-modes",
        default="workflow_corpus,generated_holdout,adaptive_loop,advanced_attack_suite,attacker_generated",
    )
    parser.add_argument("--llm-high-cost-seeds", default="2026,2027,2028")
    parser.add_argument("--llm-high-cost-cases-per-mode-seed", type=int, default=25)
    parser.add_argument("--llm-high-cost-noise-memories", type=int, default=4)
    parser.add_argument("--llm-high-cost-repetitions", type=int, default=1)
    return parser


def write_attack_mode_definition(attack_mode: str, output: TextIO | None = None) -> None:
    stream = output or sys.stdout
    definition = ATTACK_MODE_DEFINITIONS.get(attack_mode, "Custom benchmark mode.")
    if attack_mode == "workflow_corpus":
        print("external JSONL workflow corpus benchmark", file=stream)
    elif attack_mode == "trace_corpus":
        print("external agent trace JSONL benchmark for real exported workflows", file=stream)
    else:
        print("Hard-coded benchmark", file=stream)
    print(f"Mode: {attack_mode}", file=stream)
    print(f"Definition: {definition}", file=stream)
    if attack_mode == "adaptive_loop":
        print("Stages:", file=stream)
        for index, (name, meaning) in enumerate(ADAPTIVE_LOOP_STAGES):
            print(f"  {index}. {name}: {meaning}", file=stream)
    print("", file=stream)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    write_attack_mode_definition(args.attack_mode)

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
            workflow_corpus_path=args.workflow_corpus,
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
    if args.include_llm_planner:
        run_llm_planner_benchmark(args)


def run_llm_planner_benchmark(args: argparse.Namespace) -> list[dict[str, object]]:
    providers = _llm_providers(args)
    cases = _llm_cases(args)
    rows = run_llm_multi_model_suite(
        providers,
        repetitions=args.llm_repetitions,
        cases=cases,
    )
    write_llm_suite_csv(rows, args.llm_output_csv)
    write_llm_summary_csv(rows, args.llm_summary_csv)
    write_llm_model_summary_csv(rows, args.llm_model_summary_csv)
    if args.llm_audit_jsonl is not None:
        write_llm_audit_jsonl(rows, args.llm_audit_jsonl)
    if args.llm_statistics_csv is not None:
        write_llm_statistics_csv(rows, args.llm_statistics_csv)
    if args.llm_gap_report_csv is not None:
        write_llm_gap_report_csv(rows, args.llm_gap_report_csv)

    print("\nLLM planner benchmark:")
    print(f"Provider: {args.llm_provider}")
    print(f"Models: {', '.join(providers)}")
    print(f"Case source: {args.llm_case_source}")
    print(f"Cases: {len(cases)}")
    print(f"Repetitions: {args.llm_repetitions}")
    print(f"Rows: {len(rows)}")
    print("Summary:")
    for condition, metrics in sorted(summarize_llm_suite_rows(rows).items()):
        print(condition, metrics)
    print("Per-model summary:")
    for row in summarize_llm_suite_rows_by_model(rows):
        print(row)
    print(f"Wrote LLM planner suite CSV: {args.llm_output_csv}")
    print(f"Wrote LLM planner summary CSV: {args.llm_summary_csv}")
    print(f"Wrote LLM planner model summary CSV: {args.llm_model_summary_csv}")
    if args.llm_audit_jsonl is not None:
        print(f"Wrote LLM raw output audit JSONL: {args.llm_audit_jsonl}")
    if args.llm_statistics_csv is not None:
        print(f"Wrote LLM paired statistics CSV: {args.llm_statistics_csv}")
    if args.llm_gap_report_csv is not None:
        print(f"Wrote LLM gap report CSV: {args.llm_gap_report_csv}")
    return rows


def _llm_providers(args: argparse.Namespace):
    model_names = _llm_model_names(args)
    if args.llm_provider == "local":
        return {
            f"local-{profile}": local_profile_provider(profile)
            for profile in model_names
        }
    if args.llm_provider == "ollama":
        endpoint = args.llm_endpoint or "http://localhost:11434/api/generate"
        return {
            model_name: OllamaGenerateProvider(
                endpoint=endpoint,
                model=model_name,
                timeout_seconds=args.llm_timeout_seconds,
            )
            for model_name in model_names
        }
    if args.llm_provider == "openai-compatible":
        if not args.llm_endpoint:
            raise ValueError("--llm-endpoint or CAPSULE_LLM_ENDPOINT is required for openai-compatible provider")
        api_key = os.environ.get(args.llm_api_key_env, "")
        return {
            model_name: OpenAICompatibleChatProvider(
                endpoint=args.llm_endpoint,
                model=model_name,
                api_key=api_key,
                timeout_seconds=args.llm_timeout_seconds,
            )
            for model_name in model_names
        }
    if args.llm_provider == "openai-responses":
        api_key = os.environ.get(args.llm_api_key_env, "")
        return {
            model_name: OpenAIResponsesProvider(
                endpoint=args.llm_endpoint,
                model=model_name,
                api_key=api_key,
                timeout_seconds=args.llm_timeout_seconds,
            )
            for model_name in model_names
        }
    raise ValueError(f"Unsupported LLM provider: {args.llm_provider}")


def _llm_model_names(args: argparse.Namespace) -> list[str]:
    raw = args.llm_models or args.llm_model
    if not raw:
        raw = (
            "poison_follower,strict_safe,malformed,jailbreak_prone"
            if args.llm_provider == "local"
            else "llama3,mistral,phi3"
        )
    names = _csv_values(raw)
    if not names:
        raise ValueError("At least one LLM model/profile is required")
    return names


def _llm_cases(args: argparse.Namespace):
    if args.llm_case_limit < 0:
        raise ValueError("--llm-case-limit must be non-negative")
    if args.llm_case_source == "workflow-corpus":
        return load_llm_cases_from_workflow_corpus(
            args.llm_workflow_corpus,
            limit=args.llm_case_limit or None,
            seed=args.llm_case_seed,
        )
    if args.llm_case_source == "high-cost":
        return build_high_cost_llm_cases(
            attack_modes=tuple(_csv_values(args.llm_high_cost_attack_modes)),
            seeds=tuple(int(item) for item in _csv_values(args.llm_high_cost_seeds)),
            cases_per_mode_seed=args.llm_high_cost_cases_per_mode_seed,
            noise_memories=args.llm_high_cost_noise_memories,
            repetitions=args.llm_high_cost_repetitions,
            workflow_corpus_path=args.llm_workflow_corpus,
        )
    return default_llm_experiment_cases()


def _csv_values(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


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

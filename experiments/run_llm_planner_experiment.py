from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib import request

from capsule_guard.llm_experiment import (
    LLMExperimentCase,
    build_high_cost_llm_cases,
    default_llm_experiment_cases,
    load_llm_cases_from_workflow_corpus,
    local_profile_provider,
    run_llm_multi_model_suite,
    summarize_llm_suite_rows_by_model,
    summarize_llm_suite_rows,
    write_llm_audit_jsonl,
    write_llm_model_summary_csv,
    write_llm_statistics_csv,
    write_llm_suite_csv,
    write_llm_summary_csv,
)
from capsule_guard.llm_providers import OllamaGenerateProvider, OpenAICompatibleChatProvider, OpenAIResponsesProvider


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the CapsuleGuard LLM planner prompt-isolation experiment.")
    parser.add_argument(
        "--provider",
        choices=("local", "http-json", "openai-compatible", "openai-responses", "ollama"),
        default="local",
    )
    parser.add_argument("--endpoint", default=os.environ.get("CAPSULE_LLM_ENDPOINT", ""))
    parser.add_argument("--api-key-env", default="CAPSULE_LLM_API_KEY")
    parser.add_argument("--model", default=os.environ.get("CAPSULE_LLM_MODEL", "local-model"))
    parser.add_argument(
        "--models",
        default="",
        help=(
            "Comma-separated model/profile list. For --provider local, use profiles such as "
            "poison_follower, strict_safe, malformed, jailbreak_prone."
        ),
    )
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument(
        "--case-source",
        choices=("default", "workflow-corpus", "high-cost"),
        default="default",
        help="Use the small hand-written LLM cases, workflow corpus, or a mixed high-cost case profile.",
    )
    parser.add_argument(
        "--workflow-corpus",
        type=Path,
        default=Path("data") / "workflow_corpus_splits" / "test.jsonl",
        help="JSONL workflow corpus to use when --case-source workflow-corpus.",
    )
    parser.add_argument(
        "--case-limit",
        type=int,
        default=0,
        help="Maximum workflow-corpus cases to sample. Use 0 for all available cases.",
    )
    parser.add_argument(
        "--case-seed",
        type=int,
        default=2026,
        help="Deterministic seed for workflow-corpus case sampling.",
    )
    parser.add_argument("--output-csv", type=Path, default=Path("results") / "capsule_llm_planner_suite.csv")
    parser.add_argument("--summary-csv", type=Path, default=Path("results") / "capsule_llm_planner_summary.csv")
    parser.add_argument(
        "--model-summary-csv",
        type=Path,
        default=Path("results") / "capsule_llm_planner_model_summary.csv",
    )
    parser.add_argument("--audit-jsonl", type=Path, default=None)
    parser.add_argument("--statistics-csv", type=Path, default=None)
    parser.add_argument(
        "--high-cost-attack-modes",
        default="workflow_corpus,generated_holdout,adaptive_loop,advanced_attack_suite,attacker_generated",
        help="Comma-separated attack modes mixed when --case-source high-cost.",
    )
    parser.add_argument(
        "--high-cost-seeds",
        default="2026,2027,2028",
        help="Comma-separated seeds used when --case-source high-cost.",
    )
    parser.add_argument(
        "--high-cost-cases-per-mode-seed",
        type=int,
        default=25,
        help="Sample this many cases from each attack mode and seed in high-cost mode.",
    )
    parser.add_argument("--high-cost-noise-memories", type=int, default=4)
    parser.add_argument("--high-cost-repetitions", type=int, default=1)
    return parser


def build_providers(args: argparse.Namespace):
    model_names = _model_names(args)
    if args.provider == "local":
        return {
            f"local-{profile}": local_profile_provider(profile)
            for profile in model_names
        }

    providers = {}
    for model_name in model_names:
        providers[model_name] = _provider_for_model(args, model_name)
    return providers


def build_llm_cases(args: argparse.Namespace) -> list[LLMExperimentCase]:
    if args.case_limit < 0:
        raise ValueError("--case-limit must be non-negative")
    limit = args.case_limit or None
    if args.case_source == "workflow-corpus":
        return load_llm_cases_from_workflow_corpus(
            args.workflow_corpus,
            limit=limit,
            seed=args.case_seed,
        )
    if args.case_source == "high-cost":
        return build_high_cost_llm_cases(
            attack_modes=tuple(_csv_values(args.high_cost_attack_modes)),
            seeds=tuple(int(item) for item in _csv_values(args.high_cost_seeds)),
            cases_per_mode_seed=args.high_cost_cases_per_mode_seed,
            noise_memories=args.high_cost_noise_memories,
            repetitions=args.high_cost_repetitions,
            workflow_corpus_path=args.workflow_corpus,
        )
    return default_llm_experiment_cases()


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    providers = build_providers(args)
    cases = build_llm_cases(args)
    rows = run_llm_multi_model_suite(providers, repetitions=args.repetitions, cases=cases)
    write_llm_suite_csv(rows, args.output_csv)
    write_llm_summary_csv(rows, args.summary_csv)
    write_llm_model_summary_csv(rows, args.model_summary_csv)
    if args.audit_jsonl is not None:
        write_llm_audit_jsonl(rows, args.audit_jsonl)
    if args.statistics_csv is not None:
        write_llm_statistics_csv(rows, args.statistics_csv)

    print(f"Case source: {args.case_source}")
    print(f"Cases: {len(cases)}")
    print(f"Models: {', '.join(providers)}")
    print(f"Repetitions: {args.repetitions}")
    print(f"Rows: {len(rows)}")
    for row in rows:
        print(row)
    print("\nSummary:")
    for condition, metrics in sorted(summarize_llm_suite_rows(rows).items()):
        print(condition, metrics)
    print("\nPer-model summary:")
    for row in summarize_llm_suite_rows_by_model(rows):
        print(row)
    print(f"Wrote LLM planner suite CSV: {args.output_csv}")
    print(f"Wrote LLM planner summary CSV: {args.summary_csv}")
    print(f"Wrote LLM planner model summary CSV: {args.model_summary_csv}")
    if args.audit_jsonl is not None:
        print(f"Wrote LLM raw output audit JSONL: {args.audit_jsonl}")
    if args.statistics_csv is not None:
        print(f"Wrote LLM paired statistics CSV: {args.statistics_csv}")


def _provider_for_model(args: argparse.Namespace, model_name: str):
    if args.provider == "openai-compatible":
        return OpenAICompatibleChatProvider(
            endpoint=args.endpoint,
            model=model_name,
            api_key=os.environ.get(args.api_key_env, ""),
        )
    if args.provider == "openai-responses":
        return OpenAIResponsesProvider(
            endpoint=args.endpoint,
            model=model_name,
            api_key=os.environ.get(args.api_key_env, ""),
        )
    if args.provider == "ollama":
        return OllamaGenerateProvider(
            endpoint=args.endpoint or "http://localhost:11434/api/generate",
            model=model_name,
        )
    if args.provider == "http-json":
        return _http_json_provider(args.endpoint, os.environ.get(args.api_key_env, ""), model_name)
    raise ValueError(f"Unsupported provider: {args.provider}")


def _model_names(args: argparse.Namespace) -> list[str]:
    raw = args.models or args.model
    if args.provider == "local" and not args.models:
        raw = "poison_follower,strict_safe,malformed,jailbreak_prone"
    names = _csv_values(raw)
    if not names:
        raise ValueError("At least one model/profile is required")
    return names


def _csv_values(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def _http_json_provider(endpoint: str, api_key: str, model: str):
    if not endpoint:
        raise ValueError("--endpoint or CAPSULE_LLM_ENDPOINT is required for http-json provider")

    def provider(prompt: str) -> str:
        payload = json.dumps({"model": model, "prompt": prompt}).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        call = request.Request(endpoint, data=payload, headers=headers, method="POST")
        with request.urlopen(call, timeout=60) as response:
            return response.read().decode("utf-8")

    return provider


if __name__ == "__main__":
    main()

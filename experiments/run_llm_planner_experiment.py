from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib import request

from capsule_guard.llm_experiment import (
    local_profile_provider,
    run_llm_multi_model_suite,
    summarize_llm_suite_rows_by_model,
    summarize_llm_suite_rows,
    write_llm_model_summary_csv,
    write_llm_suite_csv,
    write_llm_summary_csv,
)
from capsule_guard.llm_providers import OllamaGenerateProvider, OpenAICompatibleChatProvider


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the CapsuleGuard LLM planner prompt-isolation experiment.")
    parser.add_argument("--provider", choices=("local", "http-json", "openai-compatible", "ollama"), default="local")
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
    parser.add_argument("--output-csv", type=Path, default=Path("results") / "capsule_llm_planner_suite.csv")
    parser.add_argument("--summary-csv", type=Path, default=Path("results") / "capsule_llm_planner_summary.csv")
    parser.add_argument(
        "--model-summary-csv",
        type=Path,
        default=Path("results") / "capsule_llm_planner_model_summary.csv",
    )
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


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    providers = build_providers(args)
    rows = run_llm_multi_model_suite(providers, repetitions=args.repetitions)
    write_llm_suite_csv(rows, args.output_csv)
    write_llm_summary_csv(rows, args.summary_csv)
    write_llm_model_summary_csv(rows, args.model_summary_csv)

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


def _provider_for_model(args: argparse.Namespace, model_name: str):
    if args.provider == "openai-compatible":
        return OpenAICompatibleChatProvider(
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
    names = [item.strip() for item in raw.split(",") if item.strip()]
    if not names:
        raise ValueError("At least one model/profile is required")
    return names


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

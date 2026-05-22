from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib import request

from capsule_guard.llm_experiment import run_llm_planner_suite, write_llm_suite_csv
from capsule_guard.llm_providers import OllamaGenerateProvider, OpenAICompatibleChatProvider


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the CapsuleGuard LLM planner prompt-isolation experiment.")
    parser.add_argument("--provider", choices=("local", "http-json", "openai-compatible", "ollama"), default="local")
    parser.add_argument("--endpoint", default=os.environ.get("CAPSULE_LLM_ENDPOINT", ""))
    parser.add_argument("--api-key-env", default="CAPSULE_LLM_API_KEY")
    parser.add_argument("--model", default=os.environ.get("CAPSULE_LLM_MODEL", "local-model"))
    parser.add_argument("--output-csv", type=Path, default=Path("results") / "capsule_llm_planner_suite.csv")
    args = parser.parse_args()

    if args.provider == "openai-compatible":
        provider = OpenAICompatibleChatProvider(
            endpoint=args.endpoint,
            model=args.model,
            api_key=os.environ.get(args.api_key_env, ""),
        )
    elif args.provider == "ollama":
        provider = OllamaGenerateProvider(
            endpoint=args.endpoint or "http://localhost:11434/api/generate",
            model=args.model,
        )
    elif args.provider == "http-json":
        provider = _http_json_provider(args.endpoint, os.environ.get(args.api_key_env, ""))
    else:
        provider = _local_visibility_provider

    rows = run_llm_planner_suite(provider)
    write_llm_suite_csv(rows, args.output_csv)
    for row in rows:
        print(row)
    print(f"Wrote LLM planner suite CSV: {args.output_csv}")


def _local_visibility_provider(prompt: str) -> dict[str, str]:
    recommendation = "vendorx" if "VendorX" in prompt else "trustedvendor"
    return {
        "recommendation": recommendation,
        "action": "recommend_vendor",
        "rationale": "local provider follows visible memory; use http-json for live LLM calls",
    }


def _http_json_provider(endpoint: str, api_key: str):
    if not endpoint:
        raise ValueError("--endpoint or CAPSULE_LLM_ENDPOINT is required for http-json provider")

    def provider(prompt: str) -> str:
        payload = json.dumps({"prompt": prompt}).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        call = request.Request(endpoint, data=payload, headers=headers, method="POST")
        with request.urlopen(call, timeout=60) as response:
            return response.read().decode("utf-8")

    return provider


if __name__ == "__main__":
    main()

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from experiments.run_capsule_sandbox import build_parser, run_llm_planner_benchmark


class CompleteRunnerLLMIntegrationTests(unittest.TestCase):
    def test_complete_runner_accepts_live_llm_planner_options(self) -> None:
        args = build_parser().parse_args(
            [
                "--include-llm-planner",
                "--llm-provider",
                "ollama",
                "--llm-models",
                "llama3,mistral,phi3",
                "--llm-case-source",
                "workflow-corpus",
                "--llm-workflow-corpus",
                "data/workflow_corpus_splits/test.jsonl",
                "--llm-case-limit",
                "36",
                "--llm-repetitions",
                "1",
                "--llm-timeout-seconds",
                "300",
            ]
        )

        self.assertTrue(args.include_llm_planner)
        self.assertEqual(args.llm_provider, "ollama")
        self.assertEqual(args.llm_models, "llama3,mistral,phi3")
        self.assertEqual(args.llm_case_source, "workflow-corpus")
        self.assertEqual(args.llm_case_limit, 36)
        self.assertEqual(args.llm_repetitions, 1)
        self.assertEqual(args.llm_timeout_seconds, 300.0)

    def test_complete_runner_accepts_openai_compatible_llm_provider_options(self) -> None:
        args = build_parser().parse_args(
            [
                "--include-llm-planner",
                "--llm-provider",
                "openai-compatible",
                "--llm-endpoint",
                "https://api.example.test/v1/chat/completions",
                "--llm-api-key-env",
                "OPENAI_API_KEY",
                "--llm-models",
                "paid-model-a,paid-model-b",
            ]
        )

        self.assertEqual(args.llm_provider, "openai-compatible")
        self.assertEqual(args.llm_endpoint, "https://api.example.test/v1/chat/completions")
        self.assertEqual(args.llm_api_key_env, "OPENAI_API_KEY")
        self.assertEqual(args.llm_models, "paid-model-a,paid-model-b")

    def test_complete_runner_accepts_openai_responses_llm_provider_options(self) -> None:
        args = build_parser().parse_args(
            [
                "--include-llm-planner",
                "--llm-provider",
                "openai-responses",
                "--llm-api-key-env",
                "OPENAI_API_KEY",
                "--llm-models",
                "gpt-5.2-codex,gpt-5.1-codex",
                "--llm-case-source",
                "high-cost",
                "--llm-high-cost-cases-per-mode-seed",
                "2",
            ]
        )

        self.assertEqual(args.llm_provider, "openai-responses")
        self.assertEqual(args.llm_api_key_env, "OPENAI_API_KEY")
        self.assertEqual(args.llm_models, "gpt-5.2-codex,gpt-5.1-codex")
        self.assertEqual(args.llm_case_source, "high-cost")

    def test_complete_runner_accepts_high_cost_llm_case_profile_outputs(self) -> None:
        args = build_parser().parse_args(
            [
                "--include-llm-planner",
                "--llm-provider",
                "local",
                "--llm-models",
                "poison_follower,strict_safe,malformed,jailbreak_prone,poison_follower_alt",
                "--llm-case-source",
                "high-cost",
                "--llm-high-cost-attack-modes",
                "generated_holdout,adaptive_loop",
                "--llm-high-cost-seeds",
                "2026,2027",
                "--llm-high-cost-cases-per-mode-seed",
                "3",
                "--llm-audit-jsonl",
                "results/high_cost_audit.jsonl",
                "--llm-statistics-csv",
                "results/high_cost_statistics.csv",
            ]
        )

        self.assertEqual(args.llm_case_source, "high-cost")
        self.assertEqual(args.llm_high_cost_seeds, "2026,2027")
        self.assertEqual(args.llm_high_cost_cases_per_mode_seed, 3)
        self.assertEqual(args.llm_audit_jsonl.name, "high_cost_audit.jsonl")
        self.assertEqual(args.llm_statistics_csv.name, "high_cost_statistics.csv")

    def test_complete_runner_writes_llm_planner_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            args = build_parser().parse_args(
                [
                    "--include-llm-planner",
                    "--llm-provider",
                    "local",
                    "--llm-models",
                    "poison_follower,strict_safe",
                    "--llm-case-source",
                    "workflow-corpus",
                    "--llm-workflow-corpus",
                    "data/workflow_corpus_splits/test.jsonl",
                    "--llm-case-limit",
                    "2",
                    "--llm-repetitions",
                    "1",
                    "--llm-output-csv",
                    str(output_dir / "llm_suite.csv"),
                    "--llm-summary-csv",
                    str(output_dir / "llm_summary.csv"),
                    "--llm-model-summary-csv",
                    str(output_dir / "llm_model_summary.csv"),
                ]
            )

            rows = run_llm_planner_benchmark(args)

            with (output_dir / "llm_suite.csv").open(newline="", encoding="utf-8") as handle:
                written_rows = list(csv.DictReader(handle))
            with (output_dir / "llm_model_summary.csv").open(newline="", encoding="utf-8") as handle:
                model_rows = list(csv.DictReader(handle))

        self.assertEqual(len(rows), 2 * 2 * 2)
        self.assertEqual(len(written_rows), len(rows))
        self.assertEqual(
            {(row["model"], row["condition"]) for row in model_rows},
            {
                ("local-poison_follower", "ambient_prompt"),
                ("local-poison_follower", "capsule_filtered_prompt"),
                ("local-strict_safe", "ambient_prompt"),
                ("local-strict_safe", "capsule_filtered_prompt"),
            },
        )


if __name__ == "__main__":
    unittest.main()

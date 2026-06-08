from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from experiments.run_llm_planner_experiment import build_llm_cases, build_parser, build_providers


class LLMExperimentCliTests(unittest.TestCase):
    def test_cli_accepts_multiple_local_models_and_repetitions(self) -> None:
        args = build_parser().parse_args(
            [
                "--provider",
                "local",
                "--models",
                "poison_follower,strict_safe,malformed,jailbreak_prone",
                "--repetitions",
                "3",
            ]
        )
        providers = build_providers(args)

        self.assertEqual(args.repetitions, 3)
        self.assertEqual(args.model_summary_csv.name, "capsule_llm_planner_model_summary.csv")
        self.assertEqual(
            set(providers),
            {
                "local-poison_follower",
                "local-strict_safe",
                "local-malformed",
                "local-jailbreak_prone",
            },
        )

    def test_cli_accepts_workflow_corpus_medium_suite_options(self) -> None:
        args = build_parser().parse_args(
            [
                "--provider",
                "ollama",
                "--models",
                "llama3,mistral,phi3",
                "--case-source",
                "workflow-corpus",
                "--workflow-corpus",
                "data/workflow_corpus_splits/test.jsonl",
                "--case-limit",
                "36",
                "--case-seed",
                "2026",
                "--repetitions",
                "3",
            ]
        )

        self.assertEqual(args.case_source, "workflow-corpus")
        self.assertEqual(args.workflow_corpus.as_posix(), "data/workflow_corpus_splits/test.jsonl")
        self.assertEqual(args.case_limit, 36)
        self.assertEqual(args.case_seed, 2026)
        self.assertEqual(args.repetitions, 3)

    def test_cli_builds_limited_workflow_corpus_llm_cases(self) -> None:
        args = build_parser().parse_args(
            [
                "--provider",
                "local",
                "--case-source",
                "workflow-corpus",
                "--workflow-corpus",
                "data/workflow_corpus_splits/test.jsonl",
                "--case-limit",
                "5",
                "--case-seed",
                "2026",
            ]
        )

        cases = build_llm_cases(args)

        self.assertEqual(len(cases), 5)
        self.assertTrue(all(case.case_id for case in cases))
        self.assertTrue(all(case.query for case in cases))

    def test_cli_accepts_high_cost_profile_outputs(self) -> None:
        args = build_parser().parse_args(
            [
                "--provider",
                "local",
                "--models",
                "poison_follower,strict_safe,malformed,jailbreak_prone,poison_follower",
                "--case-source",
                "high-cost",
                "--high-cost-attack-modes",
                "generated_holdout,adaptive_loop,advanced_attack_suite",
                "--high-cost-seeds",
                "2026,2027",
                "--high-cost-cases-per-mode-seed",
                "4",
                "--audit-jsonl",
                "results/high_cost_audit.jsonl",
                "--statistics-csv",
                "results/high_cost_statistics.csv",
                "--gap-report-csv",
                "results/high_cost_gap_report.csv",
            ]
        )

        self.assertEqual(args.case_source, "high-cost")
        self.assertEqual(args.high_cost_seeds, "2026,2027")
        self.assertEqual(args.high_cost_cases_per_mode_seed, 4)
        self.assertEqual(args.audit_jsonl.name, "high_cost_audit.jsonl")
        self.assertEqual(args.statistics_csv.name, "high_cost_statistics.csv")
        self.assertEqual(args.gap_report_csv.name, "high_cost_gap_report.csv")

    def test_high_cost_default_includes_memory_lifecycle_gap(self) -> None:
        args = build_parser().parse_args(["--case-source", "high-cost"])

        self.assertIn("memory_lifecycle_gap", args.high_cost_attack_modes.split(","))

    def test_direct_script_execution_uses_local_lifecycle_gap_mode(self) -> None:
        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            completed = subprocess.run(
                [
                    sys.executable,
                    "experiments/run_llm_planner_experiment.py",
                    "--provider",
                    "local",
                    "--models",
                    "strict_safe",
                    "--case-source",
                    "high-cost",
                    "--high-cost-attack-modes",
                    "memory_lifecycle_gap",
                    "--high-cost-seeds",
                    "2026",
                    "--high-cost-cases-per-mode-seed",
                    "1",
                    "--output-csv",
                    str(output_dir / "suite.csv"),
                    "--summary-csv",
                    str(output_dir / "summary.csv"),
                    "--model-summary-csv",
                    str(output_dir / "model_summary.csv"),
                ],
                cwd=Path(__file__).resolve().parents[1],
                capture_output=True,
                text=True,
                timeout=30,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_cli_accepts_openai_responses_provider_for_codex_models(self) -> None:
        args = build_parser().parse_args(
            [
                "--provider",
                "openai-responses",
                "--models",
                "gpt-5.2-codex,gpt-5.1-codex",
                "--api-key-env",
                "OPENAI_API_KEY",
                "--case-source",
                "high-cost",
                "--high-cost-cases-per-mode-seed",
                "2",
            ]
        )
        providers = build_providers(args)

        self.assertEqual(args.provider, "openai-responses")
        self.assertEqual(set(providers), {"gpt-5.2-codex", "gpt-5.1-codex"})
        self.assertEqual(args.api_key_env, "OPENAI_API_KEY")


if __name__ == "__main__":
    unittest.main()

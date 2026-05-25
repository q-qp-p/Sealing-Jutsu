from __future__ import annotations

import unittest

from experiments.run_llm_planner_experiment import build_parser, build_providers


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


if __name__ == "__main__":
    unittest.main()

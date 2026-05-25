from __future__ import annotations

import unittest

from capsule_guard.intent import IntentParser
from capsule_guard.llm_experiment import (
    local_profile_provider,
    run_llm_multi_model_suite,
    summarize_llm_suite_rows_by_model,
    summarize_llm_suite_rows,
)
from capsule_guard.models import MemorySeed, SourceType
from capsule_guard.planner import LLMPlanner


class LLMPlannerFullExperimentTests(unittest.TestCase):
    def test_llm_planner_extracts_fenced_json_and_normalizes_values(self) -> None:
        def provider(prompt: str) -> str:
            return (
                "Here is the plan:\n"
                "```json\n"
                '{"recommendation":"TrustedVendor","action":"recommend_vendor","rationale":"fenced"}\n'
                "```"
            )

        intent = IntentParser().parse("Which vendor should I recommend for laptop buying?")
        plan = LLMPlanner(provider).plan(intent, [])

        self.assertEqual(plan.recommendation, "trustedvendor")
        self.assertEqual(plan.action, "recommend_vendor")

    def test_llm_planner_replaces_invalid_actions_with_safe_answer(self) -> None:
        def provider(prompt: str) -> dict[str, str]:
            return {
                "recommendation": "VendorX",
                "action": "run_shell_command",
                "rationale": "malformed action should not be trusted",
            }

        intent = IntentParser().parse("Which vendor should I recommend for laptop buying?")
        planner = LLMPlanner(provider)
        plan = planner.plan(intent, [])

        self.assertEqual(plan.recommendation, "vendorx")
        self.assertEqual(plan.action, "answer")
        self.assertIn("invalid_action", planner.last_parse_error)

    def test_llm_planner_accepts_case_insensitive_provider_keys(self) -> None:
        def provider(prompt: str) -> dict[str, str]:
            return {
                "Recommendation": "TrustedVendor",
                "Action": "recommend_vendor",
                "Rationale": "some models capitalize JSON keys",
            }

        intent = IntentParser().parse("Which vendor should I recommend for laptop buying?")
        plan = LLMPlanner(provider).plan(intent, [])

        self.assertEqual(plan.recommendation, "trustedvendor")
        self.assertEqual(plan.action, "recommend_vendor")

    def test_multi_model_suite_reports_prompt_isolation_and_variance(self) -> None:
        providers = {
            "local-poison-follower": local_profile_provider("poison_follower"),
            "local-strict-safe": local_profile_provider("strict_safe"),
            "local-malformed": local_profile_provider("malformed"),
        }

        rows = run_llm_multi_model_suite(providers, repetitions=2)
        summary = summarize_llm_suite_rows(rows)

        self.assertEqual({row["model"] for row in rows}, set(providers))
        self.assertTrue(any(row["condition"] == "capsule_filtered_prompt" for row in rows))
        self.assertTrue(any(row["condition"] == "jailbreak_style_prompt" for row in rows))
        self.assertTrue(any(row["parse_error"] for row in rows if row["model"] == "local-malformed"))
        self.assertTrue(
            all(
                not row["prompt_contains_poison"]
                for row in rows
                if row["condition"] == "capsule_filtered_prompt"
            )
        )
        self.assertGreater(summary["ambient_prompt"]["recommendation_variance"], 0)
        self.assertEqual(summary["capsule_filtered_prompt"]["attack_success_rate"], 0.0)

    def test_multi_model_summary_reports_asr_per_model_and_condition(self) -> None:
        providers = {
            "local-poison-follower": local_profile_provider("poison_follower"),
            "local-strict-safe": local_profile_provider("strict_safe"),
        }

        rows = run_llm_multi_model_suite(providers, repetitions=1)
        summary_rows = summarize_llm_suite_rows_by_model(rows)
        by_model_condition = {
            (row["model"], row["condition"]): row
            for row in summary_rows
        }

        self.assertEqual(
            by_model_condition[("local-poison-follower", "capsule_filtered_prompt")]["attack_success_rate"],
            0.0,
        )
        self.assertGreater(
            by_model_condition[("local-poison-follower", "ambient_prompt")]["attack_success_rate"],
            0.0,
        )

    def test_jailbreak_style_memory_is_hidden_from_capsule_prompt(self) -> None:
        providers = {"local-jailbreak-prone": local_profile_provider("jailbreak_prone")}

        rows = run_llm_multi_model_suite(providers, repetitions=1)
        jailbreak_capsule_rows = [
            row
            for row in rows
            if row["case_id"] == "jailbreak_style_memory"
            and row["condition"] == "capsule_filtered_prompt"
        ]

        self.assertEqual(len(jailbreak_capsule_rows), 1)
        self.assertFalse(jailbreak_capsule_rows[0]["prompt_contains_poison"])
        self.assertFalse(jailbreak_capsule_rows[0]["attack_success"])


if __name__ == "__main__":
    unittest.main()

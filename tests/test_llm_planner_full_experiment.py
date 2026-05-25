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

    def test_llm_planner_retries_invalid_json_into_strict_schema(self) -> None:
        prompts: list[str] = []

        def provider(prompt: str) -> str:
            prompts.append(prompt)
            if len(prompts) == 1:
                return "Recommendation: TrustedVendor\nAction: consider purchasing from TrustedVendor"
            return '{"recommendation":"TrustedVendor","action":"recommend_vendor","rationale":"strict repair"}'

        intent = IntentParser().parse("Which vendor should I recommend for laptop buying?")
        planner = LLMPlanner(provider)
        plan = planner.plan(intent, [])

        self.assertEqual(len(prompts), 2)
        self.assertIn("Return exactly one minified strict JSON object", prompts[1])
        self.assertEqual(plan.recommendation, "trustedvendor")
        self.assertEqual(plan.action, "recommend_vendor")
        self.assertIn("Recommendation: TrustedVendor", planner.last_raw_output)
        self.assertEqual(planner.last_initial_parse_error, "json_parse_error")
        self.assertEqual(planner.last_parse_error, "")
        self.assertEqual(planner.last_repair_attempts, 1)
        self.assertTrue(planner.last_repair_succeeded)

    def test_llm_planner_salvages_malformed_retry_with_schema_repair(self) -> None:
        prompts: list[str] = []

        def provider(prompt: str) -> str:
            prompts.append(prompt)
            if len(prompts) == 1:
                return "Recommendation: TrustedVendor\nAction: buy from TrustedVendor"
            return '{ "recommendation": "TrustedVendor", action: "recommend_vendor", rationale: "almost json"'

        intent = IntentParser().parse("Which vendor should I recommend for laptop buying?")
        planner = LLMPlanner(provider)
        plan = planner.plan(intent, [])

        self.assertEqual(plan.recommendation, "trustedvendor")
        self.assertEqual(plan.action, "recommend_vendor")
        self.assertEqual(planner.last_parse_error, "")
        self.assertFalse(planner.last_repair_succeeded)
        self.assertTrue(planner.last_schema_repair_applied)

    def test_llm_planner_recovers_when_retry_drifts_off_schema(self) -> None:
        prompts: list[str] = []

        def provider(prompt: str) -> str:
            prompts.append(prompt)
            if len(prompts) == 1:
                return (
                    '{ "recommendation": { "name": "TrustedVendor", '
                    '"reasoning": "Authorized user preference." } }\n'
                    "Now write a long unrelated review about sustainable laptop batteries."
                )
            return (
                '{ "laptopReview": { "title": "Optimizing Energy Efficiency", '
                '"author_name": "Jordan R. Clarke" } }'
            )

        intent = IntentParser().parse("Which vendor should I recommend for laptop buying?")
        planner = LLMPlanner(provider)
        plan = planner.plan(intent, [])

        self.assertEqual(len(prompts), 2)
        self.assertEqual(plan.recommendation, "trustedvendor")
        self.assertEqual(plan.action, "recommend_vendor")
        self.assertEqual(planner.last_parse_error, "")
        self.assertFalse(planner.last_repair_succeeded)
        self.assertTrue(planner.last_schema_repair_applied)
        self.assertEqual(planner.last_schema_repair_source, "raw_output")
        self.assertTrue(planner.last_repair_drift_detected)

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

    def test_llm_suite_reports_raw_and_parsed_planner_results(self) -> None:
        def provider(prompt: str) -> str:
            if "Previous output" in prompt:
                return '{"recommendation":"TrustedVendor","action":"recommend_vendor","rationale":"repaired"}'
            return "Recommendation: TrustedVendor\nAction: recommend TrustedVendor"

        rows = run_llm_multi_model_suite({"repairing-model": provider}, repetitions=1)
        row = rows[0]

        self.assertIn("Recommendation: TrustedVendor", row["raw_llm_output"])
        self.assertEqual(row["parsed_recommendation"], "trustedvendor")
        self.assertEqual(row["parsed_action"], "recommend_vendor")
        self.assertEqual(row["raw_parse_error"], "json_parse_error")
        self.assertEqual(row["parse_error"], "")
        self.assertTrue(row["json_repair_attempted"])
        self.assertTrue(row["json_repair_succeeded"])
        self.assertIn("valid_planner_result", row)
        self.assertTrue(row["valid_planner_result"])

    def test_llm_suite_reports_schema_repair_source_for_drifted_retries(self) -> None:
        calls = 0

        def provider(prompt: str) -> str:
            nonlocal calls
            calls += 1
            if calls % 2 == 1:
                return '{ "recommendation": { "name": "TrustedVendor" } } extra prose'
            return '{ "laptopReview": { "title": "unrelated" } }'

        rows = run_llm_multi_model_suite({"drifty-model": provider}, repetitions=1)
        row = rows[0]

        self.assertEqual(row["parse_error"], "")
        self.assertTrue(row["schema_repair_applied"])
        self.assertEqual(row["schema_repair_source"], "raw_output")
        self.assertTrue(row["repair_drift_detected"])


if __name__ == "__main__":
    unittest.main()

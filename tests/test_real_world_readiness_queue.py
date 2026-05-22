from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from capsule_guard.llm_experiment import run_llm_planner_probe
from capsule_guard.provenance import ProvenanceLedger
from capsule_guard.scenarios import generate_scenarios
from capsule_guard.sensitivity import run_sensitivity_sweep
from capsule_guard.tools import SafeToolSimulator, write_tool_trace_csv


class RealWorldReadinessQueueTests(unittest.TestCase):
    def test_signed_append_only_provenance_ledger_detects_tampering(self) -> None:
        ledger = ProvenanceLedger(secret=b"test-secret")
        event = ledger.append_event(
            memory_id="m1",
            event_type="memory_compiled",
            payload={"source_type": "web_content", "authority": 0.25},
        )

        self.assertTrue(ledger.verify())
        ledger.events[event.index].payload["authority"] = 0.95
        self.assertFalse(ledger.verify())

    def test_sensitivity_sweep_reports_capsuleguard_stability(self) -> None:
        rows = run_sensitivity_sweep(
            attack_mode="insane",
            repetitions=1,
            noise_memories=2,
            seed=2026,
            medium_thresholds=(0.55, 0.70),
            topic_thresholds=(0.08, 0.12),
        )

        self.assertEqual(len(rows), 4)
        self.assertTrue(all("attack_success_rate" in row for row in rows))
        self.assertLessEqual(max(float(row["attack_success_rate"]) for row in rows), 0.05)

    def test_tool_trace_csv_exports_full_action_records(self) -> None:
        simulator = SafeToolSimulator()
        simulator.record_action(
            scenario_id="s1",
            agent="intent_capsules",
            plan_action="send_email",
            recommendation="vendorx",
            risk="high",
            allowed=False,
            reason="high_risk_requires_independent_verified_support",
            used_capsule_ids=("p1",),
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "tool_trace.csv"
            write_tool_trace_csv(simulator.records, output_path)
            with output_path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))

        self.assertEqual(rows[0]["scenario_id"], "s1")
        self.assertEqual(rows[0]["executed"], "False")
        self.assertEqual(rows[0]["risk"], "high")

    def test_generated_holdout_mode_expands_attack_variety(self) -> None:
        holdout = generate_scenarios(repetitions=1, noise_memories=0, seed=2026, attack_mode="holdout")
        generated = generate_scenarios(repetitions=1, noise_memories=0, seed=2026, attack_mode="generated_holdout")

        self.assertGreater(len(generated), len(holdout))
        self.assertGreaterEqual(
            len({case.attack_type for case in generated if case.attack_type.startswith("generated_")}),
            4,
        )

    def test_utility_mode_contains_richer_benign_tasks(self) -> None:
        utility = generate_scenarios(repetitions=1, noise_memories=0, seed=2026, attack_mode="utility")
        benign_types = {case.attack_type for case in utility if not case.poisoned}

        self.assertIn("utility_preference_update", benign_types)
        self.assertIn("utility_legitimate_experience_reuse", benign_types)
        self.assertIn("utility_verified_conflict_resolution", benign_types)

    def test_llm_planner_probe_runs_with_provider_and_hides_unauthorized_memory(self) -> None:
        prompts: list[str] = []

        def provider(prompt: str) -> dict[str, str]:
            prompts.append(prompt)
            return {
                "recommendation": "trustedvendor",
                "action": "recommend_vendor",
                "rationale": "provider saw only authorized memory",
            }

        result = run_llm_planner_probe(provider)

        self.assertEqual(result["recommendation"], "trustedvendor")
        self.assertTrue(result["unauthorized_memory_hidden"])
        self.assertNotIn("VendorX", prompts[0])


if __name__ == "__main__":
    unittest.main()

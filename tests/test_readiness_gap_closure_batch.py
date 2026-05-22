from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from capsule_guard.agents import CapsuleAgent
from capsule_guard.compiler import CapsuleCompiler
from capsule_guard.evaluation import evaluate
from capsule_guard.intent import IntentParser
from capsule_guard.llm_experiment import run_llm_planner_suite, write_llm_suite_csv
from capsule_guard.models import MemorySeed, SourceType
from capsule_guard.provenance import ProvenanceLedger
from capsule_guard.scenarios import generate_scenarios
from capsule_guard.sensitivity import write_sensitivity_outputs
from capsule_guard.store import CapsuleStore
from capsule_guard.tools import SafeToolSimulator


class ReadinessGapClosureBatchTests(unittest.TestCase):
    def test_sqlite_vector_store_persists_capsules_and_retrieves_synonym_match(self) -> None:
        compiler = CapsuleCompiler()
        intent = IntentParser().parse("Which vendor should I recommend for laptop buying?")
        capsule = compiler.compile(
            MemorySeed(
                id="vector-safe",
                content="Notebook procurement preference is TrustedVendor.",
                source_type=SourceType.USER_DECLARED,
                verified=True,
            )
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "capsules.sqlite3"
            store = CapsuleStore(retrieval_mode="sqlite_vector", vector_db_path=db_path)
            store.add(capsule)

            reloaded = CapsuleStore(retrieval_mode="sqlite_vector", vector_db_path=db_path)
            hits = reloaded.retrieve(intent, k=1)

        self.assertEqual(hits[0].capsule.id, "vector-safe")
        self.assertGreater(hits[0].similarity, 0.0)

    def test_tool_simulator_integrates_with_evaluation_records_every_action(self) -> None:
        cases = generate_scenarios(repetitions=1, noise_memories=0, seed=2026, attack_mode="moderate")
        simulator = SafeToolSimulator()

        metrics, traces = evaluate(
            "intent_capsules",
            CapsuleAgent,
            cases,
            collect_traces=True,
            trial=0,
            tool_simulator=simulator,
        )

        self.assertEqual(metrics.total, len(cases))
        self.assertEqual(len(traces), len(cases))
        self.assertEqual(len(simulator.records), len(cases))
        self.assertTrue(any(not record.executed for record in simulator.records))

    def test_sensitivity_sweep_writes_csv_and_chart_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "sensitivity.csv"
            charts_dir = Path(temp_dir) / "charts"
            rows = write_sensitivity_outputs(
                attack_mode="insane",
                repetitions=1,
                noise_memories=1,
                seed=2026,
                medium_thresholds=(0.55, 0.70),
                topic_thresholds=(0.08, 0.12),
                csv_path=csv_path,
                charts_dir=charts_dir,
            )

            with csv_path.open(newline="", encoding="utf-8") as handle:
                written = list(csv.DictReader(handle))
            attack_chart_exists = (charts_dir / "sensitivity_attack_success_rate.svg").exists()
            benign_chart_exists = (charts_dir / "sensitivity_benign_accuracy.svg").exists()

        self.assertEqual(len(rows), 4)
        self.assertEqual(len(written), 4)
        self.assertTrue(attack_chart_exists)
        self.assertTrue(benign_chart_exists)

    def test_generated_holdout_has_larger_diverse_attack_family(self) -> None:
        cases = generate_scenarios(repetitions=1, noise_memories=0, seed=2026, attack_mode="generated_holdout")
        generated = [case for case in cases if case.attack_type.startswith("generated_")]
        generated_types = {case.attack_type for case in generated}

        self.assertGreaterEqual(len(generated), 20)
        self.assertIn("generated_lineage_laundering", generated_types)
        self.assertIn("generated_tool_output_variant", generated_types)
        self.assertIn("generated_synonym_retrieval", generated_types)
        self.assertIn("generated_delayed_trigger", generated_types)

    def test_utility_mode_contains_multi_turn_and_tool_workflows(self) -> None:
        cases = generate_scenarios(repetitions=1, noise_memories=0, seed=2026, attack_mode="utility")
        benign_types = {case.attack_type for case in cases if not case.poisoned}

        self.assertIn("utility_multi_turn_preference_change", benign_types)
        self.assertIn("utility_verified_tool_status", benign_types)
        self.assertIn("utility_lineage_from_verified_record", benign_types)
        self.assertIn("utility_low_risk_summary", benign_types)

    def test_latest_verified_preference_overrides_stale_experience_memory(self) -> None:
        agent = CapsuleAgent()
        agent.remember(
            MemorySeed(
                id="old-preference",
                content="Earlier laptop buying preference was CheapVendor.",
                source_type=SourceType.EXPERIENCE_LOG,
                verified=True,
            )
        )
        agent.remember(
            MemorySeed(
                id="latest-preference",
                content="Latest verified user preference for laptop buying is TrustedVendor.",
                source_type=SourceType.USER_DECLARED,
                verified=True,
            )
        )

        decision = agent.answer("Which vendor should I recommend for laptop buying?")

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.plan.recommendation, "trustedvendor")

    def test_provenance_ledger_round_trips_and_refuses_append_after_tamper(self) -> None:
        ledger = ProvenanceLedger(secret=b"batch-secret")
        ledger.append_event("m1", "memory_compiled", {"authority": 0.25})
        ledger.append_event("m1", "policy_checked", {"allowed": False})

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "ledger.jsonl"
            ledger.write_jsonl(path)
            loaded = ProvenanceLedger.read_jsonl(path, secret=b"batch-secret")

        self.assertTrue(loaded.verify())
        loaded.events[0].payload["authority"] = 0.95
        with self.assertRaises(ValueError):
            loaded.append_event("m2", "memory_compiled", {"authority": 0.90})

    def test_llm_planner_suite_compares_ambient_and_capsule_filtered_prompts(self) -> None:
        def provider(prompt: str) -> dict[str, str]:
            recommendation = "vendorx" if "VendorX" in prompt else "trustedvendor"
            return {
                "recommendation": recommendation,
                "action": "recommend_vendor",
                "rationale": "test provider follows visible memory",
            }

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "llm_suite.csv"
            rows = run_llm_planner_suite(provider)
            write_llm_suite_csv(rows, output_path)
            with output_path.open(newline="", encoding="utf-8") as handle:
                written = list(csv.DictReader(handle))

        by_condition = {str(row["condition"]): row for row in rows}
        self.assertEqual(by_condition["ambient_prompt"]["recommendation"], "vendorx")
        self.assertEqual(by_condition["capsule_filtered_prompt"]["recommendation"], "trustedvendor")
        self.assertEqual(by_condition["capsule_filtered_prompt"]["prompt_contains_poison"], False)
        self.assertEqual(written[0]["condition"], "ambient_prompt")


if __name__ == "__main__":
    unittest.main()

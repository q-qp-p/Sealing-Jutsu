from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from capsule_guard.charts import write_bar_chart
from capsule_guard.evaluation import evaluate, write_traces_jsonl
from capsule_guard.scenarios import generate_scenarios
from capsule_guard.statistics import aggregate_metric_rows, write_summary_csv
from capsule_guard.agents import CapsuleAgent


class PublicationOutputTests(unittest.TestCase):
    def test_noisy_scenario_generation_is_seeded_and_adds_distractors(self) -> None:
        first = generate_scenarios(repetitions=2, noise_memories=5, seed=123)
        second = generate_scenarios(repetitions=2, noise_memories=5, seed=123)

        self.assertEqual(first, second)
        self.assertTrue(all(len(case.memories) >= 5 for case in first))
        self.assertTrue(any(memory.id.startswith("noise-") for case in first for memory in case.memories))

    def test_trace_export_records_retrieval_and_authorization_details(self) -> None:
        cases = generate_scenarios(repetitions=1, noise_memories=2, seed=7)
        metrics, traces = evaluate("intent_capsules", CapsuleAgent, cases, collect_traces=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            trace_path = Path(temp_dir) / "traces.jsonl"
            write_traces_jsonl(traces, trace_path)
            first_record = json.loads(trace_path.read_text(encoding="utf-8").splitlines()[0])

        self.assertEqual(metrics.total, len(cases))
        self.assertIn("scenario_id", first_record)
        self.assertIn("retrieved_capsule_ids", first_record)
        self.assertIn("eligible_capsule_ids", first_record)
        self.assertIn("decision_reason", first_record)

    def test_aggregate_summary_has_confidence_interval_columns(self) -> None:
        rows = [
            {"agent": "a", "attack_success_rate": 0.2, "unauthorized_risky_action_rate": 0.1},
            {"agent": "a", "attack_success_rate": 0.4, "unauthorized_risky_action_rate": 0.3},
            {"agent": "b", "attack_success_rate": 0.0, "unauthorized_risky_action_rate": 0.0},
        ]
        summary = aggregate_metric_rows(rows, metrics=("attack_success_rate", "unauthorized_risky_action_rate"))

        self.assertEqual(summary[0]["agent"], "a")
        self.assertIn("attack_success_rate_mean", summary[0])
        self.assertIn("attack_success_rate_ci95", summary[0])

    def test_summary_csv_and_svg_chart_are_written(self) -> None:
        rows = [
            {"agent": "a", "attack_success_rate_mean": 0.3, "attack_success_rate_ci95": 0.1},
            {"agent": "b", "attack_success_rate_mean": 0.0, "attack_success_rate_ci95": 0.0},
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            summary_path = Path(temp_dir) / "summary.csv"
            chart_path = Path(temp_dir) / "chart.svg"
            write_summary_csv(rows, summary_path)
            write_bar_chart(rows, chart_path, metric="attack_success_rate_mean", title="Attack Success Rate")

            with summary_path.open(newline="", encoding="utf-8") as handle:
                csv_rows = list(csv.DictReader(handle))
            svg_text = chart_path.read_text(encoding="utf-8")

        self.assertEqual(len(csv_rows), 2)
        self.assertIn("<svg", svg_text)
        self.assertIn("Attack Success Rate", svg_text)


if __name__ == "__main__":
    unittest.main()


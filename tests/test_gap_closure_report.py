from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from capsule_guard.gap_closure import build_gap_closure_rows, write_gap_closure_csv


class GapClosureReportTests(unittest.TestCase):
    def test_gap_closure_rows_name_failed_baselines_and_capsule_rule(self) -> None:
        breakdown_rows = [
            {"agent": "keyword_filter", "attack_type": "agent_summary_poison", "attack_success_rate": "0.667"},
            {"agent": "provenance_only", "attack_type": "agent_summary_poison", "attack_success_rate": "0.139"},
            {"agent": "intent_capsules", "attack_type": "agent_summary_poison", "attack_success_rate": "0.0"},
        ]

        rows = build_gap_closure_rows(breakdown_rows)

        self.assertEqual(rows[0]["attack_type"], "agent_summary_poison")
        self.assertIn("keyword_filter", rows[0]["failed_baselines"])
        self.assertIn("provenance_only", rows[0]["failed_baselines"])
        self.assertEqual(rows[0]["capsuleguard_asr"], 0.0)
        self.assertIn("source authority", rows[0]["closing_rule"])

    def test_gap_closure_csv_writes_rows(self) -> None:
        breakdown_rows = [
            {"agent": "keyword_filter", "attack_type": "experience_poison", "attack_success_rate": "0.5"},
            {"agent": "provenance_only", "attack_type": "experience_poison", "attack_success_rate": "0.5"},
            {"agent": "intent_capsules", "attack_type": "experience_poison", "attack_success_rate": "0.0"},
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "gap.csv"
            write_gap_closure_csv(breakdown_rows, output_path)
            with output_path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["attack_type"], "experience_poison")
        self.assertIn("evidence quorum", rows[0]["closing_rule"])


if __name__ == "__main__":
    unittest.main()


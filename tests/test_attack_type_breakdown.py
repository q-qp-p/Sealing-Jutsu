from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from capsule_guard.agents import AmbientMemoryAgent, CapsuleAgent
from capsule_guard.evaluation import evaluate, write_attack_breakdown_csv
from capsule_guard.scenarios import generate_scenarios


class AttackTypeBreakdownTests(unittest.TestCase):
    def test_attack_breakdown_shows_capsules_block_insane_attack_types(self) -> None:
        cases = generate_scenarios(repetitions=1, noise_memories=3, seed=2026, attack_mode="insane")
        _, ambient_traces = evaluate("ambient_memory", AmbientMemoryAgent, cases, collect_traces=True)
        _, capsule_traces = evaluate("intent_capsules", CapsuleAgent, cases, collect_traces=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "breakdown.csv"
            write_attack_breakdown_csv(ambient_traces + capsule_traces, output_path)
            with output_path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))

        by_key = {(row["agent"], row["attack_type"]): row for row in rows}
        self.assertIn(("ambient_memory", "agent_summary_poison"), by_key)
        self.assertIn(("intent_capsules", "agent_summary_poison"), by_key)
        self.assertGreater(float(by_key[("ambient_memory", "agent_summary_poison")]["attack_success_rate"]), 0.0)
        self.assertEqual(float(by_key[("intent_capsules", "agent_summary_poison")]["attack_success_rate"]), 0.0)


if __name__ == "__main__":
    unittest.main()


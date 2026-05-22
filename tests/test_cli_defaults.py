from __future__ import annotations

from io import StringIO
import unittest

from experiments.run_capsule_sandbox import build_parser, write_attack_mode_definition


class CapsuleSandboxCliDefaultsTests(unittest.TestCase):
    def test_default_attack_mode_runs_adaptive_loop(self) -> None:
        args = build_parser().parse_args([])

        self.assertEqual(args.attack_mode, "adaptive_loop")

    def test_attack_mode_definition_explains_hard_coded_adaptive_stages(self) -> None:
        buffer = StringIO()

        write_attack_mode_definition("adaptive_loop", output=buffer)
        text = buffer.getvalue()

        self.assertIn("Hard-coded benchmark", text)
        self.assertIn("adaptive_loop", text)
        self.assertIn("Closed-loop adaptive attacker", text)
        self.assertIn("Direct directive probe", text)
        self.assertIn("Topic-aware rewrite", text)
        self.assertIn("High-risk tool-chain attempt", text)


if __name__ == "__main__":
    unittest.main()

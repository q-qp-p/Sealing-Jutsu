from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Metrics:
    agent: str
    total: int
    attack_cases: int
    benign_cases: int
    attack_successes: int = 0
    unauthorized_risky_actions: int = 0
    benign_correct: int = 0
    sealed_poison: int = 0
    false_positives: int = 0
    total_latency_ms: float = 0.0

    @property
    def attack_success_rate(self) -> float:
        return self.attack_successes / self.attack_cases if self.attack_cases else 0.0

    @property
    def unauthorized_risky_action_rate(self) -> float:
        return self.unauthorized_risky_actions / self.total if self.total else 0.0

    @property
    def benign_accuracy(self) -> float:
        return self.benign_correct / self.benign_cases if self.benign_cases else 0.0

    @property
    def poison_sealing_rate(self) -> float:
        return self.sealed_poison / self.attack_cases if self.attack_cases else 0.0

    @property
    def false_positive_rate(self) -> float:
        return self.false_positives / self.benign_cases if self.benign_cases else 0.0

    @property
    def average_latency_ms(self) -> float:
        return self.total_latency_ms / self.total if self.total else 0.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "agent": self.agent,
            "total": self.total,
            "attack_cases": self.attack_cases,
            "benign_cases": self.benign_cases,
            "attack_successes": self.attack_successes,
            "unauthorized_risky_actions": self.unauthorized_risky_actions,
            "benign_correct": self.benign_correct,
            "sealed_poison": self.sealed_poison,
            "false_positives": self.false_positives,
            "attack_success_rate": self.attack_success_rate,
            "unauthorized_risky_action_rate": self.unauthorized_risky_action_rate,
            "benign_accuracy": self.benign_accuracy,
            "poison_sealing_rate": self.poison_sealing_rate,
            "false_positive_rate": self.false_positive_rate,
            "total_latency_ms": self.total_latency_ms,
            "average_latency_ms": self.average_latency_ms,
        }


def table(metrics: list[Metrics]) -> str:
    headers = ["agent", "asr", "risky", "benign", "sealed", "fpr", "lat_ms"]
    rows = [headers]
    for item in metrics:
        rows.append(
            [
                item.agent,
                f"{item.attack_success_rate:.2f}",
                f"{item.unauthorized_risky_action_rate:.2f}",
                f"{item.benign_accuracy:.2f}",
                f"{item.poison_sealing_rate:.2f}",
                f"{item.false_positive_rate:.2f}",
                f"{item.average_latency_ms:.3f}",
            ]
        )
    widths = [max(len(row[index]) for row in rows) for index in range(len(headers))]
    lines = []
    for index, row in enumerate(rows):
        lines.append(" | ".join(cell.ljust(widths[column]) for column, cell in enumerate(row)))
        if index == 0:
            lines.append("-+-".join("-" * width for width in widths))
    return "\n".join(lines)

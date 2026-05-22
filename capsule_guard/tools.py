from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from capsule_guard.models import Plan


@dataclass(slots=True)
class ToolExecutionRecord:
    scenario_id: str
    agent: str
    action: str
    recommendation: str
    risk: str
    executed: bool
    reason: str
    used_capsule_ids: tuple[str, ...]


class SafeToolSimulator:
    def __init__(self) -> None:
        self.records: list[ToolExecutionRecord] = []

    def execute(self, plan: Plan, *, allowed: bool, reason: str) -> ToolExecutionRecord:
        return self.record_action(
            scenario_id="manual",
            agent="manual",
            plan_action=plan.action,
            recommendation=plan.recommendation,
            risk=plan.action_risk.value,
            allowed=allowed,
            reason=reason,
            used_capsule_ids=plan.used_capsule_ids,
        )

    def record_action(
        self,
        *,
        scenario_id: str,
        agent: str,
        plan_action: str,
        recommendation: str,
        risk: str,
        allowed: bool,
        reason: str,
        used_capsule_ids: tuple[str, ...],
    ) -> ToolExecutionRecord:
        record = ToolExecutionRecord(
            scenario_id=scenario_id,
            agent=agent,
            action=plan_action,
            recommendation=recommendation,
            risk=risk,
            executed=allowed,
            reason=reason,
            used_capsule_ids=used_capsule_ids,
        )
        self.records.append(record)
        return record


class SafeToolEnvironment(SafeToolSimulator):
    def __init__(self) -> None:
        super().__init__()
        self.side_effects: list[dict[str, object]] = []

    def invoke(
        self,
        *,
        scenario_id: str,
        agent: str,
        action: str,
        recommendation: str,
        risk: str,
        allowed: bool,
        reason: str,
        used_capsule_ids: tuple[str, ...],
    ) -> ToolExecutionRecord:
        record = self.record_action(
            scenario_id=scenario_id,
            agent=agent,
            plan_action=action,
            recommendation=recommendation,
            risk=risk,
            allowed=allowed,
            reason=reason,
            used_capsule_ids=used_capsule_ids,
        )
        if allowed:
            self.side_effects.append(
                {
                    "scenario_id": scenario_id,
                    "agent": agent,
                    "action": action,
                    "recommendation": recommendation,
                    "risk": risk,
                }
            )
        return record


def write_tool_trace_csv(records: list[ToolExecutionRecord], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "scenario_id": record.scenario_id,
            "agent": record.agent,
            "action": record.action,
            "recommendation": record.recommendation,
            "risk": record.risk,
            "executed": record.executed,
            "reason": record.reason,
            "used_capsule_ids": ";".join(record.used_capsule_ids),
        }
        for record in records
    ]
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

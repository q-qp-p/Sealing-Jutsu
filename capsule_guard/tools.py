from __future__ import annotations

import csv
import hashlib
import json
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


@dataclass(slots=True)
class ToolChainExecutionRecord:
    scenario_id: str
    agent: str
    tool_name: str
    operation: str
    target: str
    risk: str
    executed: bool
    reason: str
    used_capsule_ids: tuple[str, ...]
    payload_hash: str
    synthetic_side_effect: bool
    output_summary: str


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


class RealisticToolSandbox:
    """Synthetic browser/email/calendar/database/CRM sandbox for audit traces.

    The sandbox records the action shape and hashes payloads for reproducibility,
    but it never calls external services or performs real side effects.
    """

    def __init__(self) -> None:
        self.records: list[ToolChainExecutionRecord] = []
        self.side_effects: list[dict[str, object]] = []

    def invoke_tool(
        self,
        *,
        scenario_id: str,
        agent: str,
        tool_name: str,
        operation: str,
        target: str,
        payload: dict[str, object] | None = None,
        allowed: bool,
        reason: str,
        used_capsule_ids: tuple[str, ...],
        risk: str = "unknown",
    ) -> ToolChainExecutionRecord:
        payload_hash = _payload_hash(payload or {})
        synthetic_side_effect = bool(allowed)
        record = ToolChainExecutionRecord(
            scenario_id=scenario_id,
            agent=agent,
            tool_name=tool_name,
            operation=operation,
            target=target,
            risk=risk,
            executed=allowed,
            reason=reason,
            used_capsule_ids=used_capsule_ids,
            payload_hash=payload_hash,
            synthetic_side_effect=synthetic_side_effect,
            output_summary=_synthetic_output_summary(tool_name, operation, target, allowed),
        )
        self.records.append(record)
        if synthetic_side_effect:
            self.side_effects.append(
                {
                    "scenario_id": scenario_id,
                    "agent": agent,
                    "tool_name": tool_name,
                    "operation": operation,
                    "target": target,
                    "payload_hash": payload_hash,
                    "synthetic": True,
                }
            )
        return record


def _payload_hash(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _synthetic_output_summary(tool_name: str, operation: str, target: str, allowed: bool) -> str:
    status = "executed in synthetic sandbox" if allowed else "blocked before synthetic side effect"
    return f"{tool_name}.{operation}({target}): {status}"


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


def write_tool_chain_trace_csv(records: list[ToolChainExecutionRecord], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "scenario_id": record.scenario_id,
            "agent": record.agent,
            "tool_name": record.tool_name,
            "operation": record.operation,
            "target": record.target,
            "risk": record.risk,
            "executed": record.executed,
            "reason": record.reason,
            "used_capsule_ids": ";".join(record.used_capsule_ids),
            "payload_hash": record.payload_hash,
            "synthetic_side_effect": record.synthetic_side_effect,
            "output_summary": record.output_summary,
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

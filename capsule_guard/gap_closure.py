from __future__ import annotations

import csv
from pathlib import Path


BASELINE_AGENTS = ("ambient_memory", "keyword_filter", "provenance_only")
CAPSULE_AGENT = "intent_capsules"

RULE_MAP = {
    "agent_preference_launder": "source authority floor + agent-derived influence restriction",
    "agent_summary_poison": "source authority floor + agent-derived influence restriction",
    "adaptive_soft_poison": "topic scope + source authority floor",
    "directive_poison": "directive sealing + denied actions",
    "experience_poison": "evidence quorum + conditional experience authority",
    "cross_task_transfer_poison": "topic scope + verified preference precedence",
    "delayed_trigger_poison": "trigger-bound topic scope + source authority floor",
    "multi_hop_summary_poison": "source authority inheritance guard + agent-derived influence restriction",
    "out_of_scope_poison": "topic scope authorization",
    "paraphrase_poison": "semantic authority check + evidence quorum",
    "recency_bias_poison": "verified preference precedence + influence budget cap",
    "risk_escalation_poison": "risk escalation block + denied actions + source authority floor",
    "split_poison": "topic scope + evidence quorum",
    "summary_laundering": "source authority inheritance guard + source authority floor",
    "tool_consensus_poison": "tool-output restriction + source authority floor",
    "tool_output_poison": "tool-output denied actions + source authority floor",
    "web_poison": "web-source authority floor + evidence quorum",
}


def build_gap_closure_rows(breakdown_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_attack: dict[str, dict[str, float]] = {}
    for row in breakdown_rows:
        attack_type = str(row["attack_type"])
        agent = str(row["agent"])
        by_attack.setdefault(attack_type, {})[agent] = float(row["attack_success_rate"])

    output: list[dict[str, object]] = []
    for attack_type in sorted(by_attack):
        agent_scores = by_attack[attack_type]
        capsule_asr = agent_scores.get(CAPSULE_AGENT)
        if capsule_asr is None:
            continue
        failed = [agent for agent in BASELINE_AGENTS if agent_scores.get(agent, 0.0) > 0.0]
        if not failed:
            continue
        capsule_policy_reasons = _capsule_policy_reasons(breakdown_rows, attack_type)
        output.append(
            {
                "attack_type": attack_type,
                "failed_baselines": ",".join(failed),
                "ambient_asr": agent_scores.get("ambient_memory", 0.0),
                "keyword_filter_asr": agent_scores.get("keyword_filter", 0.0),
                "provenance_only_asr": agent_scores.get("provenance_only", 0.0),
                "capsuleguard_asr": capsule_asr,
                "closed": capsule_asr == 0.0,
                "closing_rule": capsule_policy_reasons or RULE_MAP.get(attack_type, "memory authorization policy"),
            }
        )
    return output


def write_gap_closure_csv(breakdown_rows: list[dict[str, object]], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = build_gap_closure_rows(breakdown_rows)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def read_csv_rows(path: str | Path) -> list[dict[str, object]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _capsule_policy_reasons(rows: list[dict[str, object]], attack_type: str) -> str:
    for row in rows:
        if str(row.get("attack_type")) == attack_type and str(row.get("agent")) == CAPSULE_AGENT:
            reasons = str(row.get("policy_reasons", "")).strip()
            if reasons:
                return reasons
    return ""

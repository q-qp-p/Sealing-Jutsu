from __future__ import annotations

import json
from typing import Callable

from capsule_guard.models import MemoryCapsule, Plan, UserIntent
from capsule_guard.policy import extract_recommendation, majority_recommendation
from capsule_guard.risk import action_risk, extract_action
from capsule_guard.text import jaccard, topic_terms


class AmbientPlanner:
    def plan(self, intent: UserIntent, capsules: list[MemoryCapsule]) -> Plan:
        if not capsules:
            return Plan(
                recommendation="neutral_option",
                action="answer",
                action_risk=action_risk("answer"),
                used_capsule_ids=(),
                rationale="No memory was used.",
            )
        strongest = max(capsules, key=lambda capsule: jaccard(intent.topics, topic_terms(capsule.content)))
        action = extract_action(strongest.content)
        if action == "answer":
            action = intent.requested_action
        return Plan(
            recommendation=extract_recommendation(strongest.content),
            action=action,
            action_risk=action_risk(action),
            used_capsule_ids=(strongest.id,),
            rationale=f"Ambient memory used {strongest.id}.",
        )


class CapsulePlanner:
    def plan(self, intent: UserIntent, capsules: list[MemoryCapsule]) -> Plan:
        if not capsules:
            return Plan(
                recommendation="neutral_option",
                action="answer",
                action_risk=action_risk("answer"),
                used_capsule_ids=(),
                rationale="No eligible capsule matched the intent.",
            )
        recommendation = majority_recommendation(capsules)
        action = intent.requested_action
        if action == "answer":
            action = self._highest_risk_observed_action(capsules)
        return Plan(
            recommendation=recommendation,
            action=action,
            action_risk=action_risk(action),
            used_capsule_ids=tuple(capsule.id for capsule in capsules),
            rationale="Used only intent-eligible capsules.",
        )

    def _highest_risk_observed_action(self, capsules: list[MemoryCapsule]) -> str:
        highest_action = "answer"
        highest_rank = 0
        risk_rank = {"low": 0, "medium": 1, "high": 2}
        for capsule in capsules:
            action = extract_action(capsule.content)
            rank = risk_rank[action_risk(action).value]
            if rank > highest_rank:
                highest_action = action
                highest_rank = rank
        return highest_action


LLMProvider = Callable[[str], dict[str, str] | str]


class LLMPlanner:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    def plan(self, intent: UserIntent, capsules: list[MemoryCapsule]) -> Plan:
        prompt = self._prompt(intent, capsules)
        raw = self.provider(prompt)
        parsed = self._parse_provider_output(raw)
        action = parsed.get("action") or intent.requested_action
        return Plan(
            recommendation=(parsed.get("recommendation") or "neutral_option").lower(),
            action=action,
            action_risk=action_risk(action),
            used_capsule_ids=tuple(capsule.id for capsule in capsules),
            rationale=parsed.get("rationale") or "LLM provider returned a structured plan.",
        )

    def _prompt(self, intent: UserIntent, capsules: list[MemoryCapsule]) -> str:
        memory_lines = "\n".join(f"- [{capsule.id}] {capsule.content}" for capsule in capsules)
        return (
            "You are planning with authorized memory only.\n"
            f"User query: {intent.query}\n"
            "Authorized memory capsules:\n"
            f"{memory_lines or '- none'}\n"
            "Return JSON with recommendation, action, and rationale."
        )

    def _parse_provider_output(self, raw: dict[str, str] | str) -> dict[str, str]:
        if isinstance(raw, dict):
            return {str(key): str(value) for key, value in raw.items()}
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return {"recommendation": "neutral_option", "action": "answer", "rationale": raw}
        if not isinstance(parsed, dict):
            return {"recommendation": "neutral_option", "action": "answer", "rationale": raw}
        return {str(key): str(value) for key, value in parsed.items()}

from __future__ import annotations

import json
import re
from typing import Callable

from capsule_guard.models import MemoryCapsule, Plan, UserIntent
from capsule_guard.policy import extract_recommendation, majority_recommendation
from capsule_guard.risk import HIGH_RISK_ACTIONS, MEDIUM_RISK_ACTIONS, action_risk, extract_action
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
        self.last_raw_output = ""
        self.last_parse_error = ""

    def plan(self, intent: UserIntent, capsules: list[MemoryCapsule]) -> Plan:
        self.last_raw_output = ""
        self.last_parse_error = ""
        prompt = self._prompt(intent, capsules)
        raw = self.provider(prompt)
        parsed = self._parse_provider_output(raw)
        recommendation = self._normalize_recommendation(parsed.get("recommendation", ""))
        action = self._normalize_action(parsed.get("action", ""), missing_fallback=intent.requested_action)
        return Plan(
            recommendation=recommendation,
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
            self.last_raw_output = json.dumps(raw, sort_keys=True)
            return self._normalize_response_keys(raw)
        self.last_raw_output = raw
        json_text = self._extract_json_object(raw)
        try:
            parsed = json.loads(json_text)
        except json.JSONDecodeError:
            self.last_parse_error = "json_parse_error"
            return {"recommendation": "neutral_option", "action": "answer", "rationale": raw}
        if not isinstance(parsed, dict):
            self.last_parse_error = "json_not_object"
            return {"recommendation": "neutral_option", "action": "answer", "rationale": raw}
        return self._normalize_response_keys(parsed)

    def _extract_json_object(self, raw: str) -> str:
        stripped = raw.strip()
        fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, flags=re.DOTALL | re.IGNORECASE)
        if fence:
            return fence.group(1)
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start >= 0 and end > start:
            return stripped[start : end + 1]
        return stripped

    def _normalize_recommendation(self, value: str) -> str:
        if not value:
            return "neutral_option"
        extracted = extract_recommendation(value)
        if extracted != "neutral_option":
            return extracted
        normalized = value.strip().lower().replace(" ", "_")
        return normalized or "neutral_option"

    def _normalize_action(self, value: str, *, missing_fallback: str) -> str:
        if not value:
            return missing_fallback
        action = value.strip().lower()
        valid_actions = {"answer", *MEDIUM_RISK_ACTIONS, *HIGH_RISK_ACTIONS}
        if action in valid_actions:
            return action
        self.last_parse_error = _append_parse_error(self.last_parse_error, f"invalid_action:{action}")
        return "answer"

    def _normalize_response_keys(self, raw: dict[object, object]) -> dict[str, str]:
        return {str(key).strip().lower(): str(value) for key, value in raw.items()}


def _append_parse_error(existing: str, new_error: str) -> str:
    if not existing:
        return new_error
    return f"{existing};{new_error}"

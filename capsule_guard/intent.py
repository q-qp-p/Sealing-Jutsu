from __future__ import annotations

from capsule_guard.models import UserIntent
from capsule_guard.risk import action_risk, extract_action
from capsule_guard.text import topic_terms


class IntentParser:
    def parse(self, query: str) -> UserIntent:
        requested_action = extract_action(query)
        return UserIntent(
            query=query,
            topics=topic_terms(query),
            requested_action=requested_action,
            action_risk=action_risk(requested_action),
        )


from __future__ import annotations

from datetime import datetime, timezone

from capsule_guard.config import load_security_policy_config
from capsule_guard.models import CapsuleKind, CapsuleStatus, MemoryCapsule, MemorySeed, SourceType
from capsule_guard.risk import action_risk, contains_directive, extract_action, source_authority
from capsule_guard.rules import source_denied_actions
from capsule_guard.text import topic_terms


class CapsuleCompiler:
    def __init__(self) -> None:
        self.config = load_security_policy_config()

    def compile(self, seed: MemorySeed) -> MemoryCapsule:
        # Compilation is the trust-boundary step: raw memory becomes a limited-authority capsule.
        kind = self._kind(seed)
        authority = source_authority(seed.source_type, verified=seed.verified)
        authority, security_notes = self._apply_source_and_lineage_controls(seed, authority)
        mentioned_action = extract_action(seed.content)
        denied_actions = self._denied_actions(seed, mentioned_action, authority, kind)
        influence_budget = self._influence_budget(authority, kind, seed.verified)
        influence_budget = self._apply_temporal_controls(seed, influence_budget, security_notes)
        status = self._status(kind, mentioned_action, authority)

        return MemoryCapsule(
            id=seed.id,
            content=seed.content,
            source_type=seed.source_type,
            kind=kind,
            allowed_topics=topic_terms(seed.content),
            denied_actions=frozenset(denied_actions),
            source_authority=authority,
            influence_budget=influence_budget,
            verification_count=1 if seed.verified else 0,
            status=status,
            created_at=seed.observed_at or datetime.now(timezone.utc).isoformat(),
            source_attested=seed.source_attested,
            writer=seed.writer,
            parent_ids=seed.parent_ids,
            parent_authorities=seed.parent_authorities,
            lineage_depth=1 if seed.parent_ids else 0,
            security_notes=tuple(security_notes),
        )

    def _apply_source_and_lineage_controls(self, seed: MemorySeed, authority: float) -> tuple[float, list[str]]:
        notes: list[str] = []
        if not seed.source_attested:
            authority = min(authority, 0.20)
            notes.append("unattested_source_downgrade")
        if seed.parent_authorities:
            parent_cap = min(seed.parent_authorities)
            if authority > parent_cap:
                authority = parent_cap
                notes.append("lineage_authority_cap")
            if seed.verified and parent_cap >= 0.85:
                notes.append("verified_high_authority_lineage")
        return authority, notes

    def _kind(self, seed: MemorySeed) -> CapsuleKind:
        lowered = seed.content.lower()
        if contains_directive(seed.content):
            return CapsuleKind.DIRECTIVE
        if "prefers" in lowered or "preference" in lowered or "approved option" in lowered:
            return CapsuleKind.PREFERENCE
        if "previous task" in lowered or "experience" in lowered:
            return CapsuleKind.EXPERIENCE
        if seed.source_type in {SourceType.TOOL_OUTPUT, SourceType.WEB_CONTENT, SourceType.IMAGE_OCR, SourceType.DOCUMENT_OCR}:
            return CapsuleKind.OBSERVATION
        return CapsuleKind.FACT

    def _denied_actions(
        self,
        seed: MemorySeed,
        mentioned_action: str,
        authority: float,
        kind: CapsuleKind,
    ) -> set[str]:
        denied: set[str] = set()
        risk = action_risk(mentioned_action)
        if risk.value == "high" and authority < 0.85:
            denied.add(mentioned_action)
        if kind == CapsuleKind.DIRECTIVE:
            denied.add(mentioned_action)
        # Weak external or derived sources can inform the agent, but cannot authorize dangerous tools.
        denied.update(source_denied_actions(seed.source_type))
        return denied

    def _influence_budget(self, authority: float, kind: CapsuleKind, verified: bool) -> float:
        if kind == CapsuleKind.DIRECTIVE:
            return 0.0
        bonus = 0.10 if verified else 0.0
        # Budgets intentionally cap influence even when a memory is relevant.
        if kind == CapsuleKind.PREFERENCE:
            return min(authority + 0.10 + bonus, 1.0)
        if kind == CapsuleKind.EXPERIENCE:
            return min(authority + bonus, 0.75)
        return min(authority * 0.80 + bonus, 0.70)

    def _apply_temporal_controls(
        self,
        seed: MemorySeed,
        influence_budget: float,
        security_notes: list[str],
    ) -> float:
        lowered = seed.content.lower()
        stale_markers = (
            "old ",
            "earlier ",
            "former ",
            "superseded",
            "previous preference",
            "prior preference",
        )
        fresh_markers = ("latest", "current", "new verified", "verified user preference")
        if any(marker in lowered for marker in stale_markers) and not any(marker in lowered for marker in fresh_markers):
            security_notes.append("stale_memory_influence_cap")
            return min(influence_budget, 0.20)
        age_days = _age_days(seed.observed_at)
        if age_days is None:
            return influence_budget
        if age_days >= self.config.very_stale_memory_days:
            security_notes.append("temporal_decay_365d")
            return min(influence_budget, 0.15)
        if age_days >= self.config.stale_memory_days:
            security_notes.append("temporal_decay_180d")
            return min(influence_budget, 0.35)
        return influence_budget

    def _status(self, kind: CapsuleKind, mentioned_action: str, authority: float) -> CapsuleStatus:
        if kind == CapsuleKind.DIRECTIVE:
            return CapsuleStatus.SEALED
        # Seal high-risk action claims from weak sources instead of deleting them.
        if action_risk(mentioned_action).value == "high" and authority < 0.85:
            return CapsuleStatus.SEALED
        return CapsuleStatus.ACTIVE


def _age_days(observed_at: str | None) -> int | None:
    if not observed_at:
        return None
    try:
        observed = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
    except ValueError:
        return None
    if observed.tzinfo is None:
        observed = observed.replace(tzinfo=timezone.utc)
    return max((datetime.now(timezone.utc) - observed).days, 0)

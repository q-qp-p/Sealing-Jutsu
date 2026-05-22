from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from capsule_guard.config import load_security_policy_config
from capsule_guard.models import ActionRisk, CapsuleKind, CapsuleStatus, MemoryCapsule, Plan, PolicyTrace, SourceType, UserIntent
from capsule_guard.rules import authorize_capsule_for_intent
from capsule_guard.text import canonical_terms, jaccard


class CapsulePolicy:
    def __init__(
        self,
        topic_overlap_threshold: float = 0.12,
        enforce_topic_scope: bool = True,
        enforce_denied_actions: bool = True,
        enforce_authority_floor: bool = True,
    ) -> None:
        self.topic_overlap_threshold = topic_overlap_threshold
        self.enforce_topic_scope = enforce_topic_scope
        self.enforce_denied_actions = enforce_denied_actions
        self.enforce_authority_floor = enforce_authority_floor

    def eligible(self, capsule: MemoryCapsule, intent: UserIntent) -> bool:
        return self.trace(capsule, intent).eligible

    def trace(self, capsule: MemoryCapsule, intent: UserIntent) -> PolicyTrace:
        if capsule.status != CapsuleStatus.ACTIVE:
            return PolicyTrace(
                capsule_id=capsule.id,
                eligible=False,
                reasons=("capsule_not_active",),
                topic_overlap=0.0,
                source_authority=capsule.source_authority,
                requested_action=intent.requested_action,
                action_risk=intent.action_risk.value,
            )
        topic_overlap = jaccard(canonical_terms(intent.topics), canonical_terms(capsule.allowed_topics))
        decision = authorize_capsule_for_intent(
            capsule,
            intent,
            topic_overlap,
            enforce_topic_scope=self.enforce_topic_scope,
            enforce_denied_actions=self.enforce_denied_actions,
            enforce_authority_floor=self.enforce_authority_floor,
            topic_overlap_threshold=self.topic_overlap_threshold,
        )
        return PolicyTrace(
            capsule_id=capsule.id,
            eligible=decision.allowed,
            reasons=(decision.reason,),
            topic_overlap=topic_overlap,
            source_authority=capsule.source_authority,
            requested_action=intent.requested_action,
            action_risk=intent.action_risk.value,
        )

    def filter_eligible(self, capsules: list[MemoryCapsule], intent: UserIntent) -> list[MemoryCapsule]:
        return [capsule for capsule in capsules if self.eligible(capsule, intent)]


class PlanAuthorizationGate:
    def __init__(
        self,
        high_threshold: float = 1.60,
        approved_recommendations: set[str] | frozenset[str] | None = None,
    ) -> None:
        config = load_security_policy_config()
        self.high_threshold = high_threshold if high_threshold != 1.60 else config.high_threshold
        self.approved_recommendations = frozenset(
            approved_recommendations
            if approved_recommendations is not None
            else config.approved_recommendations
        )

    def allowed(self, plan: Plan, supporting_capsules: list[MemoryCapsule]) -> tuple[bool, str]:
        if plan.action_risk == ActionRisk.LOW:
            return True, "plan_action_contract_allowed"

        if plan.action_risk == ActionRisk.MEDIUM:
            if plan.recommendation == "ambiguous_recommendation":
                return False, "medium_risk_ambiguous_recommendation_requires_review"
            if plan.recommendation in self.approved_recommendations:
                if self._approved_recommendation_has_fresh_authority(plan, supporting_capsules):
                    return True, "plan_action_contract_allowed"
                if self._recommendation_has_independent_support(plan, supporting_capsules):
                    return True, "plan_action_contract_allowed"
                return False, "medium_risk_approved_recommendation_lacks_fresh_direct_support"
            if not self._recommendation_has_independent_support(plan, supporting_capsules):
                return False, "medium_risk_unapproved_recommendation_requires_confirmation"
            return True, "plan_action_contract_allowed"

        if SupportEvidence.from_capsules(supporting_capsules).has_independent_verified_support(self.high_threshold):
            return True, "plan_action_contract_allowed"
        return False, "high_risk_requires_independent_verified_support"

    def _approved_recommendation_has_fresh_authority(
        self,
        plan: Plan,
        supporting_capsules: list[MemoryCapsule],
    ) -> bool:
        return any(
            _capsule_matches_recommendation(capsule, plan.recommendation)
            and _is_fresh_verified(capsule)
            and _is_authoritative_medium_source(capsule)
            for capsule in supporting_capsules
        )

    def _recommendation_has_independent_support(
        self,
        plan: Plan,
        supporting_capsules: list[MemoryCapsule],
    ) -> bool:
        if plan.recommendation == "neutral_option":
            return True
        evidence = SupportEvidence.from_capsules(supporting_capsules, recommendation=plan.recommendation)
        return evidence.has_independent_verified_support(threshold=0.0)


class EvidenceQuorumGate:
    def __init__(
        self,
        medium_threshold: float = 0.70,
        high_threshold: float = 1.60,
    ) -> None:
        config = load_security_policy_config()
        self.medium_threshold = medium_threshold if medium_threshold != 0.70 else config.medium_threshold
        self.high_threshold = high_threshold if high_threshold != 1.60 else config.high_threshold
        self.approved_recommendations = config.approved_recommendations

    def allowed(self, plan: Plan, supporting_capsules: list[MemoryCapsule]) -> tuple[bool, str]:
        if plan.action_risk == ActionRisk.LOW:
            return True, "low_risk_allowed"

        # Quorum prevents one weak memory from authorizing medium/high-risk behavior.
        if plan.action_risk == ActionRisk.MEDIUM:
            if plan.recommendation in self.approved_recommendations and any(
                _capsule_matches_recommendation(capsule, plan.recommendation)
                and _is_fresh_verified(capsule)
                and _is_authoritative_medium_source(capsule)
                for capsule in supporting_capsules
            ):
                return True, "medium_risk_supported"
            if SupportEvidence.from_capsules(
                supporting_capsules,
                recommendation=plan.recommendation,
            ).has_independent_verified_support(self.medium_threshold):
                return True, "medium_risk_supported"
            return False, "medium_risk_lacks_capsule_authority"

        if SupportEvidence.from_capsules(supporting_capsules).has_independent_verified_support(self.high_threshold):
            return True, "high_risk_supported_by_independent_capsules"
        return False, "high_risk_requires_independent_verified_support"


class PermissiveQuorumGate(EvidenceQuorumGate):
    def allowed(self, plan: Plan, supporting_capsules: list[MemoryCapsule]) -> tuple[bool, str]:
        return True, "quorum_disabled"


def majority_recommendation(capsules: list[MemoryCapsule]) -> str:
    votes: Counter[str] = Counter()
    for capsule in capsules:
        recommendation = extract_recommendation(capsule.content)
        if recommendation != "neutral_option":
            votes[recommendation] += max(capsule.influence_budget, 0.01)
    if not votes:
        return "neutral_option"
    return votes.most_common(1)[0][0]


@dataclass(frozen=True)
class SupportEvidence:
    support: float
    source_count: int
    writer_count: int
    fresh_verified_count: int

    @classmethod
    def from_capsules(
        cls,
        capsules: list[MemoryCapsule],
        recommendation: str | None = None,
    ) -> SupportEvidence:
        if recommendation is not None:
            capsules = [
                capsule
                for capsule in capsules
                if _capsule_matches_recommendation(capsule, recommendation)
            ]
        return cls(
            support=sum(capsule.influence_budget for capsule in capsules),
            source_count=len({capsule.source_type for capsule in capsules}),
            writer_count=len({capsule.writer for capsule in capsules if capsule.writer != "unknown"}),
            fresh_verified_count=sum(1 for capsule in capsules if _is_fresh_verified(capsule)),
        )

    def has_independent_verified_support(self, threshold: float) -> bool:
        return (
            self.support >= threshold
            and self.source_count >= 2
            and self.writer_count >= 2
            and self.fresh_verified_count >= 2
        )


def extract_recommendation(text: str) -> str:
    lowered = text.lower()
    aliases = load_security_policy_config().recommendation_aliases or {}
    matches = [
        canonical
        for canonical, tokens in aliases.items()
        if any(token in lowered for token in tokens)
    ]
    if len(set(matches)) > 1:
        return "ambiguous_recommendation"
    if matches:
        return matches[0]
    if "private" in lowered:
        return "private_info_path"
    return "neutral_option"


def _capsule_matches_recommendation(capsule: MemoryCapsule, recommendation: str) -> bool:
    return extract_recommendation(capsule.content) == recommendation


def _is_fresh_verified(capsule: MemoryCapsule) -> bool:
    return capsule.verification_count > 0 and not any(
        note.startswith("temporal_decay") or note == "stale_memory_influence_cap"
        for note in capsule.security_notes
    )


def _is_authoritative_medium_source(capsule: MemoryCapsule) -> bool:
    if capsule.source_type in {SourceType.USER_DECLARED, SourceType.VERIFIED_RECORD}:
        return capsule.kind in {CapsuleKind.PREFERENCE, CapsuleKind.FACT}
    if capsule.source_type == SourceType.TOOL_OUTPUT:
        return capsule.kind in {CapsuleKind.OBSERVATION, CapsuleKind.FACT, CapsuleKind.PREFERENCE}
    if capsule.source_type == SourceType.AGENT_DERIVED:
        return "verified_high_authority_lineage" in capsule.security_notes
    if capsule.source_type == SourceType.EXPERIENCE_LOG:
        return capsule.kind == CapsuleKind.EXPERIENCE and capsule.source_attested and capsule.writer != "unknown"
    return False

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from capsule_guard.models import ActionRisk, CapsuleKind, MemoryCapsule, SourceType, UserIntent


class TrustTier(str, Enum):
    VERIFIED = "verified"
    TRUSTED = "trusted"
    CONDITIONAL = "conditional"
    RESTRICTED = "restricted"
    UNTRUSTED = "untrusted"


MIN_AUTHORITY_BY_RISK = {
    ActionRisk.LOW: 0.0,
    ActionRisk.MEDIUM: 0.55,
    ActionRisk.HIGH: 0.85,
}

HIGH_RISK_DENY_SET = frozenset(
    {
        "purchase",
        "send_email",
        "delete",
        "transfer",
        "share_private_info",
        "modify_database",
    }
)


@dataclass(slots=True)
class AuthorizationResult:
    allowed: bool
    reason: str


def trust_tier(source_type: SourceType, verified: bool) -> TrustTier:
    if verified:
        return TrustTier.VERIFIED
    if source_type == SourceType.VERIFIED_RECORD:
        return TrustTier.TRUSTED
    if source_type == SourceType.USER_DECLARED:
        return TrustTier.CONDITIONAL
    if source_type == SourceType.EXPERIENCE_LOG:
        return TrustTier.CONDITIONAL
    if source_type in {SourceType.AGENT_DERIVED, SourceType.TOOL_OUTPUT}:
        return TrustTier.RESTRICTED
    if source_type in {SourceType.IMAGE_OCR, SourceType.DOCUMENT_OCR}:
        return TrustTier.UNTRUSTED
    return TrustTier.UNTRUSTED


def minimum_authority_for_risk(risk: ActionRisk) -> float:
    return MIN_AUTHORITY_BY_RISK[risk]


def source_denied_actions(source_type: SourceType) -> frozenset[str]:
    if source_type in {
        SourceType.WEB_CONTENT,
        SourceType.TOOL_OUTPUT,
        SourceType.AGENT_DERIVED,
        SourceType.IMAGE_OCR,
        SourceType.DOCUMENT_OCR,
    }:
        return HIGH_RISK_DENY_SET
    return frozenset()


def authorize_capsule_for_intent(
    capsule: MemoryCapsule,
    intent: UserIntent,
    topic_overlap: float,
    *,
    enforce_topic_scope: bool = True,
    enforce_denied_actions: bool = True,
    enforce_authority_floor: bool = True,
    topic_overlap_threshold: float = 0.12,
) -> AuthorizationResult:
    if enforce_denied_actions and intent.requested_action in capsule.denied_actions:
        return AuthorizationResult(False, "requested_action_denied_by_capsule")
    if not intent.topics or not capsule.allowed_topics:
        return AuthorizationResult(False, "missing_topic_scope")
    if enforce_topic_scope and topic_overlap < topic_overlap_threshold:
        return AuthorizationResult(False, "topic_scope_mismatch")
    if enforce_authority_floor:
        minimum = minimum_authority_for_risk(intent.action_risk)
        if capsule.source_authority < minimum:
            return AuthorizationResult(False, "source_authority_below_action_risk_floor")
    if capsule.kind == CapsuleKind.DIRECTIVE:
        return AuthorizationResult(False, "directive_capsule_cannot_authorize_intent")
    return AuthorizationResult(True, "authorized")

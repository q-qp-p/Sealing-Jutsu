from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class SourceType(str, Enum):
    USER_DECLARED = "user_declared"
    VERIFIED_RECORD = "verified_record"
    WEB_CONTENT = "web_content"
    TOOL_OUTPUT = "tool_output"
    AGENT_DERIVED = "agent_derived"
    EXPERIENCE_LOG = "experience_log"
    IMAGE_OCR = "image_ocr"
    DOCUMENT_OCR = "document_ocr"


class CapsuleKind(str, Enum):
    FACT = "fact"
    PREFERENCE = "preference"
    OBSERVATION = "observation"
    EXPERIENCE = "experience"
    DIRECTIVE = "directive"


class CapsuleStatus(str, Enum):
    ACTIVE = "active"
    SEALED = "sealed"
    REJECTED = "rejected"


class ActionRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(slots=True)
class MemorySeed:
    id: str
    content: str
    source_type: SourceType
    verified: bool = False
    source_attested: bool = True
    writer: str = "unknown"
    parent_ids: tuple[str, ...] = ()
    parent_authorities: tuple[float, ...] = ()
    observed_at: str | None = None


@dataclass(slots=True)
class MemoryCapsule:
    id: str
    content: str
    source_type: SourceType
    kind: CapsuleKind
    allowed_topics: frozenset[str]
    denied_actions: frozenset[str]
    source_authority: float
    influence_budget: float
    verification_count: int = 0
    status: CapsuleStatus = CapsuleStatus.ACTIVE
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_attested: bool = True
    writer: str = "unknown"
    parent_ids: tuple[str, ...] = ()
    parent_authorities: tuple[float, ...] = ()
    lineage_depth: int = 0
    security_notes: tuple[str, ...] = ()


@dataclass(slots=True)
class UserIntent:
    query: str
    topics: frozenset[str]
    requested_action: str
    action_risk: ActionRisk


@dataclass(slots=True)
class RetrievalHit:
    capsule: MemoryCapsule
    similarity: float
    authority_weighted_score: float


@dataclass(slots=True)
class Plan:
    recommendation: str
    action: str
    action_risk: ActionRisk
    used_capsule_ids: tuple[str, ...]
    rationale: str


@dataclass(slots=True)
class PolicyTrace:
    capsule_id: str
    eligible: bool
    reasons: tuple[str, ...]
    topic_overlap: float
    source_authority: float
    requested_action: str
    action_risk: str


@dataclass(slots=True)
class CapsuleDecision:
    allowed: bool
    reason: str
    plan: Plan
    retrieved_capsule_ids: tuple[str, ...] = ()
    eligible_capsule_ids: tuple[str, ...] = ()
    sealed_capsule_ids: tuple[str, ...] = ()
    policy_trace: tuple[PolicyTrace, ...] = ()

from __future__ import annotations

from capsule_guard.models import ActionRisk, SourceType


DIRECTIVE_PHRASES = (
    "always",
    "never",
    "ignore",
    "override",
    "must",
    "force",
    "secretly",
    "do not tell",
    "without asking",
)

HIGH_RISK_ACTIONS = {
    "send_email",
    "purchase",
    "delete",
    "transfer",
    "share_private_info",
    "modify_database",
}

MEDIUM_RISK_ACTIONS = {
    "recommend_vendor",
    "open_link",
    "call_tool",
}

SOURCE_AUTHORITY = {
    SourceType.VERIFIED_RECORD: 0.95,
    SourceType.USER_DECLARED: 0.75,
    SourceType.EXPERIENCE_LOG: 0.60,
    SourceType.AGENT_DERIVED: 0.40,
    SourceType.TOOL_OUTPUT: 0.35,
    SourceType.WEB_CONTENT: 0.25,
    SourceType.DOCUMENT_OCR: 0.25,
    SourceType.IMAGE_OCR: 0.20,
}


def contains_directive(text: str) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in DIRECTIVE_PHRASES)


def extract_action(text: str) -> str:
    lowered = text.lower()
    if "send email" in lowered or "email" in lowered and "private" in lowered:
        return "send_email"
    if "purchase" in lowered or "buy now" in lowered or "buy immediately" in lowered:
        return "purchase"
    if "delete" in lowered or "remove record" in lowered:
        return "delete"
    if "modify database" in lowered or "update database" in lowered or "database record" in lowered:
        return "modify_database"
    if "transfer" in lowered:
        return "transfer"
    if "private" in lowered and ("share" in lowered or "send" in lowered):
        return "share_private_info"
    if "open link" in lowered:
        return "open_link"
    if "call tool" in lowered:
        return "call_tool"
    if "recommend" in lowered or "choose" in lowered or "select" in lowered:
        return "recommend_vendor"
    return "answer"


def action_risk(action: str) -> ActionRisk:
    if action in HIGH_RISK_ACTIONS:
        return ActionRisk.HIGH
    if action in MEDIUM_RISK_ACTIONS:
        return ActionRisk.MEDIUM
    return ActionRisk.LOW


def source_authority(source_type: SourceType, verified: bool = False) -> float:
    if verified:
        return max(SOURCE_AUTHORITY[source_type], 0.85)
    return SOURCE_AUTHORITY[source_type]

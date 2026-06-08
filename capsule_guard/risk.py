from __future__ import annotations

import re

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
    "send_message",
    "purchase",
    "delete",
    "transfer",
    "share_private_info",
    "modify_database",
    "grant_access",
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
    if (
        "transfer" in lowered
        or "wire " in lowered
        or "iban" in lowered
        or "send a transaction" in lowered
        or "send transaction" in lowered
        or "transaction to" in lowered
        or "payment to" in lowered
    ):
        return "transfer"
    if (
        ("grant" in lowered and "access" in lowered)
        or ("permanent access" in lowered)
        or ("unlock" in lowered)
        or ("permission" in lowered and ("add" in lowered or "grant" in lowered))
        or "sharing settings" in lowered
        or "share settings" in lowered
        or "can_edit" in lowered
        or "can edit" in lowered
        or "invite user" in lowered
        or (("add" in lowered or "invite" in lowered) and ("workspace" in lowered or "channel" in lowered))
        or (("change" in lowered or "reset" in lowered) and "password" in lowered)
    ):
        return "grant_access"
    if (
        "modify database" in lowered
        or "update database" in lowered
        or "database record" in lowered
        or "update record" in lowered
        or "health record" in lowered
        or "health records" in lowered
    ):
        return "modify_database"
    if (
        "send email" in lowered
        or "send an email" in lowered
        or "send the email" in lowered
        or "email them" in lowered
        or "email those" in lowered
        or "email it" in lowered
        or " by email" in lowered
        or " via email" in lowered
        or " through email" in lowered
        or "forward" in lowered
        or re.search(r"\b(send|sending|forward|forwarding)\b.{0,120}\b(email|e-mail|@)\b", lowered)
        or re.search(r"\bemail\s+(them|those|it|the\s+)?(details|summary|report|messages?|files?)\b", lowered)
        or re.search(r"\bemail\b.{0,80}\b(account|details|summary|report|messages?|files?)\b.{0,80}\bto\b", lowered)
    ):
        return "send_email"
    if (
        ("send" in lowered or "post" in lowered)
        and ("message" in lowered or "slack" in lowered or "channel" in lowered)
    ):
        return "send_message"
    if "purchase" in lowered or "buy now" in lowered or "buy immediately" in lowered:
        return "purchase"
    if "book" in lowered and ("flight" in lowered or "hotel" in lowered or "trip" in lowered or "reservation" in lowered):
        return "purchase"
    if "make a reservation" in lowered or "make reservation" in lowered:
        return "purchase"
    if "delete" in lowered or "remove record" in lowered:
        return "delete"
    if (
        ("private" in lowered or "confidential" in lowered or "credential" in lowered or "password" in lowered)
        and ("share" in lowered or "send" in lowered or "show" in lowered or "reveal" in lowered)
    ):
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

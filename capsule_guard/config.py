from __future__ import annotations

from dataclasses import dataclass
import os


DEFAULT_APPROVED_RECOMMENDATIONS = frozenset({"trustedvendor", "safevendor", "neutral_option"})
DEFAULT_RECOMMENDATION_ALIASES = {
    "trustedvendor": frozenset({"trustedvendor", "trusted vendor"}),
    "safevendor": frozenset({"safevendor", "safe vendor"}),
    "vendorx": frozenset({"vendorx", "vendor x", "vx-prime", "preferred_partner", "certified_supplier"}),
    "vendory": frozenset({"vendory", "vendor y"}),
    "cheapvendor": frozenset({"cheapvendor", "cheap vendor"}),
}


@dataclass(frozen=True)
class SecurityPolicyConfig:
    approved_recommendations: frozenset[str] = DEFAULT_APPROVED_RECOMMENDATIONS
    recommendation_aliases: dict[str, frozenset[str]] | None = None
    medium_threshold: float = 0.70
    high_threshold: float = 1.60
    stale_memory_days: int = 180
    very_stale_memory_days: int = 365


def load_security_policy_config() -> SecurityPolicyConfig:
    configured_recommendations = _csv_env("CAPSULE_GUARD_APPROVED_RECOMMENDATIONS")
    return SecurityPolicyConfig(
        approved_recommendations=configured_recommendations or DEFAULT_APPROVED_RECOMMENDATIONS,
        recommendation_aliases=_aliases_env("CAPSULE_GUARD_RECOMMENDATION_ALIASES") or DEFAULT_RECOMMENDATION_ALIASES,
        medium_threshold=_float_env("CAPSULE_GUARD_MEDIUM_THRESHOLD", 0.70),
        high_threshold=_float_env("CAPSULE_GUARD_HIGH_THRESHOLD", 1.60),
        stale_memory_days=_int_env("CAPSULE_GUARD_STALE_MEMORY_DAYS", 180),
        very_stale_memory_days=_int_env("CAPSULE_GUARD_VERY_STALE_MEMORY_DAYS", 365),
    )


def _csv_env(name: str) -> frozenset[str] | None:
    value = os.environ.get(name, "").strip()
    if not value:
        return None
    items = {item.strip().lower() for item in value.split(",") if item.strip()}
    return frozenset(items) if items else None


def _aliases_env(name: str) -> dict[str, frozenset[str]] | None:
    value = os.environ.get(name, "").strip()
    if not value:
        return None
    aliases: dict[str, set[str]] = {}
    for group in value.split(";"):
        if not group.strip() or "=" not in group:
            continue
        canonical, raw_aliases = group.split("=", 1)
        canonical = canonical.strip().lower()
        items = {item.strip().lower() for item in raw_aliases.split("|") if item.strip()}
        if canonical and items:
            aliases[canonical] = items
    return {key: frozenset(items) for key, items in aliases.items()} or None


def _float_env(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default

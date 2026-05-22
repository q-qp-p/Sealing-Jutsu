"""Intent-Bound Memory Capsules research prototype."""

from capsule_guard.agents import (
    AmbientMemoryAgent,
    CapsuleAgent,
    KeywordFilterAgent,
    NoDeniedActionsCapsuleAgent,
    NoQuorumCapsuleAgent,
    NoTopicScopeCapsuleAgent,
    ProvenanceOnlyAgent,
)
from capsule_guard.compiler import CapsuleCompiler
from capsule_guard.models import MemoryCapsule
from capsule_guard.store import CapsuleStore

__all__ = [
    "AmbientMemoryAgent",
    "CapsuleAgent",
    "KeywordFilterAgent",
    "NoDeniedActionsCapsuleAgent",
    "NoQuorumCapsuleAgent",
    "NoTopicScopeCapsuleAgent",
    "ProvenanceOnlyAgent",
    "CapsuleCompiler",
    "MemoryCapsule",
    "CapsuleStore",
]

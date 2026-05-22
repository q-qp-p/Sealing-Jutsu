from __future__ import annotations

from typing import Callable

from capsule_guard.agents import CapsuleAgent
from capsule_guard.models import CapsuleDecision, MemorySeed


class MultiSessionHarness:
    def __init__(self, agent_factory: Callable[[], CapsuleAgent]) -> None:
        self.agent = agent_factory()
        self.session_count = 0

    def ingest_session(self, memories: list[MemorySeed] | tuple[MemorySeed, ...]) -> None:
        self.session_count += 1
        for memory in memories:
            self.agent.remember(memory)

    def answer_later(self, query: str) -> CapsuleDecision:
        self.session_count += 1
        return self.agent.answer(query)

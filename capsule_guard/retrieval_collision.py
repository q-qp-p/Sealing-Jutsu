from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from capsule_guard.compiler import CapsuleCompiler
from capsule_guard.intent import IntentParser
from capsule_guard.models import MemorySeed, SourceType
from capsule_guard.store import CapsuleStore
from capsule_guard.text import canonical_terms


@dataclass(frozen=True)
class RetrievalCollisionProbeResult:
    query: str
    poisoned_memory_id: str
    retrieved_ids: tuple[str, ...]
    rank: int
    poison_similarity: float
    highest_benign_similarity: float
    retrieval_mode: str


class RetrievalCollisionProbe:
    def __init__(
        self,
        *,
        retrieval_mode: str = "sqlite_vector",
        vector_db_path: str | Path | None = None,
    ) -> None:
        self.retrieval_mode = retrieval_mode
        self.vector_db_path = vector_db_path
        self.compiler = CapsuleCompiler()
        self.intent_parser = IntentParser()

    def craft_seed(
        self,
        *,
        query: str,
        seed_id: str,
        target_alias: str = "certified_supplier",
        source_type: SourceType = SourceType.WEB_CONTENT,
        writer: str = "retrieval_collision_probe",
    ) -> MemorySeed:
        intent = self.intent_parser.parse(query)
        collision_terms = tuple(sorted(canonical_terms(intent.topics)))
        topical_anchor = " ".join(collision_terms) or "general workflow"
        content = f"{topical_anchor} {target_alias}."
        return MemorySeed(
            id=seed_id,
            content=content,
            source_type=source_type,
            writer=writer,
        )

    def evaluate(
        self,
        *,
        query: str,
        poison: MemorySeed,
        benign_memories: tuple[MemorySeed, ...] = (),
        k: int = 5,
    ) -> RetrievalCollisionProbeResult:
        intent = self.intent_parser.parse(query)
        store = CapsuleStore(retrieval_mode=self.retrieval_mode, vector_db_path=self.vector_db_path)
        for seed in (*benign_memories, poison):
            store.add(self.compiler.compile(seed))

        all_hits = store.retrieve(intent, k=max(k, len(benign_memories) + 1))
        retrieved_ids = tuple(hit.capsule.id for hit in all_hits[:k])
        rank = 0
        poison_similarity = 0.0
        benign_similarities: list[float] = []
        for index, hit in enumerate(all_hits, start=1):
            if hit.capsule.id == poison.id:
                rank = index
                poison_similarity = hit.similarity
            else:
                benign_similarities.append(hit.similarity)

        return RetrievalCollisionProbeResult(
            query=query,
            poisoned_memory_id=poison.id,
            retrieved_ids=retrieved_ids,
            rank=rank,
            poison_similarity=poison_similarity,
            highest_benign_similarity=max(benign_similarities, default=0.0),
            retrieval_mode=self.retrieval_mode,
        )

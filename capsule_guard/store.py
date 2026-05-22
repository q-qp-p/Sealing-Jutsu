from __future__ import annotations

from pathlib import Path

from capsule_guard.models import CapsuleStatus, MemoryCapsule, RetrievalHit, UserIntent
from capsule_guard.text import canonical_terms, jaccard, topic_terms
from typing import Any

from capsule_guard.vector_backend import SQLiteCapsuleVectorIndex


class CapsuleStore:
    def __init__(
        self,
        retrieval_mode: str = "lexical",
        vector_db_path: str | Path | None = None,
        external_vector_backend: Any | None = None,
    ) -> None:
        self._capsules: dict[str, MemoryCapsule] = {}
        self.retrieval_mode = retrieval_mode
        self._vector_index: SQLiteCapsuleVectorIndex | None = None
        self._external_vector_backend = external_vector_backend
        if retrieval_mode == "sqlite_vector":
            path = vector_db_path or Path("results") / "capsule_vectors.sqlite3"
            self._vector_index = SQLiteCapsuleVectorIndex(path)
            self._capsules = {capsule.id: capsule for capsule in self._vector_index.load_capsules()}
        if retrieval_mode == "external_vector":
            if external_vector_backend is None:
                raise ValueError("external_vector retrieval requires external_vector_backend")
            self._capsules = {capsule.id: capsule for capsule in external_vector_backend.load_capsules()}

    def add(self, capsule: MemoryCapsule) -> None:
        self._capsules[capsule.id] = capsule
        if self._vector_index is not None:
            self._vector_index.upsert(capsule)
        if self._external_vector_backend is not None:
            self._external_vector_backend.upsert(capsule)

    def all(self) -> list[MemoryCapsule]:
        return list(self._capsules.values())

    def active(self) -> list[MemoryCapsule]:
        return [capsule for capsule in self._capsules.values() if capsule.status == CapsuleStatus.ACTIVE]

    def retrieve(self, intent: UserIntent, k: int = 4, include_sealed: bool = False) -> list[RetrievalHit]:
        capsules = self.all() if include_sealed else self.active()
        hits: list[RetrievalHit] = []
        for capsule in capsules:
            similarity = self._similarity(intent, capsule)
            weighted = similarity + (0.30 * capsule.source_authority) + (0.30 * capsule.influence_budget)
            hits.append(RetrievalHit(capsule=capsule, similarity=similarity, authority_weighted_score=weighted))
        return sorted(hits, key=lambda hit: hit.authority_weighted_score, reverse=True)[:k]

    def _similarity(self, intent: UserIntent, capsule: MemoryCapsule) -> float:
        capsule_terms = capsule.allowed_topics or topic_terms(capsule.content)
        if self.retrieval_mode == "external_vector" and self._external_vector_backend is not None:
            return float(self._external_vector_backend.similarity_for_terms(intent.topics, capsule))
        if self.retrieval_mode == "sqlite_vector" and self._vector_index is not None:
            return self._vector_index.similarity_for_terms(intent.topics, capsule)
        if self.retrieval_mode == "hashed_vector":
            return jaccard(canonical_terms(intent.topics), canonical_terms(capsule_terms))
        if self.retrieval_mode == "tfidf":
            return jaccard(intent.topics, capsule_terms) * 1.15
        return jaccard(intent.topics, capsule_terms)

from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from capsule_guard.models import CapsuleKind, CapsuleStatus, MemoryCapsule, SourceType
from capsule_guard.text import topic_terms


SYNONYM_CANONICALS = {
    "notebook": "laptop",
    "procurement": "buying",
    "buy": "buying",
    "purchasing": "buying",
    "cellphone": "phone",
    "mobile": "phone",
    "handset": "phone",
    "repairing": "repair",
    "sourcing": "buying",
}


class HashingEmbedder:
    def __init__(self, dimensions: int = 96) -> None:
        self.dimensions = dimensions

    def embed_terms(self, terms: set[str] | frozenset[str]) -> tuple[float, ...]:
        vector = [0.0 for _ in range(self.dimensions)]
        for term in terms:
            canonical = SYNONYM_CANONICALS.get(term, term)
            bucket = _stable_bucket(canonical, self.dimensions)
            vector[bucket] += 1.0
        return _normalize(vector)

    def embed_text(self, text: str) -> tuple[float, ...]:
        return self.embed_terms(topic_terms(text))

    def similarity(self, left: tuple[float, ...], right: tuple[float, ...]) -> float:
        return sum(a * b for a, b in zip(left, right))


class SQLiteCapsuleVectorIndex:
    def __init__(self, path: str | Path, *, embedder: HashingEmbedder | None = None) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.embedder = embedder or HashingEmbedder()
        self._ensure_schema()

    def upsert(self, capsule: MemoryCapsule) -> None:
        vector = self.embedder.embed_terms(capsule.allowed_topics)
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO capsules(id, capsule_json, vector_json)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    capsule_json = excluded.capsule_json,
                    vector_json = excluded.vector_json
                """,
                (
                    capsule.id,
                    json.dumps(_capsule_to_dict(capsule), sort_keys=True),
                    json.dumps(vector),
                ),
            )

    def load_capsules(self) -> list[MemoryCapsule]:
        with self._connection() as connection:
            rows = connection.execute("SELECT capsule_json FROM capsules ORDER BY id").fetchall()
        return [_capsule_from_dict(json.loads(str(row[0]))) for row in rows]

    def similarity_for_terms(self, query_terms: set[str] | frozenset[str], capsule: MemoryCapsule) -> float:
        query_vector = self.embedder.embed_terms(query_terms)
        capsule_vector = self.embedder.embed_terms(capsule.allowed_topics)
        return self.embedder.similarity(query_vector, capsule_vector)

    def _ensure_schema(self) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS capsules (
                    id TEXT PRIMARY KEY,
                    capsule_json TEXT NOT NULL,
                    vector_json TEXT NOT NULL
                )
                """
            )

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path)
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()


def _stable_bucket(term: str, dimensions: int) -> int:
    digest = hashlib.sha256(term.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % dimensions


def _normalize(values: list[float]) -> tuple[float, ...]:
    norm = math.sqrt(sum(value * value for value in values))
    if norm == 0:
        return tuple(values)
    return tuple(value / norm for value in values)


def _capsule_to_dict(capsule: MemoryCapsule) -> dict[str, object]:
    return {
        "id": capsule.id,
        "content": capsule.content,
        "source_type": capsule.source_type.value,
        "kind": capsule.kind.value,
        "allowed_topics": sorted(capsule.allowed_topics),
        "denied_actions": sorted(capsule.denied_actions),
        "source_authority": capsule.source_authority,
        "influence_budget": capsule.influence_budget,
        "verification_count": capsule.verification_count,
        "status": capsule.status.value,
        "created_at": capsule.created_at,
        "source_attested": capsule.source_attested,
        "writer": capsule.writer,
        "parent_ids": list(capsule.parent_ids),
        "lineage_depth": capsule.lineage_depth,
        "security_notes": list(capsule.security_notes),
    }


def _capsule_from_dict(data: dict[str, object]) -> MemoryCapsule:
    return MemoryCapsule(
        id=str(data["id"]),
        content=str(data["content"]),
        source_type=SourceType(str(data["source_type"])),
        kind=CapsuleKind(str(data["kind"])),
        allowed_topics=frozenset(str(item) for item in data.get("allowed_topics", [])),
        denied_actions=frozenset(str(item) for item in data.get("denied_actions", [])),
        source_authority=float(data["source_authority"]),
        influence_budget=float(data["influence_budget"]),
        verification_count=int(data.get("verification_count", 0)),
        status=CapsuleStatus(str(data["status"])),
        created_at=str(data["created_at"]),
        source_attested=bool(data.get("source_attested", True)),
        writer=str(data.get("writer", "unknown")),
        parent_ids=tuple(str(item) for item in data.get("parent_ids", [])),
        lineage_depth=int(data.get("lineage_depth", 0)),
        security_notes=tuple(str(item) for item in data.get("security_notes", [])),
    )

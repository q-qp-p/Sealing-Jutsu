from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from capsule_guard.models import MemorySeed, SourceType
from capsule_guard.scenarios import Scenario


DEFAULT_WORKFLOW_CORPUS_PATH = Path(__file__).resolve().parent.parent / "data" / "workflow_corpus.jsonl"

EVENT_SOURCE_TYPES = {
    "user_preference": SourceType.USER_DECLARED,
    "verified_record": SourceType.VERIFIED_RECORD,
    "web_page": SourceType.WEB_CONTENT,
    "tool_output": SourceType.TOOL_OUTPUT,
    "agent_summary": SourceType.AGENT_DERIVED,
    "experience_log": SourceType.EXPERIENCE_LOG,
    "image_ocr": SourceType.IMAGE_OCR,
    "document_ocr": SourceType.DOCUMENT_OCR,
}


class WorkflowCorpusError(ValueError):
    pass


def load_workflow_corpus_scenarios(path: str | Path | None = None) -> list[Scenario]:
    corpus_path = Path(path) if path is not None else DEFAULT_WORKFLOW_CORPUS_PATH
    if not corpus_path.exists():
        raise WorkflowCorpusError(f"Workflow corpus not found: {corpus_path}")

    scenarios: list[Scenario] = []
    with corpus_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise WorkflowCorpusError(f"{corpus_path}:{line_number}: invalid JSONL record") from exc
            scenarios.append(_record_to_scenario(record, corpus_path, line_number))

    if not scenarios:
        raise WorkflowCorpusError(f"Workflow corpus is empty: {corpus_path}")
    return scenarios


def _record_to_scenario(record: dict[str, Any], path: Path, line_number: int) -> Scenario:
    workflow_id = _required_string(record, "id", path, line_number)
    query = _required_string(record, "query", path, line_number)
    expected = _required_string(record, "expected_recommendation", path, line_number)
    events = record.get("events")
    if not isinstance(events, list) or not events:
        raise WorkflowCorpusError(f"{path}:{line_number}: events must be a non-empty list")

    memories: list[MemorySeed] = []
    poisoned_memory_ids: list[str] = []
    for event_index, event in enumerate(events):
        if not isinstance(event, dict):
            raise WorkflowCorpusError(f"{path}:{line_number}: event {event_index} must be an object")
        if event.get("store_as_memory", True) is False:
            continue
        memory = _event_to_memory(event, path, line_number, event_index)
        memories.append(memory)
        if bool(event.get("poison", False)):
            poisoned_memory_ids.append(memory.id)

    poisoned = bool(record.get("poisoned", bool(poisoned_memory_ids)))
    if poisoned and not poisoned_memory_ids:
        raise WorkflowCorpusError(f"{path}:{line_number}: poisoned workflow must mark at least one event poison=true")

    attack_type = str(record.get("attack_type") or ("workflow_trace_poison" if poisoned else "workflow_trace_benign"))
    return Scenario(
        id=workflow_id,
        query=query,
        memories=tuple(memories),
        poisoned=poisoned,
        expected_recommendation=expected,
        poisoned_memory_ids=tuple(poisoned_memory_ids),
        bad_recommendation=str(record.get("bad_recommendation") or "vendorx"),
        attack_type=attack_type,
    )


def _event_to_memory(event: dict[str, Any], path: Path, line_number: int, event_index: int) -> MemorySeed:
    event_type = str(event.get("event_type") or "")
    source_type = _source_type(event, event_type, path, line_number, event_index)
    event_id = str(event.get("memory_id") or event.get("event_id") or f"event-{event_index}")
    content = _required_string(event, "content", path, line_number, prefix=f"event {event_index} ")
    return MemorySeed(
        id=event_id,
        content=content,
        source_type=source_type,
        verified=bool(event.get("verified", False)),
        source_attested=bool(event.get("source_attested", True)),
        writer=str(event.get("writer") or "unknown"),
        parent_ids=tuple(str(item) for item in event.get("parent_ids", ())),
        parent_authorities=tuple(float(item) for item in event.get("parent_authorities", ())),
        observed_at=str(event["observed_at"]) if event.get("observed_at") else None,
    )


def _source_type(
    event: dict[str, Any],
    event_type: str,
    path: Path,
    line_number: int,
    event_index: int,
) -> SourceType:
    explicit = event.get("source_type")
    if explicit:
        try:
            return SourceType(str(explicit))
        except ValueError as exc:
            raise WorkflowCorpusError(
                f"{path}:{line_number}: event {event_index} has unsupported source_type {explicit!r}"
            ) from exc
    if event_type in EVENT_SOURCE_TYPES:
        return EVENT_SOURCE_TYPES[event_type]
    raise WorkflowCorpusError(f"{path}:{line_number}: event {event_index} has unsupported event_type {event_type!r}")


def _required_string(
    record: dict[str, Any],
    key: str,
    path: Path,
    line_number: int,
    *,
    prefix: str = "",
) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise WorkflowCorpusError(f"{path}:{line_number}: {prefix}{key} is required")
    return value

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from capsule_guard.models import MemorySeed, SourceType
from capsule_guard.scenarios import Scenario


DEFAULT_WORKFLOW_CORPUS_PATH = Path(__file__).resolve().parent.parent / "data" / "workflow_corpus.jsonl"
DEFAULT_AGENT_TRACE_CORPUS_PATH = Path(__file__).resolve().parent.parent / "data" / "agent_trace_corpus_sample.jsonl"

EVENT_SOURCE_TYPES = {
    "user_preference": SourceType.USER_DECLARED,
    "verified_record": SourceType.VERIFIED_RECORD,
    "web_page": SourceType.WEB_CONTENT,
    "tool_output": SourceType.TOOL_OUTPUT,
    "agent_summary": SourceType.AGENT_DERIVED,
    "experience_log": SourceType.EXPERIENCE_LOG,
    "image_ocr": SourceType.IMAGE_OCR,
    "document_ocr": SourceType.DOCUMENT_OCR,
    "browser": SourceType.WEB_CONTENT,
    "tool_call": SourceType.TOOL_OUTPUT,
    "assistant_summary": SourceType.AGENT_DERIVED,
    "summary": SourceType.AGENT_DERIVED,
}


class WorkflowCorpusError(ValueError):
    pass


@dataclass(slots=True)
class TraceCorpusValidationReport:
    total_records: int = 0
    poisoned_records: int = 0
    benign_records: int = 0
    memory_events: int = 0
    poison_memory_events: int = 0
    source_type_counts: dict[str, int] = field(default_factory=dict)
    redaction_counts: dict[str, int] = field(default_factory=dict)
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "total_records": self.total_records,
            "poisoned_records": self.poisoned_records,
            "benign_records": self.benign_records,
            "memory_events": self.memory_events,
            "poison_memory_events": self.poison_memory_events,
            "source_type_counts": dict(self.source_type_counts),
            "redaction_counts": dict(self.redaction_counts),
            "errors": list(self.errors),
            "warnings": list(self.warnings),
        }


REDACTION_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "[REDACTED_EMAIL]"),
    ("url", re.compile(r"https?://[^\s\"'<>]+"), "[REDACTED_URL]"),
    ("secret", re.compile(r"\b(?:sk|ghp)[-_][A-Za-z0-9._=-]+\b"), "[REDACTED_SECRET]"),
    ("phone", re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)"), "[REDACTED_PHONE]"),
)


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


def load_agent_trace_scenarios(path: str | Path | None = None) -> list[Scenario]:
    corpus_path = Path(path) if path is not None else DEFAULT_AGENT_TRACE_CORPUS_PATH
    if not corpus_path.exists():
        raise WorkflowCorpusError(f"Agent trace corpus not found: {corpus_path}")

    scenarios: list[Scenario] = []
    with corpus_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise WorkflowCorpusError(f"{corpus_path}:{line_number}: invalid JSONL trace record") from exc
            scenarios.append(_trace_record_to_scenario(record, corpus_path, line_number))

    if not scenarios:
        raise WorkflowCorpusError(f"Agent trace corpus is empty: {corpus_path}")
    return scenarios


def validate_agent_trace_corpus(path: str | Path, *, require_redaction: bool = False) -> TraceCorpusValidationReport:
    corpus_path = Path(path)
    errors: list[str] = []
    warnings: list[str] = []
    source_type_counts: dict[str, int] = {}
    redaction_counts = {name: 0 for name, _, _ in REDACTION_PATTERNS}
    total_records = 0
    poisoned_records = 0
    benign_records = 0
    memory_events = 0
    poison_memory_events = 0

    if not corpus_path.exists():
        return TraceCorpusValidationReport(errors=(f"Agent trace corpus not found: {corpus_path}",))

    with corpus_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            total_records += 1
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError:
                errors.append(f"{corpus_path}:{line_number}: invalid JSONL trace record")
                continue
            if not isinstance(record, dict):
                errors.append(f"{corpus_path}:{line_number}: trace record must be an object")
                continue

            _, counts = redact_agent_trace_record(record)
            for name, count in counts.items():
                redaction_counts[name] = redaction_counts.get(name, 0) + count

            try:
                scenario = _trace_record_to_scenario(record, corpus_path, line_number)
            except WorkflowCorpusError as exc:
                errors.append(str(exc))
                continue

            if scenario.poisoned:
                poisoned_records += 1
            else:
                benign_records += 1
            memory_events += len(scenario.memories)
            poison_memory_events += len(scenario.poisoned_memory_ids)
            for memory in scenario.memories:
                key = memory.source_type.value
                source_type_counts[key] = source_type_counts.get(key, 0) + 1

    if total_records == 0:
        errors.append(f"Agent trace corpus is empty: {corpus_path}")
    if require_redaction and not any(redaction_counts.values()):
        warnings.append("No private identifiers matched the redaction patterns")

    return TraceCorpusValidationReport(
        total_records=total_records,
        poisoned_records=poisoned_records,
        benign_records=benign_records,
        memory_events=memory_events,
        poison_memory_events=poison_memory_events,
        source_type_counts=source_type_counts,
        redaction_counts=redaction_counts,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def redact_agent_trace_record(record: dict[str, Any]) -> tuple[dict[str, Any], dict[str, int]]:
    counts = {name: 0 for name, _, _ in REDACTION_PATTERNS}

    def redact_value(value: Any) -> Any:
        if isinstance(value, str):
            redacted = value
            for name, pattern, replacement in REDACTION_PATTERNS:
                redacted, count = pattern.subn(replacement, redacted)
                counts[name] += count
            return redacted
        if isinstance(value, list):
            return [redact_value(item) for item in value]
        if isinstance(value, dict):
            return {str(key): redact_value(item) for key, item in value.items()}
        return value

    redacted_record = redact_value(record)
    return redacted_record, counts


def write_redacted_agent_trace_corpus(input_path: str | Path, output_path: str | Path) -> TraceCorpusValidationReport:
    source = Path(input_path)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    redaction_counts = {name: 0 for name, _, _ in REDACTION_PATTERNS}

    with source.open("r", encoding="utf-8") as in_handle, target.open("w", encoding="utf-8") as out_handle:
        for line in in_handle:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                out_handle.write(line)
                continue
            record = json.loads(stripped)
            if not isinstance(record, dict):
                out_handle.write(json.dumps(record, sort_keys=True) + "\n")
                continue
            redacted, counts = redact_agent_trace_record(record)
            for name, count in counts.items():
                redaction_counts[name] = redaction_counts.get(name, 0) + count
            out_handle.write(json.dumps(redacted, sort_keys=True) + "\n")

    report = validate_agent_trace_corpus(target)
    report.redaction_counts.update(redaction_counts)
    return report


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


def _trace_record_to_scenario(record: dict[str, Any], path: Path, line_number: int) -> Scenario:
    if not isinstance(record, dict):
        raise WorkflowCorpusError(f"{path}:{line_number}: trace record must be an object")
    task = record.get("task") if isinstance(record.get("task"), dict) else {}
    labels = record.get("labels") if isinstance(record.get("labels"), dict) else {}
    trace_id = _first_string(record, ("trace_id", "session_id", "id"))
    if not trace_id:
        raise WorkflowCorpusError(f"{path}:{line_number}: trace_id, session_id, or id is required")
    query = _first_string(task, ("query", "user_goal", "instruction")) or _first_string(
        record,
        ("query", "user_goal", "instruction"),
    )
    if not query:
        raise WorkflowCorpusError(f"{path}:{line_number}: query is required")
    expected = _first_string(task, ("expected_recommendation", "expected")) or _first_string(
        record,
        ("expected_recommendation", "expected"),
    )
    if not expected:
        raise WorkflowCorpusError(f"{path}:{line_number}: expected_recommendation is required")
    bad = (
        _first_string(task, ("bad_recommendation", "attacker_target"))
        or _first_string(labels, ("bad_recommendation", "attacker_target"))
        or _first_string(record, ("bad_recommendation", "attacker_target"))
        or "vendorx"
    )
    events = record.get("events") or record.get("messages") or record.get("steps")
    if not isinstance(events, list) or not events:
        raise WorkflowCorpusError(f"{path}:{line_number}: events, messages, or steps must be a non-empty list")

    memories: list[MemorySeed] = []
    poisoned_memory_ids: list[str] = []
    for event_index, event in enumerate(events):
        if not isinstance(event, dict):
            raise WorkflowCorpusError(f"{path}:{line_number}: trace event {event_index} must be an object")
        if event.get("store_as_memory", event.get("memory", True)) is False:
            continue
        memory = _trace_event_to_memory(event, path, line_number, event_index)
        memories.append(memory)
        if bool(event.get("poison", event.get("is_poison", False))):
            poisoned_memory_ids.append(memory.id)

    poisoned = bool(labels.get("poisoned", record.get("poisoned", bool(poisoned_memory_ids))))
    if poisoned and not poisoned_memory_ids:
        raise WorkflowCorpusError(f"{path}:{line_number}: poisoned trace must mark at least one event poison=true")

    return Scenario(
        id=trace_id,
        query=query,
        memories=tuple(memories),
        poisoned=poisoned,
        expected_recommendation=expected,
        poisoned_memory_ids=tuple(poisoned_memory_ids),
        bad_recommendation=bad,
        attack_type=str(labels.get("attack_type") or record.get("attack_type") or ("real_trace_poison" if poisoned else "real_trace_benign")),
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


def _trace_event_to_memory(event: dict[str, Any], path: Path, line_number: int, event_index: int) -> MemorySeed:
    event_type = str(event.get("event_type") or event.get("kind") or event.get("type") or event.get("role") or "")
    source_type = _source_type(event, event_type, path, line_number, event_index)
    event_id = str(event.get("memory_id") or event.get("event_id") or event.get("id") or f"trace-event-{event_index}")
    content = _event_content(event)
    if not content:
        raise WorkflowCorpusError(f"{path}:{line_number}: trace event {event_index} content/text/payload.text is required")
    return MemorySeed(
        id=event_id,
        content=content,
        source_type=source_type,
        verified=bool(event.get("verified", False)),
        source_attested=bool(event.get("source_attested", True)),
        writer=str(event.get("writer") or event.get("role") or "unknown"),
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


def _first_string(record: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _event_content(event: dict[str, Any]) -> str:
    value = _first_string(event, ("content", "text", "message"))
    if value:
        return value
    payload = event.get("payload")
    if isinstance(payload, dict):
        return _first_string(payload, ("content", "text", "message"))
    if isinstance(payload, str) and payload.strip():
        return payload.strip()
    return ""

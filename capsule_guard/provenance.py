from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ProvenanceEvent:
    index: int
    memory_id: str
    event_type: str
    payload: dict[str, Any]
    previous_hash: str
    payload_hash: str
    signature: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "memory_id": self.memory_id,
            "event_type": self.event_type,
            "payload": self.payload,
            "previous_hash": self.previous_hash,
            "payload_hash": self.payload_hash,
            "signature": self.signature,
        }


class ProvenanceLedger:
    def __init__(self, secret: bytes = b"capsuleguard-local-ledger") -> None:
        self.secret = secret
        self.events: list[ProvenanceEvent] = []

    def append_event(self, memory_id: str, event_type: str, payload: dict[str, Any]) -> ProvenanceEvent:
        if self.events and not self.verify():
            raise ValueError("Cannot append to an invalid provenance chain")
        previous_hash = self.events[-1].signature if self.events else "GENESIS"
        payload_hash = _payload_hash(payload)
        signature = self._sign(len(self.events), memory_id, event_type, payload_hash, previous_hash)
        event = ProvenanceEvent(
            index=len(self.events),
            memory_id=memory_id,
            event_type=event_type,
            payload=dict(payload),
            previous_hash=previous_hash,
            payload_hash=payload_hash,
            signature=signature,
        )
        self.events.append(event)
        return event

    def verify(self) -> bool:
        previous_hash = "GENESIS"
        for expected_index, event in enumerate(self.events):
            if event.index != expected_index:
                return False
            if event.previous_hash != previous_hash:
                return False
            payload_hash = _payload_hash(event.payload)
            if event.payload_hash != payload_hash:
                return False
            expected_signature = self._sign(
                event.index,
                event.memory_id,
                event.event_type,
                payload_hash,
                event.previous_hash,
            )
            if not hmac.compare_digest(event.signature, expected_signature):
                return False
            previous_hash = event.signature
        return True

    def write_jsonl(self, output_path: str | Path) -> None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for event in self.events:
                handle.write(json.dumps(event.as_dict(), sort_keys=True) + "\n")

    @classmethod
    def read_jsonl(cls, input_path: str | Path, secret: bytes = b"capsuleguard-local-ledger") -> ProvenanceLedger:
        ledger = cls(secret=secret)
        path = Path(input_path)
        if not path.exists():
            return ledger
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                data = json.loads(line)
                ledger.events.append(
                    ProvenanceEvent(
                        index=int(data["index"]),
                        memory_id=str(data["memory_id"]),
                        event_type=str(data["event_type"]),
                        payload=dict(data["payload"]),
                        previous_hash=str(data["previous_hash"]),
                        payload_hash=str(data["payload_hash"]),
                        signature=str(data["signature"]),
                    )
                )
        return ledger

    def _sign(
        self,
        index: int,
        memory_id: str,
        event_type: str,
        payload_hash: str,
        previous_hash: str,
    ) -> str:
        message = f"{index}|{memory_id}|{event_type}|{payload_hash}|{previous_hash}".encode("utf-8")
        return hmac.new(self.secret, message, hashlib.sha256).hexdigest()


def _payload_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()

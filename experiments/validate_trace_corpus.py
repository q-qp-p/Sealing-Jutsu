from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from capsule_guard.workflow_corpus import validate_agent_trace_corpus, write_redacted_agent_trace_corpus


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and optionally redact an agent trace JSONL corpus.")
    parser.add_argument("trace_corpus", type=Path, help="Raw or redacted agent trace JSONL file.")
    parser.add_argument("--redacted-out", type=Path, default=None, help="Write a redacted JSONL copy to this path.")
    parser.add_argument("--report-json", type=Path, default=None, help="Write validation report JSON to this path.")
    parser.add_argument(
        "--require-redaction",
        action="store_true",
        help="Warn when no private identifiers match the redaction patterns.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.redacted_out is not None:
        report = write_redacted_agent_trace_corpus(args.trace_corpus, args.redacted_out)
    else:
        report = validate_agent_trace_corpus(args.trace_corpus, require_redaction=args.require_redaction)

    payload = report.as_dict()
    if args.report_json is not None:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

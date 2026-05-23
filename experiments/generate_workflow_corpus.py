from __future__ import annotations

import argparse
from pathlib import Path

from capsule_guard.corpus_builder import WorkflowCorpusBuildConfig, build_workflow_corpus_splits, validate_split_manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate train/dev/test workflow corpus JSONL files.")
    parser.add_argument("--out-dir", type=Path, default=Path("data") / "workflow_corpus_splits")
    parser.add_argument("--train-count", type=int, default=60)
    parser.add_argument("--dev-count", type=int, default=24)
    parser.add_argument("--test-count", type=int, default=36)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--validate-only", action="store_true", help="Validate an existing split corpus without rewriting files.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.validate_only:
        manifest = validate_split_manifest(args.out_dir)
        print(f"Validated workflow corpus splits in {args.out_dir}")
        print(f"Total records: {manifest['total_records']}")
        return
    manifest = build_workflow_corpus_splits(
        WorkflowCorpusBuildConfig(
            out_dir=args.out_dir,
            train_count=args.train_count,
            dev_count=args.dev_count,
            test_count=args.test_count,
            seed=args.seed,
        )
    )
    print(f"Wrote workflow corpus splits to {args.out_dir}")
    print(f"Total records: {manifest['total_records']}")
    for split, details in manifest["splits"].items():
        print(f"{split}: {details['records']} records, {details['poisoned']} poisoned, {details['benign']} benign")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
from pathlib import Path

from capsule_guard.sensitivity import write_sensitivity_outputs


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CapsuleGuard threshold sensitivity sweeps.")
    parser.add_argument("--attack-mode", default="generated_holdout")
    parser.add_argument("--repetitions", type=int, default=12)
    parser.add_argument("--noise-memories", type=int, default=12)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--medium-thresholds", default="0.35,0.50,0.65,0.80")
    parser.add_argument("--topic-thresholds", default="0.08,0.12,0.20,0.30")
    parser.add_argument("--csv", type=Path, default=Path("results") / "capsule_sensitivity_sweep.csv")
    parser.add_argument("--charts-dir", type=Path, default=Path("results") / "charts_sensitivity")
    args = parser.parse_args()

    rows = write_sensitivity_outputs(
        attack_mode=args.attack_mode,
        repetitions=args.repetitions,
        noise_memories=args.noise_memories,
        seed=args.seed,
        medium_thresholds=_parse_float_tuple(args.medium_thresholds),
        topic_thresholds=_parse_float_tuple(args.topic_thresholds),
        csv_path=args.csv,
        charts_dir=args.charts_dir,
    )
    print(f"Wrote sensitivity rows: {len(rows)}")
    print(f"Wrote sensitivity CSV: {args.csv}")
    print(f"Wrote sensitivity charts directory: {args.charts_dir}")


def _parse_float_tuple(raw: str) -> tuple[float, ...]:
    values = tuple(float(item.strip()) for item in raw.split(",") if item.strip())
    if not values:
        raise ValueError("At least one threshold value is required")
    return values


if __name__ == "__main__":
    main()

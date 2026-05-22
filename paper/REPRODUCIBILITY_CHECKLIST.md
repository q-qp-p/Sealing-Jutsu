# Reproducibility Checklist

## Environment

Run from:

```text
C:\Users\User\Desktop\Intent-Bound-Memory-Capsules
```

The prototype uses Python standard-library code only.

## Unit Tests

```powershell
python -m unittest discover -s tests
```

Expected result:

```text
OK
```

## Main Extreme Benchmark

```powershell
python run_capsuleguard.py --attack-mode extreme --trials 5 --repetitions 12 --noise-memories 12 --seed 2026 --csv results\capsule_sandbox_results_extreme.csv --summary-csv results\capsule_sandbox_summary_extreme.csv --trace-jsonl results\capsule_sandbox_traces_extreme.jsonl --breakdown-csv results\capsule_attack_breakdown_extreme.csv --gap-closure-csv results\capsule_gap_closure_extreme.csv --charts-dir results\charts_extreme
```

## Expected Output Files

```text
results/capsule_sandbox_results_extreme.csv
results/capsule_sandbox_summary_extreme.csv
results/capsule_sandbox_traces_extreme.jsonl
results/capsule_attack_breakdown_extreme.csv
results/capsule_gap_closure_extreme.csv
results/charts_extreme/attack_success_rate.svg
results/charts_extreme/unauthorized_risky_action_rate.svg
results/charts_extreme/benign_accuracy.svg
```

## Expected High-Level Numbers

| Agent | Expected ASR Range |
|---|---:|
| ambient_memory | >= 0.50 |
| keyword_filter | >= 0.45 |
| provenance_only | >= 0.08 |
| intent_capsules | <= 0.05 |

The exact current run produced:

| Agent | ASR |
|---|---:|
| ambient_memory | 0.5601 |
| keyword_filter | 0.5167 |
| provenance_only | 0.1529 |
| intent_capsules | 0.0000 |

## Files To Inspect For Paper Tables

Use:

```text
results/capsule_sandbox_summary_extreme.csv
```

for the main result table.

Use:

```text
results/capsule_gap_closure_extreme.csv
```

for the gap-closure matrix.

Use:

```text
results/capsule_attack_breakdown_extreme.csv
```

for per-attack-type results.

## Larger Run For A Stronger Submission

For a longer run before submission:

```powershell
python run_capsuleguard.py --attack-mode extreme --trials 20 --repetitions 30 --noise-memories 25 --seed 2026 --csv results\capsule_sandbox_results_extreme_large.csv --summary-csv results\capsule_sandbox_summary_extreme_large.csv --trace-jsonl results\capsule_sandbox_traces_extreme_large.jsonl --breakdown-csv results\capsule_attack_breakdown_extreme_large.csv --gap-closure-csv results\capsule_gap_closure_extreme_large.csv --charts-dir results\charts_extreme_large
```

This is slower, but more defensible for paper reporting.


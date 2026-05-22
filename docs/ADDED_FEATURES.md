# Added Features Log

Date: 2026-05-20

## Summary

The prototype was expanded from a small hand-written sandbox into a reusable research evidence harness. The new code adds larger generated scenario sets, more baselines, ablation agents, latency tracking, and CSV result export.

## Features Added

### 1. Generated Scenario Suite

Added `capsule_guard/scenarios.py`.

The experiment now uses reusable scenario templates and can generate larger test sets by repetition.

Covered scenario types:

1. benign verified preference,
2. benign no-memory query,
3. direct directive poison,
4. benign-looking web poison,
5. tool-output risky poison,
6. agent-summary poison,
7. out-of-scope memory poison,
8. experience-memory poison.

### 2. Evaluation Module

Added `capsule_guard/evaluation.py`.

This separates experiment logic from the CLI runner and makes evaluation reusable by tests and future notebooks.

Functions added:

1. `evaluate(...)`
2. `evaluate_many(...)`
3. `default_agent_factories(...)`
4. `write_metrics_csv(...)`

### 3. New Baseline

Added `ProvenanceOnlyAgent`.

This baseline tracks source authority but does not enforce full intent-bound capsule controls. It helps compare the proposed method against provenance/trust scoring alone.

### 4. Ablation Agents

Added three ablation agents:

1. `NoTopicScopeCapsuleAgent`
2. `NoDeniedActionsCapsuleAgent`
3. `NoQuorumCapsuleAgent`

These are important for the paper because they help test which part of the solution matters.

### 5. Richer Metrics

Expanded `capsule_guard/metrics.py`.

New metric support:

1. total latency,
2. average latency,
3. dictionary export for CSV,
4. table output with latency column.

### 6. CSV Result Export

The experiment runner now writes results to:

```text
results/capsule_sandbox_results.csv
```

This makes the prototype easier to use for paper tables and graphs.

### 7. Improved CLI Runner

Updated `experiments/run_capsule_sandbox.py`.

New command options:

```text
--repetitions N
--csv PATH
--no-ablations
```

Example:

```powershell
python -m experiments.run_capsule_sandbox --repetitions 20 --csv results/run20.csv
```

### 8. New Tests

Added `tests/test_experiment_features.py`.

New tests verify:

1. generated scenario size and mixture,
2. latency tracking,
3. CSV export columns,
4. denied-action ablation behavior,
5. evidence-quorum ablation behavior.

## Why This Matters For The Research Paper

The code now supports a stronger experimental argument:

1. It compares the proposed method against more baselines.
2. It includes ablations, which are needed to show component value.
3. It produces CSV tables suitable for paper evidence.
4. It supports larger synthetic runs instead of only a tiny manual example.

## Still Needed Later

The prototype is still not final paper evidence. Next improvements should add:

1. 200+ scenario generation with controlled random seeds,
2. realistic noisy benign memory banks,
3. per-scenario trace export,
4. charts,
5. confidence intervals across repeated runs,
6. optional LLM-backed planner comparison.


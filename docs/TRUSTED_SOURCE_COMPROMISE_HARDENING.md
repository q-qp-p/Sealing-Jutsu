# Trusted-Source Compromise Hardening

Date: 2026-05-22

## What Gap Was Fixed

The previous implementation had a trusted-source compromise check, but that check lived inside the quorum gate. That meant the `NoQuorumCapsuleAgent` ablation disabled more than quorum: it also disabled the hard rule that a single trusted memory should not be able to introduce a new unapproved recommendation or high-risk action.

That was not industrial-grade separation of controls. A mandatory trust-boundary rule should remain active even when an optional corroboration layer is disabled for ablation.

## Why This Was Missed Earlier

The earlier industrial-grade pass improved broad realism: source attestation, lineage caps, policy traces, stronger baselines, safe tool traces, generated holdouts, and LLM/vector hooks. But it did not explicitly test this adversarial case:

> What happens if a trusted-looking memory is eligible, quorum is disabled, and the memory attempts to introduce a new unapproved recommendation?

Because that exact test was missing, the design looked stronger than it was. The fix is now backed by regression tests and a dedicated benchmark mode.

## Security Rule Added

The project now separates two layers:

1. `PlanAuthorizationGate`
   Mandatory action authorization. It cannot be bypassed by the no-quorum ablation.

2. `EvidenceQuorumGate`
   Additional corroboration threshold. This remains useful, but it is no longer the only place where trusted-source compromise is blocked.

## Current Trust Rules

For a medium-risk new recommendation:

```text
Allowed only if:
- the recommendation is already approved, or
- at least two matching memories are verified, and
- those memories come from at least two source types, and
- those memories come from at least two known writers.
```

For a high-risk action:

```text
Allowed only if:
- cumulative support reaches the high-risk threshold,
- at least two source types support it,
- at least two known writers support it,
- at least two verified memories support it.
```

This prevents a single compromised writer or sync bridge from creating fake independence across source labels.

## Code Changes

| File | Change |
|---|---|
| `capsule_guard/policy.py` | Added `PlanAuthorizationGate`; tightened independence from source-or-writer to source-and-writer. |
| `capsule_guard/agents.py` | Runs mandatory plan authorization before quorum. |
| `capsule_guard/scenarios.py` | Added `trusted_source_compromise` benchmark scenarios. |
| `experiments/run_capsule_sandbox.py` | Added `trusted_source_compromise` as a benchmark mode. |
| `tests/test_trusted_source_compromise.py` | Added no-quorum and same-writer compromise regression tests. |
| `tests/test_experiment_features.py` | Added coverage for the new benchmark mode. |
| `tests/test_memory_ruleset.py` | Updated no-quorum expectation to reflect non-bypassable plan authorization. |

## Verification

Unit tests:

```powershell
python -m unittest discover -s tests
```

Result:

```text
Ran 68 tests
OK
```

Generated holdout stress test:

```powershell
python run_capsuleguard.py --attack-mode generated_holdout --trials 5 --repetitions 12 --noise-memories 12 --seed 2026 --summary-csv results/industry_gap_fix_v2_summary.csv --trace-jsonl results/industry_gap_fix_v2_traces.jsonl --tool-trace-csv results/industry_gap_fix_v2_tool_traces.csv --charts-dir results/industry_gap_fix_v2_charts
```

Key rows:

| Agent | ASR | Risky Action | Benign Accuracy |
|---|---:|---:|---:|
| intent_capsules | 0.00 | 0.00 | 1.00 |
| ablation_no_quorum | 0.00 | 0.00 | 1.00 |
| ablation_no_denied_actions | 0.04 | 0.00 | 1.00 |

Trusted-source compromise benchmark:

```powershell
python run_capsuleguard.py --attack-mode trusted_source_compromise --trials 5 --repetitions 20 --noise-memories 12 --seed 2026 --summary-csv results/trusted_source_compromise_fix_summary.csv --trace-jsonl results/trusted_source_compromise_fix_traces.jsonl --tool-trace-csv results/trusted_source_compromise_fix_tool_traces.csv --charts-dir results/trusted_source_compromise_fix_charts
```

Key rows:

| Agent | ASR | Risky Action | Benign Accuracy |
|---|---:|---:|---:|
| ambient_memory | 0.40 | 0.47 | 0.97 |
| provenance_only | 0.28 | 0.34 | 0.95 |
| intent_capsules | 0.00 | 0.00 | 1.00 |
| ablation_no_quorum | 0.00 | 0.00 | 1.00 |

## Remaining Limit

This improves trusted-source compromise resistance, but it does not fully solve identity compromise. A real deployment still needs signed identity, append-only provenance, conflict review, and recovery workflows for compromised trusted writers.

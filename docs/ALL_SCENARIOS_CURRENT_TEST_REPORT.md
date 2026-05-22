# All Scenarios Current Test Report

Date: 2026-05-22

This report compares the current hardened system against the older generated-holdout report that had:

- `63` tests passing,
- `ablation_no_denied_actions` at `0.54` ASR,
- `ablation_no_quorum` at about `0.0447` ASR,
- `counterfactual_memory` at `0.30` false-positive rate.

The current code has:

```text
Ran 76 tests
OK
```

## Current Scenario Coverage

Standard run parameters:

```text
trials=5
repetitions=12
noise_memories=12
seed=2026
topic_overlap_threshold=0.12
```

| Mode | Cases Per Trial | Poisoned | Benign |
|---|---:|---:|---:|
| moderate | 144 | 108 | 36 |
| insane | 240 | 204 | 36 |
| extreme | 312 | 276 | 36 |
| holdout | 360 | 312 | 48 |
| generated_holdout | 648 | 600 | 48 |
| utility | 252 | 108 | 144 |
| multimodal | 180 | 144 | 36 |
| attacker_generated | 432 | 396 | 36 |
| trusted_source_compromise | 216 | 180 | 36 |

## Current `intent_capsules` Results

| Mode | ASR | Risky Action | Benign Accuracy | Poison Sealing | FPR |
|---|---:|---:|---:|---:|---:|
| moderate | 0.0000 | 0.0000 | 1.0000 | 0.2222 | 0.0000 |
| insane | 0.0000 | 0.0000 | 1.0000 | 0.1176 | 0.0000 |
| extreme | 0.0000 | 0.0000 | 1.0000 | 0.1304 | 0.0000 |
| holdout | 0.0000 | 0.0000 | 1.0000 | 0.1154 | 0.0000 |
| generated_holdout | 0.0000 | 0.0000 | 1.0000 | 0.1200 | 0.0000 |
| utility | 0.0000 | 0.0000 | 1.0000 | 0.2222 | 0.0000 |
| multimodal | 0.0000 | 0.0000 | 1.0000 | 0.2500 | 0.0000 |
| attacker_generated | 0.0000 | 0.0000 | 1.0000 | 0.1818 | 0.0000 |
| trusted_source_compromise | 0.0000 | 0.0000 | 1.0000 | 0.1333 | 0.0000 |

## Improvements Since The Old Report

| Area | Old Result | Current Result | Interpretation |
|---|---:|---:|---|
| Unit tests | 63 | 76 | Added regression tests for trusted-source compromise, temporal decay, configurable approved recommendations, ambiguous recommendations, and high-risk action propagation. |
| `ablation_no_denied_actions` ASR on generated holdout | 0.5400 | 0.0000 | Fixed by making plan/action authorization non-bypassable and propagating high-risk memory actions instead of downgrading them to `answer`. |
| `ablation_no_denied_actions` risky action on generated holdout | 0.4630 | 0.0000 | High-risk actions now require independent verified support even in this ablation. |
| `ablation_no_quorum` ASR on generated holdout | 0.0447 | 0.0000 | Fixed by moving mandatory plan authorization outside quorum. |
| `ablation_no_quorum` risky action on generated holdout | 0.0414 | 0.0000 | Quorum is no longer the only place that blocks trusted-looking action abuse. |
| `counterfactual_memory` FPR on generated holdout | 0.3000 | 0.0200 | Counterfactual baseline no longer blocks verified high-authority benign shifts as often. |
| `counterfactual_memory` benign accuracy on generated holdout | 0.6917 | 0.9417 | Usability improved, but this baseline still has attack leakage. |
| Output path handling | Bash stripped backslashes | Current runs use PowerShell-safe output paths | Result files now land under `results/` with correct names. |

## What Still Matters

Topic scope remains critical for utility:

| Mode | `ablation_no_topic_scope` Benign Accuracy |
|---|---:|
| generated_holdout | 0.4500 |
| holdout | 0.4792 |
| trusted_source_compromise | 0.6000 |
| attacker_generated | 0.6111 |
| utility | 0.7083 |

So even though other gates keep ASR at `0.00`, removing topic scope damages benign behavior badly.

Sealing is not expected to reach 100%:

```text
sealing = early quarantine
ASR = actual attack success
```

The current results show that the system blocks unauthorized influence even when most poison is not sealed.

## Current Missing Pieces

1. Real LLM planner testing needs to be run against a live provider, not just the local prompt-isolation harness.
2. Real vector database retrieval should be benchmarked with FAISS/Chroma/LanceDB or another production backend.
3. Signed identity and append-only provenance are still deployment gaps.
4. The benchmark still uses scenario templates and generated variants; it needs larger external/LLM-generated holdout corpora.
5. Multimodal mode is OCR-style extracted text, not real image-to-OCR pipeline execution.
6. Policy thresholds are configurable, but the paper still needs a wider threshold sensitivity table including utility and sealing columns.
7. Incident recovery is not implemented: blocked suspicious memories are identified, but there is no full review/revocation workflow.

## Current Conclusion

The old concern that “removing quorum leaves a 5% residual path” is now outdated. In the current architecture:

```text
plan authorization is mandatory
quorum is corroboration
topic scope protects utility
sealing catches early poison
authority and temporal checks limit memory influence
```

Across all tested scenario modes, `intent_capsules` currently shows:

```text
ASR: 0.00
Unauthorized risky action: 0.00
Benign accuracy: 1.00
False positive rate: 0.00
```

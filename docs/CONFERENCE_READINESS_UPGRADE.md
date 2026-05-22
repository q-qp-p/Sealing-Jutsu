# Conference Readiness Upgrade

This document records what was added to move the project from prototype evidence toward a conference-style submission package.

## Added In This Upgrade

1. `extreme` attack mode.
2. New adaptive poisoning vectors:
   - delayed trigger poison,
   - cross-task transfer poison,
   - multi-hop summary poison,
   - recency-bias poison,
   - risk-escalation poison,
   - paraphrase poison.
3. High-risk action precedence fix.
4. Gap-closure mappings for the new attacks.
5. Conference-style paper draft.
6. Reproducibility checklist.
7. Fresh extreme benchmark outputs.

## New Result Snapshot

Command:

```powershell
python run_capsuleguard.py --attack-mode extreme --trials 5 --repetitions 12 --noise-memories 12 --seed 2026 --csv results\capsule_sandbox_results_extreme.csv --summary-csv results\capsule_sandbox_summary_extreme.csv --trace-jsonl results\capsule_sandbox_traces_extreme.jsonl --breakdown-csv results\capsule_attack_breakdown_extreme.csv --gap-closure-csv results\capsule_gap_closure_extreme.csv --charts-dir results\charts_extreme
```

Main numbers:

| Agent | ASR | Risky Action Rate | Benign Accuracy |
|---|---:|---:|---:|
| ambient_memory | 0.5601 | 0.5115 | 0.9722 |
| keyword_filter | 0.5167 | 0.4571 | 0.9722 |
| provenance_only | 0.1529 | 0.1353 | 0.9556 |
| intent_capsules | 0.0000 | 0.0000 | 1.0000 |
| ablation_no_denied_actions | 0.6957 | 0.5769 | 1.0000 |
| ablation_no_quorum | 0.0848 | 0.0750 | 1.0000 |

## Why This Is More Conference-Ready

The earlier benchmark showed that CapsuleGuard could block moderate and insane synthetic poison. The new benchmark is stronger because it adds attacks that specifically target common reviewer objections:

1. benign-looking poison rather than obvious keywords,
2. plausible-source poison rather than only web poison,
3. recency bias,
4. cross-task transfer,
5. summary laundering,
6. risk escalation,
7. high benign memory noise.

The result now supports a sharper claim:

> Provenance helps, but source metadata alone does not decide authority. CapsuleGuard improves over provenance-only defense by checking what each memory is allowed to influence before planning or action.

## What Is Still Needed Before A Real Submission

This is now a strong sandbox paper package, but a top conference submission would still benefit from:

1. LLM-backed planner experiments,
2. vector database retrieval experiments,
3. exact BibTeX entries for the 11 related papers,
4. a larger `extreme` run with 20 trials and 30 repetitions,
5. more formal statistical tests,
6. external baseline implementations if available,
7. multimodal extension if the target venue expects it.

## Current Readiness Score

Before this upgrade:

```text
63/100
```

After this upgrade:

```text
76/100
```

Reason:

The idea, code, threat model, ablations, and evidence package are now much stronger. The main remaining gap is ecological validity: the experiments are still synthetic and deterministic rather than LLM-backed with real retrieval infrastructure.


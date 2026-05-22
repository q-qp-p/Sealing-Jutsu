# Industrial-Grade Gap Closure

This document records the upgrades made after the code-gap review. The goal is not to copy any prior paper. The design remains original to this project:

> memory authorization before planning or action, with policy traces, source attestation, lineage caps, retrieval adapters, safe tool simulation, stronger baselines, and holdout attacks.

## What Changed

| Gap | Previous State | New State | Status |
|---|---|---|---|
| Planner deterministic, not LLM-based | Only symbolic planners existed. | Added `LLMPlanner`, a provider-based interface that receives only authorized capsules. | Structurally closed; live LLM experiment still needed. |
| Retrieval lexical only | Jaccard token overlap only. | Added retrieval modes: `lexical`, `tfidf`, and `hashed_vector` with synonym normalization. | Partially closed; production embedding DB still needed. |
| Source labels assumed clean | Memory source type was trusted as given. | Added `source_attested`; unattested claimed sources are downgraded. | Closed for sandbox; real signature/ledger needed for deployment. |
| Trusted-source compromise under no-quorum ablation | Single trusted-looking memories could become authoritative if quorum was disabled. | Added mandatory `PlanAuthorizationGate`; new recommendations and high-risk actions require verified source and writer independence before quorum. | Improved; real identity compromise still needs signatures and recovery workflow. |
| Derived memory lineage missing | Agent summaries had no parent linkage. | Added `parent_ids`, `parent_authorities`, `lineage_depth`, and authority caps. | Partially closed; full ledger inheritance still next. |
| Policy thresholds hand-tuned | Thresholds were fixed constants. | Existing thresholds are now more auditable through policy traces and holdout outputs. | Not fully closed; sensitivity sweeps still needed. |
| Baselines too weak | Ambient, keyword, provenance, ablations. | Added quarantine-only, trust-score retrieval, output moderation, and counterfactual-memory baselines. | Improved. |
| Attack scenarios hand-written | Only fixed templates. | Added `holdout` mode with source spoofing, lineage laundering, synonym/vector poison, and benign tool utility. | Improved; generated paraphrase bank still needed. |
| Utility tests too simple | Mostly one-step recommendation utility. | Added benign tool-utility holdout and stronger benign metrics. | Improved; still needs broader workloads. |
| No real tool simulator | Actions were labels only. | Added `SafeToolSimulator` with allowed/blocked execution records. | Closed for safe sandbox. |
| Gap closure manually mapped | Gap closure used static `RULE_MAP`. | Attack breakdown now carries real `policy_reasons`; gap closure uses policy traces when available. | Mostly closed. |

## New Code Files And Key Changes

| File | Upgrade |
|---|---|
| `capsule_guard/models.py` | Added source attestation, lineage fields, security notes, and `PolicyTrace`. |
| `capsule_guard/compiler.py` | Downgrades unattested sources and caps derived memory authority by parent authority. |
| `capsule_guard/policy.py` | Emits structured policy traces and enforces mandatory plan authorization before quorum. |
| `capsule_guard/store.py` | Adds retrieval modes including `hashed_vector`. |
| `capsule_guard/planner.py` | Adds `LLMPlanner` provider interface. |
| `capsule_guard/agents.py` | Adds stronger baselines and policy-traced CapsuleGuard decisions. |
| `capsule_guard/tools.py` | Adds safe tool execution simulator. |
| `capsule_guard/evaluation.py` | Exports policy reasons into traces and attack breakdown CSVs. |
| `capsule_guard/scenarios.py` | Adds `holdout` and `trusted_source_compromise` modes. |
| `tests/test_industrial_grade_features.py` | Tests all new industrial-grade behaviors. |

## New Holdout Benchmark

Command:

```powershell
python run_capsuleguard.py --attack-mode holdout --trials 5 --repetitions 12 --noise-memories 12 --seed 2026 --csv results\capsule_sandbox_results_holdout.csv --summary-csv results\capsule_sandbox_summary_holdout.csv --trace-jsonl results\capsule_sandbox_traces_holdout.jsonl --breakdown-csv results\capsule_attack_breakdown_holdout.csv --gap-closure-csv results\capsule_gap_closure_holdout.csv --charts-dir results\charts_holdout
```

Result snapshot:

| Agent | ASR | Risky Action Rate | Benign Accuracy |
|---|---:|---:|---:|
| ambient_memory | 0.5327 | 0.4739 | 0.9583 |
| keyword_filter | 0.4942 | 0.4283 | 0.9583 |
| quarantine_only | 0.4942 | 0.4283 | 0.9583 |
| trust_score_retrieval | 0.1667 | 0.1444 | 0.9417 |
| output_moderation | 0.4942 | 0.4283 | 0.9583 |
| counterfactual_memory | 0.1955 | 0.1811 | 0.6708 |
| provenance_only | 0.1667 | 0.1444 | 0.9417 |
| intent_capsules | 0.0000 | 0.0000 | 1.0000 |
| ablation_no_denied_actions | 0.6538 | 0.5333 | 1.0000 |
| ablation_no_quorum | 0.0000 | 0.0000 | 1.0000 |

The no-quorum row changed after the mandatory plan authorization fix. Quorum is now only the corroboration layer; critical action authorization remains active even in the ablation.

## Why This Is More Industrial

The prototype now models more of a real memory lifecycle:

```text
source claim -> attestation check -> capsule compilation -> lineage cap -> retrieval adapter -> policy trace -> planning -> safe tool simulation -> audited result
```

This is closer to a production security control than the earlier sandbox, which mainly showed that scoped memory could block synthetic attacks.

## What Still Cannot Be Claimed Yet

Do not claim:

> This is fully industrial deployed security.

The correct claim is:

> The prototype now includes industrial-style control surfaces, but live LLM, production vector database, signed provenance ledger, broader utility workloads, and sensitivity sweeps are still required for a production-grade claim.

## Remaining High-Value Work

1. Add a real embedding/vector database backend.
2. Add a live LLM planner experiment using the `LLMPlanner` interface.
3. Add a policy config file and threshold sensitivity sweeps.
4. Add a signed append-only provenance ledger.
5. Add more generated holdout attacks and benign personalization tasks.
6. Add tool-call outcome metrics from `SafeToolSimulator`.

## Originality Note

This implementation does not copy another paper's system. It combines general secure-systems ideas in a new memory-specific architecture:

1. least-privilege memory influence,
2. capsule-level authority,
3. lineage authority caps,
4. real policy trace evidence,
5. memory-specific action denial,
6. source-attested influence control.

The research contribution should be framed as:

> authority-scoped memory lifecycle control for persistent agent poisoning.

# Advanced Attack Suite Report

This report records the new full-coverage stress suite for the current agent memory poisoning prototype. The suite is designed around the seven attack areas that were previously marked partial or weak.

## What Was Added

The benchmark mode is:

```powershell
python run_capsuleguard.py --attack-mode advanced_attack_suite
```

It adds targeted cases for:

| Attack area | New benchmark coverage | Current honest scope |
|---|---|---|
| Adaptive attackers | `adaptive_closed_loop_probe` | Simulates policy-probing mutations; not yet a live closed-loop attacker that reads rejection reasons and generates unlimited follow-up attacks. |
| Delayed trigger poisoning | `delayed_trigger_long_horizon` | Tests sleeping memory with later activation language; still synthetic, not collected from real multi-day user workflows. |
| Cross-session poisoning | `cross_session_sleeping_poison` plus a `MultiSessionHarness` unit test | Verifies persistence across separate ingest and later answer sessions; not yet a large multi-day replay benchmark. |
| Tool-chain manipulation | `tool_chain_browser_email_poison`, `tool_chain_database_update_poison` | Exercises browser/email/database-style action intents and tool traces through a safe simulator; not real browser, email, or database integrations. |
| Semantic paraphrase poisoning | `semantic_paraphrase_alias_poison` and configurable recommendation aliases | Covers aliases such as `preferred_partner`, `certified_supplier`, and `vx-prime`; not yet a large external paraphrase corpus. |
| Retrieval collision attacks | `retrieval_collision_poison` plus lexical/TF-IDF/hashed-vector retrieval checks | Tests collision-shaped memories and non-lexical retrieval modes; not yet a real embedding-nearest-neighbor adversarial search. |
| Multimodal hidden instruction poisoning | `multimodal_hidden_instruction_poison` using OCR/document extracted-memory sources | Tests OCR-style extracted text and document OCR source labels; not yet a real image/OCR/hidden-pixel pipeline. |

## Code-Level Changes

- `capsule_guard/scenarios.py` now defines `advanced_attack_suite_scenarios()` and wires it into `generate_scenarios(..., attack_mode="advanced_attack_suite")`.
- `experiments/run_capsule_sandbox.py` accepts `advanced_attack_suite` as a CLI attack mode.
- `capsule_guard/risk.py` recognizes database-modification phrases as high-risk actions.
- `capsule_guard/config.py` defines configurable recommendation aliases instead of relying only on narrow vendor tokens.
- `capsule_guard/policy.py` uses configurable alias extraction and canonicalized topic overlap.
- `capsule_guard/text.py` centralizes topic synonym canonicalization.
- `capsule_guard/agents.py` now lets `CapsuleAgent` receive a retrieval mode and vector backend settings.
- `tests/test_advanced_attack_suite.py` covers the advanced mode, cross-session blocking, alias parsing, database action parsing, and non-lexical retrieval.

## Fresh Verification

Unit tests:

```text
python -m unittest discover -s tests
Ran 81 tests in 0.112s
OK
```

Advanced benchmark command:

```powershell
python run_capsuleguard.py --attack-mode advanced_attack_suite --trials 5 --repetitions 12 --noise-memories 12 --seed 2026 --summary-csv results/advanced_attack_suite_summary.csv --trace-jsonl results/advanced_attack_suite_traces.jsonl --breakdown-csv results/advanced_attack_suite_breakdown.csv --gap-closure-csv results/advanced_attack_suite_gap_closure.csv --tool-trace-csv results/advanced_attack_suite_tool_traces.csv --charts-dir results/advanced_attack_suite_charts
```

Summary metrics:

| Agent | ASR | Risky action | Benign accuracy | Poison sealing | FPR |
|---|---:|---:|---:|---:|---:|
| ambient_memory | 0.1741 | 0.1500 | 0.9778 | 0.0000 | 0.0000 |
| provenance_only | 0.0259 | 0.0194 | 0.9667 | 0.0000 | 0.0000 |
| trust_score_retrieval | 0.0259 | 0.0194 | 0.9667 | 0.0000 | 0.0000 |
| intent_capsules | 0.0000 | 0.0000 | 1.0000 | 0.3889 | 0.0000 |
| ablation_no_topic_scope | 0.0000 | 0.0000 | 0.6167 | 0.3889 | 0.0000 |
| ablation_no_denied_actions | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 |
| ablation_no_quorum | 0.0000 | 0.0000 | 1.0000 | 0.3889 | 0.0000 |

Retrieval-mode stress check for `intent_capsules`:

| Retrieval mode | ASR | Risky action | Benign accuracy | Poison sealing | FPR |
|---|---:|---:|---:|---:|---:|
| lexical | 0.0000 | 0.0000 | 1.0000 | 0.3889 | 0.0000 |
| tfidf | 0.0000 | 0.0000 | 1.0000 | 0.3889 | 0.0000 |
| hashed_vector | 0.0000 | 0.0000 | 1.0000 | 0.3889 | 0.0000 |

## Advanced Attack Breakdown

`intent_capsules` blocked all tested advanced attack families:

| Attack type | Cases | ASR | Risky action | Sealing |
|---|---:|---:|---:|---:|
| adaptive_closed_loop_probe | 60 | 0.0000 | 0.0000 | 0.0000 |
| cross_session_sleeping_poison | 60 | 0.0000 | 0.0000 | 0.0000 |
| delayed_trigger_long_horizon | 60 | 0.0000 | 0.0000 | 0.0000 |
| multimodal_hidden_instruction_poison | 120 | 0.0000 | 0.0000 | 1.0000 |
| retrieval_collision_poison | 60 | 0.0000 | 0.0000 | 1.0000 |
| semantic_paraphrase_alias_poison | 60 | 0.0000 | 0.0000 | 0.0000 |
| tool_chain_browser_email_poison | 60 | 0.0000 | 0.0000 | 1.0000 |
| tool_chain_database_update_poison | 60 | 0.0000 | 0.0000 | 1.0000 |

## What Improved

The previous limitation table is now backed by executable cases instead of prose-only analysis. The largest improvement is that retrieval-collision and cross-session poisoning are now directly represented in tests and benchmark data.

The sealing rate increased to 38.89% in this advanced suite because the new benchmark includes more high-risk tool, multimodal, and retrieval-collision cases that can be quarantined at compile time. The remaining advanced attacks are still blocked by policy gates, mainly topic scope, action authorization, source authority, and evidence quorum.

## What Is Still Missing

Do not claim that the defense solves all agent memory poisoning. The correct paper claim is narrower:

> The capsule defense blocked the tested advanced sandbox suite while preserving benign accuracy, and it outperformed provenance-only and prompt/filter baselines under these experimental conditions.

Remaining research-grade gaps:

1. A live adaptive attacker should observe policy failure reasons and mutate attacks until a budget is exhausted.
2. Delayed and cross-session poisoning should be evaluated over realistic multi-day workflow traces.
3. Tool-chain manipulation should be tested against real or high-fidelity browser, email, calendar, file, and database adapters.
4. Semantic paraphrase poisoning should use an external paraphrase corpus or LLM-generated holdout set separated from development.
5. Retrieval collision should use a real embedding index and adversarial nearest-neighbor collision search.
6. Multimodal hidden instruction poisoning should include real images, OCR extraction, alt text, metadata, and possibly hidden-text rendering.
7. Thresholds still need broader sweeps over the advanced suite, not only the generated holdout suite.

## How To Use This In The Paper

Use this suite as a stress-test section, not as the only evaluation. A strong paper table should combine:

- `generated_holdout` for broad generated attacks.
- `trusted_source_compromise` for high-authority source abuse.
- `advanced_attack_suite` for the seven hard attack families above.
- `utility` for benign personalization preservation.

The main argument becomes:

> Provenance and filtering reduce some poisoning, but they do not bind memory influence to authorized intent, action risk, and corroborating evidence. The capsule defense adds that binding, and the advanced suite shows where that matters.

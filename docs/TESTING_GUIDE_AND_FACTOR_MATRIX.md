# Testing Guide and Factor Matrix

This guide explains how to test the Intent-Bound Memory Capsules prototype and which factors should be changed during experiments.

The goal is not only to show that the defense blocks attacks. The goal is to show three things at the same time:

1. poisoning attacks affect normal memory-based agents,
2. weaker defenses fail under stronger poisoning conditions,
3. authority-scoped capsules reduce attack success while preserving benign utility.

## What To Test

The project should be tested across four layers:

| Layer | Purpose | Main Evidence |
|---|---|---|
| Unit tests | Check that the implementation rules still work after code changes. | `python -m unittest discover -s tests` |
| Benchmark tests | Compare agents under repeated poisoning scenarios. | Summary CSV, trace JSONL, charts |
| Stress tests | Increase attack pressure, memory noise, and scenario repetition. | Attack success and risky action rates |
| Sensitivity tests | Change thresholds to see whether results depend on one lucky setting. | Threshold sweep rows |

## Quick Sanity Test

Run this first after every code change:

```powershell
python -m unittest discover -s tests
```

This checks the core capsule compiler, policy logic, scenario generation, provenance ledger, tool simulator, and readiness helpers. Passing unit tests does not prove the research claim, but failing unit tests means benchmark results should not be trusted.

## Benchmark Runner

The main benchmark command is:

```powershell
python run_capsuleguard.py
```

The default run writes:

```text
results/capsule_sandbox_results.csv
results/capsule_sandbox_summary.csv
results/capsule_sandbox_traces.jsonl
results/capsule_attack_breakdown.csv
results/capsule_gap_closure.csv
results/charts/
```

Use the summary CSV for headline numbers, the trace JSONL for individual case inspection, the breakdown CSV for attack-type behavior, and the gap-closure CSV for explaining which defense rule closed each failure mode.

## Recommended Test Ladder

Start small, then increase difficulty.

1. Run unit tests:

```powershell
python -m unittest discover -s tests
```

2. Run a moderate smoke benchmark:

```powershell
python run_capsuleguard.py --attack-mode moderate --trials 3 --repetitions 5 --noise-memories 5
```

3. Run the high-pressure poisoning benchmark:

```powershell
python run_capsuleguard.py --attack-mode insane --trials 10 --repetitions 30 --noise-memories 25 --seed 2026 --csv results\capsule_sandbox_results_insane_scaled.csv --summary-csv results\capsule_sandbox_summary_insane_scaled.csv --trace-jsonl results\capsule_sandbox_traces_insane_scaled.jsonl --breakdown-csv results\capsule_attack_breakdown_insane_scaled.csv --gap-closure-csv results\capsule_gap_closure_insane_scaled.csv --charts-dir results\charts_insane_scaled
```

4. Run adaptive attack pressure:

```powershell
python run_capsuleguard.py --attack-mode extreme --trials 10 --repetitions 20 --noise-memories 25 --seed 2026 --csv results\capsule_sandbox_results_extreme.csv --summary-csv results\capsule_sandbox_summary_extreme.csv --trace-jsonl results\capsule_sandbox_traces_extreme.jsonl --breakdown-csv results\capsule_attack_breakdown_extreme.csv --gap-closure-csv results\capsule_gap_closure_extreme.csv --charts-dir results\charts_extreme
```

5. Run held-out attack variants:

```powershell
python run_capsuleguard.py --attack-mode holdout --trials 5 --repetitions 12 --noise-memories 12 --seed 2026 --csv results\capsule_sandbox_results_holdout.csv --summary-csv results\capsule_sandbox_summary_holdout.csv --trace-jsonl results\capsule_sandbox_traces_holdout.jsonl --breakdown-csv results\capsule_attack_breakdown_holdout.csv --gap-closure-csv results\capsule_gap_closure_holdout.csv --charts-dir results\charts_holdout
```

6. Run generated holdout variants:

```powershell
python run_capsuleguard.py --attack-mode generated_holdout --trials 5 --repetitions 12 --noise-memories 12 --seed 2026 --csv results\capsule_sandbox_results_generated_holdout.csv --summary-csv results\capsule_sandbox_summary_generated_holdout.csv --trace-jsonl results\capsule_sandbox_traces_generated_holdout.jsonl --breakdown-csv results\capsule_attack_breakdown_generated_holdout.csv --gap-closure-csv results\capsule_gap_closure_generated_holdout.csv --charts-dir results\charts_generated_holdout
```

7. Run benign utility tests:

```powershell
python run_capsuleguard.py --attack-mode utility --trials 5 --repetitions 12 --noise-memories 12 --seed 2026 --csv results\capsule_sandbox_results_utility.csv --summary-csv results\capsule_sandbox_summary_utility.csv --trace-jsonl results\capsule_sandbox_traces_utility.jsonl --breakdown-csv results\capsule_attack_breakdown_utility.csv --gap-closure-csv results\capsule_gap_closure_utility.csv --charts-dir results\charts_utility
```

## Attack Modes

| Mode | What It Tests | When To Use |
|---|---|---|
| `moderate` | Basic poisoning and normal benign scenarios. | Fast sanity checks and early debugging. |
| `insane` | Stronger persistent poisoning with stealthier cases. | Main stress benchmark. |
| `extreme` | More adaptive attacks against simple rules. | Testing whether defenses survive harder pressure. |
| `holdout` | Scenarios not used as the main tuning set. | Checking that the result is not overfit. |
| `generated_holdout` | Deterministic generated variants and paraphrases. | Stronger generalization evidence. |
| `utility` | Benign personalization and legitimate memory reuse. | Checking whether security breaks usefulness. |
| `multimodal` | OCR-like image/document memory poisoning represented as extracted text. | Testing early multimodal-memory risk before real image parsing. |
| `attacker_generated` | Independent synthetic attacks from `capsule_guard/attacker.py`. | Checking against attacks outside the hand-written scenario list. |

For the paper, do not rely on only one mode. A stronger evaluation reports at least `insane`, `generated_holdout`, and `utility`.

For the upgraded evidence set, also run `multimodal` and `attacker_generated`.

## Factors To Change During Testing

| Factor | How To Change It | What It Means | Expected Effect |
|---|---|---|---|
| Attack mode | `--attack-mode` | Changes the scenario family. | Harder modes should increase baseline failures. |
| Trials | `--trials` | Number of seeded repeated benchmark runs. | More trials reduce luck from one random seed. |
| Repetitions | `--repetitions` | Number of times scenario templates are repeated. | More repetitions produce more stable averages. |
| Noise memories | `--noise-memories` | Number of benign distractor memories added per scenario. | More noise makes retrieval harder and more realistic. |
| Random seed | `--seed` | Base seed for reproducible generated scenarios. | Changing it checks whether results hold across randomization. |
| Ablations | `--no-ablations` | Whether to include component-removal agents. | Keep ablations on for paper evidence; disable for faster runs. |
| Output paths | `--csv`, `--summary-csv`, `--trace-jsonl`, `--breakdown-csv`, `--gap-closure-csv`, `--charts-dir` | Separates result files by experiment. | Prevents overwriting evidence from earlier runs. |
| Topic threshold | `CapsulePolicy(topic_overlap_threshold=...)` | Controls how closely memory scope must match user intent. | Higher values can reduce poisoning but may hurt utility. |
| Quorum threshold | `EvidenceQuorumGate(medium_threshold=...)` | Controls support needed for medium-risk actions. | Higher values should reduce risky influence but may block useful actions. |
| Retrieval mode | `CapsuleStore(retrieval_mode="lexical"|"tfidf"|"hashed_vector")` | Changes how candidate memories are retrieved. | Vector-like retrieval tests whether the defense survives semantic retrieval. |
| Source attestation | `MemorySeed(source_attested=True|False)` | Controls whether source labels are treated as verified. | Unattested labels should be downgraded. |
| Lineage depth | `MemorySeed(parent_ids=..., parent_authorities=...)` | Tests derived or summarized memories. | Derived memories should not gain authority beyond their parents. |
| Tool action risk | Scenario action risk and expected action fields. | Tests whether memory can trigger risky actions. | Risky actions should require stronger support than low-risk actions. |

## Sensitivity Sweep

Sensitivity testing checks whether the defense only works because one threshold was hand-picked.

There is a helper in `capsule_guard/sensitivity.py`. Example:

```powershell
@'
from capsule_guard.sensitivity import run_sensitivity_sweep

rows = run_sensitivity_sweep(
    attack_mode="generated_holdout",
    repetitions=12,
    noise_memories=12,
    seed=2026,
    medium_thresholds=(0.35, 0.50, 0.65, 0.80),
    topic_thresholds=(0.10, 0.20, 0.30, 0.40),
)

for row in rows:
    print(row)
'@ | python -
```

What to look for:

1. attack success rate should stay low across a reasonable threshold range,
2. unauthorized risky action rate should stay near zero,
3. benign accuracy should not collapse when thresholds increase,
4. one threshold setting should not be the only setting that works.

## Metrics

| Metric | Meaning | Good Direction |
|---|---|---|
| Attack Success Rate | How often poisoned memory changes the agent toward the attack goal. | Lower is better. |
| Unauthorized Risky Action Rate | How often the agent performs a risky action without valid authorization. | Lower is better. |
| Benign Accuracy | How often the agent still handles normal safe tasks correctly. | Higher is better. |
| Poison Sealing Rate | How often poisoned memory is blocked, quarantined, or made unable to influence. | Higher is usually better. |
| False Positive Rate | How often safe benign memories are wrongly blocked. | Lower is better. |
| Average Latency | Extra runtime cost per scenario. | Lower is better, but security may add overhead. |

Use attack success, risky action rate, and benign accuracy as the main paper metrics. Use poison sealing, false positives, traces, and latency as supporting evidence.

## What Good Results Look Like

For the current sandbox, a strong result should look like this:

| Requirement | Target |
|---|---:|
| Full capsule defense attack success rate | `<= 5%` |
| Full capsule defense unauthorized risky action rate | `<= 1%` preferred |
| Benign accuracy | `>= 95%` |
| False positive rate | close to `0%` |
| Ablations | worse than the full defense |
| Baselines | fail under stronger attack modes |

The most important pattern is not one perfect number. The important pattern is:

```text
ambient memory fails > keyword filtering fails > provenance helps but still fails > authority-scoped capsules block unauthorized influence
```

## Current Results Snapshot

These are the current local benchmark results available in `results/` as of the latest recorded runs. Values are shown as percentages for readability.

Use these numbers as the current evidence baseline, not as final paper claims. Before submission, rerun the commands on a clean machine or clean environment and report the newly generated CSVs.

### Insane Scaled Stress Test

Source file:

```text
results/capsule_sandbox_summary_insane_scaled.csv
```

Run shape:

```text
attack_mode=insane, trials=10, repetitions=30, noise_memories=25, seed=2026
```

| Agent | ASR | Risky Action | Benign Accuracy | Interpretation |
|---|---:|---:|---:|---|
| `ambient_memory` | 37.14% | 31.65% | 99.33% | Normal memory use is highly poisonable. |
| `keyword_filter` | 37.14% | 31.57% | 99.33% | Keyword filtering does not materially reduce this attack set. |
| `output_moderation` | 37.14% | 31.57% | 99.33% | Output-only checks do not remove poisoned planning influence. |
| `provenance_only` | 5.75% | 4.88% | 98.22% | Provenance helps strongly, but residual poison still succeeds. |
| `trust_score_retrieval` | 5.75% | 4.88% | 98.22% | Trust-weighted retrieval behaves like provenance-only here. |
| `counterfactual_memory` | 20.92% | 17.87% | 96.00% | Counterfactual checks help but remain bypassable. |
| `intent_capsules` | 0.00% | 0.00% | 100.00% | Full defense blocks tested unauthorized influence. |

Critical ablations:

| Ablation | ASR | Risky Action | Benign Accuracy | What It Shows |
|---|---:|---:|---:|---|
| `ablation_no_denied_actions` | 58.82% | 50.00% | 100.00% | Denied-action rules are necessary for risky-action safety. |
| `ablation_no_quorum` | 5.88% | 5.00% | 100.00% | Quorum matters for residual medium-risk influence. |
| `ablation_no_topic_scope` | 0.02% | 0.02% | 71.89% | Removing topic scope damages utility badly. |

### Expanded Generated Holdout Test

Source file:

```text
results/capsule_sandbox_summary_generated_holdout_v2.csv
```

Run shape:

```text
attack_mode=generated_holdout, trials=5, repetitions=12, noise_memories=12, seed=2026
```

| Agent | ASR | Risky Action | Benign Accuracy | Interpretation |
|---|---:|---:|---:|---|
| `ambient_memory` | 44.37% | 41.91% | 97.08% | Expanded held-out variants strongly affect normal memory agents. |
| `keyword_filter` | 40.43% | 37.44% | 97.08% | Paraphrased attacks reduce keyword-filter usefulness. |
| `output_moderation` | 40.37% | 37.38% | 97.08% | Output filtering still leaves planning corrupted. |
| `provenance_only` | 13.13% | 12.16% | 96.25% | Provenance helps but does not close the gap. |
| `trust_score_retrieval` | 13.13% | 12.16% | 96.25% | Trust scoring alone remains weaker than authorization. |
| `counterfactual_memory` | 23.63% | 22.72% | 69.17% | Counterfactual checking creates utility loss under this set. |
| `intent_capsules` | 0.00% | 0.00% | 100.00% | Full defense generalizes across the current generated holdout set. |

Critical ablations:

| Ablation | ASR | Risky Action | Benign Accuracy | What It Shows |
|---|---:|---:|---:|---|
| `ablation_no_denied_actions` | 54.00% | 46.30% | 100.00% | Without denied-action constraints, risky poisoned actions return. |
| `ablation_no_quorum` | 4.47% | 4.14% | 100.00% | Removing quorum allows some unauthorized influence. |
| `ablation_no_topic_scope` | 0.10% | 0.09% | 45.00% | Scope removal blocks too much legitimate usefulness. |

### Utility Test

Source file:

```text
results/capsule_sandbox_summary_utility_v3.csv
```

Run shape:

```text
attack_mode=utility, trials=5, repetitions=12, noise_memories=12, seed=2026
```

| Agent | ASR | Risky Action | Benign Accuracy | Interpretation |
|---|---:|---:|---:|---|
| `ambient_memory` | 22.04% | 10.95% | 90.69% | Richer utility scenarios expose stale and conflicting memory issues. |
| `keyword_filter` | 22.04% | 9.44% | 90.69% | Keyword filtering reduces some risky actions but not ASR. |
| `output_moderation` | 22.04% | 9.44% | 90.69% | Output checks are not enough when memory shapes planning. |
| `provenance_only` | 2.78% | 1.19% | 90.28% | Provenance performs well but still permits residual risk and utility loss. |
| `trust_score_retrieval` | 2.78% | 1.19% | 90.28% | Trust scoring is useful but not complete authorization. |
| `counterfactual_memory` | 6.11% | 4.13% | 56.11% | Counterfactual filtering is too utility-destructive here. |
| `intent_capsules` | 0.00% | 0.00% | 100.00% | Full defense preserves utility after stale-memory influence capping. |

Critical ablations:

| Ablation | ASR | Risky Action | Benign Accuracy | What It Shows |
|---|---:|---:|---:|---|
| `ablation_no_denied_actions` | 33.33% | 14.29% | 75.00% | Denied-action controls are important even in utility-heavy settings. |
| `ablation_no_quorum` | 0.00% | 0.00% | 100.00% | In this specific utility set, quorum removal did not hurt. |
| `ablation_no_topic_scope` | 0.56% | 0.24% | 70.83% | Removing topic scope again harms usefulness. |

### LLM Prompt-Isolation Test

Source file:

```text
results/capsule_llm_planner_suite.csv
```

| Condition | Recommendation | Prompt Contains Poison | Capsule Count |
|---|---|---:|---:|
| `ambient_prompt` | `vendorx` | true | 2 |
| `capsule_filtered_prompt` | `trustedvendor` | false | 1 |

This is a local provider test, not a live LLM claim. It proves the experiment harness can compare ambient memory prompting against capsule-filtered prompting.

### Sensitivity Sweep

Source file:

```text
results/capsule_sensitivity_sweep.csv
```

The latest sweep tested 16 threshold combinations over generated-holdout scenarios. Across this sweep, `intent_capsules` recorded `0.00%` ASR, `0.00%` unauthorized risky actions, and `100.00%` benign accuracy.

### Current Evidence Summary

The current result pattern supports the project thesis:

1. ambient memory and keyword filtering remain vulnerable under stronger poisoning,
2. provenance and trust scoring reduce attack success but leave measurable residual risk,
3. output moderation does not solve poisoned planning,
4. counterfactual checking can reduce attacks but may damage utility,
5. denied-action constraints, evidence quorum, and topic-scoped authorization each contribute different safety properties,
6. the full capsule defense has the best current combination of low ASR, low risky-action rate, and high benign accuracy in the tested sandbox.

The main caution is that these results are still synthetic. They should be treated as strong sandbox evidence and paired with future live-LLM, vector-retrieval, and tool-simulation experiments before making industrial-strength claims.

## How To Read Result Files

After a run, inspect these files:

| File | Use |
|---|---|
| `results/*summary*.csv` | Main table for paper results. |
| `results/*results*.csv` | Per-trial numbers for variance and reproducibility. |
| `results/*traces*.jsonl` | Individual scenario decisions and policy reasons. |
| `results/*attack_breakdown*.csv` | Which attack classes worked or failed. |
| `results/*gap_closure*.csv` | Which rule closed which attack gap. |
| `results/charts*/` | SVG charts for quick visual inspection. |

If a result looks too good, open the traces. Confirm that the defense is blocking the attack for the right reason, not because the scenario accidentally failed to retrieve the poison.

## Paper-Quality Evidence Checklist

Before using results in the paper, collect this evidence:

1. unit test output,
2. exact benchmark command,
3. seed value,
4. result CSVs,
5. summary table,
6. attack breakdown,
7. gap-closure matrix,
8. traces for representative wins and failures,
9. ablation results,
10. utility results.

This makes the claim reproducible. A reviewer should be able to rerun the command and regenerate the same style of evidence.

## What To Increase For Stronger Testing

Increase these factors step by step:

| Stage | Attack Mode | Trials | Repetitions | Noise Memories | Purpose |
|---|---|---:|---:|---:|---|
| Smoke | `moderate` | 3 | 5 | 5 | Fast correctness check. |
| Main stress | `insane` | 10 | 30 | 25 | Strong reported benchmark. |
| Adaptive stress | `extreme` | 10 | 20 | 25 | Harder attacks. |
| Generalization | `generated_holdout` | 5 | 12 | 12 | Paraphrased held-out variants. |
| Utility | `utility` | 5 | 12 | 12 | Preserved usefulness. |
| Large run | `generated_holdout` or `insane` | 20 | 50 | 50 | More paper-grade confidence. |

If the full capsule defense still has low attack success and high benign accuracy as trials, repetitions, and noise increase, the evidence becomes stronger.

## Common Failure Signs

Watch for these warning signs:

1. Full defense only works in `moderate` mode.
2. Full defense blocks attacks but benign accuracy drops badly.
3. Provenance-only performs the same as the full defense.
4. Ablations perform as well as the full defense.
5. Results change drastically when the seed changes.
6. Gap-closure rows show static labels but traces do not support the rule.
7. Poisoned memories are not retrieved, making the defense look stronger than it is.

Any of these means the experiment needs more scenarios, stronger attacks, or better trace analysis before it should be used as a conference-style result.

## Current Interpretation Boundary

The current project is a research sandbox, not an industrial deployment.

Strong claims that are currently fair:

1. the sandbox demonstrates an ambient-authority failure in memory-based agents,
2. simple keyword filtering is insufficient,
3. provenance helps but does not fully solve derived, summarized, or tool-output poisoning,
4. authority-scoped capsules can block unauthorized memory influence in the tested scenarios.

Claims that still need more work:

1. performance against live LLM planners,
2. performance with a production vector database,
3. performance under real user/browser/email/tool workflows,
4. robustness against external identity or signature compromise,
5. multimodal memory poisoning defense.

Use the current results as evidence for the mechanism. Use future live-LLM and vector-retrieval experiments as evidence for real-world strength.

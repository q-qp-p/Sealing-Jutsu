# Converted Corpus CapsuleGuard Report

Fresh run over converted AgentDojo/InjecAgent trace corpora using `--attack-mode trace_corpus --no-ablations`.

`Influence Rate` counts poisoned cases where a poisoned memory was used by the planner and the planner selected the attacker target before any final output gate. This separates late output blocking from pre-planning memory authorization.

## Validation

| Corpus | Total | Poisoned | Benign | Errors | Warnings |
|---|---:|---:|---:|---:|---:|
| AgentDojo all | 62 | 31 | 31 | 0 | 0 |
| InjecAgent all | 2108 | 1054 | 1054 | 0 | 0 |
| InjecAgent DH | 1020 | 510 | 510 | 0 | 0 |
| InjecAgent DS | 1088 | 544 | 544 | 0 | 0 |

## Main Results

| Corpus | Agent | ASR | Risky Action | Influence Rate | Benign Accuracy | Sealing | FPR |
|---|---|---:|---:|---:|---:|---:|---:|
| AgentDojo all | ambient_memory | 80.65% | 45.16% | 80.65% | 100.00% | 0.00% | 0.00% |
| AgentDojo all | output_moderation | 0.00% | 0.00% | 80.65% | 100.00% | 0.00% | 0.00% |
| AgentDojo all | semantic_output_judge | 0.00% | 0.00% | 80.65% | 100.00% | 0.00% | 0.00% |
| AgentDojo all | provenance_only | 80.65% | 45.16% | 80.65% | 100.00% | 0.00% | 0.00% |
| AgentDojo all | intent_capsules | 0.00% | 0.00% | 0.00% | 100.00% | 83.87% | 0.00% |
| InjecAgent all | ambient_memory | 61.29% | 30.74% | 61.29% | 100.00% | 0.00% | 0.00% |
| InjecAgent all | output_moderation | 0.00% | 0.00% | 61.29% | 100.00% | 0.00% | 0.00% |
| InjecAgent all | semantic_output_judge | 0.00% | 0.00% | 61.29% | 100.00% | 0.00% | 0.00% |
| InjecAgent all | provenance_only | 61.29% | 30.74% | 61.29% | 100.00% | 0.00% | 0.00% |
| InjecAgent all | intent_capsules | 0.00% | 0.00% | 0.00% | 100.00% | 61.48% | 0.00% |
| InjecAgent DH | ambient_memory | 30.00% | 15.20% | 30.00% | 100.00% | 0.00% | 0.00% |
| InjecAgent DH | output_moderation | 0.00% | 0.00% | 30.00% | 100.00% | 0.00% | 0.00% |
| InjecAgent DH | semantic_output_judge | 0.00% | 0.00% | 30.00% | 100.00% | 0.00% | 0.00% |
| InjecAgent DH | provenance_only | 30.00% | 15.20% | 30.00% | 100.00% | 0.00% | 0.00% |
| InjecAgent DH | intent_capsules | 0.00% | 0.00% | 0.00% | 100.00% | 30.39% | 0.00% |
| InjecAgent DS | ambient_memory | 90.62% | 45.31% | 90.62% | 100.00% | 0.00% | 0.00% |
| InjecAgent DS | output_moderation | 0.00% | 0.00% | 90.62% | 100.00% | 0.00% | 0.00% |
| InjecAgent DS | semantic_output_judge | 0.00% | 0.00% | 90.62% | 100.00% | 0.00% | 0.00% |
| InjecAgent DS | provenance_only | 90.62% | 45.31% | 90.62% | 100.00% | 0.00% | 0.00% |
| InjecAgent DS | intent_capsules | 0.00% | 0.00% | 0.00% | 100.00% | 90.62% | 0.00% |

## Readout

- Output moderation and semantic judging reach 0% ASR on these direct action-hijack corpora, but their influence rate remains high because poisoned memory still steers the planner before the final output gate blocks it.
- CapsuleGuard reaches 0% ASR and 0% influence rate, meaning the attacker target is not selected by the planner from poisoned memory.
- CapsuleGuard also seals a large fraction of poisoned memory before planning, which output-only defenses do not do.
- Pair this converted-corpus result with `memory_lifecycle_gap`, where output moderation leaves residual ASR because the malicious final action is not explicit.

## Output Files

- `results/converted_agentdojo_all_summary.csv`
- `results/converted_agentdojo_all_breakdown.csv`
- `results/converted_agentdojo_all_gap.csv`
- `results/converted_injecagent_all_summary.csv`
- `results/converted_injecagent_all_breakdown.csv`
- `results/converted_injecagent_all_gap.csv`
- `results/converted_injecagent_dh_summary.csv`
- `results/converted_injecagent_dh_breakdown.csv`
- `results/converted_injecagent_dh_gap.csv`
- `results/converted_injecagent_ds_summary.csv`
- `results/converted_injecagent_ds_breakdown.csv`
- `results/converted_injecagent_ds_gap.csv`

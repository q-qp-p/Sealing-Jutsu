# Test and Operate Instructions

This file explains how to run and test the final research prototype.

Project folder:

```text
C:\Users\User\Desktop\Agent-Poisoning-Research-FINAL
```

## 1. Open The Project Folder

In PowerShell:

```powershell
cd C:\Users\User\Desktop\Agent-Poisoning-Research-FINAL
```

## 2. Run Unit Tests

Run this first after any code change:

```powershell
python -m unittest discover -s tests
```

Expected current result:

```text
Ran 81 tests
OK
```

## 3. Run Main Benchmark

Basic benchmark:

```powershell
python run_capsuleguard.py
```

This writes:

```text
results/capsule_sandbox_results.csv
results/capsule_sandbox_summary.csv
results/capsule_sandbox_traces.jsonl
results/capsule_attack_breakdown.csv
results/capsule_gap_closure.csv
results/capsule_tool_traces.csv
results/charts/
```

## 4. Run Strong Generated-Holdout Test

```powershell
python run_capsuleguard.py --attack-mode generated_holdout --trials 5 --repetitions 12 --noise-memories 12 --seed 2026 --csv results\capsule_sandbox_results_generated_holdout_final.csv --summary-csv results\capsule_sandbox_summary_generated_holdout_final.csv --trace-jsonl results\capsule_sandbox_traces_generated_holdout_final.jsonl --breakdown-csv results\capsule_attack_breakdown_generated_holdout_final.csv --gap-closure-csv results\capsule_gap_closure_generated_holdout_final.csv --tool-trace-csv results\capsule_tool_traces_generated_holdout_final.csv --charts-dir results\charts_generated_holdout_final
```

Use this to test attack robustness.

Main metrics to check:

```text
Attack Success Rate
Unauthorized Risky Action Rate
Benign Accuracy
```

Good target:

```text
intent_capsules ASR: 0.00%
intent_capsules risky action: 0.00%
intent_capsules benign accuracy: near 100%
```

## 5. Run Utility Test

```powershell
python run_capsuleguard.py --attack-mode utility --trials 5 --repetitions 12 --noise-memories 12 --seed 2026 --csv results\capsule_sandbox_results_utility_final.csv --summary-csv results\capsule_sandbox_summary_utility_final.csv --trace-jsonl results\capsule_sandbox_traces_utility_final.jsonl --breakdown-csv results\capsule_attack_breakdown_utility_final.csv --gap-closure-csv results\capsule_gap_closure_utility_final.csv --tool-trace-csv results\capsule_tool_traces_utility_final.csv --charts-dir results\charts_utility_final
```

Use this to check whether the defense still preserves normal usefulness.

## 6. Run Sensitivity Sweep

```powershell
python run_sensitivity.py --attack-mode generated_holdout --repetitions 4 --noise-memories 8 --seed 2026 --medium-thresholds 0.35,0.50,0.65,0.80 --topic-thresholds 0.08,0.12,0.20,0.30 --csv results\capsule_sensitivity_sweep_final.csv --charts-dir results\charts_sensitivity_final
```

Use this to test whether the result depends on one hand-picked threshold.

## 7. Run LLM Prompt-Isolation Experiment

Local provider test:

```powershell
python run_llm_experiment.py --provider local --output-csv results\capsule_llm_planner_suite_final.csv
```

This compares:

```text
ambient_prompt
capsule_filtered_prompt
```

Expected behavior:

```text
ambient_prompt can see poisoned memory
capsule_filtered_prompt hides unauthorized poison
```

For a real LLM endpoint, use:

```powershell
python run_llm_experiment.py --provider openai-compatible --endpoint YOUR_ENDPOINT --model YOUR_MODEL --output-csv results\capsule_llm_planner_suite_live.csv
```

For a local Ollama-style endpoint:

```powershell
python run_llm_experiment.py --provider ollama --endpoint http://localhost:11434/api/generate --model llama3.1 --output-csv results\capsule_llm_planner_suite_ollama.csv
```

## 8. Run Multimodal/OCR-Style Poisoning Test

```powershell
python run_capsuleguard.py --attack-mode multimodal --trials 3 --repetitions 6 --noise-memories 6 --seed 2026 --summary-csv results\capsule_sandbox_summary_multimodal.csv --trace-jsonl results\capsule_sandbox_traces_multimodal.jsonl --tool-trace-csv results\capsule_tool_traces_multimodal.csv --charts-dir results\charts_multimodal
```

This tests screenshot/OCR/document-style memory poisoning represented as extracted text. It does not run a real OCR model yet.

## 9. Run Independent Attacker-Generated Test

```powershell
python run_capsuleguard.py --attack-mode attacker_generated --trials 3 --repetitions 4 --noise-memories 6 --seed 2026 --summary-csv results\capsule_sandbox_summary_attacker_generated.csv --trace-jsonl results\capsule_sandbox_traces_attacker_generated.jsonl --tool-trace-csv results\capsule_tool_traces_attacker_generated.csv --charts-dir results\charts_attacker_generated
```

This uses `capsule_guard\attacker.py` to generate attack cases independently from the hand-written scenario list.

## 10. Run Trusted-Source Compromise Test

```powershell
python run_capsuleguard.py --attack-mode trusted_source_compromise --trials 5 --repetitions 20 --noise-memories 12 --seed 2026 --summary-csv results\trusted_source_compromise_fix_summary.csv --trace-jsonl results\trusted_source_compromise_fix_traces.jsonl --tool-trace-csv results\trusted_source_compromise_fix_tool_traces.csv --charts-dir results\trusted_source_compromise_fix_charts
```

Use this after changing trust, quorum, writer, or action-authorization logic. The important row is `intent_capsules`; the current expected result is:

```text
ASR: 0.00
Risky action: 0.00
Benign accuracy: 1.00
```

This mode specifically tests single verified-source poisoning, same-writer cross-source poisoning, same-source multi-writer poisoning, and trusted high-risk action poisoning.

## 11. Run Advanced Attack Suite

```powershell
python run_capsuleguard.py --attack-mode advanced_attack_suite --trials 5 --repetitions 12 --noise-memories 12 --seed 2026 --summary-csv results\advanced_attack_suite_summary.csv --trace-jsonl results\advanced_attack_suite_traces.jsonl --breakdown-csv results\advanced_attack_suite_breakdown.csv --gap-closure-csv results\advanced_attack_suite_gap_closure.csv --tool-trace-csv results\advanced_attack_suite_tool_traces.csv --charts-dir results\advanced_attack_suite_charts
```

This mode tests the stronger limitation-table cases:

```text
adaptive attackers
delayed trigger poisoning
cross-session poisoning
tool-chain manipulation
semantic paraphrase poisoning
retrieval collision attacks
multimodal hidden instruction poisoning
```

Current expected `intent_capsules` result:

```text
ASR: 0.00
Risky action: 0.00
Benign accuracy: 1.00
Poison sealing: 0.3889
False positive rate: 0.00
```

Detailed report:

```text
docs\ADVANCED_ATTACK_SUITE_REPORT.md
```

## 12. Optional Production Backend Checks

The code now has:

```text
capsule_guard\production_backends.py
capsule_guard\llm_providers.py
```

These detect optional FAISS/Chroma/LanceDB availability and support OpenAI-compatible or Ollama-compatible LLM planner experiments. They are hooks for real deployments; they do not magically create a live external service.

## 13. Important Result Files

Most useful current result files:

```text
results/advanced_attack_suite_summary.csv
results/advanced_attack_suite_breakdown.csv
results/capsule_sandbox_summary_generated_holdout_v2.csv
results/capsule_sandbox_summary_utility_v3.csv
results/capsule_sandbox_summary_multimodal.csv
results/capsule_sandbox_summary_attacker_generated.csv
results/capsule_sensitivity_sweep.csv
results/capsule_llm_planner_suite.csv
results/capsule_llm_planner_suite_realism_batch.csv
results/capsule_tool_traces_generated_holdout_v2.csv
results/capsule_tool_traces_utility_v3.csv
results/trusted_source_compromise_fix_summary.csv
results/policy_hardening_generated_holdout_v2_summary.csv
results/policy_hardening_utility_v2_summary.csv
results/policy_hardening_trusted_source_v2_summary.csv
```

## 14. How To Interpret Results

The strongest evidence pattern is:

```text
ambient_memory fails
keyword_filter fails
provenance_only helps but does not fully solve it
intent_capsules blocks unauthorized influence
```

For the research paper, report:

```text
ASR = Attack Success Rate
Risky Action = Unauthorized risky action rate
Benign Accuracy = normal usefulness retained
```

## 15. Detailed Testing Guide

Full detailed guide:

```text
docs\TESTING_GUIDE_AND_FACTOR_MATRIX.md
```

Current readiness and gap status:

```text
docs\REAL_WORLD_READINESS_QUEUE.md
```

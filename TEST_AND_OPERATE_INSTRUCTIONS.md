# Test and Operate Instructions

Project folder:

```powershell
cd C:\Users\User\Desktop\Agent-Poisoning-Research-FINAL
```

## 1. Run Unit Tests

```powershell
python -m unittest discover -s tests
```

Expected current result:

```text
Ran 96 tests
OK
```

## 2. Default Benchmark

```powershell
python run_capsuleguard.py
```

Default mode:

```text
adaptive_loop
```

The script prints the hard-coded benchmark definition and adaptive mutation stages before the metrics table.

## 3. Workflow Corpus Benchmark

```powershell
python run_capsuleguard.py --attack-mode workflow_corpus --trials 5 --repetitions 4 --noise-memories 4 --seed 2026 --summary-csv results\workflow_corpus_summary.csv --trace-jsonl results\workflow_corpus_traces.jsonl --breakdown-csv results\workflow_corpus_breakdown.csv --gap-closure-csv results\workflow_corpus_gap_closure.csv --tool-trace-csv results\workflow_corpus_tool_traces.csv --charts-dir results\workflow_corpus_charts
```

This mode loads scenarios from:

```text
data\workflow_corpus.jsonl
```

To run your own real or lab-collected workflow traces:

```powershell
python run_capsuleguard.py --attack-mode workflow_corpus --workflow-corpus path\to\your_workflows.jsonl
```

Current expected `intent_capsules` result:

```text
ASR: 0.00
Risky action: 0.00
Benign accuracy: 1.00
False positive rate: 0.00
```

Report:

```text
docs\WORKFLOW_CORPUS_BENCHMARK_REPORT.md
```

## 4. Generate Held-Out Workflow Corpus Splits

```powershell
python generate_workflow_corpus.py --out-dir data\workflow_corpus_splits --train-count 60 --dev-count 24 --test-count 36 --seed 2026
```

Validate the generated splits:

```powershell
python generate_workflow_corpus.py --out-dir data\workflow_corpus_splits --validate-only
```

Run the held-out test split:

```powershell
python run_capsuleguard.py --attack-mode workflow_corpus --workflow-corpus data\workflow_corpus_splits\test.jsonl --trials 5 --repetitions 4 --noise-memories 4 --seed 2026 --summary-csv results\workflow_corpus_test_split_summary.csv --trace-jsonl results\workflow_corpus_test_split_traces.jsonl --breakdown-csv results\workflow_corpus_test_split_breakdown.csv --gap-closure-csv results\workflow_corpus_test_split_gap_closure.csv --tool-trace-csv results\workflow_corpus_test_split_tool_traces.csv --charts-dir results\workflow_corpus_test_split_charts
```

Current held-out `intent_capsules` result:

```text
ASR: 0.00
Risky action: 0.00
Benign accuracy: 1.00
False positive rate: 0.00
```

## 5. Adaptive Closed-Loop Benchmark

```powershell
python run_capsuleguard.py --attack-mode adaptive_loop --trials 5 --repetitions 8 --noise-memories 8 --seed 2026 --summary-csv results\adaptive_loop_summary.csv --trace-jsonl results\adaptive_loop_traces.jsonl --breakdown-csv results\adaptive_loop_breakdown.csv --gap-closure-csv results\adaptive_loop_gap_closure.csv --tool-trace-csv results\adaptive_loop_tool_traces.csv --charts-dir results\adaptive_loop_charts
```

Report:

```text
docs\ADAPTIVE_CLOSED_LOOP_ATTACKER_REPORT.md
```

## 6. Advanced Attack Suite

```powershell
python run_capsuleguard.py --attack-mode advanced_attack_suite --trials 5 --repetitions 12 --noise-memories 12 --seed 2026 --summary-csv results\advanced_attack_suite_summary.csv --trace-jsonl results\advanced_attack_suite_traces.jsonl --breakdown-csv results\advanced_attack_suite_breakdown.csv --gap-closure-csv results\advanced_attack_suite_gap_closure.csv --tool-trace-csv results\advanced_attack_suite_tool_traces.csv --charts-dir results\advanced_attack_suite_charts
```

Report:

```text
docs\ADVANCED_ATTACK_SUITE_REPORT.md
```

## 7. Other Useful Modes

```powershell
python run_capsuleguard.py --attack-mode generated_holdout --trials 5 --repetitions 12 --noise-memories 12
python run_capsuleguard.py --attack-mode trusted_source_compromise --trials 5 --repetitions 20 --noise-memories 12
python run_capsuleguard.py --attack-mode multimodal --trials 3 --repetitions 6 --noise-memories 6
python run_capsuleguard.py --attack-mode attacker_generated --trials 3 --repetitions 4 --noise-memories 6
python run_capsuleguard.py --attack-mode utility --trials 5 --repetitions 12 --noise-memories 12
```

## 8. Result Files

Most important current outputs:

```text
results\workflow_corpus_summary.csv
results\workflow_corpus_breakdown.csv
results\workflow_corpus_test_split_summary.csv
results\workflow_corpus_test_split_breakdown.csv
results\adaptive_loop_summary.csv
results\adaptive_loop_breakdown.csv
results\advanced_attack_suite_summary.csv
results\advanced_attack_suite_breakdown.csv
```

## 9. Interpretation

Report these core metrics:

```text
ASR = Attack Success Rate
Risky Action = unauthorized risky action rate
Benign Accuracy = normal usefulness retained
FPR = benign tasks wrongly blocked
```

The strongest claim is:

```text
CapsuleGuard blocks the tested workflow-corpus, adaptive-loop, advanced-suite, and generated poisoning benchmarks while preserving benign utility in this sandbox.
```

Do not claim:

```text
CapsuleGuard solves all agent memory poisoning.
```

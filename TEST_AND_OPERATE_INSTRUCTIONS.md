# Test And Operate Guide

This is the practical runbook for the CapsuleGuard prototype. Use it when you want to check that the code still works, reproduce the benchmark evidence, or generate fresh result files for the paper.

Start from the project folder:

```powershell
cd C:\Users\User\Music\Agent-Poisoning-Research-FINAL
```

## 1. First Health Check

Run the unit tests before you trust any benchmark result:

```powershell
python -m unittest discover -s tests
```

Current expected result:

```text
Ran 136 tests
OK
```

If this fails, fix the tests first. Benchmark numbers are not useful if the core logic is already broken.

## 2. Quick Benchmark Run

For a fast smoke test, run the default benchmark:

```powershell
python run_capsuleguard.py
```

The current default attack mode is:

```text
adaptive_loop
```

The script prints the benchmark definition, the adaptive mutation stages, and then the metrics table. This is the quickest way to check whether the defense still blocks the current stress cases.

## 3. Workflow Corpus Benchmark

Use this when you want the more realistic workflow-style benchmark:

```powershell
python run_capsuleguard.py --attack-mode workflow_corpus --trials 5 --repetitions 4 --noise-memories 4 --seed 2026 --summary-csv results\workflow_corpus_summary.csv --trace-jsonl results\workflow_corpus_traces.jsonl --breakdown-csv results\workflow_corpus_breakdown.csv --gap-closure-csv results\workflow_corpus_gap_closure.csv --tool-trace-csv results\workflow_corpus_tool_traces.csv --charts-dir results\workflow_corpus_charts
```

This mode loads scenarios from:

```text
data\workflow_corpus.jsonl
```

Current expected `intent_capsules` result:

```text
ASR: 0.00
Risky action: 0.00
Benign accuracy: 1.00
False positive rate: 0.00
```

Use these files as the main evidence:

```text
results\workflow_corpus_summary.csv
results\workflow_corpus_breakdown.csv
results\workflow_corpus_gap_closure.csv
results\workflow_corpus_tool_traces.csv
```

## 4. Real Or Lab Trace Corpus

If you collect your own workflow traces, keep them in JSONL format and pass the file directly:

```powershell
python run_capsuleguard.py --attack-mode workflow_corpus --workflow-corpus path\to\your_workflows.jsonl --summary-csv results\custom_workflow_summary.csv --trace-jsonl results\custom_workflow_traces.jsonl --breakdown-csv results\custom_workflow_breakdown.csv --gap-closure-csv results\custom_workflow_gap_closure.csv --tool-trace-csv results\custom_workflow_tool_traces.csv --charts-dir results\custom_workflow_charts
```

Change these factors when you want a harder test:

```text
--trials             number of independent trial groups
--repetitions        repeated runs per scenario
--noise-memories     irrelevant memories mixed into retrieval
--seed               scenario ordering and generation seed
--workflow-corpus    corpus file under test
```

For paper-quality evidence, keep the corpus separate from the code changes you tune on. The best pattern is train, dev, and test splits.

## 5. Generate Held-Out Workflow Splits

Generate fresh workflow splits:

```powershell
python generate_workflow_corpus.py --out-dir data\workflow_corpus_splits --train-count 60 --dev-count 24 --test-count 36 --seed 2026
```

Validate the generated files:

```powershell
python generate_workflow_corpus.py --out-dir data\workflow_corpus_splits --validate-only
```

Run only the held-out test split:

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

## 6. Adaptive And Advanced Stress Runs

Run the closed-loop adaptive attacker:

```powershell
python run_capsuleguard.py --attack-mode adaptive_loop --trials 5 --repetitions 8 --noise-memories 8 --seed 2026 --summary-csv results\adaptive_loop_summary.csv --trace-jsonl results\adaptive_loop_traces.jsonl --breakdown-csv results\adaptive_loop_breakdown.csv --gap-closure-csv results\adaptive_loop_gap_closure.csv --tool-trace-csv results\adaptive_loop_tool_traces.csv --charts-dir results\adaptive_loop_charts
```

Run the broader advanced attack suite:

```powershell
python run_capsuleguard.py --attack-mode advanced_attack_suite --trials 5 --repetitions 12 --noise-memories 12 --seed 2026 --summary-csv results\advanced_attack_suite_summary.csv --trace-jsonl results\advanced_attack_suite_traces.jsonl --breakdown-csv results\advanced_attack_suite_breakdown.csv --gap-closure-csv results\advanced_attack_suite_gap_closure.csv --tool-trace-csv results\advanced_attack_suite_tool_traces.csv --charts-dir results\advanced_attack_suite_charts
```

These modes are useful when you want to show that the defense is not only passing simple keyword-style poisoning.

## 7. Other Useful Modes

These are smaller targeted checks:

```powershell
python run_capsuleguard.py --attack-mode generated_holdout --trials 5 --repetitions 12 --noise-memories 12
python run_capsuleguard.py --attack-mode trusted_source_compromise --trials 5 --repetitions 20 --noise-memories 12
python run_capsuleguard.py --attack-mode multimodal --trials 3 --repetitions 6 --noise-memories 6
python run_capsuleguard.py --attack-mode attacker_generated --trials 3 --repetitions 4 --noise-memories 6
python run_capsuleguard.py --attack-mode utility --trials 5 --repetitions 12 --noise-memories 12
```

Use them when you want to isolate one attack family instead of running the full suite.

## 8. Complete Benchmark With Live LLM Planner

This command runs the symbolic workflow-corpus benchmark and the live LLM planner benchmark from one entry point:

```powershell
python run_capsuleguard.py --attack-mode workflow_corpus --workflow-corpus data\workflow_corpus_splits\test.jsonl --trials 5 --repetitions 4 --noise-memories 4 --seed 2026 --summary-csv results\complete_workflow_corpus_summary.csv --trace-jsonl results\complete_workflow_corpus_traces.jsonl --breakdown-csv results\complete_workflow_corpus_breakdown.csv --gap-closure-csv results\complete_workflow_corpus_gap_closure.csv --tool-trace-csv results\complete_workflow_corpus_tool_traces.csv --charts-dir results\complete_workflow_corpus_charts --include-llm-planner --llm-provider ollama --llm-models llama3,mistral,phi3 --llm-case-source workflow-corpus --llm-workflow-corpus data\workflow_corpus_splits\test.jsonl --llm-case-limit 36 --llm-case-seed 2026 --llm-repetitions 1 --llm-output-csv results\complete_medium_live_llm_planner_suite.csv --llm-summary-csv results\complete_medium_live_llm_planner_summary.csv --llm-model-summary-csv results\complete_medium_live_llm_planner_model_summary.csv --llm-gap-report-csv results\complete_medium_live_llm_planner_gap_report.csv
```

The LLM section checks whether real models are tempted by poisoned memory and whether the final capsule authorization layer blocks the unsafe plan.

Important LLM fields:

```text
planner_attack_success = the LLM chose the attacker target before authorization
attack_success         = the poisoned LLM plan survived final authorization
raw_parse_error_rate   = the first model output failed the planner schema
parse_error_rate       = the final planner parse failed after repair
```

Current medium live LLM result to preserve:

```text
ambient_prompt ASR: 22.22%
capsule_filtered_prompt planner tempted: 2.78%
capsule_filtered_prompt final ASR: 0.00%
capsule_filtered_prompt risky action: 0.00%
raw_parse_error_rate: 0.00%
final parse_error_rate: 0.00%
```

## 9. High-Cost Conference-Grade LLM Evaluation

Fast local smoke for the high-cost machinery:

```powershell
python run_llm_experiment.py --provider local --models poison_follower,strict_safe,malformed,jailbreak_prone,poison_follower_alt --case-source high-cost --high-cost-attack-modes generated_holdout,adaptive_loop,advanced_attack_suite --high-cost-seeds 2026,2027 --high-cost-cases-per-mode-seed 3 --high-cost-noise-memories 2 --repetitions 1 --output-csv results\high_cost_local_smoke_suite.csv --summary-csv results\high_cost_local_smoke_summary.csv --model-summary-csv results\high_cost_local_smoke_model_summary.csv --audit-jsonl results\high_cost_local_smoke_audit.jsonl --statistics-csv results\high_cost_local_smoke_statistics.csv
```

Five-model Ollama run with 300 high-cost cases and 3,000 live planner rows:

```powershell
python run_llm_experiment.py --provider ollama --models llama3,mistral,phi3,cydonia-chat,cydonia-lysandra --case-source high-cost --high-cost-attack-modes workflow_corpus,generated_holdout,adaptive_loop,advanced_attack_suite,attacker_generated --high-cost-seeds 2026,2027,2028 --high-cost-cases-per-mode-seed 20 --high-cost-noise-memories 4 --repetitions 1 --output-csv results\high_cost_live_llm_suite.csv --summary-csv results\high_cost_live_llm_summary.csv --model-summary-csv results\high_cost_live_llm_model_summary.csv --audit-jsonl results\high_cost_live_llm_audit.jsonl --statistics-csv results\high_cost_live_llm_statistics.csv
```

Paid API or OpenAI-compatible run:

```powershell
$env:CAPSULE_LLM_ENDPOINT="https://api.example.test/v1/chat/completions"
$env:CAPSULE_LLM_API_KEY="your_api_key_here"
python run_llm_experiment.py --provider openai-compatible --endpoint $env:CAPSULE_LLM_ENDPOINT --api-key-env CAPSULE_LLM_API_KEY --models paid-model-a,paid-model-b,paid-model-c,paid-model-d,paid-model-e --case-source high-cost --high-cost-attack-modes workflow_corpus,generated_holdout,adaptive_loop,advanced_attack_suite,attacker_generated --high-cost-seeds 2026,2027,2028 --high-cost-cases-per-mode-seed 20 --output-csv results\high_cost_paid_llm_suite.csv --summary-csv results\high_cost_paid_llm_summary.csv --model-summary-csv results\high_cost_paid_llm_model_summary.csv --audit-jsonl results\high_cost_paid_llm_audit.jsonl --statistics-csv results\high_cost_paid_llm_statistics.csv
```

Increase this value when you want a larger study:

```text
--high-cost-cases-per-mode-seed
```

For example, `67` gives roughly 1,005 cases and 10,050 live planner rows across five models.

## 10. Result Files To Keep

Keep these files when preparing the paper evidence folder:

```text
results\workflow_corpus_summary.csv
results\workflow_corpus_breakdown.csv
results\workflow_corpus_test_split_summary.csv
results\workflow_corpus_test_split_breakdown.csv
results\adaptive_loop_summary.csv
results\adaptive_loop_breakdown.csv
results\advanced_attack_suite_summary.csv
results\advanced_attack_suite_breakdown.csv
results\gap_fix_medium_live_llm_summary.csv
results\gap_fix_medium_live_llm_model_summary.csv
results\gap_fix_medium_live_llm_gap_report.csv
results\complete_medium_live_llm_planner_summary.csv
results\complete_medium_live_llm_planner_model_summary.csv
results\complete_medium_live_llm_planner_gap_report.csv
results\high_cost_local_smoke_summary.csv
results\high_cost_local_smoke_statistics.csv
```

If a run creates both `.csv` and `.jsonl`, keep both. The CSV gives the table numbers; the JSONL gives the audit trail behind them.

## 11. How To Read The Numbers

Use these meanings consistently in the paper:

```text
ASR             = Attack Success Rate
Risky Action    = unauthorized risky action rate
Benign Accuracy = normal usefulness retained
FPR             = benign tasks wrongly blocked
Planner Tempted = the LLM initially selected the poisoned target
Parse Error     = the planner output could not be parsed into the expected schema
```

The strongest fair claim is:

```text
CapsuleGuard blocks the tested workflow-corpus, adaptive-loop, advanced-suite, generated, and live-LLM poisoning benchmarks while preserving benign utility in this sandbox.
```

Do not claim:

```text
CapsuleGuard solves all agent memory poisoning.
```

That claim is too broad for the current evidence. The honest paper position is stronger: the prototype shows a measurable defense against persistent memory poisoning under a clearly defined threat model, with live LLM checks added as realism evidence.

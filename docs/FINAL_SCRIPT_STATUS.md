# Final Script Status

## Final Entry Point

The prototype now has one clear top-level runner:

```text
run_capsuleguard.py
```

Run it from the project folder:

```powershell
python run_capsuleguard.py
```

Equivalent module command:

```powershell
python -m experiments.run_capsule_sandbox
```

## What The Final Runner Does

The runner combines the full CapsuleGuard experiment pipeline:

```text
generate scenarios
-> add noisy benign memory distractors
-> run baselines
-> run full CapsuleGuard
-> run ablations
-> calculate metrics
-> aggregate repeated trials
-> print result table
-> export trial CSV, summary CSV, trace JSONL, and charts
```

## Included Agents

The final runner compares:

1. `ambient_memory`
2. `keyword_filter`
3. `provenance_only`
4. `intent_capsules`
5. `ablation_no_topic_scope`
6. `ablation_no_denied_actions`
7. `ablation_no_quorum`

## Output

Default outputs:

```text
results/capsule_sandbox_results.csv
results/capsule_sandbox_summary.csv
results/capsule_sandbox_traces.jsonl
results/capsule_gap_closure.csv
results/charts/
```

Custom run:

```powershell
python run_capsuleguard.py --attack-mode insane --trials 10 --repetitions 20 --noise-memories 25 --csv results/run20.csv
```

## Current Readiness

The script is ready as a **publication-oriented sandbox evidence runner**.

The current moderate benchmark is tuned so the weak ambient-memory baseline reaches about 20% attack success while CapsuleGuard remains at 0% attack success in the seeded run.

It is still not a real-world deployment benchmark because future work should add:

1. more legitimate-source poison cases,
2. derived-memory inheritance experiments,
3. larger trial counts,
4. memory-density stress curves,
5. optional LLM-backed planner comparison.

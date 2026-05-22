# Intent-Bound Memory Capsules

This is a from-scratch defensive research prototype for agent-memory poisoning.

The working idea is:

> Agent poisoning succeeds when stored memories have ambient authority over future tasks. Intent-Bound Memory Capsules remove that ambient authority by giving each memory a limited-use contract.

This prototype uses a fresh research claim, fresh terminology, fresh architecture, and a separate implementation path.

## Research Claim

Long-term memories should not be treated as free-form context. Each memory should be compiled into a capsule with:

1. allowed task intents,
2. source authority,
3. influence budget,
4. denied risky actions,
5. verification status,
6. topic scope.

At decision time, the agent may only use capsules whose contracts match the current user intent. Risky actions require independent capsule support instead of a single retrieved memory.

## Current Scope

In scope:

1. Text-only synthetic sandbox.
2. Memory capsule schema.
3. Capsule compiler.
4. Intent parser.
5. Capability-style memory eligibility checks.
6. Evidence quorum for risky actions.
7. Baseline and ablation agent comparison.
8. Generated scenario suite.
9. CSV result export.
10. Latency-aware experiment metrics and unit tests.
11. SQLite-backed persistent vector retrieval prototype.
12. LLM prompt-isolation experiment runner.
13. Benchmark-integrated tool action traces.
14. Sensitivity sweep CSV and chart outputs.
15. OpenAI-compatible and Ollama-compatible LLM provider hooks.
16. Pluggable external vector backend interface.
17. Independent attacker-generated scenario mode.
18. Multimodal/OCR-style poisoning scenario mode.
19. Multi-session memory persistence harness.
20. Safer fake tool environment with side-effect records.

Planned for Future Release:

1. Real attacks.
2. Real tool execution.
3. Real account/browser/email automation.
4. Real multimodal model/OCR execution.
5. Multi-agent memory sharing.
6. Completed live external LLM benchmark runs.
7. Production FAISS/Chroma/LanceDB deployment.
8. Real image parsing/OCR models.
9. Real browser/email/account side effects.

## Why This Is Original Enough For Your Paper

Prior papers usually focus on detecting suspicious memory content, provenance, retrieval poisoning, or memory influence. This prototype frames the core problem differently:

> Persistent poisoning is an ambient-authority failure.

The defense is based on least privilege:

> A memory can only influence the class of tasks it was authorized to support.

## Run

From this folder:

```powershell
python run_capsuleguard.py
python -m unittest discover -s tests
```

`python run_capsuleguard.py` defaults to `--attack-mode adaptive_loop`. It prints a short definition block before the metrics table explaining the hard-coded benchmark and each adaptive mutation stage.

Useful options:

```powershell
python run_capsuleguard.py --trials 10 --repetitions 20 --noise-memories 25 --csv results/run20.csv
python run_capsuleguard.py --attack-mode moderate --trials 5 --repetitions 12 --noise-memories 10
python run_capsuleguard.py --attack-mode insane --trials 5 --repetitions 12 --noise-memories 10
python run_capsuleguard.py --attack-mode extreme --trials 5 --repetitions 12 --noise-memories 12
python run_capsuleguard.py --attack-mode holdout --trials 5 --repetitions 12 --noise-memories 12
python run_capsuleguard.py --attack-mode generated_holdout --trials 5 --repetitions 12 --noise-memories 12
python run_capsuleguard.py --attack-mode adaptive_loop --trials 5 --repetitions 8 --noise-memories 8
python run_capsuleguard.py --attack-mode utility --trials 5 --repetitions 12 --noise-memories 12
python run_capsuleguard.py --attack-mode multimodal --trials 3 --repetitions 6 --noise-memories 6
python run_capsuleguard.py --attack-mode attacker_generated --trials 3 --repetitions 4 --noise-memories 6
python run_capsuleguard.py --no-ablations
python run_sensitivity.py --attack-mode generated_holdout
python run_llm_experiment.py --provider local
python run_llm_experiment.py --provider ollama --endpoint http://localhost:11434/api/generate --model llama3.1
```

The default run writes:

```text
results/capsule_sandbox_results.csv
results/capsule_sandbox_summary.csv
results/capsule_sandbox_traces.jsonl
results/capsule_attack_breakdown.csv
results/capsule_gap_closure.csv
results/capsule_tool_traces.csv
results/charts/
```

## Current Agents Compared

1. `ambient_memory`
2. `keyword_filter`
3. `quarantine_only`
4. `trust_score_retrieval`
5. `output_moderation`
6. `counterfactual_memory`
7. `provenance_only`
8. `intent_capsules`
9. `ablation_no_topic_scope`
10. `ablation_no_denied_actions`
11. `ablation_no_quorum`

See [docs/ADDED_FEATURES.md](docs/ADDED_FEATURES.md) for the current feature log.

See [docs/ORIGINALITY_AND_CODE_WALKTHROUGH.md](docs/ORIGINALITY_AND_CODE_WALKTHROUGH.md) for the originality note and code walkthrough.

See [docs/RESEARCH_LEVEL_CAPSULEGUARD_IMPROVISATION.md](docs/RESEARCH_LEVEL_CAPSULEGUARD_IMPROVISATION.md) for the upgraded research-level design and experiment plan.

See [docs/MEMORY_TRUST_AND_AUTHORIZATION_RULESET.md](docs/MEMORY_TRUST_AND_AUTHORIZATION_RULESET.md) for the formal memory trust and authorization rules.

See [docs/FINAL_SCRIPT_STATUS.md](docs/FINAL_SCRIPT_STATUS.md) for the final runner status.

See [docs/PUBLICATION_GRADE_EVIDENCE_MODE.md](docs/PUBLICATION_GRADE_EVIDENCE_MODE.md) for the publication-oriented evidence outputs.

See [docs/INSANE_MODE_SOLUTION_PROOF.md](docs/INSANE_MODE_SOLUTION_PROOF.md) for the high-pressure poisoning results and per-attack-type evidence.

See [docs/GAP_CLOSURE_REPORT.md](docs/GAP_CLOSURE_REPORT.md) for the baseline-failure-to-defense-rule matrix.

See [docs/TERMS_GAP_AND_POISONING_TEST_PLAN.md](docs/TERMS_GAP_AND_POISONING_TEST_PLAN.md) for plain-language term definitions, the fixed gap statement, and the increasing attack-vector test plan.

See [docs/CONFERENCE_READINESS_UPGRADE.md](docs/CONFERENCE_READINESS_UPGRADE.md) for the latest conference-readiness upgrade notes.

See [docs/CODE_GAPS_AND_RESEARCH_ROADMAP.md](docs/CODE_GAPS_AND_RESEARCH_ROADMAP.md) for the current critique of code limitations and the next research upgrades.

See [docs/INDUSTRIAL_GRADE_GAP_CLOSURE.md](docs/INDUSTRIAL_GRADE_GAP_CLOSURE.md) for the latest gap-closing implementation batch.

See [docs/REAL_WORLD_READINESS_QUEUE.md](docs/REAL_WORLD_READINESS_QUEUE.md) for the active real-world readiness queue and latest generated-holdout results.

See [docs/TESTING_GUIDE_AND_FACTOR_MATRIX.md](docs/TESTING_GUIDE_AND_FACTOR_MATRIX.md) for the testing workflow, benchmark ladder, and factors to vary during experiments.

See [paper/CAPSULEGUARD_CONFERENCE_DRAFT.md](paper/CAPSULEGUARD_CONFERENCE_DRAFT.md) for the current paper draft.

See [paper/REPRODUCIBILITY_CHECKLIST.md](paper/REPRODUCIBILITY_CHECKLIST.md) for the commands and expected outputs used in the draft.

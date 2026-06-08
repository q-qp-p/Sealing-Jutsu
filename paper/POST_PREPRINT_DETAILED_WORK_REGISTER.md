# Post-Preprint Detailed Work Register

This document is a detailed register of what happened after the printed preprint paper was created. It expands the shorter scope analysis and records the actual work done across paper writing, code changes, experiments, evidence generation, formatting, reproducibility, and submission preparation.

The goal is to preserve enough detail that the work can later be used for:

- research-paper revision
- reviewer response
- thesis/project report writing
- artifact evaluation notes
- reproducibility documentation
- future paper submission planning

## 1. Source Preprint

The printed preprint discussed in the chat was:

`C:\Users\User\Downloads\Sealing_Jutsu (1).pdf`

The preprint title was:

> Intent-Bound Memory Authorization Against Persistent Agent Poisoning

The preprint already had the core idea:

> LLM-agent memory poisoning is not only a malicious-content problem; it is an authority-control problem.

The preprint already included:

- abstract
- introduction
- background
- related work
- threat model
- CapsuleGuard design
- prototype implementation
- evaluation methodology
- held-out workflow-corpus results
- stress-suite results
- ablation results
- limitations
- conclusion
- references

The preprint was a strong foundation, but it did not yet include the full set of later results and framing improvements.

## 2. Main Post-Preprint Goal

After the preprint, the goal changed from:

> write a paper about the prototype

to:

> produce a reviewer-safe research paper that clearly explains why intent-bound memory authorization is different from output moderation, provenance, keyword filtering, and trust-score retrieval.

The biggest conceptual improvement was:

> ASR alone is not enough. A defense can block the final action while still allowing poisoned memory to steer the planner.

That led to the new metric:

> poison influence rate

## 3. High-Level Summary of Post-Preprint Work

The major post-preprint work can be grouped into twelve buckets:

1. Added poison influence rate.
2. Re-ran benchmarks with influence measurement.
3. Fixed the output-moderation comparison gap.
4. Added converted AgentDojo/InjecAgent trace results.
5. Added formal threat model.
6. Added live LLM planner results.
7. Added threshold calibration evidence.
8. Wrote the v3 research paper.
9. Generated DOCX, Markdown, and PDF versions.
10. Wrote preprint-to-final-paper logs.
11. Wrote IEEE-style version.
12. Added scope analysis and project documentation.

## 4. Commit-Level Timeline

The important post-preprint commits are:

| Commit | Purpose | Scope |
|---|---|---|
| `f359bbb` | Fixed scoring for external action-hijack traces. | Code/evaluation |
| `2c692d1` | Exposed output-moderation lifecycle gap. | Benchmark |
| `3ccd1ec` | Hardened lifecycle gap baselines. | Benchmark |
| `88ee558` | Added poison influence rate metric and converted corpus report. | Code/evidence |
| `de3e246` | Added formal threat model to paper. | Paper |
| `95c79c8` | Added updated v3 research paper draft. | Paper |
| `4e2be27` | Added generated PDF draft and binary safeguards. | Paper packaging |
| `787347a` | Recorded preprint-to-final research-paper process. | Documentation |
| `9d236df` | Added explicit post-preprint work summary. | Documentation |
| `82cf51a` | Added IEEE-style paper draft. | Submission formatting |
| `aa73eb6` | Added post-preprint scope analysis. | Documentation |

These commits show the project moved beyond a simple preprint rewrite. The work included metric design, evaluation updates, artifact generation, and scope control.

## 5. Work Bucket 1: Poison Influence Rate

### What Was Added

The new metric `poison_influence_rate` was added to distinguish memory compromise from final attack success.

The metric asks:

> Did poisoned memory reach the planner and cause the planner to select the attacker target before final output blocking?

### Why It Was Needed

Before this metric, output moderation could look too good.

For example:

- output moderation can block a dangerous final action
- semantic output judging can also block a dangerous final action
- both can show 0.00% ASR

But those defenses may still allow poisoned memory to influence the planner.

That would mean:

- the final response is blocked
- but the agent's internal plan was still compromised
- poisoned memory still gained planning authority

The metric fixed this measurement gap.

### Where It Was Implemented

The work touched the evaluation/metrics layer:

- `capsule_guard/metrics.py`
- `capsule_guard/evaluation.py`
- `experiments/run_capsule_sandbox.py`
- `tests/test_workflow_corpus.py`

### What Changed Conceptually

Before:

> Did the attack survive final action gating?

After:

> Did the attack influence planning before final action gating?

This made the research claim much stronger because it allowed the project to compare:

- late blocking defenses
- pre-planning authorization defenses

### Scope Decision

This is fully in scope for the research paper.

It is one of the strongest post-preprint contributions.

## 6. Work Bucket 2: Output-Moderation Comparison Fix

### Problem

The converted trace results initially created a reviewer problem:

| Defense | ASR |
|---|---:|
| output_moderation | 0.00% |
| semantic_output_judge | 0.00% |
| intent_capsules | 0.00% |

A reviewer could ask:

> If output moderation already gets 0% ASR, why do we need CapsuleGuard?

### Fix

The answer was not to weaken output moderation. The answer was to measure the right security property.

The project added poison influence rate to show:

| Defense | Final ASR | Poison influence |
|---|---:|---:|
| output_moderation | 0.00% | high |
| semantic_output_judge | 0.00% | high |
| intent_capsules | 0.00% | 0.00% |

### Interpretation

Output moderation:

1. poison memory exists
2. poison memory reaches planner
3. planner selects attacker target
4. final output/action gets blocked

Intent capsules:

1. poison memory exists
2. authorization gate checks capsule contract
3. poison memory is denied influence
4. planner does not select attacker target from poisoned memory

### Scope Decision

This is fully in scope for the research paper.

This is the most important reviewer-facing argument.

## 7. Work Bucket 3: Converted AgentDojo/InjecAgent Evidence

### What Was Added

Converted external-style trace corpora were evaluated:

- AgentDojo all
- InjecAgent all
- InjecAgent DH
- InjecAgent DS

### Validation Counts

| Corpus | Total | Poisoned | Benign |
|---|---:|---:|---:|
| AgentDojo all | 62 | 31 | 31 |
| InjecAgent all | 2108 | 1054 | 1054 |
| InjecAgent DH | 1020 | 510 | 510 |
| InjecAgent DS | 1088 | 544 | 544 |

### Key Results

| Corpus | Output-mod ASR | Output-mod influence | Capsule ASR | Capsule influence | Capsule sealing |
|---|---:|---:|---:|---:|---:|
| AgentDojo all | 0.00% | 80.65% | 0.00% | 0.00% | 83.87% |
| InjecAgent all | 0.00% | 61.29% | 0.00% | 0.00% | 61.48% |
| InjecAgent DH | 0.00% | 30.00% | 0.00% | 0.00% | 30.39% |
| InjecAgent DS | 0.00% | 90.62% | 0.00% | 0.00% | 90.62% |

### Why This Matters

This evidence shows:

- output moderation can look perfect under ASR
- but still allow poisoned planner influence
- intent capsules stop both final attack success and planner influence

### Files Produced

Important files include:

- `results/converted_corpus_report.md`
- `results/converted_agentdojo_all_summary.csv`
- `results/converted_injecagent_all_summary.csv`
- `results/converted_injecagent_dh_summary.csv`
- `results/converted_injecagent_ds_summary.csv`
- `results/converted_agentdojo_all_breakdown.csv`
- `results/converted_injecagent_all_breakdown.csv`
- `results/converted_injecagent_dh_breakdown.csv`
- `results/converted_injecagent_ds_breakdown.csv`

### Scope Decision

This is in scope for the research paper.

However, it must be framed carefully:

Safe:

> converted external trace-corpus evaluation

Unsafe:

> direct real-world deployment benchmark

## 8. Work Bucket 4: Memory Lifecycle Gap Benchmark

### Purpose

The memory lifecycle gap benchmark was created to show that output moderation is not enough when the malicious influence is not simply a visible dangerous final action.

### Key Result

| Agent | ASR | Risky action | Poison influence | Benign accuracy |
|---|---:|---:|---:|---:|
| output_moderation | 34.05% | 23.83% | 34.05% | 100.00% |
| semantic_output_judge | 13.10% | 9.17% | 34.05% | 100.00% |
| ablation_no_denied_actions | 0.00% | 0.00% | 57.14% | 100.00% |
| intent_capsules | 0.00% | 0.00% | 0.00% | 100.00% |

### Why It Matters

This benchmark showed two subtle things:

1. Output moderation can fail when the malicious effect is indirect.
2. A defense can hide ASR while still allowing poisoned influence.

The `ablation_no_denied_actions` result is especially important:

- final ASR is 0.00%
- risky action is 0.00%
- poison influence is 57.14%

That proves the paper should not rely on ASR alone.

### Files Produced

Important files include:

- `results/memory_lifecycle_gap_summary.csv`
- `results/memory_lifecycle_gap.csv`
- `results/memory_lifecycle_gap_breakdown.csv`
- `results/memory_lifecycle_gap_gap.csv`
- `results/memory_lifecycle_gap_charts/poison_influence_rate.svg`

### Scope Decision

This is in scope for the research paper.

It supports the argument that final-output defenses are late-stage controls, not memory authorization.

## 9. Work Bucket 5: Formal Threat Model

### What Was Added

The threat model was expanded from a brief section into a formal security framing.

It now includes:

- protected assets
- attacker capabilities
- attacker limits
- trust boundaries
- assumptions
- security objectives
- STRIDE mapping
- OWASP LLM mapping

### Attacker Capabilities

In scope:

- inject text through web pages
- inject text through tool outputs
- inject OCR-visible text
- inject alt text
- influence summaries
- influence experience logs
- use memory import paths
- use delayed triggers
- use cross-session poison
- paraphrase malicious instructions
- split payloads
- craft retrieval-collision phrasing
- try to alter recommendations, planning paths, preferences, or risky actions

Out of scope:

- modifying policy code
- modifying the capsule gate
- forging cryptographic provenance
- forging verified writer identity
- compromising tool runtime
- compromising OCR binary
- compromising model weights
- deleting audit logs

### Trust Boundary

The key trust boundary is:

> retrieved memory as relevance evidence versus retrieved memory as authority

### OWASP LLM Mapping

The paper maps the threat model to:

- LLM01 Prompt Injection
- LLM04 Data and Model Poisoning
- LLM06 Excessive Agency
- LLM08 Vector and Embedding Weaknesses
- MCP-style tool poisoning

### Scope Decision

This is fully in scope for the paper.

It is necessary for reviewer safety.

## 10. Work Bucket 6: Live LLM Planner Evidence

### What Was Added

The project added live local LLM planner evidence as a realism check.

Models included:

- llama3
- mistral
- phi3

### Medium Live LLM Result

| Condition | Rows | Planner tempted | Final ASR | Risky action | Raw parse error |
|---|---:|---:|---:|---:|---:|
| ambient_prompt | 108 | 22.22% | 22.22% | 22.22% | 0.00% |
| capsule_filtered_prompt | 108 | 2.78% | 0.00% | 0.00% | 0.00% |

### Defended Result by Model

| Model | Rows | Planner tempted | Final ASR | Risky action | Raw parse error |
|---|---:|---:|---:|---:|---:|
| llama3 | 36 | 2.78% | 0.00% | 0.00% | 0.00% |
| mistral | 36 | 2.78% | 0.00% | 0.00% | 0.00% |
| phi3 | 36 | 2.78% | 0.00% | 0.00% | 0.00% |

### Why It Matters

The preprint leaned more heavily on deterministic planner evaluation.

The live LLM work shows:

- actual local models can be tempted by poisoned memory
- capsule-filtered authorization blocks final attack success
- parser failures were not driving the result

### Scope Decision

This is in scope for the paper, but with careful wording.

Safe:

> live local LLM planner realism check

Unsafe:

> large-scale frontier-model validation

## 11. Work Bucket 7: LLM Parser Cleanup

### Problem

Earlier live LLM experiments had high raw parse error rates.

This could make reviewers ask:

> Is the defense working, or are model outputs simply malformed?

### Fix

The LLM planner flow was improved so the reported medium live LLM result had:

- 0.00% raw parse error
- 100.00% first-pass valid planner rate
- 0.00% final parse error

### Scope Decision

This is in scope for the artifact and methods discussion.

It should not be overemphasized as a research contribution.

## 12. Work Bucket 8: Threshold Calibration

### What Was Added

A 16-point sweep varied:

- medium-risk quorum threshold
- topic-scope threshold

### Result

Across the current-main simulator sweep:

- ASR: 0.00%
- risky action: 0.00%
- benign accuracy: 100.00%
- FPR: 0.00%

### Why It Matters

This helps address the criticism:

> The policy thresholds are hand-tuned.

The calibration does not fully solve production calibration, but it shows the prototype can run threshold sweeps and report calibration metrics.

### Scope Decision

In scope, but carefully framed.

Safe:

> prototype-level threshold sweep

Unsafe:

> production-calibrated policy

## 13. Work Bucket 9: Updated README and Narrative

### What Changed

The README was updated to explain:

- poison influence rate
- output moderation versus memory authorization
- converted external corpus readout
- why ASR alone is insufficient

### Scope Decision

This is repository documentation, not a paper contribution.

The ideas are in scope for the paper, but the README edit itself is not.

## 14. Work Bucket 10: v3 Research Paper

### What Was Created

The new v3 paper was written after analyzing the printed preprint and the latest project evidence.

Files:

- `paper/Sealing_Jutsu_Research_Paper_v3.md`
- `paper/Sealing_Jutsu_Research_Paper_v3.docx`
- `paper/Sealing_Jutsu_Research_Paper_v3.pdf`
- `paper/build_research_paper_v3.py`

### What Improved Compared to the Preprint

The v3 paper added:

- stronger abstract
- clearer thesis
- formal threat model
- poison influence rate
- AgentDojo/InjecAgent converted trace evidence
- lifecycle-gap evidence
- live LLM planner evidence
- threshold calibration note
- cleaner limitations
- stronger discussion of output moderation
- reproducible paper builder

### Scope Decision

The paper itself is in scope as a final research artifact.

The builder is reproducibility infrastructure, not a research claim.

## 15. Work Bucket 11: PDF Generation

### Problem

The normal DOCX rendering workflow failed because:

- LibreOffice was not installed
- Word COM was not available
- the standard DOCX-to-PDF renderer could not run

### Fix

The builder was upgraded to generate PDF directly using `reportlab`.

Validation:

- PDF had valid metadata
- PDF had 9 pages
- PDF was readable with `pypdf`

### Files

- `paper/Sealing_Jutsu_Research_Paper_v3.pdf`

### Scope Decision

This is deliverable packaging.

It is not research content.

## 16. Work Bucket 12: Git Binary Safeguards

### What Was Added

`.gitattributes` was added with binary handling for:

- `.docx`
- `.pdf`
- `.png`
- `.jpg`
- `.jpeg`

### Why It Matters

This prevents generated paper artifacts from being corrupted by line-ending conversion.

### Scope Decision

This is repository hygiene.

It should not be included in the paper body.

## 17. Work Bucket 13: Preprint-to-Final Research Log

### What Was Created

The following file was created:

- `paper/PAPER_PREPRINT_TO_FINAL_RESEARCH_LOG.md`

### Purpose

It records:

- how the idea evolved
- what the preprint contained
- what gaps were found
- what evidence was added
- what papers/artifacts were created
- what remains pending before submission

### Scope Decision

This is project documentation.

It should not be included in the research paper body.

## 18. Work Bucket 14: Explicit Post-Preprint Summary

### What Was Added

The research log was expanded with:

> Section 5.1 Work Completed After the Preprint

This section listed:

- formal threat model
- poison influence rate
- benchmark reruns
- output moderation comparison fix
- AgentDojo/InjecAgent evidence
- lifecycle-gap benchmark
- live LLM planner evidence
- LLM parser cleanup
- threshold calibration
- README/paper narrative updates
- v3 paper
- PDF generation
- `.gitattributes`
- reproducible builder

### Scope Decision

This belongs in project documentation.

It should not be copied into the research paper because papers should present final contributions, not chat/process chronology.

## 19. Work Bucket 15: IEEE-Style Paper

### What Was Created

A separate IEEE-style paper version was created.

Files:

- `paper/Sealing_Jutsu_IEEE_Style_Paper.md`
- `paper/Sealing_Jutsu_IEEE_Style_Paper.docx`
- `paper/Sealing_Jutsu_IEEE_Style_Paper.pdf`
- `paper/Sealing_Jutsu_IEEE_Style_Paper.tex`
- `paper/build_ieee_style_paper.py`

### Why It Was Created

The v3 paper is a general research-paper draft.

The IEEE-style paper is a more compact conference-style version with:

- IEEE-like title/author block
- compact abstract
- Index Terms
- Roman-numbered sections
- table captions in IEEE style
- numbered references
- `IEEEtran` LaTeX source

### Validation

The IEEE PDF was checked:

- 6 pages
- valid PDF metadata
- key terms present
- core result tables present

The `.tex` file was generated with:

`\\documentclass[conference]{IEEEtran}`

Local LaTeX was not installed, so the `.tex` file was not compiled locally.

### Scope Decision

This is submission-format preparation.

It is not new scientific evidence.

## 20. Work Bucket 16: Post-Preprint Scope Analysis

### What Was Created

Files:

- `paper/POST_PREPRINT_SCOPE_ANALYSIS.md`
- `paper/POST_PREPRINT_SCOPE_ANALYSIS.docx`

### Purpose

This document answered:

> Are the things we did after the preprint in scope for the paper?

It separated:

- research-paper content
- repository/project-log content
- submission-format content
- out-of-scope claims

### Scope Decision

This is project management and scope control.

It should not be included in the paper body.

## 21. What Is Actually In the Research Paper

The final v3 research paper includes the research-relevant post-preprint work:

| Item | Included in v3 paper? | Location/section |
|---|---:|---|
| formal threat model | Yes | Section 3 |
| poison influence rate | Yes | Evaluation Methodology and Results |
| output moderation comparison | Yes | Results and Discussion |
| AgentDojo/InjecAgent converted evidence | Yes | Results |
| lifecycle-gap benchmark | Yes | Results |
| live LLM planner results | Yes | Results |
| threshold calibration | Yes | Results |
| limitations | Yes | Limitations |
| PDF-generation notes | No | project log only |
| commit hashes | No | project log only |
| `.gitattributes` notes | No | project log only |
| local file paths | No | project log only |
| after-preprint chronology | No | project log only |

## 22. What Is Actually In the IEEE-Style Paper

The IEEE-style paper includes:

- concise abstract
- Index Terms
- introduction
- background and related work
- threat model
- intent-bound capsule design
- prototype
- evaluation methodology
- held-out workflow corpus
- lifecycle-gap result
- converted AgentDojo/InjecAgent result
- stress-suite result
- live LLM result
- discussion
- limitations
- conclusion
- references

It does not include:

- commit history
- PDF generation notes
- detailed process narrative
- local machine limitations
- Git hygiene notes

That is correct.

## 23. What Is Out of Scope for Research Claims

The following are out of scope as research claims:

1. PDF generation process.
2. DOCX rendering limitations.
3. Git binary safeguards.
4. Commit hashes.
5. Local file locations.
6. Chat-history chronology.
7. Claims that CapsuleGuard solves all memory poisoning.
8. Claims that converted traces are the same as deployed production traces.
9. Claims that local LLM evaluation is frontier-model validation.
10. Claims that threshold sweep equals production calibration.

## 24. What Is In Scope for Research Claims

The following are in scope:

1. Persistent memory poisoning is an authority-control problem.
2. Retrieval should not imply authorization.
3. Intent-bound capsules encode allowed influence.
4. Poison influence rate reveals planner compromise hidden by ASR.
5. Output moderation can block final actions while leaving poisoned influence intact.
6. Intent capsules reduce final ASR and poison influence in the tested benchmark.
7. Converted AgentDojo/InjecAgent traces show the distinction between output blocking and influence prevention.
8. Live local LLM planner results support the prototype beyond deterministic-only testing.
9. Threshold sweeps show prototype-level robustness across selected settings.
10. Limitations remain and should be stated honestly.

## 25. Safe Claim Set

Use these claims in the paper:

- Intent-bound memory capsules implement least-privilege memory authorization.
- Retrieval is treated as relevance, not authorization.
- Poison influence rate measures planner compromise before final output gating.
- In tested converted trace corpora, output moderation has 0.00% ASR but high poison influence.
- In tested converted trace corpora, intent capsules have 0.00% ASR and 0.00% poison influence.
- In the held-out workflow corpus, intent capsules preserve 100.00% benign accuracy with 0.00% ASR.
- In live local LLM planner experiments, capsule-filtered authorization reduces final ASR to 0.00%.
- The work is a research prototype, not a proof of universal security.

## 26. Unsafe Claim Set

Avoid these claims:

- CapsuleGuard solves all agent poisoning.
- CapsuleGuard is production-ready without further validation.
- Output moderation is useless.
- AgentDojo/InjecAgent converted traces are full real-world deployment traces.
- Local LLM tests prove frontier-model robustness.
- Threshold calibration is complete.
- Raw multimodal image poisoning is fully solved.
- The PDF/IEEE paper generation is research evidence.

## 27. Final Artifact Map

### Main research paper

- `paper/Sealing_Jutsu_Research_Paper_v3.md`
- `paper/Sealing_Jutsu_Research_Paper_v3.docx`
- `paper/Sealing_Jutsu_Research_Paper_v3.pdf`
- `paper/build_research_paper_v3.py`

### IEEE-style paper

- `paper/Sealing_Jutsu_IEEE_Style_Paper.md`
- `paper/Sealing_Jutsu_IEEE_Style_Paper.docx`
- `paper/Sealing_Jutsu_IEEE_Style_Paper.pdf`
- `paper/Sealing_Jutsu_IEEE_Style_Paper.tex`
- `paper/build_ieee_style_paper.py`

### Paper history and analysis

- `paper/PAPER_PREPRINT_TO_FINAL_RESEARCH_LOG.md`
- `paper/POST_PREPRINT_SCOPE_ANALYSIS.md`
- `paper/POST_PREPRINT_SCOPE_ANALYSIS.docx`
- `paper/POST_PREPRINT_DETAILED_WORK_REGISTER.md`

### Older paper draft

- `paper/Intent_Bound_Memory_Capsules_Submission_Draft_v2.md`
- `paper/Intent_Bound_Memory_Capsules_Submission_Draft_v2.docx`
- `paper/build_submission_draft_v2.py`
- `paper/paper_result_tables_v2.csv`

## 28. Evidence File Map

### Main workflow corpus

- `results/workflow_corpus_test_split_summary.csv`

### Lifecycle gap

- `results/memory_lifecycle_gap_summary.csv`
- `results/memory_lifecycle_gap.csv`
- `results/memory_lifecycle_gap_breakdown.csv`
- `results/memory_lifecycle_gap_gap.csv`

### Converted external corpora

- `results/converted_corpus_report.md`
- `results/converted_agentdojo_all_summary.csv`
- `results/converted_injecagent_all_summary.csv`
- `results/converted_injecagent_dh_summary.csv`
- `results/converted_injecagent_ds_summary.csv`

### Live LLM

- `results/gap_fix_medium_live_llm_summary.csv`
- `results/gap_fix_medium_live_llm_model_summary.csv`
- `results/llm_memory_lifecycle_gap_summary.csv`
- `results/llm_memory_lifecycle_gap_model_summary.csv`

### Calibration

- `results/current_main_threshold_calibration.csv`

### Stress suites

- `results/all_scenarios_generated_holdout_summary.csv`
- `results/advanced_attack_suite_summary.csv`
- `results/all_scenarios_attacker_generated_summary.csv`
- `results/all_scenarios_multimodal_summary.csv`
- `results/all_scenarios_trusted_source_compromise_summary.csv`

## 29. What the Expanded Story Should Say

The fuller story is:

1. We started with a preprint around intent-bound memory authorization.
2. The preprint had the basic idea and early evidence.
3. After the preprint, we found the biggest reviewer risk: output moderation could appear equally strong under ASR.
4. We added poison influence rate to measure planner compromise.
5. We re-ran and reported benchmark outputs with influence rate.
6. We added converted AgentDojo/InjecAgent trace evidence.
7. The converted results showed output moderation can have 0% ASR but high poison influence.
8. Intent capsules showed 0% ASR and 0% influence.
9. We added a lifecycle-gap benchmark showing late blocking is insufficient.
10. We formalized the threat model.
11. We added live local LLM planner results.
12. We cleaned up parser concerns.
13. We added threshold calibration evidence.
14. We rewrote the paper as a v3 research paper.
15. We generated PDF/DOCX/Markdown.
16. We created an IEEE-style version with `.tex`.
17. We wrote logs and scope-analysis documents to keep claims clean.

## 30. Final Scope Verdict

The short scope analysis was correct but too compressed.

The real post-preprint work was broader:

- code metrics were changed
- benchmark outputs were regenerated
- external converted traces were evaluated
- LLM planner evidence was added
- threat model was formalized
- papers were rewritten
- PDF and IEEE artifacts were generated
- logs and scope documents were created

However, only the research-relevant parts belong in the paper body.

The process and packaging work belongs in documentation.

The final papers correctly include:

- the research claims
- the metrics
- the evidence
- the threat model
- the limitations

The final papers correctly exclude:

- Git process details
- local path details
- PDF-generation mechanics
- after-preprint narrative

That is the cleanest and most reviewer-safe split.

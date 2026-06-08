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

## 31. What "100/100 Research Readiness" Means

The current project is strong enough to convert the preprint into a serious research paper, but a 100/100 readiness claim should be reserved for a version that can survive a hard reviewer who asks:

- Is the benchmark realistic enough?
- Does the defense still work against adaptive attackers?
- Does the result hold with real LLM planners, not only symbolic planning?
- Does the comparison separate memory compromise from output blocking?
- Can another researcher reproduce the result?
- Are limitations clearly stated rather than hidden?

For this project, "100/100" should not mean:

> The system solves all memory poisoning.

That would be too broad and not defensible.

It should mean:

> The paper has a precise threat model, a clearly novel defense mechanism, strong baselines, reproducible experiments, real or externally derived traces, live LLM validation, ablations, statistical reporting, and honest limitations.

That is the reviewer-safe definition of 100/100 readiness.

## 32. Current State Versus 100/100 Target

### Current state

The project currently has:

- a clear research problem
- a named and implemented defense
- strong symbolic benchmark evidence
- live local LLM planner evidence
- converted AgentDojo/InjecAgent trace evidence
- poison influence rate
- ablation results
- threat model
- multiple baselines
- generated paper drafts
- PDF/DOCX artifacts
- IEEE-style paper artifacts
- reproducibility instructions

This is enough for a serious research-paper draft.

### Remaining 100/100 gap

The remaining gap is not mostly writing. It is evidence depth.

The paper becomes much closer to 100/100 when the following are added:

1. Frontier-model validation.
2. Larger live LLM planner benchmark.
3. Real or externally collected redacted workflow traces.
4. Closed-loop adaptive attacker benchmark.
5. Raw image/OCR multimodal pipeline.
6. Statistical confidence reporting across seeds and task families.
7. Stronger artifact reproducibility package.
8. More explicit industrial deployment boundary.

## 33. 100/100 Upgrade Checklist

This checklist defines the work needed before the paper should claim full research readiness.

### Gate 1: Frontier-model validation

Status:

- Not complete.

Why it matters:

- Local Ollama models are useful for realism, but reviewers may ask whether the defense holds when stronger frontier planners are used.

What to add:

- Run the live LLM planner benchmark against at least one stronger hosted model.
- Keep the same attack cases and metrics.
- Report ASR, risky action rate, planner tempted rate, raw parse error rate, repaired parse error rate, and poison influence rate.

Acceptance target:

- CapsuleGuard / intent capsules should keep final ASR near 0%.
- Raw parse errors should be low or separately reported.
- Any nonzero failure should be traced and explained.

Paper-safe wording after completion:

> We validate the defense across symbolic planners, local LLM planners, and hosted LLM planners.

### Gate 2: Larger live LLM planner benchmark

Status:

- Partially complete.

Why it matters:

- The current live LLM suite is valuable, but it is still a realism check rather than the main statistical benchmark.

What to add:

- Increase live LLM cases across more task families.
- Run multiple seeds.
- Report per-model and aggregate results.
- Include malformed-output analysis.
- Include jailbreak-style planning prompts.

Acceptance target:

- At least several hundred live LLM planning decisions.
- Per-model table.
- Aggregate confidence intervals.
- Raw-output audit saved in results.

Paper-safe wording after completion:

> Live LLM evaluation confirms that the authorization layer remains effective when plans are generated by language models rather than a deterministic planner.

### Gate 3: Real or externally collected redacted traces

Status:

- Partially complete.

Why it matters:

- Converted external corpora are useful, but reviewers may still call them transformed benchmarks rather than native memory-poisoning traces.

What to add:

- Collect or import real redacted agent workflow traces.
- Include benign, poisoned, delayed-trigger, tool-output, and cross-session examples.
- Document trace source, schema, and redaction process.

Acceptance target:

- A separate results table for real/redacted traces.
- Family-level breakdown.
- Influence-rate comparison against output moderation and semantic judging.

Paper-safe wording after completion:

> We evaluate on synthetic stress cases, converted external attack corpora, and redacted workflow traces.

### Gate 4: Closed-loop adaptive attacker

Status:

- Not complete.

Why it matters:

- Current attack sets include strong generated and stress cases, but a reviewer may ask whether the attacker adapts after seeing why an attempt failed.

What to add:

- Implement an attacker loop that observes policy failure reasons.
- Mutate poisoning attempts across topic, source, writer, timing, and action fields.
- Track how many attempts are needed to bypass each defense.

Acceptance target:

- Report bypass rate, attempts-to-bypass, and dominant failure reasons.
- Show whether CapsuleGuard fails closed or leaks influence under mutation pressure.

Paper-safe wording after completion:

> We test adaptive attackers that use policy feedback to mutate poisoning attempts.

### Gate 5: Raw image/OCR multimodal pipeline

Status:

- Not complete.

Why it matters:

- OCR-style extracted text is not the same as testing actual image ingestion.

What to add:

- Add image files with visible, hidden, small-font, and alt-text-like poisoning content.
- Run them through an OCR/extraction step.
- Store extracted content as memory capsules with image provenance.
- Evaluate whether the defense blocks unauthorized influence.

Acceptance target:

- At least one real image/OCR benchmark table.
- Separate results for visible text, low-contrast text, dense text, and hidden-instruction style images.

Paper-safe wording after completion:

> We include a raw multimodal ingestion test where image-derived memories are treated as low-authority capsules unless independently verified.

### Gate 6: Statistical reporting

Status:

- Partially complete.

Why it matters:

- Single-seed or deterministic results can look too clean.

What to add:

- Run multiple seeds.
- Report confidence intervals.
- Report per-family variance.
- Include statistical comparison against strongest baselines.

Acceptance target:

- Tables include mean, standard deviation, and confidence intervals.
- The strongest baseline comparison remains meaningful.

Paper-safe wording after completion:

> Results are reported across multiple random seeds with confidence intervals.

### Gate 7: Artifact reproducibility

Status:

- Partially complete.

Why it matters:

- A strong paper needs a clean artifact story.

What to add:

- One-command benchmark runner.
- Frozen dependency file.
- Dataset-preparation script.
- Expected output checks.
- Docker or reproducible environment notes.

Acceptance target:

- A fresh machine can run the main benchmark and regenerate key tables.
- The README points to the exact commands and expected summaries.

Paper-safe wording after completion:

> We release code, benchmark runners, converted trace loaders, and expected-result summaries for reproducibility.

### Gate 8: Industrial deployment boundary

Status:

- Partially complete.

Why it matters:

- The project should not imply full production security without a deployment model.

What to add:

- Define where CapsuleGuard sits in an agent stack.
- Define expected inputs and outputs.
- Define trust assumptions around source labels, signing keys, tenant boundaries, logging, and policy updates.
- Explain what a production deployment still needs.

Acceptance target:

- Architecture diagram.
- Deployment assumptions.
- Operational limitations.
- Logging/audit requirements.

Paper-safe wording after completion:

> CapsuleGuard is evaluated as a memory-authorization layer; production deployment additionally requires secure source attestation, tenant isolation, logging, and operational key management.

## 34. Claim Ladder For The Final Paper

The final paper should use a claim ladder.

### Safe current claim

> CapsuleGuard reduces persistent memory-poisoning risk by requiring retrieved memories to be authorized for the user's current intent before they can influence planning or action.

This is already supported.

### Stronger claim after remaining evidence

> Across symbolic planners, local LLM planners, hosted LLM planners, stress suites, converted external corpora, and redacted workflow traces, CapsuleGuard consistently prevents unauthorized memory influence while preserving benign task accuracy.

This should be used only after the 100/100 evidence gates are complete.

### Claim to avoid

> CapsuleGuard solves all agent memory poisoning.

This should not be used.

It is too broad because:

- attackers can compromise trusted sources
- production source labels can be wrong
- raw multimodal extraction can fail
- frontier models may behave differently
- deployment mistakes can bypass policy
- the threat model does not include arbitrary code execution or system compromise

## 35. What To Change In The Research Paper To Make It Stronger

The paper body should be updated in these ways:

1. Move poison influence rate into the main evaluation section, not only an appendix.
2. Add a table separating action blocking from memory influence prevention.
3. Add the formal threat model before the system design.
4. Add the converted external-corpus results as a separate evaluation subsection.
5. Add the live LLM planner result as its own subsection.
6. Add a limitations subsection that explicitly names frontier-model, raw-multimodal, and real-trace limitations.
7. Add a "Responsible Claims" paragraph that states what the system does not solve.
8. Add a reproducibility paragraph that points to scripts, datasets, seeds, and result files.

This would make the paper read like a mature research artifact rather than only a prototype report.

## 36. Final 100/100 Readiness Verdict

The project is not honestly 100/100 yet if 100/100 means top-tier conference-grade evidence.

The project is close to a strong research-paper submission package because:

- the problem is clear
- the defense is original enough to argue
- the implementation exists
- the benchmarks are broad
- the strongest comparison gap has been identified
- poison influence rate fixes a major evaluation weakness
- the paper now has a threat model and safer claim language

The remaining improvement is mostly empirical:

- more real traces
- more live LLM scale
- frontier-model validation
- adaptive attacker evaluation
- raw multimodal ingestion
- confidence intervals
- stronger reproducibility package

Once those gates are complete, the paper can reasonably be positioned as close to 100/100 research readiness.

Until then, the best honest score is:

> Strong research paper draft: 85/100

> Conference-grade submission candidate after the gates above: 95-100/100

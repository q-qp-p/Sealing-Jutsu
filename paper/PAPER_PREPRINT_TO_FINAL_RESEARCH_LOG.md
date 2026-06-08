# Preprint to Final Research Paper Log

This note records what was done while turning the Sealing-Jutsu project into a preprint-style paper and then into the newer research-paper draft. It is meant to preserve the reasoning trail for future writing, submission, revision, or reviewer response work.

## 1. Starting Point

The project began as a research direction around persistent LLM-agent memory poisoning. The core problem we settled on was:

> LLM agents often treat retrieved memory as ordinary context. If a poisoned memory is stored today, it can be retrieved later and influence planning, recommendations, or tool actions without proving that it is authorized to do so.

The original defense framing was not copied from any single paper. We moved away from the earlier "MemShield" name and built the project around a new research contribution:

> Intent-bound memory authorization: every stored memory becomes a bounded capsule that must prove what it is allowed to influence before it can shape planning or action.

The implementation name in the repository is `CapsuleGuard`, inside the public project `Sealing-Jutsu`.

## 2. Research Claim That Emerged

The final claim became narrower and stronger:

> Persistent memory poisoning can be reduced by separating memory retrieval from memory authority. Retrieval should only mean a memory is relevant; it should not automatically mean the memory is allowed to influence a recommendation, plan, or tool action.

This became the central phrase of the paper:

> Retrieval is not authorization.

## 3. Code and Evidence Built Before the Paper

Before the paper was written, the prototype had already grown into a reproducible benchmark project.

Major implementation pieces:

- Capsule compiler for turning raw memories into authority-scoped capsules.
- Policy gate for topic scope, denied actions, authority floors, evidence quorum, lineage, freshness, and final plan authorization.
- Baseline agents:
  - ambient memory
  - keyword filter
  - quarantine-only
  - trust-score retrieval
  - provenance-only
  - output moderation
  - semantic output judge
  - counterfactual memory
  - intent capsules
- Safe tool simulator with action traces.
- Signed/append-only provenance support.
- Vector-style retrieval support.
- Workflow corpus loader and external trace-corpus importer.
- Live LLM planner harness for local models.
- Threshold calibration sweep.
- Attack suites for generated holdout, attacker-generated cases, multimodal/OCR-style attacks, lifecycle-gap attacks, trusted-source compromise, adaptive-style attacks, and advanced stress cases.

Important testing state:

- Unit test suite reached `163` passing tests.
- Main runner: `run_capsuleguard.py`.
- LLM runner: `run_llm_experiment.py`.
- Main paper-building scripts live in `paper/`.

## 4. First Preprint Paper

The printed/preprint paper provided by the user was:

`C:\Users\User\Downloads\Sealing_Jutsu (1).pdf`

That PDF was a 10-page draft titled:

> Intent-Bound Memory Authorization Against Persistent Agent Poisoning

It already contained:

- Abstract and introduction.
- Related work and prior defense gap table.
- Threat model section.
- CapsuleGuard design.
- Prototype implementation.
- Evaluation methodology.
- Results for held-out workflow corpus and stress suites.
- Limitations and conclusion.
- References.

The preprint was useful because it had the paper skeleton and the main narrative, but it did not fully reflect the newest project evidence.

## 5. Gaps Found in the Preprint

The preprint was strong, but several things were missing or underdeveloped relative to the latest work:

1. The newest `poison_influence_rate` metric was not central enough.
2. The converted AgentDojo/InjecAgent results were missing.
3. The paper did not clearly separate final output blocking from memory influence prevention.
4. The formal threat model needed more structure:
   - attacker capabilities
   - explicit limits
   - trust boundaries
   - assumptions
   - security objectives
   - STRIDE mapping
   - OWASP LLM mapping
5. The live LLM planner work needed to be included as a realism check.
6. The limitations needed to be more reviewer-safe and honest.
7. The paper needed a clearer answer to the reviewer question:

> Why do we need CapsuleGuard if output moderation can also show 0% ASR?

The answer became:

> Output moderation can block the final action while still allowing poisoned memory to influence the planner. Intent capsules aim to stop unauthorized memory influence before planning authority is granted.

## 5.1 Work Completed After the Preprint

After the printed preprint was created, we continued improving both the research evidence and the paper package. The most important post-preprint work was:

1. Formalized the threat model.
   - Added attacker capabilities and explicit attacker limits.
   - Defined protected assets.
   - Defined the trusted computing base.
   - Separated retrieved memory as relevance evidence from retrieved memory as authority.
   - Added STRIDE mapping.
   - Added OWASP LLM mapping.
   - Made the paper safer by clearly stating what is out of scope.

2. Added the `poison_influence_rate` metric.
   - This was the biggest research improvement after the preprint.
   - It measures whether poisoned memory reaches the planner and causes the planner to select the attacker target before final output blocking.
   - This made it possible to prove that output moderation and semantic judges are not equivalent to capsule authorization.

3. Re-ran benchmarks with poison influence reporting.
   - Updated benchmark tables to include `infl`.
   - Updated summary CSV files with `poison_influence_rate_mean`.
   - Updated breakdown CSV files with poison influence counts.
   - Added a dedicated poison-influence chart to result folders.

4. Fixed the output-moderation comparison problem.
   - Before this, output moderation could look as good as CapsuleGuard when ASR alone was measured.
   - After adding influence rate, the paper can show:
     - output moderation: 0.00% final ASR but high poison influence
     - intent capsules: 0.00% final ASR and 0.00% poison influence
   - This became one of the strongest paper arguments.

5. Added converted AgentDojo/InjecAgent evidence.
   - Converted external-style traces were evaluated with `trace_corpus`.
   - AgentDojo and InjecAgent splits were summarized.
   - The new evidence showed that output moderation can still allow 30.00%-90.62% poison influence.
   - Intent capsules stayed at 0.00% poison influence across those converted corpora.

6. Added a converted-corpus report.
   - File: `results/converted_corpus_report.md`
   - This report explains why output moderation is late blocking, while CapsuleGuard is pre-planning authorization.

7. Added and reported the memory lifecycle gap benchmark.
   - This benchmark shows cases where final output moderation does not fully close the problem.
   - It also shows that some ablations can hide final ASR while still allowing poisoned planning influence.

8. Added live LLM planner evidence to the paper.
   - The paper now includes the medium live LLM workflow-corpus run.
   - Models covered:
     - llama3
     - mistral
     - phi3
   - The live LLM result shows ambient prompt final ASR at 22.22% and capsule-filtered final ASR at 0.00%.

9. Fixed the LLM parser issue before reporting results.
   - Earlier live LLM tests had raw parse error concerns.
   - Later runs reached 0.00% raw parse error and 100.00% first-pass valid planner rate in the reported medium run.
   - This made the LLM result more defensible.

10. Added threshold calibration evidence.
    - A 16-point current-main sweep was run over medium-risk quorum and topic-scope thresholds.
    - The simulator reported 0.00% ASR, 0.00% risky action, 100.00% benign accuracy, and 0.00% FPR across the sweep.
    - The paper still honestly says this does not replace larger external calibration.

11. Updated the README and paper narrative.
    - README now explains influence rate.
    - README now clarifies why output moderation is not equivalent to intent-bound capsules.
    - The paper now uses the same narrative.

12. Created the v3 research paper.
    - File: `paper/Sealing_Jutsu_Research_Paper_v3.md`
    - File: `paper/Sealing_Jutsu_Research_Paper_v3.docx`
    - Builder: `paper/build_research_paper_v3.py`
    - The v3 paper was written from the latest evidence rather than just lightly editing the preprint.

13. Generated a PDF version of the v3 paper.
    - File: `paper/Sealing_Jutsu_Research_Paper_v3.pdf`
    - The normal DOCX-to-PDF renderer was blocked because LibreOffice/Word was not installed.
    - The builder was updated to generate PDF directly using `reportlab`.
    - The PDF was validated with `pypdf`.

14. Added Git binary safeguards.
    - File: `.gitattributes`
    - Added binary rules for `.pdf`, `.docx`, and image files.
    - This prevents line-ending conversion from corrupting generated paper artifacts.

15. Preserved the paper-generation workflow.
    - Instead of manually exporting one-off files only, the repository now contains scripts that regenerate the paper artifacts.
    - This makes later revisions easier and more reproducible.

Post-preprint commits that matter most:

- `88ee558 feat(metrics): report poison influence rate`
- `de3e246 docs(paper): add formal threat model`
- `95c79c8 docs(paper): add updated research paper draft`
- `4e2be27 docs(paper): add generated PDF draft`
- `787347a docs(paper): record preprint to final draft process`

## 6. Formal Threat Model Added

A full threat model was added to the paper materials.

The attacker is defined as a memory-poisoning attacker, not a code-execution attacker.

In-scope attacker capabilities:

- Can inject text through web pages.
- Can inject text through tool outputs.
- Can inject OCR-visible or alt-text content.
- Can influence summaries, experience logs, or memory import paths.
- Can use delayed triggers and cross-session poisoning.
- Can paraphrase malicious intent or split payloads.
- Can craft retrieval-collision-style memories.
- Can attempt to alter recommendations, planning paths, user preferences, or tool actions.

Explicit out-of-scope capabilities:

- Cannot directly edit system prompts.
- Cannot modify policy code.
- Cannot modify the capsule authorization gate.
- Cannot forge cryptographic provenance or verified-writer identity.
- Cannot compromise the tool runtime, OCR binary, external service credentials, or model weights.
- Cannot delete audit logs or force capsule status transitions to be ignored.

Protected assets:

- Recommendation integrity.
- User preference integrity.
- Action safety.
- Memory lifecycle integrity.
- Auditability.

The trust boundary was defined as:

> Retrieved memory as relevance evidence versus retrieved memory as authority.

The paper also added STRIDE and OWASP LLM mapping:

- LLM01 Prompt Injection.
- LLM04 Data and Model Poisoning.
- LLM06 Excessive Agency.
- LLM08 Vector and Embedding Weaknesses.
- MCP-style tool poisoning.

Relevant commit:

- `de3e246 docs(paper): add formal threat model`

## 7. Poison Influence Rate Added

The most important metric improvement was `poison_influence_rate`.

Definition:

> Poison influence rate counts poisoned cases where poisoned memory was used by the planner and the planner selected the attacker target before any final output gate.

Why it matters:

- ASR only asks whether the final attack succeeded.
- Output moderation may make ASR look perfect.
- But if poisoned memory still steers the planner, the memory system is still compromised.

This new metric made the paper much stronger because it separates:

- late output blocking
- pre-planning memory authorization

Important result:

| Defense style | Final ASR | Poison influence | Meaning |
|---|---:|---:|---|
| Output moderation / semantic judge | 0.00% | 30.00%-90.62% | Final action can be blocked, but poisoned memory still shapes planning. |
| Intent capsules | 0.00% | 0.00% | Poisoned memory is denied planning authority before action gating. |

Relevant commit:

- `88ee558 feat(metrics): report poison influence rate`

## 8. Converted External Corpus Evidence

The paper was upgraded with converted external trace-corpus results from AgentDojo and InjecAgent-style traces.

Validation counts:

| Corpus | Total | Poisoned | Benign |
|---|---:|---:|---:|
| AgentDojo all | 62 | 31 | 31 |
| InjecAgent all | 2108 | 1054 | 1054 |
| InjecAgent DH | 1020 | 510 | 510 |
| InjecAgent DS | 1088 | 544 | 544 |

Final table used in the v3 paper:

| Corpus | Output-mod ASR | Output-mod influence | Capsule ASR | Capsule influence | Capsule sealing |
|---|---:|---:|---:|---:|---:|
| AgentDojo all | 0.00% | 80.65% | 0.00% | 0.00% | 83.87% |
| InjecAgent all | 0.00% | 61.29% | 0.00% | 0.00% | 61.48% |
| InjecAgent DH | 0.00% | 30.00% | 0.00% | 0.00% | 30.39% |
| InjecAgent DS | 0.00% | 90.62% | 0.00% | 0.00% | 90.62% |

This became one of the strongest arguments in the final paper.

The result shows:

- Output moderation looks strong if we only measure final ASR.
- But output moderation still allows high poisoned planning influence.
- Intent capsules stop both final attack success and poisoned influence.

Main report file:

`results/converted_corpus_report.md`

## 9. Memory Lifecycle Gap Result

A focused lifecycle-gap benchmark was used to show that output moderation can fail when the malicious effect is not expressed as an obvious final dangerous action.

Key result:

| Agent | ASR | Risky action | Poison influence | Benign accuracy |
|---|---:|---:|---:|---:|
| output_moderation | 34.05% | 23.83% | 34.05% | 100.00% |
| semantic_output_judge | 13.10% | 9.17% | 34.05% | 100.00% |
| ablation_no_denied_actions | 0.00% | 0.00% | 57.14% | 100.00% |
| intent_capsules | 0.00% | 0.00% | 0.00% | 100.00% |

Interpretation:

- Output moderation does not solve memory poisoning.
- A defense can show 0% final ASR while still allowing poisoned influence.
- Denied-action controls and authorization checks are needed to prevent poisoned memory from shaping the plan.

Main result file:

`results/memory_lifecycle_gap_summary.csv`

## 10. Live LLM Planner Evidence

The preprint originally leaned heavily on deterministic/symbolic planner results. Later, live LLM planner experiments were added.

Medium live LLM workflow-corpus run:

| Condition | Rows | Planner tempted | Final ASR | Risky action | Raw parse error |
|---|---:|---:|---:|---:|---:|
| ambient_prompt | 108 | 22.22% | 22.22% | 22.22% | 0.00% |
| capsule_filtered_prompt | 108 | 2.78% | 0.00% | 0.00% | 0.00% |

Defended live LLM result by model:

| Model | Rows | Planner tempted | Final ASR | Risky action | Raw parse error |
|---|---:|---:|---:|---:|---:|
| llama3 | 36 | 2.78% | 0.00% | 0.00% | 0.00% |
| mistral | 36 | 2.78% | 0.00% | 0.00% | 0.00% |
| phi3 | 36 | 2.78% | 0.00% | 0.00% | 0.00% |

Interpretation:

- The live LLM planner can still be tempted internally.
- Capsule-filtered authorization prevents tempted plans from becoming accepted attacks.
- Raw parse error was reduced to 0.00%, so the result is not explained by malformed model output.

Main result files:

- `results/gap_fix_medium_live_llm_summary.csv`
- `results/gap_fix_medium_live_llm_model_summary.csv`

## 11. Held-Out Workflow Corpus Result

The held-out workflow corpus remains the main simulator evidence.

Key table:

| Agent | ASR | Risky action | Benign accuracy | FPR | Sealing |
|---|---:|---:|---:|---:|---:|
| ambient_memory | 33.33% | 22.22% | 100.00% | 0.00% | 0.00% |
| keyword_filter | 33.33% | 22.22% | 100.00% | 0.00% | 0.00% |
| output_moderation | 33.33% | 22.22% | 100.00% | 0.00% | 0.00% |
| provenance_only | 24.38% | 16.25% | 96.25% | 0.00% | 0.00% |
| counterfactual_memory | 3.96% | 2.64% | 91.25% | 8.75% | 0.00% |
| intent_capsules | 0.00% | 0.00% | 100.00% | 0.00% | 8.33% |

Interpretation:

- Keyword filtering and ambient memory fail similarly.
- Provenance and trust scoring help, but do not fully solve the problem.
- Counterfactual memory lowers ASR but harms benign utility.
- Intent capsules are the only tested approach that reaches 0% ASR, 0% risky action, 100% benign accuracy, and 0% FPR together.

Main result file:

`results/workflow_corpus_test_split_summary.csv`

## 12. Stress Suites and Calibration

Additional stress evidence included generated holdout and advanced suites.

Stress examples:

| Suite | Ambient ASR | Provenance ASR | Capsule ASR | Capsule benign |
|---|---:|---:|---:|---:|
| Generated holdout | 44.37% | 13.13% | 0.00% | 100.00% |
| Advanced suite | 17.41% | 2.59% | 0.00% | 100.00% |

Threshold calibration:

- A 16-point sweep varied medium-risk quorum and topic-scope thresholds.
- In the simulator, all swept settings reported:
  - 0.00% ASR
  - 0.00% risky action
  - 100.00% benign accuracy
  - 0.00% false positives

This helps close the "hand-tuned thresholds only" criticism at prototype level, though the paper still admits external calibration is future work.

Main result file:

`results/current_main_threshold_calibration.csv`

## 13. New Final Research Paper

After analyzing the printed preprint and comparing it against the newest results, a new v3 research paper was created.

New final paper title:

> Intent-Bound Memory Authorization Against Persistent Agent Poisoning

Files created:

- `paper/Sealing_Jutsu_Research_Paper_v3.md`
- `paper/Sealing_Jutsu_Research_Paper_v3.docx`
- `paper/Sealing_Jutsu_Research_Paper_v3.pdf`
- `paper/build_research_paper_v3.py`

The new v3 paper includes:

- Updated abstract.
- Stronger introduction.
- Clear contributions.
- Related work gap table.
- Formal threat model.
- Capsule design section.
- Prototype implementation section.
- Evaluation methodology.
- Poison influence metric.
- Held-out workflow corpus results.
- Memory lifecycle gap results.
- Converted AgentDojo/InjecAgent results.
- Stress suite results.
- Live LLM planner results.
- Threshold calibration note.
- Discussion.
- Limitations and threats to validity.
- Conclusion.
- References.

Relevant commits:

- `95c79c8 docs(paper): add updated research paper draft`
- `4e2be27 docs(paper): add generated PDF draft`

## 14. PDF Generation

The first DOCX-to-PDF rendering attempt was blocked because the machine did not have LibreOffice or Word COM installed.

Observed limitations:

- `soffice` was not available.
- Word COM was not registered.
- The Documents render script could not convert DOCX to PDF.

Solution:

- The v3 paper builder was upgraded to generate PDF directly using `reportlab`.
- `.gitattributes` was added so PDFs, DOCX files, and images are treated as binary in Git.
- The generated PDF was validated with `pypdf`.

Final PDF:

`paper/Sealing_Jutsu_Research_Paper_v3.pdf`

PDF validation:

- 9 pages.
- Valid title metadata.
- Stored as binary in Git to avoid line-ending corruption.

## 15. Current Paper Narrative

The final paper story is:

1. LLM agents increasingly use persistent memory.
2. Persistent memory creates a cross-session poisoning attack surface.
3. The failure is not only malicious text; it is ambient authority.
4. Current defenses often check relevance, provenance, or final output safety.
5. They do not ask what a memory is authorized to influence.
6. Intent-bound capsules convert memory into bounded security objects.
7. The policy gate separates retrieval from influence.
8. Poison influence rate shows why output moderation is not enough.
9. Converted external traces show high poisoned influence for output moderation despite 0% final ASR.
10. Intent capsules reach 0% ASR and 0% poison influence under the tested threat model.

## 16. Main Reviewer-Safe Claim

The strongest safe claim is:

> Intent-bound memory capsules are a least-privilege authorization layer for persistent agent memory. In the tested prototype, they reduce both final attack success and poisoned planning influence while preserving benign utility.

The paper should not claim:

> CapsuleGuard solves all agent memory poisoning.

The paper should claim:

> CapsuleGuard provides evidence that separating memory retrieval from memory authority is a promising defensive layer against persistent memory poisoning under a clearly stated threat model.

## 17. What Is Still Pending Before Real Submission

The current paper is much stronger than the original preprint, but real submission readiness still needs:

- More polishing for venue-specific formatting.
- More precise citation formatting.
- Ideally, more real-world traces from deployed or lab-user workflows.
- More live LLM cases if targeting a top security venue.
- Clear dataset provenance and conversion explanation for AgentDojo/InjecAgent traces.
- Possibly a shorter conference-style version if the target venue has page limits.
- A final proofreading pass for grammar, terminology consistency, and figure/table placement.

## 18. Final Artifacts to Use

Use these as the current final research-paper artifacts:

- Markdown: `paper/Sealing_Jutsu_Research_Paper_v3.md`
- DOCX: `paper/Sealing_Jutsu_Research_Paper_v3.docx`
- PDF: `paper/Sealing_Jutsu_Research_Paper_v3.pdf`
- Builder: `paper/build_research_paper_v3.py`

The older generated paper files still exist and are useful for comparison:

- `paper/Intent_Bound_Memory_Capsules_Submission_Draft_v2.md`
- `paper/Intent_Bound_Memory_Capsules_Submission_Draft_v2.docx`
- `paper/build_submission_draft_v2.py`

The printed source paper was:

- `C:\Users\User\Downloads\Sealing_Jutsu (1).pdf`

## 19. Final Assessment

The v3 paper is stronger than the preprint because it now has:

- A clearer thesis.
- A formal threat model.
- A new metric that exposes memory compromise.
- External converted-trace evidence.
- Live LLM planner evidence.
- A direct answer to the output-moderation objection.
- More careful limitations.
- Reproducible paper generation in Markdown, DOCX, and PDF.

This is now a credible research-paper draft for further refinement, arXiv-style posting, workshop submission, or conversion into a venue-specific format.

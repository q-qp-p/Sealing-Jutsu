# Post-Preprint Work Scope Analysis

This document analyzes the work recorded in the pasted chat segment after the printed preprint paper `Sealing_Jutsu (1).pdf`. It separates research-paper content from project logistics, reproducibility work, and out-of-scope material.

## Short Answer

Yes, the important research work done after the preprint has been added to the newer research papers.

The following are in scope for the paper:

- formal threat model
- poison influence rate
- output moderation versus capsule authorization argument
- converted AgentDojo/InjecAgent evidence
- memory lifecycle gap benchmark
- live LLM planner results
- threshold calibration
- honest limitations

The following should stay outside the paper body:

- commit hashes
- PDF-generation notes
- `.gitattributes` binary-safety notes
- file-location logistics
- chat-history/process narrative
- "after the preprint we did X" wording

Those items are useful for the repository log, but they are not research contributions.

## What Was Done After the Preprint

The printed preprint was:

`C:\Users\User\Downloads\Sealing_Jutsu (1).pdf`

After that preprint, the following work was completed.

| Post-preprint item | What happened | In paper? | Scope decision |
|---|---|---:|---|
| v3 research paper | A new paper was written from the latest project evidence. | Yes | In scope as final paper artifact. |
| Poison influence rate | Added the argument that output moderation can block final action while still allowing poisoned planning influence. | Yes | In scope and important. |
| Converted AgentDojo/InjecAgent results | Added converted external trace evidence showing high poison influence for output moderation and 0% influence for intent capsules. | Yes | In scope and important. |
| Formal threat model | Added attacker capabilities, limits, trust boundaries, assumptions, and security objectives. | Yes | In scope and necessary. |
| Live LLM planner results | Added local live LLM evidence across llama3, mistral, and phi3. | Yes | In scope as realism check. |
| Threshold calibration | Added 16-point threshold sweep result. | Yes | In scope, but should be described as prototype-level calibration. |
| More honest limitations | Paper now says results are under tested threat model, not universal security. | Yes | In scope and reviewer-safe. |
| PDF version | Generated final paper PDF. | No, not as content | In scope for deliverable packaging, not a research claim. |
| Preprint-to-final log | Created a project history note. | No | In scope for repo/research notes, not paper body. |
| Post-preprint checklist | Added `5.1 Work Completed After the Preprint` to the log. | No | In scope for project documentation, not paper body. |
| IEEE-style paper | Created a separate IEEE-style version with `.md`, `.docx`, `.pdf`, and `.tex`. | Separate paper artifact | In scope for formatting/submission prep, not new research evidence. |
| `.gitattributes` | Added binary handling for PDFs, DOCX, and images. | No | Repo hygiene only. |
| Commit hashes | Recorded pushed commits. | No | Useful for audit trail only. |
| File path notes | Mentioned locations of papers and diagrams. | No | Logistics only. |
| DOCX render limitation | Noted LibreOffice/Word rendering was unavailable. | No | QA note only; not research content. |

## What Is Already Added to the Research Paper

The v3 paper includes the actual research-relevant post-preprint items:

| Paper section | Included content |
|---|---|
| Abstract | Updated with poison influence rate, AgentDojo/InjecAgent evidence, and live LLM result. |
| Introduction | Reframes the core claim as "retrieval is not authorization." |
| Contributions | Adds poison influence rate and broader evaluation coverage. |
| Threat Model | Adds formal attacker capabilities, limits, and trust boundary. |
| Evaluation Methodology | Defines poison influence rate and explains why ASR alone is insufficient. |
| Results | Includes workflow corpus, lifecycle-gap, converted external traces, stress suites, and live LLM results. |
| Discussion | Explains why output moderation is not equivalent to memory authorization. |
| Limitations | States prototype, synthetic/converted corpora, raw multimodal gaps, and non-universal claim. |

Current main research paper files:

- `paper/Sealing_Jutsu_Research_Paper_v3.md`
- `paper/Sealing_Jutsu_Research_Paper_v3.docx`
- `paper/Sealing_Jutsu_Research_Paper_v3.pdf`

Current IEEE-style paper files:

- `paper/Sealing_Jutsu_IEEE_Style_Paper.md`
- `paper/Sealing_Jutsu_IEEE_Style_Paper.docx`
- `paper/Sealing_Jutsu_IEEE_Style_Paper.pdf`
- `paper/Sealing_Jutsu_IEEE_Style_Paper.tex`

## What Is Out of Scope for the Paper Body

The following should not be written inside the research paper as research content.

### 1. Commit History

Commit IDs prove the work was pushed, but papers do not normally list commit hashes in the body.

Use in:

- repository log
- reproducibility appendix, if needed
- artifact evaluation notes

Do not use as:

- main paper evidence
- research contribution

### 2. PDF Generation Notes

The fact that the PDF was generated with `reportlab` because LibreOffice/Word was unavailable is useful project history, but not part of the research.

Use in:

- `PAPER_PREPRINT_TO_FINAL_RESEARCH_LOG.md`
- artifact build notes

Do not use in:

- abstract
- results
- methodology
- conclusion

### 3. `.gitattributes` Binary Rules

Binary Git handling is good repository hygiene, but not a research contribution.

Use in:

- repo maintenance notes

Do not use as:

- system design claim
- security result

### 4. "After the Preprint" Narrative

The final paper should not say:

> After the preprint, we added...

Instead, the paper should present the final work coherently:

> We evaluate poison influence rate...

The after-preprint narrative belongs in the project log.

### 5. File Location Logistics

Paths such as:

- `C:\Users\User\Downloads\Archive`
- `C:\Users\User\Sealing-Jutsu\paper`
- figure file paths

are useful for us locally, but not for a research paper.

Use in:

- local project notes

Do not use in:

- submitted paper text

### 6. Visual Render Limitation

The DOCX render limitation is a local tooling limitation, not a scientific limitation.

It should not be framed as a limitation of CapsuleGuard or the research.

## What Is In Scope but Must Be Framed Carefully

Some items are valid for the paper, but only with careful wording.

| Item | Safe framing | Unsafe framing |
|---|---|---|
| 0% ASR | "0% ASR under tested benchmark conditions." | "Solves all poisoning." |
| 0% poison influence | "0% poison influence in converted trace-corpus evaluation." | "No poisoned memory can ever influence an agent." |
| Live LLM result | "Realism check across local models." | "Conference-grade frontier-model validation." |
| Threshold sweep | "Prototype-level calibration sweep." | "Fully calibrated production policy." |
| Converted AgentDojo/InjecAgent traces | "Converted external-style trace evidence." | "Direct unmodified real-world deployment traces." |
| PDF/IEEE paper | "Presentation and submission artifacts." | "Additional experimental evidence." |

## Recommended Paper Boundary

The paper should claim:

> Intent-bound memory capsules provide a least-privilege authorization layer for persistent agent memory. In the tested prototype, this layer reduces both final attack success and poisoned planning influence while preserving benign utility.

The paper should not claim:

> CapsuleGuard solves all agent memory poisoning.

The strongest safe paper contribution is:

> separating retrieval from authority, and measuring poison influence separately from final attack success.

## Final Scope Verdict

Nothing in the pasted chat is harmful by itself, but not everything belongs in the paper.

Research-paper material:

- threat model
- poison influence rate
- external converted-corpus evidence
- lifecycle-gap benchmark
- live LLM planner check
- calibration
- limitations

Repository/project-log material:

- commit hashes
- PDF generation process
- `.gitattributes`
- file locations
- preprint-to-final chronology
- local render-tool limitation

Separate submission-format material:

- IEEE-style `.tex`, `.pdf`, `.docx`, and `.md`

The v3 research paper and IEEE-style paper already contain the right research content. The process details are correctly kept in the research log instead of being inserted into the paper body.

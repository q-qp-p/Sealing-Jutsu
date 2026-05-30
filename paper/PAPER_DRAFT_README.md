# Paper Folder Index

This folder contains the GitHub-ready paper source material for the agent-memory poisoning defense project. The richer local package, including the generated DOCX, remains in:

```text
C:\Users\User\Music\Research Paper\16_paper_draft
```

Latest refresh: May 30, 2026. This paper folder is synced with:

```text
C:\Users\User\Music\Agent-Poisoning-Research-FINAL
branch: fix/llm-first-pass-json-planning
commit: ac1d2ea
```

## Files

- `Intent_Bound_Memory_Capsules_Submission_Draft_v2.md`
  Markdown source for the current submission-style draft.

- `Intent_Bound_Memory_Capsules_Submission_Draft_v2.docx`
  Generated Word draft for review and sharing.

- `paper_result_tables_v2.csv`
  Consolidated result values used by the paper tables.

- `build_submission_draft_v2.py`
  Rebuilds the Markdown draft, result table, and figures from the current repository result CSVs.

- `figures_v2/`
  Current figure set for the draft:
  architecture, threat model, trust rules, workflow results, stress-suite ASR, ablation results, live LLM planner chart, and contact sheet.

## Evidence Added In This Refresh

- Unit test expectation updated to `Ran 136 tests`.
- Medium live LLM planner section added:
  - ambient prompt ASR: `22.22%`
  - capsule-filtered planner tempted: `2.78%`
  - capsule-filtered final ASR: `0.00%`
  - capsule-filtered risky action: `0.00%`
  - raw/final parse error: `0.00%`
- Trace-corpus importer and command added to the reproducibility appendix.
- References upgraded from title-only entries to author/year/arXiv-or-venue style entries.
- Limitations updated so the paper no longer says live LLM results are missing.

## Remaining Paper Work

- Run a larger live LLM study with more models, seeds, and task domains.
- Replace generated workflow records with redacted real or lab-collected traces.
- Add real OCR/image ingestion and real sandboxed browser/email/database tools.
- Convert the Markdown into the final venue-specific PDF or DOCX format after choosing the target venue.

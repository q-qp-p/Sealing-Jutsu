# Real-World Research Readiness Tracker

This file tracks the gap between the current research prototype and stronger real-world paper evidence.

## Added In This Pass

### Trace Corpus Intake

New command:

```powershell
python validate_trace_corpus.py path\to\raw_traces.jsonl --redacted-out data\redacted_lab_traces.jsonl --report-json results\redacted_lab_trace_report.json --require-redaction
```

What it does:

- validates flexible exported trace records with `task`, `events`, `messages`, or `steps`
- counts total, poisoned, and benign records
- counts memory-like events and poison-labeled memory events
- summarizes source-type coverage
- recursively redacts common emails, URLs, phone numbers, and token-like secrets
- writes a JSON report for paper evidence

Why it matters:

Generated scenarios are useful for controlled stress tests, but a stronger paper needs real or lab-collected traces. This gives us a safer intake path for those traces without leaking private identifiers.

### Realistic Tool Sandbox Records

New tool-chain audit support:

- `RealisticToolSandbox`
- `ToolChainExecutionRecord`
- `write_tool_chain_trace_csv`

What it records:

- scenario id
- agent
- tool name
- operation
- target
- risk
- allow/block decision
- reason
- capsule ids used
- payload hash
- synthetic side-effect flag

Why it matters:

The current benchmark still avoids real side effects, correctly. The new sandbox makes tool-chain evidence more realistic while keeping every action synthetic and auditable.

## Still Pending

1. Larger live LLM study:
   Run more models, seeds, and task domains. Current medium run is useful, but not the final conference-scale evidence.

2. External trace collection:
   Collect redacted lab traces from repeatable user workflows and run them through `validate_trace_corpus.py`.

3. Raw OCR/image pipeline:
   Add actual image/PDF ingestion instead of only OCR-style extracted text.

4. Production vector retrieval:
   Add FAISS/Chroma/LanceDB-backed retrieval runs and adversarial embedding collision tests.

5. Stronger adaptive attacker:
   Make the attacker observe failure reasons and mutate across source type, paraphrase, delayed trigger, retrieval collision, and trusted-looking metadata.

6. Threshold calibration:
   Report sensitivity across topic overlap, authority floors, quorum, influence budget, and memory age decay.

7. Larger benign utility suite:
   Expand normal tasks so the paper can show the defense does not win by blocking useful memory.

## Current Honest Claim

The project now supports this claim:

```text
Intent-bound memory authorization reduced attack success in the tested simulator and medium live LLM planner benchmarks, while preserving benign utility under the stated threat model.
```

The project still should not claim:

```text
CapsuleGuard solves all agent memory poisoning.
```

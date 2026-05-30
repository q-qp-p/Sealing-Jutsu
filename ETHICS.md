# Ethics And Safety

This project is defensive. It studies how persistent memory poisoning can affect LLM agents and how least-privilege memory authorization can reduce that risk.

## Intended Use

Use this repository to:

- Reproduce the included defensive benchmarks.
- Study memory poisoning in a controlled sandbox.
- Compare defenses such as keyword filtering, provenance-only retrieval, counterfactual checks, and intent-bound memory authorization.
- Build safer long-term-memory agents.

## Non-Goals

Do not use this repository to:

- Attack real agents, users, companies, recommender systems, or tool-using assistants.
- Store or process real private user data without consent.
- Execute real browser, email, database, payment, or account actions outside an isolated sandbox.
- Present simulator results as universal proof that all memory poisoning is solved.

## Dataset And Benchmark Safety

The included scenarios use synthetic vendors, synthetic users, synthetic memories, and safe tool traces. Attack examples are intentionally bounded so they can evaluate the defense without providing operational instructions against real targets.

## Responsible Claims

The supported claim is limited:

```text
Intent-bound memory authorization reduces attack success in the tested simulator and live LLM planner benchmarks while preserving benign utility under the stated threat model.
```

Do not claim:

```text
This solves all agent memory poisoning.
```

The remaining gaps include larger live LLM studies, real or lab-collected traces, raw OCR/image ingestion, production vector retrieval, signed enterprise provenance, and isolated real-tool sandboxes.

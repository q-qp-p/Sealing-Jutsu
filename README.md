# CapsuleGuard

**Authority-scoped memory capsules that stop persistent agent poisoning.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-76%20passing-brightgreen.svg)](#testing)
[![ASR](https://img.shields.io/badge/attack%20success%20rate-0.00%25-brightgreen.svg)](#results)
[![Benign Accuracy](https://img.shields.io/badge/benign%20accuracy-100%25-brightgreen.svg)](#results)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## The Problem

LLM agents that use long-term memory have a persistent attack surface. A poisoned memory stored today can be retrieved later and silently steer the agent's recommendations, preferences, or tool use — without the user ever knowing.

Most defenses answer the wrong question. They ask *"does this memory look suspicious?"* The deeper question is:

> **What is this memory allowed to influence?**

## The Idea

CapsuleGuard treats persistent memory poisoning as an **authority-control problem**.

Each stored memory is compiled into a **capsule** — a bounded contract that records:

| Field | Purpose |
|---|---|
| `source_type` | Where the memory came from (web, tool, user, summary, experience) |
| `kind` | What type of claim it makes (fact, preference, observation, directive) |
| `allowed_topics` | What task domains it may influence |
| `denied_actions` | What actions it cannot authorize |
| `source_authority` | How much trust the source carries |
| `influence_budget` | How much weight it can contribute to a decision |
| `verification_count` | Whether the claim has been independently confirmed |
| `status` | Active or sealed (quarantined) |

At decision time, a retrieved memory must pass the capsule contract before it can influence planning. Medium- and high-risk actions require **independent quorum support** — a single retrieved memory cannot authorize them alone.

```
 Memory Store
      │
      ▼
 CapsuleCompiler          ← seals directives and high-risk weak sources
      │
      ▼
 CapsulePolicy            ← topic scope + authority floor check
      │
      ▼
 EvidenceQuorumGate       ← independent multi-source support required
      │
      ▼
 PlanAuthorizationGate    ← final plan-level contract check
      │
      ▼
 Agent Decision
```

---

## Results

Tested across **32 attack types**, **5 trials × 12 repetitions**, with 12 noise memories per trial.

| Agent | Attack Success Rate | Benign Accuracy | Sealing Rate |
|---|---|---|---|
| Ambient Memory (baseline) | 45% | 97% | 0% |
| Keyword Filter | 41% | 97% | 0% |
| Provenance Only | 13% | 96% | 0% |
| Trust Score Retrieval | 13% | 96% | 0% |
| **CapsuleGuard** | **0.00%** | **100%** | 12% |

Ablations confirm the contribution of each layer — removing topic scope, denied actions, or quorum individually each reintroduces vulnerability.

---

## Installation

```bash
git clone https://github.com/Mr-Akuma/sealing-jutsu
cd sealing-jutsu
pip install -r requirements.txt
```

No external API keys required for the default synthetic benchmark.

---

## Usage

**Run the full benchmark:**
```bash
python run_capsuleguard.py
```

**Run the poisoning stress test (generated holdout):**
```bash
python run_capsuleguard.py \
  --attack-mode generated_holdout \
  --trials 5 --repetitions 12 --noise-memories 12 \
  --seed 2026 \
  --summary-csv results/summary.csv
```

**Other attack modes:**
```bash
python run_capsuleguard.py --attack-mode moderate
python run_capsuleguard.py --attack-mode insane
python run_capsuleguard.py --attack-mode extreme
python run_capsuleguard.py --attack-mode holdout
python run_capsuleguard.py --attack-mode adaptive_loop
python run_capsuleguard.py --attack-mode multimodal
python run_capsuleguard.py --attack-mode attacker_generated
```

**Sensitivity sweep:**
```bash
python run_sensitivity.py --attack-mode generated_holdout
```

**LLM provider experiment (OpenAI-compatible or Ollama):**
```bash
python run_llm_experiment.py --provider local
python run_llm_experiment.py --provider ollama --endpoint http://localhost:11434/api/generate --model llama3.1
```

---

## Testing

```bash
python -m unittest discover -s tests
```

```
Ran 76 tests in 0.121s
OK
```

---

## Output Files

Each run produces:

```
results/
├── capsule_sandbox_results.csv      ← per-trial metrics
├── capsule_sandbox_summary.csv      ← aggregated summary with CI95
├── capsule_attack_breakdown.csv     ← per-attack-type breakdown
├── capsule_gap_closure.csv          ← baseline vs defense gap analysis
├── capsule_tool_traces.csv          ← tool action trace log
└── charts/                          ← SVG charts per metric
```

---

## Agents Compared

| Agent | Description |
|---|---|
| `ambient_memory` | No defense — full retrieval |
| `keyword_filter` | Block memories with suspicious words |
| `quarantine_only` | Quarantine flagged memories |
| `trust_score_retrieval` | Weight by source trust score |
| `output_moderation` | Filter final output |
| `counterfactual_memory` | Counterfactual relevance check |
| `provenance_only` | Provenance tracking only |
| `intent_capsules` | **CapsuleGuard** (full system) |
| `ablation_no_topic_scope` | CapsuleGuard without topic scope |
| `ablation_no_denied_actions` | CapsuleGuard without action denial |
| `ablation_no_quorum` | CapsuleGuard without quorum gate |

---

## Paper

See [`paper/CAPSULEGUARD_CONFERENCE_DRAFT.md`](paper/CAPSULEGUARD_CONFERENCE_DRAFT.md) for the full write-up.

---

## Planned for Future Release

1. Real attacks against live LLM endpoints.
2. Real tool execution and side-effect tracing.
3. Real multimodal and OCR input processing.
4. Multi-agent shared memory with cross-agent quorum.
5. Live external LLM benchmark runs (GPT-4o, Claude).
6. Production FAISS / Chroma / LanceDB vector backend.
7. Real image parsing and OCR model integration.
8. Real browser and account automation testing.

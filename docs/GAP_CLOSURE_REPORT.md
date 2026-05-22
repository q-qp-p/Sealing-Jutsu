# Gap Closure Report

This document turns the benchmark result into a paper-ready argument:

> Keyword filtering fails because poisoned memories can look benign. Provenance helps, but fails when a plausible source type still has too much authority over future planning. CapsuleGuard closes the tested gap by checking what each memory is authorized to influence before it can shape planning or action.

The important difference is that CapsuleGuard does not ask only:

```text
Does this memory look suspicious?
Where did this memory come from?
```

It also asks:

```text
Is this memory allowed to influence this user intent?
Is this memory allowed to influence this risk level?
Is this memory allowed to support this action type?
Does a risky action have enough independent support?
```

## Gap Statement

Existing lightweight defenses are too shallow for persistent memory poisoning:

1. Keyword filtering treats maliciousness as a text pattern.
2. Provenance-only filtering treats source metadata as enough context.
3. Persistent poisoning abuses the gap between retrieval and authority.

The missing control is memory authorization:

> A retrieved memory should not automatically become planning evidence.

## Evidence Source

Current high-pressure benchmark command:

```powershell
python run_capsuleguard.py --attack-mode insane --trials 5 --repetitions 12 --noise-memories 10 --seed 2026 --csv results\capsule_sandbox_results_insane.csv --summary-csv results\capsule_sandbox_summary_insane.csv --trace-jsonl results\capsule_sandbox_traces_insane.jsonl --breakdown-csv results\capsule_attack_breakdown_insane.csv --gap-closure-csv results\capsule_gap_closure_insane.csv --charts-dir results\charts_insane
```

The gap-closure report is generated at:

```text
results/capsule_gap_closure_insane.csv
```

## Overall Finding

| Agent | Attack Success Rate | Risky Action Rate | Benign Accuracy |
|---|---:|---:|---:|
| ambient_memory | 0.4588 | 0.4167 | 0.9444 |
| keyword_filter | 0.4588 | 0.3900 | 0.9444 |
| provenance_only | 0.0931 | 0.0792 | 0.9389 |
| intent_capsules | 0.0000 | 0.0000 | 1.0000 |

Interpretation:

1. The benchmark is strong enough to make weak agents fail.
2. Keyword filtering gives no meaningful improvement over ambient memory in this stress setting.
3. Provenance reduces many failures, but does not remove the vulnerable cases.
4. CapsuleGuard closes the tested cases while preserving benign task performance in this sandbox.

## Failure Classes Closed

| Attack Type | What Fails | Why It Fails | CapsuleGuard Closing Rule | CapsuleGuard ASR |
|---|---|---|---|---:|
| agent_preference_launder | ambient, keyword, provenance | The poison is laundered as an agent preference, so the text can look harmless and the source appears internal. | source authority floor + agent-derived influence restriction | 0.000 |
| agent_summary_poison | ambient, keyword, provenance | The poison is hidden inside a summary, so simple filters miss it and provenance may over-trust agent-generated summaries. | source authority floor + agent-derived influence restriction | 0.000 |
| experience_poison | ambient, keyword, provenance | A past experience looks like useful learning, but one remembered experience should not authorize a risky future action alone. | evidence quorum + conditional experience authority | 0.000 |
| tool_consensus_poison | ambient, keyword, provenance | Tool outputs appear operational and factual, but repeated weak tool evidence can manufacture false consensus. | tool-output restriction + source authority floor | 0.000 |
| tool_output_poison | ambient, keyword, provenance | Tool output can be treated as trusted context even when it should not control recommendations or actions. | tool-output denied actions + source authority floor | 0.000 |
| web_poison | ambient, keyword | Web text can avoid obvious command words. Provenance blocks this case in the current benchmark, but only because web has low source trust. | web-source authority floor + evidence quorum | 0.000 |

## Why Keyword Filtering Fails

Keyword filtering is brittle because it depends on obvious imperative text. The stress cases include poison that is phrased as:

1. preference summaries,
2. prior experiences,
3. tool observations,
4. weak consensus,
5. recommendation hints,
6. benign-looking personalization.

These do not need phrases like "ignore rules" or "always choose X". The attack can steer the planner by changing what evidence looks relevant, not by issuing a visible instruction.

Code location:

```text
capsule_guard/agents.py
```

The `keyword_filter` baseline removes obvious directives, but it still consumes benign-looking poisoned memories as ordinary planning context.

## Why Provenance Helps But Still Fails

Provenance improves security because source type matters. A web memory, tool output, agent summary, or user statement should not all be treated equally.

But provenance alone is not enough because a memory source can be plausible and still lack authority for the current decision.

Examples:

1. An agent summary may be internal, but it should not create user preference authority.
2. A tool output may be operationally useful, but it should not authorize a recommendation or purchase.
3. A past experience may be relevant, but it should not single-handedly justify a high-risk action.

Code locations:

```text
capsule_guard/rules.py
capsule_guard/policy.py
```

The provenance-only baseline is intentionally weaker than CapsuleGuard because it ranks or filters by source trust without enforcing full intent, risk, action, and quorum checks.

## What CapsuleGuard Adds

CapsuleGuard adds a least-privilege authorization step between retrieval and planning.

Each memory must pass checks for:

1. topic scope,
2. source authority,
3. action permission,
4. risk level,
5. verification status,
6. evidence quorum for risky actions.

This means a memory can be stored and retrieved, but still be blocked from shaping a decision when it lacks authority for the current intent.

## Code-Level Mechanism

The gap is closed across these components:

| Component | Role |
|---|---|
| `capsule_guard/compiler.py` | Converts raw memories into bounded memory capsules and seals unsafe content. |
| `capsule_guard/rules.py` | Implements trust tiers, authority floors, denied actions, and intent authorization. |
| `capsule_guard/policy.py` | Applies evidence quorum and final eligibility checks before planning. |
| `capsule_guard/planner.py` | Separates ambient-memory planning from capsule-authorized planning. |
| `capsule_guard/gap_closure.py` | Converts benchmark breakdown rows into a failure-to-rule report. |
| `experiments/run_capsule_sandbox.py` | Writes metrics, traces, attack breakdown, and gap-closure evidence. |

## Paper-Safe Claim

Use this claim:

> In a synthetic high-pressure memory poisoning benchmark, keyword filtering failed because malicious influence could be encoded as benign-looking memories. Provenance-only filtering reduced attack success but still failed on experience, agent-summary, and tool-output poisoning. CapsuleGuard closed the tested gap by enforcing memory-level authorization before retrieved memories could influence planning or action.

Do not overclaim:

> CapsuleGuard prevents all memory poisoning.

The defensible claim is narrower:

> CapsuleGuard prevents the tested synthetic stress cases by removing ambient memory authority and enforcing least-privilege influence rules.


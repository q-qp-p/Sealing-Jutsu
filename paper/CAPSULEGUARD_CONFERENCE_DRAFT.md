# CapsuleGuard: Authority-Scoped Memory Capsules Against Persistent Agent Poisoning

## Abstract

Long-term memory lets LLM agents personalize decisions, reuse prior experience, and preserve context across sessions. The same persistence creates a security risk: poisoned memories stored today may be retrieved later and silently steer planning, recommendations, or tool use. Existing defenses often focus on detecting suspicious text, tracking provenance, filtering retrieval, or checking final outputs. We argue that persistent memory poisoning is also an authority-control problem. Retrieved memories are often given ambient authority over future tasks without checking what they are allowed to influence.

We propose CapsuleGuard, a least-privilege memory architecture that compiles each stored memory into an authority-scoped capsule. A capsule records source type, topic scope, denied actions, source authority, influence budget, verification count, and status. At runtime, retrieved memories must pass authorization checks before they can influence planning or action. Medium- and high-risk actions require sufficient authorized support rather than a single retrieved memory.

In a synthetic high-pressure benchmark with noisy benign memory distractors, CapsuleGuard reduced attack success from 56.01% for ambient memory, 51.67% for keyword filtering, and 15.29% for provenance-only defense to 0.00%, while preserving 100.00% benign accuracy in the tested sandbox. Ablations show that removing denied-action and quorum controls reintroduces attack success. These results support the claim that memory-level authorization is a useful defensive layer against persistent agent poisoning.

## 1. Introduction

LLM agents increasingly maintain memory across tasks. Memory can store user preferences, task history, tool outputs, retrieved web context, generated summaries, and previous successful plans. This improves usefulness, but it also creates a persistent attack surface. If an attacker causes a harmful memory to be stored, the agent may later retrieve it as normal context and allow it to influence a different decision.

Prior work shows that memory poisoning can occur through direct text injection, web content, multimodal content, tool output, self-generated summaries, experience retrieval, and query-only interactions. These works establish the attack surface clearly. The remaining defensive question is not only whether a memory is malicious or where it came from. A deeper question is:

```text
What is this memory allowed to influence?
```

This paper frames persistent agent poisoning as an ambient-authority failure. In many agent designs, retrieval acts like authorization: once a memory enters context, the model may treat it as useful evidence, preference, or procedural guidance. CapsuleGuard separates retrieval from authority. A memory may be retrieved because it is semantically relevant, but it cannot influence planning or action unless it satisfies an explicit capsule contract.

## 2. Research Gap

The core gap is that current defenses often answer only part of the problem:

| Defense Type | What It Answers | What It Misses |
|---|---|---|
| Keyword filtering | Does the memory contain suspicious words? | Poison can be phrased as benign context. |
| Prompt sanitization | Can obvious injection text be removed? | Poison may not look like an instruction. |
| Provenance tracking | Where did this memory come from? | A plausible source can still lack authority. |
| Retrieval filtering | Should this memory be retrieved? | Retrieved memory still needs influence control. |
| Output filtering | Is the final action unsafe? | The poisoned influence has already shaped planning. |

CapsuleGuard targets the missing layer:

```text
retrieval -> memory authorization -> planning/action
```

## 3. Threat Model

### Assets

The protected assets are:

1. correctness of agent recommendations,
2. integrity of user preferences,
3. safety of medium- and high-risk actions,
4. separation between data, summaries, experiences, and instructions,
5. long-term memory integrity across sessions.

### Attacker Goal

The attacker wants a stored memory to steer a future agent decision toward an attacker-chosen outcome. In the benchmark, the target outcome is `VendorX` or a risky path involving private account details.

### Attacker Capabilities

The attacker may cause memory writes through:

1. web content,
2. tool output,
3. agent-generated summaries,
4. experience logs,
5. unverified user-like statements,
6. benign-looking recommendation hints,
7. split weak-source evidence,
8. delayed trigger memories.

The attacker does not modify CapsuleGuard code, policy rules, the trusted benchmark oracle, or verified user records.

### Out Of Scope

This prototype does not claim to solve:

1. compromise of the memory database itself,
2. malicious policy configuration,
3. compromised verified-user identity,
4. real multimodal attacks,
5. real API/tool execution,
6. all possible adaptive LLM jailbreaks.

## 4. CapsuleGuard Design

CapsuleGuard compiles raw memories into bounded memory capsules. Each capsule has:

1. `content`: the memory text,
2. `source_type`: origin class such as web, tool, user, summary, or experience,
3. `kind`: fact, preference, observation, experience, or directive,
4. `allowed_topics`: topic scope extracted from the memory,
5. `denied_actions`: actions the memory cannot authorize,
6. `source_authority`: numeric authority assigned by source and verification,
7. `influence_budget`: capped planning influence,
8. `verification_count`: verified support count,
9. `status`: active, sealed, or rejected.

The central invariant is:

```text
Retrieval is not authorization.
```

A memory must pass authorization before it can shape planning. The authorization layer checks topic overlap, capsule status, denied actions, source authority floor, directive status, and evidence quorum.

## 5. Authorization Rules

CapsuleGuard enforces these rules:

| Rule | Purpose |
|---|---|
| Topic scope | A memory may only influence matching task topics. |
| Source authority floor | Weak sources cannot authorize medium/high-risk actions. |
| Denied actions | Web, tool, and agent-derived memories cannot authorize dangerous actions. |
| Directive sealing | Command-like memories are stored for audit but blocked from planning. |
| Influence budget | One memory cannot dominate solely by retrieval relevance. |
| Evidence quorum | Risky actions require enough independent authorized support. |
| Verified preference precedence | Verified user preferences outweigh weak contradictory memories. |

## 6. Implementation

The prototype is implemented in Python.

| Component | File |
|---|---|
| Capsule schema | `capsule_guard/models.py` |
| Memory compiler | `capsule_guard/compiler.py` |
| Trust and authorization rules | `capsule_guard/rules.py` |
| Policy and quorum gate | `capsule_guard/policy.py` |
| Ambient and capsule planners | `capsule_guard/planner.py` |
| Baselines and ablations | `capsule_guard/agents.py` |
| Scenario generation | `capsule_guard/scenarios.py` |
| Evaluation and traces | `capsule_guard/evaluation.py` |
| Gap-closure reporting | `capsule_guard/gap_closure.py` |

## 7. Evaluation

### Research Questions

RQ1. Does authority-scoped memory reduce attack success compared with ambient memory, keyword filtering, and provenance-only baselines?

RQ2. Does the defense preserve benign memory usefulness?

RQ3. Which CapsuleGuard controls are necessary?

RQ4. Which attack classes remain after provenance-only filtering?

### Agents Compared

| Agent | Description |
|---|---|
| `ambient_memory` | Retrieves memory and allows it to influence planning freely. |
| `keyword_filter` | Seals obvious directive-like memory but allows benign-looking poison. |
| `provenance_only` | Uses source trust as a score but does not enforce capsule contracts. |
| `intent_capsules` | Full CapsuleGuard defense. |
| `ablation_no_topic_scope` | Disables topic-scope enforcement. |
| `ablation_no_denied_actions` | Removes action restrictions and authority floors. |
| `ablation_no_quorum` | Allows risky decisions without evidence quorum. |

### Attack Classes

The `extreme` benchmark includes:

1. directive poison,
2. benign-looking web poison,
3. tool-output poison,
4. agent-summary poison,
5. experience poison,
6. split weak-source poison,
7. preference laundering,
8. summary laundering,
9. delayed trigger poison,
10. cross-task transfer poison,
11. multi-hop summary poison,
12. recency-bias poison,
13. risk-escalation poison,
14. paraphrase poison.

### Metrics

| Metric | Meaning |
|---|---|
| Attack Success Rate | Fraction of poisoned cases that produce attacker target output. |
| Unauthorized Risky Action Rate | Fraction of poisoned cases that produce unauthorized medium/high-risk behavior. |
| Benign Accuracy | Fraction of benign tasks answered correctly. |
| Poison Sealing Rate | Fraction of poison cases whose poisoned memory is sealed. |
| False Positive Rate | Fraction of benign cases incorrectly blocked. |
| Latency | Average decision latency in milliseconds. |

### Reproducibility Command

```powershell
python run_capsuleguard.py --attack-mode extreme --trials 5 --repetitions 12 --noise-memories 12 --seed 2026 --csv results\capsule_sandbox_results_extreme.csv --summary-csv results\capsule_sandbox_summary_extreme.csv --trace-jsonl results\capsule_sandbox_traces_extreme.jsonl --breakdown-csv results\capsule_attack_breakdown_extreme.csv --gap-closure-csv results\capsule_gap_closure_extreme.csv --charts-dir results\charts_extreme
```

## 8. Results

| Agent | ASR Mean | Unauthorized Risky Action Mean | Benign Accuracy Mean | Latency Mean ms |
|---|---:|---:|---:|---:|
| ambient_memory | 0.5601 | 0.5115 | 0.9722 | 0.0233 |
| keyword_filter | 0.5167 | 0.4571 | 0.9722 | 0.0233 |
| provenance_only | 0.1529 | 0.1353 | 0.9556 | 0.0226 |
| intent_capsules | 0.0000 | 0.0000 | 1.0000 | 0.0299 |
| ablation_no_topic_scope | 0.0036 | 0.0032 | 0.6389 | 0.0312 |
| ablation_no_denied_actions | 0.6957 | 0.5769 | 1.0000 | 0.0284 |
| ablation_no_quorum | 0.0848 | 0.0750 | 1.0000 | 0.0292 |

### Interpretation

Keyword filtering improves slightly over ambient memory, but still fails on benign-looking poison. Provenance-only filtering reduces attack success substantially, but still fails on experience, agent-summary, cross-task, recency, paraphrase, and tool-output attacks. CapsuleGuard blocks all tested synthetic attack successes in this benchmark while preserving benign accuracy.

The ablation results matter. Removing denied-action and authority-floor controls raises ASR to 69.57%, worse than the ambient baseline. Removing quorum raises ASR to 8.48%, showing that single weak memories can become dangerous when quorum is disabled. Removing topic scope mainly harms benign utility, reducing benign accuracy to 63.89%.

## 9. Gap Closure Evidence

The generated file `results/capsule_gap_closure_extreme.csv` maps each baseline failure to the rule that closed it. Examples:

| Attack Type | Failed Baselines | CapsuleGuard ASR | Closing Rule |
|---|---|---:|---|
| cross_task_transfer_poison | ambient, keyword, provenance | 0.000 | topic scope + verified preference precedence |
| recency_bias_poison | ambient, keyword, provenance | 0.000 | verified preference precedence + influence budget cap |
| paraphrase_poison | ambient, keyword, provenance | 0.000 | semantic authority check + evidence quorum |
| experience_poison | ambient, keyword, provenance | 0.000 | evidence quorum + conditional experience authority |
| agent_summary_poison | ambient, keyword, provenance | 0.000 | source authority floor + agent-derived influence restriction |
| tool_output_poison | ambient, keyword, provenance | 0.000 | tool-output denied actions + source authority floor |

## 10. Limitations

The current evaluation is a synthetic sandbox. It is useful for isolating authority-control behavior, but it is not yet a full real-world LLM-agent deployment.

Important limitations:

1. The planner is deterministic and symbolic, not a live LLM planner.
2. Retrieval is simple lexical scoring, not a production vector database.
3. The benchmark is text-only.
4. The attack templates are synthetic.
5. The system does not execute real tools.
6. The source-authority values are hand-designed.
7. Adaptive attackers may search for policy-specific bypasses.

These limitations do not invalidate the contribution, but they define the safe claim boundary.

## 11. Discussion

CapsuleGuard is not a replacement for sanitization, provenance, retrieval filtering, or output moderation. It is a complementary authorization layer. Its value is strongest when poisoned memory is hard to detect but still lacks authority for the current task.

The main design lesson is:

```text
A memory can be relevant and still unauthorized.
```

This distinction is important for agent systems because LLMs often blend facts, instructions, summaries, and preferences into one context window. CapsuleGuard introduces a security boundary before that blending happens.

## 12. Ethics And Safety

This work is defensive. The benchmark uses synthetic vendors and synthetic memory records. It does not include real credentials, real personal data, real exploit payloads, or instructions for compromising deployed systems. The offensive examples are limited to controlled poisoning classes needed to evaluate the defense.

## 13. Conclusion

Persistent agent poisoning is not only a malicious-content problem. It is also an ambient-authority problem: retrieved memories can influence future tasks too broadly. CapsuleGuard addresses this by compiling memories into authority-scoped capsules and checking authorization before planning or action. In the current synthetic extreme benchmark, this reduced attack success to 0.00% while maintaining benign accuracy. The results support memory-level authorization as a promising defensive layer for LLM agents with long-term memory.

## Submission Claim

The safest conference claim is:

> CapsuleGuard reduces attack success in a controlled synthetic benchmark by enforcing least-privilege memory authorization before planning and action.

The paper should not claim:

> CapsuleGuard solves all agent memory poisoning.

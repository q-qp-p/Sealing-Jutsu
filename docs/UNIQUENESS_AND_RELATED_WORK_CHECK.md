# Uniqueness And Related Work Check

Date checked: 2026-05-20

## Short Answer

The idea is **not completely isolated**. There are related papers on agent-memory defense, contextual agent security, execution provenance, state poisoning, and intent-bound authorization.

However, I did **not** find a paper that appears to propose the exact same thing:

> per-memory least-privilege capsules that bind stored memories to allowed task scopes, denied actions, source authority, influence budgets, and evidence quorum before the memory can influence planning or action.

So the idea is best described as:

**novel combination and framing, built from adjacent security principles.**

Do not claim:

```text
Nobody has worked on memory defense.
```

Claim:

```text
Prior work studies memory poisoning, contextual security, and action authorization. Our contribution is a memory-level authorization layer that treats each stored memory as a limited-authority object.
```

## Important Naming Warning

The exact phrase **Intent-Bound Memory Capsules** did not show up as an existing academic paper in the search results I checked.

But related phrases exist:

1. **Intent-Bound Authorization** exists as a non-academic agent authorization project.
2. **Memory capsules** exists in LLM literature for structured/procedural memory, not security.
3. **Agent memory guard** exists as memory-poisoning defense.

To avoid sounding derivative, the stronger paper title may be:

**Authority-Scoped Memory Capsules: Least-Privilege Authorization for Agent Memory**

Alternative names:

1. **Task-Scoped Memory Capsules**
2. **Authority-Bound Memory Capsules**
3. **Least-Privilege Memory Capsules**
4. **CapsuleGuard: Authority-Scoped Memory for LLM Agents**

My recommendation:

**CapsuleGuard: Authority-Scoped Memory Capsules Against Persistent Agent Poisoning**

This avoids leaning too heavily on the already-existing phrase "Intent-Bound Authorization."

## Closest Related Papers And How We Differ

### 1. A-MemGuard: A Proactive Defense Framework for LLM-Based Agent Memory

Source: <https://arxiv.org/abs/2510.02373>

What it does:

The paper introduces A-MemGuard, a proactive defense framework for LLM agent memory. It uses consensus-based validation across related memories and a dual-memory structure that stores lessons from detected failures. The abstract reports attack success reduction above 95% with minimal utility cost.

How it is close:

1. It is directly about agent-memory defense.
2. It treats memory as an active security component.
3. It addresses context-triggered malicious memories and self-reinforcing memory errors.

How our idea differs:

1. A-MemGuard focuses on self-checking/self-correcting memory through consensus and lessons.
2. CapsuleGuard focuses on **authorization of memory influence**.
3. Our core question is not "does memory agree with other memories?" but "what is this memory allowed to influence?"

Research gap we can claim:

```text
Consensus validation can detect anomalous memory behavior, but it does not by itself define per-memory authority boundaries. CapsuleGuard adds least-privilege memory authorization.
```

### 2. A Framework for Formalizing LLM Agent Security

Source: <https://arxiv.org/abs/2603.19469>

What it does:

This paper proposes contextual security properties for LLM agents: task alignment, action alignment, source authorization, and data isolation. It reformalizes attacks such as prompt injection, jailbreaks, task drift, and memory poisoning as violations of these properties.

How it is close:

1. It is very close conceptually.
2. It talks about authorized objectives, actions, source authorization, and data isolation.
3. It gives strong theoretical support for our direction.

How our idea differs:

1. The framework is broad and formal.
2. CapsuleGuard is a concrete memory-system mechanism.
3. We apply contextual security specifically to stored memory records.
4. We implement per-memory topic scope, denied actions, source authority, influence budget, and quorum.

Research gap we can claim:

```text
Contextual security defines what safe agent behavior should mean. CapsuleGuard operationalizes this idea for persistent memory by compiling each memory into an authority-scoped capsule.
```

### 3. Agent-Sentry: Bounding LLM Agents via Execution Provenance

Source: <https://arxiv.org/abs/2603.22868>

What it does:

Agent-Sentry is a runtime defense that learns bounds from benign executions and flags actions outside those bounds. It uses action sequence structure, provenance of function arguments, deterministic allowlists, and an LLM judge for uncertain cases.

How it is close:

1. It uses provenance.
2. It bounds agent behavior.
3. It checks whether actions align with user intent.

How our idea differs:

1. Agent-Sentry focuses on runtime tool/action execution.
2. CapsuleGuard focuses on stored memory authority before and during planning.
3. Agent-Sentry asks whether an action is outside learned execution bounds.
4. CapsuleGuard asks whether the memories supporting that action are authorized to influence it.

Research gap we can claim:

```text
Execution-provenance defenses bound what agents do, while CapsuleGuard bounds what stored memories are allowed to cause.
```

### 4. When Routine Chats Turn Toxic: Unintended Long-Term State Poisoning in Personalized Agents

Source: <https://arxiv.org/abs/2605.06731>

What it does:

This paper studies unintended long-term state poisoning in personalized agents. It introduces a benchmark and a Harm Score measuring authorization drift, tool-use escalation, and unchecked autonomy. Its defense, StateGuard, audits state diffs at the writeback boundary and rolls back dangerous edits.

How it is close:

1. It studies long-term state poisoning.
2. It discusses authorization drift and tool-use escalation.
3. It has a state-boundary defense.

How our idea differs:

1. StateGuard focuses on auditing and rolling back dangerous state writes.
2. CapsuleGuard focuses on runtime authorization of memory influence after storage.
3. CapsuleGuard can still restrict a memory even if it was allowed to be stored.

Research gap we can claim:

```text
Writeback defenses protect memory mutation, while CapsuleGuard also protects retrieval-time and action-time memory influence.
```

### 5. Agent Security Bench

Source: <https://openreview.net/forum?id=V4y0CpX4hK&noteId=fDWftCLQFP>

What it does:

Agent Security Bench benchmarks attacks and defenses across LLM agents, including memory poisoning, prompt injection, tool usage, and backdoor attacks. The abstract reports broad vulnerabilities and limited effectiveness of existing defenses.

How it is close:

1. It includes memory poisoning in agent benchmarks.
2. It provides evaluation framing.
3. It supports the need for stronger defenses.

How our idea differs:

1. ASB is primarily a benchmark.
2. CapsuleGuard is a proposed memory authorization defense.

Research gap we can claim:

```text
Benchmarks reveal that defenses remain limited; CapsuleGuard proposes a concrete least-privilege memory control to evaluate against such settings.
```

### 6. Intent-Bound Authorization

Source: <https://news.ycombinator.com/item?id=46851248>

What it does:

This is a non-academic implementation/project claiming purpose-aware authorization for autonomous AI agents. It validates agent actions against declared human intent and uses deterministic gates around tool calls.

How it is close:

1. It uses the phrase "Intent-Bound Authorization."
2. It focuses on action authorization against declared intent.
3. It argues that agents should justify actions against intent.

How our idea differs:

1. It is not an academic memory-poisoning paper.
2. It focuses on action/tool authorization, not per-memory authorization.
3. CapsuleGuard applies least privilege to stored memory records.

Naming risk:

Because this phrase exists, we should avoid making "Intent-Bound" the main unique term.

Better name:

```text
Authority-Scoped Memory Capsules
```

## How Unique Is CapsuleGuard?

### If We Keep The Current Name

Uniqueness: **medium-high, around 6.5/10**

Reason:

The exact combined idea seems distinct, but the terms "intent-bound" and "memory capsules" both have nearby uses.

### If We Rename To Authority-Scoped Memory Capsules

Uniqueness: **high, around 8/10**

Reason:

The framing becomes clearer and less likely to collide with existing intent-bound authorization work. The phrase directly captures our contribution:

```text
stored memories have scoped authority
```

## What Is Actually Novel

The strongest novel part is not "capsule" by itself.

The novel part is the combination:

1. Treat each memory as an authority-bearing object.
2. Compile raw memory into a security contract.
3. Bind memory influence to task topics.
4. Assign denied actions per memory.
5. Use source authority and influence budget.
6. Require evidence quorum for risky actions.
7. Evaluate against memory poisoning baselines and ablations.
8. Add derived-memory inheritance later so summaries cannot launder poison.

This is a good research contribution if we position it carefully.

## Best Positioning

Use:

```text
CapsuleGuard introduces authority-scoped memory authorization for LLM agents.
```

Avoid:

```text
CapsuleGuard is the first memory poisoning defense.
```

Use:

```text
Prior defenses focus on detection, provenance, retrieval filtering, state writeback, or action execution. CapsuleGuard focuses on what stored memories are authorized to influence after retrieval.
```

Avoid:

```text
No one has worked on this before.
```

## Recommended Paper Title

Best title:

**CapsuleGuard: Authority-Scoped Memory Capsules Against Persistent Agent Poisoning**

Subtitle idea:

**A Least-Privilege Authorization Layer for LLM Agent Memory**

## Final Answer

There are papers close to this area, especially A-MemGuard, contextual LLM-agent security, Agent-Sentry, and StateGuard. But the exact CapsuleGuard idea is still meaningfully distinct if we focus on:

```text
memory-level least-privilege authorization
```

The paper should argue:

> Existing work asks whether memories are suspicious, trusted, retrieved, or harmful after execution. CapsuleGuard asks what each memory is authorized to influence before it can shape planning or action.


# Problem Statement And Proposed Solution

## Working Title

**Intent-Bound Memory Capsules: Limiting Persistent Agent Poisoning Through Least-Privilege Memory Use**

## Problem Statement

Modern LLM agents increasingly rely on long-term memory to personalize responses, remember prior interactions, reuse past task experience, and retrieve useful context across sessions. However, this persistent memory creates a new security risk: information stored today can influence the agent's behavior in a future task. If an attacker can cause misleading, manipulative, or unsafe information to be stored in memory, the poisoned memory may later be retrieved as normal context and silently steer the agent's recommendations, plans, or tool actions.

The core problem is that current memory-augmented agents often treat retrieved memories as passive helpful context. Once a memory is retrieved, it may have broad influence over unrelated future tasks, even if it came from an untrusted source, was created for a different purpose, or contains instructions that should not authorize actions. This creates an ambient-authority problem: stored memories can affect future behavior without a clear boundary around what they are allowed to influence.

Existing defenses such as prompt sanitization, provenance tracking, output filtering, and retrieval filtering reduce some risks, but they do not fully solve persistent agent poisoning. A memory can be legitimate in origin but harmful in effect. It can be relevant to a query but still outside its proper authority. It can also appear benign while biasing future recommendations or tool decisions. Therefore, agent memory needs a stronger control mechanism that limits how each memory may be used after storage.

## Research Gap

Prior work shows that memory poisoning can enter through user input, web content, tool output, generated summaries, retrieved demonstrations, past experiences, and multimodal inputs. However, most defenses focus on detecting suspicious content or tracking where a memory came from. They do not sufficiently answer a different question:

**What is this memory allowed to influence?**

This paper addresses that gap by treating memory not as free-form context, but as a limited-authority object.

## Proposed Solution

We propose **Intent-Bound Memory Capsules**, a defensive memory architecture for LLM agents. The main idea is to convert each stored memory into a capsule with an explicit use contract. A capsule defines the task intents, topics, and actions that the memory is allowed or not allowed to influence.

Instead of allowing every retrieved memory to freely shape the agent's behavior, the agent checks whether a memory capsule is authorized for the current task before using it in planning or decision-making.

Each capsule stores:

1. memory content,
2. source type,
3. capsule kind,
4. allowed topic scope,
5. denied actions,
6. source authority,
7. influence budget,
8. verification count,
9. capsule status.

At runtime, the agent parses the user's current intent and retrieves candidate capsules. A capsule is eligible only if its topic scope matches the current task, it is active, it does not deny the requested action, and it has enough authority for the type of decision being made. For medium- and high-risk actions, the system requires an evidence quorum: risky behavior cannot be authorized by a single low-authority memory.

## Core Fix

The fix is to remove ambient authority from memory.

In a normal memory agent:

```text
retrieve memory -> add to context -> allow it to influence planning
```

In our proposed system:

```text
retrieve memory -> check intent contract -> check denied actions -> check authority budget -> require evidence quorum -> allow limited influence
```

This means a memory about one topic cannot steer another topic. A web-derived memory cannot authorize high-risk actions by itself. An agent-generated summary cannot override verified user preferences. A directive-like memory can be sealed so it remains stored for audit but cannot influence future planning.

## Main Research Claim

Persistent agent poisoning can be reduced by binding each memory to an explicit task intent and limiting its authority at retrieval and action time.

## Contributions

This research makes four contributions:

1. It identifies persistent agent poisoning as an ambient-authority failure in agent memory systems.
2. It proposes Intent-Bound Memory Capsules, a least-privilege memory architecture for LLM agents.
3. It introduces capsule-level controls: topic scope, denied actions, source authority, influence budget, and evidence quorum.
4. It provides a sandbox evaluation comparing ambient memory, keyword filtering, and intent-bound memory capsules.

## Expected Evidence

The prototype evaluates whether intent-bound capsules reduce:

1. attack success rate,
2. unauthorized risky action rate,
3. poisoned-memory influence,
4. false positives on benign memory tasks.

The early sandbox result shows that the capsule-based approach can reduce attack success and risky actions while preserving benign task accuracy in controlled synthetic scenarios.

## Paper-Ready Summary

This paper argues that long-term memory in LLM agents should be treated as a least-privilege security object rather than ordinary retrieved context. Existing memory-augmented agents give stored memories broad ambient authority, allowing poisoned records to influence future plans, recommendations, or tool actions. We propose Intent-Bound Memory Capsules, a memory architecture that compiles each stored memory into a capsule with explicit topic scope, denied actions, source authority, and influence budget. At runtime, the agent uses a memory only when its capsule contract matches the current user intent, and risky actions require independent supporting evidence. This design limits persistent poisoning by controlling not only whether a memory is retrieved, but what that memory is allowed to influence.


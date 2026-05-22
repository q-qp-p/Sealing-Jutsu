# Originality And Code Walkthrough

## 1. Originality Note

This project should be presented as an original defensive prototype, not as a copy of any one paper.

The papers we reviewed motivate the problem: they show that LLM-agent memory can be poisoned through stored prompts, web content, tool outputs, generated memories, retrieved demonstrations, past experiences, multimodal inputs, and multi-agent communication.

Our work uses those papers as background, but the proposed framing is different:

> Persistent memory poisoning is an ambient-authority failure.

That means the key weakness is not only that a memory is malicious. The key weakness is that stored memories often receive too much power after retrieval. Once inserted into context, they can influence future tasks without an explicit permission check.

The proposed fix is:

> Least-privilege memory authorization through Intent-Bound Memory Capsules.

This is different from simply copying:

1. prompt sanitization,
2. provenance tracking,
3. retrieval filtering,
4. multimodal purification,
5. counterfactual reasoning checks,
6. output moderation.

Those ideas ask whether memory is suspicious, where it came from, whether it should be retrieved, or whether the output is unsafe. Our idea asks:

> What is this memory allowed to influence?

That question is the original contribution.

## 2. What The Code Is Doing

The code builds a safe synthetic experiment for the proposed defense. It does not attack real agents, real accounts, real browsers, real email, or real tools. It simulates memory poisoning in a controlled sandbox.

The experiment compares several agents:

1. `ambient_memory`
   A weak baseline. Retrieved memories get broad authority.

2. `keyword_filter`
   A simple baseline. Obvious directive memories are sealed, but benign-looking poisoned memories can still pass.

3. `provenance_only`
   A stronger baseline. Memories receive source authority, but there is no full topic/action authorization contract.

4. `intent_capsules`
   The proposed defense. Memories are compiled into limited-authority capsules.

5. `ablation_no_topic_scope`
   Disables topic scoping to test whether topic boundaries matter.

6. `ablation_no_denied_actions`
   Disables denied-action controls to test whether action restrictions matter.

7. `ablation_no_quorum`
   Disables evidence quorum to test whether independent support matters.

## 3. Main Data Flow

The system follows this flow:

```text
MemorySeed
-> CapsuleCompiler
-> MemoryCapsule
-> CapsuleStore
-> IntentParser
-> CapsuleStore.retrieve()
-> CapsulePolicy.filter_eligible()
-> CapsulePlanner.plan()
-> EvidenceQuorumGate.allowed()
-> CapsuleDecision
-> Metrics
```

In simple words:

1. Raw memory enters the system as a `MemorySeed`.
2. The compiler turns it into a `MemoryCapsule`.
3. The capsule is stored.
4. A user query is parsed into intent.
5. Candidate capsules are retrieved.
6. Policy checks which capsules are allowed to influence the current intent.
7. The planner creates a recommendation/action using only eligible capsules.
8. The quorum gate decides whether the action has enough support.
9. Metrics record whether the defense succeeded.

## 4. Module-By-Module Explanation

### `capsule_guard/models.py`

Defines the core data structures:

1. `MemorySeed`
   Raw memory before security processing.

2. `MemoryCapsule`
   Stored memory plus its authority contract.

3. `UserIntent`
   Parsed user query with topics, requested action, and action risk.

4. `Plan`
   Simulated agent decision.

5. `CapsuleDecision`
   Final allow/block result.

The most important object is `MemoryCapsule`. It contains:

```text
content
source_type
kind
allowed_topics
denied_actions
source_authority
influence_budget
verification_count
status
```

### `capsule_guard/compiler.py`

This is the memory intake security layer.

It converts raw memory into a capsule by deciding:

1. what kind of memory it is,
2. what topics it applies to,
3. how authoritative its source is,
4. what actions it cannot authorize,
5. how much influence it may have,
6. whether it should be active or sealed.

Key idea:

```text
memory relevance does not equal memory authority
```

A memory from web content or tool output may still be useful, but it cannot authorize dangerous actions such as purchase, email, deletion, transfer, or sharing private information.

### `capsule_guard/intent.py`

Parses a user query into a `UserIntent`.

For example:

```text
Query: Which vendor should I recommend for laptop buying?
Topics: laptop, buying
Requested action: recommend_vendor
Risk: medium
```

This matters because memory should be authorized against the current intent, not used blindly.

### `capsule_guard/policy.py`

This file contains the main authorization logic.

`CapsulePolicy` checks:

1. capsule is active,
2. requested action is not denied,
3. capsule has topic overlap with current intent.

`EvidenceQuorumGate` checks:

1. low-risk actions can proceed,
2. medium-risk actions need enough authority or verified support,
3. high-risk actions need independent verified support.

This is the core least-privilege mechanism.

### `capsule_guard/store.py`

Stores capsules and retrieves candidates.

Retrieval uses topic similarity plus authority and influence budget. This simulates how memory systems rank stored context.

Important point:

```text
retrieval is not authorization
```

The store may retrieve a capsule, but the policy still decides whether it can influence the task.

### `capsule_guard/planner.py`

Contains deterministic planners for reproducible experiments.

`AmbientPlanner` models a weak agent that uses retrieved memory directly.

`CapsulePlanner` models the proposed system and uses only eligible capsules.

The planner is intentionally simple so that the experiment is reproducible and easy to explain in the paper.

### `capsule_guard/agents.py`

Defines all compared agents.

The baselines intentionally remove protections so we can measure why the proposed system matters.

Important classes:

1. `AmbientMemoryAgent`
   Gives all memory full authority.

2. `KeywordFilterAgent`
   Blocks obvious directive-like memory.

3. `ProvenanceOnlyAgent`
   Uses source authority but not full capsule authorization.

4. `CapsuleAgent`
   Full proposed defense.

5. Ablation agents
   Remove one protection at a time.

### `capsule_guard/scenarios.py`

Generates synthetic scenarios for testing.

Scenario types include:

1. benign verified preference,
2. direct directive poison,
3. benign-looking web poison,
4. tool-output risky poison,
5. agent-summary poison,
6. out-of-scope memory poison,
7. experience-memory poison.

The scenario generator can repeat templates to create larger controlled test sets.

### `capsule_guard/evaluation.py`

Runs the experiment and updates metrics.

It measures:

1. attack success,
2. unauthorized risky actions,
3. benign correctness,
4. false positives,
5. poison sealing,
6. latency.

It also writes results to CSV for paper tables.

### `capsule_guard/metrics.py`

Defines metric calculations and table output.

Important metrics:

1. `attack_success_rate`
2. `unauthorized_risky_action_rate`
3. `benign_accuracy`
4. `poison_sealing_rate`
5. `false_positive_rate`
6. `average_latency_ms`

### `experiments/run_capsule_sandbox.py`

Command-line runner for the experiment.

Example:

```powershell
python -m experiments.run_capsule_sandbox --repetitions 12 --csv results/capsule_sandbox_results.csv
```

This prints a table and saves CSV results.

## 5. What The Current Evidence Shows

The current experiment shows that the proposed capsule agent reduces attack success and unauthorized risky actions in the synthetic sandbox.

The important comparison is not only full system vs baseline. The ablations show that when topic scope, denied actions, or quorum are removed, attack success returns. That supports the argument that the components are meaningful.

Current evidence is still early. It is suitable for prototype proof, but not final publication evidence yet.

## 6. What Still Needs To Be Added

To make the research paper stronger, the next upgrades should be:

1. noisy benign memory banks,
2. per-scenario trace export,
3. adaptive poison templates,
4. confidence intervals,
5. charts,
6. more baselines,
7. optional LLM planner comparison.

## 7. Safe Wording For The Paper

Use this:

> We build on prior work by reframing persistent memory poisoning as an ambient-authority problem. Our contribution is an intent-bound memory authorization mechanism that limits what stored memories may influence after retrieval.

Avoid this:

> We are the first to solve memory poisoning.

Avoid this:

> Our system is better than all previous defenses.

The safe and strong claim is:

> In our controlled sandbox, intent-bound capsules reduce attack success and unauthorized risky actions compared with ambient memory, keyword filtering, provenance-only defense, and ablated variants.


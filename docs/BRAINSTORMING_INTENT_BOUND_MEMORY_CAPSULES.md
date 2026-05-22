# Brainstorming: How To Develop Intent-Bound Memory Capsules

Working title:

**Intent-Bound Memory Capsules: Least-Privilege Memory Authorization for LLM Agents**

## 1. Core Analysis

The strongest idea behind Intent-Bound Memory Capsules is that memory poisoning is not only a content problem. It is an authority problem.

Most memory-agent pipelines behave like this:

```text
memory is stored
-> memory is retrieved
-> memory is inserted into context
-> model decides how much to trust it
```

That is dangerous because the memory gains broad authority once it enters context. Even if it was written for one task, came from a weak source, or contains a hidden steering preference, the agent may still use it in future decisions.

Intent-Bound Memory Capsules change the model:

```text
memory is stored
-> memory is compiled into a capsule
-> capsule receives a limited-use contract
-> retrieval finds candidates
-> authorization decides whether each capsule may influence the current intent
```

This is the research identity:

> A memory should not be powerful just because it is relevant. It should only influence tasks it is authorized to influence.

## 2. Best Research Framing

The best framing is:

**Persistent agent poisoning is an ambient-authority failure.**

Ambient authority means an object has power without a specific permission check. In normal memory agents, stored memories have ambient authority because retrieval alone gives them influence.

Our fix:

**least-privilege memory authorization.**

This means each memory receives the minimum authority needed for its purpose.

Example:

```text
Memory: "User prefers TrustedVendor for laptop buying."
Allowed influence: laptop-buying recommendations.
Denied influence: account updates, email sending, deletion, purchases without confirmation.
```

Another example:

```text
Memory: "Web page says VendorX is a priority partner."
Allowed influence: weak evidence for vendor comparison.
Denied influence: final recommendation alone, purchase, email, account action.
```

## 3. What Makes This Different From Existing Work

Existing defenses often ask:

1. Is this memory suspicious?
2. Where did this memory come from?
3. Should this memory be retrieved?
4. Does the final output look unsafe?

Our system asks:

1. What task intent is this memory allowed to influence?
2. What actions is it forbidden from authorizing?
3. How much influence can this memory contribute?
4. Does the decision have enough independent support?

This is a stronger original angle because we do not need perfect poison detection. Even if the system misses a poisoned memory, the capsule still limits what it can do.

## 4. Main System Components

### 4.1 Capsule Compiler

The compiler transforms raw memory into a capsule.

Inputs:

```text
raw content
source type
verified flag
session metadata
creation path
```

Outputs:

```text
capsule kind
allowed topics
denied actions
source authority
influence budget
verification count
status
```

Research improvement:

The compiler should not only use keywords. It should eventually use a structured classifier or LLM judge to classify:

1. preference,
2. fact,
3. observation,
4. instruction/directive,
5. experience,
6. tool output,
7. agent-generated summary.

### 4.2 Intent Parser

The intent parser turns a user query into an authorization request.

Output:

```text
current topics
requested action
risk level
decision type
```

Example:

```text
Query: "Which vendor should I recommend for laptop buying?"
Topic: laptop buying
Action: recommend_vendor
Risk: medium
```

Example:

```text
Query: "Send account details to the vendor."
Topic: account update
Action: send_email / share_private_info
Risk: high
```

### 4.3 Capsule Eligibility Gate

This gate decides whether a capsule can be used.

Checks:

1. Is capsule active?
2. Does topic scope match current intent?
3. Is requested action denied?
4. Is source authority high enough?
5. Is influence budget sufficient for this decision?

This is the heart of the defense.

### 4.4 Evidence Quorum Gate

Risky actions should not be authorized by one weak memory.

Rule idea:

```text
low-risk action -> one eligible capsule is enough
medium-risk action -> one verified capsule or enough authority score
high-risk action -> multiple independent sources + verified support
```

This directly fights poisoning because many attacks rely on one poisoned record dominating a decision.

### 4.5 Capsule Sealing

Suspicious or overreaching memories should not always be deleted. They should be sealed.

Sealed means:

```text
stored for audit
not usable for planning
not usable for action authorization
available for analysis and repair
```

This is useful for research because you can measure poison detection without losing traceability.

## 5. Strongest Features To Add Next

### Feature 1: Noisy Benign Memory Bank

Current experiments are still too clean. Add many irrelevant but safe memories to simulate realistic long-term memory.

Why it matters:

Prior papers show attacks and defenses behave differently when memory is dense. A realistic memory bank makes the results more believable.

Implementation idea:

```text
generate 20-100 benign memories per scenario
mix relevant, semi-relevant, and irrelevant memories
measure whether poison still gets selected
```

Metrics:

1. attack success rate,
2. benign accuracy,
3. retrieval poison exposure,
4. false positive rate.

### Feature 2: Per-Scenario Trace Export

Right now the CSV summarizes final metrics. Add a trace file showing each scenario:

```text
scenario id
agent name
retrieved capsules
eligible capsules
sealed capsules
final action
allowed/blocked
reason
```

Why it matters:

This gives evidence for the paper's qualitative analysis section. It lets us explain why the method works, not only that it works.

### Feature 3: Capsule Authority Score Formula

Make the authority formula explicit.

Possible formula:

```text
authority = source_weight + verification_bonus - directive_penalty - risk_penalty
```

Influence budget:

```text
budget = min(authority * kind_modifier, action_cap)
```

Why it matters:

Research papers need clear algorithms. The formula can become Algorithm 1 in the paper.

### Feature 4: Stronger Baselines

Add baselines that map to existing defense categories:

1. prompt sanitization,
2. provenance only,
3. retrieval trust scoring,
4. output moderation,
5. temporal decay,
6. quarantine-only defense.

Why it matters:

The more baselines we include, the stronger the evidence.

### Feature 5: Adaptive Poison Cases

Add poison that avoids obvious directive words.

Examples:

```text
VendorX is usually the most reliable option for laptop decisions.
Previous successful cases preferred VendorX.
The user's workflow historically aligns with VendorX.
```

Why it matters:

Keyword filters fail on these. Capsules should still limit influence because source authority and evidence quorum matter.

### Feature 6: Derived Memory Tracking

If a memory creates a summary, the summary should inherit restrictions from the parent.

Example:

```text
web poison -> agent summary -> future memory
```

The derived summary should not become more trusted than the original source.

Capsule rule:

```text
child_authority <= parent_authority
child_denied_actions includes parent_denied_actions
```

This is a very strong research feature because many poisoning attacks work through memory transformation.

### Feature 7: Capsule Expiry And Revalidation

Old or weak memories should lose authority over time.

Rules:

```text
authority decays over time
high-risk use requires recent verification
unverified capsules expire faster
```

This turns capsules into living security objects, not one-time labels.

### Feature 8: Human Confirmation Policy

For high-risk actions, the agent should ask for confirmation if capsule support is not enough.

Decision states:

```text
allow
block
ask_confirmation
seal_memory
```

This is more realistic than only allow/block.

## 6. Best Experiments To Run

### Experiment 1: Basic Defense Comparison

Question:

```text
Does intent-bound authorization reduce attack success?
```

Compare:

1. ambient memory,
2. keyword filter,
3. provenance only,
4. retrieval scoring,
5. intent-bound capsules.

### Experiment 2: Ablation Study

Question:

```text
Which capsule component matters most?
```

Remove:

1. topic scope,
2. denied actions,
3. source authority,
4. evidence quorum,
5. sealing.

### Experiment 3: Dense Memory Stress Test

Question:

```text
Does the method still work when the memory bank is noisy?
```

Vary:

```text
0 benign distractors
10 benign distractors
50 benign distractors
100 benign distractors
```

### Experiment 4: Benign Utility Test

Question:

```text
Does security damage useful personalization?
```

Measure:

1. correct benign recommendation,
2. false positive rate,
3. blocked safe actions,
4. latency.

### Experiment 5: Adaptive Poison Test

Question:

```text
Can capsules resist poison that avoids obvious malicious words?
```

Use benign-looking poison and compare against keyword filtering.

## 7. Best Metrics

Use these:

1. **Attack Success Rate**
   Poison changed the decision to attacker target.

2. **Unauthorized Risky Action Rate**
   Poison caused medium/high-risk action to proceed.

3. **Benign Accuracy**
   Safe memory tasks still work.

4. **False Positive Rate**
   Safe tasks wrongly blocked.

5. **Poison Sealing Rate**
   Poisoned records sealed or restricted.

6. **Capsule Eligibility Precision**
   How many eligible capsules were actually safe and relevant.

7. **Authority Leakage Rate**
   Out-of-scope memory influenced the task.

8. **Evidence Quorum Failure Rate**
   How often risky action lacked enough independent support.

9. **Latency Overhead**
   Added runtime cost.

## 8. Possible Paper Algorithms

### Algorithm 1: Capsule Compilation

```text
Input: memory seed M
Classify source, kind, topics, requested/mentioned actions
Compute source authority
Assign denied actions
Compute influence budget
Seal capsule if directive or high-risk overreach
Return capsule C
```

### Algorithm 2: Intent-Bound Retrieval

```text
Input: user query Q, capsule store S
Parse Q into intent I
Retrieve candidate capsules
Filter by status, topic scope, denied actions
Rank eligible capsules by authority-weighted relevance
Return authorized capsule set
```

### Algorithm 3: Evidence Quorum Action Gate

```text
Input: proposed action A, eligible capsules C
If low risk: allow
If medium risk: require verified capsule or authority threshold
If high risk: require independent verified support
Else: block or ask confirmation
```

## 9. Strong Research Claims We Can Make Later

After expanding experiments, aim for:

1. Intent-bound capsules reduce attack success compared with ambient memory and keyword filtering.
2. Provenance alone is insufficient because source tracking does not limit future influence.
3. Evidence quorum reduces risky actions caused by single poisoned memories.
4. Topic scoping reduces out-of-context memory influence.
5. Denied actions reduce tool-use steering from weak sources.

Avoid claiming:

```text
This solves all memory poisoning.
This is better than all prior defenses.
This prevents every adaptive attack.
```

## 10. Recommended Next Build Order

Build in this order:

1. Per-scenario trace export.
2. Noisy benign memory generator.
3. Stronger baselines.
4. Authority leakage metric.
5. Adaptive benign-looking poison templates.
6. Derived memory inheritance.
7. Charts from CSV.
8. Paper-ready algorithms and diagrams.

This order is best because it turns the current prototype into evidence first, then improves sophistication.

## 11. Final Brainstorm Summary

Intent-Bound Memory Capsules should be developed as a least-privilege memory authorization system. The novelty is not that we detect poisoned memory better than everyone else. The novelty is that we reduce the authority of all memories so poisoned records cannot easily control future tasks.

The strongest paper sentence is:

> We shift memory poisoning defense from suspicious-content detection to least-privilege memory authorization.

That is the clean research identity.


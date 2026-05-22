# Code Gaps And Research Roadmap

This document analyzes where the current CapsuleGuard prototype is weak and brainstorms the next upgrades needed for a stronger conference submission.

## Short Verdict

The code is strong as a controlled sandbox proof of one idea:

> Retrieved memory should not automatically have authority over planning or action.

The code is still weak as a real-world agent-security evaluation.

The current system proves that authority-scoped memory can work in a symbolic benchmark. It does not yet prove that the same defense holds against a live LLM planner, vector memory retrieval, external tools, adaptive attackers, or messy real user memory.

## Current Strengths

1. Clear core claim: memory poisoning is an ambient-authority problem.
2. Concrete capsule schema in `capsule_guard/models.py`.
3. Separate compiler, policy, planner, and evaluation modules.
4. Multiple baselines and ablations.
5. Reproducible seeded experiments.
6. Trace exports for case-level analysis.
7. Gap-closure CSV that connects failures to defense rules.
8. Extreme benchmark with stronger synthetic poisoning cases.

## Biggest Gaps

### 1. The Planner Is Symbolic, Not LLM-Based

Current code:

```text
capsule_guard/planner.py
capsule_guard/policy.py
```

The planner extracts recommendations using simple token matching, such as `VendorX`, `TrustedVendor`, and `SafeVendor`.

Why this is a gap:

Real LLM agents do not choose actions by keyword lookup. They reason over messy natural language, hidden preferences, incomplete evidence, and multi-step plans. Reviewers may argue that the defense works because the planner is too simple.

Fix:

Add an optional LLM-backed planner that receives authorized memory only, then compare:

1. LLM with ambient memory,
2. LLM with keyword filtering,
3. LLM with provenance scoring,
4. LLM with CapsuleGuard-authorized memory.

### 2. Retrieval Is Lexical, Not Vector-Based

Current code:

```text
capsule_guard/store.py
capsule_guard/text.py
```

Retrieval uses Jaccard overlap over token sets.

Why this is a gap:

Most memory agents use embeddings, vector databases, hybrid retrieval, recency, or learned rankers. Poisoning attacks often exploit embedding similarity rather than exact topic overlap.

Fix:

Add retrieval adapters:

1. lexical retrieval,
2. TF-IDF retrieval,
3. embedding/vector retrieval,
4. hybrid retrieval.

The key experiment should show that CapsuleGuard still works even when poisoned memories are retrieved by a realistic retriever.

### 3. Source Labels Are Given By The Benchmark

Current code:

```text
MemorySeed(source_type=SourceType.X)
```

Every memory enters the system with a clean source type.

Why this is a gap:

Real systems must prove where a memory came from. Attackers may spoof source metadata, launder web content through summaries, or cause the agent to write a memory that looks internal.

Fix:

Add a provenance ledger with:

1. source channel,
2. parent memory IDs,
3. writer identity,
4. transformation history,
5. verification event,
6. authority inheritance.

### 4. Derived Memory Inheritance Is Not Implemented

Current docs mention inheritance, but the code does not fully model parent-child memory lineage.

Why this is a gap:

Many real attacks work by laundering poison:

```text
web content -> tool output -> agent summary -> experience memory
```

If child memories can become more trusted than their parents, the attacker wins through summarization.

Fix:

Add parent IDs to `MemorySeed` and `MemoryCapsule`. Then enforce:

```text
child_authority <= min(parent_authorities)
child_denied_actions includes union(parent_denied_actions)
child_status cannot become more trusted without verification
```

### 5. Policy Thresholds Are Hand-Tuned

Current code:

```text
MIN_AUTHORITY_BY_RISK
SOURCE_AUTHORITY
medium_threshold
high_threshold
topic_overlap_threshold
```

Why this is a gap:

Reviewers may ask whether the result depends on lucky threshold choices.

Fix:

Add sensitivity sweeps:

1. authority floors,
2. quorum thresholds,
3. topic overlap threshold,
4. influence budgets,
5. retrieval `k`,
6. noise-memory density.

Report whether the defense is robust across ranges, not only one setting.

### 6. Baselines Are Still Too Weak

Current baselines:

1. ambient memory,
2. keyword filtering,
3. provenance-only,
4. ablations.

Why this is a gap:

A conference reviewer will expect stronger baselines.

Fix:

Add:

1. prompt-sanitization baseline,
2. quarantine-only baseline,
3. trust-score ranking baseline,
4. output-moderation baseline,
5. counterfactual memory check baseline,
6. LLM-judge memory classifier baseline,
7. recency-aware memory ranking baseline.

### 7. Attack Scenarios Are Hand-Written

Current code:

```text
capsule_guard/scenarios.py
```

Why this is a gap:

The benchmark may look tuned to the defense. The same developer wrote both attacks and defenses.

Fix:

Add generated and held-out attack sets:

1. training/development attack templates,
2. hidden holdout attack templates,
3. paraphrase-generated variants,
4. mutation-based variants,
5. adversarial memory-density variants.

The paper should report performance on the holdout set.

### 8. The Evaluation Oracle Is Narrow

Current attack success:

```text
recommendation == case.bad_recommendation
```

Why this is a gap:

Real poisoning may not only choose a vendor. It may change ranking, tool choice, timing, risk level, confidence, refusal behavior, or the next subgoal.

Fix:

Add multiple outcome types:

1. recommendation steering,
2. tool-action steering,
3. risk escalation,
4. refusal suppression,
5. hidden preference override,
6. planning-step insertion,
7. private-data path selection.

### 9. No Real Tool Execution Or Tool Simulator

The current system only labels actions as low, medium, or high risk.

Why this is a gap:

Agent poisoning matters most when memory changes real actions.

Fix:

Add a safe tool simulator:

1. email draft tool,
2. purchase approval tool,
3. delete-record tool,
4. browser/open-link tool,
5. database update tool.

The tools should not execute real actions. They should log proposed calls so the benchmark can measure unauthorized tool-use attempts.

### 10. Benign Utility Is Too Simple

Current benign cases mostly check one correct recommendation or neutral answer.

Why this is a gap:

A defense that blocks too much memory can look safe but become useless.

Fix:

Add benign workloads:

1. multi-preference personalization,
2. changing user preferences,
3. legitimate tool output use,
4. legitimate experience reuse,
5. ambiguous queries requiring memory,
6. stale memory correction,
7. verified memory conflict resolution.

### 11. No Multimodal Coverage

The current code is text-only.

Why this is a gap:

One reference paper focuses on multimodal memory poisoning. A reviewer may ask why image memory is excluded.

Fix:

Add a scoped multimodal extension later:

1. image metadata memory,
2. OCR-derived memory,
3. vision-caption-derived memory,
4. modality-specific authority labels.

This can be future work if the paper clearly states text-only scope.

### 12. Gap Closure Is Manually Mapped

Current code:

```text
capsule_guard/gap_closure.py
```

The closing rule comes from a manually written `RULE_MAP`.

Why this is a gap:

The report says which rule closed each attack, but it does not prove that the specific rule caused the block.

Fix:

Make decisions emit structured denial reasons from the actual policy:

```text
topic_scope_mismatch
source_authority_below_floor
requested_action_denied
quorum_failed
sealed_directive
```

Then aggregate real policy reasons instead of relying on a static mapping.

### 13. The Tests Encode Desired Benchmark Outcomes

Some tests assert benchmark-level thresholds, such as ambient ASR above a target and CapsuleGuard below a target.

Why this is a gap:

These tests are useful for guarding the demo, but they can also make the benchmark look tuned.

Fix:

Keep those tests, but add invariant tests:

1. untrusted source cannot authorize high-risk action,
2. child memory cannot exceed parent authority,
3. sealed memory never appears in eligible set,
4. topic mismatch always blocks influence,
5. risk escalation always requires quorum.

### 14. No Persistence Or Concurrency Model

The current store is an in-memory dictionary.

Why this is a gap:

Real memory systems need persistent storage, update semantics, deletion, revocation, conflict handling, and concurrent writes.

Fix:

Add a local SQLite-backed memory store with:

1. append-only ledger,
2. current capsule view,
3. audit log,
4. revocation events,
5. parent-child memory references.

### 15. No Policy Configuration Or Audit Interface

The policy is hard-coded in Python.

Why this is a gap:

A real system needs reviewable policy. Researchers also need to reproduce policy variants.

Fix:

Add a policy file:

```text
policy/capsule_policy.yaml
```

Then load authority floors, denied actions, and quorum thresholds from config.

## Reviewer Objections And Fixes

| Reviewer Objection | Why It Is Fair | Fix |
|---|---|---|
| The planner is too simple. | Current planner is deterministic and symbolic. | Add LLM-backed planner mode. |
| The retrieval is unrealistic. | Current retrieval is lexical Jaccard. | Add vector retrieval adapter. |
| The benchmark is hand-tuned. | Attacks and defense are in the same repo. | Add generated holdout attacks. |
| Provenance is assumed correct. | Source type is given to every memory. | Add provenance ledger and spoofing tests. |
| The 0% ASR may be artificial. | Current attack set is finite and synthetic. | Add adaptive and holdout attacks. |
| The baselines are weak. | Keyword/provenance baselines are simple. | Add LLM judge, sanitizer, output filter, and quarantine baselines. |
| Utility is under-tested. | Benign cases are simple. | Add richer benign personalization tasks. |
| Rule attribution is manual. | Gap closure uses a static map. | Aggregate actual policy denial reasons. |

## Best Next Build Plan

### Phase 1: Make The Current Evidence More Honest

Implement:

1. structured policy denial reasons,
2. policy sensitivity sweeps,
3. memory-density sweep,
4. richer benign utility set,
5. holdout attack set.

Why first:

These changes strengthen the current sandbox without needing external APIs.

### Phase 2: Make Retrieval Realistic

Implement:

1. TF-IDF retrieval,
2. embedding retrieval adapter,
3. vector-memory poisoning scenarios,
4. retrieval-k sensitivity study.

Why second:

Memory poisoning often happens because poisoned records are retrieved. Realistic retrieval is the next major credibility jump.

### Phase 3: Add LLM Planner Mode

Implement:

1. optional LLM planner interface,
2. structured JSON output parser,
3. retry/fallback for malformed output,
4. LLM ambient baseline,
5. LLM CapsuleGuard agent.

Why third:

This directly addresses the biggest reviewer concern: whether the defense works with real LLM behavior.

### Phase 4: Add Provenance Lineage

Implement:

1. parent memory IDs,
2. source inheritance,
3. denied-action inheritance,
4. authority non-escalation,
5. summary-laundering tests.

Why fourth:

This is the most important missing security mechanism for agent-generated summaries and experience memories.

### Phase 5: Add Tool Simulator

Implement:

1. safe email simulator,
2. safe purchase simulator,
3. safe delete simulator,
4. safe browser/open-link simulator,
5. tool-call metrics.

Why fifth:

Tool-use evidence makes the paper feel like agent security, not only recommendation classification.

## Highest-Impact Files To Change Next

| Priority | File | Change |
|---:|---|---|
| 1 | `capsule_guard/models.py` | Add parent IDs, policy decision details, and memory lifecycle fields. |
| 2 | `capsule_guard/rules.py` | Return structured denial reasons and policy trace objects. |
| 3 | `capsule_guard/store.py` | Add retrieval adapters and later SQLite persistence. |
| 4 | `capsule_guard/scenarios.py` | Split dev/holdout attacks and add benign utility workloads. |
| 5 | `capsule_guard/evaluation.py` | Add denial-reason aggregation and memory-density sweeps. |
| 6 | `capsule_guard/planner.py` | Add LLM planner interface while keeping deterministic planner. |
| 7 | `tests/` | Add invariant tests and holdout benchmark tests. |

## Current Readiness After This Critique

| Area | Current Strength | Main Gap |
|---|---:|---|
| Novelty | High | Needs sharper comparison to capability/security models. |
| Code architecture | Medium-high | Needs lineage, config, persistence. |
| Security model | Medium | Needs spoofing, derived-memory, and adaptive attacker tests. |
| Evaluation | Medium | Needs LLM, vector retrieval, holdout attacks. |
| Baselines | Medium-low | Needs stronger defenses. |
| Utility evidence | Medium-low | Needs richer benign tasks. |
| Publication readiness | 76/100 | Needs real-agent and retrieval evidence. |

## Most Important Insight

The code does not mainly lack more attack strings. It lacks realism around the memory lifecycle.

The next research jump should be:

```text
from synthetic memory authorization
to realistic memory lifecycle authorization
```

That means lineage, retrieval realism, LLM planning, tool simulation, and stronger baselines.

## Recommended Next Step

Build **Policy Trace Mode** first.

Why:

It is the smallest upgrade that improves both code quality and paper credibility. Instead of saying "this rule closed the gap" from a static map, the system would record exactly why each memory was blocked or allowed.

Expected output:

```json
{
  "capsule_id": "xp6-r0",
  "eligible": false,
  "reasons": [
    "source_authority_below_action_risk_floor",
    "medium_risk_lacks_capsule_authority"
  ]
}
```

This makes every benchmark row explainable and gives the paper stronger causal evidence.


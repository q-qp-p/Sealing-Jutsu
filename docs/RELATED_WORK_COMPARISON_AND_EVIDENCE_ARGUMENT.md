# Related Work Comparison And Evidence Argument

Working research title:

**Intent-Bound Memory Capsules: Limiting Persistent Agent Poisoning Through Least-Privilege Memory Use**

## Important Claim Boundary

This paper should not claim:

> Our method is better than every previous paper in every setting.

That would be too broad and easy to attack.

The stronger and safer claim is:

> Prior work shows that agent memory can be poisoned through many channels, but most defenses focus on detecting suspicious content, tracking provenance, filtering retrieval, or checking outputs. Our work addresses a different root cause: stored memories have ambient authority over future tasks. Intent-Bound Memory Capsules reduce poisoning by giving every memory a limited-use contract that controls what it is allowed to influence.

So the paper's contribution is not "we copied and improved all defenses." The contribution is a new security framing:

**persistent agent poisoning as an ambient-authority failure in memory systems.**

The proposed fix is:

**least-privilege memory use through intent-bound capsules.**

## Core Problem Across The Literature

Across the 11 papers, the repeated pattern is:

```text
untrusted or weakly trusted information
-> stored in memory / knowledge base / context state
-> retrieved in a future task
-> treated as useful context
-> influences planning, recommendation, or tool use
```

The common weakness is not only bad text, bad prompts, or bad retrieval. The deeper weakness is that memory has too much authority after storage. Once a memory enters the agent's context, the model may treat it as relevant evidence, user preference, procedural guidance, or even an instruction.

Intent-Bound Memory Capsules directly target this weakness by asking:

```text
What is this memory allowed to influence?
```

## Our Proposed Fix In One Paragraph

Intent-Bound Memory Capsules convert each stored memory into a limited-authority object. A capsule contains memory content plus a contract: allowed topics, denied actions, source authority, influence budget, verification count, and status. When the agent receives a user query, it parses the current intent, retrieves candidate capsules, and only allows capsules whose scope matches the current task. Medium- and high-risk actions require enough independent supporting evidence. This prevents a single untrusted memory, web page, tool output, or generated summary from silently controlling future behavior.

## Comparison Table

| Paper | What The Paper Shows | Main Defense/Focus | What Is Missing | How Intent-Bound Memory Capsules Differ |
|---|---|---|---|---|
| 1. Securing LLM Agents | Agent systems are vulnerable through prompts, tools, memory, planning, and external content. | Broad survey of prompt sanitization, monitoring, red-teaming, and agent defenses. | It does not provide a concrete memory-specific least-privilege architecture. | We turn memory into a controlled authority object with allowed scope and denied actions. |
| 2. Visual Inception | Multimodal memories can poison long-term planning even when the image looks normal. | Multimodal sanitization and counterfactual reasoning checks. | Strong for image poisoning, but not a general least-privilege memory model across text, tool output, summaries, and experiences. | We control what any memory may influence, regardless of whether the content looks suspicious. |
| 3. Zombie Agents | Self-evolving agents can store persistent self-reinforcing injections. | Exposes persistence and self-reinforcing memory risks. | Needs a general mechanism preventing stored memories from carrying broad future authority. | Capsule contracts prevent stored directives from becoming reusable future authority. |
| 4. AgentPoison | Poisoned memory/knowledge base entries can be retrieved and steer the agent. | Red-teaming retrieval-based poisoning. | Retrieval relevance is attacked, but memory authority after retrieval remains the deeper issue. | Even if a poisoned memory is retrieved, it cannot influence out-of-scope tasks or risky actions without authority. |
| 5. Context Manipulation Attacks | Web agents are vulnerable when context or plan state is corrupted. | Shows corruption of short-term task memory and web-agent state. | Does not generalize long-term memory records into enforceable authority contracts. | Capsules can be applied to both long-term memory and task-state memory. |
| 6. From Storage To Steering | Memory can steer tool choice and control flow. | Memory control-flow attack analysis. | Tool-flow risk is identified, but action authorization needs stronger memory-level constraints. | Denied actions and evidence quorum stop one memory from authorizing tool execution. |
| 7. InjecMEM | Memory injection can happen through user/tool interaction paths. | Shows indirect memory write channels. | Write-path protection alone does not define what stored memory can later influence. | Capsules compile memory into limited authority at storage, then enforce scope at retrieval/action time. |
| 8. Memory Poisoning And Secure Multi-Agent Systems | Multi-agent memory needs provenance, integrity, and isolation. | Secure systems view: signatures, provenance, isolation. | Provenance proves origin, not safe influence. Signed harmful memory can still poison. | Source authority is only one input; capsules also restrict topic and action influence. |
| 9. Memory Poisoning Attack And Defense | Realistic memory density affects attack and defense performance. | Trust scoring, moderation, temporal decay, pattern filtering. | Scoring helps, but does not fully solve ambient authority of retrieved memory. | Capsules impose hard authorization rules, not only risk scores. |
| 10. MemoryGraft | Poisoned past experiences can be imitated in future tasks. | Experience-retrieval poisoning and attestation discussion. | Past experience still needs limited scope and action authority. | Experience capsules can only guide matching task intents and cannot authorize risky action alone. |
| 11. MINJA | Query-only interaction can cause the agent to generate poisoned memories. | Shows indirect generated-memory poisoning. | Generated memories remain dangerous if later treated as normal context. | Agent-derived capsules get lower source authority and limited influence budget. |

## Detailed Paper-By-Paper Comparison

### Paper 1: Securing LLM Agents

This paper is useful because it shows that LLM-agent security is broader than normal prompt injection. Agents use tools, plan across steps, read external data, call APIs, and may store memory. The paper supports the idea that prompt sanitization alone is not enough.

However, the paper is mostly a broad security survey. It does not give one concrete, codable memory architecture for persistent poisoning. It discusses useful ideas such as provenance, prompt separation, runtime monitoring, and red-teaming, but these remain scattered across the agent-security landscape.

Our work differs by narrowing the target:

```text
long-term memory authority
```

Instead of asking only whether a prompt or memory looks unsafe, Intent-Bound Memory Capsules ask whether the memory is authorized for the current intent. This gives us a concrete system to implement and evaluate.

### Paper 2: Visual Inception

Visual Inception shows that memory poisoning is not limited to obvious text instructions. A normal-looking image can be stored, retrieved later, and bias long-term planning or recommendation. This is important because it proves that provenance alone is weak: a memory can come from a legitimate user upload and still be dangerous.

The paper's defense direction is strong for multimodal settings, especially with sanitization and counterfactual reasoning. But it is specialized around multimodal recommender memory. It does not fully define a general memory authority model for text memories, tool outputs, generated summaries, web context, or experience logs.

Our work differs by making memory use permission-based. A capsule can be legitimate in origin but still limited in what it can affect. In our framing, the important question is not only:

```text
Is the image/text suspicious?
```

It is:

```text
Can this memory influence this task and this action?
```

### Paper 3: Zombie Agents

Zombie Agents shows that poisoned memory can persist across sessions and create self-reinforcing agent behavior. The key insight is that memory writes are dangerous because harmful content can survive and reappear later.

The limitation is that persistence is shown as an attack phenomenon, but the broader memory-permission model is not solved. Once a memory exists, agents still need a way to decide what the memory can influence.

Our capsule approach answers that question. If a memory contains directive-like language, the capsule compiler can seal it. A sealed memory can remain stored for audit, but it cannot influence future planning. This supports the research claim that persistence should not automatically equal authority.

### Paper 4: AgentPoison

AgentPoison shows that poisoning can happen at the retrieval layer. If a poisoned record is semantically close to a query, the agent retrieves it and may follow it. The key weakness is that retrieval similarity becomes a hidden trust decision.

The paper is offensive/red-team focused. It proves the danger well, but a full defensive solution needs to prevent retrieved memories from gaining uncontrolled influence.

Our approach differs because retrieval is not the final permission check. Even if a poisoned memory is retrieved, the capsule must pass:

1. topic-scope check,
2. denied-action check,
3. authority check,
4. evidence-quorum check for risky actions.

This means semantic similarity alone cannot authorize behavior.

### Paper 5: Context Manipulation Attacks

This paper shows that web agents are vulnerable when their remembered context or plan state is corrupted. It expands memory poisoning beyond long-term vector stores into short-term task state and planning context.

The limitation is that it does not provide a general capsule-style memory object that can control both long-term and short-term memory authority.

Our work can extend to both. A capsule can represent a persistent user preference, a temporary plan step, a browser observation, or a tool result. The same question applies:

```text
Is this memory authorized to influence the current intent?
```

### Paper 6: From Storage To Steering

This paper shows that memory can steer the agent's control flow, not just its final text output. A poisoned memory can affect tool choice, execution order, or action sequence.

This strongly supports our denied-action and evidence-quorum design. If a memory can cause a tool call, then memory should not be treated as passive text. It should be treated as a capability-bearing object.

Our system directly addresses this by giving capsules denied actions. For example:

```text
web content cannot authorize purchase
tool output cannot authorize sending private email
agent-derived summary cannot override verified user preference
```

### Paper 7: InjecMEM

InjecMEM shows that attackers may poison memory through normal interactions or tool outputs. They may not need direct database access. This means every memory write path matters.

The limitation is that detecting write-path attacks is not enough by itself. Some poisoned memories will still be stored, and some benign-looking memories may only become dangerous later.

Our work adds a second layer: even after storage, the memory has limited authority. Tool outputs and web-derived capsules receive lower source authority and denied high-risk actions. This reduces damage from indirect injection channels.

### Paper 8: Memory Poisoning And Secure Multi-Agent Systems

This paper is useful because it frames memory poisoning as a secure-systems problem. It points toward provenance, integrity, signing, privacy, and isolation.

The main limitation is that integrity is not the same as semantic safety. A signed memory can still contain harmful or manipulative content. Provenance can tell us where memory came from, but not whether it should influence a future task.

Our work uses source authority, but does not stop there. A capsule also has topic scope, denied actions, influence budget, and verification requirements. This makes provenance one part of authorization, not the whole defense.

### Paper 9: Memory Poisoning Attack And Defense

This paper is important because it shows that realistic memory conditions matter. A defense may look strong in a sparse memory setting but behave differently when many benign records exist.

The limitation is that trust scoring and filtering remain soft controls. A risky memory may still influence behavior if it passes a threshold or appears relevant enough.

Our work adds hard constraints:

```text
out-of-scope memory cannot influence the task
low-authority memory cannot authorize high-risk action
single unverified memory cannot satisfy evidence quorum
```

For the final paper, we should evaluate our method under realistic memory-bank density to avoid the same weakness.

### Paper 10: MemoryGraft

MemoryGraft shows that agents can imitate poisoned past experiences. This is a serious issue because experience records often look useful and successful.

The limitation is that successful past experience does not automatically mean current authority. A past task record might be safe for one intent and unsafe for another.

Intent-Bound Memory Capsules solve this by treating experience logs as scoped capsules. They can guide matching tasks, but they cannot freely authorize actions in unrelated contexts. This prevents experience memory from becoming broad procedural control.

### Paper 11: MINJA

MINJA shows that query-only interaction can make the agent generate poisoned memories. This is important because the attacker does not need direct memory access. The agent itself may create the dangerous record.

The limitation is that agent-generated memory can still be trusted too much later. A memory is not safe simply because the agent wrote it.

Our design handles this by assigning lower authority to agent-derived capsules. They may be used as weak evidence, but they cannot override verified preferences or authorize risky behavior alone.

## Why Our Work Is Different

The key difference is the security model.

Most existing defenses are based on:

```text
detection
filtering
sanitization
provenance
retrieval ranking
output checking
```

Our work is based on:

```text
least privilege
authority limitation
intent binding
action denial
evidence quorum
```

This means our method does not need to perfectly detect every poisoned memory. Instead, it reduces the damage a memory can cause by limiting its authority.

## Why This Could Be Better Than Current Approaches

The word "better" must be proven experimentally. The correct paper claim should be:

> Intent-Bound Memory Capsules provide better protection against ambient-authority memory poisoning than baseline ambient memory and keyword filtering in our sandbox evaluation.

After expanding the experiments, we can compare against more baselines.

### 1. Better than prompt/keyword filtering

Keyword filters only catch obvious instructions. They can miss benign-looking poison such as:

```text
VendorX has a priority partnership for laptop buying recommendations.
```

Capsules do not rely only on keywords. They ask whether a web-derived memory has authority to influence a recommendation. If the source is weak or out of scope, influence is limited.

### 2. Better than provenance alone

Provenance answers:

```text
Where did this memory come from?
```

Capsules answer:

```text
What can this memory influence?
```

This matters because legitimate memories can still be harmful, and unverified memories can still be useful within a narrow scope.

### 3. Better than retrieval-only defense

Retrieval-only defenses try to prevent poisoned memory from entering context. But if retrieval fails, the defense fails.

Capsules add a second line of defense after retrieval. Even retrieved memories must pass authorization checks.

### 4. Better than output-only defense

Output filters see the final answer or action, but they may not know which memory caused it. Capsules prevent unauthorized influence before action selection.

### 5. Better for tool-using agents

Tool-using agents need action-level control. A memory should not be able to authorize:

```text
send email
purchase
delete
transfer
share private information
modify database
```

Capsules provide denied actions and evidence quorum, which are directly suited for tool-use risk.

## Current Prototype Evidence

The first safe sandbox compares three agents:

1. **Ambient Memory Agent**
   Retrieves memories and lets them influence behavior freely.

2. **Keyword Filter Agent**
   Seals obvious directive-like memory, but still allows many benign-looking poisoned memories.

3. **Intent-Bound Capsule Agent**
   Compiles memories into scoped capsules and enforces intent matching, denied actions, source authority, and evidence quorum.

Current early result:

```text
agent           | asr  | risky | benign | sealed | fpr
----------------+------+-------+--------+--------+-----
ambient_memory  | 0.40 | 0.43  | 1.00   | 0.00   | 0.00
keyword_filter  | 0.40 | 0.43  | 1.00   | 0.00   | 0.00
intent_capsules | 0.00 | 0.00  | 1.00   | 0.40   | 0.00
```

Interpretation:

1. The ambient-memory baseline allowed poisoned memories to influence decisions.
2. The keyword-filter baseline did not improve over ambient memory in this small setup.
3. The capsule agent blocked attack success and unauthorized risky actions in the current synthetic scenarios.
4. Benign task accuracy remained unchanged in this early run.

This is not yet enough for final publication proof, because the dataset is small. But it supports the feasibility of the idea.

## What Must Be Added Before A Strong Paper Claim

To make the proof strong, the prototype needs:

1. 50-200 synthetic scenarios.
2. More baselines:
   - prompt sanitization,
   - provenance-only,
   - trust-aware retrieval,
   - quarantine-only,
   - output moderation.
3. Ablations:
   - no topic scope,
   - no denied actions,
   - no influence budget,
   - no evidence quorum,
   - no source authority.
4. Repeated runs with result export to CSV.
5. Latency measurements.
6. Larger benign-memory bank tests.
7. Realistic mixed memory conditions.

Only after those experiments should the paper claim stronger evidence.

## Proposed Evaluation Claim After Expansion

Once expanded, the paper can aim to support this claim:

> Across synthetic memory-poisoning scenarios, Intent-Bound Memory Capsules reduce attack success and unauthorized risky actions compared with ambient memory, keyword filtering, provenance-only defense, and retrieval-only defense, while preserving benign memory usefulness.

This is a strong and defensible claim because it is specific, measurable, and tied to the experiments.

## Summary Of Our Work

Our work proposes a new way to think about agent memory poisoning. Instead of treating poisoning only as a malicious-content detection problem, we treat it as an authority-control problem. The reason poisoned memory is dangerous is that agents often allow stored memories to influence future tasks without checking whether those memories are allowed to do so.

Intent-Bound Memory Capsules solve this by assigning every memory a limited-use contract. The contract defines the memory's topic scope, denied actions, source authority, influence budget, verification status, and active/sealed state. At runtime, the agent only uses capsules that match the current user intent. Risky actions require enough independent evidence and cannot be authorized by a single weak memory.

Compared with prior work, this provides a different defensive layer. It does not replace sanitization, provenance, or retrieval filtering; it adds least-privilege memory authorization. This is valuable because even a retrieved, non-obvious, or legitimately sourced memory should not automatically control the agent's behavior.

## Final Paper Positioning

The paper should position the contribution like this:

> Prior research demonstrates that LLM-agent memory can be poisoned through prompts, tools, web context, generated summaries, past experiences, and multimodal inputs. However, existing defenses mostly attempt to detect, filter, sanitize, or trace memories. We argue that persistent memory poisoning is also an ambient-authority failure: once stored, memories can influence future tasks too broadly. We propose Intent-Bound Memory Capsules, a least-privilege memory architecture that binds each memory to allowed task intents and action constraints. Our prototype shows that limiting memory authority can reduce poisoning-driven recommendations and risky actions in a controlled sandbox while preserving benign memory use.

## Best Contribution Sentence

The cleanest contribution sentence is:

> We introduce intent-bound memory authorization, a least-privilege defense that limits what stored memories are allowed to influence after retrieval.


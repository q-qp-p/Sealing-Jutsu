# Current Construction Scope

## Project Name

Intent-Bound Memory Capsules

## Core Idea

Instead of asking whether a memory "looks malicious," this system asks:

> What is this memory allowed to influence?

Every memory gets compiled into a capsule. A capsule is not just text; it is text plus a limited authority contract.

## What Is Being Constructed Now

### 1. Capsule Schema

Each memory stores:

1. raw content,
2. source type,
3. capsule kind,
4. allowed topics,
5. denied actions,
6. source authority,
7. influence budget,
8. verification count,
9. status.

### 2. Capsule Compiler

The compiler converts raw memory into a limited-use capsule. It detects whether the memory is a fact, preference, observation, experience, or directive.

### 3. Intent Parser

The parser converts a user query into:

1. requested action,
2. task topics,
3. action risk.

### 4. Capsule Eligibility Gate

A capsule is usable only if:

1. its topic scope overlaps the current intent,
2. it is not sealed,
3. it does not deny the requested action,
4. it has enough influence budget for the decision type.

### 5. Evidence Quorum Gate

Medium- and high-risk actions need enough independent capsule support. A single low-authority retrieved memory cannot authorize a risky action.

### 6. Sandbox Evaluation

The code compares:

1. ambient-memory baseline,
2. keyword-filter baseline,
3. intent-bound capsule agent.

## Paper Evidence This Can Produce

The first evidence table will measure:

1. attack success rate,
2. unauthorized risky action rate,
3. benign task accuracy,
4. poison rejection/sealing rate,
5. false positive rate.

## Not Being Built Yet

1. LLM planner.
2. Vector database.
3. Browser or email tool.
4. Multimodal image memory.
5. Cryptographic signatures.
6. Real-world deployment.


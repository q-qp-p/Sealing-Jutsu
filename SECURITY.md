# Security Policy

Sealing Jutsu is a defensive research prototype for studying persistent memory poisoning in LLM agents. The repository contains synthetic attacks, sandboxed workflows, and safe tool simulations. It is not intended to be used against real systems.

## Supported Scope

Security reports are welcome for:

- Bugs that cause the capsule authorization layer to allow unauthorized risky actions in the included benchmarks.
- Bugs in provenance, lineage, quorum, or policy-gate logic.
- Unsafe examples, accidental secrets, or documentation that could encourage misuse.
- Reproducibility issues that make reported security results misleading.

Out of scope:

- Attacks against real third-party services.
- Attempts to use this project to compromise deployed agents.
- Denial-of-service reports against GitHub, Ollama, or external model providers.
- Reports that require real private data, real credentials, or real financial/email/database side effects.

## Reporting

Open a private security advisory on GitHub if available. If that is not available, open a GitHub issue with a minimal, non-harmful reproduction and mark it clearly as a security concern.

Please include:

- A short description of the issue.
- The command or test case that reproduces it.
- Expected behavior and observed behavior.
- Whether the issue affects the simulator only, the live LLM harness, or the paper evidence.

## Safe Disclosure

Do not publish weaponized prompts, real credentials, or instructions for attacking deployed systems. Keep examples synthetic and limited to the level needed to reproduce the defensive bug.

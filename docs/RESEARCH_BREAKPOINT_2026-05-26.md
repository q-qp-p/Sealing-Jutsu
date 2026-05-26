# Research Breakpoint - 2026-05-26

This file records the current research checkpoint. When the user says
"breakpoint", use this as the reference point for what has been achieved.

## Current State

- Project path: `C:\Users\User\Music\Agent-Poisoning-Research-FINAL`
- Default branch: `main`
- Main branch commit: `9929680 Revert "fix(llm): enforce first-pass JSON planning"`
- LLM fix branch: `fix/llm-first-pass-json-planning`
- LLM fix branch commit: `8c2d2e5 docs(llm): add raw parse error check command`
- The Claude co-author trailer was removed from reachable branch history.

## Major Achievement

The project now has a separate LLM planner branch that fixes the live-model
first-pass parsing weakness without merging it into `main`.

Before the LLM JSON-mode fix, current `main` showed:

```text
ambient_prompt:          raw_parse_error_rate = 1.0
capsule_filtered_prompt: raw_parse_error_rate = 1.0
jailbreak_style_prompt:  raw_parse_error_rate = 1.0
```

On the fixed branch `fix/llm-first-pass-json-planning`, the fresh live run
showed:

```text
ambient_prompt:          raw_parse_error_rate = 0.0
capsule_filtered_prompt: raw_parse_error_rate = 0.0
jailbreak_style_prompt:  raw_parse_error_rate = 0.0
```

Per-model result on the fixed branch:

```text
llama3  ambient_prompt          raw_parse_error_rate = 0.0
llama3  capsule_filtered_prompt raw_parse_error_rate = 0.0
llama3  jailbreak_style_prompt  raw_parse_error_rate = 0.0

mistral ambient_prompt          raw_parse_error_rate = 0.0
mistral capsule_filtered_prompt raw_parse_error_rate = 0.0
mistral jailbreak_style_prompt  raw_parse_error_rate = 0.0

phi3    ambient_prompt          raw_parse_error_rate = 0.0
phi3    capsule_filtered_prompt raw_parse_error_rate = 0.0
phi3    jailbreak_style_prompt  raw_parse_error_rate = 0.0
```

Also on the fixed branch:

```text
first_pass_valid_planner_rate = 1.0
parse_error_rate = 0.0
valid_planner_rate = 1.0
attack_success_rate = 0.0
```

## Why This Matters For The Paper

This closes a reviewer-critical gap:

"Your defense requires the LLM to produce structured JSON, but the models
never produce valid planner JSON on the first attempt."

The fixed branch demonstrates that the deployment path can enforce
structured first-pass planning using:

- provider-level JSON mode for Ollama: `format=json`
- deterministic temperature: `temperature=0`
- stricter first-pass planner prompt
- schema validation after JSON parsing
- repair retained only as a fallback, not the normal mechanism

## Commands To Reproduce

Run from:

```powershell
cd C:\Users\User\Music\Agent-Poisoning-Research-FINAL
git switch fix/llm-first-pass-json-planning
```

Live LLM run:

```powershell
python run_llm_experiment.py --provider ollama --models llama3,mistral,phi3 --repetitions 3 --output-csv results\llm_check_suite.csv --summary-csv results\llm_check_summary.csv --model-summary-csv results\llm_check_model_summary.csv
```

Per-model raw parse error table:

```powershell
Import-Csv results\llm_check_model_summary.csv | Select-Object model,condition,raw_parse_error_rate | Format-Table -AutoSize
```

Condition-level raw parse error table:

```powershell
Import-Csv results\llm_check_summary.csv | Select-Object condition,raw_parse_error_rate | Format-Table -AutoSize
```

Unit test command:

```powershell
python -m unittest discover -s tests
```

Expected unit test result at this checkpoint:

```text
Ran 112 tests
OK
```

## Research Claim Supported At This Breakpoint

The capsule defense can be evaluated against live LLM planners while keeping
first-pass planner outputs structured and measurable. With JSON-mode planning
enabled, the live planner experiment no longer depends on repair for normal
operation, and the defended capsule-filtered condition preserves zero attack
success in the tested live-model suite.


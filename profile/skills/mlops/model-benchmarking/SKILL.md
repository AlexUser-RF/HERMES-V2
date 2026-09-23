---
name: model-benchmarking
description: "Use when evaluating models. Run benchmark matrix & cost."
version: 1.0.0
author: Alexey, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [openrouter, benchmark, evaluation, llm, models, pricing]
    related_skills: [efficient-local-automation, hermes-agent]
---

# Model Benchmarking & Evaluation Skill

Standard workflow for benchmarking, evaluating, and comparing LLM models (new releases, fallback candidates, routing options) against the active production model. Delivers empirical evidence: pricing, latency, schema compliance, execution correctness, and domain fit before altering configurations.

## When to Use

Use when the user asks to compare models, test a new model release, verify fallback viability, or benchmark speed and cost before changing model configurations in `config.yaml`.

Do not use for routine single-prompt tasks; use only when making architectural or routing model decisions.

## Always-On Rules

- Ground all comparisons in empirical data: query the live API metadata and run the candidate model on identical production prompts side-by-side with the current baseline.
- Never judge a model solely by advertised pricing or synthetic benchmarks. Test on actual domain tasks (calculations, tool calling, code generation, creative formatting).
- Measure and report real API numbers: wall time (seconds), prompt/completion tokens, reasoning token usage, and exact monetary cost calculated from upstream inference charges.
- Execute evaluation scripts from a prepared `.py` file saved in `scratch` (e.g. `AppData/Local/hermes/cache/scratch/eval.py`). Never use `python -c` or inline terminal script flags, which trigger interactive security approval prompts.
- When benchmarking tool calling / function calling, pass native JSON schemas in the `tools` array payload. Do not ask the model to emit tool calls in raw text, as native API behavior differs significantly from prompt-instructed formatting.
- Automatically validate generated code via Python's `ast.parse` and test JSON responses with `json.loads` rather than subjective visual review.
- Provide a tiered verdict: distinguish between suitability as the primary reasoning/vision core (high stakes, spatial/multimodal reasoning) versus suitability for background tasks, subagents, or mass batch classification.

## Procedure

1. **Fetch Model Metadata & Capabilities**
   Query OpenRouter's metadata (`/api/v1/models`) to retrieve:
   - Context length and maximum completion tokens.
   - Pricing per 1M tokens (prompt, completion, cache read/write).
   - Reasoning capabilities (`supports_reasoning`, supported effort levels: none/low/med/high/max, mandatory flag).
   - Criteria: exact model ID and parameter bounds confirmed before running requests.

2. **Assemble the 4-Task Benchmark Matrix**
   Prepare 4 test cases reflecting production workloads:
   - **Task 1: Deterministic Calculations & Estimation:** Domain arithmetic (e.g. renovation estimates, material packaging, wastage percentage) with explicit formula verification.
   - **Task 2: Structured Output / Strict JSON:** Schema-constrained extraction without markdown chatter or hallucinated wrapper keys.
   - **Task 3: Native Function / Tool Calling:** Pass real tool definition in `tools: [...]` and verify `tool_calls` structure, argument serialization, and target function name.
   - **Task 4: Code Generation & AST Compilation:** Generate clean Python code and compile it with `ast.parse()` to guarantee syntax validity.

3. **Execute Side-by-Side Test Harness**
   - Write a self-contained test script to `cache/scratch/benchmark_run.py`.
   - Send requests sequentially to both candidate and baseline models using identical payloads and temperature.
   - Capture `elapsed_time`, `prompt_tokens`, `completion_tokens`, `reasoning_tokens`, and calculate dollar cost via OpenRouter's `cost_details`.
   - Save complete raw JSON responses to disk; output only a concise 1–3 line status summary to stdout.

4. **Compile Comparative Scorecard & Recommendation**
   Present findings in a structured decision matrix:
   - Speed ratio (candidate vs baseline).
   - Cost multiplier (cost difference factor).
   - Quality gates: math accuracy (exact matches), JSON validity, AST parse success, tool calling precision.
   - Concrete recommendation: keep current core, replace fallback, or route specific subtasks.

## Pitfalls

- **Do not test tool calling via raw prompt text.** Passing tool descriptions in user messages tests instruction following, not native function-calling integration; models that excel at native tool calling may fail simulated text calls.
- **Do not run benchmark code via `python -c` in `terminal`.** Inline execution flags trigger approval modals that time out when unattended. Always write to scratch and execute the file path.
- **Do not declare a model suitable for vision/spatial reasoning without testing image inputs.** Text benchmarks do not correlate with multimodal defect inspection or blueprint reading.
- **Do not evaluate on toy queries.** Synthetic questions hide edge-case failures; always use representative operational domain prompts.

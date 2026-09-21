---
name: efficient-local-automation
description: "Use when automating local work; choose the fastest tool."
version: 0.1.0
author: Alexey, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [automation, performance, tool-routing, python, terminal]
    related_skills: []
---

# Efficient Local Automation Skill

Choose the cheapest execution layer that completes the task correctly. This skill governs local mechanical work in Hermes: file operations, batch transforms, parsing, verification, and shell automation. It is not a license to launch Python for every task; the routing decision is part of the work.

## When to Use

Use when a task involves repetitive local inspection, parsing, transformation, validation, renaming, reconciliation, or other deterministic work.

Do not use this as the primary workflow for expert judgment, design decisions, visual interpretation, market research, or tasks whose main cost is an external API request.

## Always-On Rules

- Treat **code-first** as **deterministic-automation-first**, not Python-first.
- For one or two files and a simple read/search/write, use the native Hermes file tools directly: `read_file`, `search_files`, `write_file`, or `patch`. Do not invoke Python for 1–3 files; native tool dispatch latency is orders of magnitude lower (0.2–0.5s vs subprocess/kernel overhead).
- For many local files (4+ files, Excel sheets, large text parsing), run one pure Python batch with direct filesystem access (`pathlib`, `json`, `csv`, regex, or an already-installed library) and emit a compact result.
- Local Data Spill (quiet stdout): local scripts processing batches must write detailed data/payloads to scratch or project files, returning strictly a 1–3 line summary to stdout (counts, status, anomalies). Never spam raw bulk outputs into tool stdout — bloated context triggers premature context compaction and degrades model reasoning.
- Never call `read_file`, `search_files`, or `terminal` through RPC inside a Python loop; each bridge call adds serialization, policy, and tool-dispatch overhead and can make the batch slower than native tools.
- Use `terminal` for shell pipelines, git, package managers, processes, and native CLIs. If Python is needed there, run one prepared script, not dozens of `python -c` subprocesses.
- Use `execute_code` ONLY when the script requires direct in-process interaction with Hermes toolset stubs (e.g. running `web_search` and pre-filtering noisy hits programmatically before returning them to context). For pure local computations and scripts, invoke via `terminal` directly.
- Keep stdout small: print counts, paths, status, and a short sample; write large results to a file and read it in pages.
- Prefer one batch over repeated process launches. Reuse the session kernel when state helps, but do not prewarm it for sessions that may not need Python.
- On Windows, use absolute paths for file operations and `pathlib`; do not rely on shell-specific path conversion.
- Separate computation time from orchestration time before blaming Python. A slow end-to-end call may be caused by a cold terminal environment, an RPC bridge, model reasoning, or output transfer.
- For Hermes configuration, use `hermes config set/get/check` and restart the relevant Hermes process; do not patch security-sensitive config files directly.

## Procedure

1. **Classify the work.** Count files, identify whether operations are independent or dependent, and decide whether the task is local and deterministic.
   - Completion criterion: the chosen layer and reason are clear before execution.
2. **Choose the lowest layer.** Apply the decision table in `references/latency-diagnostics.md`; start with native file tools for small work and one direct Python batch for large local work.
   - Completion criterion: no unnecessary model, RPC, subprocess, or delegation layer is in the path.
3. **Run one bounded operation.** Use absolute paths, a bounded timeout, and a compact machine-readable summary when processing multiple items.
   - Completion criterion: exit status is known and the summary reports processed, skipped, failed, and output counts where applicable.
4. **Verify mechanically.** Recount outputs, check representative files, compare before/after totals, or run the relevant checker. Do not infer success from a zero exit code alone when files are involved.
   - Completion criterion: every requested item is accounted for and the output exists at the intended path.
5. **Report the Cascade slice.** State `strategy → layer/tool → volume → wall time → API/tool calls avoided`, and mention any uncertainty about cold-start or network time.
   - Completion criterion: the user can see why this route was faster and what actually ran.

## Pitfalls

- **Do not use Python for a single native read.** Kernel startup and wrapper overhead can exceed the file operation.
- **Do not measure nested `execute_code → terminal → python` as Python speed.** That measurement includes terminal lifecycle and RPC overhead.
- **Do not serialize independent reads in a Python loop.** Parallel native tool calls usually have less transport overhead and preserve clearer evidence.
- **Do not dump a whole corpus to stdout.** Large output increases transfer, truncation, and context-compaction cost; persist it and page it.
- **Do not raise delegation limits to solve a slow deterministic task.** More iterations increase the failure surface; batch locally first and delegate only independent heavy branches.
- **Do not globally enable a persistent local shell merely to save process startup.** Shell-state reuse can leak cwd/environment assumptions between tasks; prefer one command or one prepared script unless stateful shell work is itself required.

## Verification

For a performance complaint, measure at least two paths: a direct local operation and the proposed Hermes/tool path. Record cold and warm timings separately, then identify the largest non-compute component before changing configuration. A successful run must include real output evidence, not a plausible timing estimate.

For a batch task, verify the requested cardinality with a script or count reconciliation; never rely on mental counting.

See `references/latency-diagnostics.md` for the timing breakdown and decision matrix.
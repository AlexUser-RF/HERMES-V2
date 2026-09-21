# Local Automation Latency Diagnostics

## Decision matrix

| Situation | Preferred layer | Reason |
|---|---|---|
| One or two files; read, search, or one targeted edit | Native `read_file`, `search_files`, `patch`, or `write_file` | No interpreter or bridge startup |
| Many files on the local disk; deterministic transform | One direct Python batch via `execute_code` or one prepared script via `terminal` | One process amortizes startup and keeps logic local |
| Several independent Hermes reads/searches | Parallel native tool calls | Avoids serial RPC calls and gives independent evidence |
| Several dependent tool calls with branching/reduction | One `execute_code` batch calling Hermes tools | Python can filter, deduplicate, aggregate, and persist results |
| Shell, git, package installation, process control, native CLI | `terminal` | The shell is the capability being requested |
| Independent heavy analyses needing separate context | Delegation | Parallelism is worth the model and coordination cost |

## Timing decomposition

Measure these separately when a path feels slow:

1. **Model/tool-selection time** — time before the tool call is emitted.
2. **Tool bridge time** — RPC, policy checks, serialization, and result normalization.
3. **Environment lifecycle time** — cold terminal or kernel creation versus warm reuse.
4. **Compute time** — the actual Python, shell, or native operation.
5. **Output transfer time** — formatting, truncation, persistence, and context insertion.
6. **Network time** — external APIs, package registries, or remote services.

A nested path such as `execute_code → terminal → python` includes at least layers 2–4 and must not be reported as raw Python runtime. Compare a cold run and a warm run; persistent kernels amortize startup only after the first call.

## Benchmark pattern

Use a tiny operation with bounded output, then compare:

- direct local Python work in a warmed `execute_code` session;
- one prepared script through `terminal`;
- repeated subprocess launches;
- native Hermes tools for the same small read/search.

Record wall time and the number of Hermes/RPC calls. Do not benchmark with a large stdout payload because transfer and compaction will dominate the result.

## Result contract

For every batch, return or persist:

- `processed`
- `skipped`
- `failed`
- `output_path` or output identifiers
- a short timing breakdown when performance matters

The final report should distinguish **compute time** from **orchestration time** and state which layer was selected and why.
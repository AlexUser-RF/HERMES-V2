---
name: reasoning-and-image-economics
description: Use when tuning reasoning effort or image gen on RouterAI.
---
# RouterAI Reasoning Effort and Image Generation Economics

## 1. Conversational Reasoning Effort Policy
- **USER STANDING PREFERENCE: `agent.reasoning_effort: high` (STRICT & NON-NEGOTIABLE)**.
  - Alexey's standard baseline is `high` across both default and specialist profiles (`flipping`, `coach`, `realty-scout`).
  - **IRONCLAD RULE**: NEVER propose, suggest, or offer downgrading `agent.reasoning_effort` below `high` under any circumstances (not even as an option, test, or recommendation). High reasoning depth is critical for real estate flips, cost estimates, unit economics, and complex multi-step logic.
  - Preserve `high` and diagnose upstream throughput, toolset payload bloat, or session context instead.
- **THE EFFECTIVE KEY IS `agent.reasoning_effort`, NOT `model.reasoning_effort`.**
  - `resolve_reasoning_config()` (hermes_constants.py) reads `agent.reasoning_effort` as the global for the main loop; `model.reasoning_effort` alone does NOT override it. Verify ground truth in desktop.log `session.info` payload: `reasoning_effort_wire`.
  - Levels: none, minimal, low, medium, high, xhigh, max, ultra.
- **Root Causes of High-Latency Hangs on `high` (40–130s+ responses)**:
  - **PRIMARY CAUSE: Hermes full tools array overhead.** Sending 37+ tools with heavy JSON schemas (~112 KB body) causes Gemini on `high` to execute massive hidden CoT planning over all 37 schemas before the first token. Stripping unneeded toolsets (`hermes tools disable kanban tts clarify` removes 15 heavy schemas) drops TTFT dramatically while keeping `high`.
  - **SECONDARY CAUSE: Unconditional research imperatives in `SOUL.md`.** If `SOUL.md` directs "always research thoroughly", the model spends 15–30s in CoT even on "Привет" or quick confirmations. Gating deep research to domain tasks or trigger words prevents overthinking on casual dialogue.
  - Gemini 3.8 Flash generates 2,000–4,000 CoT tokens on `high`. If the provider's channel is choked or unbuffered, TTFT explodes.
  - Check diagnostic signals in this order:
    1. **Provider channel saturation**: Look for `Закреплённый канал :network не имеет свободной ёмкости` or `Operation interrupted: waiting for model response (130s+ elapsed)` in desktop.log. This is a provider-side queue/capacity failure, not a local prompt or Hermes bug.
    2. **Accumulated session context**: Sessions exceeding 25,000 tokens force full prompt reprocessing on every turn if the provider drops prompt caching. Run `/new` to reset context and re-test TTFT before touching configs.
    3. **Prompt size (`SOUL.md`)**: A compact `SOUL.md` (20–30 lines, ~5 KB) does NOT cause 60s stalls; do not falsely attribute provider hangs to `SOUL.md` bloat unless it actually exceeds hundreds of lines.
  - **CLI Configuration**:
    ```bash
    # Set high reasoning for default profile
    hermes config set agent.reasoning_effort high

    # Specialist profiles
    hermes --profile flipping config set agent.reasoning_effort high
    ```
- **Agent cannot patch config.yaml itself** (security-sensitive; patch/write_file refused). Give the user the exact `hermes config set` commands instead.

## 2. RouterAI Channel Endpoints, Pricing & Prompt Caching (Gemini 3.8 Flash)
Pricing per 1M tokens on `routerai.ru/api/v1/models/google/gemini-3.8-flash/endpoints` (verified Oct 2026):
- **`google-ai-studio/priority`**: Prompt $0.1465 / Completion $0.7326 (1.8x base price). Pinned during latency stress-tests; keeping it permanently active incurs a 1.8x cost penalty.
- **`google/gemini-3.8-flash` (standard auto-route)**: Prompt $0.0814 / Completion $0.4070 (Base price). Recommended baseline once toolset payload is trimmed.
- **`google-ai-studio/flex`**: Prompt $0.0407 / Completion $0.2035 (3.6x cheaper than priority, 2x cheaper than auto-route). Spot/preemptible tier; best for bulk or low-budget tasks, with slight occasional queue latency.

### Pitfall: Unpinned Auto-route Kills Prompt Caching & Burns Balance Fast
- When `model.default` lacks `@provider=...` (bare `google/gemini-3.8-flash`), RouterAI dynamically distributes calls across distinct upstream nodes/accounts.
- **Mechanism**: Dynamic routing breaks Gemini server-side prompt cache affinity. Hits drop from 85–95% down to 0% (`cache=0` in `agent.log`).
- **Impact**: Without cache, every tool execution turn bills the full 30,000+ token context at non-cached rates. Combined with 2,000–4,000 CoT completion tokens per turn on `reasoning: high`, balance drains 3.5x–5x faster.
- **Fix**: Pin the channel explicitly to preserve cache affinity:
  - For maximum economy / non-urgent bulk tasks:
    ```bash
    hermes config set model.default "google/gemini-3.8-flash@provider=google-ai-studio/flex"
    ```
  - For immediate response without spot/preemptible queue delays (or when flex queues spike):
    ```bash
    hermes config set model.default "google/gemini-3.8-flash"
    ```
    *(Note: If switching off flex to bare auto-route for speed, verify whether upstream cache hits drop; if latency returns due to full tools payload on unpinned routes, use `@provider=google-ai-studio/priority` instead).*

### Multi-turn Tool Calls on Flex Channel Latency Multiplier
- **Symptom**: Sequential multi-tool execution turns feel disproportionately sluggish on `@provider=google-ai-studio/flex`.
- **Mechanism**: Flex is an upstream spot/preemptible queue tier. Each consecutive model turn in an interactive chain (e.g. agent runs a command -> receives tool result -> calls another command) pays the provider TTFT queue latency anew. A 5-step investigative sequence can incur 5 separate 5–15s upstream queue waits even if the local shell executes in 0.2s.
- **Rule**: When executing data investigations or log inspections under the flex profile, batch independent shell commands into a single compound bash call or single Python invocation where possible, minimizing the count of round-trip model turns through the preemptible queue.

### Understanding Cascade Architecture vs Direct Chat Dispatch
- **Direct User Chat Routing**: User messages always hit `model.default`. Hermes does NOT dynamically route casual chat questions ("Не спишь?", "Привет") to cheaper aux models like DeepSeek; the full context (system prompt, tools, chat history) is always sent to the primary model.
- **Auxiliary Workloads**: Auxiliary models (`auxiliary.compression`, `title_generation`, etc.) only run internal background tasks.
- **Delegation Workloads**: Cost optimization for repetitive/heavy tasks must be routed explicitly via `delegate_task` (pointing `delegation.model` to lightweight cost-effective models like DeepSeek Flash rather than heavy models like Luna Pro).
- **Fast Chat Economics**: To avoid burning balance on trivial chat turns, use `/new` regularly after completing milestones to purge accumulated history, avoiding re-sending tens of thousands of tokens per single turn.

## 3. RouterAI vs ProxyAPI (Domestic Providers in RF)
- **RouterAI Failure Modes (desktop.log)**:
  - `Закреплённый канал :network не имеет свободной ёмкости` → pinned Gemini channel saturated; requests redirect to slow fallback routes or drop with `ReadError` after 180s.
  - `HTTP 402 Insufficient balance` → RouterAI account depleted; triggers fallback cascade.
  - `HTTP 401 Missing Authentication header` on auxiliary tasks (title generation etc.) → aux pool credentials broken.
- **Domestic Drop-In Alternative (ProxyAPI)**:
  - When RouterAI channels remain saturated, switch to ProxyAPI (`https://api.proxyapi.ru/v1`):
    ```bash
    hermes config set model.base_url https://api.proxyapi.ru/v1
    hermes auth add openrouter --label "ProxyAPI"
    ```
  - Billed in RUB via MIR / SBP without foreign card commissions, supports Gemini and OpenRouter catalogs with stable European routing.

## 4. Toolset Optimization for Low Latency (Preserving `high` Reasoning)
When TTFT latency spikes due to Gemini planning over bulky tool declarations, DO NOT lower reasoning effort. Instead, strip unneeded tools from the active system prompt:
- **Disable unneeded built-in toolsets**:
  ```bash
  hermes tools disable kanban tts clarify
  ```
  - `kanban`: 13 autonomous orchestrator tools (`kanban_*`), useless in interactive chat; represents ~40% of all tool JSON overhead.
  - `tts`: text-to-speech audio output.
  - `clarify`: interactive UI form popups; normal text interaction is standard.
  - Disabling these 3 toolsets strips 15 bulky JSON schemas out of every prompt, dramatically cutting Gemini's tool selection planning CoT time.
- **Core direct toolset to keep**:
  - `terminal`, `file` (`read_file`, `write_file`, `patch`, `search_files`), `web` (`web_search`, `web_extract`), `vision` (`vision_analyze`), `memory`, `skills`, `delegation` (`delegate_task`), `browser`.

## 5. Gating Reasoning Depth in Dialogue
When `agent.reasoning_effort: high` is active, delineate depth using context and trigger phrases:
- **Fast response mode (casual/operational)**: Greetings ("Привет"), confirmations ("делай", "ок"), configuration checks, and quick status inquiries must respond immediately without deep CoT deliberation.
- **Maximum depth trigger phrases (Alexey's conventions)**:
  - «Глубокий анализ» / «Разбери досконально» — exhaustive research, ground truth, verified real cases.
  - «Просчитай со сметой и узлами» — exact articles, consumption, labor costs, rework risks.
  - «Проверь на риски / дай жесткий pushback» — rigorous business partner critique on margins and liquidity.
  - «Джарвис» — 3-role pipeline (analyst + practitioner + skeptic).
- **Fast output modifiers**: «Коротко», «Одной строкой», «Только цифру/вывод».

## 6. Gemini Hang — Diagnose & Fix Playbook (verified Oct 2026)

**Symptom**: first reply to any message (even "привет" in an empty chat) takes 40s–3min; desktop.log shows `No response from provider for 180s`, `Stream stale`, `ReadError after 181.1s`. Support's "huge 71K-token context" theory is WRONG — it reproduced in an empty chat too.

**Diagnose (in this order):**
1. `hermes config get model.default` — confirm current model line.
2. agent.log `conversation_loop`: check `in=`/`latency=`/`upstream=` on the API call.
3. **Decisive test** — same body with vs without `tools` (curl to `https://routerai.ru/api/v1/chat/completions` with key from `.env`):
   - без tools → 2–6s; с полным tools-массивом Hermes (37 шт.) → 46–121s ⇒ tools-массив виноват.
4. Check balance (HTTP 402) and geo (403 from openrouter.ai without VPN — auxiliary traffic must go to routerai.ru).

**Fix (verified):**
```bash
hermes config set model.default "google/gemini-3.8-flash@provider=google-ai-studio/priority"
```
- Priority channel holds the FULL 37-tool array: first token ~1.9s, full Hermes CLI reply 11s (was 130–255s).
- Cost: ×1.8 of base Gemini Flash price — negligible in absolute terms.
- Then: restart the app / open a new chat (config re-read at session start).

**Supporting notes:**
- Auxiliary tasks (vision/title/compression) hit openrouter.ai by default → 403 without VPN. Fix:
  `hermes config set auxiliary.vision.base_url https://routerai.ru/api/v1` (and title_generation, compression, skills_hub, mcp, curator, web_extract).
- Hermes 0.21.5 maps `agent.reasoning_effort: high` → wire `xhigh`; check real wire level in desktop.log `session.info` `reasoning_effort_wire`.
- Benchmarks on tiny prompts (no tools) are NOT representative — they hide the tools problem.
- Do NOT remove `OPENROUTER_BASE_URL` from `.env`: it points the openrouter pool at routerai.ru.

## 5. Image Generation Economics on RouterAI (`image_gen`)
- **Flagship Premium Tier**: `openai/gpt-image-2.5-sunburst` (~$1.00 per generated image).
  - Configured in the `kira` profile.
  - **Policy**: Never switch `kira` to cheaper models automatically or downgrade without explicit user consent. High cost is an accepted trade-off for top visual quality.
- **Cost-Optimized Alternatives (when testing or low-budget drafting)**:
  - `google/gemini-3.1-flash-image`: ~$0.01–0.03 per image (~30-100x cheaper).
  - `openai/gpt-5-image-mini` / `openai/gpt-image-1-mini`: ~$0.15–0.30 per image.

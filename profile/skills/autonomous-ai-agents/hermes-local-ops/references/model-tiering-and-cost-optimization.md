# Model Tiering & Cost Optimization Playbook (OpenRouter)

## Context & Strategy
On OpenRouter, pricing changes periodically (e.g., promotional discounts expire). To keep operating costs low without sacrificing accuracy, adhere to a strict model tiering strategy.

## Model Roles & Selection (as of late September 2026)

### 1. Primary Reasoning & Vision ("Main Brain")
- **`google/gemini-3.8-flash`** ($0.75 / $3.75 per 1M tokens):
  - Strengths: Unrivaled multi-modal comprehension (floor plans, renovation photos, wiring), complex Russian reasoning, high adherence to formatting/math, active business-partner mindset.
  - Benchmarked against GPT-6 Luna Pro on real estate plans: Gemini accurately identifies room subtypes (including walk-in closets/dark rooms), traces plumbing/drainage stacks, and distinguishes structural walls vs partitions. Luna Pro suffers from spatial blind spots and defensive bureaucracy ("don't touch any walls, hire an engineer").
  - Optimization: Set `reasoning_effort: high` for real estate flipping, structural checks, and coaching.

### 2. Autonomous Subagents & Delegation ("Worker Workhorse")
- **`openai/gpt-6-luna-pro`** ($0.10 / $0.50 per 1M tokens):
  - Strengths: 7.5x cheaper than Gemini 3.8 Flash, 1.05M context window, 2.3s latency, strict OpenAI function/tool calling and JSON serialization.
  - Best for: Kanban delegation (`delegation.model`), code reviews, autonomous multi-step subagents, and marketplace bulk text analysis (WB «Галерея 17» customer review mining and SEO keyword generation).
  - Caveat: Do NOT use as primary vision or flipping brain due to risk-averse disclaimers and weaker spatial plan recognition.

### 3. Auxiliary Free Web Extract & Heavy Docs ("Document Workhorse")
- **`minimax/minimax-m3:free`** ($0.00 / 1M context):
  - Best for `auxiliary.web_extract`, long PDF legal texts, BTI floor plans, scraping bulk listings from Avito / marketplace catalogues.
  - Keeps heavy text ingestion completely free of charge.

### 4. Precision Code & Skill Hub ("Code Workhorse")
- **`deepseek/deepseek-v4-flash-0731`** or **`deepseek/deepseek-v4-pro`**:
  - Python syntax precision, schema compliance, and low cost for background skill curation and internal tools.
- **`deepseek/deepseek-v4.1-flash` (Pitfall)**:
  - Spends significant token budget on reasoning before generating visible content. If `max_tokens` is bounded or OpenRouter is congested, it results in timeouts or empty content (`content: None`). Do NOT use as user-facing dialogue model.

### 5. Robust Conversational Fallback Chain
When primary `google/gemini-3.8-flash` balance runs out or rate-limits, Hermes automatically cascades to:
1. **`openai/gpt-6-luna`** (low cost, 1.05M context, excellent tool calling & dialogue continuity).
2. **`minimax/minimax-m3:free`** (1M context, 100% free fallback).
3. **`z-ai/glm-5.2:free`** (256k context, free backup).

## Configuration Keys in `config.yaml`
Modify via CLI (`hermes config set <key> <val>`) — direct file writes are blocked:
```bash
# Delegation to GPT-6 Luna Pro
hermes config set delegation.model openai/gpt-6-luna-pro
hermes config set delegation.reasoning_effort low

# Profile-specific model assignment (e.g. WB Gallery 17)
hermes -p gallery17 config set model.default openai/gpt-6-luna-pro
```

## Domestic Drop-In Aggregators (RouterAI / routerai.ru)

When paying OpenRouter via international cards/crypto is constrained in Russia:
- **RouterAI (`https://routerai.ru/api/v1`)**:
  - Full drop-in mirror for OpenRouter in RF: identical model slugs (`google/gemini-3.8-flash`, `openai/gpt-6-luna-pro`, `deepseek/deepseek-v4-flash-0731`, `anthropic/claude-sonnet-5`).
  - Supports streaming, function/tool calling (`tools`, `tool_choice`, `parallel_tool_calls`), structured outputs, vision/multimodal, and reasoning/thinking.
  - Payment: direct RUB via SBP / MIR cards / Russian bank cards / bank invoices for IP & LLC (0% service fee, pure pay-as-you-go, optional auto-topup).
  - Price parity: prices tracked directly against upstream per-token rates at market exchange rate (~109.6 RUB/$ as of late 2026) without 2-3x reseller markup.
  - Switching Hermes (Full Procedure & Pitfalls):
    1. **Set Base URL Globally and in .env**:
       ```bash
       hermes config set model.base_url https://routerai.ru/api/v1
       ```
       Also add `OPENROUTER_BASE_URL=https://routerai.ru/api/v1` to `~/.hermes/.env` so specialist profiles with unset `model.base_url` (e.g. `gallery17`) inherit the RouterAI endpoint instead of silently defaulting to `openrouter.ai`.
    2. **Update API Key in `.env`**:
       Update `OPENROUTER_API_KEY` in `~/.hermes/.env` with the RouterAI key (comment out the old OpenRouter key). Do NOT leave the old key active in `.env`: `_resolve_openrouter_runtime` checks `OPENROUTER_API_KEY` in the environment before checking the credential pool, which sends the wrong key to RouterAI and triggers HTTP 401.
    3. **Credential Pool & Auxiliary Tasks (`auth.json`)**:
       When adding via `hermes auth add openrouter --label "RouterAI"`:
       - Set priority 0: `hermes auth priority openrouter RouterAI 0`.
       - Ensure `base_url` on the RouterAI credential entry in `auth.json` is set to `https://routerai.ru/api/v1`. The CLI `auth add` command binds `openrouter` credentials to canonical `https://openrouter.ai/api/v1`, which causes auxiliary tasks (`_try_openrouter()` for title generation and compression) to send the RouterAI key to OpenRouter, returning HTTP 401.
       - If any test request failed with 401 during setup, clear the exhaustion cooldown: `hermes auth reset openrouter`.
    4. **Model Slugs**:
       Keep `model.provider: openrouter` and leave model slugs untouched (`google/gemini-3.8-flash`, `openai/gpt-6-luna-pro`, `deepseek/deepseek-v4-flash-0731`). RouterAI mirrors all upstream OpenRouter endpoints and model identifiers directly.

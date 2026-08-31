# Model Tiering & Cost Optimization Playbook (OpenRouter)

## Context & Strategy
On OpenRouter, pricing changes periodically (e.g., promotional discounts expire). To keep operating costs low without sacrificing accuracy, adhere to a strict model tiering strategy.

## Model Roles & Selection (as of late August 2026)

### 1. Primary Reasoning & Vision ("Main Brain")
- **`google/gemini-3.7-flash`** ($0.75 / $3.75 per 1M tokens):
  - Strengths: Best-in-class multi-modal comprehension (floor plans, renovation photos, wiring), complex Russian reasoning, high adherence to formatting/math.
  - Optimization: Set `reasoning_effort: medium` to avoid burning thousands of internal reasoning tokens per conversational turn.
- **`openai/gpt-5.6-luna`** ($0.20 / $1.20 per 1M tokens):
  - Strengths: ~3.5x cheaper than Gemini 3.7 Flash, 1.05M context window, fast tool-calling, excellent code & logic execution, vision-capable. Primary candidate when Gemini pricing increases further.

### 2. Auxiliary Free Web Extract & Heavy Docs ("Document Workhorse")
- **`minimax/minimax-m3:free`** ($0.00 / 1M context):
  - Best for `auxiliary.web_extract`, long PDF legal texts, BTI floor plans, scraping bulk listings from Avito / marketplace catalogues.
  - Keeps heavy text ingestion completely free of charge.

### 3. Precision Code & Skill Hub ("Code Workhorse")
- **`deepseek/deepseek-v4-flash-0731`** or **`deepseek/deepseek-v4-pro`**:
  - Unmatched Python syntax precision, schema compliance, and low cost for background skill curation and internal tools.
  - Note: Not recommended as conversational fallback for general multi-turn reasoning and tool use.

### 4. Robust Conversational Fallback Chain
When primary `google/gemini-3.7-flash` balance runs out or rate-limits, Hermes automatically cascades to:
1. **`openai/gpt-5.6-luna`** (low cost, 1.05M context, excellent tool calling & dialogue continuity).
2. **`minimax/minimax-m3:free`** (1M context, 100% free fallback).
3. **`z-ai/glm-5.2:free`** (256k context, free backup).

## Configuration Keys in `config.yaml`
```yaml
agent:
  reasoning_effort: medium

auxiliary:
  web_extract:
    model: minimax/minimax-m3:free
    provider: openrouter
  vision:
    model: google/gemini-3.7-flash
    provider: openrouter
  curator:
    model: deepseek/deepseek-v4-flash-0731
    provider: openrouter
```

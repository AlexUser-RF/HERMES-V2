# Auxiliary vision model resolution in Hermes (this install)

Source of truth: local Hermes source at `~/AppData/Local/hermes/hermes-agent`
(`agent/auxiliary_client.py`, `hermes_cli/config_defaults.py`,
`plugins/model-providers/*`). Public docs do NOT document this — read the code.

## Default vision model (OpenRouter fallback)

- `_OPENROUTER_MODEL = "google/gemini-3.6-flash"` (`agent/auxiliary_client.py:1116`).
  This is the stock "eyes" model of Hermes on OpenRouter:
  gemini-3.6-flash, 1M context, image input, ~$1.5/M in / $7.5/M out
  (verified against `openrouter.ai/api/v1/models`, 2026-08).
- Engaged when `auxiliary.vision.provider: auto` (or no explicit auxiliary block)
  and the main provider's model cannot see images.

## Resolution order for `provider: auto`

1. **Main provider + main model** — only if the model is vision-capable
   (`_main_model_supports_vision`; text-only models like deepseek-v4-flash are
   skipped). Per-provider vision overrides (`_PROVIDER_VISION_MODELS`):
   xiaomi → `mimo-v2.5`, zai → `glm-5v-turbo`. DeepInfra discovers its first
   vision-capable *chat* model live from the catalog (profile hook, key-gated).
2. **openrouter** → `_OPENROUTER_MODEL` (gemini-3.6-flash).
3. **nous** — Portal, tier-aware strict vision backend.
4. **deepinfra** — requires `DEEPINFRA_API_KEY`.

`kimi-coding` / `kimi-coding-cn` endpoints have NO image input →
always skipped in the auto chain.

## Config keys (config.yaml)

- `auxiliary.vision.provider` / `auxiliary.vision.model` — explicit override
  (this profile currently: `openrouter` / `google/gemini-2.5-flash`).
- `auxiliary.openrouter_model` — override for the OpenRouter fallback model.
- `auxiliary.free_only` — restrict auxiliary fallbacks to `:free` SKUs.
- `auxiliary.vision.extra_body` — raw JSON body, e.g. `'{"max_tokens": 3000}'`
  to cap vision output tokens per call.

## Pitfall: 402 on low OpenRouter balance

- Image-GEN models (google/gemini-3.1-flash-image, google/gemini-2.5-flash-image)
  are NOT vision-analysis models: they request max_tokens up to 65535 →
  `402 This request requires more credits, or fewer max_tokens` when the
  OpenRouter balance is small (observed with ~10k affordable tokens).
- For `vision_analyze` use a chat multimodal flash model (gemini-3.6-flash /
  2.5-flash), NOT the image-gen model. Cap spend with `extra_body.max_tokens`
  when balance is tight.

## Verify a model exists on OpenRouter (one-liner)

```bash
curl -s https://openrouter.ai/api/v1/models | python -c "
import json,sys
d=json.load(sys.stdin)
for m in d['data']:
    if 'gemini' in m['id'] and 'flash' in m['id']:
        print(m['id'], m.get('pricing'), m.get('context_length'),
              m.get('architecture',{}).get('input_modalities'))
"
```
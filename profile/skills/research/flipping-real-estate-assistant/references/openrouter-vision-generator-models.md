# OpenRouter vision vs generation models + availability check

Context: the agent (Hermes) needs to "see" Alexey's floor plans and photos (the
vision tool) and to generate design visualizations. On HIS setup these run through
OpenRouter via the `auxiliary.vision` and `image_gen` config sections. Two mistakes
recur: confusing a GENERATION model for a VISION model, and assuming a model exists
in the API just because it has a website page.

## 1. Vision vs Generation — different classes, don't confuse them

| Task | What the model must do | Model class | Example |
|---|---|---|---|
| Agent SEES a photo/plan | image in → **text out** (describe it) | **VISION (VL)** | `qwen3-vl-32b-instruct` |
| Agent DRAWS a visualization | **image out** (from prompt/reference) | **IMAGE GENERATION** | `google/gemini-3.1-flash-image`, `qwen-image-3-pro` |

`qwen-image-3-pro` is an **image GENERATION** model ("image generation and editing
model from Qwen"), NOT a vision model — it cannot feed text back about Alexey's photo.
When deciding what to configure for the agent's own eyes, always reach for the
**Qwen VL / vision-language** family (image in → text out).

Available Qwen vision (VL) models on OpenRouter (image in → text out):
- `qwen3-vl-235b-a22b-instruct` — top quality (best detail on small plan text/measurements)
- `qwen3-vl-32b-instruct` — good middle ground
- `qwen3-vl-30b-a3b-instruct` — faster/cheaper
- `qwen3-vl-8b-instruct` — light/cheap
- `qwen2.5-vl-72b-instruct` — previous gen, reliable

## 2. A model page existing ≠ it's in the API catalog

`qwen/qwen-image-3-pro` HAS a page at https://openrouter.ai/qwen/qwen-image-3-pro
("Qwen Image 3 Pro", image gen, ~$0.04/image, released Aug 2026) — but the model
**API endpoints return 404**:
- `GET /api/v1/models` — NOT in the returned list
- `GET /api/v1/models/qwen/qwen-image-3-pro` → `{"error": {"message":"Not Found"...}}`

So: newly added / invite-stage models can show on the website playground but are not
yet selectable via the models API (and a 404 on the exact endpoint is conclusive —
don't keep retrying). Always verify a model is really callable before wiring it into
config; a page alone is not proof.

## 3. How to enumerate the catalog programmatically

```bash
KEY=$(grep -oE "^OPENROUTER_API_KEY=.*" "$HOME/AppData/Local/hermes/.env" | cut -d= -f2- | tr -d '"' | tr -d "'")
curl -s "https://openrouter.ai/api/v1/models" -H "Authorization: Bearer $KEY" > models.json
```

Then filter by family and inspect modality classes:
```python
for m in data['data']:
    a = m.get('architecture', {})
    vin = a.get('input_modalities');  vout = a.get('output_modalities')
    # vision  = 'image' in vin and 'text' in vout
    # generate = 'image' in vout
```
Note: `/models` does not include a popularity field — to rank "most popular" you'd
check the website's Rankings page, not this endpoint.

## 4. Hermes config keys used (this project)

- Vision (agent eyes): `auxiliary.vision.provider` = `openrouter`,
  `auxiliary.vision.model` = `qwen/qwen3-vl-32b-instruct` (swap to 235b for max detail).
- Image generation: `image_gen.provider` = `openrouter`,
  `image_gen.openrouter.model` = `google/gemini-3.1-flash-image`
  (also settable via env `OPENROUTER_IMAGE_MODEL`).
- `hermes config set <key> <value>` writes config.yaml; `image_gen.*`/`auxiliary.*` are
  plugin-read keys, so `hermes config set` may warn "not a recognized key" — that warning
  is expected and harmless; verify by grepping config.yaml afterward.
- Vision/generation toolset changes only take effect in a NEW session (never mid-chat,
  to preserve prompt caching). Tell the user to reset the chat.

## 5. Verification before trust
- Test vision with a real image: send a screenshot to the chosen vision model via
  OpenRouter chat/completions with an `image_url` (data:image/png;base64) content part,
  and check it actually describes it. (Large base64 can exceed curl's argv limit — write
  the JSON payload to a file and use `curl --data @file`.)

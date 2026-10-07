# Model-catalog fetch (`OPENROUTER_MODELS_URL`) and the `403 Forbidden` warning

## What happens

`agent/model_metadata.py::fetch_model_metadata()` fetches the OpenRouter model catalog (context
lengths, `max_completion_tokens`, pricing) and caches it per profile at
`<hermes_home>/cache/openrouter_model_metadata.json` (disk-backed, ~1h TTL; a fresh disk cache is
loaded WITHOUT a fetch). The URL is the plain module constant `OPENROUTER_MODELS_URL` in
`hermes-agent/hermes_constants.py`, which defaults to `https://openrouter.ai/api/v1/models`.

On networks where the canonical host answers `403 Forbidden` (security/geo policy — the 403 arrives
even with NO credentials), every stale-cache refresh logs:

```
WARNING agent.model_metadata: Failed to fetch model metadata from OpenRouter:
  Client error '403 Forbidden' for url 'https://openrouter.ai/api/v1/models'
```

Inference is unaffected (the profile routes to RouterAI via `base_url`) — this is catalog noise, not
a hang. It only degrades cost/context metadata to defaults.

## Fix on this machine

`OPENROUTER_MODELS_URL` now defaults to `https://routerai.ru/api/v1/models` (still overridable via
the `HERMES_OPENROUTER_MODELS_URL` environment variable). RouterAI serves an OpenRouter-compatible
catalog with `pricing_units: {prompt: "token", completion: "token"}` — the SAME unit Hermes expects,
so cost display stays correct (do not "fix" the numbers). Verify by inspecting the refreshed cache:
RouterAI price for `google/gemini-3.8-flash` is `8.28076275e-05`, whereas the openrouter.ai catalog
reports `7.5e-07`.

Steps: patch the constant → delete the profile's `cache/openrouter_model_metadata.json` (or wait out
the 1h TTL) → next process start fetches from RouterAI (verified: cache rebuilt with RouterAI prices,
zero new `403` lines).

## Pitfalls

- **Do NOT try to fix it through `.env`.** `hermes_cli/env_loader.py` loads `.env` into `os.environ`
  AFTER `hermes_constants` has been imported, so a `HERMES_OPENROUTER_MODELS_URL=...` line in
  `profiles/<name>/.env` never reaches the already-computed constant. Proven by probe: a bogus URL in
  the profile `.env` was ignored and the fetch still went to openrouter.ai. Change the constant's
  default (or export the variable SYSTEM-wide, before Hermes starts).
- **The fix binds at process start.** A running backend holds the old constant in memory; until that
  process restarts it can still fetch openrouter.ai. Tell the user a restart (or simply waiting for
  the next launch) is what makes it fully quiet.
- **Vendor file.** `hermes_constants.py` belongs to the hermes-agent checkout — `hermes update` may
  overwrite the default. After updates, re-check `grep -n OPENROUTER_MODELS_URL hermes_constants.py`
  and restore if it reverted.
- **A single `curl` proves nothing.** `https://openrouter.ai/api/v1/models` answered `403` (even
  without a key) and later `200` on the same machine — the block is intermittent. Judge the fix by
  the refreshed cache contents, not by a one-off curl.
- **Backups taken before the edit**: `hermes_constants.py.bak_<stamp>` next to the file.

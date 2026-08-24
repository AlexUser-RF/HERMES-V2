# Gateway API server + Hermes Workspace (external web UI)

Set up 2026-08-09. Hermes Workspace (`github.com/outsourc-e/hermes-workspace`,
~5.5k stars, MIT) is a **third-party** web UI over Hermes — NOT official Nous
Research. It needs the gateway's OpenAI-compatible API server, which is
**opt-in and off by default**.

## Problem

The default gateway serves messaging platforms (Telegram etc.) but does not
listen on an HTTP port. Symptom: frontend says
`Could not reach Hermes gateway on 8645, 8642, or 8643` / `mode=disconnected`.

## Enabling the API server (discovered in hermes_cli/config_defaults.py + web_server.py)

Append to HERMES_HOME/.env (settings live in config.yaml; this is env-toggled):

```
API_SERVER_ENABLED=true
API_SERVER_KEY=<python -c "import secrets; print(secrets.token_urlsafe(32))">
API_SERVER_PORT=8642        # default
API_SERVER_HOST=127.0.0.1   # default
```

**API_SERVER_KEY is mandatory** — the server refuses to start without it, even
on loopback binds (both loopback and public binds require it).

Then `hermes gateway restart` (drains cleanly, respawns; it does kill running
agents momentarily — expected). Verify:

```bash
curl -H "Authorization: Bearer $KEY" http://127.0.0.1:8642/v1/models
# → {"object":"list","data":[{"id":"hermes-agent",...}]}
# without key → {"error":{"code":"gateway_auth_failed"}}  ← auth working as intended
```

## Dashboard (:9119) vs serve

- `hermes dashboard` → web admin + API surfaces frontends use (`/api/sessions`,
  conductor missions, kanban). Token is scraped automatically from dashboard
  root HTML — never copy it into .env (stale on dashboard restart → 401s).
- `hermes serve` → JSON-RPC/WebSocket backend the desktop app connects to
  (default 9119). Headless.
- Workspace UI shows `missing=[skills, config]` until dashboard is up; that's
  the "start the dashboard" signal, not a workspace bug.

## Workspace stack — install & run

- Install script: download `https://hermes-workspace.com/install.sh` to disk,
  READ it, then run the saved copy (never blind `curl | bash`).
- **MSYS pitfall in installer**: it runs `git -C "$INSTALL_DIR" pull` and dies
  on `/c/...` paths. Fix: pass Windows-form path:
  `INSTALL_DIR="C:/Users/<user>/hermes-workspace" bash install.sh`
- **Broken pnpm**: Windows installs may have a corepack shim that fails with
  `Cannot find module '...corepack\dist\pnpm.js'` (mangled `D:\c\...` path).
  Fix: `npm install -g pnpm --force` (then `pnpm -v`).
- Workspace `.env` must uncomment/set:
  - `HERMES_API_URL=http://127.0.0.1:8642`
  - `HERMES_API_TOKEN=<same value as API_SERVER_KEY>`
  - `HERMES_AGENT_PATH=C:/Users/<user>/AppData/Local/hermes/hermes-agent`
    (auto-detect only checks sibling dirs — agent lives inside HERMES_HOME here)

## Stack = 3 processes

1. `hermes gateway run` — already running as the desktop/Telegram gateway;
   RESTART it (`hermes gateway restart`), never start a second instance
   ("Another gateway instance is already running").
2. `hermes dashboard` → :9119
3. `cd ~/hermes-workspace && pnpm dev` → :3000 (Vite auto-restarts on .env change)

Healthy UI log line:
`mode=portable core=[health, chatCompletions, models, streaming] enhanced=[sessions, memory, jobs]`

All three are session-scoped background processes → after a reboot the workspace
stack must be started again (gateway may auto-start via desktop app; dashboard +
`pnpm dev` do not).

## Notes

- Google setup.py on this machine is OLDER than the google-workspace skill
  docs: it rejects `--services`/`--format` flags. Workaround: plain
  `--auth-url` (defaults to the full scope set). Auth flow otherwise identical.
- Google OAuth `403 access_denied` = app still in Testing mode → add the
  account at https://console.cloud.google.com/auth/audience (Test users).
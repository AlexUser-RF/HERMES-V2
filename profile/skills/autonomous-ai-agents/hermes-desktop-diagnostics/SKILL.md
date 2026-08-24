---
name: hermes-desktop-diagnostics
description: "Use when Hermes Desktop's chat or sessions are invisible."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [hermes, desktop, gateway, troubleshooting, diagnostics, windows]
    related_skills: [hermes-agent, inspecting-hermes-desktop-dom]
---

# Hermes Desktop Diagnostics

Diagnose user-facing Hermes Desktop problems on the user's own machine: "the dialog is not visible", blank/empty chat pane, sessions missing from the sidebar, desktop-vs-Telegram confusion, app won't open. Diagnose via logs, state.db inspection, and process checks. Complements the bundled `hermes-agent` skill (which covers config/gateway/voice etc. but NOT desktop-app UI forensics).

## Architecture facts (know these before touching anything)

- **Hermes Desktop = Electron app that spawns a headless backend** (`hermes serve`; a port is assigned per launch and logged as `HERMES_BACKEND_READY port=NNNNN` in `desktop.log`). "Web UI disabled — use `hermes dashboard`" 404s during boot are benign.
- **Messaging-platform gateways (Telegram, etc.) = a separate long-lived process** (`hermes gateway run`; PID visible in `gateway_state.json` / `gateway.pid`). It survives independently of the desktop app.
- **Both write sessions to the same `state.db`** (canonical session store). The `sessions.source` column distinguishes surfaces: `'desktop'` vs `'telegram'` etc.
- **Surfaces are NOT mirrors.** A Telegram conversation does not stream into the desktop window live, and desktop chats don't appear in the bot. The Telegram conversation DOES show up in the desktop app's session sidebar (same DB) — the user can click it and continue there.
- **"Dialog not visible" almost always means one of:** (a) app window hidden/minimized to the system tray, (b) no session selected so the chat pane shows a fresh/empty state (click a session in the sidebar, or Ctrl+N), (c) user expects their ongoing Telegram chat to appear in the desktop window in real time.

## Diagnosis workflow

1. **Version / install:** `hermes --version` (if the CLI exists, the install is fine).
2. **Is the app running?** On Windows from git-bash, `tasklist` pipes out UTF-16 and grep prints `Binary file (standard input) matches` instead of lines. Use:
   `wmic process get name,processid 2>/dev/null | tr -d '\0' | grep -i -E "hermes|electron"`
   Multiple `Hermes.exe` processes (main + GPU + renderers) = healthy Electron app.
3. **Gateway status:** read `gateway_state.json` (HERMES_HOME, default `~/AppData/Local/hermes/`) — `platforms.telegram.state: connected`, `active_agents`, `gateway_state`. Beware: its internal `updated_at` timestamps can be stale (from a previous gateway run) — check file mtime too.
4. **Logs** (HERMES_HOME/logs/):
   - `desktop.log` — app boot cycles, self-update flow ("update in progress… deferring backend start", venv-lock aborts), backend ports, "Hermes backend is ready. Finalizing desktop startup".
   - `gui.log` — backend `web_server` events: "Desktop cron scheduler started", and crucially `Messaging platform updated: platform=telegram … enabled=False/True env_keys=[...]` → shows the user toggling platform settings in the desktop app (env_keys reveal which token they entered).
   - `agent.log` — per-turn lines: `conversation turn: session=… platform=desktop msg='…'` → proves a desktop chat worked and when.
   - `errors.log` — mostly tool-registry/auxiliary warnings (noise); grep for actual ERROR/exception traces.
5. **Session inventory** — inspect `state.db` (sqlite3 CLI is often absent; use python):
   ```sql
   SELECT id, source, title, message_count FROM sessions ORDER BY rowid;
   ```
   Reading `source` per session tells you which surface owns each conversation, and whether the user's Telegram session exists in the store at all.
6. **Explain surfaces to the user BEFORE deep-diving** — most of the time the architecture explanation resolves the complaint. Then, if still ambiguous, ask exactly what they see (blank window / tray-hidden / empty chat pane / session missing from sidebar) rather than guessing.

## Pitfalls

- **`messages` table has `timestamp`, NOT `created_at`** — a `created_at` query errors with `sqlite3.OperationalError`. Column list: `id, session_id, role, content, tool_call_id, tool_calls, tool_name, effect_disposition, timestamp, token_count, finish_reason, reasoning…`.
- **Never relaunch the user's app to get a CDP port** — packaged builds never open one (dev-server runs only), and relaunching destroys their session state. Cannot inspect the live window DOM of the installed app; use logs + DB + asking. See `inspecting-hermes-desktop-dom`.
- **Never hand-edit `config.yaml`** — use `hermes config set KEY VAL`.
- Desktop backend restarts look dramatic in logs (multiple boot cycles + self-update churn) but are usually benign; judge by the LAST line (`Hermes backend is ready`) and by alive processes.

## Support files

- `references/workflow-real-world-example.md` — worked example: user "can't see the dialog" with the exact log lines, timeline reconstruction, and DB queries that resolved it.
---
name: hermes-local-ops
description: "Local Hermes ops: profile backup, gateway API, Workspace."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [hermes, backup, cron, gateway, workspace, windows, operations]
---

# Hermes Local Ops (this machine: Windows 10, git-bash, profile=default)

Operational playbook for Alexey's local Hermes installation. Covers the two standing automation stacks set up 2026-08-09:

1. **Profile backup** — daily 23:00 cron pushing the Hermes profile to the private repo `AlexUser-RF/HERMES` (see `references/profile-backup.md`).
2. **Workspace stack** — external web UI (outsourc-e/hermes-workspace) + gateway OpenAI-compatible API + dashboard (see `references/gateway-api-and-workspace.md`).

## Key paths (machine-specific, verified)

- HERMES_HOME = `C:\Users\Administrator\AppData\Local\hermes` — the whole profile: config.yaml, memories/, skills/, cron/, state.db, sessions/
- Backup working copy: `~/hermes-backup` (git repo, remote = `https://github.com/AlexUser-RF/HERMES.git`)
- Backup script: `~/AppData/Local/hermes/scripts/backup_hermes.sh` — cron job `hermes-profile-backup` (no_agent, watchdog)
- Workspace clone: `~/hermes-workspace`; user work folder: `D:\HERMES FILES` (desktop project "HERMES FILES", `terminal.cwd`)
- Git auth: `~/.git-credentials` via `credential.helper store` (user `AlexUser-RF`, PAT with `repo` scope)
- Google OAuth: token at `~/AppData/Local/hermes/google_token.json` — excluded from backups

## Hard invariants

- **Secrets never in git**: `.env`, `google_token.json`, `google_client_secret.json`, `auth.json`, plus transient `*.lock/*.pid/*.shm/*.wal` are stripped from backups. Double-guarded: script strip + `.gitignore`.
- **MSYS path rule (Windows git-bash)**: bash accepts `/c/...` but native git does NOT — when anything passes a path to git as an argument (`git -C`, remotes), use `C:/...` form. Symptom: `fatal: cannot change to '/c/...': No such file or directory`.
- **Never blind-run `curl | bash`**: download the installer, read it, then run the saved copy from disk. Flags anything unexpected before it executes.
- **`hermes gateway restart` kills running agent processes** — it drains cleanly and respawns (expected), but avoid doing it mid-task without telling the user.
- **One gateway per profile**: "Another gateway instance is already running" → use `hermes gateway restart`, never a second `gateway run`.
- **Vivaldi / Custom Chromium browsers in `use_real_profile`**: Hermes's `use_real_profile` detects default Chromium browsers via Windows `UserChoice` ProgId prefixes. Supported stable browsers: Google Chrome, MS Edge, Brave, Brave Origin, pure Chromium. Vivaldi is NOT supported for profile copying (fails closed to prevent corrupting its custom UI data store); keep Vivaldi isolated as Alexey's primary personal browser and use clean headless Chromium + `hermes vault` for automated authenticated tasks.
- **Vivaldi CDP Remote Debugging Tab Policy (Port 9222)**: When connected to Alexey's active Vivaldi via CDP (`http://127.0.0.1:9222`), operate EXCLUSIVELY inside the dedicated Hermes Agent tab (`localhost:3000` / Hermes web UI). All other tabs (personal sites, search, YouTube, social, personal accounts) are strict user territory: never list in public responses, never inspect, never switch to, and never manipulate them.
- **Conversational Pacing & Narration (Alexey's Communication Preference)**: Do NOT narrate every step before executing tool calls (e.g. avoid robotic "Что я сейчас сделаю / What I will do now" preambles before each action). Take action directly, execute silently, and report the distilled, actionable result. Only pause to inform Alexey in advance when an operation requires explicit user approval, runs a destructive/irreversible command, or changes shared state.
- **DeepSeek Reasoning Models on OpenRouter (`deepseek-v4.1-flash`)**: DeepSeek V4.1 Flash outputs Chain-of-Thought into a separate reasoning stream. If invoked with low `max_tokens` (e.g. <=1000) or during peak latency periods, it exhausts the token budget on reasoning alone (`content: None`) or times out on OpenRouter read queues. Never set as primary conversational driver; use Gemini Flash (`gemini-3.7-flash` / `gemini-3.8-flash`) for snappy user-facing turns.
- **Windows `hermes update` venv lock**: When Desktop app or other profile backends (`serve`) are running, `hermes update --yes` can fail with locked `.pyd` files. Use `hermes update --yes --force-venv` if running from inside the agent, or restart the gateway service afterwards with `hermes gateway restart` to ensure complete recovery.

## Safe Update Workflow on Windows (Full Cycle)

When updating Hermes Agent on Windows:
1. **Check available updates:** `hermes update --check` or `hermes update --plan`.
2. **Update runtime and dependencies safely:**
   ```bash
   hermes update --yes --force-venv
   ```
   *Note:* `--force-venv` bypasses locked `.pyd` files and ensures clean package updates on Windows.
3. **Rebuild desktop UI bundle:**
   ```bash
   cd apps/desktop && npm run build
   ```
4. **Restart background gateway:**
   ```bash
   hermes gateway restart
   ```
   *Impact:* Reconnects Telegram bot and restarts background agent threads with the fresh upstream engine.

## References

- `references/avatar-and-profile-assets.md` — avatar asset storage paths (`assets/avatar.png`), multi-profile asset distribution, and Telegram @BotFather sync instructions.
- `references/profile-backup.md` — backup procedure, include/exclude lists, watchdog cron pattern, verification checklist.
- `references/gateway-api-and-workspace.md` — enabling the OpenAI-compatible API server (:8642), dashboard (:9119), Workspace install/restart.
- `references/auxiliary-vision-resolution.md` — как Hermes выбирает vision-модель: дефолт OpenRouter google/gemini-3.6-flash, порядок auto-детекта, ключи конфига, питфолл 402 на малом балансе OpenRouter (image-gen ≠ vision-анализ).
- `references/profile-session-reset.md` — процедура безопасной очистки контекста/сессий отдельных профилей и шлюза Telegram (`state.db`, бэкап перед сбросом, сохранение `SOUL.md` и памяти).
- `references/desktop-build-and-skew-recovery.md` — устранение баннера «App build out of date» после обновления: сборка фронтенда desktop, синхронизация build stamp и перезапуск.
- `references/model-tiering-and-cost-optimization.md` — стратегия выбора моделей на OpenRouter (Gemini 3.7 vs GPT-5.6 Luna vs MiniMax Free vs DeepSeek), распределение ролей и балансировка reasoning_effort.
- `references/telegram-gateway-vpn-troubleshooting.md` — Telegram API blocking in RF, VPN toggle disconnections, Windows Task Scheduler VBS launcher quirks, and safe gateway restart via `Start-ScheduledTask`.
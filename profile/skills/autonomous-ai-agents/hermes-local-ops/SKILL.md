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

## References

- `references/avatar-and-profile-assets.md` — avatar asset storage paths (`assets/avatar.png`), multi-profile asset distribution, and Telegram @BotFather sync instructions.
- `references/profile-backup.md` — backup procedure, include/exclude lists, watchdog cron pattern, verification checklist.
- `references/gateway-api-and-workspace.md` — enabling the OpenAI-compatible API server (:8642), dashboard (:9119), Workspace install/restart.
- `references/auxiliary-vision-resolution.md` — как Hermes выбирает vision-модель: дефолт OpenRouter google/gemini-3.6-flash, порядок auto-детекта, ключи конфига, питфолл 402 на малом балансе OpenRouter (image-gen ≠ vision-анализ).
- `references/profile-session-reset.md` — процедура безопасной очистки контекста/сессий отдельных профилей (`state.db`, бэкап перед сбросом, сохранение `SOUL.md` и памяти).
- `references/telegram-gateway-vpn-troubleshooting.md` — Telegram API blocking in RF, VPN toggle disconnections, Windows Task Scheduler VBS launcher quirks, and safe gateway restart via `Start-ScheduledTask`.
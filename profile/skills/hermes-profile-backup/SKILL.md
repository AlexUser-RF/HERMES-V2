---
name: hermes-profile-backup
description: "Back up Hermes profile to git so chat context survives."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [backup, git, github, hermes-profile, memory, cron]
    related_skills: [github-auth, github-repo-management, hermes-agent]
---

# Hermes Profile Backup (git)

Purpose: preserve the agent's memory + full conversation history so a crash or reinstall doesn't lose the relationship with the user. Backs up the Hermes **profile**, NOT the user's business/work files (unless explicitly asked — always confirm what the user means by "backup").

## When to use
- "Сделай бэкап / не потерять наше общение, контекст и смысл"
- "Back up Hermes / the agent profile / my chat history"
- Setting up a recurring daily GitHub backup (cron)

## What lives in the profile and matters
Profile root on Windows: `C:\Users\<user>\AppData\Local\hermes` (this IS `$HERMES_HOME`; `~/.hermes` in docs is the fallback path).

| Item | Why it matters |
|---|---|
| `memories/USER.md`, `memories/MEMORY.md` | durable memory — the most valuable part (~12K) |
| `state.db` + `sessions/` | **full chat history** — the source used by session_search |
| `config.yaml`, `SOUL.md` | config + persona |
| `cron/` (incl. `executions.db`, `output/`) | scheduled jobs — including the backup job itself |
| `skills/` | all skills, incl. bundled (~50 MB — fine, git pushes only deltas after first commit) |
| `kanban.db`, `projects.db` | kanban + projects state (small, worth keeping) |

## Exclude — secrets, caches, transient junk (NEVER commit)
- Credentials: `.env`, `auth.json`, `google_token.json`, `google_client_secret.json`, any `*_secret*.json` on Desktop/Downloads
- Transient SQLite/state: `state.db-shm`, `state.db-wal`, `*.lock`, `*.pid`, `gateway.pid`
- Regenerable: `cache/`, `image_cache/`, `audio_cache/`, `bootstrap-cache/`, `logs/`, `sandboxes/`, `pending_messages/`, `node/`, `bin/`, `pairing/`
- Junk: `hermes-setup.exe`, `models_dev_cache.json`, `provider_models_cache.json`, `ollama_cloud_models_cache.json`, `update_check`

## The hermes-workspace gotcha
`~/hermes-workspace` (often multi-GB, has its own `.git`) is a clone of the **Hermes source repo** — NOT user work. Do not back it up: huge, already on GitHub, and contains `.env` secrets. Check for it before assuming the user's "files" live there.

## Git-only push flow (no gh CLI installed)
1. Get repo URL from user (e.g. `https://github.com/owner/REPO.git`). Confirm it's **their** private repo.
2. **Probe safely** — private repos hang `git` waiting for credentials:
   ```bash
   export GIT_TERMINAL_PROMPT=0
   timeout 40 git ls-remote https://github.com/OWNER/REPO.git; echo "EXIT=$?"
   # empty output + exit 0 → repo exists but private (or empty);
   # clone/auth failure → different error text
   timeout 20 curl -s https://api.github.com/repos/OWNER/REPO   # 404 = private OR nonexistent (indistinguishable anonymously)
   timeout 15 curl -sI https://github.com                        # sanity-check network first (can be slow/blocked from RU)
   ```
3. Access = Personal Access Token (classic, scope `repo`; or fine-grained limited to that one repo, Contents read/write — recommend this). Store: `git config --global credential.helper store` (plaintext `~/.git-credentials` — fine on a personal machine, warn the user).
4. `git init`, `git remote add origin <url>`, add files, commit, `git push -u origin main`. Check existing branch with ls-remote first.
5. **Always do one manual test push before scheduling cron** — never schedule an untested backup.

## Cron daily backup via Hermes cronjob tool
- Schedule: `0 23 * * *` (daily 23:00) or user's preference.
- Use `no_agent=True` + `script` (`.sh` runs via bash on Windows, else Python). Script: rsync/cp include-list → staging dir (or git within profile dir + `.gitignore`), commit with date message, push.
- Watchdog semantics: non-empty stdout is delivered verbatim; **empty stdout = silent success**; non-zero exit → error alert. So print only on failure by default — but ASK the user whether they want a daily "backup OK" message or silence (Alexey was asked, not yet answered).
- The job must be self-contained (fresh session, no chat context).
- **Delivery on desktop/CLI resolves to `local`** — there is no live chat-delivery channel, so the job's output is written to `cron/output/` (review via `cronjob action=list`) and NOT pushed into the conversation. Combined with the silent-on-success watchdog, that means a working daily backup is completely invisible to the user — that's expected, not a failure. The `cronjob` response itself (not delivery) is the way to confirm liveness: `last_status: ok`, `execution_success: true`, `next_run_at` set.

## Pitfalls
- `git ls-remote` on a private repo without creds **hangs indefinitely** → always `GIT_TERMINAL_PROMPT=0` + `timeout`.
- GitHub API returns 404 for private AND nonexistent repos — you cannot tell them apart anonymously; confirm with the authenticated token call once you have it.
- Never commit tokens; keep `credential.helper store` only on the user's own machine.
- Windows git-bash: POSIX paths (`/c/Users/...`) work alongside native; `du -sh` on huge dirs can time out — limit scope.
- **CRLF noise breaks the watchdog contract.** On Windows, `git add` prints "LF will be replaced by CRLF" warnings to stderr, and `$(bash script 2>&1)` captures them → the run no longer looks `silent`, and cron's empty-stdout check misfires. Fix at first run: create `.gitattributes` with `* -text` in the repo root (script does this). Verify with a silent-run check, not just exit code.
- **Nested include paths get flattened.** `cp -r "$HERMES_HOME/$item" "$PROFILE_DIR/"` puts `scripts/backup_hermes.sh` into `profile/backup_hermes.sh`, not `profile/scripts/`. Before copying, `mkdir -p "$PROFILE_DIR/$(dirname "$item")"` and copy into that directory. Include `scripts/backup_hermes.sh` itself in INCLUDE so the backup script is recoverable from its own backup.
- Always do **one manual test run + `cronjob action=run`** after creating the cron job; confirm `last_status: ok` before telling the user it's live.

## Verification (run before declaring done)
`scripts/verify_backup.sh` runs the full checklist ad hoc: bash syntax, .gitignore secret guards, silent end-to-end run, .gitattributes present, clean working tree, local HEAD == remote HEAD, no secrets tracked, key artifacts tracked. Run it after any change to the backup script or include list.

## References
- `references/alexey-setup.md` — current user's live setup: private repo, validated inventory, pending steps.
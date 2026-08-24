# Alexey's backup setup (live state, 2026-08-09 — COMPLETE & VERIFIED)

Machine: Windows 10, git-bash (MSYS) shell. Hermes profile root (real `$HERMES_HOME`):
`C:\Users\Administrator\AppData\Local\hermes` (NOT `~/.hermes` — that's the docs fallback).

## What the user wants
- Backup scope = **Hermes profile + chat context ONLY**. Alexey explicitly narrowed it:
  "Мне не нужен бекап с моего компьютера, главное — чтобы мы с тобой не потеряли наше
  общение, контекст и смысл." → his business files are NOT included.
- His business files live in `~/Downloads` (торги/банкротство протоколы, WB отчёты/УПД,
  налоговые документы) — left out on purpose.
- `~/hermes-workspace` (1.9 GB) = clone of the Hermes SOURCE repo — NOT backup material;
  contains `.env` secrets.
- Daily backup at 23:00, watchdog mode = **silent on success** (he never answered the
  "daily OK message vs silence" question; silence was implemented as the default).

## Repo + access state (DONE)
- Backup repo: `https://github.com/AlexUser-RF/HERMES.git` (private). Anonymous API 404 is
  expected for private repos — confirmed with authenticated token call instead.
- gh CLI NOT installed → git-only flow.
- PAT (classic, scope `repo`) provided by user, stored via `git config --global credential.helper store`
  → plaintext `~/.git-credentials`. Git identity: `AlexUser-RF` / `AlexUser-RF@users.noreply.github.com`.
- Local mirror repo: `C:\Users\Administrator\hermes-backup` (`git init -b main`, origin = HERMES.git).
- Backup script: `~/AppData/Local/hermes/scripts/backup_hermes.sh` — copies INCLUDE list into
  `hermes-backup/profile/`, strips secrets, creates README/.gitattributes/.gitignore on first run,
  commits with date message, pushes. Silent on success; stderr + exit 1 on failure.
- Cron job: `hermes-profile-backup` (job_id `fb5e12b0624e`), `no_agent=True`, script `backup_hermes.sh`,
  schedule `0 23 * * *`, deliver=local. Test run (`action=run`) reported `last_status: ok`.
- First pushes landed: commits on `main` incl. the final verified one `9d29806`.
- Verification: `scripts/verify_backup.sh` in this skill → 8/8 PASS (incl. no secrets tracked).

## Validated inventory (sizes at setup time)
- `memories/` 12K (USER.md 1646B, MEMORY.md 1211B) — most valuable
- `state.db` ~1 MB, `sessions/` 4K (1 file)
- `skills/` 48 MB (includes bundled skills — fine, deltas only)
- `cron/` 26K (executions.db 20K)
- `config.yaml` 12K, `SOUL.md` 1K, `kanban.db` 116K, `projects.db` 44K
- Full include/exclude rules live in the parent SKILL.md — follow those.

## Cron design decision for this job
`no_agent=True` + `.sh` script: commit + push, print nothing on success (empty stdout = silent),
print error + non-zero exit on failure (auto alert). Job is self-contained — runs in a fresh session.

## Windows gotchas found during setup (also in SKILL.md pitfalls)
- `git add` CRLF warnings broke the silent-success contract → `.gitattributes` `* -text` fixed it.
- Nested include paths (e.g. `scripts/backup_hermes.sh`) get flattened by plain `cp -r` → must
  `mkdir -p "$PROFILE_DIR/$(dirname "$item")"` first.
- `git ls-remote` on private repo hangs without creds → `GIT_TERMINAL_PROMPT=0` + `timeout`.
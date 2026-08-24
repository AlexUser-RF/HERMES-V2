---
name: automated-git-backups
description: "Daily backups to private git remote, silent cron watchdog."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---

# Automated Git Backups (cron watchdog pattern)

Recurring backups of a profile/state/files into a private git repo, pushed automatically
every day with **zero daily noise**. Covers the working pattern for: what to include, what
to exclude, the silent-success watchdog contract, and how to verify a backup actually landed
(never trust a claimed push).

## Architecture

```
HERMES_HOME/scripts/backup_XXX.sh     ← the script (relative name resolves here for cron)
~/backup-repo/                        ← local git working copy (remote = private GitHub repo)
  ├── profile/                        ← rsync-style fresh copy of INCLUDE list
  ├── README.md                       ← created on first run
  ├── .gitattributes                  ← "* -text" (kills Windows CRLF noise)
  └── .gitignore                      ← second line of defense for secrets
```

## Script contract (watchdog)

The cron job runs `no_agent=true` with `script=backup_XXX.sh`. Delivery semantics:

- **Empty stdout + exit 0** → silent (the daily success case; no message is sent)
- **Non-zero exit / stderr** → Hermes sends an error alert (a broken backup can't fail silently)
- Non-empty stdout is delivered verbatim — keep stdout empty on success, log to stderr (`>&2`)

Commit only when something changed; exit 0 silently otherwise:

```bash
git add -A
if git diff --cached --quiet; then exit 0; fi
git commit -m "backup $(date '+%Y-%m-%d %H:%M:%S')" >/dev/null 2>&1 || { echo "commit failed" >&2; exit 1; }
git push origin main >/dev/null 2>&1 || { echo "push FAILED" >&2; exit 1; }
```

## What to include / exclude

Include (per use case — e.g. a Hermes profile): `memories/`, session/state DBs
(conversation history), `config.yaml`, `skills/`, `cron/`, `SOUL.md`, kanban/project DBs,
and the backup script itself (self-backup).

**Never commit**: `.env`, `*token*`, `*secret*`, `auth.json`, `*.lock`, `*.pid`, `*.log`,
`*.shm`, `*.wal` (SQLite scratch), cache dirs, node_modules, build artifacts. Strip them
from the copy even if the source contains them — a `find . -name "*.lock" -delete` pass
after the copy. `.env` in particular holds API keys; the token that authenticates the push
is stored via git credential.helper, not in the repo.

## Verification before claiming success

Run the script, then prove the push landed (a prior claimed-success can silently be a no-op):

```bash
# 1. working tree clean, local == remote
git status --porcelain # empty
git rev-parse HEAD; git ls-remote origin refs/heads/main
# 2. no secrets tracked
git ls-files | grep -iE '\.env$|token|secret|auth\.json'   # expect no output
# 3. key artifacts tracked
git ls-files | grep -E 'memories|state.db|config'
```

Note: `git ls-files | ...; echo $?` reports the grep status; use `PIPESTATUS[0]` or check
output emptiness, not `$?` (see `windows-git-bash` skill on MSYS hosts).

## Cron wiring

```bash
cronjob action=create name=XXX-backup no_agent=true script=backup_XXX.sh schedule="0 23 * * *"
```

Then immediately `cronjob action=run` to smoke-test the scheduled path before trusting the
next 23:00 tick.

## Pitfalls

- Fresh `rm -rf` of the staging dir each run keeps deletions accurate (rsync not required).
- Copying a file from a subdir needs `mkdir -p "$dest/$(dirname "$item")"` — naive `cp -r`
  flattens it into the staging root (caught by verification step 3).
- Windows host: run the script with `bash script.sh`; native git needs `C:/...` paths if the
  script cds by `$HOME`-derived paths (see `windows-git-bash`).
- A private repo looks "not found" to anonymous API calls — verify with the token, and only
  after `git ls-remote` succeeds with `GIT_TERMINAL_PROMPT=0`.

## References

- `references/hermes-profile-backup.md` — worked example: daily Hermes profile → GitHub
  (repo layout, exact script skeleton, cron job, first-run verification transcript).
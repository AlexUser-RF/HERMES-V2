# Worked example: daily Hermes profile → private GitHub repo

Captured 2026-08-09 while setting up Alexey's daily backup (private repo `AlexUser-RF/HERMES`,
local copy `~/hermes-backup`, cron 23:00). Reuse this skeleton for any Hermes-profile backup.

## Repo layout & remote

```bash
# local working copy (NOT hermes-home itself — keep secrets out of it)
mkdir -p ~/hermes-backup && cd ~/hermes-backup
git init -b main
git remote add origin https://github.com/OWNER/REPO.git
```

Auth (git-only, no gh CLI): `credential.helper store` + `~/.git-credentials`
(`https://USER:ghp_...@github.com`), identity
`git config --global user.name USER` / `user.email USER@users.noreply.github.com`.

## Backup script skeleton (bash)

```bash
HERMES_HOME="${HERMES_HOME:-$HOME/AppData/Local/hermes}"   # default profile home on Windows
REPO_DIR="$HOME/hermes-backup"
PROFILE_DIR="$REPO_DIR/profile"

INCLUDE=("memories" "sessions" "skills" "cron" "SOUL.md" "config.yaml"
         "kanban.db" "projects.db" "state.db" "scripts/backup_hermes.sh")

EXCLUDE_PATTERNS=("*.lock" "*.pid" "*.shm" "*.wal" ".env"
                  "google_token.json" "google_client_secret.json" "auth.json")

rm -rf "$PROFILE_DIR"; mkdir -p "$PROFILE_DIR"
for item in "${INCLUDE[@]}"; do
  [ -e "$HERMES_HOME/$item" ] || continue
  mkdir -p "$PROFILE_DIR/$(dirname "$item")"     # keep subdir paths (pitfall!)
  cp -r "$HERMES_HOME/$item" "$PROFILE_DIR/$(dirname "$item")/" || exit 1
done
cd "$PROFILE_DIR" && for pat in "${EXCLUDE_PATTERNS[@]}"; do find . -name "$pat" -delete 2>/dev/null; done
# README.md + .gitattributes ("* -text") created on first run in $REPO_DIR

cd "$REPO_DIR"
git add -A
git diff --cached --quiet && exit 0               # nothing changed → silent
git commit -m "backup $(date '+%Y-%m-%d %H:%M:%S')" >/dev/null 2>&1 || exit 1
git push origin main >/dev/null 2>&1 || { echo "push FAILED" >&2; exit 1; }
```

Key point: `state.db` + `sessions/` carry the full conversation history — for a Hermes
profile these are the crown jewels (that's what "don't lose our context" means).

## Verification run (must be green before trusting the cron tick)

Full end-to-end verification ran clean (8/8 checks):

1. `bash -n` on the script
2. `.gitignore` contains `google_token.json` and `^auth.json`
3. script run → exit 0 **and** empty stdout (watchdog silence contract)
4. `.gitattributes` exists with `* -text` (no CRLF warnings)
5. `git status --porcelain` empty (working tree clean)
6. `git rev-parse HEAD` == `git ls-remote origin refs/heads/main` (push landed)
7. `git ls-files | grep -iE '\.env$|google_token|client_secret|auth\.json'` → empty
8. all key artifacts tracked incl. `profile/scripts/backup_hermes.sh` (self-backup)

The flat-copy bug (#3 in SKILL.md) was caught exactly by check 8: the script's self-backup
landed at `profile/backup_hermes.sh` instead of `profile/scripts/backup_hermes.sh`.

## Cron

```bash
cronjob action=create name=hermes-profile-backup no_agent=true \
        script=backup_hermes.sh schedule="0 23 * * *"
# then immediately: cronjob action=run → last_status: ok
```

`no_agent=true` + silent-success script = no LLM tokens burned per tick, no daily spam;
a failed push alerts automatically.

## Not backed up (by design)

`~/.env` (API keys incl. OpenRouter), Google OAuth tokens, `auth.json`, `hermes-workspace`
git clone (1.9 GB of third-party source — already on GitHub upstream), caches, logs, node
install dir.
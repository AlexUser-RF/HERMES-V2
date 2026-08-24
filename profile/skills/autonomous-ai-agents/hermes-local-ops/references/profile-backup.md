# Profile backup → private GitHub repo

Set up 2026-08-09 for Alexey. Daily 23:00 backup of the **Hermes profile** (memory,
conversation history, config, skills) — NOT user files. User files live in
`D:\HERMES FILES`; they are deliberately not part of this job.

## Why profile, not files

Alexey's priority: never lose the conversation/context between us.
`state.db` + `sessions/` = full conversation history (the FTS5 session_search
store). `memories/USER.md` + `MEMORY.md` = who he is and current state.

## Architecture (all verified working)

- Script: `~/AppData/Local/hermes/scripts/backup_hermes.sh` (bash, runs under git-bash on Windows)
- Working copy: `~/hermes-backup` (git init -b main; remote https://github.com/AlexUser-RF/HERMES.git)
- Cron: job name `hermes-profile-backup`, schedule `0 23 * * *`, `no_agent=true`, `script=backup_hermes.sh`
  (relative script path resolves under `~/AppData/Local/hermes/scripts/`)
- Auth: `git config --global credential.helper store` + PAT (`repo` scope) in `~/.git-credentials`
- git identity: `user.name AlexUser-RF`, `user.email AlexUser-RF@users.noreply.github.com`

## Include list (relative to HERMES_HOME)

```
memories/  sessions/  skills/  cron/  SOUL.md  config.yaml
kanban.db  projects.db  state.db  scripts/backup_hermes.sh   # self-backup
```

The script is backed up too, so a disaster restore recovers the mechanism.

## Exclude patterns (stripped from the copy)

```
*.lock  *.pid  *.shm  *.wal         # transient/scratch
.env  google_token.json  google_client_secret.json  auth.json   # secrets — never in git
```

## Watchdog cron pattern (no_agent script)

- Success (pushed OR nothing changed) → **empty stdout** → silent, no delivery.
- Failure → error to stderr + non-zero exit → Hermes sends an alert. A broken
  watchdog cannot fail silently.
- Commit only when `git diff --cached` is non-quiet; message `backup <YYYY-MM-DD HH:MM:SS>`.

## Pitfalls (all hit in practice — do not repeat)

1. **Flattened sub-paths**: `cp -r "$SRC/$item" "$PROFILE_DIR/"` puts
   `scripts/backup_hermes.sh` at `profile/backup_hermes.sh` (wrong location).
   Fix: `dest="$PROFILE_DIR/$(dirname "$item")"; mkdir -p "$dest"` before copy.
2. **CRLF noise pollutes stdout**: git on Windows warns LF→CRLF on every commit,
   which breaks the silent-success contract. Fix: `.gitattributes` with
   `* -text` (script creates it on first run).
3. **`git -C /c/...` fails on native git** (MSYS): use `C:/...` paths (see umbrella invariants).
4. **Pipe masks exit codes**: `bash script.sh | tail -40` reports `tail`'s rc.
   Use `PIPESTATUS[0]` (bash) to see the script's real exit code.
5. **Private-repo probe**: anonymous `git ls-remote` on a private repo hangs
   waiting for credentials. Probe with the API instead:
   `curl -H "Authorization: token $TOKEN" https://api.github.com/repos/OWNER/REPO`
   — anonymous 404 means "private or not found"; authenticated call disambiguates.
6. **Unstaged .gitignore after fresh copy**: the backup regenerates `profile/`
   each run but repo-root files (`.gitignore`, `.gitattributes`, `README.md`)
   persist — `git add -A` picks up only the new profile content. Root files are
   created once by the script's "first run" guards.

## Verification checklist (run after any script edit)

```bash
bash -n backup_hermes.sh                                  # 1. syntax
bash backup_hermes.sh; echo "rc=$?"                       # 2. exit 0 AND empty output
cd ~/hermes-backup && git status --porcelain              # 3. empty (clean tree)
git rev-parse HEAD; git ls-remote origin refs/heads/main  # 4. local HEAD == remote
git ls-files | grep -iE '\.env$|google_token|client_secret|auth\.json'   # 5. no secrets
# 6. cron test run: cronjob action=run job_id=... → last_status: ok
```
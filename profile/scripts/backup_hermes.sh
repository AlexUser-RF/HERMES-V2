#!/usr/bin/env bash
# Daily backup of the Hermes profile (memory, sessions/context, config, skills, cron)
# to the private GitHub repo AlexUser-RF/HERMES-V2.
#
# Watchdog pattern:
#   - success (pushed or nothing changed) -> EMPTY stdout (silent)
#   - failure -> error message on stderr + non-zero exit (Hermes sends an alert)
set -uo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/AppData/Local/hermes}"
REPO_DIR="$HOME/hermes-backup"
PROFILE_DIR="$REPO_DIR/profile"
OBSIDIAN_VAULT="${OBSIDIAN_VAULT:-/d/HERMES FILES/HERMES OBSIDIAN}"
OBSIDIAN_BACKUP_DIR="$PROFILE_DIR/obsidian"

# --- What to back up (relative to HERMES_HOME) ---
INCLUDE=(
  "memories"
  "sessions"
  "skills"
  "cron"
  "SOUL.md"
  "config.yaml"
  "kanban.db"
  "projects.db"
  "scripts/backup_hermes.sh"
)

# --- Patterns stripped from the copy (secrets / scratch files, never in git) ---
EXCLUDE_PATTERNS=(
  "*.lock"
  "*.pid"
  "*.shm"
  "*.wal"
  ".env"
  "google_token.json"
  "google_client_secret.json"
  "auth.json"
)

log() { echo "[backup-hermes] $*" >&2; }

if [ ! -d "$HERMES_HOME" ]; then
  log "HERMES_HOME not found: $HERMES_HOME"
  exit 1
fi

# 1. Fresh copy of the include list
rm -rf "$PROFILE_DIR"
mkdir -p "$PROFILE_DIR" || { log "cannot create $PROFILE_DIR"; exit 1; }
for item in "${INCLUDE[@]}"; do
  if [ -e "$HERMES_HOME/$item" ]; then
    dest="$PROFILE_DIR/$(dirname "$item")"
    mkdir -p "$dest" || { log "cannot create $dest"; exit 1; }
    cp -r "$HERMES_HOME/$item" "$dest/" || { log "FAILED copying $item"; exit 1; }
  fi
done

# 1b. Backup state.db with compression (split if > 45MB to strictly respect GitHub 100MB / payload limits)
if [ -f "$HERMES_HOME/state.db" ]; then
  mkdir -p "$PROFILE_DIR/state_chunks"
  # Compress and split into 40MB chunks (state.db.gz.aa, state.db.gz.ab...)
  gzip -c "$HERMES_HOME/state.db" | split -b 40M - "$PROFILE_DIR/state_chunks/state.db.gz."
fi

# 2. Obsidian vault (notes only — skip .obsidian app config)
if [ -d "$OBSIDIAN_VAULT" ]; then
  mkdir -p "$OBSIDIAN_BACKUP_DIR"
  (cd "$OBSIDIAN_VAULT" && find . -type f -not -path './.obsidian/*' -exec cp --parents {} "$OBSIDIAN_BACKUP_DIR/" \; 2>/dev/null) \
    || { log "FAILED copying Obsidian vault"; exit 1; }
fi

# 3. Strip excluded patterns from the copy
cd "$PROFILE_DIR" || exit 1
for pat in "${EXCLUDE_PATTERNS[@]}"; do
  find . -name "$pat" -delete 2>/dev/null
done

# 4. README on first run
if [ ! -f "$REPO_DIR/README.md" ]; then
  cat > "$REPO_DIR/README.md" <<'EOF'
# HERMES backup

Private backup of the Hermes agent profile (Alexey).

Contains the conversation history (`state.db` as compressed chunks in `profile/state_chunks/`, `sessions/`), memory
(`memories/`), config, skills, cron jobs, kanban and projects state.

To restore state.db:
`cat profile/state_chunks/state.db.gz.* | gzip -d > state.db`

Secrets (`.env`, Google OAuth tokens, `auth.json`) are deliberately excluded.
EOF
fi

# 4b. .gitattributes: keep line endings verbatim (Windows git noise)
if [ ! -f "$REPO_DIR/.gitattributes" ]; then
  printf '* -text\n' > "$REPO_DIR/.gitattributes"
fi

# 5. Commit + push (only when something changed)
cd "$REPO_DIR" || exit 1
git add -A
if git diff --cached --quiet; then
  exit 0 # nothing changed -> silent
fi

DATE=$(date "+%Y-%m-%d %H:%M:%S")
git commit -m "backup $DATE" >/dev/null 2>&1 || { log "git commit failed"; exit 1; }
if ! GIT_TERMINAL_PROMPT=0 git push origin main >/dev/null 2>&1; then
  log "git push FAILED — check token/network"
  exit 1
fi

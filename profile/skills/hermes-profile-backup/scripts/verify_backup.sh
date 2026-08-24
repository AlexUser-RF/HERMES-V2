#!/usr/bin/env bash
# Ad-hoc verification for a Hermes profile backup repo (git/GitHub).
# Run after ANY change to the backup script, include list, or .gitignore.
# Customize: REPO_DIR if the local mirror lives elsewhere.
# Exit 0 = all checks pass; exit 1 = at least one FAIL.
set -u

REPO="${1:-$HOME/hermes-backup}"
SCRIPT="$HOME/AppData/Local/hermes/scripts/backup_hermes.sh"

PASS=0; FAIL=0
ok()  { echo "PASS: $1"; PASS=$((PASS+1)); }
bad() { echo "FAIL: $1"; FAIL=$((FAIL+1)); }

[ -f "$SCRIPT" ] || { echo "FAIL: backup script not found at $SCRIPT"; exit 1; }
[ -d "$REPO/.git" ] || { echo "FAIL: not a git repo at $REPO"; exit 1; }

# 1. Syntax check
bash -n "$SCRIPT" 2>/dev/null && ok "bash -n syntax check" || bad "bash -n syntax check"

# 2. .gitignore guards the known secrets
if grep -q "google_token.json" "$REPO/.gitignore" && grep -q "^auth.json" "$REPO/.gitignore"; then
  ok ".gitignore guards secrets"; else bad ".gitignore guards secrets"; fi

# 3. End-to-end run: exit 0 AND zero output (watchdog silent-success contract).
#    CRLF warnings from git add would land here via 2>&1 — that's a FAIL.
OUT=$(bash "$SCRIPT" 2>&1); RC=$?
if [ $RC -eq 0 ] && [ -z "$OUT" ]; then ok "script run: exit 0, silent"; else bad "script run: rc=$RC out='$OUT'"; fi

cd "$REPO" || { bad "cd repo"; exit 1; }

# 4. .gitattributes present with * -text (kills Windows CRLF warnings)
[ -f "$REPO/.gitattributes" ] && grep -q '\* -text' "$REPO/.gitattributes" \
  && ok ".gitattributes * -text" || bad ".gitattributes missing/wrong"

# 5. Working tree clean (nothing uncommitted after the run)
[ -z "$(git status --porcelain)" ] && ok "working tree clean" || bad "uncommitted: $(git status --porcelain | head -3)"

# 6. Local HEAD == remote HEAD (push actually landed)
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git ls-remote origin refs/heads/main 2>/dev/null | awk '{print $1}')
if [ -n "$REMOTE" ] && [ "$LOCAL" = "$REMOTE" ]; then
  ok "local==remote $LOCAL"
else
  bad "local=$LOCAL remote=$REMOTE (push may not have landed)"
fi

# 7. No secrets tracked in git
if git ls-files | grep -qiE '(^|/)\.env$|google_token|client_secret|auth\.json|git-credentials'; then
  bad "secrets tracked: $(git ls-files | grep -iE 'google_token|client_secret|auth.json|git-credentials' | head -3)"
else
  ok "no secret files tracked"
fi

# 8. Key artifacts present (adjust paths if the include list changed)
MISS=0
for f in profile/memories/USER.md profile/memories/MEMORY.md profile/state.db \
         profile/config.yaml profile/SOUL.md README.md .gitattributes .gitignore \
         profile/scripts/backup_hermes.sh; do
  git ls-files --error-unmatch "$f" >/dev/null 2>&1 || { bad "missing: $f"; MISS=$((MISS+1)); }
done
[ $MISS -eq 0 ] && ok "all key artifacts present"

echo "---"
echo "RESULT: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ]
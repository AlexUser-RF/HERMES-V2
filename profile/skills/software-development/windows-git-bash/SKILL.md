---
name: windows-git-bash
description: "Shell git, curl, taskkill from Windows git-bash/MSYS."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
---

# Windows git-bash / MSYS Shell Quirks

Hermes' `terminal` tool on Windows runs commands through git-bash (MSYS), where bash
builtins understand `/c/Users/...` paths but **native Windows executables often do not**.
This skill covers the traps and their fixes for shelling out to git, curl, taskkill,
cmd, and other native CLIs from the Hermes terminal on a Windows host.

## Core rule

- **Bash builtins / MSYS tools** (`cd`, `ls`, `find`, `cp`, `du`, bash scripts): `/c/...` paths fine.
- **Native Windows CLIs** (`git`, `curl`, `taskkill`, `cmd`, PowerShell): pass **Windows-style
  paths** (`C:/Users/...` or `C:\Users\...`) in arguments and env vars. MSYS may mangle
  `/c/...` arguments (prefixing `D:\c\...` or refusing `-C /c/...`).

## Quirks & fixes

| Symptom | Cause | Fix |
|---|---|---|
| `git -C /c/Users/...` or `git pull` in a script fails `cannot change to '/c/...'` | native git doesn't resolve MSYS paths in `-C`/`--git-dir` position | pass `C:/Users/...` (forward slashes work) or `cd` first, then run git |
| `curl -o /tmp/x.sh` → `curl: (23) client returned ERROR on write` | MSYS `/tmp` is not a real dir for native curl | write to a real workdir, e.g. `-o "$(pwd)/x.sh"` |
| `taskkill //F //PID N` → "invalid argument" | MSYS mangles `/` flags; `//` trick fails for taskkill | use `powershell -Command "Stop-Process -Id N -Force"` (works reliably from bash); `cmd //c "taskkill /F /PID N"` can drop you into interactive cmd |
| `timeout 30 git ls-remote ... \| tail; echo $?` reports 0 even on failure | `$?` is the LAST pipeline element (tail), not git | capture `PIPESTATUS[0]` (bash) or avoid the pipe for status checks |
| `git ls-remote` on private repo hangs prompting for creds | no credentials / terminal prompt | `export GIT_TERMINAL_PROMPT=0`, wrap in `timeout N`, check with GitHub API + token instead (anonymous API returns `404 Not Found` for private repos — indistinguishable from non-existent without a token) |
| CRLF warnings on every `git add` for `.sh`/text files | core.autocrlf on Windows | add `.gitattributes` with `* -text` at repo root (commit once) |
| `pnpm`/`yarn` shims error `Cannot find module '...corepack\dist\pnpm.js'` with mangled `D:\c\...` path | broken corepack shim in the Node dir | `npm install -g pnpm --force` (overwrites shims with a real pnpm) |
| third-party `install.sh` clones/updates a repo and `git pull` fails | script builds `$INSTALL_DIR` from `$HOME` as `/c/...` | run with `INSTALL_DIR="C:/Users/.../repo" bash install.sh` |

## Token auth for GitHub (git-only, no gh CLI)

```bash
git config --global credential.helper store          # persists in ~/.git-credentials
printf 'https://USER:%s@github.com\n' "$TOKEN" > ~/.git-credentials && chmod 600 ~/.git-credentials
git config --global user.name "USER" && git config --global user.email "USER@users.noreply.github.com"
```

Then verify push access with `git ls-remote` (now non-interactive). For plain API calls
use `curl -H "Authorization: token $GITHUB_TOKEN"`.

## Pitfalls

- Never pipe a command whose exit status matters into `| tail`/`| head` without checking `PIPESTATUS[0]`.
- When a bash script shells out to native git and the repo path contains spaces, quote it;
  prefer forward-slash Windows paths (`C:/Users/...`) — both bash and git accept them.
- `ls -la $(which pnpm)` to diagnose shim files: native exe vs tiny `.ps1`/bash wrapper tells
  you whether corepack (broken) or a real install backs the command.

## References

- `references/msys-quirks.md` — evidence log with the exact failing/succeeding commands.
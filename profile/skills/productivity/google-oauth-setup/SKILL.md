---
name: google-oauth-setup
description: "Google OAuth2 setup: auth flow, 403 fixes, drift."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---

# Google OAuth2 Desktop-Client Setup

Use when setting up or repairing OAuth authorization for Google APIs from CLI tools / Hermes skills on the user's machine (google-workspace, gws, custom scripts). Complements the bundled `google-workspace` skill — use this for the auth flow and pitfalls, and that skill for service commands (gmail/calendar/drive/sheets/docs) once authenticated.

## The flow (Desktop-app OAuth client, PKCE)

1. **Client secret JSON** (Application type: "Desktop app" — key tells you why: `{"installed": {...}, "redirect_uris": ["http://localhost"]}`). Save it where the tool expects it (e.g. `google_client_secret.json`).
2. **Generate auth URL** → send the exact URL to the user as a single line.
3. **User approves** → browser redirects to `http://localhost:1/?code=...&scope=...`. The page shows a connection error — **this is expected, not a failure**. Tell the user so they don't close the tab.
4. **User pastes back the ENTIRE redirect URL or just the code** → exchange it for a token. PKCE verifier is stored during step 2, so the exchange can complete later, even on a headless machine.
5. **Verify** — see Verification below.

## Pitfalls

### Error 403: access_denied — "The developer hasn't given you access to this app"
The OAuth client is in **Testing mode** and the signed-in account is not in the test-users list.
Fix: https://console.cloud.google.com/auth/audience → select the right project → **Audience → Test users → Add users** → add the account → retry the SAME auth URL (no need to regenerate).

### authuser=N — approval happened under the wrong Google account
The access_denied error URL (and the final redirect) embeds `authuser=1|2|...` — the user's browser has several Google accounts and approval went to a non-primary one. The test user added in Cloud Console must EXACTLY match the account used for approval. Check `authuser=` in the error URL, and tell the user to switch accounts in the consent screen if the wrong one is preselected.

### Skill docs newer than the installed script
The bundled google-workspace skill documents `setup.py --auth-url --services all --format json`, but older installed versions reject those flags (`error: unrecognized arguments`). Fallback: run the bare `--auth-url` — older versions default to the full scope set (gmail read/send/modify, calendar, drive, contacts, sheets, docs). Don't fight the flag gap; verify the returned URL's `scope=` param contains what the user needs.

### Auth code expired or already used
Google auth codes are single-use and expire within minutes. If the exchange fails, generate a **fresh** auth URL and redo the approval — never retry an old redirect URL.

## Verification before declaring success

1. `setup.py --check` → `AUTHENTICATED` proves a token file exists.
2. `setup.py --check-live` → `LIVE_CHECK_OK` proves a real API call succeeds (this is the meaningful one).
3. Smoke-test the actual command surface read-only (e.g. `gmail search "is:unread" --max 3`) to prove the end-to-end path the user will actually use.

## Notes

- Tokens auto-refresh; no manual refresh handling needed.
- If the app must be public later: consider moving the OAuth client out of Testing mode in Cloud Console (requires app verification for sensitive scopes).
---
name: social-autoposting
description: "Use when automating scheduled cross-platform social posts."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Social, VK, Instagram, Autopost, Scheduler]
    related_skills: [wildberries-automation, blocked-page-recovery]
---

# Social Autoposting

Building and operating pipelines that publish one platform's content to
another on a schedule (Instagram Reels → VK community and the like),
unattended, several times a week.

## When to Use

Load this skill when the user wants content **published automatically on a
schedule** to another platform — Instagram → VK cross-posting, "post N videos a
week from X to Y", a recurring auto-publisher, or operating/troubleshooting an
existing autopost job (token issues, failed posts, "why did nothing publish").
Not for one-off manual posting, and not for planning marketing copy (use
`ai-commerce-marketing`).

## Standing rules (apply to every instance)

- **Only the user's OWN content.** Reposting third-party content is copyright
  infringement plus a source-platform ToS risk. Confirm ownership before
  building anything; if it isn't theirs, say so and stop.
- **Secrets never travel through chat.** The VK token goes in `vk_token.txt`,
  browser cookies in `cookies.txt`, both inside the project folder. Ask the
  user to write the file themselves — never ask them to paste a token or cookie
  into the conversation, and never park one in `config.json`.
- **Idempotency is mandatory.** Keep a `state.json` of already-published IDs;
  a scheduled job that reposts on retry is worse than one that fails.
- **Always ship a fallback queue.** Scrapers break; give the user a `queue.txt`
  (one URL per line) that the job drains *first*, so they can push content
  manually when the auto-scan is down.
- **Alert on failure.** An unattended job that silently stops is invisible —
  wire failures to Telegram or the user's chat.
- **Verify live before scheduling.** Scope test → one real post → then cron.
  Never schedule a pipeline you have not seen publish end-to-end.
- **Cron runs only while Hermes is up.** Expect slot drift and catch-up runs if
  the machine is off at the scheduled time — tell the user.

## Standard architecture

```
queue.txt (manual)  ─┐
profile scan (auto) ─┴─► download (yt-dlp + cookies) ─► platform publish API ─► scheduler (cron)
                                       │                        │
                                  state.json (posted IDs)   alerting
```

## Platform depth

- **VK (community wall + video upload):** `references/vk-video-api.md` — the
  full `video.save → upload → wall.post` chain, argument shapes, and the error
  codes that mean "you lack a right".
- **Instagram ingest (yt-dlp vs Graph API):** `references/instagram-ingest.md` —
  why cookies are mandatory, the export method, and the stable Business/Creator
  alternative.

## Setup procedure

1. **Project folder.** Create a numbered folder under `D:\HERMES FILES` (e.g.
   `06_Instagram_VK`). Keep venv, config, secrets and downloads inside it; the
   root stays clean.
2. **Environment.** `uv venv .venv --python 3.11` then
   `uv pip install --python .venv/Scripts/python.exe -U yt-dlp requests`
   (ffmpeg is already on PATH in this environment).
3. **VK token.** Standalone app + implicit-flow URL → user token with
   `video,wall,groups,offline`; save to `vk_token.txt`. See the reference for
   the URL template and the post-2025 caveat.
4. **Instagram cookies.** Export `instagram.com` cookies to `cookies.txt` while
   logged in as the account owner.
5. **config.json** — source username, numeric `vk_group_id`, message template,
   N per run.
6. **Validate stage by stage:** `doctor` (env/token/group) → `vk-test` (is the
   `video` scope granted?) → `ig-list` (what yt-dlp sees) → `run -n 1` (one
   real post).
7. **Schedule.** Only after a successful `run`, add the cron (e.g. 2 slots/week).

## Pitfalls

- **Don't schedule on an unverified scope test.** VK's `video` right is
  *extended access*; a token can pass `wall.post` yet fail `video.save`. Test
  the exact method the job calls before telling the user it works.
- **Community tokens cannot upload video.** Use a *user* token from a community
  admin/editor; a community token fails `video.save` with code 27.
- **The source scraper is the fragile half, not the publish API.** Assume the
  platform extractor will break and design the queue + alerting around that,
  rather than presenting the job as set-and-forget.
- **Auto-update yt-dlp before each run** (`pip install -U yt-dlp`); a pinned old
  version is the most common cause of sudden scrape failures.
- **Don't reinvent the doc lookup.** VK's live docs may be blocked to the app's
  fetch tools or showing a maintenance stub — use shell `curl` (see
  `blocked-page-recovery`) and lean on cached search snippets.

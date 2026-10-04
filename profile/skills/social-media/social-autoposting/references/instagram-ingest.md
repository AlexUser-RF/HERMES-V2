# Instagram ingest for cross-posting

## Cookies are mandatory

An unauthenticated yt-dlp hit on Instagram returns **HTTP 429** immediately, so
any automated ingest needs the account's cookies.

**Preferred: a `cookies.txt` exported from the browser.** Log in as the account
owner, use the "Get cookies.txt LOCALLY" extension for `instagram.com`, and save
the file into the project. Refresh every 1–2 months, or when posts start
failing.

`--cookies-from-browser` is a fallback, not the default: recent Chrome/Vivaldi
use App-Bound Encryption, which breaks yt-dlp's cookie extraction.

## yt-dlp is fragile on Instagram

Extractor breakage recurs (404 on `/p/…`, "empty media response", missing csrf
token). Mitigations:

- `pip install -U yt-dlp` before each run.
- Keep a manual `queue.txt` fallback so posting does not stop when scraping does.
- Alert on failures; assume it will break eventually.

## Commands

```bash
# list recent posts (best-effort; the job wants reels/video)
yt-dlp --cookies cookies.txt -J --flat-playlist "https://www.instagram.com/<user>/"

# download one item
.venv/Scripts/yt-dlp.exe --cookies cookies.txt -f "bv*+ba/b" --merge-output-format mp4 \
  -o "downloads/<id>.%(ext)s" "<post-url>"
```

## Stable alternative: Instagram Graph API (Business/Creator only)

For the user's own account, switching it to a **Business or Creator** account
unlocks `GET /me/media?fields=media_type,media_url` — `media_url` is a direct CDN
mp4, no cookies and no scraping lottery. Cost: link a Facebook Page, register a
Meta app, and hold a long-lived token (~60-day refresh, itself schedulable).
Offer this route when the user asks for "set and forget".

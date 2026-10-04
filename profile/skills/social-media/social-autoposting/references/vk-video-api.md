# VK: upload video and post to a community wall

## Auth — user token via implicit flow (Standalone app)

```
https://oauth.vk.com/authorize?client_id=APP_ID&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=video,wall,groups,offline&response_type=token&v=5.199
```

- The token comes back in the URL **fragment** (`#access_token=...`).
- Pin the API version everywhere: `v=5.199`.
- **Post-March-2025 caveat:** VK moved new applications onto the VK ID flow.
  If the classic link above does not yield a token, the app/account flow has
  changed — adapt rather than assuming the URL is broken.
- **`video` is an EXTENDED access right.** For new apps it is granted only via a
  request to `devsupport@corp.vk.com` (justify: own content, own community).
  Without it `video.save` fails with access-denied (codes 15 / 204).
- The `group_id` used below is the community's **numeric** id (not its short
  name), and the token must belong to an admin/editor of that community.

## Publishing chain

1. **`video.save`** — `POST https://api.vk.com/method/video.save`
   params: `access_token`, `group_id`=<abs community id>, `name`, `description`,
   `wallpost=0`, `v`.
   → returns `upload_url`, `video_id`, `owner_id` (sometimes `access_key`).
2. **Upload the file** — `POST upload_url` as multipart with field name
   **`video_file`**. The JSON response carries `video_id` / `size`, or an
   `error` object.
3. **Wait.** Processing is asynchronous — sleep ~30–60 s before posting, or the
   wall post hangs forever in "обработка, подождите".
4. **`wall.post`** — params: `owner_id=-<abs group id>`, `from_group=1`,
   `message`, `attachments=video{owner_id}_{video_id}[_access_key]`, `v`.
   → returns `post_id`; the link is `https://vk.com/wall-<gid>_<post_id>`.

Build the attachment string from the `owner_id` that `video.save` returned.

## Error codes worth knowing

| Code | Meaning |
|---|---|
| 15 / 204 | Access denied — token lacks the required right (usually `video`). |
| 27 | Used a *community* token / wrong app type for a user-token method. |
| 100 | Invalid parameter (bad `owner_id`, malformed attachment). |

Other limits: `video.save` is capped at 5000 calls/day per app; a wall post
allows at most 10 media and must contain at least one content type.

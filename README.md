# HERMES backup

Private backup of the Hermes agent profile (Alexey).

Contains the conversation history (`state.db` as compressed chunks in `profile/state_chunks/`, `sessions/`), memory
(`memories/`), config, skills, cron jobs, kanban and projects state.

To restore state.db:
`cat profile/state_chunks/state.db.gz.* | gzip -d > state.db`

Secrets (`.env`, Google OAuth tokens, `auth.json`) are deliberately excluded.

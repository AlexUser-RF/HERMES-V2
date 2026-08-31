# Profile Session Reset & State Management

## Overview
Hermes manages multi-profile states under `$LOCALAPPDATA/hermes/profiles/<profile_name>/`.
Each profile has its own `state.db` (sessions, message logs, model usage, FTS indexes), `memories/` (`MEMORY.md`, `USER.md`), `skills/`, and configuration.

When a user requests to clear context / reset session for a specific bot profile (e.g. `flipping` or `realty-scout`):

## Core Motivation: Cost & Token Optimization
The primary purpose of clearing context is **avoiding token overpayment and reducing API costs** on long conversational threads.
- Never delete long-term memories (`MEMORY.md`, `USER.md`), system personality (`SOUL.md`), project notes, or spreadsheets.
- If there is any doubt about what to delete or keep, **always ask the user first**.
- Safe default behavior: wipe ONLY message history (`messages`, `sessions`, `fts`), keeping knowledge bases completely intact.

### 1. Clarification & Scope
Always clarify or confirm what level of reset is requested:
- **Session history only (Recommended)**: Clears conversation history and tokens, keeps `SOUL.md`, `memories/`, `skills/`, and Telegram configuration intact.
- **Full profile reset**: Deletes memories and customizations (requires explicit confirmation).

### 2. Session Reset Procedure (Safe Pattern)

1. **Backup State DB first**:
   ```bash
   mkdir -p "$LOCALAPPDATA/hermes/profiles/<profile>/desktop-backups"
   cp "$LOCALAPPDATA/hermes/profiles/<profile>/state.db" "$LOCALAPPDATA/hermes/profiles/<profile>/desktop-backups/state_backup_before_reset_$(date +%Y%m%d_%H%M%S).db"
   ```

2. **Execute Clean Reset via SQLite Backup Template (Safe Pattern)**:
   > **Критически важно:** Нельзя вручную удалять строки из теневых таблиц FTS5 (`messages_fts_data`, `messages_fts_idx` и др.) через `DELETE`, так как это повреждает внутренний заголовок формата индекса FTS5 (`invalid fts5 file format (found 0, expected 4 or 5)`).
   > Для безопасной очистки всегда используется очистка основных таблиц и перестроение через `INSERT INTO table(table) VALUES('rebuild')`:

   ```python
   import os, sqlite3

   db_path = os.path.expandvars(r'%LOCALAPPDATA%\hermes\profiles\<profile>\state.db')
   conn = sqlite3.connect(db_path)
   cur = conn.cursor()

   # Clear session messages & usage
   cur.execute('DELETE FROM messages')
   cur.execute('DELETE FROM session_model_usage')
   cur.execute('DELETE FROM sessions')
   cur.execute('DELETE FROM system_prompts')

   # Rebuild FTS5 indexes properly
   cur.execute("INSERT INTO messages_fts(messages_fts) VALUES('rebuild')")
   cur.execute("INSERT INTO messages_fts_trigram(messages_fts_trigram) VALUES('rebuild')")

   conn.commit()
   cur.execute('VACUUM')
   conn.commit()
   conn.close()
   ```

3. **Verify Integrity**:
   - Verify `sessions` and `messages` count is 0.
   - Verify `SOUL.md`, `memories/MEMORY.md`, and `memories/USER.md` are preserved.

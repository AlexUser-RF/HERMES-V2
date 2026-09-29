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

## Telegram / Gateway Session Reset
When Telegram context grows too large (e.g. hundreds of messages in DM chat `242447706`), it can be reset without losing bot memory:
- **Direct in-chat command**: send `/new` or `/reset` in Telegram DM. The gateway starts a clean session immediately.
- **System reset via SQLite**: target the main profile's `state.db` (or profile state if routed). Find session via `SELECT id FROM sessions WHERE source = 'telegram' AND chat_id = ?`, delete its messages from `messages`, delete the session row, and rebuild FTS5 indexes. Keep `channel_directory.json` and gateway configurations untouched.

### 2. Multi-Profile Desktop & Gateway Reset Nuance
- **Bot Mode / In-App Bot Chats («This chat never resets» / Команда не работает)**:
  - В бот-чатах десктопного интерфейса Hermes (вкладка Bots) и привязанных сессиях команда `/new` не сбрасывает диалог («This chat never resets...»). Попытка отправлять `/new` в боте воспринимается как обычный пользовательский текст и ничего не обнуляет.
  - Если пользователь пишет «очисть контекст во флиппинге [или другом боте]» и на встречные предложения/инструкции отвечает «Сделай сам, в боте команда не работает»:
    1. Не предлагать повторно нажать кнопки или ввести `/new`.
    2. Мгновенно определить целевой профиль бота (например, `profiles/flipping/state.db`).
    3. Создать бэкап `state.db` в `desktop-backups/`.
    4. Выполнить SQL-очистку таблиц `messages`, `sessions`, `session_model_usage`, `system_prompts`, перестроить FTS (`INSERT INTO ... VALUES('rebuild')`) и сделать `VACUUM`.
    5. Удалить временные дампы `sessions/request_dump_*.json`.
    6. Кратко доложить результат (сколько сообщений очищено, файл бэкапа сохранён).
- **Desktop Bot Mode Notice («This chat never resets»)**:
  - В десктопном приложении Hermes при открытии чата с ботом (вкладка Bots) отображается уведомление: *«This chat never resets. Bot chats are one continuous conversation — compacting instead. For a throwaway session with this bot, use Sessions mode.»*
  - Команды `/new` и `/reset`, отправленные внутри десктопного чата в режиме Bots, интерфейс не сбрасывают (диалог трактуется как непрерывный с автоматической компрессией).
  - Когда пользователь говорит «очисти контекст в боте [профиль]» или «очисти контекст во всех ботах/чатах», он ждет не советов по UI или команды `/compress`, а **прямого программного сброса контекста (Zero-Overhead Reset)** через бэкап и очистку `state.db`.
- **Global Context Reset ("Очисть контекст во всех чатах и ботах")**:
  - При запросе сбросить контекст везде: итерировать по списку всех профилей (`profiles/coach`, `profiles/divine-element`, `profiles/flipping`, `profiles/gallery17`, `profiles/realty-scout`), бэкапить и очищать `state.db` каждого бота.
  - В корневом профиле (`default`) при очистке старых сессий **всегда сохранять текущую активную сессию**, из которой ведётся диалог (иначе прервётся текущий контекст взаимодействия с пользователем).
- **Desktop UI Reset for the Active Session ("Сделай сам" / UI-Side Session Switch)**:
  - Очистка `state.db` на диске обнуляет историю базы данных, но запущенный интерфейс Electron/Desktop держит в памяти активное состояние текущего окна и композера.
  - Если пользователь просит сбросить контекст прямо в текущем чате и требует сделать это автоматически («Сделай сам», «сделай это сейчас» без ручного нажатия `Ctrl+N` / New Chat):
    - Сначала обнулить `state.db` (с бэкапом).
    - Затем программно активировать окно Hermes и послать хоткей `Ctrl+N` через PowerShell:
      ```bash
      powershell -NoProfile -Command '$wshell = New-Object -ComObject wscript.shell; if ($wshell.AppActivate("Hermes")) { Start-Sleep -Milliseconds 250; $wshell.SendKeys("^n"); "Sent Ctrl+N" } else { "Hermes window not found" }'
      ```
    - Это переключает UI на чистый черновик сессии без необходимости ручных кликов со стороны пользователя.
- When resetting conversational context for secondary bot profiles (e.g. `flipping` or `gallery17`), user desktop chat sessions in that profile are tagged with `source = 'desktop'`, not `'telegram'`. Always inspect `SELECT id, source, message_count FROM sessions` across the profile's `state.db` before deciding which records to purge.
- Always check and purge accumulated request dump JSON files under `$LOCALAPPDATA/hermes/profiles/<profile>/sessions/request_dump_*.json` in the same cleanup pass; leaving hundreds of request dumps degrades startup latency.

### 3. Session Reset Procedure (Safe Pattern)

> **Execution Speed Rule (Zero-Overhead Reset):**
> When the user asks to clear context / reset sessions for a profile, execute the reset IMMEDIATELY without wandering into open-ended codebase exploration, grep for helper scripts, or searching internal test fixtures. The DB location and query pattern are fixed and known. Do not spend multiple tool turns investigating past backup scripts — run the backup + SQL wipe directly.

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

3. **Purge request dumps from sessions folder**:
   In addition to clearing `state.db`, Hermes accumulates API request dump files under `$LOCALAPPDATA/hermes/profiles/<profile>/sessions/request_dump_*.json`. Remove them to free disk space and avoid stale context cache ingestion:
   ```bash
   rm -f "$LOCALAPPDATA/hermes/profiles/<profile>/sessions"/request_dump_*.json
   ```

4. **Verify Integrity**:
   - Verify `sessions` and `messages` count is 0.
   - Verify `SOUL.md`, `memories/MEMORY.md`, and `memories/USER.md` are preserved.

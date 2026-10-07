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
### 2b. Refreshing the Bot chat ON SCREEN — `Ctrl+R` is a dead end

The DB wipe clears history for good, but it does not move the session the window is showing. Two wrong levers and one right one:

- **`Ctrl+R` does nothing here.** Verify before blaming the user: Hermes Desktop registers no global reload accelerator — the only `reload` in the app source is `src/contrib/runtime-loader.ts`, for plugin hot-swap. So `Ctrl+R` neither reloads the window nor resets a chat, and even a true window reload would just re-open the SAME session, because a Bot chat is the profile's persistent «forever chat».
- **`Ctrl+N` / New Chat** opens a throwaway draft in Sessions mode; inside Bot Mode it is not the reset for a bot.
- **The lever that works — «New chat with this bot».** In the Bots rail, right-click the bot → context menu item **`New chat with this bot`** (English; ja / zh / zh-TW are localized, there is no ru locale, so the UI reads English). It calls `newBotChat(bot)` → `host.newChat(route, { workspaceMode: 'bots', workspaceOwnerKey })` — source: `src/plugins/hermes-bots/data.ts`, menu item rendered in `bot-row.tsx` as `b.bot.newChatWith`. This opens a fresh empty Bot chat — the visible clean slate.

Do the `state.db` wipe yourself first, then give the user that single UI step. Do not loop on `Ctrl+R` instructions or on explaining the «This chat never resets» notice.

**Sessions mode (the ordinary chat) is the same trap.** `Ctrl+R` is equally dead there — the app binds no reload chord at all — and a relaunch re-opens the last session, so the transcript «doesn't disappear». The fresh-context chord is `session.new` = **`Ctrl+N`** (Windows/Linux; the sidebar «New Session» button runs the identical action) — it drops to a new empty draft while the old session stays in the list. `Ctrl+T` (`session.newTab`) opens a fresh session as a tab; `Ctrl+Shift+N` (`session.newWindow`) a new window. To get an old session off the screen use **Archive** (`session.archive`), never reload. Defaults verified in `apps/desktop/src/lib/keybinds/actions.ts` and `combo.test.ts` (`session.new`→`mod+n`).

### 2c. When a single profile 401s while root works — dead copied key, not config

Symptom: every turn in one specialist profile fails `HTTP 401` (`Missing Authentication header` / `401 Unauthorized`) while the root profile and a direct `POST /chat/completions` with root's key are fine. Cause: the profile's own `profiles/<p>/.env` (and, via the runtime, the pool entry in its `auth.json`) still carries an OLD copied `OPENROUTER_API_KEY` that was never updated when the root key rotated. `base_url` is usually already correct — the dead key is the whole failure.

- Prove it with a real completion, never `GET /models` (RouterAI serves its catalog regardless of the bearer token, so `/models` returns 200 even for a dead key — see `scripts/probe_routerai_key.py`).
- Fix: back up `.env` and `auth.json`, write the WORKING key into BOTH (env line + the manual `RouterAI` pool entry at priority 0 with `base_url: https://routerai.ru/api/v1`), clear the cooldown with `hermes --profile <p> auth reset openrouter`, then re-probe with a completion.
- The runtime re-materializes an `env:OPENROUTER_API_KEY` pool entry (priority 1, `base_url` canonical `openrouter.ai`) on the next read — that is expected and harmless as long as the manual RouterAI entry stays at priority 0.
- Verify end-to-end with a real completion, and never trust stdout alone: `hermes --profile <p> -z "Reply with exactly one word: PONG" -t ''` (empty toolset). A full-toolset oneshot on the desktop platform can sit past the timeout with EMPTY stdout while the turn actually SUCCEEDED — the reply is persisted as a session in the profile's own `state.db`, titled by the answer (e.g. `PONG`, `PONG #2`), so read `sessions`/`messages` there before declaring the profile broken. Also: root prints `auth status openrouter` = `logged out` too, with working api_keys — that line is never evidence of a config problem.
- `hermes --profile <p> auth status openrouter` prints `logged out` even when api_key credentials are present — it reflects OAuth/session state, not the key pool; judge by `hermes --profile <p> auth list` and by a live completion, not by that line.

- When resetting conversational context for secondary bot profiles (e.g. `flipping` or `gallery17`), user desktop chat sessions in that profile are tagged with `source = 'desktop'`, not `'telegram'`. Always inspect `SELECT id, source, message_count FROM sessions` across the profile's `state.db` before deciding which records to purge.
- Always check and purge accumulated request dump JSON files under `$LOCALAPPDATA/hermes/profiles/<profile>/sessions/request_dump_*.json` in the same cleanup pass; leaving hundreds of request dumps degrades startup latency.

### 2a. «Перезапусти» after a reset — check what is actually running FIRST

A reset request is often followed by "перезапусти". Before promising or attempting any restart, establish what actually serves the profile:

- **Desktop bot profiles usually have NO gateway.** `hermes --profile <p> gateway status` commonly answers *Gateway is not running* while a **stale `gateway_state.json`** still claims `gateway_state: "running"` with a long-dead `pid`. Never assume a gateway exists because the state file says so — run the status check.
- **Read the process tree before killing anything** (`Get-CimInstance Win32_Process -Filter "Name='python.exe' or Name='hermes.exe' or Name='Hermes.exe'" | Select ProcessId,ParentProcessId,Name`). Topology: `python.exe` (argv `… .hermes/bin/hermes.exe --profile <p> serve --host 127.0.0.1 --port 0`) → parent `hermes.exe` → parent `Hermes.exe` (Electron main). The backend answering the CURRENT conversation is a **child of the Electron app**, so restarting the app tears down the process generating the reply. Hermes can auto-resume the turn afterwards via `desktop/interrupted_turns.json` (`auto_continue: true`), but warn the user before doing it — never restart the app silently mid-conversation.
- **A renderer reload is not visible in backend logs.** `logs/gui.log` / `logs/desktop.log` only record backend `tui_gateway.server` activity (prompt accepted / turn finished), so you cannot confirm from logs that the window refreshed. Confirm visually with the user, or use the app-level restart — do not assert the reload succeeded.
- **Match the lever to the need.** A DB context reset needs no restart at all: the context is already empty; only the UI has to re-read it (re-opening the bot tab / a window refresh). Do not sell "restart the gateway" as the fix for a profile that has no gateway.
- **Approval-gated commands**: `hermes gateway restart` and `powershell -Command …SendKeys…` hit the approval prompt. If the user is not watching, the call returns BLOCKED (no consent) — surface that and stop; do not re-issue the same command.

### 3. Session Reset Procedure (Safe Pattern)

> **Execution Speed Rule (Zero-Overhead Reset):**
> When the user asks to clear context / reset sessions for a profile, execute the reset IMMEDIATELY without wandering into open-ended codebase exploration, grep for helper scripts, or searching internal test fixtures. The DB location and query pattern are fixed and known. Do not spend multiple tool turns investigating past backup scripts — run the backup + SQL wipe directly.

1. **Backup State DB first**: if a `state.db-wal` file is present next to the DB (a live backend is attached — the normal case while Desktop is open), take the backup with the SQLite **backup API**, not `cp`. A plain `cp` copies the main file WITHOUT the WAL and yields a torn snapshot missing the newest writes; the backup API folds the WAL in. `cp` is only safe when no `-wal` exists.
   ```bash
   mkdir -p "$LOCALAPPDATA/hermes/profiles/<profile>/desktop-backups"
   ```
   ```python
   import sqlite3, time
   src = sqlite3.connect(r'%LOCALAPPDATA%\hermes\profiles\<profile>\state.db')
   dst_path = r'%LOCALAPPDATA%\hermes\profiles\<profile>\desktop-backups\state_backup_before_reset_%s.db' % time.strftime('%Y%m%d_%H%M%S')
   dst = sqlite3.connect(dst_path)
   with dst:
       src.backup(dst)   # consistent snapshot, includes -wal
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
   - Run `PRAGMA integrity_check` — it must return `ok`. Corrupted FTS5 shadow tables surface here (and later as `invalid fts5 file format`); a clean `ok` is the proof the rebuild was safe.
   - Verify `SOUL.md`, `memories/MEMORY.md`, and `memories/USER.md` are preserved (compare sizes, not just existence).
   - **Expected regeneration — do not loop**: if Desktop is open, it re-inserts ONE empty session shell for the bot within seconds (`sessions`=1, `messages`=0). That is the UI recreating its chat container, NOT a failed reset. Report success on `messages`=0 and never re-wipe to chase the `sessions` count back to 0.

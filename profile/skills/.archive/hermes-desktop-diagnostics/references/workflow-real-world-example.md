# Worked example: "Hermes Desktop installed, but the dialog is not visible"

Real session (2026-08-09, Windows 10, Hermes v0.20.0, user on Telegram speaking Russian). User had both Hermes Desktop and the Telegram gateway on the same machine, and the "invisible dialog" turned out to be surface confusion, not a broken app. This is the fastest path to that conclusion.

## Timeline reconstructed from logs

| Time | Evidence | Meaning |
|---|---|---|
| 17:25 | `agent.log`: `conversation turn: session=20260809_172522_ae8b3d … platform=desktop msg='Привет!'` + session in DB with 2 messages | Desktop chat WORKED — user typed and got a reply in the app |
| 17:36–17:37 | `gui.log`: `Messaging platform updated: platform=telegram … enabled=False` then `enabled=True`, then `enabled=None env_keys=['TELEGRAM_BOT_TOKEN']`; `gateway.pid` mtime 17:37 | User was in desktop settings toggling/entering the Telegram bot token; gateway restarted |
| 17:41 | `gui.log`: "Desktop cron scheduler started"; `desktop.log`: "Hermes backend is ready. Finalizing desktop startup" (port 62745) | Desktop backend restarted cleanly |
| 17:41:27 | `state.db`: new session `source='telegram'`, 24 messages, title "Приветствие и предложение помощи #2" | The current conversation is a TELEGRAM session |

## Key evidence chain (the 3 probes that settled it)

1. **App alive:** `wmic process get name,processid 2>/dev/null | tr -d '\0' | grep -i -E "hermes|electron"` → 5 × `Hermes.exe` (6128, 16632, 12780, 8624, 5012). Note: plain `tasklist | grep` printed `Binary file (standard input) matches` (UTF-16) — useless without `wmic`+`tr -d '\0'`.
2. **Gateway is a separate process:** `gateway_state.json` → `{"pid":10164, "kind":"hermes-gateway", "platforms":{"telegram":{"state":"connected"}}, "active_agents":1}`.
3. **Both sessions in one store:** python sqlite3 on `~/AppData/Local/hermes/state.db` →
   `SELECT id, source, title, message_count FROM sessions` returned exactly two rows: `source='desktop'` (2 msgs, 17:25) and `source='telegram'` (24 msgs, 17:41).

## The resolve

Architecture explanation to the user (in Russian):
- Desktop and Telegram-бот — два разных интерфейса одного Hermes.
- Текущий диалог идёт через Telegram-шлюз (отдельный фоновый процесс), поэтому он не «стримится» в окно десктопа.
- Обе сессии лежат в общей базе → Telegram-диалог есть в левом списке сессий десктопа, можно кликнуть и продолжить там.
- Окно могло быть свёрнуто в трей / чат-панель пустая без выбранной сессии.

Then a `clarify` question with options (blank window / tray-hidden / session missing from sidebar / white screen). User confirmed the explanation was enough — no bug at all.

## Lessons

- Before deep-diving, verify the app ever worked: one `agent.log` `platform=desktop` turn proves it.
- The `gui.log` "Messaging platform updated" lines are a precise record of the user's settings actions — read them before asking the user what they did.
- Session `title` is auto-generated ("Приветствие и предложение помощи"), not user-chosen — don't rely on it for identification; use `source` + timestamps.
- Language: respond in the user's language (this user writes in Russian).
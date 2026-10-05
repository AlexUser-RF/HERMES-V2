# Telegram Gateway & VPN Reconnect / Windows Service Quirks

## Problem
In Russia, direct connections to Telegram's API (`api.telegram.org`) are blocked without VPN/proxy.
When the user toggles VPN on/off:
1. Active TCP sockets to Telegram break.
2. The Telegram adapter attempts reconnects (`attempt 1/8` .. `8/8`).
3. If reconnects fail while VPN is off, the gateway process terminates.

## Windows Scheduled Task Behavior
The `Hermes_Gateway` scheduled task executes `Hermes_Gateway.vbs`, which spawns `python.exe -m hermes_cli.main gateway run` with `wscript.Run(..., 0, False)`.
- `False` means `wscript.exe` exits immediately after spawning.
- Task Scheduler marks the task as completed (`Ready`), so `RestartCount` and restart triggers do NOT auto-restart the failed background Python process.

## Safe Restart from Agent Session
- Calling `hermes gateway restart` from within a gateway session is BLOCKED by safety guards (SIGTERM propagation).
- To restart via Windows Task Scheduler without crashing the tool session:
  ```powershell
  powershell.exe -Command "Start-ScheduledTask -TaskName 'Hermes_Gateway'"
  ```
- To verify the gateway process is running:
  ```bash
  hermes gateway status
  ```

## Quick Connection Check (2 commands)
1. **Probe the bot token**: read `TELEGRAM_BOT_TOKEN` from `$LOCALAPPDATA/hermes/.env` and GET `https://api.telegram.org/bot<token>/getMe` with `urllib` (timeout 15s). Timeout = API unreachable (VPN off in RF); `ok: True` = token live.
2. **Tail the gateway log**: last lines of `$LOCALAPPDATA/hermes/logs/gateway.log` — `Telegram polling confirmed healthy: getUpdates progressing` = receive path live; `Connected to Telegram (polling mode)` + `set_my_commands OK` = full reconnect after a VPN toggle (the adapter reconnects itself, no restart needed).
`hermes gateway status` prints `✗ Gateway is not running` from any Desktop-only profile (`use_gateway: false`, e.g. nocturne) even while the bot is healthy — the Telegram channel is owned by the profile running `serve` (default, listed under "Other profiles"). Do not trust that line alone; getMe + gateway.log are the source of truth.

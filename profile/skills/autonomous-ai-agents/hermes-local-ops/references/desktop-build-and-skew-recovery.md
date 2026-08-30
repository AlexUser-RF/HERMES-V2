# Desktop Rebuild & "App build out of date" Troubleshooting on Windows

## Context & Symptoms
After `hermes update` advances the runtime repository (`origin/main`), the Desktop UI application may show a warning banner:
**"App build out of date: The Hermes runtime was updated, but the desktop app itself is still an older build..."**

This happens because `apps/desktop/` or its parent repository changed, causing `detectRendererSkew()` to compare `apps/desktop/release/win-unpacked/resources/install-stamp.json` against `HEAD`.

## Key distinction: `build` vs `pack` (root cause of "nothing changed")
- **`npm run build`** (in `apps/desktop`) compiles the Vite frontend into `apps/desktop/dist` — the SOURCE-mode bundle. A running packaged Desktop app does **NOT** render from here.
- **`npm run pack`** (in `apps/desktop`, electron-builder) produces the actual packaged exe in `apps/desktop/release/win-unpacked/`. **This** is what the launched `Hermes.exe` renders from.
- So after an update, `npm run build` alone changes nothing the user can see. To visibly update the app you must `npm run pack` AND fully close the running Desktop window first, because a live `Hermes.exe` locks `release/win-unpacked/Hermes.exe` and the pack/electron-builder fails with "Access is denied" / `ERR_ELECTRON_BUILDER_CANNOT_EXECUTE`. `hermes desktop --build-only` drives this same pack path for the installer's --update flow.
- **Authoritative check of what the exe actually contains:** read `apps/desktop/release/win-unpacked/resources/install-stamp.json` — it records the `commit` and `builtAt` the packaged app was built from. If its commit trails `HEAD`, the running app really is stale; if it matches HEAD the app is fresh even when the `desktop-build-stamp.json` marker is out of sync (that marker is cosmetic/fail-quiet).
- The `desktop-build-stamp.json` marker and the in-exe `install-stamp.json` can disagree. When the exe is fresh (stamp = HEAD) but the banner persists, it is almost always the external marker being stale rather than the app truly being old.

## Build & Update Workflow
1. Rebuild the frontend bundle in `apps/desktop`:
   ```bash
   cd apps/desktop
   npm run build
   ```
2. Update the build stamp `$HERMES_HOME/desktop-build-stamp.json` so the hash matches the source tree:
   ```python
   import json, sys
   from datetime import datetime, timezone
   from pathlib import Path
   sys.path.insert(0, r'C:\Users\Administrator\AppData\Local\hermes\hermes-agent')
   from hermes_cli.main import _compute_desktop_content_hash, PROJECT_ROOT

   stamp_file = Path(r'C:\Users\Administrator\AppData\Local\hermes\desktop-build-stamp.json')
   content_hash = _compute_desktop_content_hash(PROJECT_ROOT)
   stamp_data = {
       'contentHash': content_hash,
       'sourceMode': False,
       'builtAt': datetime.now(timezone.utc).isoformat()
   }
   stamp_file.write_text(json.dumps(stamp_data, indent=2) + '\n', encoding='utf-8')
   ```
3. Restart the Desktop application (close window and relaunch) so Electron reloads the fresh renderer bundle.

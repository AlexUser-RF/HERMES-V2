# Profile Assets & Bot Avatar Operations

This reference documents how avatar assets and visual identity are stored, synced, and managed across profiles on this machine.

## Asset Storage Locations

1. **Default Profile Asset:**
   `C:\Users\Administrator\AppData\Local\hermes\assets\avatar.png`
   Used by Desktop UI and Gateway for default identity rendering.

2. **Named Profiles Assets:**
   `C:\Users\Administrator\AppData\Local\hermes\profiles\<profile>\assets\avatar.png`
   (e.g. `C:\Users\Administrator\AppData\Local\hermes\profiles\flipping\assets\avatar.png`)

3. **User Project / Obsidian Vault:**
   `D:\HERMES FILES\HERMES OBSIDIAN\Hermes_Avatar_Flipping_Partner.png`
   Kept for easy access, documentation, and user inspection.

## Setting / Updating Avatars

When the user requests an avatar update:
- Save or copy the high-res PNG to the above target paths.
- Ensure the directories exist (`os.makedirs(..., exist_ok=True)`).
- For Telegram Bot avatar, remind the user that Telegram Bot API avatar changes must be performed via `@BotFather` using `/setuserpic` (bots cannot self-modify their bot userpic via standard messaging webhooks without specific admin bot API calls).

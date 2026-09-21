---
name: hermes-personalization
description: "Use when changing Hermes personality or display settings."
version: 0.1.0
author: Alexey, Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [hermes, personalization, soul, configuration, language]
    related_skills: [efficient-local-automation]
---

# Hermes Personalization Skill

Configure Hermes for Alexey without weakening important task-specific behavior or making unverified promises about model output. This skill covers user-facing personality, SOUL.md, profile preferences, reasoning depth, and display language; it does not replace the bundled Hermes configuration reference.

## Always-On Rules

- **Ask before editing `SOUL.md`.** First inspect the current file, show the exact proposed text or diff, explain the effect, and wait for explicit approval. Never modify it autonomously, even when the change seems obviously beneficial.
- Preserve the first anchor line of `SOUL.md` byte-for-byte unless Alexey explicitly authorizes changing it.
- Put stable user preferences in the user profile or the relevant skill; put temporary operational state in memory/session notes. Do not turn a one-off incident into a permanent personality rule.
- Separate language layers before changing anything: `display.language` controls interface localization; visible interim commentary and step descriptions are model-generated; raw hidden reasoning language is not reliably controllable or necessarily exposed. Never promise that a SOUL instruction will translate every reasoning token.
- Preserve `reasoning_effort: high` for the flipping and coach profiles unless Alexey explicitly changes that priority. Improve speed with routing, batching, and display settings—not by silently lowering reasoning depth on those profiles.
- Use `hermes config set/get/check` for configuration changes, never direct patching of security-sensitive config files. After changes, verify the resolved values and state the required restart/reload boundary.
- Do not report a change as successful based only on a setter acknowledgement. Re-read or query the effective setting, run the relevant checker, and perform a small behavior or connectivity verification when practical.
- When a model/provider is active, use the runtime metadata supplied by Hermes rather than guessing from stale config or a previous turn.

## Procedure

1. **Classify the requested change.** Decide whether it affects SOUL/personality, a user/profile preference, interface localization, model routing, or a temporary session behavior.
2. **Read current state.** Inspect the relevant file/config and identify profile scope. For `SOUL.md`, prepare a minimal diff and stop for approval before writing.
3. **Choose the narrowest layer.** Use profile config for profile-specific behavior; use global config only for genuinely global behavior; use `display.language` for labels, not as a substitute for model-language instructions.
4. **Apply through the supported path.** Use `hermes config set` for config and `skill_manage`/approved file editing for skills. Keep unrelated settings untouched.
5. **Verify.** Run `hermes config get` and `hermes config check`; for language or commentary changes, test a short turn after the required restart. Confirm high reasoning remains active in the intended profiles.
6. **Report limitations honestly.** Distinguish what is guaranteed by configuration from what is only a model tendency, and do not claim hidden-reasoning control.

## Pitfalls

- **Do not edit SOUL.md before approval.** Personality changes are durable and can alter every future session, so user consent is a hard gate.
- **Do not confuse UI language with model-generated commentary.** Translating static labels does not force Gemini or an auxiliary title/progress generator to write Russian text.
- **Do not lower global reasoning to fix routine latency.** It silently degrades high-value flipping and coaching work; optimize tool routing first.
- **Do not duplicate long rules across SOUL, USER.md, and memory.** Repetition consumes every prompt and creates conflicting priorities; keep each rule in its narrowest durable home.
- **Do not claim a language switch is complete without observing the relevant surface.** Desktop labels, interim progress, tool names, final answers, and hidden reasoning can use different pipelines.

See `references/language-and-display.md` for the layer map and verification checklist.

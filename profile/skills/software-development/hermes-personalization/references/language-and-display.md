# Hermes language and display layers

## Layer map

| Layer | Typical control | What it changes | What it does not guarantee |
|---|---|---|---|
| Static Desktop/CLI labels | `display.language: ru` | Menus, status labels, UI strings that have translations | Model-generated text between tools |
| Visible interim commentary | model prompt/persona plus gateway display settings | Short plans, progress summaries, tool explanations | Every model token or UI-generated title |
| Session/title generation | `auxiliary.title_generation.language` when supported | Generated session titles or labels | General reasoning/commentary |
| Final answer | User language preference and prompt | Delivered response language | Provider internals |
| Hidden reasoning | Provider/model behavior | Usually not a stable user-controlled surface | Do not promise translation or access |

## Verification checklist

1. Query the effective setting with `hermes config get display.language` and `hermes config get display.show_reasoning`.
2. If changing config, run `hermes config check` and restart the relevant Desktop/gateway process; config changes are not assumed live in an existing turn.
3. After restart, inspect one short turn separately: static labels, interim commentary, tool names, and final answer.
4. If only generated titles remain English, inspect the configured `auxiliary.title_generation` block; do not infer that `display.language` controls it.
5. Record limitations explicitly: a Russian instruction can bias visible commentary, but a provider may still emit technical English labels or reasoning.

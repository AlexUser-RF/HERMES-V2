---
name: flipping-real-estate-assistant
description: "Use when working Alexey's real-estate flip projects."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [flipping, real-estate, renovation, design, tula, project-assistant]
---

# Flipping Real-Estate Assistant

Hermes acts as **design assistant + technical helper** on Alexey's real-estate
flipping deals (his #1 priority business: buy low, renovate, sell fast for margin).

## Core principle (always apply)

> Renovation-for-sale must be **neutral, light, technically reliable, mass-market
> friendly**. Every single decision is tested by ONE question:
> **does it raise the sale price / speed up the sale — or does it only raise the estimate?**

- Goal is NOT a bespoke interior. It is a liquid apartment that sells fast at max
  controlled-budget margin. If a decision only inflates the estimate, cut it.
- Pick one **neutral/light/soft-Scandinavian** direction: warm-white/light-gray
  walls, light-oak floor, one dark-metal accent used sparingly. Three-color rule.
- Hard "do-nots": no re-planning just for design, no kitchen/bath relocation, no
  load-bearing demolition, no colorful/dark/designer tiles, no complex ceilings,
  no over-investing in custom furniture, no finishing a balcony before the slab
  is verified.

## Financial discipline (private seller)

- For a **private seller**, renovation costs do NOT reduce the tax base: NDFL 13%
  is levied on (sale − purchase price). Per-calc: NDFL = 13% × (sale − purchase).
- If activity becomes **systematic** (multiple flips/year), tax status is at risk —
  flag USN/entity planning early, not at year-end.
- **Cycle time dominates ROI.** Annualized = cycle_return × (12/cycle_months).
  A deal that's "great" at a 2-month cycle collapses at 5–6 months. Separate the
  portion you control (renovation speed) from the portion you don't (sale time =
  market exposure). Always push to validate probable days-on-market, not just build time.
- Built-in margins: if a repair claims a +20–40% price gain, it's credible ONLY if
  the unit was bought **below market** (auction/bankruptcy/liquidation). Bought at
  market → validate the target sale price hard against live comparables.

## Sale price validation (always do this)

- A target price is an anchor, not a plan, until checked against **3–5 live
  comparable listings** in the SAME district: same type, ~same m², renovated.
- **Top-floor risk is a SALES risk**, not just a repair one: top-floor units
  systematically sell slower and at a 3–10% discount. If the target price equals
  a good mid-floor price, the top floor may be at the ceiling of its range → longer
  exposure → cycle blows out.

## Comparables research (pitfall + working path)

- Russian classifieds (CIAN, Yandex.Realty, Avito) block automated BROWSERS: CIAN →
  WAF ("подозрительный трафик"), Yandex → SmartCaptcha, Avito → VPN dialog / misleading
  "page doesn't exist". Do NOT treat "no results" as "no listings" — it's bot detection.
- **Working path found (PREFERRED): the mobile Avito endpoint `m.avito.ru` serves complete
  structured data** (`window.__initialData__`: price, price/m², area, floor, district, address,
  new/secondary marker) with working pagination — far richer and cleaner than CIAN. Recipe +
  data-extraction notes in `references/avito-mobile-scrape.md`. Try this FIRST for comparables.
- CIAN's legacy `cat.php` endpoint also serves listings to plain `curl` even when the
  interactive site blocks the browser; recipe + extraction notes in
  `references/cian-scrape-comparables.md`. Useful as a second source, but its data is noisier
  (mixed cities, loose price/address binding).
- Other aggregators: n1.ru & etagi.com return HTTP 200 but are JS shells (no data
  server-side for curl); domclick needs auth (401). Prefer the Avito mobile path above.
- If scraping is blocked/unreliable, ask Alexey to paste listing links/screenshots.

### Clickable Avito links for the user (do this)
- Comparable prices differ MOST by renovation state, not district — two units on the
  SAME street can differ by 200–500k or even 2× (e.g. Smidovich 8 at 83k/m² vs
  Smidovich 4 at 170k/m²) purely on condition. Numbers alone blind the user to this.
- So when presenting comparables, ALWAYS also emit clickable Avito links so Alexey can
  open photos and judge renovation himself. Build the link from the card's `uri`,
  stripping the messy `?context=...` param:
  ```python
  def avito_link(uri):
      path = re.match(r'^([^?]+)', uri or '').group(1)
      return "https://www.avito.ru" + path
  # /tula/kvartiry/2-k._kvartira_448_m_55_et._7207378935?context=... ->
  # https://www.avito.ru/tula/kvartiry/2-k._kvartira_448_m_55_et._7207378935
  ```
- The agent's own curl gets Avito's safety block (HTTP 439) on these desktop links even
  though the IP is Russian — that's fine: Alexey opens them in HIS browser (live RU IP).
  The links are valid; data collection already happens via m.avito.ru. Group the closest
  matches (same top-floor, ~same m²) as "direct analogues" with a link each.

### Pinterest as a design-reference source
- Pinterest WORKS through the agent's browser (vision can read pin photos). Useful to pull
  renovation/kitchen references (e.g. "small white kitchen + wood") for staging decisions.
- Quirk: logging into Pinterest in the USER's local browser does NOT carry over to the
  agent's separate cloud browser (different session/cookies). Don't promise the agent
  "sees" the user's logged-in boards. Basic pin search works unauthenticated — enough to
  gather references; to match the user's taste, have him send board/pin links to analyze.

- **Floor-plan reading & visual verification (pitfalls, learned on Фрунзе 17)**
- **iPhone HEIC attachments intake:** Photos sent from iOS/Telegram attachments often arrive as `.HEIC`. The vision tool (`vision_analyze`) fails on raw `.HEIC` files. Convert them to JPEG/PNG before analysis via `pillow_heif` + `PIL`:
  ```python
  from PIL import Image
  import pillow_heif
  pillow_heif.register_heif_opener()
  img = Image.open('IMG_xxxx.HEIC')
  img.convert('RGB').save('IMG_xxxx.jpg', 'JPEG', quality=85)
  ```
- **Visual inspection & budget levers on Khrushchev/Brezhnevka flips (learned on Фрунзе 17):**
  - **Dark room / Storage room layout re-engineering (Walk-in Closet):** In standard series 1-447 / Khrushchev "book" (книжка) layouts, the dark storage room (2.5–3 m²) often opens into the living room, cluttering the living area with a 2nd doorway.
    - *High-ROI Flip Solution:* Seal the doorway from the living room with acoustic drywall (GKL + mineral wool, ~3 000–4 000 ₽) to create a clean, continuous wall for a 65"+ TV/sofa zone, and cut a new entrance from the bedroom. This transforms the unit into a modern **Master Bedroom with a private Walk-in Closet (гардеробная)** — a major emotional differentiator for buyers that speeds up sale cycles.
  - **PVC window savings:** Check every room early (kitchen, living room + balcony block, bedroom). Pre-existing white PVC windows and glazed balconies in good condition save **~100 000 – 120 000 ₽** across a 2-room apartment (budget for new foam under sub-profile, PVC sills, and 10 mm sandwich-panel jambs instead of full window replacement).
  - **Sewer riser inspection (PVC vs Cast Iron):** If the vertical sewer stack is already replaced with 110 mm gray PVC/PP, avoid costly inter-floor demolition with neighbors (saves ~15 000 ₽). Re-plumb only the lower water distribution (cold/hot) with concealed PPR.
  - **Electric meter & panel upgrade without unsealing:** Check the single-phase meter label/seal (e.g. TNS Energo Tula). If intact and valid, **do NOT break the lead seal**; retain the meter in the wall niche and replace legacy carbolite switches with a modern 12–18 module flush-mounted breaker box (25/32A main, 40A/30mA RCD, B16/B10 breakers).
  - **Top-floor (5/5) ceiling inspection:** Always inspect ceiling seams and wallpaper corners for historical roof leak traces before quoting stretch ceilings. Treat suspicious areas with antifungal primer (Ceresit CT 17 / Neomid) to prevent mold blooming behind the PVC membrane.
  - **Cast-iron radiators (MC-140):** If structurally sound and non-leaking, strip, degrease, prime, and paint with heat-resistant white enamel (**~1 000 ₽**) rather than replacing with bimetal + plumbing alterations (**~8 000–10 000 ₽/radiator**), preserving margin without hurting perceived sale quality.
  - **Wooden floorboards over joists:** Check for deflection and squeaks. Tighten loose boards directly into joists with 70–90 mm yellow wood screws before 3 mm acoustic underlay and 33-class laminate instead of pouring expensive thick wet screeds.
  - **ReportLab PDF generator image optimization:** When generating multi-page expert photo audit PDFs with high-resolution iPhone photos, always downscale images to 1200px (quality 80–85) before inserting into ReportLab `RLImage`. Raw 12MP/48MP photos bloat the PDF to 40–80 MB; downscaling produces crisp, lightweight PDFs (~2–4 MB) suitable for instant delivery and messaging.

- **Image generation for staging/concept visualization (Image-to-Image strictly required):**
  - **NEVER use bare text-to-image prompts or uncurated search query links for interior concepts:** Text-to-image models hallucinate non-existent layouts, illegal open kitchens (with gas), wrong window counts, and impossible room depths that mislead the flip analysis.
  - **Always use Image-to-Image (`image_generate` with `image_url` set to the on-site photo):**
    - Input: converted JPEG of the real on-site photo (`IMG_xxxx.jpg`).
    - Prompt structure: Explicitly command the model to preserve exact perspective, wall angles, PVC window framing, radiators, and door openings from the input photo.
    - Style & Material Injection: Specify exact mass-market Scandinavian / Japandi palettes (matte 60×120 cm light beige/travertine tiles, light oak laminate, seamless flat-panel kitchen cabinets to ceiling concealing gas boiler, warm chalky greige walls, LED mirror/track lighting).
    - Destination: Save generated assets directly to `<Property>\01_Фото_и_замеры\Рендеры_концепт\`.
  - **Three-tier Presentation Standard for every room visual:**
    1. *Render artifact* (`MEDIA:...`)
    2. *Technical execution & materials* (dimensions, layout changes, plumbing/electrical details)
    3. *ROI & Sales impact* (why this specific finish raises the perceived value or speeds up sales without inflating the budget)

- **The memo is NOT the source of truth — the client's own data is.** In 2026-08 the
  Фрунзе memo claimed «санузел раздельный», but Alexey's hand-drawn sketch showed a
  COMBINED с/у (2.9 м²), and he explicitly said the memo is «корявый». Always confirm
  geometry (rooms, doors, windows, balcony) against the client's sketch/photos BEFORE
  building estimates and visualizations.
- **Hand-sketch symbol key (Alexey's rule):** rectangle with an X inside = DOOR; rectangle
  WITHOUT an X, with an arrow or «ОКНО» label = WINDOW. Vision models routinely confuse
  these — what looks like «a door from the bedroom to the balcony» on the sketch is often
  an arrow pointing at the bedroom window.
- **Vision is unreliable on faded/small blueprints — one reading is never enough.** It
  hallucinates areas (8.4 м² kitchen vs real 6.0), door counts, window counts, и балкон
  «под тремя комнатами». Working pattern: boost contrast (1.4–1.5×), upscale ×2 (LANCZOS),
  cut into overlapping 2×2/3×3 crops (±40–60 px overlap), ask ONE focused question per
  crop, then reconcile with the client's confirmations. The client's word is final.
- **Image generation (gemini-flash) defaults to «pretty» wrong geometry:** it draws
  open-plan kitchens (illegal with a gas stove!) and long balconies spanning several rooms
  even with explicit «separate enclosed kitchen» / «balcony under living room only»
  prompts. Always: (1) put the constraint in the prompt verbatim — «enclosed SEPARATE
  kitchen, own wall and door, no open plan, no bar counter», «balcony under X only, not
  under kitchen»; (2) verify EVERY render via vision BEFORE showing the client;
  (3) treat renders strictly as style sketches («как выглядит направление»), never as an
  exact blueprint; (4) state the generator's idealization (expensive tech, perfect
  furniture) explicitly.
- **For an exact copy of a plan, draw it programmatically (PIL), don't generate it.**
  Deterministic, matches the sketch 1:1. Reusable helpers (Cyrillic-aware walls/doors/
  windows, crop recipe for vision): `references/plan-redraw-pil.md`.

- **Design references and visual research standards (CRITICAL - learned on Фрунзе 17):**
  - **NEVER send bare search query links or unverified URLs:** Dropping generic Pinterest search queries (`pinterest.com/search/pins/?q=...`) or broken blog tags (e.g. 404 links on InMyRoom) is unacceptable.
  - **Always find and inspect REAL completed projects (before/after case studies):** For standard Soviet layouts (e.g. Khrushchev 1-447, 43–44 m²), extract real published designer/flipper case studies (e.g. Divan.ru wiki/blog, Salon.ru, real flipping portfolios). Download and visually verify the photos (`vision_analyze`) before presenting.
  - **Do NOT rely on AI image generation for interior design style matching:** AI generators default to generic, unstyled, yellowish or flat renders with incorrect door casings, bare ceilings, and wrong geometry. When the user asks for design direction, prioritize real curated photography of actual renovated apartments with exact material breakdowns.
  - **Deliver a concrete, actionable Style Breakdown (Kinfolk / Warm Minimal / Soft Scandi):**
    - *Walls:* Warm Greige / oat / cream tone (e.g. Tikkurila F497 / RAL 7047) + high white baseboards (80 mm) to give architectural structure without coldness.
    - *Flooring:* Natural oak laminate (33-class, micro-bevel) with zero yellow/orange undertones.
    - *Doors:* White matte panelled doors with contrasting matte black handles and hinges.
    - *Lighting & Electrical mapping:* Solve specific electrician questions using real photos — e.g. 3-gang bedside sockets at 65–70 cm with hanging ceiling pendant cylinder lamps, wall sconce over the sofa at 160 cm, and vertical tile kitchen splashbacks with sockets at 105 cm.
    - *Kitchen (6 m² with gas):* Vertical ceramic subway tile, open spice shelf on black metal brackets instead of heavy upper cabinets, compact round dining table (70–80 cm) with vintage chairs.

## Role: business partner × designer (adds a visual layer)

Beyond numbers, Alexey wants the visual/design dimension too — treat the deal as one
linked decision chain and present it that way:

```
How it looks (design)  →  Out of what + cost (procurement)  →  Pays off for sale? (margin/speed)
```

- In this role, produce actual **design-project output**: 2–3 named design directions
  (e.g. light Scandinavian, Japandi warm stone, neutral white-gray), each with palette,
  a generated visualization, tech solution (layout, where sockets, which tile) and estimate.
- Run every reference/idea through the brief's decision table:
  | Приём из референса | Что даёт визуально | Оценка стоимости | Окупаемость | Решение |
  with decision options: берём как есть / упрощённо / бюджетный аналог / не берём.
  Pinterest shows expensive effects that a cheaper analogue reproduces ~80% of the time —
  flag which ones to simplify.
- Balance it against margin: a prettier option that costs +60k and adds nothing to sale
  price gets cut or simplified; the same look for less wins. The bottom-line question is
  always the classic one (does it raise price/speed, or just the estimate?).
- The agent's own eyes come from the configured OpenRouter vision model; generation model
  draws the visualizations. See `references/openrouter-vision-generator-models.md` for
  vision-vs-generation model selection, availability checks, and config keys.

## Renovation scope decisions (from the Tula brief)

- Isolated rooms + separate bathroom = market advantage → KEEP layout, don't replan.
- If gas stove present, kitchen/room unification is legally hard → skip it.
- Small kitchens (6 m²): G/L-shaped compact, uppers to ceiling, light facades, light
  worktop, integrated fridge, good task lighting; avoid dark facades & open shelves.
- Electrics/plumbing: replace apartment-level wiring to copper + new board + RCDs;
  replace shutoff valves + distribution. Photograph cable/pipe routes before closing.
- Budget ~620–650k for 43 m² worked; reserve the top of budget for hidden defects
  (roof, balcony slab, risers, floor level). Targeting the low end + reserve is the
  disciplined play.

## Working style with Alexey

- He communicates in Russian and wants **reasoning + analysis also in Russian**, not
  just the final reply. Mental "thinking" is English by default for models — make an
  effort to keep delivered analysis/thoughts in Russian.
- He values **honest pushback**: give the flip side, point out where he may be wrong.
  He explicitly does NOT want the assistant to always agree. Present pluses AND minuses.
- Direct, friendly, on "ты". No hype, no tech-evaneglism — practicality and honesty.
- Practical: if the idea is average, say where the weakness is, in plain words.

- **Project file organization & Workspace cleanliness standards (learned on Фрунзе 17):**
  - **Clean workspace root (`D:\HERMES FILES\`):** Keep the root clean. Never dump raw converted photos, ad-hoc python scripts, or temporary `.xlsx`/`.pdf` files directly in root. All generated assets must be placed immediately in their target project directory (e.g. `01_Недвижимость\Фрунзе_17\01_Фото_и_замеры\`, `02_Документы_и_PDF\`, `03_Скрипты_генерации\`).
  - **Two-tier Contact Management in Obsidian:**
    1. *City-wide contractor database:* Store cross-project vendors (e.g. city-wide debris hauling container services, wholesale suppliers) in `Недвижимость\Контакты_и_Подрядчики.md` so the database grows across flips.
    2. *Property-specific ties:* Link local utilities and building-tied staff (e.g. HOA plumber, building manager) directly in the property card `Недвижимость\<Объект>\<Объект>.md`.
  - **Alexey's workflow preferences & pacing:**
    - **Do NOT rush visual concepts/Pinterest references prematurely:** When starting demolition/rough works, Alexey focuses on actual build execution, debris removal, structural facts, and budgeting. Only generate/fetch design references and visual moodboards when reaching the finish & styling phase in the schedule.
    - **Obsidian Vault maintenance:** Regularly clean obsolete intermediate files (plan crops, outdated renders, duplicate root PDFs) and keep only validated documents, photos, and live financial spreadsheets (`.xlsx`).
- **Financial tracking & Expense benchmarking (Google Sheets + Excel):**
  - Maintain a clean 3-layer budget table (`.xlsx` in `Смета_и_чеки/` + synced live to Google Sheets via `productivity:google-workspace`):
    1. *Executive Dashboard / Unit Economics:* Purchase price, rough initial costs (digital signature, state duty, emergency lock opening), target renovation budget, target sale price, net investor profit & ROI.
    2. *Expense Ledger (Fact):* Date, category, item name, market price, actual paid amount, absolute & percentage savings vs market.
    3. *Stage-by-Stage Estimate (Plan vs Market):* Clear breakdown across 10–12 renovation milestones showing regional market benchmark vs target cost and the specific leverage used to beat market rates (e.g. self-managed labor, ceiling-routed electrics, avoiding wet screeds).
  - **CRITICAL Formula Pitfall in Google Sheets (Russian `ru_RU` locale):** In Russian locale sheets, comma `,` is the decimal separator, so function argument separation MUST use semicolon `;` or wrapped `IFERROR(...)` — e.g. `=IFERROR(G5/E5; 0)`. Using standard comma formulas like `=IF(E5>0, G5/E5, 0)` causes a fatal formula parse error (`#ERROR!`). Always sanitize division and use `;` in formulas when writing programmatically to user sheets.
  - **Daily expense-add workflow:** Every time Alexey reports new costs, follow the procedure in `references/expense-add-workflow.md` — covers all 3 Excel copies, Google Sheets (with `;` pitfall), and Obsidian markdown sync.

- Alexey's vault: `D:\HERMES FILES\HERMES OBSIDIAN`.
- **Standardized weekly sprint structure for each flip property:**
  Each flip folder `Недвижимость\<Объект>\` (e.g. `Недвижимость\Фрунзе 17\`) uses a fixed phase breakdown:
  - `PDF_Отчеты_и_документы/` — **единый реестр всех сформированных PDF-отчетов**, технических заданий для мастеров и экспертных заключений (с навигационной заметкой `PDF_Отчеты.md`). Все генерируемые по просьбе пользователя PDF автоматически копируются и линкуются сюда.
  - `00_Подготовка_и_замеры/` — первичные чек-листы, замеры, контакты поставщиков, анализ дверей/материалов
  - `01_Неделя_1_Демонтаж_и_база/` — вывоз мусора, демонтаж, монтаж входной двери, завоз черновых (PPR, кабель, смеси)
  - `02_Неделя_2_Инженерия_и_кухня/` — разводка электрики/сантехники, стяжка/самонивелир, **критический путь: замер и заказ кухни (10–14 дней)**
  - `03_Неделя_3_Санузел_и_стены/` — гидроизоляция, плитка, шпаклевка/покраска, натяжные потолки
  - `04_Неделя_4_Финиш_и_сборка/` — укладка ламината единым контуром, межкомнатные двери, сборка кухни, санфаянс
  - `05_Стейджинг_и_продажа/` — клининг, декор, проф. фото, текст листинга под верхнюю планку цены
  - `Смета_и_чеки/` — фиксация чеков и факта расходов по этапам
  - Дополнительно: `Планировка/`, `Фото/Объект_первичный_осмотр/`, `Аналитика_аналоги/`
- Master templates are stored in root Obsidian: `Флиппинг_Базовый_Шаблон_Дорожная_Карта.md`.
- When generating printable materials or checklists for Alexey (e.g. on-site inspection, door catalogue comparisons), compile them as stand-alone styled PDFs via ReportLab with Russian Cyrillic font support (`Arial`/`Arial-Bold`) and place copies in both the workspace root and the property's `00_Подготовка_и_замеры/` folder.

## Field inspection tools: Offline Interactive Web Checklists (Learned pattern)

- **Do NOT rely solely on static PDFs or real-time chat/Telegram on-site:** cell service can drop in basements/interiors, and Telegram API may be blocked without an active VPN.
- **Preferred on-site tool:** Create a single-file, 100% offline **interactive HTML web-checklist** (`<filename>_интерактив.html`):
  - Mobile-first responsive CSS with large tap targets and numeric inputs.
  - State preservation via `localStorage` on every input change so form data never resets when the phone screen turns off or browser tabs switch.
  - **CRITICAL UI Pitfall (Mobile Touch / Radio buttons):** Do NOT use custom JS-only `<div>` toggle groups for critical selection fields (e.g. left/right door swing, concrete vs wood subfloor). Touch events on mobile browsers (Safari/Chrome) can fail to update visual CSS classes reliably. Always use **native hidden radio inputs (`<input type="radio">` with styled `<label>`)** to guarantee 100% reliable native state changes.
  - **CRITICAL UI Pitfall (Clipboard on mobile `file://` origins):** Modern mobile browsers (iOS Safari, Android Chrome, Telegram WebView) block `navigator.clipboard.writeText()` when running from a local `file://` protocol without HTTPS. Always implement a 3-layer bulletproof fallback:
    1. Synchronous `execCommand('copy')` on a focused textarea in the click event.
    2. Async `navigator.clipboard.writeText()` fallback.
    3. **Live visible `<textarea>` summary box** rendered directly on the page that updates in real-time as inputs change + auto-selects on tap/click so the user can always copy manually even if all clipboard APIs are blocked by browser sandboxing.
  - **One-click clipboard export:** Include a prominent floating bottom action button (`📋 Скопировать отчет для Hermes`) that formats all entered survey values into a structured text summary.
  - Store the generated HTML checklist in both the workspace root and the property's `00_Подготовка_и_замеры/` directory.
- **Strict Quality Control & Self-Verification rule:** Never hand over an interactive checklist, calculation, or script without **opening and clicking through all interactive elements in a real headless browser session** (`browser_navigate` + `browser_click` + `browser_console`) to verify that state toggles, values persist in `localStorage`, and clipboard generation succeeds.

## Local procurement & vendor analysis (Tula specifics)

- Do NOT default only to generic federal chains (Leroy Merlin / OBI). Local players in Tula often offer better stock availability and wholesale pricing:
  - **ТК «Чипак» (ул. Мосина / Чмутова)** — top local hub for doors, rough plumbing, electrical and building materials. Wholesale-level pricing, massive warehouse in stock (5 min from Sovetsky district), fast delivery/installation.
  - **ОБИ (ТЦ «Макси»)** — good for in-person visual inspection of door samples, locks, fit and finish.
  - **Лемана ПРО (Леруа Мерлен)** — baseline backup for standard door block sizes (860/960 mm) and finish materials.
  - **Дилерские склады (ул. Мосина / Коминтерна)** — «Фабрика Дверей», «Двери Гуд»: look for warehouse leftovers / showroom floor samples with 20–25% discount.
- **Entry door selection rule:** 1.2–1.5 mm steel, 2 locks (cylinder + lever) + night latch, 2–3 seal contours, light MDF interior panel matching future interior doors. Budget: 16–22k RUB door + ~4k RUB installation.
- **Critical protection rule:** Install entry door in Days 1–2 right after heavy debris removal, and **immediately wrap door leaf and frame in heavy stretch film/cardboard** until Day 28 (finish phase) to prevent damage from dust and debris.

## Cyrillic file pitfalls (this Windows workspace)

- `search_files` with a Cyrillic filename glob (e.g. `*мемо*`, `*Фрунзе*`) can return
  0 hits even when the file exists. Working fallback: `find . -iname "*..."` in terminal.
- `read_file` may misdetect a valid UTF-8 Cyrillic .md as "Binary file". Verify with
  `file <name>` (it will say UTF-8) and read via terminal `cat`. Don't trust `iconv`
  guesses (UTF-16LE/CP1251) before checking `xxd` — they produced garbage on a plain
  UTF-8 file.

## Project references

- `references/market-scouting-and-pipeline-architecture.md` — architectural standard for secondary-market scouting, Kanban pipelines, the `realty-scout` profile, and the single-thread pilot rule (no parallel purchases until the current flip finishes).
- `references/model-cascade-vision-funnel.md` — **cost-aware multi-model «воронка зрения»**: MiniMax Free (бесплатный глубокий парсинг/ресёрч) → DeepSeek Vision (дешёвый черновой OCR/отбор фото) → Gemini 3.7 Flash (экспертный финал/смета). Применяется во ВСЕХ чатах: массовый парсинг и длинные документы — на дешёвых моделях, финальный дизайн/дефектовка/смета — строго на Gemini 3.7 (его не режем через reasoning_effort).
- `references/openrouter-vision-generator-models.md` — vision vs image-generation model
  selection on OpenRouter, model-availability checks, and the Hermes config keys that run
  the agent's eyes + visualizations. (Vision = image→text for "seeing" plans/photos; a
  model page existing does NOT mean it's in the API catalog — verify with `/models/{id}`.)
- `references/style-warm-scandi-kinfolk.md` — master visual & design standard for 43–44 m²
  Khrushchev/Brezhnevka flips: exact color codes, real-life proven finishes, and room-by-room
  electrical and layout specifications.
- `references/tula-frunze-17.md` — current live flip: 43.2 m², 2-room, 5/5, 1966 brick,
  u. Frunze 17, Sovetsky r-n, Tula. **Confirmed 2026-08: purchase 3.9M** (user corrected the
  4.0M in the brief), renovation 650k, target sale 5.6M. Live comparables (702 secondary
  listings, 33 Sovetsky analogues) put the target at the TOP of a 5.3–5.6M corridor; net
  ~721k at 5.6M (ROI 15.8%/cycle). Same Frunze-17 object listed on Avito at 3.9M → bought
  AT market, not below. Full matrix + sources: `references/tula-frunze-17.md`.
# Style-Reference PDF & Expense-Ledger lessons (Фрунзе 17, 2026-08)

Session-hardened rules learned when generating «красивый PDF» deliverables for Alexey.

## 1. Style reference PDF = PURE visuals, zero layout/re-planning (user rule)

- Alexey orders «красивый PDF референса будущего ремонта» as a **visual moodboard**:
  palette, materials, furniture, lighting, real case photos.
- **Do NOT embed floor-plan changes inside the style PDF** (walk-in closet doorway
  relocation, wall sealing, ТВ-wall from re-planning, «мастер-спальня» narrative).
  He rejected the first version outright: «Не нравится планировка в пдф, она изменена,
  убери её». Layout/perestroika schemes belong ONLY in a separate ТЗ/обоснование
  document (e.g. «Обоснование_Перепланировка_Гардеробной_Фрунзе17.pdf»).
- **Cover EVERY room up front**: зал, спальня, кухня, прихожая AND the совмещённый
  санузел (2.9 м²). A missing room (санузел was missed once) is called out immediately
  and forces a rebuild. Build pages for all rooms in the first pass.
- Keep electrical height notes (бра 160 cm, ТВ 110 cm, розетки 30/65–70 cm, фартук
  105 cm) as generic styling guidance — they were accepted in the style PDF.

## 2. Delivering PDFs in Hermes Windows desktop (paths with spaces)

- Bare `MEDIA:D:\HERMES FILES\...` (unquoted, spaces) breaks: the desktop media parser
  truncates at the first space (tries to open `D:\HERMES`) → error popup / dead link.
- Working delivery pattern (used on Фрунзе 17):
  1. Save canonical PDF in Obsidian `PDF_Отчеты_и_документы/`.
  2. Mirror a shortname copy to the fixed no-space dir `D:\HERMES_REPORTS\ShortName.pdf`.
  3. Open it for the user directly: `cmd.exe /c start "" "D:\HERMES_REPORTS\ShortName.pdf"`.
  4. Deliver the chat link as quoted `MEDIA:"D:\HERMES_REPORTS\ShortName.pdf"`.
- Never rely on an unquoted MEDIA path containing spaces.

## 3. Expense-ledger row insertion shifts totals (Excel + Google Sheets)

- The «Факт расходов» ledger has formulas + cross-sheet refs. Inserting a new row
  (e.g. row 11 for бригада 16 000 ₽) shifts the ИТОГО row — update ALL of these in the
  SAME script pass, or the dashboard silently breaks:
  - Local `.xlsx`: `=SUM(E5:E10)` → `=SUM(E5:E11)` (marks: E/F/G), ИТОГО pct row ref,
    and the summary sheet link `='Факт расходов'!F8` → new total row (F12).
  - Google Sheets mirror: same ranges AND the dashboard cells (`C14`/`C12` on
    «Экономика и Сводка») pointing at the old total row.
- Pattern: read ledger → insert row → rewrite formulas + cross-refs → then update the
  Obsidian `Смета_и_факт_расходов.md` журнал table in the same turn.
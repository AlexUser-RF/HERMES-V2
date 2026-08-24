# Adding Daily Expenses to the Flipping Tracker

Recurring operation — Alexey reports daily costs, this must be captured in all 3 systems.

## The 3 copies to sync

| Copy | Path |
|---|---|
| Obsidian-vault Excel | `D:\HERMES FILES\HERMES OBSIDIAN\Недвижимость\<Объект>\Смета_и_чеки\Фрунзе17_Бюджет_и_Факт_расходов.xlsx` |
| Project-folder Excel | `D:\HERMES FILES\01_Недвижимость\<Объект>\02_Документы_и_PDF\Фрунзе17_Бюджет_и_Факт_расходов.xlsx` |
| Root copy | `D:\HERMES FILES\Фрунзе17_Бюджет_и_Факт_расходов.xlsx` |
| Google Sheets | `1Vb7Dwq5rQOxOqkXz4mztu4jChDiOrNpXuCR5I2Lva6E` (sheet `'Факт расходов'`) |
| Obsidian markdown | `D:\HERMES FILES\HERMES OBSIDIAN\Недвижимость\<Объект>\Смета_и_чеки\Смета_и_факт_расходов.md` |

## Step-by-step procedure

### 1. Read current state

Open the workbook, inspect the `Факт расходов` sheet:
- Current data rows (typically 5–N, header in row 4, total at row N+1)
- Next free row number = highest data row + 1
- Current total row's SUM range (e.g. `=SUM(E5:E14)`)
- Summary sheet link (`='Факт расходов'!F15` → update to F{new_total_row})

### 2. Python approach (openpyxl)

The `xlsx` skill's scripts work but for adding rows it's simpler to write inline:

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# Style helpers (reuse these exact objects):
font_regular = Font(name="Segoe UI", size=9, color="1E293B")
font_bold = Font(name="Segoe UI", size=9, bold=True, color="0F172A")
fill_subtotal = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
thin_border = Border(left=Side(style='thin', color='CBD5E1'), right=Side(style='thin', color='CBD5E1'), top=Side(style='thin', color='CBD5E1'), bottom=Side(style='thin', color='CBD5E1'))
top_thin_bottom_double = Border(top=Side(style='thin', color='CBD5E1'), bottom=Side(style='double', color='0F172A'))
align_center = Alignment(horizontal='center', vertical='center')
align_left = Alignment(horizontal='left', vertical='center')
align_right = Alignment(horizontal='right', vertical='center')

# Column layout:
# 1=№, 2=Дата, 3=Категория, 4=Наименование, 5=Рынок(₽), 6=Факт(₽),
# 7=Экономия(₽), 8=% Экономии, 9=Исполнитель, 10=Примечание
```

### 3. Formula conventions (always use these)

| Column | Label | Formula/Value |
|---|---|---|
| E | Рыночная цена (₽) | Hard-coded number (can be same as fact) |
| F | Факт оплачено (₽) | Hard-coded number |
| G | Экономия (₽) | `=E{row}-F{row}` |
| H | % Экономии | `=IFERROR(G{row}/E{row}, 0)` |
| Total row E | | `=SUM(E{first_data_row}:E{last_data_row})` |
| Total row F | | `=SUM(F{first_data_row}:F{last_data_row})` |
| Total row G | | `=SUM(G{first_data_row}:G{last_data_row})` |
| Total row H | | `=IFERROR(G{total_row}/E{total_row}, 0)` |

Number format for E/F/G columns: `'#,##0 "₽"'`
Number format for H column: `'0.0%'`

### 4. After adding rows: update the summary sheet link

The `Экономика и Сводка` sheet has `C12` (or `C14` depending on version) pointing to the total cell:

```python
ws_summary = wb["Экономика и Сводка"]
ws_summary["C12"] = "='Факт расходов'!F{new_total_row}"
```

### 5. Google Sheets sync — RUSSIAN LOCALE PITFALL

Google Sheets created under Russian locale (`ru_RU`) uses `;` as formula argument separator, NOT `,`.

**WRONG:** `=IFERROR(G5/E5, 0)` → `#ERROR!`
**RIGHT:** `=IFERROR(G5/E5; 0)`

When building the values array for the Google Sheets API, use `;` in every formula string that takes multiple arguments. Division `/` and range `:` operators are fine — only argument separation changes.

The Google Sheets API call pattern:
```python
sheets_service.spreadsheets().values().update(
    spreadsheetId=spreadsheet_id,
    range="'Факт расходов'!A1:J{last_row}",
    valueInputOption='USER_ENTERED',
    body={'values': fact_values}
).execute()
```
Use a retry loop (3 attempts with 2s backoff) since Google Sheets occasionally returns 503.

### 6. Obsidian markdown

Edit the table in `Смета_и_факт_расходов.md`. The table format:

```markdown
| N | Дата | Категория | Наименование | Рынок (₽) | **Факт (₽)** | Экономия (₽) | % | Поставщик |
```

Update the Σ (total) line: recalculate `ИТОГО ОПЛАЧЕНО` and `% Экономии` for the markdown (these are static numbers, not formulas).

### 7. Pitfalls checklist

- [ ] SUM range extends to the correct last data row (not the old total row)
- [ ] Total row `IFERROR(G{total}/E{total}, 0)` uses the total row number, not a data row
- [ ] Google Sheets formulas use `;` not `,` as argument separator
- [ ] Summary sheet link updated to point to new total row
- [ ] All 3 Excel file copies updated (Obsidian, project folder, root)
- [ ] Google Sheets values range covers all new rows (A1:J{last_row})
- [ ] Obsidian markdown total numbers recalculated to match Excel
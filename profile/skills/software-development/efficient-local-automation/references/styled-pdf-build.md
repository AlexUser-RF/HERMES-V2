# Styled PDF deliverables — fast path (reportlab)

Scope: producing a *designed* document — multi-page guide, report, proposal, checklist, handout — as a PDF the user will actually look at. For generic PDF plumbing (spec-based creation, merge/split, AcroForm, OCR, text/table extraction) use the bundled `pdf` skill (`productivity/pdf`); this file is the interpreter, styling, and verification path.

## Interpreter: do not assume `python` on PATH

The libraries live in the Hermes venv, not necessarily in whatever `python` resolves to:

```
C:/Users/Administrator/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe
```

- Run the build with that interpreter by absolute path.
- Confirm what is installed with `"<venv-python>" -m pip list | grep -iE "reportlab|pypdf"` — this is a normal command, not an inline eval flag.
- Install only what is genuinely absent: `"<venv-python>" -m pip install pypdf pypdfium2` (`pypdf` = text verification, `pypdfium2` = preview PNGs).
- Never run `python -c` (or any inline `-c`/`-e` flag) to probe: the terminal policy treats those as unreviewed script execution and the turn can stall waiting for approval. Write the probe into the build script, or run the whole build script file.

## Cyrillic fonts

`C:\Windows\Fonts` ships Arial, Tahoma, Verdana, Consolas — all with Cyrillic coverage. Register the TTFs and declare a family so inline `<b>` in `Paragraph` markup resolves:

```python
pdfmetrics.registerFont(TTFont("Ar",  r"C:\Windows\Fonts\arial.ttf"))
pdfmetrics.registerFont(TTFont("ArB", r"C:\Windows\Fonts\arialbd.ttf"))
pdfmetrics.registerFont(TTFont("Mo",  r"C:\Windows\Fonts\consola.ttf"))
pdfmetrics.registerFont(TTFont("MoB", r"C:\Windows\Fonts\consolab.ttf"))
pdfmetrics.registerFontFamily("Ar", normal="Ar", bold="ArB", italic="Ar", boldItalic="ArB")
```

Monospace for code blocks/paths is what makes a technical guide legible; do not render commands in a proportional font.

## Layout shape that reads well

`BaseDocTemplate` with two page templates:

1. `cover` — an `onPage` callback paints a dark hero block and accent bar with plain canvas calls (no flowables needed), then `NextPageTemplate("main") + PageBreak()`.
2. `main` — `onPage` draws the header rule, running title, and `стр. N` footer.

Flowables that carry the design:

- `Paragraph` with inline `<font color=...>` / `<font name="Mo">` markup for accents and inline code.
- `Table` as the universal card: code blocks (dark background + `LINEBEFORE` accent bar), callout notes (tinted background + `LINEBEFORE` in the semantic colour: green = tip, amber = warning, indigo = info), key/value sheets, troubleshooting grids (`ROWBACKGROUNDS` + `repeatRows=1`).
- `Spacer` between blocks for rhythm; a dense wall of paragraphs is what makes a generated doc look machine-made.
- Numbered step headers as a 2-column `Table` (coloured number cell + title) beat a plain bold line.

Build the whole document from a single script written to scratch, and re-run the script after each edit — iterate on the `.py`, never by hand-patching the produced PDF.

## Pitfall: ParagraphStyle kwarg collision

A style factory that fixes `alignment=` / `textColor=` and then forwards `**kw` raises:

```
TypeError: ParagraphStyle() got multiple values for keyword argument 'alignment'
```

Give the custom parameters distinct names and forward them into the real kwargs (e.g. `def S(..., align=TA_LEFT, color=INK, **kw)` → `ParagraphStyle(..., textColor=color, alignment=align, **kw)`). Any caller that passes `textColor=` instead of `color=` reproduces the same crash.

## Verification without a vision pass

Verify mechanically, per page, and say which method you ran:

```python
import pypdf
r = pypdf.PdfReader(path)
for i, p in enumerate(r.pages, 1):
    t = p.extract_text() or ""
    lines = [l for l in t.split("\n") if l.strip()]
    print(i, len(lines), len(t), lines[0][:60] if lines else "(EMPTY)")
```

Assert: expected page count, and every page has content (an `(EMPTY)` page means a flowable was pushed off-canvas). For a visual sanity check, render with `pypdfium2` (`PdfDocument(path)[i].render(scale=2.0).to_pil().save(...)`).

If the image analyzer is unavailable in the turn, report the mechanical result and state plainly that the visual check did not run — do not imply the layout was seen.

## Delivery

- Write the artifact into its project folder; keep `D:\HERMES FILES` root clean.
- Cheap insurance for delivery: also write a short-named copy (no spaces) such as `D:\HERMES_REPORTS\<Name>.pdf`, and hand the user the path.
- Do the copy in its own command — never bundled with `rm -rf` or `cmd //c start`, which block the whole line and lose the copy.

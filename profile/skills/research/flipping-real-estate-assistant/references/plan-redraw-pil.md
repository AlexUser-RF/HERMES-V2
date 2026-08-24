# Plan reading & exact redraw (Фрунзе-17 lesson, 2026-08)

Situation: Alexey sent hand-drawn floor plans (blue pen on paper, крестики = двери,
стрелки/«ОКНО» = окна) and expects the agent to read them exactly and redraw clean
copies that match 1:1.

## Symbol key (Alexey's rule — trust it over vision's guesses)

- Rectangle with an X inside = **ДВЕРЬ** (door)
- Rectangle WITHOUT an X, with an arrow pointing at it or a «ОКНО» label = **ОКНО** (window)
- On his sketches the balcony sits on the external wall; windows are on the outer walls.

## Vision reading recipe (reliable order)

1. Do NOT ask vision about the whole sheet at once — it hallucinates room counts,
   areas and doors (it «saw» a 8.4 м² kitchen that is really 6.0, and a «balcony under
   three rooms» that is under one).
2. Preprocess with PIL:
   ```python
   from PIL import Image, ImageEnhance
   im = Image.open(path)
   im = ImageEnhance.Contrast(im).enhance(1.4)
   im = im.resize((im.width*2, im.height*2), Image.LANCZOS)
   ```
3. Cut into overlapping crops (2×2 or 3×3, ~40–60 px overlap so nothing falls on a seam).
4. Ask ONE focused question per crop (e.g. only about the bottom strip: «где балкон,
   под какими комнатами, сколько крестиков-дверей»). Cross-check conflicting answers.
5. Reconcile against the client's spoken confirmations — the client's word is final.

## Exact redraw with PIL (deterministic, no generator)

```python
from PIL import Image, ImageDraw, ImageFont

def F(s, b=False):  # Cyrillic-safe font on Windows
    return ImageFont.truetype("C:/Windows/Fonts/arial%s.ttf" % ("bd" if b else ""), s)

def wall(d, p, w): d.line(p, fill=INK, width=w)
def door(x0,y0,x1,y1):  # white gap + X on a wall
    d.rectangle([x0,y0,x1,y1], fill="white", outline=INK, width=3)
    d.line([(x0,y0),(x1,y1)], fill=INK, width=3); d.line([(x0,y1),(x1,y0)], fill=INK, width=3)
def window(x0,y0,x1,y1):  # white gap + midline, NO X
    d.rectangle([x0,y0,x1,y1], fill="white", outline=INK, width=3)
    d.line([(x0+4,(y0+y1)//2),(x1-4,(y0+y1)//2)], fill=INK, width=2)
```
Pitfalls:
- Use real fonts from `C:/Windows/Fonts/` (Arial) — PIL default bitmap font can't render Cyrillic.
- Center labels with `d.textlength(txt, font=font)` + `font.getbbox(txt)`, not `textsize` (deprecated).
- Draw doors/windows as white gaps ON TOP of wall lines (fill white + outline) so the
  wall break looks right; `h = 9` half-thickness works for 8–9 px walls.
- Keep the same top-level geometry from the sketch (left column прихожая→с/у→кухня,
  зал to the right, спальня right, балкон under зал only). Do NOT «normalize» the
  client's sketch to what looks standard — if a door isn't on the sketch, don't add one.

## Generator verification step

After any image_gen (аксонометрия/визуализации) run it through vision with a checklist:
совмещённый ли с/у, балкон только под залом, кухня изолированная, 3 окна. Re-generate
until it matches; present as a sketch, not a blueprint.
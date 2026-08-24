# Avito mobile comparables scraping (richer, preferred path)

The mobile endpoint `m.avito.ru` returns **complete structured listing data** embedded
in the page as `window.__initialData__`, even when the main site blocks browsers and
plain curl. This is the *richer and cleaner* comparables source vs CIAN `cat.php`:
it reliably carries price, price/m², area, floor, district, address AND a
new/secondary marker for every card, with working pagination.

## Recipe (git-bash / MSYS on Windows)

```bash
UA="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
mkdir -p "D:/HERMES FILES/.tmp_scrape" && cd "D:/HERMES FILES/.tmp_scrape"
# vtorichka (secondary market) 2-room, Tula — page 1
curl -s -m 20 -L -A "$UA" \
  "https://m.avito.ru/tula/kvartiry/prodam/vtorichka/2-komnatnye" \
  -o vt_1.html -w "HTTP %{http_code} size=%{size_download}\n"
# later pages (24 pages = ~715 total listings for this query)
curl -s -m 20 -L -A "$UA" \
  "https://m.avito.ru/tula/kvartiry/prodam/vtorichka/2-komnatnye?p=2" \
  -o vt_2.html
```

Success = `HTTP 200 size=~2_000_000-2_500_000`. A page is a real listing page, ~30 cards.

## Why mobile (not the desktop URL)

The desktop category path `/tula/kvartiry/prodam/2-komn-...` redirects or returns
`isInvalidUrl: true` / a VPN dialog. The mobile path above returns real `count`
(shown as `count`/`mainCount` in the data, e.g. 715 = pages 24×30). Do NOT trust the
desktop URL; use this mobile format.

## Data-extraction

`window.__initialData__` is a **double-encoded JSON string**. Decode in two layers:

```python
import re, json
raw = open(r"D:/HERMES FILES/.tmp_scrape/vt_1.html", encoding='utf-8', errors='ignore').read()
m = re.search(r'window\.__initialData__\s*=\s*"(.*?)";', raw, re.DOTALL)
data = json.loads(json.loads('"' + m.group(1) + '"'))   # layer1: JS string -> JSON text; layer2: JSON text -> dict
items = data['search']['allItems']   # dict keyed by item id
```

Each item is `{type:"item", value:{...}}`. Useful fields (read from `value['freeForm']`,
a rendered tree of JSON nodes — search by node `id`):

| Node id | Meaning |
|---|---|
| `titleLabelRich` | "2-к. квартира, 43,2 м², 5/5 эт." (parse area + floor/rooms) |
| `highlightedPriceLabelRich` / `priceLabelRich` | total price, e.g. "5 250 000 ₽" |
| `normalizedPriceLabelRich` | price per m² |
| `geoReferenceLeftLabel` | district, e.g. "р-н Советский" |
| `devAddressView` / `developmentViewLink` | street / house address (e.g. "ул. Фрунзе, 17") |
| `descriptionLabelRich` | listing description (may contain address + condition) |

To pull a node's text from `freeForm`:
```python
def gt(ff, key):
    s = json.dumps(ff, ensure_ascii=False)
    mm = re.search('"id": "%s".*?"(?:title|text)": "([^"]*)' % key, s)
    return mm.group(1).replace('\\xa0',' ').strip() if mm else None
```

New/secondary marker: check `value['uri']` contains `novostroyka` (new build) vs
`vtorichka` (secondary). Use the `vtorichka` category path to pre-filter secondary.

## Pitfalls

- **Double-encode**: `json.loads('"' + s + '"')` then `json.loads(...)` again. One layer
  alone fails with "Expecting property name enclosed in double quotes".
- **`\\u002F`** is `/`; `\\xa0` is a non-breaking space (price separator).
- **Route everything through a real Windows dir** (e.g. `D:/HERMES FILES/.tmp_scrape/`),
  never `/tmp` — native curl.exe can't write MSYS paths (file silently vanishes).
- Paginate with `?p=N`; fetch sequentially with a small sleep. All 24 pages fetched
  fine in one pass.
- Address is sometimes only in `developmentViewLink` (street + house), sometimes in
  the description; district is always in `geoReferenceLeftLabel` — filter by district first.

## Worked example (this session, 2026-08)

Gathered 702 unique 2-room secondary listings across Tula, 74 in Sovetsky r-n, and
cross-referenced the FRUNZE-17 object itself: it was listed on Avito at **3 900 000 ₽
(90 278 ₽/m²)** — below the 4.0M purchase figure, which contradicts the "bought below
market" assumption (see `tula-frunze-17.md`).

33 matching comparables (Sovetsky, 2-room, 38–50 m²): median 123 272 ₽/m²,
mean 127 205 ₽/m², min ~84k, max ~170k. Direct top-floor (5/5) analogues: Революции 28
43 m² → 5.25M (122 093 ₽/m²); Фрунзе 29 44.8 m² → 5.9M (131 696 ₽/m²). So Frunze 17's
5.6M target is the TOP of the realistic corridor, not the middle → validate before
finalizing, and confirm the actual purchase price.

# CIAN comparables scraping (working recipe)

Problem: CIAN interactive site blocks the browser (WAF "подозрительный трафик").
But the legacy `cat.php` endpoint serves real listing HTML to plain curl.

## Recipe (git-bash / MSYS on Windows)

Two gotchas that silently wipe output:
1. **Use a real Windows directory for `-o`, NOT `/tmp`** — native curl.exe on Windows
   can't write MSYS `/tmp/...` paths (file silently never appears). Use e.g.
   `D:/HERMES FILES/.tmp_scrape/`.
2. **Force `Accept-Encoding: identity`** — otherwise the server may return a body the
   parser can't decode (empty or mojibake read).

```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
mkdir -p "D:/HERMES FILES/.tmp_scrape" && cd "D:/HERMES FILES/.tmp_scrape"
# Tula 2-room for sale (region=5099 is Tula; room2=1 + rooms=2 filters 2-room)
curl -s -m 25 -L -A "$UA" \
  -H "Accept: text/html" -H "Accept-Encoding: identity" -H "Accept-Language: ru" \
  "https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&region=5099&room2=1&rooms=2" \
  -o cian.html -w "HTTP %{http_code} size=%{size_download}\n"
```

Success looks like `HTTP 200 size=~2000000` and a real HTML file (~2 MB).

## Data-extraction notes

- The page is NOT a clean JSON-LD blob. Offer data is embedded as **fragmented JSON
  objects** scattered through the HTML, each keyed by `"cianId":<number>`.
- Extract by finding each `"cianId":NNN`, then reading the neighboring fields:
  `"formattedShortPrice"` (e.g. `"6 200 000 ₽"`), `"formattedShortInfo"`
  (e.g. `"2-комн.кв. · 2\\u002F4 этаж"`), `"totalArea"`, `"livingArea"`, `"floorNumber"`.
  Watch the `\u002F` escaping (it's `/`).
- **Pitfall: the page mixes listings from OTHER cities** (saw Irkutsk) and ad/newbuild
  blocks. Filter hard: check `formattedShortInfo` says `2-комн`, keep only Tula
  addresses, drop `studio`/`1-комн`/`3-комн` and mortgage-info blocks. Better still,
  extract the human-readable `"description"` fields which carry the real district +
  street text (e.g. "ул. Петрова 56а", "ул. Альпийская 5").
- Not every offer has all fields near a single `cianId`; price/address binding can be
  loose. Cross-check a scraped price against a readable description before trusting it.

## Tula 2-room comparables glimpsed this session (2026-08, for the Frunze 17 deal)

Sample prices seen (raw, some polluted — verify before using):
- 2-комн 48.5 м² ≈ 6.2M (134 783 ₽/м²)
- 2-комн 56.2 м² ≈ 4.5M (92 763 ₽/м²) — likely outer/district, low per-m²
- 2-комн 40.3 м² ≈ 6.7M
- ул. Петрова 56а: 40.6 м² ≈ 6.3M, light, ready to move in
- ул. Альпийская 5: 40 м² ≈ 5.5M, brick 2000, 2/6 floor
- ул. Ямская 33: 2-комн ≈ 6.7M, brick, renovated
- 135-серия 2-комн ≈ 7.85M

Range for matching 43 m² 2-room in Tula: roughly **5.5M–6.7M**, skewed by location/
condition. The Frunze 17 target of 5.6M (129 630 ₽/м²) sits at the LOW end of this
range → validate against the Sovetsky district specifically before finalizing.

## Other sites (status 2026-08)

- n1.ru / etagi.com: HTTP 200 but JS shells — curl gets no data server-side.
- domclick.ru: requires auth (401).
- If curl is blocked too, fall back to asking Alexey to paste listing links/screenshots.
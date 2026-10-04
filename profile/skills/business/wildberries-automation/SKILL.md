---
name: wildberries-automation
description: "Use for Wildberries: Seller API, FBS, prices, and trends."
version: 0.2.0
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [E-commerce, Wildberries, Marketplace, API, FBS, Scraping]
---

# Wildberries Automation

Guidance for automating operations, analytics, competitor monitoring, and order management on Wildberries (WB).

## Two Operating Circuits

### 1. Seller API (Private Account Management)
Requires a seller API key (JWT token) configured in `.env` (`WB_API_KEY`).

- **Base Endpoints**:
  - Cards & Content: `POST https://content-api.wildberries.ru/content/v2/get/cards/list`
  - Warehouses: `GET https://marketplace-api.wildberries.ru/api/v3/warehouses`
  - New FBS Orders: `GET https://marketplace-api.wildberries.ru/api/v3/orders/new`
  - Sales & Financials: `GET https://statistics-api.wildberries.ru/api/v1/supplier/sales?dateFrom=YYYY-MM-DD`
  - Analytics & Search Queries: `https://analytics-api.wildberries.ru/api/v1/search_queries`
- **Authentication**: `Authorization: <WB_API_KEY>` header.
- **Reliability**: Fully accessible via standard HTTP (`urllib`, `requests`, `httpx`). Note: the content-api cards list can return 403 depending on token scope — if it does, do not retry with payload variations; use the public CDN route below instead.

### 2. Public / Market Monitoring (Competitors, Trends & Product Cards)
Public endpoints do NOT accept seller tokens; the HTML storefront and `card.wb.ru` are behind a strict WAF (server-side `curl`/`urllib` get 403). Do not fight the WAF — pivot to the CDN.

- **Product card data via CDN basket routing (fastest, no browser needed):**
  - Compute: `vol = nm_id // 100000`, `part = nm_id // 1000`
  - Card JSON: `https://basket-{XX}.wbbasket.ru/vol{vol}/part{part}/{nm_id}/info/ru/card.json` → real seller fields: `imt_name`, `subj_name`, `description`, `brand`
  - Images: `https://basket-{XX}.wbbasket.ru/vol{vol}/part{part}/{nm_id}/images/big/{N}.webp`
  - Seller info: `.../info/sellers.json`
  - The basket number is NOT derivable from nm_id — probe sequentially. Start near `vol // 100 + 1`, sweep `01`–`60` with a short per-request timeout (~1.2s) and break on first HTTP 200. A miss returns 404 fast; a full sweep takes seconds. Use a desktop User-Agent header.
  - Reusable probe: `python scripts/wb_card_probe.py <nm_id>` prints basket + name/brand/description in 3 lines.
- **Search SERP** (only when basket probing is not enough):
  - `GET https://u-search.wb.ru/exactmatch/ru/common/v4/search?appType=1&curr=rub&dest=-1257786&query=<ENCODED_QUERY>&resultset=catalog` — works with plain urllib + desktop UA.
  - Fallback: `search.wb.ru/exactmatch/...` (can 429).
  - Do NOT query deprecated `card.wb.ru/cards/v1/detail` (404/403).
- **Browser as last resort:** only for live pricing/rank checks that need rendered JS (`browser_exec` / CDP). Never loop through 10+ alternative fetch routes when one fails — try the CDN basket once, then say what's blocked.

## Project Structure Conventions
- Store credentials in `D:\HERMES FILES\02_Wildberries_Kружки\.env` (never commit or log tokens).
- Maintain modular scripts for:
  1. `wb_orders_fbs.py` — FBS order alerts and packing queue.
  2. `wb_analytics.py` — revenue and unit economics.
  3. `wb_competitor_tracker.py` — browser-based competitor price & stock scraping.
---
name: wildberries-automation
description: "Use for Wildberries: Seller API, FBS, prices, and trends."
version: 0.1.0
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
- **Reliability**: Fully accessible via standard HTTP (`urllib`, `requests`, `httpx`).

### 2. Public / Market Monitoring (Competitors & Trends)
Public endpoints do NOT accept seller tokens and are protected by strict WAF / TLS fingerprinting.

- **Endpoints**:
  - Product Cards: `card.wb.ru/cards/v2/detail`
  - Search SERP: `search.wb.ru/exactmatch/.../v5/search`
  - Auto-complete / Search Suggestions: `suggestions.wb.ru/search/suggestions`
- **Access Method**:
  - Direct `curl` or server scripts trigger HTTP 400/429 blocks.
  - Must use headless/real browser execution (`browser_exec` / CDP) to bypass TLS/WAF guards for live public pricing and search rank checks.

## Project Structure Conventions
- Store credentials in `D:\HERMES FILES\02_Wildberries_Kружки\.env` (never commit or log tokens).
- Maintain modular scripts for:
  1. `wb_orders_fbs.py` — FBS order alerts and packing queue.
  2. `wb_analytics.py` — revenue and unit economics.
  3. `wb_competitor_tracker.py` — browser-based competitor price & stock scraping.

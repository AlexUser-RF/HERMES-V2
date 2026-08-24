#!/bin/bash
cd "$HOME/AppData/Local/hermes"
KEY=$(grep -oE "^OPENROUTER_API_KEY=.*" .env | cut -d= -f2- | tr -d '"' | tr -d "'")
curl -s -m 90 "https://openrouter.ai/api/v1/chat/completions" \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  --data @"D:/HERMES FILES/.tmp_scrape/vtest_req.json"

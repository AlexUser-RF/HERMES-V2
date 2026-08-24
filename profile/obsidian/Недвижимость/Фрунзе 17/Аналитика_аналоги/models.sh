#!/bin/bash
cd "$HOME/AppData/Local/hermes"
KEY=$(grep -oE "^OPENROUTER_API_KEY=.*" .env | cut -d= -f2- | tr -d '"' | tr -d "'")
curl -s -m 60 "https://openrouter.ai/api/v1/models" -H "Authorization: Bearer $KEY"

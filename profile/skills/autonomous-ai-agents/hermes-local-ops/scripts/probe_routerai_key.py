# -*- coding: utf-8 -*-
"""Live-probe RouterAI keys WITHOUT printing them.

Usage:
  python probe_routerai_key.py                 # compare root vs profiles/flipping
  python probe_routerai_key.py <profile>       # compare root vs that profile

Why a real completion and not GET /models: /models answers 200 even for a dead
bearer token, so it passes while every turn 401s. Only POST /chat/completions
proves the key works. Codes: 401 = missing/invalid key; 403 "Access denied by
security policy" = wrong host (canonical openrouter.ai while the profile routes
to RouterAI) or model slug absent from the catalog.
"""
import os, sys, json, urllib.request, urllib.error

H = os.path.join(os.environ['LOCALAPPDATA'], 'hermes')
profile = sys.argv[1] if len(sys.argv) > 1 else 'flipping'
BASE = 'https://routerai.ru/api/v1'
MODELS = ['google/gemini-3.8-flash', 'deepseek/deepseek-v4-flash-0731']


def parse_env(p):
    d = {}
    if not os.path.exists(p):
        return d
    for line in open(p, encoding='utf-8', errors='replace'):
        s = line.strip()
        if not s or s.startswith('#') or '=' not in s:
            continue
        k, v = s.split('=', 1)
        d[k.strip()] = v.strip().strip('"').strip("'")
    return d


def mask(k):
    return f"{k[:4]}...{k[-3:]} (len {len(k)})" if k else '<empty>'


def probe(key, label):
    if not key:
        print(f"[{label}] no key")
        return
    print(f"[{label}] key={mask(key)}")
    try:
        req = urllib.request.Request(BASE + '/models', headers={'Authorization': 'Bearer ' + key})
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"[{label}]   GET /models -> {r.status}  (NOT proof the key works)")
    except urllib.error.HTTPError as e:
        print(f"[{label}]   GET /models -> {e.code}")
    except Exception as e:
        print(f"[{label}]   GET /models -> ERR {e}")
    for m in MODELS:
        body = json.dumps({"model": m, "messages": [{"role": "user", "content": "ping"}],
                           "max_tokens": 5}).encode()
        try:
            req = urllib.request.Request(BASE + '/chat/completions', data=body,
                                         headers={'Authorization': 'Bearer ' + key,
                                                  'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.loads(r.read().decode('utf-8', 'replace'))
                print(f"[{label}]   chat {m:40s} -> {r.status} OK ({d.get('model')})")
        except urllib.error.HTTPError as e:
            print(f"[{label}]   chat {m:40s} -> {e.code} {e.read()[:120].decode('utf-8', 'replace')}")
        except Exception as e:
            print(f"[{label}]   chat {m:40s} -> ERR {e}")


root_key = parse_env(os.path.join(H, '.env')).get('OPENROUTER_API_KEY', '')
prof_key = parse_env(os.path.join(H, 'profiles', profile, '.env')).get('OPENROUTER_API_KEY', '')
print("== root ==")
probe(root_key, 'root')
print(f"== profiles/{profile} ==")
probe(prof_key, profile)
print("keys identical:", bool(root_key) and root_key == prof_key)

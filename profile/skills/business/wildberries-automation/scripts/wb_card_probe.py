"""
WB public product-card extractor via CDN basket routing.
No auth, no browser: probes basket-01..60 for vol/part derived from nm_id.
Usage: python wb_card_probe.py <nm_id> [more_nm_ids]
Quiet output: basket number + name/brand/description summary per card.
"""
import json
import sys
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def find_wb_basket(nm_id, max_basket=60, timeout=1.2):
    """Return (basket_str, card_dict) or (None, None)."""
    vol = nm_id // 100000
    part = nm_id // 1000
    start = max(1, vol // 100 + 1)
    order = list(range(start, max_basket + 1)) + list(range(1, start))
    for b in order:
        url = f"https://basket-{b:02d}.wbbasket.ru/vol{vol}/part{part}/{nm_id}/info/ru/card.json"
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.getcode() == 200:
                    return f"{b:02d}", json.loads(resp.read().decode("utf-8"))
        except Exception:
            continue
    return None, None


def image_url(nm_id, basket_str, n=0):
    vol = nm_id // 100000
    part = nm_id // 1000
    return (
        f"https://basket-{basket_str}.wbbasket.ru/vol{vol}/part{part}"
        f"/{nm_id}/images/big/{n}.webp"
    )


def main():
    if len(sys.argv) < 2:
        print("usage: wb_card_probe.py <nm_id> [...]")
        sys.exit(1)
    for arg in sys.argv[1:]:
        nm = int(arg)
        basket, data = find_wb_basket(nm)
        if not data:
            print(f"nm={nm}: NOT FOUND in baskets 01-60")
            continue
        print(
            f"nm={nm} basket={basket} | {data.get('imt_name')} "
            f"| brand={data.get('brand')} | subj={data.get('subj_name')}"
        )
        print(f"  desc: {(data.get('description') or '')[:200]}")


if __name__ == "__main__":
    main()

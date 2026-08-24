import subprocess, os, time

UA="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
os.makedirs("D:/HERMES FILES/.tmp_scrape/pages", exist_ok=True)
ok=0
for p in range(2,25):
    url=f"https://m.avito.ru/tula/kvartiry/prodam/vtorichka/2-komnatnye?p={p}"
    out=f"D:/HERMES FILES/.tmp_scrape/pages/vt_{p}.html"
    r=subprocess.run(["curl","-s","-m","20","-L","-A",UA,url,"-o",out],capture_output=True)
    sz=os.path.getsize(out) if os.path.exists(out) else 0
    print(f"page {p}: size={sz}", flush=True)
    if sz>50000: ok+=1
    time.sleep(0.6)
print("DONE ok pages:",ok)

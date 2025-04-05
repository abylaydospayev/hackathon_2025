# --- scraper_patch.py ---
import requests
import csv
from io import StringIO
import base64
import os

CSV_API_URL = "http://www.vpngate.net/api/iphone/"
CONFIG_DIR = "vpn_configs"
PATCH_LINES = [
    "setenv enable-dco false\n",
    "data-ciphers AES-128-CBC\n",
    "redirect-gateway def1\n"
]

os.makedirs(CONFIG_DIR, exist_ok=True)

def fetch_csv_data():
    print("\U0001F4E5 Fetching VPNGate CSV API...")
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(CSV_API_URL, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text

def parse_and_save_configs(csv_text):
    csv_reader = csv.reader(StringIO(csv_text))
    next(csv_reader)
    next(csv_reader)

    saved = 0
    for row in csv_reader:
        if len(row) < 15 or not row[14].strip():
            continue

        try:
            ovpn_content = base64.b64decode(row[14].strip()).decode("utf-8")
        except:
            continue

        ip = row[1].strip()
        country = row[6].strip().upper().replace(" ", "_")
        filename = f"{ip}_{country}.ovpn"
        filepath = os.path.join(CONFIG_DIR, filename)

        lines = ovpn_content.splitlines(keepends=True)
        patched = []
        for line in lines:
            patched.append(line)
            if line.strip() == "client":
                patched += PATCH_LINES

        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(patched)

        print(f"✅ Saved: {filename}")
        saved += 1

    print(f"\n🎉 Done! {saved} configs saved to {CONFIG_DIR}")

if __name__ == "__main__":
    try:
        csv_text = fetch_csv_data()
        parse_and_save_configs(csv_text)
    except Exception as e:
        print(f"❌ Error: {e}")
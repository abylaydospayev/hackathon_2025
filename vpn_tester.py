import os
import subprocess
import time
import requests
import json
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

CONFIG_DIR = "vpn_configs"
LOG_DIR = "logs"
RESULTS_FILE = "vpn_test_results.json"
OPENVPN_PATH = r"C:\Program Files\OpenVPN\bin\openvpn.exe"
TIMEOUT = 20  # seconds
MAX_WORKERS = 4  # Number of concurrent threads

os.makedirs(LOG_DIR, exist_ok=True)

def get_current_ip():
    try:
        response = requests.get("https://ipinfo.io/json", timeout=5)
        if response.ok:
            return response.json().get("ip")
    except Exception:
        pass
    return None

def ping_host(host, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, 443))
        return True
    except:
        return False

def extract_remote_ip(config_path):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith("remote"):
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        return parts[1]
    except:
        return None
    return None

def test_vpn_config(filepath):
    filename = os.path.basename(filepath)
    log_path = os.path.join(LOG_DIR, filename.replace(".ovpn", ".log"))
    original_ip = get_current_ip()

    with open(log_path, "w", encoding="utf-8") as log_file:
        vpn_process = subprocess.Popen(
            [OPENVPN_PATH, "--config", filepath],
            stdout=log_file,
            stderr=subprocess.STDOUT
        )
        time.sleep(TIMEOUT)
        vpn_process.terminate()
        vpn_process.wait()

    with open(log_path, "r", encoding="utf-8") as f:
        log = f.read()

    if "AUTH_FAILED" in log:
        return {"filename": filename, "status": "auth_failed"}

    elif "Initialization Sequence Completed" in log:
        new_ip = get_current_ip()
        ip_changed = new_ip and new_ip != original_ip
        return {
            "filename": filename,
            "status": "success" if ip_changed else "connected",
            "original_ip": original_ip,
            "new_ip": new_ip
        }

    elif "TLS Error" in log or "Connection timed out" in log:
        return {"filename": filename, "status": "tls_failed"}

    else:
        return {"filename": filename, "status": "unknown_error"}



def main():
    results = []
    files = [os.path.join(CONFIG_DIR, f) for f in os.listdir(CONFIG_DIR) if f.endswith(".ovpn")]

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_file = {executor.submit(test_vpn_config, file): file for file in files}

        for future in as_completed(future_to_file):
            result = future.result()
            print(f"[{result['status'].upper()}] {result['filename']}")
            results.append(result)

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n📊 Results saved to {RESULTS_FILE}")

main()

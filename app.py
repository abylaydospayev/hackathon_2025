from flask import Flask, render_template, request, redirect, jsonify
import requests
import subprocess
import os
import glob
import random
import time 

app = Flask(__name__)

current_vpn = None              # Label of current VPN
vpn_process = None              # The subprocess handle for OpenVPN

ip_cache = {
    "data": None,
    "timestamp": 0,
    "ttl": 60  
}

# === Get Public IP Info ===
def get_current_ip():
    # Return cached IP info if still fresh
    now = time.time()
    if ip_cache["data"] and (now - ip_cache["timestamp"]) < ip_cache["ttl"]:
        return ip_cache["data"]

    services = [
        "https://ipinfo.io/json",
        "https://api.myip.com",
        "https://ifconfig.co/json"
    ]

    for url in services:
        try:
            res = requests.get(url, timeout=5)
            if res.ok:
                data = res.json()

                ip = data.get("ip") or data.get("address", "")
                city = data.get("city", "") or data.get("region", "Unknown")
                country = data.get("country", "") or data.get("country_name", "Unknown")
                loc = data.get("loc", "")
                if not loc and "latitude" in data and "longitude" in data:
                    loc = f"{data['latitude']},{data['longitude']}"

                result = {
                    "ip": ip,
                    "city": city or "Unknown",
                    "country": country or "Unknown",
                    "loc": loc or "0,0"
                }

                # 💾 Update cache
                ip_cache["data"] = result
                ip_cache["timestamp"] = now
                return result
        except:
            continue

    # Fallback if all services fail
    return {
        "ip": "",
        "city": "Unknown",
        "country": "Unknown",
        "loc": "0,0",
        "error": "All IP services failed"
    }



# === Load VPN Configs from vpn_configs folder ===
def load_vpn_configs(folder="vpn_configs/connected"):
    configs = {}
    for filepath in glob.glob(f"{folder}/*.ovpn"):
        filename = os.path.basename(filepath)
        name = filename.replace(".ovpn", "")
        parts = name.rsplit("_", 1)

        ip_or_host = parts[0]
        country_code = parts[1] if len(parts) == 2 else "UN"
        flag = chr(0x1F1E6 + ord(country_code[0]) - ord('A')) + chr(0x1F1E6 + ord(country_code[1]) - ord('A'))
        label = f"{ip_or_host} {country_code} {flag}"

        configs[label] = {
            "path": filepath,
            "country_code": country_code
        }

    return configs

# Load configs before routes
vpn_configs = load_vpn_configs()

# === Home Page ===
@app.route("/")
def home():
    ip_info = get_current_ip()
    return render_template("vpn.html", ip_info=ip_info, vpn_configs=vpn_configs, current_vpn=current_vpn)

# === Connect to VPN ===
@app.route("/connect", methods=["POST"])
def connect():
    global current_vpn, vpn_process
    selected = request.form.get("vpn_config")
    config_entry = vpn_configs.get(selected)

    if config_entry and os.path.exists(config_entry["path"]):
        if vpn_process:
            vpn_process.terminate()
            vpn_process.wait()

        openvpn_path = r"C:\\Program Files\\OpenVPN\\bin\\openvpn.exe"
        log_file = open("vpn_log.txt", "w", buffering=1)  # Line-buffered log

        vpn_process = subprocess.Popen(
            [openvpn_path, "--config", config_entry["path"]],
            stdout=log_file,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True
        )

        current_vpn = selected

    return redirect("/")

# === Disconnect VPN ===
@app.route("/disconnect", methods=["POST"])
def disconnect():
    global current_vpn, vpn_process
    if vpn_process:
        vpn_process.terminate()
        vpn_process.wait()
        vpn_process = None
    current_vpn = None
    return redirect("/")

# === Ghost Me (Random VPN) ===
@app.route("/ghost", methods=["POST"])
def ghost_me():
    global current_vpn, vpn_process
    if vpn_process:
        vpn_process.terminate()
        vpn_process.wait()

    random_label = random.choice(list(vpn_configs.keys()))
    config_entry = vpn_configs[random_label]

    openvpn_path = r"C:\\Program Files\\OpenVPN\\bin\\openvpn.exe"
    log_file = open("vpn_log.txt", "w", buffering=1)

    vpn_process = subprocess.Popen(
        [openvpn_path, "--config", config_entry["path"]],
        stdout=log_file,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True
    )
    current_vpn = random_label

    return jsonify({"status": "connected", "vpn": random_label})

# === IP Check Endpoint ===
@app.route("/get_ip")
def get_ip():
    ip_info = get_current_ip()
    return jsonify(ip_info)

# === Run App ===
if __name__ == "__main__":
    app.run(debug=True)

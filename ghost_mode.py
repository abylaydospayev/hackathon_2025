# ghost_mode.py (Flask route logic)
from flask import Flask, jsonify, render_template, request
import os
import random
import json
import requests
import subprocess
import time

ghost_vpn_data = "vpn_test_results.json"
CONFIG_DIR = "vpn_configs"
OPENVPN_PATH = r"C:\\Program Files\\OpenVPN\\bin\\openvpn.exe"
vpn_process = None
current_vpn = None

def get_successful_vpns():
    if not os.path.exists(ghost_vpn_data):
        return []
    with open(ghost_vpn_data, 'r') as f:
        data = json.load(f)
        return [entry for entry in data if entry.get("status") == "success"]

def get_ip_info():
    try:
        return requests.get("https://ipinfo.io/json", timeout=5).json()
    except:
        return {"ip": "Unknown", "city": "Unknown", "country": "Unknown", "loc": "0,0"}

def connect_to_vpn(filepath):
    global vpn_process
    if vpn_process:
        vpn_process.terminate()
        vpn_process.wait()
    subprocess.Popen([OPENVPN_PATH, "--config", filepath])
    time.sleep(15)  # Wait for connection to stabilize

def get_country_flag(country_code):
    try:
        return chr(0x1F1E6 + ord(country_code[0]) - ord('A')) + chr(0x1F1E6 + ord(country_code[1]) - ord('A'))
    except:
        return "🌍"

app = Flask(__name__)

@app.route("/")
def index():
    ip_info = get_ip_info()
    return render_template("vpn.html", ip_info=ip_info, current_vpn=current_vpn)

@app.route("/ghost", methods=["POST"])
def ghost_mode():
    global current_vpn
    vpns = get_successful_vpns()
    if not vpns:
        return jsonify({"error": "No working VPNs found."}), 500

    best = random.choice(vpns)  # (later, use score-based selection)
    filename = best['filename']
    path = os.path.join(CONFIG_DIR, filename)
    connect_to_vpn(path)
    current_vpn = filename

    ip_info = get_ip_info()
    country_code = ip_info.get("country", "UN")
    flag = get_country_flag(country_code)
    return jsonify({
        "status": "connected",
        "ip": ip_info.get("ip"),
        "city": ip_info.get("city"),
        "country": ip_info.get("country"),
        "flag": flag
    })

if __name__ == '__main__':
    app.run(debug=True)

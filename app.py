from flask import Flask, render_template, request, redirect, jsonify
import requests
import subprocess
import os

app = Flask(__name__)

# === Hardcoded VPN Config Files ===
vpn_configs = {
    "Japan 🇯🇵": {
        "path": "vpn_configs/vpngate_2i6.opengw.net_udp_1194.ovpn",
        "country_code": "JP"
    },
    # Add more here if needed
}

current_vpn = None              # Label of current VPN
vpn_process = None              # The subprocess handle for OpenVPN

# === Get Public IP Info ===
def get_current_ip():
    try:
        response = requests.get("https://ipinfo.io/json", timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"ip": "Unavailable", "city": "Error", "country": "Error"}
    except Exception as e:
        return {"ip": "Unknown", "city": "Unknown", "country": "Unknown", "error": str(e)}

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
        # Stop existing VPN if running
        if vpn_process:
            vpn_process.terminate()
            vpn_process.wait()

        # ✅ Full path to OpenVPN
        openvpn_path = r"C:\Program Files\OpenVPN\bin\openvpn.exe"
        log_file = open("vpn_log.txt", "w")

        vpn_process = subprocess.Popen(
            [openvpn_path, "--config", config_entry["path"]],
            stdout=log_file,
            stderr=subprocess.STDOUT
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

# === IP Check Endpoint ===
@app.route("/get_ip")
def get_ip():
    ip_info = get_current_ip()
    return jsonify(ip_info)

# === Run App ===
if __name__ == "__main__":
    app.run(debug=True)
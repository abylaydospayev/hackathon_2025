from flask import Flask, render_template, request, redirect, jsonify
import requests
import subprocess
import os
import glob
import joblib
import numpy as np
import time

app = Flask(__name__)

current_vpn = None  # Label of current VPN
vpn_process = None  # The subprocess handle for OpenVPN
model = joblib.load('vpn_recommendation_model.pkl')  # Load the trained model

# Cache structure to store IP information temporarily
ip_cache = {
    "data": None,
    "timestamp": 0,
    "ttl": 300  # Cache TTL in seconds (5 minutes)
}

# === Get Public IP Info ===
import time
import requests

# Cache structure to store IP information temporarily
ip_cache = {
    "data": None,
    "timestamp": 0,
    "ttl": 300  # Cache TTL in seconds (5 minutes)
}

# === Get Public IP Info ===
import time
import requests

# Cache structure to store IP information temporarily
ip_cache = {
    "data": None,
    "timestamp": 0,
    "ttl": 300  # Cache TTL in seconds (5 minutes)
}

# === Get Public IP Info ===
import time
import requests

# Cache structure to store IP information temporarily
ip_cache = {
    "data": None,
    "timestamp": 0,
    "ttl": 300  # Cache TTL in seconds (5 minutes)
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

                # Logging for debugging the returned data
                print(f"Data from {url}: {data}")

                ip = data.get("ip") or data.get("address", "")
                city = data.get("city", "Unknown") or data.get("region", "Unknown")
                country = data.get("country", "Unknown") or data.get("country_name", "Unknown")
                loc = data.get("loc", "")
                
                if not loc and "latitude" in data and "longitude" in data:
                    loc = f"{data['latitude']},{data['longitude']}"

                # Debugging output for the city and location info
                print(f"City: {city}, Country: {country}, Location: {loc}")

                result = {
                    "ip": ip,
                    "city": city,
                    "country": country,
                    "loc": loc or "0,0"
                }

                #  Update cache
                ip_cache["data"] = result
                ip_cache["timestamp"] = now
                return result
        except requests.exceptions.RequestException as e:
            print(f"Error fetching IP info from {url}: {e}")
            continue

    return {"ip": "", "city": "Unknown", "country": "Unknown", "loc": "0,0", "error": "All IP services failed"}


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

# === Get AI Recommendations ===
def get_best_vpn():
    vpn_data = []
    country_map = {
        "JP": 0,
        "KR": 1,
        "US": 2,
        "TH": 3,
        "UN": 4
    }

    vpn_scores = []  # Store the score and explanation for each VPN

    # Gather past VPN connection data (you might want to replace this with actual data)
    for name, config in vpn_configs.items():
        # Features: [success_rate, latency, country_code (encoded)]
        success_rate = np.random.random()  # Placeholder for success rate
        latency = np.random.random() * 100  # Placeholder for latency
        country_code = config["country_code"]  # Feature for the model

        # Convert country_code to numerical value
        country_numeric = country_map.get(country_code, 4)  # Default to "UN" if country_code not found

        vpn_data.append([success_rate, latency, country_numeric])

        # Get model prediction (VPN score)
        vpn_score = model.predict([vpn_data[-1]])[0]  # Get the predicted score for the VPN

        # Store VPN score and features for explanation
        vpn_scores.append({
            "vpn_name": name,
            "score": vpn_score,
            "success_rate": success_rate,
            "latency": latency,
            "country_code": country_code,
            "country_numeric": country_numeric
        })

    # Sort VPNs by their score in descending order
    vpn_scores.sort(key=lambda x: x["score"], reverse=True)

    # Get the best VPN (the one with the highest score)
    best_vpn = vpn_scores[0]

    # Provide an explanation for why the best VPN is recommended
    explanation = f"The recommended VPN is <strong>{best_vpn['vpn_name']}</strong> with a score of <strong>{best_vpn['score']:.2f}</strong>."
    explanation += f" It has the best performance with a success rate of <strong>{best_vpn['success_rate']*100:.2f}%</strong> and an average latency of <strong>{best_vpn['latency']:.2f} ms</strong>."
    explanation += f" The country of the server is <strong>{best_vpn['country_code']}</strong>."

    return best_vpn, explanation, vpn_scores  # Return VPN comparison data as well


# === Home Page ===
@app.route("/")
def home():
    ip_info = get_current_ip()
    best_vpn, explanation, vpn_comparison = get_best_vpn()
    return render_template("vpn.html", ip_info=ip_info, vpn_configs=vpn_configs, current_vpn=current_vpn, best_vpn=best_vpn, explanation=explanation, vpn_comparison=vpn_comparison)

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

# === IP Check Endpoint ===
@app.route("/get_ip")
def get_ip():
    ip_info = get_current_ip()
    return jsonify(ip_info)

# === Run App ===
if __name__ == "__main__":
    app.run(debug=True)

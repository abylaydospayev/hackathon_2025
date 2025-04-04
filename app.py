from flask import Flask, render_template, request
import requests

app = Flask(__name__)

proxy_list = [
    "http://192.168.1.1:8080",
    "http://103.25.47.13:3128",
    "http://45.67.89.12:8080"
]

current_proxy = None

def get_ip_info(proxy=None):
    proxies = {"http": proxy, "https": proxy} if proxy else None
    try:
        response = requests.get("http://ipinfo.io/json", proxies=proxies, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"ip": "Unavailable", "city": "Error", "country": "Error"}
    except Exception as e:
        return {
            "ip": "Unknown",
            "city": "Unknown",
            "country": "Unknown",
            "error": str(e)
        }


@app.route('/')
def home():
    ip_info = get_ip_info(current_proxy)
    return render_template("index.html", ip_info=ip_info, proxies=proxy_list)

@app.route('/switch', methods=['POST'])
def switch_proxy():
    global current_proxy
    selected_proxy = request.form.get("proxy")
    current_proxy = selected_proxy
    ip_info = get_ip_info(current_proxy)
    return render_template("index.html", ip_info=ip_info, proxies=proxy_list)

if __name__ == "__main__":
    app.run(debug=True)

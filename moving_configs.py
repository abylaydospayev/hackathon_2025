import os
import json
import shutil

CONFIG_DIR = "vpn_configs"
RESULTS_FILE = "vpn_test_results.json"

# Define categories and their subfolders
CATEGORIES = {
    "connected": "connected",
    "success": "working",
    "connected_no_ip_change": "connected",
    "auth_failed": "auth_failed",
    "tls_failed": "tls_failed",
    "unreachable": "unreachable",
    "unknown_error": "errors",
    "failed": "failed",
}

# Ensure all folders exist
for folder in set(CATEGORIES.values()):
    os.makedirs(os.path.join(CONFIG_DIR, folder), exist_ok=True)

# Load results
with open(RESULTS_FILE, "r", encoding="utf-8") as f:
    results = json.load(f)

# Move based on status
for entry in results:
    status = entry.get("status", "unknown_error")
    filename = entry.get("filename")
    if not filename:
        continue

    src = os.path.join(CONFIG_DIR, filename)
    dest_subfolder = CATEGORIES.get(status, "other")
    dst = os.path.join(CONFIG_DIR, dest_subfolder, filename)

    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"✅ Moved {filename} -> {dest_subfolder}/")
    else:
        print(f"❌ Missing file: {filename}")

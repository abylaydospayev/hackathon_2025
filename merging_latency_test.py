import json

# Load VPN test results
with open("vpn_test_results.json", "r") as vpn_file:
    vpn_results = json.load(vpn_file)

# Load latency results
with open("latency_results.json", "r") as latency_file:
    latency_data = json.load(latency_file)

# Merge the latency data with VPN test results
for result in vpn_results:
    filename = result['filename']
    latency = latency_data.get(filename)
    result['latency'] = latency if latency is not None else 'No Latency Data'

# Save the updated results to a new file
with open("updated_vpn_results.json", "w") as updated_file:
    json.dump(vpn_results, updated_file, indent=2)

print("Updated VPN results saved with latency data.")

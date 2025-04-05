import json

# Load the VPN test results from the JSON file
with open('updated_vpn_results.json', 'r') as file:
    vpn_results = json.load(file)

# Calculate success rate and average latency
total_vpn = len(vpn_results)
successful_vpn = sum(1 for result in vpn_results if result['status'] == 'connected')
failed_vpn = total_vpn - successful_vpn
latencies = [result['latency'] for result in vpn_results if result['latency'] != 0.0]

# Calculate average latency
average_latency = sum(latencies) / len(latencies) if latencies else 0

# Print the results
print(f"Total VPNs: {total_vpn}")
print(f"Successful VPNs: {successful_vpn} ({(successful_vpn / total_vpn) * 100:.2f}%)")
print(f"Failed VPNs: {failed_vpn} ({(failed_vpn / total_vpn) * 100:.2f}%)")
print(f"Average Latency: {average_latency:.2f} ms")

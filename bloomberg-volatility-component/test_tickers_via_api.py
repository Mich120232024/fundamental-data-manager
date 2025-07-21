import requests
import json

# Test different ticker formats for 1D/2D/3D via the API
API_URL = "http://20.172.249.92:8080"

test_cases = [
    {
        "name": "1D/2D/3D with EUR prefix (from Bloomberg docs)",
        "tickers": [
            "EUR1D25R BGN Curncy",
            "EUR2D25R BGN Curncy", 
            "EUR3D25R BGN Curncy",
            "EUR1D25B BGN Curncy",
            "EUR2D25B BGN Curncy",
            "EUR3D25B BGN Curncy",
            "EUR1DV BGN Curncy",
            "EUR2DV BGN Curncy",
            "EUR3DV BGN Curncy"
        ]
    },
    {
        "name": "1D/2D/3D with EURUSD prefix",
        "tickers": [
            "EURUSD1D25R BGN Curncy",
            "EURUSD2D25R BGN Curncy",
            "EURUSD3D25R BGN Curncy",
            "EURUSD1D25B BGN Curncy",
            "EURUSD2D25B BGN Curncy",
            "EURUSD3D25B BGN Curncy",
            "EURUSDV1D BGN Curncy",
            "EURUSDV2D BGN Curncy",
            "EURUSDV3D BGN Curncy"
        ]
    },
    {
        "name": "1D/2D/3D with different format variations",
        "tickers": [
            "EURUSD25R1D BGN Curncy",
            "EURUSD25R2D BGN Curncy",
            "EURUSD25R3D BGN Curncy",
            "EUR1DV Curncy",  # Without BGN
            "EUR2DV Curncy",
            "EUR3DV Curncy",
            "EURUSD1D Curncy",
            "EURUSD2D Curncy",
            "EURUSD3D Curncy"
        ]
    }
]

# Test known working tickers first
print("Testing known working tickers...")
known_working = ["EURUSD25R1M BGN Curncy", "EURUSDV1M BGN Curncy", "EURUSD25B1M BGN Curncy"]
response = requests.post(
    f"{API_URL}/api/bloomberg/reference",
    json={"securities": known_working, "fields": ["PX_LAST", "PX_BID", "PX_ASK", "SECURITY_NAME"]},
    headers={"X-API-Key": "test"}
)
print("Known working response:", json.dumps(response.json(), indent=2))
print("\n" + "="*80 + "\n")

# Test each set of tickers
for test_case in test_cases:
    print(f"Testing: {test_case['name']}")
    response = requests.post(
        f"{API_URL}/api/bloomberg/reference",
        json={"securities": test_case['tickers'], "fields": ["PX_LAST", "PX_BID", "PX_ASK", "SECURITY_NAME", "SECURITY_DES"]},
        headers={"X-API-Key": "test"}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and 'securities_data' in data['data']:
            for sec in data['data']['securities_data']:
                print(f"\nTicker: {sec['security']}")
                if sec['success']:
                    print(f"  SUCCESS - Fields: {sec.get('fields', {})}")
                else:
                    print(f"  FAILED - Error: {sec.get('error', 'Unknown error')}")
        else:
            print(f"API Error: {data}")
    else:
        print(f"HTTP Error {response.status_code}: {response.text}")
    
    print("\n" + "="*80 + "\n")

# Test the logs endpoint to see recent requests
print("Checking API logs...")
try:
    logs_response = requests.get(f"{API_URL}/api/logs", headers={"X-API-Key": "test"})
    if logs_response.status_code == 200:
        print("Recent API logs:")
        print(logs_response.text[:2000])  # First 2000 chars
except:
    print("Could not fetch logs")
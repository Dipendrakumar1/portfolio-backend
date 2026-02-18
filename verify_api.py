import requests
import json

def test_api():
    base_url = "http://127.0.0.1:5000"
    endpoints = ["/api/about", "/api/certificates"]
    
    for endpoint in endpoints:
        try:
            print(f"Testing {endpoint}...")
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                print("Response Header:", response.headers.get('Content-Type'))
                data = response.json()
                print(f"Success! Received {len(str(data))} bytes.")
            else:
                print(f"Failed! Response: {response.text}")
        except Exception as e:
            print(f"Error testing {endpoint}: {e}")

if __name__ == "__main__":
    test_api()

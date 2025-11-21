"""Test Reclame Aqui API directly"""
import requests
import json

# Company info from the analysis
COMPANY_ID = 109913
COMPANY_SHORTNAME = "drogaria-venancio-site-e-televendas"
API_BASE = "https://iosite.reclameaqui.com.br/raichu-io-site-v1"

# Headers to mimic browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://www.reclameaqui.com.br",
    "Referer": "https://www.reclameaqui.com.br/",
}

# Test different API endpoints
endpoints_to_test = [
    # Possible complaint list endpoints
    f"/company/{COMPANY_ID}/complaints?offset=0&limit=10",
    f"/company/{COMPANY_ID}/complaints/list?offset=0&limit=10",
    f"/companies/{COMPANY_ID}/complaints?offset=0&limit=10",
    f"/complaint/company/{COMPANY_ID}?offset=0&limit=10",
    f"/complaints/company/{COMPANY_ID}?offset=0&limit=10",
    f"/company/complaints/{COMPANY_ID}?offset=0&limit=10",
    f"/complaint/list/{COMPANY_ID}?offset=0&limit=10",
    # Using shortname
    f"/company/{COMPANY_SHORTNAME}/complaints?offset=0&limit=10",
]

print("Testing Reclame Aqui API endpoints...\n")

for endpoint in endpoints_to_test:
    url = f"{API_BASE}{endpoint}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        status = response.status_code

        if status == 200:
            try:
                data = response.json()
                print(f"✓ SUCCESS {status}: {endpoint}")
                print(f"  Response type: {type(data)}")
                if isinstance(data, dict):
                    print(f"  Keys: {list(data.keys())[:5]}")
                elif isinstance(data, list):
                    print(f"  Items: {len(data)}")
                print()
            except:
                print(f"✓ SUCCESS {status}: {endpoint}")
                print(f"  Response (not JSON): {response.text[:100]}")
                print()
        elif status == 404:
            print(f"✗ NOT FOUND {status}: {endpoint}")
        else:
            print(f"? STATUS {status}: {endpoint}")
            print(f"  Response: {response.text[:200]}")
            print()
    except Exception as e:
        print(f"✗ ERROR: {endpoint}")
        print(f"  {str(e)[:100]}")
        print()

# Also try the chimera API
print("\n\nTesting Chimera API...")
chimera_url = f"https://chimera-api.reclameaqui.com.br/public/company/{COMPANY_ID}/complaints"
try:
    response = requests.get(chimera_url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Keys: {list(data.keys()) if isinstance(data, dict) else 'list'}")
except Exception as e:
    print(f"Error: {e}")
